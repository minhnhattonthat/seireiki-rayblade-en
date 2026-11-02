# Prior work

- **retro-trans/Seireiki-Rayblade** (github.com/retro-trans/Seireiki-Rayblade): English fan translation of the
  **Dreamcast** port (T-42201M), v0.7.23, unfinished machine translation (503 held rows). Local clone (data only, never
  run): `work/ext/rt-rayblade/src` (gitignored). Useful:
  - `work/glossary/glossary.json`: 851 entries with JP/EN names (characters, places, terms) — the "earlier fan
    patch" source for romanization (D2) when no official English exists.
  - `work/translation/en/` English-only rows (no JP), `docs/*.json` format notes. The DC data is the same game: same
    archive names (D_SCE 448 members, D_BMESS), same text encoding scheme (F0-FA prefix glyphs, FB-FF controls), same
    0x400 dialogue buffer. Their opcode is `8A 06` (DC) where PS1 has `78` — VM numbering differs.
  - `docs/battle-text-format.json` (D_BMESS layout), `docs/scenario-format.json`, `docs/chapter-cards.json`,
    `docs/location-headers.json`, `docs/attack-lettering.json`: lists of graphics-text classes to expect.
- Rolly (SEGA-SKY) VGA patch for DC: not relevant to PS1.
- No PS1 patch known.
