"""batches.py: translation batches for agents (docs/translator-brief.md).

    python -X utf8 tools/batches.py split [--chars 3500] [--max 150]   new work/tl/bNNN.tsv (+ .terms.txt) for every
                                                                       untranslated entry not already in a batch
    python -X utf8 tools/batches.py check bNNN [bNNN..]                validate work/tl/bNNN.out.tsv; prints OK
    python -X utf8 tools/batches.py merge bNNN [bNNN..]                check, then write the English into script/
    python -X utf8 tools/batches.py fit "English text"                 the wrapped ADV box and each line's px
    python -X utf8 tools/batches.py pairs bNNN [bNNN..]                reviewer pairs file work/tl/<first>-<last>.pairs.txt

Batch TSV: id, speaker, form, limit, jp (` / ` = the game's \\n). Speaker is a guess (`ryoma?` = the last character
sprite the script changed before the line); `-` when unknown. Dialogue English is written as one paragraph per box:
merge wraps it with vwf.wrap (ADV_LINE_PX) into at most vwf.ADV_LINES lines; an explicit `\\n` in the English forces a
break. Fixed slots (UI tables) are limited in bytes, NUL included (`39b` = 39 bytes of text).
Not batched here: lyric fragments (play/), the staff roll and the speaker table (done separately).
"""
import argparse, glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mzscript, vwf
from textfmt import read_json, write_json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPT = os.path.join(ROOT, 'script')
TL = os.path.join(ROOT, 'work', 'tl')
GLOSSARY = os.path.join(ROOT, 'glossary.md')
CODE = re.compile(r'\\(?:fnt|col|sbl)\d+|%[0-9]*[dsx]')
HONORIFICS = {'さん': '-san', 'くん': '-kun', '君': '-kun', 'ちゃん': '-chan', '様': '-sama', 'さま': '-sama', '殿': '-dono', '先生': '-sensei'}
FORMS = {'dialogue': 'dlg', 'choice': 'choice', 'line': 'dlg'}


def story_files():
    """Scene scripts in story order, then the UI tables."""
    sc = sorted(glob.glob(os.path.join(SCRIPT, 'scene', '*.json')))
    key = lambda p: ('OP_m_b_ED_'.find(os.path.basename(p)[:2]), os.path.basename(p))
    sc = [p for p in sc if not os.path.basename(p).startswith(('_', 'staffroll'))]
    return sorted(sc, key=key) + sorted(glob.glob(os.path.join(SCRIPT, 'ui', '*.json'))) + \
        [os.path.join(SCRIPT, 'eboot.json'), os.path.join(SCRIPT, 'param_sfo.json')]


def speakers(rel):
    """{slot off: 'name?'} for one scene script: the last chr_NN_<name> sprite op 0x5e loaded before the line."""
    stem = os.path.basename(rel)[:-5]
    path = os.path.join(ROOT, 'work', 'cpk', 'INST', 'scene', 'script', stem + '.bin')
    if not os.path.exists(path):
        return {}
    out, cur = {}, '-'
    for ins in mzscript.parse(open(path, 'rb').read(), 'scene').instrs:
        if ins.op == 0x5e:
            for t in ins.tokens:
                m = re.search(r'chr_\d+_([a-z]+)', getattr(t, 'text', '') or '')
                if m:
                    cur = m.group(1) + '?'
        for s in ins.slots:
            out[s.off] = cur
    return out


def limit(e, fmt):
    if fmt == 'mz-scene' and e['kind'] in ('dialogue', 'choice'):
        return '%dpx' % vwf.ADV_LINE_PX
    return '%db' % (e['max'] - 1)


def glossary():
    """[(jp, en, avoid list)] from every table row of glossary.md."""
    rows = []
    for line in open(GLOSSARY, encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 2 and line.startswith('|') and c[0] not in ('JP', '') and not set(c[0]) <= set('-'):
            rows.append((c[0], c[1], [a.strip() for a in (c[4] if len(c) > 4 else '').split(',') if a.strip()]))
    return rows


def has_term(jp, term):
    """Whole-run match: the term is not part of a longer kana/kanji run of the same script class."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        before, after = jp[a - 1:a], jp[b:b + 1]
        cls = lambda ch: 'k' if '\u30a0' <= ch <= '\u30ff' else 'h' if '\u3040' <= ch <= '\u309f' else 'x'
        if cls(term[0]) in 'kh' and before and cls(before) == cls(term[0]):
            continue
        if cls(term[-1]) in 'kh' and after and cls(after) == cls(term[-1]) and cls(term[-1]) == 'k':
            continue
        return True
    return False


def read_tsv(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\r\n')
        if line:
            rows.append(line.split('\t'))
    return rows


def entries():
    """id -> (rel, entry, fmt, speaker) for every batchable entry, in story order."""
    out = {}
    for p in story_files():
        if not os.path.exists(p):
            continue
        doc = read_json(p)
        rel = os.path.relpath(p, SCRIPT).replace('\\', '/')
        sp = speakers(rel) if rel.startswith('scene/') else {}
        for e in doc['entries']:
            if not e['jp'].strip() or e['kind'] in ('staff', 'speaker'):
                continue
            out[e['id']] = (rel, e, doc['format'], sp.get(e['off'], '-'))
    return out


def split(chars, most):
    os.makedirs(TL, exist_ok=True)
    done = set()
    nums = [0]
    for p in glob.glob(os.path.join(TL, 'b[0-9][0-9][0-9].tsv')):
        nums.append(int(os.path.basename(p)[1:4]))
        done |= {r[0] for r in read_tsv(p)}
    gl = glossary()
    todo = [(i, v) for i, v in entries().items() if i not in done and not v[1].get('en')]
    n, cur, size = max(nums), [], 0

    def flush():
        nonlocal n, cur, size
        if not cur:
            return
        n += 1
        b = 'b%03d' % n
        with open(os.path.join(TL, b + '.tsv'), 'x', encoding='utf-8', newline='\n') as f:
            for i, (rel, e, fmt, sp) in cur:
                jp = e['jp'].replace('\\n', ' / ').replace('\n', ' / ').replace('\t', ' ')
                f.write('\t'.join([i, sp, FORMS.get(e['kind'], e['kind']), limit(e, fmt), jp]) + '\n')
        write_terms(b, ''.join(e['jp'] for _, (_, e, _, _) in cur), gl)
        cur, size = [], 0

    last_rel = None
    for i, v in todo:
        if cur and (size + len(v[1]['jp']) > chars or len(cur) >= most or (v[0].startswith('ui/') and v[0] != last_rel)):
            flush()
        cur.append((i, v)); size += len(v[1]['jp']); last_rel = v[0]
    flush()
    print(f'{len(todo)} entries -> batches up to b{n:03d}')


def write_terms(b, text, gl):
    with open(os.path.join(TL, b + '.terms.txt'), 'w', encoding='utf-8', newline='\n') as f:
        for jp, en, avoid in gl:
            if has_term(text, jp):
                f.write(f'{jp}\t{en}' + (f'\tavoid: {", ".join(avoid)}' if avoid else '') + '\n')


def refresh_terms():
    """Rewrite every batch's terms list from the current glossary (after merging NEW TERMs between waves)."""
    gl = glossary()
    for p in sorted(glob.glob(os.path.join(TL, 'b[0-9][0-9][0-9].tsv'))):
        write_terms(os.path.basename(p)[:-4], ''.join(r[4] for r in read_tsv(p)), gl)


def wrap_dialogue(en):
    lines = []
    for para in en.split('\\n'):
        lines += vwf.wrap(para.strip()) or ['']
    return lines


def term_problems(jp, en, gl, room=None):
    """Glossary problems for one JP/EN pair. room = byte slot size: a full name longer than it may shrink to one word."""
    probs, masked = [], jp  # longest term first; a term inside a longer matched one (慶喜 in 徳川慶喜) is not asked again
    for tjp, ten, avoid in sorted(gl, key=lambda t: -len(t[0])):
        for a in avoid:
            if re.search(r'\b%s\b' % re.escape(a), en):
                probs.append(f'"{a}" is in the glossary Avoid column for {tjp}')
        if not ten or not has_term(masked, tjp):
            continue
        # name + honorific -> "Given-san" replaces the full name; lowercase EN = common noun, no honorific form
        hon = [h for h in HONORIFICS if ten[0].isupper() and tjp + h in masked]
        for h in hon:  # given or family name: Ii says "Sakamoto-dono"
            need = [w + HONORIFICS[h] for w in ten.split()]
            if not any(n.lower() in en.lower() for n in need):
                probs.append(f'{tjp}{h} needs "{need[0]}" (honorifics kept, D1)')
        short = room is not None and len(ten) > room and any(w.lower() in en.lower() for w in ten.split())
        if not hon and not short and ten.lower() not in en.lower():
            probs.append(f'glossary {tjp} -> "{ten}" missing')
        masked = masked.replace(tjp, '\0' * len(tjp))
    return probs


def check(b, ents=None, gl=None):
    """-> list of problems for batch b (empty = OK)."""
    ents = ents or entries()
    gl = gl if gl is not None else glossary()
    src = read_tsv(os.path.join(TL, b + '.tsv'))
    path = os.path.join(TL, b + '.out.tsv')
    if not os.path.exists(path):
        return [f'{b}: no {os.path.relpath(path, ROOT)}']
    out = read_tsv(path)
    probs = []
    ids = [r[0] for r in src]
    got = [r[0] for r in out]
    if got != ids:
        miss, extra = set(ids) - set(got), set(got) - set(ids)
        probs.append(f'{b}: id list differs from the input (missing {sorted(miss)[:5]}, extra {sorted(extra)[:5]}, '
                     f'or order/duplicates)')
    chars = {r[0]: r for r in out}
    for i in ids:
        if i not in chars:
            continue
        r = chars[i]
        if len(r) != 2:
            probs.append(f'{i}: expected 2 tab-separated fields, got {len(r)}'); continue
        en = r[1]
        rel, e, fmt, _ = ents[i]
        jp = e['jp']
        if not en.strip():
            probs.append(f'{i}: empty English')
        bad = sorted({c for c in en if not (' ' <= c <= '~')})
        if bad or '\\u' in en:
            probs.append(f'{i}: non-ASCII {bad}')
        if sorted(CODE.findall(jp)) != sorted(CODE.findall(en)):
            probs.append(f'{i}: control codes {sorted(CODE.findall(jp))} in JP, {sorted(CODE.findall(en))} in EN')
        if fmt == 'mz-scene' and e['kind'] in ('dialogue', 'choice'):
            lines = wrap_dialogue(CODE.sub('', en))
            wide = [ln for ln in lines if vwf.line_px(ln) > vwf.ADV_LINE_PX]
            if wide:
                probs.append(f'{i}: a word wider than the box: {wide[0]!r}')
            if len(lines) > vwf.ADV_LINES:
                probs.append(f'{i}: {len(lines)} lines in the box, max {vwf.ADV_LINES} (python -X utf8 tools/batches.py fit "...")')
        else:
            n = len(en.replace('\\n', '\n').encode('cp932' if e.get('encoding', 'cp932') != 'utf-8' else 'utf-8'))
            if n > e['max'] - 1:
                probs.append(f'{i}: {n} bytes, max {e["max"] - 1}')
        room = None if fmt == 'mz-scene' and e['kind'] in ('dialogue', 'choice') else e.get('max', 0) - 1
        probs += [f'{i}: {p}' for p in term_problems(jp, en, gl, room)]
        if re.search(r'\]\s?(st|nd|rd|th)\b', en):
            probs.append(f'{i}: ordinal suffix glued to a code')
    return probs


def merge(batches):
    ents, gl = entries(), glossary()
    bad = [p for b in batches for p in check(b, ents, gl)]
    if bad:
        print('\n'.join(bad)); sys.exit('merge refused: fix the batches first')
    by_file = {}
    for b in batches:
        for i, en in read_tsv(os.path.join(TL, b + '.out.tsv')):
            rel, e, fmt, _ = ents[i]
            if fmt == 'mz-scene' and e['kind'] in ('dialogue', 'choice'):
                en = '\\n'.join(wrap_dialogue(en))
            by_file.setdefault(rel, {})[i] = en
    for rel, t in by_file.items():
        path = os.path.join(SCRIPT, rel)
        doc = read_json(path)
        for e in doc['entries']:
            if e['id'] in t:
                e['en'] = t[e['id']]
        write_json(path, doc)
    print(f'merged {sum(len(t) for t in by_file.values())} entries into {len(by_file)} files')


def pairs(batches_, out):
    """Reviewer input: `>> id | speaker | JP` / `EN` (wrapped as the game shows it) for every entry, story order."""
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        for b in batches_:
            en = dict((r[0], r[1]) for r in read_tsv(os.path.join(TL, b + '.out.tsv')) if len(r) == 2)
            for r in read_tsv(os.path.join(TL, b + '.tsv')):
                e = en.get(r[0], '(missing)')
                if r[3].endswith('px'):
                    e = ' / '.join(wrap_dialogue(e))
                f.write(f'>> {r[0]} | {r[1]} | {r[4]}\n   {e}\n')
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['split', 'check', 'merge', 'fit', 'pairs', 'terms'])
    ap.add_argument('args', nargs='*')
    ap.add_argument('--chars', type=int, default=3500)
    ap.add_argument('--max', type=int, default=150)
    a = ap.parse_args()
    if a.cmd == 'split':
        split(a.chars, a.max)
    elif a.cmd == 'check':
        ents, gl = entries(), glossary()
        bad = [p for b in a.args for p in check(b, ents, gl)]
        print('\n'.join(bad) if bad else 'OK')
        sys.exit(1 if bad else 0)
    elif a.cmd == 'merge':
        merge(a.args)
    elif a.cmd == 'terms':
        refresh_terms()
    elif a.cmd == 'pairs':
        pairs(a.args, os.path.join(TL, '%s-%s.pairs.txt' % (a.args[0], a.args[-1])))
    else:
        for ln in wrap_dialogue(' '.join(a.args)):
            print('%4d px  %s' % (vwf.line_px(ln), ln))


if __name__ == '__main__':
    main()
