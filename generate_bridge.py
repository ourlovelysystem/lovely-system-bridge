from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
RADIUS = 5

# The Bridge is still a radius-five axial hex grid. The presentation is now
# first person: the grid is geometry, not something painted on the screen.
DIRECTIONS = [
    ("Forward", 0, -1),
    ("Forstar", 1, -1),
    ("Aftstar", 1, 0),
    ("Aft", 0, 1),
    ("Aftport", -1, 1),
    ("Forport", -1, 0),
]


def cells():
    result = []
    for q in range(-RADIUS, RADIUS + 1):
        for r in range(-RADIUS, RADIUS + 1):
            s = -q-r
            if max(abs(q), abs(r), abs(s)) <= RADIUS:
                result.append((q, r))
    return result


CELLS = cells()
assert len(CELLS) == 91

# Outer walls are the boundary edges of the 91-cell grand hexagon. JavaScript
# turns each edge into a vertical rectangle and perspective-projects its four
# corners from the viewer's continuously changing position and heading.
DATA = {"radius": RADIUS, "cells": CELLS, "directions": DIRECTIONS}

CSS = r''':root{--bg:#05090d;--ink:#e9f2f6;--line:#68879a;--glow:#bfeeff;--panel:#0c1821}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--ink);font-family:Arial,Helvetica,sans-serif}.bridge{position:fixed;inset:0;background:#05090d}.viewport{position:absolute;inset:0;overflow:hidden;perspective:900px;background:linear-gradient(#02070b 0 48%,#0b151b 48% 100%)}#walls{position:absolute;inset:0}.wall{position:absolute;inset:0;transform-origin:0 0;pointer-events:none}.wall img,.wall .texture{position:absolute;width:100%;height:100%;object-fit:cover;background:linear-gradient(135deg,#173342,#071018 55%,#1c3b49);border:1px solid #55788b}.wall .label{position:absolute;inset:0;display:grid;place-items:center;font-size:clamp(14px,2vw,28px);font-weight:700;letter-spacing:.16em;color:#c9f2ff;text-shadow:0 0 10px #00131c}.hud{position:absolute;z-index:100;left:50%;top:14px;transform:translateX(-50%);padding:8px 12px;background:#071018cc;border:1px solid #294758;font-size:12px;letter-spacing:.08em;white-space:nowrap}.crosshair{position:absolute;z-index:90;left:50%;top:50%;width:18px;height:18px;transform:translate(-50%,-50%);opacity:.45}.crosshair:before,.crosshair:after{content:"";position:absolute;background:#d6f7ff}.crosshair:before{left:8px;top:0;width:1px;height:18px}.crosshair:after{left:0;top:8px;width:18px;height:1px}.controls{position:absolute;z-index:110;left:50%;bottom:18px;transform:translateX(-50%);display:grid;grid-template-columns:repeat(5,52px);gap:7px}.controls button{height:46px;border:1px solid #63879c;background:#0d1d28dd;color:#dff8ff;font-size:20px;cursor:pointer}.controls button:hover{background:#173247}.help{position:absolute;z-index:100;right:14px;bottom:14px;font-size:11px;color:#89a5b6;background:#071018aa;padding:7px 9px}.floorline{position:absolute;left:0;right:0;top:48%;border-top:1px solid #243b47;opacity:.5}@media(max-width:650px){.controls{grid-template-columns:repeat(5,44px)}.controls button{height:42px}.help{display:none}}'''

JS = r'''const DATA=__DATA__;
const R=DATA.radius;
const SQ3=Math.sqrt(3);
const WALL_H=1.75;
const EYE_H=.78;
const HFOV=100*Math.PI/180; // instantaneous view remains well below 180 degrees
const NEAR=.05;
let viewer={q:0,r:R,x:0,y:0,heading:0};
const cellSet=new Set(DATA.cells.map(c=>`${c[0]},${c[1]}`));
const dirs=DATA.directions;

function axialCenter(q,r){return {x:SQ3*(q+r/2),y:1.5*r};}
function valid(q,r){return cellSet.has(`${q},${r}`);}
function vertex(cx,cy,k){let a=(30+60*k)*Math.PI/180;return {x:cx+Math.cos(a),y:cy+Math.sin(a)};}

// One wall for every boundary edge. Each carries a stable name so a real
// image can later replace the generated texture without changing geometry.
const boundary=[];
for(const [q,r] of DATA.cells){
  const c=axialCenter(q,r);
  for(let d=0;d<6;d++){
    const [,dq,dr]=dirs[d];
    if(valid(q+dq,r+dr)) continue;
    // Direction d points at the outward side. With pointy-top hexes its edge
    // endpoints are vertices d+3 and d+4 in this coordinate convention.
    const a=vertex(c.x,c.y,(d+3)%6), b=vertex(c.x,c.y,(d+4)%6);
    boundary.push({a,b,name:`${dirs[d][0]} WALL`,dir:d,q,r});
  }
}

const wallRoot=document.getElementById('walls');
for(let i=0;i<boundary.length;i++){
  const el=document.createElement('div');el.className='wall';el.dataset.i=i;
  const tex=document.createElement('div');tex.className='texture';
  const lab=document.createElement('div');lab.className='label';lab.textContent=boundary[i].name;
  tex.appendChild(lab);el.appendChild(tex);wallRoot.appendChild(el);
}

function worldViewer(){const c=axialCenter(viewer.q,viewer.r);return{x:c.x+viewer.x,y:c.y+viewer.y};}
function project(p,z,w,h){
  const v=worldViewer(), dx=p.x-v.x, dy=p.y-v.y;
  const ang=-viewer.heading*Math.PI/180;
  // Heading zero looks toward Forward, i.e. negative world Y.
  const right=dx*Math.cos(ang)-dy*Math.sin(ang);
  const forward=-(dx*Math.sin(ang)+dy*Math.cos(ang));
  if(forward<=NEAR)return null;
  const f=(w/2)/Math.tan(HFOV/2);
  return{x:w/2+right*f/forward,y:h/2-(z-EYE_H)*f/forward,d:forward};
}

function homographyStyle(el,p0,p1,p2,p3){
  // CSS matrix3d mapping the unit square to a screen quadrilateral. This is a
  // projective transform: oblique walls become trapezoids instead of merely
  // being squeezed to a guessed aspect ratio.
  const x0=p0.x,y0=p0.y,x1=p1.x,y1=p1.y,x2=p2.x,y2=p2.y,x3=p3.x,y3=p3.y;
  const dx1=x1-x2,dy1=y1-y2,dx2=x3-x2,dy2=y3-y2,dx3=x0-x1+x2-x3,dy3=y0-y1+y2-y3;
  let a,b,c,d,e,f,g,h;
  if(Math.abs(dx3)<1e-6&&Math.abs(dy3)<1e-6){a=x1-x0;b=x3-x0;c=x0;d=y1-y0;e=y3-y0;f=y0;g=0;h=0;}
  else{const den=dx1*dy2-dx2*dy1;g=(dx3*dy2-dx2*dy3)/den;h=(dx1*dy3-dx3*dy1)/den;a=x1-x0+g*x1;b=x3-x0+h*x3;c=x0;d=y1-y0+g*y1;e=y3-y0+h*y3;f=y0;}
  // Source is 1x1, then scaled by CSS dimensions below.
  el.style.width='1px';el.style.height='1px';
  el.style.transform=`matrix3d(${a},${d},0,${g},${b},${e},0,${h},0,0,1,0,${c},${f},0,1)`;
}

function render(){
  const w=innerWidth,h=innerHeight;
  const els=[...wallRoot.children];
  boundary.forEach((wall,i)=>{
    const el=els[i];
    const bl=project(wall.a,0,w,h),br=project(wall.b,0,w,h),tr=project(wall.b,WALL_H,w,h),tl=project(wall.a,WALL_H,w,h);
    if(!bl||!br||!tr||!tl){el.style.display='none';return;}
    el.style.display='block';homographyStyle(el,tl,tr,br,bl);
    el.style.zIndex=String(Math.max(1,10000-Math.round((bl.d+br.d)*500)));
    const fade=Math.max(.22,1-(bl.d+br.d)/34);el.style.opacity=fade.toFixed(2);
  });
  document.getElementById('hud').textContent=`POSITION ${viewer.q},${viewer.r} · HEADING ${Math.round(viewer.heading)}° · FOV 100°`;
}

function move(dir){
  const h=((Math.round(viewer.heading/60)%6)+6)%6;
  const d=(h+dir+6)%6,[,dq,dr]=dirs[d];
  if(valid(viewer.q+dq,viewer.r+dr)){viewer.q+=dq;viewer.r+=dr;viewer.x=viewer.y=0;render();}
  else location.href='ouch.html';
}
function turn(deg){viewer.heading=(viewer.heading+deg+360)%360;render();}
document.getElementById('left').onclick=()=>turn(-15);
document.getElementById('right').onclick=()=>turn(15);
document.getElementById('fwd').onclick=()=>move(0);
document.getElementById('back').onclick=()=>move(3);
document.getElementById('reset').onclick=()=>{viewer={q:0,r:R,x:0,y:0,heading:0};render();};
addEventListener('keydown',e=>{if(e.key==='ArrowLeft')turn(-5);if(e.key==='ArrowRight')turn(5);if(e.key==='ArrowUp')move(0);if(e.key==='ArrowDown')move(3);});
addEventListener('resize',render);render();'''.replace('__DATA__', json.dumps(DATA, separators=(',', ':')))

OUCH = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OUCH!</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#12090a;color:#fff;font-family:Arial,Helvetica,sans-serif}main{width:min(720px,90vw);text-align:center;border:2px solid #ff8a80;padding:2rem;background:#221012}h1{font-size:clamp(4rem,14vw,9rem);margin:0;color:#ff8a80}p{font-size:1.35rem}button{font:inherit;padding:1rem;border:1px solid #ddd;background:#161616;color:white;cursor:pointer}</style></head><body><main><h1>OUCH!</h1><p>That fuckin' hurt!</p><p>A disembodied voice says: “Report to sickbay for evaluation.”</p><button onclick="history.back()">I'll be okay, sir!</button></main></body></html>'''


def build():
    (ROOT / 'bridge.css').write_text(CSS, encoding='utf-8')
    (ROOT / 'bridge.js').write_text(JS, encoding='utf-8')
    (ROOT / 'ouch.html').write_text(OUCH, encoding='utf-8')
    index='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Our Lovely System — Bridge</title><link rel="stylesheet" href="bridge.css"></head><body><main class="bridge"><section class="viewport" aria-label="First person Bridge view"><div class="floorline"></div><div id="walls"></div></section><div class="crosshair"></div><div class="hud" id="hud"></div><div class="controls"><button id="left" aria-label="Turn left">↶</button><button id="back" aria-label="Move backward">↓</button><button id="reset" aria-label="Reset">⌂</button><button id="fwd" aria-label="Move forward">↑</button><button id="right" aria-label="Turn right">↷</button></div><div class="help">← → turn continuously · ↑ ↓ move by hex · walls are perspective-projected</div></main><script src="bridge.js"></script></body></html>'''
    (ROOT / 'index.html').write_text(index, encoding='utf-8')
    (ROOT / 'GENERATION.txt').write_text('Generated first-person Bridge: 91-cell hex geometry with perspective-projected boundary walls.\n', encoding='utf-8')
    print('Generated first-person Bridge.')


if __name__ == '__main__':
    build()
