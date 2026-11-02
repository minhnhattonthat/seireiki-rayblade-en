# Text: font, encoding, script VM, text locations

## Font — verified
- 1 bpp font in the EXE at RAM 0x800AFBCC (file 0xA03CC). Glyph code c < 0x200: 16 bytes (8x16, 1 byte/row);
  c >= 0x200: 32 bytes at base + c*32 - 0x2000 (16x16, 2 bytes/row). Within each byte the pixel order is
  bits 6,7,4,5,2,3,0,1 (the draw routine's nibble tables at 0x800C7CB0.. put bit 2k left of 2k+1).
  Verified: `tools/fontsheet.py` renders し/教/師 exactly as drawn in the VRAM text strip (work/qa/dlg1).
- Draw routine 0x80034680.. (glyph blit into a 4bpp RAM buffer at 0x800F81B4, row stride 0x20, then LoadImage to
  VRAM x=320 y=256..): adds a 1-px shadow (value 2) from the previous row. ASCII mode (flag 0x40) uses 8x8 glyphs
  `(c - 0x20) & 0x7F` * 8 from another base (TODO find base).
- Last non-empty glyph: 0xA4C. Kanji: a game subset stored in runs of rising JIS X 0208 order (0x210 亜 哀 綾 依 囲..).

## Encoding (`tbl/jp.tbl`, built by `tools/build_tbl.py`) — verified on the first scene
| bytes | meaning |
|---|---|
| 00 | full-width space (indent after a line break) |
| 01-1A, 1B-34, 36-3F | A-Z, a-z, 0-9 (8-px glyphs) |
| 40-8F | hiragana ぁ..ん (Shift-JIS order without ゎゐゑ) |
| 90-DF | katakana ァ..ン (without ヮヰヱ); E0 ヴ, E1 ?, E2 ヵ, E3 ヱ?, E4 々 |
| E5-EE | 、 。 ． （ ） 「 」 『 』 ・ |
| F0-FA xx | glyph code (b - 0xEF) * 0x100 + xx: F0 xx = punctuation 0x100.. (F0 06 ー, F0 08 ？, F0 09 ！, F0 0B ‥ (two of them = ……)); F1 10.. = kanji |
| FB | mode toggle (DC version: ASCII on/off) — guess |
| FC p1 p2 | control. In D_SCE text: `FC xx 3E` x6260 (likely a wait of xx frames: 02, 5A, 3C, B4 = 2/90/60/180), `FC 04 3C` / `FC 84 3C` x300 (DC: p2 3C has 2 more bytes — check). EXE menus: FC 80 xx, FC FF FF (position/colour?). TODO verify argument counts in the 78 handler before extraction |
| FD | line break |
| FE | page break (guess, from DC) |
| FF | end of string |

Kanji readings in `tbl/jp.tbl` are template-match first guesses (`tools/match_font.py`, MS Gothic 12 px, chamfer
distance, JIS-run window): ~1210 confident anchors, ~800 window guesses, ~115 free guesses (`work/font/match.tsv`).
Known misreads: 0x210 亜 (read 唐), 目 read as 貰, 日 read as 廿. Review before extraction (phase 4): fix in
`tbl/glyph_overrides.tsv` and re-run build_tbl.py; 51 duplicate readings carry `#<code>` suffixes until fixed.

## Scenario VM (D_SCE records) — partly verified
- Interpreter loop 0x800581A0. State struct 0x800CD570: +0x40 script base pointer, +0x48 pc (offset into the
  record), +0x54 copy of the current instruction bytes. Script record loaded at 0x800DCE00 (scene 1).
- Opcode length table 0x800C8480 (file 0xB8C80), handler table 0x800C8080 (`python -X utf8 tools/re.py ops`).
  Length 0 = variable-length op (00 1A 27 3E 3F 4D 4E 73 77 7C 7D 8B 8F 9A B1-B3 BC BD C1 C2 D9 DE DF EC-EF FA-FF).
- **Jumps:** op 01 `01 lo hi` -> pc = int16 + 1; op 02 `02 b0 b1 b2 b3` -> pc = u32 + 1 (absolute offsets inside the
  record). Other ops that write pc (03 04 06 07 0B-0E 14 15 17-19 33 3A 43 55 56 59-5B 5D 6B 6C 74 76 78 7E 7F 80 82
  86 88 8A 8E 93 9C-9F B4 BF C3 C5 CC D1-D3 D5 D6 D8 DB DD EA F9) still need classifying: plain advance vs branch.
  Choice op `7A nn ..` carries per-item u16 offsets (seen `7A 03 06 00 f6 00 fa 00 78 c0 ..`). Inserting longer
  text shifts offsets: every branch operand must be rewritten — needs a full disassembler with roundtrip (phase 4).
- **Text op 0x78** (`78 style`, then text to FF; length table says 2, the handler consumes the text). Style byte low
  nibble = mode (0..12, jump table at 0x80020000-0x15F4). Seen: `78 00` dialogue, `78 01 xx yy` (with 2 more bytes:
  portrait/speaker?), `78 C0` choice items, `78 A0`. Usually preceded by `7B xx yy` (3-byte op; speaker portrait?).
  Dialogue = `「name」` form: speaker name, EA 「, text, EB 」, FF. Formatter buffer 0x400 bytes, limit 0x3FF.
- ~46,500 `EB FF` dialogue ends across D_SCE; 34,800 preceded by `7B xx yy 78 00`.

## Other text locations
- **EXE** data section, file 0x2D00-0x7600 (RAM 0x80012500..): system/battle menu strings in the same encoding
  (フェイズ終了, 部隊表, システム, セーブ, 攻撃, 信頼コマンド, ユニット特殊能力 ..), Yamato's affection hints, and a
  leftover **debug menu** (ロード / セーブ / Mロード / Mセーブ / 全体PUT / 全体更新, P: R: W: A:) at 0x6418.
  Strings end FF; many are pointed to from code (lui/addiu pairs) — pointer survey TODO (phase 4).
- **D_BMESS** battle messages: per record 12 self-relative u16 category pointers + weapon override lists; FC 30..37
  conditional jumps with u16 self-relative targets (same as DC docs/battle-text-format.json; verified the root
  table aliasing on PS1, rest guess).
- **D_SYSTEM** some records hold names (トウヤ x41, 攻撃 x13 hits) — character/unit/weapon name tables (TODO).
- D_SCE slot 447: text list (names/terms?).
- Graphics text: see graphics.md.
