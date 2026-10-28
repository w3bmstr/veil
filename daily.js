let SEED=null, DAILY=null, dailyCur=null, lastDaily=null;
function rnd(){ if(SEED===null) return Math.random(); SEED=(SEED+0x6D2B79F5)|0; let t=Math.imul(SEED^(SEED>>>15),1|SEED); t=(t+Math.imul(t^(t>>>7),61|t))^t; return ((t^(t>>>14))>>>0)/4294967296; }
function utcKey(d){ const x=d||new Date(); return x.getUTCFullYear()+"-"+String(x.getUTCMonth()+1).padStart(2,"0")+"-"+String(x.getUTCDate()).padStart(2,"0"); }
function hashStr(s){ let h=2166136261; for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619); } return h>>>0; }
const DMODS=[
 {n:"Cold Open",d:"The countermeasure starts at 15%.",f:()=>{state.cure=15}},
 {n:"Rich Start",d:"Begin with 14 Influence.",f:()=>{state.influence=14}},
 {n:"Loud World",d:"Detection starts at 20%.",f:()=>{state.globalDetect=20}},
 {n:"Walled Borders",d:"Every region starts 20% sealed.",f:()=>{state.regions.forEach(r=>{r.sealed=20})}},
 {n:"Fast Lab",d:"Research runs 25% faster all game.",diff:1.25},
 {n:"Sleepy Lab",d:"Research runs 15% slower all game.",diff:0.85},
 {n:"Unstable Form",d:"Stability starts at 35%.",f:()=>{state.stability=0.35}},
 {n:"Head Start",d:"Begin with a free adaptation.",f:()=>{grantPerk(["quiet","shell","heat","urban","aero"][dailyCur.seed%5])}}
];
function dailySetup(key){ const h=hashStr("veil:"+key); return {key,sc:SCENARIOS[h%SCENARIOS.length],nat:NATURES[(h>>>8)%NATURES.length],mod:DMODS[(h>>>16)%DMODS.length],seed:h}; }
function dailyStreak(S){ const days=S.daily||{}; let n=0, d=new Date(); if(!days[utcKey(d)]) d=new Date(d.getTime()-864e5); while(days[utcKey(d)]){ n++; d=new Date(d.getTime()-864e5); } return n; }
function openDaily(){
  const key=utcKey(), d=dailySetup(key), S=loadStats(), e=(S.daily||{})[key], st=dailyStreak(S);
  document.getElementById("daily-desc").textContent=key+" (resets at 00:00 UTC). "+d.sc.name+" scenario, "+d.nat.name+" pathogen. Modifier: "+d.mod.n+": "+d.mod.d;
  const best=e?("Today's best: "+(e.win?"WIN in "+e.turn+" cycles":"erased at cycle "+e.turn)+", score "+e.score+"."):"Not played yet today.";
  document.getElementById("daily-stats").textContent=best+" Streak: "+st+" day"+(st===1?"":"s")+". Days played: "+Object.keys(S.daily||{}).length+".";
  document.getElementById("modal-daily").classList.remove("hidden"); const p=document.getElementById("daily-play"); if(p&&p.focus) p.focus();
}
function startDaily(){
  const key=utcKey(), d=dailySetup(key); dailyCur=d; DAILY=key; CAMP=null; MARA=false; DIFF=d.mod.diff||1; selectedScenario=d.sc.id; selectedNature=d.nat.id; SEED=d.seed;
  newGame(); if(d.mod.f) d.mod.f(); log("DAILY — "+d.mod.n+": "+d.mod.d,"warn");
  const m=document.getElementById("modal-daily"); if(m) m.classList.add("hidden"); renderAll();
}
function shareText(){
  const r=lastDaily; if(!r) return ""; const d=dailySetup(r.key), S=loadStats();
  return "VEIL Daily "+r.key+" · "+d.sc.name+"/"+d.nat.name+" · "+d.mod.n+"\n"+(r.run.win?"Permanent in "+r.run.turn+" cycles":"Erased at cycle "+r.run.turn)+" · Score "+r.run.score+"\nPresence "+r.pres+"% · Detection "+r.det+"% · Counter "+r.cure+"%\nStreak "+dailyStreak(S);
}
function dailyEnd(win){
  let btn=document.getElementById("daily-share");
  if(!btn){ btn=document.createElement("button"); btn.id="daily-share"; btn.type="button"; btn.className="pillbtn"; btn.textContent="Copy daily result"; btn.style.cssText="display:none;margin:.6rem auto"; const note=document.createElement("div"); note.id="daily-share-note"; note.style.cssText="font-size:.8rem;color:var(--muted);white-space:pre-line;text-align:center";
    const anchor=document.getElementById("end-stats"); if(anchor&&anchor.insertAdjacentElement){ anchor.insertAdjacentElement("afterend",note); anchor.insertAdjacentElement("afterend",btn); }
    btn.onclick=()=>{ const t=shareText(), n=document.getElementById("daily-share-note"); let ok=false; try{ if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t); ok=true; } }catch(e){} if(!ok){ try{ const ta=document.createElement("textarea"); ta.value=t; document.body.appendChild(ta); ta.select(); ok=document.execCommand("copy"); ta.remove(); }catch(e){} } n.textContent=ok?"Copied!\n"+t:t; };
  }
  const note=document.getElementById("daily-share-note"); if(note) note.textContent="";
  if(!DAILY){ btn.style.display="none"; return; }
  const S=loadStats(); S.daily=S.daily||{}; const score=calcScore(), entry={score,win:!!win,turn:state.turn-1}, prev=S.daily[DAILY];
  if(!prev||(entry.win&&!prev.win)||(entry.win===prev.win&&score>prev.score)) S.daily[DAILY]=entry;
  S.ach=S.ach||{}; const had1=!!S.ach["Daily Driver: finished a daily challenge"]; S.ach["Daily Driver: finished a daily challenge"]=1;
  const st=dailyStreak(S), had3=!!S.ach["On a Roll: 3-day daily streak"]; if(st>=3) S.ach["On a Roll: 3-day daily streak"]=1; saveStats(S);
  lastDaily={key:DAILY,run:entry,pres:Math.round(totalPresence()),det:Math.round(state.globalDetect),cure:Math.round(state.cure)};
  btn.style.display="block"; const es=document.getElementById("end-stats"); if(es) es.textContent+=" · Daily "+DAILY+": streak "+st+(had1?"":" ★ Daily Driver")+((st>=3&&!had3)?" ★ On a Roll":"");
}
(function(){
  const g=id=>document.getElementById(id);
  if(g("btn-daily")) g("btn-daily").onclick=openDaily;
  if(g("daily-play")) g("daily-play").onclick=startDaily;
  if(g("daily-close")) g("daily-close").onclick=()=>g("modal-daily").classList.add("hidden");
  if(g("btn-start")&&g("btn-start").addEventListener) g("btn-start").addEventListener("click",()=>{ DAILY=null; SEED=null; });
})();
