import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import batches  # noqa: E402
import vwf  # noqa: E402


def test_whole_run_terms():
    assert batches.has_term("天歌を歌え", "天歌")
    assert not batches.has_term("タイミング", "ミン")       # katakana inside a longer katakana run
    assert batches.has_term("龍馬さん", "龍馬")


def test_dialogue_wraps_to_the_gate():
    lines = batches.wrap_dialogue("Can you believe it? The capital is so lively!\\nNothing like Tosa.")
    assert all(vwf.line_px(ln) <= vwf.ADV_LINE_PX for ln in lines)
    assert lines[-1] == "Nothing like Tosa."      # an explicit \n forces a break
