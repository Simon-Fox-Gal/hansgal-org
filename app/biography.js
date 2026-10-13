/* Native links and disclosures remain usable without JavaScript. */
(()=>{'use strict';
 const contents=document.querySelector('.bio-contents'),gallery=document.querySelector('.bio-gallery details');
 if(gallery&&matchMedia('(max-width:700px)').matches)gallery.open=false;
 contents?.addEventListener('toggle',()=>{if(contents.open)contents.querySelector('[aria-current]')?.scrollIntoView({block:'nearest'});});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&contents?.open){contents.open=false;contents.querySelector('summary').focus();}});
 document.addEventListener('click',e=>{if(contents?.open&&!contents.contains(e.target))contents.open=false;});
 function revealNote(){const id=decodeURIComponent(location.hash.slice(1));if(!id.startsWith('note-'))return;const note=document.getElementById(id);if(note?.tagName==='DETAILS'){note.open=true;note.scrollIntoView({block:'start'});}}
 addEventListener('hashchange',revealNote);revealNote();
 const prose=document.getElementById('chapter-text'),bar=document.querySelector('.bio-progress span');let scheduled=false;
 function progress(){scheduled=false;if(!prose||!bar)return;const rect=prose.getBoundingClientRect();bar.style.width=(Math.max(0,Math.min(1,(innerHeight-rect.top)/rect.height))*100)+'%';}
 addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(progress);}},{passive:true});addEventListener('resize',progress);progress();
})();
