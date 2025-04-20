# segmentation.py

import numpy as np
from skimage import segmentation, color, graph, morphology
from skimage.future import graph as future_graph
from skimage.measure import label, regionprops
from skimage.color import rgb2lab
import cv2

def slic_superpixels(image, n_segments=200):
    """
    Oversegment image into superpixels with SLIC.
    """
    segments = segmentation.slic(image, n_segments=n_segments, compactness=10)  # :contentReference[oaicite:0]{index=0}
    return segments

def build_rag(image, segments):
    """
    Build a Region Adjacency Graph weighted by mean color difference.
    """
    lab = rgb2lab(image)
    rag = future_graph.rag_mean_color(lab, segments)  # :contentReference[oaicite:1]{index=1}
    return rag

def merge_regions(image, segments, rag, thresh=25):
    """
    Merge adjacent regions whose color difference < thresh.
    """
    labels = future_graph.merge_hierarchical(
        segments, rag, thresh, rag_copy=False,
        in_place_merge=True,
        merge_func=lambda g, src, dst: None,
        weight_func=lambda g, src, dst, n: {'weight': np.linalg.norm(
            g.nodes[src]['mean color'] - g.nodes[dst]['mean color']
        )}
    )
    return labels

def extract_regions(labels):
    """
    Extract connected bead regions and compute their properties.
    """
    props = regionprops(labels)
    return props
