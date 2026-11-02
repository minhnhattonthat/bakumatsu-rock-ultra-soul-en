import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import batches  # noqa: E402
import vwf  # noqa: E402


def test_whole_run_terms():
    assert batches.has_term("天歌を歌え", "天歌")
    assert not batches.has_term("タイミング", "ミン")       # katakana inside a longer katakana run
    assert batches.has_term("龍馬さん", "龍馬")


def test_terms_longest_match_and_honorifics():
    gl = [("徳川慶喜", "Yoshinobu Tokugawa", []), ("慶喜", "Yoshinobu", []), ("吉田松陰", "Shoin Yoshida", []),
          ("女将", "landlady", [])]
    assert batches.term_problems("徳川慶喜様だ", "Yoshinobu-sama!", gl) == []
    assert batches.term_problems("吉田松陰先生", "Shoin-sensei", gl) == []
    assert batches.term_problems("女将さん", "Landlady!", gl) == []
    assert batches.term_problems("徳川慶喜", "the shogun", gl) == ['glossary 徳川慶喜 -> "Yoshinobu Tokugawa" missing']


def test_wrap_breaks_after_a_dash():
    text = "the pacification--tears flowing--again"
    lines = vwf.wrap(text)
    assert vwf.line_px("pacification--tears") > vwf.ADV_LINE_PX     # one unbreakable word before the change
    assert all(vwf.line_px(ln) <= vwf.ADV_LINE_PX for ln in lines)
    assert any(ln.endswith("--") for ln in lines)


def test_dialogue_wraps_to_the_gate():
    lines = batches.wrap_dialogue("Can you believe it? The capital is so lively!\\nNothing like Tosa.")
    assert all(vwf.line_px(ln) <= vwf.ADV_LINE_PX for ln in lines)
    assert lines[-1] == "Nothing like Tosa."      # an explicit \n forces a break
