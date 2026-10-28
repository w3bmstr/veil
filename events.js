function evt(title,text,cls){ (state.marks=state.marks||[]).push({t:state.turn,x:title}); log("EVENT — "+title+": "+text,cls); toast(title); flash(cls==="bad"?"bad":"good"); sfx(cls==="bad"?"bad":"event"); }
const EVENTS=[
 {w:()=>state.globalDetect>=22,run:()=>{const t=state.regions.filter(r=>r.inf>2).sort((a,b)=>b.det-a.det).slice(0,3);t.forEach(r=>r.sealed=clamp(r.sealed+28,0,94));evt("Flight ban","Travel suspended out of "+(t.map(r=>r.name).join(", ")||"the hotspots")+".","bad")}},
 {w:()=>state.cure>=30,run:()=>{state.cureSlow=4;evt("Riots over restrictions","Lab operations disrupted for four cycles.","good")}},
 {w:()=>state.globalDetect>=35,run:()=>{state.cure=clamp(state.cure+7,0,100);evt("Emergency summit","Nations pool research. Counter +7.","bad")}},
 {w:()=>state.regions.some(r=>r.climate==="hot"&&r.inf>1),run:()=>{state.regions.forEach(r=>{if(r.climate==="hot"&&r.inf>1)r.inf=clamp(r.inf+3,0,100)});evt("Heatwave","Hot regions see a surge in cases.","good")}},
 {w:()=>state.regions.some(r=>r.climate==="cold"&&r.inf>1),run:()=>{state.regions.forEach(r=>{if(r.climate==="cold"&&r.inf>1)r.inf=clamp(r.inf+3,0,100)});evt("Cold snap","Crowding indoors helps you in the north.","good")}},
 {w:()=>infectedCount()>=2,run:()=>{const r=pick(state.regions.filter(x=>x.inf>1));r.inf=clamp(r.inf+8,0,100);r.det=clamp(r.det+6,0,100);evt("Festival in "+r.name,"A mass gathering spikes cases and attention.","good")}},
 {w:()=>state.globalDetect<60&&state.globalDetect>8,run:()=>{state.globalDetect=clamp(state.globalDetect+9,0,100);evt("Whistleblower","A lab insider talks. Detection +9.","bad")}},
 {w:()=>state.cure>=20&&state.cure<80,run:()=>{state.cure=clamp(state.cure+8,0,100);evt("Research breakthrough","A new assay speeds everything up. Counter +8.","bad")}},
 {w:()=>state.cure>=30,run:()=>{state.cure=Math.max(0,state.cure-8);evt("Funding scandal","A major cure program collapses. Counter −8.","good")}},
 {w:()=>state.regions.some(r=>r.sealed>40),run:()=>{const r=pick(state.regions.filter(x=>x.sealed>40));r.sealed=Math.max(0,r.sealed-25);evt("Aid convoy","A border reopens around "+r.name+".","good")}},
 {w:()=>true,run:()=>{state.regions.forEach(r=>{r.sealed=clamp(r.sealed-10,0,94)});evt("Border queues collapse","Checkpoints are overwhelmed everywhere.","good")}},
 {w:()=>state.globalDetect>=30&&state.regions.some(r=>r.inf>2),run:()=>{const r=pick(state.regions.filter(x=>x.inf>2));r.sealed=clamp(r.sealed+30,0,94);evt("Lockdown in "+r.name,"Authorities seal the region.","bad")}}
];
EVENTS.push(
 {w:()=>state.regions.some(r=>r.climate==="hot"),run:()=>{const t=state.regions.filter(r=>r.climate==="hot"),a=pick(t),b=pick(t);[a,b].forEach(r=>{r.sealed=Math.max(0,r.sealed-12);if(r.inf>1)r.inf=clamp(r.inf+3,0,100)});evt("Monsoon floods","Roads wash out around "+a.name+" and "+b.name+"; checkpoints fail.","good")}},
 {w:()=>state.cure>=15,run:()=>{state.cureSlow=3;evt("Cyberattack on labs","Research systems go dark for three cycles.","good")}},
 {w:()=>state.regions.some(r=>r.climate==="hot"&&r.inf>1),run:()=>{const r=pick(state.regions.filter(x=>x.climate==="hot"&&x.inf>1));r.inf=clamp(r.inf+6,0,100);r.det=clamp(r.det+4,0,100);evt("Pilgrimage season in "+r.name,"Huge crowds gather for days.","good")}},
 {w:()=>state.regions.some(r=>r.airClosed>0),run:()=>{state.regions.forEach(r=>{r.airClosed=0});evt("Airline bailout","Governments reopen the skies.","good")}},
 {w:()=>state.regions.some(r=>r.port),run:()=>{state.regions.forEach(r=>{if(r.port)r.portClosed=Math.max(r.portClosed||0,4)});evt("Port strike","Dockworkers walk out. Ports close for four cycles.","bad")}},
 {w:()=>state.globalDetect>=20,run:()=>{const r=pick(state.regions);r.sealed=clamp(r.sealed+15,0,94);evt("Nationalist election in "+r.name,"The winners promise to shut the borders.","bad")}},
 {w:()=>state.regions.some(r=>r.air&&r.inf>3),run:()=>{state.regions.forEach(r=>{r.airClosed=0});state.globalDetect=clamp(state.globalDetect+3,0,100);evt("Relief flights","Aid planes cross every border. Detection +3.","good")}},
 {w:()=>state.cure>=10&&state.cure<85,run:()=>{state.cure=clamp(state.cure+6,0,100);state.globalDetect=clamp(state.globalDetect+6,0,100);evt("Sequencing milestone","A lab publishes your genome map. Counter +6, detection +6.","bad")}},
 {w:()=>state.globalDetect>=15,run:()=>{state.globalDetect=Math.max(0,state.globalDetect-7);evt("Mistaken for seasonal flu","Headlines downplay the cases. Detection −7.","good")}},
 {w:()=>state.cure>=25,run:()=>{state.cure=Math.max(0,state.cure-5);evt("Reagent shortage","A key supply chain snaps. Counter −5.","good")}},
 {w:()=>infectedCount()>=3&&state.regions.some(r=>r.inf>1),run:()=>{const r=pick(state.regions.filter(x=>x.inf>1));r.inf=clamp(r.inf+7,0,100);r.det=clamp(r.det+8,0,100);evt("Tournament in "+r.name,"Packed stadiums spike cases and attention.","good")}},
 {w:()=>state.globalDetect>=25,run:()=>{state.globalDetect=clamp(state.globalDetect+7,0,100);state.cure=clamp(state.cure+3,0,100);evt("Outbreak map goes viral","Millions watch the spread live. Detection +7, Counter +3.","bad")}}
);
