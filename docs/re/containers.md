# Containers and file formats

Dump: `rom.sha1`. Unpack order: `python tools/iso9660.py x ROM work/iso` -> `python tools/unpack.py [--glob PAT] [INST|NOINST]`
(writes `work/cpk/<CPK>/<dir>/<name>`, CRILAYLA-decompressed) -> `python tools/gimsweep.py` (GIM index + sheets).

## ISO (verified: `iso9660.py list`, `tests/test_rom.py`)

| Path | Size | What |
|---|---|---|
| `PSP_GAME/SYSDIR/EBOOT.BIN` | 3,737,760 | encrypted (`~PSP`); plain ELF dumped to `work/eboot/EBOOT.ELF` (same size, sha1 b2695778dcb55c3884c3bbd5c76e97c03128fc61) by windowed PPSSPP with `DumpFileTypes = 7` (headless ignores ppsspp.ini); text in `text.md` §4 |
| `PSP_GAME/USRDIR/INST.CPK` | 507 MB | 1,859 files: `scene/script` (80 ADV scripts), `play/script` (29 rhythm charts `otoNN.bin`), `scene/graphics` (1,174), `play/graphics` (311), `scene/mask` (47), `sound` (218 acb/awb) |
| `PSP_GAME/USRDIR/NOINST.CPK` | 558 MB | 305 files: `systemdata` (9 UI text tables), `font` (2), `ui/graphics` (152), `eff` (27), `movie` (34 pmf + `movie_list_info.mil`), `sound`, `content/SAVEDATA` (3 PNG) |
| `PSP_GAME/INSDIR/INST.DNS` | 515 MB | install data (the game copies INST.CPK content to the memstick; guess: same bytes as INST.CPK, check before building) |
| `PSP_GAME/PARAM.SFO` | 604 | TITLE `幕末Rock 超魂` (UTF-8, 128-byte slot) |
| `ICON0.PNG`, `PIC1.PNG`, `INSDIR/*`, `SND0.AT3` | | XMB art: only the 幕末Rock logo (kept, D5: no official English logo) |
| `USRDIR/content/THEME/THM_V_0[1-6].PTF` | ~300 KB each | PSP XMB themes (installable bonus); not surveyed yet (low priority) |
| `SYSDIR/UPDATE/` | | firmware 6.60 update, leave alone |

**Free space:** not a constraint. Edited files go back through `cpk.rebuild` (re-lays the CPK) and `iso9660.patch` (a file that
grows moves to the image end). Only fixed slots (UI tables, EBOOT strings, SFO) have hard size limits.

## CPK (verified: `cpk.py list` on both; `tools/cpk.py` copied from the skill)

- Files are CRILAYLA-compressed when `FileSize < ExtractSize` (`tools/crilayla.py`, verified: every unpacked file's length equals
  ExtractSize, asserted in `unpack.py`; `tests/test_formats.py`).
- No compressor written: `cpk.rebuild` stores replaced files raw (`FileSize == ExtractSize`). Guess: the game's CRI loader accepts raw
  entries (it must: many entries, e.g. `.cnz`, `.acf`, are stored raw). Confirm with the identity/edit build in phase 3.

## Inside the CPKs

| Format | Magic | Notes | State |
|---|---|---|---|
| Scene script `.bin` | `MZ\0\0` | bytecode, see `text.md` | verified (walks to EOF in all 80) |
| Rhythm chart `oto*.bin` | `MZ\0\0` | same op framing; op 0x2c carries lyric fragments | verified framing |
| UI text tables | `STLH` `CDLH` `EVTH` `MVEH` `PFLH` `SKTH` `SUDH` `MILH` | `<4cc>H`, u32 0x10000, u32 first-record offset (0x10), u32 count; fixed-size Shift-JIS slots. See `text.md` | STLH verified, others guess (same header) |
| GIM | `MIG.00.1PSP` | `gim.py`; size = 16 + u32 at +0x14 | verified (4,236 unique parse) |
| D2C | `D2C\0` | u16 count, u16 ?, then (u32 hash, u32 off, u32 size) entries; holds GIMs + layout blocks (floats, BE). 19 `ui/graphics/sys_*` D2Cs are layout-only and reference other D2Cs by name (`sys_001_004`...) | guess |
| CANZ `.cnz` (play/graphics/songBNN) | `CANZ` | stored raw in CPK, high-entropy body; guess: rhythm-game background animation. No GIM magic. Check in the rhythm-game tour whether it shows text | unknown |
| `.msk` (scene/mask) | none | 8-bit ramps: transition masks, no text | guess |
| `.eff` (eff/) | | particle/effect definitions, no GIM inside; `eff_icon_moji.eff` ("moji" = letters) references textures; check in tour | guess |
| KFNT `.fnt` (font/font17, font24) | `KFNT` | `KFNT` + u8 w,h (0x11/0x18) + 08 02 + ...; table of 16-byte entries (u32,u32,u32 data off,u32 code?) then glyph data. Two fonts: 17 px (dialogue?) and 24 px. Glyph format, code mapping and Latin coverage: phase 5 | guess |
| PMF movies | PSMF | H.264; strip 2048-byte header and `ffmpeg -f mpeg` reads it. `mv_NN` = song music videos with burned-in kinetic lyric typography; `opening` (logo only), `special_0N`, `marvelous` (logo) | verified by frame grabs (`work/movie/*.png`) |
