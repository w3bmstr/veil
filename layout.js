let layoutDone=false, lastSel=null, lastPlacing=false, seenLogTop=null;
function setTab(t){
  const sg=document.getElementById("screen-game"); if(!sg) return; sg.dataset.tab=t;
  document.querySelectorAll("#dock-tabs button").forEach(b=>{ const on=b.dataset.t===t; b.classList.toggle("on",on); b.setAttribute("aria-selected",on?"true":"false"); });
  if(t==="log"){ const l=document.getElementById("log"); seenLogTop=l?l.firstChild:null; const bd=document.getElementById("tab-badge"); if(bd) bd.style.display="none"; }
}
function layoutGame(){
  if(layoutDone||window.__autostart) return;
  const sg=document.getElementById("screen-game"); if(!sg||!sg.querySelector) return;
  const q=s=>sg.querySelector(s), blurb=q(".phase-blurb"), turn=q(".turn-bar"), hud=q(".hud"), race=q(".race"), place=document.getElementById("place-bar"), mapw=q(".map-wrap"), row=q(".row"), adv=q(".actions");
  const pm=row?row.querySelector(":scope > .panel:nth-child(1)"):null, pl=row?row.querySelector(":scope > .panel:nth-child(2)"):null, rt=document.getElementById("region-text"), pr=rt?rt.closest(".panel"):null;
  if(!blurb||!turn||!hud||!race||!mapw||!pm||!pl||!pr||!adv) return;
  layoutDone=true;
  const mk=(tag,id)=>{ const e=document.createElement(tag); if(id) e.id=id; return e; };
  const top=mk("div","topbar"), head=mk("div"); head.className="head"; head.append(blurb,turn); top.append(head,hud,race);
  const main=mk("div","game-main"), L=mk("div","col-left"), Rr=mk("div","col-right"), dock=mk("div","dock"), dt=mk("div","dock-tabs"), ab=mk("div","advance-bar");
  dt.setAttribute("role","tablist"); dt.setAttribute("aria-label","Panels");
  [["mut","Mutate"],["region","Region"],["log","Events"]].forEach(([id,label])=>{ const b=mk("button"); b.type="button"; b.className="pillbtn"+(id==="mut"?" tab-mut":""); b.dataset.t=id; b.setAttribute("role","tab"); b.textContent=label;
    if(id==="log"){ const s=mk("span","tab-badge"); s.textContent=" ●"; s.style.cssText="display:none;color:var(--warn)"; b.append(s); } b.onclick=()=>setTab(id); dt.append(b); });
  pr.id="region-panel"; pl.id="log-panel"; pm.id="mut-panel"; pr.style.marginTop="";
  ab.append(adv); dock.append(place,pr,pl); L.append(mapw,dock); Rr.append(pm,ab); main.append(dt,L,Rr);
  sg.insertBefore(top,sg.firstChild); sg.insertBefore(main,top.nextSibling); if(row&&row.parentNode) row.remove();
  setTab("mut");
  const mq=window.matchMedia("(max-width:1000px)");
  const placeTabs=()=>{ if(mq.matches) ab.insertBefore(dt,ab.firstChild); else main.insertBefore(dt,main.firstChild); };
  placeTabs(); if(mq.addEventListener) mq.addEventListener("change",placeTabs); else if(mq.addListener) mq.addListener(placeTabs);
  const syncTb=()=>{ const st=document.documentElement.style; st.setProperty("--tb",top.offsetHeight+"px"); st.setProperty("--mh",mapw.offsetHeight+"px"); }; syncTb();
  if(typeof ResizeObserver!=="undefined"){ const ro=new ResizeObserver(syncTb); ro.observe(top); ro.observe(mapw); } window.addEventListener("resize",syncTb);
}
function layoutTick(){
  if(!layoutDone||!state) return;
  if(state.placing&&!lastPlacing){ setTab("region"); } if(!state.placing&&lastPlacing){ setTab("mut"); lastSel=selectedRegion; } lastPlacing=!!state.placing;
  if(selectedRegion!==lastSel){ lastSel=selectedRegion; if(!state.placing) setTab("region"); }
  if(typeof sparkTick==="function") sparkTick();
  const sg=document.getElementById("screen-game"), l=document.getElementById("log");
  if(sg&&l&&sg.dataset.tab!=="log"&&l.firstChild!==seenLogTop){ const bd=document.getElementById("tab-badge"); if(bd) bd.style.display="inline"; }
}
setTimeout(layoutGame,0);
