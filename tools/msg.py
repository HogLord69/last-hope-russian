"""Fallout 2 .msg parser/writer preserving order and comments."""
import re, os

# Many .msg lines carry a source comment after the closing brace, e.g.
#   {307}{}{V. Good}   # Abbreviated for character editor
# The trailing text must be tolerated or the whole message is silently lost.
LINE_RE = re.compile(r'^\s*\{(\d+)\}\s*\{([^}]*)\}\s*\{(.*)\}[^{}]*$', re.S)


STARTS = re.compile(r'^\s*\{\d+\}')


def parse(path):
    """Return list of ('msg', id, audio, text) / ('raw', text).

    Messages may wrap across lines, so an unterminated line is buffered.
    A malformed entry must not swallow the rest of the file, so buffering
    is abandoned as soon as a line begins a new {id} message.
    """
    with open(path, 'rb') as f:
        data = f.read()
    txt = data.decode('cp1251', errors='replace')
    out = []
    buf = ''

    def flush():
        nonlocal buf
        if buf:
            out.append(['raw', buf])
            buf = ''

    for ln in txt.split('\n'):
        ln = ln.rstrip('\r')
        if buf and STARTS.match(ln):
            # previous entry never closed; keep it verbatim and resync here
            flush()
        cand = (buf + '\n' + ln) if buf else ln
        m = LINE_RE.match(cand)
        if m:
            out.append(['msg', int(m.group(1)), m.group(2), m.group(3)])
            buf = ''
        elif cand.count('{') > cand.count('}'):
            buf = cand
        else:
            flush()
            out.append(['raw', ln])
    flush()
    return out


def as_dict(path):
    return {e[1]: e[3] for e in parse(path) if e[0] == 'msg'}


def dump(entries, path):
    lines = []
    for e in entries:
        if e[0] == 'msg':
            lines.append('{%d}{%s}{%s}' % (e[1], e[2], e[3]))
        else:
            lines.append(e[1])
    blob = '\r\n'.join(lines)
    with open(path, 'wb') as f:
        f.write(blob.encode('cp1251', errors='replace'))


def find(dirpath, name):
    """Case-insensitive lookup of a file in a directory."""
    if not os.path.isdir(dirpath):
        return None
    for fn in os.listdir(dirpath):
        if fn.lower() == name.lower():
            return os.path.join(dirpath, fn)
    return None
