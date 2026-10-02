/* Progressive enhancements for the Living Edition. All reading links work without JS. */
(()=>{'use strict';
 document.documentElement.classList.add('js');
 const de=document.documentElement.lang==='de',t=(en,ger)=>de?ger:en;
 const toggle=document.querySelector('.menu-toggle'),nav=document.querySelector('.site-navigation'),search=document.querySelector('.masthead .searchbox');
 function menu(open){toggle?.setAttribute('aria-expanded',String(open));nav?.classList.toggle('is-open',open);search?.classList.toggle('is-open',open);}
 toggle?.addEventListener('click',()=>menu(toggle.getAttribute('aria-expanded')!=='true'));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.querySelectorAll('.explore-menu[open]').forEach(d=>d.open=false);if(toggle?.getAttribute('aria-expanded')==='true'){menu(false);toggle.focus();}}});
 const chapters=document.querySelector('.chapter-nav>details');
 if(chapters&&matchMedia('(max-width:850px)').matches)chapters.open=false;
 document.querySelectorAll('[data-language]').forEach(a=>{if(a.dataset.language===(de?'de':'en'))a.setAttribute('aria-current','page');});
 const q=new URLSearchParams(location.search).get('keyword')||'';
 document.querySelectorAll('input[name=keyword]').forEach(i=>i.value=q);
 document.getElementById('reset-catalogue')?.addEventListener('click',()=>{const f=document.getElementById('worksform');f.reset();f.requestSubmit();});
 document.getElementById('recording-view-toggle')?.addEventListener('click',()=>{const browser=document.querySelector('.recording-browser');window.Hansgal?.viewMode(browser?.classList.contains('flow-view')?'coverlist':'coverflow');});
 // Give authored content its proper heading hierarchy without rewriting the content fields.
 document.querySelectorAll('.article input[type=radio]').forEach(input=>{if(input.labels.length)return;let next=input.nextSibling;if(next?.nodeType===Node.TEXT_NODE){const label=document.createElement('label');input.before(label);label.append(input,next);}});
 const dialog=document.createElement('dialog');dialog.className='image-dialog';dialog.setAttribute('aria-label',t('Image viewer','Bildansicht'));
 const close=document.createElement('button');close.type='button';close.className='dialog-close';close.textContent=t('Close image ×','Bild schließen ×');
 const figure=document.createElement('figure'),image=document.createElement('img'),caption=document.createElement('figcaption');figure.append(image,caption);dialog.append(close,figure);document.body.append(dialog);
 let opener;
 close.addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>opener?.focus());dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
 document.addEventListener('click',e=>{const link=e.target.closest('a.imagesItem');if(!link||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||!dialog.showModal)return;e.preventDefault();opener=link;image.src=link.href;image.alt=link.title||link.querySelector('img')?.alt||'';caption.textContent=image.alt;dialog.showModal();close.focus();});
})();
