"""Check built .msg output is renderable: CP1251-encodable and covered by the fonts."""
import os, sys, struct, collections, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msg

W = os.path.dirname(os.path.abspath(__file__))
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
GAME = os.path.join(LH, 'data', 'text', 'english', 'game')


def glyph_widths(path):
    with open(path, 'rb') as f:
        d = f.read()
    if d[:4] != b'AAFF':
        return None
    out, off = [], 12
    for _ in range(256):
        w, h, o = struct.unpack('>HHI', d[off:off + 8])
        off += 8
        out.append(w)
    return out


fonts = {}
for fn in sorted(os.listdir(os.path.join(LH, 'data'))):
    if fn.endswith('.aaf'):
        g = glyph_widths(os.path.join(LH, 'data', fn))
        if g:
            fonts[fn] = g

# space (0x20) is legitimately zero-width in some fonts; never flag it
IGNORE = {0x20}

bad_enc = collections.Counter()
missing = collections.defaultdict(collections.Counter)
used = collections.Counter()

for fn in sorted(os.listdir(GAME)):
    if not fn.lower().endswith('.msg'):
        continue
    for e in msg.parse(os.path.join(GAME, fn)):
        if e[0] != 'msg':
            continue
        for ch in e[3]:
            try:
                b = ch.encode('cp1251')[0]
            except UnicodeEncodeError:
                bad_enc[ch] += 1
                continue
            used[b] += 1
            if b in IGNORE:
                continue
            for name, g in fonts.items():
                if g[b] == 0:
                    missing[b][name] += 1

print('=== characters that cannot be stored as CP1251 ===')
print(dict(bad_enc) if bad_enc else 'none')

print('\n=== CP1251 bytes used that some font cannot draw ===')
if not missing:
    print('none')
for b in sorted(missing):
    ch = bytes([b]).decode('cp1251')
    fl = ', '.join(sorted(missing[b]))
    print(f'  0x{b:02X} {ch!r}  used {used[b]:>6}x  missing in: {fl}')
