# Text

Encoding everywhere: **Shift-JIS (cp932)**, except a few UTF-8 strings (below). Verified by decoding known strings: boot dialog
"はい/いいえ" (STB 0/1), prologue narration in `b_001001.bin` (`tests/test_formats.py`). PUA codes (U+E0xx in cp932 = lead bytes
0xF0-0xF9) appear in lyric fragments: custom glyphs (button/icon art), map them from the font in phase 5.

## 1. ADV scene scripts: `INST.CPK scene/script/*.bin` (80 files; verified walk to EOF)

`b_*` (前作 story, 18 chapters + splits), `m_*` (超魂 new story), `ED_*` (8 endings), `OP_*` (3), `staffroll*.bin` (credits).

- File = `MZ\0\0` + instruction stream. Instruction = u16 op, u16 length **in 4-byte words** (length 0 means 1), args.
- Args are 4-byte words. A string arg = u16 type (low byte 3; high byte 0x00, 0xFB or 0xF1) + u16 nwords, then nwords*4 bytes of
  NUL-padded Shift-JIS.
- **Op 0x19** (length 1) is followed by an inline table of exactly **100** string args not counted in its length: the speaker/
  character name table (ト書き = narration at index 0, ... ？？？ last). Same table in all 80 files. Verified: walk4 (scratch) found
  100 entries in every file and code resumes right after.
- Text-bearing ops (counted over all 80 files):

| Op | Strings | Layout | Notes |
|---|---|---|---|
| 0x62 | 13,059 | `62 00 LL 00` u32 id, string arg (type 0x0003) | dialogue/narration box. id: guess = message/voice id. 1-6 lines, `\n` literal (2 bytes `5C 6E`) = line break. 12,862 unique strings, ~300k chars |
| 0x51 | 121 | string arg (type 0xFB03) then u32 jump targets | choices (もう一度歌う / 武士にくってかかる ...) |
| 0x4C | 74 | string arg (0xF103 or 0xFB03) | staff roll pages (in `staffroll*.bin` and `m_010003`); `\sbl8` spacing code |
| 0x19 table | 100 x 80 | see above | speaker names |

- Control codes seen inside strings: `\n` (17,764), `\sbl8` (132, staff roll), `\fnt1`/`\fnt0` (73, font switch), `\col1`/`\col0`
  (9, colour). Codes are ASCII, so English text can carry them unchanged. Format strings: none in scripts.
- **Jumps are absolute word offsets from file start** (verified: op 0x0B at `ED_001001:0x1c2c4` -> 0x70b8*4 = 0x1c2e0, an
  instruction start). Arg positions whose value is always an instruction start (stats over all files, `offs.py` in scratch; values
  0/1 are ambiguous): 0x0B w1, 0x0D w1, 0x0E w1, 0x18 w1, 0x16 w2, 0x22 w5, 0x2B w5, 0x2F w1, 0x35 w1, 0x47 w1, 0x4F w4, 0x51 w6+
  (choice targets), 0x54 w1, 0x55 w1-4, 0x5D w2, 0x66 w5, 0x89 w2-3. **Any string-length change must re-map these** (phase 3/4:
  build an old->new map over instruction starts and assert every listed arg hits one). Guess until the identity + resize test passes.

## 2. Rhythm charts: `INST.CPK play/script/otoNN.bin` (29 songs)

Same framing. Op 0x2C (len 0x0B+) holds a lyric fragment string per note (26,854 notes, ~500 unique fragments); the tutorial says
notes "turn into words" on a hit. Fragments are timed to the sung Japanese syllables. Non-blocking question in `docs/status.md`
(default: romanize).

## 3. UI tables: `NOINST.CPK systemdata/*` (fixed slots, in-place edits)

Common header: 4cc (`STLH` ...), u32 0x00010000, u32 first-record offset 0x10, u32 record count.

| File | Records | Content |
|---|---|---|
| `ui_system_text.stb` (STLH) | 0x68 x 0x208: text[0x200], u32 line count, u32 id | system/save/install messages, menu help lines (82-101). **Mixed encoding**: most Shift-JIS, ~45 (install/error) UTF-8. Verified by decode; whether the game renders the UTF-8 ones as-is: check in phase 5 (ASCII is valid in both) |
| `ui_chapter.cil` (CDLH) | 0x1A | chapter names (オープニング, 第一話 運命 宿命 熱情のロック ...) + descriptions |
| `ui_event.evt` (EVTH) | 0x1B | gallery event titles |
| `ui_movie.mve` (MVEH) | 0x20 | movie titles + performers |
| `ui_profile.pfl` (PFLH) | 0x12 | character profiles (name, VA, birthday, height, likes) |
| `ui_skit_00/01/02.skt` (SKTH) | 0x1E... | skits (titles + many short lines; ~2,400 strings total) |
| `ui_sound.sud` (SUDH) | 0x19 | sound-test song titles |
| `movie/movie_list_info.mil` (MILH) | 0x24 | movie file names only (ASCII), no text |

Record layouts beyond the STB: phase 4 (each is fixed-stride; find stride from the header count and file size).

## 4. EBOOT (`work/eboot/EBOOT.ELF`, `jpscan.py` -> `work/eboot/jpscan.txt`)

Only real text: 3 save-data title sets, UTF-8 at 0x26925c-0x2694e0 (`幕末Rock 超魂`, `... インストールデータ`/`システムデータ`/`進行データ`
plus `...ぜよ` subtitles), shown in the PSP save dialog. All SJIS/UTF-16 hits elsewhere are code/table noise (no hiragana runs).
Patch in place in their NUL-padded slots. PARAM.SFO TITLE (UTF-8) likewise.

## 5. Not text (checked)

`.eff`, `.msk`, `.mil` (ASCII names), `sound_list_info.sil` (SILH, 0 Shift-JIS hits; UTF-16 hits are noise), `ui_movie.mve` ASCII part.
