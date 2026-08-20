const DATA={"radius":5,"cells":[[-5,0],[-5,1],[-5,2],[-5,3],[-5,4],[-5,5],[-4,-1],[-4,0],[-4,1],[-4,2],[-4,3],[-4,4],[-4,5],[-3,-2],[-3,-1],[-3,0],[-3,1],[-3,2],[-3,3],[-3,4],[-3,5],[-2,-3],[-2,-2],[-2,-1],[-2,0],[-2,1],[-2,2],[-2,3],[-2,4],[-2,5],[-1,-4],[-1,-3],[-1,-2],[-1,-1],[-1,0],[-1,1],[-1,2],[-1,3],[-1,4],[-1,5],[0,-5],[0,-4],[0,-3],[0,-2],[0,-1],[0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[1,-5],[1,-4],[1,-3],[1,-2],[1,-1],[1,0],[1,1],[1,2],[1,3],[1,4],[2,-5],[2,-4],[2,-3],[2,-2],[2,-1],[2,0],[2,1],[2,2],[2,3],[3,-5],[3,-4],[3,-3],[3,-2],[3,-1],[3,0],[3,1],[3,2],[4,-5],[4,-4],[4,-3],[4,-2],[4,-1],[4,0],[4,1],[5,-5],[5,-4],[5,-3],[5,-2],[5,-1],[5,0]],"directions":[["Forward",0,-1],["Forstar",1,-1],["Aftstar",1,0],["Aft",0,1],["Aftport",-1,1],["Forport",-1,0]]};
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
addEventListener('resize',render);render();