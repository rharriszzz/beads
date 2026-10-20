"""Expanded native contexts for every remaining ownership abstention."""
from common import *
from audit_panels import sheets
from native_audit import FOLLOWUP_RESOLVED

def main():
 records=[r for r in read(OUT/'native-audit.json.gz')['records'] if not r['measured_pixels_convincingly_owned'] or r['id'] in FOLLOWUP_RESOLVED];sheets(records,'uncertain-ownership',False);save(OUT/'uncertain-review.json',dict(records=len(records),pages=9,initial_flags=50,resolved_as_owned=6,remaining_uncertain=44,policy='Expanded context inspection of all50 initial flags; six owned not-black patches confirmed. No pigment/geometry change; no pattern vote.'));print('Expanded uncertain contexts',len(records))
if __name__=='__main__':main()
