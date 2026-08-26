import json, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = os.path.dirname(os.path.abspath(__file__))
todo = json.load(open(os.path.join(W, 'dlg_todo.json'), encoding='utf-8'))

if len(sys.argv) > 1 and sys.argv[1] == '--list':
    loose = {f.lower() for f in os.listdir(os.path.join(W, 'lh_dlg_en'))}
    rows = [(n, len(v), sum(len(x) for _, x in v), n in loose)
            for n, v in todo.items()]
    rows.sort(key=lambda r: -r[2])
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    for n, c, ch, own in rows[:lim]:
        print(f'{n:<20} {c:>5} strings {ch:>7} chars {"OWN" if own else "vanilla"}')
    print(f'... {len(rows)} files total')
else:
    for name in sys.argv[1:]:
        items = todo.get(name.lower(), [])
        print(f'### {name}: {len(items)}')
        for k, v in items:
            print(f'{k}\t{v}')
