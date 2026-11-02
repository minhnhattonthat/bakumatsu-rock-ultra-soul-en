"""Find every GIM in work/cpk (loose .gim files and GIMs embedded in .d2c/.eff/... containers), dedupe by md5,
write work/gim/<cpk>/<path>_<hexoff>.gim for the first copy of each, work/gim/index.tsv (one row per unique image:
md5, key, w, h, fmt, copies, all copy keys) and labelled contact sheets work/gimsheets/<group>_NNN.png.
usage: gimsweep.py [--no-sheets]
Key format matches showgim.py: ID = <cpk>/<dir>/<file>_<hexoff> (offset of the GIM inside the unpacked file)."""
import hashlib, os, struct, sys, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill import SCRIPTS
sys.path.insert(0, SCRIPTS)
import gim

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MAGIC = b'MIG.00.1PSP\0'


def find_gims(b):
    p = b.find(MAGIC)
    while p >= 0:
        size = 16 + struct.unpack_from('<I', b, p + 0x14)[0]
        yield p, b[p:p + size]
        p = b.find(MAGIC, p + size)


def sweep():
    uniq = collections.OrderedDict()
    skipped = []
    base = os.path.join(ROOT, 'work', 'cpk')
    for path in sorted(glob.glob(os.path.join(base, '**', '*'), recursive=True)):
        if os.path.isdir(path) or path.endswith(('.acb', '.awb', '.pmf', '.bin', '.fnt')): continue
        rel = os.path.relpath(path, base).replace('\\', '/')
        b = open(path, 'rb').read()
        n = 0
        for off, g in find_gims(b):
            n += 1
            key = f'{rel}_{off:x}'
            h = hashlib.md5(g).hexdigest()
            if h in uniq: uniq[h]['copies'].append(key); continue
            try:
                im = gim.parse(g)[0]; info = (im.w, im.h, gim.FMT.get(im.fmt, im.fmt))
            except Exception as e:
                skipped.append((key, f'parse: {e}')); continue
            out = os.path.join(ROOT, 'work', 'gim', key + '.gim')
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, 'wb').write(g)
            uniq[h] = dict(key=key, info=info, copies=[key])
        if n == 0 and not path.endswith(('.cnz', '.msk', '.PNG')):
            skipped.append((rel, 'no GIM inside'))
    with open(os.path.join(ROOT, 'work', 'gim', 'index.tsv'), 'w', encoding='utf-8') as f:
        f.write('md5\tkey\tw\th\tfmt\tcopies\tcopy_keys\n')
        for h, u in uniq.items():
            w, hh, fmt = u['info']
            f.write(f"{h}\t{u['key']}\t{w}\t{hh}\t{fmt}\t{len(u['copies'])}\t{' '.join(u['copies'])}\n")
    for k, why in skipped: print('skipped', k, why)
    print(len(uniq), 'unique GIMs,', sum(len(u['copies']) for u in uniq.values()), 'copies')
    return uniq


def sheets(uniq, per=30, width=1600):
    from PIL import Image, ImageDraw
    groups = collections.defaultdict(list)
    for u in uniq.values():
        k = u['key']; name = k.split('/')[-1]
        groups[name.split('_')[0].split('.')[0].rstrip('0123456789') or 'misc'].append(k)
    od = os.path.join(ROOT, 'work', 'gimsheets'); os.makedirs(od, exist_ok=True)
    for g, keys in sorted(groups.items()):
        for s in range(0, len(keys), per):
            cells = []
            for k in keys[s:s + per]:
                d = open(os.path.join(ROOT, 'work', 'gim', k + '.gim'), 'rb').read()
                try:
                    w, h, rows = gim.to_rgba(d, gim.parse(d)[0])
                    im = Image.frombytes('RGBA', (w, h), b''.join(rows))
                except Exception as e:
                    print('render failed', k, e); continue
                im.thumbnail((380, 300))
                cells.append((k, im))
            # simple row packing
            x = y = rowh = 0; pos = []
            for k, im in cells:
                cw, ch = max(im.width, 120), im.height + 14
                if x + cw > width: x = 0; y += rowh + 6; rowh = 0
                pos.append((x, y, k, im)); x += cw + 6; rowh = max(rowh, ch)
            sheet = Image.new('RGBA', (width, y + rowh + 6), (60, 60, 90, 255))
            dr = ImageDraw.Draw(sheet)
            name = f'{g}_{s // per:03d}'
            with open(os.path.join(od, name + '.tsv'), 'w', encoding='utf-8') as idx:
                for n, (x, y, k, im) in enumerate(pos):
                    bg = Image.new('RGBA', im.size, (128, 128, 128, 255)); bg.alpha_composite(im)
                    sheet.paste(bg, (x, y + 14)); dr.text((x, y), f'#{n} {k.split("/")[-1][-26:]}', fill=(255, 255, 0, 255))
                    idx.write(f'{n}\t{k}\n')
            sheet.convert('RGB').save(os.path.join(od, name + '.png'))


if __name__ == '__main__':
    u = sweep()
    if '--no-sheets' not in sys.argv: sheets(u)
