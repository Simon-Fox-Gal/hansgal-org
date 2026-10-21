// Exercise the real basket render and submit handler without contacting PayPal.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../app/scores.js'),'utf8');
const decode=s=>s.replace(/&(#x[\da-f]+|#\d+|amp|lt|gt|quot|apos|nbsp);/gi,(_,c)=>c[0]==='#'?String.fromCodePoint(c[1].toLowerCase()==='x'?parseInt(c.slice(2),16):Number(c.slice(1))):({amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' '})[c.toLowerCase()]);
const row=(id,title,opus_no='',extra={})=>({id,title,opus_no,score_available:'yes',score_file:'/storage/scores/test.pdf',score_suggested_donation:'10',...extra});
async function basket(rows,chosen=rows.map(r=>r.id),lang='en',remembered=null){
 const elements={},local=new Map([['hansgal-scores',JSON.stringify(chosen)]]),session=new Map();
 if(remembered)session.set('hansgal-donation',JSON.stringify(remembered));
 const storage=map=>({getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v)});
 const target={querySelectorAll:()=>[],set innerHTML(html){
  this.html=html;for(const key of Object.keys(elements))delete elements[key];
  if(html.includes('id="score-donation"'))elements['score-donation']={};
  for(const input of html.matchAll(/<input\b([^>]+)>/g)){
   const attrs=Object.fromEntries([...input[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(m=>[m[1],decode(m[2])]));
   if(attrs.id)elements[attrs.id]={...attrs,checkValidity(){return /^\d+(?:\.\d{1,2})?$/.test(this.value);}};
  }
  if(html.includes('id="download-selection"'))elements['download-selection']={};
  elements['score-download-status']={textContent:''};
 }};
 const requests=[];
 const ctx={console,CustomEvent:function(){},localStorage:storage(local),sessionStorage:storage(session),
  window:{HansgalShopLabels:{en:{},de:{},fr:{},ja:{}}},
  document:{documentElement:{lang},querySelector:()=>null,getElementById:id=>id==='score-basket'?target:elements[id],querySelectorAll:()=>[],dispatchEvent(){},
   createElement(tag){assert.equal(tag,'template');return {set innerHTML(html){this.content={textContent:decode(html.replace(/<[^>]*>/g,''))};}};}},
  fetch:async url=>{requests.push(url);return {json:async()=>({catalogue:rows,properties:[]})};}
 };
 vm.runInNewContext(source,ctx);await new Promise(resolve=>setImmediate(resolve));
 const fields=()=>Object.fromEntries([...target.html.matchAll(/<input\b([^>]+)>/g)].map(m=>Object.fromEntries([...m[1].matchAll(/([\w-]+)="([^"]*)"/g)].map(a=>[a[1],decode(a[2])]))).filter(a=>a.name).map(a=>[a.name,a.id?elements[a.id].value:a.value]));
 const submit=()=>{let prevented=false;elements['score-donation'].onsubmit({preventDefault(){prevented=true;}});return prevented;};
 return {target,elements,fields,submit,session,requests};
}
(async()=>{
 const sonata=row('17','Sonata for Violin and Piano','17');
 let b=await basket([sonata]);let f=b.fields();
 assert.equal(f.item_name,'Hans Gál Society — General Fund — Scores: Sonata for Violin and Piano, Op. 17');
 assert.equal(f.custom,'Scores: Sonata for Violin and Piano, Op. 17');assert.equal(f.item_number,'Scores: Op. 17');
 assert.equal(f.cmd,'_donations');assert.equal(f.business,'donations@hansgalsociety.org');assert.equal(f.currency_code,'GBP');assert.equal(f.charset,'utf-8');assert.equal(f.amount,'10.00');
 assert(b.target.html.includes('https://www.paypal.com/cgi-bin/webscr'));assert(b.target.html.includes('download href='));assert(b.elements['download-selection']);assert.equal(b.submit(),false);
 b.elements['score-amount'].value='3.25';b.elements['score-amount'].oninput();assert.equal(b.fields().amount,'3.25');assert.equal(b.submit(),false);
 assert.equal(JSON.parse(b.session.get('hansgal-donation')).amount,'3.25');
 for(const value of ['0','-1','invalid']){b.elements['score-amount'].value=value;assert.equal(b.submit(),true);assert(b.elements['score-download-status'].textContent.includes('No donation is needed'));}
 b=await basket([sonata],['17'],'en',{basket:'17',amount:'2.75'});assert.equal(b.fields().amount,'2.75');
 b=await basket([sonata],['17'],'en',{basket:'other',amount:'2.75'});assert.equal(b.fields().amount,'10.00');
 b=await basket([row('1','Sonata','17'),row('2','Trio','49b')]);assert(b.fields().item_name.endsWith('Sonata, Op. 17; Trio, Op. 49b'));assert.equal(b.fields().amount,'20.00');
 const long=row('1','A very long work title '.repeat(40),'90(3)');
 b=await basket([long]);assert(b.fields().item_name.includes('…'));assert(b.fields().item_name.endsWith('Op. 90(3)'));assert(b.fields().custom.endsWith('Op. 90(3)'));
 b=await basket([row('149','A long title '.repeat(40))]);assert(b.fields().item_name.includes('[#149]'));
 b=await basket(Array.from({length:8},(_,i)=>row(String(i+1),'A long title '.repeat(10),String(i+1))));
 assert(b.fields().item_name.endsWith('Op. 1; Op. 2; Op. 3; Op. 4; Op. 5; Op. 6; Op. 7; Op. 8'));
 b=await basket([row('1','Fünf <i>Lieder</i> &amp; “夜” 🎵','5')]);assert(b.fields().item_name.includes('Fünf Lieder & “夜” 🎵, Op. 5'));assert(!b.fields().item_name.includes('<i>'));
 for(const lang of ['en','de','fr','ja']){
  b=await basket([row('1','Localized “夜” 🎵'.repeat(30),'17',{title_de:'Deutscher Titel'})],['1'],lang);
  assert(b.fields().item_name.endsWith('Op. 17'));if(lang==='de')assert(b.fields().item_name.includes('Deutscher Titel'));
  assert.equal(b.requests[0],'/app/site-data'+(lang==='en'?'':'-'+lang)+'.json');
 }
 const actual=require('../content/catalogue.json').filter(r=>r.score_available==='yes'&&r.score_file);
 for(const lang of ['en','de','fr','ja']){
  const data=JSON.parse(fs.readFileSync('dist/app/site-data'+(lang==='en'?'':'-'+lang)+'.json'));
  b=await basket(data.catalogue,actual.map(r=>r.id),lang);
  for(const r of actual)assert(b.fields().item_number.includes(r.opus_no?'Op. '+r.opus_no:'#'+r.id));
  assert(!b.fields().custom.includes('…'),'Current complete selection fits custom in '+lang);
 }
 for(let count=1;count<=100;count++){
  b=await basket(Array.from({length:count},(_,i)=>row(String(i+1),'夜🎵'.repeat(100),i%2?String(i+1):'')));
  for(const [key,limit] of [['item_name',127],['item_number',127],['custom',255]]){
   assert(Array.from(b.fields()[key]).length<=limit,key+' exceeds limit');assert(!/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/.test(b.fields()[key]));
  }
 }
 for(const chosen of [[],['unknown']]){b=await basket([sonata],chosen);assert(!b.elements['score-donation']);assert.equal(b.fields().item_name,undefined);}
 b=await basket([sonata],['17','17']);assert.equal(b.fields().amount,'10.00');
 console.log('PASS: score donation POST descriptions, opus/numeric fallbacks, full current selections, Unicode/HTML, limits, four languages, edited/remembered amounts and empty baskets. No payments sent.');
})().catch(error=>{console.error(error);process.exitCode=1;});
