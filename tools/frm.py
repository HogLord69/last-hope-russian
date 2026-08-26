"""Minimal FRM -> PNG renderer so interface art can be eyeballed."""
import struct, sys, os, zlib

def read_pal(data):
    pal = []
    for i in range(256):
        r, g, b = data[i * 3:i * 3 + 3]
        # Fallout palettes are 6-bit
        pal.append((min(r * 4, 255), min(g * 4, 255), min(b * 4, 255)))
    return pal


def frm_frame0(data):
    ver, fps, af, fpd = struct.unpack('>IHHH', data[:10])
    off = 10 + 12 + 12          # xShift[6], yShift[6]
    frame_offsets = struct.unpack('>6I', data[off:off + 24])
    off += 24
    area = struct.unpack('>I', data[off:off + 4])[0]
    off += 4
    base = off + frame_offsets[0]
    w, h, sz = struct.unpack('>HHI', data[base:base + 8])
    px = data[base + 12:base + 12 + w * h]
    return w, h, px


def png(path, w, h, rgb_rows):
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    raw = b''.join(b'\x00' + r for r in rgb_rows)
    out = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(out)


def render(frm_bytes, pal_bytes, out):
    pal = read_pal(pal_bytes)
    w, h, px = frm_frame0(frm_bytes)
    rows = []
    for y in range(h):
        row = bytearray()
        for x in range(w):
            i = px[y * w + x] if y * w + x < len(px) else 0
            r, g, b = pal[i]
            row += bytes((r, g, b))
        rows.append(bytes(row))
    png(out, w, h, rows)
    return w, h
