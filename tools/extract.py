"""extract.py: unpacked game data -> script/*.json (the repo's text format), and back.

    python -X utf8 tools/extract.py dump [--force]     write script/ from work/cpk (+ work/eboot/EBOOT.ELF)
    python -X utf8 tools/extract.py verify             roundtrip + coverage checks (also run by pytest)

Text files hold one entry per text slot: id (stable, file + hex offset), off, max (slot bytes), kind, jp (original,
decoded cp932) and en (empty until phase 6). Engine strings (asset paths, thread names) are not dumped: they are
classified as data by the parsers and only enter the roundtrip check.

dump never overwrites an existing file unless --force; with --force it keeps every non-empty `en` by id.
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import mzscript, uitable
from textfmt import decode, is_japanese, japanese_runs, read_json, write_json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CPK = os.path.join(ROOT, 'work', 'cpk')
EBOOT = os.path.join(ROOT, 'work', 'eboot', 'EBOOT.ELF')
SFO = os.path.join(ROOT, 'work', 'iso', 'PSP_GAME', 'PARAM.SFO')
OUT = os.path.join(ROOT, 'script')

SCENE_DIR = os.path.join(CPK, 'INST', 'scene', 'script')
PLAY_DIR = os.path.join(CPK, 'INST', 'play', 'script')
UI_DIR = os.path.join(CPK, 'NOINST', 'systemdata')


def ui_files():
    return sorted(f for f in os.listdir(UI_DIR) if f != 'movie_list_info.mil')


def scene_scripts():
    """-> [(name, Script)] for the 80 ADV scripts."""
    out = []
    for fn in sorted(os.listdir(SCENE_DIR)):
        with open(os.path.join(SCENE_DIR, fn), 'rb') as f:
            out.append((fn, mzscript.parse(f.read(), 'scene')))
    return out


def play_scripts():
    out = []
    for fn in sorted(os.listdir(PLAY_DIR)):
        with open(os.path.join(PLAY_DIR, fn), 'rb') as f:
            out.append((fn, mzscript.parse(f.read(), 'play')))
    return out


def entry(sid, off, max_, kind, jp, **extra):
    e = {'id': sid, 'off': off, 'max': max_, 'kind': kind, 'jp': jp, 'en': ''}
    e.update(extra)
    return e


def scene_entries(name, sc, ref):
    stem = name[:-4]
    out = []
    for s in sc.slots:
        if s.kind == 'speaker':
            # only the copies that differ from the shared name table (staffroll2.bin has two)
            i = sc.table_slots.index(s)
            if s.text == ref[i].text and s.capacity == ref[i].capacity:
                continue
            out.append(entry(f'{stem}:name:{i:03d}', s.off, s.capacity, 'speaker', s.text))
            continue
        if s.kind in ('data', '') or not s.text:
            continue
        extra = {'op': f'0x{s.op:02x}'}
        if s.msg is not None:
            extra['msg'] = f'0x{s.msg:04x}'
        out.append(entry(f'{stem}:0x{s.off:x}', s.off, s.capacity, s.kind, s.text, **extra))
    return out


def speaker_ref(scripts):
    """The op-0x19 name table is identical in 79 of the 80 scene scripts; take the most common text per index.
    staffroll2.bin differs at two indices and carries those two as per-file entries instead."""
    from collections import Counter
    ref = []
    for i in range(len(scripts[0][1].table_slots)):
        votes = Counter(sc.table_slots[i].text for _, sc in scripts)
        text = votes.most_common(1)[0][0]
        for _, sc in scripts:
            if sc.table_slots[i].text == text:
                ref.append(sc.table_slots[i])
                break
    return ref


def speaker_entries(ref):
    return [entry(f'name:{i:03d}', s.off, s.capacity, 'speaker', s.text) for i, s in enumerate(ref)]


def ui_entries(name, data):
    out = []
    for s in uitable.slots(data, name):
        if not s.text:
            continue
        extra = {} if s.enc == 'cp932' else {'encoding': s.enc}
        out.append(entry(f'{name[:-4]}:0x{s.off:x}', s.off, s.capacity, s.kind, s.text, **extra))
    return out


def eboot_entries(eboot):
    return [entry(f'eboot:0x{s.off:x}', s.off, s.capacity, s.kind, s.text, encoding=s.enc)
            for s in uitable.eboot_slots(eboot)]


def sfo_entries(sfo):
    off, cap = uitable.SFO_TITLE
    text = sfo[off:off + cap].rstrip(b'\0').decode('utf-8')
    return [entry('param_sfo:title', off, cap, 'title', text, encoding='utf-8')]


def expected_files():
    """-> {relative json path: (source name, entries builder)}"""
    files = {}
    scripts = scene_scripts()
    ref = speaker_ref(scripts)
    files['scene/_speaker_names.json'] = ('speaker names', lambda: speaker_entries(ref))
    for name, sc in scripts:
        files[f'scene/{name[:-4]}.json'] = (name, lambda name=name, sc=sc: scene_entries(name, sc, ref))
    for name, sc in play_scripts():
        def build(name=name, sc=sc):
            return [entry(f'{name[:-4]}:0x{s.off:x}', s.off, s.capacity, s.kind, s.text,
                          op=f'0x{s.op:02x}') for s in sc.slots if s.kind == 'lyric' and s.text]
        files[f'play/{name[:-4]}.json'] = (name, build)
    for name in ui_files():
        with open(os.path.join(UI_DIR, name), 'rb') as f:
            data = f.read()
        files[f'ui/{name[:name.index(".")]}.json'] = (name, lambda data=data, name=name: ui_entries(name, data))
    with open(EBOOT, 'rb') as f:
        eboot = f.read()
    files['eboot.json'] = ('EBOOT.ELF', lambda: eboot_entries(eboot))
    with open(SFO, 'rb') as f:
        sfo = f.read()
    files['param_sfo.json'] = ('PARAM.SFO', lambda: sfo_entries(sfo))
    return files


def dump(force=False):
    files = expected_files()
    written = kept = 0
    for rel, (src, build) in sorted(files.items()):
        path = os.path.join(OUT, rel)
        entries = build()
        if os.path.exists(path):
            old = read_json(path)
            by_id = {e['id']: e.get('en', '') for e in old.get('entries', [])}
            for e in entries:
                e['en'] = by_id.get(e['id'], '')
            if not force:
                raise SystemExit(f'{os.path.relpath(path, ROOT)} exists: refusing to overwrite (use --force; en is kept)')
            kept += 1
        fmt = ('mz-scene' if rel.startswith('scene/') else 'mz-play' if rel.startswith('play/')
               else 'ui-table' if rel.startswith('ui/') else 'utf-8-slots')
        write_json(path, {'source': src, 'format': fmt, 'entries': entries})
        written += 1
    return written, kept


# ---- checks ---------------------------------------------------------------------------------------------------------

def check_roundtrip():
    """Every MZ file serializes back to its own bytes; every UI table slot roundtrips; every JSON jp is the slot's."""
    n = 0
    for name, sc in scene_scripts() + play_scripts():
        assert mzscript.serialize(sc) == sc.data, f'{name}: MZ roundtrip failed'
        n += 1
    for name in ui_files():
        path = os.path.join(UI_DIR, name)
        with open(path, 'rb') as f:
            data = f.read()
        slots = uitable.slots(data, name)
        patched = uitable.write_table(name, data, {s.off: s.text for s in slots})
        assert patched == data, f'{name}: UI table roundtrip failed'
        n += 1
    return n


def looks_like_text(s):
    """At least two fullwidth/kanji characters: filters halfwidth noise out of binary instruction args."""
    n = sum(1 for c in s if '぀' <= c <= 'ヿ' or '一' <= c <= '鿿' or '　' <= c <= '〿' or '！' <= c <= '｠')
    return n >= 2


def check_coverage():
    """Mask every slot in every source file, then scan the rest for Japanese text: anything left is a gap."""
    problems = []

    def scan(name, data, spans):
        masked = bytearray(data)
        for a, b in spans:
            masked[a:b] = b'\0' * (b - a)
        for off, ln, text in japanese_runs(bytes(masked)):
            if looks_like_text(text):
                problems.append(f'{name} 0x{off:x}: {text!r} outside a text slot')

    for name, sc in scene_scripts() + play_scripts():
        scan(name, sc.data, [(s.off + 4, s.off + 4 + s.capacity) for s in sc.slots if s.capacity])
    for name in ui_files():
        with open(os.path.join(UI_DIR, name), 'rb') as f:
            data = f.read()
        scan(name, data, [(s.off, s.off + s.capacity) for s in uitable.slots(data, name) if s.capacity])
    with open(EBOOT, 'rb') as f:
        eboot = f.read()
    spans = [(s.off, s.off + s.capacity) for s in uitable.eboot_slots(eboot)]
    masked = bytearray(eboot)
    for a, b in spans:
        masked[a:b] = b'\0' * (b - a)
    for lo, hi in ((0x26925C, 0x2692C8), (0x269458, 0x2694B0), (0x2694BC, 0x2694F8)):
        outside = [i for i in range(lo, hi) if masked[i] >= 0x80]
        if outside:
            problems.append(f'EBOOT: {len(outside)} high bytes outside save-title slots, first at 0x{outside[0]:x}')
    # EBOOT data sections (from 0x25A240; .text before it is code noise): a NUL-delimited Shift-JIS string with
    # kana/kanji is text. 0x2C112C: あ” in a 16-byte punctuation token table (！！, ！？, ・...), not display text.
    # Strings the code builds from immediates are insert.TEXT_CODE (found by tools/debug/sbscan.py).
    for m in re.finditer(rb'(?<=\0)(?:[\x81-\x9f\xe0-\xfc][\x40-\x7e\x80-\xfc])+(?=\0)', bytes(masked[0x25A240:])):
        off = 0x25A240 + m.start()
        try:
            text = m.group().decode('cp932')
        except UnicodeDecodeError:
            continue
        if off != 0x2C112C and len(text) >= 2 and re.search(r'[぀-ヿ一-鿿]', text):
            problems.append(f'EBOOT 0x{off:x}: {text!r} outside a text slot')
    return problems


def check_json():
    """Every dumped jp decodes back to its slot's bytes, and every text slot has an entry."""
    files = expected_files()
    problems = []
    for rel, (src, build) in files.items():
        want = {e['id']: e for e in build()}
        path = os.path.join(OUT, rel)
        if not os.path.exists(path):
            problems.append(f'{rel}: not dumped (python tools/extract.py dump)')
            continue
        got = {e['id']: e for e in read_json(path)['entries']}
        if set(want) != set(got):
            problems.append(f'{rel}: ids differ (json {len(got)}, source {len(want)})')
            continue
        for sid, e in want.items():
            if got[sid]['jp'] != e['jp']:
                problems.append(f'{rel} {sid}: jp differs from the dump')
            if got[sid]['max'] != e['max']:
                problems.append(f'{rel} {sid}: max differs')
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['dump', 'verify'])
    ap.add_argument('--force', action='store_true', help='overwrite existing files (en values are kept by id)')
    a = ap.parse_args()
    if a.command == 'dump':
        written, kept = dump(a.force)
        print(f'{written} text files in script/ ({kept} refreshed, en kept)')
    else:
        n = check_roundtrip()
        problems = check_coverage() + check_json()
        for p in problems:
            print(p)
        print(f'{n} binary files roundtrip; {len(problems)} problems')
        return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main() or 0)
