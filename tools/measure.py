"""measure.py: find text runs in a shot (white text or dark text) and report extents / advance widths.

    python -X utf8 tools/measure.py SHOT --rect X,Y,W,H [--dark] [--rows]
"""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from skill import SKILL
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import sheet as S


def text_mask(rows, w, bpp, rect, dark):
    x, y, rw, rh = rect
    out = []
    for yy in range(y, min(y + rh, len(rows))):
        line = rows[yy]
        m = []
        for xx in range(x, min(x + rw, w)):
            p = line[xx * bpp:xx * bpp + 3]
            lo, hi = min(p), max(p)
            m.append((hi < 90) if dark else (lo > 150 and hi - lo < 70))
        out.append(m)
    return out


def report(mask, x0):
    """-> list of (y, first_x, last_x, ncols) for each run of rows that has text."""
    runs = []
    cur = None
    for i, m in enumerate(mask):
        cols = [j for j, v in enumerate(m) if v]
        if cols:
            if cur is None:
                cur = [i, i, min(cols), max(cols)]
            else:
                cur[1] = i
                cur[2] = min(cur[2], min(cols))
                cur[3] = max(cur[3], max(cols))
        elif cur is not None:
            runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    return [(x0 + r[2], x0 + r[3], r[3] - r[2] + 1, r[1] - r[0] + 1) for r in runs]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('shot')
    ap.add_argument('--rect', required=True, help='x,y,w,h')
    ap.add_argument('--dark', action='store_true', help='dark text on a light background')
    ap.add_argument('--min-cols', type=int, default=8)
    a = ap.parse_args()
    w, h, bpp, rows = S.read_png(a.shot)
    rect = tuple(int(v) for v in a.rect.split(','))
    mask = text_mask(rows, w, bpp, rect, a.dark)
    runs = [r for r in report(mask, rect[0]) if r[2] >= a.min_cols]
    print(f'{os.path.basename(a.shot)} {w}x{h} rect {rect}: {len(runs)} text run(s)')
    for first, last, width, height in runs:
        print(f'  x {first}..{last}  width {width}px  height {height}px')


if __name__ == '__main__':
    main()
