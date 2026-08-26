"""Show Jackal EN + RU for given ids, alongside Last Hope EN, to keep glossary consistent."""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import msg

W = os.path.dirname(os.path.abspath(__file__))
SJRES = r'C:\Users\adamn\Downloads\The Story of the Jackal_Resource'
LH_LOOSE = os.path.join(W, 'lh_loose_en')
LH_DAT = os.path.join(W, 'lh_dat', 'text', 'english', 'game')
SJ_RU_DAT = os.path.join(W, 'sj_dat', 'text', 'english', 'game')
SJ_RU_LOOSE = os.path.join(SJRES, 'MAIN', 'DATA', 'TEXT', 'ENGLISH', 'GAME')
SJ_EN = os.path.join(SJRES, 'Components', 'US', 'DATA', 'TEXT', 'ENGLISH', 'GAME')


def layered(name, *dirs):
    d = {}
    for dd in dirs:
        p = msg.find(dd, name)
        if p:
            d.update(msg.as_dict(p))
    return d


name = sys.argv[1]
lh = layered(name, LH_DAT, LH_LOOSE)
ru = layered(name, SJ_RU_DAT, SJ_RU_LOOSE)
en = layered(name, SJ_EN)
ids = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else sorted(ru)
for i in ids:
    print(f'--- {i} ---')
    print('  LH EN:', lh.get(i))
    print('  SJ EN:', en.get(i))
    print('  SJ RU:', ru.get(i))
