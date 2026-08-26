"""Build Russian .msg files for Last Hope.

Sources, in order of trust:
  1. overrides/<file>.json  -- hand-written natural Russian (highest)
  2. Story of the Jackal RU -- used only when Jackal's own EN text matches
                               Last Hope's EN text exactly (verified drop-in)
  3. Last Hope EN           -- left as-is, reported as outstanding
"""
import os, sys, re, json, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msg

W = os.path.dirname(os.path.abspath(__file__))
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'
SJRES = r'C:\Users\adamn\Downloads\The Story of the Jackal_Resource'

# Read English from a pristine snapshot, never from the live output dir,
# so a rebuild can't consume its own Russian output as the source.
LH_LOOSE = os.path.join(W, 'lh_loose_en')
LH_DAT = os.path.join(W, 'lh_dat', 'text', 'english', 'game')
SJ_RU_DAT = os.path.join(W, 'sj_dat', 'text', 'english', 'game')
SJ_RU_LOOSE = os.path.join(SJRES, 'MAIN', 'DATA', 'TEXT', 'ENGLISH', 'GAME')
SJ_EN = os.path.join(SJRES, 'Components', 'US', 'DATA', 'TEXT', 'ENGLISH', 'GAME')
OVR = os.path.join(W, 'overrides')
OUT = os.path.join(LH, 'data', 'text', 'english', 'game')

CYR = re.compile(r'[\u0400-\u04FF]')
LAT = re.compile(r'[A-Za-z]')


def norm(s):
    s = re.sub(r'\s+', ' ', s.replace('\r', ' ').replace('\n', ' ')).strip().lower()
    return s.strip(' .!?:;,-*')


def squash(s):
    """Aggressive form: letters+digits only, for spelling-variant matching."""
    return re.sub(r'[^a-z0-9]', '', norm(s))


DIGITS = re.compile(r'\d+')

# The Cyrillic fonts carry no glyphs for these at the sizes used by the
# character sheet and item descriptions (font2/3/4), so they would render as
# blank gaps. Map each to a form every font can actually draw. Dropping the
# diaeresis on ё is standard practice in Russian Fallout text for this reason.
RENDER_FIX = {
    'ё': 'е',  # ё -> е
    'Ё': 'Е',  # Ё -> Е
    '—': '-',       # em dash
    '–': '-',       # en dash
    '«': '"', '»': '"',
    '“': '"', '”': '"',
    '‘': "'", '’': "'",
    '…': '...',
    ' ': ' ',       # non-breaking space
    '№': 'N',       # №
}
_FIX_RE = re.compile('|'.join(map(re.escape, RENDER_FIX)))


def renderable(s):
    return _FIX_RE.sub(lambda m: RENDER_FIX[m.group()], s) if s else s


def close_enough(a, b):
    """True when Last Hope's EN and Jackal's EN say the same thing.

    Guarded so a changed number or a materially reworded string never
    silently inherits Jackal's Russian:
      - every number must match, in the same order
      - length must be within 15%
      - character-level similarity must be >= 0.90
    """
    if DIGITS.findall(a) != DIGITS.findall(b):
        return False
    sa, sb = squash(a), squash(b)
    if not sa or not sb:
        return False
    if sa == sb:
        return True
    if abs(len(sa) - len(sb)) > 0.15 * max(len(sa), len(sb)):
        return False
    return difflib.SequenceMatcher(None, sa, sb).ratio() >= 0.90


def layered(name, *dirs):
    d = {}
    for dd in dirs:
        p = msg.find(dd, name)
        if p:
            d.update(msg.as_dict(p))
    return d


def audio_of(name, *dirs):
    d = {}
    for dd in dirs:
        p = msg.find(dd, name)
        if p:
            for e in msg.parse(p):
                if e[0] == 'msg':
                    d[e[1]] = e[2]
    return d


def build_index(names):
    """Map normalized Jackal-EN text -> Jackal-RU text.

    Last Hope renumbered many protos/perks, so the same string lives under a
    different id. Matching on text recovers those. An English string that maps
    to more than one distinct Russian rendering is ambiguous and is dropped,
    so context-dependent wording is never guessed at.
    """
    per_file, glob = {}, {}
    for n in names:
        en = layered(n, SJ_EN)
        ru = layered(n, SJ_RU_DAT, SJ_RU_LOOSE)
        local = {}
        for k, v in en.items():
            rv = ru.get(k)
            if not rv or not CYR.search(rv) or not v.strip():
                continue
            key = norm(v)
            if not key:
                continue
            local.setdefault(key, set()).add(rv)
            glob.setdefault(key, set()).add(rv)
        per_file[n] = {k: next(iter(s)) for k, s in local.items() if len(s) == 1}
    return per_file, {k: next(iter(s)) for k, s in glob.items() if len(s) == 1}


def main(only=None):
    names = set()
    for dd in (LH_LOOSE, LH_DAT):
        if os.path.isdir(dd):
            names |= {f.lower() for f in os.listdir(dd) if f.lower().endswith('.msg')}
    if only:
        names &= set(only)

    os.makedirs(OVR, exist_ok=True)
    sj_names = {f.lower() for f in os.listdir(SJ_EN) if f.lower().endswith('.msg')}
    per_file, glob_idx = build_index(sj_names)
    todo, allfuzz, allidx, stats = {}, {}, {}, []

    for n in sorted(names):
        en = layered(n, LH_DAT, LH_LOOSE)
        aud = audio_of(n, LH_DAT, LH_LOOSE)
        ru = layered(n, SJ_RU_DAT, SJ_RU_LOOSE)
        sjen = layered(n, SJ_EN)
        if not en:
            continue

        ovr = {}
        op = os.path.join(OVR, n + '.json')
        if os.path.exists(op):
            with open(op, encoding='utf-8') as f:
                ovr = {int(k): v for k, v in json.load(f).items()}

        # Value-keyed overrides: translate a repeated string once, apply
        # everywhere it occurs in this file. Per-id overrides still win.
        vovr = {}
        vp = os.path.join(OVR, n + '.values.json')
        if os.path.exists(vp):
            with open(vp, encoding='utf-8') as f:
                vovr = {norm(k): v for k, v in json.load(f).items()}

        local_idx = per_file.get(n, {})
        entries, left, fuzzy, viaidx = [], [], [], []
        src = {'ovr': 0, 'sj': 0, 'fuzz': 0, 'idx': 0, 'none': 0, 'na': 0}
        for k in sorted(en):
            v = en[k]
            rv, sv = ru.get(k), sjen.get(k)
            usable = rv and CYR.search(rv) and sv is not None
            key = norm(v)
            if k in ovr:
                out, tag = ovr[k], 'ovr'
            elif key in vovr:
                out, tag = vovr[key], 'ovr'
            elif usable and norm(sv) == norm(v):
                out, tag = rv, 'sj'
            elif usable and close_enough(v, sv):
                out, tag = rv, 'fuzz'
                fuzzy.append([k, v, sv, rv])
            elif key in local_idx:
                out, tag = local_idx[key], 'idx'
                viaidx.append([k, v, out, 'same-file'])
            elif key in glob_idx:
                out, tag = glob_idx[key], 'idx'
                viaidx.append([k, v, out, 'cross-file'])
            elif not LAT.search(v or ''):
                out, tag = v, 'na'
            else:
                out, tag = v, 'none'
                left.append([k, v])
            src[tag] += 1
            entries.append(['msg', k, aud.get(k, ''), renderable(out)])

        # A few vanilla entries are malformed (a missing brace merges two
        # messages). They cannot be parsed as messages, but dropping them
        # would lose text the engine still reads, so carry them over verbatim.
        carried = []
        for d in (LH_DAT, LH_LOOSE):
            p = msg.find(d, n)
            if not p:
                continue
            for e in msg.parse(p):
                if e[0] == 'raw' and '{' in e[1] and e[1] not in carried:
                    carried.append(e[1])
        entries += [['raw', c] for c in carried]

        hdr = [['raw', '# %s -- Russian' % n],
               ['raw', '# UI from Story of the Jackal (RU); mod-specific strings translated.'],
               ['raw', '#']]
        msg.dump(hdr + entries, os.path.join(OUT, n))
        if left:
            todo[n] = left
        if fuzzy:
            allfuzz[n] = fuzzy
        if viaidx:
            allidx[n] = viaidx
        stats.append((n, len(en), src['ovr'], src['sj'] + src['fuzz'],
                      src['idx'], src['none']))

    with open(os.path.join(W, 'todo.json'), 'w', encoding='utf-8') as f:
        json.dump(todo, f, ensure_ascii=False, indent=1)
    with open(os.path.join(W, 'fuzzy.json'), 'w', encoding='utf-8') as f:
        json.dump(allfuzz, f, ensure_ascii=False, indent=1)
    with open(os.path.join(W, 'byindex.json'), 'w', encoding='utf-8') as f:
        json.dump(allidx, f, ensure_ascii=False, indent=1)

    stats.sort(key=lambda r: -r[5])
    print(f'{"file":<18}{"ids":>7}{"mine":>7}{"match":>7}{"byname":>7}{"left":>7}')
    print('-' * 54)
    t = [0, 0, 0, 0, 0]
    for r in stats:
        if r[5] or r[2] or r[4]:
            print(f'{r[0]:<18}{r[1]:>7}{r[2]:>7}{r[3]:>7}{r[4]:>7}{r[5]:>7}')
        for i in range(5):
            t[i] += r[i + 1]
    print('-' * 54)
    print(f'{"TOTAL":<18}{t[0]:>7}{t[1]:>7}{t[2]:>7}{t[3]:>7}{t[4]:>7}')


def install_scrnset():
    """scrnset.msg lives in f2_res.dat, not master.dat, so it is not part of
    the merge above. Jackal's Russian copy is complete, so install it directly."""
    src = os.path.join(SJ_RU_LOOSE, 'scrnset.msg')
    if not os.path.exists(src):
        return
    ents = msg.parse(src)
    for e in ents:
        if e[0] == 'msg':
            e[3] = renderable(e[3])
    msg.dump(ents, os.path.join(OUT, 'scrnset.msg'))
    print('scrnset.msg      installed (%d ids)'
          % len([e for e in ents if e[0] == 'msg']))


if __name__ == '__main__':
    main(sys.argv[1:] or None)
    install_scrnset()
