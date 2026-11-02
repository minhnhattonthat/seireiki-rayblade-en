# Seireiki Rayblade (PS1) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md; `python tools/skill.py` prints it). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 tools/build.py`  -> `build/Seireiki Rayblade (English).cue` + 2 tracks (checks `rom.sha1` first; ~3 s; identity test `tests/test_build.py`)
- Extract:  `python -X utf8 tools/extract.py dump [--force]` -> `script/` (roundtrip + coverage: `extract.py check`)
- Check:    `python -X utf8 tools/check.py`  (tests + extraction + lint; pre-commit hook runs it; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py "rom/Seireiki Rayblade (Japan).cue" --out work/qa/smoke --route tools/routes/boot.txt --smoke` (swap in the built .cue)
- Warp:     `python -X utf8 tools/debug/warp.py <name> [--title] [--cue build/x.cue]` (`--list`; `--all` regens states + shots in work/qa/warp; raw: `--script tools/debug/warp.lua --var SCENE=<D_SCE slot>`; never ask the user to play to a scene). Flow notes: `docs/re/flow.md`
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user) (not written yet)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original disc: `rom/Seireiki Rayblade (Japan).cue` + Track 1 (MODE2 data) + Track 2 (audio) (gitignored; SHA-1s in `rom.sha1`, checked by `tools/check_rom.py`).
- Emulator: PCSX-Redux nightly 30168.20261102.2 x64 in `tools/pcsx/` (`fetch_emu.py pcsx`, distrib.app manifest dev-win-x64; gitignored). BIOS: `tools/bios/scph5500.bin` (`fetch_emu.py psx-bios`, used automatically). Savestates: `work/states/`.
- Text: `script/`. Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the `.claude/agents/` types (translator, reviewer, visual-qa, playtester), never general-purpose.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Japanese game: confirm = circle, cancel = cross (`--mash-key circle`). Boot to title takes ~5400 frames (logos + intro FMV, not skippable).

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
