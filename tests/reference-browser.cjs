const output=require('path').resolve(process.env.REFERENCE_QA_OUTPUT||require('fs').mkdtempSync(require('path').join(require('os').tmpdir(),'hansgal-reference-')));require('fs').mkdirSync(output,{recursive:true});
/* Optional Playwright audit. No forms, email or payments are submitted. */
const {chromium}=require('playwright');
const fs=require('fs'),assert=require('node:assert/strict');
const base=process.env.SITE_BASE||'http://127.0.0.1:8770/hansgal-org';
const routes=['/news/68/','/news/78/','/news/76/','/publishers/25/','/publishers/63/','/bibliography/15/','/bibliography/21/','/bibliography/22/','/bibliography/23/','/booksandarticles/67/','/booksandarticles/62/','/faqs/80/','/hansgalsociety/32/','/hansgalsociety/33/','/hansgalsociety/34/','/hansgalsociety/35/','/donate/79/','/donate/81/','/contacts/24/','/photos/','/audiosamples/','/search/?keyword=piano','/score-basket/','/comments/'];
const snapshot=()=>{
 const s=document.querySelector('[data-reference-source]');if(!s)return null;const c=s.cloneNode(true);c.querySelectorAll('[data-ref-ui]').forEach(e=>e.remove());
 return {text:[...(c.textContent||'').replace(/\s/g,'')].sort().join(''),links:[...c.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')).sort(),images:[...c.querySelectorAll('img')].map(a=>a.getAttribute('src')).sort(),inputs:[...c.querySelectorAll('input,select,textarea')].map(a=>[a.tagName,a.id,a.getAttribute('name'),a.getAttribute('type')].join('|')).sort(),forms:[...c.querySelectorAll('form')].map(a=>[a.id,a.getAttribute('action'),a.getAttribute('onsubmit')].join('|')).sort()};
};
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'}),errors=[],issues=[],cases=[];let current='';
 for(const lang of ['en','de','fr','ja']){
  const pref=lang==='en'?'':'/'+lang;
  const raw=await browser.newPage({javaScriptEnabled:false});const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});page.on('pageerror',e=>errors.push({page:current,message:String(e)}));
  for(const route of routes){
   current=lang+route;const url=base+pref+route;await raw.goto(url);const before=await raw.evaluate(snapshot);
   await page.goto(url);await page.waitForFunction(()=>document.documentElement.dataset.referenceReady==='true',null,{timeout:10000}).catch(e=>issues.push(current+' readiness'));await page.waitForFunction(()=>document.documentElement.dataset.hansgalReady==='true',null,{timeout:15000}).catch(e=>{issues.push(current+' site data readiness');console.log('Readiness failure',current,errors);});
   const after=await page.evaluate(snapshot);if(before){for(const k of Object.keys(before)){try{assert.deepEqual(after[k],before[k]);}catch{issues.push(current+' source mismatch '+k);fs.writeFileSync(output+'/mismatch-'+lang+'-'+route.replaceAll('/','_')+'-'+k+'.json',JSON.stringify({before:before[k],after:after[k]},null,2));}}}
   for(const width of [1440,768,390,320]){
    await page.setViewportSize({width,height:1000});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);if(overflow)issues.push(current+' overflow '+width);
    if(width===1440||width===390){if(['/news/68/','/publishers/25/','/bibliography/15/','/faqs/80/','/donate/79/','/hansgalsociety/32/','/contacts/24/'].includes(route)&&['en','ja'].includes(lang))await page.screenshot({path:output+'/'+lang+'-'+route.replaceAll('/','_')+'-'+width+'.png',fullPage:false});}
    cases.push({lang,route,width});
   }
   await page.setViewportSize({width:1440,height:1000});
  }
  await raw.close();await page.close();console.log('Completed',lang);
 }
 fs.writeFileSync(output+'/browser-audit.json',JSON.stringify({cases,errors,issues},null,2));await browser.close();console.log(JSON.stringify({cases:cases.length,errors,issues},null,2));if(errors.length||issues.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
