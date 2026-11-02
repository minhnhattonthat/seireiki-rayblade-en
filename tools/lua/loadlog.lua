-- Log load requests queued by 0x80022068 (no debugger: polls its ring of 12 x 20-byte entries at 0x800CE3C8 each frame).
--   emu.py <cue> --out DIR --script tools/lua/loadlog.lua [--route ...]
-- Entry: u8 type, u8 0, u16 file, u32 slot, u32 a3, u32 arg5, u32 dest. File ids: docs/re/flow.md.
local mem = PCSX.getMemPtr()
local function u32(a)
  a = a & 0x1FFFFF
  return mem[a] | (mem[a + 1] << 8) | (mem[a + 2] << 16) | (mem[a + 3] << 24)
end
local function u16(a) a = a & 0x1FFFFF; return mem[a] | (mem[a + 1] << 8) end
local last = {}
L.on_frame(function(f)
  for i = 0, 11 do
    local e = 0x800CE3C8 + 20 * i
    local s = string.format("type=%02X file=%d slot=%d a3=%X arg5=%X dest=%08X", mem[e & 0x1FFFFF], u16(e + 2),
      u32(e + 4), u32(e + 8), u32(e + 12), u32(e + 16))
    if last[i] ~= s then
      last[i] = s
      if f > 1 then L.log(string.format("f%d q%d %s", f, i, s)) end
    end
  end
end)
