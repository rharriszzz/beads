# Finish verifying the necklace pattern

**Answers received:** [maker export and assessment](r347/answers/ASSESSMENT.md).
Questions 1–3 were answered. Following the maker's note, Q1 is withheld as
insufficient photographic evidence; its yellow selection relied on the
reconstruction. Q2/Q3 are recorded as maker photo-based yellow corrections in a
separate assessment. This gives 201 supported / 0 conflicting / 7 insufficient
positions and 1040/1040 retained-color agreement. All 208 positions remain
observed. The conditional finite check uniquely admits A/208; physical and
original-chart validation remain separate. Historical R344 products are unchanged.

[Open the answer form](r347/review/index.html). Questions 1–3 are complete; the seven remaining color checks are in the next group. A fresh browser starts unanswered, so import the saved export to restore existing answers if needed. Previous maker decisions remain unchanged.

The running local address is [localhost:8347/photo2/r347/review/](http://localhost:8347/photo2/r347/review/). The form also works directly from its HTML file. Export answers before changing browsers or moving between the file and localhost addresses, because each address has separate browser storage. To restart the local server later, run this from `~/git/beads`:

```sh
.venv/bin/python -m http.server 8347 --bind 127.0.0.1 --directory /home/rharris/git/beads
```

The maker reports that both the necklace and original chart are available, although finding them may take days. The form works with the current photograph now and can be completed later. It saves answers in the browser and exports JSON or a short summary to paste into the conversation.

## The exact result available now

The complete proposed word has **minimal cyclic period 208**. This is proved by pairs of supported colors that disagree under every proper divisor of 208. That result does not depend on choosing colors at the nine uncertain positions: the witnesses use the already supported entries.

There is also a finite uniqueness proof with explicit premises:

1. Keep the current photographic lattice and its circuit translation H=(214,201).
2. Interpret the two possible family conventions as A=7a+6b, N=2704, or B=6a+7b, N=2691.
3. Assume the necklace consists of complete repeats with shortest period below 400, as specified in the reconstruction history.
4. Establish the actual body identities and colors used as observations.

For each convention, an exact shortest period must divide its count. All possible divisors below 400 are:

| Convention | Conditional count | Possible exact periods |
|---|---:|---|
| A | 2704 | 1, 2, 4, 8, 13, 16, 26, 52, 104, 169, 208, 338 |
| B | 2691 | 1, 3, 9, 13, 23, 39, 69, 117, 207, 299 |

With the **historical R344** 1,041 labels, none is exactly compatible: 208 retains its three contrary observations. In the initial, explicitly hypothetical case that independent inspection establishes those three as yellow, **A/208 is the only compatible case**, and every one of its 208 colors is determined by observations. Every rejected case has a saved pair of contrary colors at the same residue. That original certificate remains unchanged. The later maker assessment above instead withholds Q1 and corrects Q2/Q3, with a separately reproduced certificate.

[Finite certificate, all cases and witnesses](r347/conditional-proof.json) · [Source builder](r347/build_review.py) · [Frozen input hashes](r347/input-seal.json)

The physical truth of the lattice, total count and observations remains a premise. Enumerating periods cannot prove its own premises. Matching an authentic original chart is a more direct way to verify the original design and does not require solving camera or lighting.

## Questions from the current photograph

Each question shows an untouched crop, the same crop with local numbers, and the current proposed adjacency. **The target is feature 1 in its own panel.** The mark is an existing image cue; it is not asserted to be a measured bead center. Wider context is available. Existing same-position sources can be inspected separately; their pictures have their own keys.

For each target, answer three short fields: whether it identifies a distinct bead, the actual material color, and the evidence used. Choose “cannot tell” where necessary. If the cue is a reflection or edge of another numbered body, identify that body in the note. This must be resolved as an identity issue, rather than deleting a contrary reading to improve the pattern.

| Question | Existing source | Pattern position | Purpose |
|---|---|---:|---|
| 1 | R332-R-0037-0040 | 83 | Contrary red reading; identity and material need inspection |
| 2 | REC266-P035619 | 83 | Second contrary red reading, separately inspected |
| 3 | R332-R-0197-0183 | 189 | Contrary red reading; identity and material need inspection |
| 4 | K-1171-1518 | 43 | Direct pigment check of a unanimous but insufficiently corroborated entry |
| 5 | K-1069-1565 | 75 | Direct pigment check; the earlier K-1740-1575 approval is reference only |
| 6 | K-1037-1557 | 82 | Direct pigment check |
| 7 | D40-K-1014-1544 | 89 | Direct pigment check |
| 8 | K-1543-1467 | 140 | Direct pigment check |
| 9 | K-0824-1612 | 147 | Direct pigment check |
| 10 | D40-K-1384-1467 | 186 | Direct pigment check |

The old three-observation/three-region rule was a conservative corroboration policy. It is not a mathematical necessity to obtain a third photograph of an already identified bead whose pigment can be established directly. A new explicit maker judgment can strengthen the evidence while the historical R344 scores and their definition remain intact. The form collects that judgment separately; it does not automatically rewrite the strict pattern.

### What different answers will mean

- **Yellow at a contradictory target, with a sound body identification:** preserve the old reading and add a correction with its source, then evaluate the same fixed cohort again.
- **Confirmed red at its current identity and association:** this is a counterexample to the proposed exact 208 repetition on that mapping. Inspect the local association or original chart; do not majority-recolor it.
- **Not a separate bead or an alias of another mark:** verify the identity and its incident links from the native context before changing any active inference role. Do not simply remove a difficult point to claim proof.
- **Cannot tell from this image:** retain the uncertainty and use the necklace, chart or an additional image when available. Another classifier threshold is not the missing evidence.

## Verification from the original chart

When the chart is found, provide one complete repeat as R/Y/B or full color names. Include its reading convention if the chart's string order is unclear. For alternating 6/7 paper, transcribe the actual selected strip, without its side extensions or vertical continuation copies. A photograph or scan of the chart can also be supplied in the conversation for transcription with an independent check.

The form computes the entered word's shortest repeated block and compares it with the candidate under **all cyclic starting offsets and both reading directions**. It accepts a longer sequence containing several complete copies. Check the independent-record box only for an authentic record belonging to this necklace, not a copy of the reconstruction. Matching a retyped reconstruction adds no independent evidence.

An exact match to an authentic chart establishes recovery of the **intended design sequence**, up to start and direction. It does not by itself prove that every bead in the physical necklace follows the chart. To establish that stronger assembly claim, inspect the three discrepant bodies in a way tied to their photographed neighbors; if the physical object has been rearranged, its repeated motif alone may not uniquely locate a particular photographed occurrence. Independent total-count or repeat-count information is useful if available. The form leaves both unknown rather than prepopulating the inferred 2704/13.

If the chart differs, compare the actual differences before deciding whether the cause is a transcription convention, a design difference or a reconstruction error. A mismatch is informative and will not be forced into the candidate.

## Scope and preservation

R347 prepares the proof certificate, an answer interface and the separately saved assessment of received answers. It runs no new detector, geometry optimizer or renderer, and changes no existing scientific source, label, graph, pattern, material, camera or light. The assessment records its corrections and withheld evidence separately. It leaves the retrospective documents and stopped R340 files untouched. No commit or push is part of this step.

The 10 literal crops are verified against the original decoded RGB, and retain its embedded color profile. [Artifact checks](r347/artifact-checks.json) and [browser checks](r347/review/browser-verification.json) document the delivered interface. Answers 1–3 have now been received and preserved separately; 4–10 and the original chart remain pending.
