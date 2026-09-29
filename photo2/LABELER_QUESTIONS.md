# Labeler specification — R138–R141

## Q138.1 — Label content and appearance

**Answered by R139.** The maker's specification, verbatim:

> I want to assign each visible bead a location (that I pick by hand) and a unique number.  Then I want to click near each location that lies in a particular direction, I will want to start a series, name the direction, then click on some number of bbeads that  a specific direction from a given bead.  Then I will end the series.  I will use d1 for the plus or minus 1 direction, d2 for up to down while proceeding clockwise around the bracelet (according to the major diameter of the torus), and d3 for up to down while proceeding clockwise.

Implement manually selected points and unique numbers, followed by a named series
of ordered clicks on existing beads. Numbers do not automatically mean bead_index.

## Q139.1 — Distinguish d2 and d3

Asked because R139 describes d2 and d3 identically:

> You described both d2 and d3 as up-to-down while proceeding clockwise around the bracelet. How should they differ—should one proceed counterclockwise, or did you mean another distinction?

**Answered by R140 and R141**, verbatim:

> d3 is down to up, sorry

> but that is the same as up to down while proceeding counterclockwise.

Thus d2 is up to down clockwise; d3 is down to up clockwise, equivalently up to
down counterclockwise. Preserve click order; no maker assignment of d2/d3 to
6/7 or signs is supplied. No further labeler question is pending.

![The wider context being labeled](review/r135/wider-context.png)

The program extracts the middle panel's raw content directly from the original
photo. It does not load the existing B/C/G overlay. The arrows made by the editor
will represent the maker's clicks, not guessed paths drawn on this reference.

[Run the program](LABELER.md). [Current problem and overall stages](../PLAN.md).
