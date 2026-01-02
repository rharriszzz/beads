"""Lightweight end-to-end pipeline wiring segmentation, sampling, and palette mapping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from PIL import Image

from .palette import nearest_palette_indices
from .sampling import BeadSample, positions_along_centerline, sample_beads
from .segmentation import Centerline, centerline_from_mask, mask_bracelet
from .color_masks import combined_bracelet_mask, color_indices_from_masks


@dataclass
class PipelineResult:
    mask: object  # numpy.ndarray
    centerline: Centerline
    positions: List[tuple]
    samples: List[BeadSample]
    indices: List[int]
    period: Optional[int] = None
    pattern: Optional[List[int]] = None


def infer_palette_indices(
    img: Image.Image,
    palette_colors: Sequence[tuple],
    spacing_px: float,
    radius_px: float,
    brightness_threshold: Optional[int] = None,
    offset_px: float = 0.0,
    min_coverage: float = 0.3,
    use_bead_detection: bool = False,
    color_masks: Optional[dict] = None,
    color_names: Optional[List[str]] = None,
    background_names: Optional[set] = None,
) -> PipelineResult:
    """Run segmentation -> centerline -> sampling -> palette mapping.

    If color_masks/color_names are provided, use those to build the bracelet mask and assign indices
    by mask membership instead of nearest palette colors.
    """
    mask: object
    centerline: Centerline
    if color_masks and color_names:
        bg_names = background_names or set()
        bracelet_mask = combined_bracelet_mask(color_masks, color_names, bg_names)
        mask = bracelet_mask
        centerline = centerline_from_mask(bracelet_mask)
    else:
        mask = mask_bracelet(img, brightness_threshold=brightness_threshold)
        centerline = centerline_from_mask(mask)
    if use_bead_detection:
        from .bead_detect import detect_bead_centers
        from .bead_graph import order_beads_by_mst

        detected = detect_bead_centers(mask, spacing_px=spacing_px)
        ordered = order_beads_by_mst(detected)
        positions = ordered.centers
    else:
        positions = positions_along_centerline(centerline, spacing_px=spacing_px, offset_px=offset_px)

    samples = sample_beads(img, positions, radius=radius_px, mask=mask, use_median=True)
    filtered = [s for s in samples if s.coverage >= min_coverage]
    if filtered:
        if color_masks and color_names:
            indices = color_indices_from_masks(filtered, color_masks, color_names)
        else:
            indices = nearest_palette_indices([s.color for s in filtered], palette_colors)
    else:
        indices = []
    return PipelineResult(mask=mask, centerline=centerline, positions=positions, samples=samples, indices=indices)


def infer_pattern(
    img: Image.Image,
    palette_colors: Sequence[tuple],
    spacing_px: float,
    radius_px: float,
    brightness_threshold: Optional[int] = None,
    offset_px: float = 0.0,
    min_coverage: float = 0.3,
    color_masks: Optional[dict] = None,
    color_names: Optional[List[str]] = None,
    background_names: Optional[set] = None,
) -> PipelineResult:
    """Run full pipeline and estimate pattern periodicity."""
    from . import periodicity  # local import to avoid circular at module import

    base = infer_palette_indices(
        img,
        palette_colors=palette_colors,
        spacing_px=spacing_px,
        radius_px=radius_px,
        brightness_threshold=brightness_threshold,
        offset_px=offset_px,
        min_coverage=min_coverage,
        color_masks=color_masks,
        color_names=color_names,
        background_names=background_names,
    )
    period = periodicity.estimate_period(base.indices, min_period=1)
    pattern = periodicity.extract_pattern(base.indices, period=period)
    base.period = period
    base.pattern = pattern
    return base
