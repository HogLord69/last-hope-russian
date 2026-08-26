"""Lint hand-written dialogue overrides.

Catches the failure modes that actually happen when writing bulk Russian:
  * stray characters from another script (CJK etc.) slipping into a word
  * Latin letters left inside an otherwise Cyrillic sentence
  * anything that cannot be stored as CP1251
"""
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = os.path.dirname(os.path.abspath(__file__))
OVR = os.path.join(W, 'dlg_overrides')

CYR = re.compile('[' + chr(0x400) + '-' + chr(0x4FF) + ']')
LATIN_RUN = re.compile(r'[A-Za-z]{2,}')

# Latin kept on purpose inside Russian dialogue
ALLOW = {'gv', 'umb', 'mrc', 'wp', 'form', 'ahs', 'ok', 'mkii', 'mk',
    # facility name and literal terminal codes the player must type
    'wt', 'pf', 'kl', 'ax',
    # engine substitution tokens - replaced at runtime, must stay Latin
    'mm', 'cn', 'ca', 'cd', 'mn', 'nn', 'ps', 'pf', 'pm',
    'jhp', 'ap', 'fmj',   # ammunition designations
    # security-terminal strings the player reads off the screen and types back
    'ocp', 'ax9hoojkn', 'adfty78xc', 'ax8hyt334',
    'dztdbhvnj', 'zdtdjhhvb', 'hvbzdtdjt',
}


def ok_char(ch):
    o = ord(ch)
    return (o < 0x250) or (0x400 <= o <= 0x4FF) or (0x2010 <= o <= 0x203A)


def pairs(data, prefix=''):
    """Yield (label, text) from both flat and _bulk (nested) override files."""
    for k, v in data.items():
        if isinstance(v, str):
            yield prefix + str(k), v
        elif isinstance(v, dict):
            yield from pairs(v, prefix + str(k) + ':')


issues = 0
for fn in sorted(os.listdir(OVR)):
    if not fn.endswith('.json'):
        continue
    data = json.load(open(os.path.join(OVR, fn), encoding='utf-8'))
    for k, v in pairs(data):
        stray = {c for c in v if not ok_char(c)}
        if stray:
            print(f'[{fn}] {k}: STRAY {stray}')
            print(f'     {v[:100]}')
            issues += 1
            continue
        try:
            v.encode('cp1251')
        except UnicodeEncodeError as e:
            print(f'[{fn}] {k}: NOT CP1251 -> {e}')
            issues += 1
            continue
        if CYR.search(v):
            words = [w for w in LATIN_RUN.findall(v) if w.lower() not in ALLOW]
            if words:
                print(f'[{fn}] {k}: LATIN {words}')
                print(f'     {v[:100]}')
                issues += 1

print(f'\n{issues} issue(s)')
