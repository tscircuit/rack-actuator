import * as THREE from 'three';
import {OrbitControls} from './assets/OrbitControls.js';
const variant=new URLSearchParams(location.search).get('motor')==='nema14'?'nema14':'nema17',basePath=variant==='nema14'?'./variants/nema14/':'./';
const $=id=>document.getElementById(id), vp=$('viewport');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0x000000,0);vp.appendChild(renderer.domElement);
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(35,1,.1,2000);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=75;controls.maxDistance=1500;
scene.add(new THREE.HemisphereLight(0xe3f3ff,0x293038,2));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(10,-50,120);scene.add(key);const rim=new THREE.DirectionalLight(0x8fbaff,2);rim.position.set(-50,90,45);scene.add(rim);
const grid=new THREE.GridHelper(240,24,0x4d6172,0x2a3947);grid.rotation.x=Math.PI/2;grid.position.z=-34;scene.add(grid);
let data,objects=[],playing=false,mode='motion',last=0,phase=0,selected=null;
function resetCamera(){
 if(!data||!objects.length){camera.position.set(210,-260,170);controls.target.set(0,16,-10);controls.update();return}
 const bounds=new THREE.Box3(),samples=mode==='explode'?[0,...data.stages.map(s=>s.end)]:[0];
 for(const mesh of objects){if(!mesh.visible)continue;mesh.geometry.computeBoundingBox();
  for(const e of samples){const pos=new THREE.Vector3(...displacement(mesh.userData.group,e)),a=orientation(mesh.userData.group,e),matrix=new THREE.Matrix4().makeRotationZ(a);
   if(['gear','shaft','set_screw'].includes(mesh.userData.group)){const pivot=new THREE.Vector3(...data.rotationPivot);pos.add(pivot.clone().sub(pivot.clone().applyMatrix4(matrix)))}
   matrix.setPosition(pos);const box=mesh.geometry.boundingBox.clone().applyMatrix4(matrix);bounds.union(box);
   if(mode==='motion'&&mesh.userData.group==='rack'){bounds.union(box.clone().translate(new THREE.Vector3(-data.stroke/2,0,0)));bounds.union(box.clone().translate(new THREE.Vector3(data.stroke/2,0,0)))}
  }
 }
 const center=bounds.getCenter(new THREE.Vector3()),size=bounds.getSize(new THREE.Vector3()),radius=size.length()/2+3;
 const half=Math.min(THREE.MathUtils.degToRad(camera.fov/2),Math.atan(Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*camera.aspect));
 const distance=radius/Math.sin(half)*1.08;
 camera.position.copy(center).addScaledVector(new THREE.Vector3(1,-1.25,.8).normalize(),distance);controls.target.copy(center);controls.update();
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
 const l=lowerLift(-23,e),r=lowerLift(23,e),states=m.userData.springStates;
 let best=0,dist=Infinity;for(let i=0;i<states.length;i++){const d=(states[i].l-l)**2+(states[i].r-r)**2;if(d<dist){dist=d;best=i}}
 if(m.userData.springStateIndex===best)return;
 m.geometry=states[best].geometry;m.children[0].geometry=states[best].edges;
 m.userData.springStateIndex=best;m.userData.appliedSpring=[states[best].l,states[best].r];
}
function displacement(group,e){const v=[0,0,group.startsWith('lower_')?lowerLift(group.includes('_left_')?-23:23,e):0];for(const t of data.tracks[group]||[]){const f=ramp(e,t.start,t.end);for(let i=0;i<3;i++)v[i]+=(t.delta||[0,0,0])[i]*f}return v}
function orientation(group,e){return (data.tracks[group]||[]).reduce((a,t)=>a+ramp(e,t.start,t.end)*(t.degrees||0),0)*Math.PI/180}
function update(){if(!data)return;const stroke=+$('stroke').value,travel=+$('travel').value,dx=travel-stroke/2,e=mode==='explode'?+$('explosion').value/100:0;
$('travelValue').innerHTML=travel.toFixed(1)+' <small>mm</small>';$('strokeValue').textContent=stroke+' mm';$('strokeEnd').textContent=stroke+' mm';$('explodeValue').textContent=Math.round(e*100)+'%';
for(const m of objects){if(m.userData.flex_chassis)deformSpring(m,e);const d=displacement(m.userData.group,e);m.position.set(...d);m.quaternion.identity();m.rotation.z=orientation(m.userData.group,e);if(mode==='motion'){if(m.userData.group==='rack')m.position.x=dx;if(['gear','set_screw','shaft'].includes(m.userData.group))m.rotation.z=-dx/data.pitchRadius;if(m.userData.spinAxis){const c=new THREE.Vector3(...m.userData.spinCenter);m.quaternion.setFromAxisAngle(new THREE.Vector3(...m.userData.spinAxis),m.userData.spinSign*dx/8);m.position.copy(c.clone().sub(c.clone().applyQuaternion(m.quaternion)));}}
if(['gear','set_screw','shaft'].includes(m.userData.group)){const p=new THREE.Vector3(...data.rotationPivot);m.position.add(p.clone().sub(p.clone().applyQuaternion(m.quaternion)));}
const shell=m.userData.name.startsWith('01'),outer=['tray','cover','cover_screws','chassis_screws'].includes(m.userData.group);m.visible=(!shell||$('shell').checked)&&(!outer||$('enclosure').checked);m.material.transparent=(shell||['tray','cover'].includes(m.userData.group))&&$('ghost').checked;m.material.opacity=m.material.transparent?.22:1;m.material.depthWrite=!m.material.transparent;m.children[0].visible=$('edges').checked;}
const active=data.stages.findIndex(t=>e>=t.start&&e<t.end);document.querySelectorAll('.stages li').forEach((li,i)=>li.classList.toggle('active',e>0&&i===(active<0?data.stages.length-1:active)));grid.position.z=mode==='explode'?-145:data.motorRearZ-8;$('modeBadge').textContent=mode==='motion'?(playing?'ACTUATING':'ASSEMBLED'):'STAGED EXPLOSION';}
function stop(){playing=false;$('play').textContent='Play actuation';}
function setMode(m){stop();mode=m;$('motionControls').hidden=m!=='motion';$('explosionControls').hidden=m!=='explode';for(const x of ['motion','explode']){$(x+'Tab').classList.toggle('active',x===m);$(x+'Tab').setAttribute('aria-selected',x===m)}controls.update();update();resetCamera()}
$('motionTab').onclick=()=>setMode('motion');$('explodeTab').onclick=()=>setMode('explode');$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause actuation':'Play actuation';update()};$('travel').oninput=()=>{stop();update()};$('explosion').oninput=update;$('stroke').oninput=()=>{const old=+$('travel').max,f=+$('travel').value/old;$('travel').max=$('stroke').value;$('travel').value=f*+$('stroke').value;update()};for(const id of ['shell','enclosure','ghost','edges'])$(id).onchange=update;
$('teeth').onclick=()=>{setMode('motion');$('enclosure').checked=false;$('ghost').checked=true;update();camera.position.set(25,5,90);controls.target.set(0,23,17);controls.update()};$('rollers').onclick=()=>{setMode('motion');$('enclosure').checked=false;$('shell').checked=true;$('ghost').checked=false;update();camera.position.set(110,125,-5);controls.target.set(0,33,-23);controls.update()};$('iso').onclick=resetCamera;$('fit').onclick=resetCamera;$('top').onclick=()=>{camera.position.set(0,10,235);controls.target.set(0,10,0);controls.update()};$('reset').onclick=()=>{stop();$('stroke').value=40;$('travel').max=40;$('travel').value=20;$('explosion').value=0;$('shell').checked=true;$('enclosure').checked=true;$('ghost').checked=false;$('edges').checked=false;setMode('motion');resetCamera()};
const roles={cover:'Removable cover with two rear chassis clamps. Print roof-down.',tray:'Mounting tray with motor rear aperture, four M4 mounting slots and captive nuts.',cover_screws:'M3×25 lid screw; extract and park before lifting the cover.',chassis_screws:'M4×12 screw secures the front chassis seat to the tray.',rack:'Stiff beveled guide with rounded compliant-tooth reliefs. Four upper rollers act down/inward, two lower rollers support upward.',fixed:'One-piece chassis: broad integral spring floors lift the lower bearing seats. No separate flexures or extra mounting hardware.',gear:'18-tooth module 2 pinion, oversized 5.30 mm D bore.',set_screw:'M3×4 flat-point screw bears on the D-shaft flat.',shaft:'Reference 5 mm D shaft, rotating with the pinion.',front_axles:'Front M5×16 angled axle; withdraw along its axis before parking clear.',rear_axles:'Rear M5×16 angled axle; removed after the front pair.',upper_rollers:'One of four 45° upper rollers or its inner-race washer.',front_nuts:'Captured front M5 axle nut.',rear_nuts:'Captured rear M5 axle nut.',bottom_axles:'M5×25 lower roller axle.',bottom_nuts:'Lower M5 axle nut; release before withdrawing its bolt.',bottom_rollers:'Lower 625ZZ roller or washer, supporting the flat underside of the rack.',motor:'Standard-depth reference motor.',motor_screws:'M3×12 countersunk motor screw.'};
for(const side of ['left','right'])for(const kind of ['nuts','axles','rollers'])roles['lower_'+side+'_'+kind]=kind==='nuts'?'M5 nut clamps the bearing inner race to the integral chassis seat.':kind==='axles'?'M5×25 axle follows its integral spring floor seat.':'Lower bearing or inner-race washer, pushed upward by the broad chassis spring floor.';
let start;
renderer.domElement.addEventListener('pointerdown',e=>start=[e.clientX,e.clientY]);renderer.domElement.addEventListener('pointerup',e=>{if(!start||Math.hypot(e.clientX-start[0],e.clientY-start[1])>5)return;const rect=vp.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1),camera);const hit=ray.intersectObjects(objects.filter(o=>o.visible),false)[0];if(selected)selected.material.emissive.setHex(0);selected=hit?.object;if(selected){selected.material.emissive.setHex(0x17352f);$('selection').textContent=selected.userData.name+' — '+(selected.userData.name.startsWith('625ZZ')?'625ZZ: 5 mm bore × 16 mm OD × 5 mm width. Its outer rim rolls on a guide face; the inner race stays clamped.':roles[selected.userData.group])}else $('selection').textContent='Click a part to inspect its role.'});

function applyVariant(){
 const short=variant==='nema14'?'FLEX14':'FLEX17',is14=variant==='nema14',circ=2*Math.PI*data.pitchRadius;
 $('motorVariant').value=variant;document.title=short+' | Compliant linear motion';
 document.querySelector('.brand').innerHTML='F<span>'+ (is14?'14':'17')+'</span><i></i> <b>'+short+'</b>';
 document.querySelector('.view-title').innerHTML=short+' <b>/</b> ASSEMBLY EXPLORER';
 $('variantSummary').textContent=is14?'NEMA14 · 34 mm body · enclosed 14T / 25° drive':'NEMA17 · 40 mm body · enclosed 18T / 20° drive';
 const metrics=document.querySelectorAll('.metrics strong');metrics[1].innerHTML=[data.actuatorLength,+(data.caseBounds[3]-data.caseBounds[2]).toFixed(1)].join(' × ')+'<span>mm</span>';metrics[3].textContent=data.pinionTeeth+'T / m'+data.toothModule;
 document.querySelectorAll('.metrics label')[3].textContent=data.pressureAngle+'° INVOLUTE PINION';
 const details=document.querySelectorAll('.details dd');
 details[0].innerHTML=data.motor+', '+data.motorSize+' × '+data.motorSize+' × '+data.motorDepth+' mm reference motor<br>5 mm D shaft · 0.5 mm-deep flat<br>'+data.motorPitch+' mm mounting pitch<br>Integral 5 mm motor mounting land';
 details[2].innerHTML=data.rackLength+' mm guide + 14 mm output pad<br>0.60 mm walls · 8 mm tooth face<br>Round reliefs: R'+data.centralReliefRadius.toFixed(3)+' / R'+data.intertoothReliefRadius.toFixed(3)+' mm<br>'+data.rackBackboneWidth+' mm backbone · '+data.hardwareClearance+' mm head relief<br>'+data.solidRackEndLength.toFixed(2)+' mm solid end before mounting pad';
 details[4].innerHTML='4 × M4 side-mount slots, 8 × 4.5 mm<br>'+(data.caseMounts[2][0]-data.caseMounts[0][0]).toFixed(0)+' × '+(data.caseMounts[1][1]-data.caseMounts[0][1]).toFixed(0)+' mm mounting pattern<br>Two Ø3.4 mm output holes, 9 mm pitch';
 details[5].innerHTML=data.envelope.map(n=>Number(n.toFixed(1))).join(' × ')+' mm at center<br>'+(data.envelope[0]+data.stroke/2).toFixed(1)+' mm swept length · driver excluded';
 details[6].innerHTML=circ.toFixed(2)+' mm per motor revolution<br>'+(circ/200).toFixed(3)+' mm per full step at 200 steps/rev';
 $('resolutionIntro').textContent='For a 1.8° motor (200 full steps/revolution) directly driving the '+data.pinionTeeth+'-tooth, module-'+data.toothModule+' pinion. Its '+(2*data.pitchRadius)+' mm pitch diameter gives '+circ.toFixed(6)+' mm of rack travel per revolution.';
 document.querySelector('.resolution-formula').textContent='Travel per command = π × '+(2*data.pitchRadius)+' mm ÷ (200 × microstep factor)';
 document.querySelector('.resolution-table tbody').innerHTML=[1,2,4,8,16].map(f=>'<tr><th scope="row">'+(f===1?'Full step':f===2?'Half step (1/2)':'1/'+f+' step')+'</th><td>'+(200*f).toLocaleString('en-US')+'</td><td>'+(circ/(200*f)).toFixed(6)+'</td><td>'+(1000*circ/(200*f)).toFixed(3)+'</td><td>'+(200*f/circ).toFixed(5)+'</td></tr>').join('');
 for(const a of document.querySelectorAll('a[href^="downloads/"]'))a.href=basePath+a.getAttribute('href').replace('FLEX17',short);
 roles.gear=data.pinionTeeth+'-tooth module '+data.toothModule+', '+data.pressureAngle+'° pinion with oversized 5.30 mm D bore.';roles.motor=data.motor+' reference motor, '+data.motorSize+' mm square × '+data.motorDepth+' mm deep.';
 document.querySelector('footer span').textContent=short+' / ENCLOSED LINEAR MODULE';
 $('configDepth').value=data.motorDepth;updateConfiguration();
}
$('motorVariant').onchange=()=>{const url=new URL(location.href);url.searchParams.set('motor',$('motorVariant').value);location.href=url.href};


function viewDirection(v){resetCamera();const distance=camera.position.distanceTo(controls.target);camera.position.copy(controls.target).addScaledVector(new THREE.Vector3(...v).normalize(),distance);controls.update()}
$('mounts').onclick=()=>{setMode('motion');$('enclosure').checked=true;update();viewDirection([.6,1.2,-.2])};
$('driver').onclick=()=>{setMode('motion');$('enclosure').checked=true;update();viewDirection([1,-1.3,-1.2])};
function configuredValues(){
 const m=+$('configModule').value,stroke=+$('configStroke').value,depth=+$('configDepth').value,teeth=variant==='nema14'?14:18,angle=(variant==='nema14'?25:20)*Math.PI/180,pitch=Math.PI*m;
 const last=Math.floor((stroke/2+pitch)/pitch)*pitch,extent=last+pitch/4+1.25*m*Math.tan(angle)+.1;
 const right=Math.ceil(Math.max(52,extent+stroke/2+3.4)),minimum=Math.ceil(right+stroke+39.4),length=$('configLength').value===''?minimum:+$('configLength').value;
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

try{const r=await fetch(basePath+'assets/assembly.json?v=15');if(!r.ok)throw new Error('CAD mesh unavailable');data=await r.json();applyVariant();data.springStates=await(await fetch(basePath+'assets/spring-states.json?v=15')).json();document.querySelector('.stages').innerHTML=data.stages.map(t=>'<li>'+t.label+'</li>').join('');for(const p of data.parts){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(p.vertices.flat(),3));geometry.setIndex(p.triangles.flat());geometry.computeVertexNormals();const mat=new THREE.MeshStandardMaterial({color:p.color,roughness:p.group==='motor'?.58:.4,metalness:p.name.includes('625ZZ')?.78:.16});const mesh=new THREE.Mesh(geometry,mat);mesh.userData=p;mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry,30),new THREE.LineBasicMaterial({color:0x17232c,transparent:true,opacity:.5})));if(p.spinAxis){for(const sign of [-1,1]){const c=new THREE.Vector3(...p.spinCenter).addScaledVector(new THREE.Vector3(...p.spinAxis),sign*2.51);const g=new THREE.BufferGeometry().setFromPoints([c.clone().add(new THREE.Vector3(4.8,0,0)),c.clone().add(new THREE.Vector3(7.8,0,0))]);mesh.add(new THREE.Line(g,new THREE.LineBasicMaterial({color:0x273b46})));}}if(p.flex_chassis){
 mesh.userData.springStates=[{l:0,r:0,geometry,edges:mesh.children[0].geometry}];
 for(const s of data.springStates){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(s.vertices.flat(),3));g.setIndex(s.triangles.flat());g.computeVertexNormals();mesh.userData.springStates.push({l:s.leftLift,r:s.rightLift,geometry:g,edges:new THREE.EdgesGeometry(g,30)});}
}scene.add(mesh);objects.push(mesh)}$('loading').hidden=true;update();resetCamera();window.FLEX17={data,scene,camera,controls,objects,update,displacement,orientation,lowerLift,get mode(){return mode}};}catch(e){$('loading').textContent='The model could not load. Reload the page or download the STEP assembly.';console.error(e)}
try{const report=await(await fetch(basePath+'downloads/validation.json?v=15')).json(),n=report.explosion_failures.length+report.motion_failures.length;$('checkTitle').textContent=n?'Geometry issues to review':'No unintended intersections sampled';$('checkSummary').textContent=report.output_pad_update?`The added pad volume has at least ${report.output_pad_update.minimum_continuous_x_gap_mm.toFixed(1)} mm X clearance throughout travel and explosion. Unchanged geometry retains the prior ${report.explosion_samples} explosion and ${report.motion_samples} travel checks. The pad face sits directly on the print plane.`:`${report.explosion_samples} explosion positions and ${report.motion_samples} travel positions checked with OpenCascade solid intersections. ${n} unexpected intersections found. ${report.minimum_rack_frame_gap_mm!==undefined?'Minimum printed-frame gap: '+(report.minimum_rack_frame_gap_is_lower_bound?'≥':'')+report.minimum_rack_frame_gap_mm.toFixed(2)+' mm at tested travel positions. ':''}${report.minimum_rack_hardware_gap_mm!==undefined?'Minimum axle hardware gap: '+report.minimum_rack_hardware_gap_mm.toFixed(2)+' mm. ':''}See exclusions and limits in the report.`}catch(e){$('checkSummary').textContent='The validation report could not be loaded. Download it for the full results.'}
function animate(time){requestAnimationFrame(animate);const dt=Math.min(.05,(time-last)/1000);last=time;if(playing&&mode==='motion'){phase+=dt*.65;$('travel').value=(.5+.5*Math.sin(phase))*+$('stroke').value;update()}controls.update();grid.visible=camera.position.z>grid.position.z;renderer.render(scene,camera)}requestAnimationFrame(animate);
