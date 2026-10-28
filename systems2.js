function pr(f,fb){const a=state.regions.filter(f);return a.length?pick(a):fb()}
CHOICES.push(
 {id:"silence",w:()=>state.globalDetect>=25,mk:()=>({title:"A lab worker wants to talk",text:"They have seen the pattern and are weighing a public statement.",opts:[
  {l:"Silence them",d:"Costs 2 Influence. Detection −8.",run:()=>{state.influence=Math.max(0,state.influence-2);state.globalDetect=clamp(state.globalDetect-8,0,100)}},
  {l:"Let them talk",d:"Detection +6, but a public backlash slows research (Counter −4).",run:()=>{state.globalDetect=clamp(state.globalDetect+6,0,100);state.cure=Math.max(0,state.cure-4)}}]})},
 {id:"pilgrim",w:()=>state.regions.some(r=>r.climate==="hot"&&r.inf>3),mk:()=>{const r=pr(x=>x.climate==="hot"&&x.inf>3,topInf);return{title:"Pilgrims leave "+r.name,text:"A seasonal gathering is about to scatter across the region.",opts:[
  {l:"Follow the crowds",d:r.name+" +8 and two neighbors +4. Detection +4.",run:()=>{r.inf=clamp(r.inf+8,0,100);r.links.slice(0,2).forEach(id=>{const o=state.regions.find(x=>x.id===id);if(o)o.inf=clamp(o.inf+4,0,100)});state.globalDetect=clamp(state.globalDetect+4,0,100)}},
  {l:"Stay put",d:"Gain 2 Influence.",run:()=>{state.influence+=2}}]}}},
 {id:"rivalstrain",w:()=>state.turn>=10,mk:()=>({title:"A rival strain appears",text:"Another pathogen is competing for the same hosts.",opts:[
  {l:"Outcompete it",d:"Transmission +0.15, Stability −0.1.",run:()=>{state.traits.spread+=0.15;state.stability=clamp(state.stability-0.1,0.12,1)}},
  {l:"Coexist quietly",d:"Concealment +0.1, Counter +3.",run:()=>{state.traits.conceal=clamp(state.traits.conceal+0.1,0.35,2.8);state.cure=clamp(state.cure+3,0,100)}}]})},
 {id:"blackmarket",w:()=>state.cure>=25,mk:()=>({title:"Black-market antivirals",text:"A shady supplier is moving unlicensed treatments.",opts:[
  {l:"Poison the supply",d:"Counter −8, but detection +10.",run:()=>{state.cure=Math.max(0,state.cure-8);state.globalDetect=clamp(state.globalDetect+10,0,100)}},
  {l:"Ignore it",d:"Gain 2 Influence.",run:()=>{state.influence+=2}}]})},
 {id:"journalist",w:()=>state.globalDetect>=18,mk:()=>({title:"A journalist is digging",text:"They are getting close to a connection between clusters.",opts:[
  {l:"Feed false leads",d:"Costs 2 Influence. Detection −8.",run:()=>{state.influence=Math.max(0,state.influence-2);state.globalDetect=clamp(state.globalDetect-8,0,100)}},
  {l:"Go to ground",d:"Concealment +0.08, detection +2.",run:()=>{state.traits.conceal=clamp(state.traits.conceal+0.08,0.35,2.8);state.globalDetect=clamp(state.globalDetect+2,0,100)}}]})},
 {id:"upload",w:()=>state.cure>=10,mk:()=>({title:"A genome gets uploaded",text:"A lab is about to share your sequence with the world.",opts:[
  {l:"Corrupt the data",d:"Counter −6, Stability −0.08.",run:()=>{state.cure=Math.max(0,state.cure-6);state.stability=clamp(state.stability-0.08,0.12,1)}},
  {l:"Let it go",d:"Counter +4, but you gain 3 Influence.",run:()=>{state.cure=clamp(state.cure+4,0,100);state.influence+=3}}]})},
 {id:"gala",w:()=>infectedCount()>=4,mk:()=>({title:"A charity gala goes global",text:"Delegates from everywhere are flying home tonight.",opts:[
  {l:"Hop aboard",d:"Four random regions +4. Detection +4.",run:()=>{for(let i=0;i<4;i++){const r=pick(state.regions);r.inf=clamp(r.inf+4,0,100)}state.globalDetect=clamp(state.globalDetect+4,0,100)}},
  {l:"Pass",d:"Gain 2 Influence.",run:()=>{state.influence+=2}}]})},
 {id:"climate",w:()=>state.turn>=8,mk:()=>({title:"A climate shift",text:"Weather patterns are changing where your pattern thrives.",opts:[
  {l:"Adapt to the heat",d:"Hot regions +4, cold regions −3.",run:()=>{state.regions.forEach(r=>{if(r.inf>1){if(r.climate==="hot")r.inf=clamp(r.inf+4,0,100);else if(r.climate==="cold")r.inf=Math.max(0,r.inf-3)}})}},
  {l:"Adapt to the cold",d:"Cold regions +4, hot regions −3.",run:()=>{state.regions.forEach(r=>{if(r.inf>1){if(r.climate==="cold")r.inf=clamp(r.inf+4,0,100);else if(r.climate==="hot")r.inf=Math.max(0,r.inf-3)}})}}]})},
 {id:"camp",w:()=>state.regions.some(r=>r.sealed>30),mk:()=>{const r=pr(x=>x.sealed>30,()=>state.regions.slice().sort((a,b)=>b.sealed-a.sealed)[0]);return{title:"A quarantine camp opens in "+r.name,text:"It holds thousands behind the new border.",opts:[
  {l:"Infiltrate the camp",d:r.name+": seals −25, detection +10.",run:()=>{r.sealed=Math.max(0,r.sealed-25);r.det=clamp(r.det+10,0,100)}},
  {l:"Avoid it",d:"Detection −3.",run:()=>{state.globalDetect=Math.max(0,state.globalDetect-3)}}]}}},
 {id:"decree",w:()=>state.globalDetect>=30,mk:()=>({title:"An emergency decree",text:"Leaders are ready to act fast and loud.",opts:[
  {l:"Exploit the panic",d:"Gain 4 Influence, detection +6.",run:()=>{state.influence+=4;state.globalDetect=clamp(state.globalDetect+6,0,100)}},
  {l:"Lie low",d:"All seals −8.",run:()=>{state.regions.forEach(r=>{r.sealed=Math.max(0,r.sealed-8)})}}]})}
);
let MARA=false, CAMP=null, memCamp=null;
const PTn=()=>MARA?PT+14:PT;
function setMode(m,d){ MARA=!!m; if(d) DIFF=d; }
function grantPerk(id){ state.perks[id]=true;
  if(id==="quiet") state.traits.conceal=clamp(state.traits.conceal+0.45,0.35,2.8);
  if(id==="shell") state.traits.resilience=clamp(state.traits.resilience+0.4,0.4,2.8);
  if(id==="aero") state.traits.spread+=0.3;
  if(id==="memory") state.stability=clamp(state.stability+0.3,0.12,1);
  if(id==="rapid") state.traits.spread+=0.25;
  if(id==="overclock"){ state.traits.spread+=0.2; state.stability=clamp(state.stability-0.15,0.12,1); } }
const CHAPTERS=[
 {n:"First Breath",sc:"bloom",nat:"spore",d:0.8,brief:"A quiet start. Learn the rhythm: seed, spread, stay unseen.",mod:()=>{}},
 {n:"Crossing Water",sc:"ghost",nat:"vector",d:1.2,brief:"Ports and airports matter now, and some borders are already tight.",mod:()=>{state.cure=12;state.regions.forEach((r,i)=>{if(i%4===0)r.sealed=30})}},
 {n:"Cold Front",sc:"iron",nat:"viral",d:1.1,brief:"Governments are prepared. The countermeasure starts ahead of you.",mod:()=>{state.cure=15}},
 {n:"Glass Houses",sc:"fire",nat:"spore",d:1.35,brief:"Fast and loud. The world is already watching, so spread before it reacts.",mod:()=>{state.globalDetect=30;state.cure=20}},
 {n:"Iron Curtain",sc:"iron",nat:"spore",d:1.35,brief:"The halfway point: a hardened world and an early countermeasure.",mod:()=>{state.cure=25;state.globalDetect=18;state.regions.forEach((r,i)=>{if(i%4===0)r.sealed=25})}},
 {n:"Rising Tide",sc:"monsoon",nat:"fungal",d:1.3,brief:"Hot, wet and crowded. Your new strain loves it, and so do the labs.",mod:()=>{state.cure=18;state.globalDetect=14}},
 {n:"Deep Freeze",sc:"frostbite",nat:"parasite",d:1.2,brief:"A cold world and a hidden strain that never flies. Go overland.",mod:()=>{state.cure=12}},
 {n:"Fortress World",sc:"fortress",nat:"synthetic",d:1.25,brief:"Sealed borders and an evolving strain. Outgrow the walls.",mod:()=>{state.cure=28;state.globalDetect=18}},
 {n:"Open Skies",sc:"skies",nat:"dormant",d:1.4,brief:"Every airport is watching. Move fast before they connect the dots.",mod:()=>{state.cure=30;state.globalDetect=25}},
 {n:"The Last Veil",sc:"iron",nat:"synthetic",d:1.4,brief:"The final test: a ruthless world, an early cure, no second chances.",mod:()=>{state.cure=30;state.globalDetect=25;state.regions.forEach((r,i)=>{if(i%3===0)r.sealed=30})}}
];
function loadCamp(){ let o=memCamp; try{const j=localStorage.getItem("veil_camp"); if(j) o=JSON.parse(j)}catch(e){} o=o||{}; return {done:CHAPTERS.map((_,i)=>!!(o.done&&o.done[i])),carry:o.carry||{}}; }
function saveCamp(C){ memCamp=C; try{localStorage.setItem("veil_camp",JSON.stringify(C))}catch(e){} }
function startChapter(i){
  const c=CHAPTERS[i], C=loadCamp(); CAMP=i; MARA=false; DIFF=c.d; selectedScenario=c.sc; selectedNature=c.nat;
  document.querySelectorAll(".lenbtn").forEach(b=>b.classList.toggle("on",b.dataset.m==="0"));
  newGame(); c.mod(); (C.carry[i]||[]).forEach(grantPerk);
  log("CHAPTER "+(i+1)+" — "+c.n+": "+c.brief,"warn");
  if(C.carry[i]&&C.carry[i].length) log("You carry over: "+C.carry[i].map(id=>MUT_OPTIONS.find(m=>m.id===id).name).join(", ")+".","good");
  $("modal-camp").classList.add("hidden"); renderAll();
}
function openCamp(){
  const C=loadCamp(), box=$("camp-list"); box.innerHTML="";
  CHAPTERS.forEach((c,i)=>{ const open=i===0||C.done[i-1], row=document.createElement("button"), a=document.createElement("strong"), b=document.createElement("span");
    row.className="pillbtn"; a.textContent=(C.done[i]?"✓ ":open?"":"🔒 ")+"Chapter "+(i+1)+": "+c.n; b.textContent=open?c.brief:"Complete the previous chapter to unlock."; row.append(a,document.createElement("br"),b);
    if(open) row.onclick=()=>startChapter(i); else row.setAttribute("aria-disabled","true"); box.appendChild(row); });
  $("modal-camp").classList.remove("hidden"); if(box.firstChild&&box.firstChild.focus) box.firstChild.focus();
}
function campaignEnd(win){
  if(CAMP===null) return;
  const C=loadCamp(), ch=CAMP, el=$("end-stats");
  if(win){ C.done[ch]=true; if(ch<CHAPTERS.length-1) C.carry[ch+1]=Object.keys(state.perks).slice(0,Math.min(4,2+Math.floor(ch/3))); saveCamp(C);
    el.textContent+=" · Campaign: Chapter "+(ch+1)+" complete"+(ch<CHAPTERS.length-1?" — Chapter "+(ch+2)+" unlocked"+(C.carry[ch+1].length?", carrying "+C.carry[ch+1].map(id=>MUT_OPTIONS.find(m=>m.id===id).name).join(" & "):""):"");
    if(C.done.every(Boolean)){ const S=loadStats(); S.ach["Campaigner: finished the campaign"]=1; saveStats(S); el.textContent+=" — CAMPAIGN COMPLETE ★"; } }
  else el.textContent+=" · Campaign: Chapter "+(ch+1)+" failed. Retry from the Campaign menu.";
}
(function(){
  const g=id=>document.getElementById(id);
  if(g("btn-camp")) g("btn-camp").onclick=openCamp;
  if(g("camp-close")) g("camp-close").onclick=()=>g("modal-camp").classList.add("hidden");
  if(g("btn-start")&&g("btn-start").addEventListener) g("btn-start").addEventListener("click",()=>{CAMP=null});
  document.querySelectorAll(".lenbtn").forEach(b=>{b.onclick=()=>{if(b.getAttribute("aria-disabled")==="true")return;MARA=b.dataset.m==="1";document.querySelectorAll(".lenbtn").forEach(x=>x.classList.toggle("on",x===b))}});
})();
