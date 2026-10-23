/* No banking instructions or email addresses are stored in browser storage. */
(function(){
 'use strict';
 const base=document.querySelector('meta[name="hansgal-base"]')?.content||'',language=document.documentElement.lang||'en';
 const copies={"en": ["Request bank transfer details by email", "Your email address", "Email me the bank details", "We use your email address only to send these instructions. We do not add you to a mailing list. Resend processes the email; Cloudflare hosts this service. Keyed hashes used to prevent spam expire within 24 hours. Email delivery records follow the provider’s retention policy.", "Checking…", "Your request was accepted for email delivery. Please check your inbox and spam folder.", "We could not confirm email delivery. Please try again or contact the Society.", "Too many requests. Please wait before trying again; check your inbox for an earlier email.", "Leave this empty", "Bank details are sent by email.", "Contact the Society"], "de": ["Bankverbindung per E-Mail anfordern", "Ihre E-Mail-Adresse", "Bankverbindung zusenden", "Wir verwenden Ihre E-Mail-Adresse nur für diese Anleitung und nehmen Sie in keine Mailingliste auf. Resend verarbeitet die E-Mail; Cloudflare betreibt diesen Dienst. Schlüsselbasierte Hashwerte zur Spamabwehr verfallen innerhalb von 24 Stunden. Für E-Mail-Zustellprotokolle gelten die Aufbewahrungsregeln des Anbieters.", "Wird geprüft…", "Ihre Anfrage wurde zur E-Mail-Zustellung angenommen. Bitte prüfen Sie auch Ihren Spamordner.", "Die E-Mail-Zustellung konnte nicht bestätigt werden. Bitte versuchen Sie es erneut oder kontaktieren Sie die Gesellschaft.", "Zu viele Anfragen. Bitte warten Sie und prüfen Sie, ob bereits eine E-Mail eingegangen ist.", "Dieses Feld leer lassen", "Die Bankverbindung wird per E-Mail zugesandt.", "Kontakt zur Gesellschaft"], "fr": ["Recevoir les coordonnées bancaires par e-mail", "Votre adresse e-mail", "Envoyer les coordonnées bancaires", "Votre adresse sert uniquement à envoyer ces instructions. Aucune inscription à une liste de diffusion. Resend traite l’e-mail ; Cloudflare héberge ce service. Les empreintes protégées utilisées contre le spam expirent sous 24 heures. Les journaux d’envoi suivent la politique de conservation du prestataire.", "Vérification…", "Votre demande a été acceptée pour envoi par e-mail. Vérifiez votre boîte de réception et les courriers indésirables.", "L’envoi n’a pas pu être confirmé. Réessayez ou contactez la Société.", "Trop de demandes. Veuillez patienter et vérifier si un e-mail est déjà arrivé.", "Laissez ce champ vide", "Les coordonnées bancaires sont envoyées par e-mail.", "Contacter la Société"], "ja": ["銀行振込の案内をメールで受け取る", "メールアドレス", "振込先をメールで受け取る", "メールアドレスはこの案内の送信にのみ使用し、メーリングリストには登録しません。メールはResendが処理し、サービスはCloudflareが提供します。迷惑送信防止用の鍵付きハッシュは24時間以内に失効します。送信記録にはメール事業者の保存方針が適用されます。", "確認中…", "メール送信の受付が完了しました。受信トレイと迷惑メールフォルダーをご確認ください。", "メール送信を確認できませんでした。再試行するか、協会にお問い合わせください。", "リクエストが多すぎます。しばらく待ち、すでにメールが届いていないかご確認ください。", "この欄は空欄のままにしてください", "振込先はメールでお送りします。", "協会へのお問い合わせ"]};
 const l=copies[language]||copies.en,lang=copies[language]?language:'en';
 const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let count=0,configuration;
 const config=()=>configuration||(configuration=fetch(base+'/app/bank-details-config.json',{cache:'no-store',signal:AbortSignal.timeout(20000)}).then(r=>{if(!r.ok)throw Error();return r.json();}).catch(e=>{configuration=null;throw e;}));
 const contact=base+(lang==='en'?'':'/'+lang)+'/contacts/';
 async function solve(token){
  const encoder=new TextEncoder(),until=Date.now()+60000;
  for(let proof=0;proof<10000000;proof++){
   const bytes=new Uint8Array(await crypto.subtle.digest('SHA-256',encoder.encode(token+':'+proof)));
   if(bytes[0]===0&&bytes[1]===0)return proof;
   if(Date.now()>until)throw Error();
  }
  throw Error();
 }
 function mount(){document.querySelectorAll('[data-bank-request]').forEach(slot=>{
  if(slot.querySelector('form'))return;
  const id='bank-email-'+(++count);slot.classList.add('bank-request');
  slot.innerHTML='<h4>'+esc(l[0])+'</h4><form><label for="'+id+'">'+esc(l[1])+'</label><div class="bank-request-fields"><input id="'+id+'" name="email" type="email" autocomplete="email" maxlength="254" required><button type="submit">'+esc(l[2])+'</button></div><label class="bank-honeypot" aria-hidden="true">'+esc(l[8])+'<input name="website" tabindex="-1" autocomplete="off"></label><p class="bank-privacy">'+esc(l[3])+' <a href="https://resend.com/legal/privacy-policy" target="_blank" rel="noopener">Resend</a> · <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">Cloudflare</a></p><p class="bank-status" role="status" aria-live="polite"></p></form><p><a href="'+esc(contact)+'">'+esc(l[10])+'</a></p>';
  const form=slot.querySelector('form'),button=form.querySelector('button'),status=form.querySelector('[role=status]');let pending=null;
  form.onsubmit=async event=>{
   event.preventDefault();if(button.disabled||!form.reportValidity())return;
   button.disabled=true;status.textContent=l[4];
   const email=form.elements.email.value.trim(),fund=slot.dataset.bankFund||'general';
   try{
    const {endpoint}=await config();if(!endpoint)throw Error();
    if(!pending||pending.email!==email||Date.now()-pending.created>540000){
     const challenge=await fetch(endpoint,{cache:'no-store',signal:AbortSignal.timeout(20000)});if(challenge.status===429)throw Error('rate');if(!challenge.ok)throw Error();
     const c=await challenge.json();if(c.difficulty!==16||typeof c.token!=='string')throw Error();
     pending={email,language:lang,fund,token:c.token,proof:await solve(c.token),website:form.elements.website.value,created:Date.now()};
    }
    const {created,...body}=pending;
    const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(20000)});
    if(response.status===429)throw Error('rate');const result=await response.json();if(!response.ok||result.accepted!==true)throw Error();
    status.textContent=l[5];form.reset();pending=null;
   }catch(e){status.textContent=e.message==='rate'?l[7]:l[6];}finally{button.disabled=false;}
  };
 });}
 window.HansgalBankDetails={mount};document.addEventListener('hansgal-scores-rendered',mount);mount();
})();
