const AIRK=%AIRK%, PORTK=%PORTK%, ACH_N=12;
function airSea(n,press,grew){
  state.flights=[]; const closedNow=[]; sfx("tick"); if(n.id==="parasite") return;
  state.regions.forEach(r=>{ if(r.airClosed>0) r.airClosed--; if(r.portClosed>0) r.portClosed--; });
  const airOpen=state.regions.filter(r=>r.air&&!(r.airClosed>0)), portOpen=state.regions.filter(r=>r.port&&!(r.portClosed>0));
  state.regions.forEach(r=>{
    if(r.inf>=6){
      if(r.air&&!(r.airClosed>0)&&rnd()<AIRK*(MARA?0.6:1)*(state.scenario.air||1)*(r.inf/100)*n.spread*(state.perks.flyer?1.7:1)){
        const t=pick(airOpen.filter(x=>x!==r));
        if(t){ const ob=t.inf; t.inf=clamp(t.inf+3+rnd()*4,0,100); state.flights.push({a:r.id,b:t.id,k:"air"}); if(ob<1&&t.inf>=1) grew.push(t.name); }
      }
      if(r.port&&!(r.portClosed>0)&&rnd()<PORTK*(r.inf/100)*(state.perks.cargo?1.8:1)){
        const t=pick(portOpen.filter(x=>x!==r));
        if(t){ const ob=t.inf; t.inf=clamp(t.inf+3+rnd()*4,0,100); state.flights.push({a:r.id,b:t.id,k:"sea"}); if(ob<1&&t.inf>=1) grew.push(t.name); }
      }
    }
    if(r.air&&r.det>40&&!(r.airClosed>0)&&rnd()<(0.12+press*0.2)*(state.perks.cargo?0.6:1)){ r.airClosed=5; closedNow.push(r.name); }
    if(r.port&&r.sealed>50&&!(r.portClosed>0)&&rnd()<0.1+press*0.15){ r.portClosed=6; }
  });
  const f=state.flights;
  if(f.length){ sfx("flight"); const a=state.regions.find(x=>x.id===f[0].a), b=state.regions.find(x=>x.id===f[0].b); log((f[0].k==="air"?"Flight":"Cargo")+" carries it "+a.name+" → "+b.name+(f.length>1?" (+"+(f.length-1)+" more)":"")+".","good"); }
  if(closedNow.length) log("Airports closed: "+closedNow.slice(0,3).join(", ")+".","bad");
}
function topInf(){ return state.regions.slice().sort((a,b)=>b.inf-a.inf)[0]; }
const CHOICES=[
 {id:"leak",w:()=>state.globalDetect>=12,mk:()=>({title:"Leaked lab notes",text:"An analyst has pieced together part of your pattern, and the notes are circulating.",opts:[
  {l:"Plant disinformation",d:"Costs 3 Influence. Detection −10, but the noise teaches the cure program (+3).",run:()=>{state.influence=Math.max(0,state.influence-3);state.globalDetect=clamp(state.globalDetect-10,0,100);state.cure=clamp(state.cure+3,0,100)}},
  {l:"Let it circulate",d:"Detection +4, but the confusion earns you 2 Influence.",run:()=>{state.globalDetect=clamp(state.globalDetect+4,0,100);state.influence+=2}}]})},
 {id:"hospital",w:()=>topInf().inf>8,mk:()=>{const r=topInf();return{title:"Hospitals overwhelmed in "+r.name,text:"Cases are stacking up and staff are stretched thin.",opts:[
  {l:"Exploit the chaos",d:r.name+": presence +10, detection +10.",run:()=>{r.inf=clamp(r.inf+10,0,100);r.det=clamp(r.det+10,0,100)}},
  {l:"Stay quiet",d:r.name+": detection −10, presence −2.",run:()=>{r.det=clamp(r.det-10,0,100);r.inf=Math.max(0,r.inf-2)}}]}}},
 {id:"rival",w:()=>state.cure>=15,mk:()=>({title:"A rival lab offers a deal",text:"Their lead researcher is open to leaks, for the right pressure.",opts:[
  {l:"Sabotage the lab",d:"Counter −10, but detection +8.",run:()=>{state.cure=Math.max(0,state.cure-10);state.globalDetect=clamp(state.globalDetect+8,0,100)}},
  {l:"Steal their findings",d:"Counter +4, but you gain 5 Influence.",run:()=>{state.cure=clamp(state.cure+4,0,100);state.influence+=5}}]})},
 {id:"exodus",w:()=>infectedCount()>=3,mk:()=>({title:"Mass exodus from a city",text:"Panicked crowds are heading for airports and highways.",opts:[
  {l:"Ride the flights",d:"Three random regions gain +6 presence. Detection +5.",run:()=>{for(let i=0;i<3;i++){const r=pick(state.regions);r.inf=clamp(r.inf+6,0,100)}state.globalDetect=clamp(state.globalDetect+5,0,100)}},
  {l:"Stay hidden",d:"Concealment +0.12.",run:()=>{state.traits.conceal=clamp(state.traits.conceal+0.12,0.35,2.8)}}]})},
 {id:"drift",w:()=>state.turn>=6,mk:()=>({title:"A mutation window opens",text:"Your pattern is unusually unstable this cycle.",opts:[
  {l:"Embrace the drift",d:"Stability −0.15, but Transmission +0.2.",run:()=>{state.stability=clamp(state.stability-0.15,0.12,1);state.traits.spread+=0.2}},
  {l:"Hold form",d:"Stability +0.15, costs 2 Influence.",run:()=>{state.stability=clamp(state.stability+0.15,0.12,1);state.influence=Math.max(0,state.influence-2)}}]})},
 {id:"politics",w:()=>state.globalDetect>=20,mk:()=>({title:"Governments split over borders",text:"Hawks want closures; doves want calm.",opts:[
  {l:"Feed the denial",d:"All seals −10, but the cure gains +3 from calmer coordination.",run:()=>{state.regions.forEach(r=>{r.sealed=clamp(r.sealed-10,0,94)});state.cure=clamp(state.cure+3,0,100)}},
  {l:"Stay quiet",d:"Detection −4.",run:()=>{state.globalDetect=clamp(state.globalDetect-4,0,100)}}]})},
 {id:"ships",w:()=>state.regions.some(r=>r.port&&r.inf>6),mk:()=>({title:"Container ships are sailing",text:"A huge convoy leaves infected ports tonight.",opts:[
  {l:"Hitch a ride",d:"Two random ports gain +5 presence. Detection +3.",run:()=>{const p=state.regions.filter(r=>r.port);for(let i=0;i<2;i++){const r=pick(p);r.inf=clamp(r.inf+5,0,100)}state.globalDetect=clamp(state.globalDetect+3,0,100)}},
  {l:"Let it pass",d:"Gain 3 Influence.",run:()=>{state.influence+=3}}]})}
];
function maybeChoice(){
  if(state.choiceId||state.turn<6||state.turn-(state.lastChoice||0)<7||rnd()>0.55) return;
  const pool=CHOICES.filter(c=>c.w()&&c.id!==state.lastChoiceId&&!(state.chDone&&state.chDone[c.id])); if(!pool.length) return;
  const c=pick(pool); state.lastChoice=state.turn; state.lastChoiceId=c.id; state.choiceId=c.id; (state.chDone=state.chDone||{})[c.id]=1; showChoice(c);
}
function resolveChoice(i){ const c=CHOICES.find(x=>x.id===state.choiceId); if(!c) return; const m=c.mk(); m.opts[i%m.opts.length].run(); if(state.perks.ledger) state.influence+=2; state.choiceId=null; }
function showChoice(c){
  const m=c.mk(); $("choice-title").textContent=m.title; $("choice-text").textContent=m.text;
  const box=$("choice-opts"); box.innerHTML="";
  m.opts.forEach((o,i)=>{
    const b=document.createElement("button"), s1=document.createElement("strong"), s2=document.createElement("span");
    b.className="diffbtn"; s1.textContent=(i+1)+". "+o.l; s2.textContent=o.d; b.append(s1,document.createElement("br"),s2);
    b.onclick=()=>{ o.run(); if(state.perks.ledger) state.influence+=2; state.choiceId=null; $("modal-choice").classList.add("hidden"); log("DECISION — "+o.l+".","warn"); (state.marks=state.marks||[]).push({t:state.turn,x:o.l}); renderAll(); };
    box.appendChild(b);
  });
  $("modal-choice").classList.remove("hidden"); sfx("choice"); if(box.firstChild&&box.firstChild.focus) box.firstChild.focus();
}
let memSave=null, memStats=null;
function clearSave(){ memSave=null; try{localStorage.removeItem("veil_save")}catch(e){} }
function saveGame(){ if(window.__nosave) return;
  try{ if(!state||state.dead||state.won){ clearSave(); return; }
    const j=JSON.stringify(Object.assign({},state,{nature:state.nature.id,scenario:state.scenario.id,camp:CAMP,mara:MARA,diff:DIFF,daily:DAILY,rng:SEED})); memSave=j; localStorage.setItem("veil_save",j); }catch(e){}
}
function loadSave(){
  let j=memSave; try{ j=localStorage.getItem("veil_save")||j }catch(e){}
  if(!j) return null;
  try{ const o=JSON.parse(j), nat=NATURES.find(n=>n.id===o.nature), sc=SCENARIOS.find(s=>s.id===o.scenario); if(!nat||!sc||!o.regions) return null; o.nature=nat; o.scenario=sc; return o; }catch(e){ return null; }
}
function loadStats(){ let o=memStats; try{ const j=localStorage.getItem("veil_stats"); if(j) o=JSON.parse(j) }catch(e){} return Object.assign({games:0,wins:0,fastest:0,ach:{}},o||{}); }
function saveStats(S){ memStats=S; try{localStorage.setItem("veil_stats",JSON.stringify(S))}catch(e){} }
function statLine(){ const S=loadStats(); return "Runs "+S.games+" · Wins "+S.wins+(S.fastest?" · Fastest win: cycle "+S.fastest:"")+" · Achievements "+Object.keys(S.ach).length+"/"+ACH_N; }
(function(){ const rb=document.getElementById("btn-resume"); if(!rb) return;
  rb.onclick=()=>{ const o=loadSave(); if(!o) return; state=o; CAMP=(o.camp===undefined)?null:o.camp; DAILY=o.daily||null; SEED=(o.rng===undefined)?null:o.rng; dailyCur=DAILY?dailySetup(DAILY):null; MARA=!!o.mara; DIFF=o.diff||1; selectedRegion=o.origin; tipStep=3; $("scenario-label").textContent=o.scenario.name; $("log").innerHTML=""; log("Run resumed.","sys"); $("delta").textContent="Advance to see what changes."; setTip(); renderAll(); show("screen-game"); const c=CHOICES.find(x=>x.id===o.choiceId); if(c) showChoice(c); };
})();
function drawRecap(){
  let cv=$("recap-chart");
  if(!cv){
    cv=document.createElement("canvas"); cv.id="recap-chart"; cv.setAttribute("role","img"); cv.setAttribute("aria-label","Run recap: presence, detection and counter by cycle");
    cv.style.cssText="width:100%;max-width:560px;height:220px;display:block;margin:1rem auto"; $("end-stats").insertAdjacentElement("afterend",cv);
    const nt=document.createElement("div"); nt.id="recap-notes"; nt.style.cssText="max-width:560px;margin:.4rem auto;font-size:.8rem;color:var(--muted);white-space:pre-line;text-align:left"; cv.insertAdjacentElement("afterend",nt);
  }
  const H=state.hist||[], W=1120, Ht=440; cv.width=W; cv.height=Ht; const g=cv.getContext("2d"); if(!g||H.length<2) return;
  const L=44, Rr=W-12, T=16, B=Ht-34, X=i=>L+(Rr-L)*i/(H.length-1), Y=v=>B-(B-T)*v/100;
  g.clearRect(0,0,W,Ht); g.font="22px sans-serif"; g.lineWidth=1; g.strokeStyle="rgba(150,190,180,.18)"; g.fillStyle="#9fb3ad";
  [0,25,50,75,100].forEach(v=>{g.beginPath();g.moveTo(L,Y(v));g.lineTo(Rr,Y(v));g.stroke();g.fillText(String(v),4,Y(v)+7)});
  const S=[["p","#7cfcb0","Presence"],["d","#5ab9ff","Detection"],["c","#ff7a7a","Counter"]];
  S.forEach(([k,col])=>{g.beginPath();g.strokeStyle=col;g.lineWidth=4;H.forEach((h,i)=>{const y=Y(clamp(h[k],0,100));if(i)g.lineTo(X(i),y);else g.moveTo(X(i),y)});g.stroke()});
  S.forEach(([k,col,nm],i)=>{g.fillStyle=col;g.fillText(nm,L+i*170,Ht-8)});
  const all=state.marks||[], mk=all.length>9?all.filter((_,i)=>i%Math.ceil(all.length/9)===0).slice(0,9):all;
  g.strokeStyle="rgba(255,255,255,.28)"; g.lineWidth=1; g.fillStyle="#e8f3ef";
  mk.forEach((m,k)=>{const i=Math.max(0,H.findIndex(h=>h.t>=m.t)), x=X(i); g.beginPath();g.moveTo(x,T);g.lineTo(x,B);g.stroke();g.fillText(String(k+1),x-6,T+18)});
  const nt=$("recap-notes"); if(nt) nt.textContent=mk.map((m,k)=>(k+1)+". Cycle "+Math.max(1,m.t-1)+" — "+m.x).join("\n");
}
