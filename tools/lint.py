"""Lint my hand-written overrides for leftover English and stray scripts."""
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W = os.path.dirname(os.path.abspath(__file__))
OVR = os.path.join(W, 'overrides')

CYR_LO, CYR_HI = 0x0400, 0x04FF
CYR = re.compile('[' + chr(CYR_LO) + '-' + chr(CYR_HI) + ']')
LATIN_WORD = re.compile(r'\b[A-Za-z]{3,}\b')

# Latin kept on purpose: model designations, filenames, engine tokens
ALLOW = {
    'blank', 'gcd', 'error', 'map', 'name', 'this', 'goes', 'with', 'the',
    'temporary', 'one', 'for', 'descriptions', 'don', 'translate', 'what',
    'unimped', 'normal', 'dam', 'end', 'par', 'disk', 'last', 'hope', 'since',
    'prva', 'umb', 'mrc', 'form', 'chq', 'ahs', 'poseidon', 'oil', 'network',
    'computer', 'quartz', 'nuka', 'cola', 'red', 'wine', 'property', 'duntown',
    'golden', 'lley', 'test', 'and', 'seems', 'proficient',
    # brand / model designations kept in Latin on purpose
    'dogs', 'netcom', 'hpfa', 'fal', 'colt', 'garrett', 'neostead',
    'sterling', 'dks', 'rockwell', 'bigbazooka', 'glock',
}


def is_ok_char(ch):
    o = ord(ch)
    if o < 0x0250:            # ASCII + Latin-1 + Latin Extended-A/B
        return True
    if CYR_LO <= o <= CYR_HI:  # Cyrillic
        return True
    if 0x2010 <= o <= 0x203A:  # general punctuation (dashes, quotes)
        return True
    return False


issues = 0
for fn in sorted(os.listdir(OVR)):
    if not fn.endswith('.json'):
        continue
    data = json.load(open(os.path.join(OVR, fn), encoding='utf-8'))
    for k, v in data.items():
        if not isinstance(v, str):
            continue
        odd = {c for c in v if not is_ok_char(c)}
        if odd:
            print(f'[{fn}] {k[:40]!r}: stray {odd} -> {v[:70]!r}')
            issues += 1
            continue
        if CYR.search(v):
            words = [w for w in LATIN_WORD.findall(v) if w.lower() not in ALLOW]
            if words:
                print(f'[{fn}] {k[:40]!r}: latin {words} -> {v[:70]!r}')
                issues += 1

print(f'\n{issues} issue(s)')
