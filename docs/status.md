# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) **done**; next is phase 6 (translate). Done: insertion pipeline, marker
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
      work/mark`), sha1 fb1f45606196f1ece1d32850fdcfdc264a2f0044 (smoke exit 0 on the previous, NUL-fix-only-different build).
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
- **Open bugs:** `warp.py live_pause` dies with `JSONDecodeError` from the driver (psp.py's lenient JSON patch covers
  `log` events but not this one): the scene itself was fine in phase 2, so it is a driver/timing regression to re-check.
- **Waiting on the user** (non-blocking; defaults in use):
  - Song MVs (`mv_*.pmf`) have burned-in Japanese lyric typography: default leave as is (PSMF re-encode out of scope).
  - Rhythm-game lyric fragments (words on notes, timed to sung syllables): default romanized Hepburn, since English word order
    can't follow the syllable timing.
  - 誠 on 誠仮面's mask / Shinsengumi crests: default keep (costume/crest art).
  - **Plain-ELF EBOOT (D12, replaces D11)**: English dialogue needs a small EBOOT code patch, so the build ships the
    decrypted EBOOT.BIN (PPSSPP and CFW run it; a patched ISO can't run elsewhere anyway) and translates its 8 save
    titles too. Default in use; say so if you want a different trade-off.
