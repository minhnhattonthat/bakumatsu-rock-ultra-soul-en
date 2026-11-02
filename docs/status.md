# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (repo setup) done; next is phase 1 (research and recon). No build yet.
- **Done:**
  - Template files, `tools/skill.py`, `tools/iso9660.py`, `tools/check.py` + `tests/test_rom.py`, pre-commit hook in `tools/hooks/` (`core.hooksPath`), verified: a failing test blocks the commit.
  - `rom.sha1` pinned (SHA-1 4fa0409f0a547cc4250a34c8ef5ac5b62bdd1cb2, 1,699,610,624 bytes).
  - PPSSPPHeadless QA fork (machine-wide) boots the original ISO: `tools/routes/boot.txt` reaches the main menu (input works). PPSSPP v1.20.4 in `tools/ppsspp/` for the EBOOT dump / human play. Guard hook (plugin) blocks `sed -i` and heredocs.
  - ISO layout: `PSP_GAME/USRDIR/INST.CPK` (507 MB), `NOINST.CPK` (558 MB), `INSDIR/INST.DNS` (515 MB, install data), `content/THEME/*.PTF` (6 PSP themes), `SYSDIR/EBOOT.BIN` (encrypted), `SYSDIR/UPDATE/` (firmware update, leave alone).
  - Boot shows menus drawn as graphics (MENU / OPTION / LIVE / STORY / GALLERY / CHAPTER, help line in Japanese at the bottom).
- **Next (phase 1):** earlier patches/research; dump decrypted EBOOT (PPSSPP `DumpFileTypes = 7`); `cpk.py list` both CPKs, find the script format, encoding, pointer tables, font; graphics-text survey (GIMs, PTF themes, ICON0/PIC1, movies). Record in `docs/re/`.
- **Open bugs:** none.
- **Not verified in Step 0:** PPSSPP has no Lua in emu.py (no probe-log check possible; memory reads go through the WebSocket API). The windowed `tools/ppsspp/` GUI's keyboard input was not tested headlessly (stock default key map).
- **Waiting on the user:** nothing.
