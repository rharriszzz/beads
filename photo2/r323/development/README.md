# R323 prevalidation development archive

- `first-tracker.py`: first implementation. The initial run completed inference
  but failed JSON serialization because a NumPy integer was not serializable.
  No R161 evaluation had run. A serialization adapter fixed this.
- `first-complete/`: single strongest reciprocal triangle,60px window stride.
  104 observations;71 indexed,62 interior heuristic confidence;107 links,
  104 unresolved links,8 components. Original review and source retained.
- `multispectral/`: up to10 distinct reciprocal spectral bases,40px stride.
  98 indexed observations,82 interior,192 links,17 unresolved,one component.
  The final primary adds separate timing/provenance/representative-location
  fields; scientific topology is unchanged. No R161 scores selected refinements.

These old development HTML pages link to final report/validation paths relative
to their original experimental destinations and are not the delivery viewer.
Use `../../results/index.html` from this directory's child archives, or the
repository's `photo2/r323/results/index.html`. Their original links are preserved
as historical outputs; the final delivery viewer has independently checked links.

The subsequent fixed-candidate local-winner ablation is in results/controls.json.
All maker-labeled diagnosis is post-freeze and separate from the detector.
