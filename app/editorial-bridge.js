/* Private editorial context bridge. Inert outside the authorized CMS frame. */
(function(){
 'use strict';
 if(window.parent===window)return;
 const allowed=new Set(['https://hans-gal-editorial.simonfoxgal.chatgpt.site','http://127.0.0.1:5173']);
 let peer=null,pick=false,last='';
 const base=document.querySelector('meta[name="hansgal-base"]')?.content||'';
 function context(element){
  const path=location.pathname.slice(base.length)||'/';
  let reference=path+location.search+location.hash,url=location.href;
  const album=document.getElementById('webshop')?.dataset.recordingId;
  if(album){reference='recording:'+album;url=location.origin+base+'/recordings/'+album+'/';}
  else if(/^\/works\/show\/\d+/.test(path))reference='catalogue:'+path.split('/')[3];
  else if(/^\/[a-z]+\/\d+\/?$/.test(path))reference='menu:'+path.split('/')[2];
  const text=element?element.innerText||element.textContent||'':getSelection()?.toString()||'';
  let selector='';
  if(element){const parts=[];for(let node=element;node&&node.nodeType===1&&parts.length<6;node=node.parentElement){if(node.id){parts.unshift('#'+CSS.escape(node.id));break;}const siblings=node.parentElement?[...node.parentElement.children].filter(e=>e.tagName===node.tagName):[];parts.unshift(node.tagName.toLowerCase()+(siblings.length>1?':nth-of-type('+(siblings.indexOf(node)+1)+')':''));}selector=parts.join(' > ');}
  return {url,title:album?(document.getElementById('webshop')?.dataset.recordingTitle||document.title):document.title,reference,selectedText:text.slice(0,8000),selector};
 }
 function send(element,picked=false){if(!peer)return;const c=context(element),s=JSON.stringify(c);if(picked||s!==last){last=s;parent.postMessage({type:'hansgal:context',context:c,picked},peer);}}
 addEventListener('message',e=>{
  if(e.source!==parent||!allowed.has(e.origin))return;
  if(e.data?.type==='hansgal:hello'){peer=e.origin;last='';send();}
  if(e.data?.type==='hansgal:pick'&&peer===e.origin){pick=true;document.documentElement.style.cursor='crosshair';}
 });
 document.addEventListener('click',e=>{if(!pick)return;e.preventDefault();e.stopImmediatePropagation();pick=false;document.documentElement.style.cursor='';send(e.target.closest('p,h1,h2,h3,li,td,img,a,div')||e.target,true);},true);
 addEventListener('keydown',e=>{if(e.key==='Escape'){pick=false;document.documentElement.style.cursor='';}});
 addEventListener('selectionchange',()=>send());
 addEventListener('popstate',()=>send());addEventListener('hashchange',()=>send());
 const observer=new MutationObserver(()=>send());observer.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['data-recording-id']});
 const replace=history.replaceState;history.replaceState=function(){const r=replace.apply(this,arguments);send();return r;};
})();
