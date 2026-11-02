# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| `tools/font_en.py` (art in the source) | drawn for this project | MIT, same as repo | yes | English punctuation cells 0x114-0x12B in the game's 1 bpp font | added 24 cells |
| <fonts/vwf_8px.png> | <drawn for this project> | <MIT, same as repo> | yes | <dialogue VWF> | <-> |
| <fonts/Title.ttf> | <url, v1.2> | <OFL 1.1> | <yes, as rendered glyphs> | <typeset.py title cards> | <-> |
