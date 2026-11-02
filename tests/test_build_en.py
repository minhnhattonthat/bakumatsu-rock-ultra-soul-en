"""The English build from the current script/: build.build() runs isodiff.check + readback and raises on any problem.
Then the gate must reject an unrelated directory record changed in a sector it shares with an edited file.
Skips without rom/. Writes work/test/en.iso (~1.7 GB, deleted after)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import insert  # noqa: E402
import iso9660  # noqa: E402
import isodiff  # noqa: E402

need = pytest.mark.skipif(not Path(build.ROM).exists(), reason="no ROM")
OUT = ROOT / "work" / "test" / "en.iso"


@pytest.fixture(scope="module")
def en_iso():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        build.build(str(OUT))   # planned edits from script/: diff gate + read-back inside
        yield OUT
    finally:
        OUT.unlink(missing_ok=True)


@need
def test_plan_log_and_english_build(en_iso):
    lines = []
    ed = insert.plan(log=lines.append)   # the documented `insert.py plan` path logs every file
    assert lines and ed["iso"] and ed["INST"]
    assert isodiff.check(str(en_iso), ed) == []


@need
def test_gate_rejects_unrelated_directory_record(en_iso):
    ed = insert.plan()
    with open(en_iso, "rb") as f:
        files = {p: (lba, ln, pos) for p, lba, ln, pos in iso9660.listing(f)}
    edited_secs = {files[p][2] // 2048 for p in ed["iso"]}
    victim = next(p for p, (_, _, pos) in files.items() if pos // 2048 in edited_secs and p not in ed["iso"])
    pos = files[victim][2]
    with open(en_iso, "r+b") as f:
        f.seek(pos + 10); old = f.read(8)
        f.seek(pos + 10); f.write(iso9660.both(1))
    try:
        assert isodiff.check(str(en_iso), ed)
    finally:
        with open(en_iso, "r+b") as f:
            f.seek(pos + 10); f.write(old)
