// Reuse the exact ready-to-print STL in the bundle instead of hosting a second
// copy. ZIP central-directory sizes support archives with data descriptors.
const archives=new Map();
export async function readZipEntry(url,filename){
 const key=new URL(url,location.href).href;
 if(!archives.has(key))archives.set(key,fetch(key).then(async r=>{if(!r.ok)throw Error('Bundle download returned '+r.status);return r.arrayBuffer()}).catch(e=>{archives.delete(key);throw e}));
 const buffer=await archives.get(key),view=new DataView(buffer),bytes=new Uint8Array(buffer),decoder=new TextDecoder();
 let end=buffer.byteLength-22;
 while(end>=Math.max(0,buffer.byteLength-65557)&&view.getUint32(end,true)!==0x06054b50)end--;
 if(end<Math.max(0,buffer.byteLength-65557))throw Error('Invalid ZIP directory');
 const count=view.getUint16(end+10,true);let pos=view.getUint32(end+16,true);
 for(let i=0;i<count;i++){
  if(view.getUint32(pos,true)!==0x02014b50)throw Error('Invalid ZIP entry');
  const method=view.getUint16(pos+10,true),crc=view.getUint32(pos+16,true),size=view.getUint32(pos+20,true),rawSize=view.getUint32(pos+24,true),nameLength=view.getUint16(pos+28,true),extraLength=view.getUint16(pos+30,true),commentLength=view.getUint16(pos+32,true),offset=view.getUint32(pos+42,true),name=decoder.decode(bytes.subarray(pos+46,pos+46+nameLength));
  if(name===filename){
   if(view.getUint32(offset,true)!==0x04034b50)throw Error('Invalid ZIP file header');
   const start=offset+30+view.getUint16(offset+26,true)+view.getUint16(offset+28,true),compressed=buffer.slice(start,start+size);
   const result=method===0?compressed:method===8?await new Response(new Blob([compressed]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer():null;
   if(!result||result.byteLength!==rawSize)throw Error('Unsupported or incomplete ZIP entry');
   let checksum=0xffffffff;for(const b of new Uint8Array(result)){checksum^=b;for(let k=0;k<8;k++)checksum=(checksum>>>1)^((checksum&1)?0xedb88320:0)}
   if(((checksum^0xffffffff)>>>0)!==crc)throw Error('STL checksum mismatch');
   return result;
  }
  pos+=46+nameLength+extraLength+commentLength;
 }
 throw Error('Part missing from bundle: '+filename);
}
