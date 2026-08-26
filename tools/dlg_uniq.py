"""Emit the unique outstanding strings of a dialogue file as an exact
JSON skeleton, so value-keyed override keys always match byte for byte."""
import json, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = os.path.dirname(os.path.abspath(__file__))
todo = json.load(open(os.path.join(W, 'dlg_todo.json'), encoding='utf-8'))
name = sys.argv[1].lower()
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
count = int(sys.argv[3]) if len(sys.argv) > 3 else 100000
seen, order = set(), []
for k, v in todo.get(name, []):
    if v not in seen:
        seen.add(v)
        order.append(v)
sel = order[start:start + count]
print('# %s: %d unique, showing %d..%d' % (name, len(order), start, start + len(sel)))
for v in sel:
    print('  %s: "",' % json.dumps(v, ensure_ascii=False))
