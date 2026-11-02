# Graphics text survey (phase 1)

Every Japanese-on-screen element that is a picture, not font-drawn text. Font-drawn text (dialogue, help lines, UI tables) is in
`text.md`. Row list: **`docs/re/graphics-survey.tsv`** (744 unique GIMs, 840 copies counting md5 duplicates; columns key, w, h,
copies, kind, text, status). Keys are `work/gim/<key>.gim` after `tools/unpack.py` + `tools/gimsweep.py`; `copy_keys` in
`work/gim/index.tsv` lists every copy (write a replacement to all of them).

## How it was made

- **Static sweep (done):** `tools/gimsweep.py` found every GIM (loose `.gim` and embedded in `.d2c`), 4,236 unique, rendered into
  154 numbered sheets (`work/gimsheets/<group>_NNN.png` + `.tsv` cell index). Six read-only visual-qa subagents read every sheet
  (chunks `work/survey/chunk0N`, raw results `work/survey/result0N.tsv`), keys validated against the index (0 unknown).
  Skipped and why (printed by gimsweep): 19 layout-only `ui/graphics/sys_*` D2Cs (no images), `.eff` (effect scripts), systemdata
  tables (text, see `text.md`), `.cnz`/`.msk` (see `containers.md`; CANZ unknown, check in a rhythm-game tour).
- **Tour (partial):** `work/qa/tour1-3` (title -> STORY menu -> ROCK story prologue). Confirms: title logo + PUSH START (GIM),
  STORY menu labels データ連動 / 超魂 (GIM, `sys_010_001`), bottom help line (font, STB 82-101), ADV dialogue (font, **vertical**
  text in manga-style speech panels, see below), character name card 坂本龍馬 + 声:谷山紀章 (GIM, `adv_002`/`adv_003` single
  kanji cells), SE lettering ドン / バン (GIM, `adv_009`-`adv_022`). Mid-game screens (chapter cards, results, endings, credits)
  still need warps (phase 2 debug tool) for the phase-8 shot check.

## Summary by kind (rows)

| Kind | Rows | Where | Notes |
|---|---|---|---|
| sfx | 292 | `adv_009`-`adv_022`, `adv_3xx` | manga SE lettering; mostly single kana pieces the scripts assemble into words (ド+ン...). Plan: English SFX per piece set, or re-letter whole words; decide in the engine spike |
| banner | 111 | `gam_605`-`gam_692` (88 kanji word tiles with katakana English readings, e.g. 流星=メテオ), `adv_011`/`adv_300` unlock banners (プロフィール解放! ...), FAN!増加! | rhythm-game shout words |
| sign / caption | 144 | `bg_*` scenery strips (shop signs いわき屋/越後屋, 八幡宮 plaque, lanterns, 誠 banners), `adv_004/005` vertical narration strips, `adv_006` | scenery signs: translate where legible (D5), keep 誠 crest |
| title | 62 | `ui_tit_101`-`113` chapter cards (第一話..第十話, 超魂 第一話..第三話 + subtitles), `sys_*` screen titles, `gam_200_*` song-title logos (13) | chapter titles must match `ui_chapter.cil` text |
| menu | 32 | `sys_006`-`sys_010` option/config/data labels, `adv_002` ADV end menu (セーブ/チャプター選択へ/オトゲーをもう一回/次の章へ, 5 states each), `gam_100_033/034` pause menu, `sys_022_000` break screen, `adv_008_000` スキップ | |
| tutorial | 21 | `sys_021_001` (HOW TO PLAY panels), `sys_021_002` (manual page cut into 32-px strips) | strips: reassemble the page, redraw, re-slice |
| label | 29 | small hints (決定, 進む, リトライ, キャンセル), `ci_22` 秘 seal, chr_18 眠り | |
| logo | 9 | 幕末Rock / 超魂 logos (`sys_000_000`, `sys_000_001`, `ui_tit_116`, `adv_407_a`, `sys_013_001`) | **keep** (D5: no official English logo; the 2014 anime keeps 幕末Rock too) |
| other | 44 | 誠 painted on 誠仮面's mask (`chr_97_makoto_*`, `gam_200_020`, `gam_381`), bg_020 door brushwork | costume art: keep |

Notable oddity: `bg_011_001` strips carry a burned-in dev caption ("1.5…用の背景"); likely never visible, check on a warp.

## Not GIMs

- **Movies** (`movie/*.pmf`): `mv_00`-`mv_28` song MVs with burned-in kinetic lyric typography (Japanese + romaji/English words);
  `opening`, `marvelous`, `special_01`-`05`. Re-encoding PSMF is out of scope by default: non-blocking question in `docs/status.md`.
- **XMB**: ICON0/PIC1 (ISO + INSDIR + content/SAVEDATA) show only the 幕末Rock logo: keep. PARAM.SFO title and the EBOOT
  save-dialog titles are text (`text.md` §4). PTF themes: not surveyed (optional bonus content).
- **System dialogs** (autosave notice, save/load prompts): firmware message dialog drawing STB UTF-8 strings, e.g. STB #45 (verified
  in `work/qa/smoke_orig/final.png`). Text work, not graphics.

## ADV text box (affects phase 5)

Dialogue is drawn by the game font **vertically** (tategaki, right-to-left columns) inside cream speech panels about 70x110 px at
the left of the screen (`work/qa/tour2/sheet.png`). English needs horizontal rendering in a box of that size or a re-laid-out box:
the main engine question for phase 5 (font KFNT 17 px; VWF; horizontal mode switch, if the engine has one: check whether any
script/box uses horizontal text, e.g. staff roll or narration).
