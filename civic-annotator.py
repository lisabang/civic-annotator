import sys
from cravat import BaseAnnotator
from cravat import constants, InvalidData
from pyliftover import LiftOver
import sqlite3
import requests
import json
from civicpy import civic
import os

class CravatAnnotator(BaseAnnotator):

    def setup(self): 
        """
        Set up data sources. 
        Cravat will automatically make a connection to 
        data/example_annotator.sqlite using the sqlite3 python module. The 
        sqlite3.Connection object is stored as self.dbconn, and the 
        sqlite3.Cursor object is stored as self.cursor.
        """
        #print("dlwfno")
        #self.lifter = LiftOver(constants.liftover_chain_paths[self.input_assembly])
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
        self.civicdata = vdict

    def annotate(self, input_data, secondary_data=None):
        """
        The annotator parent class will call annotate for each line of the 
        input file. It takes one positional argument, input_data, and one
        keyword argument, secondary_data.
        
        input_data is a dictionary containing the data from the current input 
        line. The keys depend on what what file is used as the input, which can 
        be changed in the module_name.yml file. 
        Variant level includes the following keys: 
            ('uid', 'chrom', 'pos', 'ref_base', 'alt_base')
        Variant level crx files expand the key set to include:
            ('hugo', 'transcript','so','all_mappings')
        Gene level files include
            ('hugo', 'num_variants', 'so', 'all_so')
        
        secondary_data is used to allow an annotator to access the output of
        other annotators. It is described in more detail in the CRAVAT 
        documentation.
        
        annotate should return a dictionary with keys matching the column names
        defined in example_annotator.yml. Extra column names will be ignored, 
        and absent column names will be filled with None. Check your output
        carefully to ensure that your data is ending up where you intend.
        """
        #here we get all variants from CIViC
        #all_variants=civic.get_all_variants()
        input_data["chrom"]=input_data["chrom"][3:]
         
        out={}        
        out['placeholder_annotation'] = ":".join([input_data["chrom"],str(input_data["pos"]),input_data["ref_base"],input_data["alt_base"]])
        match=self.civicdata.get(out["placeholder_annotation"], False)
        if match:
            out["description"]=match['description']
            out["clinical_a_score"]=match['civic_actionability_score']
        return out
    
    def cleanup(self):
        """
        cleanup is called after every input line has been processed. Use it to
        close database connections and file handlers. Automatically opened
        database connections are also automatically closed.
        """
        pass
        
if __name__ == '__main__':
    annotator = CravatAnnotator(sys.argv)
    annotator.run()
