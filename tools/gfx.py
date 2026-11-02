"""gfx.py: graphics text. gfx/<key>.png (the English image, same size as the GIM) is encoded into the original GIM and
written to every copy of it (work/gim/index.tsv `copy_keys`); build.edits() merges edits() into the plan.

    python -X utf8 tools/gfx.py gen [GLOB]          # render gfx/text.tsv rows into gfx/<key>.png
    python -X utf8 tools/gfx.py show OUT.png GLOB   # original | English, zoom 1, for the eye

gfx/text.tsv: key, style, en, opts. `en` uses \\n for a line break. Styles are in STYLES below. opts (space separated):
  box=x,y,w,h   draw into this rect (default: the original's opaque bbox, widened to the canvas on its open side)
  clear=x,y,w,h make this rect transparent first (repeatable; default: the whole image is redrawn from blank)
  keep          start from the original image instead of blank (use with clear= / inpaint=)
  inpaint=x,y,w,h  remove light lettering over art in that rect (typeset.inpaint)
  rot=90|270    render horizontally, then rotate (vertical strips)
  align=l|c|r valign=t|m|b size=N font=FILE fill=RRGGBB
Keys are `work/gim/<key>.gim` (tools/gimsweep.py); the survey with every key is docs/re/graphics-survey.tsv."""
import fnmatch, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.environ.setdefault('TYPESET_FONTS', os.path.join(ROOT, 'fonts'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gim

GFX = os.path.join(ROOT, 'gfx')
GIM = os.path.join(ROOT, 'work', 'gim')
CPK = os.path.join(ROOT, 'work', 'cpk')
TSV = os.path.join(GFX, 'text.tsv')

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
# one font and look per label class (graphics.md: Lettering)
STYLES = {
    'menu': dict(font_name='Anton-Regular.ttf', stroke=(2, BLACK)),            # white heavy menu labels, black edge
    'small': dict(font_name='Anton-Regular.ttf', stroke=(1, BLACK)),           # small hint labels (決定, 戻る)
    'title': dict(font_name='PT_Serif-Web-Bold.ttf', stroke=(2, BLACK), align='c'),     # chapter cards, serif like the Mincho
    'sfx': dict(font_name='Bangers-Regular.ttf', auto=True, maxsize=110),      # manga sound effects
    'banner': dict(font_name='Anton-Regular.ttf', stroke=(2, BLACK)),
    'notice': dict(font_name='Anton-Regular.ttf', fill=(40, 16, 24, 255), align='c'),   # dark text on a light bar
    'soul': dict(font_name='Anton-Regular.ttf', align='c', maxsize=64),                 # glowing rhythm-game soul words (glow=)
    'body': dict(font_name='PT_Serif-Web-Bold.ttf', fill=(20, 20, 20, 255), align='l'),   # tutorial/manual body text
    'plain': dict(font_name='ArchivoBlack-Regular.ttf'),
}


def index():
    """key -> copy keys, from work/gim/index.tsv."""
    out = {}
    with open(os.path.join(GIM, 'index.tsv'), encoding='utf-8') as f:
        next(f)
        for line in f:
            c = line.rstrip('\n').split('\t')
            out[c[1]] = c[6].split()
    return out


def load(key):
    """-> (gim bytes, Img, PIL RGBA) of the original."""
    from PIL import Image
    with open(os.path.join(GIM, key + '.gim'), 'rb') as f:
        d = f.read()
    im = gim.parse(d)[0]
    w, h, rows = gim.to_rgba(d, im)
    return d, im, Image.frombytes('RGBA', (w, h), b''.join(rows))


def pngs():
    """Every gfx/<key>.png -> key."""
    out = []
    for dp, _, fs in os.walk(GFX):
        out += [os.path.relpath(os.path.join(dp, f), GFX).replace('\\', '/')[:-4] for f in fs if f.endswith('.png')]
    return sorted(out)


def encode(key):
    """The English PNG as GIM bytes (same length as the original)."""
    from PIL import Image
    d, im, orig = load(key)
    new = Image.open(os.path.join(GFX, key + '.png')).convert('RGBA')
    assert new.size == orig.size, f'{key}: {new.size} != {orig.size}'
    rows = [new.tobytes()[y * 4 * new.width:(y + 1) * 4 * new.width] for y in range(new.height)]
    out = gim.encode(d, im, rows)
    assert len(out) == len(d)
    return out


def edits():
    """-> {CPK: {'dir/name': bytes}}: each file that holds a replaced GIM, with every copy patched."""
    idx, files = index(), {}
    for key in pngs():
        g = encode(key)
        for ck in idx[key]:
            path, off = ck.rsplit('_', 1)
            if path not in files:
                with open(os.path.join(CPK, *path.split('/')), 'rb') as f:
                    files[path] = bytearray(f.read())
            o = int(off, 16)
            assert files[path][o:o + 11] == b'MIG.00.1PSP', ck
            files[path][o:o + len(g)] = g
    ed = {'INST': {}, 'NOINST': {}}
    for path, data in files.items():
        cpk, rel = path.split('/', 1)
        ed[cpk][rel] = bytes(data)
    return ed


def rows():
    """gfx/text.tsv -> [(key, style, en, {opt: value})]."""
    out = []
    with open(TSV, encoding='utf-8') as f:
        for line in f:
            if not line.strip() or line.startswith('#') or line.startswith('key\t'):
                continue
            c = line.rstrip('\n').split('\t') + ['', '']
            opts = {}
            for o in c[3].split():
                k, _, v = o.partition('=')
                opts.setdefault(k, []).append(v)
            out.append((c[0], c[1], c[2].replace('\\n', '\n'), opts))
    return out


def _rect(v):
    return tuple(int(x) for x in v.split(','))


def render(key, style, en, opts, base=None):
    """-> PIL RGBA, the English image for one text.tsv row (BASE: the previous row's image of the same key)."""
    import typeset
    from PIL import Image
    orig = page(key[5:])[0] if key.startswith('PAGE:') else load(key)[2]
    w, h = orig.size
    img = base.copy() if base else orig.copy() if 'keep' in opts else Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for v in opts.get('smear', []):   # text on horizontal stripes: repeat a clean column across the rect
        x, y, bw, bh, sx = _rect(v)
        col = img.crop((sx, y, sx + 1, y + bh))
        for cx in range(x, x + bw):
            img.paste(col, (cx, y))
    for v in opts.get('inpaint', []):
        x, y, bw, bh = _rect(v)
        img = typeset.inpaint(img, (x, y, x + bw, y + bh))
    for v in opts.get('erase', []):   # text on a flat or horizontal-gradient box: per column, blend the rows around it
        x, y, bw, bh = _rect(v)
        px = img.load()
        for cx in range(x, x + bw):
            a, b = px[cx, max(y - 1, 0)], px[cx, min(y + bh, h - 1)]
            for k in range(bh):
                t = (k + 1) / (bh + 1)
                px[cx, y + k] = tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(4))
    for v in opts.get('flat', []):   # text on a flat colour: fill the rect with its most common colour
        x, y, bw, bh = _rect(v)
        from collections import Counter
        c = Counter(img.crop((x, y, x + bw, y + bh)).getdata()).most_common(1)[0][0]
        img.paste(c, (x, y, x + bw, y + bh))
    for v in opts.get('clear', []):
        x, y, bw, bh = _rect(v)
        img.paste((0, 0, 0, 0), (x, y, x + bw, y + bh))
    rot = int(opts.get('rot', ['0'])[0])
    st = dict(STYLES[style])
    if st.pop('auto', False):   # SFX: dark lettering with a white edge, or white with a black edge, like the original
        core = [p for p in orig.getdata() if p[3] > 200]
        dark = core and sum(sum(p[:3]) for p in core) / len(core) < 300
        st['fill'], st['stroke'] = ((24, 28, 28, 255), (3, WHITE)) if dark else (WHITE, (3, BLACK))
        x0, y0, x1, y1 = orig.getbbox() or (0, 0, w, h)
        if not rot and len(en) > 2 and y1 - y0 > 1.6 * (x1 - x0):   # vertical lettering: run the word down the strip
            rot = 270
    if 'font' in opts:
        st['font_name'] = opts['font'][0]
    if 'stroke' in opts:   # stroke=W,RRGGBB (W=0: none)
        sw, _, c = opts['stroke'][0].partition(',')
        st['stroke'] = (int(sw), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)) if int(sw) else None
    if 'fill' in opts:
        c = opts['fill'][0]
        st['fill'] = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    if 'size' in opts:
        st['size'] = int(opts['size'][0])
    if 'maxsize' in opts:   # cap: keeps a run of tiles (one word split over several) the same letter size
        st['maxsize'] = int(opts['maxsize'][0])
    if 'box' in opts:
        box = _rect(opts['box'][0])
    else:   # the original lettering's bbox, widened to the canvas edge on the side it is not anchored to
        x0, y0, x1, y1 = orig.getbbox() or (0, 0, w, h)
        if rot:
            box = (x0, 0, x1 - x0, h)
        else:   # the ink fit (fit()) makes the English as tall as the original lettering
            bh = y1 - y0
            box = (0, y0, w, bh) if x0 <= 4 and x1 >= w - 4 else (x0, y0, w - x0, bh) if x0 <= w - x1 else (0, y0, x1, bh)
            box = (box[0], max(box[1] - 1, 0), box[2], min(box[3] + 2, h))
    align = opts.get('align', [st.pop('align', None)])[0]
    st.pop('align', None)
    if align is None:   # follow the original: centred, or anchored to the nearer edge
        x0, _, x1, _ = orig.getbbox() or (0, 0, w, h)
        align = 'c' if 'box' in opts or rot or abs(x0 - (w - x1)) <= 6 else ('l' if x0 < w - x1 else 'r')
    valign = opts.get('valign', ['m'])[0]
    bx, by, bw, bh = box
    glow = opts.get('glow', [None])[0]
    if glow:   # neon lettering: the original halo's colour (auto) as the stroke and a blurred glow around it
        if glow == 'auto':
            from collections import Counter
            c = Counter(p[:3] for p in orig.getdata() if 40 < p[3] < 220 and max(p[:3]) - min(p[:3]) > 40)
            glow = '%02x%02x%02x' % (c.most_common(1)[0][0] if c else (255, 255, 255))
        gc = tuple(int(glow[i:i + 2], 16) for i in (0, 2, 4))
        st['stroke'] = (3, gc + (255,))
        bw, bh, bx, by = bw - 16, bh - 16, bx + 8, by + 8   # room for the halo
    if rot:   # lay the text out along the strip, then turn it
        bw, bh = bh, bw
    ink = fit(en, bw, bh, align, **st)
    if rot:
        ink = ink.rotate(rot, expand=True)
        bw, bh = bh, bw
    x = bx + {'l': 1, 'c': (bw - ink.width) // 2, 'r': bw - ink.width - 1}[align if not rot else 'c']
    y = by + {'t': 1, 'm': (bh - ink.height) // 2, 'b': bh - ink.height - 1}[valign if not rot else 'm']
    if glow:
        from PIL import ImageFilter
        a = Image.new('L', img.size, 0)
        a.paste(ink.split()[3], (max(x, 0), max(y, 0)))
        a = a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(5))
        halo = Image.new('RGBA', img.size, gc + (0,))
        halo.putalpha(a.point(lambda v: min(255, v * 2)))
        img.alpha_composite(halo)
    img.alpha_composite(ink, (max(x, 0), max(y, 0)))
    return img


def fit(text, bw, bh, align='c', size=None, maxsize=None, **st):
    """The text's ink (cropped to its drawn pixels) at the largest size whose ink fits bw-2 x bh-2. Fitting the ink,
    not the font's line box, keeps Latin caps as tall as the kanji they replace."""
    import typeset
    def ink(s):
        c = typeset.text_image(bw * 4 + 64, bh * 4 + 64, text, size=s, align=align, **st)
        return c.crop(c.getbbox() or (0, 0, 1, 1))
    if size:
        return ink(size)
    s = min(int(bh * 1.6) + 2, maxsize or 999)
    while s > 6:
        i = ink(s)
        if i.width <= bw - 2 and i.height <= bh - 2:
            return i
        s -= 1 if s < 40 else 2
    return ink(6)


def page(path):
    """PAGE:<file> keys: a picture the game cuts into 32-px-wide vertical strips (every 32x256 GIM in <file>, in file
    order, left to right) -> (whole page RGBA, [strip keys])."""
    from PIL import Image
    keys = sorted((k for k in index() if k.rsplit('_', 1)[0] == path), key=lambda k: int(k.rsplit('_', 1)[1], 16))
    keys = [k for k in keys if load(k)[2].size == (32, 256)]
    pg = Image.new('RGBA', (32 * len(keys), 256), (0, 0, 0, 0))
    for i, k in enumerate(keys):
        pg.paste(load(k)[2], (32 * i, 0))
    return pg, keys


def gen(pattern='*'):
    done = {}   # a key on several rows: each row draws onto the previous one (several labels in one image)
    for key, style, en, opts in rows():
        if not fnmatch.fnmatch(key, pattern):
            continue
        done[key] = render(key, style, en, opts, done.get(key))
    for key in [k for k in done if k.startswith('PAGE:')]:   # cut a page back into its strips (changed ones only)
        img = done.pop(key)
        for i, k in enumerate(page(key[5:])[1]):
            strip = img.crop((32 * i, 0, 32 * i + 32, 256))
            if strip.tobytes() != load(k)[2].tobytes():
                done[k] = strip
    for key, img in done.items():
        out = os.path.join(GFX, key + '.png')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        img.save(out)
    print(f'gfx: {len(done)} image(s) rendered')


def show(out, pattern):
    from PIL import Image, ImageDraw
    cells = []
    for key in pngs():
        if fnmatch.fnmatch(key, pattern):
            o = load(key)[2]
            n = Image.open(os.path.join(GFX, key + '.png')).convert('RGBA')
            c = Image.new('RGBA', (o.width * 2 + 6, o.height + 12), (70, 70, 110, 255))
            c.alpha_composite(o, (0, 12)); c.alpha_composite(n, (o.width + 6, 12))
            ImageDraw.Draw(c).text((1, 0), key.split('/')[-1], fill=(255, 255, 0, 255))
            cells.append(c)
    if not cells:
        sys.exit('no match')
    cw = max(c.width for c in cells) + 4
    cols = max(1, 1600 // cw)
    hs = [max(c.height for c in cells[i:i + cols]) + 4 for i in range(0, len(cells), cols)]
    sheet = Image.new('RGB', (cw * min(cols, len(cells)), sum(hs)), (20, 20, 20))
    y = 0
    for r, i in enumerate(range(0, len(cells), cols)):
        for k, c in enumerate(cells[i:i + cols]):
            sheet.paste(c.convert('RGB'), (k * cw, y))
        y += hs[r]
    sheet.save(out)
    print(len(cells), 'images ->', out)


def info(pattern):
    """Size, opaque bbox and the bbox of each main colour (to find text rects for box=/erase=)."""
    from collections import Counter
    idx = index()
    for key in sorted(idx):
        if not fnmatch.fnmatch(key, pattern):
            continue
        img = load(key)[2]
        px = img.load()
        q = Counter()
        boxes = {}
        for y in range(img.height):
            for x in range(img.width):
                p = px[x, y]
                if p[3] < 128:
                    continue
                c = tuple(v // 64 * 64 for v in p[:3])
                q[c] += 1
                b = boxes.get(c, [x, y, x, y])
                boxes[c] = [min(b[0], x), min(b[1], y), max(b[2], x), max(b[3], y)]
        print(f'{key} {img.size} bbox={img.getbbox()}')
        for c, n in q.most_common(6):
            x0, y0, x1, y1 = boxes[c]
            print(f'   colour~{c} n={n} rect={x0},{y0},{x1 - x0 + 1},{y1 - y0 + 1}')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'info':
        info(a[1])
    elif a and a[0] == 'gen':
        gen(a[1] if len(a) > 1 else '*')
    elif a and a[0] == 'show' and len(a) == 3:
        show(a[1], a[2])
    else:
        sys.exit(__doc__)
