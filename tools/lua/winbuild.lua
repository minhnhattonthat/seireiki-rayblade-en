-- Log every call of the window-layout builder 0x800314B8 (a0..a3, 5th arg = layout stream pointer, caller ra).
--   emu.py ... --debugger --script tools/lua/winbuild.lua
local mem = require("ffi").cast("uint8_t*", PCSX.getMemPtr())
local function u32(a) a = a & 0x1FFFFF; return mem[a] | mem[a + 1] << 8 | mem[a + 2] << 16 | mem[a + 3] << 24 end
L.on_exec(0x800314B8, function()
  local r = PCSX.getRegisters().GPR.n
  local p = u32(r.sp + 0x10)
  local b = {}
  for i = 0, 47 do b[#b + 1] = string.format("%02X", mem[(p + i) & 0x1FFFFF]) end
  L.log(string.format("f%d ra=%08X a0=%X a1=%X a2=%X a3=%X lay=%08X %s", L.frame, r.ra, r.a0, r.a1, r.a2, r.a3, p,
    table.concat(b, " ")))
end)
