// Surface annotations use CAD mesh coordinates, independent of rigid viewer motion.
export function createPointMarkers({THREE,getObjects,getContext,closeMenu}){
 const $=id=>document.getElementById(id),menu=$('partMenu');
 const markButton=document.createElement('button');markButton.id='menuMarkPoint';markButton.textContent='Mark point';markButton.setAttribute('role','menuitem');markButton.hidden=true;
 menu.appendChild(markButton);
 const copyMenu=document.createElement('button');copyMenu.id='menuCopyPoints';copyMenu.textContent='Copy points';copyMenu.setAttribute('role','menuitem');copyMenu.disabled=true;menu.appendChild(copyMenu);
 const resetMenu=document.createElement('button');resetMenu.id='menuResetPoints';resetMenu.textContent='Reset marked points';resetMenu.setAttribute('role','menuitem');resetMenu.disabled=true;menu.appendChild(resetMenu);
 const panel=document.createElement('section');panel.className='point-tools';panel.setAttribute('aria-label','Marked points');
 panel.innerHTML='<strong>Marked points <span id="pointCount">0</span></strong><p class="hint">Right-click a surface → Mark point. Copy the points to describe a bridge.</p><div class="point-actions"><button id="copyPoints" disabled>Copy points</button><button id="undoPoint" disabled>Undo</button><button id="clearPoints" disabled>Reset points</button></div><ol id="pointList"></ol><p id="pointStatus" class="hint" aria-live="polite"></p><textarea id="pointCopyText" aria-label="Marked point coordinates to copy" readonly hidden></textarea>';
 document.querySelector('aside').appendChild(panel);
 const geometry=new THREE.SphereGeometry(1.4,20,12),material=new THREE.MeshBasicMaterial({color:0xef2424,transparent:true,opacity:.4,depthWrite:false,depthTest:false});
 let pending=null,points=[],markers=[],storageKey;
 const vector=v=>v.toArray().map(x=>+x.toFixed(3));
 function capture(hit){
  pending=null;markButton.hidden=!hit;
  if(hit){hit.object.updateWorldMatrix(true,false);pending={part:hit.object.userData.name,model_mm:vector(hit.object.worldToLocal(hit.point.clone())),view_mm_at_mark:vector(hit.point),normal_model:hit.face?vector(hit.face.normal.clone().normalize()):null,context:structuredClone(getContext())};}
 }
 function addVisual(point){
  const part=getObjects().find(o=>o.userData.name===point.part);if(!part)return;
  const sphere=new THREE.Mesh(geometry,material);sphere.name='Marked point P'+point.id;sphere.position.fromArray(point.model_mm);sphere.renderOrder=20;sphere.raycast=()=>{};
  const canvas=document.createElement('canvas');canvas.width=96;canvas.height=48;const ctx=canvas.getContext('2d');ctx.font='bold 32px system-ui';ctx.textAlign='center';ctx.textBaseline='middle';ctx.lineWidth=5;ctx.strokeStyle='#fff';ctx.strokeText('P'+point.id,48,24);ctx.fillStyle='#c41515';ctx.fillText('P'+point.id,48,24);
  const texture=new THREE.CanvasTexture(canvas),label=new THREE.Sprite(new THREE.SpriteMaterial({map:texture,transparent:true,depthTest:false,depthWrite:false}));label.scale.set(6,3,1);label.position.set(0,0,3);label.renderOrder=21;label.raycast=()=>{};sphere.add(label);part.add(sphere);markers.push(sphere);
 }
 function removeVisual(sphere){sphere.removeFromParent();for(const label of sphere.children){label.material.map.dispose();label.material.dispose();}}
 function refresh(){
  $('pointCount').textContent=points.length;for(const id of ['copyPoints','undoPoint','clearPoints'])$(id).disabled=!points.length;copyMenu.disabled=!points.length;resetMenu.disabled=!points.length;
  $('pointList').replaceChildren();for(const p of points){const li=document.createElement('li');li.textContent=`P${p.id} · ${p.model_mm.map(n=>n.toFixed(2)).join(', ')} mm — ${p.part}`;$('pointList').appendChild(li);}
  $('pointCopyText').hidden=true;
  if(storageKey)try{localStorage.setItem(storageKey,JSON.stringify(points))}catch{}
 }
 function restore(){
  const c=getContext(),preset=[c.drive,c.motor,c.stroke_mm,c.enclosure];storageKey='actuator-points:'+JSON.stringify(preset);
  try{
   let raw=localStorage.getItem(storageKey);
   // Keep annotations made before a CAD update; each point retains its source revision.
   if(raw===null){const legacy=[];for(let i=0;i<localStorage.length;i++){const key=localStorage.key(i);if(!key.startsWith('actuator-points:'))continue;try{const signature=JSON.parse(key.slice('actuator-points:'.length));if(Array.isArray(signature)&&signature.length===5&&JSON.stringify(signature.slice(0,4))===JSON.stringify(preset)){const old=JSON.parse(localStorage.getItem(key));if(Array.isArray(old))legacy.push(...old);}}catch{}}raw=JSON.stringify(legacy);}
   const saved=JSON.parse(raw||'[]');if(Array.isArray(saved))points=saved.filter(p=>typeof p.part==='string'&&Array.isArray(p.model_mm)&&p.model_mm.length===3&&p.model_mm.every(Number.isFinite)&&p.context&&getObjects().some(o=>o.userData.name===p.part)).map((p,i)=>({...p,id:i+1}));
  }catch{}
  points.forEach(addVisual);refresh();
  if(points.some(p=>p.context.model_revision!==c.model_revision))$('pointStatus').textContent='Restored points from an earlier model. Copied coordinates include their original revision and pose.';
 }
 function exportData(){return {schema:'actuator-marked-points/v1',units:'mm',coordinates:'model_mm are CAD mesh coordinates before rigid actuation/explode transforms; context records the spring/assembly pose at marking.',points:structuredClone(points)}}
 async function copy(){
  if(!points.length)return;closeMenu();const text=JSON.stringify(exportData(),null,2);
  try{await navigator.clipboard.writeText(text);$('pointStatus').textContent=`Copied ${points.length} points. Paste them into the chat.`;}
  catch{$('pointCopyText').value=text;$('pointCopyText').hidden=false;$('pointCopyText').focus();$('pointCopyText').select();$('pointStatus').textContent='Clipboard unavailable. Copy the selected text below.';}
 }
 markButton.onclick=()=>{if(!pending)return;const p={id:points.length+1,...structuredClone(pending)};points.push(p);addVisual(p);closeMenu();refresh();$('pointStatus').textContent=`Marked P${p.id}.`;};
 copyMenu.onclick=copy;$('copyPoints').onclick=copy;
 $('undoPoint').onclick=()=>{if(!points.length)return;points.pop();removeVisual(markers.pop());refresh();$('pointStatus').textContent='Last point removed.';};
 function resetPoints(){
  closeMenu();pending=null;markButton.hidden=true;points=[];markers.forEach(removeVisual);markers=[];
  // Remove older revision entries for this preset so cleared marks cannot return.
  if(storageKey)try{const preset=JSON.parse(storageKey.slice('actuator-points:'.length));for(const key of Object.keys(localStorage)){if(!key.startsWith('actuator-points:'))continue;try{const signature=JSON.parse(key.slice('actuator-points:'.length));if(Array.isArray(signature)&&JSON.stringify(signature.slice(0,4))===JSON.stringify(preset))localStorage.removeItem(key);}catch{}}}catch{}
  $('pointCopyText').value='';refresh();$('pointStatus').textContent='Marked points reset.';
 }
 resetMenu.onclick=resetPoints;$('clearPoints').onclick=resetPoints;
 return {capture,restore,exportData,get markers(){return markers}};
}
