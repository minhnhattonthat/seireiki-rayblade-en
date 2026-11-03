-- Log the system-VM op that opens a window (handler 0x80071FCC): VM pc (state 0x800CD570+0x40), op bytes +0x54..
-- and the variable bytes it may read (0x800D1840 + n for args >= 0xF0).
--   emu.py ... --debugger --script tools/lua/winop.lua
local mem = require("ffi").cast("uint8_t*", PCSX.getMemPtr())
local function u32(a) a = a & 0x1FFFFF; return mem[a] | mem[a + 1] << 8 | mem[a + 2] << 16 | mem[a + 3] << 24 end
local function hex(a, n)
  local b = {}
  for i = 0, n - 1 do b[#b + 1] = string.format("%02X", mem[(a + i) & 0x1FFFFF]) end
  return table.concat(b, " ")
end
L.on_exec(0x80071FCC, function()
  L.log(string.format("f%d vmpc=%08X op=%s vars=%s", L.frame, u32(0x800CD5B0), hex(0x800CD5C4, 8),
    hex(0x800D1840, 16)))
end)
