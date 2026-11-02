# Glossary - Seireiki Rayblade (聖霊機ライブレード)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the Characters, Places, Mechs, Weapons and Items tables (the EN form must appear when
the JP term does, as a whole katakana/kanji run) and the speaker tags; the Reference table is advice only.
Seeded from the Dreamcast fan project's glossary (docs/re/prior-work.md; D2: earlier fan patch when no official name).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Touya-chan, Ymir-san, Celica-sama, Ayaka-sensei). Name order: Western (given name
  first): カザミ・トウヤ -> Touya Kazami.
- Romanisation source: official English names (title screen, in-game English, art), else the earlier (DC) fan patch's
  glossary, else Hepburn without macrons.
- Credits: English.
- Register / flavour: keep light JP flavour (honorifics, mecha/fantasy terms). Sound effects: *Slam!*.
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening (D4). Over-long menu names are
  reported, not shortened.

## Style rules (D8)
- Speaker lines: `Name: text` - the JP `名前「...」` becomes the glossary name, a colon, a space, then the line with
  no quote marks. Thoughts `名前（...）` -> `Name: (text)`. `名前『...』` (Yamato's whispered/telepathic asides) ->
  `Name: 'text'`. The name must be exactly the glossary EN (the check enforces it per {page} segment).
- Lines that continue a speech without a name tag (start with a full-width space) are plain text.
- Quotes inside a line: 「」 and “” -> "...", 『』 -> '...' (a title or quoted phrase); ＜ゼ＝オード＞-style brackets
  around a proper noun are dropped: Ze=Ode.
- ‥‥ / ・・・ -> `...`; ！？/⁉ -> `!?`; ‼ -> `!!`; a dash or trailing-off -> `--` or `...`; ～ (drawn-out vowel) ->
  stretch the word ("Heeey", "Touyaaa") or a single `~` at the end.
- Only plain ASCII. No `{`/`}` except the control codes copied from the JP; never `[` + two hex digits + `]`.
- Write paragraphs: the tools wrap at 30 characters (dialogue) / 36 (battle) and page every 3 lines. Use `{nl}` only for a
  break that must fall at that spot (a list, a dramatic pause); copy every `{page}` (count is checked).
- Voices: docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ヴォーリア | Vorlia |  |  |  |
| トウヤ | Touya |  | male; Rayblade main pilot; summoned from Earth. |  |
| ヤマト | Yamato |  | female; Touya's cat and family member; becomes a cyborg cat. |  |
| ユミール | Ymir |  | female; Chief First-Class Scholar of the Holy Alchemical Society; technical pr |  |
| セリカ | Celica |  | female; Princess of Agarthia; engineer, programmer and later Selphin pilot. |  |
| アイ | Ai |  | female; Vishal pilot; Earth high school student. |  |
| フェイン | Fain |  | male; Knight and Rest's pupil; Mireon and later Dusseldorf pilot. |  |
| カスミ | Kasumi |  | female; Touya's childhood friend; later Orbest pilot. |  |
| オーレリィ | Aurelie |  | female; Parikar pilot. |  |
| クロビス | Clovis |  | male; Baldock pilot; former Brazilian Air Force and Smoke Squadron pilot. |  |
| レオーネ | Leone |  | female; Eleana pilot; artificially created human; Debish's daughter. |  |
| メルヴィ | Melvi |  | female; Forzen and Paldia's daughter; Ymir's niece; test pilot and later Forst |  |
| アーサー | Arthur |  | male; Drydes pilot; long-serving summoned member. |  |
| メリッサ | Melissa |  | female; Xiujian's lover; Baio's test pilot; possible Ahti pilot. |  |
| シィウチェン | Xiujian |  | male; Hongshenguang pilot; Melissa's lover. |  |
| デロック | Derock |  | male; Liebhofen navigator and gunnery officer; Sefia's fiance. |  |
| クルル | Kururu |  | female; Grad and Thora's daughter; Forstin simulator trainee. |  |
| ローディス | Lodis |  | male; Initially Crown Prince of Agarthia and first in succession; project in |  |
| ミヤスコ | Miyasco |  | female; Liebhofen communications officer; physician; Code 3 subject. |  |
| ゲン | Gen |  | male; Rosalie's younger brother; later Zeifon pilot. |  |
| カイン | Cain |  | male; Disinherited second prince of Limberg; Black Prince; clone created by  |  |
| ベルンスト | Bernst |  | male; Bioengineering specialist in Ze=Ode project; Gaiozon pilot. |  |
| デビッシュ | Debish |  | male; Ze=Ode project leader; Goderius pilot; Sharl and Leone's father. |  |
| シスク | Sisk |  | female; Liebhofen radar operator and galley chief; crown prince's lady-in-wait |  |
| ウェニマス | Wenimas |  | female; Ze=Ode researcher; Lyle's lover; Ymir's mother; later disembodied cons |  |
| ライル | Lyle |  | male; Self-taught researcher; Rayode pilot; Wenimas's lover and Ymir's fathe |  |
| ガボン | Gabon |  | male; Liebhofen engineer and doctor; cyborg-Yamato's surgeon. |  |
| レイフォン | Rayfon |  | male; Illegitimate son of Grand Duke Gaharin; Lodis's former close friend; c |  |
| ガリュード | Garyud |  | male; York knight; Sword Radiance title holder; Ciel's father; Bosendorfer p |  |
| 晃一郎 | Koichiro |  | male; Touya's high school friend. |  |
| ベイオ | Baio |  | male; Designant workshop owner, designer and accountant; Bio's older brother |  |
| リシュナ | Rishuna |  | female; Alien from Lin Karma; Coolmarishin pilot; borrows priestess Mana Elua' |  |
| シャール | Sharl |  | female; Alchemist; Debish's daughter and assistant; Leone's older sister; Part |  |
| グロウスター | Growster |  | male; Zigrim general; de facto military leader; Baresios commander. |  |
| ティックス | Tix |  | male; Prince of Agarthia; second in succession; younger brother of Lodis and |  |
| レデュース | Reduce |  | male; York royal guard; Three Sword Knights; Ragrade pilot; Reduce the Silve |  |
| シエル | Ciel |  | female; York royal guard; Three Sword Knights; Garyud's daughter; Almaris pilo |  |
| マキ | Maki |  | female; Freelance journalist; Reisuke's owner; Rest's partner. |  |
| レスト | Rest |  | male; Agarthian Army major; Phoenix knight; Fain's mentor and guardian; Zaxa |  |
| リーモンド | Reamond |  | male; Zigrim first lieutenant; Code 3 subject; Griol and Rayal Klose pilot. |  |
| タイロン | Tyron |  | male; York royal guard; Three Sword Knights; Brandeim pilot. |  |
| アルフォリナ | Alforina |  | female; Queen of York; gifted with foresight; supports Spirit Mech project. |  |
| イヴェル | Ivel |  | female; Highest authority in the Holy Land; knows Ymir's past. |  |
| フォルゼン | Forzen |  | male; Holy Land scholar and summoning negotiator; Ymir's brother; Melvi's fa |  |
| フォレス | Fores |  | female; Zigrim lieutenant colonel; commander; Griol pilot. |  |
| グラード | Grad |  | male; Zigrim major; Thora's husband and Kururu's father; custom Griol pilot. |  |
| ヴァルガ | Valga |  | male; Alien from Lin Karma; Sivarius pilot; awakens companions. |  |
| ムルク | Murk |  | male; Gazette Project head; genetic engineering authority at Brufle institut |  |
| シュテイニーズ | Steinies |  | male; Zigrim captain; personal Griol and Bargion pilot. |  |
| レンダー | Render |  | male; Dawn of an Era field commander; former Venir mercenary commander. |  |
| ロザリー | Rosalie |  | female; Gen's older sister; Liebhofen cook and general helper. |  |
| ドリス | Doris |  | female; Dei's secretary and partner in public and private life. |  |
| ヴァレス | Vales |  | male; Solitary Silver Wings commander; former foremost sacred royal knight;  |  |
| レギレス | Regiles |  | full name レギレス・ブライアー = Regiles Briar | Regiless |
| ホーレム | Horem |  | male; President of Zigrim; architect of York invasion. |  |
| レシュ | Resh |  | male; Dawn of an Era member; friend of Barkin. |  |
| エミィ | Emy |  | female; Gifted alchemist; Ymir's junior colleague. |  |
| バーキン | Barkin |  | male; Dawn of an Era member; secretly supports orphanage. |  |
| オズヴァルド | Oswald |  | male; York chancellor; conspirator with Zigrim. |  |
| ロア | Roa |  | male; Admiral; Liebhofen captain and commander; retired York soldier. |  |
| パルディア | Paldia |  | female; Forzen's wife; Melvi's mother; Ymir's sister-in-law. |  |
| バイオ | Bio |  | male; Baio's younger brother and sponsor; supplies terrorists. |  |
| ジョノ | Jono |  | male; Solitary Silver Wings mercenary; proposes to Ymir. |  |
| ヴェル | Vel |  | male; Solitary Silver Wings mercenary; former scrap dealer. |  |
| バレン | Baren |  | male; Liebhofen helmsman; wanted to become an alchemist. |  |
| トーラ | Thora |  | female; Grad's wife; Kururu's mother. |  |
| ゴウ | Goh |  | unconfirmed; Veteran mercenary alongside Render. |  |
| ヨアニス | Ioannis |  | male; Third son of a middling noble family; Dawn of an Era financial patron. |  |
| ギール | Geel |  | male; Agarthian Army colonel; Marshal Revios's right-hand man. |  |
| フェイン・ジン・バリオン | Fain Jin Barion |  | male; Knight and Rest's pupil; Mireon and later Dusseldorf pilot. |  |
| バート | Bart |  | male; Liebhofen purser; operational records and accounting. |  |
| デイ | Dei |  | male; Agarthian Council chairman; Dawn of an Era leader; vessel for Debish. |  |
| セルグ | Selg |  | male; Agarthian Army lieutenant colonel; Domanon pilot. |  |
| リョード | Ryord |  | male; Dawn of an Era member; Kinari's friend. |  |
| キナリ | Kinari |  | male; Lowest-ranking newcomer; former Ioannis hanger-on. |  |
| レビオス | Revios |  | male; Agarthian marshal; deputy commander of general staff. |  |
| レニス | Lenis |  | male; Scientist; Lyle's younger twin; former Rayode pilot; Touya's ancestor. |  |
| ガルナ | Garna |  | male; Veteran York knight; Roa's old comrade; Garyud's early mentor. |  |
| 綾華 | Ayaka |  | female; Touya's new teacher; former shrine maiden from priestly family. |  |
| グラウザー | Grauzer |  | male; Alien from Lin Karma; Shinkaio designer; Aidion pilot; shares existenc |  |
| バルアミー | Baluamy |  |  |  |
| レイスケ | Reisuke |  | not applicable; device; Computerized camera 03K-01 owned by Maki; nickname Reisuke. |  |
| セレア | Celea |  | female; Bio's secretary and mistress. |  |
| グラード・バーグリー | Grad Burgley |  | male; Zigrim major; Thora's husband and Kururu's father; custom Griol pilot. |  |
| ワーグス | Wargs |  | unconfirmed; Agarthian councilor. |  |
| ユミール・エアル・クラシオ | Ymir Eal Clasio |  | female; Chief First-Class Scholar of the Holy Alchemical Society; technical pr |  |
| バフレッド・デビッシュ | Bafred Debish |  | male; Ze=Ode project leader; Goderius pilot; Sharl and Leone's father. |  |
| クロビス・カミリオン | Clovis Camillion |  | male; Baldock pilot; former Brazilian Air Force and Smoke Squadron pilot. |  |
| マーシャ | Marsha |  | female; Murk's personal assistant; later successor; self-taught alchemical kno |  |
| トウヤ・カザミ | Touya Kazami |  | male; Rayblade main pilot; summoned from Earth. |  |
| ライル・エンロード | Lyle Enroad |  | male; Self-taught researcher; Rayode pilot; Wenimas's lover and Ymir's fathe |  |
| レニス・エンロード | Lenis Enroad |  | male; Scientist; Lyle's younger twin; former Rayode pilot; Touya's ancestor. |  |
| アーサー・ヌコモ | Arthur Nkomo |  | male; Drydes pilot; long-serving summoned member. |  |
| ローディス・ラング・メスティナ | Lodis Lang Mestina |  | male; Initially Crown Prince of Agarthia and first in succession; project in |  |
| ガリュード・ビア・ヴラッツェン | Garyud Via Vratzen |  | male; York knight; Sword Radiance title holder; Ciel's father; Bosendorfer p |  |
| ウェニマス・ラティーア | Wenimas Latia |  | female; Ze=Ode researcher; Lyle's lover; Ymir's mother; later disembodied cons |  |
| ゲンズバリオレッド・メルセーヌ | Genzbariored Mercene |  | male; Rosalie's younger brother; later Zeifon pilot. |  |
| セリカ・ラニアード・メスティナ | Celica Laniard Mestina |  | female; Princess of Agarthia; engineer, programmer and later Selphin pilot. |  |
| シエル・レン・ヴラッツェン | Ciel Ren Vratzen |  | female; York royal guard; Three Sword Knights; Garyud's daughter; Almaris pilo |  |
| ベルンスト・ビューロー | Bernst Bulow |  | male; Bioengineering specialist in Ze=Ode project; Gaiozon pilot. |  |
| レオーネ・デビッシュ | Leone Debish |  | female; Eleana pilot; artificially created human; Debish's daughter. |  |
| レジオナル | Reginal |  | male; King of Agarthia; widower of Ipha; father of Lodis, Celica and Tix. |  |
| ネル・ホーレム | Nell Horem |  | male; President of Zigrim; architect of York invasion. |  |
| デイ・ラクバル | Dei Rakbal |  | male; Agarthian Council chairman; Dawn of an Era leader; vessel for Debish. |  |
| エレナ | Elena |  | female; Clovis late wife; daughter of his former military superior. Full name  |  |
| オーレリィ・パンダボアヌ | Aurelie Pandavoine |  | female; Parikar pilot. |  |
| メリッサ・グールド | Melissa Gould |  | female; Xiujian's lover; Baio's test pilot; possible Ahti pilot. |  |
| フォレス・ミシュアル | Fores Mishual |  | female; Zigrim lieutenant colonel; commander; Griol pilot. |  |
| アルフォリナ・エル・イスターシュ | Alforina El Istarsh |  | female; Queen of York; gifted with foresight; supports Spirit Mech project. |  |
| アイ・テンノージ | Ai Tennoji |  | female; Vishal pilot; Earth high school student. |  |
| カスミ・スオウ | Kasumi Suoh |  | female; Touya's childhood friend; later Orbest pilot. |  |
| ロザリー・テオラ・メルセーヌ | Rosalie Theora Mercene |  | female; Gen's older sister; Liebhofen cook and general helper. |  |
| メルヴィ・クラシオ | Melvi Clasio |  | female; Forzen and Paldia's daughter; Ymir's niece; test pilot and later Forst |  |
| ロア・ジン・クランクハイト | Roa Jin Krankheit |  | male; Admiral; Liebhofen captain and commander; retired York soldier. |  |
| ルーファス | Rufus |  | male; Agarthian councilor; well-born and well-educated noble scion. |  |
| フィリス | Phyllis |  | female; Third Princess Phyllis Alma Falmight; Ciel mother and past sole surviv |  |
| コォウ・シィウチェン | Guo Xiujian |  | male; Hongshenguang pilot; Melissa's lover. |  |
| クルル・バーグリー | Kururu Burgley |  | female; Grad and Thora's daughter; Forstin simulator trainee. |  |
| バルアミークイーン | Baluamy Queen |  |  |  |
| リーモンド・ダライム | Reamond Dalaim |  | male; Zigrim first lieutenant; Code 3 subject; Griol and Rayal Klose pilot. |  |
| アナベラ | Annabella |  | female; Agarthian councilor; noblewoman. |  |
| タイロン・レン・アースダルアー | Tyron Ren Arsdaluar |  | male; York royal guard; Three Sword Knights; Brandeim pilot. |  |
| レイフォン・ラング・マクソード | Rayfon Lang Maxord |  | male; Illegitimate son of Grand Duke Gaharin; Lodis's former close friend; c |  |
| レスト・ジン・ベニッシュ | Rest Jin Benish |  | male; Agarthian Army major; Phoenix knight; Fain's mentor and guardian; Zaxa |  |
| ヴァルガ・ソルマ | Valga Solma |  | male; Alien from Lin Karma; Sivarius pilot; awakens companions. |  |
| シュテイニーズ・ファルモア | Steinies Falmore |  | male; Zigrim captain; personal Griol and Bargion pilot. |  |
| ガボン・ジン・ボレイショ | Gabon Jin Boleisho |  | male; Liebhofen engineer and doctor; cyborg-Yamato's surgeon. |  |
| イヴェル・エアル・ロシュフォルン | Ivel Eal Rochforn |  | female; Highest authority in the Holy Land; knows Ymir's past. |  |
| フォルゼン・ジン・クラシオ | Forzen Jin Clasio |  | male; Holy Land scholar and summoning negotiator; Ymir's brother; Melvi's fa |  |
| リカーラ | Ricara |  | female; Former principal consort of Limberg; Cain's mother. Estate registered  |  |
| ギール・ジン・ディアル | Geel Jin Dial |  | male; Agarthian Army colonel; Marshal Revios's right-hand man. |  |
| バルアミーノーブル | Baluamy Noble |  |  |  |
| シャール・デビッシュ | Sharl Debish |  | female; Alchemist; Debish's daughter and assistant; Leone's older sister; Part |  |
| ベイオ・ダングル | Baio Dangle |  | male; Designant workshop owner, designer and accountant; Bio's older brother |  |
| ヴァレス・ブライアー | Vales Briar |  | male; Solitary Silver Wings commander; former foremost sacred royal knight;  |  |
| ミヤスコ・ジニア・ブランブレ | Miyasco Ginia Bramble |  | female; Liebhofen communications officer; physician; Code 3 subject. |  |
| バレン・ジン・ヨークル | Baren Jin Jokul |  | male; Liebhofen helmsman; wanted to become an alchemist. |  |
| デロック・ジン・エイカク | Derock Jin Eikak |  | male; Liebhofen navigator and gunnery officer; Sefia's fiance. |  |
| バート・ジン・ガッキョク | Bart Jin Gakkyok |  | male; Liebhofen purser; operational records and accounting. |  |
| ムルク・エルク・ベルオール | Murk Elk Berol |  | male; Gazette Project head; genetic engineering authority at Brufle institut |  |
| マキ・テオラ・トレス | Maki Theora Tres |  | female; Freelance journalist; Reisuke's owner; Rest's partner. |  |
| トーラ・バーグリー | Thora Burgley |  | female; Grad's wife; Kururu's mother. |  |
| セフィア | Sefia |  | female; Derock's fiancee and childhood friend; belongs to La=Dis. |  |
| オズヴァルド・レイオ・エグゾギルム | Oswald Reio Exogilm |  | male; York chancellor; conspirator with Zigrim. |  |
| ルーナ | Luna |  | female; Palace maid who helped Tix escape Cain, according to Tix's account. |  |
| アクレシア | Aclesia |  | People army figurehead in overthrow of Falmight tyrant; parent of Ciel |  |
| ティックス・ラング・メスティナ | Tix Lang Mestina |  | male; Prince of Agarthia; second in succession; younger brother of Lodis and |  |
| レデュース・レン・クロムハーツ | Reduce Ren Chromehearts |  | male; York royal guard; Three Sword Knights; Ragrade pilot; Reduce the Silve |  |
| セルグ・ジン・ボイヤード | Selg Jin Boyard |  | male; Agarthian Army lieutenant colonel; Domanon pilot. |  |
| カイン・イスファンデイル | Cain Isfandeil |  | male; Disinherited second prince of Limberg; Black Prince; clone created by  |  |
| ブレイン・コア | Brain Core |  |  |  |
| ドリス・ベンフィス | Doris Benfis |  | female; Dei's secretary and partner in public and private life. |  |
| ヴェル・ドレスナ | Vel Dresna |  | male; Solitary Silver Wings mercenary; former scrap dealer. |  |
| レジオナル・ラング・メスティナ | Reginal Lang Mestina |  | male; King of Agarthia; widower of Ipha; father of Lodis, Celica and Tix. |  |
| ガルア | Garua |  |  |  |
| ダーレン | Darren |  |  |  |
| ルディス | Rudis |  | male; Orphan nicknamed Rudi; older-brother figure to Rii and Demi. |  |
| デミット | Demitt |  | male; Orphan nicknamed Demi; brought by Barkin's sister; current name is not |  |
| イーファ | Ipha |  | female; Deceased Agarthia queen; mother of Lodis, Celica and Tix. Lodis was al |  |
| リカーラ・ゼア・イスファンデイル | Ricara Zea Isfandeil |  | female; Former principal consort of Limberg; Cain's mother. Estate registered  |  |
| ジーナ | Gina |  | female; Barkin's deceased younger sister; former palace lady-in-waiting in Lim |  |
| フィセル | Fisel |  | Person addressed by Render in an apology during his desperate attack. |  |
| バルアミークイーン1 | Baluamy Queen 1 |  |  |  |
| バルアミークイーン2 | Baluamy Queen 2 |  |  |  |
| リシュナ（マナ・エルア） | Rishuna (Mana Elua) |  | female; Alien from Lin Karma; Coolmarishin pilot; borrows priestess Mana Elua' |  |
| ナガレク・グロウスター | Nagarek Growster |  | male; Zigrim general; de facto military leader; Baresios commander. |  |
| ヨアニス・サラム・レイドマン | Ioannis Salam Reidman |  | male; Third son of a middling noble family; Dawn of an Era financial patron. |  |
| レンダー・フォート | Render Fort |  | male; Dawn of an Era field commander; former Venir mercenary commander. |  |
| レシュ・ランカク | Resh Rankak |  | male; Dawn of an Era member; friend of Barkin. |  |
| バーキン・ガッシュ | Barkin Gash |  | male; Dawn of an Era member; secretly supports orphanage. |  |
| ゴウ・ブランケット | Goh Blanket |  | unconfirmed; Veteran mercenary alongside Render. |  |
| リョード・バークル | Ryord Burkle |  | male; Dawn of an Era member; Kinari's friend. |  |
| キナリ・ソクナ | Kinari Sokna |  | male; Lowest-ranking newcomer; former Ioannis hanger-on. |  |
| ジョノ・ボンドレー | Jono Bondre |  | male; Solitary Silver Wings mercenary; proposes to Ymir. |  |
| シスク・テオラ・レトレス | Sisk Theora Retres |  | female; Liebhofen radar operator and galley chief; crown prince's lady-in-wait |  |
| ガルナ・ジン・ノーマ | Garna Jin Norma |  | male; Veteran York knight; Roa's old comrade; Garyud's early mentor. |  |
| ディルマ・ジン・レビオス | Dilma Jin Revios |  | male; Agarthian marshal; deputy commander of general staff. |  |
| ガルア・ジン・デュレン | Garua Jin Duren |  |  |  |
| パルディア・テオラ・クラシオ | Paldia Theora Clasio |  | female; Forzen's wife; Melvi's mother; Ymir's sister-in-law. |  |
| グラウザー・ジェスティ | Grauzer Jesty |  | male; Alien from Lin Karma; Shinkaio designer; Aidion pilot; shares existenc |  |
| バイオ・ダングル | Bio Dangle |  | male; Baio's younger brother and sponsor; supplies terrorists. |  |
| セレア・セグニスタ | Celea Segnista |  | female; Bio's secretary and mistress. |  |
| ダーレン・オレイスキー | Darren Oreisky |  |  |  |
| セフィア・イユール | Sefia Iyul |  | female; Derock's fiancee and childhood friend; belongs to La=Dis. |  |
| リィスティ | Risty |  | unconfirmed; Orphan nicknamed Rii; close to Rudi and Demi; regards Barkin as father |  |
| リィスティ・クレイス | Risty Kreis |  | unconfirmed; Orphan nicknamed Rii; close to Rudi and Demi; regards Barkin as father |  |
| アナベラ・カティサーク | Annabella Cutty Sark |  | female; Agarthian councilor; noblewoman. |  |
| ワーグス・モンブレン | Wargs Montblanc |  | unconfirmed; Agarthian councilor. |  |
| ルーファス・ザーベイル | Rufus Sabeil |  | male; Agarthian councilor; well-born and well-educated noble scion. |  |
| ルディス・ラインデイル | Rudis Line Dale |  | male; Orphan nicknamed Rudi; older-brother figure to Rii and Demi. |  |
| デミット・カイモン | Demitt Kaimon |  | male; Orphan nicknamed Demi; brought by Barkin's sister; current name is not |  |
| エミィ・エアル・キャルタス | Emy Eal Kyaltas |  | female; Gifted alchemist; Ymir's junior colleague. |  |
| カルシオン | Kalsion |  | Mayor of Karua Kalba; immediately supports Lodis's Holy War declaratio |  |
| カルシオン・レンワード | Kalsion Renward |  | Mayor of Karua Kalba; immediately supports Lodis's Holy War declaratio |  |
| フィリス・アルマ・ファルマイト | Phyllis Alma Falmight |  | female; Third Princess Phyllis Alma Falmight; Ciel mother and past sole surviv |  |
| クラース | Klaas |  | male; Last king of the former Falmight dynasty, overthrown by the people arm |  |
| アクレシア・エル・イスターシュ | Aclesia El Istarsh |  | People army figurehead in overthrow of Falmight tyrant; parent of Ciel |  |
| トウヤちゃん | Touya-chan |  |  |  |
| フェインちゃん | Fain-chan |  |  |  |
| リィ | Rii |  |  |  |
| ルディ | Rudi |  |  |  |
| デミー | Demi |  |  |  |
| バルちゃん | Little Balu |  |  |  |
| ヴァルガっち | Valga-cchi |  |  |  |
| ユミール二世 | Ymir the Second |  |  |  |
| パティシエ・アイちゃん | Patissier Ai-chan |  |  |  |
| 千尋 | Chihiro |  |  |  |
| ガイウス | Gaius |  |  |  |
| マナ・エルア | Mana Elua |  |  |  |
| フラム・ゼオ・イスファンデイル | Fram Zeo Isfandeil |  |  |  |
| リシュナ・ミルシュ | Rishuna Milsh |  |  |  |
| マリエ・クリスティル | Marie Christil |  |  |  |
| ガイザルディングテリウス・ジン・メルセーヌ | Gaizardingterius Jin Mercene |  |  |  |
| イーファ・ラニアード・メスティナ | Ipha Laniard Mestina |  |  |  |
| 天草四郎 | Amakusa Shiro |  |  |  |
| カート・エルク・プラーム | Kurt Elk Plaam |  |  |  |
| オーキス | Orkis |  |  |  |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ファルマイト | Falmight |  |  |  |
| イスターシュ王家 | Istarsh royal family |  |  |  |
| ファルマイト王家 | Falmight royal family |  |  |  |
| アガルティア王家 | Agarthia royal family |  |  |  |
| クラシオ家 | Clasio family |  |  |  |
| ジグリム共和国 | Zigrim Republic |  |  |  |
| 時代の曙 | Dawn of an Era |  |  |  |
| アガルティア評議会 | Agarthian Council |  |  |  |
| 孤高の銀翼 | Solitary Silver Wings |  |  |  |
| 国連 | United Nations |  |  |  |
| 王宮騎士団 | Royal Knights |  |  |  |
| ベルオール研究所 | Berol Research Institute |  |  |  |
| 連盟議会 | League Assembly |  |  |  |
| ヴェニル | Venir |  |  |  |
| 全国女子高生連合 | National High School Girls' Union |  |  |  |
| 国民労働党 | National Labor Party |  |  |  |
| 近衛騎士団 | Royal Guard |  |  |  |
| 錬金学聖協会 | Holy Alchemical Society |  |  |  |
| ブルフレ人工進化研究所 | Brufle Artificial Evolution Research Institute |  |  |  |
| ジグリム共和国軍第二師団 | Zigrim Republic Army's Second Division |  |  |  |
| アルマ方面軍 | Alma Front Army |  |  |  |
| アガルティア | Agarthia |  |  |  |
| ヨーク | York |  |  |  |
| ジグリム | Zigrim |  | bare form of ジグリム共和国 |  |
| リンバーグ | Limberg |  | bare form of リンバーグ公国 |  |
| ゼ＝オード | Ze=Ode |  | ＜ゼ＝オードの恐怖＞ = the Ze=Ode Terror (the explosion 109 years ago) | Ze-Ode, Zeode |
| 三剣騎士 | Three Sword Knights |  | York's royal guard trio (Reduce, Tyron, Ciel) |  |
| 聖地 | Holy Land |  |  |  |
| アガルティア王国 | Kingdom of Agarthia |  |  |  |
| リン・カーマ | Lin Karma |  |  |  |
| フラムエルク城 | Flamuelk Castle |  |  |  |
| エステリア | Estelia |  |  |  |
| シャングリア | Shangria |  |  |  |
| コルネル村 | Cornel Village |  |  |  |
| ベルネア砦 | Belnea Fort |  |  |  |
| クロンデェム | Krondem |  |  |  |
| アルテリアス渓谷 | Alterias Valley |  |  |  |
| 刻の狭間 | Rift in Time |  |  |  |
| 臨海パーク | Seaside Park |  |  |  |
| ムールの樹海 | Muur Forest |  |  |  |
| グラスシェールの谷 | Glascher Valley |  |  |  |
| 封印の間 | Chamber of Sealing |  |  |  |
| 第二聖霊機格納庫 | Spirit Mech Hangar 2 |  |  |  |
| クルシエル通り | Crusiel Street |  |  |  |
| リンバーグ公国 | Principality of Limberg |  |  |  |
| ステラ・マルキス | Stella Marquis |  |  |  |
| ブランデンクロイス | Brandenkrois |  |  |  |
| 岬ヵ原公園 | Misakigahara Park |  |  |  |
| 成田 | Narita |  |  |  |
| ジンバブエ | Zimbabwe |  |  |  |
| ソールズベリー | Salisbury |  |  |  |
| クロンデェム鉱山跡 | Krondem mine ruins |  |  |  |
| カルア・カルバ | Karua Kalba |  |  |  |
| ホェライ川 | Hoelai River |  |  |  |
| 青木ヵ原樹海 | Aokigahara Forest |  |  |  |
| ハラレ | Harare |  |  |  |
| シェスタの店 | Shesta's shop |  |  |  |
| アガルティア王室アカデミー | Agarthian Royal Academy |  |  |  |

## Mechs
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ライブレード | Rayblade |  |  |  |
| リーボーフェン | Liebhofen |  |  |  |
| コア | Core |  |  |  |
| ゼイフォン | Zeifon |  |  |  |
| ダーガ | Daga |  |  |  |
| バイン・ダーガ | Bine Daga |  |  |  |
| ゴーデリウス | Goderius |  |  |  |
| エレアナ | Eleana |  |  |  |
| レイオード | Rayode |  |  |  |
| フォルスティン | Forstin |  |  |  |
| デュッセルドフ | Dusseldorf |  |  |  |
| ビシャール | Vishal |  |  |  |
| ガイオゾン | Gaiozon |  |  |  |
| ミレオン | Mireon |  |  |  |
| オルベスト | Orbest |  |  |  |
| エイディオン | Aidion |  |  |  |
| セルフィン | Selphin |  |  |  |
| アハティ | Ahti |  |  |  |
| ガドラン | Gadran |  |  |  |
| グリオール | Griol |  |  |  |
| バルドッグ | Baldock |  |  |  |
| ザクサス | Zaxas |  |  |  |
| パルテノス | Parthenos |  |  |  |
| ドライデス | Drydes |  |  |  |
| ヴェイル・アスティン | Veil Astin |  |  |  |
| クールマリシン | Coolmarishin |  |  |  |
| ラグレード | Ragrade |  |  |  |
| ベーゼンドルファー | Bosendorfer |  |  |  |
| ヘスティア | Hestia |  |  |  |
| パリカール | Parikar |  |  |  |
| シーヴァリアス | Sivarius |  |  |  |
| フェルミオン | Fermion |  |  |  |
| アルマリス | Almaris |  |  |  |
| ランドシップ | Landship |  |  |  |
| バレシオス | Baresios |  |  |  |
| ホンシェンコワン | Hongshenguang |  |  |  |
| バージオン | Bargion |  |  |  |
| バゾルド | Bazold |  |  |  |
| ブラックライブレード | Black Rayblade |  |  |  |
| ブランダイム | Brandeim |  |  |  |
| ガドラン（支援用） | Gadran (Support) |  |  |  |
| グリストル | Gristol |  |  |  |
| レンバードン | Renbardon |  |  |  |
| ダグエル | Daguel |  |  |  |
| デロウガ | Derouga |  |  |  |
| ザイクス | Zaiks |  |  |  |
| ブランドゥ | Brandu |  |  |  |
| プレシオン砲 | Presion Cannon |  |  |  |
| グランバイド | Granbide |  |  |  |
| デック・バスタイト | Deck Bustite |  |  |  |
| カイザール | Kaisar |  |  |  |
| ハウザー | Hauser |  |  |  |
| キンバイト | Kinbite |  |  |  |
| レイアル・クローゼ | Rayal Klose |  |  |  |
| バレイド | Baleid |  |  |  |
| ディレット | Dilet |  |  |  |
| セクティ | Secti |  |  |  |
| ドーマノン | Domanon |  |  |  |
| シードル | Seedle |  |  |  |
| プラズマバルカン砲 | Plasma Vulcan Cannon |  |  |  |
| バイン・ダーガ改 | Bine Daga Custom |  |  |  |
| ベルーラ | Berula |  |  |  |
| バルアミーエッグ | Baluamy Egg |  |  |  |
| オズワルド | Oswald |  |  |  |
| ゴーデリウス影 | Goderius Shadow |  |  |  |
| パルテノス影 | Parthenos Shadow |  |  |  |
| エレアナ影 | Eleana Shadow |  |  |  |
| ガイオゾン影 | Gaiozon Shadow |  |  |  |
| レイオード影 | Rayode Shadow |  |  |  |
| ホンシェンコワン影 | Hongshenguang Shadow |  |  |  |
| アハティ影 | Ahti Shadow |  |  |  |
| ゼイフォン影 | Zeifon Shadow |  |  |  |
| デュッセルドフ影 | Dusseldorf Shadow |  |  |  |
| パリカール影 | Parikar Shadow |  |  |  |
| バルドッグ影 | Baldock Shadow |  |  |  |
| フォルスティン影 | Forstin Shadow |  |  |  |
| ビシャール影 | Vishal Shadow |  |  |  |
| ドライデス影 | Drydes Shadow |  |  |  |
| オルベスト影 | Orbest Shadow |  |  |  |
| セルフィン影 | Selphin Shadow |  |  |  |
| エイディオン影 | Aidion Shadow |  |  |  |
| クールマリシン影 | Coolmarishin Shadow |  |  |  |
| シーヴァリアス影 | Sivarius Shadow |  |  |  |
| コア4 | Core 4 |  |  |  |
| コア5 | Core 5 |  |  |  |
| ブラオ・アーベント | Blau Abend |  |  |  |
| 紅閃光 | Hongshenguang |  |  |  |
| 聖霊機 | Spirit Mech |  |  |  |
| 装兵機 | Armored Mech |  |  |  |
| 守護装兵機 | Guardian Armored Mech |  |  |  |
| スタンドアローンタイプ | standalone type |  |  |  |
| 大陸四大装兵機 | Four Great Armored Mechs of the Continent |  |  |  |
| アート・ウェスペル | Art Wesper |  |  |  |
| 複製 | replica |  |  |  |

## Weapons
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 戒めの聖域 | Sanctuary of Restraint |  |  |  |
| 二の太刀・屠龍 | Second Blade: Dragon Slayer |  |  |  |
| プラズマソード | Plasma Sword |  |  |  |
| ゼイフォニック・ブラドラー | Zeifonic Bradler |  |  |  |
| 神剣ダイフォゾン | Divine Sword Daifozon |  |  |  |
| レーザーソード | Laser Sword |  |  |  |
| プラズマガトリング | Plasma Gatling |  |  |  |
| リムラッドミサイル | Rimrad Missile |  |  |  |
| カーネスの翼 | Wings of Carnes |  |  |  |
| ジグリム砲 | Zigrim Cannon |  |  |  |
| 七閃・龍操隙破 | Seven Flashes: Dragon Command Rift Breaker |  |  |  |
| 機銃 | Machine Gun |  |  |  |
| ダイオミサイル | Daio Missile |  |  |  |
| 剛剣ゼウレアー | Mighty Sword Zeulear |  |  |  |
| ラウクルス | Raucrus |  |  |  |
| ヴァイアル・ジェイド | Vial Jade |  |  |  |
| ゼイン・ライフル | Zein Rifle |  |  |  |
| プレシオンブラスト | Presion Blast |  |  |  |
| ブライファング・リメイション | Bryfang Rimation |  |  |  |
| ブラッシュ・ブラスト | Brush Blast |  |  |  |
| バイン・コレダー | Bine Collider |  |  |  |
| ブラン・ダイガード | Blanc Daigard |  |  |  |
| 白の贖罪 | White Atonement |  |  |  |
| スプレッドミサイル | Spread Missile |  |  |  |
| 双覇・疾風魔狼閃光斬 | Twin Supremacy: Gale Demon Wolf Flash Slash |  |  |  |
| 唸り斬り裂け大気 | Roar and Rend the Air |  |  |  |
| マイクロミサイル | Micro Missile |  |  |  |
| エムルレーザー | Emul Laser |  |  |  |
| ウェンディスの翼 | Wings of Wendis |  |  |  |
| ベルモスの轟雷 | Thunder of Belmos |  |  |  |
| バンゼクルス | Banzecrus |  |  |  |
| ヴォルティクランサー | Voltic Lancer |  |  |  |
| ギガント・ディスソリュージョン | Gigant Dissolution |  |  |  |
| 転移集中 | Focused Transfer |  |  |  |
| ノーグライズの風 | Winds of Norgrize |  |  |  |
| レス・リフラーム | Res Reflame |  |  |  |
| 天舞空裂 | Heavenly Dance, Sky Rend |  |  |  |
| ラルフィン・プライディール | Ralfin Prydeil |  |  |  |
| エスジオンミサイル | Esgion Missile |  |  |  |
| タワー・キャノン | Tower Cannon |  |  |  |
| ゼイン・ストリーム | Zein Stream |  |  |  |
| ブレイクアーム | Break Arm |  |  |  |
| ディグ・ブライザー | Dig Bryzer |  |  |  |
| プラズマアックス | Plasma Axe |  |  |  |
| かぎ爪 | Claw |  |  |  |
| 殴り | Punch |  |  |  |
| 真ゼイフォニック・ブラドラー | True Zeifonic Bradler |  |  |  |
| ノワール・エクレール | Noir Eclair |  |  |  |
| プラズマキャノン | Plasma Cannon |  |  |  |
| プラズマショット | Plasma Shot |  |  |  |
| プラズマランス | Plasma Lance |  |  |  |
| ゼイン・カノン | Zein Cannon |  |  |  |
| 烈・炎波昇天轟弾破 | Fury: Flame Wave, Heavenward Thunder Burst |  |  |  |
| 聖剣エンゲーザー | Holy Sword Engezer |  |  |  |
| 降雷刃 | Thunderfall Blade |  |  |  |
| スラッシュ・ブラスト | Slash Blast |  |  |  |
| ロングライフル | Long Rifle |  |  |  |
| 多連装プラズマガトリング | Multi-Barrel Plasma Gatling |  |  |  |
| プラズマファング | Plasma Fang |  |  |  |
| パワーストリング | Power String |  |  |  |
| 高周波クロー | High-Frequency Claw |  |  |  |
| 剛剣ゼウレアー（故障中） | Mighty Sword Zeulear (Malfunctioning) |  |  |  |
| 一の太刀・雷剛凱斬 | First Blade: Mighty Thunder Triumph Slash |  |  |  |
| レイ・ブランザード | Ray Blanzard |  |  |  |
| ノワール・ディファンス | Noir Defense |  |  |  |
| シルヴァリアの聖域 | Sanctuary of Silvaria |  |  |  |
| アミーナの洗礼 | Baptism of Amina |  |  |  |
| 仁王拳 | Nio Fist |  |  |  |
| ゼイン・ショット | Zein Shot |  |  |  |
| トライデント | Trident |  |  |  |
| ブラッディ・ローズ | Bloody Rose |  |  |  |
| 高周波ランサー | High-Frequency Lancer |  |  |  |
| 有線ブレイクアーム | Wired Break Arm |  |  |  |
| グラディオス | Gladios |  |  |  |
| ヴァルゴスの逆鱗 | Wrath of Vargos |  |  |  |
| プラズマウィップ | Plasma Whip |  |  |  |
| スタンロッド | Stun Rod |  |  |  |
| ファルジオカノン | Falgio Cannon |  |  |  |
| ゲウマミサイル | Geuma Missile |  |  |  |
| 大型ミサイル | Heavy Missile |  |  |  |
| デュバルナック・ライバー | Duvalnac Reiber |  |  |  |
| プラズマドライブ | Plasma Drive |  |  |  |
| プラズマナックル | Plasma Knuckle |  |  |  |
| オーガディスの斬撃 | Slash of Ogadis |  |  |  |
| プレシオンショット | Presion Shot |  |  |  |
| ギガプレシオンブラスト | Giga Presion Blast |  |  |  |
| プラズマバルカンファランクス | Plasma Vulcan Phalanx |  |  |  |
| 幻夜刀・天翔空裂 | Phantom Night Blade: Heaven Soar, Sky Rend |  |  |  |
| シュヴァハイムの咆哮 | Roar of Schwaheim |  |  |  |
| 天の太刀・紫焔凱絶斬 | Heavenly Blade: Violet Flame Supreme Victory Slash |  |  |  |
| 聖剣ランゼイダー | Holy Sword Lanzeider |  |  |  |
| オリジナル・シン | Original Sin |  |  |  |
| 凄然たる奈落 | Dreadful Abyss |  |  |  |
| ラルベール・ブラドラー | Ralber Bradler |  |  |  |
| セルバリオ・ゼオ | Selbario Zeo |  |  |  |
| 哀しみの風そよぐロンド | Rondo in a Breeze of Sorrow |  |  |  |
| 現し身の享楽 | Pleasures of the Mortal Form |  |  |  |
| ギガプラズマソード | Giga Plasma Sword |  |  |  |
| ティデール・ブラドラー | Tidear Bradler |  |  |  |
| 歓喜の御柱 | Divine Pillar of Rapture |  |  |  |
| 聖剣マーシュニクス | Holy Sword Marshnix |  |  |  |
| 憤怒の垂迹 | Manifestation of Wrath |  |  |  |
| 分身斬 | Clone Slash |  |  |  |
| プレシオンガン | Presion Gun |  |  |  |
| ガルムミサイル | Garm Missile |  |  |  |
| プラグマティックソーサー | Pragmatic Saucer |  |  |  |
| 真分身斬 | True Clone Slash |  |  |  |
| フォースビット | Force Bit |  |  |  |
| エンゼル・ハィロウ | Angel Halo |  |  |  |
| ストライク・アンカー | Strike Anchor |  |  |  |
| 赤き血の紋章 | Crest of Crimson Blood |  |  |  |
| 黒の裁き | Black Judgment |  |  |  |
| プラズマガン | Plasma Gun |  |  |  |
| 有線アーム | Wired Arm |  |  |  |
| ヒートブレード | Heat Blade |  |  |  |
| プレシオンカノン | Presion Cannon |  |  |  |
| プラズマサイズ | Plasma Scythe |  |  |  |
| ブランザイバー | Branzaiber |  |  |  |
| 多連装ロケットランチャー | Multi-Rocket Launcher |  |  |  |
| ドラグディスベイド | Dragdisbade |  |  |  |
| プラズマランサー | Plasma Lancer |  |  |  |
| スラッシュランス | Slash Lance |  |  |  |
| プラズマザンバー | Plasma Zamber |  |  |  |
| クラッシュザンバー | Crash Zamber |  |  |  |
| 皇剣デイズザイファー | Imperial Sword Deiz Zeipher |  |  |  |
| バリオン・ディスインテグレーター | Baryon Disintegrator |  |  |  |
| 皇剣リーブラ | Imperial Sword Libra |  |  |  |
| ライ・トレイアー | Rai Treiar |  |  |  |
| 皇剣ネブロイダー | Imperial Sword Nebroider |  |  |  |
| グラン・エクスプロジオン | Grand Explosion |  |  |  |
| 修理機能 | Repair Function |  |  |  |
| レイオン・ダイガード | Rayon Daigard |  |  |  |
| 紅き光 | Crimson Light |  |  |  |
| 蒼き光 | Azure Light |  |  |  |
| エプシオンカノン | Epsion Cannon |  |  |  |
| ライブレードキャノン | Rayblade Cannon |  |  |  |
| G型兵器 | Type-G weapons |  |  |  |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ローグワー賞 | Roguewar Prize |  |  |  |
| ピュリッツァー賞 | Pulitzer Prize |  |  |  |
| ガイス | Gais |  |  |  |
| ウルゥス | Uluus |  |  |  |
| ミル | mil |  |  |  |
| 銀の騎士 | Silver Knight |  |  |  |
| 銀狼 | Silver Wolf |  |  |  |
| 西の獅子 | Lion of the West |  |  |  |
| 紅蓮の騎士 | Crimson Knight |  |  |  |
| 西の蛮勇 | Wild Valor of the West |  |  |  |
| 鳳の騎士 | Phoenix Knight |  |  |  |
| 黒太子 | Black Prince |  |  |  |
| 紅蓮のガイウス | Crimson Gaius |  |  |  |
| 蒼き餓狼 | Azure Ravenous Wolf |  |  |  |
| 銀のレデュース | Reduce the Silver |  |  |  |
| テオラ | Theora |  |  |  |
| リーク | liek |  | Agarthian length unit (半径400リーク = a 400-liek radius) | leek |
| 本陣強襲部隊 | Headquarters Assault Unit |  |  |  |
| 輜重隊奇襲部隊 | Supply Train Ambush Unit |  |  |  |
| 錬金学士 | Alchemist |  |  |  |
| コード3 | Code 3 |  |  |  |
| 聖霊機開発計画 | Spirit Mech Development Project |  |  |  |
| ガゼット・プロジェクト | Gazette Project |  |  |  |
| 剣煌 | Sword Radiance |  |  |  |
| 教母 | Matriarch |  |  |  |
| 鳳 | Phoenix |  |  |  |
| 剣煌幻聖 | Sword Radiance, Phantom Saint |  |  |  |
| 第一王女 | First Princess |  |  |  |
| 筆頭錬金学士 | Chief Alchemical Scholar |  |  |  |
| 幻聖 | Phantom Saint |  |  |  |
| プラーナ | Prana |  |  |  |
| “陽”のプラーナ | yang Prana |  |  |  |
| “陰”のプラーナ | yin Prana |  |  |  |
| 操者 | Pilot |  |  |  |
| リスリーク | risleek |  |  |  |
| 好感度 | Affection |  |  |  |
| バースト・プラーナ | Burst Prana |  |  |  |
| 共鳴結晶 | Resonance Crystal |  |  |  |

## Speaker labels
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 声 | Voice |  | male narrator pronoun; nonhuman being; Estelian final antagonist in the library profile; source name-table la |  |
| 兵士 | Soldier |  | Agarthian Soldier label reporting capital rescue; unnamed individual. |  |
| ジグリム兵士 | Zigrim Soldier |  | Zigrim Soldier label; unnamed Armored Mech occupants in alternate rese |  |
| テロリスト | Terrorist |  |  |  |
| 隊長 | Commander |  | Zigrim commander speaker label in Hestia encounter; full identity and  |  |
| 謎の人物 | Mysterious Figure |  |  |  |
| 部下 | Subordinate |  | Unidentified subordinate in Fores/Reamond postassault exchange. |  |
| 整備士A | Mechanic A |  | male; York mechanic who gives day-to-day orders under Chief Celica in s_0df; |  |
| 副官 | Adjutant |  | male; Zigrim colonel; Growster's longtime comrade and adjutant; married with |  |
| 整備士F | Mechanic F |  | Mechanic at the Holy Land maintenance area; full identity unestablishe |  |
| 整備士C | Mechanic C |  | male; Mechanic C speaker label at Rayode recovery; full identity unestablish |  |
| 整備士B | Mechanic B |  | Mechanic B speaker label in Gen hangar encounter; full identity unesta |  |
| ヨーク兵士 | York Soldier |  |  |  |
| 村長 | Village Elder |  |  |  |
| 所員 | Staff Member |  | Unidentified laboratory Staff Member label in Murk security/outage sce |  |
| 整備士E | Mechanic E |  | Mechanic E speaker label in Gen aptitude conversation; full identity u |  |
| 整備士D | Mechanic D |  | Mechanic D speaker label in pre-sortie encouragement; full identity un |  |
| ジグリム兵士A | Zigrim Soldier A |  | Zigrim Soldier A label in Reduce/Steinies engagement; individual ident |  |
| アガルティア兵士 | Agarthian Soldier |  | Agarthian Soldier label reporting capital rescue; unnamed individual. |  |
| 侍女 | Lady-in-Waiting |  | Lady-in-Waiting speaker label in Tix departure scene; exact identity u |  |
| セル | Cell |  |  |  |
| ジグリム兵士E | Zigrim Soldier E |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ジグリム兵士F | Zigrim Soldier F |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| デカイ | Big Guy |  |  |  |
| ニヒル | Nihil |  |  |  |
| チビ | Shorty |  |  |  |
| ジグリム兵士B | Zigrim Soldier B |  | Zigrim Soldier B label in Reduce/Steinies engagement; individual ident |  |
| ジグリム兵士C | Zigrim Soldier C |  | Zigrim Soldier C label in Reduce/Steinies engagement; individual ident |  |
| 研究員 | Researcher |  |  |  |
| エリート兵士 | Elite Soldier |  |  |  |
| ヨーク兵士B | York Soldier B |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| 洗脳兵士 | Brainwashed Soldier |  |  |  |
| アガルティア兵士（エリート） | Agarthian Soldier (Elite) |  |  |  |
| アガルティア兵士（洗脳ver） | Agarthian Soldier (Brainwashed) |  |  |  |
| ジグリム兵士（エリート） | Zigrim Soldier (Elite) |  |  |  |
| ジグリム兵士（洗脳ver） | Zigrim Soldier (Brainwashed) |  |  |  |
| 隊長（ジグリム） | Commander (Zigrim) |  | Zigrim commander speaker label in Hestia encounter; full identity and  |  |
| テロリスト（エリート） | Terrorist (Elite) |  |  |  |
| 助手（マーシャ・モンシアン） | Assistant (Marsha Monsian) |  | female; Murk's personal assistant; later successor; self-taught alchemical kno |  |
| ヨーク兵士A | York Soldier A |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ヨーク兵士C | York Soldier C |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ヨーク兵士D | York Soldier D |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ヨーク兵士E | York Soldier E |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ヨーク兵士F | York Soldier F |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ヨーク兵士G | York Soldier G |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ヨーク兵士H | York Soldier H |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ジグリム兵士D | Zigrim Soldier D |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ジグリム兵士G | Zigrim Soldier G |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| ジグリム兵士H | Zigrim Soldier H |  | Lettered soldier role in York fortress scenes; individual identity and |  |
| 不適合者 | unfit individual |  |  |  |
| ？ | ? |  | unknown speaker (keep the count) |  |
| ？？ | ?? |  | unknown speaker (keep the count) |  |
| ？？？ | ??? |  | unknown speaker (keep the count) |  |
| ？？？？ | ???? |  | unknown speaker (keep the count) |  |
| ？？？？？ | ????? |  | unknown speaker (keep the count) |  |
| ？？？？？？ | ?????? |  | unknown speaker (keep the count) |  |
| ？？？？？？？ | ??????? |  | unknown speaker (keep the count) |  |
| 透夜 | Touya |  | 390 lines |  |
| 佳澄美 | Kasumi |  | 185 lines |  |
| ロア艦長 | Captain Roa |  | 138 lines |  |
| 助手 | Assistant |  | 111 lines |  |
| エリート兵 | Elite Soldier |  | 91 lines |  |
| クイーン | Queen |  | 51 lines |  |
| 教師 | Teacher |  | 30 lines |  |
| 女性 | Woman |  | 28 lines |  |
| 亜依 | Ai |  | 22 lines |  |
| レポーター | Reporter |  | 11 lines |  |
| クライム | Clime |  | 6 lines |  |
| アガルティア兵 | Agarthian Soldier |  | 6 lines |  |
| 巨漢 | Big Man |  | 4 lines |  |
| トウヤ＆クルル | Touya & Kururu |  | 4 lines |  |
| トウヤ＆ユミール | Touya & Ymir |  | 4 lines |  |
| 議員A | Councilor A |  | 3 lines |  |
| ノーブル | Noble |  | 3 lines |  |
| アイ＆トウヤ | Ai & Touya |  | 3 lines |  |
| トウヤ＆オーレリィ | Touya & Aurelie |  | 3 lines |  |
| トウヤ＆セリカ | Touya & Celica |  | 3 lines |  |
| トウヤ＆レオーネ | Touya & Leone |  | 3 lines |  |
| 議員B | Councilor B |  | 2 lines |  |
| ラジオの声 | Radio Voice |  | 2 lines |  |
| トウヤ＆カスミ | Touya & Kasumi |  | 2 lines |  |
| クラスメイト達 | Classmates |  | 1 lines |  |
| アイ＆フェイン | Ai & Fain |  | 1 lines |  |
| おじさん | Mister |  | 1 lines |  |
| 老人 | Old Man |  | 1 lines |  |
| シュテイニズ | Steinies |  | 1 lines |  |
| 男の子の声 | Boy's Voice |  | 1 lines |  |
| オーリレィ | Aurelie |  | 1 lines |  |
| 全員 | Everyone |  | 1 lines |  |
| 整備士達 | Mechanics |  | 1 lines |  |
| ロディス | Lodis |  | 1 lines |  |
| ジグリム兵F | Zigrim Soldier F |  | 1 lines |  |
| ベルント | Bernst |  | 1 lines |  |
| ベルスト | Bernst |  | 1 lines |  |
| トウヤ＆アイ | Touya & Ai |  | 1 lines |  |
| トウヤ＆メルヴィ | Touya & Melvi |  | 1 lines |  |

## Reference (not enforced; prefer these renderings)
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 調査機関 | research organization |  |  |  |
| 医務室 | infirmary |  |  |  |
| タワー | Tower |  |  |  |
| 展望室 | Observation Room |  |  |  |
| ドール | Doll |  |  |  |
| ミサイルランチャー | Missile Launcher |  |  |  |
| 輸送艇 | Transport Craft |  |  |  |
| クゥー | kuu |  |  |  |
| 昼行灯 | good-for-nothing / dimwit |  | idiom (a lamp lit in daylight = useless person); not "daytime lantern" |  |
| ヴォーリアを導く者 | one who guides Vorlia |  |  |  |
| 叡智の器 | vessel of wisdom |  |  |  |
| 鉄の女 | Iron Lady |  |  |  |
| 選定都市 | elector cities |  |  |  |
| 調印式 | signing ceremony |  |  |  |
| 継承権 | succession rights |  |  |  |
| 即位 | accession |  |  |  |
| 独立行動権 | independent operational authority |  |  |  |
| 立憲君主国 | constitutional monarchy |  |  |  |
| 共和制 | republic |  |  |  |
| 女系国家 | matrilineal state |  |  |  |
| 停戦 | ceasefire |  |  |  |
| 貴族院 | House of Peers |  |  |  |
| 和平条約 | peace treaty |  |  |  |
| 造られた人間 | manufactured human |  |  |  |
| 輜重隊 | supply train |  |  |  |
| 操者特性 | pilot aptitude |  |  |  |
| 適合者 | compatible candidate |  |  |  |
| パティシエ | patissier |  |  |  |
| アガルティア人類の浄化 | purification of Agarthian humanity |  |  |  |
| 人体強化計画 | human enhancement project |  |  |  |
| 一等学士主席 | Chief First-Class Scholar |  |  |  |
| 主席学士 | Chief Scholar |  |  |  |
| カルシウム | calcium |  |  |  |
| 感情エネルギー | emotional energy |  |  |  |
| プラーナ放射 | Prana radiation |  |  |  |
| 主計士 | purser |  |  |  |
| メイン操者 | main pilot |  |  |  |
| 通常警護任務 | regular guard duty |  |  |  |
| 同乗者 | Co-pilot |  |  |  |
| 装甲 | Armor |  |  |  |
| 闘志 | Fighting Spirit |  |  |  |
| 防御 | Defense |  |  |  |
| 回避 | Evasion |  |  |  |
| 命中 | Accuracy |  |  |  |
| 間接 | Ranged |  |  |  |
| 近接 | Melee |  |  |  |
| 信頼度 | Trust |  |  |  |
| 同調率 | synchronization rate |  |  |  |
| 係数誤差 | coefficient error |  |  |  |
| 期待出力 | expected output |  |  |  |
| 因果律 | Causality |  |  |  |
| 復讐リスト | revenge list |  |  |  |
| 記憶喪失 | amnesia |  |  |  |
| 国際連盟条約 | International League Treaty |  |  |  |
| デオ | deo |  |  |  |
| リス | ris |  |  |  |
| ジキ | jiki |  |  |  |
| ロット | lot |  |  |  |
| 魔眼 | Evil Eye |  | ability |  |
| テレパシー | telepathy |  | ability |  |
| プラズマバリア | Plasma Barrier |  | ability |  |
| 対実弾バリア | Ballistic Barrier |  | ability |  |
| プラズマコート | Plasma Coating |  | ability |  |
| 予知夢 | precognitive dreams |  | ability |  |
| 飛天八艘跳び | Flying Heavens: Eight-Boat Leap |  | ability |  |
| 超無双斬り | Super Peerless Slash |  | ability |  |
| 霞突 | Mist Thrust |  | ability |  |
| 先見 | foresight |  | ability |  |
| キス | kiss |  | action |  |
| 刺繍 | embroidery |  | action |  |
| クライム・ストラース | Clime Strass |  | alias |  |
| 攪乱粒子 | jamming particles |  | battle_phenomenon |  |
| 必殺技 | Special Move |  | battle_term |  |
| 誘導レーザー | guided laser |  | battle_term |  |
| 正式な一騎討ち | formal duel |  | battle_term |  |
| レイドル | Raidol |  | beverage |  |
| カラム水 | Karam water |  | beverage |  |
| 遺伝子操作 | genetic engineering |  | biology |  |
| クローン | clone |  | biology |  |
| 七つの棺 | The Seven Coffins |  | book_title |  |
| ハッキング | hacking |  | computing |  |
| セキュリティシステム | security system |  | computing |  |
| サポートプログラム | support program |  | computing |  |
| 暗証番号 | passcode |  | computing |  |
| 意識体 | disembodied consciousness |  | concept |  |
| 個 | individuality |  | concept |  |
| 平行宇宙 | parallel universe |  | concept |  |
| ゾルゲの場 | Sorge Field |  | concept |  |
| 他者 | other |  | concept |  |
| 愛の力 | power of love |  | concept |  |
| 宇宙の意志 | will of the universe |  | concept |  |
| 多次元宇宙 | multidimensional universe |  | concept |  |
| 状態ベクトル | state vector |  | concept |  |
| 自己 | self |  | concept |  |
| 光球 | Orb of Light |  | concept |  |
| 客観性 | objectivity |  | concept |  |
| 五行二天 | Five Elements and Two Heavens |  | concept |  |
| タイムスリップ | time slip |  | concept |  |
| 遺伝情報 | genetic information |  | concept |  |
| 運命の赤い糸 | red thread of fate |  | concept |  |
| 空間跳躍 | spatial jump |  | concept |  |
| 守護者 | Guardian |  | concept |  |
| 主観性 | subjectivity |  | concept |  |
| 命の尊厳 | dignity of life |  | concept |  |
| 電子共振 | electronic resonance |  | concept |  |
| 依代 | vessel |  | concept |  |
| 精神制御 | mental control |  | concept |  |
| 強化人間 | enhanced human |  | concept |  |
| 多面波長形式 | multi-aspect wavelength format |  | concept |  |
| 精神呪縛 | mental binding |  | concept |  |
| エゴの投影 | projection of the ego |  | concept |  |
| 二人乗り | two-seater |  | configuration |  |
| 対フィールドユニット | anti-field unit |  | device |  |
| アジャスター | Adjuster |  | device |  |
| 発信器 | transmitter |  | device |  |
| ゼルバリオ | Zelbario |  | device |  |
| 特攻君3号 | Charge Buddy No. 3 |  | device |  |
| 脱出装置 | escape system |  | device |  |
| 電磁ロック | electromagnetic lock |  | device |  |
| 補助出力装置 | auxiliary output device |  | device |  |
| メッセージボックス | message box |  | device |  |
| バイン・ダーガ整備キット | Bine Daga maintenance kit |  | device |  |
| 時限装置 | timed device |  | device |  |
| フレイル結界 | Frail Barrier |  | device |  |
| ナノコン | nanocom |  | device |  |
| 万能複合通信観測装置 | Universal Integrated Communications and Observation Device |  | device |  |
| フレイルの結晶 | Frail Crystal |  | device |  |
| ピッチ | PHS phone |  | device |  |
| 記録結晶 | recording crystal |  | device |  |
| 仮想戦闘訓練機 | virtual combat trainer |  | device |  |
| 受信機 | receiver |  | device |  |
| 対障壁突破装置 | barrier-breaching device |  | device |  |
| 鳴石 | chime stone |  | device |  |
| パーソナルセンサー | personal sensor |  | device |  |
| 反省君1号 | Repentance Buddy No. 1 |  | device |  |
| 操者保護システム | pilot protection system |  | device |  |
| インスタントカメラ | instant camera |  | device |  |
| 起動キー | activation key |  | device |  |
| シーカー | Seeker |  | device |  |
| 制御結晶 | control crystal |  | device |  |
| 反応君13号 | Reaction Buddy No. 13 |  | device |  |
| 生命工学 | bioengineering |  | discipline |  |
| 錬金学 | Alchemy |  | discipline |  |
| グラタン | gratin |  | dish |  |
| プチマルミット | petite marmite |  | dish |  |
| トルティ | torti |  | dish |  |
| ポヌ・ファム | bonne femme |  | dish |  |
| ポトフ | pot-au-feu |  | dish |  |
| 入団試験 | entrance exam |  | education |  |
| 超精神体 | transcendent consciousness |  | entity_state |  |
| 人造人間 | artificial human |  | entity_state |  |
| 光柱 | pillars of light |  | event |  |
| 文化祭 | school festival |  | event |  |
| 大戦 | Great War |  | event |  |
| 暗黒時代 | Dark Ages |  | event |  |
| 召喚 | summoning |  | fictional_process |  |
| 自己増殖機能 | self-replication function |  | fictional_process |  |
| 調和作用 | harmonizing effect |  | fictional_process |  |
| ラクリマ | Lacrima |  | flower |  |
| アゼラの花 | Azera flower |  | flower |  |
| メザシ | skewered dried fish |  | food |  |
| 味噌汁 | miso soup |  | food |  |
| チョコバー | chocolate bar |  | food |  |
| 弁当 | packed lunch |  | food |  |
| パム | Pam |  | food |  |
| クラウ | klau |  | food |  |
| 賞味期限 | best-before date |  | food_label |  |
| 桶狭間 | Okehazama |  | historical_reference |  |
| 烙印 | brand |  | identification |  |
| 門 | Gate |  | interworld_link |  |
| 特ダネ映像 | exclusive footage |  | journalism |  |
| シルク | silk |  | material |  |
| 結晶金属装甲 | crystalline-metal armor |  | material |  |
| 剛石 | Hardstone |  | material |  |
| 応急処置 | first aid |  | medical_term |  |
| 栄養剤 | nutrient supplement |  | medical_term |  |
| 睡眠薬 | sleep medication |  | medical_term |  |
| 組織崩壊 | tissue breakdown |  | medical_term |  |
| 視力 | visual acuity |  | medical_term |  |
| 催眠術 | hypnosis |  | mental_technique |  |
| 撤退 | Retreat |  | menu |  |
| 改造 | Upgrade |  | menu |  |
| 反撃命令 | Counterattack Orders |  | menu |  |
| 作戦目的 | Mission Objectives |  | menu |  |
| キャラクター設定 | Character Profiles |  | menu |  |
| ユニット設定 | Unit Profiles |  | menu |  |
| 思い出アルバム | Memory Album |  | menu |  |
| デバッグメニュー | Debug Menu |  | menu |  |
| 部隊表 | Unit List |  | menu |  |
| 画面効果テスト | Screen Effects Test |  | menu |  |
| バストアップギャラリィー | Bust Portrait Gallery |  | menu |  |
| 第一種警戒態勢 | Type One alert |  | military_designation |  |
| 聖戦 | Holy War |  | mobilization |  |
| 飛行形態 | flight mode |  | mode |  |
| 演歌 | enka |  | music_genre |  |
| トップ屋 | scoop hunter |  | occupation |  |
| 時間跳躍 | time leap |  | phenomenon |  |
| 磁場 | magnetic field |  | physics |  |
| クラージ | Kuraji |  | plant |  |
| 主席補佐官 | chief aide |  | position |  |
| 共鳴君1号 | Resonance Buddy No. 1 |  | project_label |  |
| 分析君 | Analysis Buddy |  | project_label |  |
| アイちゃんメモリアルアルバム | Ai-chan Memory Album |  | project_label |  |
| ヤマトちゃん強化計画 | Yamato Enhancement Project |  | project_label |  |
| 因果律の変化 | Changes in Causality |  | recall_topic |  |
| 騎士教本 | knight's handbook |  | reference |  |
| 感情構築実験 | emotion-construction experiment |  | research |  |
| コギャル語 | kogyaru slang |  | slang |  |
| マゴギャル | magogyaru |  | slang |  |
| 通風孔 | air vent |  | structure |  |
| プライベート | Private Phase |  | system |  |
| 話題 | Topic |  | system |  |
| ゆらぎ | fluctuation |  | system |  |
| 光学遮蔽 | optical cloaking |  | system |  |
| 特殊フィールド | special field |  | system |  |
| 防御フィールド | defensive field |  | system |  |
| 信頼コマンド | Trust Commands |  | system |  |
| 操者登録 | Pilot registration |  | system |  |
| 補完的修復システム | complementary repair system |  | system |  |
| 管制システム | control system |  | system |  |
| 生体スキャン | life-form scan |  | system |  |
| 光学遮蔽システム | optical cloaking system |  | system |  |
| 共時性 | synchronicity |  | system |  |
| 出力制限 | output limit |  | system |  |
| 制御ユニット | control unit |  | system |  |
| 着陸許可 | landing clearance |  | system |  |
| 物理障壁 | physical barrier |  | system |  |
| 一方通行のフィールド | one-way field |  | system |  |
| 操者防御システム | pilot defense system |  | system |  |
| 浮遊ブロックシステム | Floating Block System |  | system |  |
| 分担操縦 | shared piloting |  | system |  |
| 操者の反応係数 | pilot response coefficient |  | system |  |
| マインドコントロール | mind control |  | system |  |
| 保護フィールド | protective field |  | system |  |
| 自動操縦 | autopilot |  | system |  |
| 領域遮断 | area isolation |  | system |  |
| エーテルエンジン | Ether Engine |  | system |  |
| プラズマフィールド | Plasma Field |  | system |  |
| プラーナの伝達回路 | Prana transmission circuits |  | system |  |
| 発進許可 | departure clearance |  | system |  |
| 対フィールドシステム | anti-field system |  | system |  |
| ゼルバリオシステム | Zelbario system |  | system |  |
| 機動防御補助制御機構 | Mobile Defense Auxiliary Control Mechanism |  | system |  |
| 擬似訓練モード | simulated training mode |  | system |  |
| 目測 | measuring by eye |  | trait |  |
| 力ある子 | child of power |  | trait |  |
| 絆 | Bond |  | trust_command |  |
| 集中 | Focus |  | trust_command |  |
| 友情 | Friendship |  | trust_command |  |
| 察知 | Awareness |  | trust_command |  |
| 加速 | Accelerate |  | trust_command |  |
| 直感 | Intuition |  | trust_command |  |
| 激励 | Encourage |  | trust_command |  |
| 鉄腕 | Iron Arms |  | trust_command |  |
| 鉄壁 | Iron Wall |  | trust_command |  |
| 再動 | Act Again |  | trust_command |  |
| みがわり | Cover |  | trust_command |  |
| 表情 | Expression |  | ui |  |
| 話題ポイント | Topic Points |  | ui |  |
| ヤマトチェック | Yamato's Check |  | ui |  |
| 包丁 | kitchen knife |  | utensil |  |
| 白雪姫 | Snow White |  | work_title |  |
| ヨーク独立戦争の記録 | Record of the York War of Independence |  | work_title |  |
| 眠れる森の美女 | Sleeping Beauty |  | work_title |  |
## Decisions from earlier batches
