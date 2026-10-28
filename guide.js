let memTut=false, tutStep=-1, tutOn=false, tutTimer=0;
function tutDone(){ try{ if(localStorage.getItem("veil_tut")) return true; }catch(e){} return memTut; }
function incomeNow(){ return 2.5+totalPresence()/18+(state.globalDetect>25?1.3:0)+infectedCount()*0.12*RS+(state.perks&&state.perks.viralload?1:0); }
function openHelp(){ const m=document.getElementById("modal-help"); if(m){ m.classList.remove("hidden"); const c=document.getElementById("help-close"); if(c&&c.focus) c.focus(); } }
(function(){
  const box=document.getElementById("stat-inf-box"), hb=document.getElementById("btn-help"), hc=document.getElementById("help-close"), tb=document.getElementById("btn-tut");
  if(box){ box.onclick=openHelp; box.onkeydown=e=>{ if(e.key==="Enter"||e.key===" "){ e.preventDefault(); openHelp(); } }; }
  if(hb) hb.onclick=openHelp;
  if(hc) hc.onclick=()=>document.getElementById("modal-help").classList.add("hidden");
  if(window.addEventListener) window.addEventListener("scroll",()=>{ if(tutOn) tutPlace(); },{passive:true});
  if(tb) tb.onclick=()=>{ selectedScenario="bloom"; selectedNature="spore"; DIFF=0.8; MARA=false; CAMP=null; DAILY=null; SEED=null; tutStep=-1; newGame(); startTutorial(); };
})();
const TUT=[
 {sel:"#place-bar",title:"Welcome to VEIL",text:()=>"You steer a spreading pathogen. First choose where it begins: tap a region on the map, then press Start here (or Random).",done:()=>!state.placing},
 {sel:".stat-box.influence",title:"Influence is your currency",text:()=>"You have "+Math.floor(state.influence)+" Influence now, and you earn about +"+incomeNow().toFixed(1)+" every cycle (more as you spread). You spend it to steer mutations. Each button shows its price."},
 {sel:"#mut-actions",view:"mut",title:"Steer a mutation",text:()=>"Buy your first mutation. Bias Concealment (3 Influence) makes you harder to detect. Click it, or press its number key.",done:()=>state.mutCount>=1,tab:"core"},
 {sel:"#btn-advance",title:"Advance a cycle",text:()=>"Time only moves when you press Advance Cycle (or Space). Each cycle you spread, the world reacts, and you earn more Influence.",done:()=>state.turn>=2},
 {sel:".race",title:"The race",text:()=>"Fill your Permanence bar before the Countermeasure bar fills. If the world's bar reaches 100% first, you are erased."},
 {sel:".stat-box.detect",title:"Detection wakes the world",text:()=>"The more the world notices you, the faster it researches a cure and closes borders. Concealment keeps you quiet; raw speed makes you loud. Balance them."},
 {sel:"#mut-tabs",view:"mut",title:"A tree of adaptations",text:()=>"The other tabs hold one-time adaptations. Many need a prerequisite, so plan a path: spread, survive, or hide."},
 {sel:"#map",title:"The map",text:()=>"Tap any region to inspect it. Green glow is presence, blue rings are detection, amber rings are sealed borders. Seed Reservoir plants you in the region you have selected."},
 {sel:"#dock",view:"log",title:"Events and region details",text:()=>"Under the map you will find the details of the region you select and the log of everything that happens: news, world events and your decisions. On a phone, use the Mutate, Region and Events tabs."},
 {sel:null,title:"You're ready",text:()=>"Spend your Influence every cycle, watch the Countermeasure bar, and expect decisions and events. Press Glossary any time to revisit what the numbers mean. Good luck."}
];
function tutEls(){
  let ring=document.getElementById("tut-ring"), card=document.getElementById("tut-card");
  if(!ring){ ring=document.createElement("div"); ring.id="tut-ring"; document.body.appendChild(ring); }
  if(!card){ card=document.createElement("div"); card.id="tut-card"; card.setAttribute("role","dialog"); card.setAttribute("aria-live","polite"); card.setAttribute("aria-label","Tutorial");
    card.innerHTML='<div class="tut-step" id="tut-n"></div><h3 id="tut-t"></h3><p id="tut-p"></p><div class="tut-btns"><button type="button" class="btn-main" id="tut-next"></button><button type="button" class="pillbtn" id="tut-skip">Skip tutorial</button></div>';
    document.body.appendChild(card);
    document.getElementById("tut-next").onclick=()=>tutAdvance();
    document.getElementById("tut-skip").onclick=()=>tutFinish();
  }
  return {ring,card};
}
function tutRender(){
  if(!tutOn) return; const s=TUT[tutStep]; if(!s) return; const {card}=tutEls();
  document.getElementById("tut-n").textContent="Step "+(tutStep+1)+" of "+TUT.length;
  document.getElementById("tut-t").textContent=s.title;
  document.getElementById("tut-p").textContent=s.text();
  document.getElementById("tut-next").textContent=s.done?"Skip step":(tutStep===TUT.length-1?"Finish":"Next");
  card.style.display="block";
}
function tutPlace(){
  if(!tutOn) return; const s=TUT[tutStep], {ring}=tutEls(); const el=s&&s.sel?document.querySelector(s.sel):null;
  const card=document.getElementById("tut-card"); if(!el){ ring.style.display="none"; if(card){ card.style.top=""; card.style.bottom=""; } return; }
  const r=el.getBoundingClientRect(); if(!r.width||!r.height){ ring.style.display="none"; return; }
  if(card&&window.innerWidth>1000){ const low=(r.top+r.height/2)>window.innerHeight*0.55; card.style.bottom=low?"auto":""; card.style.top=low?"92px":""; }
  ring.style.display="block"; ring.style.left=(r.left-6)+"px"; ring.style.top=(r.top-6)+"px"; ring.style.width=(r.width+12)+"px"; ring.style.height=(r.height+12)+"px";
}
function tutGo(i){
  tutStep=i; const s=TUT[i]; if(!s){ tutFinish(); return; }
  if(s.tab&&curTab!==s.tab){ curTab=s.tab; setTimeout(renderAll,0); }
  if(s.view&&typeof setTab==="function") setTab(s.view);
  tutRender();
  const el=s.sel?document.querySelector(s.sel):null; if(el&&el.scrollIntoView){ const tall=el.getBoundingClientRect().height>window.innerHeight*0.45; el.scrollIntoView({block:tall?"start":"center",behavior:"smooth"}); }
  setTimeout(tutPlace,60);
}
function tutAdvance(){ tutGo(tutStep+1); }
function tutFinish(){
  tutOn=false; memTut=true; try{ localStorage.setItem("veil_tut","1"); }catch(e){}
  if(tutTimer){ clearInterval(tutTimer); tutTimer=0; }
  const r=document.getElementById("tut-ring"), c=document.getElementById("tut-card"); if(r) r.style.display="none"; if(c) c.style.display="none";
}
function startTutorial(){
  if(!state) return; tutOn=true; tutEls();
  if(!tutTimer) tutTimer=setInterval(tutPlace,150);
  tutGo(0);
}
function guideTick(){
  if(!state) return;
  const inc=document.getElementById("inc-sub"); if(inc) inc.textContent=state.placing?"":"+"+incomeNow().toFixed(1)+" / cycle";
  const rate=Math.max(0.5,incomeNow());
  document.querySelectorAll("#mut-actions button").forEach(b=>{
    const id=(b.dataset.fk||"").slice(2), m=MUT_OPTIONS.find(x=>x.id===id); if(!m) return;
    const blocked=m.branch==="perk"&&(state.perks[m.id]||(m.req&&!state.perks[m.req])), lacks=state.influence<m.cost;
    b.classList.toggle("afford",!lacks&&!blocked&&!state.placing); b.title="Costs "+m.cost+" Influence";
    let n=b.querySelector(".need"); if(!n){ n=document.createElement("em"); n.className="need"; b.appendChild(n); }
    const more=Math.ceil(m.cost-state.influence), cyc=Math.max(1,Math.ceil((m.cost-state.influence)/rate));
    n.textContent=(lacks&&!blocked&&!state.placing)?" · need "+more+" more (~"+cyc+" cycle"+(cyc>1?"s":"")+")":"";
  });
  if(!tutOn&&tutStep<0&&!window.__autostart&&!tutDone()&&!state.placing===false&&state.turn===1&&state.mutCount===0&&CAMP===null){ startTutorial(); return; }
  if(!tutOn&&tutStep<0&&!window.__autostart&&!tutDone()&&state.turn===1&&state.mutCount===0&&CAMP===null&&document.getElementById("screen-game").classList.contains("active")){ startTutorial(); return; }
  if(tutOn){ const s=TUT[tutStep]; if(s&&s.done&&s.done()){ tutAdvance(); } else tutRender(); }
}
