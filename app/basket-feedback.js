/* Shared basket counts and a short musical celebration; never blocks adding. */
(function(){
 'use strict';
 const lang=document.documentElement.lang||'en',l=window.HansgalShopLabels[lang]||window.HansgalShopLabels.en;
 const base=document.querySelector('meta[name=hansgal-base]')?.content||'';
 const basketUrl=base+(lang==='en'?'':'/'+lang)+'/score-basket/';
 const read=key=>{try{const value=JSON.parse(localStorage.getItem(key)||'[]');return Array.isArray(value)?value:[];}catch{return [];}};
 let data=null,timer;
 const scoreSvg='<path class="icon-page" d="M6 2.5h10l6 6V25.5H6Z"/><path class="icon-line" d="M16 2.5v6h6M11.5 12.5v7.2a2.5 2.5 0 1 1-1.5-2.3m1.5-4.9 5-1.2v6.5a2.5 2.5 0 1 1-1.5-2.3"/>';
 const cdSvg='<circle class="icon-disc" cx="14" cy="14" r="10.5"/><circle class="icon-line" cx="14" cy="14" r="3.2"/><circle class="icon-hole" cx="14" cy="14" r="1"/><path class="icon-shine" d="M6.3 7.8a10 10 0 0 1 4-3l2.1 6.2a3.4 3.4 0 0 0-1.5 1.2Zm15.4 12.4a10 10 0 0 1-4 3L15.6 17a3.4 3.4 0 0 0 1.5-1.2Z"/>';
 function update(){
  if(!data)return;
  const selected=new Set(read('hansgal-scores'));
  const pdfs=new Set(data.catalogue.filter(r=>selected.has(r.id)&&r.score_available==='yes').flatMap(r=>String(r.score_file||'').split(/\r?\n/).map(s=>s.trim()).filter(s=>/^\/storage\/scores\/[^/]+\.pdf$/.test(s)))).size;
  const ids=new Set();const cds=read('hansgal-cds').reduce((n,r)=>{if(ids.has(r.id)||!Number.isInteger(r.quantity)||r.quantity<1||r.quantity>20||!data.recording.some(p=>p.id===r.id&&p.hgs_shop==='yes'&&Number(p.hgs_price)>0))return n;ids.add(r.id);return n+r.quantity;},0);
  document.querySelectorAll('.basket-link').forEach(link=>{
   let counts=link.querySelector('.basket-counts');if(!counts){counts=document.createElement('span');counts.className='basket-counts';link.append(counts);}
   counts.replaceChildren();
   for(const [kind,count,label,svg] of [['score',pdfs,l.pdf_count,scoreSvg],['cd',cds,l.cd_count,cdSvg]]){
    const badge=document.createElement('span');badge.className='basket-count basket-count-'+kind;badge.title=label+': '+count;badge.setAttribute('aria-label',badge.title);
    badge.innerHTML='<svg viewBox="0 0 28 28" aria-hidden="true">'+svg+'</svg><b aria-hidden="true">'+count+'</b>';counts.append(badge);
   }
  });
 }
 function added(button){
  update();
  const region=button.closest('.hgs-shop-offer')?.querySelector('.hgs-shop-status')||document.getElementById('score-added-status');
  if(region){region.replaceChildren(document.createTextNode(l.added+' '));const link=document.createElement('a');link.href=basketUrl;link.textContent=l.view_basket+' →';region.append(link);}
  // A fixed toast stays visible even if the player is scrolled or changes tracks.
  let toast=document.getElementById('basket-added-toast');if(!toast){toast=document.createElement('div');toast.id='basket-added-toast';toast.setAttribute('role','status');document.body.append(toast);}
  toast.replaceChildren(document.createTextNode('✓ '+l.added+' '));const link=document.createElement('a');link.href=basketUrl;link.textContent=l.view_basket+' →';toast.append(link);toast.hidden=false;clearTimeout(timer);timer=setTimeout(()=>{toast.hidden=true;},6500);
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
  const rect=button.getBoundingClientRect(),burst=document.createElement('div');burst.className='basket-note-burst';burst.setAttribute('aria-hidden','true');burst.style.left=(rect.left+rect.width/2)+'px';burst.style.top=(rect.top+rect.height/2)+'px';document.body.append(burst);
  const colours=['#a72970','#326f63','#b67814','#7050a5','#c7473e','#22748a'];
  for(let i=0;i<20;i++){const note=document.createElement('span'),angle=i*Math.PI*2/20,radius=65+(i%3)*19;note.textContent=['♪','♫','♬'][i%3];note.style.color=colours[i%colours.length];note.style.setProperty('--x',Math.cos(angle)*radius+'px');note.style.setProperty('--y',Math.sin(angle)*radius+'px');note.style.setProperty('--turn',(i%2?24:-24)+'deg');burst.append(note);}
  setTimeout(()=>burst.remove(),1100);
 }
 window.HansgalBasketFeedback={update,added};
 document.addEventListener('hansgal-basket-changed',update);
 document.addEventListener('hansgal-scores-rendered',update);
 window.addEventListener('storage',update);
 fetch(base+'/app/site-data'+(lang==='en'?'':'-'+lang)+'.json').then(r=>r.json()).then(d=>{data=d;update();}).catch(()=>{});
})();
