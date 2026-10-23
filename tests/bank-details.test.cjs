const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
const sensitive=/\b\d{2}[- ]\d{2}[- ]\d{2}\b.*(?:Account|account)|\bGB\d{2}\s*LOYD\b|\bLOYD\s*GB\b/;
for(const dir of ['app','content','config','dist']){
 function walk(p){for(const e of fs.readdirSync(p,{withFileTypes:true})){const f=path.join(p,e.name);if(e.isDirectory())walk(f);else if(/\.(html?|js|json|txt|xml)$/i.test(e.name))assert(!sensitive.test(fs.readFileSync(f,'utf8')),f+' exposes banking details');}}
 walk(path.join(root,dir));
}
const menu=JSON.parse(fs.readFileSync(path.join(root,'content/menu.json'),'utf8'));
for(const id of ['32','34','79','81'])for(const field of ['body','body_de','body_fr','body_ja'])assert(menu.find(r=>r.id===id)[field].includes('data-bank-request'));
const script=fs.readFileSync(path.join(root,'app/bank-details.js'),'utf8');assert(!/localStorage|sessionStorage/.test(script));assert(script.includes('crypto.subtle.digest'));assert(script.includes('finally{button.disabled=false;}'));assert(script.includes("result.accepted!==true"));
for(const lang of ['','de/','fr/','ja/']){
 const html=fs.readFileSync(path.join(root,'dist',lang,'hansgalsociety/32/index.html'),'utf8');assert(html.includes('data-bank-request'));assert(html.includes('/app/bank-details.js'));assert(html.includes('/app/bank-details.css'));
}
console.log('PASS: bank details absent from public assets/data/pages; Society, donation, membership and fund forms in all four published languages; no browser persistence.');
