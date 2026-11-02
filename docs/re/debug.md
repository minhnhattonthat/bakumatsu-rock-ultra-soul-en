# Debug tool (phase 2): warps, unlocks, sequences

Tool: `tools/debug/warp.py` (scene list `tools/debug/scenes.tsv`, helpers `tools/debug/pspdbg.py`). PPSSPP has no Lua, so
everything is exec breakpoints + `memory.read/write` over the QA fork's WebSocket debugger. Nothing is patched into the ISO.

Addresses are RAM addresses for the EBOOT in `rom.sha1` (PRX loaded at **0x08804000**; ELF file offset = addr - 0x08804000 +
0xC0). Strings-only EBOOT edits (phase 4+) keep them; any code change in the EBOOT must re-check this file.

## Script manager (verified: warps land on the named script, `work/qa/warp/<scene>/seq.txt` + shots)

- `*(u32*)0x08AA8480` = manager object (0x08AF72F0 on every cold boot so far; read it, don't hard-code).
- `obj + 0x26AC`: current script file name (char[64], e.g. `m_001001.bin`); `obj + 0x26EC`: start arg (0 from menus).
- `0x08888D8C(obj, name, arg)`: set next script by name (strcpy into obj+0x26AC). 12 callers (menus, script jump op).
  Breakpoint at **0x08888DAC** (just after the strcpy, `s0` = obj) and overwrite the name = warp.
- `0x08888DC4(obj, index, arg)`: same by index into the id table at **0x08A679AC**: 81 x (u32 id, char* name), e.g. 100101
  OP_001001, 200101 m_001001, 300101 ED_001001, 400101 b_001001, 900101 staffroll, 900102 "dummy". `staffroll2.bin` is not
  in the table (reached by name from a script; the name warp handles it).
- Story menu (0x088A54D0 switch): ROCKstory -> index 0 (OP_001001), Ultra Soul ROCKstory -> index 0x21 (OP_003001),
  chapter select -> index from the chapter record.
- Chapter cards (`ui_tit_101`-`113`) are drawn by the `m_0NN001` scripts themselves, so a script warp shows the card.

## Sequences (verified by the 0x08892948 hook log)

`0x08892948(mgr, name)` switches sequence. Names seen: Opening, Adventure, TopMenuAdvPause, Chapter, TopMenuSpecial,
SkitGallery, Skit, EventGallery, Event, MovieGallery, Movie, Profile, SoundGallery, TopMenuOption, TextSetting, SoundSetting,
DataManagement, KeySetting, DifficultySetting, Live, SoundGame, PlayResult, DownLoad. Not reached yet: Break.
Leftovers in the EBOOT: `SequenceDebugMenu` ("--- SELECT SEQUENCE MODULE ---", shortcuts L+triangle TestOtoGame, L+square
TestAdv, L+cross TestUI), `SequenceTestAdv` (DebugStart%d over the script list), test scripts `test_*.bin` (not on disc).
Not needed: the name warp covers the same ground. Guess: DebugMenu would draw with a debug font that may be stripped.

## System data (SYSTEM01 save, 0x1548 bytes at obj + 0x3B30; verified by poking and opening each menu)

Defaults written by 0x08887D74. Offsets below are from obj.

| Offset | What |
|---|---|
| 0x3B38 | 2 (?) |
| 0x3B40..0x4730 | guess: read-message bits (17 bits at 0x3EA5-0x3EA7 set after 40 lines of m_009003) |
| 0x474C-0x4770 | settings (difficulty, text speed, volumes...) |
| 0x4F4C | flag bits 0..0xFFF (bit n = word n>>5, bit n&31): chapter/song unlocks, profiles from bit 0x1F2, event NEW from 0x29F |
| 0x4FFC | skits: s8[70], -1 locked, else unlock order; counter at 0x5042 (accessor 0x088875F8) |
| 0x5044 | events: s8[26], -1 locked, else order 1..; counter at 0x506C (accessor 0x0888802C, unlock 0x08888070) |
| 0x5070 | u16 checksum/counter (changes on any write) |

Four 0x74-byte blocks of 0xFF from 0x4800 (29 x u32 each): guess, per-song scores per difficulty (init loop 29 x 4).
`warp.py` UNLOCK writes all of the above as "everything unlocked"; the in-memory copy is enough (nothing is saved).

## Buttons

Menus: circle OK, cross back, up/down cycle (top MENU: OPTION LIVE STORY GALLERY CHAPTER, STORY default). CHAPTER: left/right switch MAIN/BONUS
tabs (BONUS = the b_ scripts; R does nothing).
ADV: start AUTO, triangle pause MENU (PROFILE LOAD SAVE SKIT OPTION, SAVE default), select BACK LOG, square SKIP.
Rhythm game: song select circle, then ~1500 frames of intro before PRESS START works; start = PAUSE; with no input the song
ends in PlayResult ~8500 frames after start (rank E, unlock notices).

## psp.py gotchas found here

- `WS.recv` json-decodes raw bytes: the game's Shift-JIS debug printf arrives as `log` events and crashed the decode.
  `pspdbg.py` swaps in a lenient decoder.
- `cpu.stepInto` answers with a `cpu.stepping` event, not a ticketed reply (`ws.call` hangs on it).
- A crash (`memory.exception`) leaves the CPU stopped; `run_until` raises instead of waiting forever. A warp to a script name
  that does not exist crashes this way.
- Memory breakpoints report `relatedAddress` = the start of the watched range, not the accessed byte; use the pc.
