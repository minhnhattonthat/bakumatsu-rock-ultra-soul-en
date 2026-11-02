"""Find strings the EBOOT code builds with byte stores of immediates (sb of addiu/ori zero,imm) and decode as cp932."""
import re, struct, sys
d = open(sys.argv[1], 'rb').read()
BASE = 0x08804000 - 0xc0
regs, mem, last = {}, {}, {}
hits = []
def flush():
    for base, bs in mem.items():
        offs = sorted(bs)
        run = []
        for o in offs + [None]:
            if run and (o is None or o != run[-1] + 1):
                b = bytes(bs[x][0] for x in run)
                s = b.split(b'\0')[0]
                try:
                    t = s.decode('cp932')
                except Exception:
                    t = ''
                if re.search(r'[぀-ヿ一-鿿！-～]', t):
                    hits.append((bs[run[0]][1], base, run[0], t))
                run = []
            if o is not None:
                run.append(o)
    mem.clear(); regs.clear()
for o in range(0, len(d) - 4, 4):
    w = struct.unpack_from('<I', d, o)[0]
    op, rs, rt, imm = w >> 26, w >> 21 & 31, w >> 16 & 31, w & 0xffff
    if w == 0x03e00008:   # jr ra: function end
        flush(); continue
    if op == 0x09 and rs == 0:
        regs[rt] = imm & 0xff if imm < 0x8000 else (imm - 0x10000) & 0xff
    elif op == 0x0d and rs == 0:
        regs[rt] = imm & 0xff if imm < 0x100 else None
    elif op == 0x28 and rt in regs and regs[rt] is not None:
        off = imm if imm < 0x8000 else imm - 0x10000
        mem.setdefault(rs, {})[off] = (regs[rt], BASE + o)
    elif op == 0x28 and rt == 0:
        off = imm if imm < 0x8000 else imm - 0x10000
        mem.setdefault(rs, {})[off] = (0, BASE + o)
    elif rt in regs and op not in (0x28, 0x29, 0x2b, 0x04, 0x05):
        regs.pop(rt, None)
for va, base, off, t in hits:
    print('%08x r%d+%#x %s' % (va, base, off, t))
