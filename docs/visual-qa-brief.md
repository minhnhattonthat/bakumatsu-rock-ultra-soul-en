# Visual-QA reviewer brief - Bakumatsu Rock: Ultra Soul (PSP)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same file names) and `glossary.md`.

## How to look
- `$SKILL` = the output of `python tools/skill.py` (run from the repo root).
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible (text or graphics: menus, cards, signs, SFX);
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a scene still loading after a warp; a black first frame;
- anything identical in the original's sheet.
- Rhythm-game lyric fragments in Japanese during play (decision D13 keeps them).
- Dialogue drawn horizontally in the ADV panels instead of vertically (D10, intended).
- Japanese painted into scene art, kept by decision D14: shop signs, lanterns and banners in backgrounds and event
  CGs, the 誠 crest (masks, drapes, banners), the 秘 seal on a notebook, 新選組 on the flyer/ticket props, the
  onmyo disk, door calligraphy, and the 幕末Rock title logo. Japanese in a menu, title card, notice, button, SFX or
  label is still an issue.
- Profile list / NAME bar initials "S. Takasugi", "T. Hijikata", "T. Suzuki", "T. Morikawa", "S. Morikubo" (D15: the
  slot is 15 bytes).
- ADV caption-card text faintly visible behind the pause menu panel (the original shows its card text there too).
- Ending routes (chapter list rows 11-13) start without a chapter card, as in the original.
- CHAPTER list rows are shorter forms of the chapter-card titles (the rows clip at 241 px), e.g. card "Rock of
  Passion", row "Passion Rock".
- Manga SFX built from kana pieces (one sprite per kana, re-arranged by the game) show romaji per piece ("GO O O O
  O", "DO GO O N", "WA A A"); a ー or ! piece stays as drawn. Whole English words are for one-sprite SFX.
- Full-size frames: `work/qa/warp/<scene>/f<frame>.png` (every 120 frames) are the English frames the sheets were
  made from; zoom those before calling a glyph missing.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
