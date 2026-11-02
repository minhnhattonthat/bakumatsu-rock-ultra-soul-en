"""textprobe.py: locate the ADV text layout in the EBOOT by diffing RAM across a line change, then watch writes.

    python -X utf8 tools/debug/textprobe.py diff   [--state work/states/warp/m_001001.ppst] [--iso ISO]
    python -X utf8 tools/debug/textprobe.py watch  [--addr 0x95ea410] [--size 0x500] [--hits 10]

Why it exists (docs/re/text.md §7): read breakpoints on the dialogue string or the KBTF font are useless - the ADV line
is parsed once into a display structure and the renderer then works from that. So: dump user RAM, advance one line,
dump again, cluster the differences (the ADV background is static, so the parsed line stands out), then set a *write*
breakpoint on the buffer and log the pcs that fill it. `watch` prints the top writers disassembled.

Addresses are stable across runs started from the cached MENU state, so `watch --addr` can reuse a buffer found by an
earlier `diff`. Facts as of phase 5: four 0x500-byte column buffers start at 0x95ea410; the writers are 0x088f7040
(per-column copy loop) and 0x08945fb4..0x08946024 (u16 copy), both calling the memcpy stub at 0x259e80.
"""
import argparse, base64, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pspdbg as D  # noqa: E402
import psp as P     # noqa: E402
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN  # noqa: E402

ELF = open(os.path.join(D.ROOT, 'work', 'eboot', 'EBOOT.ELF'), 'rb').read()
TEXTOFF, BASE = 0xC0, 0x08804000
MD = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
MENU_STATE = os.path.join(D.ROOT, 'work', 'states', 'warp', '_menu_Bakumatsu_Rock_-_Ultra_Soul_(Japan).ppst')
SCRIPT_STATE = os.path.join(D.ROOT, 'work', 'states', 'warp', 'm_001001.ppst')


def dis(pc, n=14):
    off = pc - BASE + TEXTOFF
    if off < n * 4:
        return ''
    return '\n'.join('%08x  %-8s %s' % (i.address, i.mnemonic, i.op_str)
                     for i in MD.disasm(ELF[off - n * 4:off + n * 4], pc - n * 4))


def clusters(a, b, minlen=0x100, maxlen=8000):
    out, i = [], 0
    while i < len(a):
        if a[i] == b[i]:
            i += 1
            continue
        j, last = i, i
        while j < len(a) and j - last < 64:
            if a[j] != b[j]:
                last = j
            j += 1
        if minlen <= last + 1 - i <= maxlen:
            out.append((i, last + 1 - i))
        i = last + 1
    return out


def step_over(ws):
    ws.ticket += 1
    ws._send(1, json.dumps(dict(event='cpu.stepInto', ticket=ws.ticket)).encode())
    ws.wait('cpu.stepping')


def run_to(run, frame, on_write=None, limit=None):
    ws = run.ws
    target = run.base + round(frame * P.FRAME_US)
    while True:
        st = ws.call('cpu.status')
        if st['us'] >= target - 100:
            return
        ws.call('cpu.runUntilTime', us=target)
        try:
            ev = ws.wait('cpu.stepping')
        except TimeoutError:
            return
        st = ws.call('cpu.status')
        if ev.get('reason') != 'memory.breakpoint' or st['us'] >= target - 100:
            continue
        pc = st['pc']
        if on_write:
            on_write(pc)
            if limit and on_write.hits > limit:
                return
        ws.call('memory.breakpoint.remove', address=on_write.addr, size=on_write.size, type='write')
        step_over(ws)
        ws.call('memory.breakpoint.add', address=on_write.addr, size=on_write.size, type='write')


def line_change(run, state):
    """Advance one dialogue line (press circle, hold 4 frames, release, run 80)."""
    f = run.frame()
    run.press('circle'); run_to(run, f + 4); run.press('')
    run_to(run, f + 80)


def cmd_diff(run):
    run_to(run, 20)
    a = D.read(run, D.RAM, D.RAM_SIZE)
    line_change(run, None)
    b = D.read(run, D.RAM, D.RAM_SIZE)
    run.shot('line2.png')
    cl = clusters(a, b)
    cl.sort(key=lambda t: -t[1])
    print(f'{len(cl)} changed block(s) of 0x100..8000 bytes; largest:')
    for off, size in cl[:10]:
        print('  %08x  %5d bytes  %s' % (D.RAM + off, size, b[off:off + 32].hex(' ')))
    return cl


def cmd_watch(run, addr, size, hits):
    counts = collections.Counter()

    def on_write(pc):
        counts[pc] += 1
        on_write.hits += 1

    on_write.hits = 0
    on_write.addr, on_write.size = addr, size
    run_to(run, 20)
    run.ws.call('memory.breakpoint.add', address=addr, size=size, type='write')
    line_change(run, None)
    print(f'{on_write.hits} write(s) to {addr:#x}+{size:#x}')
    for pc, n in counts.most_common(hits):
        print('--- %x  %d hit(s)' % (pc, n))
        print(dis(pc))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['diff', 'watch'])
    ap.add_argument('--state', default=SCRIPT_STATE)
    ap.add_argument('--iso', default=D.ISO)
    ap.add_argument('--addr', default='0x95ea410')
    ap.add_argument('--size', default='0x500')
    ap.add_argument('--hits', type=int, default=8)
    a = ap.parse_args()
    run = D.start(a.iso, os.path.join(D.ROOT, 'work', 'qa', 'dbg_textprobe'), a.state)
    try:
        if a.cmd == 'diff':
            cmd_diff(run)
        else:
            cmd_watch(run, int(a.addr, 0), int(a.size, 0), a.hits)
    finally:
        run.close()


if __name__ == '__main__':
    main()
