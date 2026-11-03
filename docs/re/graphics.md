# Graphics-text survey

Static sweep (phase 1): `python -X utf8 tools/qx.py sweep <ARC>` renders every LZ/QX record to `work/gfx/<ARC>/`
(+ contact sheets, `skipped.txt`). Sheets were read by visual-qa subagents (`work/gfx/survey_*.md`) and by hand
(D_CUTIN, D_FACE2). Labels are `<slot>.<image>`. A tour of live screens (marker build, phase 5/8) and the debug tool
(phase 2) still have to add runtime-only elements. Source column: archive slot; all are LZ records holding QX images
(re-pack with `lz.pack_record` + `arc.pack`).

| # | Element | Source | Japanese | State |
|---|---|---|---|---|
| G1 | Title logo 聖霊機 + ライブレード (+ letter pieces) | D_SYSTEM 3.0-3.5, 4.0-4.2 | logo | keep Japanese (D5: no official English logo); "New Game/Continue/PRESS START BUTTON" already English |
| G2 | Battle status icons プラーナ マ 反 積 無 防 | D_SYSTEM 0.57-0.62, 1.57-1.62 | 6 x2 | done (gfx_en: "Prana", order icons M C A S D = bank00:0AE Manual/Counter/Aggressive/Safe/Defend; seen in battle > Orders, work/qa/p8g2/ord) |
| G3 | Battle ability labels クリティカル 回避 防御 プラズマコート プラズマバリア 対実弾バリア 特殊フィールド バリア | D_SYSTEM 1.89-1.95, 1.107 | 8 | done (gfx_en BATTLE, metal rows; "Defend" seen in an enemy-phase attack, work/qa/p8g2/def) |
| G4 | Character name plates (small) | D_SYSTEM 2.35-2.68 | 34 | done (gfx_en PLATES) |
| G5 | World-map place names | D_SYSTEM 8.17-8.26 | 10 | done (gfx_en MAP_LABELS) |
| G6 | Demo-disc screens (warning, release date, thank-you) | D_SYSTEM 9.0, 11.0, 12.0 | 3 | probably unused in retail; check reachability before redrawing |
| G7 | Trust gauge header 信頼度ゲージ + name plates | D_SYSTEM 13.0, 13.2-13.16 | 16 | done (gfx_en GAUGE) |
| G8 | Episode number 第 N 話 pieces | D_SYSTEM 16.6-16.17 | 12 | done ("Ep." + Arabic digits; 話 blank) |
| G9 | Episode title banners 『…』 + furigana strips | D_SYSTEM 17.0-20.15 | 136 | done (bank10 titles; unused 17, 47, 61-67 left) |
| G10 | Memory album screen 思い出アルバム | D_SYSTEM 33.0 | 1 | done: tag "Memory Album" (gfx_en ALBUM_TAG; this 320-wide image is linear rows, not strips); the book cover's lettering is decorative script, kept |
| G11 | Party cards / album thumbnails with captions | D_SYSTEM 36, 49-51, 56-58, 64-78 | 165 | done: captions in docs/album-captions.tsv (read off the images; palette = entry flags & 0xF, 71.x decode fine with it) |
| G12 | New Year card, handwritten letter CGs | D_SYSTEM 110.0, 246.0; D_SCREEN 189.0 | 3 | New Year card redrawn "Happy New Year!" (gfx_en NEW_YEAR); letter 246.0 is read out in the dialogue (sce 129, translated), kept; D_SCREEN 189.0: check |
| G13 | Staff credits (roles + names) | D_SYSTEM 472.21-472.83 | 63 | done but 7 names with no sourced reading stay Japanese (owner question) |
| G14 | Gallery heading カット/イベント集 (vertical) | D_SCREEN 151-168, 298, 333-334 (same image x12) | 1 unique | todo; strip layout still scrambled (qx.py w>128 guess) |
| G15 | Brush-lettered title card(s) | D_SCREEN 240, 241, 248 | 3 | todo; layout scrambled, unreadable |
| G16 | Pre-rendered dialogue text sheets (white on blue) | D_SCREEN 323, 324 | 2 | todo: find where shown (scroll text?) |
| G17 | Lore text sheets (silk) | D_SCREEN 325-329 | 5 | todo: find where shown |
| G18 | Attack brush-kanji cut-ins 破, 斬(?) | D_EFFECT 142.8, 143.8, 455.8, 456.8 | 2 unique | todo (DC patch: attack-lettering.json) |
| G19 | Battle HUD copies of G2/G3 (icons, popup labels) | D_EFFECT 250.57-62, 250.89-95, 250.107 | 14 | done: D_EFFECT 250 is a byte copy of D_SYSTEM 1; insert.py writes gfx_en's record there too |
| G20 | Tiny label beside SUPPORTOR/NPC; small green HUD panels | D_EFFECT 250.116, 312.0-312.9 | 11 | unconfirmed: check in a live battle (debug tool) |

Clean: D_UNIT (unit sprites), D_SCREEN 346-638 (backgrounds/portrait atlases), D_CUTIN (mecha cut-ins), D_FACE (portraits), D_FACE2
(83 decodable portraits; 84 records with header 0x183A0000 are not LZ: TODO).

Not yet swept: D_FIELD (maps; signs?), D_ANIME, MOVIE.BIN (STR FMV: opening has no on-screen Japanese seen so far).
