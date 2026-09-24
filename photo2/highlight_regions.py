"""Conservative image-only repair of enclosed bright gaps in observed regions.

No bead templates, clicks, indices or evaluator truth are accepted. Existing
labels stay fixed; an ambiguous cavity remains unassigned.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgb2hsv

# Same bright/low-saturation cutoff as the R045 foreground exclusion.
# Frozen before R055 truth scoring. Eight-connectivity preserves diagonal exits.
PARAMETERS = dict(max_saturation=.20, min_value=.75, connectivity=8,
                  require_single_owner=True, require_all_pixels_bright=True)


def fill_highlights(rgb, labels):
    rgb, labels = np.asarray(rgb), np.asarray(labels)
    if (rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3
            or labels.shape != rgb.shape[:2] or labels.dtype.kind not in 'iu'
            or np.any(labels < 0)):
        raise ValueError('Expected uint8 RGB and matching nonnegative integer labels')
    neighbors = np.ones((3, 3), bool)
    foreground = labels > 0
    holes = ndi.binary_fill_holes(foreground, structure=neighbors) & ~foreground
    cavities, count = ndi.label(holes, structure=neighbors)
    hsv = rgb2hsv(rgb)
    bright = ((hsv[..., 1] < PARAMETERS['max_saturation']) &
              (hsv[..., 2] >= PARAMETERS['min_value']))
    output = labels.copy()
    records = []
    for cavity in range(1, count+1):
        mask = cavities == cavity
        boundary = ndi.binary_dilation(mask, structure=neighbors) & ~mask
        owners = np.unique(labels[boundary])
        owners = owners[owners > 0]
        all_bright = bool(bright[mask].all())
        accept = len(owners) == 1 and all_bright
        if accept:
            output[mask] = owners[0]
        yy, xx = np.nonzero(mask)
        records.append(dict(cavity=cavity, pixels=int(mask.sum()),
            bbox_xyxy=[int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)],
            adjacent_labels=owners.tolist(), all_bright=all_bright, filled=accept,
            assigned_label=int(owners[0]) if accept else None))
    return output, dict(parameters=PARAMETERS, cavities=records,
        enclosed_pixels=int(holes.sum()), added_pixels=int(np.count_nonzero(output != labels)),
        filled_cavities=sum(r['filled'] for r in records),
        preserved_existing_labels=bool(np.array_equal(output[foreground], labels[foreground])))
