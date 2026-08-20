from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
RADIUS = 5
DIRECTIONS = [("Forward",0,-1),("Forstar",1,-1),("Aftstar",1,0),("Aft",0,1),("Aftport",-1,1),("Forport",-1,0)]

def cells():
    out=[]
    for q in range(-RADIUS,RADIUS+1):
        for r in range(-RADIUS,RADIUS+1):
            s=-q-r
            if max(abs(q),abs(r),abs(s))<=RADIUS: out.append((q,r))
    return out
CELLS=cells(); assert len(CELLS)==91
DATA={"radius":RADIUS,"cells":CELLS,"directions":DIRECTIONS}
WALL_NAMES=["forward","forstar","aftstar","aft","aftport","forport"]
WALL_LABELS=[x.upper() for x in WALL_NAMES]

CSS=r''':root{--bg:#03080c;--ink:#e9f2f6}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif}.bridge,.viewport{position:fixed;inset:0;overflow:hidden}.viewport{background:linear-gradient(#02070b 0 49%,#0a1218 49% 100%)}#walls{position:absolute;inset:0}.wall{position:absolute;overflow:hidden;pointer-events:none;background:#10212c}.wall img{position:absolute;inset:0;width:100%;height:100%;object-fit:fill}.floorline{position:absolute;left:0;right:0;top:49%;border-top:1px solid #263d49}.hud{position:absolute;z-index:100;left:50%;top:14px;transform:translateX(-50%);padding:8px 12px;background:#071018dd;border:1px solid #294758;font-size:12px;letter-spacing:.08em}.crosshair{position:absolute;z-index:90;left:50%;top:50%;width:18px;height:18px;transform:translate(-50%,-50%);opacity:.42}.crosshair:before,.crosshair:after{content:"";position:absolute;background:#d6f7ff}.crosshair:before{left:8px;width:1px;height:18px}.crosshair:after{top:8px;width:18px;height:1px}.control{position:absolute;z-index:110;display:grid;place-items:center;width:54px;height:54px;border:1px solid #63879c;background:#0d1d28dd;color:#dff8ff;font-size:28px;cursor:pointer}.fwd{left:50%;top:4px;transform:translateX(-50%)}.back{left:50%;bottom:6px;transform:translateX(-50%)}.left{left:8px;top:50%;transform:translateY(-50%)}.right{right:8px;top:50%;transform:translateY(-50%)}.tl1{left:8px;top:8px}.tr1{right:8px;top:8px}.bl2{left:8px;bottom:8px}.br2{right:8px;bottom:8px}.help{position:absolute;z-index:100;left:50%;bottom:12px;transform:translateX(-50%);font-size:11px;color:#89a5b6}@media(max-width:700px){.control{width:46px;height:46px}.help{display:none}}'''

JS=r'''const DATA=__DATA__,R=DATA.radius,SQ3=Math.sqrt(3),WALL_H=2.4,EYE_H=1,HFOV=100*Math.PI/180,NEAR=.05;
const dirs=DATA.directions,cellSet=new Set(DATA.cells.map(c=>`${c[0]},${c[1]}`));let viewer={q:0,r:R,heading:0};
const valid=(q,r)=>cellSet.has(`${q},${r}`),center=(q,r)=>({x:SQ3*(q+r/2),y:1.5*r});
function vertex(c,k){const a=(30+60*k)*Math.PI/180;return{x:c.x+Math.cos(a),y:c.y+Math.sin(a)}}
const byDir=Array.from({length:6},()=>[]);for(const[q,r]of DATA.cells){const c=center(q,r);for(let d=0;d<6;d++){const[,dq,dr]=dirs[d];if(!valid(q+dq,r+dr))byDir[d].push(vertex(c,(d+3)%6),vertex(c,(d+4)%6))}}
function farthest(P){let z=[P[0],P[1]],bd=-1;for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){let dx=P[i].x-P[j].x,dy=P[i].y-P[j].y,d=dx*dx+dy*dy;if(d>bd){bd=d;z=[P[i],P[j]]}}return z}
const walls=byDir.map((p,d)=>{let[a,b]=farthest(p);return{a,b,d,src:`assets/wall-${dirs[d][0].toLowerCase()}.svg`}}),root=document.getElementById('walls');walls.forEach(w=>{let e=document.createElement('div');e.className='wall';let i=document.createElement('img');i.src=w.src;e.appendChild(i);root.appendChild(e)});
function cam(p,z){const v=center(viewer.q,viewer.r),dx=p.x-v.x,dy=p.y-v.y,a=-viewer.heading*Math.PI/180;return{x:dx*Math.cos(a)-dy*Math.sin(a),y:z-EYE_H,z:-(dx*Math.sin(a)+dy*Math.cos(a))}}
function clip(poly){let out=[];for(let i=0;i<poly.length;i++){let A=poly[i],B=poly[(i+1)%poly.length],ai=A.z>=NEAR,bi=B.z>=NEAR;if(ai)out.push(A);if(ai!==bi){let t=(NEAR-A.z)/(B.z-A.z);out.push({x:A.x+t*(B.x-A.x),y:A.y+t*(B.y-A.y),z:NEAR})}}return out}
function proj(p,W,H){let f=(W/2)/Math.tan(HFOV/2);return{x:W/2+p.x*f/p.z,y:H/2-p.y*f/p.z,d:p.z}}
function place(el,Q){let xs=Q.map(p=>p.x),ys=Q.map(p=>p.y),x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys),w=Math.max(1,x1-x0),h=Math.max(1,y1-y0);el.style.left=x0+'px';el.style.top=y0+'px';el.style.width=w+'px';el.style.height=h+'px';el.style.clipPath=`polygon(${Q.map(p=>`${(p.x-x0)/w*100}% ${(p.y-y0)/h*100}%`).join(',')})`}
function render(){let W=innerWidth,H=innerHeight,E=[...root.children];walls.forEach((w,i)=>{let poly=clip([cam(w.a,WALL_H),cam(w.b,WALL_H),cam(w.b,0),cam(w.a,0)]),el=E[i];if(poly.length<3){el.style.display='none';return}let q=poly.map(p=>proj(p,W,H));el.style.display='block';place(el,q);let dist=poly.reduce((s,p)=>s+p.z,0)/poly.length;el.style.zIndex=String(Math.max(1,10000-Math.round(dist*500)))});hud.textContent=`POSITION ${viewer.q},${viewer.r} · HEADING ${Math.round(viewer.heading)}° · FOV 100°`}
function hi(){return((Math.round(viewer.heading/60)%6)+6)%6}function move(o){let d=(hi()+o+6)%6,[,dq,dr]=dirs[d],q=viewer.q+dq,r=viewer.r+dr;if(valid(q,r)){viewer.q=q;viewer.r=r;render()}else location.href='ouch.html'}function turn(d){viewer.heading=(viewer.heading+d+360)%360;render()}
fwd.onclick=()=>move(0);back.onclick=()=>move(3);left.onclick=()=>move(-1);right.onclick=()=>move(1);tl1.onclick=()=>turn(-60);tr1.onclick=()=>turn(60);bl2.onclick=()=>turn(-120);br2.onclick=()=>turn(120);addEventListener('keydown',e=>{if(e.key==='ArrowUp')move(0);if(e.key==='ArrowDown')move(3);if(e.key==='ArrowLeft')move(-1);if(e.key==='ArrowRight')move(1)});addEventListener('resize',render);render();'''.replace('__DATA__',json.dumps(DATA,separators=(',',':')))

OUCH='''<!doctype html><html><head><meta charset="utf-8"><title>OUCH!</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#12090a;color:white;font-family:Arial}main{text-align:center}h1{font-size:8rem;color:#ff8a80}button{padding:1rem}</style></head><body><main><h1>OUCH!</h1><p>That fuckin' hurt!</p><button onclick="history.back()">I'll be okay, sir!</button></main></body></html>'''

def svg_wall(label,index):
    hue=188+index*4
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 700" preserveAspectRatio="none"><defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="hsl({hue},35%,26%)"/><stop offset="1" stop-color="hsl({hue},45%,11%)"/></linearGradient></defs><rect width="1600" height="700" fill="url(#g)"/><path d="M0 80H1600M0 620H1600" stroke="#9cc7d7" opacity=".2"/><text x="800" y="365" fill="#d6f5ff" opacity=".72" font-family="Arial" font-size="72" text-anchor="middle" letter-spacing="18">{label}</text></svg>'''

def build():
    ASSETS.mkdir(exist_ok=True)
    for i,(n,l) in enumerate(zip(WALL_NAMES,WALL_LABELS)):(ASSETS/f'wall-{n}.svg').write_text(svg_wall(l,i),encoding='utf-8')
    (ROOT/'bridge.css').write_text(CSS,encoding='utf-8');(ROOT/'bridge.js').write_text(JS,encoding='utf-8');(ROOT/'ouch.html').write_text(OUCH,encoding='utf-8')
    index='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Our Lovely System — Bridge</title><link rel="stylesheet" href="bridge.css"></head><body><main class="bridge"><section class="viewport"><div class="floorline"></div><div id="walls"></div></section><div class="crosshair"></div><div class="hud" id="hud"></div><button class="control fwd" id="fwd">↑</button><button class="control back" id="back">↓</button><button class="control left" id="left">←</button><button class="control right" id="right">→</button><button class="control tl1" id="tl1">↶</button><button class="control tr1" id="tr1">↷</button><button class="control bl2" id="bl2">⟲</button><button class="control br2" id="br2">⟳</button><div class="help">Movement: ↑ ↓ ← → · Turn: upper corners ±60° · lower corners ±120°</div></main><script src="bridge.js"></script></body></html>'''
    (ROOT/'index.html').write_text(index,encoding='utf-8');(ROOT/'GENERATION.txt').write_text('Six-wall first-person Bridge with near-plane polygon clipping.\n',encoding='utf-8')
if __name__=='__main__':build()
