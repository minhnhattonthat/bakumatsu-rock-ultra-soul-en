"""mips.py: static look at the relocated EBOOT code (RAM addresses), for engine RE.

    python -X utf8 tools/debug/mips.py dis ADDR [N]     disassemble N instructions from ADDR (default 40)
    python -X utf8 tools/debug/mips.py func ADDR        whole function containing ADDR (prologue scan back, to jr ra)
    python -X utf8 tools/debug/mips.py callers ADDR     every jal to ADDR (or to the function containing it with -f)
    python -X utf8 tools/debug/mips.py refs VALUE       lui/addiu|ori pairs and words that build VALUE

Code image: work/dump/code.bin = RAM 0x08804000.. as loaded (relocated, so jal/lui targets are real addresses);
falls back to work/eboot/EBOOT.ELF segment 0 (unrelocated, file offset 0xC0) if the dump is missing.
"""
import os, struct, sys
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = 0x08804000
_p = os.path.join(ROOT, 'work', 'dump', 'code.bin')
CODE = open(_p, 'rb').read() if os.path.exists(_p) else open(os.path.join(ROOT, 'work', 'eboot', 'EBOOT.ELF'), 'rb').read()[0xC0:0xC0 + 2944940]
MD = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)


def word(a):
    return struct.unpack_from('<I', CODE, a - BASE)[0]


def dis(a, n=40, out=print):
    for i in MD.disasm(CODE[a - BASE:a - BASE + n * 4], a):
        out('%08x  %08x  %-8s %s' % (i.address, word(i.address), i.mnemonic, i.op_str))


def func_start(a):
    """Scan back for 'addiu sp, sp, -X' (0x27bdXXXX, negative)."""
    a &= ~3
    while a > BASE:
        w = word(a)
        if w >> 16 == 0x27bd and w & 0x8000:
            return a
        a -= 4
    return BASE


def func_end(a):
    while a - BASE < len(CODE):
        if word(a) == 0x03e00008:  # jr ra
            return a + 8
        a += 4
    return a


def callers(t):
    j = 0x0c000000 | ((t >> 2) & 0x03ffffff)
    return [BASE + o for o in range(0, len(CODE) - 3, 4) if struct.unpack_from('<I', CODE, o)[0] == j]


def refs(v):
    hi, lo = (v + 0x8000) >> 16 & 0xffff, v & 0xffff
    out = []
    for o in range(0, len(CODE) - 3, 4):
        w = struct.unpack_from('<I', CODE, o)[0]
        if w == v:
            out.append((BASE + o, 'word'))
        if w >> 26 == 0x0f and w & 0xffff in (hi, v >> 16):  # lui
            rt = w >> 16 & 31
            for k in range(1, 17):
                if o + 4 * k + 4 > len(CODE):
                    break
                w2 = struct.unpack_from('<I', CODE, o + 4 * k)[0]
                if (w2 >> 21 & 31) == rt and w2 & 0xffff == lo and w2 >> 26 in (0x09, 0x0d, 0x20, 0x21, 0x23, 0x24,
                                                                              0x25, 0x28, 0x29, 0x2b, 0x31, 0x39):
                    out.append((BASE + o, 'lui+%d' % k))
                    break
    return out


def main(a):
    cmd, x = a[0], int(a[1], 16)
    if cmd == 'dis':
        dis(x, int(a[2]) if len(a) > 2 else 40)
    elif cmd == 'func':
        s = func_start(x)
        dis(s, (func_end(s) - s) // 4)
    elif cmd == 'callers':
        if '-f' in a:
            x = func_start(x)
        for c in callers(x):
            print('%08x  in %08x' % (c, func_start(c)))
    elif cmd == 'refs':
        for r, k in refs(x):
            print('%08x  %s  in %08x' % (r, k, func_start(r)))


if __name__ == '__main__':
    main(sys.argv[1:])
