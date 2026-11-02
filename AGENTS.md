# Bakumatsu Rock: Ultra Soul (PSP) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder. Read its SKILL.md (and `references/platform-psp.md`) before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/bakumatsu_rock_us_en.iso (checks the dump against `rom.sha1` first; `insert.py` feeds `edits()`; no `en` = byte-identical ISO, ~7 s). `--texts work/mark` builds the marker set
- Insert:   `python -X utf8 tools/insert.py plan [--dir script] [--eboot]` (JSON -> CPK/ISO edits; MZ slots resize, jumps re-map; `check` = identity) and `python -X utf8 tools/mark.py --force` -> `work/mark` (marker text: every line `[id] ...`); how and the width table: `docs/re/text.md` §7
- Measure:  `python -X utf8 tools/measure.py SHOT --rect X,Y,W,H [--dark]` (text extents in px; zoom/crop with `sheet.py`)
- Check:    `python -X utf8 tools/check.py` (pytest over `tests/` + lint; the pre-commit hook runs this; hooks: `git config core.hooksPath tools/hooks`)
- Lint:     `python -X utf8 tools/lint.py [--all]` (every `script/` entry: px/lines, byte slots, codes, glossary, stubs; `script/keep_jp.txt`); `tools/isodiff.py` (build.py runs it: nothing changed but the planned edits); `batches.py rewrap` (balanced wrap)
- Text:     `python -X utf8 tools/extract.py dump` -> `script/*.json` (one file per source file, `jp`/`en` per string slot);
            `python -X utf8 tools/extract.py verify` checks the roundtrip, the slot coverage and the JSON against `work/cpk`.
            `.txt`/`.json` text lives in `script/`; format and layouts: `docs/re/text.md` §6.
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/bakumatsu_rock_us_en.iso --out work/qa/smoke --route tools/routes/boot.txt --smoke --sheet` (boot.txt reaches the main menu on a fresh memstick)
- Warp:     `python -X utf8 tools/debug/warp.py SCENE.. [--iso build/bakumatsu_rock_us_en.iso] [--sheet] [--state]` (cold boot -> any scene in `tools/debug/scenes.tsv`: every script by file name, every menu, gallery, live, ADV dialog; all unlocked; shots in `work/qa/warp/<scene>/`; `--all` regenerates every state into `work/states/warp/`; `--list`; how: `docs/re/debug.md`. Never ask the user to play to a scene)
- Text RE:  `python -X utf8 tools/debug/textprobe.py diff|watch` (RAM diff across an ADV line change -> write breakpoint on the text column buffers; the way into the dialogue layout, `docs/re/text.md` §7)
- Release:  `python -X utf8 tools/release.py` (xdelta3 patch + verify; not written yet; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ISO: `rom/Bakumatsu Rock - Ultra Soul (Japan).iso` (1,699,610,624 bytes; gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulators: QA = PPSSPPHeadless QA fork `qa-1` (one per machine in `%LOCALAPPDATA%\translate-retro-game\ppsspp-headless\`, `fetch_emu.py ppsspp-headless`); people/EBOOT dump = PPSSPP v1.20.4 in `tools/ppsspp/` (https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-Windows-x64.zip; gitignored). Each emu.py run gets a fresh memstick; no settings to commit. Savestates: `work/states/`.
- ISO helpers: `tools/iso9660.py`, `tools/cpk.py` (from the skill, rebuild fixed: keys `dir/name`), `tools/crilayla.py`. Unpack: `iso9660.py x ROM work/iso` -> `tools/unpack.py` (work/cpk) -> `tools/gimsweep.py` (work/gim, sheets). Plain EBOOT: `work/eboot/EBOOT.ELF`. Text: `script/` (format TBD in phase 4). Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- PSP: circle = OK, cross = cancel. Fresh memstick boot shows the autosave notice, then "load failed, retry?" (answer No). EBOOT.BIN is encrypted; dump the plain ELF with PPSSPP (`platform-psp.md`).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
