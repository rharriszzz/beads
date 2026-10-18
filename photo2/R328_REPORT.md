# R328 — one seed grown all the way around

**The new working reconstruction has one component: 900 indexed observed supports and 1,862 links.** It starts at C-0986-0371, attaches a connected photographic patch at each of the 187 windows, and returns to 17 starting observations with the same integer translation, H=(214,201). There are no skipped windows in the selected history. This is a completed provisional circuit, not merely two fragments joined afterward.

[Photographic review and growth playback](r328/results/index.html) · [Working reconstruction](r328/results/graph.json.gz) · [Independent subset](r328/results/established-subset.json) · [Reproduce](R328_REPRODUCE.md).

## The simpler algorithm

Start with one observed support and one coordinate origin. At each geographic window, offer connected patches from the retained photographic candidate bank. Attach a patch only when its shared observations agree with the existing coordinates and its actual neighbor links connect it to that same component. No second component is started. Each selected patch contains 9 or more supports and all three primitive directions, so **both diagonal families and neighboring rows grow together**.

A bounded beam keeps competing growth histories alive. Subsequent patches decide which earlier continuation remains strongest. During the final run, the leading history changed earlier assignments at **11 frontiers**. At step 127 it reconsidered windows 122–126 together after seeing the next patch. Some older alternatives remained alive for 37 windows. A separate simple recovery rule reopens the previous five windows with a wider beam if every continuation stalls; a failure-oriented test demonstrates recovery from a wrong greedy seed choice. This emergency rollback was not needed in the photographic run.

The score is one sum of local photographic terms: target-excluded position/native response, supported sequences, retained discovery score, and the shared colored-pigment geometry penalty. These are the R327 measurements, now used directly during growth. **There is no cyclic DP, max-marginal-regret objective, binary compatibility optimizer, or separate graph-synchronization optimizer.** The seed is an observed support, not a maker index. Geographic order supplies the search direction, not bead identities.

Only the connected subpatch is asserted. Fourteen selected windows omit disconnected assignments from their parent hypothesis; those omissions are recorded, and observations may still enter through neighboring patches. Photographic cross-prediction scores retain the wider parent context, including its anchor observations: those fits are conditional photographic evidence, not a claim that every parent assignment belongs to the working lattice. All attached assignments themselves agree exactly across the grown graph.

At the end, another photographically supported patch must overlap the grown frontier and recover at least three already observed starting supports with one common translation. Its translation is measured from the return, never supplied as a target. Six otherwise eligible final extensions lacked enough return evidence and were excluded from completed alternatives. Connectivity without this return is explicitly incomplete.

## What changed in the photograph

Relative to R327: **26 links added, one old direction withdrawn and replaced, seven additional supports indexed.** All previously indexed supports remain. There are 38 unindexed observations; no new observed bead or reflection was invented.

The lower-bend bridges C-1440-3032 → C-1423-3004 and C-1440-3032 → E5-1413-3039 are now both supported by selected windows **74 and 75**. The growing search recovered compatible local evidence that the earlier global assembly omitted. This improvement is more than admitting the two formerly single-window links.

The inward bend now has an uninterrupted working lattice through C-1749-1623, C-1775-1637, C-1777-1612, C-1796-1653 and NEW-1745-1648. One existing pair, **C-1721-1566 → K-1740-1575**, changes from delta (-1,0) to (0,-1). The endpoints stay linked; their diagonal-family assignment changes. There is concrete photographic support for this choice:

| Target | Previous contexts: prediction error | Selected contexts: prediction error | Previous → selected native-response ratio |
|---|---:|---:|---:|
| C-1721-1566 | 9.71–10.40 px | 4.32–4.43 px | 0.47–0.48 → 0.82 |
| Black K-1740-1575 | 7.57–8.02 px | 5.09–5.68 px | 0.06–0.08 → 0.63–0.75 |

Errors average the affine/curved target-excluded predictions. Response ratios measure the original blurred native signal at the predicted position relative to the observed support. These correlated contexts favor the new interpretation; they do not independently disprove every alternative. Exact predictions and anchor IDs are in [the changed-link ledger](r328/results/changes.json.gz).

The upper bridge remains linked. The faint black site near (290,1410) retains its three provisional links. Other newly indexed supports are C-0615-0584 and NEW-1681-1498. The latter's three previously withdrawn links return as working choices. The original observation positions and all earlier candidate evidence are preserved.

The hard two-window admission rule is removed from the **working** graph. Twelve of its 1,862 links have a single selected-window witness. The existing foreground and potential-intervening-observation checks remain unchanged. No arbitrary distance bridge or general threshold relaxation is used.

## Alternatives and stopping

Search widths 32, 128 and 256 select the same primary graph, score and winding. A final replay with an explicit minimum return-overlap check also leaves that primary unchanged. The final beam retains **16 alternative completed windings**, each with its own connected growth history and photographic consequences. They are not combined into one graph.

| Alternative H | Score below primary | Changed windows | Common-support mean prediction error, primary → alternative |
|---|---:|---|---:|
| (215,200) | 1.359 | 124–126 | 3.785 → 3.802 px |
| (213,202) | 4.010 | 122–125 | 3.785 → 3.792 px |
| (214,202) | 6.261 | 11–14,16 | 3.785 → 3.773 px |
| (213,201) | 8.180 | lower bend 79–82 | 3.784 → 3.788 px |

The close runner-up is a real remaining ambiguity. Lower-bend alternatives were extended through subsequent windows and the return, rather than rejected at the first uncertain link. Position error alone does not determine the score; native response, sequence and shared geometry also contribute. Score gaps are heuristic preferences, not calibrated probabilities. H=(214,201) is the selected working winding; **no physical bead count or color pattern is adopted**.

The four searches took **10.719 + 47.381 + 100.441 + 98.153 = 256.694 seconds**, within the 600-second cumulative search allowance. Native pair preparation took 2.723 seconds. The R327 candidate bank is cached input, so these timings are not a cold detector benchmark or a speedup claim. Verification, review and retrospective analysis are separate. Search stopped after wider beams and the return-check replay agreed, not because the entire candidate space was proved exhausted. Beam pruning and the retained candidate bank still limit exploration.

## Verification and independent evidence

Independent replay verifies every attachment and **5,964 local edge equations**, proves connectivity at each of 188 patch attachments, checks every exported edge against native foreground/intervening-support measurements, and checks all global coordinate and return equations. Recomputing **3,232 native prediction rows** exactly reproduces the cached predictions and utilities. Four native photographic crops match the original pixels exactly. Growth playback, overlay toggle, desktop, narrow and offline browser checks pass.

Failure-oriented tests cover disconnected attachment, shared-row disagreement, duplicate lattice ownership, a free return translation, a contradictory return, rollback recovery, and a connected but unfinished circuit. The historical R161 check is performed only after the working graph is sealed: **25/25 interior associations and 45/45 interior links, zero wrong**; all-reference recovery stays 33/40 associations and 65/86 links, with 21 missing endpoint associations. This reference was exposed in earlier development, so it is retrospective, not a fresh blind test.

The 45 historically supported interior links and 20 peripheral reference links remain in a separate [independent subset](r328/results/established-subset.json). The wider 900-support reconstruction is provisional. Completing the circuit demonstrates that this growth algorithm can pursue and revise a coherent working interpretation; it does not independently establish the accuracy of every added link.

Original photograph, R161, R319–R327, every older result and beads.pov are preserved. The initial searches, alternative paths and browser-launch correction are retained under r328/development. No physical fitting or model/session switch occurred. Stop for photographic review of this completed working circuit.
