"""Verify the shipped dialogue.

Engine semantics: a loose data/ file REPLACES the archive file entirely, it
is not merged id-by-id. So the correct source for each file is the loose
English if Last Hope shipped one, otherwise the archive version.
"""
import os, re, sys, io, struct
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msg

W = os.path.dirname(os.path.abspath(__file__))
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
OUT = os.path.join(LH, 'data', 'text', 'english', 'dialog')
DAT = os.path.join(W, 'lh_dlg', 'text', 'english', 'dialog')
LOOSE = os.path.join(W, 'lh_dlg_en')

ID = re.compile(r'^\s*\{(\d+)\}', re.M)
LAT = re.compile(r'[A-Za-z]')
CYR = re.compile('[' + chr(0x400) + '-' + chr(0x4FF) + ']')


def find(d, n):
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        if f.lower() == n.lower():
            return os.path.join(d, f)
    return None


def ids(p):
    return set(int(x) for x in ID.findall(
        open(p, 'rb').read().decode('cp1251', errors='replace')))


def glyph_widths(path):
    d = open(path, 'rb').read()
    if d[:4] != b'AAFF':
        return None
    return [struct.unpack('>HHI', d[12 + i * 8:20 + i * 8])[0] for i in range(256)]


fonts = {f: glyph_widths(os.path.join(LH, 'data', f))
         for f in os.listdir(os.path.join(LH, 'data')) if f.endswith('.aaf')}
fonts = {k: v for k, v in fonts.items() if v}

lost = badenc = 0
tot = ru = en = 0
missing_glyph = {}
files = 0

for f in sorted(os.listdir(OUT)):
    if not f.lower().endswith('.msg'):
        continue
    files += 1
    src = find(LOOSE, f) or find(DAT, f)
    p = os.path.join(OUT, f)
    if src:
        miss = ids(src) - ids(p)
        if miss:
            print(f'  LOST {f}: {sorted(miss)[:6]}')
            lost += 1
    try:
        raw = open(p, 'rb').read().decode('cp1251')
    except Exception as e:
        print('  DECODE', f, e)
        badenc += 1
        continue
    for e in msg.parse(p):
        if e[0] != 'msg':
            continue
        t = e[3] or ''
        if not t.strip():
            continue
        tot += 1
        if CYR.search(t):
            ru += 1
        elif LAT.search(t):
            en += 1
        for ch in t:
            try:
                b = ch.encode('cp1251')[0]
            except UnicodeEncodeError:
                missing_glyph.setdefault('UNENCODABLE ' + ch, 0)
                missing_glyph['UNENCODABLE ' + ch] += 1
                continue
            if b == 0x20:
                continue
            for name, g in fonts.items():
                if g[b] == 0 and b >= 0x80:
                    key = '0x%02X %r' % (b, bytes([b]).decode('cp1251'))
                    missing_glyph[key] = missing_glyph.get(key, 0) + 1

print(f'files                : {files}')
print(f'files with lost ids  : {lost}')
print(f'cp1251 failures      : {badenc}')
print(f'strings              : {tot:,}')
print(f'  Russian            : {ru:,}  ({ru*100//max(tot,1)}%)')
print(f'  still English      : {en:,}')
print(f'high bytes with no glyph: {missing_glyph if missing_glyph else "none"}')
