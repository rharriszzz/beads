# Checkpoint3 — reviewed development before confirmation

First implementation retained without threshold tuning. All masks and failed alternatives
are saved in development.json.gz and P1–P5-all.png. Native area comparison:

|Case|J|S|M|A|B|C|
|---|---:|---:|---:|---:|---:|---:|
|P1|439|540|540|540|540|604|
|P2|200|495|495|495|495|495|
|P3|405|446|446|451|446|519|
|P4|439|320|320|325|320|363|
|P5|511|1817|664|665|664|777|

P2 masks are exactly unchanged from good S, not merely equal in area. P5 M/B
remove1153 pixels from S and recover the single central yellow interior; the
19.88px centroid correction is toward that interior. The marker repair alone
explains this development improvement: B and M match on every reviewed case.
No extra benefit of B's protected merger rule is established by these five cases.
A independently obtains nearly the same separation without watershed markers.
C leaves larger lobes/wedges, especially P3; preserve it as a failed alternative.
P1 still inherits acceptable S rather than preferred J, and P3 remains slightly
worse than preferred J. Separation improvement is not a claim of universal boundary
improvement. No method is adopted. M/A/B domain32 versus48 IoU is1 on all five.

Freeze current algorithms and parameters now, before generating or inspecting the
10 independently selected confirmation regions (52 photographic cues). No tuning
against confirmation. Next: report central and edge strata separately, inspect all
outputs, quantify overlap/stability/coverage and preserve unexpected failures.
