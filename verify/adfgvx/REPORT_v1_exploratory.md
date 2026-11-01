> **EXPLORATORY (v1).** Written before the prereg addenda (tickets tmvx73kgy75mi, tmvx7943upnzn, tmvx7a10qu6pt, tmvx7dv1vfs8f) were read. Nothing here is a strand-R result; see `REPORT.md`. Scorer and corpus are unchanged since commit 50b772c, so these numbers are what that scorer gives, but the designs (nulls, decoys, masking, search family) were not pre-registered.

# check-adfgvx: independent ADFGVX implementation, replication of R1-R4, independent census

Branch `agent/check-adfgvx`. Written 2026-10-31 / 2026-11-01 by the second-implementation chat.
Everything below was produced by code in this directory. Commands to re-run each number are in
`run_all.sh`; raw outputs are in `results/`.

## 0. Verdicts

| claim | verdict | one line |
|---|---|---|
| **R1** p.153 pair, new 18-column key | **PARTIAL** (key and part 5 REPRODUCED; part 6 and "all but three letters" not) | Part 5 decrypts to the claimed 66 letters, and a free square search on the claimed key alone re-derives 60/66 of them. Part 6 reads where the log has symbols (37 of 38 letters), but 2 letters need a corrected log symbol, 12 are filled by reading and 3 stay open. |
| **R2** p.176 GGDAA, nov10 key + 20-symbol gap at 160 | **REPRODUCED**, with two caveats (section 3) | The claimed fill gives the claimed reading, all 100 non-gap letters match. Under a telegram-style scorer it beats every wrong key and 400 random controls by a wide margin. A literary-German-only scorer does NOT separate it, and the gap position is a plateau (158-162), not a point. |
| **R3** p.152 p155E = copy of last 104 symbols of p139B | **REPRODUCED** | 88 of 102 readable symbols equal at the fixed offset 210 (chance 17.0 +- 3.8). Contributes nothing new to read: p139B is already fully read. |
| **R4** p.189 p192A = damaged copy of p188_.2 | **REPRODUCED** | 63 equal / 16 different / 11 unreadable / 6 symbols missing, exactly the claimant's 63/16. The claimed "AUTO" rests on ONE letter that disagrees with p188_.2's own log. |
| **Census** | done, [C] on minimal edit distance (590/591 equal to comp's); event typing is NOT stable | see section 6 |

Labels follow CLAUDE.md. "One implementation" means exact but not yet two-implementation [C].

## 1. Sources, hashes, independence

Data used (nothing else from the third-party repos):

| file | where | sha256 |
|---|---|---|
| `data/records.json` (688 entries) | github.com/creilly11235/adfgvx-1918 @ `e60da03db4ea673c70c8c3286a4dc4d37176909c` | `4a27e2e163ef73ca5c20f3c6cb67942258eaed25a77c966bd96616a549c37c40` |
| `data/keys.json` (22 keys) | same | `095de9ce1e9ec903db6bf9588b4fa8932272d7fc49ab6f9d5925d5008116f2a7` |
| `data/messages.json` (claimed 2305 and p153 keys, fills, corrections) | same | `beed069aaf8a302f3da4c4abdef7ca9e8da61faedff990f5225ccddb42c674f1` |
| `README.md` (claim wording, claimed readings) | same | read, not hashed (prose; reading copied into `r1_repro.py` and `r2.py`) |
| `docs/PAPER.md` (section 3 catalogue E1-E8) | github.com/0wwafa/adfgvx-1918 @ `083921732d7c18e52424336ab4160fada5c61b4b` | `c04300d58094cc7b301eae6f970688d0c3aeeb0a8d4b2a68c376cf8bcdd58c53` |
| issue #1 (R3, R4 claims) on 0wwafa/adfgvx-1918, author AyushAg1002, 2026-10-28 | copy in `data_snapshots/issue1_0wwafa.json` | `8fcb5783b76666f1b05174fdd77eab0ca16533023c1f0f0745a16979aa709059` |
| 14 Project Gutenberg German texts (scorer training) | ids in `german.py`, hashes in `data_snapshots/gutenberg_sha256.txt` | listed there |

Not read: their `scripts/`, `src/`, any score or alignment code; this repo's `search/` (harness-denied). I never opened
`results/adfgvx-mutilation*` until my census was committed and pushed (commit `50b772c`);
comp's files were read afterwards from `origin/agent/comp-adfgvx`.

Honest limit on independence: creilly's README describes their method in prose (hill-climbing the square, an exact
dynamic program over the six candidates of a lost symbol). I read that prose, so my R1 and R2 use the same *families*
of method. The code, the scorer (my own quadgram model, different corpus), the nulls and all numbers are mine.
All four checks use creilly's transcription (`printed` / `ciphertext`). I did not compare against Schmeh's
transcription or the Bean scan; whether R1-R4 survive other transcriptions is untested.

## 2. Task 0: my decrypter, validated

`adfgvx.py` (textbook: 6x6 square labelled ADFGVX; keyed columnar transposition; `trans[i]` = read-out rank of the
column at block position i, ciphertext = columns concatenated in rank order, short columns on the right).
Convention discovered by testing and then fixed: the key lists in `keys.json` are per-position ranks.

`step0_validate.py`, all 595 entries that have a published plaintext and a key:

* **511 of 595 decrypt cleanly** from the entry's `ciphertext` field, meaning every position agrees with the published
  plaintext, where unknown plaintext marks (`-`,`?`,`_`,`#`) and unknown symbols match anything. 317 of those 511 are
  also strict (no wildcard anywhere). One implementation, exact.
* All **465** entries filed "period key, as transcribed" decrypt cleanly.
* The other 84 do not: 79 "length repaired" (by construction), 3 "model read", 1 "blind readings", 1 "known key repair (2 edits)".
  Their published plaintext is consistent with the key only via edits to the log. Those edits are what the census
  (section 6) measures, by re-encrypting the plaintext, so they are validated that way (451 of 595 re-encrypt with
  zero edits, 144 need at least one).
* Of the 511, 60 are not zero-edit against the log transcription: 44 entries whose `ciphertext` field is a page
  re-reading, not the log transcription, plus 15 with one orphan trailing symbol, plus 1.

## 3. R2: p.176 GGDAA (p179B1) under nov10 with a 20-symbol gap at 160

Claim (creilly README, `messages.json`): square `4ARUT1OIFSKN35BZPVLD6JMXCWHQ2E7G08Y9` (5 blank cells filled 5-9 from
a 2017 blog comment), transposition `9 12 7 11 3 8 16 6 14 2 10 15 5 13 1 4`, a block of 20 lost symbols inserted
after log symbol 160.

**Reproduction** (`r2.py`, `results/r2_repro.txt`). With the claimed fill `DFFXXDXXVVXDXXXVXXAF` inserted at 160, the
decryption is `ANXOXHXLXX11XARMEEXALPENKORPSRAUMXPETERREVEXVERBASZXX217X216X9XRXDXLINIEXNAGYBESKIEREKXVERSECZXVERSECZX
VONSERBENBESETZTX`. All 100 letters the README prints as known equal the decryption (0 mismatches). My own exact
Viterbi fill, with no knowledge of the claimed fill: with the TEL scorer it agrees with the claimed fill on 17 of the 20 gap letters
(it cannot tell digits apart; the other differences are `KI` -> `ON` in NAGYBES-KI-EREK, i.e. `NAGYBESONEREK`) and reads
ARMEE ALPENKORPS RAUM PETERREVE VERBASZ VERSECZ VERSECZ VON SERBEN BESETZT; with the LIT scorer it agrees on only 11 of 20
(`RNXOXHXLLX00XARMEEXALPENNORPSRAUM...`), which is why scorer choice matters (section below).

**Null: the same gap model under every wrong key** (`r2_null.py`, `r2_analyse.py`). For each of the 21 other keys in
`keys.json`, a block of 20 unknown symbols at each of 221 positions (0..220), exact Viterbi best fill, score = best total
log10 quadgram probability / 117. Exhaustive over that grid (one implementation). Two scorers, two treatments of
unknown ("?") square cells:

| scorer | claim@160 | best wrong key (any position) | margin |
|---|---|---|---|
| **TEL** (Gutenberg + 1918 telegrams of the OTHER key periods, nov10 held out), `?` = digit | -1.004 | -1.374 (nov13_20, g=105) | **0.37 per quad = 43 log10** |
| TEL, restricted to the 11 wrong keys with a (nearly) complete square | -1.004 | -1.627 (nov25) | 0.62 per quad = 73 log10 |
| TEL, `?` cells may be any letter | -1.004 | -0.795 (nov13_20) | **-0.21: the claim LOSES** |
| LIT (Gutenberg only), `?` = digit | -1.764 | -1.766 (ours_nov07_18col, g=107) | 0.002: no separation (z=3.0 over 4,641 cells) |
| LIT, restricted to complete-square wrong keys | -1.764 | -1.776 (nov07) | 0.012 |

Reading these honestly:

1. The two "claim loses/ties" rows are properties of the scorer and of the null, not evidence against the reading.
   LIT is trained on prose and punishes X and digits, which fill this message. In the `?`-any rows a wrong key with
   12-14 unknown cells can pick a free letter for each unknown cell at every occurrence, which hands the null far more
   freedom than the claim has. Keys with that many holes cannot be tested this way at all.
2. Under the scorer that fits the data (TEL), the claim wins by a wide margin. Extra nulls, TEL, best over all 221
   positions: 200 random 16-column transpositions with the claimed square (mean -1.666, sd 0.063, max -1.497; claim
   -1.004; z=10.5); 200 shuffles of the log (max -1.506); claimed transposition with each of the 21 other squares
   (best -1.316). The claim exceeds all 421 [S].
3. **The gap position is a plateau, not a point.** TEL scores for g=156..166 are -1.095 -1.043 -1.005 -1.010 -1.0037
   -1.0037 -1.0037 -1.042 ... : 158, 160, 161, 162 are within 0.006 per quad. Best placement outside g=154..167 is g=168,
   9.5 log10 below. So a gap in the window 158-162 is supported; "99% on exactly 160" is not something my scorer can
   reproduce. It does not change the reading. (LIT prefers 161-162.)
4. Dependence on the blank cells: the digits in the reading (`11`, `217`, `216`, `9`) rest on the blog commenter's
   filling of the five blank cells. Not checked here.
5. The reading itself (ARMEE, ALPENKORPS RAUM, PETERREVE, VERBASZ, NAGYBESKIEREK, VERSECZ, VON SERBEN BESETZT) is
   real German military text with geography. That is the main evidence. The scorer comparisons only show that it is not
   a generic product of the gap model.

Not done: the "four separate groups of five" variant (194,756 placements) of the claimant's search.

## 4. R1: p.153 pair under the 18-column key

Claim: transposition `16 7 13 4 15 8 17 3 1 12 14 2 5 9 10 18 11 6`; square (24 of 36 cells known)
`?TXUGI????8?2WO?CMB1?SZ?5NDH?VEA??LR` (`messages.json`; equals the table in the README).

**Which square, and the reading from key + square** (`r1_repro.py`, `results/r1_repro.txt`):

* Part 5 (p156C3, 132 symbols, 18 columns, 8 rows): decrypts to `ANORDNUNGENVOM2TEN11TENNR858BEZIEHENLASSENSOWEITNOCHNICHTGESCHEHEN`, **66/66** equal to the claimed reading.
* Part 6 (p156C6, 108 symbols, 15 lost): of 54 letters, 38 decrypt to a letter with no hole; 37 equal the claimed reading,
  1 (the second L of ARTILLERIE) is G in the log (pair AV) and needs the claimed correction A->X. One letter (the E of
  MELDEN, pair AA) falls in an unknown cell and needs the second claimed correction A->X. The remaining 15 letters have a
  lost symbol: 12 filled by reading, 3 open. So 37 + 2 + 12 + 3 = 54.
* Round trip: re-encrypting the claimed reading under the claimed key and square reproduces 220 of the 222 logged known symbols; the 2 exceptions are exactly the 2 corrected symbols. This only shows consistency.
* The implied pair->letter map has no conflict apart from the two corrections (AV: L or G; AA/XA: E).

**Reproduction from the transposition key alone** (`r1_null.py`, `r1_part6.py`). I hill-climb the 36 cells of the square
(my iterated local search, LIT scorer, nothing about the claimed square used) on the decrypted pair streams of both parts.
Result at 400 restarts x 40 kicks, best of 8 seeds: part 5 reads
`ANORDNUNGENKOPFTENMMTENNR0V0BEZIEHENLASSENSOWEITNOCHNICHTGESCHEHEN`, **60/66** letters equal to the claimed reading
(digits treated as one class); 18 of the 24 claimed square cells recovered. The six misses are the rare cells (VOM2,
11, 5). Square learned from part 5 alone and applied to part 6: 34 part-6 letters have a pair seen in part 5, 24 agree.
So the key and part 5 reproduce from the key alone; part 6 does not independently reach the claimed text.

**Nulls** (same optimiser, same effort, same LIT scorer, statistic = best total log10 / 76 scored quadgrams;
the 15 lost symbols break the text identically in each):

| | n | mean | sd | max | claim -0.9432 |
|---|---|---|---|---|---|
| random 18-column keys | 736 | -1.336 | 0.048 | -1.192 | exceeds all, z=8.2 |
| ciphertext shuffled within each part, claimed key | 486 | -1.354 | 0.044 | -1.173 | exceeds all, z=9.4 |
| the 153 two-position swaps of the claimed key | 153 | -1.191 | | -0.984 | exceeds all by 0.041 |

* [S] sample sizes as stated; the optimiser is a heuristic, so null scores are lower bounds. At 4x effort (48 of the
  random keys re-run at 400x40) null scores rose by 0.020 on average (max 0.049); the claim does not move (16 runs, best
  -0.9432 reached in 10/16). Correcting by +0.05 leaves the claim above every null.
* Gumbel extrapolation (method of moments) gives P(null >= claim) ~ 1.4e-5 (random keys), 3.1e-6 (shuffles) [H]. That is
  a single-key test. The claimed key was picked out of a very large search by the claimants; my null cannot remove that
  selection, only say the key scores far above anything a random key reaches. With a few hundred fully scored candidates
  the claim stays significant, with 10^5 or more it would not on the score alone. The words in part 5 are the stronger evidence.
* Sharpness: all 153 swaps of two positions lose score, so the key is a strict local maximum, not a ridge.

**What is not reproduced.** "Solved apart from three letters" overstates part 6: its 54 letters are 37 read directly, 2
corrected to fit (each correction is a chosen one of ~108 symbols x 5 alternatives, motivated by the word it fixes),
12 filled by reading in the lost groups, 3 open. The corrections are consistent with the census (typical damage is
0.8 symbol edits per 100 symbols, so 2 in 240 is ordinary) but they are post-hoc. I tried a TEL-scored hill-climb first;
it degenerated into mapping the frequent pairs to the digit class (digits are autocorrelated in telegrams), so the R1
free-square search uses LIT only. This is the only scorer variant dropped.

## 5. R3 and R4

`r34.py`, `r34_detail.py`, `results/r34_detail.json`, `results/r34_sw.txt`. Symbol chance probability from the
log's own letter frequencies: sum p_i^2 = 0.1672.

**R3: p155E (104) vs p139B (314, nov04).**

* Fixed offset 210 (last 104 symbols), no indels: **88 of 102 readable symbols equal** (the claimant's figure; p155E has 2
  unreadable). Chance 17.05 +- 3.77; binomial tail 2e-53. Best other offset in p139B: 29.
* Levenshtein alignment vs the last 104: 91 equal, 10 substitutions (5 of them in the first five symbols), 1 deletion,
  1 insertion, cost 12. Cost of the same alignment against 20,000 composition-preserving shuffles of p155E: min 54, mean
  67.6 [S].
* Smith-Waterman against all 682 other log entries: p139B 170; next best 20 (p123B1); shuffle max 26 over 20,000 [S].
* Decrypt: p155E alone (as a 104-symbol message) under nov04 gives noise (`CTEKBU0MUOEAT9W?IYL...`); no key in
  `keys.json` makes it read (best LIT per-quad -1.2, junk). Placed as the tail of the 314-symbol transposition, only 6
  letters have both symbols inside the tail; 3 agree with p139B's plaintext, 3 do not (the substitutions). **p155E adds
  nothing to read:** p139B re-encrypts to its log with zero edits (census).
* Note the two headers: NKJ v LP, p139B 6 Nov 6.16 pm, p155E 7 Nov 9.10 pm. A day apart, so a retransmission rather
  than a second reception of one transmission. Not decided by this data.

**R4: p192A (90, 11 unreadable) vs p188_.2 (96, nov13_16).**

* Levenshtein alignment: **63 equal, 16 different, 11 unreadable (wildcard), 6 symbols of p188_.2 missing in p192A**
  (cost 22): the claimant's 63/16 exactly. Expected equal by chance among 79 compared: 13.2; binomial tail 1.4e-34.
  Shuffle min cost 44 (20,000), mean 53.6. Smith-Waterman 87 vs next best 21 over 682 entries [S].
* The 16 substitutions are mostly V/X/F confusions (V->X x4, F->V x4, X->V, ...), plausible for Morse reception.
  The copy is far worse (20% symbol error) than R3's.
* The alignment is not unique: with different gap costs the 6 deletions near the end could trade against substitutions.
  The 63/16 figure is for unit-cost Levenshtein.
* Decrypting the reconstructed 96-symbol stream (missing symbols unknown) under nov13_16 determines 31 letters:
  22 equal p188_.2's published plaintext, 9 differ. Decrypted as a 90-symbol message it is noise.
* Published p188_.2 plaintext is `GESTELLUNGAUTUUNMOEGLICH...` (exactly what its log decrypts to). The claimed reading
  `Gestellung Auto unmoeglich` needs letter 13 to be O: p192A gives O there, p188_.2's log gives U. At letter 16
  p192A gives U where p188_.2 gives M, which the claimed reading rejects. So the new content is one letter chosen
  between two noisy witnesses; it gives a word, which is mild support. Letters 4 and 37 (p192A: C, C; p188_.2: E, E)
  show the same copy-error pattern.
* Headers disagree: p192A is "CZ v OM (7.15 a.m., November 12th)" filed 14 Nov; p188_.2 is "CM v CZ (18.03 p.m., November 13th)".
  The copy would be earlier than its source, under a different call-sign order. Either a header error or a different
  event; not resolved.

## 6. Census

Method (`census.py`, own code): for each of the 595 entries, re-encrypt the published plaintext under its key (wildcards
for unknown plaintext marks, digit-cell set for `#`), align the sent stream S against the logged transcription
(`printed`, the log as transcribed; Gotoh affine gap: substitution 1, gap 1 + 0.05 per symbol; an unreadable log symbol or
wildcard matches anything at cost 0), and group the edit script into events. Typing, applied literally from PAPER.md section 3:
E1 gap in the log (symbols missing), E2 extra symbols, E3 a gap or extra run of a multiple of 5 that can be slid
cost-neutrally to a 5-group boundary, E4 unreadable symbol, E5 substitution, E6 one interim-stream insertion/deletion
(tried on every message with cost >= 1.5, adopted if it lowers the event count). E7 and E8 are key-level and cannot be
typed per message from this data. Per-message table: `results/census_check_printed.tsv`.

Results (595 messages, 128,380 sent symbols; `results/census_summary_printed.md`):

| | |
|---|---|
| messages with zero edits | 451 (75.8%) |
| events per message (mean) | 0.42 ; per 100 sent symbols 0.195 |
| distribution of events per message | 0:451, 1:90, 2:28, 3:13, 4:7, 5:2, 6+:4 |
| events by type (events / symbols) | E1 49/206, E2 110/437, E3 45/300, E5 43/43, E6 3/3 (E3 = 45 five-multiple runs) |
| E4 unreadable symbols in the log | 895 = 0.70 per 100 logged symbols |
| unit-cost symbol edits per message | mean 1.71, median 0, p90 5, p95 8, p99 25, max 194 |
| symbol edits per 100 sent symbols (sum/sum) | 0.79 |
| as-transcribed entries (465) | 16 edits in total, all one orphan trailing symbol |
| all repaired/other entries (130) | 1.80 events per message, 0.79 per 100 symbols |
| edits per 100 symbols by length class | <100: 0.32; 100-200: 0.22; 200-300: 0.20; 300+: 0.14 (events) |

Things the lead needs before fixing a cap:

* **Selection.** This is the census of messages that someone could read. The 83 unsolved entries are, almost by
  definition, the worse ones, so these rates are a lower bound for the log as a whole. A cap taken from this table
  would be a cap on the *readable* damage.
* The largest outliers are not damage: p149C1 (log 367 symbols, reading covers 176; 190 symbols are unread remainder),
  p135B (71 symbol edits against the log, but ONE interim-stream deletion (E6) explains all of it; both censuses see this).
* The four "Partially solved" entries (p075A2, p174A1, p190D1, p216_3: 30-40% wildcards) are in my census and not comp's.

**Comparison with comp-adfgvx's census** (`census_compare.py`, `census_lev.py`; comp's `results/adfgvx-mutilation.csv` read
only after my commit):

* Common messages: 591. **Minimal unit-cost edit distance equal on 590/591** (my Levenshtein run `census_lev.py` against comp's `cost`).
  The one difference: p059B, mine 4, comp 3, because comp aligned against the page re-reading (168 symbols) and
  I against the log (169). [C] on edit distance, with the caveat that both programs are alignment dynamic programs, so
  "no shared method" is only partly true.
* **Event typing is NOT stable between the two.** Same number of events on 556/591; identical type counts and symbol cost on
  550/591. Overall: comp 403 events (E1 128, E2 134, E3 33, E5 108) vs my 250 (E1 49, E2 110, E3 45, E5 43, E6 3). The 41
  disagreeing messages come from (a) comp counting a 5-symbol deletion as 2-3 separate E1 events where I count one E3 run
  (my affine gap cost prefers one contiguous gap; theirs is unit cost with a tie-break, and 118 of their messages have
  more than one optimal alignment); (b) substitution-versus-indel trades in damaged messages (p162A, p163B, p178C3,
  p193_, p153B3: both are minimal, they pick different optima); (c) p135B, where comp reports the 70 ciphertext-space
  events and separately notes that one E6 explains it, while I report only the E6 reading.
* Recommendation: fix the cap in symbol edit distance (and let the search enumerate gap placements itself), not in
  typed events. The typing depends on a tie-break rule and the same data gives 250 or 403 events.

## 7. What is still not established

* Transcription dependence of all four verdicts (creilly's transcription only).
* R1: whether the claimed key was found among so many candidates that the score alone would be unremarkable; the fills in
  part 6; the three open letters.
* R2: the blank-cell digits; the four-groups-of-five variant; plateau 158-162.
* R3/R4: nothing about whether duplicates are retransmissions or double reception.
* Census: E7/E8 are not typable here; the selection bias is not quantified; typing rule not agreed with comp.
* Trials factor of this work: scorers tried LIT, TEL (TEL dropped for the R1 hill-climb, kept for R2 scans and shown);
  R2 nulls report all four (scorer x `?` treatment) combinations; no other variants were examined.
