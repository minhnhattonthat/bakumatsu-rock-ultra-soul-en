# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 4 (extract) done; next is phase 5 (engine spike + marker build). Build = identity (no edits yet).
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
    stored decompressed -> 9 warps (title, menu, options, profile, live, ADV, backlog, ending) ok, shots match the original
    apart from animation. Smoke passes on the build.
  - Phase 4: `tools/textfmt.py` (cp932 codec + JSON writer), `tools/mzscript.py` (MZ bytecode parse/serialize), `tools/uitable.py`
    (the 9 UI tables + EBOOT/SFO slots), `tools/extract.py` (`dump`, `verify`). `script/`: 121 JSON files, 27,815 entries,
    355k JP chars — 13,059 dialogue, 121 choices, 78 staff, 100 shared speaker names (+2 staffroll2 overrides), 11,439 lyric
    fragments, 3,003 UI strings, 8 EBOOT save titles + XMB title. Every file reserializes byte-identically (`serialize(parse(b)) == b`),
    every slot re-encodes exactly, and a mask-and-scan finds 0 Japanese runs outside extracted slots. UI record layouts
    derived and documented in `text.md` §3; 46 system-text records are UTF-8 (kept per slot). `tests/test_extract.py` (8 tests).
- **Next (phase 5, engine spike + marker build):** vertical ADV text + KFNT fonts (17/24 px). Decide the English layout
  (horizontal? box metrics? VWF on KFNT), then marker build = every line `[id] ...` and the width gate per box variant.
  Also: EBOOT patch renaming the install path (INST.DNS, below); marker build + `jp_left.py` will confirm nothing was missed.
- **Phase 4+ notes:** script insertion must re-map jump args (`text.md` list) when string lengths change. Debug addresses in
  `docs/re/debug.md` assume an unchanged EBOOT code segment (string-only edits are fine).
- **Phase 5 (install data):** INST.DNS = PGD-encrypted INST.CPK; a player who used Options > data management would read the
  original Japanese INST from the memstick. Plan: EBOOT patch renaming the install path it probes (`containers.md`), so it
  always reads the UMD. Build leaves INST.DNS untouched.
- **Phase 5 (big item):** ADV dialogue is vertical text in small manga panels; find the renderer's direction flag/box metrics in
  the EBOOT, decide horizontal English layout + VWF on the KFNT fonts.
- **Open bugs:** none.
- **Waiting on the user** (non-blocking; defaults in use):
  - Song MVs (`mv_*.pmf`) have burned-in Japanese lyric typography: default leave as is (PSMF re-encode out of scope).
  - Rhythm-game lyric fragments (words on notes, timed to sung syllables): default romanized Hepburn, since English word order
    can't follow the syllable timing.
  - 誠 on 誠仮面's mask / Shinsengumi crests: default keep (costume/crest art).
