-- Log the scenario VM each frame it changes: scene (0x800CDC86), base (+0x40), pc (+0x48), op state (+0x4C), op (+0x54).
--   emu.py <cue> --out DIR --script tools/lua/vmtrace.lua [--var VM_FROM=200]
local mem = PCSX.getMemPtr()
local function u32(a) return mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24) end
local last
L.on_frame(function(f)
  if f < (VM_FROM or 0) then return end
  local s = string.format("scene=%d base=%08X pc=%04X st=%d op=%02X %02X%02X%02X%02X", mem[0xCDC86] | (mem[0xCDC87] << 8),
    u32(0xCD5B0), u32(0xCD5B8), mem[0xCD5BC], mem[0xCD5C4], mem[0xCD5C5], mem[0xCD5C6], mem[0xCD5C7], mem[0xCD5C8])
  if s ~= last then last = s; L.log("f" .. f .. " " .. s) end
end)
