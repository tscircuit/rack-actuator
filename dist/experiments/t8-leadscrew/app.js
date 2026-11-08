import * as THREE from 'three';
import {OrbitControls} from '../../assets/OrbitControls.js';
import {createPointMarkers} from '../../point-markers.js?v=43';
import {downloadPart} from '../../part-download.js?v=44';
const requestedWidth=Number(new URLSearchParams(location.search).get('width')||1),width=location.pathname.includes('/printed-leadscrew/')&&[1,2,4].includes(requestedWidth)?requestedWidth:1,assetPrefix=width===1?'':`widths/${width}x/`;
const $=id=>document.getElementById(id),vp=$('viewport'),scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(35,1,.1,2500);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0,0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;vp.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=15;controls.maxDistance=1500;
scene.add(new THREE.HemisphereLight(0xffffff,0x738291,2));for(const [x,y,z,p] of [[-90,-110,220,3],[100,100,100,2]]){const light=new THREE.DirectionalLight(0xffffff,p);light.position.set(x,y,z);scene.add(light)}
const grid=new THREE.GridHelper(600,60,0xcbd5e1,0xe2e8f0);grid.rotation.x=Math.PI/2;grid.position.z=-.2;scene.add(grid);
const extensionGeometry=new THREE.BufferGeometry(),extensionLine=new THREE.LineSegments(extensionGeometry,new THREE.LineBasicMaterial({color:0xea580c}));scene.add(extensionLine);
const objects=[],hidden=new Set();let data,selected=null,playing=false,phase=0,last=0;
function closeMenu(){$('partMenu').hidden=true}
const markers=createPointMarkers({THREE,getObjects:()=>objects,closeMenu,getContext:()=>({drive:data?.experiment||'t8-leadscrew',motor:'nema17',stroke_mm:40,enclosure:'structural-lid'+(width===1?'':`-${width}x`),width_multiple:width,model_revision:data?.modelSourceSha256,mode:$('viewMode').value,travel_mm:$('viewMode').value==='exploded'?0:+$('travel').value,explosion_percent:+$('explode').value,snap_prong_deflection_mm:snapDeflection(),bearing_adjustment_mm:$('viewMode').value==='exploded'?[1]:[+$('adjust0').value]})});
function labelName(p){return p.name===data?.baseName?'Adjustable bearing base':p.name}
function select(o){selected=o;$('partSelect').value=o?.userData.name||'';for(const id of ['hideSelected','downloadSelected'])$(id).disabled=!o}
function stop(){playing=false;$('play').textContent='Play actuation'}
function explodeOffset(p,t){const keys=p.explodeKeyframes;let a=keys[0],b=keys.at(-1);for(let i=1;i<keys.length;i++)if(t<=keys[i].t){a=keys[i-1];b=keys[i];break}const f=Math.max(0,Math.min(1,(t-a.t)/(b.t-a.t)));return a.offset.map((v,i)=>v+(b.offset[i]-v)*f)}
function explosionPhase(){return Math.max(0,Math.min(1,(+$('explode').value/100-.2)/.8))}
function snapDeflection(){if($('viewMode').value!=='exploded')return 0;const t=explosionPhase();return (data?.snapAxle?.compression??.85)*Math.max(0,Math.min(1,(t-.6)/.02,(.72-t)/.02))}
const originalGeometry=new WeakMap();
function bendSnapGeometry(g,bearings,amount){
 if(!originalGeometry.has(g))originalGeometry.set(g,new Float32Array(g.attributes.position.array));
 const original=originalGeometry.get(g),pos=g.attributes.position;
 for(let i=0;i<pos.count;i++){
  const x=original[3*i],y=original[3*i+1],z=original[3*i+2];let mx=x,my=y,mz=z;
  if(amount)for(const b of bearings){const spec=data.snapAxle,dx=x-b.center[0],dy=y-b.center[1],dz=z-b.center[2],t=dy*b.axis[1]+dz*b.axis[2];
   const n=Math.abs(b.axis[2])>.01?[0,Math.sign(b.axis[1])*Math.sqrt(3)/2,.5]:[0,0,-1],bias=Math.tan(spec.tip_bend_degrees*Math.PI/180)*Math.min(0,t-spec.bend_start_t),uy=dy-bias*n[1],uz=dz-bias*n[2],r2=dx*dx+uy*uy+uz*uz-t*t;
   if(t>=spec.tip_t-.002&&t<spec.root_t&&r2<=(t<spec.head_back_t+.001?3.202**2:2.402**2)&&Math.abs(dx)>.001){
    mx-=Math.sign(dx)*amount*Math.min(1,(spec.root_t-t)/(spec.root_t-spec.head_back_t));
    const straighten=Math.min(1,amount/spec.compression);my-=straighten*bias*n[1];mz-=straighten*bias*n[2];break;
   }
  }
  pos.setXYZ(i,mx,my,mz);
 }
 pos.needsUpdate=true;if(g.index)g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();
}
function update(){if(!data)return;const exploded=$('viewMode').value==='exploded',dx=exploded?0:+$('travel').value,theta=-(exploded?200*Math.min(1,explosionPhase()/.2):dx)*2*Math.PI/data.lead,pivot=new THREE.Vector3(...data.axisOrigin),axis=new THREE.Vector3(1,0,0);
 for(const o of objects){const p=o.userData;o.position.set(0,0,0);o.quaternion.identity();if(p.group==='carriage')o.position.x=dx;
  if(p.group==='rotor'){o.quaternion.setFromAxisAngle(axis,theta);o.position.copy(pivot).sub(pivot.clone().applyQuaternion(o.quaternion))}
  if(p.bearing){const c=new THREE.Vector3(...p.center),u=new THREE.Vector3(...p.axis);o.quaternion.setFromAxisAngle(u,-dx/8*(p.axis[2]===0?-p.axis[1]:Math.sign(p.axis[1])));o.position.add(c).sub(c.clone().applyQuaternion(o.quaternion))}
  if(!exploded&&p.adjustIndex!==undefined)o.position.z+=+$('adjust'+p.adjustIndex).value-1;
  if(exploded)o.position.add(new THREE.Vector3(...explodeOffset(p,+$('explode').value/100)));
  if(p.snapBearings){const amount=snapDeflection();if(o.snapAmount!==amount){bendSnapGeometry(o.geometry,p.snapBearings,amount);bendSnapGeometry(o.children[0].geometry,p.snapBearings,amount);o.snapAmount=amount}}
  o.visible=!hidden.has(p.name)&&(p.name!==data.baseName||$('baseVisible').checked)&&(p.name!==data.lidName||$('lidVisible').checked);o.children[0].visible=$('edges').checked;
  const translucent=(p.name==='Hollow triangular carriage'&&$('transparentCarriage').checked)||(p.name===data.lidName&&$('transparentLid').checked);o.material.transparent=translucent;o.material.opacity=translucent?.25:1;o.material.depthWrite=!translucent;
 }
 for(let j=0;j<1;j++)$('adjustValue'+j).textContent=+$('adjust'+j).value===1?'Contact':(1-+$('adjust'+j).value).toFixed(2)+' mm loose';$('adjustControls').hidden=exploded;extensionLine.visible=!exploded;$('motionControls').hidden=exploded;$('explosionControls').hidden=!exploded;$('explodeValue').textContent=$('explode').value+'%';
 const exit=data.exitPlaneX,face=exit+dx,dimensionY=-(data.baseWidth||80)/2-4;extensionGeometry.setFromPoints([new THREE.Vector3(exit,dimensionY,8),new THREE.Vector3(face,dimensionY,8),new THREE.Vector3(exit,dimensionY,3),new THREE.Vector3(exit,dimensionY,13),new THREE.Vector3(face,dimensionY,3),new THREE.Vector3(face,dimensionY,13)]);
 $('travelValue').textContent=dx.toFixed(2)+' mm';$('rotationValue').textContent=(dx/data.lead).toFixed(2)+' screw revolutions from retracted';$('modeBadge').textContent=exploded?'EXPLODED ASSEMBLY':playing?'ACTUATING':'PROTOTYPE';$('status').textContent=hidden.size?hidden.size+' hidden parts':'';
}
function fit(direction=new THREE.Vector3(1,-1.3,.9)){direction.normalize();const bb=new THREE.Box3();for(const o of objects)if(o.visible)bb.expandByObject(o);if(bb.isEmpty())return;const c=bb.getCenter(new THREE.Vector3()),s=bb.getSize(new THREE.Vector3());let d=s.length()/2/Math.sin(THREE.MathUtils.degToRad(camera.fov/2));if(camera.aspect<1)d/=camera.aspect;controls.target.copy(c);camera.position.copy(c).addScaledVector(direction,d*1.05);controls.update()}
function showAll(){hidden.clear();$('baseVisible').checked=true;$('lidVisible').checked=true;$('transparentCarriage').checked=false;closeMenu();update()}
function hide(o){if(o){hidden.add(o.userData.name);select(null)}closeMenu();update()}
function isolate(o){if(!o)return;hidden.clear();for(const q of objects)if(q!==o)hidden.add(q.userData.name);$('baseVisible').checked=true;$('lidVisible').checked=true;$('transparentCarriage').checked=false;closeMenu();update()}
function download(o){if(!o)return;closeMenu();const p=o.userData;downloadPart(p,{url:p.stl?assetPrefix+p.stl+'?rev='+data.modelSourceSha256:undefined,filename:data.experiment+'-'+width+'x-40mm-'+(p.printed?'':'reference-')+labelName(p).toLowerCase().replaceAll(' ','_')+'.stl'})}
$('viewMode').onchange=()=>{stop();update();fit()};$('explode').oninput=()=>{stop();update()};$('explodeAll').onclick=()=>{$('explode').value=100;update();fit()};$('assembleAll').onclick=()=>{$('explode').value=0;update();fit()};
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause actuation':'Play actuation';phase=Math.asin((+$('travel').value-20)/20);update()};$('travel').oninput=()=>{stop();update()};for(const id of ['baseVisible','lidVisible','transparentLid','transparentCarriage','edges','adjust0'])$(id).oninput=update;
$('iso').onclick=()=>fit();$('fit').onclick=()=>fit();$('top').onclick=()=>fit(new THREE.Vector3(0,-.001,1));$('reset').onclick=()=>{stop();$('viewMode').value='motion';$('explode').value=0;$('adjust0').value=1;showAll();$('travel').value=0;$('edges').checked=false;$('transparentLid').checked=true;select(null);update();fit()};
$('guideView').onclick=()=>{stop();showAll();for(const o of objects)if(!o.userData.bearing&&o.userData.group!=='rotor'&&o.userData.name!=='T8x8 brass flange nut')hidden.add(o.userData.name);update();controls.target.set((data.stations[0]+data.stations[1])/2,0,42);fit(new THREE.Vector3(1,-1,.5))};
$('axisView').onclick=()=>{stop();showAll();update();fit(new THREE.Vector3(1,0,0))};
$('flexureView').onclick=()=>{stop();showAll();for(const o of objects)if(o.userData.group!=='guide'&&o.userData.name!==data.baseName&&o.userData.name!==data.carrierName&&!o.userData.heatSet&&!o.userData.name.includes('adjustment'))hidden.add(o.userData.name);update();fit(new THREE.Vector3(.8,-1,.65))};
$('nutView').onclick=()=>{stop();showAll();for(const o of objects)if(o.userData.group!=='carriage'&&!o.userData.name.startsWith('Printed 20 mm')&&!o.userData.name.startsWith('T8x8 threaded'))hidden.add(o.userData.name);$('transparentCarriage').checked=true;update();fit(new THREE.Vector3(.8,-1,.6))};
$('ridgeView').onclick=()=>{stop();isolate(objects.find(o=>o.userData.name===data.carrierName));fit(new THREE.Vector3(.8,-1,.6))};
$('partSelect').onchange=()=>select(objects.find(o=>o.userData.name===$('partSelect').value));$('hideSelected').onclick=()=>hide(selected);$('downloadSelected').onclick=()=>download(selected);$('showAll').onclick=showAll;
const ray=new THREE.Raycaster();function pick(e){scene.updateMatrixWorld(true);camera.updateMatrixWorld(true);const r=renderer.domElement.getBoundingClientRect();ray.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,1-(e.clientY-r.top)/r.height*2),camera);return ray.intersectObjects(objects.filter(o=>o.visible),false)[0]||null}
let start;renderer.domElement.addEventListener('pointerdown',e=>{start=[e.clientX,e.clientY];closeMenu()});renderer.domElement.addEventListener('pointerup',e=>{if(e.button===0&&start&&Math.hypot(e.clientX-start[0],e.clientY-start[1])<5)select(pick(e)?.object)});
renderer.domElement.addEventListener('contextmenu',e=>{e.preventDefault();stop();const hit=pick(e),o=hit?.object;markers.capture(hit);select(o);$('menuPartName').textContent=o?labelName(o.userData):'Parts';for(const id of ['menuHide','menuIsolate','menuDownload'])$(id).hidden=!o;$('menuDownload').textContent=o?.userData.printed?'Download STL':'Download reference STL';const menu=$('partMenu');menu.hidden=false;menu.style.left=Math.min(e.clientX,innerWidth-menu.offsetWidth-8)+'px';menu.style.top=Math.min(e.clientY,innerHeight-menu.offsetHeight-8)+'px';(o?$('menuHide'):$('menuShowAll')).focus()});
$('menuHide').onclick=()=>hide(selected);$('menuIsolate').onclick=()=>isolate(selected);$('menuDownload').onclick=()=>download(selected);$('menuShowAll').onclick=showAll;document.addEventListener('pointerdown',e=>{if(!$('partMenu').contains(e.target))closeMenu()});document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu()});
new ResizeObserver(()=>{camera.aspect=vp.clientWidth/vp.clientHeight;camera.updateProjectionMatrix();renderer.setSize(vp.clientWidth,vp.clientHeight,false);if(data)fit()}).observe(vp);
if($('widthVariant')){$('widthVariant').value=String(width);$('widthVariant').onchange=()=>{stop();const url=new URL(location.href);url.searchParams.set('width',$('widthVariant').value);location.assign(url.href)};}
try{
 const response=await fetch(assetPrefix+'assembly.json.gz?v=17');if(!response.ok)throw Error('Assembly download failed');data=await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();
 if((data.widthMultiple||1)!==width)throw Error('Width configuration does not match the requested variant.');
 if($('widthSummary')){$('widthSummary').textContent=`${data.outputPlateWidth} × 42 mm output plate · ${data.baseWidth} mm base width · ${data.upperBearingSpan.toFixed(1)} mm upper bearing span. Motor and screw stay centered; ${data.lowerBearingCount/2} lower bearing${data.lowerBearingCount===2?'':'s'} per station. ${data.baseMount.hole_centers_xy_mm.length} base-floor holes.`;document.querySelector('.view-title').textContent=`NEMA17 · Printed Ø20 · 40 mm · ${width}× width`;$('bundleDownload').href=assetPrefix+'printed-leadscrew-prototype.zip?v=17';$('bundleDownload').download=`printed-leadscrew-${width}x-prototype.zip`;$('bundleDownload').textContent=`Download ${width}× STL & source bundle ↓`;$('reportDownload').href=assetPrefix+'validation.json?v=17';$('buildNotes').href=assetPrefix+'README.txt?v=17';}
 for(const p of data.parts){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p.vertices.flat(),3));g.setIndex(p.triangles.flat());g.computeVertexNormals();const mesh=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:p.color,metalness:p.printed?.05:.35,roughness:p.printed?.7:.4}));mesh.userData=p;mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(g,35),new THREE.LineBasicMaterial({color:0x475569,transparent:true,opacity:.45})));objects.push(mesh);scene.add(mesh);const option=document.createElement('option');option.value=p.name;option.textContent=labelName(p);$('partSelect').appendChild(option);
  if(p.printed){const a=document.createElement('a');a.href=assetPrefix+p.stl+'?rev='+data.modelSourceSha256;a.textContent=labelName(p)+' ↓';a.onclick=e=>{e.preventDefault();download(mesh)};$('printedDownloads').appendChild(a)}
 }
 // Helix lines communicate lead and rotation; fit checks use the conservative
 // smooth Ø8 mm screw envelope, not a manufacturing thread profile.
 const rod=objects.find(o=>o.userData.name.startsWith('T8x8 threaded rod'));
 if(rod)for(let start=0;start<4;start++){const points=[];for(let j=0;j<=1100;j++){const x=26+70*j/1100,t=(x-26)*2*Math.PI/8+start*Math.PI/2;points.push(new THREE.Vector3(x,4.015*Math.cos(t),42+4.015*Math.sin(t)))}const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:0x526a80}));line.raycast=()=>{};rod.add(line)}
 const metric=document.querySelectorAll('.metrics strong')[2];metric.innerHTML=data.guideBearingCount+'<span>625ZZ</span>';metric.nextElementSibling.textContent='Two bearing stations';
 $('adjustControls').querySelector('.hint').textContent=`Four M5 bolts engage heat-set inserts in the shared carrier and raise all ${data.lowerBearingCount} lower bearings together. Tighten evenly. The slider shows rigid take-up, not preload force.`;
 $('loading').hidden=true;update();fit();markers.restore();window.t8Viewer={objects,data,scene,camera,controls,renderer,update,fit,markers};
 const report=await(await fetch(assetPrefix+'validation.json?v=17')).json();if(report.source_sha256!==data.modelSourceSha256)throw Error('The check report does not match this geometry.');$('proof').innerHTML=`<div><strong>${report.motion?.samples??'—'} positions</strong><span>40 mm travel</span></div><div><strong>${data.stations[1]-data.stations[0]} mm</strong><span>Bearing-station spacing</span></div><div><strong>1 carrier</strong><span>Four tightening bolts</span></div>`;
 $('checkSummary').textContent=report.passed?`Geometry, 40 mm motion and staged assembly pass collision checks. ${data.guideBearingCount} snap-mounted bearings provide rank-5 guidance; ${data.lowerBearingCount} lower bearings share one carrier with four M5 heat-set inserts. The STL has Ø6.4 mm pilots for M5×9.5 mm inserts; the viewer shows the installed cavity. 4 × 4 mm retaining rails flank the bearing tracks. The bearing journals are straight; 3 mm longer exposed tips bend 30° and taper from Ø6.4 mm retaining shoulders 0.25 mm beyond the bearing faces; Ø7.4 mm lands support the inner races. Outer base holes are plain Ø5.5 mm through-holes; the central NEMA17 output pattern is retained. `+(data.baseMount.inherited_holes_xy_mm?.length?`The ${data.baseMount.inherited_holes_xy_mm.length} inherited inner holes are countersunk for flush M5 heads. Fasten them from above before installing the bearing carrier and carriage. `:'')+(data.printedDrive?`The motor braces are 42 mm long and 12 mm wide, with 1.5 mm nominal motor-side clearance. Rounded cutouts remove ${data.lightening.base.reduction_percent.toFixed(1)}% of the uncut revised base volume and ${data.lightening.carriage.reduction_percent.toFixed(1)}% of the carriage volume. Both threaded bands remain engaged throughout travel. `:'')+'Print fit, insert installation, PETG snap retention and structural stiffness require physical testing.':'Geometry checks are incomplete. See the report before printing.';
}catch(e){console.error(e);if(data)$('checkSummary').textContent='Check report unavailable: '+e.message;else $('loading').textContent='Could not load model: '+e.message}
function frame(now){const dt=last?Math.min(.05,(now-last)/1000):0;last=now;if(playing){phase+=dt*.4;$('travel').value=20+20*Math.sin(phase);update()}controls.update();renderer.render(scene,camera);requestAnimationFrame(frame)}requestAnimationFrame(frame);
