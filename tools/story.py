"""Story-pass chapter files: every scene line of a chapter in story order, for the read-only story reviewers.

    python -X utf8 tools/story.py [--out work/qa/story/chapters]

One file per chapter (CHAPTERS below: scene scripts in play order), lines `>> id | - | JP` then `EN`. The scripts don't
name speakers (text.md section 2), so the speaker column is `-`: reviewers infer it from context."""
import argparse, json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SCENE = os.path.join(ROOT, 'script', 'scene')


def _m(ch):
    return sorted(f[:-5] for f in os.listdir(SCENE) if f.startswith(f'm_{ch:03d}'))


def chapters():
    names = sorted(f[:-5] for f in os.listdir(SCENE) if f.endswith('.json') and not f.startswith('_'))
    b = [n for n in names if n.startswith('b_')]
    ed = [n for n in names if n.startswith('ED_')]
    out = {'00_opening_prologue': ['OP_001001', 'OP_002001']}
    out.update({f'{c:02d}_chapter{c}': _m(c) for c in range(1, 11)})
    out['11_ultra_soul_1'] = ['OP_003001'] + _m(11)
    out['12_ultra_soul_2'] = _m(12)
    out['13_ultra_soul_3'] = _m(13)
    out['14_endings_a'], out['15_endings_b'] = ed[:4], ed[4:]
    for i in range(0, len(b), 5):   # bonus stories, five scripts a file
        out[f'{16 + i // 5}_bonus_{i // 5 + 1}'] = b[i:i + 5]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=os.path.join(ROOT, 'work', 'qa', 'story', 'chapters'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    seen = set()
    for name, files in chapters().items():
        lines = []
        for fn in files:
            seen.add(fn)
            lines.append(f'### {fn}')
            for e in json.load(open(os.path.join(SCENE, fn + '.json'), encoding='utf-8'))['entries']:
                lines += [f'>> {e["id"]} | - | {e["jp"]}', e.get('en') or '']
        with open(os.path.join(a.out, name + '.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print(f'{name}: {", ".join(files)}')
    left = {f[:-5] for f in os.listdir(SCENE) if f.endswith('.json') and not f.startswith('_')} - seen
    assert left <= {'staffroll', 'staffroll2'}, left   # credits are names, reviewed in the tour


if __name__ == '__main__':
    main()
