let heroRAF=0, heroPulses=[], heroColCache="93,242,177", heroColAt=0;
function heroColor(){ return (PREFS&&PREFS.cb)?"86,180,233":"93,242,177"; }
function heroDraw(ts){
  const cv=document.getElementById("hero-canvas"), scr=document.getElementById("screen-title");
  if(!cv||!scr||!scr.classList.contains("active")){ heroRAF=0; return; }
  const w=cv.clientWidth, h=cv.clientHeight; if(!w||!h){ heroRAF=requestAnimationFrame(heroDraw); return; }
  const dpr=Math.min(window.devicePixelRatio||1,2); if(cv.width!==Math.round(w*dpr)||cv.height!==Math.round(h*dpr)){ cv.width=Math.round(w*dpr); cv.height=Math.round(h*dpr); }
  const g=cv.getContext("2d"); g.setTransform(dpr,0,0,dpr,0,0); g.clearRect(0,0,w,h);
  const sc=Math.max(w/1504,h/870)*1.06, ox=(w-1504*sc)/2, oy=(h-870*sc)/2, t=ts/1000;
  if(!calm&&heroPulses.length<4&&(!heroPulses.length||t-heroPulses[heroPulses.length-1].t0>2.0)){ const n=Math.floor(Math.random()*(LAND.length/3))*3; heroPulses.push({x:LAND[n]*10+5,y:LAND[n+1]*10+5,t0:t}); }
  heroPulses=heroPulses.filter(p=>t-p.t0<7);
  const col=heroColor(), pr=Math.max(1,sc);
  for(let n=0;n<LAND.length;n+=3){
    const x=LAND[n]*10+5, y=LAND[n+1]*10+5; let a=0.17, r=1.25;
    for(let i=0;i<heroPulses.length;i++){ const p=heroPulses[i], age=(t-p.t0)/7, rad=(t-p.t0)*95, d=Math.hypot(x-p.x,y-p.y);
      if(d<rad+45){ const k=Math.max(0,1-Math.abs(d-rad)/55)*(1-age), fill=d<rad?0.2*(1-age):0; a=Math.max(a,0.17+k*0.75+fill); r=Math.max(r,1.25+k*1.7); } }
    g.fillStyle="rgba("+col+","+a.toFixed(2)+")"; g.beginPath(); g.arc(ox+x*sc,oy+y*sc,r*pr*0.85,0,6.283); g.fill();
  }
  heroRAF=requestAnimationFrame(heroDraw);
}
function heroStart(){ if(window.__autostart||heroRAF) return; heroRAF=requestAnimationFrame(heroDraw); }
function cardSubs(){
  if(window.__autostart) return;
  const C=loadCamp(), done=C.done.filter(Boolean).length, a=document.getElementById("camp-sub"), d=document.getElementById("daily-sub"), t=document.getElementById("tut-sub");
  if(a) a.textContent=done>=CHAPTERS.length?"Completed ✓":"Chapter "+(done+1)+" of "+CHAPTERS.length;
  if(d){ const k=utcKey(), x=dailySetup(k), e=(loadStats().daily||{})[k]; d.textContent=e?("Today: "+(e.win?"won":"played")+" · "+e.score):("Today: "+x.sc.name+" · "+x.mod.n); }
  if(t) t.textContent=tutDone()?"Replay":"Recommended";
}
function sparkTick(){
  const H=state.hist||[];
  [[".stat-box.infect","p"],[".stat-box.detect","d"],[".stat-box.cure","c"]].forEach(([sel,k])=>{
    const box=document.querySelector(sel); if(!box) return;
    let sv=box.querySelector(".spark");
    if(!sv){ sv=document.createElementNS("http://www.w3.org/2000/svg","svg"); sv.setAttribute("class","spark"); sv.setAttribute("viewBox","0 0 100 30"); sv.setAttribute("preserveAspectRatio","none"); sv.innerHTML="<polyline points=\"\"></polyline>"; box.appendChild(sv); }
    const pts=H.slice(-24).map(h=>Math.max(0,Math.min(100,h[k]))), n=pts.length, m=Math.max(20,Math.max.apply(null,pts.concat([0])));
    sv.querySelector("polyline").setAttribute("points",n<2?"":pts.map((v,i)=>(i*100/(n-1)).toFixed(1)+","+(28-v/m*26).toFixed(1)).join(" "));
  });
}
setTimeout(()=>{ heroStart(); cardSubs(); },60);
