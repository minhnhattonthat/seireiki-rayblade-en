# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1 (recon) done -> next phase 2 (debug tool). No build yet (`tools/build.py` not written).
- **Done:**
  - Step 0: PCSX-Redux in `tools/pcsx/`, SCPH-5500 BIOS, mkpsxiso/dumpsxiso 2.30 in `tools/mkpsxiso/`, armips 0.11 in
    `tools/armips/` (all gitignored; re-fetch: `fetch_emu.py pcsx|psx-bios`, `gh release download` from
    Lameguy64/mkpsxiso v2.30 and Kingcom/armips v0.11.0). ROM pinned, pre-commit check gates commits (tested),
    guard hook active (blocks sed -i / heredoc writes), boot route `tools/routes/boot.txt` reaches New Game ->
    first dialogue (~7000 frames). Rulings D1-D7 in docs/decisions.md.
  - Recon (docs/re/): archive format + LZ codec + QX images (all roundtrip), font decoded, `tbl/jp.tbl` draft
    (kana exact, kanji template-matched), scenario VM interpreter/length table/jump ops, text op 0x78, text sources
    (D_SCE, D_BMESS, EXE menus, D_SYSTEM name tables), RAM limit (0x8000 script buffer), graphics-text static sweep
    (`tools/qx.py sweep`, survey in docs/re/graphics.md). Identity rebuild verified by hand (phase 3 test not written).
  - Dreamcast fan patch cloned to `work/ext/rt-rayblade/src` (glossary of 851 names; format notes) — docs/re/prior-work.md.
- **Next:**
  1. Phase 2 debug tool: the EXE has a leftover debug menu (ロード/セーブ/Mロード/Mセーブ/全体PUT/全体更新 at EXE file 0x6418)
     — find what calls it; else warp by loading D_SCE scene records (VM state 0x800CD570) from `tools/debug/warp.lua`.
     Scene list must include chapter cards (D_SYSTEM 17-20 banners), album, credits (D_SYSTEM 472), demo screens.
  2. Phase 3: `tools/build.py` + identity test (dumpsxiso -> arc.pack/lz -> mkpsxiso, split back to 2 tracks).
  3. Phase 4: full VM disassembler (length table + variable ops) with roundtrip; classify branch ops; review kanji
     table (`tbl/glyph_overrides.tsv`, 51 `#` duplicates; known misreads 亜/目/日); verify FC/FB/FE arg counts.
  4. Phase 5 blockers to plan: 0x8000 script buffer (largest record 0x75C0), 0x400 format buffer, Latin font
     (8-px glyphs 01-34 exist; ASCII mode via FB?), VM offset fix-ups on text growth.
- **Open bugs:** none (no build).
- **Waiting on the user:** nothing blocking. Non-blocking: title logo 聖霊機ライブレード has no official English logo,
  kept Japanese per D5 unless the owner wants an English logo.
