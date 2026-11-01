"""Task 0: decrypt every solved entry under its published key; report how many are clean.

'Clean' = the decryption of the entry's own `ciphertext` field is compatible with the
entry's published `plaintext` at every position, where
  plaintext '-', '?', '_' : unknown letter, matches anything
  plaintext '#'  : a digit cell the publisher could not fix; matches a digit or '?' cell
  decrypt  '?'   : unknown symbol or unknown square cell; matches anything
We also report the strict count (no wildcard needed anywhere) and the length failures.
"""
import sys, json, collections
import adfgvx as A, data as D

def compatible(d, p, square):
    if d == "?" or p in "-?_":
        return True
    if p == "#":
        return d.isdigit() or d == "?"
    return d == p

def check(r, K, field="ciphertext"):
    k = K[r["key"]]
    c = r[field].replace(" ", "")
    d = A.decrypt(c, k["transposition"], k["square"])
    p = r["plaintext"]
    if len(d) != len(p):
        return "len", len(d), len(p), []
    bad = [i for i in range(len(p)) if not compatible(d[i], p[i], k["square"])]
    strict = all(d[i] == p[i] for i in range(len(p)))
    return ("ok" if not bad else "mismatch"), len(d), len(p), bad, strict

if __name__ == "__main__":
    R = D.records(); K = D.keys()
    sol = [r for r in R if r["plaintext"] and r["key"]]
    cnt = collections.Counter(); bad_list = []
    for r in sol:
        res = check(r, K)
        cnt[res[0]] += 1
        if res[0] == "ok" and res[4]: cnt["strict"] += 1
        if res[0] != "ok": bad_list.append((r["id"], r["key"], res[:4]))
    print("solved entries with plaintext+key:", len(sol))
    print(dict(cnt))
    for b in bad_list: print(b)
    # also: how many of the ciphertext fields are identical to the printed transcription
    same = sum(1 for r in sol if r["ciphertext"].replace(" ", "") == r["printed"])
    print("ciphertext==printed for", same, "of", len(sol))
    by = collections.defaultdict(collections.Counter)
    for r in sol:
        by[r["method"]][check(r, K)[0]] += 1
    for m, c in by.items(): print(m, dict(c))
