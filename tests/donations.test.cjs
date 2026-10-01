const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const row=JSON.parse(fs.readFileSync(require('path').join(__dirname,'../content/menu.json'),'utf8')).find(r=>r.id==='79');
for(const field of ['body','body_de']) {
 const html=row[field],script=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
 const el={};for(const id of ['donation_amount','paypal_amount_hidden','donation_fund','paypal_item_name','currency','paypal_currency_code','payment_method'])el['hgs_'+id]={value:''};
 el.hgs_currency.options=['GBP','EUR','USD','Other'].map(value=>({value}));
 const alerts=[];const ctx={document:{getElementById:id=>el[id],addEventListener(){}},alert:s=>alerts.push(s),console};vm.createContext(ctx);vm.runInContext(script,ctx);
 el.hgs_payment_method.value='Bank transfer';el.hgs_currency.value='EUR';ctx.hgsUpdatePaymentCurrencyOptions();assert.equal(el.hgs_currency.value,'GBP');assert(el.hgs_currency.options.slice(1).every(o=>o.disabled));
 el.hgs_donation_amount.value='3.25';el.hgs_donation_fund.value='Live Performance Fund';el.hgs_currency.value='GBP';assert.equal(ctx.hgsPreparePayPalDonation(),true);assert.equal(el.hgs_paypal_amount_hidden.value,'3.25');assert.equal(el.hgs_paypal_currency_code.value,'GBP');assert(el.hgs_paypal_item_name.value.endsWith('Live Performance Fund'));
 el.hgs_donation_amount.value='0';assert.equal(ctx.hgsPreparePayPalDonation(),false);assert.equal(alerts.length,1);
 assert(html.includes('name="business" value="donations@hansgalsociety.org"'));
 assert(html.includes('GB16 LOYD 3099 9902 5318 52'));
}
console.log('PASS: EN/DE donation logic retains recipient, bank account, chosen fund and exact amount; GBP-only payment methods and zero rejection preserved. No payment or email sent.');
