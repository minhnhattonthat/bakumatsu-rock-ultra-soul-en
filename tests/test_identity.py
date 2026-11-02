"""Phase 3 identity build: unpack -> repack with no edits gives the original ISO byte for byte; an edit round-trips.
Skips without rom/ (fresh clone). Writes scratch images to work/test/ (H:, not the system temp)."""
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import cpk  # noqa: E402
from unpack import read_entry  # noqa: E402

need = pytest.mark.skipif(not Path(build.ROM).exists(), reason="no ROM")
SCRATCH = ROOT / "work" / "test"


def rom_sha1():
    return next(l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and l[0] != "#").split()[0]


@need
def test_no_edit_build_is_identical():
    out = SCRATCH / "identity.iso"
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        assert build.build(str(out), {"INST": {}, "NOINST": {}, "iso": {}}) == rom_sha1()
    finally:
        out.unlink(missing_ok=True)


@need
def test_edited_cpk_reads_back():
    """Replace a CRILAYLA file (stored raw) and a duplicate-named one; every entry must read back as expected."""
    src = Path(build.WORK_ISO) / "PSP_GAME" / "USRDIR" / "INST.CPK"
    _, ents = cpk.open_cpk(src)
    comp = next(e for e in ents if e.csize < e.size)
    dup = [e for e in ents if e.name == "com_000.gim"]
    assert len(dup) == 2 and dup[0].dir != dup[1].dir
    repl = {f"{comp.dir}/{comp.name}": read_entry(src, comp), f"{dup[1].dir}/{dup[1].name}": b"MIG.00.1PSP\0" + b"x" * 5000}
    out = SCRATCH / "edit.cpk"
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        out.write_bytes(cpk.rebuild(src, repl))
        info, new = cpk.open_cpk(out)
        assert info["ContentSize"] + info["ContentOffset"] == info["EtocOffset"]
        for a, b in zip(ents, new):
            key = f"{a.dir}/{a.name}"
            assert (b.dir, b.name) == (a.dir, a.name) and b.off % 2048 == 0
            if key in repl:   # stored raw: FileSize == ExtractSize == len
                assert read_entry(out, b) == repl[key] and b.size == b.csize == len(repl[key])
                continue
            assert (b.size, b.csize) == (a.size, a.csize)
            if a.off % 97 == 0 or a is dup[0]:   # sample: untouched entries keep their stored bytes
                with open(src, "rb") as f, open(out, "rb") as g:
                    f.seek(a.off); g.seek(b.off)
                    assert f.read(a.csize) == g.read(b.csize)
    finally:
        out.unlink(missing_ok=True)
