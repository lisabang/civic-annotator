from civicpy import civic
from pyliftover import LiftOver
from cravat import constants

variants = civic.get_variants_by_ids(civic.get_all_variant_ids())
lifter = LiftOver(constants.liftover_chain_paths['hg19'])
vdict = {}
for variant in variants:
    chrom_37 = 'chr'+variant.coordinates.chromosome
    pos_37 = variant.coordinates.start
    new_coords = lifter.convert_coordinate(chrom_37, int(pos_37))
    if len(new_coords) > 0:
        chrom_38 = new_coords[0][0].replace('chr','')
        pos_38 = new_coords[0][1]
    else:
        continue
    ref = variant.coordinates.reference_bases
    alt = variant.coordinates.variant_bases
    toks = [chrom_38, pos_38, ref, alt]
    if None not in toks:
        vkey = ':'.join(map(str, toks))
        vdict[vkey] = variant
    else:
        continue

print(vdict[list(vdict.keys())[0]])