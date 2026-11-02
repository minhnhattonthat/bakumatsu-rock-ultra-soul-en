# Bakumatsu Rock: Ultra Soul (PSP) English translation

Skill: translate-retro-game; `python tools/skill.py` prints its folder. Read its SKILL.md (and `references/platform-psp.md`) before ROM, text or QA work. `"$(python tools/skill.py)"` works in bash and PowerShell; never paste a `plugins/cache/<hash>` path.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py` -> build/bakumatsu_rock_us_en.iso (checks the dump against `rom.sha1` first; edits plug into `edits()`; no edits = byte-identical ISO, ~7 s)
- Check:    `python -X utf8 tools/check.py` (pytest over `tests/` + lint; the pre-commit hook runs this; hooks: `git config core.hooksPath tools/hooks`)
- Smoke:    `python -X utf8 "$(python tools/skill.py)/scripts/emu.py" build/bakumatsu_rock_us_en.iso --out work/qa/smoke --route tools/routes/boot.txt --smoke --sheet` (boot.txt reaches the main menu on a fresh memstick)
- Warp:     `python -X utf8 tools/debug/warp.py SCENE.. [--iso build/bakumatsu_rock_us_en.iso] [--sheet] [--state]` (cold boot -> any scene in `tools/debug/scenes.tsv`: every script by file name, every menu, gallery, live, ADV dialog; all unlocked; shots in `work/qa/warp/<scene>/`; `--all` regenerates every state into `work/states/warp/`; `--list`; how: `docs/re/debug.md`. Never ask the user to play to a scene)
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
