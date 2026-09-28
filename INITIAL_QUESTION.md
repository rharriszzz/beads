# Initial question — bead-rope reconstruction

This reusable brief preserves the conversation's opening request verbatim, then
adds the maker's nonduplicate construction facts and later clarifications.
The original request is historical: its new branch already exists as
`photo-2-reconstruction-v2`, based on `master` (this repository has no `main`).
Read the current handoff before resuming; this document does not restart work.
Algorithm proposals and experiment results belong in [METHODS.md](METHODS.md).

## Opening request

> We are going to work in the "beads" directory, in a new branch off of the main branch.
> Our eventual goal is to extend beads.pov so that it can render a simulation of beads-photo-2.jpg.
> We will want to be able to render the magenta paper the necklace is on
> (however this should be done in a way that does not depend on the color of the background),
> we want to attempt to replicate the lighting,
> we will need a spline that replicates the way the necklace is physically arranged,
> we want to identify the beads color and material (use povray's definition for material),
> we want to identify the helicity of the necklace, and
> we will need to identify the pattern of beads (which hass pattern length of
> somewhere between 200 and 400).
> use povray and python.
> You can use ideas you find in any branch of these repos: beads fft-image-explorer bead_map hsv_tools.
> Use workflow ideas from the photo-2-reconstruction branch of the beads repo;
> these ideas had been developed first fot the navier-stokes-vortex-lab repo read this if you want.
> I want you to focus one aspect of the project at a time, then tell me which aspect,
> as well a presenting options for solving that aspect.  For example, suppose
> that the first thing to do is to distinguish the background from the foreground.
> In this case the background might be a piece of paper, and it includes all of the paper that is visible,
> even if it in the shadow of the necklace.  I want you to come up with 3 to 6 methods of doing
> this, and present it to me, and I will provide more if you are missing some.  I do want you to
> evaluate using a 2d fft, using a gaussian filter of radius 0.05 of the square root of the total number
> of pixels in the image as a starting point.  Interpreting the results is tricky, but it can tell you
> if point is entirely over the background versus entirely over the bracelet.  Also, once
> you know the centerline of the bracelet, this fft can tell you all three spacings (1,6,7) as well
> as the helicity, no mater where you sample along the centerline.  Again figuring out how to do
> this is tricky.  It is ok to not use ffts if it is too hard.
> Next, in order to come up with a good approximation to the lighting.
> There are specular reflections in many of the beads.  You might be able to find clues on how to
> reconstruct the lighting from the web.  Most likely the photo was taken by an iphone.
> Once you have the background and lighting, you may add them into beads.pov, if you
> think that it would be helpfil
> Next we need to determine the locations of some or most or all of the beads.  In general,
> there will be shadows at the edge of each bead, however if two beads are adjacent, one bead
> will be more in front of the other will occlude some or all if the part of the shadow of the
> bead that is behind.  Please try to be relatively color independent; I know that this is
> hard for black beads.  At each phase, please give me you list of possible implementation
> methods, so I can give you advice.  Also come up with questions, if you want.
> I did work on the photo-2-reconstruction branch for quite some time.

## Additional image and analysis constraints

- **Every supplied computed image and actual photograph has the bracelet in the
  middle of the picture, with substantial margins.** This is maker-supplied
  framing knowledge, not a measured margin width or permission to hard-code bead
  coordinates. Use margins to obtain initial background examples. The clear
  width is unspecified; no fixed percentage is established. Interior paper can
  be enclosed by the necklace and need not connect to the image border.
- Aim to identify background under varying illumination, including cast shadows.
  Final code should have little knowledge of this picture's particular colors
  or bead locations. The known palette below describes this necklace; do not use
  it as a required segmentation palette for other inputs.
- The immediate purpose of identifying paper is to fit smooth splines to the
  necklace without including cast shadow in its outline. Pixel-perfect separation
  is not required now; later bead/geometry steps can refine it. Prioritize avoiding
  broad shadow-induced displacement and preserve local uncertainty.
- One proposed background method is to sample every HSV value in a strip around
  a line near an image edge, fit an enclosing region in HSV space, and test other
  pixels for membership. The line should remain on paper. Include ways to handle
  shadowed paper, evaluate the alternatives for spline fitting, and explain the
  recommended combination. This is a method proposal, not a confirmed rule that
  every matching color belongs to paper; see [METHODS.md](METHODS.md).
- Shadowed red beads and shadowed paper definitely overlap in HSV, from the
  maker's earlier deliberately labeled regions. The intended saved map is
  `fft-image-explorer/hsv_mask_triptych.py`, with overlapping `red-and-shadow`
  and `shadow` profiles. Those bounds belong to the white-balanced photo and
  use H/S/V on 0–255. Local hue changes can still give boundary clues. Do not
  transfer those boxes to the original JPEG or treat overlap as proof that hue
  is useless. See [the recovered provenance](photo2/HUE_TRANSITIONS.md).
- The maker reports Gaussian-window FFT works well in `fft-image-explorer` for
  background, especially shadowed paper, and for bead directions. Latest background
  description: use a low-pass filter and measure power. An earlier description
  removed the central peak and inspected remaining power. The saved scanner's
  `hp_removed` is low-frequency retained power divided by total power; this is
  complementary to retained high-frequency fraction with the same cutoff.
  Preserve the exact statistic when reproducing it; see [source notes](photo2/FFT_EXPLORER_NOTES.md).
  For direction analysis, reject both low and high frequencies outside expected
  bead spacings, then find **three pairs of opposite noncentral peaks** representing
  directions 1/6/7. This is prior maker experience, not a newly measured result here.
  The maker proposes that direction 1's angle relative to the local centerline
  determines helicity; demonstrate conventions and validate it before claiming
  recovery. The Gaussian “radius” convention remains unspecified; existing
  experiments explicitly interpret it as spatial sigma.
- Once approximate inner/outer boundaries give a usable centerline, consider
  bead colors and other identifying features, pixel sizes, directions 1/6/7 and
  helicity without requiring a perfect mask first. Sample pixels along the
  centerline and inspect their path through HSV: local dark areas can indicate
  seams (poorly for black beads), and very bright areas can indicate specular
  reflections. Compare nearby paths and other cues rather than treating either
  brightness rule as certain. For directional analysis, center Gaussian 2D FFT
  windows on the curve with width comparable to the local necklace width;
  interpret directions 1/6/7 and compare direction 1 to the centerline for
  helicity. [Six bead-analysis methods](METHODS.md#bead-analysis-given-approximate-boundaries-and-a-centerline)
  include these maker proposals and alternatives. This assumes a centerline for
  planning; it does not assert one has been recovered in the current work.
- FFTs should be explored for both background/shadow separation and local bead
  directions/spacings/helicity, but their use in the final solution is optional.
  The next assignment objective is a `bead_index` (in the full-string sense of
  `beads.pov`) and a color for every clearly visible bead. Select methods for
  that task; do not replace string indices with consecutive visible-region labels.
  See [index and color methods](METHODS.md#assign-bead_index-and-color-to-clearly-visible-beads).
- If a boundary is locally ambiguous, go farther in either direction **along the
  necklace** until reliable boundary evidence appears. Bridge the uncertain
  span using a smooth larger-scale envelope. Individual bead geometry still
  makes smaller curves. Show measured/supportable sections separately from
  inferred bridges. Earlier edge corrections produced false indents and bumps;
  review raw images beside candidate boundaries before propagating them.
- A later maker answer confirms an iPhone photo but leaves flash use unknown.
  Highlights are lighting reflections, not bead centers or boundary landmarks.
  Surface shading, neighboring-bead occlusion and cast shadow must be distinguished.
- Keep focused questions, answers and useful supporting illustrations in tracked
  Markdown/files. Explain raw context, proposed interior endpoints and why they
  were chosen, then the sampling route and what changes along it. The assistant
  can choose provisional points; the maker need not click every bead.

## Physical construction and appearance — maker's saved information

### Crochet, closure and placement

I designed and made the necklace in photo 2. The beads are pre-strung in sequence,
a slipknot is added, and the rope is crocheted with one bead per chain stitch.
The first three rows require dexterity. Every stitch is the same: I do not need
to manage alternating rounds. The extra half-step of advance is built into the
way a stitch attaches to the preceding row. Extra twist is small, only as much
as needed to join the ends; no numerical twist bound has been supplied.

Photo 2 settled into its position naturally; I did not arrange its sections to
show chosen colors. The necklace lies flat on paper on a table. Keep the major
centerline planar, with a single global camera/plane relationship; individual
beads and their placement around the rope remain three-dimensional.

I use an integer number of complete pattern repeats: total beads `N = kL` for
integer repeat count `k` and repeat length `L`. Typical totals are 700–800 for a
bracelet and 3,000–5,000 for a necklace, not exact counts for this photo. An older
2,698-bead model estimate was accepted as adequate for that work; it is not an
exact count or a divisibility constraint for current recovery.

### Bead geometry and the neighbor directions

The beads have the same size and shape across colors, with small differences in
gloss. Their surfaces are smoothly rounded. A bead is torus-like; use the actual
rounded hollow bead geometry and proportions in `beads.pov`, as authorized, rather
than replacing every exposed shape with an oval. The holes point along the local
length of the necklace and are never visible. The thread is white and never
visible. Usually a bead has one bright patch, depending on lighting; this is not
an exactly-one-highlight rule. There is almost no tilting or sliding between beads.

Immediate neighbors follow three index-difference families: **±1, ±6, ±7**.
Direction 1 progresses around the rope's small circumference; 6 and 7 follow the
diagonals. Helicity changes their orientation. The maker describes top beads as
visibly rectangular, direction 1 as bringing their shorter lengths close, and
6/7 as brick-like arrangements with short edges together and successive layers
halfway offset. Treat these as qualitative contact cues, not fixed image axes.
The maker reports unseen beads at the edges of a visible patch, rather than
between its visible neighbors. Detection failures remain possible.

**Source-model detail, not a separately measured physical count:** `beads.pov`
uses nominal 6.5 beads per turn; `nrows = floor(0.5 + N/6.5)` and
`exact_beads_per_row = N/nrows` close the model with a small distributed adjustment.
Geometric turns do not mean alternating maker-controlled stitch types. The
source places the hole axis along the rope tangent. Keep minor-circle progression
(helicity) separate from the section's direction relative to the camera, which
changes the visible shape and neighbor occlusion around the major loop.

### Pattern, observations and conventions

Photo 2 uses red, yellow and black beads. I check each pattern sequence against
the previous one, so error-free repeating construction is the working assumption.
Image readings and index assignments can still be wrong. Record insufficiently
visible bead colors as **unknown**, preserving missing indices; unknown is not a
fourth material and must not be silently filled with an inferred color. Ignore
slivers as active bead observations, without absorbing their pixels into neighbors.

The target is the **shortest repeating block**, with no required designated first
bead, stringing direction or output handedness convention. Choose and document
consistent conventions while still testing the helicity that explains the image.
This is my longest design; I confirmed it is less than 400, consistent with the
opening estimate of roughly 200–400. It was designed on custom graph paper with
continuous black/yellow/red spirals. My later recollection was roughly rectangular
paths, probably using ±6/±7; the exact continuity rule and path lengths are unknown.
R112 strengthens the earlier recollection: **this necklace's repeat length is
not a multiple of 13**. Apply that exclusion to photo 2; keep the general solver
configurable and retain multiples of 13 as synthetic tests. It does not imply
that the total bead count is indivisible by 13.
Reminder from the earlier discussion: at 6.5 beads per turn, 13 beads span two
full turns, so a multiple-of-13 repeat returns each color slot to the same
cross-section position and can keep that slot hidden across repeat occurrences.
See the [historical visibility check](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/VISIBILITY.md);
actual coverage also depends on viewing geometry, and excluding such repeats
does not by itself guarantee that every slot is readable.

Once every bead has a complete, consistent full-string index, the total count
is known. Find the smallest color repeat matching all clearly visible indexed
beads, using whole-repeat closure. Visible-only indexing still needs verified
closure across hidden regions to establish that count. Preserve unresolved colors
and unobserved pattern slots. Then fit the paper, individual bead colors and
lighting in POV-Ray; compare methods before implementation. See the
[repeat methods](METHODS.md#shortest-color-pattern-from-indexed-observations) and
[appearance methods](METHODS.md#fit-paper-bead-materials-and-lighting-in-pov-ray).

Invented patterns are authorized for tests. One supplied simpler example is the
concatenated 30-bead sequence `123333 112333 111233 111123 111112`, with freely
chosen colors. It is a test pattern, **not** the photo-2 answer. Known synthetic
patterns and renderer IDs are evaluator truth, not image-analysis inputs.
A render colored by sampling the photograph is not recovered bead order or a
recovered repeating pattern. Do not infer physical bead composition: “material”
means POV-Ray pigment, finish, normal and interior properties.

## Sources and deduplication

The opening is copied exactly from [R092 in the request log](REQUEST_LOG.md).
Later facts above are consolidated once by topic, rather than repeating every
historical plan/handoff entry. They are paraphrases of saved maker answers except
where explicitly labeled as source-model details. Historical algorithm proposals,
provisional masks and counts are not promoted to maker-confirmed measurements.
Current Python requirement is 3.12; older setup versions and obsolete task gates
are not part of this reusable brief.

Historical construction sources are pinned at commit
`2c4c116bf7f7b9e8c773358a97740dcd77879a8a`:

| Information | Source |
| --- | --- |
| Pre-stringing, slipknot, one bead/stitch, small closure twist; source proportions | [PLAN.md, R016](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/PLAN.md#r016-construction-constraints-and-source-authority), request R016 |
| Identical stitches/half-step, natural placement, whole repeats/count caveat | [Request log](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/REQUEST_LOG.md), R019/R021/R022 |
| Palette, checked repeats, unknown colors, neighbors, free conventions, example | Same log, R025/R028/R030/R033/R035 |
| Rectangular cues, corrected spiral recollection, holes, thread, gloss/highlights | Same log, R038/R042/R049–R051/R054; flash unknown in R057 |
| Ignore slivers; planar centerline, exposed shapes and camera view | Same log, R069/R086; [SHAPE_REASONING.md](https://github.com/rharriszzz/beads/blob/2c4c116bf7f7b9e8c773358a97740dcd77879a8a/photo2/SHAPE_REASONING.md) |
| Color independence, FFT advice, HSV evidence, smooth bridging, margins, spline purpose, centerline cues and index/color objective | [Current request log](REQUEST_LOG.md), R092–R111 |

### Branch-history review for this consolidation

Reviewed all seven distinct published branch names after fetching on 2026-09-28;
local/remote counterparts agree. All share root `c100ac8`. Branch creation is not
recorded by Git, so “first” below means the earliest reachable addition relative
to the listed parent, not an inferred creation date. Read the root's HTML and
instructions; it has no Markdown. Reviewed earliest plans and relevant later
construction entries, not every implementation commit.

| Branch / reviewed tip | Earliest relevant addition | What was retained |
| --- | --- | --- |
| master / `020303e` | `c100ac8` initial files; then photo additions | Forward scene and image collection; no construction Markdown |
| pattern / `8467264` | `d91bbab` code after master; first Markdown `1580239:patterm.md`, renamed in `2eaf8d3` | Historical segmentation/repeat ideas; no new maker construction facts |
| image-to-pattern / `26ba79a` | `42358e3:image-to-pattern/plan.md` after master | Helical order/forward-format context; discard assumptions that crop/color quantization recovers order |
| image-to-pattern-2 / `402663e` | `402663e` replaces the inherited plan after image-to-pattern | Synthetic validation and shadow-failure lessons; old workflow is not a new instruction |
| archive/image-to-pattern-2-wip / `debec40` | `debec40` after `402663e` | Archive adds six code/data/render files, no new Markdown or maker facts; nothing restored |
| photo-2-reconstruction / `2c4c116` | `63ba75c` after `402663e`; later R016 onward | Construction and corrections above; repeated plan/log/handoff prose merged |
| photo-2-reconstruction-v2 / `d60274f` at review start | `eae80ce` after master | Exact opening request and subsequent FFT/color/boundary clarifications |

To reproduce the historical reads without changing branches:

```bash
git show 1580239:patterm.md
git show 42358e3:image-to-pattern/plan.md
git show 402663e:image-to-pattern/plan.md
git show 63ba75c:REQUEST_LOG.md
git show 2c4c116:PLAN.md
git show 2c4c116:REQUEST_LOG.md
git show 2c4c116:photo2/SHAPE_REASONING.md
git log --reverse --oneline refs/heads/photo-2-reconstruction ^refs/heads/image-to-pattern-2 --
```
