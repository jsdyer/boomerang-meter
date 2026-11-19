"""Summarize completed public Atlas mesh results alongside same-day PeeringDB records."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date, timezone, timedelta
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / 'web/data'
ANCHORS = json.loads((BASE / 'scripts/anchors.json').read_text())
PROBES = {a['probe']: a for a in ANCHORS}
ATLAS = 'https://atlas.ripe.net/api/v2/measurements/'
ARCHIVE = 'https://data.caida.org/datasets/peeringdb-v2'

def read_url(url):
    with urlopen(Request(url,headers={'User-Agent':'CoolCode historical mesh research'}),timeout=150) as r:
        return json.load(r)

def member_locations(db):
    def rows(key):
        return [r for r in db[key]['data'] if r.get('status')=='ok']
    facs={r['id']:r['country'] for r in rows('fac')}
    footprint={}
    for r in rows('ixfac'):
        footprint.setdefault(r['ix_id'],set()).add(facs.get(r['fac_id']))
    ix={r['id']:(r['country'],r['name']) for r in rows('ix') if r['country'] in ('US','CA') and footprint.get(r['id'])=={r['country']}}
    lans={r['id']:ix[r['ix_id']] for r in rows('ixlan') if r['ix_id'] in ix}
    addresses={}
    for r in rows('netixlan'):
        if r['ixlan_id'] in lans and r.get('ipaddr4') and r.get('operational') is not False:
            addresses.setdefault(r['ipaddr4'],set()).add(lans[r['ixlan_id']])
    return {ip:next(iter(candidates)) for ip,candidates in addresses.items() if len(candidates)==1}

def summarize(results, target, locations, start, stop):
    groups={}
    seen=set()
    for trace in results:
        probe=trace.get('prb_id')
        when=trace.get('timestamp',0)
        if probe not in PROBES or probe==target['probe'] or (probe,when) in seen or not start<=when<stop:
            continue
        if trace.get('msm_id')!=target['measurement'] or trace.get('af')!=4 or not isinstance(trace.get('result'),list):
            continue
        seen.add((probe,when))
        group=groups.setdefault(probe,{'from':probe,'to':target['probe'],'n':0,'reached':0,'us':0,'ca':0,'unmatched':0,'evidence':Counter()})
        group['n']+=1
        hops=trace['result']
        destination=trace.get('dst_addr')
        reached=False
        matches=set()
        for hop in hops:
            for reply in hop.get('result',[]):
                ip=reply.get('from')
                if ip and ip==destination:
                    reached=True
                elif ip in locations:
                    matches.add(locations[ip])
        if reached:
            group['reached']+=1
            for code in ('US','CA'):
                if any(country==code for country,_ in matches):group[code.lower()]+=1
            if not matches:group['unmatched']+=1
            group['evidence'].update(name for _,name in matches)
    return list(groups.values())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--date',type=date.fromisoformat)
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args()
    now=datetime.now(timezone.utc).date()
    day=args.date or now-timedelta(days=2)
    base=datetime.combine(day,datetime.min.time(),tzinfo=timezone.utc)+timedelta(hours=18)
    start=int(base.timestamp());stop=start+7200
    archive=f'{ARCHIVE}/{day:%Y/%m}/peeringdb_2_dump_{day:%Y_%m_%d}.json'
    snapshot=json.loads(args.archive.read_bytes()) if args.archive else read_url(archive)
    places=member_locations(snapshot)
    del snapshot
    def download(a):
        query=urlencode({'start':start,'stop':stop-1,'probe_ids':','.join(map(str,PROBES))})
        traces=read_url(ATLAS+str(a['measurement'])+'/results/?'+query)
        return summarize(traces,a,places,start,stop)
    with ThreadPoolExecutor(3) as workers:
        groups=sorted([g for group in workers.map(download,ANCHORS) for g in group],key=lambda g:(g['from'],g['to']))
    if not groups or sum(g['reached'] for g in groups)<5:raise ValueError('Insufficient completed historical results')
    DATA.mkdir(parents=True,exist_ok=True)
    def save(path,d):path.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
    save(DATA/(str(day)+'.json'),{'source':archive,'groups':groups})
    dates=sorted(p.stem for p in DATA.glob('????-??-??.json'))
    count=sum(g['n'] for daystr in dates for g in json.loads((DATA/(daystr+'.json')).read_text())['groups'])
    save(DATA/'status.json',{'retrieved':str(now),'dates':dates,'start':dates[0],'end':dates[-1],'count':count,'anchors':ANCHORS})

if __name__=='__main__':
    main()
