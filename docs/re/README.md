# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| `containers.md` | ISO layout, CPK + CRILAYLA, D2C, CANZ, KFNT font, PMF, EBOOT dump | CPK/CRILAYLA verified; D2C/CANZ/KFNT guess |
| `text.md` | Shift-JIS (+UTF-8 system dialogs), script bytecode, op 0x62/0x51/0x4C/0x19 strings, control codes, jump word-offsets, UI tables, EBOOT strings, lyrics | encoding + framing verified; offset-arg list statistical (verify with resize test) |
| `debug.md` | debug tool: script manager + id table, sequence names, system-data unlock layout, button map, psp.py gotchas | verified by warps (`tools/debug/warp.py`) |
| `graphics.md` + `graphics-survey.tsv` | graphics-text survey: 744 Japanese GIMs by kind, movies, XMB, vertical ADV box | static sweep complete; tour partial (mid-game screens need phase-2 warps) |
