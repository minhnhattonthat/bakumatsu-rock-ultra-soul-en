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

| File | Header count | Layout (verified phase 4) | Content |
|---|---|---|---|
| `ui_system_text.stb` (STLH) | 0x68 | 104 records x 0x208 at 0x10: text[0x200] + u32 line count + u32 id | system/save/install messages, menu help lines. **Mixed encoding**: 58 records Shift-JIS, 46 (install/save/error) UTF-8; only one record (idx 2, `OK`) decodes both ways |
| `ui_chapter.cil` (CDLH) | 0x1A | 3 sections (below) | chapter names, gallery event titles/descriptions/unlock text, song list |
| `ui_event.evt` (EVTH) | 0x1B | 27 records x 0x48 at 0x10: u32 id + text[0x40] + u32 lines | gallery event titles |
| `ui_movie.mve` (MVEH) | 0x20 | 32 records x 0x8C at 0x10: u32 id + title[0x40] + u32 + performers[0x40] + u32 | movie titles + performers |
| `ui_profile.pfl` (PFLH) | 0x12 | 18 records x 0x7E8 at 0x10 (below) | character profiles |
| `ui_skit_00/01/02.skt` (SKTH) | 0x1E / 0xA / 0x9 | records of variable length (below) | 51 skits: title + up to 3 short lines per message (~2,400 strings) |
| `ui_sound.sud` (SUDH) | 0x19 | 25 records x 0x48 at 0x10 (id + title[0x40] + u32), then 2 records x 0x88 at 0x77C (u32 + u32 id + title[0x40]) | sound-test song titles (the last two are leftover entries, ids 14/15 repeated) |
| `movie/movie_list_info.mil` (MILH) | 0x24 | 36 records x 34 bytes at 0x10: name[0x20] + u16 | ASCII file names only, no text |

**ui_chapter.cil** (0x5A84 bytes, three sections back to back, each record 4-byte aligned):
- 0x1C: 26 x 0x1A4 = chapter/event names, text[0x80] at +0 (line count at +0x80, id at +0x1A0).
- 0x2AC4: 16 x 0x1A4 = gallery events: title[0x80] at +0, description[0x80] at +0x84, unlock text[0x80] at +0x108
  (each followed by its line-count u32); tail 0x1C bytes of metadata.
- 0x4500: 27 x 0xCC = song list, ids 1..28 with 16 missing: title[0x40] at +4, performer[0x80] at +0x48, u32 at +0 and +0xC8.

**ui_profile.pfl**: 18 records x 0x7E8 at 0x10 = u32 id, then 11 fields each text + u32 line count:
name[0x10] @+0x04, voice actor[0x10] @+0x18, origin[8] @+0x2C, birthday[0x10] @+0x38, height[0x10] @+0x4C,
weight[0x10] @+0x60, blood type[8] @+0x74, star sign[8] @+0x80, likes[0x20] @+0x8C, favourite food[0x20] @+0xB0,
dislikes[0x20] @+0xD4; then six 0x128 biography sections at +0xF8 (title[0x20] + u32, text[0x100] + u32), unused = zero.

**ui_skit_*.skt**: 0x10 placeholder name[0x28]; then per skit: u32 index, name[0x28], u32 speakers, u32 message count,
then that many messages of 0x8C bytes = u32 voice id, 4 more u32 words, 3 line slots of 0x28. The extra message
blocks at the end of skit_00 (0x10D38-0x11C38) and skit_01 (0x5934-0x5AD8) have no record header and variable header
length (a single text slot of 0x80 after 1-5 words); the extractor takes those by run scanning, so their slot is
"text up to the next non-zero byte". They are alternate/debug skits (one is labelled "only distributed on Twitter",
one "shelved skit").

## 4. EBOOT (`work/eboot/EBOOT.ELF`, `jpscan.py` -> `work/eboot/jpscan.txt`)

Only real text: 3 save-data title sets, UTF-8, shown in the PSP save dialog. Verified: exactly these 8 slots and nothing
else in the region (phase 4 mask-and-scan); all SJIS/UTF-16 hits elsewhere are code/table noise.

| Offset | Slot | Text |
|---|---|---|
| 0x26925C | 0x14 | 幕末Rock 超魂 |
| 0x269270 | 0x30 | 幕末Rock 超魂 インストールデータ |
| 0x2692A0 | 0x28 | インストールデータぜよ |
| 0x269458 | 0x14 | 幕末Rock 超魂 |
| 0x26946C | 0x28 | 幕末Rock 超魂 システムデータ |
| 0x269494 | 0x1C | システムデータぜよ |
| 0x2694BC | 0x24 | 幕末Rock 超魂 進行データ |
| 0x2694E0 | 0x18 | 進行データぜよ |

Patch in place in their NUL-padded slots (UTF-8, so an English title may use the whole slot minus a NUL).
PARAM.SFO TITLE likewise: value at 0x1D8, max length 0x80 (UTF-8), found through the SFO index (key table at 0xF4,
data table at 0x184).

## 5. Not text (checked)

`.eff`, `.msk`, `.mil` (ASCII names), `sound_list_info.sil` (SILH, 0 Shift-JIS hits; UTF-16 hits are noise), `ui_movie.mve` ASCII part.

## 6. Text files: `script/` (phase 4)

`python -X utf8 tools/extract.py dump [--force]` writes one JSON file per source file; `verify` runs the checks below
(also in `tests/test_extract.py`). `en` is empty until phase 6; `dump` never overwrites without `--force`, and with it
keeps every non-empty `en` by id.

| Directory | Source | Entries |
|---|---|---|
| `script/scene/<name>.json` | `INST.CPK scene/script/*.bin` (80) | dialogue 13,059, choices 121, staff roll 78; `jp` keeps the literal `\n` and `\sbl8`/`\fnt`/`\col` codes |
| `script/scene/_speaker_names.json` | the op-0x19 name table (same in 79 of 80 files) | 100 names; `staffroll2.bin` differs at indices 8/9 and carries those two as `name:008`/`name:009` entries in its own file |
| `script/play/otoNN.json` | `INST.CPK play/script/otoNN.bin` (29) | 11,439 non-empty lyric fragments (one slot per note, 1-6 chars; single-char and PUA glyph codes included) |
| `script/ui/<name>.json` | `NOINST.CPK systemdata/*` (9) | 3,003 entries: chapters, gallery events, songs, profiles, skits, system text, sound list |
| `script/eboot.json`, `script/param_sfo.json` | EBOOT.ELF, PARAM.SFO | 8 save titles + the XMB title (`encoding: utf-8`) |

Each entry: `id` (`<stem>:0x<offset of the string>` = the slot's type word for MZ scripts, the slot start for UI
tables), `off`, `max` (slot size in bytes: text capacity for MZ string args, the field size for UI tables), `kind`,
`jp`, `en`. MZ metadata: `op` (and `msg`, the dialogue id, for op 0x62). UI entries add `encoding: utf-8` when the slot
is not Shift-JIS.

Engine strings inside the scripts (asset paths, script/job/thread names, `in`/`out` section names) are classified as data
by opcode and stay out of the JSON; the roundtrip still covers them. MZ string args are `u16 type | u16 nwords | text`
and `tools/mzscript.py` parses every instruction into plain words plus slots, so `serialize(parse(b)) == b` for all 109
files; UI tables are parsed by `tools/uitable.py` from the layouts above.

Checks (`extract.py verify`): every file reserializes byte-identically; every slot re-encodes from its `jp`; mask every
slot and scan the rest for Japanese text (any run outside a slot fails) — currently 0 problems; and the JSON `jp`/`max`
equal the source's. Counts above are asserted, so an extractor regression shows up as a failing count, not silently.

Note for phase 5/6: op 0x62's last word is a 0/1 flag, not a speaker index; nothing in the instruction stream names the
speaker of a line (the op-0x19 table is only the name list). Translators get the scene file and can infer speakers from
the text; the dialogue `msg` id can be used for later voice/QA lookups.

## 7. Insertion, marker build and width gate (phase 5)

**insert.py** (`tools/insert.py plan [--dir script] [--eboot]`) turns the JSON back into the files `build.py` patches:

- MZ scene/rhythm files are **rebuilt with resized string slots**. A slot keeps its original capacity when the English
  fits (no shift); otherwise capacity = text + NUL rounded up to 4 bytes. Every jump argument is then re-mapped over the
  old -> new instruction offsets. Jump positions (word index after the opcode word, verified over all 80 scene scripts:
  every value landed on an instruction start) are `0x0B:0, 0x0D:0, 0x0E:0, 0x16:1, 0x18:0, 0x22:4, 0x2B:4, 0x2F:0,
  0x35:0, 0x47:0, 0x4F:3, 0x54:0, 0x55:0-3, 0x5D:1, 0x89:1-2`, plus **every word after the choice string in op 0x51**
  (the target count follows the string's capacity). Op 0x47's argument is only a jump when the instruction has one
  (a bare `47` end marker has no args) and in `play/` charts 0x47's argument is not an offset at all (26 of 29 miss every
  instruction start), so charts skip it. Values 0 and 1 are ambiguous and stay unchanged. After the rebuild the file is
  re-parsed and every jump re-checked, so a bad map fails the build instead of the game (`tests/test_insert.py`).
- The shared op-0x19 speaker table (`scene/_speaker_names.json`, ids `name:NNN`) is applied **by index** to all 80 scene
  scripts; a file's own `name:NNN` entries (staffroll2's two) win for that file.
- UI tables are fixed slots: `uitable.write_table` writes them in place and raises on overflow (`ui_event.evt` test).
- `param_sfo.json` patches the XMB title. `eboot.json` is **off by default** (`--eboot`): patching the 8 save-dialog
  titles means shipping a plain-ELF EBOOT.BIN, which PPSSPP and CFW run but real hardware may not (D11).
- `python -X utf8 tools/insert.py check` asserts the untouched `script/` produces no edits; `build.py --texts DIR` builds
  from any text directory (`work/mark` for the marker build).

**Marker build** (`tools/mark.py --force` -> `work/mark`, then `tools/build.py --texts work/mark`): every entry gets
`[<id>] The quick brown fox jumps over the lazy dog. 0123456789 abc...`, truncated to the slot for fixed files. Scene
slots grow, so each dialogue line shows its id in full. Boots and warps clean: `work/qa/markboot/`, `work/qa/warp/
{m_001001,adv_backlog,gallery_music}` (shots taken against the marker ISO). Nothing left Japanese was seen in the
toured boxes; `extract.py verify`'s mask-and-scan still covers the rest.

**Engine finding (the big one).** The game draws text two ways:

- **horizontal** with the KFNT font: menu list rows, the bottom help line, and the ADV **back log** all render the same
  English marker strings left to right with proportional widths and clipping at the box edge;
- **vertical** (tategaki) in the ADV speech panels: each glyph is drawn **rotated 90°**, one per ~15 px down the column,
  ~4 columns of ~13 characters in a panel about 140x210 px (`work/qa/warp/m_001001/final.png`).

So English dialogue needs the horizontal path, not a new font: ASCII/`[]`/digits already exist in font17 and render
in every horizontal box. The ADV panel text is laid out by a different routine than the backlog; making dialogue
horizontal (or re-laying out the panels) is EBOOT engine work, not data. Known anchors for the next pass: the font
object is read at `0x088066a4` (font+4 width, +5 height, +6/+7 flags, from `0x0880543c`); the KFNT copy in RAM sits at
0x96fdaec (font17) / 0x978445c (font24) after a script load; the map's per-frame work for a line change sits in
0x089a0000-0x089b0000. Memory breakpoints work (`memory.breakpoint.add`, `reason == 'memory.breakpoint'`), but the
**ADV script string is not read at display time** (the line is parsed once into a display structure) and the STB help
text is not re-read on menu redraw, so read-watching the text is not a way in.

**Width gate (provisional: horizontal boxes measured, ADV pending the layout change).**

| Variant | Where | Text area | Observed | Shot |
|---|---|---|---|---|
| Menu list row (sound/music, event, skit, movie) | `NEW [id] ...` row | x 205..444, ~240 px | ~30 marker chars before the clip | `work/qa/warp/gallery_music/final.png` |
| Bottom help line | every menu | x 8..235, ~227 px | ~32 marker chars | `work/qa/warp/story_menu/final.png` |
| ADV back log line | SELECT in ADV | x 47..458, ~412 px, 1 line | ~40 marker chars, scrolls | `work/qa/warp/adv_backlog/final.png` |
| ADV speech panel (vertical) | dialogue | ~140x210 px panel, 4 columns x ~13 chars | ~15 px/char down a column | `work/qa/warp/m_001001/final.png` |
| Chapter card / profile / system dialog | | not measured yet | | |

These are read off the zoomed marker shots, not yet from a per-variant px budget; the ADV panel will be re-measured
after the horizontal layout lands, and the font is proportional, so the budget is in px (chars are approximate).
