"""Phase 5 insert pipeline: no edits -> no patch, resized MZ strings keep every jump valid, fixed slots refuse overflow."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import insert  # noqa: E402
import mzscript  # noqa: E402
import uitable  # noqa: E402
from textfmt import read_json  # noqa: E402

need = pytest.mark.skipif(not Path(insert.CPK).exists(), reason="no unpacked CPK (work/cpk)")


@need
def test_no_english_no_edits():
    """script/ has no `en` yet: insert.plan() patches nothing (identity, checked again by test_identity)."""
    ed = insert.plan(insert.SCRIPT)
    assert ed == {"INST": {}, "NOINST": {}, "iso": {}}


@need
@pytest.mark.parametrize("fn", ["m_001001.bin", "ED_001001.bin", "staffroll.bin", "b_006002.bin"])
def test_longer_text_keeps_every_jump_valid(fn):
    """Replace every text slot with a much longer marker: the file must re-parse to EOF and every jump arg must
    still land on an instruction start."""
    src = Path(insert.CPK) / "INST" / "scene" / "script" / fn
    data = src.read_bytes()
    sc = mzscript.parse(data, "scene")
    texts = {s.off: f"[{s.off:x}] The quick brown fox jumps over the lazy dog." for s in sc.text_slots if s.kind != "speaker"}
    assert texts
    out = insert.patch_script(fn, data, texts)
    assert out is not None and len(out) > len(data)
    new = mzscript.parse(out, "scene")
    starts = {i.off // 4 for i in new.instrs}
    for ins in new.instrs:
        widx = insert._word_index(ins.tokens)
        for w in insert.jump_positions(ins):
            if w not in widx:
                continue
            v = ins.tokens[widx.index(w)]
            assert not isinstance(v, int) or v <= 1 or v in starts, f"{fn}: jump at {ins.off:#x} word {w} -> {v:#x}"
    # the text slots survived in order, and the untouched data slots were not re-encoded
    old_t = [s for s in sc.text_slots if s.kind != "speaker"]
    new_t = [s for s in new.text_slots if s.kind != "speaker"]
    assert [s.kind for s in old_t] == [s.kind for s in new_t]
    assert all(s.text.startswith("[") for s in new_t)
    # horizontal ADV layout: no box left vertical, speech-box pitch changed (docs/re/text.md §8)
    modes = [insert._s16pair(i.tokens[0]) for i in new.instrs if i.op == insert.LAYOUT_OP]
    assert modes and all(m != insert.VERTICAL for _, m in modes)
    pitches = [insert._s16pair(i.tokens[0]) for i in new.instrs if i.op == insert.PITCH_OP]
    assert all(p == insert.ADV_PITCH for b, p in pitches if b < 3)


@need
def test_same_text_is_not_a_patch():
    src = Path(insert.CPK) / "INST" / "scene" / "script" / "m_001002.bin"
    data = src.read_bytes()
    sc = mzscript.parse(data, "scene")
    assert insert.patch_script("m_001002.bin", data, {s.off: s.text for s in sc.slots}) is None


@need
def test_ui_overflow_is_refused():
    """Fixed UI slots must raise instead of silently clipping."""
    name = "ui_event.evt"
    data = (Path(insert.CPK) / "NOINST" / "systemdata" / name).read_bytes()
    slot = next(s for s in uitable.slots(data, name) if s.capacity)
    with pytest.raises(ValueError, match="does not fit"):
        uitable.write_table(name, data, {slot.off: "x" * (slot.capacity + 1)})


@need
def test_marker_set_fits_every_slot():
    """work/mark (the marker build's text) patches every file it names without an overflow."""
    mark = Path(ROOT) / "work" / "mark"
    if not mark.exists():
        pytest.skip("no marker set (python tools/mark.py --force)")
    ed = insert.plan(str(mark))
    # NOINST: 9 UI tables + font17 (VWF); iso: PARAM.SFO + the plain EBOOT with the ADV code patch (D12)
    assert len(ed["INST"]) == 109 and len(ed["NOINST"]) == 10 and len(ed["iso"]) == 2
