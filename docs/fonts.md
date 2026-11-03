# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font_en.py` (art in the source) | drawn for this project | MIT, same as repo | yes | the narrow proportional English font (VWF) in the game's 1 bpp cells: Latin, digits, punctuation 0x114-0x12B, the small "Prana" label 0x111-0x113 | all English cells redrawn |
| `fonts/LiberationSans-Bold.ttf` | github.com/liberationfonts/liberation-fonts release 2.1.5 | SIL OFL 1.1 (`fonts/LICENSE-Liberation.txt`) | yes, as rendered glyphs | `tools/gfx_en.py` graphics redraws (chapter cards) | none |
