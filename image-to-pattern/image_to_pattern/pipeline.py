"""Lightweight end-to-end pipeline wiring segmentation, sampling, and palette mapping."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from PIL import Image

from .palette import nearest_palette_indices
from .sampling import BeadSample, positions_along_centerline, sample_beads
from .segmentation import Centerline, centerline_from_mask, mask_bracelet


@dataclass
class PipelineResult:
    mask: object  # numpy.ndarray
    centerline: Centerline
    positions: List[tuple]
    samples: List[BeadSample]
    indices: List[int]


def infer_palette_indices(
    img: Image.Image,
    palette_colors: Sequence[tuple],
    spacing_px: float,
    radius_px: float,
    brightness_threshold: int = 230,
    offset_px: float = 0.0,
) -> PipelineResult:
    """Run segmentation -> centerline -> sampling -> palette mapping."""
    mask = mask_bracelet(img, brightness_threshold=brightness_threshold)
    centerline = centerline_from_mask(mask)
    positions = positions_along_centerline(centerline, spacing_px=spacing_px, offset_px=offset_px)
    samples = sample_beads(img, positions, radius=radius_px)
    indices = nearest_palette_indices([s.color for s in samples], palette_colors)
    return PipelineResult(mask=mask, centerline=centerline, positions=positions, samples=samples, indices=indices)
