const DATA={"radius":5,"cells":[[-5,0],[-5,1],[-5,2],[-5,3],[-5,4],[-5,5],[-4,-1],[-4,0],[-4,1],[-4,2],[-4,3],[-4,4],[-4,5],[-3,-2],[-3,-1],[-3,0],[-3,1],[-3,2],[-3,3],[-3,4],[-3,5],[-2,-3],[-2,-2],[-2,-1],[-2,0],[-2,1],[-2,2],[-2,3],[-2,4],[-2,5],[-1,-4],[-1,-3],[-1,-2],[-1,-1],[-1,0],[-1,1],[-1,2],[-1,3],[-1,4],[-1,5],[0,-5],[0,-4],[0,-3],[0,-2],[0,-1],[0,0],[0,1],[0,2],[0,3],[0,4],[0,5],[1,-5],[1,-4],[1,-3],[1,-2],[1,-1],[1,0],[1,1],[1,2],[1,3],[1,4],[2,-5],[2,-4],[2,-3],[2,-2],[2,-1],[2,0],[2,1],[2,2],[2,3],[3,-5],[3,-4],[3,-3],[3,-2],[3,-1],[3,0],[3,1],[3,2],[4,-5],[4,-4],[4,-3],[4,-2],[4,-1],[4,0],[4,1],[5,-5],[5,-4],[5,-3],[5,-2],[5,-1],[5,0]],"directions":[["Forward",0,-1],["Forstar",1,-1],["Aftstar",1,0],["Aft",0,1],["Aftport",-1,1],["Forport",-1,0]]};
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
addEventListener('keydown',e=>{if(e.key==='ArrowUp')moveRelative(0);if(e.key==='ArrowDown')moveRelative(3);if(e.key==='ArrowLeft')moveRelative(-1);if(e.key==='ArrowRight')moveRelative(1)});addEventListener('resize',render);render();