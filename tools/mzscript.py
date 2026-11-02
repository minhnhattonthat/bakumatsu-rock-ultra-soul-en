"""mzscript.py: reader/writer for the MZ bytecode used by ADV scene scripts and rhythm charts.

Format (docs/re/text.md, verified by walking every file to EOF):
  file  = b'MZ\\0\\0' + instruction*
  instr = u16 op + u16 words + args      (words = the instruction's total size in 4-byte units, 0 means 1)
  args  = word* where a string argument is u16 type (low byte 3, high byte 0x00/0xFB/0xF1) + u16 nwords +
          nwords*4 bytes of NUL-padded cp932
  op 0x19 is followed by an inline table of 100 string arguments (the speaker/name table), not counted in its words.

`parse` turns every instruction into a token list of ints (plain u32 words) and Slot objects, so `serialize` covers
every byte of the file and `serialize(parse(b)) == b` is the roundtrip test. String slots carry the offset of their type
word, so a slot's id is stable.

Text kinds (what a translator sees) are decided by opcode:
  scene: 0x62 dialogue, 0x51 choice, 0x4C staff roll, op-0x19 table speaker names; everything else is engine data
         (asset paths, script names, thread/job labels) and is kept as data.
  play:  op 0x2C lyric fragment per note.
"""
import struct

from textfmt import decode, slot_bytes

MAGIC = b'MZ\0\0'
TYPE_HI = (0x00, 0xFB, 0xF1)     # every string type word in the game
SCENE_TEXT = {0x62: 'dialogue', 0x51: 'choice', 0x4C: 'staff'}
PLAY_TEXT = {0x2C: 'lyric'}
NAME_TABLE_OP = 0x19
NAME_TABLE_COUNT = 100


class Slot:
    """One string argument: a type word at `off`, then nwords*4 bytes of text."""

    __slots__ = ('off', 'capacity', 'type', 'kind', 'text', 'op', 'msg')

    def __init__(self, off, capacity, type_, kind, text, op, msg=None):
        self.off, self.capacity, self.type, self.kind = off, capacity, type_, kind
        self.text, self.op, self.msg = text, op, msg

    def __repr__(self):
        return f'Slot(0x{self.off:x}, {self.capacity}, {self.kind}, {self.text[:12]!r})'


class Instr:
    __slots__ = ('off', 'op', 'words', 'tokens', 'table')

    def __init__(self, off, op, words):
        self.off, self.op, self.words = off, op, words
        self.tokens, self.table = [], None

    @property
    def slots(self):
        return [t for t in self.tokens if isinstance(t, Slot)]


class Script:
    def __init__(self, data):
        self.data = data
        self.instrs = []
        self.slots = []          # every slot in file order, including shared name-table slots
        self.table_slots = []    # the op-0x19 table (identical in all 80 scene scripts)

    @property
    def text_slots(self):
        return [s for s in self.slots if s.kind not in ('data', '')]


def _string_at(data, p, limit):
    """If a string argument starts at p and fits before limit -> (type word, capacity, text) else None."""
    if p + 4 > limit or data[p] != 3 or data[p + 1] not in TYPE_HI:
        return None
    nwords = struct.unpack_from('<H', data, p + 2)[0]
    if p + 4 + nwords * 4 > limit:
        return None
    raw = data[p + 4:p + 4 + nwords * 4]
    try:
        return struct.unpack_from('<H', data, p)[0], nwords * 4, decode(raw)
    except (UnicodeDecodeError, AssertionError):
        return None


def parse(data, kind='scene'):
    """kind: 'scene' or 'play'. Raises ValueError if the instruction stream does not end exactly at EOF."""
    if data[:4] != MAGIC:
        raise ValueError('not an MZ script')
    sc = Script(data)
    text_ops = SCENE_TEXT if kind == 'scene' else PLAY_TEXT
    p = 4
    while p < len(data):
        op, words = struct.unpack_from('<HH', data, p)
        size = (words or 1) * 4
        if p + size > len(data):
            raise ValueError(f'{p:#x}: instruction runs past EOF')
        ins = Instr(p, op, words)
        q, end = p + 4, p + size
        while q < end:
            s = _string_at(data, q, end)
            if s is None:
                ins.tokens.append(struct.unpack_from('<I', data, q)[0])
                q += 4
                continue
            type_, cap, text = s
            slot_kind = text_ops.get(op, 'data') if cap else 'data'
            msg = struct.unpack_from('<I', data, p + 4)[0] if op == 0x62 else None
            slot = Slot(q, cap, type_, slot_kind, text, op, msg)
            ins.tokens.append(slot)
            sc.slots.append(slot)
            q += 4 + cap
        sc.instrs.append(ins)
        p += size
        if op == NAME_TABLE_OP and p + 2 <= len(data) and struct.unpack_from('<H', data, p)[0] == 0xFB03:
            ins.table = []
            for _ in range(NAME_TABLE_COUNT):
                type_, cap, text = _string_at(data, p, len(data))
                slot = Slot(p, cap, type_, 'speaker', text, op)
                ins.table.append(slot)
                sc.table_slots.append(slot)
                sc.slots.append(slot)
                p += 4 + cap
    return sc


def serialize(sc, texts=None):
    """Rebuild the file. texts: {slot offset: str} overrides (missing = keep the original jp)."""
    texts = texts or {}
    out = bytearray(MAGIC)
    for ins in sc.instrs:
        assert len(out) == ins.off, (len(out), ins.off)
        out += b'\0\0\0\0'
        for tok in ins.tokens:
            if isinstance(tok, Slot):
                out += struct.pack('<HH', tok.type, tok.capacity // 4) + slot_bytes(texts.get(tok.off, tok.text), tok.capacity)
            else:
                out += struct.pack('<I', tok)
        size = (len(out) - ins.off) // 4
        # an instruction whose size is unchanged keeps the original words field (0 means 1, both appear in the dump)
        struct.pack_into('<HH', out, ins.off, ins.op, ins.words if size == (ins.words or 1) else size)
        if ins.table:
            for slot in ins.table:
                out += struct.pack('<HH', slot.type, slot.capacity // 4) + slot_bytes(texts.get(slot.off, slot.text), slot.capacity)
    if len(out) != len(sc.data):
        raise ValueError(f'serialize: {len(out)} bytes, original {len(sc.data)}')
    return bytes(out)
