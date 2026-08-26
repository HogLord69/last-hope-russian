# -*- coding: utf-8 -*-
"""Recover RPU translations for lines Last Hope only lightly edited.

dlg_build refuses an RPU line when Last Hope's English differs at all from the
vanilla English, because a rewritten line means a different meaning.  A great
many of those "rewrites" are typo and punctuation fixes ("amoung"->"among",
a missing full stop).  This walks the still-English list and accepts the RPU
line only when the two English texts are near-identical: same digits, same
length to within 12%%, difflib ratio >= 0.93.  Everything else is left alone.
"""
import os, sys, json, re, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dlg_build as B, msg

DIG = re.compile(r'\d+')


def close(a, b):
    if DIG.findall(a) != DIG.findall(b):
        return False
    if not a or not b:
        return False
    if abs(len(a) - len(b)) / max(len(a), len(b)) > 0.12:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.93


def main():
    todo = json.load(open(os.path.join(B.W, 'dlg_todo.json'), encoding='utf-8'))
    rpu_n = {f.lower() for f in os.listdir(B.RPU) if f.lower().endswith('.msg')}
    dat_n = {f.lower() for f in os.listdir(B.DAT) if f.lower().endswith('.msg')}
    out, kept, files = {}, 0, 0
    for n, lines in sorted(todo.items()):
        if n not in rpu_n or n not in dat_n:
            continue
        ru_g = B.groups(B.find(B.RPU, n))
        van = B.ent(B.find(B.DAT, n))
        src = B.find(B.LOOSE, n) if os.path.exists(os.path.join(B.LOOSE, n))             else B.find(B.DAT, n)
        src_g = B.groups(src)
        got = {}
        for k, v in lines:
            if k not in van or len(ru_g.get(k, [])) != 1                     or len(src_g.get(k, [])) != 1:
                continue
            rv = ru_g[k][0]
            if not B.CYR.search(rv) or (n, k) in B.SKIP:
                continue
            if close(B.norm(v), B.norm(van[k][1])):
                got[str(k)] = rv
                kept += 1
        if got:
            out[n] = got
            files += 1
    p = os.path.join(B.OVR, '_bulk_rpufix.json')
    json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'recovered {kept:,} lines in {files} files -> {os.path.basename(p)}')


if __name__ == '__main__':
    main()
