"""Restore delivery-only measured summary after generic figure regeneration."""
from photo2.r323.tracker import ROOT
p=ROOT/'photo2/r323/results/index.html'
s=p.read_text()
if 'href="diagnosis.json"' not in s:s=s.replace('· <a href="observation-pixels.json">Native supports</a>','· <a href="observation-pixels.json">Native supports</a> · <a href="diagnosis.json">Local alternatives and overlap conflicts</a> · <a href="heldout-validation.png">All 40 held-out associations</a>')
s=s.replace('See held-out evaluation for measured errors.','Held-out result: 25/25 interior beads, 45/45 interior links, zero wrong interior links; 33/40 beads and 65/86 links overall. The larger 98-site graph remains conditional.')
s=s.replace('Automatically selected competing continuations, with original pixels alongside.','Automatically selected unresolved continuations: original pixels beside two retained local hypotheses, their integer steps, scores and overlap evidence.')
p.write_text(s)
