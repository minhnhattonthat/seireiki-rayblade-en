-- Log one line per completed VM instruction: opcode, sub-op byte, advance.
-- Hooks the interpreter's "base += pc" store (0x8005826C). Needs --debugger on PCSX-Redux.
local mem = PCSX.getMemPtr()
local function u32(a) a = a & 0x1FFFFF; return mem[a] | (mem[a+1] << 8) | (mem[a+2] << 16) | (mem[a+3] << 24) end
local function u16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a+1] << 8) end
L.on_exec(0x8005826C, function()
  local base = u32(0x800CD5B0)
  local adv = u32(0x800CD5B8)
  local op = mem[0x800CD5C4 & 0x1FFFFF]
  local sub = mem[0x800CD5C5 & 0x1FFFFF]
  if base >= 0x800D0000 and base < 0x800E0000 then
    L.log(string.format("OP %05X %02X %02X %d", base - 0x800DCE00, op, sub, adv))
  else
    L.log(string.format("OP ext %08X %02X %02X %d", base, op, sub, adv))
  end
end)
