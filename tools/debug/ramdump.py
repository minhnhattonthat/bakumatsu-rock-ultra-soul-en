"""ramdump.py: dump user RAM from a savestate (after N frames), for offline pointer hunts.

    python -X utf8 tools/debug/ramdump.py STATE.ppst OUT.ram [--iso ISO] [--frames 30]

The RAM base is pspdbg.RAM (file offset 0 = that address). Used for the back-log speaker-label hunt (text.md §7):
dump the JP and the English back log, then compare the pointers into the loaded script.
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pspdbg as D  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('state'); ap.add_argument('out')
    ap.add_argument('--iso', default=D.ISO); ap.add_argument('--frames', type=int, default=30)
    a = ap.parse_args()
    run = D.start(os.path.abspath(a.iso), os.path.join(D.ROOT, 'work', 'qa', 'dbg_ramdump'), os.path.abspath(a.state))
    try:
        D.run_until(run, a.frames)
        D.dump(run, a.out)
    finally:
        run.close()
    print(f'{a.out}: 0x{D.RAM:08x} + 0x{D.RAM_SIZE:x}')


if __name__ == '__main__':
    main()
