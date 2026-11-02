# Review-and-fix brief - Seireiki Rayblade

You review translated batches of the JP->English fan translation and fix what is wrong. You did not translate them.
Mechanical validity (ids, codes, speaker names, glossary terms, honorifics, widths) is enforced by
`tools/batches.py check` - judge translation quality. Repo root: `H:\translation\seireiki-rayblade-en`.

## For each batch named in your dispatch
1. `python -X utf8 tools/batches.py pairs <batch>` writes `work/tl/<batch>.pairs.txt` (`>> id | JP` / English).
   Read ALL of it (in passes if large), with `docs/style-reference.md`, `work/tl/<batch>.terms.txt`, the glossary
   Style rules and, once, `docs/synopsis.md`. The translator's `work/tl/<batch>.report.txt` holds unverified claims.
2. Judge:
   - Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and
     say what it means.
   - Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics stable;
     a recurring phrase rendered the same way within the batch.
   - Voice: each speaker against the style reference. Quirks (Yamato's ニャ, Derock's なんだな, Fain's bombast,
     Melvi's third person, old-man ワシ/じゃ), register and emotional intensity must come through, not be
     normalised into neutral prose. Register markers flatten most often.
   - Things players caught that reviewers missed: jokes losing their punch, ordinal suffix after a variable,
     abbreviated names, stock phrases that read awkwardly ("... GET!").
   - Naturalness: would a reader stumble?
3. Fix every Critical and Important finding yourself in `work/tl/<batch>.out.tsv` with your file-edit tool, line by
   line (never a script that rewrites many lines), then run `python -X utf8 tools/batches.py check <batch>` until OK.
   Don't touch lines that are fine; don't "improve" style beyond the findings.
4. Write `work/tl/<batch>.review.txt`:
   ```
   ### Critical (meaning reversed, wrong speaker, broken code grammar)   - each: id - JP gist - problem - fix applied
   ### Important (mistranslation, glossary slip, flattened voice, dead joke) - each: id - JP gist - problem - fix applied
   ### Minor (style; NOT fixed, deferred to the polish pass) - each: id - note - suggested EN
   ### Assessment: Approved after fixes | Approved | Needs translator - one sentence
   ```

Edit nothing but the batches' `.out.tsv` and `.review.txt`/`.pairs.txt`. Reply with only one line:
`reviewed <batches>: <n> critical, <n> important fixed, <n> minor`.
