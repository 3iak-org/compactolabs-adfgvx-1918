import ctypes, os, numpy as np
_l = ctypes.CDLL(os.path.join(os.path.dirname(os.path.abspath(__file__)), "libkern.so"))
_l.hc_square.restype = ctypes.c_double
_l.hc_square.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint64, ctypes.c_void_p]
_l.vit_fill.restype = ctypes.c_double
_l.vit_fill.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]

def hc_square(codes, lp32, restarts=50, kicks=20, seed=1):
    """codes: int8 array of pair codes 0..35, negative = unknown/break. Returns (score, square_classes[36])."""
    codes = np.ascontiguousarray(codes, dtype=np.int8)
    sq = np.zeros(36, dtype=np.int32)
    s = _l.hc_square(codes.ctypes.data, len(codes), lp32.ctypes.data, restarts, kicks, seed, sq.ctypes.data)
    return s, sq

def vit_fill(masks, lp32):
    masks = np.ascontiguousarray(masks, dtype=np.uint32)
    out = np.zeros(len(masks), dtype=np.int32)
    s = _l.vit_fill(masks.ctypes.data, len(masks), lp32.ctypes.data, out.ctypes.data)
    return s, out

def to32(lp):
    return np.ascontiguousarray(lp, dtype=np.float32)
