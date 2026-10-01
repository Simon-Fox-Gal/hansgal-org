const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync(require('node:path').join(__dirname,'../app/language.js'),'utf8');
const events={},saved={};
const links=['en','de'].map(language=>({dataset:{language},setAttribute(){},addEventListener(name,fn){events[language]=fn;}}));
const location={pathname:'/hansgal-org/de/works/',search:'',hash:''};
vm.runInNewContext(source,{location,document:{documentElement:{lang:'de'},querySelector:()=>({content:'/hansgal-org'}),querySelectorAll:()=>links},localStorage:{setItem:(k,v)=>saved[k]=v,getItem:k=>saved[k]}});
// A search followed by sorting changes the URL after initial page setup.
location.search='?title=Trio&ordercolumn=year_of_composition&orderby=DESC';
location.hash='#results';events.en();
assert.equal(links[0].href,'/hansgal-org/works/'+location.search+'#results');
assert.equal(saved['hansgal-language'],'en');
events.de();assert.equal(links[1].href,'/hansgal-org/de/works/'+location.search+'#results');
assert.equal(saved['hansgal-language'],'de');
console.log('PASS: language links preserve current search, sorting and fragment after client navigation.');
