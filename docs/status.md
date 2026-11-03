# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8 (full QA tour) next. Phase 7 (insert, fit, check) done 2026-11-03: lint 0 errors, lint_known.txt
  empty, check ok.
  - Phase 7 close-out: trust list renamed short (Amity, Cheer, Haste, Iron Fist, Encore, Sense; glossary rows
    updated, D10), weapon names shortened to the 152-px list (menu-fit.tsv). The 6 `special` strings translated
    by hand: padding sized so every value/pen lands at its JP pixel position (JP 1-byte codes incl. the 00 space
    were 8 px, `<200>` = F1 00 blank 12 px; English space 4 px), `{fb}` small-font runs kept as `[XX]` bytes;
    cells 0x111-0x113 (small プラナ label, only user bank00:003) redrawn as a 24-px "Prana" (font_en.LABEL).
    lint skips width/hex checks for form `special`; verified in-game (work/qa/p7spec2: status panel, system
    options, trust list). Turns/Funds (bank00:002), Bond (021), Partner (0F4) not seen in-game yet (no scene).
    Slot 239 dev lists stay Japanese (D11). The old system help-text garble (p7vwf/int_system) is gone on the
    current build; a probe of 264/306-px help rows rendered whole (work/qa/p7spec).
    **work/states/title.sstate is stale** (pre-VWF EXE: warps from it time out): `--all --title` regenerates it.
  - Phase 7 detail (2026-11-03): **VWF** (tools/font_en.py: narrow proportional English glyphs in every Latin/
    punctuation cell, even advances 2-8 px; hook on the glyph routine's `x += 8` at 0x80035258 and on the message
    pixel-width fn 0x80031010, which places the location label / sizes the weapon popup / centres event titles;
    hook + 0x200-byte advance table live after the relocated bank). Verified in-game (work/qa/p7vwf*/).
    Balanced word wrap in tlform.wrap (0 stub last lines, was 3,215). `tools/lint.py` (in check.py, ~16 s) =
    whole-script lint; menu rows checked in px against pen moves / tools/menu_room.tsv (measured or inferred
    rooms, each with its evidence) / the bank group's widest JP row / the JP row. `script/keep_jp.txt` = ids
    allowed no English. `tools/lint_known.txt` = open-error ratchet (empty since phase 7 closed).
    Menu rewordings (D10) in docs/menu-fit.tsv, applied by `tools/set_en.py docs/menu-fit.tsv`.
    ROM gate: tests/test_romdiff.py (every EXE byte change covered by a logged write with the right original).
    Help text (bank group 1) may use up to 3 rows (tlform.HELP_ROWS).
  - **Menu rooms = window cell chains** (RAM 0x800CEF40, 60-byte entries of 4 cells {+4 right, +6 below, +8 x,
    +9 y, +A w, +B h} + x/y/flags/buffer): message and list lines are 4 x 64 = 256 px; battle command window
    cells are 32 px wide; status/ability panels 64-px cells (the window frame can be narrower than the cells:
    "Move Type Ground" clips at the frame). Text past the chain wraps into the next buffer row (garbles the line
    start of cell 4). Dumps: work/qa/p7cells/<scene>/ (scratch decoder printed `w64h16>0401` chains).
  - Code 00 = English space AND the JP full-width space: advance 4 now (was 8).
  - Phase 6 result: 340 batches translated (b279 = binary data res07:0EEB, skipped on purpose), each reviewed +
    fixed by a fresh agent (D9; pilot b009 approved in-game), `batches.py check` 0 errors on all, merged into
    script/ (31,660 units). Untranslated now: junk/data only, the 9 `special` bank strings ({fb} small-font runs /
    raw cells, by hand), slot 239's dev scenario lists (junk form), exe_vm/exe_inline (copies of res58 lines).
    473 Minors in `docs/polish.md` (phase 9 gate).
  - Pipeline: `tools/batches.py split|check|merge|pairs|terms|status` (work/tl/, gitignored); merge keys each
    unit on today's script entry by id (the batch jp predates the tbl fixes). `tools/tlform.py` = forms, word
    wrap and checks. Briefs: `docs/translator-brief.md`, `docs/reviewer-brief.md`. Dialogue format D8.
  - Fixes in phase 6: tbl E1 = ヴ / E0 = ゔ, 305 圧 (was 庄), 8A2 氏 (was 兵), 983 嘗, 9D3 枯 (cells rendered);
    check: glossary rows beat the honorific rule, ムコ/ジイ/バア + さん are nouns, リーク unenforced ("leak" too).
  - **Far branches**: English pushed slot 239's 7A choice items past s16; `patch.rebuild` routes such branches
    through `02 <u32>` trampolines at the record head (behind an 01) or tail and verify() follows them
    (`tests/test_patch.py::test_far_branch_gets_trampoline`). In-game, `warp.py debug_239` picks item 2 and lands
    on the same menu as the JP disc (work/qa/tramp*/).
  - English build boots; story_S01, story_S31, battle_unit_menu reached and render English (work/qa/p6/).
- **Done:**
  - Step 0: PCSX-Redux in `tools/pcsx/`, SCPH-5500 BIOS, mkpsxiso/dumpsxiso 2.30 in `tools/mkpsxiso/`, armips 0.11
    in `tools/armips/` (all gitignored; re-fetch: `fetch_emu.py pcsx|psx-bios`, `gh release download` from
    Lameguy64/mkpsxiso v2.30 and Kingcom/armips v0.11.0). ROM pinned, pre-commit check gates commits, guard hook
    active, boot route `tools/routes/boot.txt`. Rulings D1-D7 in docs/decisions.md.
  - Phase 1 recon (docs/re/): archive/LZ/QX (roundtrip), font, `tbl/jp.tbl`, VM opcode table, text sources,
    RAM limit, graphics-text survey (docs/re/graphics.md).
  - **Phase 2 debug tool** (`tools/debug/`, facts in docs/re/flow.md): `warp.lua` patches the New Game `0B 01 00`
    in the resident EXE script to any D_SCE scene (or falls through to the intermission, SCENE=-1), sets story
    flags / episode / pokes, and can stop on a VM op (`STOP_OP`) and play a route after it (`POST`).
    `warp.py NAME|--all [--title]` runs entries of `scenes.tsv` (generated by `gen_scenes.py`): 26 chapter starts,
    69 chapter cards, intermission + Save / System / Next, character + unit settings, Continue, first battle,
    sortie screen, dev guard message, endings 347-352, credits (scene 0). All 115 reach their screen from a cold
    boot (re-verified 2026-11-03 on the marker build). States in work/states/<name>.sstate.
  - **Phase 3 identity build**: `tools/build.py` (dumpsxiso once -> arc.pack -> mkpsxiso via a layout pointing
    changed files at build/files -> split into Track 1/2 + cue), ~5 s. `tests/test_build.py` asserts both track
    SHA-1s == rom.sha1 (green). Files may grow on disc (found by ISO name).
  - **Phase 4 extract** (2026-11-02): `tools/vm.py` decodes the scenario bytecode; `tools/extract.py dump` writes
    `script/sce/NNN.json` (49,363), `script/exe_bank.json` (1,990), `script/exe_vm.json` (6), `script/resident.json`
    (11), `script/exe_inline.json`; `check` re-encodes every `jp` and re-discovers every block. `tbl/jp.tbl` covers
    all 2,637 glyph cells.
  - **Phase 5 insert + marker build** (2026-11-03):
    - `tools/patch.py` re-emits a VM record from an instruction partition and rewrites every offset operand
      (01/02/03/04/07/14/7A); identity rebuild is byte-exact for all 448 records and `verify()` re-decodes the
      result. Operand formulas corrected from the handlers (01/03 are s16; 07 is `07 <count> <s16>`), see
      docs/re/text.md.
    - **The three archives' slot tables are duplicated in the EXE** (D_SCE 0x9D5FC, D_BMESS 0x9DCFC, D_SYSTEM
      0x9787C) and the loader reads *that* copy: repacking D_SCE without patching it loaded every record from the
      old offset (scene 1 came up black). `insert.py` now rewrites the copy and fails when the match is ambiguous.
    - `tools/insert.py` writes `en` (or marker) text into D_SCE, repacks through `arc.pack`, patches the font and
      logs every write to `build/writes.txt` (romdiff format). `tools/build.py --marker [--slots] [--width]
      [--override TSV]`.
    - English font: the game already has 8x16 half-width A-Z a-z 0-9 and ? ! : / = + % ~; `tools/font_en.py` adds
      24 punctuation cells (0x114-0x12B) into blank cells, `tbl/en.tbl` is the encoder. Verified in-game.
    - Marker build (`build/`, `--marker`) tours: **115/115 scenes reached**, contact sheets
      `work/qa/marker_all/sheet.png`, per-scene shots in `work/qa/marker_all/`.
    - **Width gate**: 30 chars/line, 3 lines/page for the dialogue box (portrait and plain), measured with a
      90-digit probe (`work/qa/probe1/`). Table and rules in `docs/widths.md`.
  - **Missed text fixed** (2026-11-03): resync pass (`vm.resync_texts`, shared by extract and insert via
    `patch.sweep`) +146 lines; `FC xx 3C a b` carries 2 more bytes (inline face change; its FF was read as the
    end, ~370 lines cut short) -> `{face:..}` in tbl (`FC??3C` wildcard key, tbl.py). jp_left on the marker
    D_SCE: 778 runs/6,605 B -> 349/1,592 B, all ≤7-byte bytecode noise. 51,364 strings.
  - **VM grammar fixes** (docs/re/text.md "Opcode operand fixes"): op 15/D1/D2/D3 and sub-ops 16/19, 5C/20,
    C8/*, DC/3-5 are branches the rewriter ignored; 0E carries hook pointers; vm.SUBK had branch biases as
    lengths (5C/20 swallowed a text op and hung story_S31) and lacked 8 one-byte entries. `tools/subops.py`
    audits the handlers. Undecoded D_SCE bytes 5,944 -> 3,964.
  - **Trailing offset tables + switch + variable lengths** (same day): helper 0x8005832C branches through
    self-relative s16 tables after the op (`vm.TRAIL`: 17/18/19, C0/29/30/35 + handler-derived keys), B9
    switch tables (FFFF-terminated), 82/C0-45/5C-24/C8-21/DC-5 lengths. D_SCE undecoded bytes 5,944 -> 1,174,
    walk errors 266 -> 8; 51,366 strings. `warp.py --deep N` = flow check to the Nth text box.
  - **Flow check** `warp.py --all --match story_ --deep 30`: 24/26 reach the 30th box on the marker build;
    S22 and S30 stop short on the original disc too (their scenes end first). Normal tour 115/115.
  - **Script buffer raised 0x8000 -> 0xFFF0** (one EXE immediate, logged in build/writes.txt); heap has
    480+ KB free even mid-battle; a 0x9690-byte slot 1 verified in-game (docs/re/disc.md).
  - **EXE message bank** (menus, names): relocated past the EXE end behind a new root, heap moved above it
    (docs/re/disc.md); 13 menu scenes verified with marker text. Groups 12-21 + 2 table entries = status data.
  - **D_BMESS**: `tools/bmess.py` walker, extract + insert with re-aimed offsets, record stride 0x3FF8, output
    buffer 0x800; verified in a battle (docs/re/text.md).
  - **Resident sub 58** (Yamato's affection hints): copied after the bank with call stubs (docs/re/text.md);
    `warp.py res58_status` shows the relocated sub running; structural test in tests/test_patch.py.
  - Marker regression tour 2026-11-03 (`warp.py --all --title`): **118/118** reached, sheets
    `work/qa/marker_all/sheet*.png`. Choice rows now stop on `0x78/C0` (warp.lua STOP_ARG; the 7A runs within
    a frame) and a STOP halts the mash so the shot holds the box.
  - Width gate complete (docs/widths.md): dialogue 30x3, choice 30, battle band 36x3 (no wrap, `{nl}` by
    hand), menus = Japanese pixel width, hints 30 (assumed).
- **Next:**
  1. Phase 8: `warp.py --all --title --cue "build/Seireiki Rayblade (English).cue" --out work/qa/p8` (regenerates
     the stale title state first) + visual-QA verdicts per chunk. Weapon list (bank04, room 152 px inferred from
     the pen columns) and Turns/Funds/Partner rows still want an in-game look (no scene yet).
- **Open items (text, non-blocking):**
  - `tbl/jp.tbl`: all shaky/supplement-block cells in use were reviewed glyph-beside-reading (2026-11-03,
    `work/scratch/glyphsus.py`); the confident anchored cells were not. Translators report odd kanji as UNSURE.
  - `1E xx` op insertions inside text (runtime values: names/items) are plain argument bytes; document them per
    sub-op for the translators.
  - `tbl/en.tbl`: `[XX]` with two hex digits inside an English line is read as a hex byte by the encoder, so
    English must not contain that pattern.
- **Open items (debug tool, non-blocking):**
  - Yamato's affection-hint lines (sub 58 at 0x3B1..) not reached in-game: the New Game warp into sub 58
    (`c58`, also with FLAGS 1E/70-77, or `c58+33B@200` = warp.lua ENTRY/ENTRY_F) shows only the status screen.
    Try a state after chapter S22's `0C 3A` call (scene 17 at 0x608) reached by real flow.
  - System > Sound test and > Memory album stop the emulator (frames stop inside op E0) when reached from the
    warped New-Game-state intermission; try from a state after a real chapter.
  - Private events (1B0 guard scenes) stay black with flag 0x1B0 set: they need the intermission free-roam context.
  - Game over screen, battle attack animation/cut-ins and the phase menu not in the scene list yet.
- **Open bugs:** none.
- **Waiting on the user:** nothing blocking. Non-blocking: title logo 聖霊機ライブレード has no official English logo,
  kept Japanese per D5 unless the owner wants an English logo.
