# Translator brief - Seireiki Rayblade (PS1, 1998)

You translate part of the Japanese script of Seireiki Rayblade into English for a fan patch: a mecha strategy RPG with
dating-sim free time. A brusque Japanese teen, Touya, is pulled into the parallel world Agarthia to pilot the Spirit
Mech Rayblade; his talking cat Yamato, a crew of quirky pilots and several heroines come along. Tone: anime drama
with lots of comedy and banter. Work only on the batches named in your dispatch, in order, each to a passing check
before the next. Do all translation yourself; no subagents. Repo root: `H:\translation\seireiki-rayblade-en`.

## Read first
1. `docs/style-reference.md` - character voices and approved pairs. Match these voices.
2. `work/tl/<batch>.terms.txt` - the binding glossary rows for this batch (JP -> EN). Full table: `glossary.md`
   (read its Style rules section once).
3. `docs/synopsis.md` - plot and late reveals (once, at the start). Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`, in story order (use neighbours for context). ` / ` marks a line
break of the original box - translate the box as one utterance, don't reproduce the breaks. Some lines were already
translated in an earlier batch and are left out, so a scene can have gaps.

Forms:
- `dlg` - dialogue/narration. Write a paragraph; the tools wrap it at 30 chars and page every 3 lines.
- `choice` - menu items separated by `{nl}` (kept literally): same number of items, each <= 29 letters, no leading
  space (the tool adds the indent). Often player choices; keep them short and in the player's (Touya's) voice.
- `menu` - EXE menu strings: names, commands, map/room names, topic titles, chapter titles. Keep every `{nl}` (rows are
  fixed) and every `{ctl:XXXX}` (FFFF = a number or name the game fills in; others move the pen). `limit` lists each
  row's Japanese width in characters: aim for it, but never abbreviate a name or term to fit - write it in full;
  the check lists over-width rows as warnings for the engine fix later.
- `battle` - battle cut-in lines, `{ctl:XXXX}` speaker code first. Keep every `{page}`; each `{page}` segment must
  wrap into <= 3 lines of 36 chars (~100 chars). Short, punchy shouts.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (never a shell heredoc or echo)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`, `!?`; `♥` is
allowed where the JP has it. No tabs inside the English, no Japanese or full-width characters, no `\uXXXX`.

## Speaker tags (enforced)
- `名前「...」` -> `Name: text` (no quote marks). `名前（...）` (thought) -> `Name: (text)`. `名前『...』`
  (whisper/aside) -> `Name: 'text'`. Name = the glossary EN exactly (`?????` for ？？？？？ - keep the count).
- Battle: `{ctl:0041}トウヤ「...」` -> `{ctl:0041}Touya: text`.
- Lines without a tag (start with a full-width space) continue a speech or are narration: plain text.

## Codes (enforced)
- Copy every `{ctl:XXXX}` and `{face:XXXXXX}` exactly (same multiset). In dialogue `{ctl:XX3E}` is a pause of XX
  frames and `{face:..}` changes the portrait's expression: put each at the matching point of the English sentence.
- Copy every `{page}` (same count): it starts a new box. `{nl}` only where a break must fall (a dramatic line,
  a list); never needed to wrap.
- Never write `{` or `}` except in codes, and never `[` + two hex digits + `]`.

## Validate
`python -X utf8 tools/batches.py check <batch>` until it prints `<batch>: OK` (warnings are fine). It checks ids,
codes, speaker names, glossary terms, honorifics and widths.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add or skip. Adapt wordplay and
  jokes so they still land (no translator notes).
- Keep the speaker audible (style reference): JP register markers become English devices. Old men's ワシ/じゃ/のう
  ("eh?", "my boy"), rough ぜ/ねぇ/やがる ("dammit", "the hell", clipped), feminine かしら/わよ/のね ("I wonder...",
  "you know"), Yamato's ニャ (cat puns on n-sounds), Derock's なんだな (sentence tag), Melvi's third person.
- Names and terms exactly as in the glossary; full names, never abbreviated. Honorifics kept, hyphenated:
  さん -san, くん/君 -kun, ちゃん -chan, 様 -sama, 殿 -dono (the check enforces them after names); 先生 as a
  title -> "Sensei"; 殿下 -> "Your/His Highness"; 姫 -> "Princess".
- Punctuation: ‥‥ -> `...`; ！？/⁉ -> `!?`; ‼ -> `!!`; ～ -> stretch the word or a trailing `~`; 「」“” inside a line
  -> "..."; 『』 inside a line -> '...' or "..." for a title; ＜ゼ＝オード＞ -> Ze=Ode (drop the brackets).
- Numbers the game fills in: no suffix glued to `{ctl:FFFF}` (write "No. {ctl:FFFF}", never "{ctl:FFFF}th").
- Sound effects: *Slam!* style.
- The Japanese is decoded through a font table that may still misread a rare kanji. If a word makes no sense, infer
  it from context and report it (`UNSURE: id - reads X, probably Y`).
- Dev/debug lines (flag-check messages, test menus) get a plain literal translation.

## Consistency
Never edit `glossary.md` or any file except your `work/tl/<batch>.out.tsv` and `.report.txt`. For a recurring
name or term not in the terms file, pick a form, use it consistently, and report it.

## Report
Write `work/tl/<batch>.report.txt` per batch: lines `NEW TERM: jp -> en`, `UNSURE: id - note`,
`LONG: id - note` (a menu name over width), or `none`. Then reply with only one line:
`done <batches>: <n> NEW TERM, <n> UNSURE, <n> LONG`.
