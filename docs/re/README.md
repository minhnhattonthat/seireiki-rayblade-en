# Reverse-engineering notes

One file per subsystem. Mark every finding with how far it is proven: **verified** (and how) or **guess** (and why).
Addresses are for the dump in `rom.sha1` (SLPS-02652) unless a note says otherwise. EXE: RAM = file - 0x800 + 0x80010000.

| File | Covers | State |
|---|---|---|
| [disc.md](disc.md) | disc rebuild (identity verified), archive format, LZ codec, QX images, RAM limits | verified (tools roundtrip) |
| [text.md](text.md) | font, encoding/table, control codes, scenario VM (verified lengths/jumps/text op), text locations (D_SCE, EXE bank, resident script), what is not extracted yet | verified (extract roundtrip + emulator trace) |
| [flow.md](flow.md) | game flow: loads, scene ids, story flags, VM jumps/gotos, intermission, cards, endings, credits, EXE message bank (debug tool basis) | verified by warping |
| [graphics.md](graphics.md) | graphics-text survey (static sweep of every LZ/QX archive) | first pass |
| [prior-work.md](prior-work.md) | Dreamcast fan translation (glossary, format notes) | — |

Helpers: `tools/arc.py` `lz.py` `qx.py` `fontsheet.py` `match_font.py` `build_tbl.py` `findtext.py` `re.py`
`vramview.py` `vm.py` (scenario VM decoder) `extract.py` (script/ dump + roundtrip/coverage check), `tools/lua/dump_at.lua`
(VRAM+RAM dump at a frame), `loadlog.lua` (load queue), `vmtrace.lua` (VM base/pc per frame), `vmlens.lua` (op +
advance per instruction; needs --debugger and is very slow), `tools/re.py xref` (lui/lo pairs),
`tools/debug/catalog.py` (scene first lines).
