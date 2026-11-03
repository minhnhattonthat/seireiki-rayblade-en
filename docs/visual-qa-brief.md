# Visual-QA reviewer brief - Seireiki Rayblade (PS1)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- each tile is one screen reached by a debug warp (tools/debug/scenes.tsv), not a play route: a black screen,
  a menu with `????` entries (locked trust commands, unknown unit), placeholder stats, or a dialogue box the warp
  stopped before it filled are the warp's state, not a translation bug when tour_jp shows the same;
- the English font is a narrow proportional font (VWF) drawn by the game's own 8x16 cells: tight letter spacing
  and uneven glyph widths are intended; "Lv 1 Exp 0" / "HP" in a small bold font are the game's own labels;
- battle status panel `Spirit±0  Prana 57/57`: "Prana" is a compact label on purpose;
- trust-command names are short on purpose (Amity, Cheer, Haste, Iron Fist, Encore, Sense; docs/menu-fit.tsv);
- the title logo 聖霊機ライブレード stays Japanese (D5: no official English logo).
- Japanese drawn as graphics (chapter cards, name plates, icons, credits) is still an `issue`, but start its note
  with `gfx:` so it sorts apart from text bugs (docs/re/graphics.md tracks those images).

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
