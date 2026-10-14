# R284B checkpoint 0 — requirements and initial diagnosis

Preflight: daisy, clean73021c2/photo-2-strategy-v3, no stashes, fetched origin0/0.
Read current project instructions/handoff/plan/log, R282 specification/integrated
report, R283/R284A reports, Phase1 implementation and scientific tests/results.
Full user request and planned experiments saved before algorithm changes.
300–500-word explanation written in R284B_ALGORITHM_EXPLANATION.md.

User chooses A as picture1 starting point, with lower-left tails still wrong.
For black, R283/A are starts; C is NOT preferred. Reflection only, no dark collar.
Picture3 B is smoothest but fails brightness agreement; its splitting remains a
failure. These are method-development/evaluation guidance, not runtime identities.

Hypotheses to test next: capped disk opening leaves broad tails; one-pixel
reconstruction regrows them; low brightness saddles are ignored by morphology.
Contour irregularity can reflect native sampling, noise, a poor isophote, or
included dark material. A smoother subpixel contour is justified only with native
intensity/gradient evidence and perturbation stability. Save failures and metrics.

Next: generate native diagnostic profiles/thickness maps; save CP1, then implement
separate tail, reflection and colored brightness methods as specified.
