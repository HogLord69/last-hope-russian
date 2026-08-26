"""Install Jackal's Russian interface art into Last Hope as loose overrides.

Only text-bearing vanilla UI chrome is copied. Deliberately excluded:
  * combat/diplomat/stealth .frm - premade character PORTRAITS, not text
  * death, helpscrn, iface, pip, intrface.lst - Last Hope ships its own
  * wrldmp*, wm*, wrldspr* - Last Hope has a wholly custom world map
Every file is dimension-checked against the English original before it is
written, so a mismatched graphic can never corrupt the interface.
"""
import os, sys, struct

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dat2 import Dat2

W = os.path.dirname(os.path.abspath(__file__))
SJ = r'C:\Users\adamn\Downloads\Fallout-Story-of-the-Jackal-English\Fallout-Story-of-the-Jackal-English'
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
OUT = os.path.join(LH, 'data', 'art', 'intrface')

INCLUDE = """
about aggdn aggoff aggup berdn beroff berup cowdn cowoff cowup cusdn cusoff
cusup custom defdn defoff defup distdn distup chadn chaup chemdn chemup
attackdn attackup burst burstdn burstup called bullseye single reload swing
throw thrust punch kick use useon uset unarmed weapdn weapup movemult
chopuch cm_hookk cm_hymkr cm_jab cm_plmst cm_prckk cm_pstrk cm_pwkck dblossk
dragpuch forcpuch hampnch hipk jumpk lignpuch roundk skick snapkick spunch
automap barter control edtrcrte edtredt loot trade review invbox skldxbox
lscover pickchar months
autodwn autoup di_done1 di_done2 di_talk di_talkp endcmbtd endcmbtu endturnd
endturnu invbutdn invbutup invmadn invmaup mapdn mapup pipdn pipup rundn runup
el_base1 el_bos el_mast2 el_mil1
""".split()


def dims(b):
    """(width, height, frames-per-direction) of an FRM's first frame."""
    fpd = struct.unpack('>H', b[8:10])[0]
    off = 10 + 12 + 12
    fo = struct.unpack('>6I', b[off:off + 24])[0]
    base = off + 24 + 4 + fo
    w, h = struct.unpack('>HH', b[base:base + 4])
    return w, h, fpd


sj = Dat2(os.path.join(SJ, 'master.dat'))
lh = Dat2(os.path.join(LH, 'master.dat'))

loose = {f.lower() for f in os.listdir(OUT)} if os.path.isdir(OUT) else set()

copied, skipped, bad = [], [], []
for name in INCLUDE:
    key = 'art/intrface/%s.frm' % name
    if key not in sj.entries or key not in lh.entries:
        skipped.append((name, 'not in both archives'))
        continue
    if (name + '.frm') in loose:
        skipped.append((name, 'Last Hope ships its own loose file'))
        continue
    a, b = sj.read(key), lh.read(key)
    if a == b:
        skipped.append((name, 'identical - nothing to localise'))
        continue
    try:
        da, db = dims(a), dims(b)
    except Exception as e:
        bad.append((name, 'unreadable: %s' % e))
        continue
    if da != db:
        bad.append((name, 'dimension mismatch %s vs %s' % (da, db)))
        continue
    with open(os.path.join(OUT, name + '.frm'), 'wb') as f:
        f.write(a)
    copied.append((name, da))

print(f'copied  : {len(copied)}')
print(f'skipped : {len(skipped)}')
print(f'rejected: {len(bad)}')
for n, r in skipped:
    print(f'  skip {n:<12} {r}')
for n, r in bad:
    print(f'  BAD  {n:<12} {r}')
