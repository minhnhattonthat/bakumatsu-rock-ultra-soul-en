# Translator brief - Bakumatsu Rock: Ultra Soul (PSP, 2014)

You translate part of the Japanese script of Bakumatsu Rock: Ultra Soul into English for a fan patch. It is a
rock-and-roll comedy-action story set in an alternate Bakumatsu Japan: Ryoma Sakamoto and his band fight the
shogunate's mind-controlling idol songs with rock. Work only on the batches named in your dispatch, one at a time in
the order given, each to a passing check before the next. Do all translation yourself; do not dispatch subagents.

## Read first
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `work/tl/<batch>.terms.txt` - binding glossary rows for this batch (`glossary.md` has the full table and rulings).
3. `docs/synopsis.md` - who is who and the late reveals. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`
- speaker is a guess: `ryoma?` = the character sprite last shown before the line (often, not always, the speaker;
  narration boxes and off-screen voices get it wrong). Decide from the content.
- form: dlg (speech box or skit balloon), choice, title, text, name, ... (menu/table items).
- ` / ` marks the line breaks of the Japanese box. Translate the box as one utterance; don't copy the breaks.
- limit: `112px` = an ADV speech box: your English is wrapped automatically at 112 px (about 17-19 characters per
  line) into at most 8 lines, i.e. roughly 130 characters. Aim for 2-5 lines. `39b` = a fixed slot of 39 bytes
  (= 39 ASCII characters, including spaces) - a hard limit.
- Lines are in story order; use the neighbours for context.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs inside
the English, no Japanese or fullwidth characters, no `\uXXXX`. For speech boxes write one paragraph; write `\n` only
where a break must fall (a dramatic pause, a list). For fixed slots with ` / ` in the Japanese (skit balloons, gallery
descriptions), `\n` is allowed where the Japanese breaks, and each byte counts.
Control codes: copy `\fnt1` ... `\fnt0` (big text) and `\col1` ... `\col0` (colour) around the matching English words;
copy `%d`, `%s`, `%x` exactly.

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every reported id until it prints OK.
`python -X utf8 tools/batches.py fit "your English"` shows how a speech box wraps.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible (style-reference table). Ryoma's Tosa dialect (ぜよ/じゃ/わし/おんし) becomes folksy swagger,
  Takasugi's オレ様 becomes cocky boasting, Katsura stays polite, Hijikata clipped, Okita cool. A line any speaker
  could have said is a mistake.
- Names and terms exactly as in the glossary; Western order (Ryoma Sakamoto); honorifics kept and hyphenated
  (龍馬さん -> Ryoma-san, 土方さん -> Hijikata-san, 慶喜様 -> Yoshinobu-sama). The check enforces both.
- Never abbreviate to fit. If a speech box can't fit 8 lines without losing meaning, keep the meaning and report
  `LONG: id`; for a fixed slot, rephrase until it fits.
- Shouts: keep them short and punchy ("Let's ROCK!"). Stretched vowels (〜, ー) can stretch the English word.
- Sound effects in ADV text: *Slam!* style.

## Notes from earlier batches
- US spelling (honored, license, favorite, recognize, practiced, traveler).
- 京の都 is "the capital, Kyoto" or "Kyoto", never "the capital of Kyoto".
- Don't calque オレ様 as "the great me": "the great Takasugi", "yours truly", or a cocky sentence.
- Old men (the Tengu, elders: ワシ/じゃ/のう) keep an elder register ("lad", "eh?"); keeping only "Ho ho ho" is flat.
- 『』 -> single quotes. ！ lines don't end in "?". Giggles (んふふ) are "Hehe"/"Tee hee", not "Mmhm".
- When \fnt1 spans the whole JP box, the big text spans the whole English too.
- The speaker column (`ryoma?`) is the last sprite loaded and is often wrong; take the speaker from the content.
- Ruby words: translate the reading (glossary "Decisions from earlier batches"). Takasugi plays bass, Katsura drums.
- A wordplay you adapt (a pun on 龍 = dragon, etc.): keep it short and report it as UNSURE.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
