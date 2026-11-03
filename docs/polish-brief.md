# Polish brief - Seireiki Rayblade (PS1)

You settle one chunk of `docs/polish.md` (Minor findings from the batch reviewers and the story pass). The release
refuses to run while any line is unticked. Write only your two output files; never edit `script/`, `docs/` or git.

## Inputs
- Chunk `work/polish/pNN.txt`: `N| - [ ] <batch or story chapter> <id(s)> - <finding> - <suggestion>`.
- `python -X utf8 tools/polish.py show ID [ID..]` prints each entry's current `jp` and `en` (always look before you
  decide; the suggestion may be stale or quote the line loosely). Ids like `sce002:0152D`, `bank00:08F`; "(+...)" or
  "/" lists more ids with the same fix: settle them all.
- Rules: `docs/translator-brief.md` (forms, speaker tags, codes, widths), `glossary.md`, `docs/style-reference.md`.

## Decide each line
- **fixed**: the finding is right. Write the entry's whole new English. Keep every code exactly as in the current
  `en`: `{ctl:..}`, `{page}`, `{nl}`, `{fb}`, `[XX]` bytes, the `Name: ` speaker prefix, honorifics. Dialogue wraps
  automatically, so don't add `{nl}`. Menu/choice rows (`bank..`, choice lines) must not get longer than the
  current English unless the finding is about a cut-off; prefer equal or shorter.
- **waived: <reason>**: the finding is wrong, the current line is already fine, it needs an in-game check you can't
  make and the current text is acceptable, or the change would break a glossary ruling or a width. Short reason.
- A line of yours may be partly applied by an earlier fix (same id in another finding): read the current `en`.

## Outputs
- `work/polish/pNN.en.tsv`: `id<TAB>full new English`, one row per changed entry (UTF-8, no header).
- `work/polish/pNN.ticks.tsv`: `N<TAB>fixed` or `N<TAB>waived: reason`, one row for EVERY chunk line.
- Final message: counts fixed/waived and any id you could not find.
