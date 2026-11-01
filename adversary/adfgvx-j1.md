# Adversary on strand J1 (READ-KNOWN-KEY): the 23 detections

adv-adfgvx, 2026-11-01. Target: lead-adfgvx f26cded / c9e554a, `results/adfgvx-J1-targets.jsonl`
(ticket tmvxr15fone8p; counterexample ticket to dev tmvxroux7sf8g). Prereg: `findings/adfgvx-1918-prereg.md`, strand J, J1(ii).

## Answer

**J1(ii) fails for one detection, p218A, and holds for the other 22.**
- The wrong-key test is exhaustive over all 21 other keys and every ≤ 2-edit set [C, 2026-11-01:
  e2.c, with every row re-checked by pycheck.py]. The random-key part is [S].

- **p218A (nov22, S = −3.683).** A wrong period key reaches a higher score on the same unit
  under the same freedom (≤ 2 jattack edits). nov13_20 scores −3.537 with ins5@275,ins5@380.
  A non-period key, childs_jul18, scores −3.518. So by the prereg's own rule, p218A stays a
  detection and is **not** READ-KNOWN-KEY.
  - The mechanism is structural, not bad luck. S_p218A is below ln(1/36) = −3.584, the charge
    the statistic puts on a trigram with an unknown letter. So a decryption in which **every
    letter is unknown** would outscore the claimed reading.
  - nov13_20 has 12 blank cells out of 36, and childs_jul18 has 13. Their "readings" are 81%
    and 76% unknown trigram positions (`results/wrongkeys.tsv`).
- **p062A (sep19) survives by 0.011.** S = −3.452; best wrong period key nov13_20 = −3.463.
- **The other 21 survive by ≥ 0.088.** The margins are listed in the table below.
  - The weakest of them are p170D (+0.088), p071A2 (+0.094), p071A1 (+0.101) and p220B (+0.106).
  - The five the lead reads as clean German (p213D, p189B3, p0924#1, p110D, p139A2) survive the
    best wrong key by 0.64–1.30. The tightest is p110D, against childs_aug03.
  - No random key comes within 0.69 of any of the five. The nearest is p139A2, at R1 −3.294.
- **Random keys on the real ciphertext.** CLAUDE.md test 3 calls for this null; the J1 null
  does not contain it. The random-key null is 2,600 keys per unit (59,800 in all), cap 2 [S; seeds fixed in
  `randkeys.py`; families defined below].
  - **p218A falls again.** 124 of 1000 random keys carrying a Lasry blank pattern (R1) score
    ≥ S. None of the blank-free random keys (R0) do.
  - **On the other 22 units, not one random draw reaches S** in any family.
  - The closest are:
    - p062A: R1 max −3.479 against S −3.452, a gap of 0.027;
    - p071A2: max −3.439 against S −3.383, a gap of 0.056;
    - p220B: R1 max −3.425 against S −3.330, a gap of 0.095;
    - p170D: R1 max −3.469 against S −3.369, a gap of 0.100.
  - **What this rules out.** A per-unit rate of random keys reaching S of more than about
    3/2600 ≈ 0.12% is excluded at roughly 95% for each of those 22 units. That is a sampled
    statement, not a bound on the 36!·w! key space.
  - No HS draw (the claimed square with a random transposition) reaches S on any unit. So no
    detection is reproduced by the claimed square's letter frequencies alone.
  - On the clean five, the HS maximum stays 0.65–1.23 below S.
  - On p071A2 it comes within 0.057.
- **None of the 23 readings is a near-copy of a solved plaintext.** The longest common
  substring with any solved plaintext is 18 symbols, `XKRIEGSMINISTERIUM` in p213D vs p124A2.
  Every other detection is at ≤ 14. So none is a repeat reception of an already-read message
  [C, `overlap.py`].

**What would have to be true for this to be wrong:**
- My variant set differs from comp's. I checked this: e2.c reproduces comp's S, score0 and
  edit list exactly on all 64 (target, candidate-key) pairs, 0 mismatches (`repro.py`).
- The keys file I used differs from the frozen one. I used the file at lead-adfgvx c9e554a,
  and the LM table I built hashes to the `lm_sha256` recorded in the targets file (675a65d4…).
- The prereg means "a wrong key" to exclude keys with blank cells. It does not say so. If it
  does, p218A survives: the best blank-free wrong key on p218A (nov25) scores −4.048, well below
  S. Only blank-heavy keys beat it (nov13_20 and childs_jul18). The two readings of the rule have to be stated
  either way.

## Why blank-heavy wrong keys are the adversary's best tool (a property of the statistic)

The J1 statistic charges an unknown-letter trigram ln(1/36) = −3.584. The mean of the LM table
over uniform trigrams is −4.788. So an unknown is worth about **1.2 nats per trigram more than a
random letter**.

- **The effect on wrong keys.** A wrong key with many blank cells decrypts any text to a reading
  that is mostly unknown, and scores close to −3.58 with no information at all. Two inserted
  unknown 5-groups lift it further.
  - Of the 13 wrong period keys, nov13_20 (12 blanks) is the best wrong key on 18 of the 23
    units. nov13_16 and nov16 (8 blanks each) win 2 each, and sep19 wins 1.
- **Where this decides the result.** Over all 23 units, blank-free wrong keys have a median of
  −4.54 before edits and −3.96 after the best ≤ 2 edits. So the adversary's ceiling is set by
  the blank pattern, not by German.
  - On p218A the best blank-free wrong key (nov25) reaches only −4.048, and on p062A only
    −3.896.
  - Every detection with S near or below about −3.45 is within reach of a blank-heavy key. Only
    p218A is actually below.
- **The statistic is unchanged.** I am not proposing a change. The per-target null uses the
  same statistic, so the FWER bound is unaffected.
- **What it means for J1(ii).** For detections in the −3.45…−3.30 band, "the adversary failed
  to produce an equal score" is a weak statement. The adversary's best competitors there are
  readings that say nothing.
  - **The safer reading test for those units is the unknown fraction.** p071A1 is 59% unknown
    trigrams under its own claimed key, p071A2 77%, p102A 77%, p125B 73% and p231B2 58%. Those
    claimed readings owe much of S to lost symbols in the transcription. The shuffled-text half
    of the null does preserve the lost symbols, so the threshold accounts for that.

## Evidence

All code is in `adversary/adfgvx/j1/`. Nothing there was copied from `search/` or `verify/`.

- **`e2.c`.** My own exhaustive ≤ 2-edit search and decryption, written from the prereg's
  definition of the statistic. The edit-application rule is matched to jattack's on purpose,
  so the adversary gets exactly the claim's freedom and no more.
  - jattack drops some edits silently: a second edit at a deletion's own position, or strictly
    inside a deletion's span. So "≤ 2 edits" is slightly smaller than the literal set.
  - This is harmless to the FWER, because the null uses the same code. It is noted for comp.
- **`repro.py`.** Reproduces comp's per-key S for all 64 (target, candidate) pairs. Result:
  0 mismatches at 2e-6.
- **`wrongkeys.py`.** Runs every detection under each of the 21 keys other than its argmax key
  (13 period keys and 8 non-period keys), exhaustively at cap 2. Output:
  `results/wrongkeys.tsv`, 483 rows.
- **`randkeys.py`.** Runs the real ciphertext of every detection under random keys, cap 2,
  with fixed seeds. There are four families per unit:
  - R0: 1000 uniform squares with no blanks, at a width drawn from a uniform Lasry key;
  - R1: 1000 of the same, carrying that key's blank pattern;
  - HS: 300 with the claimed square and a random transposition of the claimed width;
  - HT: 300 with the claimed transposition and a random square carrying the claimed key's
    blanks.
  - Output: `results/randkeys.tsv.gz`.
- **`pycheck.py`.** An independent Python re-decryption and re-score: a different language and
  a different decryption method (column slicing by rank). It covers every wrong-key row, the
  top 500 random-key rows and every 50th random-key row. Result: 483/483 wrong-key rows and 1,696 random-key rows agree; max |score diff| 5e-7; 0 plaintext mismatches (`results/pycheck.txt`).
- **`overlap.py`.** The longest common substring of each reading with every solved plaintext.
- **`summarize_j1.py`.** Produces the table below.

| unit | key | S | thr | S-thr | best wrong period key (of 13) | best other key (of 8) | R0: n, max, #>=S | R1: n, max, #>=S | HS: n, max, #>=S | HT: n, max, #>=S |
|---|---|---|---|---|---|---|---|---|---|---|
| p062A | sep19 | -3.452 | -3.628 | +0.175 | nov13_20 -3.463 | childs_aug03 -3.487 | 1000, -3.743, 0 | 1000, -3.479, 0 | 300, -3.695, 0 | 300, -3.748, 0 |
| p071A1 | oct04 | -3.372 | -3.492 | +0.120 | nov16 -3.534 | childs_jul18 -3.472 | 1000, -3.530, 0 | 1000, -3.453, 0 | 300, -3.499, 0 | 300, -3.537, 0 |
| p071A2 | oct04 | -3.383 | -3.423 | +0.040 | sep19 -3.476 | childs_jul18 -3.488 | 1000, -3.439, 0 | 1000, -3.441, 0 | 300, -3.440, 0 | 300, -3.445, 0 |
| p072A | oct04 | -2.724 | -3.780 | +1.056 | nov13_20 -3.546 | childs_aug03 -3.387 | 1000, -3.795, 0 | 1000, -3.493, 0 | 300, -3.840, 0 | 300, -3.743, 0 |
| p072B1 | oct04 | -3.180 | -4.015 | +0.835 | nov13_20 -3.561 | chi_2017_comments -3.459 | 1000, -3.995, 0 | 1000, -3.535, 0 | 300, -4.000, 0 | 300, -3.993, 0 |
| p0924#1 | nov01 | -2.564 | -3.769 | +1.205 | nov13_20 -3.506 | childs_aug03 -3.511 | 1000, -3.899, 0 | 1000, -3.541, 0 | 300, -3.940, 0 | 300, -3.873, 0 |
| p102A | nov01 | -3.120 | -3.332 | +0.213 | nov16 -3.429 | chi_2017_comments -3.458 | 1000, -3.403, 0 | 1000, -3.388, 0 | 300, -3.372, 0 | 300, -3.403, 0 |
| p102C | nov01 | -2.921 | -3.447 | +0.526 | nov13_20 -3.441 | ours_nov07_18col -3.376 | 1000, -3.410, 0 | 1000, -3.389, 0 | 300, -3.444, 0 | 300, -3.481, 0 |
| p110D | nov01 | -2.745 | -3.570 | +0.825 | nov13_20 -3.457 | childs_aug03 -3.388 | 1000, -3.754, 0 | 1000, -3.447, 0 | 300, -3.790, 0 | 300, -3.753, 0 |
| p125B | nov04 | -3.239 | -3.486 | +0.248 | nov13_16 -3.468 | chi_2017_comments -3.483 | 1000, -3.520, 0 | 1000, -3.471, 0 | 300, -3.503, 0 | 300, -3.512, 0 |
| p139A2 | nov04 | -2.603 | -3.211 | +0.607 | nov13_20 -3.361 | ours_nov07_18col -3.329 | 1000, -3.396, 0 | 1000, -3.294, 0 | 300, -3.319, 0 | 300, -3.389, 0 |
| p141B.2 | nov04 | -2.545 | -3.777 | +1.232 | nov13_20 -3.490 | childs_aug03 -3.486 | 1000, -3.911, 0 | 1000, -3.513, 0 | 300, -3.800, 0 | 300, -3.916, 0 |
| p142A2+p142A | nov04 | -3.277 | -3.744 | +0.466 | nov13_20 -3.485 | childs_aug03 -3.450 | 1000, -3.826, 0 | 1000, -3.445, 0 | 300, -3.868, 0 | 300, -3.787, 0 |
| p153B4+p153B | nov04 | -2.536 | -3.638 | +1.102 | nov13_20 -3.415 | childs_jul18 -3.438 | 1000, -3.648, 0 | 1000, -3.464, 0 | 300, -3.596, 0 | 300, -3.635, 0 |
| p170D | nov07 | -3.369 | -3.432 | +0.063 | nov13_20 -3.457 | childs_jul22 -3.490 | 1000, -3.786, 0 | 1000, -3.469, 0 | 300, -3.548, 0 | 300, -3.750, 0 |
| p189B3 | nov13_16 | -2.157 | -3.289 | +1.132 | nov13_20 -3.495 | chi_2017_comments -3.461 | 1000, -3.908, 0 | 1000, -3.494, 0 | 300, -3.391, 0 | 300, -3.572, 0 |
| p190G | nov13_20 | -2.486 | -3.030 | +0.544 | nov13_16 -3.487 | childs_aug03 -3.398 | 1000, -3.487, 0 | 1000, -3.408, 0 | 300, -3.134, 0 | 300, -3.388, 0 |
| p194A.2 | nov13_16 | -2.759 | -3.306 | +0.548 | nov13_20 -3.418 | childs_jul22 -3.466 | 1000, -3.619, 0 | 1000, -3.475, 0 | 300, -3.420, 0 | 300, -3.450, 0 |
| p213D | nov19 | -2.324 | -3.414 | +1.089 | nov13_20 -3.503 | chi_2017_comments -3.383 | 1000, -3.517, 0 | 1000, -3.304, 0 | 300, -3.449, 0 | 300, -3.530, 0 |
| p218A | nov22 | -3.683 | -3.873 | +0.190 | **nov13_20 -3.537** | **childs_jul18 -3.518** | 1000, -3.889, 0 | 1000, -3.540, 124 | 300, -3.912, 0 | 300, -3.953, 0 |
| p218C | nov22 | -3.164 | -3.750 | +0.586 | nov13_20 -3.551 | chi_2017_comments -3.460 | 1000, -3.821, 0 | 1000, -3.513, 0 | 300, -3.796, 0 | 300, -3.801, 0 |
| p220B | nov22 | -3.330 | -3.506 | +0.176 | nov13_20 -3.476 | chi_2017_comments -3.436 | 1000, -3.526, 0 | 1000, -3.425, 0 | 300, -3.529, 0 | 300, -3.595, 0 |
| p231B2 | nov28 | -3.315 | -3.510 | +0.195 | nov13_20 -3.527 | childs_aug20 -3.492 | 1000, -3.490, 0 | 1000, -3.489, 0 | 300, -3.484, 0 | 300, -3.548, 0 |

Bold = a wrong key at or above S (J1(ii) fails). R0/R1/HS/HT cells give n, max, and the
number of draws ≥ S.

## Addendum: does p062A survive with the edit cap varied? (dev, ticket tmvxroux7sf8g)

p062A is run under its claimed key (sep19), all 21 other keys and R1 random keys (randkeys.py
seeds), at caps 0–3 (`j1/capvary.py`, `results/capvary.tsv`, `results/capvary_summary.txt`).
e2.c now takes the cap as an argument and still reproduces comp 64/64 at cap 2. [C for the 22
keys; S for the random draws.]

| Cap | S (sep19) and edits | Best wrong key | Margin | Wrong keys ≥ S | R1 random: n, max, ≥ S |
|---|---|---|---|---|---|
| 0 | −4.420 (none) | chi_2017_comments −3.599 | −0.821 | 13/21 | 1000, −3.644, 436 |
| 1 | −3.500 (del5@200) | nov13_20 −3.525 | +0.024 | 0/21 | 1000, −3.536, 0 |
| 2 | −3.452 (ins1@131,del5@200) | nov13_20 −3.463 | +0.011 | 0/21 | 1000, −3.479, 0 |
| 3 | −3.312 (del1@93,ins1@83,del5@200) | nov13_20 −3.369 | +0.057 | 0/21 | 200, −3.489, 0 |

**What the table shows:**
- **p062A survives J1(ii) at every cap ≥ 1, and its margin is thinnest at cap 2.**
- **At cap 0 it is not a reading at all.** It needs the del5@200 group deletion, which every cap
  ≥ 1 finds.
- **From cap 2 to cap 3, the claimed key gains +0.140 and the best wrong key +0.094.** The claimed
  key gains more per edit than any wrong key. This is the real-key signature of the baseline
  (`adfgvx.md`).
- **The cap-3 reading reads better.** It includes `AUFDAM`, `BURDAL` and `PFERDENA`.
- **Caution.** Cap 3 is outside the prereg (the cap was fixed at 2 before J1 met the text), so
  this is a robustness note, not a re-test. I did not rebuild comp's per-target null at caps
  1 or 3, so the detection itself is not re-tested at those caps either.

## Addendum 2: does the J3 shuffle-null bias reach J1? No. (dev, ticket tmvxuh7oxv38h)

**Answer.** For every one of the 49 J1 targets, the J1 threshold holds against a mask-matched
null [S, 2026-11-01].
- **How it was tested.** 100 draws per target:
  - each draw is real printed ciphertext of a solved entry whose key is not among t's
    candidates (as in J1 half (b)), cut to t's length;
  - the source window has no lost symbol of its own;
  - t's own lost-symbol mask is imposed on it;
  - it is scored exactly as S_t (max over t's candidates, cap 2, e2.c).
- **What it gave.**
  - **0 of 4900 draws exceed their target's threshold.**
  - The mask-matched mean is *below* the shuffle half's (a) mean on average, in every damage bin
    (mean(c) − mean(a), and its range across targets):

    | Damage bin | Targets | Mean shift | Range |
    |---|---|---|---|
    | ≥ 10% lost | 14 | −0.021 | −0.069 … +0.057 |
    | 2–10% lost | 15 | −0.038 | −0.127 … +0.027 |
    | < 2% lost | 20 | −0.069 | −0.262 … +0.044 |

  - The largest positive shift is p125B (+0.057), and its mask-matched max (−3.532) is still
    below its threshold (−3.486).
- **Why J1 differs from J3.** The J3 bias needs a *free* square to cash in on the column
  structure of real ciphertext. With J1's fixed candidate keys there is nothing to fit, and
  shuffled text under the candidate key is the more generous null.
- **A warning about my own first attempt.** v1 (`results/masknull_v1_unclean*`) let source
  windows carry their own lost symbols on top of t's mask. It gave 17/4900 exceedances, all
  from three heavily damaged train-side sources (p232_, p218B4, p062A3).
  - That null had more damage than the target, so it was not matched. It is kept only as a
    demonstration that extra lost symbols raise the score under any key.
  - Comp's half (b) draws only from the plant side, which happens to exclude those three
    sources.
- **Files.** `j1/masknull.py`, `results/masknull.tsv`, `results/masknull_cmp.md` (per-target
  table).

## What I could not establish

- **Readability.** I make no claim about which of the 22 surviving readings are German. That
  is the reader's call, and check-'s.
  - Surviving J1(ii) means only that no wrong key with the same freedom matches the score.
  - For the units with a high unknown fraction (p071A1, p071A2, p102A, p125B, p231B2) and for
    p170D, p218C and p220B, it is a weaker statement than for the clean five.
- **Freedom beyond J1's.** I did not search wrong keys with more than 2 edits, and I did not
  search mixed keys outside HS/HT. Nor did I run a keyless solver on these units. Each would
  give the adversary more freedom than the claim had, so none is a J1(ii) test.
- **The other transcription.** I did not test whether the readings survive on creilly's
  transcription. The lead reports they do not (length errors), and detection is defined on the
  scan only (F8).
