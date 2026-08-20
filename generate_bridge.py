from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
RADIUS = 5

DIRECTIONS = [
    ("Forward", 0, -1),
    ("Forstar", 1, -1),
    ("Aftstar", 1, 0),
    ("Aft", 0, 1),
    ("Aftport", -1, 1),
    ("Forport", -1, 0),
]


def cells():
    out = []
    for q in range(-RADIUS, RADIUS + 1):
        for r in range(-RADIUS, RADIUS + 1):
            s = -q - r
            if max(abs(q), abs(r), abs(s)) <= RADIUS:
                out.append((q, r))
    return out


CELLS = cells()
assert len(CELLS) == 91
DATA = {"radius": RADIUS, "cells": CELLS, "directions": DIRECTIONS}

WALL_NAMES = ["forward", "forstar", "aftstar", "aft", "aftport", "forport"]
WALL_LABELS = ["FORWARD", "FORSTAR", "AFTSTAR", "AFT", "AFTPORT", "FORPORT"]

CSS = r''':root{--bg:#03080c;--ink:#e9f2f6;--line:#68879a;--glow:#bfeeff}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif}.bridge,.viewport{position:fixed;inset:0;overflow:hidden}.viewport{background:linear-gradient(#02070b 0 49%,#0a1218 49% 100%)}#walls{position:absolute;inset:0}.wall{position:absolute;overflow:hidden;transform-origin:0 0;background:#10212c;pointer-events:none}.wall img{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;display:block}.floorline{position:absolute;left:0;right:0;top:49%;border-top:1px solid #263d49;opacity:.65}.hud{position:absolute;z-index:100;left:50%;top:14px;transform:translateX(-50%);padding:8px 12px;background:#071018dd;border:1px solid #294758;font-size:12px;letter-spacing:.08em;white-space:nowrap}.crosshair{position:absolute;z-index:90;left:50%;top:50%;width:18px;height:18px;transform:translate(-50%,-50%);opacity:.42}.crosshair:before,.crosshair:after{content:"";position:absolute;background:#d6f7ff}.crosshair:before{left:8px;top:0;width:1px;height:18px}.crosshair:after{left:0;top:8px;width:18px;height:1px}.control{position:absolute;z-index:110;display:grid;place-items:center;width:54px;height:54px;border:1px solid #63879c;background:#0d1d28dd;color:#dff8ff;text-decoration:none;font-size:28px;line-height:1;cursor:pointer;user-select:none}.control:hover{background:#173247}.fwd{left:50%;top:4px;transform:translateX(-50%)}.back{left:50%;bottom:6px;transform:translateX(-50%)}.left{left:8px;top:50%;transform:translateY(-50%)}.right{right:8px;top:50%;transform:translateY(-50%)}.tl1{left:8px;top:8px}.tr1{right:8px;top:8px}.bl2{left:8px;bottom:8px}.br2{right:8px;bottom:8px}.help{position:absolute;z-index:100;left:50%;bottom:12px;transform:translateX(-50%);font-size:11px;color:#89a5b6;background:#071018aa;padding:7px 9px;pointer-events:none}@media(max-width:700px){.control{width:46px;height:46px;font-size:24px}.help{display:none}}'''

JS = r'''const DATA=__DATA__;
const R=DATA.radius, SQ3=Math.sqrt(3), WALL_H=2.4, EYE_H=1.0, HFOV=100*Math.PI/180, NEAR=.05;
const dirs=DATA.directions, cellSet=new Set(DATA.cells.map(c=>`${c[0]},${c[1]}`));
let viewer={q:0,r:R,heading:0};
function valid(q,r){return cellSet.has(`${q},${r}`)}
function center(q,r){return{x:SQ3*(q+r/2),y:1.5*r}}
function vertex(c,k){const a=(30+60*k)*Math.PI/180;return{x:c.x+Math.cos(a),y:c.y+Math.sin(a)}}

// Build the perimeter as SIX continuous walls. We collect all boundary-edge
// endpoints for each absolute direction, then take the two most distant points.
const pointsByDir=Array.from({length:6},()=>[]);
for(const [q,r] of DATA.cells){const c=center(q,r);for(let d=0;d<6;d++){const [,dq,dr]=dirs[d];if(valid(q+dq,r+dr))continue;pointsByDir[d].push(vertex(c,(d+3)%6),vertex(c,(d+4)%6));}}
function farthestPair(points){let best=[points[0],points[1]],bestD=-1;for(let i=0;i<points.length;i++)for(let j=i+1;j<points.length;j++){const dx=points[i].x-points[j].x,dy=points[i].y-points[j].y,v=dx*dx+dy*dy;if(v>bestD){bestD=v;best=[points[i],points[j]]}}return best}
const walls=pointsByDir.map((pts,d)=>{const [a,b]=farthestPair(pts);return{a,b,d,name:dirs[d][0],src:`assets/wall-${dirs[d][0].toLowerCase()}.svg`}});
const root=document.getElementById('walls');
walls.forEach((w,i)=>{const el=document.createElement('div');el.className='wall';el.dataset.i=i;const img=document.createElement('img');img.src=w.src;img.alt='';el.appendChild(img);root.appendChild(el)});

function worldViewer(){return center(viewer.q,viewer.r)}
function project(p,z,W,H){const v=worldViewer(),dx=p.x-v.x,dy=p.y-v.y,ang=-viewer.heading*Math.PI/180;const right=dx*Math.cos(ang)-dy*Math.sin(ang);const forward=-(dx*Math.sin(ang)+dy*Math.cos(ang));if(forward<=NEAR)return null;const f=(W/2)/Math.tan(HFOV/2);return{x:W/2+right*f/forward,y:H/2-(z-EYE_H)*f/forward,d:forward}}
function place(el,quad){const xs=quad.map(p=>p.x),ys=quad.map(p=>p.y),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys),w=Math.max(1,maxX-minX),h=Math.max(1,maxY-minY);el.style.left=`${minX}px`;el.style.top=`${minY}px`;el.style.width=`${w}px`;el.style.height=`${h}px`;el.style.clipPath=`polygon(${quad.map(p=>`${((p.x-minX)/w*100).toFixed(2)}% ${((p.y-minY)/h*100).toFixed(2)}%`).join(',')})`;}
function render(){const W=innerWidth,H=innerHeight,els=[...root.children];walls.forEach((wall,i)=>{const bl=project(wall.a,0,W,H),br=project(wall.b,0,W,H),tr=project(wall.b,WALL_H,W,H),tl=project(wall.a,WALL_H,W,H),el=els[i];if(!bl||!br||!tr||!tl){el.style.display='none';return}el.style.display='block';place(el,[tl,tr,br,bl]);const distance=(bl.d+br.d)/2;el.style.zIndex=String(Math.max(1,10000-Math.round(distance*500)));el.style.opacity='1'});document.getElementById('hud').textContent=`POSITION ${viewer.q},${viewer.r} · HEADING ${Math.round(viewer.heading)}° · FOV 100°`}
function headingIndex(){return((Math.round(viewer.heading/60)%6)+6)%6}
function moveRelative(offset){const d=(headingIndex()+offset+6)%6,[,dq,dr]=dirs[d],nq=viewer.q+dq,nr=viewer.r+dr;if(valid(nq,nr)){viewer.q=nq;viewer.r=nr;render()}else location.href='ouch.html'}
function turn(delta){viewer.heading=(viewer.heading+delta+360)%360;render()}

document.getElementById('fwd').onclick=()=>moveRelative(0);document.getElementById('back').onclick=()=>moveRelative(3);document.getElementById('left').onclick=()=>moveRelative(-1);document.getElementById('right').onclick=()=>moveRelative(1);document.getElementById('tl1').onclick=()=>turn(-60);document.getElementById('tr1').onclick=()=>turn(60);document.getElementById('bl2').onclick=()=>turn(-120);document.getElementById('br2').onclick=()=>turn(120);
addEventListener('keydown',e=>{if(e.key==='ArrowUp')moveRelative(0);if(e.key==='ArrowDown')moveRelative(3);if(e.key==='ArrowLeft')moveRelative(-1);if(e.key==='ArrowRight')moveRelative(1)});addEventListener('resize',render);render();'''.replace('__DATA__', json.dumps(DATA, separators=(',', ':')))

OUCH = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OUCH!</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#12090a;color:#fff;font-family:Arial,Helvetica,sans-serif}main{width:min(720px,90vw);text-align:center;border:2px solid #ff8a80;padding:2rem;background:#221012}h1{font-size:clamp(4rem,14vw,9rem);margin:0;color:#ff8a80}p{font-size:1.35rem}button{font:inherit;padding:1rem;border:1px solid #ddd;background:#161616;color:white;cursor:pointer}</style></head><body><main><h1>OUCH!</h1><p>That fuckin' hurt!</p><p>A disembodied voice says: “Report to sickbay for evaluation.”</p><button onclick="history.back()">I'll be okay, sir!</button></main></body></html>'''


def svg_wall(label, index):
    hue = 188 + index * 4
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 700" preserveAspectRatio="none"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="hsl({hue},35%,26%)"/><stop offset="1" stop-color="hsl({hue},45%,11%)"/></linearGradient><pattern id="p" width="160" height="700" patternUnits="userSpaceOnUse"><rect width="160" height="700" fill="none" stroke="#79a6b8" stroke-opacity=".22" stroke-width="3"/><path d="M20 80H140M20 620H140" stroke="#a8d1df" stroke-opacity=".16" stroke-width="2"/></pattern></defs><rect width="1600" height="700" fill="url(#g)"/><rect width="1600" height="700" fill="url(#p)"/><rect x="20" y="20" width="1560" height="660" rx="18" fill="none" stroke="#9cc7d7" stroke-opacity=".35" stroke-width="5"/><text x="800" y="365" fill="#d6f5ff" fill-opacity=".72" font-family="Arial,Helvetica,sans-serif" font-size="72" text-anchor="middle" letter-spacing="18">{label}</text></svg>'''


def build():
    ASSETS.mkdir(exist_ok=True)
    for i, (name, label) in enumerate(zip(WALL_NAMES, WALL_LABELS)):
        (ASSETS / f"wall-{name}.svg").write_text(svg_wall(label, i), encoding="utf-8")
    (ROOT / "bridge.css").write_text(CSS, encoding="utf-8")
    (ROOT / "bridge.js").write_text(JS, encoding="utf-8")
    (ROOT / "ouch.html").write_text(OUCH, encoding="utf-8")
    index = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Our Lovely System — Bridge</title><link rel="stylesheet" href="bridge.css"></head><body><main class="bridge"><section class="viewport"><div class="floorline"></div><div id="walls"></div></section><div class="crosshair"></div><div class="hud" id="hud"></div><button class="control fwd" id="fwd" aria-label="Move forward">↑</button><button class="control back" id="back" aria-label="Move backward">↓</button><button class="control left" id="left" aria-label="Move left">←</button><button class="control right" id="right" aria-label="Move right">→</button><button class="control tl1" id="tl1" aria-label="Turn 60 degrees left">↶</button><button class="control tr1" id="tr1" aria-label="Turn 60 degrees right">↷</button><button class="control bl2" id="bl2" aria-label="Turn 120 degrees left">⟲</button><button class="control br2" id="br2" aria-label="Turn 120 degrees right">⟳</button><div class="help">Movement: ↑ ↓ ← → · Turn: upper corners ±60° · lower corners ±120°</div></main><script src="bridge.js"></script></body></html>'''
    (ROOT / "index.html").write_text(index, encoding="utf-8")
    (ROOT / "GENERATION.txt").write_text("Generated first-person Bridge with six perimeter wall images and restored eight-control navigation.\n", encoding="utf-8")
    print("Generated six-wall first-person Bridge.")


if __name__ == "__main__":
    build()
