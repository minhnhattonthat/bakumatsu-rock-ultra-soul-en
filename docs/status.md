# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5 (engine spike + marker build) **in progress**. Done: insertion pipeline, marker build (boots, ids show in
  every toured box), horizontal-vs-vertical renderer finding, provisional width table. Open: make ADV dialogue
  horizontal in the EBOOT (the phase-5 blocker), then the real width gate and the glyph torture line.
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
      `story_menu`), profile, option, chapter, skit, event.
    - Engine finding (see `docs/re/text.md` §7): the engine draws **horizontal** text (menu rows, help line, backlog) and
      **vertical rotated** text (ADV panels) with the same KFNT font. ASCII exists in the font, so English needs the
      horizontal path, i.e. ADV engine work in the EBOOT (D10).
    - `tools/measure.py`: text-extent measurement from shots (crop/zoom via sheet.py for the visual read).
- **Next (finish phase 5):** make the ADV text horizontal. Anchors: font metric read at `0x088066a4` (from `0x0880543c`),
  KFNT RAM copies 0x96fdaec / 0x978445c, per-line work in 0x089a0000-0x089b0000, menu/backlog horizontal path unlocated.
  Look for the text object's direction/layout field and the panel rect source; the panel art is `msgBord*.gim`; the D2C
  layout files may carry the rect. Then: widen/re-lay the box, re-measure the width gate per variant, boot a **glyph
  torture line** (all printable ASCII + double spaces), and run `jp_left.py` on the marker build.
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
  - **PSP save-dialog titles (EBOOT)**: translating them means shipping a plain-ELF EBOOT.BIN (fine in PPSSPP/CFW, not
    guaranteed on real hardware). Default: keep the encrypted EBOOT, those 8 titles stay Japanese (D11). Say the word and
    the build switches to `insert.py --eboot`.
