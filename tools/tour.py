"""tour.py: collect the warp tour's contact sheets into one dir for the visual-QA gate.

    python -X utf8 tools/debug/warp.py --all --sheet --iso build/bakumatsu_rock_us_en.iso   (warp's default = the JP ROM)
    python -X utf8 tools/tour.py [--dest work/qa/tour]
    python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/manifest.tsv work/qa/tour

warp/<scene>/sheet.png, sheet_2.png.. -> DEST/<scene>_sheet.png, <scene>_sheet_2.png..: every page, so no frame
escapes review (pages older than the scene's sheet.png are a stale earlier run and skipped). A scene too short for
any periodic shot (menu_top) gives its final.png as <scene>_sheet.png.
"""
import argparse, glob, os, re, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WARP = os.path.join(ROOT, 'work', 'qa', 'warp')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dest', default=os.path.join(ROOT, 'work', 'qa', 'tour'))
    a = ap.parse_args()
    os.makedirs(a.dest, exist_ok=True)
    n = 0
    for d in sorted(glob.glob(os.path.join(WARP, '*', 'seq.txt'))):
        d = os.path.dirname(d); scene = os.path.basename(d)
        first = os.path.join(d, 'sheet.png')
        if not os.path.exists(first) or os.path.getmtime(first) < os.path.getmtime(os.path.join(d, 'seq.txt')):
            first = os.path.join(d, 'final.png')   # no shots this run: sheet.py wrote nothing
            pages = [first] if os.path.exists(first) else []
        else:
            pages = [first] + sorted((p for p in glob.glob(os.path.join(d, 'sheet_*.png'))
                                      if re.fullmatch(r'sheet_\d+\.png', os.path.basename(p))
                                      and os.path.getmtime(p) >= os.path.getmtime(first)),
                                     key=lambda p: int(re.findall(r'\d+', os.path.basename(p))[0]))
        for k, p in enumerate(pages):
            shutil.copyfile(p, os.path.join(a.dest, f'{scene}_sheet' + (f'_{k + 1}' if k else '') + '.png'))
            n += 1
    print(f'{n} sheets -> {a.dest}')


if __name__ == '__main__':
    main()
