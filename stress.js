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

const errs={};let runs=0;
for(let i=0;i<(+process.argv[2]||2500);i++){const mode=i%2,k=['idle','balanced','smart','vet','surge'][i%5];const chap=(i%7<5&&i%3===0)?i%10:undefined;
 try{run(NA[i%8],SC[(i>>3)%8],k,mode,chap);runs++}catch(e){const m=(e.stack||String(e)).split("\n").slice(0,2).join(" | ").slice(0,200);errs[m]=(errs[m]||0)+1}}
for(let i=0;i<500;i++){ try{ g.startDaily(); const st=g.state; let n=0; const kind=['idle','balanced','smart','vet','surge'][i%5]; while(!st.won&&!st.dead&&n++<90){ if(st.choiceId) g.resolveChoice(i%2); bot(kind); g.advanceCycle(); } runs++; }catch(e){ const m=(e.stack||String(e)).split("\n").slice(0,2).join(" | ").slice(0,200); errs[m]=(errs[m]||0)+1; } }
console.log('runs ok',runs,'errors',JSON.stringify(errs,null,1));
