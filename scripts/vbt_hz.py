#!/usr/bin/env python3
# Usage: python3 vbt_hz.py vbt_original.bin vbt_60hz.bin 60
import struct, sys
src, dst, hz = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = bytearray(open(src, 'rb').read())
assert d[:4] == b'$VBT', 'not a VBT dump'
vbt_size = struct.unpack_from('<H', d, 24)[0]
bdb = struct.unpack_from('<I', d, 28)[0]
p = bdb + struct.unpack_from('<H', d, bdb + 18)[0]
end = bdb + struct.unpack_from('<H', d, bdb + 20)[0]
blocks = {}
while p < end - 3:
    bid, size = d[p], struct.unpack_from('<H', d, p + 1)[0]
    blocks[bid] = p + 3
    p += 3 + size
panel = d[blocks[40]] & 0x7f                 # LFP options: panel_type
e = blocks[58] + 2 + panel * struct.unpack_from('<H', d, blocks[58])[0]  # generic DTD entry
clk, ha, hb, _, _, va, vb = struct.unpack_from('<I6H', d, e)
total = (ha + hb) * (va + vb)
new = round(total * hz / 1000)
print(f'panel {panel}: {ha}x{va}, {clk} kHz = {clk*1000/total:.3f} Hz -> {new} kHz = {new*1000/total:.3f} Hz')
struct.pack_into('<I', d, e, new)
d[26] = 0
d[26] = -sum(d[:vbt_size]) & 0xff            # fix VBT checksum
open(dst, 'wb').write(d)
