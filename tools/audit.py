"""Final audit: what English is still visible in the shipped UI text?"""
import os, re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msg

LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
GAME = os.path.join(LH, 'data', 'text', 'english', 'game')

CYR = re.compile('[' + chr(0x400) + '-' + chr(0x4FF) + ']')
WORD = re.compile(r'[A-Za-z]{3,}')

# Latin kept deliberately: engine tokens, filenames, model/brand designations
KEEP = re.compile(
    r'^(error:Map Name|BLANK\.GCD|normal_dam|ERROR\.UNIMPED!|\*\*END-[A-Z]+\*\*|x|X)$')

total = cyr = latin_only = 0
offenders = collections.Counter()
examples = {}

for fn in sorted(os.listdir(GAME)):
    if not fn.lower().endswith('.msg'):
        continue
    for e in msg.parse(os.path.join(GAME, fn)):
        if e[0] != 'msg':
            continue
        v = (e[3] or '').strip()
        if not v:
            continue
        total += 1
        if CYR.search(v):
            cyr += 1
            continue
        if KEEP.match(v) or not WORD.search(v):
            continue
        latin_only += 1
        offenders[fn] += 1
        examples.setdefault(fn, []).append(f'{e[1]}: {v[:70]}')

print(f'total non-empty strings : {total}')
print(f'contain Cyrillic        : {cyr}  ({cyr*100//max(total,1)}%)')
print(f'English-only remaining  : {latin_only}')
if offenders:
    print('\nby file:')
    for fn, n in offenders.most_common():
        print(f'  {fn:<18} {n}')
        for ex in examples[fn][:4]:
            print(f'      {ex}')
