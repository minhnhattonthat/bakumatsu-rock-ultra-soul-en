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
| 高杉晋作 | Shinsaku Takasugi | | bass (ベース), Choshu, self-styled "ore-sama" | Takasugi Shinsaku |
| 高杉 | Takasugi | | | |
| 桂小五郎 | Kogoro Katsura | | drums (ドラム), inventor | Katsura Kogoro |
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
| 女将 | landlady | | Otose; 女将さん -> plain "landlady" (lowercase = no "-san" form) | |

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
| 大舞台（オーディション） | audition | | glossed form enforced; bare 大舞台 = the audition in the story, or "a big stage" when literal; 大舞台会場 -> audition hall | |
| 片魂 | Piece Soul | | 片魂（ピースソウル）, plural Piece Souls | |
| 天歌師範 | Heaven's Song master | | | |
| 黒船 | Black Ships | | 黒船来航 -> the arrival of the Black Ships | |
| 六絃琴 | six-string | | Ryoma's guitar | |
| 千塵万華 | Alter Soul | | Ii's curse technique, 千塵万華（オルターソウル） | |
| 呪魂 | Dark Soul | | 呪魂（ダークソウル）, b_007001 | |
| 雷舞券 | ticket | | 雷舞券（チケット） -> live ticket | |
| 局長 | Commander | | Kondo (Shinsengumi) | |
| 副長 | Vice-Commander | | Hijikata | |
| 一番隊組長 | First Unit | | Okita: "Captain of the (Shinsengumi's) First Unit" | |
| 暗黒桜桃隊 | Dark Cherries | | the girls' unit, 暗黒桜桃隊（ダークチェリーズ） | Dark Cherry Corps |
| 黄泉の歌姫 | Divas of the Underworld | | | |
| スカシくん | Mr. Poser | | Okita's name for Takasugi | Dud-kun |
| 苺慶喜 | strawberry Yoshinobu cake | | ichigo keiki pun; a clipped 慶喜 (the cake) -> "Yoshinobu" | Keiki-cake |
| (style) | | | Avoid list applies to every line: British forms (US English ruling) | Oi, you lot |
| 姐さん | Sis | | お龍姐さん -> Sis Oryo | Big Sis |
| ヨッシー | Yosshi | | Ryoma's nickname for Yoshinobu | |
| ショウ | Show | | Shoin's stage name (Tengu, old rockers) | |
| 御前試合 | Royal Concert | | 御前試合（ロイヤルコンサート） | |
| 彦根 | Hikone | | Ii's domain | |
| 見回り隊 | patrol | | 見回り隊探知機（レーダー） -> patrol radar | |
| 龍子 | Ryoko | | drag-bar stage name (源氏名 -> stage name) | |
| 歳子 | Toshiko | | drag-bar stage name | |
| 桂子 | Keiko | | drag-bar stage name | |
| 総美 | Somi | | drag-bar stage name | |
| 晋子 | Shinko | | drag-bar stage name | |
| 大江戸天歌祭 | Great Edo Heaven's Song Festival | | | |
| ハチノジディストーション | Figure-Eight Distortion | | song | |
| 共鳴進歌 | Resonant Evolution | | song (進化 pun) | |
| 生きてゆこう | Let's Live On | | song | |
| モット!!! | MORE!!! | | song | |
| 群青を射す光 | Light Piercing the Ultramarine | | song | |
| 不完全パズル | Incomplete Puzzle | | song | |
| 混色様式 | Mixed Color Style | | song: GOD BREATH -Mixed Color Style- | |
| 宙ノ翼 | Wings of the Sky | | song | |
| 絶頂DAYBREAK | Zenith DAYBREAK | | song | Climax DAYBREAK |
| 光の原石 | The Uncut Gem of Light | | song | |
| サークルサークル | Circle Circle | | song | |
| 非常幻想オーバーミラージュ | Extraordinary Fantasy Over Mirage | | song | |
| 松下村塾 | Shoka Sonjuku | | Shoin's school | |
| 壬生組 | Mibu-gumi | | | |
| 記録メディア | Memory Stick | | system text | |
| 溜詰 | Inner Council | | Ii's seat (溜間詰 lords) | Tamarizume |
| 老中首座 | Chief Elder | | 老中 = Elder; 老中筆頭 head of the Elders | |
| 五大ツアー | Big Five Tour | | | |
| 宴の松原 | En no Matsubara | | first mention: "the En no Matsubara, the Banquet Pines" | |
| 奇兵隊 | Strange Rockers | | 奇兵隊（ストレンジロッカーズ） | Kiheitai |

## Phrases
- 京 -> Kyoto (京の都 -> "the capital, Kyoto" / "Kyoto"). 烈（レッツ）ロックンロォォル -> "Let's rock 'n' rooooll!".
- Junior's 大体オッケー -> "pretty much okay". 紹介状 -> letter of introduction; 免状 -> license; 死罪 -> death
  penalty (a shout may cut it to "DEATH!?").
- モジャモジャの先生 -> the Shaggy Sensei. 龍さん (Yataro) -> Ryo-san. お登勢やん -> Otose-yan. ♪ -> ~.

## Decisions from earlier batches
- Ruby words (JP（English reading）): use the reading. 火威斗（ビート） beat, 仲間（メンバー） member/bandmate, 志士（ロッカー）
  rebel rocker, 煌（ファン） fan, 喩似尊（ユニゾン） unison, 旋律（メロディ） melody, 入魂（ソウルフル） soulful, 合奏（セッション）
  session. Plain 仲間 -> comrade(s)/friends; 同志 -> "share the same cause"; 腐れ縁 -> "stuck with each other".
- Nicknames: 晋作 (Katsura) Shinsaku; トシ (Kondo) Toshi; 晋ちゃん / 五郎ちゃん (Otose) Shin-chan / Goro-chan;
  総司様 / 総司くん (fans) Soji-sama / Soji-kun. 御神祖様 -> our divine founder (Ieyasu). 選抜隊士 / 選抜雷舞 -> select
  members / select live.
- お発勢 -> Ohase (Otose's cousin; Ohase-yan / Ohase-san). 大老 -> Great Elder (Ii). 泰平化 -> pacification/pacified.
  突風雷舞 -> guerrilla live (巡回突風雷舞 touring guerrilla lives). イケダヤン -> Ikedayan. 鳳舞合奏（フェニックスライジング）
  Phoenix Rising; 鳳舞（フェニックスダンス） Phoenix Dance; 囚須（トランス） trance; 天使の双璧（ユニット） the Angelic Duo;
  瓦落多（ガラクタ） junk; 蓄音機 phonograph; メガネくん Glasses-kun; 若年寄 (teasing Katsura) young fogey.
  雷ロックンロール (Takasugi) -> "Thunder rock 'n' roll!". 御大老様 -> Your Excellency (the Great Elder); 井伊大老 ->
  Great Elder Ii. Ii's chant オン キリキリバサラ ウンハッタ -> "On kiri kiri basara un hatta". 誠の道 -> the path of
  sincerity. オッサン (Ryoma, of Kondo) -> old man / ol' Kondo. 片魂仲間（ソウルメイト） Piece Soul mates; 男前（イケメン）
  hunks; ロックバカ rock-crazy idiot; ショウ (Shoin's stage name) Show. 鮒鮨 funazushi. A name + 殿/さん may use the
  family name when the speaker would (Ii: "Sakamoto-dono"). 『重力のない世界』 'A World Without Gravity' (Katsura's
  song); 交響曲第一章 煌燐雅劇（フライングシンフォニア） Symphony Movement One: Flying Symphonia; 御礼（サービス） fan service;
  能天気 (pun on 上天気) "sunshine between the ears"; 玉子酒 egg sake; 流鏑馬 horseback archery; 二条城 Nijo Castle.
  スカシくん's スカ死 pun -> "From Poser to decomposer!". 愛獲三娘（ユニット） idol unit; 姐さん (to Oryo) Sis; ボウヤ
  (Oryo to Takasugi) boy; 痺れ玉 numbing bomb; 小柄 throwing knives; 合一（フュージョン） Fusion; ご家老様 (Oryo to Ii) my
  lord; ゲーベル銃 Geweer rifle; 茶店（カフェ） cafe. "Oi" is British: Takasugi says "Hey".
- b076-b079: 色男 ladies' man; 『場亜　オカマちゃん』 'Bar Okama-chan'; オカマバー drag bar; オカマちゃん愛獲 drag idols;
  オカマちゃん (generic) drag darlings; 隊名 band name; 乙女姉やん Sis Otome; 迅馬笛（ジンバブエ） the Zimbabwe;
  (お)腹の虫 the hunger bug; 鼓舞鳥隊 (こぶとり pun) the Bold Eagles; Ｒ安堵Ｒ R&R. 色男 lady-killer (with ruby イケメン:
  hunk); 戻るんるん Rewinderoo; skit end card 『X』　おわり -> 'X' -- The End; Heaven's Song never takes "the" unless
  it modifies a noun (the Heaven's Song Festival); 一件落着 "this matter is settled" (not "Case closed" where Ryoma's quip follows).
  黄泉路の歌姫 the Diva of the Underworld; 幾松姐さん Sis Ikumatsu; 地下愛獲 underground idol; 看板娘 poster girls;
  一人雷舞（ソロライブ） solo live; お白州 the court; 総ちゃん (Otose) So-chan; カイ (Katsu's old stage name) Kai; 勝先生
  Katsu-sensei; ケツの穴の小せえ "chickenshit" (timid, not uptight).
- 上様: "Ue-sama" only in m_010002 where Ryoma takes the title for a name; elsewhere "His Highness"/"my lord".
  将軍様 -> Lord Shogun. Junior's names: ナデシコ Nadeshiko (Okita), レッドボーイ Red Boy, モンキー Monkey (Ryoma); Ｊ J.
  ヱゲレス/エゲレス English; ヨタ話 tall tale; 龍河洞 Ryugado; カスティラ castella; 蘭出舞 rendezvous; 判じ物 hanjimono;
  誠仮面 Makoto Mask; 勝老中 Elder Katsu; ペリージュニア Perry Junior; 贔屓倶楽部 fan club; 眠り病 sleeping sickness;
  小姓 page; 徳川の怨念 the Tokugawa grudge; 魂友（ソウルメイト） soulmates; 千利休 Sen no Rikyu; メリケン America.
  大江戸天歌祭 the Great Edo Heaven's Song Festival; なか吉屋 Nakayoshiya Beef Bowls; 戒厳令 martial law. 烈シンギング -> "Let's SING!".
- 雷舞屋（ライブハウス） live house; 最高雷舞屋（メジャーライブハウス） major live house; 愛獲笑顔（アイドルスマイル） idol smile;
  癒声（ヒーリングボイス） healing voice; 雷光（スパーク） spark; 稽古（リハーサル） rehearsal; 稽古場（スタジオ） studio;
  エレキテル elekiter (エレキ electricity); 平賀源内 Gennai Hiraga; 超スベールＸ Super Slipperoo X; 隊士 troopers;
  スカシくん (Okita to Takasugi) Mr. Poser; 天然 natural-born airhead; 敵（ライバル） rival; 団主（ダンス） dance;
  大伝聞（ニュース） big news; 御用改めである "This is an official inspection!"; 未来来る（ミラクル） MIRACLE;
  解散 (Takasugi's catchphrase) "We're breaking up!"; お兄ちゃん (a child, to Ryoma) mister.
- Food/props: ハリセン paper fan; 鰹のたたき seared bonito; おはぎ ohagi.
- Running gag バカボケナス野郎 -> "stupid, bonehead, turnip-brained jackass" (same wording every time).
- Speaker tags in the batch TSVs (`ryoma?`) are the last sprite loaded, often wrong: read the speaker from content.
