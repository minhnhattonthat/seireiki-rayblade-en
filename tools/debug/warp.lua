-- Warp: New Game starts D_SCE scene SCENE instead of scene 1 (cold boot or a title state + the boot route).
--   emu.py <cue> --out DIR --route tools/routes/boot.txt --script tools/debug/warp.lua --var SCENE=103
--          [--var "FLAGS={0x1B0}"] [--var EP=2] [--var "POKE={{0x800CDC8A,6}}"]
--   By name: python -X utf8 tools/debug/warp.py <name> (scene list: tools/debug/scenes.tsv; notes: docs/re/flow.md).
-- How: the resident system script (EXE, RAM 0x80010374) ends its New Game branch with `0B 01 00` (VM op 0B = goto
-- scene u16) at 0x80010620; we rewrite the operand once the EXE is in RAM. When the VM picks up the new scene
-- (scene id u16 0x800CDC86 == SCENE) we apply: FLAGS (story-flag bits, array at 0x800CDA84, flag n = byte n>>3,
-- mask 1<<(n&7)), EP (episode number byte 0x800CDC8B, shown on chapter cards; chapter-start scenes add 1 to it
-- themselves), POKE ({addr, byte} pairs), and log `WARP scene=N`.
local mem = PCSX.getMemPtr()
local OP = 0x10620  -- 0x80010620 & 0x1FFFFF
-- SCENE=-1: New Game falls through into the next resident sub-script (5 = intermission) via `01 02 00` (op 01 =
-- relative jump: next op = this op + 2 + 1); the other settings then apply on the first frame after the patch.
local scene = assert(SCENE, "set --var SCENE=<D_SCE slot or -1>")
local patched, reported = false, false
local last_base, seen_op, stop_at
L.on_frame(function(f)
  if not patched and mem[OP] == 0x0B and mem[OP + 1] == 0x01 and mem[OP + 2] == 0x00 then
    if scene < 0 then
      mem[OP], mem[OP + 1], mem[OP + 2] = 0x01, 0x02, 0x00
      scene = mem[0xCDC86] | (mem[0xCDC87] << 8)  -- unchanged: report on the next frame
    else
      mem[OP + 1] = scene & 0xFF
      mem[OP + 2] = scene >> 8
    end
    patched = true
    L.log(string.format("f%d patched New Game -> scene %d", f, scene))
  end
  if patched and not reported and (mem[0xCDC86] | (mem[0xCDC87] << 8)) == scene then
    reported = true
    for _, n in ipairs(FLAGS or {}) do mem[0xCDA84 + (n >> 3)] = mem[0xCDA84 + (n >> 3)] | (1 << (n & 7)) end
    if EP then mem[0xCDC8B] = EP end
    for _, p in ipairs(POKE or {}) do mem[p[1] & 0x1FFFFF] = p[2] end
    L.log(string.format("f%d WARP scene=%d", f, scene))
  end
  -- STOP_OP: end the run STOP_AFTER frames after the VM starts its STOP_N-th op STOP_OP in the warped scene
  -- (0x8C = chapter card start, 0x78 = text box, 0x43 = battle player phase): shot final.png, --state-out, quit 0.
  -- (SCENE=-1 reports at the patch, before New Game's init op 10: FLAGS/EP set there may be cleared again.)
  if reported and STOP_OP then
    local base = mem[0xCD5B0] | (mem[0xCD5B1] << 8) | (mem[0xCD5B2] << 16)
    if base ~= last_base and mem[0xCD5C4] == STOP_OP and not stop_at then
      seen_op = (seen_op or 0) + 1
      if seen_op >= (STOP_N or 1) then
        stop_at = f + (STOP_AFTER or 60)
        if TITLE then mem[0xCDC89] = TITLE end  -- chapter-card title id, read when the card is drawn (after op 8C)
        L.log(string.format("f%d STOP op %02X (#%d)", f, STOP_OP, seen_op))
      end
    end
    last_base = base
    if stop_at and f >= stop_at and POST then  -- POST: route-str steps ("6 cross;60 -") played after the stop point
      MASH = nil  -- the driver reads this global each frame; the route queue must be empty here (warp.py: --frames)
      for step in POST:gmatch("[^;]+") do
        local n, b = step:match("^%s*(%d+)%s+(%S+)")
        L.press(b, tonumber(n))
        stop_at = stop_at + tonumber(n)
      end
      POST = nil
    end
    if stop_at and f >= stop_at then
      L.shot("final.png")
      L.log("final frame " .. f)
      if STATE_OUT then L.save_state(STATE_OUT) end
      L.finish(0)
    end
  end
end)
