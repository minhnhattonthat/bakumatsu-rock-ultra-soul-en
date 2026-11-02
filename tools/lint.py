"""lint.py: text lint over every script/*.json entry (phase 7 fit check; tools/check.py runs it).

    python -X utf8 tools/lint.py [--dir script] [--all]

Errors (exit 1): Japanese with no English unless keep-listed (script/keep_jp.txt: `id-or-prefix*<TAB>reason`),
non-ASCII or leftover Japanese in English, control codes JP != EN, ADV dialogue/choice lines wider than
vwf.ADV_LINE_PX or more than vwf.ADV_LINES (the engine char-wraps otherwise, which breaks centring), fixed-slot text
over its byte budget (NUL included), glossary misses/Avoid spellings, an ordinal glued to a code, leading/trailing
blanks the JP lacks, and a one-word last line (< STUB chars) under a longer dialogue paragraph.
Prints the first 40 errors (--all: every one) and a count.
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vwf
from batches import CODE, glossary, term_problems
from textfmt import read_json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT = os.path.join(ROOT, 'script')
JP = re.compile(r'[぀-ヿ㐀-鿿！-｠]')
STUB = 6


def keep_list(directory):
    path = os.path.join(directory, 'keep_jp.txt')
    if not os.path.exists(path):
        return []
    return [ln.split('\t')[0].strip() for ln in open(path, encoding='utf-8') if ln.strip() and not ln.startswith('#')]


def kept(key, keep):
    return any(key.startswith(k[:-1]) if k.endswith('*') else key == k for k in keep)


def entry_problems(rel, fmt, e, gl):
    jp, en = e['jp'], e.get('en') or ''
    adv = fmt == 'mz-scene' and e['kind'] in ('dialogue', 'choice')
    p = []
    bad = sorted({c for c in en if not (' ' <= c <= '~' or (c == '\n' and e['kind'] == 'staff'))})
    if bad:
        p.append(f'non-ASCII {bad}' + (' (Japanese left)' if any(JP.match(c) for c in bad) else ''))
    if sorted(CODE.findall(jp)) != sorted(CODE.findall(en)):
        p.append(f'control codes {sorted(CODE.findall(jp))} in JP, {sorted(CODE.findall(en))} in EN')
    if adv:
        lines = CODE.sub('', en).split('\\n')
        wide = [ln for ln in lines if vwf.line_px(ln) > vwf.ADV_LINE_PX]
        if wide:
            p.append(f'{vwf.line_px(wide[0])} px > {vwf.ADV_LINE_PX}: {wide[0]!r}')
        if len(lines) > vwf.ADV_LINES:
            p.append(f'{len(lines)} lines > {vwf.ADV_LINES}')
        if len(lines) > 1 and len(lines[-1].strip()) < STUB and len(lines[-2]) > 3 * STUB and '\\n' not in jp:
            p.append(f'stub last line {lines[-1]!r}')
    elif fmt != 'mz-scene':   # scene/play slots resize; UI tables, EBOOT and SFO slots don't
        n = len(en.encode('utf-8' if e.get('encoding') == 'utf-8' or fmt == 'utf-8-slots' else 'cp932', 'replace'))
        if n > e['max'] - 1:
            p.append(f'{n} bytes > {e["max"] - 1}')
    room = None if adv else e.get('max', 0) - 1
    # terms are matched on the text as read: a wrap break or a colour code may sit inside one ("Heaven's\nSong")
    p += term_problems(jp, CODE.sub('', en.replace('\\n', ' ').replace('\n', ' ')), gl, room)
    if re.search(r'(\\\w+\d|%[0-9]*[dsx])\s?(st|nd|rd|th)\b', en):
        p.append('ordinal suffix glued to a code')
    multi = re.search(r'\\n|\n', jp)   # multi-line UI text pads its rows to centre them, as the JP rows do
    if en[:1].isspace() and not jp[:1].isspace() and not multi:
        p.append('leading blank the JP lacks')
    if en[-1:].isspace() and not jp[-1:].isspace():
        p.append('trailing blank the JP lacks')
    return p


def lint(directory=SCRIPT):
    """-> [(id, problem)] over every entry of every text file in DIRECTORY."""
    gl, keep, out = glossary(), keep_list(directory), []
    for base, _, files in os.walk(directory):
        for fn in sorted(files):
            if not fn.endswith('.json'):
                continue
            rel = os.path.relpath(os.path.join(base, fn), directory).replace('\\', '/')
            doc = read_json(os.path.join(base, fn))
            for e in doc['entries']:
                if not e['jp'].strip():
                    continue
                if not (e.get('en') or '').strip():
                    if not (kept(e['id'], keep) or kept(rel, keep)):
                        out.append((e['id'], 'Japanese with no English (keep_jp.txt lists intended ones)'))
                    continue
                out += [(e['id'], p) for p in entry_problems(rel, doc['format'], e, gl)]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dir', default=SCRIPT)
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    probs = lint(a.dir)
    for i, p in probs if a.all else probs[:40]:
        print(f'{i}: {p}')
    print(f'lint: {len(probs)} error(s)' if probs else 'lint: OK')
    sys.exit(1 if probs else 0)


if __name__ == '__main__':
    main()
