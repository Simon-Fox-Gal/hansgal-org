(function(){
 const base=document.querySelector('meta[name="hansgal-base"]')?.content||'';
 const lang=document.documentElement.lang||'en';
 const prefix=code=>code==='en'?'':'/'+code;
 const route=location.pathname.slice(base.length).replace(/^\/(de|fr|ja)(?=\/|$)/,'')||'/';
 document.querySelectorAll('[data-language]').forEach(link=>{
  link.href=base+prefix(link.dataset.language)+route+location.search+location.hash;
  if(link.dataset.language===lang)link.setAttribute('aria-current','true');
  link.addEventListener('click',()=>{
   // Search and sort update the current URL without reloading the page.
   link.href=base+prefix(link.dataset.language)+route+location.search+location.hash;
   try{localStorage.setItem('hansgal-language',link.dataset.language);}catch{}
  });
 });
 // Explicit deep links retain their language; a remembered choice applies on entry.
 try{const remembered=localStorage.getItem('hansgal-language');if((location.pathname===base+'/'||location.pathname===base)&&remembered!=='en'&&Array.from(document.querySelectorAll('[data-language]')).some(a=>a.dataset.language===remembered))location.replace(base+prefix(remembered)+'/'+location.search+location.hash);}catch{}
})();
