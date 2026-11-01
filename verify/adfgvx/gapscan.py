import ctypes, os, numpy as np
import adfgvx as A, german as G
_l = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libgap.so"))
_l.gap_scan.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
def cls_of_square(sq, blank=()):
    """class 0..26 per cell; '?' cells and any cell index in `blank` are unknown (-1)."""
    return np.array([-1 if (ch == "?" or i in blank) else G.cls_of_plain(ch) for i, ch in enumerate(sq)], dtype=np.int32)
def scan(ct, trans, cls, lp32, Lmax=20):
    n0 = len(ct)
    enc = bytes(A.IDX[c] for c in ct)
    tr = np.array(trans, dtype=np.int32)
    out = np.zeros((Lmax + 1, n0 + 1, 3))
    _l.gap_scan(enc, n0, Lmax, tr.ctypes.data, len(trans), cls.ctypes.data, lp32.ctypes.data, out.ctypes.data)
    return out   # [L, g, (total, nq, nmasked)]
