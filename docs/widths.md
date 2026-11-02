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
| Choice list (78 C0 / op 7A) | mid-battle, dev chapter menu | not measured yet | | | scene 2 and 43 were not reachable to the choice inside a 9000-frame run; see below |
| Battle message boxes (D_BMESS) | battles | not extracted yet (own bytecode) | | | docs/re/text.md |
| Menu rows, item/skill/name lists (EXE message bank) | system, shop, battle unit menu | not measured yet | | | the bank's 1,990 strings cannot be re-inserted yet: they live in the EXE and need relocation + table repointing (phase 6/7) |

Box geometry, for reference: the dialogue window's text area starts at x≈50 (right of the portrait) and the
right edge is x≈308; 30 glyphs × 8 px = 240 px, so a 30-char line ends 8–10 px short of the edge. Ink extents
measured on `work/qa/probe1/story_S01/final.png`: line 1 x=52..302, line 3 ends at x=299 with the page arrow
after it.

## Menu geometry measured from shots (provisional, EXE-bank text is not insertable yet)

These come from the window pixels in existing shots, not from a probe build, because those strings live in the
EXE message bank and cannot be re-inserted until they are relocated (docs/status.md, next step 2). Read them as
"how much room the window leaves", then confirm with a probe once bank insertion exists.

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
- Before translating a scene that shows a choice list, measure the choice box the same way (probe one `style C0`
  entry, warp to it, stop on op 7A) and add its row here.
