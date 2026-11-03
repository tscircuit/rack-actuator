import * as THREE from 'three';
import {OrbitControls} from './assets/OrbitControls.js';
const params=new URLSearchParams(location.search),variant=params.get('motor')==='nema14'?'nema14':'nema17',presetStrokes=[40,100,150],presetStroke=presetStrokes.includes(+params.get('stroke'))?+params.get('stroke'):40,basePath=presetStroke===40?(variant==='nema14'?'./variants/nema14/':'./'):'./variants/'+variant+'/'+presetStroke+'/',springPath=basePath+'assets/spring-states.json.gz';
if(params.has('layout')){params.delete('layout');history.replaceState(null,'',location.pathname+(params.size?'?'+params:'')+location.hash)}
let presetInfo;
const $=id=>document.getElementById(id), vp=$('viewport');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0x000000,0);vp.appendChild(renderer.domElement);
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(35,1,.1,20000);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=75;controls.maxDistance=20000;
scene.add(new THREE.HemisphereLight(0xffffff,0x9ca3af,2));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(10,-50,120);scene.add(key);const rim=new THREE.DirectionalLight(0x8fbaff,2);rim.position.set(-50,90,45);scene.add(rim);
const grid=new THREE.GridHelper(240,24,0xd1d5db,0xe5e7eb);grid.rotation.x=Math.PI/2;grid.position.z=-34;scene.add(grid);
let data,objects=[],playing=false,mode='motion',last=0,phase=0,selected=null;
const hiddenParts=new Set();let menuTarget=null;
function resetCamera(direction){
 if(!(direction instanceof THREE.Vector3))direction=new THREE.Vector3(1,-1.25,.8);direction.normalize();
 if(!data||!objects.length){camera.position.set(210,-260,170);controls.target.set(0,16,-10);controls.update();return}
 const bounds=new THREE.Box3(),samples=mode==='explode'?[0,...data.stages.map(s=>s.end)]:[0];
 for(const mesh of objects){if(!mesh.visible)continue;mesh.geometry.computeBoundingBox();
  for(const e of samples){const pos=new THREE.Vector3(...displacement(mesh.userData.group,e)),a=orientation(mesh.userData.group,e),matrix=new THREE.Matrix4().makeRotationZ(a);
   if(['gear','shaft','set_screw'].includes(mesh.userData.group)){const pivot=new THREE.Vector3(...data.rotationPivot);pos.add(pivot.clone().sub(pivot.clone().applyMatrix4(matrix)))}
   matrix.setPosition(pos);const box=mesh.geometry.boundingBox.clone().applyMatrix4(matrix);bounds.union(box);
   if(mode==='motion'&&mesh.userData.group==='rack'){bounds.union(box.clone().translate(new THREE.Vector3(-data.stroke/2,0,0)));bounds.union(box.clone().translate(new THREE.Vector3(data.stroke/2,0,0)))}
  }
 }
 if(bounds.isEmpty())return;
 const center=bounds.getCenter(new THREE.Vector3()),right=new THREE.Vector3(0,0,1).cross(direction).normalize(),up=direction.clone().cross(right).normalize(),tanV=Math.tan(THREE.MathUtils.degToRad(camera.fov/2)),tanH=tanV*camera.aspect;
 let distance=75;
 for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
  const q=new THREE.Vector3(x,y,z).sub(center);distance=Math.max(distance,q.dot(direction)+Math.max(Math.abs(q.dot(right))/tanH,Math.abs(q.dot(up))/tanV)*1.15);
 }
 camera.near=Math.max(.5,(distance+8)/200);camera.far=Math.max(20000,(distance+8)*20);camera.updateProjectionMatrix();
 camera.position.copy(center).addScaledVector(direction,distance+8);controls.target.copy(center);controls.update();
}resetCamera();
new ResizeObserver(()=>{const w=vp.clientWidth,h=vp.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false);resetCamera()}).observe(vp);
const ramp=(e,a,b)=>Math.max(0,Math.min(1,(e-a)/(b-a)));
function lowerLift(x,e){
 const edge=data.rackLeft+data.withdrawal*ramp(e,data.rackWithdrawalStart,data.rackWithdrawalEnd),candidates=[-17+data.springPreload];
 for(const [x0,x1,z0,slope] of [[edge,edge+data.rackLength,-9,0]]){
  const lo=Math.max(x0,x-8),hi=Math.min(x1,x+8);if(lo>hi)continue;
  const tangent=Math.max(lo,Math.min(hi,x-8*slope/Math.sqrt(1+slope*slope)));
  for(const q of [lo,hi,tangent])candidates.push(z0+slope*(q-x0)-Math.sqrt(Math.max(0,64-(q-x)**2)));
 }
 return Math.max(0,Math.min(data.springPreload,Math.min(...candidates)+17));
}
function deformSpring(m,e){
 const l=lowerLift(data.stationXs[0],e),r=lowerLift(data.stationXs[1],e),states=m.userData.springStates;
 let best=0,dist=Infinity;for(let i=0;i<states.length;i++){const d=(states[i].l-l)**2+(states[i].r-r)**2;if(d<dist){dist=d;best=i}}
 if(m.userData.springStateIndex===best)return;
 m.geometry=states[best].geometry;m.children[0].geometry=states[best].edges;
 m.userData.springStateIndex=best;m.userData.appliedSpring=[states[best].l,states[best].r];
}
function displacement(group,e){const v=[0,0,group.startsWith('lower_')?lowerLift(data.stationXs[group.includes('_left_')?0:1],e):0];for(const t of data.tracks[group]||[]){const f=ramp(e,t.start,t.end);for(let i=0;i<3;i++)v[i]+=(t.delta||[0,0,0])[i]*f}return v}
function orientation(group,e){return (data.tracks[group]||[]).reduce((a,t)=>a+ramp(e,t.start,t.end)*(t.degrees||0),0)*Math.PI/180}
function update(){if(!data)return;const stroke=+$('stroke').value,travel=+$('travel').value,dx=travel-stroke/2,e=mode==='explode'?+$('explosion').value/100:0;
$('travelValue').innerHTML=travel.toFixed(1)+' <small>mm</small>';$('strokeValue').textContent=stroke+' mm';$('strokeEnd').textContent=stroke+' mm';$('explodeValue').textContent=Math.round(e*100)+'%';
for(const m of objects){if(m.userData.flex_chassis)deformSpring(m,e);const d=displacement(m.userData.group,e);m.position.set(...d);m.quaternion.identity();m.rotation.z=orientation(m.userData.group,e);if(mode==='motion'){if(m.userData.group==='rack')m.position.x=dx;if(['gear','set_screw','shaft'].includes(m.userData.group))m.rotation.z=-dx/data.pitchRadius;if(m.userData.spinAxis){const c=new THREE.Vector3(...m.userData.spinCenter);m.quaternion.setFromAxisAngle(new THREE.Vector3(...m.userData.spinAxis),m.userData.spinSign*dx/8);m.position.copy(c.clone().sub(c.clone().applyQuaternion(m.quaternion)));}}
if(['gear','set_screw','shaft'].includes(m.userData.group)){const p=new THREE.Vector3(...data.rotationPivot);m.position.add(p.clone().sub(p.clone().applyQuaternion(m.quaternion)));}
const shell=m.userData.name.startsWith('01'),outer=['tray','cover','cover_screws','chassis_screws'].includes(m.userData.group);
m.visible=!hiddenParts.has(m.userData.name)&&(!shell||$('shell').checked)&&(!outer||$('enclosure').checked);
// Ghost only the printed outer shell. Hardware and the bearing chassis stay opaque.
const ghost=$('ghost').checked&&m.userData.printed&&['tray','cover'].includes(m.userData.group);
m.material=ghost?m.userData.ghostMaterial:m.userData.solidMaterial;
m.renderOrder=ghost?1:0;
const edge=m.children[0];edge.visible=$('edges').checked||ghost;edge.material.color.setHex(ghost?0x94a3b8:0x475569);edge.material.opacity=ghost?.35:.45;edge.renderOrder=ghost?2:0;
}
updatePartActions();
const active=data.stages.findIndex(t=>e>=t.start&&e<t.end);document.querySelectorAll('.stages li').forEach((li,i)=>li.classList.toggle('active',e>0&&i===(active<0?data.stages.length-1:active)));grid.position.z=mode==='explode'?-145:data.motorRearZ-8;$('modeBadge').textContent=mode==='motion'?(playing?'ACTUATING':'ASSEMBLED'):'STAGED EXPLOSION';}
function stop(){playing=false;$('play').textContent='Play actuation';}
function setMode(m){stop();mode=m;$('motionControls').hidden=m!=='motion';$('explosionControls').hidden=m!=='explode';for(const x of ['motion','explode']){$(x+'Tab').classList.toggle('active',x===m);$(x+'Tab').setAttribute('aria-selected',x===m)}controls.update();update();resetCamera()}
$('motionTab').onclick=()=>setMode('motion');$('explodeTab').onclick=()=>setMode('explode');$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause actuation':'Play actuation';update()};$('travel').oninput=()=>{stop();update()};$('explosion').oninput=update;$('stroke').oninput=()=>{const old=+$('travel').max,f=+$('travel').value/old;$('travel').max=$('stroke').value;$('travel').value=f*+$('stroke').value;update()};for(const id of ['shell','enclosure','ghost','edges'])$(id).onchange=update;
$('teeth').onclick=()=>{setMode('motion');$('enclosure').checked=false;$('ghost').checked=true;update();camera.position.set(25,5,90);controls.target.set(0,23,17);controls.update()};$('rollers').onclick=()=>{setMode('motion');$('enclosure').checked=false;$('shell').checked=true;$('ghost').checked=false;update();viewDirection([1,1.25,.55])};$('iso').onclick=resetCamera;$('fit').onclick=resetCamera;$('top').onclick=()=>viewDirection([0,-.001,1]);$('reset').onclick=()=>{if(!data)return;stop();hiddenParts.clear();closePartMenu();selectPart(null);$('stroke').value=data.stroke;$('travel').max=data.stroke;$('travel').value=data.stroke/2;$('explosion').value=0;$('shell').checked=true;$('enclosure').checked=true;$('ghost').checked=false;$('edges').checked=false;setMode('motion');resetCamera()};
function pickPart(clientX,clientY){
 const rect=renderer.domElement.getBoundingClientRect(),ray=new THREE.Raycaster();
 ray.setFromCamera(new THREE.Vector2((clientX-rect.left)/rect.width*2-1,-(clientY-rect.top)/rect.height*2+1),camera);
 return ray.intersectObjects(objects.filter(o=>o.visible),false)[0]?.object||null;
}
function selectPart(part){
 if(selected)selected.userData.solidMaterial.emissive.setHex(0);
 selected=part;if(selected)selected.userData.solidMaterial.emissive.setHex(0x172554);
 $('selection').textContent=selected?selected.userData.name:'Select a part.';updatePartActions();
}
function updatePartActions(){
 $('hideSelected').disabled=!selected||!selected.visible;
 $('showAll').disabled=hiddenParts.size===0&&$('shell').checked&&$('enclosure').checked;
 $('hiddenCount').textContent=hiddenParts.size?hiddenParts.size+' hidden '+(hiddenParts.size===1?'part':'parts'):'';
}
function closePartMenu(){ $('partMenu').hidden=true;menuTarget=null; }
function hidePart(part){if(!part)return;hiddenParts.add(part.userData.name);closePartMenu();if(selected===part)selectPart(null);update()}
function showAllParts(){hiddenParts.clear();$('shell').checked=true;$('enclosure').checked=true;closePartMenu();update()}
function openPartMenu(part,x,y){
 closePartMenu();menuTarget=part;selectPart(part);const menu=$('partMenu');
 $('menuPartName').textContent=part?part.userData.name:'Parts';$('menuHide').hidden=!part;
 $('menuShowAll').disabled=hiddenParts.size===0&&$('shell').checked&&$('enclosure').checked;
 menu.hidden=false;const rect=menu.getBoundingClientRect();menu.style.left=Math.max(8,Math.min(x,innerWidth-rect.width-8))+'px';menu.style.top=Math.max(8,Math.min(y,innerHeight-rect.height-8))+'px';
 (part?$('menuHide'):$('menuShowAll')).focus({preventScroll:true});
}
$('menuHide').onclick=()=>hidePart(menuTarget);$('menuShowAll').onclick=showAllParts;
$('hideSelected').onclick=()=>hidePart(selected);$('showAll').onclick=showAllParts;
let start;
renderer.domElement.addEventListener('pointerdown',e=>{start=[e.clientX,e.clientY];if(e.button===0)closePartMenu()});
renderer.domElement.addEventListener('pointermove',e=>{if(e.buttons&&start&&Math.hypot(e.clientX-start[0],e.clientY-start[1])>5)closePartMenu()});
renderer.domElement.addEventListener('pointerup',e=>{if(e.button!==0||!start||Math.hypot(e.clientX-start[0],e.clientY-start[1])>5)return;selectPart(pickPart(e.clientX,e.clientY))});
renderer.domElement.addEventListener('contextmenu',e=>{e.preventDefault();openPartMenu(pickPart(e.clientX,e.clientY),e.clientX,e.clientY)});
document.addEventListener('pointerdown',e=>{if(!$('partMenu').contains(e.target)&&e.target!==renderer.domElement)closePartMenu()});
document.addEventListener('keydown',e=>{
 if($('partMenu').hidden)return;
 if(e.key==='Escape'){closePartMenu();renderer.domElement.focus({preventScroll:true})}
 if(['ArrowDown','ArrowUp','Home','End'].includes(e.key)){e.preventDefault();const buttons=[...$('partMenu').querySelectorAll('button')].filter(b=>!b.hidden&&!b.disabled);if(!buttons.length)return;let i=buttons.indexOf(document.activeElement);i=e.key==='Home'?0:e.key==='End'?buttons.length-1:(i+(e.key==='ArrowUp'?-1:1)+buttons.length)%buttons.length;buttons[i].focus()}
});
window.addEventListener('resize',closePartMenu);window.addEventListener('scroll',closePartMenu,true);
renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('aria-label','3D assembly. Select a part or right-click to hide it.');
renderer.domElement.addEventListener('keydown',e=>{if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();const r=renderer.domElement.getBoundingClientRect();openPartMenu(selected,r.left+r.width/2,r.top+r.height/2)}});

function applyVariant(){
 const short=variant==='nema14'?'FLEX14':'FLEX17',is14=variant==='nema14',circ=2*Math.PI*data.pitchRadius;
 $('motorVariant').value=variant;$('strokePreset').value=data.stroke;$('stroke').max=data.stroke;$('stroke').value=data.stroke;$('travel').max=data.stroke;$('travel').value=data.stroke/2;document.title=short+' | Compliant linear motion';
 document.querySelector('.brand').textContent='Rack actuator';
 document.querySelector('.view-title').textContent=data.motor+' · '+data.stroke+' mm';
 $('variantSummary').textContent=is14?'34 mm body · 25° pinion':'40 mm body · 20° pinion';
 const metrics=document.querySelectorAll('.metrics strong');metrics[0].innerHTML=data.stroke+'<span>mm</span>';metrics[1].innerHTML=[data.actuatorLength,+(data.caseBounds[3]-data.caseBounds[2]).toFixed(1)].join(' × ')+'<span>mm</span>';metrics[3].textContent=data.pinionTeeth+'T / m'+data.toothModule;
 document.querySelectorAll('.metrics label')[3].textContent=data.pressureAngle+'° pinion';
 const details=document.querySelectorAll('.details dd');
 details[0].innerHTML=data.motor+', '+data.motorSize+' × '+data.motorSize+' × '+data.motorDepth+' mm reference motor<br>5 mm D shaft · 0.5 mm-deep flat<br>'+data.motorPitch+' mm mounting pitch<br>Integral 5 mm motor mounting land';
 details[2].innerHTML=data.rackLength+' mm guide + '+data.outputPadSize[0]+' mm output pad<br>0.60 mm walls · 8 mm tooth face<br>Round reliefs: R'+data.centralReliefRadius.toFixed(3)+' / R'+data.intertoothReliefRadius.toFixed(3)+' mm<br>'+data.rackBackboneWidth+' mm backbone · '+data.hardwareClearance+' mm head relief<br>'+data.solidRackEndLength.toFixed(2)+' mm solid end before mounting pad';
 details[3].innerHTML='Two sets of 3 × 625ZZ · '+data.stationSpacing+' mm apart<br>Exit bearing center '+data.exitBearingOffset+' mm behind opening<br>Motor and rear bearing set fixed<br>Restored single-floor flexure · '+data.springThickness.toFixed(2)+' mm thick';
 details[4].innerHTML='Front: 4 × M3 inserts, '+(data.frontMounts[2][0]-data.frontMounts[0][0]).toFixed(1)+' × '+(data.frontMounts[1][1]-data.frontMounts[0][1]).toFixed(1)+' mm pattern<br>Side: 4 × M3 inserts, '+(data.caseMounts[2][0]-data.caseMounts[0][0]).toFixed(1)+' × '+(data.caseMounts[1][1]-data.caseMounts[0][1]).toFixed(1)+' mm pattern<br>Side inserts: '+data.sideMountInsertRecess+' mm recessed<br>Top: 4 × M3 inserts, '+(data.topMounts[2][0]-data.topMounts[0][0]).toFixed(1)+' × '+(data.topMounts[1][1]-data.topMounts[0][1]).toFixed(1)+' mm pattern<br>Top screws: 3–'+data.insertLength+' mm engagement<br>Output: 4 × M3 inserts, '+data.outputMountPitch+' × '+data.outputMountPitch+' mm pattern<br>Output pad: '+data.outputPadSize[0]+' × '+data.outputPadSize[1]+' mm; '+data.outputInsertRecess+' mm insert recess';
 details[5].innerHTML=data.envelope.map(n=>Number(n.toFixed(1))).join(' × ')+' mm at center<br>'+(data.envelope[0]+data.stroke/2).toFixed(1)+' mm swept length · driver excluded';
 details[6].innerHTML=circ.toFixed(2)+' mm per motor revolution<br>'+(circ/200).toFixed(3)+' mm per full step at 200 steps/rev';
 $('resolutionIntro').textContent='1.8° motor · 200 full steps/rev · '+data.pinionTeeth+'T, module '+data.toothModule+' · '+circ.toFixed(3)+' mm/rev';
 document.querySelector('.resolution-formula').textContent='Travel per command = π × '+(2*data.pitchRadius)+' mm ÷ (200 × microstep factor)';
 document.querySelector('.resolution-table tbody').innerHTML=[1,2,4,8,16].map(f=>'<tr><th scope="row">'+(f===1?'Full step':f===2?'Half step (1/2)':'1/'+f+' step')+'</th><td>'+(200*f).toLocaleString('en-US')+'</td><td>'+(circ/(200*f)).toFixed(6)+'</td><td>'+(1000*circ/(200*f)).toFixed(3)+'</td><td>'+(200*f/circ).toFixed(5)+'</td></tr>').join('');
 for(const a of document.querySelectorAll('a[href^="downloads/"]'))a.href=basePath+a.getAttribute('href').replace('FLEX17',short);

 document.querySelector('footer span').textContent=data.motor+' rack actuator';
 $('configDepth').value=data.motorDepth;$('configStroke').value=data.stroke;updateConfiguration();
 const gridSize=Math.max(240,Math.ceil((data.envelope[0]+data.stroke/2)/100)*100),newGrid=new THREE.GridHelper(gridSize,gridSize/(gridSize>400?20:10),0xd1d5db,0xe5e7eb);grid.geometry.dispose();grid.geometry=newGrid.geometry;newGrid.material.dispose();grid.position.x=(data.caseBounds[0]+data.rackRight+data.outputPadSize[0]+data.stroke/2)/2;
 $('presetNote').textContent=data.actuatorLength+' mm housing · '+data.stationSpacing+' mm bearing span';
 $('sizeNote').textContent=data.stroke>40?'Long-stroke versions require a suitably large printer; stiffness and load capacity have not been physically tested.':'';
 $('insertSpec').textContent=data.insertCount+' × M3 heat-set inserts, Ø'+data.insertOD+' × '+data.insertLength+' mm; Ø'+data.insertPilot+' mm pilot ('+data.enclosureInsertCount+' enclosure + '+data.outputInsertCount+' output). '+data.coverScrewCount+' × M3×20 lid screws and '+data.chassisScrewCount+' × M3×10 chassis screws. Front, side and output mounts each use four M3 screws with 3–'+data.insertLength+' mm thread engagement.';
 if(presetInfo){$('bundleDownload').href=basePath+'downloads/'+presetInfo.bundleFile+'?v=21';$('stepDownload').href=basePath+'downloads/'+presetInfo.stepFile+'?v=21';$('stepDownload').textContent=presetInfo.stepFile.endsWith('.gz')?'STEP (.gz)':'STEP assembly'}
}
$('motorVariant').onchange=()=>{const url=new URL(location.href);url.searchParams.set('motor',$('motorVariant').value);location.href=url.href};


$('strokePreset').onchange=()=>{const url=new URL(location.href);url.searchParams.set('motor',variant);url.searchParams.set('stroke',$('strokePreset').value);location.href=url.href};
function viewDirection(v){resetCamera(new THREE.Vector3(...v))}
$('mounts').onclick=()=>{setMode('motion');$('enclosure').checked=true;update();viewDirection([.6,1.2,-.2])};
$('frontMounts').onclick=()=>{setMode('motion');$('enclosure').checked=true;$('ghost').checked=false;update();viewDirection([1,0,0])};
$('topMounts').onclick=()=>{setMode('motion');$('enclosure').checked=true;$('ghost').checked=false;update();viewDirection([.15,-.2,1])};
$('driver').onclick=()=>{setMode('motion');$('enclosure').checked=true;update();viewDirection([1,-1.3,-1.2])};
function configuredValues(){
 const m=+$('configModule').value,stroke=+$('configStroke').value,depth=+$('configDepth').value,teeth=variant==='nema14'?14:18,angle=(variant==='nema14'?25:20)*Math.PI/180,pitch=Math.PI*m;
 const last=Math.floor((stroke/2+pitch)/pitch)*pitch,extent=last+pitch/4+1.25*m*Math.tan(angle)+.1;
 const right=Math.max(57,Math.ceil(Math.max(52,extent+stroke/2+3.4))),minimum=Math.ceil(right+32+stroke+16.4),length=$('configLength').value===''?minimum:+$('configLength').value;
 return {motor:variant,tooth_module:m,stroke,actuator_length:length,motor_depth:depth,minimum,pitch,increment:Math.PI*m*teeth/200};
}
function updateConfiguration(){
 const v=configuredValues();$('configLength').min=v.minimum;$('configLength').placeholder='Auto: '+v.minimum+' mm';
 const valid=['configModule','configStroke','configLength','configDepth'].every(id=>$(id).checkValidity())&&Number.isFinite(v.minimum)&&v.actuator_length>=v.minimum;
 $('configDownload').disabled=!valid;$('configCopy').disabled=!valid;
 $('configSummary').textContent=valid?'Housing '+v.actuator_length+' mm (minimum '+v.minimum+' mm) · tooth pitch '+v.pitch.toFixed(3)+' mm · full step '+v.increment.toFixed(6)+' mm · 1/16 '+(v.increment/16).toFixed(6)+' mm':'Check the parameter limits. Housing must be at least '+v.minimum+' mm for this configuration.';
 $('configCommand').textContent='python model.py --motor '+v.motor+' --tooth-module '+v.tooth_module+' --stroke '+v.stroke+' --actuator-length '+v.actuator_length+' --motor-depth '+v.motor_depth+' --out build/'+v.motor+' --check';
}
for(const id of ['configModule','configStroke','configLength','configDepth'])$(id).oninput=updateConfiguration;
$('configCopy').onclick=async()=>{await navigator.clipboard.writeText($('configCommand').textContent);$('configCopy').textContent='Copied';setTimeout(()=>$('configCopy').textContent='Copy command',1500)};
$('configDownload').onclick=()=>{const v=configuredValues();delete v.minimum;delete v.pitch;delete v.increment;const u=URL.createObjectURL(new Blob([JSON.stringify(v,null,2)+'\n'],{type:'application/json'})),a=document.createElement('a');a.href=u;a.download='actuator-'+variant+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};

async function readSpringStates(url){const response=await fetch(url);if(!response.ok)throw new Error('Spring geometry unavailable');const buffer=await response.arrayBuffer(),bytes=new Uint8Array(buffer);if(bytes[0]===31&&bytes[1]===139)return new Response(new Blob([buffer]).stream().pipeThrough(new DecompressionStream('gzip'))).json();return JSON.parse(new TextDecoder().decode(bytes))}
try{const catalog=await(await fetch('./presets.json?v=21')).json();presetInfo=catalog.presets.find(p=>p.motor===variant&&p.stroke===presetStroke);data=await readSpringStates(basePath+'assets/'+(presetInfo?.assemblyFile||'assembly.json')+'?v=21');applyVariant();data.springStates=await readSpringStates(springPath+'?v=21');document.querySelector('.stages').innerHTML=data.stages.map(t=>'<li>'+t.label+'</li>').join('');for(const p of data.parts){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(p.vertices.flat(),3));geometry.setIndex(p.triangles.flat());geometry.computeVertexNormals();const mat=new THREE.MeshStandardMaterial({color:p.color,roughness:p.group==='motor'?.58:.4,metalness:p.name.includes('625ZZ')?.78:.16});const mesh=new THREE.Mesh(geometry,mat);mesh.userData=p;mesh.userData.solidMaterial=mat;mesh.userData.ghostMaterial=new THREE.MeshBasicMaterial({color:0xcbd5e1,transparent:true,opacity:.12,depthWrite:false,depthTest:true,side:THREE.FrontSide});mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry,30),new THREE.LineBasicMaterial({color:0x17232c,transparent:true,opacity:.5})));if(p.spinAxis){for(const sign of [-1,1]){const c=new THREE.Vector3(...p.spinCenter).addScaledVector(new THREE.Vector3(...p.spinAxis),sign*2.51);const g=new THREE.BufferGeometry().setFromPoints([c.clone().add(new THREE.Vector3(4.8,0,0)),c.clone().add(new THREE.Vector3(7.8,0,0))]);mesh.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:0x273b46})));}}if(p.flex_chassis){
 mesh.userData.springStates=[{l:0,r:0,geometry,edges:mesh.children[0].geometry}];
 for(const s of data.springStates){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(s.vertices.flat(),3));g.setIndex(s.triangles.flat());g.computeVertexNormals();mesh.userData.springStates.push({l:s.leftLift,r:s.rightLift,geometry:g,edges:new THREE.EdgesGeometry(g,30)});}
}scene.add(mesh);objects.push(mesh)}$('loading').hidden=true;update();resetCamera();window.FLEX17={data,scene,camera,controls,objects,hiddenParts,update,displacement,orientation,lowerLift,get mode(){return mode}};}catch(e){$('loading').textContent='The model could not load. Reload the page or download the STEP assembly.';console.error(e)}
try{const [report,service]=await Promise.all(['validation.json','flexure-service-validation.json'].map(async name=>(await fetch(basePath+'downloads/'+name+'?v=21')).json())),n=report.explosion_failures.length+report.motion_failures.length+service.failures.length;
 $('checkTitle').textContent='Validation';$('checkSummary').textContent=`${report.explosion_samples.toLocaleString()} explosion poses · ${service.samples} service poses · ${report.motion_samples} travel positions · ${n} unexpected intersections. Sampled CAD checks.`;
}catch(e){$('checkSummary').textContent='Check report unavailable.'}
function animate(time){requestAnimationFrame(animate);const dt=Math.min(.05,(time-last)/1000);last=time;if(playing&&mode==='motion'){phase+=dt*.65;$('travel').value=(.5+.5*Math.sin(phase))*+$('stroke').value;update()}controls.update();grid.visible=camera.position.z>grid.position.z;renderer.render(scene,camera)}requestAnimationFrame(animate);
