"""textfmt.py: the repo's text encoding (Shift-JIS / cp932) and the JSON text-file format.

A text slot is a fixed region of a file holding a NUL-padded string: (offset, capacity, jp). `decode` strips the
trailing NUL padding, `encode` re-pads to the same capacity, so encode(decode(raw)) == raw for every slot in the game
(asserted by tests/test_extract.py).

PUA bytes: cp932 lead bytes 0xF0-0xF9 are user-defined and decode to U+E000..; the encoder maps them back, so glyph
codes inside lyric text roundtrip unchanged.

Text files (script/*.json) are written with indent=1, ensure_ascii=False, LF endings; `jp` is the decoded original,
`en` the translation (empty until phase 6), `max` the slot size in bytes.
"""
import json, os

ENC = 'cp932'


def decode(raw):
    """NUL-padded cp932 slot -> str. Raises UnicodeDecodeError on bytes cp932 cannot decode."""
    body = raw.rstrip(b'\0')
    assert b'\0' not in body, 'embedded NUL in text slot'
    s = body.decode(ENC)
    assert encode(s) == body, s
    return s


def decode_any(raw):
    """-> (text, encoding): cp932 when it decodes, else UTF-8 (46 ui_system_text records are UTF-8)."""
    body = raw.rstrip(b'\0')
    assert b'\0' not in body, 'embedded NUL in text slot'
    try:
        s = body.decode(ENC)
        if encode(s) == body:
            return s, ENC
    except UnicodeDecodeError:
        pass
    s = body.decode('utf-8')
    assert s.encode('utf-8') == body, s
    return s, 'utf-8'


def encode(s):
    """str -> cp932 bytes (no padding). Raises UnicodeEncodeError for a character cp932 has no code for."""
    return s.encode(ENC)


def slot_bytes(s, capacity, enc=ENC):
    """str -> exactly `capacity` bytes: encoded text + NUL padding. Raises if it does not fit."""
    b = s.encode(enc)
    if len(b) > capacity:
        raise ValueError(f'{s!r}: {len(b)} bytes does not fit in {capacity}')
    return b + b'\0' * (capacity - len(b))


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write('\n')


def is_japanese(s):
    return any('぀' <= c <= 'ヿ' or '一' <= c <= '鿿' or 'ｦ' <= c <= 'ﾟ' for c in s)


def japanese_runs(raw):
    """Every maximal run of cp932 Japanese text in bytes: [(offset, length, str)]. Used by the coverage tests."""
    out, p, n = [], 0, len(raw)
    while p < n:
        if not is_japanese_byte(raw, p):
            p += 1
            continue
        q = p
        try:
            while q < n and raw[q] != 0 and (raw[q] < 0x80 or is_japanese_byte(raw, q)):
                q += 2 if raw[q] >= 0x81 else 1
            out.append((p, q - p, raw[p:q].decode(ENC)))
        except UnicodeDecodeError:
            p += 1
            continue
        p = q
    return out


def is_japanese_byte(raw, i):
    """A byte that starts a Japanese cp932 char: double-byte lead 0x81-0x9F/0xE0-0xFC, or halfwidth katakana 0xA1-0xDF."""
    b = raw[i]
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xFC or 0xA1 <= b <= 0xDF
