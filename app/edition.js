/* Progressive enhancements for the Living Edition. All reading links work without JS. */
(()=>{'use strict';
 document.documentElement.classList.add('js');
 const language=document.documentElement.lang||'en',de=language==='de',t=(en,ger)=>window.HansgalLocale?.labels?.[en]??(de?ger:en);
 const toggle=document.querySelector('.menu-toggle'),nav=document.querySelector('.site-navigation'),search=document.querySelector('.masthead .searchbox');
 function menu(open){toggle?.setAttribute('aria-expanded',String(open));nav?.classList.toggle('is-open',open);search?.classList.toggle('is-open',open);}
 toggle?.addEventListener('click',()=>menu(toggle.getAttribute('aria-expanded')!=='true'));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.querySelectorAll('.explore-menu[open]').forEach(d=>d.open=false);if(toggle?.getAttribute('aria-expanded')==='true'){menu(false);toggle.focus();}}});
 const chapters=document.querySelector('.chapter-nav>details');
 if(chapters&&matchMedia('(max-width:850px)').matches)chapters.open=false;
 const advanced=document.querySelector('.advanced-filters');if(advanced&&matchMedia('(max-width:600px)').matches&&!new URLSearchParams(location.search).size)advanced.open=false;
 const recordSearch=document.getElementById('recording-search');recordSearch?.addEventListener('input',()=>{const q=recordSearch.value.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();let count=0;document.querySelectorAll('.albumlist .item').forEach(a=>{a.hidden=!a.textContent.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(q);if(!a.hidden)count++;});document.getElementById('recording-count').textContent=count+' '+t('recordings','Aufnahmen');});
 document.querySelectorAll('[data-language]').forEach(a=>{if(a.dataset.language===language)a.setAttribute('aria-current','page');});
 const q=new URLSearchParams(location.search).get('keyword')||'';
 document.querySelectorAll('input[name=keyword]').forEach(i=>i.value=q);
 document.getElementById('reset-catalogue')?.addEventListener('click',()=>{const f=document.getElementById('worksform');f.reset();f.requestSubmit();});
 document.getElementById('recording-view-toggle')?.addEventListener('click',()=>{const browser=document.querySelector('.recording-browser');window.Hansgal?.viewMode(browser?.classList.contains('flow-view')?'coverlist':'coverflow');});
 // Give authored content its proper heading hierarchy without rewriting the content fields.
 document.querySelectorAll('.article input[type=radio]').forEach(input=>{if(input.labels.length)return;let next=input.nextSibling;if(next?.nodeType===Node.TEXT_NODE){const label=document.createElement('label');input.before(label);label.append(input,next);}});
 const dialog=document.createElement('dialog');dialog.className='image-dialog';dialog.setAttribute('aria-label',t('Image viewer','Bildansicht'));
 const close=document.createElement('button');close.type='button';close.className='dialog-close';close.textContent=t('Close image ×','Bild schließen ×');
 const figure=document.createElement('figure'),image=document.createElement('img'),caption=document.createElement('figcaption');figure.append(image,caption);dialog.append(close,figure);document.body.append(dialog);
 const previous=document.createElement('button'),next=document.createElement('button'),controls=document.createElement('div');controls.className='image-controls';previous.type=next.type='button';previous.textContent=t('← Previous','← Zurück');next.textContent=t('Next →','Weiter →');controls.append(previous,next);dialog.append(controls);caption.setAttribute('aria-live','polite');
 let opener,group=[],index=0;
 function showImage(link){image.src=link.href;image.alt=link.title||link.querySelector('img')?.alt||'';caption.textContent=image.alt;}
 function step(offset){index=(index+offset+group.length)%group.length;showImage(group[index]);}
 previous.addEventListener('click',()=>step(-1));next.addEventListener('click',()=>step(1));dialog.addEventListener('keydown',e=>{if(group.length>1&&['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();step(e.key==='ArrowLeft'?-1:1);}});
 close.addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>opener?.focus());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
 document.addEventListener('click',e=>{const link=e.target.closest('a.imagesItem');if(!link||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||!dialog.showModal)return;e.preventDefault();opener=link;group=link.rel?[...document.querySelectorAll('a.imagesItem')].filter(a=>a.rel===link.rel):[link];index=group.indexOf(link);controls.hidden=group.length<2;showImage(link);dialog.showModal();close.focus();});
})();
