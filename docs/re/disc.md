# Disc, archives, compression, images

Dump: Redump "Seireiki Rayblade (Japan)" SLPS-02652 (Winkysoft, 1999-12), `rom.sha1`. Track 1 MODE2/2352 data, track 2 audio.

## Disc rebuild — verified
- `tools/mkpsxiso/.../dumpsxiso.exe -x work/disc/tree -s work/disc/layout.xml <cue>`; `mkpsxiso.exe -y -o X.bin -c X.cue layout.xml`
  (cwd `work/disc`). mkpsxiso v2.30 (github.com/Lameguy64/mkpsxiso).
- **verified**: the rebuilt image is byte-identical: first 643,965,840 bytes == Track 1, the rest == Track 2
  (sha1 bd1fde88...). mkpsxiso writes one .bin with both tracks; split it back at the Track 1 size for the release.
- Files: `SLPS_026.52` (EXE, 776 KB), `D_SYSTEM D_SCE D_FIELD D_SCREEN D_FACE D_FACE2 D_UNIT D_SE D_EFFECT D_CUTIN D_BMESS
  D_ANIME D_BGM .BIN`, `MOVIE.BIN` (mixed/XA+STR), `NULL.DA` (track 2). The EXE holds the file names at 0x80010039..
- **Files may grow — verified 2026-11-02**: no LBA table in the EXE (u32/BCD-MSF search finds only unaligned noise),
  and a disc with D_SYSTEM.BIN grown by 40 sectors (every later file, MOVIE included, shifted) boots through the intro
  FMV and warps to story_S01 (portrait from D_FACE) and battle_map (D_FIELD) with frames identical to the original.
  The game looks files up by name in the ISO directory.
- **Build**: `tools/build.py` (unpack once -> repack D_SCE/D_BMESS/D_SYSTEM via arc.pack -> mkpsxiso with a layout whose
  changed files point at build/files -> split at track 2 INDEX 00). Identity test `tests/test_build.py` (both track
  SHA-1s == rom.sha1). `build/lba.txt` = mkpsxiso's LBA listing of the last build.

## Archive format (`tools/arc.py`) — verified
Header = N u32 LE **self-relative** offsets: slot i -> `4*i + off[i]`; `off[0] = 4*N`. Slots can alias a record (D_BMESS
slots 0/1, D_FACE2 many). A record ends at the next distinct target. `arc.pack(data, {})` rebuilds every archive
byte-identically (records 4-byte aligned). Verified: D_SCE slot 1 = bytes loaded at RAM 0x800DCE00 in the first scene.

| Archive | slots / records | content |
|---|---|---|
| D_SCE | 448 / 444 | scenario VM scripts, raw (not compressed); slot 447 = string list. Max record 0x75C0 (slot 239) |
| D_BMESS | 128 / 93 | battle messages, raw (see text.md) |
| D_SYSTEM | 512 / 476 | LZ: mostly QX images (UI, labels, name plates, title logo); a few non-image records (14, 15, 35: TODO) |
| D_SCREEN | 640 / 585 | LZ QX images: backgrounds, event CGs, UI screens (slot 305 magic 0x5F51: TODO) |
| D_FACE / D_FACE2 | 768 / 736, 768 / 168 | LZ QX portraits 64x64 / cut-in 128x112. D_FACE2: 84 records decode 2-3 bytes short (TODO) |
| D_CUTIN, D_UNIT, D_EFFECT | | LZ QX images (cut-ins, unit sprites, effects) |
| D_FIELD | 80 / 80 | maps (not decoded) |
| D_SE, D_BGM | | sound (VAB/SEQ-like, not needed) |
| D_ANIME | 768 / 643 | animation scripts (not decoded) |

## LZ (`tools/lz.py`) — verified
Decompressor in EXE at 0x80025574 (a0 dst, a1 src; found by a read watch on D_SCREEN slot 0 in RAM). Record = u32 size
+ stream; flag bits MSB-first; `1` literal; `01` long copy (13-bit offset, 3-bit length, extension byte, 0 = end);
`00bb` short copy (8-bit offset, length 2-5). `lz.py test <archive>`: every record of D_FACE, D_UNIT, D_CUTIN,
D_SCREEN, D_EFFECT, D_SYSTEM decompresses and roundtrips through `lz.compress` (not byte-identical to the original
compressor; the game only needs a valid stream). Some D_FACE streams emit zero bytes past the header size before the
end code; the header size is the data length.

## QX images (`tools/qx.py`) — verified by rendering (title logo, menus, faces render correctly)
u16 magic, u16 count, count x {u32 offset, u16 a, u16 b, u16 w, u16 h, i16 x, i16 y}, u32 ncolors, CLUT (BGR555).
`QX` 0x5851 = 8 bpp; `qX` 0x5871 = 4 bpp, palette (a & 0xF) of the CLUT (guess; colours look right on most sheets).
`qx.py sweep <ARC>` writes `work/gfx/<ARC>/` PNGs + contact sheets + skipped.txt.

## Free space / limits
- Disc: rebuilt by mkpsxiso, so files can grow; nothing needs to fit in place on disc.
- **RAM is the limit.** Script buffer: the loader (0x80058298) allocates 0x8000 bytes (`jal 0x80036860` with
  a0 = 0x8000) for a D_SCE record; largest record 0x75C0 -> only 2.6 KB slack. Dialogue format buffer: 0x400
  bytes (78 handler).
- **Heap — verified 2026-11-03** (`tools/heap.py`): allocator 0x80036860 (best fit), free 0x800365E8 (addr, size,
  coalescing), free list 0x800D4E58 (64 x {addr, size}, count at +0x200). Boot seeds it with free(0x800DCE00,
  0xF3200) = 0x800DCE00..0x801D0000; the script buffer is the first block, allocated once, never freed. Free at
  runtime: 846 KB in story scenes and endings, 932 KB at the intermission, 511/481 KB on the battle map / ability
  screen (one or two blocks).
- **Script buffer raised to 0xFFF0** by the build (`insert.BUFFER_ALLOC`: `ori a0, zero, 0x8000` at file 0x48AB4
  -> 0xFFF0). Verified: slot 1 grown to 0x9690 (`build.py --marker --slots 1 --width 330`) warps and plays, the
  whole record is intact in RAM at 0x800DCE00, and the heap is 0x7FF0 smaller (814 KB free). English estimate
  for the largest records (2.5x Japanese chars) is ~0xCB00, inside the new limit; s16 branches cap a record at
  ±32 KB spans (patch.rebuild fails on overflow).
- **EXE message bank relocated past the EXE end — verified 2026-11-03** (`insert.bank_patch`, test
  `test_bank_relocation_resolves_every_entry`). Every bank reader loads the root through `*0x80015348` (30+
  `lui/lw 0x5348` sites) and no code or data word points into 0x80015348..0x8001CF7E otherwise, so the build
  writes a new root + the edited text groups' (0-11) tables and strings at 0x800DCE00 and repoints that one
  word; data groups 12-21 keep their old tables (their entry 0 is not a count). Layout at boot:
  - EXE `t_size` (header 0x1C) grows from 0xBD000 to cover the bank (the BIOS loads it; +~100 KB). crt0 clears
    BSS 0x800CC898..0x800DBAB0 only, so the bank survives.
  - The heap init (0x80036C40, called at boot and again from 0x8005BD14) did `memset(0x800DC000, 0, 0xF4000)`
    then `free(0x800DCE00, 0xF3200)`. 0x800DC000..0x800DCE00 are buffers used by 0x80020xxx code, not heap.
    The build points the memset `jal` at a 17-instruction hook at 0x800DCE00 that clears 0x800DC000+0xE00 and
    the heap from its new base, and rewrites the free() immediates: heap = (bank end rounded to 0x800) ..
    0x801D0000 (marker build: 0x800E5800, 938 KB; was 972 KB).
  - The script buffer is the first heap block, so it moves too: tools read its pointer at 0x800CD5C0.
- EXE: other free-space candidates not surveyed (not needed: the bank and anything else can go past the end).
