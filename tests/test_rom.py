"""Cheap checks on the dump listing; ROM-dependent ones skip when rom/ is absent (fresh clone)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import iso9660  # noqa: E402

ISO = ROOT / "rom" / "Bakumatsu Rock - Ultra Soul (Japan).iso"


def test_rom_sha1_lists_the_iso():
    lines = [l for l in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines() if l and not l.startswith("#")]
    assert len(lines) == 1
    sha, name = lines[0].split(None, 1)
    assert len(sha) == 40 and (ROOT / name.strip()).name == ISO.name


@pytest.mark.skipif(not ISO.exists(), reason="no ROM")
def test_iso_layout():
    assert ISO.stat().st_size == 1699610624
    with open(ISO, "rb") as f:
        paths = {p for p, *_ in iso9660.listing(f)}
    assert {"/PSP_GAME/SYSDIR/EBOOT.BIN", "/PSP_GAME/USRDIR/INST.CPK", "/PSP_GAME/USRDIR/NOINST.CPK"} <= paths
