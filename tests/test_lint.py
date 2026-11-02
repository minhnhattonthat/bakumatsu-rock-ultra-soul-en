"""Phase 7 checks: text lint (tools/lint.py), balanced wrap, and the ISO diff gate's comparators (tools/isodiff.py)."""
import io
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import isodiff  # noqa: E402
import lint  # noqa: E402
import vwf  # noqa: E402
from batches import join_lines  # noqa: E402


def test_script_lint_is_clean():
    assert lint.lint() == []


def problems(en, jp="テスト", kind="dialogue", fmt="mz-scene", mx=64):
    return lint.entry_problems("scene/x.json", fmt, {"jp": jp, "en": en, "kind": kind, "max": mx}, [])


def test_lint_catches_each_rule():
    assert any("px" in p for p in problems("a" * 60))
    assert any("lines" in p for p in problems("\\n".join(["Hi"] * 9)))
    assert any("control codes" in p for p in problems("Hi", jp="\\col1テスト\\col0"))
    assert any("non-ASCII" in p for p in problems("テスト"))
    assert any("bytes" in p for p in problems("x" * 10, kind="line", fmt="ui-table", mx=8))
    assert any("stub" in p for p in problems("Tears... tears, you\\nsay?"))
    assert any("trailing" in p for p in problems("Hi "))
    assert problems("Tears...\\ntears, you say?") == []


def test_balanced_wrap_keeps_the_line_count_and_fills_the_last_line():
    text = "Tears... tears, you say?"
    assert len(vwf.wrap(text)) == len(vwf.greedy(text)) == 2
    assert vwf.wrap(text)[-1] != "say?"
    assert all(vwf.line_px(ln) <= vwf.ADV_LINE_PX for ln in vwf.wrap(text))
    assert join_lines(["Kyoto--", "the city"]) == "Kyoto--the city"


def test_chapter_end_titles_keep_the_colon_the_eboot_searches_for():
    """insert.CHAPTER_CODE: chapter end copies the title up to ':' (was 話); a title without one crashes the game."""
    import glob
    import struct
    import insert
    from textfmt import read_json
    cil = glob.glob(os.path.join(insert.CPK, "NOINST", "systemdata", "ui_chapter.cil"))
    if not cil:
        import pytest
        pytest.skip("no work/cpk")
    data = open(cil[0], "rb").read()
    doc = read_json(os.path.join(insert.SCRIPT, "ui", "ui_chapter.json"))
    ids = {struct.unpack_from("<I", data, e["off"] - 4)[0]: e for e in doc["entries"] if e["kind"] == "chapter"}
    for i in insert.CHAPTER_END_IDS:
        assert "話" in ids[i]["jp"] and ":" in ids[i]["en"], ids[i]


def test_staffroll2_keeps_its_own_speaker_names():
    """Per-file op-0x19 names (`staffroll2:name:NNN`) win over the shared table (they were dropped before)."""
    import insert
    import mzscript
    if not os.path.isdir(insert.CPK):
        import pytest
        pytest.skip("no work/cpk")
    data = open(os.path.join(insert.CPK, *insert.SCENE_DIR, "staffroll2.bin"), "rb").read()
    sc = mzscript.parse(insert.patch_script("staffroll2.bin", data, {}, "scene", {8: "Elder"}, {8: "TBD"}), "scene")
    assert sc.table_slots[8].text == "TBD"


def test_isodiff_flags_changes_outside_the_allowed_sectors():
    a = bytes(4 * isodiff.SEC)
    b = bytearray(a); b[1 * isodiff.SEC] = 1; b[3 * isodiff.SEC + 5] = 1
    assert isodiff.bad_sectors(io.BytesIO(a), io.BytesIO(bytes(b)), {1}, len(a)) == [3]
    assert isodiff.spans_diff(b"abcdef", b"aXcdeY", [(1, 1)]) == ["0x5"]
