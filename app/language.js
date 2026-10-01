(function(){
 const base=document.querySelector('meta[name="hansgal-base"]')?.content||'';
 const lang=document.documentElement.lang==='de'?'de':'en';
 const route=location.pathname.slice(base.length).replace(/^\/de(?=\/|$)/,'')||'/';
 document.querySelectorAll('[data-language]').forEach(link=>{
  link.href=base+(link.dataset.language==='de'?'/de':'')+route+location.search+location.hash;
  if(link.dataset.language===lang)link.setAttribute('aria-current','true');
  link.addEventListener('click',()=>{try{localStorage.setItem('hansgal-language',link.dataset.language);}catch{}});
 });
 // Explicit deep links retain their language; a remembered choice applies on entry.
 try{if((location.pathname===base+'/'||location.pathname===base)&&localStorage.getItem('hansgal-language')==='de')location.replace(base+'/de/'+location.search+location.hash);}catch{}
})();
