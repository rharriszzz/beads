# Maker answers received 20 October 2026

The export was found at `/mnt/c/Users/rharr/Downloads/beads-pattern-answers.json`.
The [archived export](maker-2026-10-20.json) preserves its exact bytes, including
the maker's notes. Its SHA-256 is
`cb68b238d04c9700499b055ff93ae990b48e31076046547a3e8083dfd67c4e11`.
The baseline commit, original-photo hash, all five scientific input hashes and
all ten question identifiers/positions/coordinates match the delivered form.
Only questions 1–3 were answered. The necklace and original chart remain pending.

| Question | Answer and authority | Treatment in this assessment |
|---|---|---|
| 1, R332-R-0037-0040, position 83 | Distinct/yellow selected, but maker explicitly relied on the reconstructed picture and said photographic evidence was insufficient; requested ignoring this observation | Withhold its pigment evidence; do not count its selected yellow as an independent confirmation |
| 2, REC266-P035619, position 83 | Distinct/yellow, judged from the current photograph | Two-way provenance retained: historical software red and current maker yellow |
| 3, R332-R-0197-0183, position 189 | Distinct/yellow, judged from the current photograph | Two-way provenance retained: historical software red and current maker yellow |

The maker subsequently reiterated an earlier instruction to ignore beads near
the edge that are dark and lack usable specular reflections. Presenting Q1 again
as an unresolved conflict failed to apply that instruction. Its reconstruction-
dependent answer cannot supply independent validation of the reconstruction.
The exclusion here follows an explicit evidence-quality judgment, not a vote
for the candidate pattern. This assessment does not automatically classify or
remove other edge records. It does not require highlights as a universal test
for black pigment: darkness and highlights need interpretation in body context.

## What the answers establish

This is a separately saved assessment overlay. Historical R344 colors, active
roles, identities, coordinates, links and products remain byte-identical. Q1's
color is withheld here; its physical identity and incident links have not been
deleted or independently re-established. Q2/Q3 corrections record maker photo
judgments; they are not observations of the physical object or original chart.

| Evidence epoch | Color observations used | Candidate agreements | Supported / conflicting / insufficient positions |
|---|---:|---:|---:|
| Historical R344 | 1041 | 1038 | 199 / 2 / 7 |
| Withhold Q1 only | 1040 | 1038 | 199 / 2 / 7 |
| Correct Q2/Q3 only, retain historical Q1 red | 1041 | 1040 | 200 / 1 / 7 |
| Withhold Q1 and apply Q2/Q3 maker yellow | 1040 | 1040 | 201 / 0 / 7 |

The historical three-observation/three-geographic-region rule is unchanged.
Position 83 retains six yellow observations in five regions (0,1,9,10,11);
position 189 has eight yellow observations in seven regions (0,1,2,3,4,6,11).
**Q1 is unnecessary for pattern coverage: every one of the 208 positions still
has photographic observations.** This is pattern-residue coverage, not proof of
every physical bead around the necklace. Poor evidence should remain unknown;
coverage is a result to report, not a reason to force a color or body identity.

For the saved lattice/closure, the two A/B indexing conventions and a complete
cyclic repeat shorter than 400, all 22 possible divisor cases were checked for
each evidence epoch. Only the final assessment admits a compatible case:
**A, conditional count 2704, period 208**. Every residue is observed, so its color
word is uniquely determined within those premises and equals the existing
provisional word. Every rejected case has a contradictory pair of retained
observations in the [machine-readable assessment](assessment.json).

This is a conditional uniqueness result and complete agreement with the retained
recorded colors. It is not an independent physical proof of the lattice,
correspondence, count or original design. The seven black positions
43/75/82/89/140/147/186 still have fewer than three geographic supporters;
questions 4–10 remain unanswered. An authentic original chart can directly
confirm the intended word under cyclic offset/reversal. No additional image
classifier or rendering optimization is required to perform that comparison.

## Reproduction and preservation

Run `python3 -m photo2.r347.assess_answers` from the repository root. The script
validates the archived export and frozen inputs, preserves the raw answers,
and reproduces four explicitly distinguished evidence epochs. It changes no
historical scientific inputs. The browser's automatic save remains in browser
local storage; the downloaded export is the readable handoff to this analysis.
No source change to an earlier experiment, commit or push accompanies this step.
