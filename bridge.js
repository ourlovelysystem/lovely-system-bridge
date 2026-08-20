const DATA={"radius":5,"cells":[[-5,0],[-5,1],[-5,2],[-5,3],[-5,4],[-5,5],[-4,-1],[-4,0],[-4,1],[-4,2],[-4,3],[-4,4],[-4,5],[-3,-2],[-3,-1],[-3,0],[-3,1],[-3,2],[-3,3],[-3,4],[-3,5],[-2,-3],[-2,-2],[-2,-1],[-2,0],[-2,1],[-2,2],[-2,3],[-2,4],[-2,5],[-1,-4],[-1,-3],[-1,-2],[-1,-1],[-1,0],[-1,1],[-1,2],[-1,3],[-1,4],[-1,5],[0,-5],[0,-4],[0,-3],[0,-2],[0,-1],[0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[1,-5],[1,-4],[1,-3],[1,-2],[1,-1],[1,0],[1,1],[1,2],[1,3],[1,4],[2,-5],[2,-4],[2,-3],[2,-2],[2,-1],[2,0],[2,1],[2,2],[2,3],[3,-5],[3,-4],[3,-3],[3,-2],[3,-1],[3,0],[3,1],[3,2],[4,-5],[4,-4],[4,-3],[4,-2],[4,-1],[4,0],[4,1],[5,-5],[5,-4],[5,-3],[5,-2],[5,-1],[5,0]],"directions":[["Forward",0,-1],["Forstar",1,-1],["Aftstar",1,0],["Aft",0,1],["Aftport",-1,1],["Forport",-1,0]]};
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
addEventListener('keydown',e=>{if(e.key==='ArrowUp')move(0);if(e.key==='ArrowDown')move(3);if(e.key==='ArrowLeft')move(-1);if(e.key==='ArrowRight')move(1)});addEventListener('resize',resize);resize();