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
