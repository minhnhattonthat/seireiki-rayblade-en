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
`build_tbl.py` now emits every glyph cell 0x00-0xA4C: unread cells get a `<XXX>` placeholder so the byte stream never
misaligns (before that, a missing code decoded as `[XX]` and shifted the rest of the line). 464 cells are still
placeholders. Known misreads seen in extracted text: 0x210 亜 read as 唐, 目 read as 貰, 日 read as 廿, 回 as 廻,
同 as 伺, 向 as 徇, 真 as 審, 膨 as 脹, 今 as ?; fix them in `tbl/glyph_overrides.tsv` (code<TAB>reading) and re-run
build_tbl.py, then re-run `tools/extract.py dump --force` so `jp` fields regenerate.

## Scenario VM (D_SCE records) — verified (tools/vm.py; emulator trace work/scratch/tr1)
- Interpreter loop 0x800581A0. State struct 0x800CD570: +0x40 script base pointer, +0x48 advance/displacement,
  +0x4C multi-frame sub-state counter, +0x54 copy of the current instruction bytes. Scene 1 is loaded at
  0x800DCE00; the record bytes in RAM are byte-identical to D_SCE slot 1 (checked against a RAM dump).
- Opcode length table 0x800C8480 (file 0xB8C80), handler table 0x800C8080 (`python -X utf8 tools/re.py ops`).
  **A length of 0 means the op is not implemented** (the handler is a bare `ret 0x80`, so the interpreter spins on
  the same byte forever) — a 0 at an instruction boundary is a decode error, not a variable-length op.
- The loop copies `length` bytes to state+0x54, calls handler[op] and advances `base += state+0x48` when the
  handler returns an odd value. **A handler may add to state+0x48**, which is how an op consumes argument bytes
  beyond its table length (e.g. `1E 00 <4 args>` inserts two runtime values into the text). `vm.SUBK` holds the
  per-sub-op extra counts, derived from the handlers (`addiu $x,$x,K` before `sw $x, 0x48`); 11 sub-op dispatcher
  opcodes exist: 16 1B 1E 1F 5C AD AE B0 C0 C8 DC.
- **Branches** (target = op offset + displacement): 01 rel (+1), 07 rel (+2), 14 conditional rel (+1, flag in the
  u16: bit 15 set = jump if the flag is set), 02 abs u32 (+1), 03 call rel (+1, pushes the return address on a
  16-deep stack at state+0x64), 04 call abs u32, 06 return, 0B goto scene, B4 table goto (27 flag/scene pairs).
  7A = choice: `7A count` then `count` u16 self-relative offsets (one per item) — total length 2+2*count.
  08 = wait: `08 <u16 frames>` (countdown in state+0x4E).
- **Text op 0x78**: `78 style [args]` then the text. Styles 1 and 2 carry two argument bytes before the text
  (portrait/speaker id); styles 0, 8..12 carry none; styles 3..7 return without advancing (unused).
  78 C0 = choice items, 78 A0, 78 80 = other boxes. Usually preceded by `7B xx yy` (speaker). The handler formats
  into a 0x400-byte buffer (limit 0x3FF) and leaves state+0x48 = the whole `78 style args text FF` length.
- **Text ends at an FF that is not a glyph low byte**: F0..FA are two-byte glyph codes (so `F3 FF` = 私), FC
  carries two argument bytes, FB/FD/FE one. `vm.text_end` walks glyph-wise for this reason; a raw `find(b"\xff")`
  cut 2052 strings short in the first pass.
- 49,363 text blocks in D_SCE (styles: 00 dialogue 38.6k, 01 7.7k, 02 1.7k, 80/81 0.8k, A0 407, C0 128 choices).
  A linear sweep with skip-on-undecodable-byte leaves 0.24% of the file undecoded in runs shorter than 32 bytes;
  every trace boundary of scene 1 lands on a sweep instruction start.

## Other text locations
- **EXE message bank** (22 groups) — verified, extracted: root table at RAM 0x8001534C, 22 self-relative u32
  entries, each pointing at a group table. A group table is an array of self-relative u32 pointers to strings;
  entry 0 points just past the table (its value / 4 = the table's entry count) and is an empty string. The reader
  takes `(group << 8) | index`. Group 0 = system menu (フェイズ終了, 部隊表, システム, セーブ), group 1 = battle
  abilities, 2/3/4 = character/weapon/item names, 6/7 = place names, 8 = private events, 9-13 = more names.
  Groups 14-21 resolve to tables of mixed kinds (struct tables, kana/font order tables); only entries whose target
  decodes to text are taken (1990 strings).
- **Resident system script** in the EXE at RAM 0x80010374: 70 self-relative sub-scripts (archive layout). Only
  sub-script 58 (0x80015270 = Yamato's affection hints) and sub 7 hold 78-text blocks; the menus are drawn from
  the message bank via op A3.
- **EXE VM region** 0x800124E0-0x800126E0: the same VM bytecode inline in the data section — the six Yamato
  affection-hint lines (`01 <off> 7B 12 00 78 00 text FF` records).
- **EXE inline strings** (debug menu ロード/セーブ/Mロード/Mセーブ/全体PUT/全体更新, P: R: W: A:, Yamato hints):
  FF-terminated runs with no pointer table. Only quote-delimited ones are extracted (status `candidate`); the rest
  are left for the marker build, because runs of the EXE's kana/font order tables also decode as text.
- **D_BMESS** battle messages: 128 records, each starting with `28 00`-style header + 12 self-relative u16
  category pointers, then a bytecode with `FC 30..37` conditional jumps. The strings are *not* plain text at the
  pointer targets (the bytes decode as control codes + u16 ids), so this needs its own decoder — not extracted yet;
  battle text is out of scope for the first pass (marker build will show what is missing).
- **D_SYSTEM** holds character/unit/weapon name tables (トウヤ x41) — not extracted yet.
- D_SCE slot 447: 63 text blocks (names/terms list); slot 2 is the chapter dispatcher + dev chapter-select menu.
- Graphics text: see graphics.md.

