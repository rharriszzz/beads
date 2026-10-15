# Inference and split freeze

Detector runs on entire RGB image, saves all147268 thresholded maxima events,
1545 retained features. No accepted masks, historic locations, indices or geometry
are arguments. Paper rejection reordered early for performance before any output;
initial source retained. Native connected85%-peak patch,3..100px,16px window,
local contrast and paper gate; alternate maxima retained; no neighboring substitute.
Six image-angle regions;1/4evaluation,100px development buffer. Frozen method/split
hashes in calibration-frozen.json before evaluation. 207 eligible unique training
R275 matches,163evaluation. Multiple/missing references never borrowed from neighbor.
