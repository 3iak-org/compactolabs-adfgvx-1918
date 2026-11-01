import ctypes, os, numpy as np
import adfgvx as A
_l = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libtsearch.so"))
_l.ic_search.restype = ctypes.c_int
_l.ic_search.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
_l.ic_key.restype = ctypes.c_double
_l.ic_key.argtypes = [ctypes.c_void_p]

def enc(parts):
    return b"".join(bytes(A.IDX[c] if c in A.IDX else 6 for c in p) for p in parts), np.array([len(p) for p in parts], dtype=np.int32)

def search(parts, w, restarts, seed, topk):
    buf, lens = enc(parts)
    keys = np.zeros((topk, w), dtype=np.int32); sc = np.zeros(topk)
    n = _l.ic_search(buf, lens.ctypes.data, len(parts), w, restarts, seed, topk, keys.ctypes.data, sc.ctypes.data)
    o = np.argsort(-sc[:n])
    return keys[o], sc[o]

def ic_of(parts, key):
    buf, lens = enc(parts)
    # reuse search machinery: evaluate a single key via 0-restart trick is not exposed; do it in python
    cnt = np.zeros(36); N = 0
    for p in parts:
        inter = A.untranspose(p, list(key))
        for i in range(0, len(inter) - 1, 2):
            a, b = inter[i], inter[i + 1]
            if a in A.IDX and b in A.IDX: cnt[A.IDX[a] * 6 + A.IDX[b]] += 1; N += 1
    return float((cnt * (cnt - 1)).sum() / (N * (N - 1)))
