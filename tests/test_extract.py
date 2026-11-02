"""Phase 4 checks: the text extractor roundtrips every source file and every dumped string.

Needs work/iso + work/cpk (python tools/iso9660.py x ROM work/iso; python tools/unpack.py).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import extract  # noqa: E402
import mzscript  # noqa: E402
import textfmt  # noqa: E402
import uitable  # noqa: E402

need = pytest.mark.skipif(not (ROOT / "work" / "cpk" / "INST" / "scene").exists(), reason="no work/cpk")
need_script = pytest.mark.skipif(not (ROOT / "script" / "scene").exists(), reason="no script/ dump")


def test_textfmt_roundtrip():
    cases = ["意気揚々と土佐の地を\\n出発した龍馬は", "はい", "…………", "龍馬　高杉　桂", "Rock", "㈱",
             "\ue040\ue041", "ソ"]     # ソ = 83 5C: a trail byte that is also an ASCII backslash
    for s in cases:
        raw = textfmt.encode(s)
        assert textfmt.decode(raw + b"\0\0") == s
    assert textfmt.decode_any(b'\xef\xbc\x9c\xe3\x82\xa4\0') == ("＜イ", "utf-8")
    with pytest.raises(ValueError):
        textfmt.slot_bytes("toolong", 4)


@need
def test_mz_roundtrip():
    for name, sc in extract.scene_scripts():
        assert mzscript.serialize(sc) == sc.data, name
        assert len(sc.table_slots) == 100, name
    for name, sc in extract.play_scripts():
        assert mzscript.serialize(sc) == sc.data, name
        assert not sc.table_slots, name


@need
def test_scene_counts():
    """The extractor finds the string arguments docs/re/text.md counted."""
    kinds = {"dialogue": 0, "choice": 0, "staff": 0}
    for _, sc in extract.scene_scripts():
        for s in sc.slots:
            if s.kind in kinds:
                kinds[s.kind] += 1
        assert len(sc.table_slots) == 100
    assert kinds["dialogue"] == 13063
    assert kinds["choice"] == 121
    assert kinds["staff"] == 78


@need
def test_ui_roundtrip():
    for name in extract.ui_files():
        path = Path(extract.UI_DIR) / name
        data = path.read_bytes()
        assert uitable.write_table(name, data, {}) == data, name
        for s in uitable.slots(data, name):
            textfmt.slot_bytes(s.text, s.capacity, s.enc)
    assert len(extract.ui_files()) == 9


@need
def test_eboot_roundtrip():
    eboot = Path(extract.EBOOT).read_bytes()
    slots = uitable.eboot_slots(eboot)
    assert len(slots) == 18   # 8 UTF-8 save titles + 9 profile labels + the play-time label
    assert uitable.write_eboot(eboot, {}) == eboot
    assert uitable.write_eboot(eboot, {s.off: s.text for s in slots}) == eboot
    sfo = Path(extract.SFO).read_bytes()
    assert uitable.write_sfo(sfo, uitable.sfo_title(sfo).text) == sfo


@need
def test_coverage():
    assert extract.check_coverage() == []


@need_script
def test_json_matches_sources():
    assert extract.check_json() == []


@need_script
def test_json_files_are_wellformed():
    files = sorted((ROOT / "script").rglob("*.json"))
    assert len(files) > 100
    seen = set()
    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert doc["source"] and doc["format"] in ("mz-scene", "mz-play", "ui-table", "utf-8-slots")
        for e in doc["entries"]:
            assert set(e) >= {"id", "off", "max", "kind", "jp", "en"}, path
            assert e["id"] not in seen, e["id"]
            seen.add(e["id"])
            assert isinstance(e["off"], int) and e["max"] > 0
            assert isinstance(e["en"], str), e["id"]
