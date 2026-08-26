import json, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = os.path.dirname(os.path.abspath(__file__))
todo = json.load(open(os.path.join(W, 'todo.json'), encoding='utf-8'))
name = sys.argv[1]
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
count = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
items = todo.get(name, [])
print(f'# {name}: {len(items)} outstanding (showing {start}..{min(start+count,len(items))})')
for k, v in items[start:start + count]:
    print(f'{k}\t{v}')
