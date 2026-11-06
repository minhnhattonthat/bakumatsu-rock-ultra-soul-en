# Bakumatsu Rock: Ultra Soul English translation

Unofficial English fan translation of **Bakumatsu Rock: Ultra Soul** (PSP, Marvelous, 2014): the source text and tools
that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game. The patched game runs in PPSSPP and on custom
firmware, not on an unmodified PSP.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Story dialogue, choices, narration, skits | Translated |
| Profiles, menus, system messages, save data, credits | Translated |
| Menu, title-card, notice, sound-effect and button graphics | Translated |
| Game logo; signs, banners and crests painted into the art | Left in Japanese |
| Lyrics on the rhythm-game notes and in the song videos | Left in Japanese |

Known issues (see also [Issues](../../issues)):

- Five profile names are shortened to fit their slot: "S. Takasugi", "T. Hijikata" and three voice actors.
- Option > Data install copies the original Japanese data: leave install off.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+, your own dump of the Japanese game, and
[translate-retro-game](https://github.com/minhnhattonthat/translate-retro-game) (shared scripts; the graphics step
imports them).

```sh
git clone https://github.com/minhnhattonthat/bakumatsu-rock-ultra-soul-en
git clone https://github.com/minhnhattonthat/translate-retro-game
export TRANSLATE_SKILL="$PWD/translate-retro-game/skills/translate-retro-game"
cd bakumatsu-rock-ultra-soul-en
pip install pillow numpy pytest
# copy your dump to: rom/Bakumatsu Rock - Ultra Soul (Japan).iso
#   (1,699,610,624 bytes, SHA-1 4fa0409f0a547cc4250a34c8ef5ac5b62bdd1cb2; the build refuses any other dump, see rom.sha1)
python -X utf8 tools/iso9660.py x "rom/Bakumatsu Rock - Ultra Soul (Japan).iso" work/iso
python -X utf8 tools/unpack.py
python -X utf8 tools/gimsweep.py --no-sheets
# dump the decrypted EBOOT to work/eboot/EBOOT.ELF (below)
python -X utf8 tools/build.py                          # -> build/bakumatsu_rock_us_en.iso
python -X utf8 tools/check.py                          # tests + text lint
```

The disc's `EBOOT.BIN` is encrypted, and the build patches the plain ELF. To dump it, use windowed PPSSPP (the headless
build ignores this setting): set `DumpFileTypes = 7` under `[General]` in `memstick/PSP/SYSTEM/ppsspp.ini` and boot the
game. Copy `memstick/PSP/SYSTEM/DUMP/ULJM06388_EBOOT.BIN` to `work/eboot/EBOOT.ELF` (SHA-1
`b2695778dcb55c3884c3bbd5c76e97c03128fc61`), then set the value back to 0.

The v1.0 text builds to the released image: SHA-1 `72fc332bc96076e1d86c5e7436e60ad57f4ecf17`.

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Marvelous's and is included only so
the translation can be checked against it. Bakumatsu Rock: Ultra Soul is (c) Marvelous; this project is not affiliated
with them. Fonts: see `docs/fonts.md`. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
