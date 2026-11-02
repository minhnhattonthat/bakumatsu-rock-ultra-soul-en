"""uitable.py: the fixed-slot UI text tables in NOINST.CPK systemdata/ (and the EBOOT / PARAM.SFO strings).

Every table file is a header (4cc + 0x00010000 + u32 first-record offset + u32 count) followed by records of a fixed
stride; text lives in NUL-padded slots of a fixed capacity, so English is inserted in place and must fit the slot.
Layouts were derived by record dumps (work/scratch) and are asserted by tests/test_extract.py: every Japanese run in
each file must fall inside one of these slots.

Most slots are Shift-JIS; 46 records of ui_system_text.stb (install and save messages) are UTF-8, so each slot keeps the
encoding it decoded with and `write_table` writes it back in that encoding.

`slots(data, name)` -> [Slot(off, capacity, kind, text, enc)]; `write_table(name, data, texts)` -> patched bytes.
"""
import struct

from textfmt import decode_any, japanese_runs, slot_bytes


class Slot:
    __slots__ = ('off', 'capacity', 'kind', 'text', 'enc')

    def __init__(self, off, capacity, kind, text, enc='cp932'):
        self.off, self.capacity, self.kind, self.text, self.enc = off, capacity, kind, text, enc

    def __repr__(self):
        return f'Slot(0x{self.off:x}, {self.capacity}, {self.kind}, {self.text[:12]!r})'


# (base, count, stride, [(record offset, capacity, kind)])
SECTIONS = {
    'ui_system_text.stb': [(0x10, 0x68, 0x208, [(0x00, 0x200, 'text')])],
    'ui_event.evt':       [(0x10, 0x1B, 0x48, [(0x04, 0x40, 'title')])],
    'ui_movie.mve':       [(0x10, 0x20, 0x8C, [(0x04, 0x40, 'title'), (0x48, 0x40, 'performers')])],
    'ui_sound.sud':       [(0x10, 0x19, 0x48, [(0x04, 0x40, 'title')]),
                           (0x77C, 0x02, 0x88, [(0x08, 0x40, 'title')])],
    'ui_chapter.cil':     [(0x1C, 0x1A, 0x1A4, [(0x00, 0x80, 'chapter')]),
                           (0x2AC4, 0x10, 0x1A4, [(0x00, 0x80, 'title'), (0x84, 0x80, 'description'),
                                                  (0x108, 0x80, 'unlock')]),
                           (0x4500, 0x1B, 0xCC, [(0x04, 0x40, 'song'), (0x48, 0x80, 'performer')])],
}

# ui_profile.pfl: u32 index, then 11 short fields (name, VA, origin, birthday, height, weight, blood type, sign,
# likes, favourite food, dislikes), each text + u32 line count, then six 0x128-byte biography sections
# (title[32] + u32 + text[256] + u32). Unused biography sections are all zero.
PFL_FIELDS = [(0x04, 0x10, 'name'), (0x18, 0x10, 'va'), (0x2C, 0x08, 'origin'), (0x38, 0x10, 'birthday'),
              (0x4C, 0x10, 'height'), (0x60, 0x10, 'weight'), (0x74, 0x08, 'blood'), (0x80, 0x08, 'sign'),
              (0x8C, 0x20, 'likes'), (0xB0, 0x20, 'food'), (0xD4, 0x20, 'dislikes')]
PFL_STRIDE, PFL_COUNT = 0x7E8, 0x12
BIO = 0x128

# EBOOT save-data titles (UTF-8, not Shift-JIS; see text.md section 4). (offset, capacity)
EBOOT_SLOTS = [(0x26925C, 0x14), (0x269270, 0x30), (0x2692A0, 0x28),
               (0x269458, 0x14), (0x26946C, 0x28), (0x269494, 0x1C), (0x2694BC, 0x24), (0x2694E0, 0x18)]
SFO_TITLE = (0x1D8, 0x80)   # absolute offset of the TITLE value and its max length (the maxlen column)


def slots(data, name):
    """-> [Slot] for a systemdata table, in file order."""
    out = []
    if name == 'ui_profile.pfl':
        for r in range(PFL_COUNT):
            base = 0x10 + r * PFL_STRIDE
            for off, cap, kind in PFL_FIELDS:
                out.append(_slot(data, base + off, cap, kind))
            for b in range(6):
                sec = base + 0xF8 + b * BIO
                out.append(_slot(data, sec, 0x20, 'bio-title'))
                out.append(_slot(data, sec + 0x24, 0x100, 'bio'))
    elif name.startswith('ui_skit_'):
        out += _skit_slots(data)
    else:
        for base, count, stride, fields in SECTIONS[name]:
            for r in range(count):
                for off, cap, kind in fields:
                    out.append(_slot(data, base + r * stride + off, cap, kind))
    return out


def _slot(data, off, cap, kind):
    raw = data[off:off + cap]
    assert len(raw) == cap, f'slot at {off:#x} past EOF'
    # a slot is text + NUL padding; anything after the first NUL must be zero
    body = raw.rstrip(b'\0')
    assert b'\0' not in body, f'non-padding NUL inside slot at {off:#x}'
    text, enc = decode_any(raw)
    return Slot(off, cap, kind, text, enc)


def _skit_slots(data):
    """SKTH: name[0x28]; then per skit: u32 index, name[0x28], u32 speakers, u32 messages,
    and per message 5 u32 words + 3 line slots of 0x28. The last skits of some files carry extra messages in a
    looser layout (no record header, variable header length); those are taken by run scanning, capacity = the free
    space up to the next non-zero byte."""
    out = [_slot(data, 0x10, 0x28, 'title')]          # the "no skit" placeholder
    p = 0x38
    while p + 0x34 <= len(data):
        idx = struct.unpack_from('<I', data, p)[0]
        speakers = struct.unpack_from('<I', data, p + 0x2C)[0]
        count = struct.unpack_from('<I', data, p + 0x30)[0]
        if not (1 <= idx <= 99 and speakers <= 30 and count <= 60):
            break
        nxt = p + 0x34 + count * 0x8C
        if nxt > len(data):
            break
        out.append(_slot(data, p + 4, 0x28, 'title'))
        m = p + 0x34
        for _ in range(count):
            for k in range(3):
                out.append(_slot(data, m + 0x14 + k * 0x28, 0x28, 'line'))
            m += 0x8C
        p = nxt
    for off, ln, text in japanese_runs(data[p:]):
        start = p + off
        end = start + ln
        # skip id words that happen to decode (e.g. 0x34a7 -> halfwidth kana + "4")
        if ln <= 4 and not any('぀' <= c <= 'ヿ' or '一' <= c <= '鿿' or '　' <= c <= '〿' or '！' <= c <= '｠'
                              for c in text):
            continue
        cap = end
        while cap < len(data) and data[cap] == 0:
            cap += 1
        out.append(_slot(data, start, cap - start, 'line'))
    return out


def write_table(name, data, texts):
    """Patch every slot of one table in place: texts = {slot offset: str}; returns the new bytes."""
    for s in slots(data, name):
        if s.off in texts:
            nul = texts[s.off] != s.text      # new text keeps a terminator (textfmt.slot_bytes)
            data = data[:s.off] + slot_bytes(texts[s.off], s.capacity, s.enc, nul) + data[s.off + s.capacity:]
    return data


def eboot_slots(eboot):
    """EBOOT save-data titles (UTF-8). Bounds-checked from the raw bytes."""
    out = []
    for off, cap in EBOOT_SLOTS:
        body = eboot[off:off + cap].rstrip(b'\0')
        assert b'\0' not in body, f'non-padding NUL in EBOOT slot {off:#x}'
        out.append(Slot(off, cap, 'save-title', body.decode('utf-8'), 'utf-8'))
    return out


def write_eboot(eboot, texts):
    out = bytearray(eboot)
    for off, cap in EBOOT_SLOTS:
        if off in texts:
            b = texts[off].encode('utf-8')
            assert len(b) < cap, f'EBOOT slot {off:#x}: {len(b)} bytes + NUL > {cap}'
            out[off:off + cap] = b + b'\0' * (cap - len(b))
    return bytes(out)


def sfo_title(sfo):
    off, cap = SFO_TITLE
    body = sfo[off:off + cap].rstrip(b'\0')
    return Slot(off, cap, 'title', body.decode('utf-8'), 'utf-8')


def write_sfo(sfo, text):
    off, cap = SFO_TITLE
    b = text.encode('utf-8')
    assert len(b) < cap, f'SFO title: {len(b)} bytes + NUL > {cap}'
    return sfo[:off] + b + b'\0' * (cap - len(b)) + sfo[off + cap:]
