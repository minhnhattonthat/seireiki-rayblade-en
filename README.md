# Seireiki Rayblade English translation

Unofficial English fan translation of **Seireiki Rayblade** (聖霊機ライブレード; PlayStation, Banpresto / Winkysoft, 1999;
SLPS-02652): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue and story (all scenes, Private Phase events, endings) | Translated |
| Menus, unit/weapon/ability names, help text, battle messages | Translated |
| Graphics with text (chapter cards, battle labels, map names, name plates, album captions, cut-in lettering, credits roles) | Translated |
| Title logo | Left in Japanese (no official English logo) |
| Staff credits: 7 personal names with no sourced reading | Left in Japanese |
| Developer leftovers never shown in normal play (debug scenario lists, test menus, "event cut dummy" cards) | Left in Japanese |
| Voices, songs | Japanese audio (not subtitled) |

Known issues: some menu labels are shortened to fit fixed-width windows; anything else, see [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched disc

Needs Windows, Python 3.12+ with Pillow, numpy and pytest, [mkpsxiso 2.30](https://github.com/Lameguy64/mkpsxiso/releases)
unpacked to `tools/mkpsxiso/mkpsxiso-2.30-win64/`, and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/seireiki-rayblade-en
cd seireiki-rayblade-en
# copy your dump (Redump "Seireiki Rayblade (Japan)") to rom/; the build refuses any other dump:
#   Seireiki Rayblade (Japan) (Track 1).bin  643,965,840 bytes  SHA-1 cf33a1b9c0d144205a4da0f53b9339a453e9b591
#   Seireiki Rayblade (Japan) (Track 2).bin   32,104,800 bytes  SHA-1 bd1fde88c2b79e3cf8821c969373460d51f3155a
#   Seireiki Rayblade (Japan).cue                    220 bytes  SHA-1 55ff32e9c35108f70d726bf743757149c8e688b1
python -X utf8 tools/build.py                          # -> build/Seireiki Rayblade (English).cue + 2 tracks
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Banpresto / Winkysoft's and is included
only so the translation can be checked against it. Seireiki Rayblade is (c) Banpresto / Winkysoft; this project is not
affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
