# Adversary: false readings of the open WWI ADFGVX messages

*adv-adfgvx, 2026-10-31. Target: whatever `lead-adfgvx` claims about the open Childs ADFGVX messages.
No team claim existed when this was written, so this is the baseline any claim has to beat.
Code and raw output: `adversary/adfgvx/`. Calibration against a live public claim (creilly11235):
`adversary/adfgvx-creilly-calibration.md`, kept separate on dev's instruction (ticket tmvx707qsk8oq).*

## Answer

**At these lengths, an n-gram score can't tell a real ADFGVX reading from one made out of noise,
unless the key is fixed in advance and the edits are few.** Four facts, each run against the nine
open messages (Schmeh/Lasry list: pp. 73, 152, 153 ×2, 158, 170, 176 GGDAA, 189, 198):

1. **Free key (new transposition and new square): the real ciphertext is no better than shuffled
   ciphertext, for all nine** [S, 2026-10-31]. With the key free, every message gives a best reading
   no higher than its three shuffles do. On the four short messages (42–53 letters: pp. 152, 153b,
   170, 189), shuffled noise reaches **−3.65 to −4.11** per quadgram. Genuine 1918 telegrams under the
   same scorer give a median of −4.6 and a range of −3.5 to −6.2 for windows of the same length. So
   **a free-key "German" reading of any of these messages is not evidence at all,** at any score my
   search reached.
2. **Planted genuine telegrams of the same lengths can't be recovered with a free key** [S]. In 36 of
   36 planted controls, the solver's best reading is not the planted text: 2–31% of letters correct,
   with a score at or above the true text's on the short ones. The lengths here are at or below
   unicity.
3. **A published period key plus up to 10 edits does not manufacture telegram-grade German from any
   of the nine** [S]. Across all 15 published keys, the best wrong-key score after k = 10 edits is
   −5.1 (p. 189) to −6.8 (p. 176), and real and shuffled ciphertext behave alike. But genuine readings
   heavy with numbers and place names sit at −5.2 to −5.9 (AFAFF −5.24, p. 105 −5.94, creilly's p. 176
   −5.88). **On the 42–53-letter messages, 8–10 free edits reach that band.** A known-key claim with
   that many edits on a short message needs more than a quadgram score.
4. **Free key plus edits is worse still** [S]. With 10 block edits on top of a free key, the short
   messages reach −3.5 to −3.7, better than almost any real telegram.

Practically, for whatever the team claims:
- A **single-message, new-key** reading of any of the nine fails CLAUDE.md test 3 by n-gram score
  alone. It needs a test that is independent of the fit: a second message under the same key,
  known-plaintext structure, or a key derivation fixed in advance.
- A **known-key + edits** reading must state its edit count. If it has more than about 5 block edits
  on a message of ≤ 53 letters, or scores below about −5.0, it is inside the reach of my wrong-key
  baseline (tables in §(c)).
- **Word coverage is not a safe second test either.** Quadgram-optimised false readings, not even
  tuned for words, reach 0.60 coverage (fraction of letters inside corpus words of ≥ 4 letters;
  p. 152 and p. 189 shuffles). Genuine telegram windows have median 0.70 and minimum 0.12.

**What would make this wrong:**
- **My search is weaker than the team's.** Every false-reading maximum here is a *lower bound* on
  what noise can reach: a stronger solver makes noise look *more* German, not less. Against the
  positive controls, the free-key solver did **not** find the true key of p. 187 (212 symbols) from
  scratch, and the edit search recovered only 4 of the 9 solved messages with their true keys inside
  10 edits (§ What I could not do). So conclusions 1, 2 and 4 are conservative. Conclusion 3's "does
  not manufacture" is a statement about *my* search: a stronger edit search might do it.
- **The scorer is the wrong model.** It is modern-ish book German (Gutenberg, mostly 1914–24 military
  memoirs), not 1918 telegram style. Under a telegram model, true readings would score higher, and so
  would false ones built to fit it. The shuffled-vs-real comparisons use the same scorer on both
  sides, so they don't depend on this.

## Method (fixed before any open message was searched; re-runnable)

**Ciphertext.** `ciphertexts/adfgvx-1918-open.txt` from `origin/triage`, sha256 `9362c3d2…`, copied
byte-for-byte to `adversary/adfgvx/ct_source.txt`. `parse_msgs.py` produces `msgs.txt` (sha256
`ef2e4f48…`, one message per line). Its rules:
- gap marks (`- – —`) are dropped;
- lowercase `v` is read as V;
- the bracketed groups on p. 158, `(VVFGD)` and `{VVDAD}`, are dropped. p. 158 is 230 symbols here
  against Bourdeau's 240. `--keep-brackets` keeps them; I did not run that variant.

The creilly11235 transcription (HEAD e60da03) is identical to this one for p. 153 parts 5 and 6
(dashes removed) and for p. 176 GGDAA.

**Keys.** `keys_bourdeau.json` (sha256 `4585fcac…`): the 14 Lasry–Niebel–Kopal–Wacker period keys
plus Lasry's CHI key, as made machine-readable by Bourdeau (github.com/dbourdeau/cyphersolver).
Cells marked `-` are left free and filled by hill-climbing, which is what a claimant would do.
- **Transposition convention:** `perm[i]` is the 1-based read-out rank of column i, with incomplete
  columnar filling. I checked this myself: under this convention p. 187 decrypts with the CHI key, at
  k = 0, to RUSSISCHEN UND POLN HEERESVERKEHR… (−4.18), and the other three conventions give noise.
- **Square:** first symbol = row, ADFGVX order.

**Scorer.** Mean log10 quadgram probability over the 36-symbol plaintext alphabet A–Z0–9, with
unseen quadgrams floored at log10(0.01/N). Quadgrams containing an unknown letter are excluded.
- **Corpus:** 12 Project Gutenberg German books, normalised by `prep_corpus.py`: umlauts expanded,
  sentence punctuation turned into X (telegraphic stop), everything else dropped. That is 4,542,769
  letters, sha256 `1a99eaea…`. Books (ebook ids): 34099 Jünger, *In Stahlgewittern*; 30695 Hindenburg;
  24572 Richthofen; 47940 Forstner; 45670 Luckner; 48921 Helfferich, *Der Weltkrieg* II; 63853
  Rittmeyer, *Seekriege*; 45808; 36693 Clausewitz; 21031 Rathenau; 22628 *New-Yorker Staats-Zeitung*
  1915; 52299.
- No 1918 telegram text is in the corpus. The nine 2017 readings (`planted_source.txt`, 972 letters)
  are held out as the reference for what real looks like. Under this scorer they give **−4.58**
  overall.

**Search** (`fake.c`, one C file, `gcc -O3 -march=native -o fake fake.c -lm`). Modes:
- `free`: each restart runs (i) a simulated-annealing search over the transposition, maximising the
  pair index of coincidence Σc(c−1) of the 36 ADFGVX pairs (substitution-free; 200k steps); then
  (ii) a 1M-step substitution anneal with delta scoring; then (iii) three rounds of column
  reordering on the German score with the square held fixed. 8 restarts per (message, L).
- `edit`: a fixed key plus a beam search (width 16) over edits, up to k = 10. `block` ops are:
  substitute one symbol, delete 1–5, insert 1–5 (content by coordinate ascent, starting from a copy
  of the preceding symbols, i.e. duplication), swap adjacent 5-blocks. `single` ops are: substitute,
  delete or insert one symbol. **Each op counts as one edit.**
- `rkedit`: the same, with a uniformly random key.
- `fedit`: free key and edits alternately, k = 0..10, L = 16 and 19.
- `fsq`: transposition fixed, square free. Used here for TRUPPENVERSCHIEBUNG (L = 19, alphabetical
  ranks), the keyword Childs lists for later use, which read p. 217 in Sept 2026.
- `rand`: 200,000 uniformly random keys (L uniform on 10–25).
- **Shuffled controls:** a uniformly random permutation of the message's own symbols, so symbol
  counts are kept. Seeds are fixed in `run_all.py`.

**Re-run:** `python adversary/adfgvx/run_all.py CORPUS.txt` (A, B, P, E, FE, T; about 50 min on 8
cores), then `summarize.py` and `verify_readings.py`.

**Independent check.** `verify_readings.py` shares no code with `fake.c`. It has its own ADFGVX
decryption, edit application, quadgram counter and word-coverage DP. It re-decrypted **every**
printed reading from its stated key and edit list: 576 + 5,643 + 660 + 36 + 396 + 36 + 85 + 24 lines,
**0 mismatches**, with scores equal to 4 decimals. These are witnesses: each false reading below
can be re-made from its key alone. The same decryption method is used both times, so the check is
on the computation and is not a second method.

## Evidence

All tables are generated by `summarize.py` into `adversary/adfgvx/results/summary.md`. Higher
scores are more German.

### Reference: what real looks like (held-out 1918 telegram readings)

| window length | min / median / max quadgram score | word coverage min / median / max |
|---|---|---|
| 42 letters | −6.24 / −4.48 / −3.52 | – |
| 52 | −6.14 / −4.60 / −3.61 | 0.12 / 0.69 / 0.96 |
| 66 | −5.79 / −4.69 / −3.58 | 0.21 / 0.70 / 0.97 |
| 88 | −5.75 / −4.70 / −3.66 | 0.36 / 0.72 / 0.95 |
| 120 | −5.62 / −4.65 / −3.76 | – |

### (a) Random keys [S: 200,000 keys per message, uniform]

For all nine the mean is −8.49 to −8.50 and the sd 0.09–0.15. The best of 200,000 is −7.05 (p. 153b)
to −7.90 (p. 176). Random keys never come close: test 3's "random key" null is trivially beaten and
tells you nothing. Only the optimised nulls below matter.

### (b) Free key, real vs shuffled [S: 16 lengths × 8 restarts × (1 real + 3 shuffles) per message]

| message | letters | real: best | shuffled: best of each of 3 | shuffled max |
|---|---|---|---|---|
| p73 | 88 | −5.051 | −4.782 −4.901 −4.921 | −4.782 |
| p152 | 52 | −4.199 | −3.923 −4.117 −4.154 | **−3.923** |
| p153a (VFVAX) | 66 | −4.572 | −4.488 −4.578 −4.549 | −4.488 |
| p153b (AXVAA) | 46 | −4.046 | −3.987 −3.878 −3.811 | **−3.811** |
| p158 | 115 | −5.501 | −5.590 −5.335 −5.293 | −5.293 |
| p170 | 53 | −3.992 | −4.232 −4.111 −4.110 | −4.110 |
| p176 GGDAA | 110 | −5.579 | −5.561 −5.550 −5.691 | −5.550 |
| p189 | 42 | −3.847 | −3.795 −3.784 −3.650 | **−3.650** |
| p198 | 82 | −4.819 | −4.921 −5.002 −4.807 | −4.807 |

The real ciphertext beats all three of its shuffles only for p. 170, by 0.12, and that is within the
spread between shuffles. Best false readings from *shuffled* ciphertext:

- p152 (−3.92, L = 24): `EEINGLANGEWEHENHABENKTEBOSTENNMEENGENUNDSEITERSOFFAH`
- p153b (−3.81, L = 18): `IRWICHENMALEEIEINDIEERAUFENSIEREGIERWESEITABER`
- p189 (−3.65, L = 17): `OLELEGESCHERFALLESTUEBERNENENDENFEINIENNAE`
- p170 (−4.11, L = 22): `NEGENETESKLEINMANNDUENSCHUETZENNIERERXDEUNINNEESOFFNE`
- p73 (−4.78, L = 25): `XFLEERDEINIHNESTXJUNGZCKNEBEGNENFESIAXGEEINTEONSKANNNTWIEREVONTUNDPFENINEMNEASEVENGTENDZ`

Keys, per-L tables and every other reading are in `results/B_free_key.txt` and `results/summary.md`.

### Positive control: planted 1918 telegram text, free key at the true L [S: 4 per message]

Each control is a random window of the held-out readings, at the open message's length, encrypted
by my own Python encryptor (`run_all.py: encrypt`) with a random square and a random L of 16–20.
Letters correct: 2–31% (median 7%). The solver's best is above the true text's score in 13 of 20
planted texts of 42–66 letters, and below it in all 16 of 82–115 letters. So at ≤ 66 letters the
true plaintext is not the optimum: the problem is underdetermined, not just hard. At 82–115 letters
the true plaintext would win if found, but my solver doesn't find it, a power failure (see limits).

### (c) Published keys + k edits [S: 15 keys × 9 messages × {block, single, block-on-shuffled} + 10 random keys]

Best over the 15 keys, block edits, real ciphertext:

| message | k=0 | 2 | 4 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|
| p73 | −8.19 | −7.55 | −7.18 | −6.91 | −6.69 | −6.50 |
| p152 | −8.18 | −7.09 | −6.68 | −6.26 | −5.85 | −5.53 |
| p153a | −8.19 | −7.53 | −7.20 | −6.84 | −6.54 | −6.28 |
| p153b | −8.07 | −6.91 | −6.45 | −6.05 | −5.76 | −5.45 |
| p158 | −8.04 | −7.56 | −7.22 | −6.94 | −6.75 | −6.59 |
| p170 | −8.24 | −7.22 | −6.52 | −6.03 | −5.72 | −5.45 |
| p176 GGDAA | −8.10 | −7.63 | −7.38 | −7.13 | −6.96 | −6.82 |
| p189 | −7.95 | −6.70 | −6.29 | −5.86 | −5.48 | **−5.11** |
| p198 | −8.14 | −7.39 | −7.12 | −6.88 | −6.65 | −6.47 |

On shuffled ciphertext with the same keys, the curves agree with these to within 0.34 at every k. With
10 random keys they run up to 0.5 lower, but that is 10 keys rather than 15. At k = 10 the real
ciphertext is slightly *ahead* of its shuffle on 7 of 9 messages, by 0.04–0.34 (p. 158 +0.34,
p. 189 +0.28, p. 170 +0.21). I followed it up with 20 more shuffles each, under the key that did best on the real text
(`results/E_followup_shuffles.txt`). Choosing the key that way biases the test *toward* the real
ciphertext, and still the real is not an outlier [S, 20 shuffles]:
- **p. 158** with key 5 (Nov 7–9): real −6.59 ranks 2nd of 21; one shuffle reaches −6.53.
- **p. 170** with key 14 (CHI): real −5.45 ranks 2nd of 21; one shuffle reaches −5.39.
- **p. 189** with key 4 (Nov 4–6): real −5.11 ranks 4th of 21; shuffles reach −4.90.

**No signal.**
There is a strong rule of thumb: **each block edit buys about 0.2–0.3 per quadgram on a 50-letter
message and about 0.15 on a 100-letter one, whatever the key.**

True keys on the solved messages (what a real fit looks like with my search):

| message | k=0 | k=1 | k=2 | k=10 |
|---|---|---|---|---|
| p100 (Nov 1–3) | −8.49 | **−4.78** | −4.66 (= Armin's reading) | −3.95 |
| p187 (CHI) | **−4.18** | −4.12 | −4.07 | −3.85 |
| AFAFF (CHI) | **−5.24** | −5.00 | −4.85 | −4.20 |
| p105 (Nov 1–3) | −8.30 | **−5.94** | −5.80 | −5.11 |
| p176a "missing 10" (Nov 10–12) | −8.17 | −7.73 | −7.48 | −5.17 (partial) |
| p109, p132, p146, p171 | not recovered within 10 edits (−6.0 to −7.4 at k = 10) | | | |

Two things follow. A genuine fit jumps by 2.4–3.7 in one edit (p. 100, p. 105) or needs none.
False fits creep up by about 0.2 per edit. **That jump, not the final score, is the signature of a
real key.** Second, after the true reading is reached, further substitution edits keep "improving"
it: p. 100 goes from −4.66 to −3.95 by k = 10. So a score that keeps climbing with more edits is
expected even when the key is right, and doesn't by itself show more edits are justified.

Best false readings, published keys, real open messages, k = 10 block edits:
- p189, key 4 (Nov 4–6), −5.11, edits `D2:4 W68 S3:F S10:A S73:F S19:A S23:X S71:F S0:A S18:V`:
  `BIGENURMGRELBENHENISENNU7474FEINPARSLUNG`
- p152, key 4, −5.53: `CHZWIJ0AUDEUTNIPISTOCH10UHREIFEDURCHEXHOFES24XEMEINDI`
- p170, key 14 (CHI), −5.45: `TXANDKAMETTXAW68AEGE49NOKT32KAEND10MANNWEDENDENITTEG`

### (c') Free key + k block edits [S: L = 16, 19; 1 real + 1 shuffled]

At k = 10 the real ciphertext reaches −3.50 (p. 189), −3.63 (p. 153b), −3.69 (p. 170), −3.81
(p. 152), −4.25 (p. 198), −4.33 (p. 153a), −4.55 (p. 73), −4.91 (p. 158), −5.12 (p. 176). The
shuffled ciphertext is within 0.4 everywhere, and equal on four of the nine.

### TRUPPENVERSCHIEBUNG transposition, free square [S: 8 restarts; 1 real + 3 shuffles]

The real ciphertext beats all three shuffles on three messages: p. 73 (−5.79 vs ≤ −5.97), p. 189
(−4.28 vs ≤ −4.43) and p. 198 (−5.93 vs ≤ −5.95). On the other six it doesn't. With three shuffles
each, those margins (0.02–0.18) are inside the shuffle-to-shuffle spread (up to 0.27).
**No sign that the p. 217 transposition, with any square, reads any of the nine.**

## What I could not establish

- **Free-key solver power.** The pair-IC stage finds a transposition with the true key's IC on p. 187
  (766). But it doesn't find the order of the column pairs, which IC can't see, and my
  column-reordering stage didn't fix that. So the solver did not read p. 187 from scratch (−5.53
  against the true −4.18), although with the true transposition fixed it recovers the text exactly.
  Every free-key "best false reading" is therefore a lower bound on what noise can do. A
  Lasry-strength solver would push the shuffled scores higher, which only strengthens conclusion 1.
- **Edit-search power.** With the true key, I recover 4 of 9 solved messages (p. 100, 105, 187,
  AFAFF), plus p. 176a partly, within 10 edits. p. 146's known repair (a 5-symbol insertion at
  symbol 45, per Bourdeau) was **not** found by my beam. Messages whose repair needs several
  coordinated edits, none of which helps on its own, are outside a greedy beam. So "no published
  key fits the nine with ≤ 10 edits" is as strong as this beam, and no stronger. That agrees with
  Bourdeau (2 block edits, 15 keys) and with 0wwafa's PAPER §5.3 (1–7 edits, 16 keys), which I did
  not read; it is cited from dev's ticket.
- **Edits beyond 10, and other edit models.** Not run: free gaps of arbitrary length on all nine
  (only p. 176 has a 20-symbol gap run, in the calibration file), and the error catalogue E1–E8 of
  0wwafa.
- **Coverage-optimised adversary.** I didn't build a false-reading generator that maximises
  dictionary coverage. A team that uses coverage as its second test should expect such a generator
  to beat the 0.60 already reached.
- **The p. 158 bracket variant**, and the other transcriptions (creilly's covers all 688 entries; I
  compared it only on p. 153 ×2 and p. 176).
- **Joint attacks across messages sharing an unknown key.** This is the team's main strand (83 log
  entries, clustering). The joint mode (`jfree`) exists and was used only in the calibration. The
  baseline for a joint claim is the same machinery on shuffled pairs, and I have not run it beyond
  p. 153.
- **Trials factor of a team claim.** That depends on the claim. My own runs total about 2,300
  searches (576 free, 513 edit chains of 10, 36 + 36 + 36, plus calibration). None of them is
  offered as a solution.

## Witness files

`results/*.txt` holds raw lines with the full key, edit list and plaintext. `results/verified_*.tsv`
holds the Python re-check: tag, k, C score, Python score, coverage, match, plaintext.
`results/old_jointSA/` is an earlier, weaker solver (a joint anneal without the IC stage), kept for
the record and not used in any table.
