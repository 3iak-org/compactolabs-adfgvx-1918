# Adversary on the J3 lead: the nov07 group, keyless joint, +0.0042

adv-adfgvx, 2026-11-01. Target: lead-adfgvx ticket tmvxt2rrx6ml8, `results/adfgvx-J3-runs.jsonl`
and `adfgvx-J3-nulls.jsonl` at origin/lead-adfgvx 845b919.
- **Group:** nov07 = p076A p166A p166A.2 p167A p167A5 p173A. That is 1056 symbols on the J0
  text, 206 of them lost (20%).
- **comp's result:** width 22, pscore −3.4630, against a 60-draw null max of −3.4672 (all of
  the top of the null comes from half (a), the shuffles).

## Answer

**The J3 lead is fully explained without a shared key** [S, 2026-11-01]. Its margin over the
null (+0.0042) is smaller than the amount by which the real group already beats its own
shuffles when **no transposition is searched at all** (+0.009).

The shuffle half of the J3 null is not exchangeable with this group. The other half (plant-side
text) does not carry the group's lost symbols, and sits ~0.5 lower, so it never competes. Under
a null matched for both properties, the group is unremarkable.

- **Test A: no search.**
  - Setup: random transpositions (6 per width, widths 15–22), with the square solved for each
    by my annealer.
  - Real group: mean −3.6039.
  - 30 shuffles (each member shuffled, as in J3 half (a)): draw means −3.6127 ± 0.0033, max
    −3.6045. **The real group beats all 30.**
  - So comp's +0.0042 is inside a bias that exists before any key is looked for.
- **Test B: a matched null.**
  - Setup: real ciphertexts of solved entries under six *different* keys (none nov07), cut to
    the members' lengths, with **each member's own lost-symbol mask imposed** (c). Same
    statistic as Test A.
  - c: draw means −3.6315 ± 0.0189. 4 of 30 are at or above the real group's −3.6039.
  - The same draws without the mask (c0, like J3 half (b)) are at −4.090 ± 0.030. That is the
    half of the J3 null that contributed nothing (its max was −3.764).
  - Real ADFGVX ciphertext with the group's damage spreads ~6× wider than shuffles, and the
    group sits at about its 87th percentile.
- **Test C: my own joint search.** Widths 15–22, annealed transposition with the square refitted
  per move, then a full square solve. I ran it on the real group (3 seeds), 12 shuffles and 12
  matched draws.

  | Draws | Mean | Max |
  |---|---|---|
  | Real group (3 seeds) | −3.486 | −3.475 |
  | Shuffles (12) | −3.502 | −3.485 |
  | Matched c (12) | −3.511 | −3.480 |

  - The real seeds' own spread (0.023) is as large as the gap.
  - One real seed (−3.498) is below 4 of the 12 shuffles.
  - My search does not separate the real group from either null.

**What would have to be true for this to be wrong:**
- comp's search finds a key-specific structure that mine cannot. My joint search is weaker:
  −3.475 against comp's −3.463 on the real group. I make no claim that no shared key exists.
  The claim is that the evidence offered for one (+0.0042 over shuffles) is smaller than a bias
  that needs no key.
- The Test A offset comes from my square solver and would vanish under comp's. This is unlikely:
  the effect is a property of the texts (lost-symbol bursts that survive as column-aligned runs,
  plus the column structure of real ADFGVX ciphertext), not of the solver. Still, it is measured
  with one solver.

## Why the shuffle null sits low

- **Shuffling destroys two kinds of structure that a free square can exploit with any
  transposition:**
  - real ADFGVX columns carry only row-coordinates or only column-coordinates, a structure that
    survives in long runs of the ciphertext;
  - the lost symbols come in bursts of 77, 67 and 27, which are whole columns. They change how
    the unknowns fall on cells and trigram positions.
- **Both arrive with the real group whatever its keys.** Half (b) of the null keeps the first but
  has almost no lost symbols, so it scores ~0.5 lower (Test B, c0). Neither half is matched.
- **The penalty makes the losses pay.** The unknown-trigram charge, ln(1/36) = −3.584, is above
  what a fitted noise trigram earns. So how the losses fall is worth more to the score than
  anything else in play here (cf. `adfgvx-j1.md`).

**Implication beyond this lead:** the J2 detection is the nov07/nov10 group under the nov10
square, at +0.0032 against the same kind of null. Its group is the ambiguous nov07/nov10 group, a
different set of entries, but its null is built the same way. I have not tested it, but its margin is smaller still, and the same
bias would be expected to cover it.

## Evidence

All code is in `adversary/adfgvx/j3/` (own code; none from `search/` or `verify/`).

- **`a3.c`.** Free-square solver, random-transposition mode and joint search. It is scored with
  the J3 statistic, using the LM table with lm_sha256 675a65d4….
- **`common3.py`.** Inputs, and an independent Python decryption/score.
  - It reproduces comp's J3 pscore exactly from comp's key (−3.462998).
  - On comp's transposition, a3's square solver reaches −3.453, so the square-only freedom
    exceeds comp's own result.
- **`randt.py`** gives Test A (`results/randt.tsv`, 2880 rows).
- **`matched.py`** gives Test B (`results/matched.tsv`, with sources in
  `results/matched_sources.json`; fixed seeds).
- **`joint.py`** gives Test C (`results/joint.tsv`).
- **Members are not repeats of one another.** The longest common substring between any two
  members' ciphertexts is 7.

## What I could not establish

- **A search at comp's power on matched draws.** That is the real fix: re-draw the J3 null as
  Test B's (c), real ciphertext of other keys with the group's lost-symbol mask, and re-run
  jattack mode 1 on it. That is the team's search and the team's prereg, so it is not run here.
- **Whether a shared off-list key exists for nov07.** That is not ruled out, at any power.
- **The J2 detection.** Not attacked, as the lead says it claims no reading. The bias above is
  expected to apply to it as well.
