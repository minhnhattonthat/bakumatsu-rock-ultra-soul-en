# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9 (release) **done, published** (D16, 2026-11-03): repo public, release v1.0
  https://github.com/minhnhattonthat/bakumatsu-rock-ultra-soul-en/releases/tag/v1.0 (zip sha1
  6b5e82314d9ab126f01169a54363ad5ecc513599, download re-checked). Repo description = game title. Next: player bug
  reports (GitHub issues), the INST.DNS install-path patch if wanted.
- **Release v1.0** (2026-11-03): `tools/release.py` exit 0 -> `release/Bakumatsu_Rock_Ultra_Soul_EN_v1.0.zip`
  (xdelta 7,977,825 bytes, sha1 0cf4239d60760caec48cf29763f823ba5798ab8d, + README.txt). Patched image = build
  sha1 72fc332bc96076e1d86c5e7436e60ad57f4ecf17 (CRC32 588ae4c5). Steps all passed: build (isodiff), tests 40/40,
  smoke exit 0, jp_left 0 runs (24,407 records), visual gate 152/152, story gate 21/21, polish 0 unticked, debug off,
  re-applied to the clean original with plain `xdelta3 -d` -> same sha1. xdelta needs `-B 1879048192` (source window
  = whole ISO): the default 64 MB window gave a 994 MB patch.
- **Phase 9** (2026-11-03): skit balloon centring fixed in the EBOOT (`insert.TEXT_CODE` 0x088545d4..fc: line
  measured with 0x08805524 = font advances; `text.md` §8 "Skit balloons", incl. the relocatable-ELF jal gotcha),
  in game on `gallery_skit_more`, visual QA r4 (3 re-shot skit sheets, `verdicts/r4_chunk_000.tsv`) -> gate 152/152.
  polish.md: 0 unticked. README in `release.py`: Redump search link, cold-boot note.
- **Phase 8 done** (2026-11-03): build 73788b787f8bb8315e5db97f7fe3d2f44174112b, smoke exit 0, tour 137/137 warps ok,
  visual QA round 3: 152/152 sheets ok (`qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` exit 0; 5 reviewers
  on 150 sheets, `gallery_skit_more` (new row) read by the controller); story gate 21/21. No game-over screen exists
  (lives only score); chapter cards 1-10, credits (staffroll, staffroll2) English in the tour.
  - Phase 7 review fixed (45f77d0): isodiff checks dir/PVD bytes, unedited extents, the appended tail;
    `tests/test_build_en.py` builds the English ISO from `script/` (read-back included) + a negative dir-record test;
    `insert.py plan` log crash.
  - **Graphics pipeline** `tools/gfx.py`: `gfx/text.tsv` (key, style, en, opts) -> `gen` renders `gfx/<key>.png`
    (fonts/: Anton, Bangers, Archivo Black, PT Serif Bold; styles in `gfx.STYLES`; opts keep/erase/flat/smear/clear/
    box/rot/glow/maxsize/fill/stroke; repeated key = several labels in one image; `PAGE:<file>` = a picture cut into
    32-px strips) -> `build.edits()` encodes each PNG into its GIM and writes every copy (`work/gim/index.tsv`).
    `gfx.py show OUT GLOB` (orig|new sheet), `gfx.py info GLOB` (colour rects). `tests/test_gfx.py`.
  - Done (rows in text.tsv): all sys_* menus/labels/titles, chapter cards ui_tit_101-113, unlock notices adv_300-302,
    quick-save prompt, FANS UP, ADV end-menu buttons adv_002, break screen, pause items, song title logos gam_200,
    HOW TO PLAY panels + manual page (sys_021), hint bars, 88 soul-word tiles gam_605-692 (English ruby word split
    over the tiles). In game ok: option_text/sound/data, story_menu, chapter_enter (card "Chapter 1 / Destiny,
    Fate, / Rock of Passion").
    Also done: SFX (romaji per kana piece, whole words English, leftover stroke/dakuten pieces blank, ー/〜 kept),
    fan medals 10K..50K, ending narration adv_050/051, Ryoma card adv_220, name cut-ins adv_009, Ikumatsu "Asleep".
    Kept Japanese by D14 (scene-art signs, 誠 crests, 秘 seal, flyer props, logo); `bg_011` (dev caption) is unused.
  - Fixes from QA: `\fnt1` big-font words were invisible in horizontal ADV -> `insert.load_texts` drops
    `\fnt1/\fnt0` from scene `en` (73 entries render in font17). CHAPTER select rows clip at 241 px: 7 long
    titles shortened, lint rule `CHAPTER_ROW_PX`.
  - In game: chapter cards 1-10 English (`warp.py chapter_card_02..13`; list rows 11-13 are ending routes, no card
    in the original either). Tour `--all` 123/123 ok on the English build and the original (`work/qa/tour`,
    `work/qa/tour_jp`, `*_sheet.png`; menu_top uses final.png). Visual QA: `docs/visual-qa-brief.md`,
    `qa_gate.py` manifest `work/qa/manifest.tsv`, chunks `work/qa/chunks/`, verdicts `work/qa/verdicts/`.
  - Visual QA round 1 (5 read-only reviewers, 135 sheets) found, now fixed: UI-table text printed a literal `\n`
    (boot/autosave/data-link notices: `insert.load_texts` turns `\n` into 0x0A for `ui/`, as the JP has); profile
    box row 7 and the back log's 2nd line clipped (`vwf.DROP` 4 -> 0); ULTRA difficulty label went black when
    tinted (no stroke); chapter cards off-centre (`gfx` title rows keep the canvas centre); b_017001 stub line,
    b_006002 wording. Checked, not bugs: ADV card text behind the pause menu (the original does it too), the
    "--Edo" dash (drawn), ui_system_text 0x5d80. font24 had blank ASCII: `vwf.font24()` now ships Latin glyphs.
  - Visual QA round 2 (after the round-1 fixes): 3 issues, fixed: SFX textures that are kana atlases (the game
    draws one sprite per kana piece and re-arranges them: adv_260/265/271/279/287/293/320/336/337/339, found by
    sprite-quad count in the D2C) now carry romaji per piece (`box=` per connected component, ー/! pieces kept);
    SQUEEZE kept inside its sprite; Bangers italic overhang was clipped by typeset's layer (gfx.fit pads it).
  - Polish pass: all 47 earlier polish.md lines (43 fixed, 4 waived). Memstick-space notice: the number now starts
    its own line (the game joins "at least" + number).
  - Story pass (`tools/story.py` -> `work/qa/story/chapters/*.txt`, 21 files; reviewer brief
    `docs/story-reviewer-brief.md`; verdicts `work/qa/story/verdicts/`): 21/21 ok, one Important fixed
    (m_006001:0x34928 Ryoma's 風流 line), 117 Minors -> polish.md "Story pass" section. Speaker column is "-" (the
    speaker op isn't decoded), reviewers inferred speakers.
  - **Back log speaker labels fixed** (2adec6e): op 0x37 `217, x, W` holds the word offset of the op-0x19 table's
    first slot; resized slots before the table left it stale (labels read other script bytes or nothing). insert.py
    re-maps it by slot (`TABLE_REF_OP`, self-check + test). Proof: a same-size-slot build had labels, a build growing
    one early slot lost them; RAM showed the back log buffer `#NN<text>` (NN = speaker index). Labels: 96 px per
    line, `\n` = 2nd line ("Ryoma\nSakamoto", "Ryoma/\nTakasugi"), lint `LABEL_PX`. "Fewer entries" was the route:
    English lines type out longer, so some circle presses finish the line instead of advancing.
    `tools/debug/ramdump.py STATE OUT` dumps RAM from a state.
  - Story-pass minors: all 117 applied (90f3c52); Ryoma's ピッツァ/ぴっつぁ = "peetsa" everywhere (brief updated).
  - jp_left: `tools/textscan.py` (every text record read back from the built ISO) + `jp_left.py` -> 0 runs.
  - Tour: `warp.py --all --sheet --iso build/bakumatsu_rock_us_en.iso` (**warp's default ISO is the JP ROM**), then
    `tools/tour.py` (every sheet page -> `work/qa/tour/`, 150 sheets), then `qa_gate.py init`.
  - Visual QA round 3 (every sheet page; rounds 1/2 only saw page 1): 0 issues. Notes, ok: skit balloon lines sit
    left of centre (engine centres at 8 px/byte; polish.md item), b_007001 "What an insult~" keeps a `~`.
- **Phase 7 done** (2026-11-03): build green.
  - `tools/lint.py` over every `script/` entry (in `tools/check.py` via `tests/test_lint.py`): ADV px/lines, byte
    slots, control codes, non-ASCII/leftover JP, glossary (on the unwrapped text), ordinals, blanks, one-word last
    lines; `script/keep_jp.txt` (play/* lyrics, D13). 0 errors.
  - `tools/isodiff.py`, run by every `build.py`: no ISO sector, CPK entry, UI-table byte, EBOOT or SFO byte changed
    outside the plan; plus a read-back of every `en` from the files the plan wrote. Found and fixed: staffroll2's own
    speaker names were silently dropped (`insert.patch_script(names=)`).
  - Balanced wrap (`vwf.wrap`; `batches.py rewrap` re-wrapped 5,942 boxes whose breaks were all greedy ones).
  - Speaker names 桂子/総美 now match the glossary (Keiko, Somi); staffroll2 未定 -> TBD.
  - **EBOOT text the phase 4 scan missed** (`text.md` §4): 9 profile labels + save-detail "Play time" (new
    `eboot.json` slots), code-built strings patched by immediates (`insert.TEXT_CODE`: h/m/s, "Choose"), and a
    **crash fix**: chapter end did `strstr(title, "話")` and a NUL result wraps a memcpy; now searches ':' and appends
    " Done" (`insert.CHAPTER_CODE`, test keeps ':' in chapter titles 2-11, 34-36). `extract.py verify` now scans all
    EBOOT data; `tools/debug/sbscan.py` finds code-built strings.
  - In game (build sha1 df0b3f193d0a6b6a64955ae6397fa338f947409d, smoke exit 0): warps `ch1_end` (new: chapter 1
    played to its end in SKIP -> unlock toasts, autosave, BREAK, next chapter; RAM game state "Chapter 1: Done"),
    `adv_save_done` (new: memstick SAVEDATA_DETAIL "Play time  0h 1m20s / Chapter 1: ..."), `gallery_profile_view`
    (new: English labels fit), staffroll2, m_001001 ok. warp ARG `FILE.bin>NEXT.bin` asserts a run that plays on.
- **Next (phase 8):** full warp tour (`--all`) + visual-QA verdicts (`qa_gate.py`), fix overflow; graphics text (744
  GIMs incl. the unlock toasts `adv_300_*`, BREAK screen, chapter cards); jp_left on the build. Known gaps below.
- **Phase 6 done** (2026-11-02): b001-b119 (16,267 entries: every scene line,
  choice, UI table, skit, profile, save title, SFO title, staff roll) translated, `batches.py check` OK on all, every
  batch reviewed (no Critical/Important left; minors in `docs/polish.md`), merged into `script/`. Lyrics (play/) stay
  Japanese (see Waiting on the user). `work/tl/` is gitignored; `script/` holds the result.
  English build: `tools/build.py` -> smoke exit 0; warps ok: boot_autosave, chapter_main, gallery_profile,
  gallery_skit_view, gallery_event_view, live_play, m_005001, b_013001, ED_002001, staffroll (English renders in ADV
  panels and the staff roll).
- **Known gaps for phase 8:** menus in font24 are monospace 8 px (profile names cramped), staff-roll two-column cast lines are ragged
  (proportional font), chapter title cards / menu art are Japanese graphics (744 GIMs, graphics survey), skit balloon
  widths unchecked in game, ui_system_text line counts kept as JP, ui_profile zodiac slots 7 bytes ("Goat", "Archer",
  "Aquar.").
- **Phase 5** (engine spike + marker build) **done**. Done: insertion pipeline, marker
  build, **horizontal ADV dialogue centred on every panel** (script ops + 9-word EBOOT patch, D12), PT Serif VWF in
  font17, ADV width gate 112 px x 8 lines on all four panel variants, torture line, every box variant measured
  (`text.md` §7 table + §8), fixed-slot NUL fix (skit run-on).
- **Done:**
  - Step 0: repo, hooks, check, `rom.sha1`, PPSSPPHeadless boot route (`tools/routes/boot.txt`; `menu.txt` = to top MENU).
  - Phase 1 (`docs/re/README.md` indexes it): no earlier patch exists. ISO/CPK layout, CRILAYLA, unpacker, GIM sweep, plain
    EBOOT (`work/eboot/EBOOT.ELF`). Text: Shift-JIS script bytecode (`text.md`), UI tables, EBOOT save titles. Graphics survey:
    744 Japanese GIMs (`docs/re/graphics-survey.tsv`).
  - Phase 2: `tools/debug/warp.py` + `scenes.tsv` (120 scenes: all 80 scene scripts by file name incl. endings, OPs, both
    staff rolls; boot notices + title; every top/story/chapter/gallery/option/live screen; rhythm game play, pause, result;
    ADV auto/menu/save/load/backlog/skip). Cold boot each (cached MENU state per ISO), everything unlocked by RAM pokes,
    script warp = breakpoint on the script-name setter. Each run asserts the loaded script / entered sequence; proof shots
    `work/qa/warp/<scene>/`. `--all` -> states in `work/states/warp/`. How it works: `docs/re/debug.md`.
  - Phase 3: `tools/build.py` (check_rom -> `cpk.rebuild` both CPKs with `edits()` -> `iso9660.patch`), ~7 s. No edits =
    byte-identical ISO (`tests/test_identity.py`, plus an edited-CPK read-back test). Fixed 3 bugs in the skill's
    `cpk.rebuild` (untouched compressed files got ExtractSize = FileSize; last file unpadded; name-only keys hit INST's two
    `com_000.gim`). In-game proof that raw-stored replacements load: all 224 compressed NOINST files + all 80 scene scripts
    stored decompressed -> 9 warps ok. Smoke passes on the build.
  - Phase 4: `tools/textfmt.py` (cp932 codec + JSON writer), `tools/mzscript.py` (MZ bytecode parse/serialize), `tools/uitable.py`
    (the 9 UI tables + EBOOT/SFO slots), `tools/extract.py` (`dump`, `verify`). `script/`: 121 JSON files, 27,815 entries,
    355k JP chars. Every file reserializes byte-identically, every slot re-encodes exactly, 0 Japanese runs outside slots.
    `tests/test_extract.py` (8 tests).
  - Phase 5 (this session):
    - `tools/insert.py`: `script/` -> CPK edits. MZ scene/chart files are rebuilt with **resized string slots** and every
      jump argument re-mapped (positions verified over all 80 scripts, re-checked after the rebuild); the shared op-0x19
      speaker table is applied by index; UI tables are in-place with an overflow error; PARAM.SFO title too; the EBOOT save
      titles are off by default (`--eboot`, D11). `insert.py check` = identity; `tests/test_insert.py` (8 tests).
    - `tools/mark.py` -> `work/mark`: 27,808 markers (`[id] The quick brown fox...`). `tools/build.py --texts work/mark`
      builds the marker ISO; it boots (`emu.py --smoke` exit 0) and warps ok. Every toured box shows its id: ADV dialogue
      (vertical, `work/qa/warp/m_001001`), backlog (horizontal, `adv_backlog`), music list + help line (`gallery_music`,
      `story_menu`), profile, option, chapter, skit, event. **`build/bakumatsu_rock_us_en.iso` currently is that marker
      build** (sha1 587a1a66008deeaba49b0c0022b1830e9adfa66e); plain `tools/build.py` (empty `en`) rebuilds the
      byte-identical identity ISO, so pass `--texts work/mark` to reproduce the marker one.
    - Engine finding (see `docs/re/text.md` §7): the engine draws **horizontal** text (menu rows, help line, backlog) and
      **vertical rotated** text (ADV panels) with the same KFNT font. ASCII exists in the font, so English needs the
      horizontal path, i.e. ADV engine work in the EBOOT (D10).
    - `tools/measure.py`: text-extent measurement from shots (crop/zoom via sheet.py for the visual read).
    - **Horizontal ADV** (`docs/re/text.md` §8): `insert.py` rewrites op 0x4D mode 2 -> 0 and op 0x4E pitch 24 -> 16 /
      gap 0 for boxes 0-2, and patches 9 EBOOT words (`ADV_CODE`) so the engine's block-centring pass (0x0881430c)
      runs for mode 0 with row axes. English sits centred in rounded, octagon, spiky and caption panels
      (`work/qa/gate_c.png`, gate build from a scratch script: every m_001001 line = the wrapped pangram). The EBOOT now
      ships as plain ELF whenever scene text is English (D12), save titles included.
    - `tools/kfnt.py` (KFNT decode/encode, byte-identical), `tools/vwf.py` (PT Serif 12 px into font17, `wrap()`, gate
      constants `ADV_LINE_PX = 112`, `ADV_LINES = 8`), `tools/debug/widths.py` (engine glyph widths ->
      `tools/adv_widths.tsv`), `tools/debug/mips.py` (EBOOT disassembly: `dis`, `func`, `callers`).
      `tools/mark.py --torture` puts ASCII/double-space/full-box torture lines in m_001001.
    - **`build/bakumatsu_rock_us_en.iso` = marker build** (`tools/mark.py --force --torture`, then `tools/build.py --texts
      work/mark`), sha1 fb1f45606196f1ece1d32850fdcfdc264a2f0044 ; smoke exit 0.
- **Next (phase 6):** read `references/translation.md`; build the batch tooling (work/tl batches, translator/reviewer
  agents per `.claude/agents/`), and a width lint that enforces `vwf.ADV_LINE_PX`/`ADV_LINES` on dialogue with explicit
  `\n` breaks (engine char-wrap breaks centring) plus byte slots (NUL included) for fixed files. Notes: menus drawn
  with font24 are still monospace 8 px (only font17 has the VWF); `jp_left.py` on the marker build not run yet.
- **Phase 4+ notes:** script insertion re-maps jump args (`text.md` §1/§7) when string lengths change; the marker build
  proves it in game. Debug addresses in `docs/re/debug.md` assume an unchanged EBOOT code segment (string-only edits are
  fine; the EBOOT is not patched at all by default now).
- **Phase 5 (install data):** INST.DNS = PGD-encrypted INST.CPK; a player who used Options > data management would read the
  original Japanese INST from the memstick. Plan: EBOOT patch renaming the install path it probes (`containers.md`), so it
  always reads the UMD. Build leaves INST.DNS untouched.
- **Open bugs:** rhythm charts: a lyric slot that changes size makes `live_play` halt (jump to 0 after chart load);
  probably a chart offset that is not a known jump arg. Same-size lyric edits work (fixed: insert rewrote 0 `words`
  header fields as 1, test `test_same_size_lyric_changes_only_its_bytes`).
  `warp.py live_pause` dies with `JSONDecodeError` from the driver (psp.py's lenient JSON patch covers
  `log` events but not this one): the scene itself was fine in phase 2, so it is a driver/timing regression to re-check.
- **Waiting on the user** (non-blocking; defaults in use):
  - Song MVs (`mv_*.pmf`) have burned-in Japanese lyric typography: default leave as is (PSMF re-encode out of scope).
  - Rhythm-game lyric fragments (words on notes, shown on a hit, timed to sung syllables): default now **keep
    Japanese**. Romaji doesn't fit the fixed slots (刺激を -> "shigeki o", 9 chars in 7 bytes) and resized chart slots
    crash; the songs are sung in Japanese and the MVs keep Japanese lyrics anyway. Say so if you want romaji
    (needs the chart resize fix first).
  - 誠 on 誠仮面's mask / Shinsengumi crests: default keep (costume/crest art).
  - D14: Japanese painted into scene art (shop signs, lanterns, banners, 秘 seal, flyer props, 幕末Rock logo) kept;
    say so if you want any of it repainted. Chapter list titles shortened to fit (e.g. "Chapter 8: Guilty Rock,
    Execution Idol"); the chapter cards keep the full titles.
  - **Plain-ELF EBOOT (D12, replaces D11)**: English dialogue needs a small EBOOT code patch, so the build ships the
    decrypted EBOOT.BIN (PPSSPP and CFW run it; a patched ISO can't run elsewhere anyway) and translates its 8 save
    titles too. Default in use; say so if you want a different trade-off.
