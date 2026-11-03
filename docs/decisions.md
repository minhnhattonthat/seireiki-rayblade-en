# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All of D1-D7 came from the owner's standing answers injected into the one-shot run (2026-11-02).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-02 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer. |
| D2 | 2026-11-02 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-02 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-02 | Abbreviations | engine work first (default), abbreviate | Default: engine work first (wider box, VWF, small font), abbreviate only as a flagged last resort. |
| D5 | 2026-11-02 | Graphics text left in Japanese | none (default), list | Translate all (titles, menus, banners, cards); keep the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-02 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through checkpoints, report at the end. |
| D7 | 2026-11-02 | Existing saves / memory cards | user supplies, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-03 | English dialogue layout (controller default under D6, owner may override) | `Name: "text"` with quote marks; `Name: text`; name on its own line | `Name: text`, thoughts `Name: (text)`, whispers `Name: 'text'`: no quote marks saves 2 of 30 columns per box and reads like other mecha-SRPG fan patches. Translators write paragraphs; `tools/tlform.py` word-wraps (30/line, 3rd line of a page 28, battle 36x3) so line breaks never split words. `♥` kept (the font has it at 0xF002). |
| D9 | 2026-11-03 | Review pass without a write-capable reviewer type | reviewer type (read-only, reports into the controller's context), a fresh translator-type agent per review that also applies fixes | Fresh translator-type agent following docs/reviewer-brief.md: an independent read that writes `work/tl/<batch>.review.txt` and fixes Critical/Important itself; Minors go to docs/polish.md. |
| D10 | 2026-11-03 | English set at the game's 8-px advance overflowed most menus (fields sit at pen positions sized for 12-px kanji) (controller default under D4/D6, owner may override) | abbreviate everything to the JP width; VWF (narrow proportional font) + reword only what still overflows; widen each window (per-window engine RE) | VWF everywhere (tools/font_en.py: dialogue, menus, battle) - it cut menu overflows from 1,212 rows to ~40 - then shorter synonyms for fixed narrow windows (battle command cells are 32 px but clip text past ~26 px (2026-11-03 player report "Attac"; owner OK'd abbreviating): Fight, Fix, Refill, Form, Stats, Flee; phase menu: Orders, Objectives), each listed in docs/menu-fit.tsv; abbreviations there are marked ABBR (Atk, Req.). Widening windows stays open for the windows still listed in tools/lint_known.txt. |
| D11 | 2026-11-03 | Slot 239's developer scenario-select lists (reachable only through the debug menu, extracted as junk form) (controller default under D6, owner may override) | translate literally, leave Japanese | Leave Japanese: no player reaches them, and their records hold op bytes the far-branch trampolines already had to work around; translating risks the record for no player benefit. |
| D12 | 2026-11-03 | AI order 無理はするな: its battle icon (D_SYSTEM x.61, 10 px box) holds one letter, and "Cautious" shares C with "Counter" (controller default under D6, owner may override) | keep "Cautious" with a two-letter icon; reword to "Safe" with icon S | "Safe" (bank00:0AE) and icons M C A S D: one readable letter each, and "play it safe" keeps the sense. |
