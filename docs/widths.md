# Text width gate (phase 5)

Measured limits for every text box variant, so translators write to a real budget instead of guessing. Each
number comes from a build with one line replaced by a probe string of digits (`work/qa/probe*.tsv`, built with
`tools/build.py --marker --override <tsv>`), warped to and shot in the emulator.

Method: the engine's own formatter wraps at a **glyph budget**, not at the window edge, so the probe is a run of
digits 8 px wide — where the digits break is the formatter's limit, and a shot shows both the break and whether
the box clips. Glyph advance is 8 px for a one-byte code (Latin, kana) and 12 px for a two-byte kanji code, so the
English budget in characters *is* the glyph budget.

| Variant | Where | Chars/line | Lines/page | Chars/page | Evidence |
|---|---|---|---|---|---|
| Dialogue, portrait box (78 style 0 under a speaker op; 38.6k lines) | chapters, events | **30** | **3** | 90 | `work/qa/probe1/story_S01/final.png`: 90 digits break 30/30/30, page arrow on line 3 |
| Dialogue, same box, marker lines (style 1/2 with portrait args) | chapters | **30** | 3 | 90 | `work/qa/marker_all/*.png`: a 30-char marker fills the line to the arrow (`[00208] quick brown fox jumps`) |
| Choice list (78 C0 items, one per `{nl}`, 113 blocks) | dialogue box, e.g. scene 90 bridge talk | **30** per item, incl. the leading space (cursor indent) | 3 items | | `work/qa/probe_choice/zoom.png` (probe `work/qa/probe_choice.tsv`, `warp.py choice_090`, frame 8700): the highlight bar is x 64..304 = 30 glyphs; a 41-char item wraps and pushes the list out of the box. Keep the leading space and ≤ 29 letters after it |
| Battle message (D_BMESS, `script/bmess.json`; band under the attack cut-in) | battle animations | **36** | **3** | 108 | `work/qa/probe_bm/f000920.png` (probe `work/qa/probe_bm.tsv`, first battle enemy phase): a 36-letter line fills x 33..317; **no automatic wrap** — a 60-digit line overwrote itself — so break every line with `{nl}` at ≤ 36 |
| Yamato's affection hints (`script/resident.json`, 11 lines, sub 58 `7B 12 00 78 00`) | heroine status screen | **30** (assumed: dialogue-box op; not reached in-game yet) | 3 | | lines carry the `ヤマト「..{nl}　..` name-tag layout: keep `{nl}` breaks, ≤ 30 per line incl. the indent |
| Menu rows, item/skill/name lists (EXE message bank) | system, shop, battle unit menu | see "Menu geometry" below | | | insertable since 2026-11-03 (bank relocated past the EXE end, docs/re/disc.md); probe one field with `--override` on a `bankGG:KKK` id |

Box geometry, for reference: the dialogue window's text area starts at x≈50 (right of the portrait) and the
right edge is x≈308; 30 glyphs × 8 px = 240 px, so a 30-char line ends 8–10 px short of the edge. Ink extents
measured on `work/qa/probe1/story_S01/final.png`: line 1 x=52..302, line 3 ends at x=299 with the page arrow
after it.

## Menu geometry measured from shots

These come from the window pixels in shots (marker bank strings fill exactly their Japanese pixel width and fit
in every menu shot). Read them as "how much room the window leaves"; probe a field with `--override bankGG:KKK`
before using more than the Japanese width.

| Field | Shot | Room (px) | Chars at 8 px |
|---|---|---|---|
| Battle unit command list (移動/信頼/能力) rows | `work/qa/marker_all/battle_unit_menu.png` | x 258..316 | **6** |
| Battle status panel rows (name, LV/EXP, HP/VP) | same | x 60..240 | **22** total, name field ~11 |
| Dialogue box interior | `work/qa/probe1/story_S01/final.png` | x 50..308 | 32 (engine stops at 30) |

Menu strings also redraw in more than one window (a character name shows in the status panel, the sortie list and
battle), so the *smallest* of those rooms is the budget — 11 characters for a name until measured per screen.

## Rules that follow
- Write to **30 characters per line**, **3 lines per page**, and let the engine break lines: a line of 30 or
  fewer characters never needs a `{nl}`. Put `{nl}` only where the break must be semantic (a name tag, a dash
  before a cut-in).
- A single text block longer than 90 characters pages instead of clipping — but the page arrow costs the last
  column of the last line, so keep the 3rd line to 28 characters.
- Two-byte codes (kanji, `?`/`!`/`:` and the added punctuation) advance 8 px while costing the formatter 2 units;
  kanji cost 3. English text is all 8 px, so a 30-glyph line is always exactly 240 px wide.
- Choice items (`style` 192 = 0xC0): one item per line, ≤ 30 characters including the leading space; never let an
  item wrap.
- Battle messages (`script/bmess.json`): ≤ 36 characters per line, break with `{nl}` yourself (the band does not
  wrap), ≤ 3 lines; keep the leading `{ctl:..}` speaker code.
- Menu/bank strings (`script/exe_bank.json`): budget = the Japanese string's own pixel width (kana 8 px, kanji 12
  px → letters at 8 px) unless a row in the table above gives more room; the marker build fills exactly that width
  and every menu shot shows it fits. Keep `{ctl:XXXX}` codes (FFFF = a number/name the game fills in, others move
  the pen) and `{fb}` small-font runs byte for byte.
