export function filterGroups(rows,source,destination,kind){
 return rows.filter(g=>(!source||g.from===Number(source))&&(!destination||g.to===Number(destination))&&(kind==='all'||g[kind]>0));
}
export function counts(rows){return rows.reduce((t,g)=>({n:t.n+g.n,reached:t.reached+g.reached,us:t.us+g.us}),{n:0,reached:0,us:0})}
export function percent(n,d){return d?(100*n/d).toLocaleString('en-CA',{maximumFractionDigits:1})+'%':'—'}
