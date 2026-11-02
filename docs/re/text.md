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
| FC p1 p2 | control. In D_SCE text: `FC xx 3E` x6260 (likely a wait of xx frames: 02, 5A, 3C, B4 = 2/90/60/180). **`FC xx 3C a b` carries two more bytes** (372 in D_SCE; `a b` mirror op `87 xx a b`, an inline portrait/face change, e.g. `FC 04 3C 1C 05`); `a` is often FF, which the first extraction read as the end of the line (cut ~300 lines short, the rest left Japanese in the marker build). Table entry `FC??3C={face:2}` (tbl.py `??` wildcard key) prints it as `{face:043CFF10}`-style `{face:xxab}`. EXE menus: FC 80 xx, FC FF FF (position/colour?) |
| FD | line break |
| FE | page break (guess, from DC) |
| FF | end of string |

Kanji readings in `tbl/jp.tbl` are template-match first guesses (`tools/match_font.py`, MS Gothic 12 px, chamfer
distance, JIS-run window): ~1210 confident anchors, ~800 window guesses, ~115 free guesses (`work/font/match.tsv`).
`build_tbl.py` now emits every glyph cell 0x00-0xA4C: unread cells get a `<XXX>` placeholder so the byte stream never
misaligns (before that, a missing code decoded as `[XX]` and shifted the rest of the line). 17 readings were corrected
by hand into `tbl/glyph_overrides.tsv` (rendered each cell and checked the surrounding line): 目/日/回/同/向/真/貫/服/
直/口/正/問/活/互/煌/泊/妄/田 had all been read as a look-alike (貰/廿/廻/伺/徇/審/…). 50 glyph cells are **aliases**
— the font holds the same character twice — so their table entries carry a `#<code>` suffix (e.g. `止#4FD`) to keep
decode→encode byte-exact; read such a suffix as the character itself. The rest of the readings are still the
template matcher's guesses: review them before phase 6 by rendering cells (`tools/fontsheet.py`, or
`work/scratch/glyphreview.py` which labels each cell with its reading), fix in `tbl/glyph_overrides.tsv`, re-run
build_tbl.py and then `tools/extract.py dump --force` so the `jp` fields pick the fixes up.

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
- **Text op 0x78**: `78 style [args]` then the text. Style 1 carries two argument bytes before the text,
  style 2 carries three (`78 02 <u16> <u8>`; reading it as two left an 'A'/'B' glyph in front of 1699 lines),
  styles 0, 8..12 carry none, and `78 78 <style> <args>` is a wrapper whose inner 78 at the second byte owns the
  text (3 lines, battle-style windows). Styles 3..7 return without advancing (unused). 78 C0 = choice items,
  78 A0, 78 80 = other boxes. Usually preceded by `7B xx yy` (speaker). The handler formats into a 0x400-byte
  buffer (limit 0x3FF) and leaves state+0x48 = the whole `78 style args text FF` length.
- **Text ends at an FF that is not a glyph low byte**: F0..FA are two-byte glyph codes (so `F3 FF` = 私), FC
  carries two argument bytes (four when the second is 3C), FB/FD/FE are one byte. `vm.text_end` walks glyph-wise for this reason; a raw `find(b"\xff")`
  cut 2052 strings short in the first pass.
- 49,363 text blocks in D_SCE (styles: 00 dialogue 38.6k, 01 7.7k, 02 1.7k, 80/81 0.8k, A0 407, C0 128 choices).
  A linear sweep with skip-on-undecodable-byte leaves 0.24% of the file undecoded in runs shorter than 32 bytes;
  every trace boundary of scene 1 lands on a sweep instruction start.
- **Resync** (`vm.resync_texts`, used by `patch.sweep`, so extract and insert share one partition): after an
  undecodable byte in dead code the sweep can be out of step and swallow a 78 op inside another op's arguments
  (slot 1 `01 06 00 FC EA 01 FE 7B 53 00 78 00 晃一郎「…`: `53 00 78 00` eats the text). Candidates = 78 ops whose
  text reads as dialogue (punctuation 「」。、‥？！ + ≥4 kana; data decodes as kana half the time). Several candidates
  sharing one FF are one line reached from an earlier 78 byte in an operand: take the one right after a speaker op
  `7B xx yy`, else the latest; an unanchored candidate that cuts a control-flow-walk instruction is data (dropped:
  e.g. slot 103 `14 78 00 ..`). +164 lines. A rebuilt record is re-decoded with the old text offsets remapped
  (`patch.decode(new, resync=…)`), since English no longer reads as Japanese dialogue.
- After resync + the `FC xx 3C` fix, `jp_left.py` on the marker D_SCE finds 349 runs / 1,592 bytes, none longer
  than 7 bytes and all bytecode that happens to decode (e.g. `ヱ易ヴ給も` after `FF 79 00 11 B0`).
- `1E 08` likely carries one more argument byte than `vm.SUBK` knows (slot 11 `1E 08 14 7B 26 00 78 00`: the walk
  reads `14 7B 26 00 78` as a branch). Not fixed: the resync's speaker anchor covers the text it hid; check the
  handler before relying on the walk there.

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

## Insertion, phase 5 (tools/patch.py, tools/insert.py, tools/font_en.py)

### Opcode operand fixes — verified from the handlers
`vm.py` decoded `01`/`03` as an 8-bit displacement in an early pass; the handlers say otherwise:
- **01 / 03** (jump / call relative): operand = s16 at +1, target = op + disp + 1 (handlers 0x80058738, 0x800587A8).
- **07** (repeat): `07 <count> <s16>` — byte 1 is a counter in state+0x46, not part of the offset; when the
  counter is still running the handler sets state+0x48 = s16(at +2) + 2 (handler 0x80058920). So the offset sits
  at +2 and the target is op + disp + 2.
- **14** (conditional): s16 at +1, target = op + disp + 1; bit 15 of the flag word inverts the test
  (handler 0x8005A9C0). **02 / 04**: u32 at +1, target = op + u32 + 1.
- **7A** (choice): `7A count` then `count` u16, each self-relative to its own slot.
~~These are all the ops that write an offset into state+0x48.~~ **Wrong** (2026-11-03, `tools/subops.py` +
D_SCE hit rates = how often the decoded target is an instruction start). More branch forms, now in
`vm.rel_operands` / `patch.operand_fields`:
- Top-level `s16 + bias` branches (`vm.TOP_BRANCH`): **15** (s16 @+1, +1; 2507/2513), **D1/D2** (@+3, +3;
  567/568, 335/338), **D3** (@+5, +5). Rare, mostly in data: 33 3A 55 56 6B F9 (@+1) DB (@+3).
- Sub-op branches (`vm.SUB_BRANCH`): **16/19** (`16 13 a <s16>`, @+3, +3; 640/640), **5C/20** (`5C 14 <8 args>
  <s16>`, @+10, +10, fall through 12; 858/858 — vm.SUBK had 10 = the branch bias, which swallowed the next text
  op and made the marker build hang at story_S31), **C8/0-5, 8-13, 19-21** and **DC/3-5** (@+2, +2; DC/4
  955/955). C8's table length is 4, so its branch subs fall through at 4 (SUBK had 2 = the bias again); C8/8-9
  carry 4 more bytes.
- **0E** = event-hook pointers: `0E n <s16>` (n < 6, 4 bytes) or `0E n <6 x s16>` (14 bytes); each pointer =
  its own position + s16. The length table says 2 (the handler adds 2 or 12).
- Missing SUBK entries (handler adds 1 byte): 16/46, 1B/14, 1E/2, B0/50, C0/19, C0/31, C0/43, C0/46.
- Non-classic forms are rewritten only when their old target is an instruction start (`patch.trusted_target`),
  since the same byte patterns occur in data. Undecoded bytes in D_SCE: 5,944 -> 3,964.
- **Still open — trailing offset tables**: helper **0x8005832C(k)** sets the advance to `L + 2k + s16(op + L +
  2k)` (L = the advance when called, normally the instruction length), i.e. it branches through entry k of a
  table of self-relative s16s right after the instruction. ~80 handlers call it: top-level 17/18/19 (`17 a b c
  <s16>`: on match branch, else skip 2 -> 6 bytes; verified in data, e.g. `18 81 10 14 2B 00 78 01 セリカ…`),
  22, 43, 57, 6B, AA, AB, B9, BB, CC, E5, EA, EB, F7, and sub-ops 16/33-40, 1B/1-8, AD/16-54, AE/0-58,
  B0/6-54, C0/2-63, C8/4 (list: `python -X utf8 tools/trail.py`). Their table entries are not rewritten yet, and where
  vm.SUBK does not count the table the sweep decodes it as ops. Needed before real text goes in.

### Archive slot tables are duplicated in the EXE — verified
The loader does **not** read a rebuilt archive's own header: each of the three archives has a byte-identical copy
of its slot table (self-relative u32 per slot) inside the EXE, and that copy is what the game uses.

| archive | slots | EXE copy (file offset, RAM) |
|---|---|---|
| D_SCE | 448 | 0x9D5FC (RAM 0x8009D5FC) |
| D_BMESS | 128 | 0x9DCFC |
| D_SYSTEM | 512 | 0x9787C |

Proof: a marker build that only rewrote D_SCE.BIN loaded scene 1 from the *old* slot offset (0x192C instead of
0x184C) and the buffer held the record from 0xE0 bytes in; after `insert.py` rewrote the EXE copy the same build
shows the markers. `insert.py` finds each copy by exact match and fails when the match is not unique.

### Record growth
`arc.pack` moves the records after an edited one; each record must still fit the 0x8000 script buffer
(0x800DCE00) — `insert.py` fails the build above that. Records are 4-byte aligned, order preserved. Slot 0 (the
credits) is mostly FF padding, and a rebuilt record drops that padding, so *later* slots can move backwards;
that is what exposed the EXE header copy.

### Offset rewriter (tools/patch.py)
`patch.rebuild(record, edits)` re-emits the record from an instruction partition (text blocks the linear sweep
found are authoritative — extraction proved they roundtrip; then the control-flow walk; then the rest of the
sweep) and rewrites the operands above. `patch.verify` re-decodes the result and fails unless every branch, call,
choice item and text block maps to the same instruction. Identity rebuild is byte-exact for all 448 records
(tests/test_patch.py). A record's unreachable padding can decode as instructions whose "operands" are data; those
are reported as `target … has no new home` and left untouched.

### English in the text stream — verified in the marker build
- Letters and digits already exist as 1-byte 8x16 half-width cells (codes 01-1A A-Z, 1B-34 a-z, 36-3F 0-9,
  00 = space). Half-width symbols at codes 0x100-0x10D (`F0 xx`): % ~ / = + ? ! : ‥ etc.
- Half-width punctuation the font lacks (`.,'"-()[];&*<>#$@_\`{}|\^`) is drawn by `tools/font_en.py` into blank
  8x16 cells 0x114-0x12B (blank in the original font and unused by any extracted Japanese string; 0x35 is a
  blank cell the Japanese text *does* use — never repurpose it).
- Encoder: `tbl/en.tbl` (one line per glyph code, controls like the jp table). 30-char marker lines render in a
  full-width dialogue box (work/qa/marker/story_S01/final.png).
- Advance: 8 px for a code < 0x200 (one byte per row) and 12 px for a code >= 0x200 (kanji, 16x16). Escape:
  `[..]` in a string is read as a hex byte, so an English line must not contain `[XX]` with two hex digits.


