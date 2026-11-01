"""Strand R, plain deterministic decrypts for the lead's comparison (referee C4). No scoring, no
null: check-adfgvx owns those. comp-adfgvx, 2026-11-01.

    ~/dev/projects/ciphers/.venv/bin/python -I search/adfgvx/rdecrypt.py

R1  p156C3, p156C6 (Childs p.153 parts 5 and 6) under the claimed 18-column transposition
    16 7 13 4 15 8 17 3 1 12 14 2 5 9 10 18 11 6 and the claimed square (creilly
    data/messages.json 'p153', 24 known cells, '?' = cell never used).
R2  p179B1 (Childs p.176, message 2305 part 1) under nov10 (Lasry's transposition), with 20
    lost symbols inserted at position 160 (after the first 160 log symbols), under (a) the
    claimed square (Lasry's + the 2017 blog-comment digits, creilly data/messages.json '2305')
    and (b) Lasry's published square with its 5 blank cells.
Ciphertext: creilly @ e60da03 records.json `printed`. Output marks: '-' a letter with a lost
symbol in its pair, '?' a pair whose square cell is blank. Odd length: the dangling symbol is
dropped (reported).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
from engine import decrypt, check_key  # noqa: E402
from provenance import header as prov_header  # noqa: E402

CLAIMED_T18 = [16, 7, 13, 4, 15, 8, 17, 3, 1, 12, 14, 2, 5, 9, 10, 18, 11, 6]


def main():
    ct = os.path.join(ROOT, "ciphertexts")
    rec = {e["id"]: e for e in json.load(open(os.path.join(ct, "adfgvx-1918-log.records.json")))}
    keys = {k["id"]: k for k in json.load(open(os.path.join(ct, "adfgvx-1918-log.keys.json")))}
    msgs = {m["name"]: m for m in json.load(open(os.path.join(ct, "adfgvx-1918-log.messages.json")))["messages"]}
    L = []
    W = L.append
    W("# Strand R: plain decrypts of R1 (p.153) and R2 (p.176 '2305')\n")
    W(prov_header("", "search/adfgvx/rdecrypt.py"))
    W("Plaintext only: no scoring, no null, no reading. Engine: `search/adfgvx/engine.py` "
      "(validated on all 465 as-transcribed solved entries, results/adfgvx-census-validation.md).\n")
    W("Marks: `-` a letter whose pair contains a lost symbol; `?` a pair whose square cell is "
      "blank in the stated square.\n")
    # R1
    k = msgs["p153"]["key"]
    assert k["transposition"] == CLAIMED_T18 == keys["ours_nov07_18col"]["transposition"]
    check_key(k["square"], k["transposition"])
    W("## R1: p156C3 and p156C6 (Childs p.153, FKR v CGH, parts 5 and 6)\n")
    W(f"Transposition `{' '.join(map(str, k['transposition']))}` (18 columns). Square, row-major "
      f"ADFGVX x ADFGVX: `{k['square']}` ({36 - k['square'].count('?')} known cells; "
      f"creilly messages.json, identical to keys.json `ours_nov07_18col`: "
      f"{k['square'] == keys['ours_nov07_18col']['square']}).\n")
    for i in ("p156C3", "p156C6"):
        o = rec[i]["printed"]
        p = decrypt(o, k["square"], k["transposition"])
        W(f"### {i}: {len(o)} log symbols ({o.count('-')} lost){', odd: last symbol dropped' if len(o) % 2 else ''}\n")
        W("```\n" + p + "\n```\n")
        W(f"{len(p)} characters: {p.count('-')} with a lost symbol, {p.count('?')} on a blank cell.\n")
    # R2
    W("## R2: p179B1 (Childs p.176, LP v ZON, message 2305 part 1)\n")
    o = rec["p179B1"]["printed"]
    assert len(o) == 220 and "-" not in o
    gapped = o[:160] + "-" * 20 + o[160:]
    tr = keys["nov10"]["transposition"]
    assert tr == msgs["2305"]["key"]["transposition"]
    W(f"Log text {len(o)} symbols, header count 240. Gap: 20 lost symbols inserted after the "
      f"first 160 (between log group 32 and group 33), giving 240. Transposition nov10 "
      f"`{' '.join(map(str, tr))}`.\n")
    for lab, sq in (("(a) claimed square: Lasry's nov10 with the 2017 blog-comment digits in its 5 blank cells", msgs["2305"]["key"]["square"]),
                    ("(b) Lasry's published nov10 square, 5 cells blank", keys["nov10"]["square"])):
        check_key(sq, tr)
        p = decrypt(gapped, sq, tr)
        W(f"### {lab}\n")
        W(f"Square `{sq}`.\n")
        W("```\n" + p + "\n```\n")
        W(f"{len(p)} characters: {p.count('-')} with a lost symbol, {p.count('?')} on a blank cell.\n")
    W("Not done here, by design: filling the 20 lost symbols (creilly's `fill` in messages.json "
      "is not used), and any judgement of whether these read.\n")
    open(os.path.join(ROOT, "results", "adfgvx-R-decrypt.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
