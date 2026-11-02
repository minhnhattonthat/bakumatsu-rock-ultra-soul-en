# Glossary - Bakumatsu Rock: Ultra Soul

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: when a JP term appears, its EN form must appear (case-insensitive), and
an `Avoid` spelling fails. Name + honorific (龍馬さん) must come out as `Ryoma-san`.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ryoma-san, Hijikata-san, Okita-kun, Yoshinobu-sama). Name order: Western (given name first).
- Romanisation: official English (the 2014 anime "Samurai Jam -Bakumatsu Rock-") where it exists, else Hepburn
  without macrons (Ryoma, not Ryōma).
- Credits: English. Abbreviations: never to fit; report `LONG:` instead.
- Spelling: US English (honored, license, favorite, recognize, practiced, traveler).
- Register: a rock-and-roll comedy set in an alternate Bakumatsu: modern, punchy, playful English with period names
  and titles kept (shogun, shogunate, Shinsengumi). No archaic "thee/thou". Sound effects: *Slam!*, *Clang!*.

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...' (titles of songs in quotes), ……/・・・ -> `...`, ―― -> `--`, ！？ -> `!?`,
  ～ / ー stretches -> a stretched word ("Heeey") or `~` dropped. No fullwidth characters.
- Voices: `docs/style-reference.md` (per character JP markers -> English devices).
- Song titles stay as the game gives them in English ("Rolling Thunder", "What's this?"); Japanese titles get a
  translation in quotes the first time a batch needs one, reported as NEW TERM.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 坂本龍馬 | Ryoma Sakamoto | | lead guitar/vocals, Tosa | Sakamoto Ryoma |
| 龍馬 | Ryoma | | | Ryouma |
| 高杉晋作 | Shinsaku Takasugi | | guitar, Choshu, self-styled "ore-sama" | Takasugi Shinsaku |
| 高杉 | Takasugi | | | |
| 桂小五郎 | Kogoro Katsura | | bass/keys, inventor | Katsura Kogoro |
| 桂 | Katsura | | | |
| 土方歳三 | Toshizo Hijikata | | Shinsengumi vice-commander | Toshizou |
| 土方 | Hijikata | | | |
| 沖田総司 | Soji Okita | | Shinsengumi idol | Souji |
| 沖田 | Okita | | | |
| 徳川慶喜 | Yoshinobu Tokugawa | | the shogun | |
| 一橋慶喜 | Yoshinobu Hitotsubashi | | Yoshinobu before he became shogun | |
| 慶喜 | Yoshinobu | | | |
| 井伊直弼 | Naosuke Ii | | | |
| 井伊 | Ii | | | |
| 吉田松陰 | Shoin Yoshida | | | |
| 松陰 | Shoin | | | |
| 岩崎弥太郎 | Yataro Iwasaki | | Ryoma's childhood friend/manager | |
| 弥太郎 | Yataro | | | |
| 近藤勇 | Isami Kondo | | Shinsengumi commander | |
| 近藤 | Kondo | | | |
| 阿部正弘 | Masahiro Abe | | | |
| 勝海舟 | Kaishu Katsu | | | |
| お登勢 | Otose | | runs the Terada inn | |
| お龍 | Oryo | | | |
| 幾松 | Ikumatsu | | | |
| おうの | Ouno | | | |
| 乙女 | Otome | | Ryoma's sister | |
| 天狗 | Tengu | | | |
| 誠仮面 | Makoto Mask | | masked hero (Hijikata in disguise) | |
| ジュニア | Junior | | | |
| 老中 | Elder | | shogunate senior councillor (rōjū) | |
| ト書き | Narration | | speaker label for narration | |
| マシューカルブレイスペリージュニア | Matthew Calbraith Perry Junior | | full name of Junior | |
| ヒジゾー | Hijizo | | Ryoma's nickname for Hijikata (ヒジゾーさん -> Hijizo-san) | |
| ソウちん | So-chin | | Ryoma's nickname for Okita | |
| トサカ | Tosaka | | Okita's nickname for Ryoma (トサカくん -> Tosaka-kun) | |
| シンディ | Shindy | | Ryoma's nickname for Takasugi | |
| センセー | Sensei | | Ryoma's name for Katsura | |
| テンちゃん | Ten-chan | | the Tengu | |
| 龍ちゃん | Ryo-chan | | Otose's name for Ryoma | |
| 女将 | Landlady | | Otose | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 土佐 | Tosa | | | |
| 長州 | Choshu | | | Chōshū |
| 江戸 | Edo | | | |
| 富士 | Fuji | | | |
| テラーダ | Terada | | Otose's inn (live house); アルベルゴ ディテラーダ -> Albergo di Terada | Teradaya |
| 錦市場 | Nishiki Market | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 天歌 | Heaven's Song | | the shogunate's mandated songs (anime: ヘヴンズソング) | Tenka, Heavenly Song |
| 天歌泰平 | Heaven's Song Peace | | chapter / slogan: peace under the Heaven's Song | |
| 愛獲 | idol | | 愛獲 is read aidoru; the Shinsengumi are idols | |
| 雷舞 | live | | read raibu = a live show; "Special Live" | |
| 超魂團 | Ultra Soul | | the five-man band's name (團 = group) | Chokon |
| 超魂 | Ultra Soul | | | |
| 新選組 | Shinsengumi | | | Shinsen-gumi |
| 幕府 | shogunate | | | bakufu |
| 将軍 | shogun | | | |
| 志士 | rebel | | 志士 = the loyalist activists; "three rebels" | shishi |
| 大舞台 | audition | | when glossed （オーディション）; 大舞台会場 -> audition hall | |
| 片魂 | Piece Soul | | 片魂（ピースソウル）, plural Piece Souls | |
| 天歌師範 | Heaven's Song master | | | |
| 黒船 | Black Ships | | 黒船来航 -> the arrival of the Black Ships | |
| 六絃琴 | six-string | | Ryoma's guitar | |

## Phrases
- 京 -> Kyoto (京の都 -> "the capital, Kyoto" / "Kyoto"). 烈（レッツ）ロックンロォォル -> "Let's rock 'n' rooooll!".
- Junior's 大体オッケー -> "pretty much okay". 紹介状 -> letter of introduction; 免状 -> license; 死罪 -> death
  penalty (a shout may cut it to "DEATH!?").
- モジャモジャの先生 -> the Shaggy Sensei. 龍さん (Yataro) -> Ryo-san. お登勢やん -> Otose-yan. ♪ -> ~.

## Decisions from earlier batches
- (none yet)
