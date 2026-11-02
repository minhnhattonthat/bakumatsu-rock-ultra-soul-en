# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2 (debug tool) done; next is phase 3 (identity build). No build yet.
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
- **Next (phase 3, identity build):** `cpk.rebuild` with no edits + `iso9660.patch` -> byte-identical ISO, as a test. Check
  whether INST.DNS mirrors INST.CPK. Then `tools/build.py` skeleton (check_rom first). Run `warp.py --all --iso build/...` on
  the identity ISO.
- **Phase 3/4 notes:** script insertion must re-map jump args (`text.md` list) when string lengths change. Debug addresses in
  `docs/re/debug.md` assume an unchanged EBOOT code segment (string-only edits are fine).
- **Phase 5 (big item):** ADV dialogue is vertical text in small manga panels; find the renderer's direction flag/box metrics in
  the EBOOT, decide horizontal English layout + VWF on the KFNT fonts.
- **Open bugs:** none.
- **Waiting on the user** (non-blocking; defaults in use):
  - Song MVs (`mv_*.pmf`) have burned-in Japanese lyric typography: default leave as is (PSMF re-encode out of scope).
  - Rhythm-game lyric fragments (words on notes, timed to sung syllables): default romanized Hepburn, since English word order
    can't follow the syllable timing.
  - 誠 on 誠仮面's mask / Shinsengumi crests: default keep (costume/crest art).
