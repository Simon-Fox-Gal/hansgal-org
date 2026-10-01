const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const json=(folder,name)=>JSON.parse(fs.readFileSync(path.join(root,folder,name+'.json'),'utf8'));
const engine=require('../app/catalogue.js');
const data=json('tests','preservation-data');
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
// Editing sort fields must invalidate captured ranks; new works must join the
// catalogue, categories and search immediately without another SQL capture.
const edited=structuredClone(data),changed=edited.catalogue.find(r=>r.id==='6');
changed.title='ZZZZ Editorial ordering test';
assert.equal(engine.select(edited,{ordercolumn:'title',orderby:'DESC'},accent,orders)[0].id,'6');
changed.opus_no='9999';
assert.equal(engine.select(edited,{ordercolumn:'opus_no',orderby:'DESC'},accent,orders)[0].id,'6');
const added={...edited.catalogue[0],id:'9999',title:'Aardvark newly added work',opus_no:'9998',hidden_terms:'editorialnewwork'};
edited.catalogue.push(added);
edited.catalogue_category.push({id:'9999',catalogue_id:'9999',category_id:'1'});
assert(engine.select(edited,{},accent,orders).some(r=>r.id==='9999'));
assert(engine.select(edited,{genre:'1'},accent,orders).some(r=>r.id==='9999'));
assert.deepEqual(engine.select(edited,{submitbutton:'Search',title:'editorialnewwork'},accent,orders).map(r=>r.id),['9999']);
const current={catalogue:json('content','catalogue'),catalogue_category:json('content','catalogue_category')};
assert.equal(engine.select(current,{},accent,orders).length,current.catalogue.length);
console.log('PASS: edited sort values, new work visibility, category membership and search; current catalogue contains every work.');
