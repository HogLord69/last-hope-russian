"""Build all Russian dialogue for Last Hope - one idempotent pass.

Covers every dialogue file the engine can reach: Last Hope's own 368 plus the
802 vanilla files it inherits. English is read from pristine snapshots, never
from the live output, so this is safe to re-run.

Per line, in priority order:
  1. dlg_overrides/<file>.json / .values.json   hand-written Russian
  2. RPU Russian                                only when verified safe
  3. Last Hope English                          left as-is, and reported

Engine semantics: a loose file replaces the archive file wholesale, so the
base for each file is Last Hope's loose English when it ships one, else the
vanilla English. Last Hope's own audio field is always preserved.
"""
import os, re, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msg
from build import renderable

W = os.path.dirname(os.path.abspath(__file__))
LH = r'C:\Users\adamn\Downloads\Last Hope mod 1.088'

LOOSE = os.path.join(W, 'lh_dlg_en')                              # LH's own EN
DAT = os.path.join(W, 'lh_dlg', 'text', 'english', 'dialog')      # vanilla EN
RPU = os.path.join(W, 'rpu_dlg', 'text', 'russian', 'dialog')     # vanilla RU
OUT = os.path.join(LH, 'data', 'text', 'english', 'dialog')
OVR = os.path.join(W, 'dlg_overrides')

LAT = re.compile(r'[A-Za-z]')
CYR = re.compile('[' + chr(0x400) + '-' + chr(0x4FF) + ']')

# audio tags disagree -> not the same line of dialogue
SKIP = {('kcsulik.msg', 482), ('kcsulik.msg', 483)}


def find(d, n):
    if not os.path.isdir(d):
        return None
    for f in os.listdir(d):
        if f.lower() == n.lower():
            return os.path.join(d, f)
    return None


def ent(p):
    return {e[1]: (e[2], e[3]) for e in msg.parse(p) if e[0] == 'msg'}


def groups(p):
    """id -> ordered list of texts.

    Vanilla files repeat {000} for extra random variants of the preceding
    line, so an id is not unique. Keeping the occurrences in order lets a
    variant be matched by its position within its own id group.
    """
    g = {}
    if not p:
        return g
    for e in msg.parse(p):
        if e[0] == 'msg':
            g.setdefault(e[1], []).append(e[3])
    return g


def norm(s):
    s = re.sub(r'\s+', ' ', (s or '').replace('\r', ' ')).strip().lower()
    return s.strip(' .!?:;,-*')


def load_bulk():
    """_bulk*.json hold many files at once: {"file.msg": {"id": "russian"}}.

    Writing a few hundred lines across a dozen files in one document is far
    less overhead than a file per conversation.
    """
    out = {}
    for fn in sorted(os.listdir(OVR)):
        if not (fn.startswith('_bulk') and fn.endswith('.json')):
            continue
        data = json.load(open(os.path.join(OVR, fn), encoding='utf-8'))
        for name, ids in data.items():
            d = out.setdefault(name.lower(), {})
            for k, v in ids.items():
                d[int(k)] = v
    return out


def load_global():
    """Lines that recur across many files ([Back.], Thanks., ...), translated once."""
    p = os.path.join(OVR, '_global.values.json')
    if not os.path.exists(p):
        return {}
    return {norm(k): v for k, v in json.load(open(p, encoding='utf-8')).items()}


def load_ovr(name):
    by_id, by_val = {}, {}
    p = os.path.join(OVR, name + '.json')
    if os.path.exists(p):
        by_id = {int(k): v for k, v in json.load(open(p, encoding='utf-8')).items()}
    p = os.path.join(OVR, name + '.values.json')
    if os.path.exists(p):
        by_val = {norm(k): v for k, v in
                  json.load(open(p, encoding='utf-8')).items()}
    return by_id, by_val


def main(only=None):
    os.makedirs(OVR, exist_ok=True)
    loose_n = {f.lower() for f in os.listdir(LOOSE) if f.lower().endswith('.msg')}
    dat_n = {f.lower() for f in os.listdir(DAT) if f.lower().endswith('.msg')}
    rpu_n = {f.lower() for f in os.listdir(RPU) if f.lower().endswith('.msg')}
    allf = sorted(loose_n | dat_n)
    if only:
        allf = [f for f in allf if f in {o.lower() for o in only}]

    glob_val = load_global()
    bulk = load_bulk()
    todo = {}
    n_ovr = n_rpu = n_left = n_plain = 0
    rows = []

    for n in allf:
        overridden = n in loose_n
        src = find(LOOSE, n) if overridden else find(DAT, n)
        van = ent(find(DAT, n)) if n in dat_n else {}
        ru_g = groups(find(RPU, n)) if n in rpu_n else {}
        src_g = groups(src)
        by_id, by_val = load_ovr(n)
        by_id.update(bulk.get(n, {}))   # bulk entries win: they are newer

        seen = {}
        out, left = [], []
        for e in msg.parse(src):
            if e[0] != 'msg':
                out.append(e)
                continue
            k, aud, v = e[1], e[2], e[3]
            # which occurrence of this id are we on?
            ord_ = seen.get(k, 0)
            seen[k] = ord_ + 1
            if k in by_id:
                t = by_id[k]
                n_ovr += 1
            elif norm(v) in by_val:
                t = by_val[norm(v)]
                n_ovr += 1
            else:
                # take the matching occurrence, but only when this id has the
                # same number of variants on both sides - otherwise the
                # variants cannot be paired up reliably
                mine, theirs = src_g.get(k, []), ru_g.get(k, [])
                rv = theirs[ord_] if len(mine) == len(theirs) and ord_ < len(theirs) else None
                ok = rv is not None and CYR.search(rv or '') and (n, k) not in SKIP
                # if Last Hope rewrote the line, RPU translates the stock one
                if ok and overridden and norm(van.get(k, ('', ''))[1]) != norm(v):
                    ok = False
                if ok:
                    t = rv
                    n_rpu += 1
                elif norm(v) in glob_val:
                    # generic recurring line, used only where RPU has nothing:
                    # a professional in-context translation always wins
                    t = glob_val[norm(v)]
                    n_ovr += 1
                else:
                    t = v
                    if LAT.search(v or ''):
                        left.append([k, v])
                        n_left += 1
                    else:
                        n_plain += 1
            raw_id = e[4] if len(e) > 4 else str(k)
            out.append(['msg', k, aud, renderable(t), raw_id])
        msg.dump(out, os.path.join(OUT, n))
        if left:
            todo[n] = left
        rows.append((n, len(left)))

    with open(os.path.join(W, 'dlg_todo.json'), 'w', encoding='utf-8') as f:
        json.dump(todo, f, ensure_ascii=False, indent=1)

    chars = sum(len(v) for l in todo.values() for _, v in l)
    print(f'dialogue files      : {len(allf)}')
    print(f'  hand-written      : {n_ovr:,}')
    print(f'  from RPU Russian  : {n_rpu:,}')
    print(f'  no prose          : {n_plain:,}')
    print(f'  still English     : {n_left:,}  ({chars:,} chars) in {len(todo)} files')
    rows.sort(key=lambda r: -r[1])
    if todo:
        print('\nlargest remaining:')
        for n, c in rows[:18]:
            if c:
                print(f'  {n:<20} {c}')


if __name__ == '__main__':
    main(sys.argv[1:] or None)
