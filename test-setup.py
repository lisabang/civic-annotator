from civicpy import civic
from pyliftover import LiftOver
from cravat import constants
import requests
import json
r = requests.get('https://civicdb.org/api/variants?count=5000&page=1')
variants=json.loads(r.text)['records']
#variants = civic.get_variants_by_ids(civic.get_all_variant_ids())
lifter = LiftOver(constants.liftover_chain_paths['hg19'])
print("lifted variants")
vdict = {}
for variant in variants:
    chrom_37 = variant['coordinates']['chromosome']
    pos_37 = variant['coordinates']['start']
    if chrom_37 is None or pos_37 is None: continue
    new_coords = lifter.convert_coordinate("chr" + chrom_37, int(pos_37))
    if len(new_coords) > 0:
        chrom_38 = new_coords[0][0].replace('chr','')
        pos_38 = new_coords[0][1]
    else:
        continue
    ref = variant['coordinates']['reference_bases']
    alt = variant['coordinates']['variant_bases']
    toks = [chrom_38, pos_38, ref, alt]
    if None not in toks:
        vkey = ':'.join(map(str, toks))
        vdict[vkey] = variant
    else:
        continue

print(vdict[list(vdict.keys())[0]])
