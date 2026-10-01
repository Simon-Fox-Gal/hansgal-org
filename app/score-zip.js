/* Portable ZIP writer: UTF-8 names, uncompressed bytes, CRC-32 integrity. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.HansgalScoreZip=factory();})(typeof window==='undefined'?globalThis:window,function(){
 function zip(files){
  const chunks=[],directory=[];let offset=0;
  const header=(size,values)=>{const b=new Uint8Array(size),v=new DataView(b.buffer);for(const [o,n,w] of values)w===2?v.setUint16(o,n,true):v.setUint32(o,n,true);return b;};
  for(const f of files){const name=new TextEncoder().encode(f.name);let crc=-1;for(const b of f.bytes){crc^=b;for(let i=0;i<8;i++)crc=(crc>>>1)^((crc&1)?0xedb88320:0);}crc=(crc^-1)>>>0;
   const h=header(30,[[0,0x04034b50,4],[4,20,2],[6,0x800,2],[14,crc,4],[18,f.bytes.length,4],[22,f.bytes.length,4],[26,name.length,2]]);
   const d=header(46,[[0,0x02014b50,4],[4,20,2],[6,20,2],[8,0x800,2],[16,crc,4],[20,f.bytes.length,4],[24,f.bytes.length,4],[28,name.length,2],[42,offset,4]]);
   chunks.push(h,name,f.bytes);directory.push(d,name);offset+=h.length+name.length+f.bytes.length;
  }
  const size=directory.reduce((n,b)=>n+b.length,0);return new Blob([...chunks,...directory,header(22,[[0,0x06054b50,4],[8,files.length,2],[10,files.length,2],[12,size,4],[16,offset,4]])],{type:'application/zip'});
 }
 return zip;
});
