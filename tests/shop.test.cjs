const assert=require('node:assert/strict'),fs=require('node:fs');
const core=require('../app/shop-core.js'),records=require('../content/recording.json'),properties=require('../content/properties.json'),labels=require('../config/shop-labels.json');
const selected=records.filter(r=>r.hgs_shop==='yes');assert.equal(selected.length,1);assert.equal(selected[0].id,'57');assert.equal(selected[0].hgs_price,'14.00');
assert.equal(properties.find(p=>p.name==='hgs_shop_postage').value,'7.00');
const q=core.quote(records,[{id:'57',quantity:3}],'5.50','7.00');assert.equal(q.cds,4200);assert.equal(q.postage,700);assert.equal(q.total,5450);assert.equal(core.quote(records,[],'0','7').total,0);
for(const quantity of [0,21,1.5,-1])assert.throws(()=>core.quote(records,[{id:'57',quantity}],'0','7'));
assert.throws(()=>core.quote(records,[{id:'24',quantity:1}],'0','7'));
assert.throws(()=>core.quote(records,[{id:'57',quantity:1},{id:'57',quantity:1}],'0','7'));
for(const lang of ['en','de','fr','ja']){
 assert.deepEqual(Object.keys(labels[lang]).sort(),Object.keys(labels.en).sort());
 const prefix=lang==='en'?'':'/'+lang;
 const html=fs.readFileSync('dist'+prefix+'/recordings/57/index.html','utf8');assert(html.includes('data-add-cd="57"'));assert(html.includes('£14.00'));assert(html.includes(labels[lang].invitation));
 const unchecked=fs.readFileSync('dist'+prefix+'/recordings/24/index.html','utf8');assert(!unchecked.includes('data-add-cd="24"'));
 const data=JSON.parse(fs.readFileSync('dist/app/site-data'+(lang==='en'?'':'-'+lang)+'.json'));assert.equal(data.properties.find(p=>p.name==='hgs_shop_postage').value,'7.00');assert.equal(data.recording.find(r=>r.id==='57').hgs_price,'14.00');
}
const layout=fs.readFileSync('templates/default-layout.html','utf8');assert(layout.indexOf('shop-i18n.js')<layout.indexOf('shop.js'));
console.log('PASS: shop offers in all four languages, disabled recordings unchanged, shared price/postage, quantity validation and separate basket totals.');
