const TAB_OF={aero:"spread",flyer:"spread",cargo:"spread",urban:"spread",rural:"spread",insect:"spread",water:"spread",rapid:"spread",shell:"survive",memory:"survive",heat:"survive",cold:"survive",drugres:"survive",sleeper:"survive",quiet:"stealth",sabotage:"stealth",whisper:"stealth",camo:"stealth",media:"stealth",infiltrate:"stealth",sealbreak:"stealth"};
const TABS=[["core","Core"],["spread","Spread"],["survive","Survive"],["stealth","Stealth"],["special","Special"]];
let curTab="core";
function tabOf(m){ return m.branch==="perk"?(TAB_OF[m.id]||"special"):"core"; }
function visibleMuts(){ return MUT_OPTIONS.filter(m=>tabOf(m)===curTab); }
function renderTabs(){
  const box=document.getElementById("mut-tabs"); if(!box||!state) return; box.innerHTML="";
  TABS.forEach(([id,label])=>{
    const all=MUT_OPTIONS.filter(m=>tabOf(m)===id), own=all.filter(m=>state.perks&&state.perks[m.id]).length;
    const b=document.createElement("button"); b.type="button"; b.className="pillbtn"+(id===curTab?" on":""); b.dataset.fk="t:"+id;
    b.textContent=label+(id==="core"?"":" "+own+"/"+all.length); b.setAttribute("role","tab"); b.setAttribute("aria-selected",id===curTab?"true":"false");
    b.onclick=()=>{ curTab=id; renderAll(); }; box.appendChild(b);
  });
}
function perkTick(){
  const P=state.perks, sc=state.scenario, nid=state.nature.id;
  state.regions.forEach(r=>{
    if(r.inf>1){
      r.peak=Math.max(r.peak||0,r.inf);
      let g=0;
      if(P.heat&&r.climate==="hot") g+=0.02;
      if(P.cold&&r.climate==="cold") g+=0.02;
      if(P.urban&&r.pop>=15) g+=0.02;
      if(P.rural&&r.pop<15) g+=0.025;
      if(sc.hot&&r.climate==="hot") g+=0.025;
      if(sc.cold&&r.climate==="cold") g+=0.03;
      if(nid==="fungal") g+=r.climate==="hot"?0.03:(r.climate==="cold"?-0.02:0);
      if(nid==="parasite") g+=0.03;
      if(g) r.inf=clamp(r.inf+r.inf*g*(1-Math.min(0.9,r.sealed/130)),0,100);
      if(P.insect&&r.climate==="hot"&&r.links.length&&rnd()<0.35){ const o=state.regions.find(x=>x.id===pick(r.links)); if(o) o.inf=clamp(o.inf+0.9*(r.inf/40),0,100); }
      if(P.water&&r.port&&rnd()<0.3){ const ps=r.links.map(id=>state.regions.find(x=>x.id===id)).filter(x=>x&&x.port); if(ps.length){ const o=pick(ps); o.inf=clamp(o.inf+1.0*(r.inf/40),0,100); } }
    }
    if(P.sleeper&&(r.peak||0)>=3&&r.inf<1.5) r.inf=1.5;
    if(P.sealbreak) r.sealed*=0.9;
  });
  if(P.viralload) state.influence+=1;
  if(P.media&&state.globalDetect>8) state.globalDetect=Math.max(0,state.globalDetect-0.6);
  if(P.infiltrate) state.cure=Math.max(0,state.cure-1);
  if(nid==="synthetic"){ const t=state.traits; t.spread+=0.012; t.resilience+=0.012; t.conceal+=0.008; state.globalDetect=clamp(state.globalDetect+0.5,0,100); }
}
