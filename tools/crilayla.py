"""CRI CRILAYLA decompressor (CPK per-file compression).
usage: crilayla.py IN OUT
Layout: 'CRILAYLA' | u32 LE uncompressed size (minus 0x100 header) | u32 LE compressed size | bitstream (read
backwards from its end) | 0x100 bytes stored raw = the first 0x100 bytes of the output.
No compressor: cpk.rebuild stores replaced files uncompressed (FileSize == ExtractSize), which CPK readers accept."""
import struct, sys

VLE = (2, 3, 5, 8)


def is_crilayla(b): return b[:8] == b'CRILAYLA'


def decompress(src):
    usize, csize = struct.unpack_from('<II', src, 8)
    out = bytearray(usize + 0x100)
    out[:0x100] = src[0x10 + csize:0x10 + csize + 0x100]
    pos = 0x10 + csize - 1          # next input byte (stream runs backwards)
    pool = 0; nbits = 0
    end = 0x100 + usize - 1         # output is also written backwards
    done = 0

    def bits(n):
        nonlocal pool, nbits, pos
        while nbits < n:
            pool = (pool << 8) | src[pos]; pos -= 1; nbits += 8
        nbits -= n
        v = (pool >> nbits) & ((1 << n) - 1)
        pool &= (1 << nbits) - 1
        return v

    while done < usize:
        if bits(1):
            ref = end - done + bits(13) + 3
            ln = 3
            for w in VLE:
                v = bits(w); ln += v
                if v != (1 << w) - 1: break
            else:
                while True:
                    v = bits(8); ln += v
                    if v != 255: break
            for _ in range(ln):
                out[end - done] = out[ref]; ref -= 1; done += 1
        else:
            out[end - done] = bits(8); done += 1
    return bytes(out)


if __name__ == '__main__':
    open(sys.argv[2], 'wb').write(decompress(open(sys.argv[1], 'rb').read()))
