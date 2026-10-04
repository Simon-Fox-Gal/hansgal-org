(async function(){
 const panel=document.querySelector('[data-contact-panel]');if(!panel)return;
 const form=panel.querySelector('[data-contact-form]'),status=form.querySelector('[data-contact-status]'),submit=form.querySelector('button[type="submit"]');
 const started=Date.now();let endpoint='',busy=false,key='';
 panel.querySelectorAll('[data-contact-person]').forEach(link=>link.addEventListener('click',()=>{form.elements.recipient.value=link.dataset.contactPerson;form.elements.name.focus({preventScroll:true});}));
 form.addEventListener('input',()=>{key='';});
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(busy||!form.reportValidity())return;
  if(!endpoint){status.textContent=form.dataset.unavailable;return;}
  busy=true;submit.disabled=true;status.textContent=form.dataset.sending;
  key=key||crypto.randomUUID();
  const body=Object.fromEntries(new FormData(form));
  Object.assign(body,{language:document.documentElement.lang,id:key,elapsedMs:Date.now()-started});
  try{
   const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),credentials:'omit',signal:AbortSignal.timeout(20000)});
   const result=await response.json();if(!response.ok||result.accepted!==true)throw new Error('Not accepted');
   status.textContent=form.dataset.success;form.reset();key='';
  }catch{status.textContent=form.dataset.error;}
  finally{busy=false;submit.disabled=false;}
 });
 try{
  const base=document.querySelector('meta[name="hansgal-base"]')?.content||'';
  const response=await fetch(base+'/app/contact-config.json');if(!response.ok)return;
  const config=await response.json();if(config.endpoint&&new URL(config.endpoint).protocol==='https:'){endpoint=config.endpoint;submit.disabled=false;status.textContent='';}
 }catch{}
})();
