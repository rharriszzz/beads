"""Explicit native contact-atlas inspection ledger; independent of pattern analysis."""
from common import *
# Every one of the16 B/R sheets and7 yellow sheets was inspected. These are
# exceptions to native patch ownership, not exceptions to the pigment threshold.
UNCERTAIN={
 'C-0257-1090':'Selected patch reaches the lower body rim; shadow/material ownership is not certain.',
 'C-0451-0731':'Selected patch reaches upper glass/rim boundary.',
 'C-0505-1557':'Maker red. New circle selects darkness above the actual red body; raw false black. Preserve red.',
 'C-1004-2311':'Selected patch is at the upper glass boundary, not a safe interior sample.',
 'C-1189-2919':'Selected patch at far-right boundary of dim red body; keep label, abstain.',
 'C-1478-2990':'Selected patch reaches upper glass boundary.',
 'C-1796-1653':'Selected patch approaches the boundary against the yellow material above.',
 'C-1868-2785':'Partly exposed colored material beside yellow neighbor; ownership of selected peripheral patch unclear.',
 'C-2099-0725':'Selected lower rim rather than a confidently interior body patch.',
 'E5-1178-2887':'Dim red body is visible; the score73 patch reaches right-hand rim/shadow. No threshold change or recoloring.',
 'NEW-1247-1469':'Selected patch at lower edge of body.',
 'NEW-1519-2976':'Maker red retained. Selected upper/right pixels approach background; raw not-black does not certify interior ownership.',
 'NEW-1681-1498':'Support lies on/near the upper edge of visible yellow C-1677-1513; selected dark patch lies above it. Separate target material not established; no identity/coordinate/color change.',
 'NEW-1684-1980':'Orange-yellow material at the source appears close to another recorded yellow body. Own material is not independently established; no pigment change.',
 'NEW-1826-438':'Peripheral partly exposed source; safe ownership of the selected patch is uncertain.',
 'NEW-563-1633':'Support lies on/near lower edge of yellow E5-0562-1620; selected darkness lies below it. Do not invent or merge a body, or infer black from neighboring shadow.',
 'PROV326-290-1410':'Very dim body context; known working identity retained, but exact material boundary at selected patch is not convincingly resolved.',
 'R332-R-0037-0040':'Very dim peripheral colored source; selected patch not safely attributable to an interior body.',
 'R332-R-0077-0077':'Partial lower-right crescent beside red C-1739-2960 and black NEW-1764-2958; selected dark patch could be own material or boundary/neighbor. Preserve record and ask a native-body question.',
 'R332-R-0111-0104':'Selected upper colored boundary near adjoining yellow material.',
 'R332-R-0125-0118':'Dim peripheral orange material; red/yellow association and safe patch ownership remain uncertain.',
 'R332-R-0142-0132':'Patch at upper edge of thin exposed colored body.',
 'R332-R-0147-0142':'Orange/yellow-looking peripheral material; own recorded-red body is not independently distinguished.',
 'R332-R-0167-0155':'Maker red retained; peripheral patch reaches material/background boundary.',
 'R332-R-0197-0183':'Dim orange material at rope boundary; safe own-body sample and red/yellow association unresolved.',
 'REC266-P035619':'Dim peripheral colored body; selected right-edge patch may include boundary.',
 'REC266-P100583':'Dim orange material at boundary; own safe glass patch not established.',
 'REC266-P119618':'Selected upper edge of dim colored body rather than secure interior.',
 'C-0234-1447':'Selected patch at lower edge of partly exposed yellow body.',
 'C-0326-0793':'Selected right edge approaches adjoining material.',
 'C-0384-0878':'Dark yellow control, score90; selected far-right boundary is not a safe body interior.',
 'C-0666-1567':'Selected upper edge of orange/yellow material.',
 'C-1001-2678':'Selected lower rim of yellow body.',
 'C-1119-2879':'Selected patch at lower/right boundary near adjoining red material.',
 'C-1151-2862':'Raw score78 near threshold belongs to peripheral material/boundary, not a certified glass interior.',
 'C-1241-2153':'Peripheral colored strip; selected right-side patch not securely inside one body.',
 'C-1253-2928':'Known R340 yellow stress case. New score44 samples beyond yellow glass at upper/right boundary; raw false black, preserve yellow.',
 'C-1264-2957':'Visible yellow body; score43 patch lies above/right of its glass. Raw false black, preserve yellow.',
 'C-1364-2971':'Maker yellow retained. Selected upper/right patch is peripheral to the actual yellow body.',
 'C-1659-0261':'Selected lower rim close to adjoining material.',
 'C-1837-2811':'Selected lower rim of partly exposed yellow bead.',
 'C-1977-2780':'Dim partly exposed yellow control, score96; selected peripheral patch may contain boundary.',
 'C-2145-1092':'Selected patch near top material boundary.',
 'C-2221-1524':'Selected patch at right body boundary near adjacent black material.',
 'NEW-1169-2185':'Selected lower patch approaches dark boundary below visible yellow material.',
 'R332-Y-0128-0121':'Selected upper patch is at boundary against neighboring black material.',
 'R332-Y-0145-0140':'Selected right/lower boundary, not secure glass interior.',
 'R332-Y-0197-0184':'Dim colored material at rope edge; patch ownership uncertain.',
 'R332-Y-0197-0189':'Source near lower boundary of visible yellow material; own-body association uncertain.',
 'REC266-P074050':'Selected lower/right patch at visible yellow boundary.',
}
CHANGES={
 'E9-2263-1691':'Distinct existing oval body between red neighbors. Dark glass to right of bright lobe is clearly within its outline; new patch32. Red tint is confined to illumination, not surrounding material.',
 'NEW-1251-1537':'Weak-lobe black body has a visible oval outline against paper below/right and yellow neighbors above/left. Patch36 lies inside that dark material; no visible reflection is required.',
 'NEW-2136-2445':'Existing body bounded by yellow neighbors and paper-side outline. Patch58 is dark glass above/right of the bright lobe, inside the same body.',
 'NEW-2199-2298':'Existing oval dark body among red neighbors; patch36 lies in its upper/right glass, separated from the surrounding red bodies.',
 'NEW-2251-1608':'Existing dark body between red neighbors; patch32 lies to the right of its bright lobe and remains within visible glass.',
 'NEW-451-650':'Existing black-looking oval between red bodies. Patch27 is in right-side dark material, not the adjacent red body or paper.',
 'NEW-910-2406':'Existing elongated dark body between red and yellow neighbors. Patch30 lies on its right-side glass beside the vertical bright lobe.',
 'R332-R-0196-0188':'Distinct dark oval above two yellow bodies; reddish lobe on left is separate from dark right-side glass. Patch65 is inside that established body.',
 'REC266-P054157':'Existing dark body with a tinted lobe among yellow neighbors. Patch40 lies inside the dark glass to the right; no body move or association change.',
 'REC266-P054537':'Existing dark body with a pale/colored lobe; yellow bodies remain separately visible below/right. Patch46 is on its right-hand glass.',
 'REC266-P076585':'Existing dark oval between yellow bodies. Patch37 is on its right-side material; the yellow body below is separate.',
 'REC266-P106767':'Existing dark oval between red bodies and yellow material above/left. Patch47 is within its upper/right dark glass, separate from red neighbors.'}

def main():
 g,obs,co,rgb,auth,old=load();data=read(OUT/'classification.json.gz');records=[];manifest=read(OUT/'audit-black-red-manifest.json')+read(OUT/'audit-yellow-manifest.json');lookup={r['id']:r for r in manifest};assert set(lookup)==set(obs);assert len(lookup)==1058
 for r in data['records']:
  o=r['id'];m=r['measurement'];owned=o not in UNCERTAIN;raw=m['raw_decision'] if m else 'unknown';source=lookup[o]
  row=dict(r,native_contact_page=source['page'],native_contact_number=source['number'],native_contact_set='black-red' if r['recorded_color'] in ['black','red'] else 'yellow',native_glass_ownership='convincingly_inside_visible_body' if owned else 'uncertain_or_wrong_material',measured_pixels_convincingly_owned=owned,native_assessment=CHANGES[o] if o in CHANGES else UNCERTAIN[o] if not owned else 'Native contact-atlas inspection: selected contiguous patch appears inside this established body; does not certify a complete contour or create a bead identity.',audited_decision=raw if owned else 'unknown',binary_recorded_agreement=(raw=='black')==(r['recorded_color']=='black') if owned else None,full_pigment_certification='maker authoritative' if o in auth else 'black material supported' if owned and raw=='black' else 'not-black only; this test does not decide red versus yellow' if owned else 'not established')
  records.append(row)
 assert all(o in obs and o not in auth and obs[o]['color']=='red' for o in CHANGES)
 for r in records:
  if r['binary_recorded_agreement'] is False:assert r['id'] in CHANGES
 save(OUT/'native-audit.json.gz',dict(records=records,reviewed_contact_pages=dict(black_red=list(range(1,17)),yellow=list(range(1,8))),reviewed_observations=1058,reviewed_black=378,reviewed_red=356,reviewed_yellow=324,all_disagreements_detail_reviewed=19,uncertain_ownership=UNCERTAIN,accepted_changes=CHANGES,policy='Every native contact-atlas tile inspected, including all algorithmic abstentions; all19 disagreement contexts separately inspected unaltered and marked. Ownership statements are explicit native visual judgments, not classifier truth labels or pattern votes. Allmaker labels retained; no identity/coordinate changes.',pattern_used=False))
 save(OUT/'native-judgments.json',dict(uncertain_ownership=UNCERTAIN,accepted_changes=CHANGES,contact_pages=dict(black_red=16,yellow=7),policy='Frozen photographic ownership judgments, independent of strict208 analysis.'))
 print('AUDIT',len(records),'owned',sum(r['measured_pixels_convincingly_owned'] for r in records),'uncertain',len(UNCERTAIN),'corrections',len(CHANGES));print('audited decisions',Counter(r['audited_decision'] for r in records))
if __name__=='__main__':main()
