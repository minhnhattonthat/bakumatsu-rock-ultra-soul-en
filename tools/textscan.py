"""Every text record the game can show, read back from a built ISO, as one cp932 blob for jp_left.py.

    python -X utf8 tools/textscan.py [ISO] [--out work/qa/text.bin]
    python -X utf8 "$(python tools/skill.py)/scripts/jp_left.py" work/qa/text.bin --sjis --halfwidth --kanji-runs --min 1

Scene scripts, UI tables (systemdata), EBOOT text slots, the SFO title. play/ lyric charts are left out (D13)."""
import argparse, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpk, isodiff, iso9660, mzscript, uitable
from crilayla import decompress, is_crilayla


def records(image):
    out = []
    with open(image, 'rb') as f:
        files = {p: (lba, size) for p, lba, size, _ in iso9660.listing(f)}
        for name in ('INST', 'NOINST'):
            lba, _ = files[f'/PSP_GAME/USRDIR/{name}.CPK']
            _, _, entries = cpk.parse(isodiff._head(f, lba), isodiff.Sub(f, lba * 2048))
            for e in entries:
                if e.dir not in ('scene/script', 'systemdata'):
                    continue
                data = isodiff._raw(f, lba, e)
                data = decompress(data) if is_crilayla(data) else data
                slots = mzscript.parse(data, 'scene').text_slots if e.dir == 'scene/script' else uitable.slots(data, e.name)
                out.extend((f'{name}/{e.dir}/{e.name}', s.off, s.text) for s in slots)
        lba, size = files['/PSP_GAME/SYSDIR/EBOOT.BIN']
        f.seek(lba * 2048)
        out.extend(('EBOOT', s.off, s.text) for s in uitable.eboot_slots(f.read(size)))
        lba, size = files['/PSP_GAME/PARAM.SFO']
        f.seek(lba * 2048)
        s = uitable.sfo_title(f.read(size))
        out.append(('PARAM.SFO', s.off, s.text))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso', nargs='?', default=os.path.join(ROOT, 'build', 'bakumatsu_rock_us_en.iso'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'work', 'qa', 'text.bin'))
    a = ap.parse_args()
    recs = records(a.iso)
    with open(a.out, 'wb') as f:
        f.write(b'\0'.join(t.encode('cp932') for _, _, t in recs))
    print(f'{len(recs)} text records -> {a.out}')


if __name__ == '__main__':
    main()
