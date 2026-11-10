import * as THREE from 'three';
import {OrbitControls} from '../../assets/OrbitControls.js';
import {createPointMarkers} from '../../point-markers.js';
import {downloadPart} from '../../part-download.js';
const $=id=>document.getElementById(id), viewport=$('viewport'), objects=[];
const scene=new THREE.Scene();scene.background=new THREE.Color('#f8fafc');
const camera=new THREE.PerspectiveCamera(35,1,.1,2500);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.localClippingEnabled=true;viewport.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x657b8e,2.2));const light=new THREE.DirectionalLight(0xffffff,2.8);light.position.set(80,-120,200);scene.add(light);
const grid=new THREE.GridHelper(700,70,0xc8d2dc,0xe1e6ed);grid.rotation.x=Math.PI/2;grid.position.z=15.8;scene.add(grid);
const sectionPlane=new THREE.Plane(new THREE.Vector3(0,1,0),0);
let data, angle=0, playing=false, selected=null;
const clamp=x=>Math.max(0,Math.min(1,x));
function closeMenu(){$('partMenu').hidden=true;}
const markers=createPointMarkers({THREE,getObjects:()=>objects,getContext:()=>({drive:'bearing-supported-screw',motor:'nema17',stroke_mm:40,enclosure:'independent-bearing-holder',model_revision:data?.sourceRevision,mode:$('viewMode').value,explosion_percent:+$('explode').value,rotation_degrees:angle*180/Math.PI}),closeMenu});
function select(o){selected=o;$('partSelect').value=o?.userData.name||'';for(const id of ['isolate','download'])$(id).disabled=!o;}
function isolate(){if(selected){for(const o of objects)o.visible=o===selected;closeMenu();fit();}}
function showAll(){for(const o of objects)o.visible=true;closeMenu();}
async function download(p=selected?.userData){if(!p)return;await downloadPart(p,{url:p.stl?p.stl+'?v=5':undefined,filename:'6805-prototype-'+p.name.toLowerCase().replaceAll(' ','_')+'.stl'});closeMenu();}
function pose(){
 const exploded=$('viewMode').value==='exploded',t=exploded?+$('explode').value/100:0;
 $('explodeControls').hidden=!exploded;$('explodeValue').value=(100*t).toFixed(0)+'%';$('play').disabled=exploded;
 for(const o of objects){const p=o.userData;const progress=p.stage?clamp(t*data.explosionStages-(p.stage-1)):0;
  const a=!exploded&&['rotor','bearingRotor','motorRotor'].includes(p.group)?angle:0;
  o.quaternion.setFromAxisAngle(new THREE.Vector3(1,0,0),a);o.scale.set(1,1,1);
  let akey=p.explodeKeyframes[0],bkey=p.explodeKeyframes.at(-1);
  for(let i=1;i<p.explodeKeyframes.length;i++)if(t<=p.explodeKeyframes[i].t){akey=p.explodeKeyframes[i-1];bkey=p.explodeKeyframes[i];break;}
  const f=clamp((t-akey.t)/(bkey.t-akey.t));const delta=akey.offset.map((v,i)=>v+(bkey.offset[i]-v)*f);
  o.position.set(delta[0],delta[1]+42*Math.sin(a),delta[2]+42*(1-Math.cos(a)));
  const transparent=$('transparent').checked&&p.name==='Bearing holder';
  o.material.transparent=transparent;o.material.opacity=transparent?.22:1;o.material.depthWrite=!transparent;
  o.material.clippingPlanes=$('section').checked?[sectionPlane]:[];
 }
}
function fit(direction=new THREE.Vector3(1,-1,.7)){
 const box=new THREE.Box3();for(const o of objects)if(o.visible)box.expandByObject(o);
 if(box.isEmpty())return;const center=box.getCenter(new THREE.Vector3());direction.normalize();
 const right=new THREE.Vector3().crossVectors(camera.up,direction).normalize(),up=new THREE.Vector3().crossVectors(direction,right).normalize(),tan=Math.tan(THREE.MathUtils.degToRad(camera.fov/2));let distance=0;
 for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const v=new THREE.Vector3(x,y,z).sub(center);distance=Math.max(distance,Math.abs(v.dot(right))/(tan*camera.aspect)+v.dot(direction),Math.abs(v.dot(up))/tan+v.dot(direction));}distance*=1.18;
 controls.target.copy(center);camera.position.copy(center).add(direction.normalize().multiplyScalar(distance));camera.near=.1;camera.far=Math.max(2500,distance*4);camera.updateProjectionMatrix();controls.update();
}
function focus(section=false){showAll();$('viewMode').value='assembled';$('section').checked=section;playing=false;angle=0;$('play').textContent='Rotate screw';pose();controls.target.set(25,0,42);camera.position.set(104,-97,93);controls.update();}
function reset(){playing=false;angle=0;$('play').textContent='Rotate screw';$('viewMode').value='assembled';$('explode').value=100;$('transparent').checked=false;$('section').checked=false;showAll();select(null);pose();fit();}
$('reset').onclick=reset;$('fit').onclick=()=>fit(camera.position.clone().sub(controls.target));$('iso').onclick=()=>fit();$('supportView').onclick=()=>focus();$('sectionView').onclick=()=>focus(true);
$('flangeView').onclick=()=>{focus();for(const o of objects)o.visible=o.userData.name==='Bearing holder'||o.userData.name.includes('holder');select(objects.find(o=>o.userData.name==='Bearing holder'));fit(new THREE.Vector3(1,-1,.6));};
$('rearView').onclick=()=>{focus();for(const o of objects)o.visible=o.userData.name==='Bearing holder'||o.userData.name.startsWith('6805');select(objects.find(o=>o.userData.name==='Bearing holder'));controls.target.set(24,0,42);camera.position.set(-60,-75,86);controls.update();};
$('couplingView').onclick=()=>{focus();controls.target.set(17,0,42);camera.position.set(20,-80,100);controls.update();};
$('viewMode').onchange=()=>{playing=false;angle=0;$('play').textContent='Rotate screw';pose();fit();};$('explode').oninput=pose;
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause rotation':'Rotate screw';};
$('transparent').onchange=pose;$('section').onchange=pose;
$('partSelect').onchange=()=>select(objects.find(o=>o.userData.name===$('partSelect').value)||null);
$('isolate').onclick=isolate;$('download').onclick=()=>download();$('showAll').onclick=showAll;
$('menuIsolate').onclick=isolate;$('menuDownload').onclick=()=>download();$('menuShowAll').onclick=showAll;$('menuHide').onclick=()=>{if(selected)selected.visible=false;closeMenu();};
const raycaster=new THREE.Raycaster();
renderer.domElement.addEventListener('contextmenu',e=>{e.preventDefault();const r=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2(2*(e.clientX-r.left)/r.width-1,1-2*(e.clientY-r.top)/r.height),camera);const hits=raycaster.intersectObjects(objects.filter(o=>o.visible),false);const hit=hits.find(h=>!$('section').checked||sectionPlane.distanceToPoint(h.point)>=0)||null;select(hit?.object||null);markers.capture(hit);$('menuPartName').textContent=selected?.userData.name||'Assembly';for(const id of ['menuHide','menuIsolate','menuDownload'])$(id).disabled=!selected;const menu=$('partMenu');menu.hidden=false;menu.style.left=Math.min(e.clientX,innerWidth-menu.offsetWidth-8)+'px';menu.style.top=Math.max(8,Math.min(e.clientY,innerHeight-menu.offsetHeight-8))+'px';});
document.addEventListener('pointerdown',e=>{if(!$('partMenu').contains(e.target))closeMenu();});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu();});
new ResizeObserver(()=>{camera.aspect=viewport.clientWidth/viewport.clientHeight;camera.updateProjectionMatrix();renderer.setSize(viewport.clientWidth,viewport.clientHeight);}).observe(viewport);
let last=performance.now();renderer.setAnimationLoop(now=>{if(playing){angle+=(now-last)*.0005;pose();}last=now;controls.update();renderer.render(scene,camera);});
try{
 const response=await fetch('assembly.json.gz?v=5');if(!response.ok)throw Error('Assembly request failed');data=await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();
 for(const p of data.parts){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(p.vertices.flat(),3));geometry.setIndex(p.triangles.flat());geometry.computeVertexNormals();const material=new THREE.MeshStandardMaterial({color:p.color,roughness:.62,metalness:p.printed?.08:.38,side:THREE.DoubleSide});const mesh=new THREE.Mesh(geometry,material);mesh.userData=p;scene.add(mesh);objects.push(mesh);const opt=document.createElement('option');opt.value=p.name;opt.textContent=p.name;$('partSelect').appendChild(opt);if(p.printed){const button=document.createElement('button');button.textContent=p.name+' ↓';button.onclick=()=>download(p);$('printedDownloads').appendChild(button);}}
 const result=await fetch('validation.json?v=5');if(!result.ok)throw Error('Check report request failed');const report=await result.json();if(!report.passed)throw Error('Geometry checks failed');
 $('checkSummary').textContent=`Passed: ${report.print_meshes.length} watertight printed meshes; no assembled intersections; full rotating-envelope clearance; coupling and motor-bolt tool access; rear bearing-loading clearance; captured removal and front hex-key access for four shared NEMA17 screws and a continuous outer-race shoulder. Original screw material preserved; additions confined to the bearing ring.`;
 $('loading').hidden=true;markers.restore();reset();window.bearingViewer={data,objects,camera,controls,fit,pose,markers};
}catch(error){console.error(error);$('loading').textContent='Could not load the prototype. Reload to retry.';$('status').textContent=error.message;}
