const PREF_DEF={master:false,music:true,sfx:true,musicVol:0.5,sfxVol:0.7,cb:false,rm:false,big:false};
let PREFS=Object.assign({},PREF_DEF), memPrefs=null;
const AU={sfx:null,mus:null,noise:null}, MUS={timer:0,next:0}, SFXT={};
function loadPrefs(){ try{ const j=localStorage.getItem("veil_prefs"); if(j) PREFS=Object.assign({},PREF_DEF,JSON.parse(j)); else if(memPrefs) PREFS=Object.assign({},PREF_DEF,memPrefs); }catch(e){ if(memPrefs) PREFS=Object.assign({},PREF_DEF,memPrefs); } }
function savePrefs(){ memPrefs=Object.assign({},PREFS); try{ localStorage.setItem("veil_prefs",JSON.stringify(PREFS)); }catch(e){} }
function ensureAudio(){
  if(!audioCtx){
    audioCtx=new (window.AudioContext||window.webkitAudioContext)(); const c=audioCtx;
    AU.sfx=c.createGain(); AU.mus=c.createGain(); AU.sfx.connect(c.destination); AU.mus.connect(c.destination);
    const n=c.createBuffer(1,c.sampleRate,c.sampleRate), d=n.getChannelData(0); for(let i=0;i<d.length;i++) d[i]=Math.random()*2-1; AU.noise=n; applyVol();
  }
  if(audioCtx.state==="suspended") audioCtx.resume();
  return {ctx:audioCtx,sfx:AU.sfx,mus:AU.mus,noise:AU.noise};
}
function applyVol(){ if(AU.sfx) AU.sfx.gain.value=PREFS.sfxVol; if(AU.mus) AU.mus.gain.value=PREFS.musicVol; }
function beep(freq,dur,type){
  if(!soundOn||!PREFS.sfx) return;
  try{ const A=ensureAudio(), t=A.ctx.currentTime, o=A.ctx.createOscillator(), g=A.ctx.createGain(), d=dur||0.08;
    o.type=type||"sine"; o.frequency.value=freq; g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(0.1,t+0.008); g.gain.exponentialRampToValueAtTime(0.0008,t+d);
    o.connect(g); g.connect(A.sfx); o.start(t); o.stop(t+d+0.03); }catch(e){}
}
function tone(f,dur,type,vol,delay,slide){
  const A=ensureAudio(), t=A.ctx.currentTime+(delay||0), o=A.ctx.createOscillator(), g=A.ctx.createGain();
  o.type=type||"sine"; o.frequency.setValueAtTime(f,t); if(slide) o.frequency.exponentialRampToValueAtTime(slide,t+dur);
  g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(vol||0.1,t+0.01); g.gain.exponentialRampToValueAtTime(0.0008,t+dur);
  o.connect(g); g.connect(A.sfx); o.start(t); o.stop(t+dur+0.03);
}
function swoosh(dur,f0,f1,vol){
  const A=ensureAudio(), t=A.ctx.currentTime, s=A.ctx.createBufferSource(), bp=A.ctx.createBiquadFilter(), g=A.ctx.createGain();
  s.buffer=A.noise; bp.type="bandpass"; bp.Q.value=2; bp.frequency.setValueAtTime(f0,t); bp.frequency.exponentialRampToValueAtTime(f1,t+dur);
  g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(vol,t+dur*0.3); g.gain.exponentialRampToValueAtTime(0.0008,t+dur);
  s.connect(bp); bp.connect(g); g.connect(A.sfx); s.start(t); s.stop(t+dur+0.05);
}
function sfx(name){
  if(!soundOn||!PREFS.sfx) return; const now=Date.now(); if(SFXT[name]&&now-SFXT[name]<120) return; SFXT[name]=now;
  try{ switch(name){
    case "ui": tone(900,0.04,"triangle",0.05); break;
    case "tick": tone(196,0.07,"sine",0.08); tone(294,0.09,"sine",0.05,0.04); break;
    case "event": tone(330,0.14,"triangle",0.09); tone(247,0.22,"triangle",0.08,0.1); break;
    case "bad": tone(150,0.34,"sawtooth",0.07,0,70); swoosh(0.3,600,120,0.05); break;
    case "choice": tone(660,0.12,"sine",0.08); tone(880,0.14,"sine",0.08,0.09); tone(1320,0.24,"sine",0.07,0.18); break;
    case "flight": swoosh(0.7,500,2600,0.07); break;
    case "purge": tone(110,0.3,"sine",0.12,0,48); swoosh(0.25,900,200,0.05); break;
    case "win": [523,659,784,1047].forEach((f,i)=>tone(f,0.5,"triangle",0.09,i*0.13)); break;
    case "lose": [220,175,147,110].forEach((f,i)=>tone(f,0.7,"sawtooth",0.06,i*0.2)); break;
    case "unlock": [1047,1319,1568,2093].forEach((f,i)=>tone(f,0.25,"sine",0.06,i*0.07)); break;
  } }catch(e){}
}
const CHORDS=[[57,60,64],[53,57,60],[50,53,57],[52,56,59]], PENT=[0,3,5,7,10,12,15,17]; let beatN=0;
function mtof(m){ return 440*Math.pow(2,(m-69)/12); }
function tension(){ if(!state||state.dead||state.won) return 0.1; return clamp((state.globalDetect*0.5+state.cure*0.8)/100+(state.cure>60?0.2:0),0,1); }
function padChord(A,t,notes,dur,vol,cut){
  const f=A.ctx.createBiquadFilter(), g=A.ctx.createGain(); f.type="lowpass"; f.frequency.value=cut;
  g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(vol,t+dur*0.35); g.gain.linearRampToValueAtTime(0.0001,t+dur+1.2); f.connect(g); g.connect(A.mus);
  notes.forEach((m,i)=>{ const o=A.ctx.createOscillator(); o.type=i%2?"triangle":"sine"; o.frequency.value=mtof(m); o.detune.value=(i-1)*6; o.connect(f); o.start(t); o.stop(t+dur+1.3); });
}
function pluck(A,t,m,vol,cut){
  const o=A.ctx.createOscillator(), f=A.ctx.createBiquadFilter(), g=A.ctx.createGain(); o.type="triangle"; o.frequency.value=mtof(m); f.type="lowpass"; f.frequency.value=cut;
  g.gain.setValueAtTime(0.0001,t); g.gain.linearRampToValueAtTime(vol,t+0.01); g.gain.exponentialRampToValueAtTime(0.0008,t+0.6); o.connect(f); f.connect(g); g.connect(A.mus); o.start(t); o.stop(t+0.65);
}
function thump(A,t,vol){
  const o=A.ctx.createOscillator(), g=A.ctx.createGain(); o.type="sine"; o.frequency.setValueAtTime(90,t); o.frequency.exponentialRampToValueAtTime(40,t+0.18);
  g.gain.setValueAtTime(vol,t); g.gain.exponentialRampToValueAtTime(0.0008,t+0.22); o.connect(g); g.connect(A.mus); o.start(t); o.stop(t+0.25);
}
function scheduleBeat(A,t){
  const tn=tension(), ch=CHORDS[Math.floor(beatN/8)%4], b=beatN%8;
  if(b===0){ padChord(A,t,ch,4.0,0.05,500+tn*1400); padChord(A,t,[ch[0]-24],4.0,0.07,220); if(tn>0.75) padChord(A,t,[ch[0]+1,ch[0]+7],4.0,0.025,900); }
  if(Math.random()<0.25+0.55*tn) pluck(A,t,ch[0]+12+PENT[Math.floor(Math.random()*PENT.length)],0.035+0.02*tn,900+tn*2200);
  if(tn>0.55&&b%2===0) thump(A,t,0.07*tn);
  beatN++;
}
function musicTick(){
  if(!soundOn||!PREFS.music||document.hidden){ MUS.next=0; return; }
  try{ const A=ensureAudio(), t=A.ctx.currentTime; if(!MUS.next||MUS.next<t) MUS.next=t+0.1; while(MUS.next<t+0.7){ scheduleBeat(A,MUS.next); MUS.next+=0.5; } }catch(e){}
}
function audioSync(){
  if(soundOn){ try{ ensureAudio(); }catch(e){} if(!MUS.timer) MUS.timer=setInterval(musicTick,200); }
  else if(MUS.timer){ clearInterval(MUS.timer); MUS.timer=0; MUS.next=0; }
}
function applyPrefs(){
  const b=document.body; b.classList.toggle("cb",!!PREFS.cb); b.classList.toggle("rm",!!PREFS.rm); b.classList.toggle("big",!!PREFS.big);
  calm=(window.matchMedia&&matchMedia("(prefers-reduced-motion:reduce)").matches)||!!PREFS.rm; applyVol();
  const mt=document.querySelector(".map-title"); if(mt) mt.textContent=PREFS.cb?"World — yellow glow = presence · purple = detection · white dashed = sealed":"World — green glow = presence · blue = detection · amber = sealed";
  const sp=document.querySelectorAll(".legend span"); if(sp.length>=4){ sp[1].textContent=PREFS.cb?"· Yellow glow = presence":"· Green glow = presence"; sp[2].textContent=PREFS.cb?"· Purple ring = detected":"· Blue ring = detected"; sp[3].textContent=PREFS.cb?"· White dashed ring = sealed":"· Amber ring = sealed"; } if(state&&typeof drawLand==="function") drawLand();
}
function setMaster(v){
  soundOn=!!v; PREFS.master=soundOn; savePrefs(); const bs=document.getElementById("btn-sound");
  if(bs){ bs.textContent=soundOn?"Sound: On":"Sound: Off"; bs.classList.toggle("on",soundOn); } const sm=document.getElementById("set-master"); if(sm) sm.checked=soundOn; audioSync();
}
function syncSettingsUI(){
  const g=id=>document.getElementById(id), set=(id,k,v)=>{ const e=g(id); if(e) e[k]=v; };
  set("set-master","checked",soundOn); set("set-music","checked",PREFS.music); set("set-sfx","checked",PREFS.sfx); set("set-cb","checked",PREFS.cb); set("set-rm","checked",PREFS.rm); set("set-big","checked",PREFS.big);
  set("set-musicvol","value",Math.round(PREFS.musicVol*100)); set("set-sfxvol","value",Math.round(PREFS.sfxVol*100));
}
function openSettings(){ syncSettingsUI(); const m=document.getElementById("modal-settings"); if(m){ m.classList.remove("hidden"); const c=document.getElementById("set-close"); if(c&&c.focus) c.focus(); } }
setTimeout(()=>{
  loadPrefs(); applyPrefs(); const g=id=>document.getElementById(id);
  if(PREFS.master){ soundOn=true; const bs=g("btn-sound"); if(bs){ bs.textContent="Sound: On"; bs.classList.add("on"); } }
  syncSettingsUI();
  if(g("btn-settings")) g("btn-settings").onclick=openSettings;
  if(g("set-close")) g("set-close").onclick=()=>g("modal-settings").classList.add("hidden");
  const bind=(id,fn)=>{ const e=g(id); if(e) e.onchange=e.oninput=fn; };
  bind("set-master",()=>setMaster(g("set-master").checked));
  bind("set-music",()=>{ PREFS.music=g("set-music").checked; savePrefs(); });
  bind("set-sfx",()=>{ PREFS.sfx=g("set-sfx").checked; savePrefs(); });
  bind("set-musicvol",()=>{ PREFS.musicVol=g("set-musicvol").value/100; savePrefs(); applyVol(); });
  bind("set-sfxvol",()=>{ PREFS.sfxVol=g("set-sfxvol").value/100; savePrefs(); applyVol(); });
  bind("set-cb",()=>{ PREFS.cb=g("set-cb").checked; savePrefs(); applyPrefs(); });
  bind("set-rm",()=>{ PREFS.rm=g("set-rm").checked; savePrefs(); applyPrefs(); });
  bind("set-big",()=>{ PREFS.big=g("set-big").checked; savePrefs(); applyPrefs(); });
  if(document.addEventListener){
    document.addEventListener("click",e=>{ const b=e.target&&e.target.closest?e.target.closest("button,[role=button]"):null; if(b&&!b.disabled&&!b.classList.contains("mut-btn")&&b.id!=="btn-advance") sfx("ui"); },true);
    document.addEventListener("pointerdown",()=>{ if(soundOn) audioSync(); },{once:true});
    document.addEventListener("visibilitychange",()=>{ MUS.next=0; });
  }
  if(soundOn) audioSync();
},0);
