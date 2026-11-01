# Referee report: lead-adfgvx (open WWI ADFGVX 1918 messages)

**Current verdict: accept** on the final finding (lead-adfgvx `4b95558` + the K1 fix). K1 is
met: "J1 ≤ 3.3% … none for strand J as a whole" is in both the finding and `results/adfgvx-J.md`.
Part K has the details.
- J1 and J2 from Part J are done.
- The J2/J3 rewording after the adversary's J3 result is right.
- The J3 shuffle bias does **not** carry over to J1. A mask-matched J1 null of my own (1,470 draws
  per detection) is cleared by all 23 detections, with 0 draws at or above S.
- K1: delete "about 10% for strand J". Only J1 now has a bound.

Part J (`1aed138`) was accept with revisions (minor).

The strand-J result at `0df9a7f` was **revise** (Part I).

Clarifications C1–C3 (`cd85680`) were **no objection, with conditions** (Part H). H1–H3 are
met in J0 (`d2c2dc6`).

Strand-J Revision 1 (`e9c318b`) was **accept with revisions** (Part G). The first strand-J text
(`dbf591d`) was **revise** (Part F).

Earlier verdicts on this branch: prereg-R `a588c31` revise; `a0ae584` accept with revisions;
strand-R result `519423c` **accept with revisions** (Part E; E5–E7 still owed by the lead).

Referee: `ref-adfgvx`, opened by `dev` on 2026-10-31. I did no part of the work.
Branch read: `lead-adfgvx`, in three passes:
- `ff9b7a5`: the master plan (Part A).
- `cd067b2`: master plan Revision 1 (Part B).
- `a588c31`: the strand-R prereg (Part C).
- `a0ae584`: prereg Revision 1 (Part D).
- `519423c`: the strand-R result (Part E).
- `dbf591d`: the strand-J pre-registration (Part F).
- `e9c318b`: strand-J Revision 1 (Part G).
- `cd85680`: strand-J clarifications C1–C3, with comp's scan run `30b375b` (Part H).
- `0df9a7f`: the strand-J result, J0 `d2c2dc6` → creilly re-run `b9b5666`, and the adversary's J1(ii) `f8f616d` (Part I).
- `1aed138`: the revised finding (Part J).
- `4b95558`: the J2/J3 rewording after adversary J3 (`a1a7590`), on dev's ticket tmvxuk0knqqwo (Part K).

At `a588c31`, nothing exists yet in `results/`, `search/` or `verify/`, and `findings/` holds
only the prereg. Later stages (strand-J prereg, results) will update this file on the same
branch.

---

## Part A: comments on the master plan, for the pre-registration to answer

None of these is a defect yet, because nothing has been claimed. Each is something
`findings/adfgvx-1918-prereg.md` has to settle before it is committed. I will review the prereg
against this list.

### A1. The mutilation cap is calibrated on a biased sample (`master-plan/README.md`, G1 and "second hazard")

The plan fixes the cap from a census of the solved messages. That is the right source, and better
than choosing one. But the sample is biased in two ways, and both push the same way:

- **Survivorship.** A message got solved partly *because* its mutilation was light enough for
  the 2017 team's search. The nine open messages are open partly because they may be worse.
- **Minimum-edit reconstruction.** For a solved message, the "true" ciphertext is whatever the
  solvers' edits produced. That is a minimal fit, not an observed truth, so it undercounts.

What follows: a NEGATIVE such as "no known key under ≤ m edits" is a valid statement. But it says
nothing about whether these messages use known keys. The finding must say it is conditional on the
cap. The prereg must also state **which statistic of the census** sets m (the max? a percentile?)
and decide that before the census numbers are seen, or as a stated rule applied to them.

A free check on the bias: an ADFGVX ciphertext must have even length. By my count, 2 of the 9 open
messages are odd at face value: 153b (93 letters plus gap marks) and 198 (165). Among the solved
messages, 132 and "Page ??" are odd.
The prereg can compare the odd-length and gap-mark rates of the solved and open sets. That
measures the bias rather than leaving it assumed.

### A2. Mutilation freedom is key material: count it in unicity and in the trials factor

The edit search over positions and types is extra freedom, just like key bits. With about 13
alternatives per position (5 substitutions, 1 deletion, about 6 insertions; an approximation), I
computed the variant counts. Method: the sum over j ≤ m of C(N, j)·13^j, in the venv [H]:

| N (cipher letters) | m = 1 | m = 2 | m = 3 | m = 4 |
|---|---|---|---|---|
| 84 | 10.1 bits | 19.2 | 27.6 | 35.7 |
| 176 | 11.2 | 21.3 | 30.9 | 40.0 |
| 240 | 11.6 | 22.2 | 32.2 | 41.8 |

At D ≈ 3.4 bits/letter, m = 4 costs about 12 plaintext letters of unicity. That is small but not
zero, and it must be counted. More important: the significance threshold must be the
**best-of-null over the same edit search**, not a per-variant p-value. The prereg should state the
search as a number of variants per message per key, and that number goes into
`results/adfgvx-trials.log`.

### A3. The right null for the known-key attack

"Random keys and shuffled ciphertext" (CLAUDE.md) is the floor. For an ADFGVX known-key search,
neither null is the sharpest one:
- Shuffling the ciphertext is close to applying another random transposition, which is a weak
  null.
- A random 36-square plus random transposition is easier to reject than a wrong *period* key.

The null this attack actually faces is **real ADFGVX text under the wrong real key**. That is
available exactly:
- the 11 solved messages (and the read 217), each run against every period key except its own,
- with the identical edit search and scoring.

That gives the null distribution of "best score after ≤ m edits" on genuine, mutilated, period
ciphertext. I recommend the prereg uses it as the primary null, alongside the random-key and
shuffle nulls, and sets the threshold from it.

### A4. Clustering touches the open ciphertext, so it belongs in the prereg

G3(b) clusters the open messages by "same page/date, then column-length compatibility". That
second criterion is computed *on the open ciphertext*. So it is a contact before the run, and every
partition tried is a trial. The prereg should fix the clustering rule (or the clusters themselves),
and record the number of partitions considered.

Also, "same page" is not "same date". The ADFGVX keys of autumn 1918 changed about daily. Give the
date evidence per message, and say where it comes from (Childs, the 2017 paper, the lit ticket),
for any pair assumed to share a key.

### A5. A missing outcome class: a partially known key

The plan's outcomes are READ-JOINT, READ-KNOWN-KEY and NEGATIVE. A middle case exists: a known
period **square** with an unknown **transposition** (or the reverse, if keys were changed
separately). That case lowers the unicity sharply. The transposition alone is log2(k!) = 44 bits
at k = 16 and 70 bits at k = 22, which is about 13–21 plaintext letters at D = 3.4 [H]. Against
that, the full key is about 50–66 letters (below).

The prereg should either include this case (key space and trials stated) or exclude it with a
reason. Leaving it unspecified invites adding it after the fact, which test 1 forbids.

### A6. Unicity per message: the brief's "≤ 55–62 plaintext letters" is not right for every message

I computed U = (log2 36! + log2 k!)/D in the venv. log2 36! = 138.1 bits.

| k | D = 3.2 | D = 3.4 | D = 3.6 |
|---|---|---|---|
| 16 | 57.0 | 53.6 | 50.7 |
| 20 | 62.2 | 58.6 | 55.3 |
| 22 | 65.0 | 61.2 | 57.8 |

The values are plaintext letters, or ciphertext/2. I counted ADFGVX letters at face value (gap
marks excluded) with my own script on the committed transcription. The open messages' plaintext
lengths are:

| Message | Plaintext letters |
|---|---|
| 73 | 88 |
| 152 | 52 |
| 153a | 66 |
| 153b | ~46.5, with gaps |
| 158 | 120 |
| 170 | 53 |
| 176-GGDAA | 110 |
| 189 | 42 |
| 198 | 82.5 |

So 158, 176 and 73 sit well above U even with a full unknown key; 152, 170 and 189 sit at or
below it.

**dev's brief to me says single messages are "at or under ~55–62 plaintext letters". That holds
for 152, 170, 189 and 153b only.** The master plan does not repeat the claim, but the prereg
should state provability **per message**, with its own D (and its source: 1918 military German,
with abbreviations and digit groups, has a lower D than literary German) and the A2 correction
added.

Unicity is a floor, not a tractability claim. Bourdeau's failure at 224 cipher letters (112
plaintext letters) is about search, not information. The plan already says this ("the hard step,
named"), correctly.

### A7. The power test has to match the real conditions

At G3, the planted controls should use:
- 1918 military German in the period's conventions (abbreviations, numbers),
- mutilations **drawn from the census distribution**, not only placed at the cap,
- each real length, and each real cluster composition.

The test must also report the false-positive rate of the full pipeline on the A3 nulls at the
chosen threshold. Run enough null trials that the threshold quantile is resolved; at least 10/α
is a reasonable floor.

### Sound as written

- The ownership split, with the lead (not comp or check) authoring the prereg.
- Gate G3's rule that a method failing its controls is reported as a negative about the method
  and not run.
- The plan names the hard step correctly: joint-attack power at 300–480 letters. It does not
  wave at it.

---

## Part B: on master plan Revision 1 (`cd067b2`), new points for the prereg

The lead adopted A1–A7 (ticket tmvx6v6thn960, closed). Revision 1 moves the target to two
strands. Strand R replicates four outside claims: the p.153 key, the p.176 gap, and the claims
that p.152 and p.189 are duplicates. Strand J is a joint attack on the ~83 unread log entries,
clustered by header. That raises the following.

### B1. Replication must be measured against the claimant's search, not ours

"REPRODUCED from the stated method + key" shows only that the key decrypts. It does not show that
the reading is significant. Significance depends on how much freedom the *claimant* used to find
it:
- the key family they searched,
- the gap positions and lengths they tried,
- how many of the 688 entries they tried each idea on.

The prereg should define REPRODUCED as two things: the decryption re-runs, **and** it beats the
best-of-null of a search with the claimant's freedom. Where that freedom is undocumented,
estimate it from their repo or paper, or report PARTIAL with the reason.

Two cases need this most:
- **p.176, "nov10 key + a 20-symbol gap".** Check whether the gap is *marked in the
  transcription* (observed) or *inferred*. A position chosen to make the text read is search
  freedom. So is a length chosen the same way.
- **p.153, "new 18-col key".** This is a keyless recovery on 153a+153b: 225 cipher letters, or
  ~112 plaintext letters, about twice U at k = 18 [H].
  - It is above unicity, so the reading can be unique.
  - The null must be the same keyless solver's best score on (i) same-length null ciphertext
    and (ii) the real ciphertext under scoring alone. A wrong-key decrypt is not that null.
  - Also check whether 153a and 153b were *joined* by assumption. Joining is a choice, and it
    goes in the trials factor.

### B2. A duplicate claim needs its own null

Calling p.152 or p.189 a "duplicate of a solved message" is a near-match claim between log
entries. The trials are about 688 candidates per entry, or C(688, 2) pairs if the claimant swept
the whole log. The prereg should state:
- the alignment and edit distance used,
- the null rate of matches at least that close among unrelated pairs in the same log, or between
  shuffled entries.

A duplicate is strong evidence only if that rate is tiny. It is stronger still if the duplicate's
known key then decrypts the open copy, which is a separate and checkable test.

### B3. Date clusters: one key per key period, not one per pool

"About 40 unread entries fall in 6–9 Nov" is four days. If keys changed about daily (see Limits:
I have not sourced this), the joint unit is **a day**, or whatever key period the solved messages
show. The prereg should:
- take the key-change boundaries from the *solved* messages' dates and keys,
- forbid merging across a boundary unless a stated test supports it,
- count each merge it allows as a trial.

Header fields (date, time, call signs) come from one transcription, creilly's. A wrong date puts
a message in the wrong cluster. A joint solve's power test should include a planted wrong-day
intruder at the observed header-error rate. Measure that rate on the solved set, where the key
fixes the true day.

### B4. Shared data means the comp and check agreement is not about the transcription

The independence rule lets comp and check both use creilly/0wwafa data. So their agreement is
[C] about the *computation*. It is not evidence about the transcription or the headers, which they
share. Each result must name its transcription. Where a Schmeh/Lasry text also exists (the nine),
the result must be re-run on that text too, as CLAUDE.md requires ("test whether it survives the
others").

### B5. The acceptance sentence still names the nine

The revision marks it "superseded in scope". The prereg should restate it for R and J with the
actual entry IDs (creilly numbering, cross-referenced to Childs page). A NEGATIVE can then be
checked against a fixed list.

---

## Part C: the strand-R pre-registration (`findings/adfgvx-1918-prereg.md` @ `a588c31`), verdict **revise**

The prereg takes up B1, B2, B4 and B5 in outline:
- outcome classes with a PARTIAL for undocumented freedom,
- a null per claim,
- named transcriptions,
- creilly entry IDs,
- logging of exploratory runs.

The gaps below are in the *details* of the nulls. That is where a replication claim does its
work, so each one could flip an outcome.

### C1. The R1 decoy null can contain real solutions (prereg "Null per claim", R1, "real 1918 ciphertext ... whose key is known to be different")

The R1 search family is: width-18 transposition, plus square recovery if the square was
recovered. A decoy is a real enciphered message, so it has a true key. If that key lies inside
the searched family, check's solver can find a genuine German reading of the decoy:
- a width-18 transposition under any square, when the square is recovered;
- or a width-18 transposition under the same period square, when it is known.

That raises the null maximum and wrongly sinks R1 to NOT REPRODUCED. A decoy key just outside the
family makes the null pick up partial readings instead.

**Fix:** use only decoys whose true transposition width is not 18, and also not a divisor or
multiple of 18 that the solver could partly align with. If the square is known, use decoys under
a different square. List the decoys by log ID in the prereg.

### C2. R1: the join and the parts

R1 joins p156C3 and p156C6 as "parts 5-6 of one message". The prereg counts the join as one
trial, which is right. It does not say how the two parts were *enciphered*: as separate
transpositions under one key, or as one block.
- If separately, each part must read on its own under the key, and the prereg should require
  it. That is a strong internal test, and it costs nothing.
- If as one block, the order and the boundary are freedom, and they must go into the null.

State which reading the claim makes. Then test (i) on each part alone where that applies.

At width 18 with a known period square, the unknown key is log2 18! = 52.5 bits, about
15 plaintext letters at D = 3.4 [H], computed in the venv. A correct reading of ~112 letters
should beat any honest null by a wide margin. If it only scrapes past the null, that is itself
informative, and the report should say so.

### C3. R2: the filled symbols must be excluded from (i) and from scoring (R2, "a 20-symbol gap at position 160, filled")

"Filled" means the claimant supplied 20 ciphertext symbols. Under a transposition, those symbols
scatter into ~20 plaintext half-positions, about 10–20 letters, across the message.
- If the fill content was chosen to make the text read, it is up to 2.58 × 20 ≈ 52 bits of
  freedom. That would buy the claimant ~15 letters of plausibility.
- The prereg's null covers gap *position* and *length*, not gap *content*.

**Fix:** in (i) and in (ii), score and compare only the plaintext positions that come from
transmitted symbols, and mask every position that depends on a filled symbol. Do the same in the
null runs. If the claim's plaintext depends on the fill to read, the masked score is what counts.

### C4. Who is the second implementation? (prereg "Scoring", "Outcome definitions")

Only check-adfgvx is named. The claimant is a first implementation, but not one of ours, and we
cannot read its code. Test 4 needs **two of ours**, sharing no code, for the deterministic part.
That part is (i): the decrypt under the stated key and edits.
- comp-adfgvx is free to do it.
- It is cheap: a decryption, not a search.

The null (ii) can stay check's alone, but then it is labelled [S] from one implementation, not
[C].

### C5. The scorer must predate contact with the R entries (prereg "Scoring"; the lead's ticket says check "may already be running exploratory R work")

"Fixed and committed before it scores any R entry" is the right rule. It cannot be checked if
exploratory scoring already happened.
- **Require:** check states, with a commit sha, when its scorer and corpus were fixed, and
  whether either changed after any R entry was decrypted or scored.
- Re-running under the prereg does not undo tuning on the entries. A changed scorer must be
  disclosed in the result.

### C6. The null's search budget has to match (B1 / R1, R2)

"Null with at least the claimant's freedom" covers the *search space*. For a stochastic search
like the R1 hill-climb, the null max also depends on *compute*: restarts, iterations, the
annealing schedule.
- **Require:** each null run uses at least the budget check used on the real entry.
- Report both budgets.

For the exhaustive nulls (R2 gap positions × lengths × wrong keys; R3/R4 alignments), "≥ 100 null
runs" should be replaced by "the exhaustive enumeration, of size stated".

### C7. R3/R4: the hard null is same-day traffic, and the second test is not independent

- **The hard null.** Unrelated messages under the *same* key with formulaic plaintext can share
  whole column segments after transposition. A duplicate claim must beat them, not only random
  unrelated entries. Report the tail separately for:
  - (a) all unrelated solved entries;
  - (b) solved entries under the twin's key, or from the twin's day.
- **The second test.** For a second intercept, "the solved twin's key decrypts the open copy (with
  the alignment's edits only)" is largely the alignment over again. Once the copy is aligned onto
  the twin's positions, it decrypts to the twin's plaintext by construction. It adds independent
  evidence only for symbols the alignment did *not* match. Say so in the outcome, and do not
  count it as a second test.
- **The statistic.** Use the same best-offset, gap-aware statistic in the null as on the claim.
  The prereg implies this; say it.

### Checked and sound in Part C

- The R1 key is a permutation of 1..18 (checked in the venv).
- The REPRODUCED / PARTIAL / NOT definitions are exhaustive. They correctly put undocumented
  freedom in PARTIAL, not in REPRODUCED.
- The R2 null includes A3's wrong-period-key null on the solved entries. That is the right
  primary null.
- Exploratory runs are logged and re-run. With C5 added, that is enough.
- "Never the claimant's code" is the right independence line. The data is shared, and B4 covers
  that.

---

## Part D: prereg strand R, Revision 1 (`a0ae584`), verdict **accept with revisions**

I checked each of C1–C7 against the Revision 1 text.

**Answered:**
- **C1.** Decoys are outside the family. The exclusion list (6, 9, 12, 36) is wider than needed,
  which is harmless.
- **C2.** The block structure is stated first, and each part must read alone if the parts were
  transposed separately.
- **C3.** Fill-dependent positions are masked in (i), in (ii) and in every null, and the masked
  count is stated.
- **C4.** comp produces a second plain decrypt, plaintext only, with no scoring. That is
  sufficient: the deterministic step is what test 4 needs two implementations of. The nulls are
  labelled [S].
- **C6.** Each null gets at least the real entry's budget, and exhaustive nulls report their size.
- **C7.** The tail is reported against two sets, the same statistic is used in the null, and the
  twin-key test is demoted.

### D1. C5's remedy is the wrong one (Revision 1, bullet C5)

"If either [scorer or corpus] changed after any exploratory contact with an R entry, the
exploratory results are discarded, not reused."

The hazard in C5 is not the exploratory *results*. It is the *scorer*: a scorer revised after
seeing R entries may have been tuned to them. Discarding the results and keeping the revised
scorer leaves the hazard in place.

**Fix:** if the scorer or corpus changed after contact, either:
- (a) score R under the last version committed before any contact, by sha; or
- (b) keep the revised scorer, but justify every change without reference to R entries, and
  state in the result that the scorer postdates contact.

If neither changed, there is nothing to do.

### D2. "Listed in the report before they are scored" (Revision 1, bullet C1)

The report is written after the runs, so "in the report" cannot be checked for order. Commit the
decoy IDs, in the trials log or the prereg, before any decoy is scored, and cite that sha in the
result.

### Unchanged by the revision, noted for the result review

ddfece8 logs lit-adfgvx's count of **22** period keys. R2's wrong-period-key null must therefore
use all 21 wrong keys, not the ~16 assumed at A3.

---

## Part E: the strand-R result (verdict **accept with revisions**)

I re-ran the deterministic steps, and parts of the nulls, myself from the method and keys alone.
- **Inputs:** `ciphertexts/adfgvx-1918-log.{records,keys,messages}.json` at `519423c`.
- **Code:** my own, written from the cipher's definition. I did not read any code in `search/` or
  `verify/`.
- **Location:** the scripts and outputs are in `referee/adfgvx-r/`. I read check's REPORT, comp's
  R-decrypt and the adversary's calibration *after* writing my decrypt.

### E0. Engine check

I tried both transposition conventions on every solved entry that is clean (no `-` or `?`, header
count equal to log count): 273 entries under their own keys.
- "key[c] = read rank of column c; long columns first" reproduces the stored plaintext (≥ 90%
  letters) on **271/273**.
- The other convention reproduces it on 0/273.

### E1. C4 decrypts: confirmed by a third implementation [C, 3 implementations, 2026-11-01]

My decrypts of p156C3, p156C6, and p179B1 (under nov10, 20 lost symbols after symbol 160, blank
cells left blank) are **identical, character for character,** to comp's
`results/adfgvx-R-decrypt.md`. check reports the same agreement.

### E2. R1 (p.153 parts 5+6): ruling on question (b)

**PARTIAL is the right word.** The prereg defines three outcomes, and (ii) unestablished is
PARTIAL by definition. Adding "undecided" after the result would be changing the outcome classes
after the fact. The finding can say in plain words what PARTIAL means here.

**The hard step, named: (ii), a search-family null with the claimant's power. It is not done.**
Neither check's solver nor the adversary's finds the claimed key on the real text. Check found it
0/3 times on real text and 0/12 on planted controls. So neither solver's null maximum says what a
solver that *does* reach the claim would find on noise.

What exists does not substitute for it:
- **Check's fixed-key rows** (the claim beats 100 random keys, 100 shuffles and 100 decoys by
  0.24–0.32 per quadgram). These are tests of the *given* key and carry no correction for the
  claimant's search over 18! orderings (and possibly widths 15–25).
- **The unicity argument** [H, computed in the venv]. The free key is the transposition plus the 24
  used square cells: log2 18! + log2(36!/12!) = 52.5 + 109.3 = **161.8 bits**, or ~48 plaintext
  letters at D = 3.4. Part 5 has 66 letters, so a unique reading is *possible*. That says nothing
  about whether this n-gram scoring can identify it.
- **The adversary's result** cuts against relying on part 5. With the claimed transposition fixed
  and the square free, its annealer found a *different* part-5 reading that scores higher than the
  claim (−4.50 vs −4.68). Only the joint parts pin the square.

Ruling on (i) for part 6: the 12 "fills" are letters chosen by reading for lost symbols. They are
not decrypted, so they cannot "match". With C2 in force, part 6 meets (i) only on its 37
decrypted letters plus the 2 stated corrections. The finding must describe part 6 as:
- 37 letters decrypted,
- 2 by correction,
- 15 undetermined, 12 of them conjectured.

It must not say "3 open". Check's REPORT §3 says the same; the finding must not lose it.

Also checked: the claimed square agrees with every other known square in at most 1 of the 15–24
cells compared (my count, matching check's). So this is the recovered-square case, not A5's
known-square case.

### E3. R2 (p.176 GGDAA): ruling on question (a)

**REPRODUCED stands, for the letter reading.** The reasons:
1. **Both scorers predate the prereg-run scoring.** LIT and TEL were committed in `50b772c`
   (22:30:19), before the prereg-compliant R2 run in `cbaf3b3` (authored 23:05:57). Choosing TEL
   among two committed scorers × two '?' rules is a selection over 4 configurations. It is
   disclosed and counted (Bonferroni × 4, p < 0.004 on 0/991). That is what the prereg asks of a
   post-contact choice (D1(b)).
2. **LIT's failure is a scorer-power failure, not evidence against the reading.** On 58 solved
   non-R entries it ranks the true key above every wrong-key placement 45/58 times, against TEL's
   50/58. This was measured without reference to R2.
3. **An independent scorer agrees** [S, 2026-11-01, `referee/adfgvx-r/`]. Mine is a quadgram model
   on the creilly plaintexts with the nov10 period held out:
   - alphabet A–Z plus one digit class, add-0.5 smoothing, no Gutenberg corpus;
   - blank cells and lost-symbol letters masked, ≥ 40 clean quadgrams;
   - **disclosed: I chose a telegram-trained model knowing TEL had worked and LIT had not.**

   It gives:
   - the claim: **−4.960** over 50 quadgrams;
   - **the unique maximum** over every (L ≤ 20, g) under nov10;
   - best wrong key on p179B1, over the same grid: **−5.357** (nov01);
   - best of **201** valid solved-entry/wrong-key grid maxima (12 entries of 200–250 symbols,
     seeded draw, × their 21 wrong keys): **−5.171**;
   - so the claim beats all 222 null cases, the nearest by 0.21 per quadgram.
4. **The adversary agrees independently**, under a stronger null (gap content optimised, not
   masked): about 1.9 per quadgram over 30 nulls.
5. **The freedom is small** [H]. The key is Lasry's published nov10 key, and the entry's date
   (10 Nov) is in its period. The gap length is not free: the header says 240 and the log has 220.
   That leaves the position, log2 221 ≈ 7.8 bits, against 97 coherent unmasked letters.

**Not reproduced, and the finding must not claim it:**
- **The position "160".** Under my scorer the top six positions are 160, 152, 159, 158, 154 and
  153, all within 0.009 per quadgram. Check's margin over 158 is the same size, and the adversary
  prefers 162. The finding should say "a 20-symbol loss at about 152–162".
- **The digits `217`, `216`, `9` and the fills.** They depend on 2017 blog-comment fills of the 5
  blank nov10 cells. Under the headline rule they are masked, and so unsupported.

### E4. R3 and R4: reproduced by a third implementation [S, 2026-11-01]

I reran S3 (best ungapped offset, ≥ 40 compared symbols) with my own code:

| | open vs twin | best of null (594 solved entries) |
|---|---|---|
| R3, p155E vs p139B | **88/102 at offset 210** | 37 |
| R4, p192A vs p188_.2 | **52/79 at offset 0** | 29 |

These are identical to check's figures.
- **REPRODUCED holds for the duplicate relation only.**
- Retransmission versus double reception is not decided.
- For R4, the claimant's reading `Gestellung Auto unmoeglich` rests on one letter that p192A
  contradicts at letter 16 (check §4). It is **not** reproduced. The finding should give the
  relation, not that plaintext.

### E5. Revision: the finding's wording

`findings/adfgvx-1918.md` (not yet on the branch) must carry E2's part-6 description, E3's
position range and digit exclusion, and E4's "relation only".

### E6. Revision: reproducibility

The lead reports that `verify/adfgvx/run_all.sh` does not build `libgap.so`, which `gapscan.py`
needs. Until it is fixed and a clean export runs end to end, the R2 scan is reproducible only by
hand. My R2 numbers do not depend on it.

### E7. Revision: the D1 evidence window

The scorer commit `50b772c` (22:30:19) is **after** the first exploratory R scoring (22:24, check's
REPORT §0). That nothing changed in those six minutes rests on a file mtime (german.py, 22:20:47),
not a commit. A file mtime is not something git records or anyone else can check.
- The REPORT should say this plainly, not "fixed at 50b772c … before the first scoring".
- E3.3's independent scorer reduces what hangs on it for R2. For R1, the conclusion is PARTIAL
  either way.

Minor: the REPORT gives the decoy commit time as "23:33". That is the rebase's committer date of
`81ce00b`. The original `f821aa8` was committed at 22:46:48, before `cbaf3b3`'s first scoring
(23:05:57). `decoys_r1.json` is byte-identical in the two (`git diff` is empty). **D2 is
satisfied.**

### Checked and sound in Part E

- **C4.** Three-way decrypt agreement.
- **D2.** Ancestry and content checked.
- **B4.** check reports p156C3, p156C6 and p179B1 identical in Schmeh's text (I did not re-check
  this).
- **The R2 wrong-key null.** It uses all 21 wrong keys.
- **R3/R4.** The S3 statistics and their nulls.

---

## Part F: the strand-J pre-registration (`dbf591d`), verdict **revise**

Read at lead-adfgvx `dbf591d`: the "Strand J" section of `findings/adfgvx-1918-prereg.md`, and
the inputs it cites: `results/adfgvx-power.md` and its jsonl records, `results/adfgvx-clusters.csv`
and `.md`, `results/adfgvx-duplicates.md`, `search/adfgvx/{jattack.c, power.py, powerreport.py,
plant.py, lm.py}`, `ciphertexts/adfgvx-1918-scan-transcription.json` and `...log.keys.tsv`.

Every number below that is not quoted from those files is my own recomputation from them. I used
the venv and a `git archive` export of `dbf591d` in my scratch directory. I wrote nothing into the
lead's tree, and I ran no attack on any unread entry.

The hard step in J is the **J1 threshold**: one family-wise bound across about 50 targets of very
different lengths, candidate-key counts and blank cells. Next come the J2 null and the J3
rationale. The edit vocabulary, the stop rule and the detection-versus-reading gates are sound
(see "Checked and sound" below).

**Counts used throughout** [C-lite: my script on clusters.csv and duplicates.md, one
implementation]:
- 29 unread entries are flagged as copies of solved entries.
- Removing those, the entries under 60 letters, and p220C leaves **T = 50 J1 targets**.
- Single-period groups of at least 300 letters after the duplicate exclusion (creilly letters):
  nov04 1670, nov22 1329, oct04 1169, nov01 947, nov07 826. So **G = 5** before any J1 detection
  is removed.

### F1. The J1 family-wise bound does not follow (J1, "Null and threshold")

**Claim.** The threshold is the maximum of N ≥ 20(T+1) null statistics, half from plant-side
solved entries of length within ±20% under wrong keys, half from shuffled pool entries. The
prereg says this "gives a family-wise false-detection rate across all J1 targets of ≤ T/(N+1) <
5%".

**Why it does not follow.**
- P(new draw > max of N draws) = 1/(N+1) needs the new draw to be **exchangeable** with the N
  draws. The union bound over T targets then needs that to be true of **every** target.
- The J1 targets are not exchangeable with a pooled null. They differ in:
  - length (60 to 545 letters);
  - the number of candidate keys K (1 to 5), since S is a max over K;
  - the blank-cell count of those keys (0 to 12).
- The null statistic moves with all three. From `adfgvx-power-f3.jsonl` at cap 2 (my
  recomputation):
  - Wrong-key null median by length: −3.64 (60–149 letters), −3.88 (150–249), −3.98 (250+).
    Shuffled: −3.55, −3.75, −3.99.
  - Wrong-key null median by the blank cells of the key applied: −3.97 (0 blanks), −3.81 (2),
    −3.69 (5), −3.57 (8), −3.50 (12).
  - The cause is in `jattack.c` `lm_pscore`: an unknown cell is charged ln(1/36) = −3.58, which
    is *better* than a typical wrong-key trigram. So many blanks pull a null up toward −3.58.
- "Matched length (±20%)" does not say matched to *what*. "Wrong keys drawn uniformly from the 21
  that are not its own" includes keys no target is ever tested under: the five Childs keys
  (11–13 blanks), `chi_2017_comments` (14 blanks) and `dec09_history`.
- So the pooled maximum has no proved relation to any single target's null. What can be proved is
  FWER ≤ Σ_t 1/(n_t+1), where n_t is the number of draws that are exchangeable with target t.
  With N spread over strata, that sum is about (number of strata) × T/N, not T/N.

**Fix (cheap; I recommend it).** Use a per-target null.
- For each target t, build n_t ≥ 20·T draws by t's own procedure, half of each kind:
  - t's ciphertext shuffled, under t's own candidate keys. This is matched exactly in length,
    letter frequencies, K and blanks.
  - a plant-side solved entry of t's length (truncated if need be), from a period not among t's
    candidates, under **t's candidate keys**. This is A3 done exactly.
- Threshold_t = the maximum of t's draws. Then FWER ≤ Σ_t 1/(n_t+1) ≤ T/(20T+1) < 5%, and that
  is proved.
- Cost from power.md (cap 2, median 0.12 CPU s per key): 50 × 1000 × ~1.4 keys × 0.12 s ≈ 2.3
  CPU-h. Under an hour at 6 workers.
- If the lead keeps a pooled threshold instead, the prereg must state the bound as Σ_t 1/(n_t+1),
  with each target's matched n_t, and drop "≤ T/(N+1)".

### F2. The positive controls are partly in the scorer's training text (J1, "Positive controls")

**Claim.** The excluded duplicates whose solved twin has a known key are run through J1 like
targets. A rate below 50% declares J1 underpowered.

**Problem.**
- The trigram scorer is trained on the TRAIN side of `lm.split()` (seed 20261101).
- I ran `lm.split()` on the 29 flagged twins: **17 twins are TRAIN-side and 12 PLANT-side**.
- Of the 24 controls with at least 60 letters, **13 are TRAIN-side**: p083B, p104D2, p155E,
  p161E, p165A1, p169A3, p169B2, p177A3, p187C3, p190B, p192A, p200C, p201E.
- A scorer that has seen the plaintext scores its own decryption higher. So the control rate is
  inflated by leakage, which is exactly what the split exists to prevent.

**Fix.**
- Apply the 50% rule to the **11 plant-side controls**: p101B, p112D, p114A, p125D1, p160A,
  p162B, p165C1, p175E, p196B, p213D, p215A2. Report the rate with its Wilson interval; 6/11
  would be 21–72%.
- Report the train-side rate beside it, as a leakage-inflated figure only.
- Define control detection as **above threshold AND the maximising key is the twin's key**.
  A wrong-key exceedance is a false positive, not power.
- Report the controls by twin alignment cost too. Several are far from cap-sized: p101B has 90
  edits, p112D 52, p213D 53, and p213D's d = 0.482 is close to the null cell minimum.

### F3. The J2 threshold comes from a null that is partly a true solution, drawn for the wrong groups (J2, "Threshold"; lead question 2)

**The contamination.**
- In `power.py` `run_trial`, kind `wrongperiod`, family F2, each member of the null cluster is a
  real solved text from a *different* key. The square handed to the attack is
  `KEYS[keys_used[0]]["square"]`, which is **member 0's own square**.
- So the known-square attack can recover member 0's real transposition, and decrypt member 0 as
  real German.
- The records show it. A null whose found width equals member 0's true width occurs far above the
  chance rate of about 1/8:

  | bin | width found = member 0's width | expected by chance (1/8) |
  |---|---|---|
  | 0–299 | 64/110 | 14 |
  | 300–699 | 38/86 | 11 |
  | 700–1299 | 26/101 | 13 |
  | 1300–2200 | 18/67 | 8 |

- The 300–699 threshold, −3.086, is set by a two-member null that found width 20, which is member
  0's width.

**Effect.** The effect is **conservative**, not anti-conservative: the threshold is too high and
J2's power is understated. But it is not a null for J2's hypothesis ("this period's square, an
unknown transposition"), and the prereg should not cite it as one.

**Question 2, on 200 nulls per bin with G groups.**
- The arithmetic is fine: G·1/(n+1) ≈ 5/191 ≈ 2.6% at G = 5.
- The bound has the same exchangeability gap as F1. The bin's nulls were drawn for the
  **pre-dedup** group compositions; power.md says so itself. Removing the 29 duplicates changes
  every large group: nov07 drops from 13 members (2118 letters) to 6 (826), and nov04 from 15 to
  12.

**Fix.**
- Redraw the J2 nulls **per real group**, after J0 and J1 have fixed its membership:
  - same member lengths;
  - the attack's square = **that group's period square**;
  - members taken from solved entries of periods whose square differs, and shuffled versions of
    the group;
  - n_g ≥ 20·G per group (100 at G = 5), threshold_g = the maximum, FWER ≤ Σ_g 1/(n_g+1).
- Cost from power.md: about 8–15 CPU s per trial, so 5 × 200 × 15 s ≈ 4 CPU-h at most.
- **State the blank-cell rule for the real run.** nov07's square has 2 blanks. The F2 nulls fill
  blanks with the unused symbols, but the prereg says only "the period's known square". The rule
  must be the same in the real run and in its null.

### F4. Nets and keys: two statements are contradicted by the project's own data (J1 "Candidate keys", J2 "Which groups"; lead question 4)

**(a) "Net" is undefined.**
- `adfgvx-clusters.csv` column `net` is known for **5 of 83** entries.
- The scan transcription (`a4028ce`, field `net`) has 80: 65 RICHI, 12 RIZI, 2 CHI, plus 3 with
  none.
- J1, J2 and J3 all branch on net. The prereg must name the field, and say what happens to the
  3 entries with no net.

**(b) "Because the 22 keys are RICHI keys" is false.**
- `chi_2017_comments` is a CHI key. It solves p190A1 and p190A, "SU v LP", 13 Nov.
- The five Childs keys are from other theatres and dates (Berlin–Constantinople, Salonika,
  July–August).
- The J1 candidates are the 14 Lasry period keys only. The prereg must say that, and stop calling
  the 22 the key set.

**(c) The RIZI caveat is contradicted by data.**
- Both calibration RIZI entries in the scan transcription, p188_.2 and p200D, are **solved under
  nov13_16**.
- **8 of the 12 unread RIZI entries are near-identical copies of ciphertexts solved under RICHI
  period keys**. Each is listed as twin → twin's key:

  | copy | twin | twin's key |
  |---|---|---|
  | p104D2 | p104A2 | nov01 |
  | p112D | p112B | nov01 |
  | p185A | p177B | nov10 |
  | p185C | p177C | nov10 |
  | p186D | p186E | nov10 |
  | p192A | p188_.2 | nov13_16 |
  | p200C | p201B | nov13_16 |
  | p201E | p200D | nov13_16 |

- So for RIZI, a J1 NEGATIVE under the period keys is a real test, not "only not under a RICHI
  key". The caveat should state this evidence.
- J2's restriction to RICHI also loses its stated reason. Excluding RIZI stays allowed as a
  pre-registered choice; the non-duplicate RIZI entries of at least 60 letters are p102A, p130B2
  and p140B.

**(d) CHI.**
- The solved CHI traffic uses its own key (`chi_2017_comments`, 13 Nov).
- So for the two unread CHI entries (p201D, 15 Nov; p071A1, 5 Oct), the period keys are a weak
  test.
- Either add `chi_2017_comments` to p201D's candidates as one declared extra trial, with its 14
  blanks in the null per F1 (power will be low, which is an honest negative about the method), or
  say why it is left out.

### F5. The J3 rationale is false as written (J3)

**Claim.** "No RIZI or CHI group, and no gap or ambiguous group, reaches 700 letters."

**Recount.**
- The RICHI group "ambiguous between nov07 and nov10" (p170D, p174A3, p179A, p179A6) has
  **717 letters** on the primary scan transcription after the duplicate exclusion. On creilly
  it has 713, and 1029 before the exclusion.
- I could not reproduce the prereg's "537" for the RIZI group from any committed file.
- "No keyless joint attack at this budget has power on any group the headers support" is false
  too. On single-period groups F1 has 14% (700–1299) and 32% (1300–2200) power [S, power.md].
  Five groups qualify: nov04 1670, nov22 1329, oct04 1169, nov01 947, nov07 826.
- On those groups J3 tests a different hypothesis from J2: a wholly off-list key (E8).

**Fix.**
- Correct the sentence and the letter counts, on the primary transcription.
- Then either:
  - run J3 as a **detection-only** family on the groups of at least 700 letters, with its own
    nulls and its FWER counted. A detection would be the right key only 31–49% of the time
    (power.md "Detection is not reading"), so it is a lead at most.
  - or state plainly: "the unknown-key hypothesis is not tested on groups X, Y, Z, where F1 has
    14–32% power."
- Either is acceptable. The present sentence is not.

### F6. The cap unit (J1 "Edit model"; lead question 1)

**The mismatch.**
- The rule counts **structural runs**: E1, E2 and E3, each counted once.
- jattack's cap counts **edits**: a single-symbol insert or delete anywhere, or a whole 5-group at
  a group boundary.
- Census runs are not single symbols. E1 averages 272/128 = 2.1 symbols per run, E2 233/134 =
  1.7, and E3 360/33 = 10.9 (`adfgvx-mutilation.md`). For example, a 3-symbol E1 is one run but
  three jattack edits.

**Re-run.** I re-ran the rule's simulation with `power.damage`: 2,000 messages per length at
60, 150, 250 and 400 symbols, seed 7. I counted three ways [S, my run, one implementation]:

| unit | p90 | share within cap 2 |
|---|---|---|
| runs | 2 | 92–93% |
| jattack edits (groups at 5j, as `plant.mutilate` places E3) | 2 | 91% |
| symbols | 4–5 | 88% |

So **the cap value 2 survives the change of unit**. What has to change is the wording. The rule,
and every J1 NEGATIVE, must be stated in the unit actually searched: "≤ 2 jattack edits, which
covers about 91% of messages under the damage model [S]".

**On Levenshtein agreement.**
- check reproduced comp's census **Levenshtein cost** (590/591). A cost does not fix the run
  decomposition: a cost of 6 can be one run or six.
- So the run profiles that drive the damage model rest on one implementation.
- That is acceptable for a design input, but the finding must label it that way. If the lead
  wants it as [C], check must reproduce the per-entry (E1_ev, E2_ev, E3_ev).

### F7–F10. Recommended, not required

- **F7. Candidate coverage on the unread side.**
  - The duplicates give an out-of-sample check of the derived rule: their twins' keys are known.
  - The twin's key is among the derived candidates for **22 of the 24** controls of at least 60
    letters (92%, Wilson 74–98%). The misses are p190B (dated 13 Nov, twin under nov04) and
    p215A2 (22 Nov, twin under nov25).
  - The LOO figure is 98.3% (96.9–99.1%). Quote both.
  - A second J1 pass under all 14 period keys, as its own family with its own per-target null,
    would remove the dependence. It costs about 10× F1's estimate.
- **F8. Secondary transcription.**
  - Say that detection is defined on the primary transcription, and that the creilly re-run is a
    robustness check that cannot add a detection.
  - Otherwise count 2T tests.
- **F9. Ambiguous-period entries out of J2 (question 3).**
  - Valid as a pre-registered choice. State the count and the letters (the nov07/nov10 group: 4
    entries, 717 letters).
  - The ambiguity has only two options, so J2 under both squares is two extra counted tests. That
    is cheap, and it is the only ambiguous group in a bin with 70% F2 power. I recommend it, but do
    not require it.
- **F10. Widths.**
  - J2 and J3 search widths 15–22. nov25's key has width 23.
  - State that an unknown transposition of width 23 or more is not searched.

### Checked and sound in Part F

- **The FWER arithmetic, given exchangeability.** T/(20(T+1)+1) < 1/20 for every T.
- **J1's edit vocabulary.** It matches `jattack.c` mode 3 (candidate lists at lines 500–502, and
  the nested loop over distinct edits).
- **The statistic.** It is `lm_pscore`: unknown and blank-cell trigrams are charged ln(1/36), and
  the skip-unknowns objective is never used to decide.
- **Detection is not reading.** It is correctly separated, with check reproduction and the
  adversary as gates. The F2 P(correct | above) of 84–93% matches power.md.
- **The stop rule and the trials-factor log.** They are adequate as written.
- **J0 symbol policy and entry joins/splits.** They are mechanical, they add no freedom, and they
  are stated before contact.
- **The cap rule's own figure.** I reproduce p90 = 2 in runs at every length I simulated.
- **The power.md F3 figures by blank count.** I recomputed planted recovery at cap 2 from the
  jsonl: 109/125 (0 blanks), 15/21, 15/16, 32/35, 3/3. It is consistent with the table.

---

## Part G: strand-J pre-registration, Revision 1 (`e9c318b`), verdict **accept with revisions**

I read the rewritten "Strand J" section at `e9c318b` against Part F, item by item. I re-derived
each bound from the text as written. No new computation was needed: every count it cites is
mine from Part F, or is deferred to the J0 commit.

### F1–F10: disposition

| item | Revision 1 | ruling |
|---|---|---|
| F1 | per-target null: n_t ≥ 20T draws, half t shuffled and half plant-side text from a period not among t's candidates (cut to t's length), all under t's candidate keys | **answered.** Σ_t 1/(n_t+1) ≤ T/(20T+1) < 1/20 holds, because each draw is made by t's own procedure. Wording point at G2 |
| F2 | rule applied to plant-side controls only; a detection needs the twin's key to be the argmax; Wilson CI, alignment cost and the train-side rate reported | **answered** |
| F3 | a null per group, with the group's own square; members from periods with a different square, or the group's members shuffled; the blank-fill rule stated for the real run and the null alike; power.md F2 thresholds dropped | **answered** |
| F4 | net = the scan field; candidates = the 14 period keys only; RIZI joins the period groups on the F4c evidence; one declared CHI-key trial for p201D | **answered.** Grouping regardless of net is supported by the data I cited. Leaving CHI ungrouped is a stated choice |
| F5 | the false sentence is gone; J3 runs detection-only on single-period groups of ≥ 700 letters; a J3 detection is a lead and never a reading | **answered.** Its null (members drawn from different periods) is the right null for "shares an off-list key" |
| F6 | cap stated in jattack edits, with ~91% coverage [S]; run profiles labelled single-implementation; NEGATIVE wording fixed | **answered** |
| F7 | both coverage figures quoted; the all-14-keys pass is not run, and the gap is stated | **accepted.** This was a recommendation |
| F8 | detection on the primary transcription only | **answered** |
| F9 | the nov07/nov10 group runs under both squares, as 2 declared tests counted in G′ | **answered.** Wording point at G2 |
| F10 | widths ≥ 23 are not searched, and this is stated | **answered** |

On the lead's extra decisions:
- **(2)** p148A and p215A.3 are treated as RICHI. Grouping is now regardless of net, so this
  affects nothing except the CHI exclusion. It is harmless.
- **(5)** T, G and the control list are frozen in J0 before J1. That is the right order. The
  bounds depend on T and G′, so they must come from that commit.

### G1. Revision: state the error rate across the three families (J1, J2, J3 "Null")

- Each family is held below 5% on its own.
- A detection in any of them is reported. So the chance of at least one false detection
  anywhere in strand J is bounded only by the sum: **≤ 15%** (5% + 5% + 5%).
- Either state that figure in the prereg and in the finding, or split it. For example, use
  n ≥ 60·T, 60·G′ and 60·G3 for an overall 5%. That costs 3× the null CPU, which is about 7 h
  for J1 at the F1 estimate.
- Either choice is acceptable. Leaving it unstated is not, because a reader will take "< 5%" to
  be the strand's rate.

### G2. Revision: two places where "per target" has to be literal

- **(a) The two nov07/nov10 tests.**
  - Each test (group, square) needs its own null, under *that* square.
  - The text says "for each group g ... g's period square", and this group has two.
  - Write "for each test (group, square)".
- **(b) The wrong-period draws for a target whose candidates include a non-period key.**
  - p201D gets `chi_2017_comments` as a candidate.
  - Its draws (b) must come from solved entries whose key is not among *its* candidates. That
    excludes p190A1 and p190A, which are under the CHI key.
  - "A period NOT among t's candidates" does not cover a key that has no period. Write "a solved
    entry whose key is not among t's candidate keys".

### G3. Recommended: plant-side text in the J2 and J3 nulls too

- J1's draws (b) are plant-side; the J2 and J3 nulls do not say.
- In J2 the square is wrong for every null member, so leakage hardly matters there.
- In J3 the attack is keyless, and a train-side member decrypted by chance would score
  unrealistically well.
- Saying "plant-side" everywhere costs nothing.

### Checked and sound in Part G

- **The arithmetic of all three bounds**, given the per-target, per-test and per-group draws as
  written.
- **The order and stop rule:** each null is committed before its targets, and the J2 and J3 group
  lists are fixed after the earlier family's detections are removed and before their nulls are
  drawn. A null drawn after removal still matches its group, because it is drawn for the
  frozen membership.
- **The J1 and J2 READ gates, and J3 as lead-only.** They are consistent with power.md's
  P(correct | above threshold).
- **The Changes section matches the body.** I compared each line.

## Part H: strand-J clarifications C1–C3 (`cd85680`), verdict **no objection, with conditions**

Read at lead-adfgvx `cd85680`: the prereg's new final section, `results/adfgvx-scan-units.md`,
`results/adfgvx-power.md` (scan variant), and the scan transcription's entries, all read-only
(`git archive`). The test I applied: does each clarification give every case exactly ONE
reading, fixed without any decryption, and does it leave the decision rules alone?
Nothing in strand J has decrypted unread text yet. The only contact so far is the scan
transcription, the duplicate screen and the clusters.

### H1. Required (C1): put p0924's 100 lost slots in block 2 only, at offset 200

- C1 inserts a stated count "at its position". p0924 is the only unit whose note states a
  count. I checked every unsolved entry's `lines`, preamble and reader notes. The other notes
  are "(Jm'd)", "(interference)", "(Balance jammed)", "(jammed)", "(missed first part)" and
  "(missed beginning)", and none of them gives a number.
- In the scan's joined `lines`, the note opens line 13. Block 1 (p0924#1) is lines 0–7: 290
  symbols, matching its header of 290. Block 2 (p0924#2) is lines 8–14: 200 printed symbols,
  then the note, then 58 more. 258 + 100 = 358, which matches its header.
- The rule therefore has exactly one answer: p0924#1 has 290 slots and nothing is inserted;
  p0924#2 has 358 slots, with slots 200–299 lost.
- But comp's `scan-units.md` counts the note on **both** split units, because "the entry's notes
  are not attributed to a block in the scan file". If J0 carries that over, p0924#1 gets 100
  phantom slots. That is a 390-slot unit under a 290 header, and no ≤ 2-edit search can repair
  it.
- **Fix:** the J0 commit states the two slot counts and the gap position above. It derives the
  position from `lines`, because the `symbols` field does not carry the note.

### H2. Required (C3): call it an amendment of the frozen net rule, not a clarification

- The frozen J0 rule is "Net: the scan transcription's field `net`". For p071A2 that field reads
  **RICHI** (`net_indicator` "CHI-186 / RICHI-186"). So the frozen rule did name this case:
  RICHI, and therefore grouped (in oct04, per the clusters).
- C3 overrides that. It makes p071A2 CHI, and so ungrouped in J2/J3. The ticket's framing,
  "cases the frozen symbol policy does not name", does not fit C3.
- I do not object to the override:
  - It is made before any decryption, on heading evidence alone. Both parts share the heading
    "A) COS, POT v NKJ (9.19 p.m., October 5th)". Part 1's preamble says "2 TEILE", and part 1
    is labelled CHI-220.
  - It gives one reading. It changes J2/J3 membership only, because J1 treats p071A2 the same
    way under either net.
- **Fix:** the finding and the J0 commit must say that C3 amends the J0 net rule for one unit,
  and why. They must also say that the other single readings were not tested: RICHI for p071A2
  alone (the frozen rule), or RICHI for both parts (if the CHI label is the error). The oct04
  group is then reported without p071A2.

### H3. Required wording: some J1 negatives cannot carry the "~91%" sentence

- C1 inserts nothing where a note gives no count. That is a legitimate single reading. But for
  several units the printed length falls short of the header by far more than 2 edits can
  restore:
  - p074A.2: 85 printed, 192 header;
  - p087C: 118 of 244;
  - p119A1: 160 of 222;
  - p222C: 284 of 394;
  - p140A5: 215 of 252.
- The frozen NEGATIVE sentence ("under ≤ 2 jattack edits, covering ~91% of messages under the
  damage model") is false for these units. A truncated tail at a known header length is outside
  the damage model's support.
- **Fix:** J0 lists every unit whose slot count differs from its header by more than 10 (two
  5-group edits). Its J1 negative reads "uninformative: N symbols short of the header". That
  changes reporting only, not a decision rule.

### Checked and sound in Part H

- **C2 is the frozen rule, read literally, and it is length-consistent.** Frozen J0: "a printed
  non-ADFGVX letter, a parenthesised symbol, `-` and `?` are each one lost symbol". C2 says the
  same, and a whole parenthesised group is five such symbols. I checked the slot count against
  the header for every unit with parentheses:
  - p071A1: 220 = 220, with (DDAGD) and (F-DKV) inside the count;
  - p072A: 220 = 220;
  - p072B1: 329 against 330 (its 4-letter group);
  - p110D: 176 = 176;
  - p222C: 284 against 394, short for the reason in H3.
  So C2 deletes no group, and the parenthesised groups are part of the counted message. C2
  throws away about 29 printed symbols in total (p071A1 10, p072A 3, p072B1 1, p110D 2, p222C
  15). That is a loss of power, not a freedom. Rejecting comp's 32,768 reading variants is the
  conservative choice.
- **The cap.** It stays at ≤ 2 jattack edits, and that is still what the frozen F6 rule gives
  under the scan scaling.
  - The scan-scaled simulation in `power.md` gives "events p90" = 2 at every length from 60 to
    400.
  - Structural events in the scan F3 sample: 0: 90, 1: 75, 2: 17, 3+: 18. So ≤ 2 covers 182/200
    = 91% [S, n = 200, scan-scaled], the same as the creilly-scaled ~91%.
  - Rejecting comp's symbol-cost cap (M = 5) keeps the accepted unit. Part F, F6, required jattack
    edits.
- **The power figures quoted** (comp `30b375b`, recomputed by me from its jsonl records):
  - F1 at 700–1299: 11/160 (7%). F1 at 1300–2200: 33/160 (21%).
  - F2 at 700–1299: 85/160 (53%). F2 at 1300–2200: 113/160 (71%).
  - F3 at cap 2: 161/200 (80%), threshold −3.2244.
  - All of these are exact under powerreport.py's convention: `pscore`, with the threshold
    taken by the cluster's ACTUAL letter bin.
  - If the threshold is taken by the planted cell bin instead, F2 at 700–1299 is 86/160. One
    planted cluster sits in a different actual bin. It is immaterial, but note the convention if
    the figure is quoted to the unit.
  - The figures are guides and set no threshold. The J thresholds are per target and per group
    (F1, Part F), so switching from creilly-scaled to scan-scaled figures changes no decision
    rule.
- **No freedom added.** C1–C3 each fix one reading, and none needs a decryption to apply.

## Part I: the strand-J result (`0df9a7f`), verdict **revise**

Read: `findings/adfgvx-1918.md` (strand J), `results/adfgvx-J.md`, every J1/J2/J3 null and run
record, `results/adfgvx-J0.json`, `search/adfgvx/strandj.py`. Also the adversary's
`adversary/adfgvx-j1.md` and `j1/results/wrongkeys.tsv` (agent/adv-adfgvx `f8f616d`). All of it
was read from `git archive`, and all of it was recomputed in the venv by scripts of mine, written
from the record formats rather than from comp's code.

The hard step is whether a threshold of "max of n draws" bounds the false-detection chance by
1/(n+1). That needs every draw to be exchangeable with the target under H0. The prereg asserts
it. The records refute it.

### I1. Required: the two null halves are not exchangeable, so "strand J < 5%" is not shown

- **What is claimed** (finding, strand J intro; prereg "Overall false-detection bound"):
  - each family is below 1/60, because the per-target threshold is the max of n_t ≥ 60·T draws;
  - so the strand is below 5%.
- **What the records show.** Half (a), the target's own text shuffled, scores systematically
  higher than half (b), plant-side solved text cut to length. The gap is largest where the
  target has many lost slots, because an unknown trigram is charged −3.584 against a uniform
  mean of −4.79, and half (b) carries creilly's lower lost rate.
  - J1, mean of a against mean of b:
    - p071A2: −3.533 / −4.089;
    - p0924#2: −3.564 / −4.312 (101 lost slots);
    - p231B2: −3.650 / −4.212;
    - p125B: −3.675 / −4.199.
    Half (a) sets the max for 35 of the 49 targets.
  - J2: in every one of the 5 tests the max comes from half (a). The means are 0.24–0.65 apart.
    For example, nov07: a −3.693 against b −4.340, and the b max is −4.203.
  - J3 (nov07): a −3.514 against b −3.871. The max comes from half (a).
- **Why the bound does not follow.** P(S > max of n draws) ≤ 1/(n+1) holds only if S under H0
  is exchangeable with all n draws. Here the draws come from two visibly different
  distributions. Wherever S under H0 actually lies, the only defensible bound is one built on a
  single half. Halving n doubles the bound.
- **The bound that does follow**, if half (a) is a valid null on its own [H]:
  - J1: Σ 1/(n_a+1) = 49/1471 ≈ 3.3%;
  - J2: 5/151 ≈ 3.3%;
  - J3: 1/31 ≈ 3.2%;
  - strand J: ≈ 9.9% by the union bound.

  Half (a) being a valid null is plausible but not proved. The best support is the adversary's
  random keys on the real ciphertext: R0/R1 maxima are on the same scale as half (a)'s.
- **What does not change.** Every detection, every READ-KNOWN-KEY gate and every negative. The
  thresholds are the same numbers. Only the stated error level moves.
  - The J1 detections are also individually backed by 0 of 2,600 random keys reaching S on each
    of the 22 [S, adversary].
  - Expected false J1 detections under the corrected bound: ≤ 0.033.
- **Fix:** state the per-family bounds above, and "strand J ≤ 10%", with the exchangeability
  failure named. Alternatively, show that half (b) is exchangeable, for example with a
  lost-slot-matched half (b). That would be a new null, and so a new pre-registration.
- **Consequence for J2 and J3.** The J2 exceedance (+0.0032 over a 150-draw half) and the J3
  LEAD (+0.0042 over 30 draws) are each consistent with chance at these levels, and the finding
  should say so. Neither claims a reading, so no verdict there changes.
- **This is my miss too.** Part G accepted the bound's arithmetic "given the draws as written".
  The arithmetic was right; the exchangeability it assumed was not checked until there was data.

### I2. Required (the lead's question 1): READ-KNOWN-KEY stands for all 22, but say what it means, and drop the margin-based ranking

- **The label.** The rule was detection + (i) + (ii), fixed in advance. All 22 meet it. I do not
  re-grade a pre-registered label after the fact, so READ-KNOWN-KEY stands.
- **What the label establishes:**
  - the unit is enciphered under the stated period key with the stated edits (I1's level, [S]);
  - the decryption is reproducible [C] (check-adfgvx-j1, plus the adversary's pycheck).
- **What it does not establish:** the content of the letters that are unknown. For p071A2 (40%
  unknown letters, 77% unknown trigrams), p102A (36%), p231B2 (32%), p071A1 (27%), p125B (26%),
  p220B (21%) and p102C (21%), "read" in plain prose overstates it.
  - **Fix:** the Answer says "22 identified under their period key and decrypted
    (READ-KNOWN-KEY)", and gives each unit's unknown share. The table already has it.
- **The "clear / thin" split uses the wrong axis.** The margin over the best wrong key is set
  almost entirely by blank-heavy wrong keys: nov13_20 (12 blank cells) is the best wrong key on
  18 of 23 units (adversary). So the margin measures the target's distance from −3.58, not
  legibility.
  - The counter-example is p072B1: 2% unknown, place names and numbers, S − threshold = +0.835,
    yet it is filed as "thin" (margin +0.279).
  - "Eleven read as German" is the lead's own reading [H], not a measurement, and it includes
    p102C at 21% unknown.
- **Fix:**
  - describe the 22 by unknown share and S − threshold, or add the margin against blank-free
    wrong keys;
  - label any "reads as German" sentence as the lead's reading;
  - remove the sentence "beat every wrong key by 0.45–1.34 … only 0.01–0.31" as a quality
    ranking, or say plainly that it ranks distance from the unknown-letter charge.

### I3. Required (the lead's question 2): lead the J1 negatives with the measured power, not the 91%

- `results/adfgvx-J.md` line 63 and the finding read: "no reading … with ≤ 2 jattack edits
  (covering ~91% of messages under the damage model); J1 is declared underpowered …".
- The ~91% is how much of the damage model the edit cap covers. It is not power. The plant-side
  controls are the only real-text measure, and they give **5/12 (42%, Wilson 19–68%)**. The
  controls also show that the damage model omits a whole class: fragments, 0/6.
- **Fix:** each negative reads "not detected; J1's measured detection rate on real text is 5/12
  (19–68%)". The 91% figure follows it, as the cap's coverage of the damage model. The H3 units
  stay "uninformative: N short of the header", as they are now.
- The finding's "its 26 negatives exclude nothing" is right; keep it.
- The fragments-versus-others split (0/6 against 5/6) is correctly labelled post hoc [H]. It must
  not be used to call any negative informative.

### I4. Minor (the lead's question 3): the margins are right, and one range in the text is not

- I recomputed all 23 margins (any-key and period-only) from `wrongkeys.tsv` (483 rows, 21
  keys per unit, none of them the argmax key) against comp's S. All 46 figures match the table
  to the printed precision. So does the unknown share.
- The text's "0.45–1.34" mixes the two columns. Over any key, the clear eleven span
  **0.455–1.304**; 1.338 is p189B3's period-only figure. Write "0.45–1.30".
- The finding labels the adversary's wrong-key search "exhaustive at cap 2 [C]". The search is
  one implementation (e2.c). pycheck re-scores the maxima it reports but does not search, and
  the cross-check against jattack covers the 64 candidate pairs, not the 21 wrong keys. Label
  it as one implementation, cross-checked on 64 pairs.

### Checked and sound in Part I

- **Thresholds.** For all 77 subjects (49 targets, 28 controls), I rebuilt each threshold from the
  two null files. Each has exactly 2,940 complete draws (1,470 per half; per draw, the max over
  the subject's candidate keys), and each threshold equals the recorded one to 1e-6.
  - 23/49 targets are above threshold.
  - The null statistic is the same max-over-candidates as S (`strandj.py` `thresholds`).
- **Controls.** 5/12 plant-side detected under the twin-key rule. p215A2's argmax is nov22, but
  its twin is under nov25, which is not among its candidates. 9/16 train-side. Wilson 19–68%.
  So the UNDERPOWERED declaration follows the rule.
- **Order.** Each step's commit is an ancestor of the next: J0 `d2c2dc6` → J1 nulls `7eb78f7`,
  `ae8da4a` → controls `cd0cd93` → targets `e49c8cc` → J2 nulls `f459bb9` → runs `f2886a0` →
  J3 null `10a7ad7` → run `3d8173d`. The targets file's provenance is cd0cd93. G2 (per-(group,
  square) J2 nulls) is in the records.
- **H1–H3 in J0.**
  - p0924#1: 290 slots, 2 lost. p0924#2: 358 slots, 101 lost.
  - p071A1 and p071A2 are CHI with candidate oct04, and "p071A2 as RICHI" is listed as not
    tested.
  - The header-mismatch list is applied to the negatives.
- **J2 and J3** runs against their thresholds, from the records: nov07/nov10@nov10 is
  −3.3921 against −3.3952 (+0.0032), and J3 nov07 is −3.4630 against −3.4672 (+0.0042). The
  other four J2 tests are below threshold.
- **Novelty counts** agree with lit-adfgvx-j: 7 of the 22, and 16 "not found" of the 23 with p218A
  included. p213D, a plant-side control candidate at dbf591d (twin d = 0.482), is now a target.
  Its longest overlap with any solved plaintext is 18 letters (`XKRIEGSMINISTERIUM`), so it is
  not a copy.

## Part J: the revised finding (`1aed138`), verdict **accept with revisions** (minor)

I read the diff `0df9a7f..1aed138`, which touches only `findings/adfgvx-1918.md`. I checked each
Part I item against it, and then the lead's answers on my not-checked list.

### Adopted

- **I1.** The per-half bounds are stated: J1 49/1471 = 3.3%, J2 5/151 = 3.3%, J3 1/31 = 3.2%,
  and about 10% for the strand. They are labelled [H] on half (a), the failure is named, and J2
  and J3 are called consistent with chance. No "< 5%" claim remains in the finding.
- **I2.**
  - READ-KNOWN-KEY is defined as "key identified + decryption reproduced [C]; not legibility".
  - The seven high-unknown units are listed in the Answer.
  - The clear/thin ranking is gone, and the table order is labelled as not legibility.
  - The "reads as German" list (10 units, now including p072B1) is labelled as the lead's [H].
- **I3.** Negatives lead with 5/12 (Wilson 19–68%). The ~91% figure is labelled as the cap's
  coverage, and "exclude nothing" is kept.
- **I4.** The range is removed. e2.c is labelled a single implementation, cross-checked on 64
  pairs.

### J1. Minor: `results/adfgvx-J.md` still states the old bound and the old negative sentence

- Line 61: "FWER <= sum 1/(n_t+1) < 1/60 … accepted by the referee, Part G". Line 63: the
  negative leads with "(covering ~91% …)".
- The finding cites this file as its evidence, so the two now disagree.
- **Fix:** regenerate or annotate the report with the Part I bounds and the I3 sentence. This is
  comp's file, so ask comp; the lead does not edit it.

### J2. Minor: one unmeasured claim still uses the margin ordering

- "What would make strand J wrong", the scorer bullet: "Thin-margin detections (the bottom half
  of the table) are sensitive to it; the top half are not."
- No scorer-sensitivity run exists.
- **Fix:** label it [H], or drop it. If kept, tie it to the unknown share rather than to the
  margin order, which I2 retired.

### Checked and sound in Part J

- **creilly re-run.** From `results/adfgvx-J-creilly.jsonl`, 17 of the 23 detections are above
  their primary thresholds on creilly's text. The six that are not are p072B1, p102C, p139A2,
  p153B4+p153B, p189B3 and p231B2, exactly the finding's scan-only list.
- **E5** (strand R wording):
  - part 6 is stated as 37 decrypted / 2 corrected / 15 undetermined;
  - the R2 gap is "about 152–162", with 217/216/9 unsupported;
  - R3/R4 are "relations between ciphertexts only", and R4's plaintext is not supported.
- **E6.** check `5c3f191` (in lead-adfgvx): `run_all.sh` builds all six shared objects,
  including libgap.so, before any step. From a clean `git archive` of `verify/adfgvx` at
  1aed138, all six compile.
- **E7.** The disclosure of the scorer-freeze window is in "What would make this wrong".

## Part K: does the J3 null bias reach J1? (`4b95558`), verdict **accept with revisions** (K1)

Dev asked two things:
- whether its ruling is right: reword J2 and J3, with no re-draw;
- whether the adversary's J3 null bias (`adversary/adfgvx-j3.md`) also undermines the J1 half-(a)
  bound, which Part I made the only supported one.

### The J1 answer: no, measured, not argued

- **Why it might.** J1 targets carry lost bursts too, up to 43 of 264 slots. The adversary's
  bias needs two things:
  - a free square, to exploit the column structure that shuffling destroys;
  - lost bursts that land differently once shuffled.
  J1 has no free square, because the key is fixed. The second mechanism could still act through
  the unknown-trigram charge.
- **Test.** I built a mask-matched null, the adversary's construction (c), for every J1
  detection: `referee/adfgvx-r/j1mask.py`. For each of the 23 detections, 1,470 draws, as many as
  half (a).
  - Each draw is a plant-side solved ciphertext from comp's half-(b) bank, under a key NOT among
    the target's candidates. It is cut to the target's length, with the target's own lost-symbol
    mask imposed.
  - Each draw is scored by comp's own statistic: jattack mode 3 at cap 2, the max over the
    target's candidate keys. This was run through `strandj.run_mode3` from a read-only archive
    of 0df9a7f.
  - The seeds are fixed (sha256 of "ref-j1mask:unit:i"). Records: `referee/adfgvx-r/j1mask.jsonl.gz`
    (sha256 fdbf9bd2…).
  - The bank keeps creilly's own lost marks, so each draw carries at least the target's losses.
    That biases the test toward finding the bias.
- **Result [S, 2026-11-01, one implementation, comp's statistic]:**

| unit | lost / slots | S | half (a): mean, max | masked (1470): mean, max | masked ≥ S | S − masked max |
|---|---|---|---|---|---|---|
| p062A | 8/225 | -3.452 | -3.891, -3.628 | -3.984, -3.686 | 0 | +0.234 |
| p071A1 | 30/220 | -3.372 | -3.654, -3.492 | -3.687, -3.497 | 0 | +0.126 |
| p071A2 | 41/186 | -3.383 | -3.533, -3.423 | -3.565, -3.415 | 0 | +0.032 |
| p072A | 4/220 | -2.724 | -3.994, -3.780 | -4.065, -3.698 | 0 | +0.974 |
| p072B1 | 2/329 | -3.180 | -4.218, -4.015 | -4.251, -4.016 | 0 | +0.835 |
| p0924#1 | 2/290 | -2.564 | -4.155, -3.918 | -4.196, -3.758 | 0 | +1.194 |
| p102A | 24/133 | -3.120 | -3.500, -3.332 | -3.515, -3.365 | 0 | +0.245 |
| p102C | 14/136 | -2.921 | -3.624, -3.447 | -3.636, -3.373 | 0 | +0.452 |
| p110D | 2/176 | -2.745 | -4.053, -3.802 | -4.000, -3.542 | 0 | +0.797 |
| p125B | 33/252 | -3.239 | -3.675, -3.486 | -3.618, -3.483 | 0 | +0.244 |
| p139A2 | 1/92 | -2.603 | -3.635, -3.211 | -3.707, -3.295 | 0 | +0.692 |
| p141B.2 | 6/285 | -2.545 | -4.014, -3.777 | -4.135, -3.818 | 0 | +1.274 |
| p142A2+p142A | 1/220 | -3.277 | -4.155, -3.920 | -4.117, -3.755 | 0 | +0.478 |
| p153B4+p153B | 9/202 | -2.536 | -3.823, -3.638 | -3.908, -3.642 | 0 | +1.107 |
| p170D | 2/187 | -3.369 | -3.652, -3.432 | -3.686, -3.455 | 0 | +0.087 |
| p189B3 | 0/242 | -2.157 | -3.482, -3.345 | -3.502, -3.340 | 0 | +1.183 |
| p190G | 0/134 | -2.486 | -3.283, -3.030 | -3.426, -3.230 | 0 | +0.744 |
| p194A.2 | 12/186 | -2.759 | -3.440, -3.339 | -3.471, -3.329 | 0 | +0.571 |
| p213D | 0/116 | -2.324 | -3.707, -3.414 | -3.866, -3.475 | 0 | +1.150 |
| p218A | 18/390 | -3.683 | -4.081, -3.873 | -4.072, -3.846 | 0 | +0.162 |
| p218C | 11/248 | -3.164 | -3.957, -3.750 | -3.974, -3.712 | 0 | +0.548 |
| p220B | 21/204 | -3.330 | -3.718, -3.506 | -3.716, -3.527 | 0 | +0.197 |
| p231B2 | 43/264 | -3.315 | -3.650, -3.510 | -3.655, -3.525 | 0 | +0.210 |

- **Reading.**
  - For 19 of 23 the masked mean is at or below the shuffle mean. For the other four it is above
    by ≤ 0.06 (p110D, p125B, p142A2+p142A, p218A).
  - The masked maxima are on the same scale. For p071A2 the masked max (−3.415) is slightly above
    the recorded threshold (−3.423), but still 0.032 below S.
  - **No masked draw reaches S for any of the 23**, p218A included.
- **Consequence.**
  - For J1, a null matched for the lost-symbol pattern behaves like half (a), and every detection
    clears it.
  - Detection on max(half (a), masked) gives the same 23. Adding a null can only raise a
    threshold, so no negative changes either.
  - So J1 ≤ 49/1471 ≈ 3.3% holds if EITHER half (a) or the masked null is exchangeable with the
    target. That is better support than the [H] in Part I. Still [S]: it is not a proof that
    the masked null is exchangeable.
  - **The finding may say:** "J1 ≤ 3.3%; the J1 detections also clear a mask-matched null
    (referee Part K, 0/1470 for each)."

### Dev's J2/J3 ruling: right

- No reading rests on J2 or J3, so a re-draw would change no claim.
- The finding now says the J2 and J3 bounds do not hold on damaged groups. It reports that the J3
  exceedance is reproduced by masking alone, and lists a mask-matched null for J2/J3 as not
  tested.
- The p062A cap result (survives at caps 1–3, not a reading at cap 0) is reported as the
  adversary's. I did not re-run it.

### K1. Required (one sentence): no strand-wide bound remains

- `findings/adfgvx-1918.md` line 134 (and `results/adfgvx-J.md` line 65) still say "…so about 10%
  for strand J by the union bound". The next bullet says the J2/J3 bounds do not hold.
- A union bound needs every term. With J2 and J3 having none, there is no strand-wide figure.
- **Fix:** replace it with "J1 ≤ 3.3% (half (a), and also a mask-matched null, referee Part K). No
  bound is established for J2 or J3 on damaged groups, so none for strand J as a whole". The
  results file needs the same change, from comp. No re-review is needed.

### Independent confirmation (adv-adfgvx, `adversary/adfgvx-j1.md` Addendum 2, ec2bc83)

- The adversary ran the same test with its own code, on all 49 targets at 100 draws each. Its
  source windows are clean, so its draws are matched exactly rather than from above.
- Result: 0 of 4,900 draws exceed their target's threshold. The mask-matched mean is below the
  shuffle mean in every damage bin.
- Its first version allowed damaged source windows and gave 17/4,900 above threshold. That
  version was over-damaged, and the adversary labels it as such.
- My bank also allows damaged windows, which is why I compared against S rather than the
  threshold. On that comparison it is still 0 of 1,470 for every detection.
- So the two runs agree. The thresholds are sensitive to over-damage, and the detections are
  not.

### Checked and sound in Part K

- Part J's J1 is met: `results/adfgvx-J.md` marks the < 1/60 bound and the old negative sentence
  as SUPERSEDED, and leads the negatives with 5/12.
- Part J's J2 is met: the scorer bullet now reads "not measured … [H]".

---

## What I could not check

**For Part K:**
- **The masked null runs on comp's jattack**, the same code as the claim. It tests the null's
  construction, not the implementation.
- **I did not test J2 or J3** with a matched null. Dev ruled that out, and I agree, since no
  reading is at stake.
- **I did not re-run the adversary's J3 tests or the p062A cap result.**
- **The masked bank** stacks creilly's own lost marks on top of the target mask. So it is
  matched from above, not exactly.

**For Part J:**
- **E6.** I ran only the build step from the clean archive, not the whole pipeline. Its long
  steps need the creilly, 0wwafa and Gutenberg inputs in $TMPDIR, plus hours of CPU.
- I did not read the revised finding's strand-R sections beyond the E5–E7 items.
- Part I's limits still apply.

**For Part I:**
- I did not decrypt any J unit myself. Gate (i) rests on check-adfgvx-j1 and the adversary's
  pycheck, and I re-tabulated their records only.
- I re-ran no null and no attack. Whether half (a) alone is a valid null (I1) is [H]. I can
  bound it only by the adversary's random-key scale.
- **Whether nulls were scored before targets** cannot be proved from git, beyond commit
  ancestry. The commits are 45 s to 1 min apart (06:27, 06:28, 06:29).
- I read none of the plaintexts as German. Legibility claims are the lead's.
- I did not re-check strand-R items E5 and E6 in this pass. E7's disclosure is present in "What
  would make this wrong".
- I did not check the creilly robustness re-run's 17/23 figure.

**For Part H:**
- I did not look at the scan images. Everything here rests on the scan transcription's `lines`,
  `net`, header counts and reader notes: how p0924's note is placed, what p071A2's label says,
  and where the parentheses are.
- Whether the parentheses meant "doubtful" or "repeated" to Childs is not established. C2 does
  not need it, because the counts include the bracketed symbols.
- I did not re-run comp's power trials. I re-tabulated their records only.
- I did not read J0's code. None exists yet for C1's insertion.

**For Part G:**
- I did not re-run anything for Part G. It is a reading of the revised text against Part F.
- The J0 commit does not exist yet. T, G, G′, the control list and the group letter counts are
  still the dbf591d figures, and J0 may change them. The bounds are proved for whatever J0
  fixes, but I have not seen those numbers.
- Whether the null scripts implement the procedures as written is for the result review. Seeds,
  per-target matching and the blank fill are all to be checked there.

**For Part F:**
- **I ran no attack.** I did not run jattack on anything. Every power or null figure is power.md's,
  re-tabulated from its jsonl. My own runs are the damage-model simulation (F6) and the counts.
- **The duplicate screen and the twin keys.** I did not re-run the screen. The twin-key inference
  in F4(c) and F7 assumes a flagged copy shares its twin's key. That is safe for near-identical
  texts (d < 0.2) and weaker for p101B (d 0.398), p192A (0.333), p142A2 (0.375) and p213D (0.482).
- **The net labels.** I took them from the scan transcription's `net` field. I did not look at the
  scan images.
- **The history of the RIZI and CHI nets.** I did not read about them [L, not read].
- **The source of the prereg's "537 letters".** I could not find it in any committed file.
- **Letter counts.** In F5 they are on the scan `symbols` field. Elsewhere they are clusters.csv's
  creilly counts. Each is one script of mine.
- **The F7 coverage estimate.** It rests on 24 controls, and its interval is wide.

**For Part E:**
- **R1 (ii).** I have no solver that reaches the claimed key, so I cannot supply the
  missing null either.
- **check's R1 solver runs and S1/S2.** I did not re-run them.
- **The B4 identity on Schmeh's text, and the Bean scan.** I did not check either.
- **My R2 null is smaller than check's:** 12 solved entries, not 58.
- **Whether the R2 place names fit the Alpenkorps's actual position on 10-11 Nov 1918.** That is
  a historical check, for `lit-`.
- **My scorer choice** postdates seeing check's results (E3.3).

**From the earlier passes:**

- **The ciphertext against its sources.** I did not compare `ciphertexts/adfgvx-1918-open.txt`
  with Schmeh's page, Bourdeau's `msgs.txt` or Childs. The header claims a per-message cross-check
  against Bourdeau. My letter counts are face-value counts of that file only, by one script of
  mine. They are not [C].
- **The redundancy D for 1918 German.** I used 3.2–3.6 as a bracket. I did not measure it.
- **Key-change frequency in 1918** ("about daily"). This is from general knowledge of the system,
  not read in a source here [L, not read].
- **creilly11235/adfgvx-1918 and 0wwafa's PAPER: not read by me.** Parts B and C rely on
  the prereg's statement of their claims (keys, gap position, IDs). I did not check the claims
  against the claimants' own write-ups, nor whether p179B1's gap is marked in either
  transcription. That is R's own work, and I will check it at the result review. When I review strand R, I will read the claims at source.
- **No pre-registration, power test or result exists yet.** Everything that matters for a verdict
  is still to come.
