# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (research and recon) done; next is phase 2 (debug tool). No build yet.
- **Done:**
  - Step 0: repo, hooks, check, `rom.sha1`, PPSSPPHeadless boot route (`tools/routes/boot.txt`).
  - Phase 1 (`docs/re/README.md` indexes it): no earlier patch exists (only a 2014 screenshot-guide blog). ISO/CPK layout,
    CRILAYLA decompressor (`tools/crilayla.py`), unpacker (`tools/unpack.py`), GIM sweep (`tools/gimsweep.py`), plain EBOOT dumped
    (`work/eboot/EBOOT.ELF`; headless ignores ppsspp.ini, the windowed `tools/ppsspp/` build did it).
  - Text: Shift-JIS; script bytecode framing + 100-name table + jump word-offsets (`text.md`); ~13k dialogue lines (300k chars),
    121 choices, 74 staff-roll pages, 9 UI tables, ~500 lyric fragments, 3 EBOOT save titles + SFO.
  - Graphics survey: 744 Japanese GIMs (`docs/re/graphics-survey.tsv`), movies, XMB. Tests: `tests/test_formats.py`.
  - Tour: `work/states/mainmenu.ppst` (STORY menu after boot.txt), `work/qa/tour1-3`.
- **Next (phase 2, debug tool):** warp to any scene: find the current-script / chapter id in RAM (ramsearch over
  `memory.read` dumps while changing chapters via Chapter Select), poke + trigger load over the WebSocket (`psp.py`), scene list in
  `tools/debug/` covering every chapter card (b_/m_ chapters), endings ED_001-008, OP_, staffroll, each menu (option, gallery,
  skit, profile, sound, movie), rhythm game (song select, pause, results, break screen), save/load dialogs. Cheats ini is an option.
  Note: `--mash-key circle` did not advance ADV text in tour3 (stuck on one line); explicit presses every 300 frames did (tour2).
- **Phase 3/4 notes:** identity = `cpk.rebuild` with no edits + `iso9660.patch`; INST.DNS (install data) may mirror INST.CPK:
  check. Script insertion must re-map jump args (`text.md` list) when string lengths change.
- **Phase 5 (big item):** ADV dialogue is vertical text in small manga panels; find the renderer's direction flag/box metrics in
  the EBOOT, decide horizontal English layout + VWF on the KFNT fonts.
- **Open bugs:** none.
- **Waiting on the user** (non-blocking; defaults in use):
  - Song MVs (`mv_*.pmf`) have burned-in Japanese lyric typography: default leave as is (PSMF re-encode out of scope).
  - Rhythm-game lyric fragments (words on notes, timed to sung syllables): default romanized Hepburn, since English word order
    can't follow the syllable timing.
  - 誠 on 誠仮面's mask / Shinsengumi crests: default keep (costume/crest art).
