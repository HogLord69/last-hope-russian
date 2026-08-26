"""Measure the dialogue translation job precisely."""
import os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msg

W = os.path.dirname(os.path.abspath(__file__))
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
SJRES = r'C:\Users\adamn\Downloads\The Story of the Jackal_Resource'

LH_LOOSE = os.path.join(LH, 'data', 'text', 'english', 'dialog')
LH_DAT = os.path.join(W, 'lh_dlg', 'text', 'english', 'dialog')
SJ_RU_DAT = os.path.join(W, 'sj_dlg', 'text', 'english', 'dialog')
SJ_RU_LOOSE = os.path.join(SJRES, 'MAIN', 'DATA', 'TEXT', 'ENGLISH', 'DIALOG')
SJ_EN = os.path.join(SJRES, 'Components', 'US', 'DATA', 'TEXT', 'ENGLISH', 'DIALOG')

LAT = re.compile(r'[A-Za-z]')
CYR = re.compile('[' + chr(0x400) + '-' + chr(0x4FF) + ']')


def stats(d):
    n = c = 0
    for f in os.listdir(d):
        if not f.lower().endswith('.msg'):
            continue
        for e in msg.parse(os.path.join(d, f)):
            if e[0] == 'msg' and LAT.search(e[3] or ''):
                n += 1
                c += len(e[3])
    return n, c


def names(d):
    return {f.lower() for f in os.listdir(d) if f.lower().endswith('.msg')}


loose = names(LH_LOOSE)
dat = names(LH_DAT)
sj_ru = names(SJ_RU_DAT) | names(SJ_RU_LOOSE)
sj_en = names(SJ_EN)

print('Last Hope dialogue files')
print(f'  loose (mod content) : {len(loose)}')
print(f'  master.dat (vanilla): {len(dat)}')
print(f'  loose also in dat   : {len(loose & dat)}')
print(f'  total distinct      : {len(loose | dat)}')
print()
print('Jackal Russian dialogue available')
print(f'  RU files            : {len(sj_ru)}')
print(f'  EN overlay files    : {len(sj_en)}')
print(f'  RU overlapping LH   : {len((loose | dat) & sj_ru)}')
print()
n, c = stats(LH_LOOSE)
print(f'loose strings with Latin : {n:>7}   chars {c:>9,}')
n2, c2 = stats(LH_DAT)
print(f'dat   strings with Latin : {n2:>7}   chars {c2:>9,}')
