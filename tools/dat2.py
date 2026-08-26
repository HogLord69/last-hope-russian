import struct, sys, zlib, os

BS = chr(92)  # backslash

def norm(n):
    return n.replace(BS, '/').lower()

class Dat2:
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as f:
            f.seek(-8, 2)
            tree_size, data_size = struct.unpack('<II', f.read(8))
            f.seek(-(8 + tree_size), 2)
            tree = f.read(tree_size)
        self.entries = {}
        cnt = struct.unpack('<I', tree[:4])[0]
        off = 4
        for _ in range(cnt):
            nlen = struct.unpack('<I', tree[off:off + 4])[0]
            off += 4
            name = tree[off:off + nlen].decode('cp1251')
            off += nlen
            comp, real_sz, pack_sz, data_off = struct.unpack('<BIII', tree[off:off + 13])
            off += 13
            self.entries[norm(name)] = (comp, real_sz, pack_sz, data_off)

    def read(self, name):
        comp, real_sz, pack_sz, data_off = self.entries[norm(name)]
        with open(self.path, 'rb') as f:
            f.seek(data_off)
            raw = f.read(pack_sz if comp else real_sz)
        return zlib.decompress(raw) if comp else raw

    def list(self, prefix=''):
        p = norm(prefix)
        return sorted(k for k in self.entries if k.startswith(p))


if __name__ == '__main__':
    d = Dat2(sys.argv[1])
    if len(sys.argv) == 2:
        print(len(d.entries), 'entries')
    elif sys.argv[2] == 'ls':
        for k in d.list(sys.argv[3] if len(sys.argv) > 3 else ''):
            print(k)
    elif sys.argv[2] == 'x':
        pref, outdir = sys.argv[3], sys.argv[4]
        n = 0
        for k in d.list(pref):
            dst = os.path.join(outdir, k)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as f:
                f.write(d.read(k))
            n += 1
        print('extracted', n)
