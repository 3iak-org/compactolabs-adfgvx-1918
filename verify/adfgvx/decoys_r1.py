"""R1 decoy selection (prereg C1, D2). Run ONCE and commit the output before any decoy is scored.
Rule (fixed here): pool = solved entries (creilly records, status 'Solved', plaintext present) whose key is a period
key with width not in {6,9,12,18,36}, whose printed ciphertext has no '-' or '?' and length >= 132,
excluding p156C3, p156C6 and the R2-R4 entries.  Their true square is a different square from the R1 square
(checked in r1_square_known.py).  Seeded shuffle (seed 20261101); decoy k = (part-5-like = first 132 symbols of
pool[2k], part-6-like = first 108 symbols of pool[2k+1] with symbols 5..19 replaced by '-'), 100 decoys."""
import json, random
import data as D
R = D.records(); K = D.keys()
EXCL = {"p156C3", "p156C6", "p179B1", "p155E", "p192A"}
pool = sorted(r["id"] for r in R if r["status"] == "Solved" and r["plaintext"] and r["key"] in K
              and K[r["key"]]["source"] == "lasry" and K[r["key"]]["width"] not in (6, 9, 12, 18, 36)
              and r["id"] not in EXCL and len(r["printed"]) >= 132 and not set(r["printed"]) & set("-?"))
random.Random(20261101).shuffle(pool)
dec = [{"k": k, "part5_from": pool[2*k], "part6_from": pool[2*k+1]} for k in range(100)]
json.dump({"pool_size": len(pool), "decoys": dec}, open("decoys_r1.json", "w"), indent=1)
print("pool", len(pool), "decoys", len(dec))
