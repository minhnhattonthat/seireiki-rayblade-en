# Story reviewer brief - Seireiki Rayblade (PS1)

You read one chapter of a JP->English fan translation straight through, in story order, the way a player
meets it. Per-batch reviewers already judged single lines with +-2 lines of context; your job is what they can't see.
Read-only: no edits, no git, no subagents. Return the report as your final message; the controller saves it.

## Inputs (paths in your dispatch)
- Chapter file: every line of the chapter in story order, `>> id | speaker | JP` / `EN`. Read ALL of it, in passes if
  large, before judging.
- `docs/synopsis.md` (plot, who is who, late reveals), `docs/style-reference.md` (voice per character),
  `glossary.md` (rulings at the top).

## This game's chapter files
- `## scene NNN` marks a D_SCE scene; scenes run in slot order, which is story order inside a scene group of the
  synopsis. Private Phase events (080-127, 186-190, 219-230, 256-298, 362-446) are standalone vignettes: judge each
  on its own, not as a sequence. Final-dungeon and ending variants (048-079, 347-361) repeat scenes per heroine.
- JP ` / ` = a line break in the box; EN is shown unwrapped (the build wraps it). Control codes are dropped,
  including the page break: a sentence glued to the next with no space (`reason.But`) is a new page in game, not
  an issue — don't report it.
- The speaker column is the name before 「 in the JP (`-` = narration, or a name the box shows elsewhere).
- Dev lines (「1B0のフラグが立っていません…」 guards, test menus) are never seen by players: skip them.
- Keep the report short: every Critical and Important, at most 15 Minors (the clearest ones).

## Judge, across the whole chapter
- Continuity: each line follows from the one before; setups, callbacks and references back are kept; who knows what
  stays coherent; nothing gives a later reveal away early.
- Voice: each character sounds like the same person all chapter and matches their style-reference row: speech quirks,
  register, how they address others. Name the line where a voice drifts or goes neutral.
- Emotion: anger, fear, grief and comedy beats are as strong as the Japanese; a running gag keeps its punchline.
- Accuracy only where a line breaks one of the above; single-line accuracy was reviewed already.

## Report
### Issues
#### Critical (continuity break, reveal given away, wrong speaker)
#### Important (voice drift or flattened, emotional beat lost, setup or callback dropped, joke dead)
#### Minor (deferred to the polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
`ok` (no Critical/Important) | `issue` - one sentence why. The controller writes this word into the chapter's verdict.
