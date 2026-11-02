"""vwf.py: proportional English glyphs for the game font (font17.fnt), rendered from an open-licence TTF.

    python -X utf8 tools/vwf.py preview OUT.png [--text "..."]   glyph strip + a sample line, 4x
    python -X utf8 tools/vwf.py widths                            the advance table (px) the width lint uses

The game font is monospace for ASCII (every glyph 8 px, ink filling the cell). The engine takes each glyph's advance
from byte 0 of its 8-byte header (docs/re/text.md §8), so a proportional font is a data edit: re-render printable
ASCII (0x21-0x7e; backslash too, it shows as ¥ in the original and is the control-code escape in scripts) into the
17x17 cell at 2 bpp, set byte 0 to the advance, and re-encode the font with kfnt.py. Space keeps its own width.
The advance includes the 1 px gap between letters (the ADV boxes' own glyph gap is set to 0 by insert.py, so menus,
back log and dialogue space letters the same way).

Font: fonts/PT_Serif-Web-Regular.ttf (OFL 1.1, docs/fonts.md), chosen to sit next to the game's Mincho kana/kanji.
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kfnt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TTF = os.path.join(ROOT, 'fonts', 'PT_Serif-Web-Regular.ttf')
SIZE = 12          # px em size: ~6 px per lowercase letter, ~20 per ADV line (11 and 13 tried)
BASELINE = 13      # cell row of the baseline (descenders use rows 14-16)
SPACE = 4          # advance of ' '
GAP = 1            # px after each glyph, part of the advance
BEARING = 2        # header byte 4 (horizontal x offset of the drawing, not the advance) = a 2 px left margin per line
DROP = 4           # header byte 5 (horizontal y offset): line 1 clears the panel's top border
LEVELS = (40, 110, 190)   # 8-bit coverage thresholds for 2-bpp levels 1, 2, 3
CHARS = [chr(c) for c in range(0x21, 0x7f)]


def render(ch, f):
    """-> (advance, rows[17][17] of 0..3)."""
    W = 17
    im = Image.new('L', (W * 2, 17), 0)
    d = ImageDraw.Draw(im)
    asc = f.getmetrics()[0]
    left = f.getbbox(ch)[0]
    x0 = max(0, -left)            # keep a negative left bearing inside the cell
    d.text((x0, BASELINE - asc + 1), ch, font=f, fill=255)
    px = im.load()
    cols = [x for x in range(W * 2) if any(px[x, y] >= LEVELS[0] for y in range(17))]
    if not cols:
        return SPACE, [[0] * W for _ in range(17)]
    x_first = cols[0]
    ink = cols[-1] - x_first + 1
    rows = []
    for y in range(17):
        row = []
        for x in range(W):
            v = px[x + x_first, y] if x + x_first < W * 2 else 0
            row.append(sum(v >= t for t in LEVELS))
        rows.append(row)
    adv = min(W, ink + GAP)
    return adv, rows


def glyphs():
    f = ImageFont.truetype(TTF, SIZE)
    out = {' ': (SPACE, [[0] * 17 for _ in range(17)])}
    for ch in CHARS:
        out[ch] = render(ch, f)
    return out


def widths():
    return {ch: g[0] for ch, g in glyphs().items()}


# Width gate for ADV speech boxes (docs/re/text.md §8), measured in game on every panel variant with the engine's
# centring patch (insert.ADV_CODE): the canvas wraps at 128 px; rounded panels hold 12 lines x 120 px, but the octagon
# (thought) and spiky (shout) panels clip lines past ~112 px and blocks past 8 lines at insert.ADV_PITCH.
ADV_LINE_PX = 112
ADV_LINES = 8


def line_px(line, w=None):
    """Pixel width of one line of script text (control codes like \\fnt1 take no space)."""
    import re
    w = w or widths()
    line = re.sub(r'\\(fnt|col)\d|\\sbl\d+', '', line)
    return sum(w.get(c, 17) for c in line)   # full-width / unknown = the 17 px cell


def wrap(text, px=ADV_LINE_PX, w=None):
    """Greedy word wrap to PX -> list of lines (a word longer than PX gets its own line)."""
    w = w or widths()
    lines, cur = [], ''
    for word in text.split(' '):
        t = word if not cur else cur + ' ' + word
        if line_px(t, w) <= px or not cur:
            cur = t
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines


def font17(data=None):
    """-> font17.fnt bytes with the proportional ASCII glyphs."""
    data = data or kfnt.load('font17.fnt')
    fnt = kfnt.Font(data)
    for ch, (adv, rows) in glyphs().items():
        hd, _ = fnt.glyph(ord(ch))
        hd[0] = adv
        hd[4], hd[5] = BEARING, DROP
        fnt.set_glyph(ord(ch), hd, rows)
    return fnt.encode()


def preview(out, text):
    g = glyphs()
    z = 4
    strip_w = sum(a for a, _ in g.values()) + 4
    line_w = sum(g.get(c, g['?'])[0] for c in text) + 4
    im = Image.new('RGB', (max(strip_w, line_w) * z, 40 * z), (240, 236, 222))
    px = im.load()
    shade = {1: (170, 165, 150), 2: (100, 95, 85), 3: (20, 20, 20)}

    def put(x0, y0, rows):
        for y, row in enumerate(rows):
            for x, v in enumerate(row):
                if v:
                    for dy in range(z):
                        for dx in range(z):
                            px[(x0 + x) * z + dx, (y0 + y) * z + dy] = shade[v]
    x = 2
    for ch, (a, rows) in g.items():
        put(x, 2, rows); x += a
    x = 2
    for c in text:
        a, rows = g.get(c, g['?']); put(x, 21, rows); x += a
    im.save(out)
    print(out, 'line', line_w - 4, 'px')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['preview', 'widths'])
    ap.add_argument('out', nargs='?')
    ap.add_argument('--text', default="Ryoma: Kyoto's so lively! Way more than Tosa.")
    a = ap.parse_args()
    if a.cmd == 'preview':
        preview(a.out, a.text)
    else:
        print(' '.join(f'{c}{w}' for c, w in widths().items()))


if __name__ == '__main__':
    main()
