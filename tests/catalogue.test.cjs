const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const json=(folder,name)=>JSON.parse(fs.readFileSync(path.join(root,folder,name+'.json'),'utf8'));
const engine=require('../app/catalogue.js');
const data={catalogue:json('content','catalogue'),catalogue_category:json('content','catalogue_category')};
const accent=json('content','accent-map'),orders=json('content','catalogue-orders').orders;
const fixtures=json('tests','legacy-works-fixtures');
let failed=[];
for(const fixture of fixtures){
 const actual=engine.select(data,fixture.form,accent,orders).map(r=>r.id);
 try{assert.deepEqual(actual,fixture.ids);}catch{failed.push({name:fixture.name,expected:fixture.ids,actual});}
}
assert.equal(new Set(data.catalogue.map(r=>r.id)).size,179);
if(failed.length){console.error(JSON.stringify(failed,null,2));process.exitCode=1;}
else console.log(`PASS: ${fixtures.length} independently captured live catalogue cases; filters, search, order and results match.`);
