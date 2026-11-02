"""Format checks on the unpacked data; skip when work/iso (python tools/iso9660.py x ROM work/iso) is absent."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cpk import open_cpk  # noqa: E402
from crilayla import decompress, is_crilayla  # noqa: E402

NOINST = ROOT / "work" / "iso" / "PSP_GAME" / "USRDIR" / "NOINST.CPK"
INST = ROOT / "work" / "iso" / "PSP_GAME" / "USRDIR" / "INST.CPK"
need = pytest.mark.skipif(not NOINST.exists(), reason="no work/iso")


def entry(cpk, name):
    _, ents = open_cpk(cpk)
    e = next(e for e in ents if f"{e.dir}/{e.name}" == name)
    with open(cpk, "rb") as f:
        f.seek(e.off)
        b = f.read(e.csize)
    return e, b


@need
def test_crilayla_system_text():
    e, b = entry(NOINST, "systemdata/ui_system_text.stb")
    assert is_crilayla(b)
    d = decompress(b)
    assert len(d) == e.size == 54096
    # STLH: 16-byte header, 0x68 records of text[0x200] + u32 lines + u32 id
    magic, _, first, count = struct.unpack_from("<4sIII", d, 0)
    assert magic == b"STLH" and first == 0x10 and count == 0x68
    assert d[0x10:0x14].decode("cp932") == "はい"
    assert struct.unpack_from("<II", d, 0x10 + 0x200) == (1, 0)


@need
def test_scene_script_walks_to_end():
    """Ops are u16 op + u16 length in words (0 = 1); op 0x19 is followed by an inline table of 100 fb03 strings."""
    e, b = entry(INST, "scene/script/b_001001.bin")
    d = decompress(b) if is_crilayla(b) else b
    assert d[:4] == b"MZ\0\0"
    p, texts = 4, []
    while p < len(d):
        op, ln = struct.unpack_from("<HH", d, p)
        if op == 0x62:
            t, n = struct.unpack_from("<HH", d, p + 8)
            texts.append(d[p + 12:p + 12 + n * 4].rstrip(b"\0").decode("cp932"))
        p += (ln or 1) * 4
        if op == 0x19 and struct.unpack_from("<H", d, p)[0] == 0xFB03:
            for _ in range(100):
                p += 4 + struct.unpack_from("<H", d, p + 2)[0] * 4
    assert p == len(d)
    assert texts[0].startswith("意気揚々と土佐の")
