# Pre-registration: ADFGVX 1918, strand R (replication of four outside claims)

Written 2026-10-31 by lead-adfgvx, before any result of ours on these entries exists. Strand J
(the joint attack on the unread pool) gets its own section here later. That section is written
only after the two mutilation censuses agree, and it is refereed before any run.

Scope: strand R only. These are not novelty claims. Each is a replicate-or-refute of an
unrefereed public claim, made between 2026-10-11 and 2026-10-28.

## Entries (B5)

Childs-log IDs are creilly11235/adfgvx-1918 data/records.json @ e60da03.

| R | log ID | Schmeh 2017 label | claim | claimant |
|---|---|---|---|---|
| R1 | p156C3 + p156C6 | p.153 VFVAX, p.153 AXVAA | parts 5-6 of one message; new 18-col transposition 16 7 13 4 15 8 17 3 1 12 14 2 5 9 10 18 11 6; 3 letters open | creilly |
| R2 | p179B1 | p.176 GGDAA | Lasry nov10 key + a 20-symbol gap at position 160, filled | creilly |
| R3 | p155E | p.152 | second intercept of the last 104 symbols of solved p139B | 0wwafa issue #1 |
| R4 | p192A | p.189 | damaged copy of solved p188_.2 | 0wwafa issue #1 |

## Inputs we may use

- The claimant's key, edits and claimed plaintext.
- The transcriptions.
- Never the claimant's code (independence).

Every result names its transcription: creilly@e60da03, and also Schmeh 2017
(`ciphertexts/adfgvx-1918-open.txt`, sha256 9362c3d2…df94) wherever that entry exists there.
A result that holds on one transcription but not the other is reported as exactly that (B4).

## Scoring

check-adfgvx's own German n-gram log-likelihood, from a corpus it names. It is fixed and
committed before it scores any R entry. Numerals and X-separators are handled by a stated rule.

## Outcome definitions (B1)

- **REPRODUCED** means both of these hold:
  - (i) our decrypt of the transcription, under the stated key and the stated edits only,
    matches the claimed plaintext except in at most the letters the claimant marked open;
  - (ii) its score exceeds the **maximum** over a null that has at least the claimant's
    freedom, with ≥ 100 null runs.
- **PARTIAL** means (i) holds but (ii) cannot be established, because the claimant's search
  freedom is undocumented or too large to replicate. The undocumented part is stated.
- **NOT REPRODUCED** means (i) fails, or (ii) fails under a null of the claimant's own stated
  freedom.

## Null per claim

- **R1 (keyless or partly keyless recovery).**
  - First establish which square is used: a known period square (then A5's known-square /
    unknown-transposition case applies, with unicity ~13-21 plaintext letters), or a recovered
    one.
  - Null: the same search family (transposition of width 18; plus square recovery if the square
    was recovered) run by check's own solver on null inputs. The null inputs are the shuffled
    ciphertext of the same length, and real 1918 ciphertext of the same length whose key is
    known to be different.
  - Joining 153a with 153b is one trial, and so is the choice of width 18 if the claimant
    searched widths. Both are counted.
  - The claimant's own null (shuffled max -301.1 vs -266.7) is cited, not adopted.
- **R2 (known key + gap).**
  - First record whether the gap is marked in either transcription. If it is not marked, its
    position and length are search freedom.
  - Null: the same gap search (every position; every length 0-20 symbols) under every WRONG
    period key on p179B1. Also, the solved entries under wrong period keys with the same gap
    search (A3's primary null).
  - REPRODUCED needs the claimed reading to exceed the best of all of these.
- **R3, R4 (duplicates) (B2).**
  - The alignment method is fixed before running. Report the matches at the best offset, and a
    gap-aware edit distance.
  - Null: the same statistic between the open entry and every unrelated solved entry in the
    log, giving an empirical tail probability with the number of comparisons stated.
  - Second test: the solved twin's key decrypts the open copy (with the alignment's edits only).
    Report what reads.

## Revision 1 (2026-10-31, referee Part C, REVISE C1-C7)

Where this section conflicts with anything above, this section governs.

- **C1 (R1 decoys).** A decoy must not have a true key inside the searched family. Decoys are
  real 1918 entries:
  - whose true transposition width is neither 18 nor commensurate with 18 (not 6, 9, 12, 36);
  - and, if the R1 square is a known period square, under a different square.

  Shuffled ciphertext stays as a second null. The decoy IDs are listed in the report before
  they are scored.
- **C2 (R1 block structure).** The report first states whether the claim transposes parts 5 and
  6 separately or as one block.
  - If separately: (i) requires EACH part to read on its own under the key.
  - If as one block: the part order and the boundary are search freedom, and they enter the null.
- **C3 (R2 fill).** The 20 filled symbols are content freedom. Every plaintext position whose
  value depends on a filled symbol is MASKED, in (i), in (ii) and in every null run. (i) and
  (ii) are judged on the unmasked positions only, and the masked count is stated.
- **C4 (two implementations).** The deterministic decrypt in (i) is done by BOTH check-adfgvx
  and comp-adfgvx, independently, and the outputs are compared. Only that agreement is [C]. The
  nulls in (ii) are check's alone and are labelled [S], with the sample stated.
- **C5 (scorer freeze).** check states the commit sha at which its scorer and corpus were fixed.
  It also states whether either changed after any exploratory contact with an R entry. If either
  did, the exploratory results are discarded, not reused.
- **C6 (budget).** Each null run gets at least the compute budget (restarts × iterations, or
  wall-time) used on the real entry, and both budgets are reported. A null that is exhaustive
  reports its enumeration size instead of a run count.
- **C7 (R3/R4).**
  - The duplicate statistic is a best-offset, gap-aware alignment score, and the null uses that
    same statistic.
  - The tail is reported twice: against all unrelated solved entries, and separately against
    solved entries of the same key or day, because formulaic traffic shares column segments.
  - 'The twin's key decrypts' is NOT counted as a second independent test. It is reported only
    as the plaintext that results.

## Revision 2 (2026-10-31, referee Part D: ACCEPT WITH REVISIONS)

- **D1 (replaces C5's remedy).** If check's scorer or corpus changed after any exploratory
  contact with an R entry, then for each R result, one of these applies:
  - (a) it is scored under the last pre-contact scorer sha; or
  - (b) every change is justified without reference to the R entries, and the report states
    that the scorer postdates contact.

  If nothing changed, this is stated with the sha.
- **D2.** The decoy IDs for R1 are COMMITTED (in check's trials log) before any of them is
  scored, and the report cites that commit's sha.
- R2's wrong-key null uses all 21 wrong keys of the 22.

## Logging

Every configuration run on R entries goes to check's trials log: keys, gap positions/lengths,
widths, transcriptions. Anything run before this file was committed is logged as exploratory and
re-run under it.

---

# Strand J: the unread pool (pre-registration, Revision 1, 2026-11-01)

This text **replaces** the first version (lead-adfgvx dbf591d). That version was reviewed by the
referee (Part F, REVISE, F1–F10) and the changes are listed at the end. Nothing in strand J has
met unread text. So far the only contact is header fields, letter counts, the decryption-free
duplicate screen and the blind scan transcription.

## J0. Inputs, pool and groups (frozen before J1)

- **Primary transcription:** `ciphertexts/adfgvx-1918-scan-transcription.json` (sha256
  `9713a390…8270`, a4028ce), field `symbols`.
  - **Detection is defined on the primary only.**
  - The re-run on creilly `printed` @ e60da03 is a robustness check. It cannot add a detection
    (F8).
- **Net:** the scan transcription's field `net`.
  - p148A and p215A.3 have none. They are treated like RICHI.
  - p220C is excluded, because it is not ciphertext.
- **Keys:** `ciphertexts/adfgvx-1918-log.keys.json` (sha256 `095de9ce…f2a7`). The J1 candidate
  keys come ONLY from the **14 Lasry period keys** (sep19 … nov28).
  - The other 8 keys are not "the period's keys". Five are Childs keys (other theatres and
    dates). The rest are `chi_2017_comments` (a CHI key, 13 Nov), `dec09_history` and
    `ours_nov07_18col`.
  - They enter only where named below (F4b).
- **Symbol policy (no alternatives tried):** a printed non-ADFGVX letter, a parenthesised symbol,
  `-` and `?` are each one lost symbol.
- **Entry structure (applied mechanically, nothing else):**
  - p0924 is split into its two blocks;
  - p083B2+p083B, p101B2+p101B and p142A2+p142A are joined, first line first;
  - p153B4+p153B is joined.
- **Duplicates:** comp re-runs `duplicates.py` on the primary transcription with its committed
  threshold. Flagged entries leave the pool and become positive controls (J1).
- **Pool:** unflagged Unsolved entries with ≥ 60 ADFGVX letters. Shorter ones are reported as
  too short. At dbf591d, on creilly letters, the referee counts T = 50. The J0 commit gives the
  exact list.
- **Groups (for J2/J3):** pool entries grouped by single derived period (`derived_period` in
  `results/adfgvx-clusters.csv`, re-derived in J0), **regardless of net**.
  - Why not by net: the evidence is that RIZI traffic was enciphered in the RICHI period keys.
    The solved RIZI entries p188_.2 and p200D are solved under nov13_16, and 8 of the 12 unread
    RIZI entries are near-copies of ciphertexts solved under period keys (referee F4c).
  - CHI entries are not grouped.
  - Entries with an ambiguous period are grouped only as in J2 (F9).
- **J0 output (committed and cited before J1 runs):** the pool list, the control list, the group
  memberships and the letter counts. All of these are computed on the primary transcription.

## J1. Known key + edits (family F3): READ-KNOWN-KEY

- **Targets:** every pool entry.
- **Candidate keys:** the entry's derived candidates among the 14 period keys.
  - Coverage of the true key: 98.3% LOO on solved entries (96.9–99.1%). Out of sample on the
    duplicate controls, 22/24 (92%, Wilson 74–98%) (F7). Both are quoted in the finding.
  - **One declared extra trial:** p201D (CHI, 15 Nov) also gets `chi_2017_comments` (F4d). Its
    blank cells make that test weak, and the null says so.
- **Edit model and cap (F6).**
  - An edit is one jattack mode-3 operation: delete 1 symbol anywhere; insert 1 unknown anywhere;
    delete a 5-group at a group boundary; insert 5 unknowns at a group boundary.
  - **Cap: ≤ 2 edits per message.**
  - Rule: the 90th percentile of jattack edits per message under the unread-scaled damage model.
    It is 2 at 60–400 symbols, and ≤ 2 edits covers about 91% of simulated messages [S, referee
    re-run; power.md gives the same p90 counted in runs].
  - Substitutions are not searched.
  - The damage model's run profiles come from one implementation of the census. That is labelled
    as a design input, not [C].
  - Every J1 NEGATIVE reads "under ≤ 2 jattack edits, covering ~91% of messages under the damage
    model".
- **Statistic:** S_t = the max over t's candidate keys of the penalised mode-3 trigram score at
  cap 2. The scorer, budget and blank-cell charge are exactly as in power.py F3 at ef93381.
- **Null: per target (F1).**
  - For each target t, there are n_t ≥ 60·T draws, made by t's own procedure (same candidate
    keys, same cap, same budget). Half are of each kind:
    - (a) t's ciphertext, shuffled;
    - (b) a plant-side solved entry whose KEY is not among t's candidate keys, cut to t's
      length, under t's candidate keys. For p201D this excludes p190A1 and p190A, which are
      solved under chi_2017_comments.
  - Threshold_t = the max of t's draws.
  - FWER ≤ Σ_t 1/(n_t+1) ≤ T/(60T+1) < 1/60 ≈ 1.7%.
  - Seeds are fixed in the script, and the null records are committed before any target is
    scored.
- **Positive controls (F2).**
  - The rule applies to the **plant-side** controls only: those whose twin is not in the
    scorer's training text. At dbf591d these were p101B, p112D, p114A, p125D1, p160A, p162B,
    p165C1, p175E, p196B, p213D and p215A2; the J0 commit gives the final list.
  - Each control gets its own per-target null, built exactly as for targets.
  - **Control detected** = above its threshold AND the maximising key is the twin's key.
  - If fewer than 50% of plant-side controls are detected, J1 is declared underpowered on real
    text, and its negatives say so.
  - Reported beside it: the Wilson interval, each control's twin alignment cost, and the
    train-side controls' rate, labelled as leakage-inflated.
- **Detection** = S_t above threshold_t.
- **READ-KNOWN-KEY** needs, in addition:
  - (i) check- reproduces the decryption from the key and the edit list alone;
  - (ii) adv-adfgvx, given the same freedom, fails to produce an equal score.

  The edit-jump diagnostic is reported. A detection that fails (i) or (ii) stays a detection.

## J2. Known square + unknown transposition, joint (family F2): READ-JOINT (partial key)

- **Groups:** the single-period groups of J0 after removing J1 detections, each of ≥ 300 letters.
  Let G be their number.
  - Plus, as two declared extra tests, the ambiguous nov07/nov10 group (4 entries, 717 letters at
    dbf591d) under each of the two squares (F9).
  - Every other ambiguous entry is excluded from J2, and the count and letters are stated.
- **Method:** the group's period square, jattack mode 2, transposition widths 15–22, at the power.py
  F2 budget (ef93381).
  - **Blank cells** of the period square are filled with the unused symbols, as in the F2 power
    test, identically in the real run and in its null.
  - Widths ≥ 23 are not searched (nov25's key is width 23) (F10).
- **Statistic:** the penalised trigram score of the final key.
- **Null: per group (F3).**
  - **For each test (group, square)**, there are n ≥ 60·G′ draws (G′ = G + 2, the two extra
    tests being the nov07/nov10 group under each square). Every draw has that test's member
    lengths and that test's square.
  - Half of the draws: members are PLANT-side solved entries whose key's square differs from the
    test's square.
  - The other half: g's members, each shuffled.
  - Threshold = the max, per test. FWER ≤ Σ 1/(n+1) < 1/60.
  - The null records are committed before any group is attacked.
  - The power.md F2 thresholds are NOT used. Their wrong-period nulls handed the attack member 0's
    own square (referee F3), and they were drawn for pre-dedup groups.
- **Power:** power.md F2, 24/70/83% by bin [S], is an approximate guide. Its null was
  conservative.
- **READ-JOINT:** needs J1's (i)–(ii), plus the adversary running a free-transposition search on
  the same group. In the controls, P(correct | above threshold) was 84–93%.

## J3. Unknown square + unknown transposition (family F1): detection only

- **Groups:** the single-period groups of J0 with ≥ 700 letters, after removing J1 and J2
  detections. At dbf591d on creilly letters, those were nov04 1670, nov22 1329, oct04 1169,
  nov01 947 and nov07 826. The J0 commit gives the final list. The test is whether the group
  shares an **off-list** key (E8), a hypothesis neither J1 nor J2 tests.
- **Method:** jattack mode 1, widths 15–22, at the power.py F1 budget (ef93381).
- **Null: per group.**
  - n ≥ 60·G3 draws, same member lengths.
  - Half are PLANT-side solved entries from several different periods (no shared key); half are
    g's members shuffled.
  - Threshold = the max. FWER ≤ Σ 1/(n+1) < 1/60. Committed before the groups run.
- **Power:** 14% (700–1299) and 32% (1300–2200) at this budget [S], limited by the search at
  width 21. A J3 negative is stated as **"no off-list shared key detected, at 14–32% power"**,
  which is a statement mainly about the method.
- **A J3 detection is a LEAD, never a reading.** In the controls only 31–49% of detections were
  the right key. It goes to check- and the adversary, and is reported as a lead whatever they
  find.

## Overall false-detection bound (referee G1)

Each family (J1, J2, J3) is held below 1/60 by its own null. By the union bound, the chance of
any false detection anywhere in strand J is below 3/60 = 5%. This is the figure stated in the
finding.

## Trials factor

- Logged in `results/adfgvx-trials.log`:
  - every (target, key, cap), (group, square, width) and (group, width) run;
  - each target's or group's null count;
  - the declared extra trials (p201D under the CHI key; the nov07/nov10 group under two squares).
- Outside families are stated beside ours, not folded in: 0wwafa §5.3, Bourdeau, and creilly's
  p.153 key on 40 unread messages.

## Order and stop rules

- **Order:**
  1. J0 commit (pool, controls, groups).
  2. J1 nulls committed.
  3. J1 controls.
  4. J1 targets.
  5. J2 group list, then J2 nulls committed.
  6. J2 groups.
  7. J3 group list, then J3 nulls committed.
  8. J3 groups.
  9. The creilly-transcription robustness re-run.
  10. check- reproduction and the adversary, for every detection.
- **Stop rule:** no step is re-run with a changed budget, cap, scorer, candidate rule or group
  rule after it has met unread text. Any such change is a new pre-registration, and everything
  before it counts in the trials factor.
- **Novelty:** recheck creilly, 0wwafa, Schmeh and Bourdeau before the write-up. A detection that
  has already been published is reported as a replication.

## Changes from dbf591d (referee Part F)

- **F1:** a per-target null replaces the pooled one, and the FWER is proved.
- **F2:** plant-side controls only; detection requires the twin's key.
- **F3:** J2 nulls are redrawn per group with the group's square; the blank rule is stated; the
  power.md thresholds are dropped.
- **F4:** the net field is named; the candidate keys are the 14 period keys only; the RIZI
  caveat is replaced by the evidence that RIZI shares the period keys (so RIZI joins the period
  groups); one declared CHI-key trial for p201D.
- **F5:** the false J3 sentence is removed; J3 runs as detection-only on groups of ≥ 700 letters.
- **F6:** the cap is restated in jattack edits (p90 = 2, ~91% coverage); run profiles are
  single-implementation.
- **F7:** both coverage figures are quoted. The all-14-keys second pass is NOT run, because it
  costs ~10× and is not required. The gap is stated.
- **F8:** detection on the primary transcription only.
- **F9:** the ambiguous nov07/nov10 group goes into J2 under both squares, as 2 declared tests.
- **F10:** widths ≥ 23 are not searched, and this is stated.

## Revision 2 (referee Part G: ACCEPT WITH REVISIONS, applied 2026-11-01)

- **G1:** null sizes are raised from 20× to 60× the family's test count in J1, J2 and J3, so all
  of strand J is held below 5%.
- **G2a:** the J2 null is per (group, square) test.
- **G2b:** J1(b) draws are from entries whose KEY is not among t's candidates. For p201D this
  excludes p190A1 and p190A.
- **G3** (recommended, adopted): J2 and J3 nulls use plant-side text.

## Clarifications C1–C3 (2026-11-01, before any J run; they add no freedom)

The scan transcription contains cases the frozen symbol policy does not name. Each case gets
exactly one reading, and no alternative is tried or counted.
- **C1. Notes in the log** (words in parentheses, e.g. "(interference)", "(missed 20 groups)"):
  these are not ciphertext.
  - If the note states a count of missing symbols or groups, that many lost slots are inserted
    at its position (5 per group).
  - Otherwise nothing is inserted.
  - Words are never read as symbols. This is how J0's "printed non-ADFGVX letter" rule is meant:
    it applies to stray letters inside symbol groups.
- **C2. Parentheses and W.**
  - A parenthesised symbol is one lost slot; a whole parenthesised group is five lost slots.
  - A printed W (or any other non-ADFGVX letter inside a group) is one lost slot.
  - comp-adfgvx proposed alternatives (W = VV; kept vs deleted groups; 32,768 variants). They are
    NOT adopted.
- **C3 (an AMENDMENT, not a clarification, per referee H2).** The scan's `net` field for p071A2
  reads RICHI, so the frozen rule did name this case.
  - It is amended, on heading evidence only and before any decryption, with one reading: p071A2
    prints "CHI-186 RICHI-186" and is part 2 of p071A1's message (same heading, 21:19, 5 Oct),
    which is CHI. So p071A2 is treated as CHI: ungrouped in J2/J3, and with J1's derived period
    candidates like every target.
  - Not tested: p071A2 as RICHI, and both parts as RICHI.
  - The oct04 group is reported without p071A2.

The cap stays **≤ 2 jattack edits**, as accepted. comp's symbol-cost cap (M = 5) is NOT adopted.
The scan-scaled power figures (comp 30b375b: F1 7/21%, F2 53/71% in the 700–1299 and 1300–2200
bins; F3 cap 2 80%) replace the creilly-scaled ones as the guide that is quoted. Thresholds are
per target and per group, as accepted, so none of this changes a decision rule.

## Referee Part H conditions (no objection to C1–C3; 2026-11-01)

These must be carried by the J0 commit:
- **H1.** C1's note position is taken from the `lines` field, not from `symbols`.
  - p0924's "(missed 20 groups)" opens line 13, which is inside block 2.
  - So p0924#1 = 290 slots with nothing inserted, and p0924#2 = 358 slots with slots 200–299
    lost.
- **H2.** C3 is called an amendment, here, in J0 and in the finding.
- **H3.** J0 lists every unit whose slot count differs from its header count by more than 10
  (e.g. p074A.2 85/192, p087C 118/244, p119A1 160/222, p222C 284/394, p140A5 215/252).
  - A J1 negative for such a unit reads "uninformative: N symbols short of the header", not the
    ~91% coverage sentence.
- The J0 commit also cites Revision 2 (G1: 60× nulls; G2: a per-(group, square) J2 null and the
  key-based J1 exclusion).
