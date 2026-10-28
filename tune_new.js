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

function run(n,s,k,mode,chap){g.setMode(mode?1:0);if(chap!==undefined){g.startChapter(chap)}else{g.setSel(n,s);g.newGame()}const st=g.state;let i=0;const lim=mode?150:80;
 while(!st.won&&!st.dead&&i++<lim){if(st.choiceId)g.resolveChoice(Math.floor(Math.random()*2));bot(k);g.advanceCycle()}return{w:st.won,t:st.turn-1}}
const N=+process.argv[2]||6;const out={};
for(const k of ['smart','vet']){
 const byN={},byS={};
 for(const n of NA)for(const s of SC)for(let i=0;i<N;i++){const r=run(n,s,k,0);(byN[n]=byN[n]||[0,0,0]);(byS[s]=byS[s]||[0,0,0]);byN[n][0]+=r.w?1:0;byN[n][1]++;byN[n][2]+=r.t;byS[s][0]+=r.w?1:0;byS[s][1]++;byS[s][2]+=r.t}
 const f=o=>Object.entries(o).map(([a,v])=>a+' '+(100*v[0]/v[1]).toFixed(0)+'%(T'+(v[2]/v[1]).toFixed(0)+')').join(' | ');
 console.log(k+' natures: '+f(byN));console.log(k+' scenarios: '+f(byS));
}
const ch=[];for(let c=0;c<10;c++){let w=0,tt=0;const M=Math.max(6,N*2);for(const k of ['smart','vet'])for(let i=0;i<M;i++){const r=run(0,0,k,0,c);w+=r.w?1:0;tt+=r.t}ch.push('ch'+(c+1)+' '+(100*w/(2*M)).toFixed(0)+'%')}
console.log('campaign:',ch.join(' | '));
