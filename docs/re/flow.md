# Game flow, scenes, flags, loads (phase 2: debug tool)

## Loads — verified (`tools/lua/loadlog.lua`)
- 0x80022068(type, file, slot, a3, [sp+10], [sp+14]=dest) queues a load into a ring of 12 x 20-byte entries at
  0x800CE3C8 (u8 type, u8 0, u16 file, u32 slot, u32 a3, u32 arg5, u32 dest). type 0x10 = raw record to dest,
  0x30 = LZ record (decoded), 0x40 = raw sectors (slot = byte offset, arg5 = size).
- File ids (not the name order in the EXE): 2 = D_SYSTEM?, 3 = D_SCREEN?, 4 = **D_SCE** (verified: New Game queues
  type 0x10 file 4 slot 1 -> 0x800DCE00), 7 = ?; 29/30 = MOVIE/sound streams (sector loads). TODO pin the rest.
- loadlog polls the ring each frame (no `--debugger`: the debugger mode stalls this game's CD loads; a 1,750-frame
  run timed out at 600 s).

## Scenario VM and scenes — verified unless marked
- State struct 0x800CD570: +0x40 base = address of the current instruction (the loop adds the op length to it),
  +0x48 pc offset within the op, +0x4C op sub-state (multi-frame ops count 0,1,2..), +0x54.. current op bytes.
- **Scene id** (= D_SCE slot) u16 at 0x800CDC86. Script buffer pointer at 0x800CD5C0 (0x8000 bytes, 0x800DCE00).
- Op **0B lo hi = goto scene** (stores the id at 0x800CDC86, queues D_SCE slot, base = buffer, pc = 0).
  Op **B4** = goto the first scene of the 27-pair table at 0x800C89E4 (u16 flag, u16 scene) whose flag is set
  (route branches: flags 0x190-0x19F, 0x386-0x38F, 0x5E0/0x5E1).
- Op **14 off16 flag16** = conditional relative jump (new op address = op address + off + 1): flag bit 15 set ->
  jump if flag (n & 0x7FFF) is set; clear -> jump if the flag is clear.
- **Story flags**: bit array at 0x800CDA84, flag n = byte n >> 3, mask 1 << (n & 7), 0x600 flags
  (test 0x80036E2C).
- **Resident system script** (title, New Game, Continue): in the EXE at RAM 0x80010374 (file 0xB74), 70
  self-relative sub-scripts (same layout as an archive). Sub-script 1 (New Game) ends `0B 01 00` at 0x80010620:
  New Game = goto scene 1. `tools/debug/warp.lua` rewrites that operand.
- Scripts guard dev-only entries with a message: 「1B0のフラグが立っていません。…強制終了いたします。」 (scene 103 and
  the 440-446 group): the private events need flag 0x1B0 (`tools/debug/catalog.py` lists guards per scene).
- **Scene 2 head = chapter dispatcher**: `14 0C 00 <flag> 00  5C 09 47 4F FF  0B <scene> 00` for flags
  0xA2-0xBB, then a developer chapter-select menu (「次のページへ S01 S03」 .. 「1ページ目へ戻る S31 S32」, 26 entries).
  Chapter label -> start scene (the `0B` operands, in menu order): S01 1, S03 3, S04 4, S06 5, S09 6, S09.5 7,
  S10 8, S11 9, S11.5 10, S13 11, S15 12, S16 13, S17 14, S20 15, S21 16, S22 17, S23 18, S24 19, S25 20,
  S26 23, S27 26, S28 31, S29 36, S30 41, S31 44, S32 208. (Labels vs story order: guess.)

## Scene map — verified by warping (tools/debug/scenes.tsv)
- Scene 0 = staff roll (credits). Scene 1 = prologue (classroom). Scene 2 = chapter dispatcher + dev menu + story.
- Battle scenes: `16 02 <map>` (map id 0x800CDC8A) + `40 FF` (load D_FIELD map) + `16 03 <title>` (chapter title
  id 0x800CDC89) + resident card sub-script (op 8C starts it; the card is fully drawn ~500-580 frames later).
  The card number is the episode byte 0x800CDC8B (`16 01` = +1; chapter-start scenes begin `16 01 01 00`).
  Titles 0-60 are set by some battle scene (17 and 47 by none); first scene per title -> `card_NN` entries.
- Op 16 = sub-op dispatcher (table 0x800C8580): 00 sets 0x800CDA82/83, 01 episode+1, 02 map id, 03 title id,
  10 sets 0x800CDC8C/8D. Op 10 = New Game init (episode 1, title 0, ...).
- Intermission = resident sub-script 5 (0x80010623): インターミッション / セーブ / システム / 次へすすむ + 「第N話『…』まで
  クリア」. System = options list (sound test, character settings, unit settings, memory album).
- Final battle 355 -> 356-360 -> endings 347-352 (heroine routes) -> `84 FF 81 06` -> credits.
- Private events (1B0 guard): 101-127, 186-190, 219-230, 362-366, 440-446 (catalog column `guards`).
- File ids: 0 = D_FIELD (maps, op 40), 2 = D_FACE (portraits, op 82), 3 = D_SYSTEM (title logo at boot),
  4 = D_SCE, 7 = D_SCREEN (backgrounds). Others TODO.
- Dialogue advances with circle. Battle: cross on the selected unit opens 移動/信頼/能力 + status panel.

## EXE message bank — verified
- `*0x80015348` = 0x8001534C: two-level self-relative u32 tables (same as the archive format); string id =
  (group << 8) | index; strings in the table encoding, FF-terminated. 22 groups. Reader e.g. 0x80031010 (width).
- The leftover debug menu (ロード/セーブ/Mロード/Mセーブ/全体PUT/全体更新, P: R: W: A:) = ids 0x006D-0x0070.
  No caller found (no constant 0x6D-0x70 passed to a bank reader; the strings' addresses appear nowhere): its code
  looks compiled out. The warp does not depend on it.
