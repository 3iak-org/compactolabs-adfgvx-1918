# Adversary calibration: creilly11235/adfgvx-1918 on Childs p. 153 and p. 176

*adv-adfgvx, 2026-10-31, for dev's ticket tmvx707qsk8oq. **lead-adfgvx: don't read this until your
own replication (strand R) is finished.** Dev asked that the two not be shared before both are done.*

The claims are public and unrefereed: github.com/creilly11235/adfgvx-1918, HEAD `e60da03`, read
2026-10-31. Only the claimed keys, plaintexts and transcriptions were read (`keys.json`,
`records.json`, `messages/p156C3.md`, `p156C6.md`, `p179B1.md`); none of their search code was.
Their transcription of all three entries is identical to the Schmeh/Lasry text used here (dashes
removed).

## Answer

**p. 176 GGDAA, Lasry's nov10 key plus a 20-symbol gap: survives the adversary by a wide margin**
[S, 2026-10-31].
- My own gap filler at their position (insert at symbol 160) reproduces their reading to within a
  few letters, at −5.88. Left free to choose the position, it puts the gap at 162, at −5.77.
- **Null with the same freedom** (any gap position, gap content optimised, 20 symbols):
  - nov10 on 16 shuffles of the message: best −7.77;
  - each of the 14 other published keys on the real message: best −7.79.
- So the claim beats the best of 30 nulls by **≈ 1.9 per quadgram**, over about 117 quadgrams.
- The gap *length* is not free. The log header counts 240 symbols and 220 were received, so the
  freedom is the gap's position and content, which the null had too.
- Re-scoring the reading under my scorer (−5.90) shows why the quadgram score is low: it is mostly
  place and unit names (ALPENKORPS, PETERREVE, VERBASZ, NAGYBECSKEREK, VERSECZ).

**p. 153 parts 5+6, a new 18-column key: not decided by anything I can compute. The square follows
from the transposition, but nothing here certifies the transposition** [S].
1. **Part 5 alone (66 letters) can't be told from noise by n-gram score.** The claimed reading
   scores −4.68 under my scorer. With the claimed transposition fixed and the square free, my
   annealer finds a *different* reading that scores higher, −4.50:
   `OESXUEBEWIEGSCHDIEFFDIEEX1915IMLINIEVORRIERSTILDESANELANDWIRANINIE`. A free-key search on 16
   shuffles of part 5 reaches −4.75 (range −4.75 to −5.09), and the real part 5 reaches −4.56.
2. **The claimed transposition's pair IC is not distinctive against an optimised null.** It is 320
   for part 5 and 654 for the two parts jointly. An IC-annealing search on shuffled ciphertext
   reaches 294–334 (part 5, 16 shuffles) and 592–688 (both parts, 16 shuffles). 20,000 *random*
   permutations top out at 208, so a sampled null would have called 320 wildly significant. **The
   null has to be optimised, not sampled.**
3. **Given the claimed transposition, the square is determined.** With both parts jointly and the
   transposition fixed, two of eight restarts converge on their reading:
   `ANORDNUNGENKOMPTENFFTENNRX2XBEZIEHENLASSENSOWEITNOCHNICHTGESCHEHEN | M?N?T?ONSB?S?A?DDERNA?H?UTARTI?G?RIEMEL?`
   at −4.38. The only difference is in the digit cells, which n-grams can't pin (`VOM2TEN11TEN` →
   `KOMPTENFFTEN`; creilly says three letters are open). The other six restarts land on isomorphs of
   it (`URANKRORDERVALCHER…`, −4.90). The same transposition on shuffled ciphertext gives at best
   −6.00 (16 shuffles).
4. **My free search over transpositions never finds the claimed optimum.** On the real joint text
   it gets −5.31; on shuffled joint text, −5.45 at best. The claim (−4.80 as printed, −4.38 with
   free digit cells) beats both by a lot. But **my solver demonstrably misses the claimed key on the
   real text**, so its shuffled maximum is not a null with the claimant's power. Whether a solver
   that *does* find −4.4 on the real text would also find about −4.4 on shuffled text is the
   question that decides the claim. I can't answer it.

What would settle p. 153: run the claimant's keyless solver, or the team's, on (a) same-length
shuffles of parts 5+6 with the 15 gap symbols in the same places, and (b) planted controls. Then
compare its best false joint score with −4.38/−4.80. That is also referee B1's requirement. If
shuffles reach −4.4, the claim is not unique. If they stall near −5.4, as mine do, it stands on the
transposition.

**The human-level evidence I can state:** the reading is word-coherent across both parts, with no
edits to part 5. Part 5 has 0.74 dictionary-word coverage against 0.20 for my best false reading
under the same transposition, and part 6 continues it (MUNITIONSBESTAND DER NACHHUT ARTILLERIE
MELDEN). That is persuasive but not a significance test. The square is fitted to both parts, so
part 6 is not out-of-sample.

## Method and witnesses

`adversary/adfgvx/calib_creilly.sh` (the recipe for the second pass is at its foot). Raw lines are
in `results/C_creilly.txt` and `results/C_creilly_fixedperm.txt`. They were re-decrypted by
`verify_readings.py`: 85 + 24 lines, 0 mismatches. Modes, scorer and corpus are as in
`adversary/adfgvx.md`.
- **Part 6** is used as printed: 108 symbols, with the 15 dashes as unknown symbols (`?`). Pairs
  that touch an unknown symbol give an unknown letter, and quadgrams containing one are excluded.
- **Joint scoring:** the parts' pair streams are joined by three unknown pairs, so no quadgram
  crosses the boundary.
- Search effort per run: 8 restarts × (200k-step IC anneal, 1M-step substitution anneal, 3
  reordering rounds); 2M steps in the fixed-transposition runs.

## What I could not do

- Build a keyless solver strong enough to find the claimed p. 153 key from scratch. That is the
  missing power control, and without it item 4 is open.
- Test a free gap *length* on p. 176, or gaps elsewhere in the 83 log entries.
- Check either reading against the Childs page images.
