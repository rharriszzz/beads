"""Beauty-image instance baselines. No layout, instance truth or indices accepted."""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from skimage.color import rgb2gray, rgb2hsv
from skimage.feature import peak_local_max
from skimage.filters import sobel
from skimage.morphology import disk
from skimage.segmentation import watershed


# Fixed before R045 scored runs. All spatial values are for a 2400-pixel image.
PARAMETERS = dict(saturation=0.20, dark_value=0.75, black_value=0.35,
                  hue_radius=0.10, close_radius=2, min_area=12,
                  seed_spacing=12, seed_depth=2.5, gray_edge=0.025,
                  smooth_sigma=0.8, color_fraction=0.60)
METHODS = ('color_components', 'color_distance', 'gray_boundary', 'hybrid_boundary')
PALETTES = {'rgb': ('red', 'green', 'blue'), 'ryb': ('red', 'yellow', 'black'),
            'gray': ('gray',), 'black': ('black',)}
HUES = {'red': 0., 'yellow': 1/6, 'green': 1/3, 'blue': 2/3}


def color_classes(rgb, palette):
    """0 means no confident color, not background and never inferred black."""
    hsv = rgb2hsv(np.asarray(rgb, dtype=np.float32)/255.)
    h, s, v = np.moveaxis(hsv, -1, 0)
    classes = np.zeros(h.shape, np.uint8)
    for i, name in enumerate(palette, 1):
        if name in HUES:
            delta = np.abs(h-HUES[name])
            mask = ((np.minimum(delta, 1-delta) <= PARAMETERS['hue_radius']) &
                    (s >= PARAMETERS['saturation']) & (v >= PARAMETERS['black_value']))
        elif name == 'black':
            mask = v < PARAMETERS['black_value']
        elif name == 'gray':
            mask = (s < PARAMETERS['saturation']) & (v < PARAMETERS['dark_value'])
        else:
            raise ValueError(f'Unknown palette color: {name}')
        classes[mask] = i
    return classes, hsv


def keep_components(mask, min_area):
    labels, _ = ndi.label(mask)
    sizes = np.bincount(labels.ravel())
    keep = sizes >= min_area
    keep[0] = False
    return keep[labels]


def compact(labels, min_area):
    sizes = np.bincount(labels.ravel())
    keep = sizes >= min_area
    keep[0] = False
    table = np.zeros(len(sizes), np.int32)
    table[keep] = np.arange(1, np.count_nonzero(keep)+1)
    return table[labels]


def markers_from_distance(mask, spacing, depth):
    distance = ndi.distance_transform_edt(mask)
    peaks = peak_local_max(distance, min_distance=spacing, threshold_abs=depth,
                           exclude_border=False, labels=mask.astype(np.uint8))
    markers = np.zeros(mask.shape, np.int32)
    if len(peaks):
        # Sorting makes marker naming independent of peak_local_max's order.
        peaks = peaks[np.lexsort((peaks[:, 1], peaks[:, 0]))]
        markers[tuple(peaks.T)] = np.arange(1, len(peaks)+1)
    return markers, distance


def detect(rgb, method, palette_name='rgb'):
    """Return visible-region masks and colors; marker points are not body centers.

    Foreground assumes the legacy white floor. It intentionally includes some
    shadows; this assumption is unsuitable for the magenta photo background.
    """
    rgb = np.asarray(rgb)
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError('Expected an H x W x 3 uint8 beauty image')
    if method not in METHODS or palette_name not in PALETTES:
        raise ValueError('Unknown method or palette')
    palette = PALETTES[palette_name]
    scale = rgb.shape[1]/2400
    area = max(1, round(PARAMETERS['min_area']*scale**2))
    spacing = max(1, round(PARAMETERS['seed_spacing']*scale))
    depth = PARAMETERS['seed_depth']*scale
    radius = max(1, round(PARAMETERS['close_radius']*scale))
    classes, hsv = color_classes(rgb, palette)
    raw_foreground = ((hsv[..., 1] >= PARAMETERS['saturation']) |
                      (hsv[..., 2] < PARAMETERS['dark_value']))
    foreground = keep_components(ndi.binary_closing(raw_foreground, structure=disk(radius)), area)
    labels = np.zeros(rgb.shape[:2], np.int32)
    marker_count = 0
    if method in ('color_components', 'color_distance', 'hybrid_boundary'):
        # Each confident color is segmented independently. Unknown highlights
        # remain unassigned in the first two methods, filled by boundaries in hybrid.
        for i in range(1, len(palette)+1):
            mask = foreground & (classes == i)
            if method == 'color_components':
                part, _ = ndi.label(mask)
            else:
                markers, distance = markers_from_distance(mask, spacing, depth)
                marker_count += int(markers.max())
                if method == 'color_distance':
                    part = watershed(-distance, markers, mask=mask)
                else:
                    part = markers
            selected = part > 0
            labels[selected] = part[selected]+int(labels.max())
        if method == 'hybrid_boundary':
            smooth = ndi.gaussian_filter(rgb.astype(np.float32)/255.,
                                         sigma=(PARAMETERS['smooth_sigma']*scale,)*2+(0,))
            gradient = np.max(np.stack([sobel(smooth[..., i]) for i in range(3)]), axis=0)
            labels = watershed(gradient, labels, mask=foreground)
    else:
        # No hue labels or color transitions enter the interior-marker/edge rule.
        gray = rgb2gray(rgb)
        gradient = sobel(ndi.gaussian_filter(gray, PARAMETERS['smooth_sigma']*scale))
        interior = foreground & (gradient < PARAMETERS['gray_edge'])
        markers, _ = markers_from_distance(interior, spacing, depth)
        marker_count = int(markers.max())
        labels = watershed(gradient, markers, mask=foreground)
    labels = compact(labels, area)
    count = int(labels.max())
    sizes = np.bincount(labels.ravel(), minlength=count+1)
    votes = np.bincount((labels.ravel()*(len(palette)+1)+classes.ravel()),
                        minlength=(count+1)*(len(palette)+1)).reshape(count+1, len(palette)+1)
    objects = []
    boxes = ndi.find_objects(labels)
    centers = ndi.center_of_mass(np.ones(labels.shape, np.uint8), labels, range(1, count+1))
    for i in range(1, count+1):
        best = int(np.argmax(votes[i, 1:]))+1
        fraction = float(votes[i, best]/sizes[i])
        ys, xs = boxes[i-1]
        objects.append(dict(detection_id=i, visible_pixels=int(sizes[i]),
                            bbox_xyxy=[xs.start, ys.start, xs.stop, ys.stop],
                            visible_centroid_xy=[float(centers[i-1][1]), float(centers[i-1][0])],
                            color=palette[best-1] if fraction >= PARAMETERS['color_fraction'] else 'unknown',
                            color_fraction=fraction, bead_index=None))
    return labels, dict(method=method, palette=palette_name, objects=objects,
                        marker_count=marker_count, foreground_pixels=int(foreground.sum()),
                        position_definition='Visible-region mask/bbox; centroid is descriptive, not body center',
                        index_status='unassigned')
