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

## Story pass (phase 8, work/qa/story/verdicts)

#### 00_opening_prologue
- [x] OP_001001:0x6d24 Takasugi: gag is that Ryoma asked him *third* (after Hijizo, So-chin) -> e.g. "Askin' the great Takasugi *third*!? Some 'countin' on' that is! Sing like your life depends on it!" (Takasugi's voice, not Ryoma's dropped g's)
- [x] OP_001001:0x3e44 Ii: "Know your place, peasant!" -> "Know your place, wretch!" ("peasant" is Takasugi's pet insult)
- [x] OP_002001:0x1239c Ryoma: わしは助かったのか -> "Did I... make it?" / "A-am I alive?"

#### 20_bonus_5
- [x] b_018002:0xc6cc Ii: 皆殺しだ -> "...will be slaughtered, every last one." (not "will die")
- [x] b_018002:0x1d0c narration: 慶喜たちの歌 -> "their song" (たち dropped)
- [x] b_018002:0xf2d4 Ii's mad laugh "Wahahahaha!" -> "Ha ha ha... Ahahahaha!"
- [x] b_018002:0xd55c Ii: 差し上げよう -> "I shall graciously let you live."

#### 03_chapter3
- [x] m_003001:0x5c278 Takasugi: drop "your" -> "I'll go to that Shinsengumi live!"
- [x] m_003001:0x401ac Takasugi irritated あぁ: "Huh?" -> "Hah?"
- [x] m_003001:0x9d48 Otose いやん: more flirty -> "Oh, Ryo-chan~ where have you been?"
- [x] m_003002:0x1a10 Okita: "its mouths" -> "their mouths"
- [x] m_003002:0x179ec Kondo いかん: "Oops, can't have that" -> "Oops, I'd better not dawdle. Back to my seat..."
- [x] m_003002:0x48c14 Okita: "let us hear it" -> "Come on, let's hear it! Your rock!"

#### 04_chapter4
- [x] m_004001:0x19ff4 Ryoma: drop Takasugi's "obviously" -> "Well, 'cause we want everybody to have fun, of course! Ain't that right, Sensei?"
- [x] m_004001:0x1c3b8 Takasugi: no dropped g's (Ryoma's device) -> "...the ace song I've been saving up finally got finished yesterday!"
- [x] m_004001:0x78dc Takasugi: "You lot" (British) -> "Don't you peasants dare miss a single note of mine. Got it?"
- [x] m_004002:0x2bac4 Hijikata: "his lot" -> "his gang"
- [x] m_004001:0x8d9c Katsura ですねぇ: "Isn't he, though." -> "He certainly is."
- [x] m_004002:0x4220 Yoshinobu: -> "I wonder if their rock might spread among the people like an epidemic."
- [x] m_004002:0x1af0c Takasugi おめでたいヤロウ: -> "You're a hopelessly naive fool, through and through."
- [x] m_004002:0x2b2d4 trooper 上様の命: "shogun" -> "By order of His Highness" (glossary)

#### 01_chapter1
- [x] m_001002:0x73a58 patrol: "You lot" -> "You people were about to play forbidden music just now, weren't you!"
- [x] m_001001:0x28724, m_001002:0x27da8 Ryoma ぴっつぁ: keep the quirk -> "peetsa" (set up at 0x18c80)
- [x] m_001002:0x5b4c4 Ryoma: -> "I ain't done nothin' like that! If you doubt me, go ask this Shoin-sensei yourself!"
- [x] m_001001:0x26dc8 Tengu しまった: -> "Dang! Forgot my wallet!"
- [x] m_001001:0x7e9c narration: "He got punched." -> "Ryoma got punched."
- [x] m_001002:0x10b40 Otose: -> "Pretty awful for singing, if you ask me~"
- [x] Otose laughs: one signature for うふふ/んふっ/んふふ (0x1b1c4, 0x2dfa8, 0x2e9ec, 0x33d24, 0x3665c, 0x10c48) -> "Tee hee~"
- [x] m_001003:0x2964 Ryoma 志を同じくするダチ: -> "buddies who share the same cause"
- [x] m_001002:0x44cdc Takasugi: -> "A thieving punk like you doesn't get to call me anything!"
- [x] Tengu "lad"/"my boy" tags: drop about a third in the long pizza/gear scenes

#### 02_chapter2
- [x] m_002001:0x29080 Ryoma: -> "Yeah, yeah! Otose-yan's peetsa is real tasty, after all!" (ぴっつぁ quirk; also 0x290d0/0x29f7c if Ryoma's)
- [x] m_002002:0x21c58 Takasugi: -> "Quit gawking at them like an airhead!"
- [x] m_002002:0x6f520 Ryoma: -> "First we gotta subdue this fella, or we ain't gettin' anywhere."
- [x] m_002002:0x4faec, 0x50ec8 Tengu: no dropped g's -> "fighting only happens because your souls resonate", "how you're getting on, eh?"
- [x] m_002001:0x18fdc, 0x2bce8 Ryoma ぜよ: -> "I'm off, I tell ya!", "I'd sure appreciate it, I tell ya!"

#### 05_chapter5
- [x] m_005001:0x4c51c Takasugi オレ様: -> "Even yours truly is taking heavy damage."
- [x] m_005003:0x74cc Katsura quoting 先生 (Shoin): -> "That's what Shoin-sensei used to say."
- [x] m_005003:0x177ec Ryoma ぴっつぁ: -> "peetsa" (quirk)
- [x] m_005003:0x375f8 Hijikata: drop "you know" -> "Good grief... They're wanted men."
- [x] m_005003:0x27bc8 Hijikata: -> "If there were, I'd never have been haunted by a killing, or by wanting to kill in turn."

#### 09_chapter9
- [x] m_009002:0x1b3e0 Okita ノるさ！: -> "I'm in! Obviously!"
- [x] m_009001:0x31208 Hijikata: -> "If your tongue were a little shorter, you might talk less. Might've been for the best."
- [x] m_009001:0x1c5ec Katsura: -> "That's even tougher."
- [x] m_009001:0x47c48 narration: -> "Katsu had probably set up the patrol arrangements himself."
- [x] m_009001:0x50754 Okita: -> "you're the one who said you were hungry, mister."
- [x] m_009004:0x7f84 将軍様: -> "You mean Lord Shogun!" (glossary)
- [x] m_009004:0xf8f0 Ryoma: -> "You're the arrogant one here!"
- [x] m_009002:0x123b0 Takasugi オレ様達: -> "knock our socks off" / "the great Takasugi and company's"
- [x] m_009001:0x260b4, 0x2687c Ryoma: -> "Whoa, whoa! That ain't okay, I tell ya!" (0x2687c only; 0x260b4 is the cuckoo poem, kept)

#### 08_chapter8
- [x] m_008001:0x37808 Hijikata: "You lot" -> "You guys are only safe because, by luck, they hadn't been ordered to kill you yet."
- [x] m_008001:0x30420 Takasugi: -> "You could've come sooner..."
- [x] m_008002:0x1b218 Ouno: "big sisters" -> "Ouno's not gonna lose to Sis and Sis Ikumatsu eitheeer~!"
- [x] m_008001:0x467b8 Ii: "How fares" -> "And how is our captive Sakamoto, Oryo?"

#### 07_chapter7
- [x] m_007003:0x1d34 Tengu/Shoin: "I tell you" is Ryoma's tic -> "It's coming! I can feel it, lad!"
- [x] m_007002:0x76298 Takasugi オレ様: -> "Yours truly will shake Sensei's soul awake with his rock and make him open his eyes!"
- [x] m_007001:0x5ee68 Ryoma: -> "Aw, jeez. Shindy just can't be honest with himself, can he?"
- [x] m_007002:0x1f9c0 Ryoma そうだ: -> "That's right! So the Shaggy Sensei's safe!"
- [x] m_007002:0xdc6c Ryoma ほえ: -> "Hwah?"
- [x] m_007002:0x5d40 Okita: -> "You've got a truly happy-go-lucky brain, you know~ I'm actually appalled."
- [x] m_007001:0x3dca0 "Piece Soulmates" vs glossary "Piece Soul mates": make it match the glossary
- [x] m_007001:0x188b4 Hijikata: "playing lives" -> "holding lives"

#### 06_chapter6
- [x] m_006001:0xbc74, 0x45904 Takasugi 能天気: unify to glossary "sunshine between the ears" ("You really do have sunshine between the ears...", "Don't lump me in with your sunshine between the ears!")
- [x] m_006001:0x16e34 Ryoma その通りじゃ: "Darn right!" -> "Damn straight!"
- [x] m_006001:0x47c5c Katsura: -> "the arrow Takasugi pulled out"
- [x] m_006001:0x58ba4 Okita うふふ: "Tee hee" -> "Heh heh..."
- [x] m_006003:0x9654 Ii: -> "You've won Okita over, and you think that's a victory?"
- [x] m_006003:0x22904 Ii: -> "How beautiful... Now, become a monster!"
- [x] m_006003:0x25fa0 Katsura: -> "has lost all reason!"

#### 10_chapter10
- [x] m_010001:0x12d4 narration: -> "Troopers freed from pacification, with their fervent pleas and a word from Kaishu Katsu, got Hijikata and Okita reinstated..."
- [x] m_010002:0x672a4: Ryoma dialect only if Ryoma speaks; if Okita -> "A monster that brings peace to no one, only devours people's souls, over and over--"
- [x] m_010001:0x35ed4 Ryoma: -> "Tell us what happened while we were gone, will ya?"
- [x] m_010001:0x1ea58 Hijikata: -> "Have they been struck down too...?"
- [x] m_010002:0x4c450 narration: -> "On the boy's lips was that hollow smile Ryoma had seen so many times."
- [x] m_010002:0x4f0b8 Ryoma ロックンロールぜよ: -> "Rock 'n' roll, I tell ya!"

#### 11_ultra_soul_1
- [x] m_011002:0x14e5c Ryoma 頼もーう: echo the dojo-challenge gag of m_011001:0x11dec -> "Ho there, within! I request entry!"
- [x] m_011001:0x4def4 Ryoma: -> "Then make it a Black Ship!"
- [x] m_011002:0x11060 Takasugi: no "ain't" -> "Tch. That stuff isn't rock! Only super-spicy is rock!"
- [x] OP_003001:0x10c68: -> "It'd wilt my red-hot, throbbing heart."
- [x] Katsu: "old man Katsu" (m_011001:0xb520) vs "Old Man Katsu" (0x2d4bc, 0x5adc4): one capitalization

#### 13_ultra_soul_3
- [x] m_013004:0x8cb4 Junior 神（スター）: -> "A god never loses! It's because he never loses that he's the king!"
- [x] m_013004:0x5048 Ryoma dash spacing: -> "Rock, songs -- they ain't anything like that!" (house dash style)
- [x] m_013002:0x30c4 Ryoma: -> "We're joinin' in, as the rebels representin' Japan!"
- [x] m_013001:0x20bc8 Okita ああん？: "Hah!?" -> "What was that!?"

#### 14_endings_a
- [x] ED_003001:0x222c0 Takasugi オレ様: -> "The great Takasugi is leaving the band, as of today." (optional ED_002001:0x1bf20 "The great Takasugi still has a mountain of things he never told you!")
- [x] ED_001001:0xdb10 narration: drop added "hollow" -> "steeped in a dim happiness"
- [x] ED_001001:0x10a08 Yoshinobu: -> "Ah, there you are! Hehe, of course. Naosuke would never leave me behind!"
- [x] ED_004001:0x14264 Hijikata 分際: -> "You skipped training. You've no right to talk back."

#### 12_ultra_soul_2
- [x] m_012001:0x1f834 Ryoma 烈！ロックンロールぜよ: -> "Let's rock 'n' rooooll, I tell ya!" (bookend with m_012003:0x4f9bc)
- [x] m_012001:0x18ad8 Ryoma: -> "Haha, spare me that one, I tell ya!"
- [x] m_012003:0x446d8 Ryoma: -> "Makoto Mask! What're we s'posed to do?"
- [x] m_012003:0x4daac Ryoma わかったぜよ: -> "Got it, pal!"
- [x] m_012003:0x2f1a4 Katsura: -> "Well, naturally, he is wearing a mask..."
- [x] m_012001:0x10518, 0x11404 Okita 負け犬: "loser" -> "whipped dog"

#### 15_endings_b
- [x] ED_005001:0x2db7c Takasugi: no Ryoma dropped-g/"ya" -> "Getting cold feet, are you?"
- [x] ED_006001:0x85f0 narration: -> "Just then, as Junior finished speaking with a smile--"
- [x] ED_007001:0x765c Heaven's Song takes no "the": -> "He who masters Heaven's Song masters heaven and earth!"
- [x] ED_007001:0x19c0 Ii: -> "Rebels... your hopes are crushed."
- [x] ED_008001:0xee70 Otose's 店 is the tavern, not "the inn": -> "...outside the shop..." / "Otose stepped out of the tavern" (0xee70 "the shop"; 0xfccc keeps "the inn": glossary calls Terada an inn)

#### 17_bonus_2
- [x] b_006001:0x34c60, 0xb5f0, 0x4805c, 0x4a0fc 誠の武士 echo: use "samurai of sincerity" everywhere (0x34c60 "...if you want to become a truly strong samurai of sincerity, I'll lend you a hand", 0xb5f0 "...a true samurai of sincerity...")
- [x] b_006001:0xa9fc (about Okita): -> "...he caused Kondo-san trouble right to the very end..."
- [x] b_007001:0x19e8c Hijikata はい: "Yes, sir." -> "Understood."
- [x] b_007001:0x4ac40 Okita 斬るよ？: -> "Want me to cut you?"
- [x] b_007001:0x408a8 呪魂（ダークソウル） "Dark Soul": add to glossary.md
- [x] b_008001:0x189e4 Ryoma: -> "Yo-ho, gotcha, ya hear!"

#### 16_bonus_1
- [x] b_001001:0x2ee88 narration: -> "...when Ryoma had forgotten these chance meetings, the four of them would meet again."
- [x] b_003001:0x2c388 Takasugi: no "ain't" -> "Watching your health? That's not exactly rock..."
- [x] b_003001:0xd008 Takasugi なにがだよ: -> "What makes sense?"

#### 18_bonus_3
- [x] b_009001:0x511e4 Katsura これにて一件落着: period-drama closer -> "And thus, all is well that ends well~!"
- [x] b_009001:0x40f90: -> "That, Great Detective Katsura-kun shall now deduce!"
- [x] b_009001:0x1830: "at the Terada's" -> "at Terada's" (glossary)
- [x] b_009001:0x43370 Katsura: -> "Of course, knowing Hijikata-kun's character, Okita-kun also never believed he'd steal it."
- [x] b_012001 色男: one term "ladies' man" (0x1d7fc, 0x20460, 0x20acc, 0x2119c, 0x37f70; already 0x46240, 0x499a8, 0x4a2f8)
- [x] Ryoma Tosa tag: b_011001:0x6970 "...can't sleep a wink, I tell ya.", b_012001:0x31380 "That's dangerous, I tell ya!", b_012001:0x9f14 "Seriously? What's gotten into y'all?"
- [x] b_013001:0x13318: spaced " -- " -> house dash style (also m_013002:0xa3e8, m_013004:0x5048; ~50 other spaced dashes left as is, not flagged)
- [x] Ryoma's ピッツァ/ぴっつぁ -> "peetsa" everywhere he says it (skit lines ui_skit_00:0x29cc/0x6588 too); translator brief updated

#### 19_bonus_4
- [x] b_016001:0x7b78 Takasugi それはオレ様のセリフだ: -> "I should be the one asking that! I'm ashamed of you, Katsura-san. You of all people!"
- [x] b_018001:0xa414 Ii: -> "can I catch whoever that is?"

## Skit balloon centring (phase 8, visual QA r3)
- [x] ui_skit_*: fixed by `insert.TEXT_CODE` (0x088545d4..fc: the line is measured with 0x08805524, font advances
  summed; text.md §8); lines centred in game (`gallery_skit_more`, visual QA r4). Was: the skit balloon centres each line as if every byte were 8 px wide (start = centre - bytes*4; measured
  on `warp.py gallery_skit_more`: "Cheeeers!!" at x 257, the 36-char line at 152), so proportional English sits left
  of centre, long lines most (~45 px). Legible, inside the balloon. Fix: find the skit line-centring code (EBOOT,
  like `ADV_CODE`) and make it sum the font17 advances; waive if it is not a small patch.
