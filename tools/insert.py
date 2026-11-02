"""insert.py: script/*.json -> the game files the build patches in.

    python -X utf8 tools/insert.py plan [--dir script] [--json work/insert.json]
    python -X utf8 tools/insert.py check

`plan()` reads the text JSON (default `script/`, or `work/mark/` for the marker build) and returns
{CPK name: {'dir/name': bytes}, 'iso': {'/ISO/PATH': bytes}} for `build.edits()`. Files whose text did not change are
left out, so an all-empty `en` gives no edits and a byte-identical ISO.

MZ scripts (scene + play) are rebuilt with resized string slots: every jump argument (absolute word offset from file
start, positions verified over all 80 scene scripts) is re-mapped old -> new instruction offsets, then the result is
re-parsed and every jump re-checked. UI tables, the EBOOT save titles and the PARAM.SFO title are fixed slots, edited in
place, so their English must fit (insert raises with the id otherwise).
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mzscript, uitable
from textfmt import encode, read_json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CPK = os.path.join(ROOT, 'work', 'cpk')
SCRIPT = os.path.join(ROOT, 'script')
EBOOT = os.path.join(ROOT, 'work', 'eboot', 'EBOOT.ELF')
SFO = os.path.join(ROOT, 'work', 'iso', 'PSP_GAME', 'PARAM.SFO')

SCENE_DIR = ('INST', 'scene', 'script')
PLAY_DIR = ('INST', 'play', 'script')


def _pad(n, m=4):
    return (n + m - 1) // m * m


# Absolute-word-offset arguments, by opcode: the word indexes (0 = first arg word after op+size) that hold a jump.
# Positions and the hit rate (every value landed on an instruction start over all 80 scripts) are in docs/re/text.md.
JUMP_WORDS = {
    0x0B: (0,), 0x0D: (0,), 0x0E: (0,), 0x16: (1,), 0x18: (0,), 0x22: (4,), 0x2B: (4,), 0x2F: (0,),
    0x35: (0,), 0x47: (0,), 0x4F: (3,), 0x54: (0,), 0x55: (0, 1, 2, 3), 0x5D: (1,), 0x89: (1, 2),
}
CHOICE_OP = 0x51      # every word after the choice string is a jump target
# rhythm charts: 0x47's argument is not an offset (26 of 29 values miss every instruction start)
PLAY_SKIP = {0x47}


def jump_positions(ins, kind='scene'):
    """-> word indexes of the instruction's jump arguments (CHOICE_OP: all words after the string)."""
    if kind == 'play' and ins.op in PLAY_SKIP:
        return ()
    if ins.op == CHOICE_OP:
        out, seen_slot = [], False
        wi = 0
        for tok in ins.tokens:
            if isinstance(tok, mzscript.Slot):
                seen_slot = True
                wi += 1 + tok.capacity // 4
                continue
            if seen_slot:
                out.append(wi)
            wi += 1
        return tuple(out)
    return JUMP_WORDS.get(ins.op, ())


def _word_index(tokens):
    """token index -> arg word index (a string slot occupies 1 + capacity/4 words)."""
    idx, wi = [], 0
    for tok in tokens:
        idx.append(wi)
        wi += (1 + tok.capacity // 4) if isinstance(tok, mzscript.Slot) else 1
    return idx


def patch_script(name, data, texts, kind='scene', shared=None):
    """Rebuild one MZ file with new text for the slots in TEXTS ({} or same text -> the original bytes).
    SHARED: {name-table index: text} for the op-0x19 speaker table (its slots follow the table order)."""
    sc = mzscript.parse(data, kind)
    texts = dict(texts)
    for i, ins in enumerate(sc.instrs):
        if ins.table and shared:
            for k, slot in enumerate(ins.table):
                if k in shared:
                    texts.setdefault(slot.off, shared[k])
    if not any(texts.get(s.off, s.text) != s.text for s in sc.slots):
        return None
    # 1. new capacity per slot: keep the original when the text still fits (no shift, no need to re-map)
    caps = {}
    for s in sc.slots:
        t = texts.get(s.off, s.text)
        if t == s.text:
            caps[s.off] = s.capacity
            continue
        n = len(encode(t))
        caps[s.off] = s.capacity if n <= s.capacity else _pad(n + 1)
    # 2. old -> new instruction offsets (bytes and words)
    off_map, new_off, sizes = {}, 4, []
    for ins in sc.instrs:
        size = 4 + sum((4 + caps[t.off]) if isinstance(t, mzscript.Slot) else 4 for t in ins.tokens)
        if ins.table:
            size += sum(4 + caps[t.off] for t in ins.table)
        off_map[ins.off] = new_off
        sizes.append(size)
        new_off += size
    word_map = {k // 4: v // 4 for k, v in off_map.items()}
    starts = set(word_map)
    # 3. rewrite jump arguments
    for ins in sc.instrs:
        js = jump_positions(ins, kind)
        if not js:
            continue
        widx = _word_index(ins.tokens)
        for wi in js:
            if wi not in widx:
                continue          # the op carries this argument only in some instances (e.g. 0x47 end marker)
            ti = widx.index(wi)
            v = ins.tokens[ti]
            if not isinstance(v, int) or v in (0, 1):
                continue          # 0/1 are ambiguous ("end", "none", index) and stay as they are
            if v in word_map:
                ins.tokens[ti] = word_map[v]
            elif v not in starts:
                raise ValueError(f'{name} 0x{ins.off:x} op 0x{ins.op:02x} word {wi}: {v:#x} is not an instruction start')
    # 4. serialize with the new capacities
    out = bytearray(mzscript.MAGIC)
    for ins in sc.instrs:
        out += b'\0\0\0\0'
        for tok in ins.tokens:
            if isinstance(tok, mzscript.Slot):
                out += _slot(tok, texts.get(tok.off, tok.text), caps[tok.off])
            else:
                out += tok.to_bytes(4, 'little')
        words = (len(out) - off_map[ins.off]) // 4
        out[off_map[ins.off]:off_map[ins.off] + 4] = ins.op.to_bytes(2, 'little') + words.to_bytes(2, 'little')
        if ins.table:
            for tok in ins.table:
                out += _slot(tok, texts.get(tok.off, tok.text), caps[tok.off])
    # 5. self-check: the new file parses to EOF and every jump lands on an instruction start
    new = mzscript.parse(bytes(out), kind)
    starts = {i.off // 4 for i in new.instrs}
    for ins in new.instrs:
        wi = _word_index(ins.tokens)
        for w in jump_positions(ins, kind):
            if w not in wi:
                continue
            v = ins.tokens[wi.index(w)]
            if isinstance(v, int) and v > 1 and v not in starts:
                raise ValueError(f'{name}: rebuilt jump 0x{ins.off:x} word {w} -> {v:#x} misses every instruction')
    return bytes(out)


def _slot(slot, text, cap):
    return (slot.type.to_bytes(2, 'little') + (cap // 4).to_bytes(2, 'little')
            + encode(text) + b'\0' * (cap - len(encode(text))))


def load_texts(directory=SCRIPT):
    """-> {(relpath under script/): {slot offset: text}}, only non-empty `en`; plus ('names', {index: text}) for the
    shared op-0x19 speaker table (`scene/_speaker_names.json`, whose offsets belong to one reference script)."""
    out = {}
    names = {}
    for base, _, files in os.walk(directory):
        for fn in sorted(files):
            if not fn.endswith('.json'):
                continue
            path = os.path.join(base, fn)
            rel = os.path.relpath(path, directory).replace('\\', '/')
            doc = read_json(path)
            texts = {}
            for e in doc['entries']:
                en = e.get('en') or ''
                if not en or en == e['jp']:
                    continue
                if rel == 'scene/_speaker_names.json':
                    names[int(e['id'].split(':')[1])] = en
                elif ':name:' in e['id']:
                    names[(rel.split('/')[1][:-5], int(e['id'].split(':')[2]))] = en
                else:
                    texts[e['off']] = en
            if texts:
                out[rel] = texts
    return out, names


def plan(directory=SCRIPT, log=None, eboot=False):
    """-> the build edits: {'INST': {...}, 'NOINST': {...}, 'iso': {...}}.
    EBOOT=False keeps the disc's (encrypted) EBOOT.BIN: its save-dialog titles stay Japanese unless the owner accepts a
    plain-ELF EBOOT, which PPSSPP and CFW run but real hardware may not (docs/decisions.md D11)."""
    texts, names = load_texts(directory)
    ed = {'INST': {}, 'NOINST': {}, 'iso': {}}
    shared = {i: t for i, t in names.items() if isinstance(i, int)}
    for rel in sorted(texts):
        if not (rel.startswith('scene/') or rel.startswith('play/')):
            continue
        kind = 'scene' if rel.startswith('scene/') else 'play'
        d = SCENE_DIR if kind == 'scene' else PLAY_DIR
        stem = rel.split('/')[1][:-len('.json')]
        key = '/'.join(d[1:] + (stem + '.bin',))
        src = os.path.join(CPK, *d, stem + '.bin')
        with open(src, 'rb') as f:
            data = f.read()
        own = dict(texts[rel])
        own.update({i: t for i, t in names.items() if isinstance(i, tuple) and i[0] == stem})
        out = patch_script(rel, data, own, kind, shared if kind == 'scene' else None)
        if out is not None:
            ed['INST'][key] = out
            if log: log(f'{rel}: {len(own)} strings, {len(data)} -> {len(out)} bytes')
    # the shared name table alone (phase 6: only names translated) still rebuilds every scene script
    if shared and not any(r.startswith('scene/') for r in texts):
        for fn in sorted(os.listdir(os.path.join(CPK, *SCENE_DIR))):
            with open(os.path.join(CPK, *SCENE_DIR, fn), 'rb') as f:
                data = f.read()
            out = patch_script(fn, data, {}, 'scene', shared)
            if out is not None:
                ed['INST']['/'.join(SCENE_DIR[1:] + (fn,))] = out
    for rel in sorted(texts):
        t = texts[rel]
        if rel.startswith('ui/'):
            src = _ui_path(rel.split('/')[1][:-len('.json')])
            name = os.path.basename(src)
            with open(src, 'rb') as f:
                data = f.read()
            ed['NOINST']['systemdata/' + name] = uitable.write_table(name, data, t)
        elif rel in ('eboot.json', 'param_sfo.json'):
            continue    # handled below from their own sources (they are not table files)
        elif not (rel.startswith('scene/') or rel.startswith('play/')):
            raise ValueError(f'unknown text file {rel}')
    if eboot and 'eboot.json' in texts:
        ed['iso']['/PSP_GAME/SYSDIR/EBOOT.BIN'] = _eboot_patch(texts['eboot.json'])
    if 'param_sfo.json' in texts:
        with open(SFO, 'rb') as f:
            ed['iso']['/PSP_GAME/PARAM.SFO'] = uitable.write_sfo(f.read(), list(texts['param_sfo.json'].values())[0])
    return ed


def _ui_path(stem):
    """ui_system_text -> work/cpk/NOINST/systemdata/ui_system_text.stb (the stem keeps the table's prefix)."""
    path = os.path.join(CPK, 'NOINST', 'systemdata')
    for fn in os.listdir(path):
        if os.path.splitext(fn)[0] == stem:
            return os.path.join(path, fn)
    raise ValueError(f'no systemdata file for ui/{stem}.json')


def _eboot_patch(texts):
    """The EBOOT is a plain ELF we patch in place (string slots only: code addresses stay valid, docs/re/debug.md)."""
    with open(EBOOT, 'rb') as f:
        eboot = f.read()
    got = uitable.write_eboot(eboot, texts)
    assert len(got) == len(eboot)
    return got


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=['plan', 'check'])
    ap.add_argument('--dir', default=SCRIPT)
    ap.add_argument('--eboot', action='store_true', help='also patch the EBOOT save titles (ships a plain-ELF EBOOT)')
    ap.add_argument('--json')
    a = ap.parse_args()
    ed = plan(a.dir, log=print, eboot=a.eboot)
    n = sum(len(v) for v in ed.values())
    if a.command == 'check':
        assert n == 0, f'{n} files would be patched from an untouched {a.dir}'
        print('insert check: no edits from the source text (identity)')
        return
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump({k: {p: len(b) for p, b in v.items()} for k, v in ed.items()}, f, indent=1)
    print(f'{n} file(s) to patch: ' + ', '.join(f'{k}:{len(v)}' for k, v in ed.items() if v))


if __name__ == '__main__':
    main()
