"""PPSSPP debugger helpers on top of the skill's psp.py (QA fork headless + WebSocket API): play a route with
exec-breakpoint hooks, read/write RAM, dump user RAM.

    python -X utf8 tools/debug/pspdbg.py dump --state work/states/X.ppst --frames 60 --out work/dump/X.ram [--shot S.png]
    python -X utf8 tools/debug/pspdbg.py dump --route tools/routes/menu.txt --out work/dump/menu.ram

User RAM 0x08800000..0x0A000000 (24 MB) is written raw to OUT (offset 0 = 0x08800000)."""
import argparse, base64, json, os, shutil, struct, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from skill import SKILL  # noqa: E402
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import psp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ISO = os.path.join(ROOT, 'rom', 'Bakumatsu Rock - Ultra Soul (Japan).iso')
RAM, RAM_SIZE = 0x08800000, 0x01800000


class _Json:
    """psp.WS.recv json-decodes raw bytes; the game's own debug printf (Shift-JIS) arrives as 'log' events that are
    not UTF-8 and crashed the decode. Decode leniently instead."""
    @staticmethod
    def loads(b):
        s = b.decode('utf-8', 'replace') if isinstance(b, (bytes, bytearray)) else b
        try:
            return json.loads(s)
        except json.JSONDecodeError:   # empty / non-JSON frame (seen in the rhythm game): surface it, don't crash
            return {'event': '_raw', 'data': s[:200]}
    dumps = staticmethod(json.dumps)


psp.json = _Json


def start(iso=ISO, out=None, state=None):
    """A Run stopped at frame 0 with a fresh memstick in OUT/memstick."""
    out = out or os.path.join(ROOT, 'work', 'qa', 'dbg')
    shutil.rmtree(os.path.join(out, 'memstick'), ignore_errors=True)
    return psp.Run(psp.find_emu(None), iso, out, state)


def u32(run, addr):
    return struct.unpack('<I', run.ws.mem(addr, 4))[0]


def reg(run, name):
    return run.ws.call('cpu.getReg', category=0, name=name)['uintValue']


def cstr(run, addr, n=64):
    b = run.ws.mem(addr, n)
    return b.split(b'\0')[0].decode('cp932', 'replace')


def read(run, addr, size):
    out = bytearray()
    while size:
        n = min(size, 0x100000)
        out += run.ws.mem(addr, n); addr += n; size -= n
    return bytes(out)


def write(run, addr, data):
    run.ws.call('memory.write', address=addr, base64=base64.b64encode(bytes(data)).decode())


def dump(run, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, 'wb').write(read(run, RAM, RAM_SIZE))


def run_until(run, frame, hooks=None):
    """Run to FRAME (relative to run.base). HOOKS: {pc: fn(run)}; each is an exec breakpoint, fn runs when hit (CPU
    stopped there) and returns True to remove the breakpoint. Execution resumes at the hit pc."""
    hooks = hooks or {}
    target = run.base + round(frame * psp.FRAME_US)
    ws = run.ws
    while True:
        st = ws.call('cpu.status')
        if st['us'] >= target - 100: return
        ws.call('cpu.runUntilTime', us=target)
        while True:
            ev = ws.wait('cpu.stepping')
            st = ws.call('cpu.status')
            if os.environ.get('PSPDBG_TRACE'): print('trace', target, ev, st, flush=True)
            if 'exception' in ev.get('reason', ''):   # the game crashed: the CPU stays stopped, never reaches target
                raise RuntimeError(f'emulator stopped: {ev["reason"]} at pc {st["pc"]:#x}')
            if st['pc'] in hooks or st['us'] >= target - 100: break
        pc = st['pc']
        if pc in hooks and st['us'] < target - 100:
            if hooks[pc](run):
                ws.call('cpu.breakpoint.remove', address=pc); del hooks[pc]
            else:   # step over the breakpoint: remove, single-step, re-add
                ws.call('cpu.breakpoint.remove', address=pc)
                # cpu.stepInto answers with a cpu.stepping event, not a ticketed reply
                ws.ticket += 1
                ws._send(1, json.dumps(dict(event='cpu.stepInto', ticket=ws.ticket)).encode()); ws.wait('cpu.stepping')
                ws.call('cpu.breakpoint.add', address=pc)


def add_hooks(run, hooks):
    for pc in hooks: run.ws.call('cpu.breakpoint.add', address=pc)


def play(run, route_text, shots=(), hooks=None, shot_prefix='f'):
    """Play a route (psp.py format) from the run's current frame; shots are frame numbers relative to the route
    start, saved as OUT/<prefix><frame>.png. Returns the end frame (relative to run.base)."""
    hooks = hooks if hooks is not None else {}
    add_hooks(run, hooks)
    f0 = run.frame()
    steps = psp.parse_route(route_text)
    n = sum(k for k, _ in steps)
    for f, shoot, keys in psp.plan(steps, n, set(shots)):
        run_until(run, f0 + f, hooks)
        if shoot: run.shot(f'{shot_prefix}{f:06d}.png')
        run.press(keys)
    for pc in list(hooks): run.ws.call('cpu.breakpoint.remove', address=pc)
    return f0 + n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['dump'])
    ap.add_argument('--iso', default=ISO); ap.add_argument('--state'); ap.add_argument('--route'); ap.add_argument('--route-str')
    ap.add_argument('--frames', type=int, default=0); ap.add_argument('--out', required=True)
    ap.add_argument('--shot')
    a = ap.parse_args()
    run = start(a.iso, os.path.join(ROOT, 'work', 'qa', 'dbg_' + os.path.basename(a.out)), a.state)
    try:
        r = open(a.route).read() if a.route else (a.route_str or '')
        if a.frames: r += f'\n{a.frames} -'
        if r.strip(): play(run, r)
        dump(run, a.out)
        if a.shot: run.shot(os.path.abspath(a.shot))
        print('dumped', a.out, 'frame', run.frame())
    finally:
        run.close()


if __name__ == '__main__':
    main()
