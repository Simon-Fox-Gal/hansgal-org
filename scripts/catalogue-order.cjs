const fs=require('node:fs');
const {data,accent,orders}=JSON.parse(fs.readFileSync(0,'utf8'));
process.stdout.write(JSON.stringify(require('../app/catalogue.js').select(data,{},accent,orders).map(r=>r.id)));
