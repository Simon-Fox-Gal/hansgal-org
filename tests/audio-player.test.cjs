const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'app/audio-player.js'),'utf8');
const markup=fs.readFileSync(path.join(root,'dist/audiosamples/index.html'),'utf8');
const rows=JSON.parse(markup.match(/id="audio-page-data">([\s\S]*?)<\/script>/)[1]);
function boot(records,search='',discovery=false){
 const ids=new Map(),links=records.flatMap(r=>r.files.map(f=>({dataset:{sample:f.filename},events:{},setAttribute(){},addEventListener(n,fn){this.events[n]=fn;},closest(){return null;}})));
 const make=()=>({textContent:'',dataset:{},hidden:true,checked:false,classList:{toggle(){return false;},add(){}},setAttribute(){},addEventListener(){}});
 for(const id of ['audio-page-data','listening-now','now-title','now-track','now-credit','now-cover','now-recording','now-work','player-message','previous-excerpt','next-excerpt','close-listening','continuous-listening','mini-play','minimise-listening','popout-listening'])ids.set(id,make());
 ids.get('audio-page-data').textContent=JSON.stringify(records);
 if(discovery)for(const id of ['daily-title','daily-track','play-daily','surprise-listening'])ids.set(id,make());
 const player={...make(),src:'',paused:true,plays:0,play(){this.paused=false;this.plays++;return Promise.resolve();},pause(){this.paused=true;}};ids.set('listening-player',player);
 const location={search,pathname:'/works/show/19/',hash:'',origin:'https://hansgal.org'};let address='';
 const context={URLSearchParams,Map,Date,Math,Number,JSON,console,location,history:{replaceState(a,b,c){address=c;}},document:{documentElement:{lang:'en'},getElementById:id=>ids.get(id)||null,querySelector:()=>({content:'/test'}),querySelectorAll:()=>links,createElement:()=>({set innerHTML(v){this.textContent=v.replace(/<[^>]*>/g,'');}})},window:{addEventListener(){},opener:null},fetch(){throw Error('Player must not load a separate cached playlist');}};
 vm.runInNewContext(source,context);return {links,player,ids,address:()=>address};
}
let count=0;
for(const row of rows){
 const state=boot([row]);
 for(const [i,link] of state.links.entries()){
  const before=state.player.plays;let prevented=false;
  link.events.click({preventDefault(){prevented=true;}});
  assert.equal(prevented,true);assert.equal(state.player.plays,before+1,'Play must start synchronously from the click');
  assert.equal(state.player.src,'/test/storage/audiosamples/'+encodeURIComponent(row.files[i].filename));
  assert.match(state.address(),/^\/works\/show\/19\/\?sample=/,'Work page must not navigate away');
  assert.equal(state.ids.get('now-cover').src,'/test'+(row.files[i].credit?.cover||'/app/audio-placeholder.svg'));count++;
 }
}
const ente=rows.find(r=>r.id==='14'),opus8=rows.find(r=>r.opus_no==='Op.8');
assert.equal(ente.files.length,33);assert(ente.files.every(f=>f.filename.startsWith('gal-ente-')));
assert.equal(opus8.files.length,2);assert(opus8.files.every(f=>f.filename.startsWith('gal-tocc0751-')));
for(const bad of ['?sample=not-a-track.mp3','?chosenfile=999','?chosenfile=-1']){const s=boot([ente],bad);assert.equal(s.player.src,'');assert.equal(s.player.plays,0);}
const legacy=boot([ente],'?chosenfile=2');assert.equal(legacy.player.src,'/test/storage/audiosamples/'+ente.files[2].filename);assert.equal(legacy.player.plays,0);
console.log(`PASS: ${count} click-to-play selections stay on the work page with correct audio/artwork; invalid tracks never fall back; old work bookmarks select locally; no network playlist dependency.`);

const discover=boot(rows,'',true);
assert.equal(discover.ids.get('listening-now').hidden,true);assert.equal(discover.player.src,'');assert.equal(discover.player.plays,0);assert.equal(discover.address(),'');
const dailyIndex=(Math.floor(Date.now()/86400000)*37)%count;
const allTracks=rows.flatMap(r=>r.files);
discover.ids.get('play-daily').onclick();assert(discover.player.src.endsWith(allTracks[dailyIndex].filename));assert.equal(discover.player.plays,1);assert.equal(discover.ids.get('listening-now').hidden,false);
const previous=discover.player.src;discover.ids.get('surprise-listening').onclick();assert.notEqual(discover.player.src,previous);assert.equal(discover.player.plays,2);
const chosen=boot(rows,'?sample='+rows[1].files[0].filename,true);assert(chosen.player.src.endsWith(rows[1].files[0].filename));assert.equal(chosen.player.plays,0);
console.log('PASS: discovery waits for a click; daily and surprise buttons open and play their chosen track in situ; surprise avoids an immediate repeat; explicit track requests still work.');
