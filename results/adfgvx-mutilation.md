# ADFGVX 1918: mutilation census of the solved log entries

comp-adfgvx, 2026-10-31. Branch `agent/comp-adfgvx`.

Every number below is copied from a generated file. Regenerate them all with
`search/adfgvx/run_all.sh`:
- `results/adfgvx-mutilation.tables.md`: the tables, with a provenance header;
- `results/adfgvx-mutilation.csv`: one row per message;
- `results/adfgvx-census-validation.md`: engine and census validation.

If a number here disagrees with those files, the files are right.

**Transcription:** creilly11235/adfgvx-1918 @ e60da03, field `printed` (the Childs log as
transcribed from the scan). Schmeh's 2017 text is not used here. The page re-readings appear only
in the class C split.

**Evidence status.** All counts are exhaustive over the stated set, by ONE implementation
(`search/adfgvx/`). They become [C] only when check-adfgvx's independent census agrees. Until
then they are "computed, one implementation" (2026-10-31). Rates extrapolated beyond the
measured set are [H] and are marked as such.

## The answer, in five lines

1. **Census, as reconstructed (591 solved entries).**
   - Median 0 edit events per message; p90 2, p95 3, p99 9, max 70.
   - 140 messages (24%) need at least one event, and 41 (7%) need three or more.
   - Per 100 reference symbols: mean 0.35 events, p95 1.5, p99 4.4.
2. **The census is biased low, and not mainly by minimality.**
   - On 2,000 planted controls, minimal-edit reconstruction recovers 94.9% of planted symbol
     edits. It undercounts in 2.5% of controls.
   - The larger bias is invisibility. In the 465 "as transcribed" entries, the plaintext *is*
     the decryption of the log text, so a wrong symbol (E5) re-encrypts to itself and the census
     cannot see it.
   - Thirty-seven pairs of repeated receptions show that E5 is real: 0.66 wrong symbols per 100
     symbols per copy. The census finds about 1/7 of that on the same copies.
3. **The unread entries are more damaged than the solved ones, on every header-free measure.**

   | measure | unsolved | solved | Fisher p |
   |---|---|---|---|
   | odd length | 35% | 17% | 5e-4 |
   | entries with a lost mark | 63% | 39% | 8e-5 |
   | lost marks per 100 slots | 3.6 | 0.7 | |
   | header count ≠ received length | 81% | 29% | 4e-14 |
   | median \|header count − length\| | 9 | 0 | |

   This is the survivorship bias of referee A1, measured. A cap read off the solved
   distribution would be exceeded by much of the unread pool.
4. **Much of the damage in the log text is transcription.** For the 44 entries whose page creilly
   re-read, 630 of the 730 edits lie between the log transcription and the page reading, not
   between the page and the true ciphertext. No unread entry has been re-read. (The caveat on the
   page readings is below.)
5. **One clerk error (E6) was found.** p135B (Schmeh "Page 132"): a single interim-text
   insertion at position 54 explains, with no residual, what costs 71 edits in ciphertext space.
   No other message is explained better by E6.

What would make this wrong:
- creilly's `printed` field is not what the attack will meet. The census is against that
  field.
- creilly's plaintexts are not the true plaintexts. They are creilly's 2026 decryptions;
  Lasry et al. 2017 published keys and totals, not per-entry plaintexts.
- The repeated-reception pairs are not copies of one cryptogram.
- check-adfgvx's census disagrees with this one.

## Method

**Set.** Every entry in `ciphertexts/adfgvx-1918-log.records.json` (creilly11235/adfgvx-1918
@ e60da03) with status `Solved*`, a key and a plaintext: 591 entries.

**Reference and observed.**
- T = encrypt(plaintext, key), using our engine (`search/adfgvx/engine.py`, written from the
  cipher's definition).
- An unknown plaintext character (`- ? # _`) becomes a wildcard pair `**`: 3,010 of 127,426
  reference symbols.
- O = `printed`, the log as transcribed, with `-` for a slot the log shows as lost.

**Edit script.** The minimal-cost alignment of T to O (`search/adfgvx/align.py`):
- substitution 1, deletion 1, insertion 1;
- a `-` slot against a known symbol costs 0 and is counted as E4;
- a wildcard costs 0.

The aligner also returns the number of optimal alignments and the [min, max] of each type
over ALL of them. It is cross-checked against an independent C cost function (`edcost.c`)
on every message (an assertion in `census.py`).

**Vocabulary.** 0wwafa PAPER.md §3, used as vocabulary only. We read their §2, §3 and §5.3 and
none of their code.

| type | how it is counted here |
|---|---|
| E1 | a run of consecutive deletions whose length is not a multiple of 5 |
| E2 | a run of consecutive insertions, same rule |
| E3 | a deletion or insertion run whose length is a multiple of 5 (a lost or duplicated group) |
| E4 | a lost mark |
| E5 | a substitution |
| E6 | tested separately on every message with cost ≥ 2: does ONE insertion or deletion in the interim text (before transposition) plus residual edits beat the ciphertext-space script? |

E7 (wrong day) and E8 (key not in the list) cannot be seen by a census that is conditional on
the key.

**Events and symbols.** An event is one run (E1/E2/E3) or one substitution (E5). E4 marks are
reported separately and not counted as events: an attacker gets their positions for free.

**Classes,** by creilly's `method` field:

| class | entries | what it means |
|---|---|---|
| A | 465 | read as transcribed |
| B | 79 | length repaired |
| C | 44 | page re-read (`ciphertext` field ≠ `printed`) |
| D | 3 | other |

## Results

### Edits per message (tables §2–§3)

| class | n | events: mean | median | p90 | p95 | p99 | max | symbol edits: mean | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| A as transcribed | 465 | 0.03 | 0 | 0 | 0 | 1 | 1 | 0.03 | 0 | 1 |
| B length repaired | 79 | 1.56 | 1 | 3 | 3 | 4 | 4 | 2.75 | 6.1 | 10 |
| C page re-read | 44 | 5.93 | 3 | 9.7 | 10 | 48 | 70 | 16.6 | 37.9 | 194 |
| ALL | 591 | 0.68 | 0 | 2 | 3 | 9 | 70 | 1.65 | 7 | 194 |

Messages with at least k events:

| k | 1 | 2 | 3 | 4 | 5 | 10 |
|---|---|---|---|---|---|---|
| messages | 140 | 65 | 41 | 24 | 17 | 5 |

The 16 class A events are each a single extra symbol (E2): an odd-length log text whose
surplus symbol the decryption ignored.

### By type (tables §4), all classes

| type | events | symbols |
|---|---|---|
| E1 symbols dropped | 128 | 272 |
| E2 symbols inserted | 134 | 233 |
| E3 whole groups | 33 | 360 |
| E4 lost marks | | 124 |
| E5 substitutions (canonical alignment) | 108 | |

Over all optimal alignments the totals range over:

| | min | max |
|---|---|---|
| substitutions | 72 | 110 |
| deletions | 376 | 395 |
| insertions | 487 | 506 |

The type breakdown is forced except in 4 messages. 118 messages have more than one optimal
alignment, mostly an indel sliding inside a run of equal symbols, which changes no count.

### Outliers (tables §6)

- **p149C1** (194 symbol edits). The log row holds 367 slots against a 176-symbol reference: a
  190-symbol tail that is another entry. This is a structure error of the transcription, not
  mutilation. Exclude it from any rate, or treat it explicitly.
- **p135B** (71). The E6 case above.
- **p077C, p075A1, p126A2, p163B, p060A3, p165B1, p07943, p162A, p153B3** (19–40 each). All are
  class C, and in every one of them almost all of the cost is transcription (§9 of the tables).
- The largest class B cost is 10.

### The E6 test (tables §5)

84 messages were tested. Exactly one, p135B, is explained better by a single clerk error than
by ciphertext edits: residual 0 after the interim insertion, against 71.

### Header count against received length (tables §7)

Of 563 census entries with a header count, the count equals the true (reference) length for
506 (89.9%).

Header counts are not error-free:
- In class A, whose log text decrypts perfectly, the header count still disagrees with the
  length in 50 of 444 entries (11.3%), and by more than 10 in 17 of them.
- So a header mismatch is evidence of damage, not proof of it. The baseline is ~11%
  count-or-transcription noise.

## How the low bias was handled, rather than hidden

Referee A1 says minimal-edit reconstruction undercounts. We separated three sources of
undercount and measured each.

1. **Ties among minimal scripts.** We report the [min, max] of every type over all optimal
   alignments, not one arbitrary script (above).

2. **Minimality itself.** `validate.py` §3 used 2,000 planted controls:
   - random keys, widths 15–23, lengths drawn from the census;
   - event profiles drawn from the census rows at random positions;
   - extra E5 at the repeated-reception rate.

   The minimal cost never exceeded the planted count. It equalled it in 97.5% of controls with
   damage, and recovered 94.9% of planted symbol edits overall. Undercount comes from adjacent
   edits merging, such as an insertion next to a deletion becoming a substitution. This source
   is small.

3. **Invisibility of E5, the large one.** The census compares the log text with a plaintext
   that was itself obtained by decrypting that log text. A wrong symbol therefore shows up as a
   garbled plaintext letter, never as an edit.

   We measured it without any reconstruction (tables §10):
   - Take 37 pairs of solved entries with the same key, the same plaintext length and ≥ 90%
     positionwise plaintext agreement. Each pair is two receptions or copies of one cryptogram.
   - Their LOG texts can be compared directly: 90 substitutions over 6,870 symbol positions.
   - That is **0.655 substitutions per 100 symbols per copy**, assuming independent errors that
     never coincide, so if anything an underestimate.
   - Plaintext agreement threshold f = 0.95 gives 0.575; f = 0.8 gives 0.657.
   - On the same 68 copies the main census records only 11 E5.

   **Extrapolation [H]:** about 1.3 hidden wrong symbols in a typical 200-symbol message. This
   is an estimate of the rate, not a count per message.

   Indel events between copies come to 0.255 per 100 symbols per copy, against 0.23 per 100
   for E1+E2+E3 events in the main census (295 events over 127,426 reference symbols). This is consistent with indels NOT being hidden
   the way E5 is.

A **fourth source** (survivorship) was not corrected, only measured. The unread set is a
different, more damaged population (tables §8):

| | solved (591) | unsolved (83) |
|---|---|---|
| odd slot count | 17.4% | 34.9% |
| any lost mark | 39.4% | 62.7% |
| lost marks per 100 slots | 0.69 | 3.59 |
| header count ≠ slots | 29.0% | 81.5% |
| median \|header count − slots\| | 0 | 9 |
| \|d\| > 10 | 34 / 563 | 24 / 54 |
| median length (slots) | 210 | 161 |

Every rate difference is significant (Fisher two-sided, p from 4e-14 to 4e-3). The length
difference has Mann-Whitney p = 4e-7. The unread entries are also shorter.

No census of solved messages can tell how the unread ones were damaged. It can only say they
were damaged more. The header-count statistic is the one damage measure that exists for the
unread entries without decryption. We report it per entry in `results/adfgvx-clusters.csv` so
the prereg can use it.

## Transcription against reception (tables §9)

For the 44 page re-read entries:

| | total edits | median |
|---|---|---|
| total (true vs log text) | 730 | 8.5 |
| reception (true vs page reading) | 88 | 0 |
| transcription (page reading vs log text) | 630 | 7 |

Caveat, which limits this split: for 32 of the entries, creilly's `method` says the page reading
was "a model read of the decode". That reading was guided by the decryption, so it may have
absorbed real reception damage into the "transcription" share. The split is an upper bound on
transcription and a lower bound on reception.

Either way, the log text of the unread entries comes through the same transcription pipeline,
and none of them has been re-read. **An independent transcription of the unread entries from the
Childs scan** (Bean's index of the Aegean Park PDF; creilly's page files give the PDF page per
entry) would remove a large, measurable share of the damage before any attack. It costs no
trials. I recommend it to the lead before the prereg fixes a cap.

## What I could not establish

- **Whether creilly's `printed` matches Childs's page.** I did not read the page images. The
  class C numbers suggest it often does not.
- **Whether the plaintexts are right.** They are creilly's, and unrefereed. A garbled
  plaintext letter in a class A entry is an E5 that we count only through the repeated-reception
  rate.
- **The meaning of `count_in_log`.** It is creilly's field ("the heading counts N symbols"). I
  did not check it against the page.
- **Whether repeated-reception pairs are independent receptions** (two stations) or a repeat
  transmission copied by one operator. If copies share errors, the per-copy rate is
  underestimated.
- **E7 and E8,** by construction.
- **[C].** It awaits check-adfgvx.

## Disclosure on independence

- I read creilly's DATA files (`data/*.json`, `SOURCES.md`) and the parts of its README that
  describe the fields and the status table.
- One grep over its README briefly showed lines of the prose description of the p.153 search
  method (split, pair, order, square). It was not used here.
- I did not open `scripts/` in creilly or `src/` in 0wwafa.
- I did not contact check-adfgvx.
