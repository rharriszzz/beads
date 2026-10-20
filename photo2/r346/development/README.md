# Rejected local-paper reference

These gzip files preserve the first measurement epoch and its search/control tables. The axis-radius115..150pixel band was incorrectly treated as unobstructed paper. Full-loop checks found that the photographed cast shadow extends into that band, especially to the right. Local log-plane extrapolation then produced implausibly steep apparent illumination gradients and false bright/inward-shadow behavior.

These measurements are **rejected**, including their displacement, width, darkness and camera-control scores. The final `output/background.json` uses a robust global illumination surface from a fixed grid farther than260pixels from the entire image-axis curve. Final profiles extend260pixels beyond each silhouette estimate and retain border censoring. Final search tables are recomputed against these corrected profiles. The R345 camera is unchanged.
