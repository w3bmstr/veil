import re,json,math,numpy as np
src=open('veil_original.html',encoding='utf8').read()
P={}
for m in re.finditer(r'\{id:"(\w+)",name:"([^"]+)",pop:(\d+),climate:"(\w+)",science:(\d+),open:(\d+),links:\[([^\]]*)\]\}',src):
    P[m[1]]=dict(pop=int(m[3]),sci=int(m[5]),open=int(m[6]),links=re.findall(r'"(\w+)"',m[7]))
HID=['na_west','na_east','c_amer','s_amer','eu_west','eu_east','n_africa','w_africa','e_africa','mideast','c_asia','s_asia','se_asia','e_asia','oceania']
COL=[[90,180,70],[90,180,70],[140,190,60],[70,170,80],[80,170,200],[90,140,190],[190,160,70],[170,140,70],[190,150,60],[200,130,70],[150,110,190],[190,90,90],[70,180,150],[70,190,160],[150,100,170]]
T="""na_west|Western Canada|.5|.1|-5|-5|cold|1;US West|.45|.72|2|3|temp|4
na_east|Eastern Canada & Greenland|.62|.1|-2|-3|cold|2;US Midwest|.33|.55|0|0|temp|3;US East & South|.7|.78|2|2|temp|5
c_amer|Mexico|.25|.35|-10|-5|hot|3;Central America & Caribbean|.72|.72|-18|-10|hot|2
s_amer|Northern South America|.4|.08|-20|-10|hot|2;Brazil|.78|.4|-12|-5|hot|4;Andes|.2|.5|-15|-8|temp|2;Southern Cone|.45|.92|-5|0|temp|2
eu_west|Nordics & Britain|.45|.12|3|5|cold|2;Iberia & France|.22|.72|0|0|temp|3;Central Europe & Italy|.7|.62|2|2|temp|4
eu_east|Eastern Europe|.3|.62|-8|-5|temp|3;Western Russia|.68|.25|-5|-8|cold|3;Turkey & Caucasus|.42|.92|-10|-8|temp|2
n_africa|Maghreb|.18|.38|-10|-8|hot|2;Egypt & Sudan|.75|.55|-15|-10|hot|2
w_africa|Sahel|.5|.08|-20|-10|hot|2;Guinea Coast & Congo|.5|.75|-20|-5|hot|4
e_africa|Horn of Africa|.72|.12|-18|-10|hot|2;Great Lakes|.45|.45|-15|-5|hot|3;Southern Africa|.4|.92|-5|-5|temp|2
mideast|Levant & Iraq|.28|.2|-3|-5|hot|2;Arabian Peninsula|.52|.72|-3|-8|hot|2;Iran|.82|.28|-5|-12|temp|2
c_asia|Siberia|.5|.1|-3|-15|cold|1;Kazakh Steppe & Central Asia|.25|.62|-8|-8|temp|2;Mongolia & Xinjiang|.75|.62|-8|-10|temp|1
s_asia|Pakistan & Afghanistan|.12|.22|-12|-8|hot|3;India|.4|.58|-3|0|hot|8;Bangladesh & Myanmar|.85|.38|-12|-5|hot|3
se_asia|Indochina|.3|.18|-5|0|hot|3;Malay Archipelago West|.38|.75|-3|3|hot|3;Philippines & East Indonesia|.88|.5|-8|0|hot|2
e_asia|North China & Manchuria|.4|.22|3|0|temp|4;South China|.28|.72|2|3|temp|4;Japan & Korea|.9|.38|5|5|temp|3
oceania|Australia|.4|.45|5|5|hot|2;New Zealand & Pacific|.96|.85|5|5|temp|1"""
land=json.load(open('land_parent.json')); dots=[(land[i],land[i+1],land[i+2]) for i in range(0,len(land),3)]
R=[];newland=[]
for line in T.split('\n'):
    pid,rest=line.split('|',1); pi=HID.index(pid); p=P[pid]
    kids=[k.split('|') for k in (pid+'|'+rest).split(';')][0:0]
    parts=rest.split(';'); kids=[]
    for j,kp in enumerate(parts):
        f=kp.split('|') if j else ([x for x in line.split('|')[1:]] if False else None)
    # parse: first kid fields follow pid, others are full
    raw=line.split('|')[1:]; items=[]; cur=raw[:]
    flat='|'.join(raw).split(';'); items=[s.split('|') for s in flat]
    mine=[(c,r) for c,r,i in dots if i==pi]; xs=[c for c,r in mine]; ys=[r for c,r in mine]
    x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys); tw=sum(float(i[6]) for i in items)
    seeds=[(x0+float(i[1])*(x1-x0),y0+float(i[2])*(y1-y0)) for i in items]
    asg={}
    for c,r in mine:
        asg[(c,r)]=min(range(len(items)),key=lambda k:(c-seeds[k][0])**2+(r-seeds[k][1])**2)
    for k,it in enumerate(items):
        pts=[(c*10+5,r*10+5) for (c,r),a in asg.items() if a==k]
        assert len(pts)>=5,(it[0],len(pts))
        cx=sum(x for x,y in pts)/len(pts); cy=sum(y for x,y in pts)/len(pts)
        hub=min(pts,key=lambda q:(q[0]-cx)**2+(q[1]-cy)**2)
        v=((len(R)*37%31)-15)//3
        R.append(dict(id=re.sub('[^a-z]+','_',it[0].lower()).strip('_'),name=it[0],pop=max(3,round(p['pop']*float(it[6])/tw)),climate=it[5],science=max(15,min(98,p['sci']+int(it[3]))),open=max(15,min(98,p['open']+int(it[4]))),links=[],hub=list(hub),col=[max(30,min(255,c+v)) for c in COL[pi]],parent=pid,n=len(pts)))
        for (c,r),a in asg.items():
            if a==k: newland.append((c,r,len(R)-1))
idx={(c,r):i for c,r,i in newland}
adj=set()
for (c,r),i in idx.items():
    for dc in(-1,0,1):
        for dr in(-1,0,1):
            j=idx.get((c+dc,r+dr))
            if j is not None and j!=i: adj.add((min(i,j),max(i,j)))
big={}
for i,x in enumerate(R): 
    if x['parent'] not in big or x['pop']>R[big[x['parent']]]['pop']: big[x['parent']]=i
for a,pl in P.items():
    for b in pl['links']:
        if a<b: adj.add((min(big[a],big[b]),max(big[a],big[b])))
def comps():
    g={i:set() for i in range(len(R))}
    for a,b in adj: g[a].add(b);g[b].add(a)
    seen=set();cs=[]
    for s in g:
        if s in seen: continue
        st=[s];c=set()
        while st:
            u=st.pop()
            if u in c: continue
            c.add(u);st+=list(g[u]-c)
        seen|=c;cs.append(c)
    return cs
cs=comps()
while len(cs)>1:
    a,b=cs[0],cs[1]
    p=min(((i,j) for i in a for j in b),key=lambda q:(R[q[0]]['hub'][0]-R[q[1]]['hub'][0])**2+(R[q[0]]['hub'][1]-R[q[1]]['hub'][1])**2)
    adj.add((min(p),max(p))); cs=comps()
for a,b in adj: R[a]['links'].append(R[b]['id']);R[b]['links'].append(R[a]['id'])
land_set=set(idx.keys())
for k,x in enumerate(R):
    ds=[(c,r) for (c,r),i in idx.items() if i==k]
    coast=sum(1 for c,r in ds if sum(((c+dc,r+dr) in land_set) for dc in (-1,0,1) for dr in (-1,0,1) if dc or dr)<8)
    x['port']=coast/len(ds)>0.62; x['air']=False
for i in sorted(range(len(R)),key=lambda i:-R[i]['pop']*R[i]['science'])[:18]: R[i]['air']=True
print('ports',sum(x['port'] for x in R),'airports',sum(x['air'] for x in R))
for x in R: x.pop('parent');x.pop('n')
json.dump(R,open('regions.json','w'),separators=(',',':'),ensure_ascii=False)
json.dump([v for t in sorted(newland,key=lambda t:(t[1],t[0])) for v in t],open('land.json','w'),separators=(',',':'))
print(len(R),'regions,',len(adj),'links, avg',round(2*len(adj)/len(R),1),'per region; pop',sum(x['pop'] for x in R),'; min dots',min(sum(1 for t in newland if t[2]==i) for i in range(len(R))))
