/* Integer-pence calculations shared by the basket and its tests. Prices come from the catalogue. */
(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.HansgalShopCore=api;})(typeof window==='object'?window:globalThis,function(){
 'use strict';
 function pence(value){if(!/^\d{1,4}(?:\.\d{1,2})?$/.test(String(value)))throw Error('Invalid amount');const [a,b='']=String(value).split('.');return Number(a)*100+Number(b.padEnd(2,'0'));}
 function quote(catalogue,items,donation,postage){
  if(!Array.isArray(items)||items.length>50)throw Error('Invalid basket');
  const seen=new Set();const lines=items.map(item=>{
   if(seen.has(item.id)||!Number.isInteger(item.quantity)||item.quantity<1||item.quantity>20)throw Error('Invalid quantity');seen.add(item.id);
   const r=catalogue.find(r=>r.id===item.id&&r.hgs_shop==='yes');if(!r)throw Error('CD no longer available');
   const unit=pence(r.hgs_price);if(!unit)throw Error('Invalid price');return {id:r.id,title:r.title,unit,quantity:item.quantity,total:unit*item.quantity};
  });
  const cds=lines.reduce((a,r)=>a+r.total,0),gift=pence(donation),shipping=lines.length?pence(postage):0;
  return {lines,cds,donation:gift,postage:shipping,total:cds+gift+shipping,currency:'GBP'};
 }
 function ukPostcode(value){const s=String(value).trim().toUpperCase().replace(/\s+/g,'');return !/^(GY|JE|IM)/.test(s)&&/^(GIR0AA|[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2})$/.test(s);}
 return {pence,quote,ukPostcode};
});
