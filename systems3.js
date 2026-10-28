const SC_REQ={bloom:0,ghost:1,iron:2,fire:3,monsoon:4,frostbite:5,fortress:6,skies:7};
const NAT_REQ={spore:0,vector:0,viral:1,dormant:1,fungal:2,parasite:3,prion:4,synthetic:5};
function winsNow(){ return loadStats().wins; }
function scUnlocked(id){ return winsNow()>=(SC_REQ[id]||0); }
function refreshLocks(){
  const w=winsNow(), natN=NATURES.filter(n=>isUnlocked(n.id)).length, scN=SCENARIOS.filter(s=>scUnlocked(s.id)).length;
  document.querySelectorAll(".lenbtn").forEach(b=>{
    const isM=b.dataset.m==="1", lock=isM&&w<1;
    b.classList.toggle("locked",lock); b.setAttribute("aria-disabled",lock?"true":"false");
    b.title=lock?"Win 1 run to unlock Marathon":""; b.textContent=isM?(lock?"🔒 Marathon":"Marathon"):"Standard run";
    if(lock&&b.classList.contains("on")){ MARA=false; document.querySelectorAll(".lenbtn").forEach(x=>x.classList.toggle("on",x.dataset.m==="0")); }
  });
  const br=document.querySelector('.diffbtn[data-d="1.25"]');
  if(br){ const lock=w<2; br.classList.toggle("locked",lock); br.setAttribute("aria-disabled",lock?"true":"false"); br.title=lock?"Win 2 runs to unlock Brutal":""; br.textContent=lock?"🔒 Brutal":"Brutal";
    if(lock&&DIFF>1){ DIFF=1; document.querySelectorAll(".diffbtn[data-d]").forEach(x=>x.classList.toggle("on",x.dataset.d==="1")); } }
  const items=[[1,"Marathon"],[2,"Brutal"]];
  NATURES.forEach(n=>{ const r=NAT_REQ[n.id]; if(r>0) items.push([r,n.name]); });
  SCENARIOS.forEach(s=>{ const r=SC_REQ[s.id]; if(r>0) items.push([r,s.name]); });
  const later=items.map(i=>i[0]).filter(r=>r>w), nxv=later.length?Math.min(...later):0;
  const note=$("unlock-note");
  if(note) note.innerHTML="Natures "+natN+"/"+NATURES.length+" · Scenarios "+scN+"/"+SCENARIOS.length+" · Marathon "+(w>=1?"✓":"🔒")+" · Brutal "+(w>=2?"✓":"🔒")+"<br>"+(nxv?"Next unlock at "+nxv+" win"+(nxv>1?"s":"")+": <strong>"+items.filter(i=>i[0]===nxv).map(i=>i[1]).join(", ")+"</strong>":"Everything unlocked.");
}
(function(){
  const rb=document.getElementById("btn-reset"); if(!rb) return; let armed=0;
  rb.onclick=()=>{
    if(!armed){ armed=1; rb.textContent="Click again to erase all progress"; setTimeout(()=>{armed=0;rb.textContent="Reset progress"},4000); return; }
    armed=0; rb.textContent="Reset progress";
    memTut=false; memUnlocks=null; memBest=null; memStats=null; memCamp=null; memSave=null;
    try{["veil_unlocks","veil_best","veil_stats","veil_camp","veil_save","veil_tut"].forEach(k=>localStorage.removeItem(k))}catch(e){}
    showTitleBest(); refreshLocks();
  };
  setTimeout(refreshLocks,0);
})();
