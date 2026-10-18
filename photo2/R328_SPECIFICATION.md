# R328 — grow one photographic component around the circuit

The user requests a simpler algorithm that starts with one component and grows it
around the entire loop. This supersedes historical stop instructions and R327's
hard two-window admission rule. Preserve R327 and all earlier sources/results.

Reuse R327's original-photo observation and local candidate bank as cached image
analysis, including target-excluded native response, colored-anchor black evidence,
sequence support, and shared colored-pigment geometry. Do not reuse its selected
states, graph components, winding, maker labels, count, or global solver choices
as inference inputs. No new bead observations or 3D fitting in this experiment.

Start at one measured support in window zero. Sweep the geographic windows once,
attaching only connected candidate patches that share observations with the grown
component and agree on those observations' lattice coordinates. Retain a bounded
beam of alternative growth histories so an earlier choice can be reversed. A
window may contribute no patch; the next patch must still attach to the SAME grown
component. Never start another component or add an artificial bridging edge.
Every working edge must be a primitive neighbor in a chosen local image hypothesis,
pass the existing foreground test, and have no observed potential intervening bead.
Single-window support is provisional evidence, not grounds for automatic exclusion.

Use a single additive local photographic score, without cyclic DP, max-marginal
regrets, binary compatibility optimization, or a separate edge synchronization
optimizer. Keep shared-assignment consistency in the growing state. Preserve
connected subpatch selection explicitly: a chosen subpatch does not assert all
assignments in its parent hypothesis. Missing support/model conflict is not called
contradictory image evidence. Alternatives and every attach/skip decision are saved.

Unwrap geographic station across the start. A return must recover the SAME observed
starting supports with one common integer translation; this determines a conditional
winding, rather than imposing one. One connected component without a return witness
is incomplete. Export a replayable connected-growth trace, native-photo review,
frontier failures, alternatives and separate independent historical reference.

Allow at most 600 cumulative seconds of search, checking between stages, plus
separately timed preprocessing, validation and review. Begin with beam 32; broaden
and inspect changing choices while budget remains. Explicitly report pruning and
any failure to get around. No convergence, accuracy, or full physical reconstruction
claim from connectivity alone. Historical reference evaluation is retrospective,
performed after selecting and sealing the working result; it cannot tune inference.
