"""English graphics (tools/gfx.py): every gfx/<key>.png is a known GIM of the same size, every text.tsv row has its PNG,
and the encoded GIM decodes back close to the PNG (palette loss shows up here, not in game). Skips without work/gim."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import gim  # noqa: E402

need = pytest.mark.skipif(not (ROOT / "work" / "gim" / "index.tsv").exists(), reason="no work/gim")


@need
def test_rows_have_pngs():
    idx = gfx.index()
    have = set(gfx.pngs())
    for key, style, en, opts in gfx.rows():
        assert key in idx, key
        assert style in gfx.STYLES, (key, style)
        assert key in have, f"{key}: run tools/gfx.py gen"


@need
def test_encode_round_trip():
    from PIL import Image
    worst = []
    for key in gfx.pngs():
        g = gfx.encode(key)
        w, h, rows = gim.to_rgba(g, gim.parse(g)[0])
        back = Image.frombytes("RGBA", (w, h), b"".join(rows))
        png = Image.open(os.path.join(gfx.GFX, key + ".png")).convert("RGBA")
        assert back.size == png.size, key
        a, b = png.tobytes(), back.tobytes()
        bad = sum(1 for i in range(3, len(a), 4) if abs(a[i] - b[i]) > 96)   # alpha flipped = a lost stroke or hole
        if bad > len(a) // 4 // 50:
            worst.append((key, bad))
    assert not worst, worst
