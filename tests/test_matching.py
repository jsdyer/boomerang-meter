import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from refresh import ANCHORS,summarize

class MatchingTests(unittest.TestCase):
    def test_duplicates_incomplete_paths_and_country_overlap(self):
        origin, target=ANCHORS[:2]
        def trace(t, hops):
            return {'prb_id':origin['probe'],'timestamp':t,'msm_id':target['measurement'],'af':4,'dst_addr':'end','result':[{'result':[{'from':x}]} for x in hops]}
        success=trace(100,['west','east','end'])
        groups=summarize([success,success,trace(109,['east'])],target,{'west':('CA','Canada IX'),'east':('US','US IX')},90,120)
        row=groups[0]
        self.assertEqual([row[k]for k in ('n','reached','ca','us','unmatched')],[2,1,1,1,0])
        self.assertEqual(row['evidence']['US IX'],1)
