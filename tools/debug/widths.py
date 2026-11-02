"""widths.py: read each ADV glyph's width/height from the engine itself, off the torture build.

    python -X utf8 tools/mark.py --force --torture && python -X utf8 tools/build.py --texts work/mark
    python -X utf8 tools/debug/warp.py m_001001 --state              # state at the first ADV line
    python -X utf8 tools/debug/widths.py [--state work/states/warp/m_001001.ppst] [--out tools/adv_widths.tsv]

The ADV typewriter (0x088137a0, docs/re/text.md §8) asks the font for each glyph's metrics (call to 0x08806604 at
0x088139a0); at 0x088139a8 s1 = the character code, *(u32*)*(sp+0) = its width, *(u32*)fp = its height. AUTO mode
plays the torture lines (every printable ASCII glyph, mark.py --torture), and every new code is written to OUT as
`char<TAB>code<TAB>width<TAB>height`. The advance in a box is width + the box's glyph gap (op 0x4E word 4, 1 for the
speech boxes).
"""
import argparse, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg as D

HOOK = 0x088139a8


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--iso', default=os.path.join(D.ROOT, 'build', 'bakumatsu_rock_us_en.iso'))
    ap.add_argument('--state', default=os.path.join(D.ROOT, 'work', 'states', 'warp', 'm_001001.ppst'))
    ap.add_argument('--out', default=os.path.join(D.ROOT, 'tools', 'adv_widths.tsv'))
    ap.add_argument('--frames', type=int, default=2400)
    a = ap.parse_args()
    seen = {}

    def hook(run):
        code = D.reg(run, 's1')
        if code not in seen:
            sp, fp = D.reg(run, 'sp'), D.reg(run, 'fp')
            w = D.u32(run, D.u32(run, sp))
            h = D.u32(run, fp)
            seen[code] = (w, h)
        return False

    run = D.start(a.iso, os.path.join(D.ROOT, 'work', 'qa', 'dbg_widths'), a.state)
    try:
        D.play(run, f'30 -\n6 start\n{a.frames} -', hooks={HOOK: hook}, shots=(600, a.frames))
    finally:
        run.close()
    rows = sorted(seen.items())
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# char\tcode\twidth\theight  (ADV font, read by tools/debug/widths.py; advance = width + box gap)\n')
        for code, (w, h) in rows:
            ch = chr(code) if 0x20 <= code < 0x7f else bytes([code >> 8, code & 0xff]).decode('cp932', 'replace') if code > 0xff else '?'
            f.write(f'{ch}\t{code:#06x}\t{w}\t{h}\n')
    asc = [c for c in seen if 0x20 <= c < 0x7f]
    print(f'{len(seen)} codes ({len(asc)} printable ASCII of 95) -> {a.out}')
    missing = [chr(c) for c in range(0x20, 0x7f) if c not in seen and c != 0x5c]
    if missing:
        print('ASCII not seen:', ''.join(missing))


if __name__ == '__main__':
    main()
