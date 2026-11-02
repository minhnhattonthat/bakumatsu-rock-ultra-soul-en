# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-02 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-02 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-02 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-02 | Abbreviations | engine work first (default), abbreviate | Default: engine work first, full names and terms; abbreviate only as a flagged last resort. |
| D5 | 2026-11-02 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-02 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. |
| D7 | 2026-11-02 | Existing saves / memory cards / savestates | use the user's, none | None provided; build the debug tool (phase 2) as usual. |
| D8 | 2026-11-02 | Git identity | ask, preset | Already set by new-game.ps1 (minhnhattonthat); do not change. |
| D9 | 2026-11-02 | Release boundary | publish, stop at zip | Never run `gh release create` or change repo visibility; the run ends at a built and verified release zip. |
| D10 | 2026-11-02 | English layout for ADV dialogue | keep vertical, horizontal via engine work, graphics | Horizontal, by engine work. The ADV panels draw rotated glyphs in ~4-column tategaki (~140x210 px, ~13 chars/column), which English cannot live in; the same engine already draws the same strings horizontally (menu rows, help line, backlog) with the same KFNT font, so the fix is the ADV text routine's direction/layout, not a new font. Width-table facts: `docs/re/text.md` §7. |
| D11 | 2026-11-02 | EBOOT save-dialog titles | ship plain-ELF EBOOT, keep the original | Keep the original encrypted EBOOT.BIN by default (the 8 PSP save-dialog titles stay Japanese); the build patches PARAM.SFO (XMB title) only. A plain-ELF EBOOT is what PPSSPP and CFW run, but real hardware may not: owner's call before release (`docs/status.md`, "Waiting on the user"). |
