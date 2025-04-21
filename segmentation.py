"""
segmentation.py
---------------
Oversegmentation and region‐merging routines for bead detection.
Follows PEP 257 docstring conventions: high-level purpose first. :contentReference[oaicite:2]{index=2}
"""

import numpy as np
from skimage import segmentation, color
try:
    import skimage.future.graph as graph # type: ignore
except ImportError:
    import skimage.graph as graph
from skimage.measure import label, regionprops
import cv2

def slic_superpixels(image, n_segments=200):
    """
    Generate SLIC superpixels as an initial oversegmentation.
    
    Parameters
    ----------
    image : ndarray
        RGB input image.
    n_segments : int
        Approximate number of superpixels to generate.

    Returns
    -------
    segments : 2D ndarray of ints
        Label mask of superpixel regions.
    """
    # SLIC partitions image into roughly uniform superpixels :contentReference[oaicite:3]{index=3}
    segments = segmentation.slic(image, n_segments=n_segments, compactness=10)
    return segments

def build_rag(image, segments):
    """
    Build a Region Adjacency Graph (RAG) based on mean color.

    Uses skimage’s rag_mean_color under the hood :contentReference[oaicite:4]{index=4}.
    """
    lab = color.rgb2lab(image)  # convert to perceptual LAB space for color diffs
    # Each edge weight = Euclidean distance between region mean colors :contentReference[oaicite:5]{index=5}
    rag = graph.rag_mean_color(lab, segments)
    return rag

def merge_regions(image, segments, rag, thresh=25):
    """
    Hierarchically merge RAG nodes whose color difference < thresh.

    This yields contiguous bead‐like regions by merging similar superpixels. :contentReference[oaicite:6]{index=6}
    """
    merged = graph.merge_hierarchical(
        segments, rag, thresh, rag_copy=False, in_place_merge=True,
        merge_func=lambda g, src, dst: None,
        weight_func=lambda g, s, d, n: {'weight': np.linalg.norm(
            g.nodes[s]['mean color'] - g.nodes[d]['mean color']
        )}
    )
    return merged

def extract_regions(labels):
    """
    Label connected components and compute region properties.

    Returns a list of skimage.measure.RegionProperties for each bead. 
    """
    # regionprops supplies area, bbox, solidity, etc., useful for certainty 
    props = regionprops(labels)
    return props
