# check-adfgvx: strand R under the pre-registration, plus the independent census

Branch `agent/check-adfgvx`. Prereg: `findings/adfgvx-1918-prereg.md` on `lead-adfgvx` (a588c31, Revision 1 a0ae584, Revision 2 accepted).
The first version of this report was written before the addenda were read. It is kept as `REPORT_v1_exploratory.md`
and is NOT a strand-R result. Everything below was re-run under the prereg. Commands: `run_all.sh`. Trials log: `trials.log`.

## 0. Compliance block (C5, C6, D1, D2, addenda)

* **Scorer freeze (C5/D1).** Scorer = `german.py` (blob `388c2c676d30ab34fc5a1c9422ffe8d03a8e2eb9`), kernels `kern.c`
  (`2f23bf345c59efbd8527550b59eab757085962d6`), `kern.py`, corpus = 14 Project Gutenberg German texts (ids and sha256 in
  `data_snapshots/gutenberg_sha256.txt`) plus, for model TEL, the published 1918 plaintexts of the OTHER key periods.
  **LIT and TEL were both fixed at commit `50b772c`** (still `50b772c` after the rebase: it is in lead-adfgvx's history; only the later decoy commit was rewritten). Both models are produced by the same `german.py` code (`model("LIT")`, `model("TEL", held_out=...)`);
  **Evidence window (referee E7).** The scorer commit `50b772c` is stamped 2026-10-31 **22:30:19**, which is AFTER my first exploratory scoring of an R entry (about 22:24). So the scorer was NOT committed before the first R scoring. That nothing changed in those six minutes rests only on the file modification time of german.py (22:20:47), which git does not record and which is my own testimony, not a verifiable fact; the files in `50b772c` are what was in use, and I know of no edit between 22:20:47 and 22:30:19. I claim: no change after any R contact that I am aware of. I do not claim it was fixed in git before contact.
  One thing was *built* after R2 contact: the file for TEL with period nov10 held out (22:24:27, first needed for R2) and TEL with nov07 held out (22:22, first needed for R1, later unused). Those are parameter instances of
  the frozen code, but strictly TEL-nov10 first existed during R2 contact. Whether to use TEL at all for R2 was decided after seeing LIT's R2 scores (D1): so the TEL choice **postdates contact**, is justified without reference to R entries (below), and
  **is counted as a trial in R2's significance**: R2 was scored in 4 configurations (scorer {TEL, LIT} x '?'-rule {mask, digit}), and the claim passes cleanly in 1 of the 4 (section 2). A Bonferroni factor of 4 on an empirical tail of "0 of 992 null cases" gives p < 0.004.
  What did happen after contact, and is disclosed: (a) the choice of TEL as the *primary* scorer for R2 was made after
  exploratory contact (LIT failed to separate there). It is justified without reference to R entries: LIT's docstring
  (committed in 50b772c) already says it lacks X-stops and digits, and a power control on 58 solved non-R entries
  (own key at L=0 beats the best wrong-key placement) gives LIT 45/58, TEL 50/58 (`results/r2_scorer_power_on_solved.json`).
  Both are reported. (b) TEL is not used for the R1 square search because on a solved non-R message (p139B) it degenerated into
  mapping frequent pairs to the digit class; LIT is used there.
* **Numerals and X-separators.** One digit class (all ten digits), X is an ordinary letter. In LIT digits get a flat 2% prior and X is rare
  (prose); in TEL both are learned from telegrams.
* **Trials log.** `trials.log` (append-only JSON lines). The v1 runs are logged as exploratory. Aborted R1 launch (8 results, `results/r1_prereg_aborted.jsonl`) is logged.
* **D2.** The R1 decoy IDs (`decoys_r1.json`, sha256 `5dc2d03c...afe28`, 100 decoys, rule in `decoys_r1.py`) were committed at **`f821aa8`** (2026-10-31 **22:46:48**, pushed to origin before any decoy was scored). After rebasing onto lead-adfgvx the same commit has sha **`81ce00b`** (stamped 23:33:54, which is the rebase time, not the original commit time); the tree content is identical.
* **Transcriptions.** creilly@e60da03 and Schmeh 2017 (`ciphertexts/adfgvx-1918-open.txt`, sha256 9362c3d2...). Dash rule verified on the 5-slot groups:
  `-`=1, en dash=2, em dash=3 lost symbols (`schmeh.py`). `results/transcr_compare.txt`: p156C3, p156C6, p179B1 are **identical** in both (including the
  15 lost symbols of p156C6); p155E differs at 2 symbols (creilly `-`, Schmeh `V`); p192A differs at 5 (creilly `-`, Schmeh `V`).
  The twins (p139B, p188_.2) exist only in creilly's. Not compared: the Bean scan.
* **All 22 keys.** R2's wrong-key null uses the 21 other keys of `keys.json` (source column in `results/r2_prereg_claim.json`: 13 Lasry, 5 Childs Jul-Aug,
  dec09_history = Childs history, chi_2017_comments = "repair key list" (Lasry's CHI key), ours_nov07_18col = creilly). I did not apply the lit
  chat's noted discrepancies (e.g. Childs's Nov 4-6 transposition lacking an element) because `keys.json` has no such key; I took each key exactly as `keys.json` gives it.
* **C4.** My plain decrypts (R1 parts 5 and 6; R2 with the claimed square and with Lasry's blank-cell square; marks `-` lost symbol, `?` blank cell) are **identical, string for string, to comp-adfgvx's** `results/adfgvx-R-decrypt.md` (compared after I had produced mine; `results/schmeh_rerun_and_c4.txt`). That agreement is [C]. The nulls below are mine alone, [S], with the samples stated.
* **C6 budgets, by table.** R1 search-family null: stage 1 6,000 restarts + stage 2 300x(10x3) + 5x(100x20), ~17 CPU s per run, identical for the 3 real runs and for each of the 120 null and 12 planted runs. R1 fixed-key rows: 100x20 square search per input, identical for the claim (10 seeds) and each null input. R2: exhaustive enumeration, no random budget: 21 lengths x (n+1) positions per (entry,key) = 4,641 for p179B1, 22 keys on p179B1, 58 entries x 21 wrong keys. R3/R4: exhaustive over 593 entries.
* **B4 (Schmeh).** Re-run on Schmeh's strings (`r_schmeh_rerun.py`): p156C3, p156C6, p179B1 are identical to creilly's (asserted in code), so every R1 and R2 number is identical and the verdicts survive; the 3 real solver runs on Schmeh's strings reproduce the committed ones exactly. R3 and R4 differ and are scored on both (section 4).

## 1. Verdicts (prereg definitions)

| claim | verdict | why, in one line |
|---|---|---|
| **R1** | **PARTIAL** (whole claim). Not split | (i) holds for part 5 outright; for part 6 only with the claimant's 2 stated corrections and 12 stated fills. (ii) cannot be established for either part: my keyless solver, the same search family, does not find the claimed key (0 of 3 real runs, 0 of 12 planted), so its null is not "at least the claimant's freedom". A split (part 5 REPRODUCED, part 6 PARTIAL) is NOT warranted: the prereg definitions require (ii) for each part separately and I have no part-5-only null with power. |
| **R2** | **REPRODUCED** under the headline rule (TEL, all '?' cells masked); **fragile**: it fails under LIT and under TEL with the digit-fill rule | (i) holds on all 97 unmasked letters. (ii) With 23 letters masked, the claim (-1.064) is the unique maximum over every (length 0-20, position) under nov10, and beats the best of 21 wrong keys on p179B1 (-1.570) and of 970 solved-entry/wrong-key cases (-1.413). LIT does not separate it. |
| **R3** | **REPRODUCED** | Best-offset statistics beat all 593 other solved entries on every statistic and both transcriptions; no null entry comes close. |
| **R4** | **REPRODUCED** | Same, on creilly's transcription. On Schmeh's the statistics are weaker (5 more symbols read, all `V`, mostly wrong) but still beat all 593. |
| **Census** | done | minimal edit distance equals comp's on 590/591; event typing does not agree (section 5). |

## 2. R2: p179B1 under nov10 with a 20-symbol gap at 160

**Is the gap marked?** No, in neither transcription (both give the same 220 symbols, no dash). The log's own header says 240 symbols (`RICHI-240`), so the length 20 is
inferred from the header and the position is not marked. Per the prereg, position and length are treated as search freedom.

**(i) Reproduction, masked (C3).** Square = `keys.json` nov10 with its 5 blank cells left blank (the claimant's fill of 5-9 is NOT used; letters in blank cells
are masked). Claim: L=20 unknown symbols inserted after log symbol 160. 23 of 120 letters are masked (20 depend on the filled symbols, 3 fall in blank cells), 97 unmasked.
All 97 unmasked decrypted letters equal the claimed reading (`r2.py`, `results/r2_repro.txt`):
`...ARMEE.ALPENKORPS RAUM PETERREVE VERBASZ ... VERSECZ VERSECZ VON SERBEN BESETZT`. 50 quadgrams lie entirely in unmasked letters and are scored.

**The '?'-cell rule (one headline).** The claimant filled the 5 blank cells of nov10 with digits 5-9 taken from a 2017 comment; a wrong key has 0-14 blank cells. HEADLINE RULE = **mask**: every '?' cell of every key, the claim's included, is unknown
and any letter that lands on it is masked (so the claimant's fill is not used and nobody gets cell-filling freedom; it is the one rule that treats claim and null identically without assuming what a blank cell holds). Other rules are reported as they come
(`r2_rules.py`, `results/r2_rules.json`): **digit** (every '?' cell of every key is a digit: the claimant's fill applied as a rule to all keys) and **complete-square-only** (mask rule, only wrong keys with at most 2 '?' cells: 11 of the 21).
Gap masking (C3) holds in all rows: the claim has 23 masked letters under mask (20 depend on filled symbols, 3 on blank cells), 20 under digit.

**(ii) Null** (`r2_prereg.py`, `r2_rules.py`; exhaustive over the stated grid; one implementation, so [S]-grade). Statistic = mean log10 probability per fully-unmasked quadgram, placements with at least 40 such quadgrams. Compared: the claim; every (L in 0..20, g in 0..220)
under nov10; the same grid under each of the 21 wrong keys on p179B1 (4,641 placements each); and 58 solved entries (200-250 symbols, clean, periods nov01 nov04 nov07 nov10 nov13_16 nov22, seeded draw logged in `trials.log`) under each of their 21 wrong keys
(TEL trained with that entry's own period held out; 970 (entry,key) maxima have a valid placement under mask, 1,218 under digit).

| scorer | rule | claim (nq) | best placement under nov10 | best wrong key on p179B1 | best solved-entry/wrong-key case | claim wins? |
|---|---|---|---|---|---|---|
| **TEL** | **mask (HEADLINE)** | **-1.064** (50) | **(20,160) itself**; next g=158 -1.073 | -1.570 (nov01) | -1.413 | **yes**, 0.35 per quad over the best null; same with complete-square keys only |
| TEL | digit | -1.041 (55) | (20,145) -1.005; (20,160) is not the best | -1.341 | **-1.037** | **no**: loses to one solved-entry case by 0.003, and to g=145 under its own key; complete-square keys only: wins (-1.413) |
| LIT | mask | -1.885 (50) | (20,215) -1.725 | -1.828 | -1.548 | **no** |
| LIT | digit | -1.986 (55) | (20,141) -1.550 | -1.786 | -1.633 | **no** |

Reading it:

1. The claim passes cleanly in **1 of 4** configurations. The TEL-digit failure is small and comes from wrong keys with many blank cells, whose cells become digits, which TEL (trained on telegrams with digit runs) scores generously: that is the same digit-gaming that stopped me using TEL in the R1 square search, so I regard the digit row as contaminated, not as evidence against the reading, but it is a failure and is reported.
2. Under the headline row the claimed placement is the sharpest on offer, but its margin to g=158 is 0.009 per quad (about 0.5 log10 over 50 quadgrams): 160 is preferred, not proven. That agrees with the claimant qualitatively and not with a 99% figure.
3. LIT fails in both rules. The power control (section 0) says why: LIT picks the true key over the best wrong-key placement on 45/58 solved non-R entries, TEL on 50/58. The claim is a telegram, full of X and digits, and LIT is a prose model.
4. The reading's digits (`11`, `217`, `216`, `9`) depend on the blank cells; they are masked in the headline row and are therefore NOT supported by it.
5. Significance with the trials counted: 4 configurations tried (2 scorers x 2 rules), 1 passes; the headline tail is 0 of 991 null cases (21 wrong keys + 970 solved-entry cases), so p < 1/991, times 4 configurations = p < 0.004, if the null cases were exchangeable with the claim (they are not exactly: the claim is longer-gapped and has fewer quadgrams).
6. Both transcriptions agree on this entry, so the result is not transcription-sensitive.
7. The v1 Viterbi-best-fill scan (exploratory, `REPORT_v1_exploratory.md`) is an extra row, not the pre-registered statistic: it gave the claim a margin of 0.37 per quad (TEL) and 0.002 (LIT).
8. **If a referee rules that LIT was the declared scorer, or that the digit rule is the equal-freedom rule, this verdict becomes PARTIAL.**

Not done: the claimant's "four separate groups of five" gap variant; gap placements inside the middle of the stream with unequal run lengths (only one contiguous block is searched, as claimed).

## 3. R1: p156C3 + p156C6 under the 18-column key

**C2: block structure.** The claim (creilly README) transposes the two parts **separately**, each under the same 18-column key (part 5: 132 symbols, 8 rows; part 6: 108 symbols, 6 rows).
So (i) requires each part to read on its own, and joining the two parts under one key is one trial.

**Which square.** `transcr_compare.py`: the 24 known cells of the claimed square agree with every one of the other 21 keys' squares in at most 1 cell of 15-24 compared
(chance 0.4-0.7). It is not a known period square. The case is therefore the recovered-square one (transposition and square both unknown), not A5's known-square case.

**(i) Reproduction** (`r1_repro.py`, `results/r1_repro.txt`; creilly = Schmeh transcription here).
* Part 5 decrypts under key + claimed square to `ANORDNUNGENVOM2TEN11TENNR858BEZIEHENLASSENSOWEITNOCHNICHTGESCHEHEN`, 66/66.
* Part 6: 54 letters = 37 equal to the claimed reading, 1 mismatch (L, needs the claimant's stated correction A->X), 1 in an unknown cell (E, second stated correction), 15 with a lost symbol
  (12 stated fills, 3 open). Re-encrypting the reading reproduces 220 of 222 logged known symbols; the 2 exceptions are the 2 corrections. So (i) holds only if the 2 corrections and 12 fills are accepted as "stated edits"; strictly, 12 letters are not determined by the decrypt.
* The square is consistent: no pair maps to two letters and no letter to two pairs, apart from the two corrected positions.

**(ii) The search-family null** (`r1_solver.py`, `tsearch.c`, `r1_run.py`). Family: width-18 transposition + square, both unknown, on the pooled pair stream of both parts.
My solver: stage 1 hill-climbs the transposition on the index of coincidence of the pair stream (6,000 random restarts, swap and insertion moves), keeps the 300 best distinct optima; stage 2 hill-climbs
the square on the LIT quadgram score for each (10 restarts x 3 kicks), then 5 best get 100 x 20. Statistic = best total log10 / scored quadgrams.
**Budget (C6): identical for the real entry and every null: stage 1 6,000 restarts; stage 2 300 x (10x3) + 5 x (100x20); about 17 CPU seconds per run.**
Null inputs: 60 shuffles (known symbols shuffled within each part, the 15-symbol hole fixed) and 60 decoys (`decoys_r1.json`, committed `f821aa8`: first 132 symbols of one real
Lasry-period entry and first 108 of another, true widths 16-23 (Lasry period keys) and never 18, 6, 9, 12 or 36, different squares, hole at 5..19), plus 12 planted controls and 3 real-entry runs.

Results (`results/r1_prereg.jsonl`, `results/r1_prereg_analysis.txt`; statistic = best per-quad LIT score, higher is better):

| inputs | runs | mean | sd | max |
|---|---|---|---|---|
| shuffled ciphertext | 60 | -1.069 | 0.024 | -0.996 |
| real decoys (other widths, other squares) | 60 | -1.041 | 0.029 | -0.978 |
| **real entry (claim), my solver** | 3 | -1.058 | 0.015 | -1.042 |
| planted controls (truth hidden from the solver) | 12 | -1.025 | 0.031 | -0.955 |
| claimed key, scored by the same stage 2 (10 seeds) | | | | **-0.9432** |

* My solver, on the real entry, **returned the claimed key in 0 of 3 runs**, and on planted controls the exact key in **0 of 12** (the claimant reports 10/24 for theirs). On planted data the spurious keys it finds score
  as well as or better than the true key under this scorer; stage 1 (index of coincidence on about 105 pairs) is not selective enough. My search family is therefore much less powerful than the claimant's.
* Null max over the 120 search-family null runs: -0.978. The claimed key's score -0.9432 exceeds it, by 0.034 per quad (about 2.6 log10 over 76 quadgrams; 3.7 null sd above the null mean).
  This is a statement about the claimed key as an outlier, not a replication of the search: my solver did not reach it.
* Power: only 1 of 12 planted controls scores above the null max, so with my solver a true message of this size is mostly indistinguishable from the null. That limits what the null can say.

**Fixed-key rows (additional; claimed key given, square searched 100x20 per input, identical budget on every row; `r1_fixed.py`, `results/r1_fixed.txt`).**

| inputs | n | mean | sd | max | claim -0.9432 |
|---|---|---|---|---|---|
| random width-18 keys on the real ciphertext | 100 | -1.326 | 0.054 | -1.192 | exceeds all, margin 0.249 |
| shuffles of the real ciphertext, claimed key (hole fixed) | 100 | -1.346 | 0.040 | -1.263 | exceeds all, margin 0.320 |
| real decoys (committed IDs) under the claimed key | 100 | -1.313 | 0.050 | -1.185 | exceeds all, margin 0.242 |

These are fixed-key tests: the claimed key is a large outlier from nulls of all three kinds. They do not replicate the claimant's search and carry no correction for how many keys the claimant tried.

**The gap, stated.** The claimant's search used a structural split of the columns by symbol statistics plus about a CPU-hour of hill-climbing per search, and found the key in 10 of 24
planted trials. Mine is weaker and cannot be made equivalent without reimplementing their method. Whether the claimant searched widths other than 18 is not documented
(the README tests squares at widths 15-25, plans the search for 18); that is up to 11 widths of search freedom not in my null, and joining the two parts is a counted trial.
So (ii) in the prereg's sense cannot be established, and the verdict is PARTIAL by definition.

**Still exploratory (v1, pre-prereg design, scorer unchanged):** the free square search on the claimed key recovers 60/66 letters of part 5 and 18/24 square cells from the key alone; all 153 two-position swaps of the key score worse (best -0.984, a strict local optimum). Cited, not relied on.

**Part 6 is weaker than the headline.** 37 of its 54 letters read; 2 are corrections chosen to fit (each picked from about 108 symbols x 5 alternatives, motivated by the word it repairs); 12 are fills chosen by reading; 3 are open.
A square learned from part 5 alone reads 24 of the 34 part-6 letters whose pairs it has seen. "Solved apart from three letters" overstates part 6.

## 4. R3 and R4

Statistics fixed before running (`r34_prereg.py`): S1 Smith-Waterman local score (+2/-2/-3, lost symbol scores 0) = best offset, gap-aware; S2 semi-global Levenshtein distance of the open entry
against any substring of the other; S3 best ungapped offset (matches among compared pairs, at least 40 compared). Null = every other solved entry in the log (593 entries, excluding the twin and the open entry), reported
over all, over the twin's key, and over the twin's date. Empirical tail = number of null entries at least as good as the twin (0 of N means p < 1/N, N stated).

| | statistic | open vs twin | best of null (all 593) | null entries as good |
|---|---|---|---|---|
| R3 creilly | S1 / S2 / S3 | 170 / 11 / 88 of 102 at offset 210 | 20 / 39 / 37 | 0 / 0 / 0 (p < 1/593) |
| R3 Schmeh (`v`->V) | | 170 / 11 / 89 of 104 | 20 / 40 / 37 | 0 / 0 / 0 |
| R3 Schmeh (`v` lost) | | 170 / 11 / 88 of 102 | 20 / 39 / 37 | 0 / 0 / 0 |
| R4 creilly | | 87 / 19 / 52 of 79 (offset 0) | 21 / 26 / 29 | 0 / 0 / 0 |
| R4 Schmeh | | 79 / 24 / 52 of 84 | 21 / 29 / 30 | 0 / 0 / 0 |

Same-key subsets (R3: 100 nov04 entries; R4: 49 nov13_16 entries): 0 null entries as good on any statistic. Same-date subsets are in `results/r34_prereg.json`.
The claimant's figures check out: R3 "88 of 102 at a fixed offset" (S3), R4 "63 equal against 16 different" (Levenshtein alignment, `results/r34_detail.json`: 63 equal, 16 different, 11 lost, 6 missing).

Plaintext from the twin's key (reported as plaintext, not as a second test, C7): R3 adds nothing, p139B is already read and p155E decrypted alone is noise; as the tail of the 314-symbol transposition only 6 letters
have both symbols in the tail (3 agree). R4, reconstructed onto the 96-symbol grid, determines 31 letters of p188_.2's plaintext, 22 agree, 9 differ. The claimed `Gestellung Auto unmoeglich` rests on one letter
(letter 13: p192A reads O, p188_.2's log reads U, giving `AUTUUN`); at letter 16 p192A reads U where p188_.2 reads M, which the claimed reading rejects.
Differences between transcriptions matter for R4: Schmeh's five extra readable symbols are all `V`, and they make the match worse (S2 24 vs 19), so creilly's `-` marks are the safer reading.

Headers disagree for R4 (`CZ v OM, 12 Nov` vs `CM v CZ, 13 Nov`), and R3's pair are a day apart, so these are retransmissions or re-receptions; not decided here.

## 5. Census

Unchanged from v1 apart from priority (`results/census_summary_printed.md`, `results/census_check_printed.tsv`): 595 messages; 451 with zero edits; mean 1.71 symbol edits per message
(median 0, p90 5, p95 8, p99 25, max 194); 0.79 symbol edits per 100 sent symbols. Selection: only readable messages are counted, so these are lower bounds for the whole log.
Vs comp (read only after my census was committed at 50b772c): minimal edit distance identical on 590/591 common messages (p059B differs by 1: comp aligned to the page re-reading);
event typing differs (comp 403 events, mine 250; 41/591 messages) because of tie-breaking among equal-cost alignments; recommend fixing the cap in symbol edits.
Both programs are alignment dynamic programs, so [C] on edit distance is subject to "no shared method" being only partly true.

## 6. What is not established

* R1 (ii): see section 3; the claimant's freedom is not replicated.
* R2: verdict depends on the primary scorer; blank-cell digits untested; the claimant's four-groups-of-five variant not run.
* R3/R4: nothing about retransmission versus double reception.
* All: the Bean scan was not consulted; C4 agreement with comp is pending.
* Census: E7/E8 not typable; selection bias not quantified.
