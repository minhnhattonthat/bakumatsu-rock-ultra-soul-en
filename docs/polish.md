# Polish pass

Minor review findings, deferred to one pass at the end. Each line gets ticked `[x]`: fixed, or `waived: reason`.
The release script refuses to run while any line is unticked.

## b001-b003 (pilot review)
- [x] OP_001001:0x9584 / 0x95d8 - Ryoma's ぜよ dropped in the shouting climax; add "I tell ya" to one
- [x] OP_001001:0x3e44 - 思い上がるな！下郎が: "Know your place, peasant!"
- [x] OP_001001:0x7ee0 - Katsura "let us begin" too stiff: "Let's begin." (the line is 0x77d0)
- [x] OP_002001:0x47d0 - "I'll give nothing to a shogunate dog!" stilted: "Never! I'd never hand it to a shogunate dog!"
- [x] OP_002001:0x1344 - 『』 should be single quotes
- [x] OP_002001:0x988c / 0x98d0 - emphatic 光だっ lost across the split
- [x] m_001001:0x10434 - "That song of yours" -> "Your singing isn't half bad, lad." (general, Tengu voice)
- [x] m_001001:0x1e084 / 0x1e0c8 - make the two halves parallel
- [x] m_001001:0x16850 - "swell guy ... thaaat!?" -> "You're a real good guy, I tell ya~!"
- [x] m_001001:0x184c0 - Otose はぁい: "Heeere you go!"
- [x] m_001001:0x2dfa8, 0x2d5d8 area, 0x3665c - Otose giggles "Mmhm" -> "Hehe"/"Tee hee~" (also 0x2e9ec, 0x33d24)
- [x] waived: \fnt1/\fnt0 are stripped at insertion in scene text (big font draws nothing in the horizontal ADV) - m_001001:0x1a9ec - \fnt1 span covers all three JP lines
- [x] m_001002:0x701c - アテがあるぜよ: "I got somebody in mind."
- [x] m_001001:0xc640 - "That is not my role." -> "Judging isn't my place."
- [x] OP_003001:0x13628 - "Feel free to call me a god."
- [x] m_001001:0xe054 - "Good. You understand."
- [x] waived: already US in script/ (grep finds no British forms) - b001-b003 - British spellings -> US (honoured, licence, favourites, monopolised, recognises, practised, traveller)

## b004-b067
- [x] waived: nothing listed to apply; the per-chapter story pass covers these files - Minor findings from these reviews were applied or dropped at merge time and not listed; the per-chapter story
  pass (`docs/story-reviewer-brief.md`) re-reads these files.

## b068-b071
- [x] b_007001:0x13444 / 0x13c04 - 頑張ってる echo: "give it our all" / "'Give it our all,' huh"
- [x] b_007001:0x4a7a0 - "What's that supposed to mean? You serious?"; 0x4ac40 "I'll cut you, you know?"
- [x] b_007001:0xf684 あ～あ "Sheesh~"; 0x6bfc "Look who's talking."; 0x3cbb8 untangle the Piece Soul sentence
- [x] b_008001:0x2e120 "old geez..."; 0x33738 "Same here. I'm asking too."; 0x36bac "I'm never swapping with this guy again!"
- [x] b_009001:0x1941c / 0x1c384 / 0x472c - Ryoma touch ("I tell ya") (0x472c ほえ？ -> "Whuh?")

## b072-b075
- [x] b_009001:0x52d28 cause misparsed (incident sparked by a daifuku gave a glimpse of friendship)
- [x] b_009001:0x382ec "commit seppuku"; 0x3fe80 "sew their mouths shut"; 0x33680 "The great Takasugi's daifuku"
- [x] b_011001:0x1d508 "Why would they kill her?"; 0x2798c / 0x27f98 "lift a hand or a foot" / "Hands and feet are all that ghost has"
- [x] b_012001:0xab10 drop "color me surprised"; Ryoma touches 0x15f48 0x8840 0x13454 0x6d38; Oryo 0x2774 0x5084 (0x15f48 is b_010001, 0x8840/0x13454 b_011001)

## b076-b079
- [x] b_014001:0x35fd4 "Just kidding~"; 0x4a1ac / b_016001:0xf1e4 Takasugi "ain't" -> "it's not"
- [x] b_014001:0x5b4b0 "about smiles"; b_012001:0x473b0, 0x49e4c; b_016001:0x9dbc "I'll treat it as such"; 0x14a44 "penny-pinching"
- [x] b_015001:0x20de0 "Young man with the burning soul"

## b080-b083
- [x] b_018001:0x408c drop "Lord"; 0x622c / 0x76cc ご老中 consistent (already "my lord Elder" both); 0x81cc 老害 "old relics"; 0x17e20 "Singing, you say?"
- [x] b_018002:0x6c00 "A power I gained by paying the price."; 0xa754 なあ "Wouldn't you agree?"
- [x] b_016001:0x1c0c0 cut "Not that it matters--"; 0x1c574 Hijikata "face me, fair and square!"; 0x1d8f0 birthday ("birthday festival", as b_016001:0x88d0)
- [x] b_017001:0x17210 / 0x17254 lyrics-merge meaning; 0x231c4 tense; 0x16790 神業 "masterstroke"

## b084-b087
- [x] ED_002001:0x4684 下手; 0x2a858 / 0x2acfc "eyes"; 0x2d00c "both of your rock souls"; 0x314f8 そうそう "Right."
- [x] ED_003001:0x3d2ac "*Flinch*"; 0x36ab8 drop stutter; 0x34320 "If you say so."
- [x] ED_004001:0x754c vs 0x16f0c 茶店/茶屋 one word ("teahouse"); 0x18204 "Here are a ... and a parfait"
- [x] ED_005001:0x2720 "best too?"; 0x4050 Katsura "please"; 0x18b54 ya/you mix (fixed in 0x18ba4)

## b092-b114 (profiles, skits, UI)
- [x] ui_skit_00:0x2b0, 0x7d0, 0x1c1c, 0x288c, 0x3838, 0x3928, 0x46a4/0x46cc, 0x3a68 'I like you', 0x5544, 0x5c94, 0x67b8
- [x] ui_profile:0x29dc "I was made for the world."; 0x67ac rakkyo; 0x18e4 "behind Kondo's back"; bio tense pass (past for life sections, present for [Present])
- [x] ui_skit_00:0x9c30 calisthenics; 0x933c; 0x9938; 0xe310 "I was Kondo-san's man"; 0xf46c "talking about"
- [x] ui_skit_01:0x2e50/0x2edc pronoun; 0x3bd8; 0x2534; 0x1fe4; 0x2bf8; Katsura "you know" over-use
- [x] ui_skit_02:0x454, 0x236c, 0x3494 "HUP!!???", 0x43c0, Okita "Tee hee" -> "Hehe", 0x5718 (is ui_skit_01), 0x274 "Bring it on!"
- [x] ui_system_text:0x628 "O Enter"; 0x8418, 0x36e8, 0x65a0, 0x2090, 0xc518 wording; 0xa290/0xa498 number join not changed: needs the in-game check (a trailing space fails lint)
- [x] waived: not a script wording fix; for visual QA (layout) and a credits-source check - staff roll: two-column cast lines ragged in the proportional font; names romanized without an official source
  check (list in the b115-b119 translator report: Sora Fujii, Masaaki Shimoma, ...)

## b088-b091
- [x] ED_005001:0x28260, 0x2b0d8 "I know he's an idiot", 0x2db7c "Getting cold feet, are ya?"; Alright/All right one spelling ("All right" everywhere in script/; "Alrighty" kept)
- [x] ED_006001:0x85f0, 0x10d84 "test it"; ED_008001:0xb7c4 "Ready, go~!"; ui_event:0x17c "The Trio's Live"; 0x20c check stomper/stomped (Okita stomps Takasugi in m_005001: "Okita Stomps")
