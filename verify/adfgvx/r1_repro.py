"""R1 step 1: reproduce the claimed p.153 reading from key (+ claimed square).
Claim text copied from creilly README 'Page 153, a new key' (HEAD e60da03) and
data/messages.json (square string, corrections, fills, open letters)."""
import json, os, collections
import adfgvx as A, data as D

KEY18 = [16, 7, 13, 4, 15, 8, 17, 3, 1, 12, 14, 2, 5, 9, 10, 18, 11, 6]
SQ = "?TXUGI????8?2WO?CMB1?SZ?5NDH?VEA??LR"   # messages.json p153.key.square
# README reading, part 5 / part 6 (lower case = filled by reading; '_' open)
P5 = "ANORDNUNGENVOM2TEN11TENNR858BEZIEHENLASSENSOWEITNOCHNICHTGESCHEHEN"
P6 = "MuNiTiONSBeStAnDDERNAcHhUTARTILLERIEMELdEnX8XGXR___BXA"   # as printed in README rectangle (corrections: 2 letters)
P6 = "MuNiTiONSBeStAnDDERNAcHhUTARTILLERIEMELdEnX8XGXR___BXA"

def pairs(inter):
    return [inter[i:i+2] for i in range(0, len(inter) - 1, 2)]

if __name__ == "__main__":
    R = D.by_id()
    c5 = R["p156C3"]["ciphertext"].replace(" ", "")
    c6 = R["p156C6"]["ciphertext"].replace(" ", "")
    assert len(c5) == 132 and len(c6) == 108
    for name, c in (("part5", c5), ("part6", c6)):
        inter = A.untranspose(c, KEY18)
        print(name, "w=18 rows=%d" % ((len(c) + 17) // 18), "n=", len(c), "colLens", sorted(set(A.col_lengths(len(c), 18))))
        print(" interim pairs:", " ".join(pairs(inter)))
        print(" decrypt (claimed square, no corrections):", A.decrypt(c, KEY18, SQ))
    cl5 = P5.upper(); cl6 = P6.upper()
    # compare
    d5 = A.decrypt(c5, KEY18, SQ); d6 = A.decrypt(c6, KEY18, SQ)
    print("part5 match with claimed reading:", sum(a == b for a, b in zip(d5, cl5)), "/", len(cl5), "diff idx", [i for i,(a,b) in enumerate(zip(d5,cl5)) if a!=b])
    print("part6 match:", sum(a == b for a, b in zip(d6, cl6) if a != "?"), "known-decrypt letters of", len(cl6), " mismatches:", [(i,a,b) for i,(a,b) in enumerate(zip(d6,cl6)) if a!="?" and a!=b])
    # square-free consistency: pair -> letter map implied by the claimed reading
    mp = collections.defaultdict(set); inv = collections.defaultdict(set)
    for c, rd in ((c5, cl5), (c6, cl6)):
        inter = A.untranspose(c, KEY18)
        for k, ch in enumerate(rd):
            pr = inter[2*k:2*k+2]
            if "-" in pr or ch == "_": continue
            mp[pr].add(ch); inv[ch].add(pr)
    print("pairs with >1 letter:", {k: v for k, v in mp.items() if len(v) > 1})
    print("letters with >1 pair:", {k: sorted(v) for k, v in inv.items() if len(v) > 1})
    print("distinct pairs used:", len(mp), "distinct letters:", len(inv))

def roundtrip():
    """Re-encrypt the claimed reading under claimed key+square and compare with the logged symbols."""
    inv = {}
    for k, ch in enumerate(SQ):
        if ch != "?": inv[ch] = A.LAB[k // 6] + A.LAB[k % 6]
    R = D.by_id(); tot = ok = 0; mism = []
    for name, rd, pid in (("part5", P5.upper(), "p156C3"), ("part6", P6.upper(), "p156C6")):
        c = R[pid]["ciphertext"].replace(" ", "")
        inter = "".join(inv.get(ch, "??") for ch in rd)
        enc = A.transpose(inter, KEY18)
        for i, (a, b) in enumerate(zip(enc, c)):
            if b == "-" or a == "?": continue
            tot += 1
            if a == b: ok += 1
            else: mism.append((name, i, a, b))
    return tot, ok, mism

if __name__ == "__main__":
    t, o, m = roundtrip()
    print("round trip: %d logged known symbols compared, %d identical, mismatches %s" % (t, o, m))
