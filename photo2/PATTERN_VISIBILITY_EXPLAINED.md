# How a repeating bead pattern can reveal—or conceal—its hidden side

A repeat divisible by thirteen can keep the same positions hidden in every copy,
but it does not make the pattern impossible to recover. Recovery is possible
when different views or occurrences reveal the needed positions and we can match
those positions correctly. A repeat not divisible by thirteen helps by moving
successive copies to different angular phases.

*Draft 2 for discussion: short explanation first, then the full argument, a
middle-sized example and the complete target candidate. The examples are
mathematical constructions; the proposed illustrations will be rendered in POV-Ray after the explanation
and examples have been reviewed. PDF production comes at the end of that process.*

Knowing a pattern lets us predict hidden beads. Recovering an unknown pattern
from a photograph asks a different question: **does the visible evidence determine
what is hidden?** A regular-looking front can coexist with a very different,
perfectly regular back. Repetition helps only when it supplies information we
did not already have.

## 1. An adversary hides a different pattern on the back

Imagine a straight crocheted tube, held without twist and viewed from one side.
Use the ideal construction of 6.5 beads per turn. Thirteen successive beads make
two turns, after which the circumferential arrangement repeats.

An adversary chooses this 26-bead color word. `R` means red, `B` black and `Y` yellow.
The space separates two 13-bead groups; it is not a gap in the necklace.

```text
RRRBBRRRRBBRR RRRYYRRRRYYRR
```

All reliably visible front beads are red. Deep on the back, the first group has
black beads and the second has yellow beads. This repeats: a plain red front,
with a black/yellow arrangement on the hidden side. Someone given the complete
word can predict every hidden color. The front alone does not establish that word.

For example, consider a second 26-bead word:

```text
RRRBYRRRRBBRR RRRYBRRRRYYRR
```

It rearranges black and yellow on the back while keeping the visible front red.
Both words have shortest period 26 and the same totals: eighteen red, four black
and four yellow. They are genuinely different even if we change the starting
point or reverse the reading direction. The second contains adjacent black/yellow
pairs in string order; the first has none. Even knowing the color totals would
not decide between them.

The same front would even fit an all-red pattern of length one. If we already
know the repeat length is 26, the two different 26-bead explanations still remain.
A perfect match to the visible colors does not settle the hidden pattern.

In our stated observation model, **the visible measurements are identical**.
An algorithm cannot decide between these words from those measurements. Greater
confidence, better optimization or more copies of the same fixed-facing view
cannot supply the missing information. Additional views, a chart or a justified
construction rule could distinguish them.

### What “visible” means in this example

We deliberately use clear front-facing positions and skip the edges. This is a
simple measurement model, not an already verified simulation of glass optics.
Number circumferential phases by `r=k mod 13`, where k is the string index. In the
ideal helix their angles are `4πr/13`, measured from the front.

- Reliably read phases: `0, 1, 6, 7, 12`, within 60° of the front.
- Changed rear phases: `3, 4, 9, 10`, more than 135° from the front.
- All other phases keep red; their evidence is not needed.

In each 13-bead group, the adversary changes only the four deep-rear phases.
The read phases are red in both words. The model reveals ten positions per
26-bead repeat and leaves sixteen unread, regardless of how many copies we see.

A physical POV-Ray version must check that the changed rear surfaces contribute
no visible color information to the chosen front view. Classifying a bead center
as rear-facing is not by itself that check: some bead surfaces can protrude,
show through gaps or transmit light. That is a requirement for the eventual
figure, rather than an assumption to conceal in the rendering.

## 2. Why a repeat not divisible by thirteen can be easier

Now append one red bead to the first word, making a 27-bead repeat:

```text
RRRBBRRRRBBRR RRRYYRRRRYYRR R
```

This still has a deterministic hidden color sequence. What changes is where
each copy sits around the tube.

A 26-bead repeat advances by four complete turns. Every copy puts each pattern
position at the same angle, so a hidden position stays hidden. A 27-bead repeat
advances one bead farther. Each new copy puts the same pattern position in the
next phase class. In physical angle this is about 55.4°, not one whole turn.

Follow position 3, one of the first word's black beads. Positions are zero-based:

| Copy of the 27-bead pattern | Circumferential phase | Evidence in our model |
|---:|---:|---|
| 0 | 3 | Deep rear; unread |
| 1 | 4 | Deep rear; unread |
| 2 | 5 | Near the edge; deliberately skipped |
| 3 | 6 | Clear front; read as black |

That black bead's corresponding position has now become observable. No inference
from a dark edge was necessary. Other pattern positions likewise move through
the available angles.

More generally, position p in copy j has phase:

```text
r = (p + jL) mod 13
```

If 13 divides L, the phase is constant as j changes. Otherwise, because 13 is
prime, successive copies visit all thirteen phase classes. With enough copies
visible, every pattern position reaches a readable phase. Thirteen copies are
a sufficient full cycle in this ideal model, although fewer can suffice.

| Same front-view rule, thirteen copies | Distinct pattern positions read | Colors seen |
|---|---:|---|
| Repeating 26-bead word | 10 of 26 | Red only |
| Repeating 27-bead word | 27 of 27 | Red, black and yellow |

This example isolates **color coverage**. It assumes the repeat length and the
correspondence between copies are known. Discovering those correspondences from
similar-looking beads is an additional problem. A short or occluded sample may
also contain too few copies, and actual twist or deformation changes the simple
phase calculation. Being nondivisible by 13 helps; it is not a general guarantee
that one photograph determines the pattern.

## 3. What changes when the tube bends or twists?

A repeat divisible by 13 stays aligned relative to the construction. It need
not stay on the same side relative to the camera. Twist can turn its back toward
us; changes in the tube's direction can change the surface facing the camera.
An additional view can do the same thing.

The useful question is therefore not just “does the repeat divide by thirteen?”
It is **“do different occurrences provide complementary views of its positions?”**
A hidden position in one occurrence can be directly observed in another. We
then combine those observations using their pattern addresses.

Bending alone does not guarantee this. A curve, its material-frame orientation,
occlusion and camera direction must actually expose the missing positions. The
figures should demonstrate a specific mechanism rather than imply that every
loop automatically reveals its entire circumference.

## 4. A middle-sized example: fifty-two beads, fully recoverable

Consider this 52-bead pattern, shown as four groups of thirteen:

```text
RRRRYYYYBBBBR
YYYYBBBBRRRRY
BBBBRRRRYYYYB
RYBRYBRYBRYBR
```

Its shortest period really is 52: it is not a 13- or 26-bead word written several
times. It has enough longitudinal variation to distinguish the groups while
remaining small enough to inspect every position.

Hold the tube's orientation fixed and use the same clear-front rule as before.
From the first viewing direction, we read 20 of its 52 positions. Because 52 is a
multiple of 13, simply observing more identically facing repetitions never fills
the gaps.

Now examine it from three directions around the tube: 0°,120° and 240°. Keep a
reference position and reading direction so the observations can be aligned.
In our ideal color-reading model, the three views give:

| View direction | Readable phase classes | Pattern positions read |
|---:|---|---:|
| 0° | 0, 1, 6, 7, 12 | 20 of 52 |
| 120° | 2, 3, 8, 9 | 16 of 52 |
| 240° | 4, 5, 10, 11 | 16 of 52 |
| Combined | All thirteen classes | **52 of 52** |

Each gap is filled by a direct reading in another view. We need no rule guessing
the back's colors from the front. These could be three photographs of one part
of a tube, or three correctly matched occurrences facing complementary directions
in one photograph. Actual optical visibility will need checking in the POV-Ray
version, as with the first example.

This illustrates **many** decodable patterns rather than a lucky choice of colors.
The coverage argument does not depend on any of the 52 color choices: changing
them leaves every position observable in at least one view. The same construction
works for any length 13m under this phase model, provided the views and position
correspondences are available. Some words will have a shorter true period; the
specific word above is checked to have shortest period 52.

The example also identifies what is doing the work. With one fixed-facing view,
the color word is underdetermined. Complementary observations establish it.
Being divisible by thirteen has neither changed the color information in a
measurement nor prevented different measurements from completing the pattern.

## 5. The full 208-bead target of this branch

The proposed length 208 is 16 times 13. It therefore has the alignment that could
defeat the straight-tube example. Divisibility did not become mathematically
irrelevant; the fixed-facing visibility restriction turned out not to describe
our retained evidence.

The reconstruction assigns reliable-enough color observations from different
parts of the photograph to positions in a common proposed repeat. **Every one
of its 208 positions has observational evidence.** One occurrence can be missing
a position while another supplies it. The proposed lattice and neighbor directions
provide the correspondence needed to combine them.

This is an evidence statement under the current indexing, not proof of a detailed
physical visibility mechanism. We have not independently established exactly
which bend, twist or bead pose exposed each body. A generic illustration can
explain complementary coverage; it must not be presented as a measured explanation
of every bead in the photograph.

The present record is:

- 1040 retained color observations agree with the 208-bead candidate.
- All 208 positions are observed; 201 satisfy the historical strict support rule.
- Seven positions are provisionally black and lack that level of corroboration.
- The unreadable Q1 pigment is withheld; it contributes no confirming color.
- Two former red interpretations were corrected to yellow from maker inspection
  of the original photograph.

The hidden side of every occurrence has therefore not been guessed from a plain
front. Instead, the saved mapping combines partial observations of the proposed
repeat. The diagram that most directly explains this should show **which repeat
positions are actually observed in which occurrences**.

The pattern is also richer than thirteen angular colors. A 208-bead word contains
sixteen positions in each phase class, and their colors can vary along the tube.
The best 13-bead word fits only 43.37% of the retained observations; the best 104-bead
word fits 91.73%; 208 fits all of them. This is compatibility with the retained
labels, not independent proof of the physical pattern or indexing.

### The complete candidate, with its uncertainty visible

The table below contains all 208 positions of the branch's current candidate.
`R` means red, `Y` yellow and `B` black. In the complete-candidate column,
lowercase `b` marks the seven black assignments that lack strict corroboration.
The strict-evidence column leaves those same positions as `?`; every other entry
has the current R347 support status. The uppercase stored candidate remains
unchanged.

Positions are zero-based in the current A indexing, relative to C-1302-0316.
The chosen origin and reading direction are conventions, not a recovered physical
start of the necklace. The full working necklace realization uses thirteen copies
of this block, giving 2704 beads under the conditional closure interpretation.
Each line groups thirteen string positions for readability;
it spans two turns, rather than a single row of thirteen beads. The eventual
crochet chart will use alternating six/seven-bead rows.

<!-- BEGIN_CURRENT_208_TABLE -->
| String positions | Strict evidence | Complete candidate (`b` tentative) |
|---|---|---|
| 0–12 | `YBYYBYBYBYBYR` | `YBYYBYBYBYBYR` |
| 13–25 | `BYBBYRRBYBYRB` | `BYBBYRRBYBYRB` |
| 26–38 | `RBYYRBBRBYRBR` | `RBYYRBBRBYRBR` |
| 39–51 | `BRBR?RBRBRRBR` | `BRBRbRBRBRRBR` |
| 52–64 | `RBRYRBRBRYYRB` | `RBRYRBRBRYYRB` |
| 65–77 | `BRYBYRBRYB?YR` | `BRYBYRBRYBbYR` |
| 78–90 | `RYBY?YRYBYY?Y` | `RYBYbYRYBYYbY` |
| 91–103 | `YBYBYBYBYBYBY` | `YBYBYBYBYBYBY` |
| 104–116 | `RBYBBYRRBYBYR` | `RBYBBYRRBYBYR` |
| 117–129 | `BRBYYRBBRBYRB` | `BRBYYRBBRBYRB` |
| 130–142 | `RBRBRBRRBR?RB` | `RBRBRBRRBRbRB` |
| 143–155 | `BRBR?RBRBRRBR` | `BRBRbRBRBRRBR` |
| 156–168 | `RBRYRBRBRYYRB` | `RBRYRBRBRYYRB` |
| 169–181 | `BRYBYRBRYBBYR` | `BRYBYRBRYBBYR` |
| 182–194 | `RYBY?YRYBYYBY` | `RYBYbYRYBYYBY` |
| 195–207 | `YBYBYBYBYBBYB` | `YBYBYBYBYBBYB` |
<!-- END_CURRENT_208_TABLE -->

The tentative black positions are 43, 75, 82, 89, 140, 147 and 186. They all have
observations; the shortage is corroboration, not complete invisibility. In this
presentation, the 201 supported positions contain 62 red,62 yellow and 77 black;
the complete candidate contains 62 red,62 yellow and 84 black.

The colors come from the saved [208-position candidate](r344/pattern208.json).
The support distinction comes from the later [R347 assessment](r347/answers/assessment.json),
not the older R344 strict table. The original pattern chart has not yet supplied
independent confirmation that this is the exact intended word.

## 6. Proposed POV-Ray figures

These are illustration specifications, not completed figures. The example words,
phase conventions, view and legend should remain consistent across panels.

### Figure A: identical visible evidence, different hidden patterns

Render the two 26-bead adversarial words with identical geometry, camera and
lighting. Show their front views side by side, then rear views revealing the
different black/yellow patterns. A small string-order key connects color words
to numbered beads. Initially use opaque matte beads so transparency does not
undermine the visibility example. Include an orientation marker outside the tube.

Before claiming front-view indistinguishability, verify both actual visible
surface ownership and the effect of changing the hidden pigments. Use guard
beads at the ends so rear colors are not exposed through an artificial cut.
If the proposed rear positions leak visible information, revise the illustrative
geometry or hidden set and update the mathematical example together.

### Figure B: a single added bead moves the hidden pattern into view

Show enough repeats of the 26- and 27-bead words to reveal their different alignment.
Track one selected pattern position through successive copies with an external
marker or annotation, keeping its pigment unchanged. The 27 example should show
the position clearly arriving at the front; the near-edge occurrence remains
unread. Use the same camera, lighting, bead dimensions and readable labels.
Perspective and reflections should support the explanation, not obscure it.

### Figure C: a 52-bead repeat assembled from complementary views

Render the middle-sized pattern at the three specified viewing directions, with
the same reference bead, index convention and clear-front rule. Under each view,
show only the color readings that view genuinely supports. A combined indexed
strip shows where all 52 entries come from; its cells should link visibly to
their source view. The reader should be able to follow a hidden position into
a readable view without trusting a complicated geometric argument.

### Figure D: the full target and its actual observation coverage

Use the saved photograph-to-index assignments to make an occurrence-by-position
coverage diagram. Observed cells carry their recorded colors; unobserved cells
remain empty. Distinguish the seven undercorroborated positions and the maker
corrections in a compact legend. A summary strip shows the union of observations
covering all 208 positions. Repeated display copies and the withheld Q1 do not
add evidence. This diagram can use an orthographic POV-Ray scene for clear,
consistent presentation without pretending it is a new physical reconstruction.

Alongside the coverage, show the complete 208-bead candidate on alternating 6/7
crochet graph paper, with row/string indices, repeat boundaries and the seven
tentative blacks marked. If side extensions are included, identify them as
same-index copies. Pair a whole-necklace overview with a readable repeat detail
so the target is recognizable and every displayed color can be traced to the
table above. The observed coverage and the candidate's completion must remain
visually distinct.

If we add a curved-tube explanatory rendering, label it an illustration of a
possible exposure mechanism. The coverage diagram is the direct evidence for
the saved mapping; an attractive render is not a substitute for it.

## Sources and limits for this draft

The 26/27 comparison and 52-bead example are deliberately constructed examples,
not alternative fits to the necklace or claims about its physical bead count. Their arithmetic
is checked in [visibility-example checks](retrospective/visibility-example-checks.json)
by [a small independent-enumeration script](retrospective/visibility_examples.py).

The actual necklace discussion uses the [R347 assessment](r347/answers/ASSESSMENT.md),
[period scan](retrospective/PATTERN_LENGTH_MATCH.md) and
[crochet lattice conventions](GRAPH_PAPER_6_5_BEADS.md).
Exact physical topology, count, geometry and the authentic original chart remain
independently unverified. This draft introduces no new observations or adopted
pattern changes. Subsequent rounds can refine the narrative and the examples
before committing to the final figure layout and PDF.
