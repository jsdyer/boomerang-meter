import {get,options,data,fmt,stats,table,barlist,link,csv,initial,share,failure} from './ui.mjs';
import {filterGroups,counts,percent} from './model.mjs';
const controls=['date','source','destination','kind','direction'];
let state,anchors,observations,visible=[],previousDirection=initial.get('direction')||'',sequence=0;
const key=g=>g.from+'-'+g.to;
const label=id=>{const a=anchors.get(id);return a.city+' · AS'+a.network};
async function render(){
 const version=++sequence,day=get('date').value;
 if(!observations.has(day))observations.set(day,await data(day));
 if(version!==sequence)return;
 const edition=observations.get(day),groups=filterGroups(edition.groups,get('source').value,get('destination').value,get('kind').value);
 visible=[...groups].sort((a,b)=>(b.us/Math.max(1,b.reached))-(a.us/Math.max(1,a.reached))||label(a.from).localeCompare(label(b.from))||label(a.to).localeCompare(label(b.to)));
 const totals=counts(visible);
 stats([[fmt(totals.n),'Published traces'],[fmt(totals.reached),'Reached destination'],[fmt(totals.us),'Reached with US exchange evidence'],[percent(totals.us,totals.reached),'Share of reached traces in selection']]);
 get('matches').textContent=fmt(visible.length)+' sampled directions for '+day+', 18:00–20:00 UTC. Select a source city in the table to inspect its exchange matches.';
 table('records',['Source','Destination','Reached / observed','US evidence','Share of reached'],visible.map(g=>{
 const a=link(label(g.from),'?date='+day+'&direction='+key(g));a.addEventListener('click',e=>{e.preventDefault();previousDirection=key(g);get('direction').value=previousDirection;detail()});
 return [a,label(g.to),g.reached+' / '+g.n,g.us,percent(g.us,g.reached)]}));
 options('direction',visible.map(g=>[key(g),label(g.from)+' → '+label(g.to)]),previousDirection);detail();
}
function detail(){
 const g=visible.find(r=>key(r)===get('direction').value);previousDirection=get('direction').value;
 const day=get('date').value,edition=observations.get(day);
 get('finding').textContent=g?g.reached+' of '+g.n+' traces reached the destination. '+g.us+' had US exchange evidence, '+g.ca+' had Canadian exchange evidence, and '+g.unmatched+' had neither. Each bar counts reached traces matching that exchange.':'No directional sample matches these filters.';
 barlist('evidence',g?Object.entries(g.evidence).sort((a,b)=>b[1]-a[1]):[]);
 get('sources').replaceChildren(link('Same-day PeeringDB snapshot',edition.source));
 if(g){const a=anchors.get(g.to),start=Date.parse(day+'T18:00:00Z')/1000;
 const url='https://atlas.ripe.net/api/v2/measurements/'+a.measurement+'/results/?start='+start+'&stop='+(start+7199)+'&probe_ids='+g.from;
 get('sources').append(' · ',link('Original published results for this direction',url),' · ',link('RIPE Atlas measurement','https://atlas.ripe.net/measurements/'+a.measurement));}share(controls);
}
async function start(){state=await data('status');anchors=new Map(state.anchors.map(a=>[a.probe,a]));observations=new Map();
 options('date',[...state.dates].reverse().map(day=>[day,day]),initial.get('date'));
 const choices=[...anchors.keys()].map(id=>[id,label(id)]).sort((a,b)=>a[1].localeCompare(b[1]));
 for(const id of ['source','destination'])options(id,[['','All anchors'],...choices],initial.get(id));
 const kind=initial.get('kind');if([...get('kind').options].some(o=>o.value===kind))get('kind').value=kind;
 get('stamp').textContent=fmt(state.count)+' archived trace observations · '+state.dates.length+' sample dates · '+state.anchors.length+' Canadian anchors in the panel · Retrieved '+state.retrieved;
 for(const id of controls.slice(0,-1))get(id).onchange=()=>render().catch(failure);get('direction').onchange=detail;
 get('export').onclick=()=>csv('boomerang-'+get('date').value,['UTC date','Source anchor','Destination anchor','Source','Destination','Traces','Reached','US match','Canada match','Neither match'],visible.map(g=>[get('date').value,g.from,g.to,label(g.from),label(g.to),g.n,g.reached,g.us,g.ca,g.unmatched]));await render();
}start().catch(failure);
