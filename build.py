import re,sys
CURE_K,PURGE_K,CURE_PURGE,PP,PC,PT,JK,EVT_P,AIRK,PORTK=sys.argv[1:11]
SITE=sys.argv[11] if len(sys.argv)>11 else ''
s=open('veil_original.html').read()
def R(old,new,count=1):
    global s
    assert s.count(old)==count,(s.count(old),old[:70])
    s=s.replace(old,new)

# ---- CSS / HTML ----
R('</style>',''':focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.region .rwarn{font-size:.66rem;color:var(--danger);font-weight:700}
</style>''')
R('<div class="log" id="log"></div>','<div class="log" id="log" role="log" aria-live="polite"></div>')
R('<div class="delta" id="delta">','<div class="delta" id="delta" aria-live="polite">')
R('<div class="modal">','<div class="modal" role="dialog" aria-modal="true">',2)
R('<span>· Amber = sealed</span>','<span>· Amber outline = heavily sealed</span><span>· ⚠ = purge risk</span>')
R('<p><strong style="color:var(--text)">Lose</strong> if the countermeasure bar fills while you are still weak, or presence collapses.</p>',
  '<p><strong style="color:var(--text)">Lose</strong> if the countermeasure bar fills before you are permanent, or every reservoir is purged.</p>')
R('Surge is power with a price.</p>','Surge is power with a price. Sealed, detected regions get purged: Resilience softens it, Concealment keeps you off the radar.</p>')

# ---- constants + helpers ----
R('const MUT_OPTIONS=[','const CURE_K=%s, PURGE_K=%s, CURE_PURGE=%s, PP=%s, PC=%s, PT=%s;\nconst MUT_OPTIONS=['%(CURE_K,PURGE_K,CURE_PURGE,PP,PC,PT))
R('function pick(arr){return arr[Math.floor(rnd()*arr.length)]}','''function pick(arr){return arr[Math.floor(rnd()*arr.length)]}
function activatable(el,fn,label){el.tabIndex=0;el.setAttribute("role","button");if(label)el.setAttribute("aria-label",label);el.onclick=fn;el.onkeydown=e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();fn()}}}
function keepFocus(fn){const a=document.activeElement,k=a&&a.dataset?a.dataset.fk:null;fn();if(k){const n=document.querySelector('[data-fk="'+k+'"]');if(n&&!n.disabled)n.focus()}}
function purgeRate(r){
  const press=worldPressure();
  const base=(r.det/100)*(0.4+r.sealed/100)*(r.science/100)*(0.15+press*PURGE_K);
  return clamp(base*(1.35-Math.min(state.traits.resilience,1.6)*0.4),0,0.3);
}''')

# ---- storage fallback ----
R('''function unlockedSet(){
  try{return''','''let memUnlocks=null, memBest=null;
function unlockedSet(){
  if(memUnlocks) return new Set(memUnlocks);
  try{return''')
R('''  try{localStorage.setItem("veil_unlocks",JSON.stringify(["spore","vector","viral","dormant"]))}catch(e){}''',
  '''  memUnlocks=["spore","vector","viral","dormant"];
  try{localStorage.setItem("veil_unlocks",JSON.stringify(memUnlocks))}catch(e){}''')
R('function loadBest(){try{','function loadBest(){if(memBest)return memBest;try{')
R('if(!prev||entry.score>prev.score){try{','if(entry.win&&(!prev||entry.score>prev.score)){memBest=entry;try{')
R('''el.innerHTML=b?("Best score: <strong>"+b.score+"</strong> · "+b.nature+" / "+b.scenario):"Best score: <strong>—</strong>";''',
  '''el.textContent="Best score: ";const bs=document.createElement("strong");bs.textContent=b?String(b.score):"—";el.append(bs);if(b)el.append(" · "+b.nature+" / "+b.scenario);''')

# ---- scoring ----
R('let s=Math.round(pres*12+infectedCount()*9+state.turn*2);','let s=Math.round(pres*12+infectedCount()*9);')
R('if(state.won) s+=220;','if(state.won) s+=220+Math.max(0,46-state.turn)*4;')
R('if(state.scenario.id==="iron") s=','if(state.won&&state.scenario.id==="iron") s=')
R('if(state.scenario.id==="ghost"&&state.globalDetect<38)','if(state.won&&state.scenario.id==="ghost"&&state.globalDetect<38)')

# ---- honest permanence bar ----
R('''  const pres=totalPresence(), crit=criticalPresence(), regions=infectedCount();
  return clamp(pres/40*45 + crit/24*40 + regions/10*15, 0, 100);''','''  const pres=totalPresence(), crit=criticalPresence();
  const fireNeed=state.scenario.id==="fire"?68:74;
  const a=Math.min(pres/PP,crit/PC,state.turn/PT);
  const b=Math.min(pres/fireNeed,state.globalDetect/42);
  return clamp(Math.max(a,b)*100,0,100);''')

# ---- accessible selection screens ----
R('function initScenarioSelect(){\n','function initScenarioSelect(){keepFocus(initScenarioInner)}\nfunction initScenarioInner(){\n')
R('function initNatureSelect(){\n','function initNatureSelect(){keepFocus(initNatureInner)}\nfunction initNatureInner(){\n')
R('card.onclick=()=>{selectedScenario=s.id;$("btn-to-nature").disabled=false;initScenarioSelect()};',
  'card.dataset.fk="s:"+s.id;activatable(card,()=>{selectedScenario=s.id;$("btn-to-nature").disabled=false;initScenarioSelect()},s.name+" scenario");')
R('if(!locked) card.onclick=()=>{selectedNature=n.id;$("btn-confirm-nature").disabled=false;initNatureSelect()};',
  'card.dataset.fk="n:"+n.id;if(!locked) activatable(card,()=>{selectedNature=n.id;$("btn-confirm-nature").disabled=false;initNatureSelect()},n.name+" nature"); else card.setAttribute("aria-disabled","true");')

# ---- render: focus-safe, regions, mutations ----
R('function renderAll(){\n','function renderAll(){keepFocus(renderAllInner)}\nfunction renderAllInner(){\n')
R('''<div class="rdet">${r.det>2?"det "+r.det.toFixed(0)+"%":""}</div></div>`;''','''<div class="rdet">${r.det>2?"det "+r.det.toFixed(0)+"%":""}</div>${(r.inf>1&&purgeRate(r)>0.03)?'<div class="rwarn">⚠ purge</div>':""}</div>`;''')
R('div.onclick=()=>{selectedRegion=r.id;renderAll()};','div.dataset.fk="r:"+r.id;activatable(div,()=>{selectedRegion=r.id;renderAll()},r.name+", presence "+r.inf.toFixed(0)+" percent");')
R('b.className="mut-btn"; b.disabled=state.influence<m.cost;','b.className="mut-btn"; b.dataset.fk="m:"+m.id; b.disabled=state.influence<m.cost;')

# ---- world response: stronger cure + purge ----
R('*(1+press*0.35)*(1-state.traits.resilience*0.15);','*(1+press*0.35)*(1-state.traits.resilience*0.15)*CURE_K;')
R('''  const pres=totalPresence();
  state.influence+=2.5''','''  const purged=[];
  state.regions.forEach(r=>{
    if(r.inf<=0.5) return;
    let rate=purgeRate(r);
    if(state.cure>55) rate+=((state.cure-55)/45)*(r.det/100)*(r.science/100)*CURE_PURGE;
    rate=clamp(rate,0,0.35);
    if(rate>0.004){ const loss=r.inf*rate*(0.7+rnd()*0.6); r.inf=Math.max(0,r.inf-loss); if(loss>1.2) purged.push(r.name); }
  });
  if(purged.length){ log("Purge — "+purged.slice(0,3).join(", ")+".","bad"); }

  const pres=totalPresence();
  state.influence+=2.5''')

# ---- end-condition order + fixes ----
R('''  if(state.cure>=100&&pres<50){ endGame(false,"Countermeasures finished while you were still containable. Erased."); return; }\n''','')
R('''  if(pres<0.3&&state.turn>5){ endGame(false,"Presence collapsed. No reservoirs left."); return; }\n''','')
R('  if(state.turn>46){','''  if(state.cure>=100){ endGame(false,"Countermeasures finished before you were permanent. Erased."); return; }
  if(state.turn>3&&state.regions.every(r=>r.inf<0.5)){ endGame(false,"Every reservoir was purged. Nothing left to steer."); return; }
  if(state.turn>46){''')
R('turn:state.turn,win}','turn:state.turn-1,win}')
R('`Cycles ${state.turn} ·','`Cycles ${state.turn-1} ·')

R('if(crit>=23&&pres>=36&&state.turn>=9&&','if(crit>=PC&&pres>=PP&&state.turn>=PT&&')
R('pres>=34&&state.globalDetect<33&&state.turn>=11','pres>=PP-2&&state.globalDetect<33&&state.turn>=PT+2')
R('if(pres>=28) endGame','if(pres>=PP*0.8) endGame')
R('return clamp(base*(1.35-Math.min(state.traits.resilience,1.6)*0.4),0,0.3);','return clamp(base*(1.35-Math.min(state.traits.resilience,1.6)*0.4)*(state.scenario.id==="ghost"?0.6:1),0,0.3);')

LAND=open('land.json').read()
CSS=""".map-stage{position:relative;aspect-ratio:1504/870;border-radius:12px;overflow:hidden;border:1px solid var(--border);background:radial-gradient(ellipse at 50% 42%,#0e211e 0,#050b0b 78%)}
.map-stage:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(80,200,170,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(80,200,170,.05) 1px,transparent 1px);background-size:6.65% 11.5%}
.map-stage canvas{position:absolute;left:0;top:0}
.routes{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.route{fill:none;stroke:rgba(110,200,230,.28);stroke-width:1.2;stroke-dasharray:5 7;animation:flow 1.6s linear infinite;vector-effect:non-scaling-stroke}
.route.live{stroke:rgba(150,255,190,.7);stroke-width:1.7}
@keyframes flow{to{stroke-dashoffset:-24}}
.fx{position:absolute;aspect-ratio:1;translate:-50% -50%;pointer-events:none}
.fx i{position:absolute;inset:0;border-radius:50%}
.fx .g{background:radial-gradient(circle,rgba(130,255,170,.55) 0,rgba(130,255,170,.18) 38%,transparent 70%);mix-blend-mode:screen;animation:breathe 3.2s ease-in-out infinite}
.fx .d{inset:14%;border:2px solid rgba(90,185,255,.9);box-shadow:0 0 16px rgba(90,185,255,.75),inset 0 0 14px rgba(90,185,255,.35)}
.fx .s{inset:-4%;border:2px dashed rgba(255,180,84,.95);animation:spin 14s linear infinite}
@keyframes breathe{50%{transform:scale(1.14)}}
@keyframes spin{to{transform:rotate(360deg)}}
.map-stage .region{position:absolute;translate:-50% -100%;margin-top:-9px;background:rgba(5,12,12,.8);padding:.18rem .42rem;border-radius:6px;display:flex;gap:.35rem;align-items:center;z-index:3;white-space:nowrap}
.map-stage .region .rname{font-size:.66rem;letter-spacing:.04em;text-transform:uppercase}
.map-stage .region>div:last-child{display:flex;gap:.3rem;align-items:center}
.map-stage .region:after{content:"";position:absolute;left:50%;bottom:-13px;width:9px;height:9px;translate:-50% 0;border-radius:50%;background:#fff;box-shadow:0 0 8px #7cfcb0}
.map-stage .region:hover{transform:scale(1.06)}
.map-stage .region.pulse{animation:hubpulse .5s}
@keyframes hubpulse{40%{transform:scale(1.18);box-shadow:0 0 18px rgba(130,255,170,.8)}}
@media(max-width:640px){.map-stage .region .rname,.map-stage .region .rdet{display:none}.map-stage .region.selected .rname{display:block}}
@media(prefers-reduced-motion:reduce){.route,.fx .g,.fx .s{animation:none}}
"""
JS=r"""const LAND=__LAND__;
const landCanvas=document.createElement("canvas"); let landRAF=0;
const calm=window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches;
function drawLand(){
  const w=$("map").clientWidth; if(typeof w!=="number"||!w||!state) return;
  const h=w*870/1504, dpr=Math.min(window.devicePixelRatio||1,2), c=landCanvas;
  if(c.width!==Math.round(w*dpr)){c.width=Math.round(w*dpr);c.height=Math.round(h*dpr);c.style.width=w+"px";c.style.height=h+"px"}
  const g=c.getContext("2d"); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,w,h);
  const k=w/1504, t=performance.now()/1000;
  for(let n=0;n<LAND.length;n+=3){
    const ri=LAND[n+2], r=state.regions[ri], b=BASE[ri], f=clamp(r.inf/55,0,1);
    const tw=(f>0&&!calm)?0.86+0.14*Math.sin(t*2+LAND[n]*0.7+LAND[n+1]*0.45):1;
    g.fillStyle="rgba("+((b[0]+(130-b[0])*f)|0)+","+((b[1]+(255-b[1])*f)|0)+","+((b[2]+(170-b[2])*f)|0)+","+((0.3+0.7*f)*tw).toFixed(2)+")";
    g.beginPath(); g.arc((LAND[n]*10+5)*k,(LAND[n+1]*10+5)*k,Math.max(0.8,(2.2+1.8*f)*k),0,6.283); g.fill();
  }
}
function landLoop(){ landRAF=1; if(!calm&&$("screen-game").classList.contains("active")) drawLand(); setTimeout(()=>requestAnimationFrame(landLoop),60); }
if(window.addEventListener) window.addEventListener("resize",drawLand);
""".replace("__LAND__",LAND)
R('</style>',CSS+'</style>')
R('<div class="map-grid" id="map"></div>','<div class="map-stage" id="map"></div>')
R('World — brighter = higher presence','World — green glow = presence · blue = detection · amber = sealed')
R('<span>Tap region for detail</span><span>· Amber outline = heavily sealed</span>','<span>Tap a hub for detail</span><span>· Green glow = presence</span><span>· Blue ring = detected</span><span>· Amber ring = sealed</span>')
R('function activatable(el,fn,label)',JS+'function activatable(el,fn,label)')
R('''const map=$("map"); map.innerHTML="";
  state.regions.forEach(r=>{
    const div=document.createElement("div");
    div.className="region lvl"+lvl(r.inf)''','''const map=$("map"); map.innerHTML=""; map.appendChild(landCanvas);
  const seen={}; let sv='<svg class="routes" viewBox="0 0 1504 870" preserveAspectRatio="none" aria-hidden="true">';
  state.regions.forEach(r=>r.links.forEach(l=>{const k=[r.id,l].sort().join();if(seen[k])return;seen[k]=1;const o=state.regions.find(x=>x.id===l),a=HUB[r.id],b=HUB[l],mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2-Math.hypot(b[0]-a[0],b[1]-a[1])*0.18;sv+='<path class="route'+((r.inf>1||o.inf>1)?" live":"")+'" d="M'+a[0]+" "+a[1]+"Q"+mx+" "+my+" "+b[0]+" "+b[1]+'"/>';}));
  map.insertAdjacentHTML("beforeend",sv+"</svg>");
  state.regions.forEach(r=>{
    const px=HUB[r.id][0]/15.04, py=HUB[r.id][1]/8.70;
    const fx=document.createElement("div"); fx.className="fx"; fx.style.cssText="left:"+px+"%;top:"+py+"%;width:"+(7+r.pop/20)+"%";
    fx.innerHTML='<i class="g" style="opacity:'+clamp(r.inf/55,0,1)+';scale:'+(0.55+r.inf/160)+'"></i><i class="d" style="opacity:'+clamp(r.det/70,0,1)+'"></i><i class="s" style="opacity:'+(r.sealed>15?clamp(r.sealed/80,0.25,1):0)+'"></i>';
    map.appendChild(fx);
    const div=document.createElement("div");
    div.style.left=px+"%"; div.style.top=py+"%";
    div.className="region hub lvl"+lvl(r.inf)''')
R('map.appendChild(div);\n  });','map.appendChild(div);\n  });\n  if(!landRAF) landLoop(); drawLand();')

R('.map-stage{position:relative;','.map-stage{container-type:inline-size;position:relative;')
R('@media(max-width:640px){.map-stage .region .rname,.map-stage .region .rdet{display:none}.map-stage .region.selected .rname{display:block}}',
  '@container (max-width:780px){.map-stage .region .rname,.map-stage .region .rdet{display:none}.map-stage .region.selected .rname{display:block}}\n.fx .p{border:2px solid rgba(255,90,90,.95);box-shadow:0 0 18px rgba(255,90,90,.8);animation:ping .9s ease-out forwards}\n@keyframes ping{from{transform:scale(.4);opacity:1}to{transform:scale(1.3);opacity:0}}')
R('@media(prefers-reduced-motion:reduce){.route,.fx .g,.fx .s{animation:none}}','@media(prefers-reduced-motion:reduce){.route,.fx .g,.fx .s,.fx .p{animation:none}}')
R('''+'"></i>';
    map.appendChild(fx);''','''+'"></i>'+((state.purgedNow||[]).includes(r.name)?'<i class="p"></i>':"");
    map.appendChild(fx);''')
R('if(purged.length){ log(','state.purgedNow=purged.slice(); if(purged.length){ log(')
R('div.dataset.fk="r:"+r.id;activatable(','div.title=r.name+" · presence "+r.inf.toFixed(0)+"% · detected "+r.det.toFixed(0)+"% · sealed "+r.sealed.toFixed(0)+"%";div.dataset.fk="r:"+r.id;activatable(')
R('Routes: ${sel.links.map(regionName).join(", ")}<br>','Routes: ${sel.links.map(regionName).join(", ")}<br>\n      Purge risk: ${(purgeRate(sel)*100).toFixed(0)}% / cycle<br>')

R('const landCanvas=document.createElement("canvas"); let landRAF=0;','''const landCanvas=document.createElement("canvas"); let landRAF=0, hoverRi=-1;
const LG=new Map(); for(let n=0;n<LAND.length;n+=3) LG.set(LAND[n]*1000+LAND[n+1],LAND[n+2]);
function landAt(e){
  const rc=landCanvas.getBoundingClientRect(); if(!rc.width) return -1;
  const x=(e.clientX-rc.left)/rc.width*1504, y=(e.clientY-rc.top)/rc.height*870, c=Math.floor(x/10), r=Math.floor(y/10);
  let best=-1, bd=1e9;
  for(let dc=-1;dc<=1;dc++)for(let dr=-1;dr<=1;dr++){const v=LG.get((c+dc)*1000+r+dr); if(v!==undefined){const d=((c+dc)*10+5-x)**2+((r+dr)*10+5-y)**2; if(d<bd){bd=d;best=v}}}
  return bd<=400?best:-1;
}
if(landCanvas.addEventListener){
  landCanvas.addEventListener("mousemove",e=>{const v=landAt(e); if(v!==hoverRi){hoverRi=v; landCanvas.style.cursor=v>=0?"pointer":"default"; landCanvas.title=(v>=0&&state)?state.regions[v].name:""; drawLand();}});
  landCanvas.addEventListener("mouseleave",()=>{hoverRi=-1; drawLand();});
  landCanvas.addEventListener("click",e=>{const v=landAt(e); if(v>=0&&state){selectedRegion=state.regions[v].id; renderAll();}});
}''')
R('const ri=LAND[n+2], r=state.regions[ri], b=BASE[ri], f=clamp(r.inf/55,0,1);','const ri=LAND[n+2], r=state.regions[ri], b=BASE[ri], f=clamp(r.inf/55,0,1), q=(ri===hoverRi||r.id===selectedRegion)?0.4:0;')
R('''g.fillStyle="rgba("+((b[0]+(130-b[0])*f)|0)+","+((b[1]+(255-b[1])*f)|0)+","+((b[2]+(170-b[2])*f)|0)+","+((0.3+0.7*f)*tw).toFixed(2)+")";''','''const cr=b[0]+(130-b[0])*f, cg=b[1]+(255-b[1])*f, cb=b[2]+(170-b[2])*f;
    g.fillStyle="rgba("+((cr+(255-cr)*q)|0)+","+((cg+(255-cg)*q)|0)+","+((cb+(255-cb)*q)|0)+","+Math.min(1,(0.3+0.7*f)*tw+q*0.5).toFixed(2)+")";''')
R('Math.max(0.8,(2.2+1.8*f)*k),0,6.283)','Math.max(0.8,(2.2+1.8*f)*k*(1+q*0.35)),0,6.283)')
R('const target=weak[0]||pick(state.regions);','const picked=state.regions.find(r=>r.id===selectedRegion&&r.inf<12); const target=picked||weak[0]||pick(state.regions);')
R('desc:"Foothold in a weak region"','desc:"Foothold in the selected region (if weak)"')
R('"Open corridors"}`;','"Open corridors"}${sel.inf<12?`<br><span style="color:var(--accent)">Seed Reservoir will target this region</span>`:""}`;')

R('</style>','.diffbtn{background:var(--panel);border:1px solid var(--border);color:var(--muted);padding:.4rem .85rem;border-radius:8px;cursor:pointer;margin:0 .2rem;font:inherit}.diffbtn.on{border-color:var(--accent);color:var(--text)}\n</style>')
R('<div><button class="btn-main" id="btn-start">','<div id="diff-row" role="group" aria-label="Difficulty" style="margin:.2rem 0 .9rem"><button class="diffbtn" data-d="0.8">Casual</button><button class="diffbtn on" data-d="1">Normal</button><button class="diffbtn" data-d="1.25">Brutal</button></div>\n      <div><button class="btn-main" id="btn-start">')
R('function activatable(el,fn,label)','''let DIFF=1;
document.querySelectorAll(".diffbtn").forEach(b=>{b.onclick=()=>{DIFF=+b.dataset.d;document.querySelectorAll(".diffbtn").forEach(x=>x.classList.toggle("on",x===b))}});
function activatable(el,fn,label)''')
R('*CURE_K;','*CURE_K*DIFF*(state.perks.sabotage?0.78:1);')
R('const base=(r.det/100)*(0.4+r.sealed/100)*(r.science/100)*(0.15+press*PURGE_K);','const base=(r.det/100)*(0.4+r.sealed/100)*(r.science/100)*(0.15+press*PURGE_K)*DIFF;')
R('if(state.won) s+=220+Math.max(0,46-state.turn)*4;','if(state.won) s+=220+Math.max(0,46-state.turn)*4;\n  s=Math.round(s*(DIFF>1?1.25:DIFF<1?0.85:1));')
R('regions:REGIONS.map(r=>({...r,inf:r.id===startId?base:0,det:0,sealed:0})),','perks:{}, flags:{}, everPurged:false,\n    regions:REGIONS.map(r=>({...r,inf:r.id===startId?base:0,det:0,sealed:0})),')
R('branch:"seed",trade:"May draw local eyes"}','''branch:"seed",trade:"May draw local eyes"},
  {id:"quiet",name:"Silent Carriers",cost:6,desc:"Permanent concealment boost",branch:"perk",trade:"One-time adaptation"},
  {id:"shell",name:"Hardened Shell",cost:6,desc:"Permanent resilience boost",branch:"perk",trade:"One-time adaptation"},
  {id:"memory",name:"Host Memory",cost:6,desc:"Locks your form, far less drift",branch:"perk",trade:"One-time adaptation"},
  {id:"aero",name:"Aerosol Hops",cost:7,desc:"Faster spread everywhere",branch:"perk",req:"shell",trade:"One-time adaptation"},
  {id:"sabotage",name:"Cure Sabotage",cost:9,desc:"Counter −12 and 22% slower research",branch:"perk",req:"quiet",trade:"One-time adaptation"},
  {id:"whisper",name:"Border Whispers",cost:8,desc:"Seals erode faster every cycle",branch:"perk",req:"aero",trade:"One-time adaptation"}''')
R('} else if(m.branch==="seed"){','''} else if(m.branch==="perk"){
    state.perks[m.id]=true;
    if(m.id==="quiet") state.traits.conceal=clamp(state.traits.conceal+0.45,0.35,2.8);
    if(m.id==="shell") state.traits.resilience=clamp(state.traits.resilience+0.4,0.4,2.8);
    if(m.id==="aero") state.traits.spread+=0.3;
    if(m.id==="memory") state.stability=clamp(state.stability+0.3,0.12,1);
    if(m.id==="sabotage") state.cure=Math.max(0,state.cure-12);
    log("Adaptation acquired — "+m.name+".","good"); toast(m.name); beep(587,0.06);
  } else if(m.branch==="seed"){''')
R('b.disabled=state.influence<m.cost;','b.disabled=state.influence<m.cost||(m.branch==="perk"&&(state.perks[m.id]||(m.req&&!state.perks[m.req])));')
R('MUT_OPTIONS.forEach(m=>{','MUT_OPTIONS.forEach((m,mi)=>{')
R('b.innerHTML=`<strong>${m.name}</strong><span>${m.desc}<br>','b.innerHTML=`<strong>${mi<9?(mi+1)+". ":""}${state.perks[m.id]?"✓ ":""}${m.name}</strong><span>${m.desc}${m.req&&!state.perks[m.req]?" · needs "+MUT_OPTIONS.find(x=>x.id===m.req).name:""}<br>')
R('  const pres=totalPresence();\n  state.influence+=2.5','''  state.flags=state.flags||{};
  const ms=(k,txt,cls)=>{ if(!state.flags[k]){ state.flags[k]=1; log("NEWS — "+txt,cls||"warn"); toast(txt); } };
  if(purged.length) state.everPurged=true;
  if(state.perks.whisper) state.regions.forEach(r=>{ r.sealed*=0.93; });
  const nInf=infectedCount();
  if(nInf>=3) ms("n3","Cases appear in three regions at once.");
  if(nInf>=8) ms("n8","Officials call it a global event.");
  if(nInf>=15) ms("n15","Every region reports cases.","bad");
  if(state.globalDetect>=15) ms("d15","Health agencies flag an unexplained cluster.");
  if(state.globalDetect>=45) ms("d45","Emergency briefings begin worldwide.","bad");
  if(state.cure>=25) ms("c25","Labs share a first promising lead.");
  if(state.cure>=50) ms("c50","Trials begin. Governments fund a rush program.","bad");
  if(state.cure>=75) ms("c75","Mass production is being prepared.","bad");
  const hardSeal=state.regions.find(r=>r.sealed>60); if(hardSeal) ms("s60","Borders close around "+hardSeal.name+".");
  if(purged.length) ms("p1","The first purge succeeds in "+purged[0]+".","bad");
  const pres=totalPresence();
  state.influence+=2.5''')
R('showTitleBest(); show("screen-end");','''const ach=[], gotA=(t,c)=>{ if(c) ach.push(t); };
  gotA("Ghost: won under 30% detection",win&&state.globalDetect<30);
  gotA("Sprinter: permanent by cycle 20",win&&state.turn-1<=20);
  gotA("Untouchable: won with zero purges",win&&!state.everPurged);
  gotA("Pandemic: reached all 15 regions",infectedCount()>=15);
  gotA("Against the Odds: won with Counter above 70%",win&&state.cure>70);
  gotA("Fully Adapted: owned every adaptation",["quiet","shell","aero","memory","sabotage","whisper"].every(k=>state.perks[k]));
  gotA("Brutal: won on Brutal difficulty",win&&DIFF>1);
  if(ach.length) $("end-stats").textContent+=" · Achievements: "+ach.join("; ");
  showTitleBest(); show("screen-end");''')

import json as _j
RJ=open('regions.json',encoding='utf8').read(); NR=len(_j.loads(RJ))
_i=s.index('const REGIONS=['); _j2=s.index('\n];',_i)+3
s=s[:_i]+'const REGIONS='+RJ+';\nconst HUB=Object.fromEntries(REGIONS.map(r=>[r.id,r.hub]));\nconst BASE=REGIONS.map(r=>r.col);\n'+s[_j2:]
R('const MUT_OPTIONS=[','const RS=%s, JK=%s, EVT_P=%s;\nconst MUT_OPTIONS=['%(15/NR,JK,EVT_P))
R('infectedCount()*0.12','infectedCount()*0.12*RS')
R('detectGain+=r.det*(r.science/100)*0.024;','detectGain+=r.det*(r.science/100)*0.024*RS;')
R('(r.science/100)*(r.det/100)*0.45,0)','(r.science/100)*(r.det/100)*0.45*RS,0)')
R('const jump=(r.inf/100)*(other.open/100)*2.4*','const jump=(r.inf/100)*(other.open/100)*2.4*JK*')
R('if(nInf>=3) ms("n3","Cases appear in three regions at once.");','if(nInf>=Math.ceil(REGIONS.length*0.2)) ms("n3","Cases are now turning up in many places at once.");')
R('if(nInf>=8) ms("n8"','if(nInf>=Math.ceil(REGIONS.length*0.5)) ms("n8"')
R('if(nInf>=15) ms("n15","Every region reports cases.","bad");','if(nInf>=REGIONS.length-2) ms("n15","Nearly every region reports cases.","bad");')
R('gotA("Pandemic: reached all 15 regions",infectedCount()>=15);','gotA("Pandemic: reached nearly every region",infectedCount()>=REGIONS.length-2);')
R('${infectedCount()}/15 regions','${infectedCount()}/${REGIONS.length} regions')
R('(7+r.pop/20)','(4.5+r.pop/12)')
R('div.className="region hub lvl"+lvl(r.inf)','div.className="region hub lvl"+lvl(r.inf)+((r.inf<0.5&&r.id!==selectedRegion)?" zero":"")')
R('</style>','.map-stage .region.zero{padding:0;width:13px;height:13px;min-width:0;translate:-50% -50%;margin-top:0;border-radius:50%;background:rgba(220,255,240,.12);border:1px solid rgba(220,255,240,.35)}.map-stage .region.zero>*{display:none}.map-stage .region.zero:after{display:none}.route:not(.live){display:none}\n</style>')
R('perks:{}, flags:{}, everPurged:false,','perks:{}, flags:{}, everPurged:false, cureSlow:0, lastEvent:0,')
R('(state.perks.sabotage?0.78:1);','(state.perks.sabotage?0.78:1)*(state.cureSlow>0?0.5:1);')
EVJS=open('events.js',encoding='utf8').read()
R('function activatable(el,fn,label)',EVJS+'function activatable(el,fn,label)')
R('if(purged.length) ms("p1","The first purge succeeds in "+purged[0]+".","bad");','''if(purged.length) ms("p1","The first purge succeeds in "+purged[0]+".","bad");
  if(state.cureSlow>0) state.cureSlow--;
  if(state.turn>=4&&state.turn-(state.lastEvent||0)>=3&&rnd()<EVT_P){ const pool=EVENTS.filter(e=>e.w()); if(pool.length){ state.lastEvent=state.turn; pick(pool).run(); } }''')

SYS=open('systems.js',encoding='utf8').read().replace('%AIRK%',AIRK).replace('%PORTK%',PORTK)
R('function activatable(el,fn,label)',SYS+'function activatable(el,fn,label)')
R('<div class="modal-bg hidden" id="modal-how">','<div class="modal-bg hidden" id="modal-choice"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="choice-title"><h2 id="choice-title"></h2><p id="choice-text"></p><div id="choice-opts"></div></div></div>\n<div class="modal-bg hidden" id="modal-how">')
R('<div id="diff-row"','<div><button class="diffbtn" id="btn-resume" style="display:none;margin-bottom:.6rem">Resume saved run</button></div>\n      <div id="diff-row"')
R('</style>','#choice-opts button{display:block;width:100%;text-align:left;margin:.5rem 0;padding:.65rem .9rem;border-radius:10px}#choice-opts span{color:var(--muted);font-size:.85rem}.flight{fill:none;stroke:#bfffe0;stroke-width:2.2;stroke-dasharray:2400;stroke-dashoffset:2400;animation:fly 1.5s ease-out forwards;vector-effect:non-scaling-stroke;filter:drop-shadow(0 0 4px #7cfcb0)}.flight.sea{stroke:#7fd0ff;stroke-dasharray:8 6;stroke-dashoffset:0;animation:fade 2.4s ease-out forwards}@keyframes fly{to{stroke-dashoffset:0}}@keyframes fade{from{opacity:1}to{opacity:.15}}@media(prefers-reduced-motion:reduce){.flight{animation:none;stroke-dashoffset:0}}\n</style>')
R('  if(!state||state.dead||state.won) return;\n  if(tipStep===1)','  if(!state||state.dead||state.won||state.choiceId) return;\n  if(tipStep===1)')
R('  if(n.id==="vector"&&rnd()<0.3){','  airSea(n,press,grew);\n  if(n.id==="vector"&&rnd()<0.3){')
R('if(pool.length){ state.lastEvent=state.turn; pick(pool).run(); } }','if(pool.length){ state.lastEvent=state.turn; pick(pool).run(); } }\n  maybeChoice();')
R('  const pres=totalPresence();\n  state.influence+=2.5','  const pres=totalPresence();\n  (state.hist=state.hist||[]).push({t:state.turn,p:pres,d:state.globalDetect,c:state.cure,n:infectedCount()});\n  state.influence+=2.5')
R('state.flags[k]=1; log("NEWS — "+txt,cls||"warn");','state.flags[k]=1; (state.marks=state.marks||[]).push({t:state.turn,x:txt}); log("NEWS — "+txt,cls||"warn");')
R('branch:"perk",req:"aero",trade:"One-time adaptation"}','branch:"perk",req:"aero",trade:"One-time adaptation"}',2) if False else None
R('{id:"whisper",name:"Border Whispers",cost:8,desc:"Seals erode faster every cycle",branch:"perk",req:"aero",trade:"One-time adaptation"}','{id:"whisper",name:"Border Whispers",cost:8,desc:"Seals erode faster every cycle",branch:"perk",req:"aero",trade:"One-time adaptation"},\n  {id:"flyer",name:"Frequent Flyers",cost:7,desc:"Long-haul flight seeding 70% stronger",branch:"perk",req:"aero",trade:"One-time adaptation"},\n  {id:"cargo",name:"Cargo Stowaways",cost:7,desc:"Ship seeding stronger; airport closures less likely",branch:"perk",req:"shell",trade:"One-time adaptation"}')
R('["quiet","shell","aero","memory","sabotage","whisper"].every','["quiet","shell","aero","memory","sabotage","whisper","flyer","cargo"].every')
R('Purge risk: ${(purgeRate(sel)*100).toFixed(0)}% / cycle<br>','Purge risk: ${(purgeRate(sel)*100).toFixed(0)}% / cycle<br>\n      Airport: ${sel.air?(sel.airClosed>0?"closed ("+sel.airClosed+")":"open"):"none"} · Port: ${sel.port?(sel.portClosed>0?"closed ("+sel.portClosed+")":"open"):"none"}<br>')
R('map.insertAdjacentHTML("beforeend",sv+"</svg>");','sv+=(state.flights||[]).map(f=>{const a=HUB[f.a],b=HUB[f.b],mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2-Math.hypot(b[0]-a[0],b[1]-a[1])*0.28;return \'<path class="flight \'+f.k+\'" d="M\'+a[0]+" "+a[1]+"Q"+mx+" "+my+" "+b[0]+" "+b[1]+\'"/>\'}).join("");\n  map.insertAdjacentHTML("beforeend",sv+"</svg>");')
R('function renderAll(){keepFocus(renderAllInner)}','function renderAll(){keepFocus(renderAllInner); saveGame()}')
R('if(ach.length) $("end-stats").textContent+=" · Achievements: "+ach.join("; ");','''{ const S=loadStats(); S.games++; if(win){ S.wins++; S.fastest=S.fastest?Math.min(S.fastest,state.turn-1):state.turn-1; }
    const fresh=ach.filter(a=>!S.ach[a]); ach.forEach(a=>{S.ach[a]=1}); saveStats(S);
    if(ach.length) $("end-stats").textContent+=" · Achievements: "+ach.map(a=>(fresh.includes(a)?"★ ":"")+a).join("; "); }''')
R('showTitleBest(); show("screen-end");','drawRecap(); clearSave(); showTitleBest(); show("screen-end");')
R('if(b)el.append(" · "+b.nature+" / "+b.scenario);','if(b)el.append(" · "+b.nature+" / "+b.scenario); el.append(" · "+statLine()); { const rb=$("btn-resume"); if(rb) rb.style.display=loadSave()?"":"none"; }')

SYS2=open('systems2.js',encoding='utf8').read()
R('function activatable(el,fn,label)',SYS2+'function activatable(el,fn,label)')
R('<div class="modal-bg hidden" id="modal-how">','<div class="modal-bg hidden" id="modal-camp"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="camp-title"><h2 id="camp-title">Campaign: The Long Quiet</h2><p>Five linked chapters. Win to unlock the next and carry up to two adaptations forward.</p><div id="camp-list"></div><button class="btn-main" style="width:100%;margin-top:1rem" id="camp-close">Close</button></div></div>\n<div class="modal-bg hidden" id="modal-how">')
R('<div><button class="diffbtn" id="btn-resume"','<div><button class="pillbtn" id="btn-camp" style="margin-bottom:.6rem">Campaign</button></div>\n      <div id="len-row" role="group" aria-label="Run length" style="margin:.2rem 0 .6rem"><button class="pillbtn lenbtn on" data-m="0">Standard run</button><button class="pillbtn lenbtn" data-m="1">Marathon</button></div>\n      <div><button class="diffbtn" id="btn-resume"')
R('</style>','.pillbtn{background:var(--panel);border:1px solid var(--border);color:var(--muted);padding:.4rem .85rem;border-radius:8px;cursor:pointer;margin:0 .2rem;font:inherit}.pillbtn.on{border-color:var(--accent);color:var(--text)}#camp-list button{display:block;width:100%;text-align:left;margin:.5rem 0;padding:.65rem .9rem}#camp-list span{color:var(--muted);font-size:.85rem}.pillbtn[aria-disabled=true]{opacity:.5;cursor:not-allowed}\n</style>')
R('const localGrowth=r.inf*0.09*n.spread','const localGrowth=r.inf*0.09*(MARA?0.55:1)*n.spread')
R('*2.4*JK*','*2.4*JK*(MARA?0.55:1)*')
R('*CURE_K*DIFF*','*CURE_K*DIFF*(MARA?0.3:1)*')
R('(0.15+press*PURGE_K)*DIFF;','(0.15+press*PURGE_K)*DIFF*(MARA?0.6:1);')
R('state.turn>=PT&&(sc.id','state.turn>=PTn()&&(sc.id')
R('state.turn>=PT+2','state.turn>=PTn()+2')
R('state.turn/PT)','state.turn/PTn())')
R('if(state.turn>46){','if(state.turn>(MARA?90:46)){')
R('Math.max(0,46-state.turn)','Math.max(0,(MARA?90:46)-state.turn)')
R('s=Math.round(s*(DIFF>1?1.25:DIFF<1?0.85:1));','s=Math.round(s*(DIFF>1?1.25:DIFF<1?0.85:1));\n  if(MARA) s=Math.round(s*1.4);')
R('const pool=EVENTS.filter(e=>e.w()); if(pool.length){ state.lastEvent=state.turn; pick(pool).run(); }','const pool=EVENTS.filter((e,i)=>e.w()&&((state.evCount&&state.evCount[i])||0)<2&&i!==state.lastEvIdx); if(pool.length){ state.lastEvent=state.turn; const ev=pool[Math.floor(rnd()*pool.length)], ix=EVENTS.indexOf(ev); (state.evCount=state.evCount||{})[ix]=(state.evCount[ix]||0)+1; state.lastEvIdx=ix; ev.run(); }')
R('gotA("Brutal: won on Brutal difficulty",win&&DIFF>1);','gotA("Brutal: won on Brutal difficulty",win&&DIFF>1);\n  gotA("Marathoner: won a Marathon run",win&&MARA);')
R('ach.map(a=>(fresh.includes(a)?"★ ":"")+a).join("; "); }','ach.map(a=>(fresh.includes(a)?"★ ":"")+a).join("; "); }\n  campaignEnd(win);')

SYS3=open('systems3.js',encoding='utf8').read()
R('function activatable(el,fn,label)',SYS3+'function activatable(el,fn,label)')
R('b.onclick=()=>{DIFF=+b.dataset.d;','b.onclick=()=>{if(b.getAttribute("aria-disabled")==="true"||!b.dataset.d)return;DIFF=+b.dataset.d;')
R('function show(id){document.querySelectorAll(".screen").forEach(s=>s.classList.remove("active"));$(id).classList.add("active")}','function show(id){document.querySelectorAll(".screen").forEach(s=>s.classList.remove("active"));$(id).classList.add("active");if(typeof refreshLocks==="function")refreshLocks()}')
R('if(rb) rb.style.display=loadSave()?"":"none"; }','if(rb) rb.style.display=loadSave()?"":"none"; refreshLocks(); }')
R('<p class="unlocks" id="unlock-note">','<p><button class="pillbtn" id="btn-reset" style="font-size:.75rem">Reset progress</button></p>\n      <p class="unlocks" id="unlock-note">')
R('card.className="scenario-card"+(selectedScenario===s.id?" selected":"");','const lockS=!scUnlocked(s.id); card.className="scenario-card"+(selectedScenario===s.id?" selected":"")+(lockS?" locked":"");')
R('card.innerHTML=`<h3>${s.name}</h3><p>${s.blurb}</p><div class="stat">${s.stat}</div>`;','card.innerHTML=`<h3>${s.name}${lockS?" 🔒":""}</h3><p>${lockS?"Win "+SC_REQ[s.id]+" run"+(SC_REQ[s.id]>1?"s":"")+" to unlock.":s.blurb}</p><div class="stat">${s.stat}</div>`;')
R('card.dataset.fk="s:"+s.id;activatable(card,()=>{selectedScenario=s.id;$("btn-to-nature").disabled=false;initScenarioSelect()},s.name+" scenario");','card.dataset.fk="s:"+s.id;if(!lockS) activatable(card,()=>{selectedScenario=s.id;$("btn-to-nature").disabled=false;initScenarioSelect()},s.name+" scenario"); else card.setAttribute("aria-disabled","true");')
R('for(let n=0;n<LAND.length;n+=3) LG.set(LAND[n]*1000+LAND[n+1],LAND[n+2]);','for(let n=0;n<LAND.length;n+=3) LG.set(LAND[n]*1000+LAND[n+1],LAND[n+2]);\nconst EDGE=new Uint8Array(LAND.length/3); for(let n=0;n<LAND.length;n+=3){ for(const [dc,dr] of [[1,0],[-1,0],[0,1],[0,-1]]){ const v=LG.get((LAND[n]+dc)*1000+LAND[n+1]+dr); if(v!==undefined&&v!==LAND[n+2]){EDGE[n/3]=1;break} } }')
R('(0.3+0.7*f)*tw+q*0.5','((0.5+0.5*f)*tw+q*0.5)*(EDGE[n/3]?0.55:1)')
R('Math.max(0.8,(2.2+1.8*f)*k*(1+q*0.35))','Math.max(1.1,(2.6+1.6*f)*k*(1+q*0.35))')
R('</style>','''.scenario-card.locked,.pillbtn.locked,.diffbtn.locked{opacity:.5;cursor:not-allowed}
.map-stage .region{display:flex!important;flex-direction:row!important;align-items:center;gap:.3rem;min-height:0!important;height:auto!important;width:auto!important;padding:.1rem .4rem!important;margin:0!important;translate:-50% -50%!important;border-radius:999px!important;background:rgba(6,14,13,.88)!important;border:1px solid rgba(160,255,200,.55);font-size:.64rem;line-height:1.2;z-index:3;transition:transform .15s}
.map-stage .region:after{display:none!important}
.map-stage .region .rname,.map-stage .region .rdet{display:none}
.map-stage .region>div:last-child{display:flex;gap:.25rem;align-items:center}
.map-stage .region .rpct{color:#eafff4;font-weight:700;font-size:.66rem}
.map-stage .region:hover,.map-stage .region:focus-visible,.map-stage .region.selected{z-index:12;transform:scale(1.08)}
.map-stage .region:hover .rname,.map-stage .region:focus-visible .rname,.map-stage .region.selected .rname,.map-stage .region:hover .rdet,.map-stage .region.selected .rdet{display:block}
.map-stage .region .rname{white-space:nowrap;font-weight:700;letter-spacing:.03em}
.map-stage .region.lvl2{border-color:#b6e64f}.map-stage .region.lvl3{border-color:#ffd54f}.map-stage .region.lvl4{border-color:#ff8a50}
.map-stage .region.zero{width:10px!important;height:10px!important;padding:0!important;background:rgba(200,255,230,.3)!important;border:1px solid rgba(200,255,230,.6)!important}
.map-stage .region.zero>*{display:none!important}
.map-stage .region.zero:hover{transform:scale(1.5)}
.flight{stroke-width:1.6;filter:none;opacity:.9;animation:fly 1.2s ease-out forwards,fade 3.2s ease-in 1s forwards}
</style>''')
R('div.className="region hub lvl"+lvl(r.inf)+((r.inf<0.5&&r.id!==selectedRegion)?" zero":"")','div.className="region hub lvl"+lvl(r.inf)+((r.inf<0.5&&r.id!==selectedRegion)?" zero":"")+(px>74?" edge-r":px<22?" edge-l":"")')
R('</style>','.map-stage .region.edge-r{translate:-86% -50%!important}.map-stage .region.edge-l{translate:-14% -50%!important}@container (max-width:520px){.map-stage .region .rname{font-size:.56rem}.map-stage .region{font-size:.58rem}}\n</style>')

R('</style>','@media(max-width:640px){.shell{padding:.45rem .35rem 2.5rem}.map-wrap{margin-left:-.35rem;margin-right:-.35rem;padding:.35rem 0;border-left:0;border-right:0;border-radius:0}.map-stage{border-radius:0;border-left:0;border-right:0}.panel{padding:.7rem .65rem}.map-title,.legend{padding:0 .7rem}.end-box{padding:1.3rem .9rem}.modal{width:calc(100vw - 1rem)!important;max-width:none!important}}\n</style>')

SYS4=open('systems4.js',encoding='utf8').read()
R('function activatable(el,fn,label)',SYS4+'function activatable(el,fn,label)')
R('const startId=pick(REGIONS).id;','const startId=pick(REGIONS).id; const placing=!window.__autostart;')
R('inf:r.id===startId?base:0,det:0,sealed:0})),','inf:(!placing&&r.id===startId)?base:0,det:0,sealed:0})),')
R('origin:startId,dead:false','placing, pendingBase:base, origin:placing?null:startId,dead:false')
R('log("Pattern active in "+regionName(startId)+".","sys");','if(placing) log("Choose where the pattern begins.","sys"); else log("Pattern active in "+regionName(startId)+".","sys");')
R('<div class="map-wrap">','<div id="place-bar" class="place-bar" style="display:none" role="region" aria-label="Choose starting region"><div><strong>Choose where it begins.</strong> Tap a region on the map, then confirm.<br><span id="place-info"></span></div><div class="place-btns"><button type="button" class="btn-main" id="place-go">Start here</button><button type="button" class="pillbtn" id="place-rand">Random</button></div></div>\n    <div class="map-wrap">')
R('function renderAll(){keepFocus(renderAllInner); saveGame()}','function renderAll(){keepFocus(renderAllInner); placeUI(); saveGame()}')
R('if(!state||state.influence<m.cost) return;','if(!state||state.placing||state.influence<m.cost) return;')
R('if(!state||state.dead||state.won||state.choiceId) return;','if(!state||state.dead||state.won||state.choiceId||state.placing) return;')
R('</style>','.place-bar{display:flex;gap:.8rem;align-items:center;justify-content:space-between;flex-wrap:wrap;background:var(--panel);border:1px solid var(--accent);border-radius:var(--radius);padding:.7rem .85rem;margin-bottom:.85rem;font-size:.9rem}.place-bar #place-info{color:var(--muted);font-size:.8rem}.place-btns{display:flex;gap:.5rem;align-items:center}.place-btns .btn-main{padding:.55rem 1rem;width:auto}.placing .mut-grid,.placing #btn-advance{opacity:.4;pointer-events:none}@media(max-width:640px){.place-bar{margin:0 .35rem .6rem}}\n</style>')

SYS5=open('systems5.js',encoding='utf8').read()
R('function activatable(el,fn,label)',SYS5+'function activatable(el,fn,label)')
R('spreadMult:1.32,startInf:1.2}','''spreadMult:1.32,startInf:1.2},
  {id:"monsoon",name:"Monsoon",blurb:"Hot, wet, crowded. Warm regions are fertile ground.",stat:"Heat",detectMult:1.1,cureMult:1.05,spreadMult:1.05,startInf:1,hot:1},
  {id:"frostbite",name:"Frostbite",blurb:"Cold regions favour you. Warm labs outpace you.",stat:"Cold",detectMult:1.1,cureMult:1.12,spreadMult:0.95,startInf:1,cold:1},
  {id:"fortress",name:"Fortress",blurb:"Borders are already sealed. Every gap matters.",stat:"Sealed",detectMult:1.15,cureMult:1.2,spreadMult:1.1,startInf:1,sealStart:28},
  {id:"skies",name:"Open Skies",blurb:"Flights and ports are everywhere. So is surveillance.",stat:"Global",detectMult:1.3,cureMult:1.1,spreadMult:0.95,startInf:1,air:2}''')
R('mutRate:0.88,unlock:false}','''mutRate:0.88,unlock:false},
  {id:"fungal",name:"Fungal",blurb:"Loves heat and damp. Struggles in the cold.",stat:"Climate · Hardy",spread:0.8,resilience:1.3,conceal:1.0,mutRate:0.9,unlock:false},
  {id:"parasite",name:"Parasite",blurb:"Hides in hosts. Spreads only overland, never by air or sea.",stat:"Hidden · Overland",spread:0.62,resilience:1.0,conceal:1.6,mutRate:0.8,unlock:false},
  {id:"prion",name:"Prion",blurb:"Nearly uncurable, painfully slow.",stat:"Uncurable · Slow",spread:0.5,resilience:1.6,conceal:1.3,mutRate:0.5,unlock:false},
  {id:"synthetic",name:"Synthetic",blurb:"Engineered and self-improving, but it leaves a loud signature.",stat:"Evolving · Loud",spread:1.1,resilience:0.9,conceal:0.7,mutRate:1.3,unlock:false}''')
R('{id:"cargo",name:"Cargo Stowaways",cost:7,desc:"Ship seeding stronger; airport closures less likely",branch:"perk",req:"shell",trade:"One-time adaptation"}','''{id:"cargo",name:"Cargo Stowaways",cost:7,desc:"Ship seeding stronger; airport closures less likely",branch:"perk",req:"shell",trade:"One-time adaptation"},
  {id:"urban",name:"Urban Density",cost:7,desc:"Big regions (pop 15+) grow 2% faster each cycle",branch:"perk",req:"aero",trade:"One-time adaptation"},
  {id:"rural",name:"Rural Reach",cost:7,desc:"Small regions (pop under 15) grow 2.5% faster",branch:"perk",req:"shell",trade:"One-time adaptation"},
  {id:"insect",name:"Insect Vectors",cost:8,desc:"Infected hot regions seed their neighbours",branch:"perk",req:"rural",trade:"One-time adaptation"},
  {id:"water",name:"Waterborne",cost:8,desc:"Infected ports seed linked ports",branch:"perk",req:"cargo",trade:"One-time adaptation"},
  {id:"rapid",name:"Rapid Replication",cost:9,desc:"Transmission +0.25 immediately",branch:"perk",req:"urban",trade:"One-time adaptation"},
  {id:"heat",name:"Heat Adaptation",cost:6,desc:"Hot regions grow 2% faster each cycle",branch:"perk",req:"shell",trade:"One-time adaptation"},
  {id:"cold",name:"Cold Adaptation",cost:6,desc:"Cold regions grow 2% faster each cycle",branch:"perk",req:"shell",trade:"One-time adaptation"},
  {id:"drugres",name:"Drug Resistance",cost:8,desc:"Research runs 15% slower",branch:"perk",req:"heat",trade:"One-time adaptation"},
  {id:"sleeper",name:"Sleeper Cells",cost:9,desc:"A region past 3% can never be fully purged",branch:"perk",req:"drugres",trade:"One-time adaptation"},
  {id:"camo",name:"Cellular Camouflage",cost:7,desc:"Purges are 30% weaker",branch:"perk",req:"quiet",trade:"One-time adaptation"},
  {id:"media",name:"Media Fog",cost:8,desc:"Detection drifts down every cycle",branch:"perk",req:"camo",trade:"One-time adaptation"},
  {id:"infiltrate",name:"Lab Infiltration",cost:9,desc:"Counter −1 every cycle",branch:"perk",req:"sabotage",trade:"One-time adaptation"},
  {id:"sealbreak",name:"Border Breakers",cost:8,desc:"Seals erode 10% every cycle",branch:"perk",req:"whisper",trade:"One-time adaptation"},
  {id:"viralload",name:"Viral Load",cost:8,desc:"+1 Influence every cycle",branch:"perk",req:"memory",trade:"One-time adaptation"},
  {id:"ledger",name:"Black Ledger",cost:6,desc:"Every decision also pays 2 Influence",branch:"perk",trade:"One-time adaptation"},
  {id:"overclock",name:"Overclock",cost:6,desc:"Transmission +0.2 now, Stability −0.15",branch:"perk",trade:"One-time adaptation"}''')
R('if(m.id==="sabotage") state.cure=Math.max(0,state.cure-12);','if(m.id==="sabotage") state.cure=Math.max(0,state.cure-12);\n    if(m.id==="rapid") state.traits.spread+=0.25;\n    if(m.id==="overclock"){ state.traits.spread+=0.2; state.stability=clamp(state.stability-0.15,0.12,1); }')
R('*CURE_K*DIFF*(MARA?0.3:1)*','*CURE_K*DIFF*(MARA?0.3:1)*(state.nature.id==="prion"?0.55:1)*(state.perks.drugres?0.85:1)*')
R('(0.15+press*PURGE_K)*DIFF*(MARA?0.6:1);','(0.15+press*PURGE_K)*DIFF*(MARA?0.6:1)*(state.perks.camo?0.7:1)*(state.nature.id==="prion"?0.6:1);')
R('  airSea(n,press,grew);','  airSea(n,press,grew); perkTick();')
R('selectedRegion=startId; tipStep=0; setTip();','if(scenario.sealStart) state.regions.forEach(r=>{r.sealed=scenario.sealStart}); selectedRegion=startId; tipStep=0; setTip();')
R('<div class="mut-grid" id="mut-actions"></div>','<div id="mut-tabs" class="mut-tabs" role="tablist" aria-label="Mutation branches"></div>\n        <div class="mut-grid" id="mut-actions"></div>')
R('</style>','.mut-tabs{display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:.5rem}.mut-tabs .pillbtn{margin:0;padding:.3rem .6rem;font-size:.78rem}#camp-list{max-height:58vh;overflow:auto}\n</style>')
R('function renderAll(){keepFocus(renderAllInner); placeUI(); saveGame()}','function renderAll(){keepFocus(()=>{renderAllInner(); placeUI(); renderTabs();}); saveGame()}')
R('MUT_OPTIONS.forEach((m,mi)=>{','visibleMuts().forEach((m,mi)=>{')
R('function isUnlocked(id){return unlockedSet().has(id) || NATURES.find(n=>n.id===id)?.unlock}','function isUnlocked(id){ const r=NAT_REQ[id]; return r===undefined||winsNow()>=r||(r<=1&&unlockedSet().has(id)); }')
R('${locked?"Win a run to unlock.":n.blurb}','${locked?"Win "+NAT_REQ[n.id]+" run"+(NAT_REQ[n.id]>1?"s":"")+" to unlock.":n.blurb}')
R('Five linked chapters. Win to unlock the next and carry up to two adaptations forward.','Ten linked chapters. Win to unlock the next and carry adaptations forward (more as you progress).')
R('gotA("Fully Adapted: owned every adaptation",["quiet","shell","aero","memory","sabotage","whisper","flyer","cargo"].every(k=>state.perks[k]));','gotA("Mastermind: owned 12 adaptations in one run",Object.keys(state.perks).length>=12);')
R('{ const S=loadStats(); S.games++;','{ const S=loadStats(); S.games++; S.nw=S.nw||{}; if(win) S.nw[state.nature.id]=1; if(Object.keys(S.nw).length>=4) ach.push("Collector: won with 4 different natures");')

R('spread:0.72,resilience:1.38,conceal:1.15,mutRate:0.8,unlock:true','spread:0.88,resilience:1.38,conceal:1.15,mutRate:0.8,unlock:true')
R('spread:1.14,resilience:0.92,conceal:0.95,mutRate:1.15,unlock:true','spread:0.92,resilience:0.92,conceal:0.95,mutRate:1.15,unlock:true')
R('spread:1.4,resilience:0.7,conceal:0.8,mutRate:1.48','spread:1.1,resilience:0.7,conceal:0.8,mutRate:1.48')
R('spread:1.1,resilience:0.9,conceal:0.7,mutRate:1.3','spread:0.98,resilience:0.9,conceal:0.7,mutRate:1.3')
R('spread:0.62,resilience:1.0,conceal:1.6,mutRate:0.8','spread:0.9,resilience:1.0,conceal:1.6,mutRate:0.8')
R('spread:0.5,resilience:1.6,conceal:1.3,mutRate:0.5','spread:0.72,resilience:1.6,conceal:1.3,mutRate:0.5')
R('detectMult:1,cureMult:1,spreadMult:1,startInf:1}','detectMult:1,cureMult:1.2,spreadMult:1,startInf:1}')
R('detectMult:1.35,cureMult:0.82,spreadMult:0.88','detectMult:1.15,cureMult:0.65,spreadMult:0.95')
R('detectMult:1.22,cureMult:1.55,spreadMult:0.94','detectMult:1.2,cureMult:1.2,spreadMult:1.0')
R('detectMult:1.22,cureMult:1.18,spreadMult:1.32','detectMult:1.35,cureMult:1.46,spreadMult:1.25')
R('detectMult:1.1,cureMult:1.05,spreadMult:1.05,startInf:1,hot:1','detectMult:1.2,cureMult:1.3,spreadMult:1.05,startInf:1,hot:1')
R('(state.nature.id==="prion"?0.55:1)','(state.nature.id==="prion"?0.7:1)')
R('(state.nature.id==="prion"?0.6:1);','(state.nature.id==="prion"?0.8:1);')
R('detectMult:1.3,cureMult:1.1,spreadMult:0.95,startInf:1,air:2','detectMult:1.22,cureMult:1.06,spreadMult:0.95,startInf:1,air:2')
R('spread:0.8,resilience:1.3,conceal:1.0,mutRate:0.9','spread:0.86,resilience:1.3,conceal:1.0,mutRate:0.9')

GUIDE=open('guide.js',encoding='utf8').read()
R('function activatable(el,fn,label)',GUIDE+'function activatable(el,fn,label)')
R('<div class="stat-box influence"><div class="label">Influence</div><div class="val" id="s-inf">0</div></div>','<div class="stat-box influence" id="stat-inf-box" role="button" tabindex="0" aria-label="Influence: what is it?" title="Influence is your currency. Click for details."><div class="label">Influence <span class="qm">?</span></div><div class="val" id="s-inf">0</div><div class="sub" id="inc-sub"></div></div>')
R('<button type="button" id="btn-how">How to Play</button>','<button type="button" id="btn-how">How to Play</button>\n      <button type="button" id="btn-help">Glossary</button>')
R('<div class="modal-bg hidden" id="modal-how">','<div class="modal-bg hidden" id="modal-help"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="help-title"><h2 id="help-title">What the numbers mean</h2><p><strong style="color:var(--text)">Influence</strong> is your currency. You start with 7 and earn about +2.5 every cycle at first, rising as you spread (more presence, more regions, and high detection all help). Spend it on mutations and adaptations; prices are shown on each button. Unspent Influence carries over.</p><p><strong style="color:var(--text)">Presence</strong> is how much of the world carries you.</p><p><strong style="color:var(--text)">Detection</strong> is how much the world knows. High detection speeds up the cure and border closures.</p><p><strong style="color:var(--text)">Counter</strong> is the world\'s cure progress. At 100% you are erased unless you are already permanent.</p><p><strong style="color:var(--text)">Stability</strong> is how steady your form is. Low stability means random drift in your traits.</p><p><strong style="color:var(--text)">Permanence</strong> is your progress toward becoming impossible to remove.</p><button class="btn-main" style="width:100%;margin-top:1rem" id="help-close">Got it</button></div></div>\n<div class="modal-bg hidden" id="modal-how">')
R('<div><button class="pillbtn" id="btn-camp" style="margin-bottom:.6rem">Campaign</button></div>','<div><button class="pillbtn" id="btn-tut" style="margin-bottom:.6rem">Tutorial</button><button class="pillbtn" id="btn-camp" style="margin-bottom:.6rem">Campaign</button></div>')
R('function renderAll(){keepFocus(()=>{renderAllInner(); placeUI(); renderTabs();}); saveGame()}','function renderAll(){keepFocus(()=>{renderAllInner(); placeUI(); renderTabs(); guideTick();}); saveGame()}')
R('Bias mutations with Influence, then advance cycles.','Bias mutations with Influence (your currency: you earn it every cycle and spend it on mutations), then advance cycles.')
R('</style>','.stat-box .sub{font-size:.68rem;color:var(--muted);margin-top:.1rem}.stat-box.influence{cursor:pointer}.stat-box .qm{display:inline-block;width:1.05em;height:1.05em;line-height:1.05em;text-align:center;border:1px solid var(--muted);border-radius:50%;font-size:.65em;color:var(--muted);margin-left:.2rem}.mut-btn.afford{box-shadow:0 0 0 1px var(--accent),0 0 12px rgba(124,252,176,.22)}.mut-btn .need{display:block;font-style:normal;font-size:.72rem;color:var(--muted)}#tut-ring{display:none;position:fixed;z-index:60;border:2px solid var(--accent);border-radius:12px;box-shadow:0 0 0 9999px rgba(0,0,0,.58);pointer-events:none;transition:all .25s}#tut-card{display:none;position:fixed;z-index:61;left:50%;bottom:14px;transform:translateX(-50%);width:min(440px,calc(100vw - 20px));background:var(--panel);border:1px solid var(--accent);border-radius:14px;padding:.9rem 1rem;box-shadow:0 10px 40px rgba(0,0,0,.6)}#tut-card h3{margin:.15rem 0 .35rem;color:var(--accent);font-size:1.05rem}#tut-card p{margin:0 0 .7rem;font-size:.92rem;line-height:1.45}.tut-step{font-size:.72rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}.tut-btns{display:flex;gap:.5rem;align-items:center;justify-content:space-between}@media(prefers-reduced-motion:reduce){#tut-ring{transition:none}}\n</style>')

AUDIO=open('audio.js',encoding='utf8').read()
DAILYJS=open('daily.js',encoding='utf8').read()
R('function activatable(el,fn,label)',AUDIO+DAILYJS+'function activatable(el,fn,label)')
R('function rnd(){return Math.random()}','')
_i=s.index('function beep(freq, dur, type){'); _j=s.index('  }catch(e){}\n}\n',_i)+len('  }catch(e){}\n}\n'); s=s[:_i]+s[_j:]
R('const calm=window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches;','let calm=window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches;')
R('if(soundOn) beep(440,0.06);\n};','if(soundOn) beep(440,0.06);\n  PREFS.master=soundOn; savePrefs(); audioSync(); { const sm=$("set-master"); if(sm) sm.checked=soundOn; }\n};')
R('const cr=b[0]+(130-b[0])*f, cg=b[1]+(255-b[1])*f, cb=b[2]+(170-b[2])*f;','const T=PREFS.cb?[240,228,66]:[130,255,170], B2=PREFS.cb?CB_BASE[(ri*3)%8]:b, cr=B2[0]+(T[0]-B2[0])*f, cg=B2[1]+(T[1]-B2[1])*f, cb=B2[2]+(T[2]-B2[2])*f;')
R('const landCanvas=document.createElement("canvas");','const CB_BASE=[[70,110,170],[60,140,190],[100,100,170],[50,130,150],[90,120,160],[130,100,170],[80,150,190],[60,110,140]];\nconst landCanvas=document.createElement("canvas");')
R('if(win){ unlockAllNatures(); flash("good"); beep(523,0.15); setTimeout(()=>beep(659,0.15),120); }','if(win){ unlockAllNatures(); flash("good"); sfx("win"); }')
R('else { flash("bad"); beep(110,0.2,"sawtooth"); }','else { flash("bad"); sfx("lose"); }')
R('const c=CHAPTERS[i], C=loadCamp(); CAMP=i;','const c=CHAPTERS[i], C=loadCamp(); CAMP=i; DAILY=null; SEED=null;')
R('state.purgedNow=purged.slice(); if(purged.length){ log(','state.purgedNow=purged.slice(); if(purged.length){ sfx("purge"); log(')
R('  campaignEnd(win);','  campaignEnd(win); dailyEnd(win);')
R('<button type="button" id="btn-help">Glossary</button>','<button type="button" id="btn-help">Glossary</button>\n      <button type="button" id="btn-settings">Settings</button>')
R('<button class="pillbtn" id="btn-camp" style="margin-bottom:.6rem">Campaign</button></div>','<button class="pillbtn" id="btn-camp" style="margin-bottom:.6rem">Campaign</button><button class="pillbtn" id="btn-daily" style="margin-bottom:.6rem">Daily Challenge</button></div>')
R('<div class="modal-bg hidden" id="modal-how">','''<div class="modal-bg hidden" id="modal-settings"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="set-title"><h2 id="set-title">Settings</h2>
<div class="set-row"><label><input type="checkbox" id="set-master"> Sound</label></div>
<div class="set-row"><label><input type="checkbox" id="set-music"> Music</label><input type="range" id="set-musicvol" min="0" max="100" aria-label="Music volume"></div>
<div class="set-row"><label><input type="checkbox" id="set-sfx"> Sound effects</label><input type="range" id="set-sfxvol" min="0" max="100" aria-label="Effects volume"></div>
<div class="set-row"><label><input type="checkbox" id="set-cb"> Colorblind-safe palette</label></div>
<div class="set-row"><label><input type="checkbox" id="set-rm"> Reduce motion</label></div>
<div class="set-row"><label><input type="checkbox" id="set-big"> Larger text</label></div>
<button class="btn-main" style="width:100%;margin-top:1rem" id="set-close">Done</button></div></div>
<div class="modal-bg hidden" id="modal-daily"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="daily-title"><h2 id="daily-title">Daily Challenge</h2><p>Everyone gets the same scenario, pathogen, modifier and random seed today. Choose your start and see how far you get. Retry as often as you like; your best result counts.</p><p id="daily-desc"></p><p id="daily-stats" style="color:var(--muted)"></p><button class="btn-main" style="width:100%;margin-top:1rem" id="daily-play">Play today's challenge</button><button class="pillbtn" style="margin:.6rem 0 0" id="daily-close">Close</button></div></div>
<div class="modal-bg hidden" id="modal-how">''')
R('</style>','''.set-row{display:flex;align-items:center;justify-content:space-between;gap:.8rem;margin:.6rem 0}.set-row label{display:flex;align-items:center;gap:.5rem;cursor:pointer}.set-row input[type=range]{width:42%;accent-color:var(--accent)}
body.big{font-size:18.5px}body.rm *,body.rm *::before,body.rm *::after{animation:none!important;transition:none!important}
body.cb{--accent:#56b4e9;--accent-dim:rgba(86,180,233,.14);--infect:#f0e442;--detect:#cc79a7;--cure:#e69f00;--warn:#e69f00;--danger:#d55e00}
body.cb .btn-main{background:linear-gradient(180deg,#8fd0f5,#56b4e9)!important;color:#05131d!important;box-shadow:0 0 18px rgba(86,180,233,.3)}
body.cb .fx .g{background:radial-gradient(circle,rgba(240,228,66,.55) 0,rgba(240,228,66,.18) 38%,transparent 70%)}
body.cb .fx .d{border-color:#cc79a7;box-shadow:0 0 16px rgba(204,121,167,.75),inset 0 0 14px rgba(204,121,167,.35)}
body.cb .fx .s{border-color:#fff}
body.cb .route.live{stroke:rgba(240,228,66,.75)}body.cb .flight{stroke:#f0e442}body.cb .flight.sea{stroke:#56b4e9}
body.cb .mut-btn.afford{box-shadow:0 0 0 1px var(--accent),0 0 12px rgba(86,180,233,.28)}
body.cb .map-stage .region.lvl1{border-color:#56b4e9}body.cb .map-stage .region.lvl2{border-color:#f0e442}body.cb .map-stage .region.lvl3{border-color:#e69f00}body.cb .map-stage .region.lvl4{border-color:#d55e00}
</style>''')

LAYOUT=open('layout.js',encoding='utf8').read()
R('function activatable(el,fn,label)',LAYOUT+'function activatable(el,fn,label)')
R('function renderAll(){keepFocus(()=>{renderAllInner(); placeUI(); renderTabs(); guideTick();}); saveGame()}','function renderAll(){keepFocus(()=>{renderAllInner(); placeUI(); renderTabs(); guideTick(); layoutTick();}); saveGame()}')
R('</style>','''
#topbar{position:sticky;top:0;z-index:20;background:rgba(7,10,13,.95);backdrop-filter:blur(8px);padding:.3rem 0 .4rem}
#topbar .head{display:flex;align-items:center;justify-content:space-between;gap:.8rem;margin-bottom:.3rem}
#topbar .phase-blurb{flex:1;min-width:0;margin:0;padding:.25rem .6rem;font-size:.78rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#topbar .turn-bar{margin:0;font-size:.8rem;white-space:nowrap}
#topbar .hud{display:grid;grid-template-columns:repeat(5,1fr)!important;gap:.35rem;margin:0 0 .35rem}
#topbar .stat-box{padding:.28rem .2rem}
#topbar .stat-box .label{font-size:.58rem;letter-spacing:.04em}
#topbar .stat-box .val{font-size:1.05rem;line-height:1.15}
#topbar .stat-box .sub{font-size:.6rem;margin:0}
#topbar .race{grid-template-columns:1fr 1fr!important;gap:.4rem;margin:0}
#topbar .race-item{padding:.22rem .5rem}
#topbar .rl{font-size:.66rem}
#advance-bar .actions{margin:0}
#advance-bar button{width:100%}
@media(min-width:1001px){
 .shell{max-width:1280px}
 #game-main{display:grid;grid-template-columns:minmax(0,1.45fr) minmax(360px,1fr);gap:.7rem;align-items:start}
 #col-left{position:sticky;top:calc(var(--tb,150px) + 6px);display:flex;flex-direction:column;gap:.5rem}
 #col-left .map-title{display:none}
 #col-left .map-wrap{padding:.4rem .5rem .3rem;margin:0}
 #col-left .map-stage{width:min(100%,max(380px,calc((100vh - 470px)*1.728)));margin:0 auto}
 #dock{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
 #dock>.panel{max-height:150px;overflow:auto;margin:0;padding:.5rem .7rem}
 #region-panel{order:1}#log-panel,#dock>.place-bar{order:2}
 body.placing #log-panel{display:none}
 #dock>.place-bar{max-height:150px;margin:0!important;flex-direction:column;align-items:stretch!important;justify-content:space-between;gap:.4rem;padding:.5rem .7rem;font-size:.82rem}
 #dock>.place-bar .place-btns{justify-content:space-between}
 #dock>.panel h3{margin:.1rem 0 .3rem;font-size:.9rem}
 #dock-tabs{display:none}
 #col-right .panel{margin:0}
 #advance-bar{position:sticky;bottom:8px;z-index:6;margin-top:.6rem;background:var(--bg);padding:.3rem 0}
}
@media(max-height:700px) and (min-width:1001px){#col-left{position:static}}
@media(max-width:640px){.nav{flex-wrap:wrap;gap:.1rem .6rem;justify-content:flex-end}.nav button{padding:.25rem .3rem;font-size:.82rem}}
@media(max-width:1000px){
 #game-main{display:flex;flex-direction:column}
 #col-left{display:contents}
 .map-wrap{order:1}
 #dock-tabs{order:2}
 #dock{order:3}
 #col-right{order:4}
 #topbar .phase-blurb{display:none}
 #topbar .head{justify-content:flex-start;margin-bottom:.2rem}
 .map-wrap{position:sticky;top:var(--tb,110px);z-index:15;background:var(--bg);padding:.3rem 0 .1rem!important}
 .map-title{display:none}
 .legend{font-size:.6rem;padding:0 .5rem}
 #dock-tabs{display:flex;gap:.35rem;margin:0 0 .5rem;position:sticky;top:calc(var(--tb,110px) + var(--mh,240px));z-index:14;background:var(--bg);padding:.35rem 0}
 #dock-tabs .pillbtn{margin:0;flex:1}
 #dock>.panel{margin:0 0 .6rem;max-height:none}
 #screen-game[data-tab="mut"] #dock>.panel{display:none}
 #screen-game:not([data-tab="mut"]) #mut-panel{display:none}
 #screen-game[data-tab="log"] #region-panel{display:none}
 #screen-game[data-tab="region"] #log-panel{display:none}
 #advance-bar{position:fixed;left:0;right:0;bottom:0;z-index:30;padding:.5rem .7rem calc(.5rem + env(safe-area-inset-bottom));background:rgba(7,10,13,.97);border-top:1px solid var(--border)}
 #screen-game{padding-bottom:84px}
 body.placing #advance-bar{display:none}
 .place-bar{position:fixed!important;left:.35rem;right:.35rem;bottom:.35rem;z-index:31;margin:0!important;padding:.5rem .7rem!important;font-size:.82rem;gap:.4rem!important}
 .place-bar>div:first-child{flex:1 1 100%}
 .place-bar #place-info{font-size:.72rem}
 .place-btns{width:100%}
 .place-btns .btn-main{flex:1}
 body.placing #screen-game{padding-bottom:150px}
 #tut-card{bottom:88px}
 .toast{bottom:5.2rem}
 #topbar .rl span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
 #topbar .rl{gap:.3rem}
}
</style>''')

import urllib.parse
ICONS={
 "sound":'<path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/>',
 "book":'<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5z"/><path d="M8 7h7"/>',
 "help":'<circle cx="12" cy="12" r="9"/><path d="M9.5 9.2a2.5 2.5 0 1 1 3.6 2.2c-.7.4-1.1 1-1.1 1.8M12 17h.01"/>',
 "gear":'<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M4.5 4.5l2.1 2.1M17.4 17.4l2.1 2.1M2.5 12h3M18.5 12h3M4.5 19.5l2.1-2.1M17.4 6.6l2.1-2.1"/>',
 "info":'<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
 "eye":'<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "flask":'<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3"/><path d="M7.5 14h9"/>',
 "bolt":'<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/>',
 "virus":'<circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
 "shield":'<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6l-8-3z"/>',
 "dna":'<path d="M8 3c0 5 8 5 8 9s-8 4-8 9M16 3c0 5-8 5-8 9s8 4 8 9M9 7h6M9 17h6"/>',
 "pin":'<path d="M12 21s7-6.2 7-11a7 7 0 1 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
 "list":'<path d="M4 6h16M4 12h16M4 18h10"/>',
 "play":'<path d="M7 4.5l13 7.5-13 7.5V4.5z"/>',
 "calendar":'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/>',
 "flag":'<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
 "cap":'<path d="M2 9l10-5 10 5-10 5L2 9z"/><path d="M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/>',
 "check":'<path d="M5 12.5l4.5 4.5L19 7.5"/>'}
def _ic(p):
    svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+p+'</svg>'
    return 'url("data:image/svg+xml,'+urllib.parse.quote(svg,safe="")+'")'
ICONCSS=':root{'+''.join('--i-%s:%s;'%(k,_ic(v)) for k,v in ICONS.items())+'}\n'
THEMECSS=open('theme.css',encoding='utf8').read()
THEMEJS=open('theme.js',encoding='utf8').read()
MARK='<svg class="mark" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="21" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M8 19c10 7 22 7 32 0M8 29c10 7 22 7 32 0" fill="none" stroke="currentColor" stroke-width="2.2" opacity=".55"/><circle cx="24" cy="24" r="4.2" fill="currentColor"/></svg>'
HERO='''<div class="hero2"><canvas id="hero-canvas" aria-hidden="true"></canvas>
      <div class="hero-inner">
        <div class="brand">'''+MARK+'''<h1>VEIL</h1></div>
        <p class="tag">You do not control the contagion.<br><em>You steer it.</em><br>Become permanent before the world erases you.</p>
        <div class="score-pill" id="title-best">Best score: <strong>—</strong></div>
        <div class="cta"><button class="btn-main" id="btn-start">Begin Emergence</button><button class="diffbtn" id="btn-resume" style="display:none">Resume saved run</button></div>
        <div class="opts">
          <div class="opt"><span class="opt-l">Run length</span><div class="seg" id="len-row" role="group" aria-label="Run length"><button class="pillbtn lenbtn on" data-m="0">Standard run</button><button class="pillbtn lenbtn" data-m="1">Marathon</button></div></div>
          <div class="opt"><span class="opt-l">Difficulty</span><div class="seg" id="diff-row" role="group" aria-label="Difficulty"><button class="diffbtn" data-d="0.8">Casual</button><button class="diffbtn on" data-d="1">Normal</button><button class="diffbtn" data-d="1.25">Brutal</button></div></div>
        </div>
        <div class="modecards">
          <button type="button" class="mc" id="btn-camp"><span class="mc-ic ic-flag"></span><strong>Campaign</strong><em>Ten linked chapters with carry-over adaptations.</em><span class="mc-sub" id="camp-sub"></span></button>
          <button type="button" class="mc" id="btn-daily"><span class="mc-ic ic-cal"></span><strong>Daily Challenge</strong><em>One shared seed for everyone, every day.</em><span class="mc-sub" id="daily-sub"></span></button>
          <button type="button" class="mc" id="btn-tut"><span class="mc-ic ic-cap"></span><strong>Tutorial</strong><em>A guided first run that teaches by doing.</em><span class="mc-sub" id="tut-sub"></span></button>
        </div>
        <div class="foot"><button class="btn-ghost" id="btn-how2">How it works</button><button class="pillbtn" id="btn-reset">Reset progress</button></div>
        <p class="unlocks" id="unlock-note"></p>
      </div></div>'''
R('function activatable(el,fn,label)',THEMEJS+'function activatable(el,fn,label)')
R('<div class="logo">VEIL <span>contagion protocol</span></div>','<div class="logo">'+MARK+'VEIL <span>contagion protocol</span></div>')
_a=s.index('<div class="hero">'); _b=s.index('</section>',_a); s=s[:_a]+HERO+'\n  '+s[_b:]
R('<div class="modal-bg hidden" id="modal-choice">','<div id="toasts" aria-live="polite"></div>\n<div class="modal-bg hidden" id="modal-choice">')
R('document.body.appendChild(t); setTimeout(()=>t.remove(),1900);','const box=document.getElementById("toasts")||document.body; Array.from(box.querySelectorAll(".toast")).forEach(c=>{ if(c.textContent===msg) c.remove(); }); const all=box.querySelectorAll(".toast"); for(let i=0;i<all.length-2;i++) all[i].remove(); box.appendChild(t); setTimeout(()=>t.remove(),2200);')
R('if(typeof refreshLocks==="function")refreshLocks()}','if(typeof refreshLocks==="function")refreshLocks(); if(typeof heroStart==="function")heroStart(); if(typeof cardSubs==="function")cardSubs()}')
R('</style>',ICONCSS+THEMECSS+'</style>')

import html as _html, urllib.parse as _up
SITE_N=(SITE.rstrip('/')+'/') if SITE else ''
_TITLE='VEIL — Steer the Contagion'
_DESC='Steer a spreading pathogen across 41 world regions, outwit the cure, and become permanent. 8 pathogens, a 10-chapter campaign and a daily challenge. Play in your browser.'
_ALT='VEIL: a glowing dot-matrix world map with an outbreak spreading across it, and the tagline "Steer the contagion."'
_E=lambda x:_html.escape(x,quote=True)
_FAV='data:image/svg+xml,'+_up.quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="11" fill="#04060a"/><circle cx="24" cy="24" r="16" fill="none" stroke="#5df2b1" stroke-width="2.6"/><path d="M11 21c8 5.5 18 5.5 26 0M11 28c8 5.5 18 5.5 26 0" fill="none" stroke="#5df2b1" stroke-width="2.6" opacity=".55"/><circle cx="24" cy="24" r="3.4" fill="#5df2b1"/></svg>',safe='')
_META='''<title>%s</title>
<meta name="description" content="%s"/>
<meta name="theme-color" content="#04060a"/>
<meta name="color-scheme" content="dark"/>
<link rel="icon" href="%s"/>
<link rel="apple-touch-icon" href="%sapple-touch-icon.png"/>
<meta property="og:type" content="website"/>
<meta property="og:site_name" content="VEIL"/>
<meta property="og:title" content="%s"/>
<meta property="og:description" content="%s"/>
<meta property="og:image" content="%sshare.png"/>
<meta property="og:image:type" content="image/png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta property="og:image:alt" content="%s"/>
%s<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="%s"/>
<meta name="twitter:description" content="%s"/>
<meta name="twitter:image" content="%sshare.png"/>
<meta name="twitter:image:alt" content="%s"/>'''%(_E(_TITLE),_E(_DESC),_FAV,SITE_N,_E(_TITLE),_E(_DESC),SITE_N,_E(_ALT),('<meta property="og:url" content="%s"/>\n<link rel="canonical" href="%s"/>\n'%(_E(SITE_N),_E(SITE_N)) if SITE_N else ''),_E(_TITLE),_E(_DESC),SITE_N,_E(_ALT))
R('<title>VEIL — Steer the Contagion</title>\n<meta name="description" content="VEIL: steer an unstable contagion. Become permanent before the world erases you."/>',_META)

# ---- keyboard ----
i=s.index('document.addEventListener("keydown"'); j=s.index('showTitleBest();\n})();')
s=s[:i]+'''document.addEventListener("keydown",e=>{
  const open=!$("modal-how").classList.contains("hidden")||!$("modal-about").classList.contains("hidden");
  if(e.key==="Escape"&&open){$("modal-how").classList.add("hidden");$("modal-about").classList.add("hidden");return}
  if(e.repeat||open) return;
  if(e.code!=="Space"&&e.key!=="Enter") return;
  if(!$("screen-game").classList.contains("active")||!state||state.dead||state.won) return;
  const t=e.target; if(t&&t.closest&&t.closest("button,[role=button]")) return;
  e.preventDefault(); advanceCycle();
});
'''+s[j:]
R('if(e.code!=="Space"&&e.key!=="Enter") return;','''if(/^[1-9]$/.test(e.key)){ const mo=MUT_OPTIONS[+e.key-1]; if(mo&&$("screen-game").classList.contains("active")&&state&&!state.dead&&!state.won){ const bb=document.querySelector('[data-fk="m:'+mo.id+'"]'); if(bb&&!bb.disabled) bb.click(); } return; }
  if(e.code!=="Space"&&e.key!=="Enter") return;''')

R('const open=!$("modal-how").classList.contains("hidden")||!$("modal-about").classList.contains("hidden");','const open=!$("modal-how").classList.contains("hidden")||!$("modal-about").classList.contains("hidden")||!$("modal-choice").classList.contains("hidden");')
R('if(e.repeat||open) return;','if(!$("modal-choice").classList.contains("hidden")&&/^[1-3]$/.test(e.key)){ const ob=document.querySelectorAll("#choice-opts button")[+e.key-1]; if(ob) ob.click(); return; }\n  if(e.repeat||open) return;')

R('||!$("modal-choice").classList.contains("hidden");','||!$("modal-choice").classList.contains("hidden")||!$("modal-camp").classList.contains("hidden");')
R('$("modal-about").classList.add("hidden");return}','$("modal-about").classList.add("hidden");$("modal-camp").classList.add("hidden");return}')

R('state&&!state.dead&&!state.won){ const bb=','state&&!state.dead&&!state.won&&!state.placing){ const bb=')

R('const mo=MUT_OPTIONS[+e.key-1];','const mo=visibleMuts()[+e.key-1];')

R('||!$("modal-camp").classList.contains("hidden");','||!$("modal-camp").classList.contains("hidden")||!$("modal-help").classList.contains("hidden");')
R('$("modal-camp").classList.add("hidden");return}','$("modal-camp").classList.add("hidden");$("modal-help").classList.add("hidden");return}')

R('||!$("modal-help").classList.contains("hidden");','||!$("modal-help").classList.contains("hidden")||!$("modal-settings").classList.contains("hidden")||!$("modal-daily").classList.contains("hidden");')
R('$("modal-help").classList.add("hidden");return}','$("modal-help").classList.add("hidden");$("modal-settings").classList.add("hidden");$("modal-daily").classList.add("hidden");return}')

open('veil.html','w').write(s)
js=re.search(r'<script>(.*)</script>',s,re.S).group(1)
js=js.replace("showTitleBest();\n})();","showTitleBest();\nglobalThis.__g={get state(){return state},setSel(n,s){selectedNature=n;selectedScenario=s},newGame,advanceCycle,applyMut,MUT_OPTIONS,totalPresence,criticalPresence,permanenceProgress,resolveChoice,setMode,startChapter,startDaily,dailySetup,utcKey};\n})();")
open('game.js','w').write(js)
