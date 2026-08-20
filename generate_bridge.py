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
            if max(abs(q),abs(r),abs(s))<=RADIUS:
                out.append((q,r))
    return out

CELLS=cells(); assert len(CELLS)==91
DATA={"radius":RADIUS,"cells":CELLS,"directions":DIRECTIONS}
WALL_NAMES=["forward","forstar","aftstar","aft","aftport","forport"]
WALL_LABELS=[x.upper() for x in WALL_NAMES]

CSS=r''':root{--bg:#03080c;--ink:#e9f2f6}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif}.bridge,.viewport{position:fixed;inset:0;overflow:hidden}.viewport{background:#03080c}#scene{position:absolute;inset:0;width:100%;height:100%;display:block}.hud{position:absolute;z-index:100;left:50%;top:14px;transform:translateX(-50%);padding:8px 12px;background:#071018dd;border:1px solid #294758;font-size:12px;letter-spacing:.08em;white-space:nowrap}.crosshair{position:absolute;z-index:90;left:50%;top:50%;width:18px;height:18px;transform:translate(-50%,-50%);opacity:.42}.crosshair:before,.crosshair:after{content:"";position:absolute;background:#d6f7ff}.crosshair:before{left:8px;width:1px;height:18px}.crosshair:after{top:8px;width:18px;height:1px}.control{position:absolute;z-index:110;display:grid;place-items:center;width:54px;height:54px;border:1px solid #63879c;background:#0d1d28dd;color:#dff8ff;font-size:28px;cursor:pointer;user-select:none}.control:hover{background:#173247}.fwd{left:50%;top:4px;transform:translateX(-50%)}.back{left:50%;bottom:6px;transform:translateX(-50%)}.left{left:8px;top:50%;transform:translateY(-50%)}.right{right:8px;top:50%;transform:translateY(-50%)}.tl1{left:8px;top:8px}.tr1{right:8px;top:8px}.bl2{left:8px;bottom:8px}.br2{right:8px;bottom:8px}.help{position:absolute;z-index:100;left:50%;bottom:12px;transform:translateX(-50%);font-size:11px;color:#89a5b6;background:#071018aa;padding:5px 8px;pointer-events:none}@media(max-width:700px){.control{width:46px;height:46px;font-size:24px}.help{display:none}}'''

JS=r'''const DATA=__DATA__;
const R=DATA.radius,SQ3=Math.sqrt(3),WALL_H=2.4,EYE_H=1.0,HFOV=100*Math.PI/180,NEAR=.05,STRIPS=96;
const dirs=DATA.directions,cellSet=new Set(DATA.cells.map(c=>`${c[0]},${c[1]}`));
let viewer={q:0,r:R,heading:0};
const canvas=document.getElementById('scene'),ctx=canvas.getContext('2d');
const valid=(q,r)=>cellSet.has(`${q},${r}`),center=(q,r)=>({x:SQ3*(q+r/2),y:1.5*r});
function vertex(c,k){const a=(30+60*k)*Math.PI/180;return{x:c.x+Math.cos(a),y:c.y+Math.sin(a)}}

const byDir=Array.from({length:6},()=>[]);
for(const[q,r]of DATA.cells){const c=center(q,r);for(let d=0;d<6;d++){const[,dq,dr]=dirs[d];if(!valid(q+dq,r+dr))byDir[d].push(vertex(c,(d+3)%6),vertex(c,(d+4)%6));}}
function farthest(P){let best=[P[0],P[1]],bd=-1;for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const dx=P[i].x-P[j].x,dy=P[i].y-P[j].y,d=dx*dx+dy*dy;if(d>bd){bd=d;best=[P[i],P[j]]}}return best}
const walls=byDir.map((p,d)=>{const[a,b]=farthest(p);return{a,b,d,src:`assets/wall-${dirs[d][0].toLowerCase()}.svg`,img:new Image()}});
let loaded=0;walls.forEach(w=>{w.img.onload=()=>{loaded++;render()};w.img.src=w.src});

function resize(){const dpr=Math.max(1,devicePixelRatio||1),W=innerWidth,H=innerHeight;canvas.width=Math.round(W*dpr);canvas.height=Math.round(H*dpr);canvas.style.width=W+'px';canvas.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);render()}
function camXY(p,z){const v=center(viewer.q,viewer.r),dx=p.x-v.x,dy=p.y-v.y,a=-viewer.heading*Math.PI/180;return{x:dx*Math.cos(a)-dy*Math.sin(a),y:z-EYE_H,z:-(dx*Math.sin(a)+dy*Math.cos(a))}}
function lerp(a,b,t){return{x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t}}
function project(c,W,H){const f=(W/2)/Math.tan(HFOV/2);return{x:W/2+c.x*f/c.z,y:H/2-c.y*f/c.z,z:c.z}}

function drawTriangle(img,s0,s1,s2,d0,d1,d2){
  const den=s0.x*(s1.y-s2.y)+s1.x*(s2.y-s0.y)+s2.x*(s0.y-s1.y);if(Math.abs(den)<1e-8)return;
  const a=(d0.x*(s1.y-s2.y)+d1.x*(s2.y-s0.y)+d2.x*(s0.y-s1.y))/den;
  const c=(d0.x*(s2.x-s1.x)+d1.x*(s0.x-s2.x)+d2.x*(s1.x-s0.x))/den;
  const e=(d0.x*(s1.x*s2.y-s2.x*s1.y)+d1.x*(s2.x*s0.y-s0.x*s2.y)+d2.x*(s0.x*s1.y-s1.x*s0.y))/den;
  const b=(d0.y*(s1.y-s2.y)+d1.y*(s2.y-s0.y)+d2.y*(s0.y-s1.y))/den;
  const d=(d0.y*(s2.x-s1.x)+d1.y*(s0.x-s2.x)+d2.y*(s1.x-s0.x))/den;
  const f=(d0.y*(s1.x*s2.y-s2.x*s1.y)+d1.y*(s2.x*s0.y-s0.x*s2.y)+d2.y*(s0.x*s1.y-s1.x*s0.y))/den;
  ctx.save();ctx.beginPath();ctx.moveTo(d0.x,d0.y);ctx.lineTo(d1.x,d1.y);ctx.lineTo(d2.x,d2.y);ctx.closePath();ctx.clip();ctx.setTransform(a,b,c,d,e,f);ctx.drawImage(img,0,0);ctx.restore();
}

function wallDepth(w){const m=lerp(w.a,w.b,.5);return camXY(m,EYE_H).z}
function drawWall(w,W,H){if(!w.img.complete||!w.img.naturalWidth)return;const iw=w.img.naturalWidth,ih=w.img.naturalHeight;
  for(let i=0;i<STRIPS;i++){
    let u0=i/STRIPS,u1=(i+1)/STRIPS,p0=lerp(w.a,w.b,u0),p1=lerp(w.a,w.b,u1),c0=camXY(p0,0),c1=camXY(p1,0);
    if(c0.z<NEAR&&c1.z<NEAR)continue;
    if(c0.z<NEAR||c1.z<NEAR){const t=(NEAR-c0.z)/(c1.z-c0.z);if(c0.z<NEAR){u0=u0+(u1-u0)*t;p0=lerp(w.a,w.b,u0);c0=camXY(p0,0)}else{u1=u0+(u1-u0)*t;p1=lerp(w.a,w.b,u1);c1=camXY(p1,0)}}
    const bl=project(camXY(p0,0),W,H),tl=project(camXY(p0,WALL_H),W,H),br=project(camXY(p1,0),W,H),tr=project(camXY(p1,WALL_H),W,H);
    const sx0=u0*iw,sx1=u1*iw;
    const sTL={x:sx0,y:0},sTR={x:sx1,y:0},sBR={x:sx1,y:ih},sBL={x:sx0,y:ih};
    drawTriangle(w.img,sTL,sTR,sBR,tl,tr,br);drawTriangle(w.img,sTL,sBR,sBL,tl,br,bl);
  }
}

function render(){const W=innerWidth,H=innerHeight;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,canvas.width,canvas.height);const dpr=Math.max(1,devicePixelRatio||1);ctx.setTransform(dpr,0,0,dpr,0,0);
  const grad=ctx.createLinearGradient(0,0,0,H);grad.addColorStop(0,'#02070b');grad.addColorStop(.49,'#02070b');grad.addColorStop(.491,'#0a1218');grad.addColorStop(1,'#0a1218');ctx.fillStyle=grad;ctx.fillRect(0,0,W,H);
  const visible=walls.filter(w=>wallDepth(w)>-1).sort((a,b)=>wallDepth(b)-wallDepth(a));visible.forEach(w=>drawWall(w,W,H));
  document.getElementById('hud').textContent=`POSITION ${viewer.q},${viewer.r} · HEADING ${Math.round(viewer.heading)}° · FOV 100°`;
}
function hi(){return((Math.round(viewer.heading/60)%6)+6)%6}function move(o){const d=(hi()+o+6)%6,[,dq,dr]=dirs[d],q=viewer.q+dq,r=viewer.r+dr;if(valid(q,r)){viewer.q=q;viewer.r=r;render()}else location.href='ouch.html'}function turn(d){viewer.heading=(viewer.heading+d+360)%360;render()}
fwd.onclick=()=>move(0);back.onclick=()=>move(3);left.onclick=()=>move(-1);right.onclick=()=>move(1);tl1.onclick=()=>turn(-60);tr1.onclick=()=>turn(60);bl2.onclick=()=>turn(-120);br2.onclick=()=>turn(120);
addEventListener('keydown',e=>{if(e.key==='ArrowUp')move(0);if(e.key==='ArrowDown')move(3);if(e.key==='ArrowLeft')move(-1);if(e.key==='ArrowRight')move(1)});addEventListener('resize',resize);resize();'''.replace('__DATA__',json.dumps(DATA,separators=(',',':')))

OUCH='''<!doctype html><html><head><meta charset="utf-8"><title>OUCH!</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#12090a;color:white;font-family:Arial}main{text-align:center}h1{font-size:8rem;color:#ff8a80}button{padding:1rem}</style></head><body><main><h1>OUCH!</h1><p>That fuckin' hurt!</p><button onclick="history.back()">I'll be okay, sir!</button></main></body></html>'''

def svg_wall(label,index):
    hue=188+index*4
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 700" preserveAspectRatio="none"><defs><linearGradient id="g" x2="0" y2="1"><stop stop-color="hsl({hue},35%,26%)"/><stop offset="1" stop-color="hsl({hue},45%,11%)"/></linearGradient><pattern id="p" width="160" height="700" patternUnits="userSpaceOnUse"><rect width="160" height="700" fill="none" stroke="#79a6b8" stroke-opacity=".20" stroke-width="3"/><path d="M20 80H140M20 620H140" stroke="#a8d1df" stroke-opacity=".15" stroke-width="2"/></pattern></defs><rect width="1600" height="700" fill="url(#g)"/><rect width="1600" height="700" fill="url(#p)"/><rect x="20" y="20" width="1560" height="660" rx="18" fill="none" stroke="#9cc7d7" stroke-opacity=".35" stroke-width="5"/><text x="800" y="365" fill="#d6f5ff" fill-opacity=".72" font-family="Arial" font-size="72" text-anchor="middle" letter-spacing="18">{label}</text></svg>'''

def build():
    ASSETS.mkdir(exist_ok=True)
    for i,(n,l) in enumerate(zip(WALL_NAMES,WALL_LABELS)):(ASSETS/f'wall-{n}.svg').write_text(svg_wall(l,i),encoding='utf-8')
    (ROOT/'bridge.css').write_text(CSS,encoding='utf-8');(ROOT/'bridge.js').write_text(JS,encoding='utf-8');(ROOT/'ouch.html').write_text(OUCH,encoding='utf-8')
    index='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Our Lovely System — Bridge</title><link rel="stylesheet" href="bridge.css"></head><body><main class="bridge"><section class="viewport"><canvas id="scene"></canvas></section><div class="crosshair"></div><div class="hud" id="hud"></div><button class="control fwd" id="fwd">↑</button><button class="control back" id="back">↓</button><button class="control left" id="left">←</button><button class="control right" id="right">→</button><button class="control tl1" id="tl1">↶</button><button class="control tr1" id="tr1">↷</button><button class="control bl2" id="bl2">⟲</button><button class="control br2" id="br2">⟳</button><div class="help">Movement: ↑ ↓ ← → · Turn: upper corners ±60° · lower corners ±120°</div></main><script src="bridge.js"></script></body></html>'''
    (ROOT/'index.html').write_text(index,encoding='utf-8');(ROOT/'GENERATION.txt').write_text('Six-wall Bridge rendered as perspective-mapped textured planes using triangle-strip subdivision.\n',encoding='utf-8')
if __name__=='__main__':build()
