"""The warp scene list parses, its routes are valid psp.py routes, and every script scene names a script on the disc."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "debug"))
warp = pytest.importorskip("warp")   # needs the skill (psp.py) via tools/skill.py
SCRIPTS = ROOT / "work" / "cpk" / "INST" / "scene" / "script"


def test_scene_list_parses():
    rows = warp.load_scenes()
    assert len(rows) > 100
    for r in rows.values():
        route = r["arg"].partition(";")[2] if r["kind"] == "script" else r["arg"]
        warp.D.psp.parse_route(route)          # exits on an unknown button
        assert r["frames"] > 0


def test_every_script_has_a_scene():
    if not SCRIPTS.exists():
        pytest.skip("no work/cpk")
    rows = warp.load_scenes()
    args = [r["arg"].partition(";")[0] for r in rows.values() if r["kind"] == "script"]   # FILE.bin[>NEXT.bin]
    named = {n for a in args for n in a.split(">")}
    on_disc = {p.name for p in SCRIPTS.glob("*.bin")}
    assert named <= on_disc, named - on_disc       # a missing name crashes the game on load
    assert on_disc <= named, on_disc - named
