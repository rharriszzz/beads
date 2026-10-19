# R336 — phantom evidence rejected, identities separated, five links repaired

**All ten maker decisions have been applied. All five previously withheld links
now pass their remaining checks and are accepted in the R336 working layer.**
The [new review](r336/review/index.html) contains only two visible row-continuation
questions. Solved phantom/weak observations and corrected edge colors are not
questions there. The [completed pixel investigation](r336/review/evidence.html)
and [completed link illustrations](r336/review/repairs.html) are separate appendices.

Baseline is delivery `8c8ecab00f726c2010c2571e9ada953a60e878dc` on
`photo-2-strategy-v3`. All historical R330–R335 observations, photographs, source
code, corrections and scientific artifacts remain unchanged.

## What went wrong with the alleged body evidence

The investigation preceded applying the other changes. Both cases reproduce at
their actual native coordinates; there is **no crop, orientation, scale or cached-ID
transformation error**. The bug is an inference/ownership failure in evidence
generation, compounded by recentering and misleading body terminology:

1. R332 queried a 12px disk around a predicted vacant lattice site.
2. It selected a connected dark, low-chromaticity pixel component. That component
   could be neighboring glass, a dark boundary or cast shadow rather than a new body.
3. It moved the proposed observation to the component centroid and sampled again.
   The enlarged second sample was reported as native body/material evidence.
4. The foreground mask deliberately fills bead-scale holes and includes dark pixels.
   Its value of1 in these regions does not distinguish glass from shadow.
   Later pigment classifiers also did not establish a separate bead's existence.

| Candidate | Initial predicted query | Initial response → marker | Resampled response |
|---|---|---|---|
| R332-B-0196-0183 | (571.569,629.095) | 32 pixels → (561.969,629.656) | 208 pixels; centroid(557.236,631.365) |
| R332-B-0138-0130 | (1736.941,1547.837) | 143 pixels → (1743.455,1545.769) | 246 pixels; centroid(1745.191,1545.260) |

For the first case, the response moves toward the existing K-0548-0636 body and its
edge. For the second, a dark outer-edge/shadow component is not a distinguishable
new glass body. The maker's negative visible-body judgments therefore supersede
these responses. **Both candidates are rejected as visible bead observations.**
They were provisional, so rejecting them removes no previously indexed site.

The appendix shows the exact initial pixels, resampled pixels, R334 intensity-test
annulus and R335 compact annulus, independently toggleable over unaltered native
photographs. Marker1, reassessed P and initial P0 are distinct and have exact keys.
No prediction is substituted for a measured center.

The corrected R336 evidence API calls these **threshold responses**, explicitly
sets `visible_body_established=False` and `can_create_bead=False`, and prevents
admission from that evidence alone. A separate body identity needs independent
ownership/shape evidence; a reflection, centroid, fitted vacancy or predicted color
cannot certify itself. Historical R332 code is retained; the new evidence consumer
does not run its permissive prediction/centroid admission path.

The global check covers **687** retained R332 native-evidence records:194 black
responses, including60 prediction-seeded black records.158 records of all colors
have an initial relocation of at least6px. These are **risk flags, not158 discovered
phantoms**. All actual stored pixels were re-read and checked. The seven previously
working prediction-seeded black observations were also inspected in native context;
no additional exclusion is asserted solely from their threshold statistics. Their
existing conditional working status is not promoted to independently validated body
identity. No unreviewed candidate was newly admitted.

## Exact maker decisions and active roles

The [machine ledger](r336/results/maker-decisions.json) resolves each reference
against the actual R335 target panel and its own feature key. The actual browser
inspection expands all ten original keys; no global-number interpretation is used.

| Named photograph / feature | Stable observation | R336 decision |
|---|---|---|
| K-1508-3038 /2 | E5-1499-3037 | Phantom; retain pixels as lighting evidence, exclude all bead-inference roles. |
| K-2225-1294 /2 | E7-2235-1306 | Exclude weak reflection from association, indexing, counting, obstruction and pattern. |
| NEW-946-2684 /2 | E5-0948-2669 | Exclude unreliable dim observation from all active bead roles. |
| NEW-985-2766 /2 | E5-0986-2754 | Exclude dim support; retain the existing brighter, body-consistent observations, without inventing a second body at the weak point. |
| R332-B-0196-0183 /1 | same ID | Reject as a visible-body candidate after causal pixel audit. |
| R332-B-0138-0130 /1 | same ID | Reject independently; same ownership/recentering failure class. |
| R332-B-0098-0092 /1 | same ID | Maker-confirmed one body at proposed site(98,92); defer active fitting/pattern use. P is the same bead; D40-K-1036-2780 is **not** merged. |
| C-1979-2669 /1 | same ID | Accept1=P association at(71,66); retain yellow and uncertainty, exclude edge observation from active roles. |
| REC266-P146299 /1 | same ID | Maker-corrected **yellow**; exclude difficult edge observation from active fitting/pattern use. |
| NEW-1927-2829 /1 | same ID | Maker-corrected **red**; exclude from active fitting/pattern use as requested. |

There are no image-location changes or forced lattice remappings. The two accepted
1=P associations each describe **one** physical identity; P was already proposal
metadata, not a second accepted observation. The reflection-free black body's
REC266-P134549 cache alias remains within its own group, separate from numbered2.
Unindexed, unresolved supports cannot automatically block links merely because a
point exists; role flags distinguish recorded evidence from established identity.

Local geometry uses the same three primitive-family support spacings for every
color. These are support-displacement proxies, **not measured bead centers or exact
outside diameters**. Actual body boundaries/alignment and maker judgments supply
the physical identity constraint. No new shape parameter or renderer was introduced.
Matched5px apertures give peak luminance .243 for E7-2235-1306 versus .730/.801 for
its two neighboring black supports; E5-0986-2754 gives .330 versus .701/.897.
This corroborates relative weakness without treating glints as separate bodies.

## Blocked links: all five repaired

Each excluded blocker was the sole old intervening observation. After exclusion,
all five have no remaining blockers, pass the original filled native-corridor gate,
fit common local spacing, and satisfy the unchanged lattice equation modulo H.

| Accepted working link | Family | Length / nearby same-family median |
|---|---|---:|
| K-1508-3038 → K-1473-3021 | F0 | 1.175 |
| K-1508-3038 → NEW-1487-3054 | F1 | 1.105 |
| K-2225-1294 → K-2244-1307 | F1 | .952 |
| NEW-946-2684 → K-0951-2652 | F0 | 1.118 |
| NEW-985-2766 → MAT25-K-0980-2735 | F0 | .985 |

Filled foreground fractions are1.000 for all five. Raw mask fractions are also
retained (.106–.844); the original threshold does not include every bright/neutral
glass or reflection pixel. The filled mask is a corridor/silhouette check, **not
independent glass-body proof**. The maker-resolved identities, native contexts,
common alignment/spacing and exact equations are additional evidence. These remain
working hypotheses, not a claimed whole-photo accuracy certification.

All1,064 original records and1,041 coordinate assignments remain in the retained
evidence layer. The active layer has **1,057 records,1,039 indexed sites and2,284
links**, in one component. Seven recorded observations are excluded; the two
rejected candidates and the deferred black association were never active indexed
records. Five links are added; six historical links incident on the two excluded
indexed edge observations become inactive. The retained layer contains2,290 links.
All retained old equations and established neighbor relationships remain exact.

## Pattern effects, with exclusions separated from corrections

Only the existing(16,16) relation, fixed BR3/3 and BY2/2 staircase rules, and208
consensus were reevaluated. No repeat-length, winding, rendering or classifier search.

| Cohort / change | Observations | (16,16) agreeing/pairs | Significant disagreements | 208 known/unknown |
|---|---:|---:|---:|---:|
| R335 baseline | 1041 | 713/748 | 6 | 180/28 |
| Maker colors only, same1041 | 1041 | 715/748 | 4 | 180/28 |
| Common active cohort, before | 1039 | 713/746 | 4 | 180/28 |
| Same active cohort, after link repair | 1039 | 713/746 | 4 | 180/28 |
| Fixed interior-support proxy, before | 710 | 429/440 | 0 | 149/59 |
| Same interior proxy, after | 710 | 429/440 | 0 | 149/59 |

The fixed interior proxy requires at least four **pre-repair** working neighbors.
It is a conservative connectivity criterion, not a certified photographic edge
classifier. Its membership is frozen across comparison, so adding links cannot
manufacture a better evaluation cohort. Marginal observations remain available in
the broader diagnostic; they are not silently relabeled to erase contradictions.

The common active cohort's deterministic regular cover retains63 segments and
increases distinct coverage623→627 after adding the five measured links. Coverage
depends on the path-cover choice and is not accuracy. Maximum BR/BY lengths remain
16/15. The stricter710-support cohort's30 segments/280 covered observations remain
unchanged. Its zero disagreements were already zero; reducing the cohort is not
proof of a correct reconstruction.208 remains a useful spatial tile, divisible
by13 and incompatible with the actual shortest stringing repeat constraint.

## Next review and checks

The next page has two carefully delimited row-continuation questions around
**C-1423-3004** and **C-0481-1576**. Both involve visible indexed bodies and two
existing diagonal routes versus saved competing direct continuations. Current
Δ(a,b)=(−1,−1) is nonprimitive; the dashed alternative cannot be added without a
coherent row remapping. Cached overlapping-window support is correlated evidence,
not independent confirmation of an error. No alternative is adopted, and the maker
may say the photograph cannot distinguish it. Unresolved edge colors and invisible
sites are not new questions.

[Independent verification](r336/verification.json) checks all ten mappings,
four suspicious pixel sets,687 native-response records, five repairs, active
occupancy/component/equations, six matched diagnostic cohorts,3,136 staircase
edge incidences,51 numbered supports and11 literal native crops. All **910 sealed
historical scientific files** remain unchanged. R161 remains33 associations,
25 interior,65 links,45 interior and zero retained wrong links. These checks are
reproducibility/regression evidence, not new blind body-identity accuracy.

[Reproduction commands](R336_REPRODUCE.md), native-pixel exports, decision/role
ledgers, global risk flags and browser receipts accompany the delivery. The [fresh exact replay](r336/performance.json) takes about8.8s across five
processes, peaking at1.62GiB during review generation. Native coordinates, science
JSON, viewer templates and crops reproduce exactly, excluding measured time only.
The work is bounded, uses cached evidence and native pixels, and introduces no
color-model complexity. Logs/handoff are updated and scoped work pushed with independent
remote confirmation. Stop for maker review; no automatic R337.
