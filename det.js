const fs=require('fs');const cap={};
function mk(id){const st={};return new Proxy(function(){},{get(t,p){if(p in st)return st[p];if(p==='children')return{length:0};if(p==='classList')return{add(){},remove(){},toggle(){},contains(){return id==='screen-game'}};if(p==='style')return{};return(...a)=>mk(id)},set(t,p,v){st[p]=v;if(id==='end-desc'&&p==='textContent')cap.end=v;return true},apply(){return mk(id)}})}
const els={};
globalThis.document={getElementById:id=>els[id]||(els[id]=mk(id)),querySelectorAll:()=>[],querySelector:()=>null,createElement:()=>mk('x'),addEventListener(){},body:mk('body')};
globalThis.window=globalThis;globalThis.__nosave=true;globalThis.__autostart=true;globalThis.localStorage={getItem:()=>null,setItem(){}};globalThis.requestAnimationFrame=()=>0;
eval(fs.readFileSync('game.js','utf8'));const g=__g;
const SC=['bloom','ghost','iron','fire','monsoon','frostbite','fortress','skies'],NA=['spore','vector','viral','dormant','fungal','parasite','prion','synthetic'];
function bot(kind){const st=g.state,M=Object.fromEntries(g.MUT_OPTIONS.map(m=>[m.id,m]));const t=id=>st.influence>=M[id].cost&&(g.applyMut(M[id]),true);
 if(kind==='idle')return; if(kind==='vet'){for(const id of ['quiet','shell','heat','urban','aero','camo','memory','drugres','sabotage','rural','flyer','media','whisper','viralload']){const m=M[id];if(m&&!st.perks[id]&&(!m.req||st.perks[m.req])&&st.influence>=m.cost+3){g.applyMut(m);break}}} if(kind==='surge'){while(t('surge'));return}
 let n=0;while(n++<10){let ok=false;if(st.stability<0.45)ok=t('stabilize');
  if(!ok){const o=(kind==='smart'||kind==='vet')?(st.globalDetect>15?['hide','res','hide','trans']:['trans','trans','seed','hide']):['trans','hide','res','trans','seed'];ok=t(o[st.mutCount%o.length])}
  if(!ok)break}}

function runDaily(){ g.startDaily(); const st=g.state; let i=0;
  while(!st.won&&!st.dead&&i++<90){ if(st.choiceId) g.resolveChoice(0); bot('smart'); g.advanceCycle(); }
  return JSON.stringify({w:st.won,t:st.turn,inf:+st.influence.toFixed(3),pres:+g.totalPresence().toFixed(3),cure:+st.cure.toFixed(3),det:+st.globalDetect.toFixed(3),origin:st.origin,sc:st.scenario.id,nat:st.nature.id}); }
const a=runDaily(), b=runDaily(), c=runDaily();
console.log('run A:',a);console.log('run B:',b);console.log('identical:',a===b&&b===c);
const k=g.utcKey(); const d1=g.dailySetup(k), d2=g.dailySetup('2026-10-27'), d3=g.dailySetup('2026-10-28');
console.log('today',k,'->',d1.sc.id+'/'+d1.nat.id+'/'+d1.mod.n,'| next days:',d2.sc.id+'/'+d2.nat.id+'/'+d2.mod.n,'|',d3.sc.id+'/'+d3.nat.id+'/'+d3.mod.n);
// distribution of 200 days
const cnt={};for(let i=0;i<400;i++){const dd=new Date(Date.UTC(2026,0,1+i));const x=g.dailySetup(g.utcKey(dd));cnt[x.sc.id]=(cnt[x.sc.id]||0)+1}
console.log('scenario spread over 400 days:',JSON.stringify(cnt));
