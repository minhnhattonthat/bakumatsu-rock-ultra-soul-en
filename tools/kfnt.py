"""kfnt.py: the game's KFNT bitmap fonts (NOINST.CPK font/font17.fnt, font24.fnt): decode, edit glyphs, re-encode.

    python -X utf8 tools/kfnt.py check                 decode -> encode roundtrip of both fonts (byte-identical)
    python -X utf8 tools/kfnt.py show FONT CODES OUT.png   render glyphs (codes: hex, or 'ascii')

Format (read from the EBOOT's font code, docs/re/text.md §8: 0x08806334 glyph offset, 0x08806374 decompressor,
0x08805a24 draw):
- header 0x10: 'KFNT', u8 cell width, u8 cell height, u8 row stride (bytes), u8 bits per pixel (2), u16 0,
  u16 data section offset, u16 0xf1bf (?), u16 index entry count N. Then N 16-byte seek entries, then the data section.
- The glyphs form one virtual array: glyph i (i = SJIS code - 0x8140; single-byte code c uses c + 0x84c0) is
  `8 + height * stride` bytes at i * that size: an 8-byte header (s8 width = the advance, flag, 2 vertical-mode
  offsets, 2 horizontal-mode bearings, height, 0) then `height` rows of `stride` bytes, 2 bpp, low bits = leftmost pixel.
- Data section: u32 (data words + R + 1), u32 virtual word count, u32 R, then R (u16 skip, u16 count) run entries,
  then data words. Unused seek entries are all 0xffffffff. Expanding:
  walk the data words; at stream positions p0 = skip0, p1 = p0 + skip1, ... the word there is repeated `count` times
  (a zero-filled gap is one zero word repeated); every other word is emitted once.
- Seek entry k (word values a, b, c, d) = the decoder state at data-stream position (k+1) * (0x40000 // (N+1)): a = the
  next run's stream position, b = its run index, c = the virtual byte position, d = the data word index counted from
  file offset 0x10. The decoder skips to the last entry whose c <= the wanted offset.
"""
import os, struct, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FONT_DIR = os.path.join(ROOT, 'work', 'cpk', 'NOINST', 'font')


class Font:
    def __init__(self, data):
        assert data[:4] == b'KFNT', data[:4]
        self.head = bytearray(data[:0x10])
        self.w, self.h, self.stride, self.bpp = data[4:8]
        self.sec, self.unk, self.nidx = struct.unpack_from('<HHH', data, 0xa)
        self.glyph_size = 8 + self.h * self.stride
        total, self.zero, nruns = struct.unpack_from('<III', data, self.sec)
        runs = struct.unpack_from('<%dH' % (2 * nruns), data, self.sec + 12)
        self.runs = list(zip(runs[0::2], runs[1::2]))
        dpos = self.sec + 12 + 4 * nruns
        ndata = total - nruns - 3      # total counts the section's words after its own first word? checked by roundtrip
        self.total = total
        words = struct.unpack_from('<%dI' % ((len(data) - dpos) // 4), data, dpos)
        self.tail = data[dpos + 4 * len(words):]
        self.virt = self._expand(words)
        self.nwords_stream = len(words)

    def _expand(self, words):
        out = []
        r, nxt = 0, self.runs[0][0] if self.runs else -1
        for p, w in enumerate(words):
            if p == nxt and r < len(self.runs):
                out.extend([w] * self.runs[r][1])
                r += 1
                nxt = nxt + self.runs[r][0] if r < len(self.runs) else -1
            else:
                out.append(w)
        self.stream_runs = r
        return out

    # --- glyph access ---
    def index(self, code):
        if code < 0x100:
            code += 0x84c0
        return code - 0x8140

    def glyph(self, code):
        """-> (header 8 bytes, rows [[pixel value]*w]*h)."""
        o = self.index(code) * self.glyph_size
        raw = struct.pack('<%dI' % (self.glyph_size // 4), *self.virt[o // 4:(o + self.glyph_size) // 4])
        rows = []
        for y in range(self.h):
            r = raw[8 + y * self.stride:8 + (y + 1) * self.stride]
            rows.append([(r[x >> 2] >> ((x & 3) * 2)) & 3 for x in range(self.w)])
        return bytearray(raw[:8]), rows

    def set_glyph(self, code, header, rows):
        o = self.index(code) * self.glyph_size
        raw = bytearray(self.glyph_size)
        raw[:8] = header
        for y, row in enumerate(rows):
            for x, v in enumerate(row):
                raw[8 + y * self.stride + (x >> 2)] |= (v & 3) << ((x & 3) * 2)
        self.virt[o // 4:(o + self.glyph_size) // 4] = struct.unpack('<%dI' % (self.glyph_size // 4), raw)

    # --- encode ---
    def encode(self):
        """Re-compress: every maximal run of >= 2 equal words becomes one repeated word (the original packs runs of
        length 2+ the same way; checked by the roundtrip test), then rebuild the seek index."""
        v = self.virt
        words, runs, i, last_run_pos = [], [], 0, 0
        while i < len(v):
            j = i
            while j < len(v) and v[j] == v[i] and j - i < 0xffff:
                j += 1
            if j - i >= self.MIN_RUN:
                runs.append((len(words) - last_run_pos, j - i))
                last_run_pos = len(words)
                words.append(v[i])
            else:
                words.extend(v[i:j])
            i = j
        n = self.nidx
        step = 0x40000 // (n + 1)
        nruns = len(runs)
        dbase = self.sec + 12 + 4 * nruns          # file offset of data word 0
        # decoder state at each stream position multiple of step
        idx = []
        r, nxt, vpos = 0, runs[0][0] if runs else -1, 0
        targets = [(k + 1) * step for k in range(n)]
        t = 0
        for p in range(len(words) + 1):
            while t < n and targets[t] == p:
                idx.append((nxt if r < nruns else 0, r, vpos * 4, (dbase - 0x10) // 4 + p))
                t += 1
            if p == len(words):
                break
            if p == nxt and r < nruns:
                vpos += runs[r][1]
                r += 1
                nxt = nxt + runs[r][0] if r < nruns else -1
            else:
                vpos += 1
        while len(idx) < n:          # past the end of the stream: the original fills with this (checked by roundtrip)
            idx.append(self.FILL)
        out = bytearray(self.head)
        struct.pack_into('<H', out, 0xa, 0x10 + 16 * n)
        for e in idx:
            out += struct.pack('<4I', *e)
        out += struct.pack('<III', len(words) + nruns + 1, len(v), nruns)
        for s, c in runs:
            out += struct.pack('<HH', s, c)
        out += struct.pack('<%dI' % len(words), *words)
        return bytes(out + self.tail)

    MIN_RUN = 2
    FILL = (0xffffffff,) * 4


def load(name):
    with open(os.path.join(FONT_DIR, name), 'rb') as f:
        return f.read()


def main(a):
    if a[0] == 'check':
        for fn in ('font17.fnt', 'font24.fnt'):
            d = load(fn)
            f = Font(d)
            e = f.encode()
            first = next((i for i in range(min(len(d), len(e))) if d[i] != e[i]), None)
            print(fn, len(d), len(e), 'identical' if d == e else 'differs at %s' % (hex(first) if first is not None else 'length'),
                  'virt words', len(f.virt), 'glyphs', len(f.virt) * 4 // f.glyph_size, 'runs', len(f.runs), f.stream_runs)
    elif a[0] == 'show':
        from PIL import Image
        f = Font(load(a[1]))
        codes = list(range(0x20, 0x7f)) if a[2] == 'ascii' else [int(x, 16) for x in a[2].split(',')]
        z = 4
        im = Image.new('L', (len(codes) * (f.w + 2) * z, (f.h + 2) * z), 255)
        for k, c in enumerate(codes):
            hd, rows = f.glyph(c)
            for y, row in enumerate(rows):
                for x, v in enumerate(row):
                    if v:
                        for dy in range(z):
                            for dx in range(z):
                                im.putpixel(((k * (f.w + 2) + x) * z + dx, (y + 1) * z + dy), 255 - v * 85)
            for y in range(f.h * z):   # advance marker
                im.putpixel(((k * (f.w + 2) + hd[0]) * z, y), 128) if hd[0] < f.w + 2 else None
        im.save(a[3])
        print('saved', a[3])


if __name__ == '__main__':
    main(sys.argv[1:])
