import sys
from cravat import BaseAnnotator
from cravat import constants, InvalidData
from pyliftover import LiftOver
import sqlite3
import requests
import json
import os

class CravatAnnotator(BaseAnnotator):

    def setup(self): 
        r = requests.get('https://civicdb.org/api/variants?count=5000&page=1')
        variants=json.loads(r.text)['records']
        lifter = LiftOver(constants.liftover_chain_paths['hg19'])
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
        self.civicdata = vdict

    def annotate(self, input_data, secondary_data=None):
        input_data["chrom"]=input_data["chrom"][3:]
         
        out={}        
        var_key = ":".join([input_data["chrom"],str(input_data["pos"]),input_data["ref_base"],input_data["alt_base"]])
        match=self.civicdata.get(var_key, False)
        if match:
            out["description"]=match['description']
            out["clinical_a_score"]=match['civic_actionability_score']
            civic_id = match['id']
            out['link'] = 'https://civicdb.org/links/variant/'+str(civic_id)
            evidence_link = 'https://civicdb.org/api/variants/{civic_id}/evidence_items?count=5000&page=1'.format(civic_id=civic_id)
            r = requests.get(evidence_link)
            d = json.loads(r.text)
            diseases = {x['disease']['display_name'] for x in d['records']}
            if len(diseases) > 0:
                out['diseases'] = ', '.join(sorted(list(diseases)))
        return out
    
    def cleanup(self):
        pass
        
if __name__ == '__main__':
    annotator = CravatAnnotator(sys.argv)
    annotator.run()
