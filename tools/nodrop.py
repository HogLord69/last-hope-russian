"""Prove no message id was lost: every id in the English source must exist
in the shipped Russian file. Counts ids with a permissive scan that does not
depend on the parser used to build the files."""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = os.path.dirname(os.path.abspath(__file__))
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
OUT = os.path.join(LH, 'data', 'text', 'english', 'game')
SRC_LOOSE = os.path.join(W, 'lh_loose_en')
SRC_DAT = os.path.join(W, 'lh_dat', 'text', 'english', 'game')

# permissive: any {digits} at line start begins a message
ID = re.compile(r'^\s*\{(\d+)\}', re.M)


def ids(path):
    d = open(path, 'rb').read().decode('cp1251', errors='replace')
    return set(int(m) for m in ID.findall(d))


def find(d, n):
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        if f.lower() == n.lower():
            return os.path.join(d, f)
    return None


problems = 0
for fn in sorted(os.listdir(OUT)):
    if not fn.lower().endswith('.msg'):
        continue
    src = set()
    for d in (SRC_DAT, SRC_LOOSE):
        p = find(d, fn)
        if p:
            src |= ids(p)
    if not src:
        continue
    got = ids(os.path.join(OUT, fn))
    lost = src - got
    if lost:
        print(f'{fn:<18} LOST {len(lost)} ids e.g. {sorted(lost)[:8]}')
        problems += 1
    else:
        extra = len(got - src)
        print(f'{fn:<18} ok  src={len(src):<5} out={len(got):<5}' +
              (f' (+{extra} new)' if extra else ''))

print('\n%d file(s) with lost ids' % problems)
