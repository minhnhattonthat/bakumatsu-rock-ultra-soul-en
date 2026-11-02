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

# Horizontal ADV dialogue (D10, docs/re/text.md §8), applied to every scene script that carries English:
# op 0x4D (box, mode, _, _) sets a text box's direction; mode 2 = vertical tategaki (columns right to left, half-width
# glyphs rotated), mode 0 = horizontal, left to right (the engine already supports it). Op 0x4E (box, pitch, _, gap)
# sets the line pitch: 24 px suits the tategaki column, ADV_PITCH the horizontal lines.
LAYOUT_OP, PITCH_OP, DIALOGUE_OP = 0x4D, 0x4E, 0x62
VERTICAL, HORIZONTAL = 2, 0
ADV_PITCH = 16

# EBOOT code patch that goes with it (docs/re/text.md §8). A box draws into a 128x256 canvas sprite; the engine
# centres the text block on the panel by measuring it (0x0881430c) and setting the canvas pivot, but only for mode 2
# and with tategaki axes, so mode 0 text kept pivot (128,128) and sat off the panel's left edge. These words run the
# measure pass for mode 0 and measure rows: pivot = (widest line / 2, sum of line pitches / 2).
# (vaddr, original word, patched word); the plain ELF maps vaddr 0x08804000 to file offset 0xc0.
ADV_CODE = [
    (0x088147d8, 0x34050002, 0x34050000),  # 0x0881479c: run the centring pass when mode == 0 (was 2)
    (0x088147e4, 0x8e0400a4, 0x8e0400a0),  #   measure wrap limit = canvas width (was height)
    (0x088147f0, 0x34070003, 0x34070001),  #   measure direction 1 = left to right (was 3, down)
    (0x0881434c, 0xae1400ac, 0xae1300a8),  # 0x0881430c: each measured line restarts at x (was y)
    (0x0881436c, 0x8e0400ac, 0x8e0400a8),  #   block width = max line end x (was column length)
    (0x088143fc, 0x00a62823, 0x00c02821),  #   first value = sum of pitches / 2 (was canvas w - that)
    (0x08814418, 0x02b42823, 0x02b32823),  #   second value = (max x - start x) / 2
    (0x08814430, 0xe48c0024, 0xe48c0028),  #   first -> pivot y
    (0x08814438, 0xe48c0028, 0xe48c0024),  #   second -> pivot x
]
ELF_BASE = 0x08804000 - 0xc0


def _s16pair(w):
    lo, hi = w & 0xffff, w >> 16
    return lo - 0x10000 * (lo >> 15), hi - 0x10000 * (hi >> 15)


def _layout(ins):
    """Horizontal-layout rewrite of one instruction's int tokens, in place (op 0x4D mode, op 0x4E pitch)."""
    if ins.op == LAYOUT_OP and isinstance(ins.tokens[0], int) and _s16pair(ins.tokens[0])[1] == VERTICAL:
        ins.tokens[0] = (ins.tokens[0] & 0xffff) | HORIZONTAL << 16
    elif ins.op == PITCH_OP and isinstance(ins.tokens[0], int) and _s16pair(ins.tokens[0]) in ((0, 24), (1, 24), (2, 24)):
        ins.tokens[0] = (ins.tokens[0] & 0xffff) | ADV_PITCH << 16
        ins.tokens[1] = ins.tokens[1] & 0xffff     # glyph gap 0: the VWF advances carry their own gap (vwf.py)


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
    if kind == 'scene':   # English present: horizontal ADV boxes (see LAYOUT_OP)
        for ins in sc.instrs:
            _layout(ins)
    # 1. new capacity per slot: keep the original when the text still fits (no shift, no need to re-map)
    caps = {}
    for s in sc.slots:
        t = texts.get(s.off, s.text)
        if t == s.text:
            caps[s.off] = s.capacity
            continue
        n = len(encode(t))
        caps[s.off] = s.capacity if n < s.capacity else _pad(n + 1)
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
    English scene text ships the plain-ELF EBOOT with ADV_CODE and the save titles (D12); EBOOT=True patches the
    titles even without scene text. Otherwise the disc's encrypted EBOOT.BIN is kept."""
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
    if any(ed[k] for k in ('INST', 'NOINST')):   # English somewhere: proportional ASCII in the game font
        import vwf
        ed['NOINST']['font/font17.fnt'] = vwf.font17()
    # horizontal ADV needs the code patch, so the EBOOT ships as a plain ELF and its save titles come along (D12)
    horizontal = any(k.startswith('scene/script/') for k in ed['INST'])
    if horizontal or (eboot and 'eboot.json' in texts):
        ed['iso']['/PSP_GAME/SYSDIR/EBOOT.BIN'] = _eboot_patch(texts.get('eboot.json', {}), horizontal)
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


def _eboot_patch(texts, code=False):
    """The EBOOT is a plain ELF patched in place: string slots, plus ADV_CODE words (same size, no code moves, so the
    debug addresses in docs/re/debug.md stay valid)."""
    with open(EBOOT, 'rb') as f:
        eboot = f.read()
    got = bytearray(uitable.write_eboot(eboot, texts) if texts else eboot)
    for va, old, new in ADV_CODE if code else ():
        o = va - ELF_BASE
        assert int.from_bytes(got[o:o + 4], 'little') == old, f'EBOOT word at {va:#x} is not the expected original'
        got[o:o + 4] = new.to_bytes(4, 'little')
    assert len(got) == len(eboot)
    return bytes(got)


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
