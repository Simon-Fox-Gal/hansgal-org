/* HGS CDs share the basket with freely downloadable scores. */
(function(){
 'use strict';
 const base=document.querySelector('meta[name=hansgal-base]')?.content||'',lang=document.documentElement.lang||'en';
 const l=window.HansgalShopLabels[lang]||window.HansgalShopLabels.en,core=window.HansgalShopCore;
 const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const plain=v=>{const d=document.createElement('div');d.innerHTML=v||'';return d.textContent;};
 const money=n=>'£'+(n/100).toFixed(2),basketUrl=base+(lang==='en'?'':'/'+lang)+'/score-basket/';
 let data=null,config=null,items=[],started=Date.now(),busy=false,receipt=null;
 try{const a=JSON.parse(localStorage.getItem('hansgal-cds')||'[]');if(Array.isArray(a))items=a.filter(x=>typeof x.id==='string'&&Number.isInteger(x.quantity)&&x.quantity>0&&x.quantity<=20);}catch{}
 const save=()=>{try{localStorage.setItem('hansgal-cds',JSON.stringify(items));}catch{}};
 const product=id=>data?.recording.find(r=>r.id===id&&r.hgs_shop==='yes'&&Number(r.hgs_price)>0);
 function offer(r){return '<aside class="hgs-shop-offer" aria-label="'+esc(l.shop)+'"><span class="hgs-shop-label">'+esc(l.shop)+'</span><p>'+esc(l.invitation)+'</p><div class="hgs-shop-actions"><strong>'+money(core.pence(r.hgs_price))+'</strong><button type="button" data-add-cd="'+esc(r.id)+'">'+esc(l.add)+'</button></div><small>'+esc(l.postage_extra)+'</small><span class="hgs-shop-status" role="status"></span></aside>';}
 function refreshPlayer(){const slot=document.getElementById('now-shop');if(!slot)return;const r=product(slot.dataset.recordingId);slot.hidden=!r;slot.innerHTML=r?offer(r):'';}
 window.HansgalShop={refreshPlayer};
 function scores(){let ids=[];try{ids=JSON.parse(localStorage.getItem('hansgal-scores')||'[]');}catch{}return data.catalogue.filter(r=>ids.includes(r.id)&&r.score_available==='yes'&&r.score_file);}
 function donation(){const selected=scores(),key=selected.map(r=>r.id).sort().join(',');let amount=selected.reduce((s,r)=>s+(Number(r.score_suggested_donation)||0),0).toFixed(2);try{const saved=JSON.parse(sessionStorage.getItem('hansgal-donation'));if(saved?.basket===key)amount=saved.amount;}catch{}return amount;}
 function totals(q){return '<dl class="shop-totals"><dt>'+esc(l.cd_total)+'</dt><dd>'+money(q.cds)+'</dd><dt>'+esc(l.postage)+'</dt><dd>'+money(q.postage)+'</dd><dt>'+esc(l.donation)+'</dt><dd>'+money(q.donation)+'</dd><dt class="grand">'+esc(l.total)+'</dt><dd class="grand">'+money(q.total)+'</dd></dl>';}
 function field(name,label,extra='',wide=false){return '<label'+(wide?' class="wide"':'')+'>'+esc(label)+'<input name="'+name+'" '+extra+'></label>';}
 function render(){
  const target=document.getElementById('score-basket');if(!target||!data||busy)return;
  showReceipt(target);
  target.querySelectorAll('.cd-basket,.shop-checkout').forEach(e=>e.remove());target.classList.toggle('shop-has-cds',items.length>0);if(!items.length)return;
  const postage=data.properties.find(r=>r.name==='hgs_shop_postage')?.value;
  let q;try{q=core.quote(data.recording,items,donation(),postage);}catch{target.insertAdjacentHTML('beforeend','<p role="alert">'+esc(l.unavailable)+'</p>');return;}
  const section=document.createElement('section');section.className='cd-basket';section.innerHTML='<h2>'+esc(l.cds)+'</h2><p>'+esc(l.uk_only)+'</p>'+q.lines.map(row=>{const r=product(row.id);return '<div class="cd-basket-row"><img src="'+esc(base+'/storage/recordingcovers/'+r.cover)+'" alt=""><div><h3>'+esc(plain(r.title))+'</h3><p>'+money(row.unit)+' '+esc(l.each)+'</p><label>'+esc(l.quantity)+' <input type="number" min="1" max="20" step="1" data-cd-quantity="'+row.id+'" value="'+row.quantity+'"></label><button type="button" data-remove-cd="'+row.id+'">'+esc(l.remove)+'</button></div><strong>'+money(row.total)+'</strong></div>';}).join('');
  target.querySelector('h1')?.insertAdjacentElement('afterend',section);
  const checkout=document.createElement('section');checkout.className='shop-checkout';checkout.innerHTML='<h2>'+esc(l.checkout)+'</h2><form id="hgs-checkout"><div class="shop-checkout-grid"><div><fieldset><legend>'+esc(l.delivery)+'</legend><div class="shop-fields">'+field('name',l.name,'required maxlength="120" autocomplete="name"',true)+field('email',l.email,'required type="email" maxlength="254" autocomplete="email"',true)+field('address1',l.address1,'required maxlength="160" autocomplete="address-line1"',true)+field('address2',l.address2,'maxlength="160" autocomplete="address-line2"',true)+field('city',l.city,'required maxlength="100" autocomplete="address-level2"')+field('postcode',l.postcode,'required maxlength="10" autocomplete="postal-code"')+'<label class="wide">'+esc(l.country)+'<input name="countryLabel" value="'+esc(l.uk)+'" readonly><input type="hidden" name="country" value="GB"></label></div></fieldset><fieldset class="shop-payment"><legend>'+esc(l.payment)+'</legend>'+[['paypal',l.card],['bank',l.bank],['cheque',l.cheque]].map(([v,label])=>'<label><input type="radio" name="method" value="'+v+'" '+(v==='paypal'?'checked':'')+'> '+esc(label)+'</label>').join('')+'<small>'+esc(l.card_note)+'</small></fieldset></div><div><label>'+esc(l.optional_donation)+' <input id="shop-donation" name="donation" type="number" min="0" max="9999.99" step="0.01" value="'+(q.donation/100).toFixed(2)+'" required></label><p>'+esc(l.donation_note)+'</p><div id="shop-totals">'+totals(q)+'</div><p>'+esc(l.postage_note)+'</p><small>'+esc(l.privacy)+'</small><p><button type="submit">'+esc(l.place_order)+'</button></p><p class="shop-feedback" role="status"></p></div></div><label class="shop-honeypot" aria-hidden="true" tabindex="-1">Website<input name="website" tabindex="-1" autocomplete="off"></label></form>';
  target.append(checkout);
  const form=checkout.querySelector('form'),gift=form.elements.donation;
  gift.oninput=()=>{if(!gift.checkValidity())return;try{q=core.quote(data.recording,items,gift.value,postage);checkout.querySelector('#shop-totals').innerHTML=totals(q);sessionStorage.setItem('hansgal-donation',JSON.stringify({basket:scores().map(r=>r.id).sort().join(','),amount:gift.value}));}catch{}};
  form.onsubmit=async event=>{
   event.preventDefault();if(busy||!form.reportValidity())return;const feedback=form.querySelector('.shop-feedback');
   if(!core.ukPostcode(form.elements.postcode.value)){feedback.textContent=l.invalid_postcode;form.elements.postcode.focus();return;}
   if(!config.endpoint){feedback.textContent=l.setup_pending;return;}
   const fields=Object.fromEntries(new FormData(form)),payload={items,scoreIds:scores().map(r=>r.id),donation:fields.donation,expectedTotal:q.total,language:lang,method:fields.method,customer:Object.fromEntries(['name','email','address1','address2','city','postcode','country'].map(k=>[k,fields[k]])),website:fields.website,elapsedMs:Date.now()-started};
   let saved;try{saved=JSON.parse(sessionStorage.getItem('hansgal-order-attempt'));}catch{}delete payload.elapsedMs;
   // Reuse the request ID after an uncertain response, without persisting personal details.
   const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(payload)))),b=>b.toString(16).padStart(2,'0')).join('');
   const id=saved?.digest===digest?saved.id:crypto.randomUUID();try{sessionStorage.setItem('hansgal-order-attempt',JSON.stringify({id,digest}));}catch{}
   busy=true;form.querySelector('button[type=submit]').disabled=true;feedback.textContent=l.submitting;
   try{
    const response=await fetch(config.endpoint+'/api/orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...payload,id,elapsedMs:Date.now()-started})});const result=await response.json();
    if(!response.ok)throw Error(response.status===409?l.changed:l.failed);
    feedback.textContent=l.received+' '+result.reference+'\n'+l.pending;
    if(result.payment?.url){const pay=document.createElement('form');pay.action=result.payment.url;pay.method='post';for(const [name,value] of Object.entries(result.payment.fields)){const input=document.createElement('input');input.type='hidden';input.name=name;input.value=value;pay.append(input);}document.body.append(pay);pay.submit();}
    else{receipt={reference:result.reference,message:result.status==='paid'?l.paid:l.pending,quote:q,instructions:result.instructions};items=[];save();try{sessionStorage.setItem('hansgal-order-receipt',JSON.stringify(receipt));}catch{}busy=false;render();}
   }catch(e){feedback.textContent=e.message||l.failed;}finally{busy=false;const button=form.querySelector('button[type=submit]');if(button)button.disabled=false;}
  };
 }
 function showReceipt(target){
  target.querySelector('.shop-receipt')?.remove();if(!receipt)return;
  const box=document.createElement('section');box.className='shop-receipt shop-confirmation';
  box.innerHTML='<h2>'+esc(l.received)+' '+esc(receipt.reference||'')+'</h2><p>'+esc(receipt.message)+'</p>'+(receipt.quote?totals(receipt.quote):'')+(receipt.instructions?'<p>'+esc(receipt.instructions)+'</p>':'')+'<button type="button" class="shop-print">'+esc(l.print)+'</button>';
  box.querySelector('button').onclick=()=>window.print();target.prepend(box);
 }
 async function returned(){
  const query=new URLSearchParams(location.search),id=query.get('order');
  if(id&&/^[a-f0-9-]{36}$/.test(id)&&config.endpoint){
   try{const response=await fetch(config.endpoint+'/api/orders?id='+encodeURIComponent(id));if(!response.ok)throw Error();const r=await response.json();
    receipt={reference:r.reference,quote:r.quote,message:r.status==='paid'?l.paid:l.receipt_pending};
    // Clear only the quantities in this completed checkout, preserving later additions.
    if(sessionStorage.getItem('hansgal-return-cleared')!==id){items=items.map(x=>({...x,quantity:Math.max(0,x.quantity-(r.quote.lines.find(v=>v.id===x.id)?.quantity||0))})).filter(x=>x.quantity);save();sessionStorage.setItem('hansgal-return-cleared',id);}
    sessionStorage.setItem('hansgal-order-receipt',JSON.stringify(receipt));
   }catch{receipt={message:l.receipt_unavailable};}
  }else if(query.get('payment')==='cancelled')receipt={message:l.cancelled};
  else{try{receipt=JSON.parse(sessionStorage.getItem('hansgal-order-receipt'));}catch{}}
  render();
 }
 document.addEventListener('click',event=>{const add=event.target.closest('[data-add-cd]'),remove=event.target.closest('[data-remove-cd]');if(add){const r=product(add.dataset.addCd);if(!r)return;const existing=items.find(x=>x.id===r.id);if(existing)existing.quantity=Math.min(20,existing.quantity+1);else items.push({id:r.id,quantity:1});save();const status=add.closest('.hgs-shop-offer').querySelector('.hgs-shop-status');status.innerHTML=esc(l.added)+' <a href="'+esc(basketUrl)+'">'+esc(l.view_basket)+' →</a>';render();}if(remove&&!busy){items=items.filter(x=>x.id!==remove.dataset.removeCd);save();render();}});
 document.addEventListener('change',event=>{if(!event.target.matches('[data-cd-quantity]')||busy)return;const value=Number(event.target.value);if(!Number.isInteger(value)||value<1||value>20){event.target.reportValidity();return;}const item=items.find(x=>x.id===event.target.dataset.cdQuantity);if(item)item.quantity=value;save();render();});
 document.addEventListener('hansgal-scores-rendered',render);
 Promise.all([fetch(base+'/app/site-data'+(lang==='en'?'':'-'+lang)+'.json').then(r=>r.json()),fetch(base+'/app/shop-config.json').then(r=>r.json())]).then(([d,c])=>{data=d;config=c;const seen=new Set();items=items.filter(x=>product(x.id)&&!seen.has(x.id)&&seen.add(x.id));save();refreshPlayer();render();returned();}).catch(()=>{});
})();
