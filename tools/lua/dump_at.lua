-- Dump VRAM + main RAM + a shot at frame DUMP_AT (and every DUMP_EVERY after, if set).
--   emu.py <cue> --out DIR --route ... --script tools/lua/dump_at.lua --var DUMP_AT=7000 [--var DUMP_EVERY=300]
local at, every = DUMP_AT or 600, DUMP_EVERY
L.on_frame(function(f)
  if f == at or (every and f > at and (f - at) % every == 0) then
    local p = string.format("d%06d", f)
    L.dump_ppu(p); L.dump_ram(p .. ".ram.bin"); L.shot(p .. ".png")
  end
end)
