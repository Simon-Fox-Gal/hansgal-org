const vm=require('vm'),fs=require('fs'),assert=require('assert/strict');
const script=fs.readFileSync('app/bank-details.js','utf8');
async function scenario(lang){
 let html='',handler,reset=0,requests=[],responses=[503,200],challenges=0;
 const button={disabled:false},status={textContent:''},email={value:'visitor@example.test'},website={value:''};
 const form={elements:{email,website},querySelector:s=>s==='button'?button:status,reportValidity:()=>true,reset(){reset++;email.value='';},set onsubmit(f){handler=f;}};
 const slot={dataset:{bankFund:'general'},classList:{add(){}},querySelector:()=>html?form:null,set innerHTML(s){html=s;}};
 const context={document:{documentElement:{lang},querySelector:()=>({content:'/base'}),querySelectorAll:()=>[slot],addEventListener(){}},window:{},TextEncoder,Uint8Array,Date,AbortSignal,crypto:{subtle:{digest:async()=>new Uint8Array(32).buffer}},fetch:async(url,o)=>{
  if(url==='/base/app/bank-details-config.json')return {ok:true,json:async()=>({endpoint:'https://service.test/api/bank-details'})};
  assert.equal(url,'https://service.test/api/bank-details');if(!o?.method){challenges++;return {ok:true,json:async()=>({token:'test',difficulty:16})};}
  requests.push(JSON.parse(o.body));const code=responses.shift()||200;return {ok:code===200,status:code,json:async()=>({accepted:code===200})};
 }};
 vm.runInNewContext(script,context);assert(html.includes('type="email"'));assert(html.includes('role="status"'));assert(html.includes('Resend'));assert(html.includes('Cloudflare'));
 await handler({preventDefault(){}});assert.equal(button.disabled,false);assert.equal(reset,0);assert.equal(email.value,'visitor@example.test');
 await handler({preventDefault(){}});assert.equal(reset,1);assert.equal(challenges,1,'Uncertain retry reuses challenge');assert.deepEqual(requests[0],requests[1]);assert.equal(requests[0].language,lang);assert.equal(button.disabled,false);
 const before=html;context.window.HansgalBankDetails.mount();assert.equal(html,before,'No duplicate form on remount');
}
(async()=>{for(const l of ['en','de','fr','ja'])await scenario(l);console.log('PASS: four-language form mounting, successful submission, uncertain retry reuse, no personal-data storage, failure preserves input, reset/re-enable and no duplicate mounts. No email sent.');})().catch(e=>{console.error(e);process.exitCode=1;});
