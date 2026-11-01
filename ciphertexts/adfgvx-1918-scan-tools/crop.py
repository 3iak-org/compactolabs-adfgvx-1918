"""Crop a region of a scan page to PNG, for viewing.

usage: crop.py PDF PAGE OUT.png [x0 y0 x1 y1] [--scale S]
Coordinates are fractions of the page (0..1) or pixels at 300 dpi (>1).
The page is rendered by mutool at 300 dpi (the scan's native resolution) into a
grey PGM cache under $TMPDIR/pgm. No PIL needed: PNG is written with zlib.
"""
import os, sys, subprocess, zlib, struct
import numpy as np

def page_array(pdf, page):
    cache = os.path.join(os.environ.get("TMPDIR", "/tmp"), "pgm")
    os.makedirs(cache, exist_ok=True)
    f = os.path.join(cache, f"p{page:03d}.pgm")
    if not os.path.exists(f):
        subprocess.run(["mutool", "draw", "-q", "-r", "300", "-c", "gray", "-o", f, pdf, str(page)],
                       check=True, stderr=subprocess.DEVNULL)
    data = open(f, "rb").read()
    # P5 header: magic, w, h, maxval
    parts = data.split(maxsplit=4)
    w, h = int(parts[1]), int(parts[2])
    return np.frombuffer(parts[4][-w * h:], dtype=np.uint8).reshape(h, w)

def write_png(path, a):
    h, w = a.shape
    raw = b"".join(b"\x00" + a[i].tobytes() for i in range(h))
    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b"")
    open(path, "wb").write(png)

def main():
    args = sys.argv[1:]
    scale = 1.0
    if "--scale" in args:
        i = args.index("--scale"); scale = float(args[i + 1]); del args[i:i + 2]
    pdf, page, out = args[0], int(args[1]), args[2]
    a = page_array(pdf, page)
    h, w = a.shape
    if len(args) >= 7:
        c = [float(v) for v in args[3:7]]
        x0, y0, x1, y1 = [int(v * (w if j % 2 == 0 else h)) if v <= 1 else int(v) for j, v in enumerate(c)]
        a = a[y0:y1, x0:x1]
    if scale != 1.0:
        hh, ww = a.shape
        yi = (np.arange(int(hh * scale)) / scale).astype(int)
        xi = (np.arange(int(ww * scale)) / scale).astype(int)
        a = a[yi][:, xi]
    write_png(out, np.ascontiguousarray(a))
    print(out, a.shape)

if __name__ == "__main__":
    main()
