function placeUI(){
  const bar=document.getElementById("place-bar"); if(!bar||!state) return;
  const on=!!state.placing; bar.style.display=on?"flex":"none"; document.body.classList.toggle("placing",on);
  if(!on) return;
  const r=state.regions.find(x=>x.id===selectedRegion), tip=$("tip");
  $("place-go").textContent="Start in "+(r?r.name:"…");
  $("place-info").textContent=r?("Pop "+r.pop+" · Science "+r.science+" · Openness "+r.open+" · Links "+r.links.length+" · "+r.climate+(r.air?" · airport":"")+(r.port?" · port":"")):"";
  if(tip){ tip.style.display="block"; tip.textContent="Choose your starting region. Open, well-connected regions spread faster; low-science regions are slower to notice you."; }
}
function confirmStart(id){
  if(!state||!state.placing) return; const r=state.regions.find(x=>x.id===id); if(!r) return;
  state.placing=false; state.origin=id; r.inf=state.pendingBase; selectedRegion=id;
  log("Pattern begins in "+r.name+".","sys"); (state.marks=state.marks||[]).push({t:1,x:"Began in "+r.name});
  beep(330,0.08); setTip(); renderAll();
}
(function(){
  const go=document.getElementById("place-go"), rd=document.getElementById("place-rand");
  if(go) go.onclick=()=>confirmStart(selectedRegion);
  if(rd) rd.onclick=()=>{ if(state&&state.placing) confirmStart(pick(state.regions).id); };
})();
