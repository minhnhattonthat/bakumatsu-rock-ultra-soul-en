"""mark.py: write the marker text set (phase 5) into a text directory, for the marker build.

    python -X utf8 tools/mark.py [--dir work/mark] [--force]

Every entry with Japanese text gets an English marker that starts with its id:

    [m_001001:0x18d0] The quick brown fox jumps over the lazy dog. 0123456789

MZ script slots grow as needed (insert.py re-maps every jump), so they always get the full marker. Fixed slots (UI
tables, EBOOT, PARAM.SFO) and the tiny rhythm-chart lyric slots get the longest marker that still fits: `[id] fox`,
then `[id]`, then a compact tag. `jp` is never touched; the marker build reads this directory instead of script/
(`python -X utf8 tools/build.py --texts work/mark`).

Why: the marker build shows every text slot's id on screen, finds text the extractor missed (anything still Japanese)
and measures each box variant's width in game (the width gate, docs/re/text.md)."""

import argparse, os, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textfmt import read_json, write_json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT = os.path.join(ROOT, 'script')
MARK = os.path.join(ROOT, 'work', 'mark')

FULL = '[{id}] The quick brown fox jumps over the lazy dog. 0123456789 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SHORT = ['[{id}] fox', '[{id}]', '[{tag}]', '[x]', 'x']


def fits(text, cap, enc):
    try:
        return len(text.encode(enc)) <= cap
    except UnicodeEncodeError:
        return False


def marker(entry, cap, enc):
    """The longest marker that fits CAP bytes; scene slots (cap None) always get the full one.
    Everything here is ASCII, so a byte budget is a character count."""
    tag = _tag(entry['id'])
    head = '[%s] ' % entry['id']
    full = FULL.format(id=entry['id'], tag=tag)
    if cap is None:
        return full
    if fits(head, cap, enc):
        return full[:cap] if len(full) > cap else full
    for pat in SHORT:
        t = pat.format(id=entry['id'], tag=tag)
        if fits(t, cap, enc):
            return t
    t = tag
    while t and not fits(t, cap, enc):
        t = t[:-1]
    return t or '.'


def _tag(sid):
    """Compact id for a 2-3 byte slot: file prefix letter + last 3 hex digits, e.g. b123."""
    stem, _, off = sid.partition(':')
    off = off.replace('0x', '') or '0'
    return (stem[:1] + off[-3:])[:4]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', default=MARK)
    ap.add_argument('--force', action='store_true', help='overwrite a non-empty target directory')
    a = ap.parse_args()
    if os.path.isdir(a.dir) and os.listdir(a.dir) and not a.force:
        sys.exit(f'{a.dir} exists and is not empty: pass --force (a real translation set would be lost)')
    shutil.rmtree(a.dir, ignore_errors=True)
    n = 0
    for base, _, files in os.walk(SCRIPT):
        for fn in sorted(files):
            if not fn.endswith('.json'):
                continue
            src = os.path.join(base, fn)
            rel = os.path.relpath(src, SCRIPT)
            doc = read_json(src)
            for e in doc['entries']:
                enc = e.get('encoding', 'cp932')
                # only scene slots resize safely; a rhythm note's fragment is 1-6 chars of its own buffer
                cap = None if doc['format'] == 'mz-scene' else e['max']
                e['en'] = marker(e, cap, enc)
                n += 1
            write_json(os.path.join(a.dir, rel), doc)
    print(f'{n} markers written to {os.path.relpath(a.dir, ROOT)}')


if __name__ == '__main__':
    main()
