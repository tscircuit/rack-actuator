import {readZipEntry} from './zip-download.js';
// Printed parts use the CadQuery exports. Hardware uses its original reference
// mesh, independent of the viewer's actuation or exploded position.
export function referenceSTL(part) {
  const {vertices,triangles}=part;
  const minimum=[Infinity,Infinity,Infinity];
  for(const v of vertices)for(let j=0;j<3;j++)minimum[j]=Math.min(minimum[j],v[j]);
  const buffer=new ArrayBuffer(84+50*triangles.length),view=new DataView(buffer);
  new Uint8Array(buffer,0,80).set(new TextEncoder().encode('Rack actuator reference mesh; coordinates in mm'));
  view.setUint32(80,triangles.length,true);
  let offset=84;
  for(const triangle of triangles){
    const [a,b,c]=triangle.map(i=>vertices[i]);
    const u=b.map((v,j)=>v-a[j]),v=c.map((value,j)=>value-a[j]);
    const normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],length=Math.hypot(...normal)||1;
    for(const n of normal){view.setFloat32(offset,n/length,true);offset+=4;}
    for(const point of [a,b,c])for(let j=0;j<3;j++){view.setFloat32(offset,point[j]-minimum[j],true);offset+=4;}
    view.setUint16(offset,0,true);offset+=2;
  }
  return buffer;
}
let notification,timer;
function status(message){
  if(!notification){notification=document.createElement('div');notification.setAttribute('role','status');notification.className='part-download-status';document.body.appendChild(notification);}
  clearTimeout(timer);notification.textContent=message;notification.hidden=!message;
}
export async function downloadPart(part,{url,filename,zipEntry,mimeType='model/stl'}) {
  status('Downloading '+part.name+'…');
  try {
    let blob;
    if(part.printed&&zipEntry){
      blob=new Blob([await readZipEntry(url,zipEntry)],{type:mimeType});
    }else if(part.printed){
      const response=await fetch(url);
      if(!response.ok)throw new Error('Part download returned '+response.status);
      blob=new Blob([await (new URL(url,location.href).pathname.endsWith('.gz')
        ?new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).arrayBuffer()
        :response.arrayBuffer())],{type:mimeType});
    }else blob=new Blob([referenceSTL(part)],{type:mimeType});
    const objectURL=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=objectURL;link.download=filename;link.hidden=true;document.body.appendChild(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(objectURL),60000);status('');
  }catch(error){
    console.error('Part download failed',error);
    status('Could not download '+part.name+'. Please try again.');
    timer=setTimeout(()=>status(''),12000);
  }
}
