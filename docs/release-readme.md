Seireiki Rayblade (PlayStation) - English translation patch v{version}
=====================================================================

Unofficial fan translation of Seireiki Rayblade (聖霊機ライブレード; Banpresto / Winkysoft, 1999; SLPS-02652) into English.
This zip holds only a patch. You need your own dump of the Japanese disc; no game data is included, and
pre-patched images must not be shared.

Base disc (Redump "Seireiki Rayblade (Japan)", http://redump.org/disc/ - search "Seireiki Rayblade")
-----------------------------------------------------------------------------------------------------
  Seireiki Rayblade (Japan) (Track 1).bin   {orig_size} bytes   CRC32 {orig_crc}   SHA-1 {orig_sha1}
  Seireiki Rayblade (Japan) (Track 2).bin   unchanged (audio)                   SHA-1 {track2_sha1}

Patched Track 1: {new_size} bytes, CRC32 {new_crc}, SHA-1 {new_sha1}

How to patch
------------
1. Apply {patch} to "Seireiki Rayblade (Japan) (Track 1).bin" with xdelta3 or Delta Patcher
   (https://github.com/marco-calautti/DeltaPatcher):
       xdelta3 -d -s "Seireiki Rayblade (Japan) (Track 1).bin" {patch} "Track 1 (English).bin"
2. Keep Track 2 and the .cue as they are. Either rename the patched file to the Track 1 name the .cue lists
   (after moving the original away), or edit the .cue's first FILE line to the new name.
3. Load the .cue in your emulator.

Tested in PCSX-Redux (SCPH-5500 BIOS). Start from a cold boot (a fresh power-on), not from a savestate made
with the Japanese disc: states keep the old script in memory and will show garbage or hang. Saves on a memory
card carry over.

Translation status
------------------
  Dialogue and story (all scenes, Private Phase events, endings)   Translated
  Menus, unit/weapon/ability names, help text, battle messages     Translated
  Graphics with text (chapter cards, battle labels, map names,
    name plates, album captions, cut-in lettering, credits roles)  Translated
  Title logo                                                        Left in Japanese (no official English logo)
  Staff credits: 7 personal names with no sourced reading           Left in Japanese
  Developer leftovers never shown in normal play (debug scenario
    lists, test menus, "event cut dummy" cards)                     Left in Japanese
  Voices, songs                                                     Japanese audio (not subtitled)

Known issues
------------
Some menu labels are shortened to fit fixed-width windows. Report anything else (untranslated text, overflow,
typos, hangs) on the project's issue page; a savestate helps most.

Credits
-------
Translation, tools and patch: minhnhattonthat. This translation was made with extensive AI assistance (Claude by
Anthropic). Seireiki Rayblade is (c) Banpresto / Winkysoft; this project is not affiliated with them.
