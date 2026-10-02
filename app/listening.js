(async function(){
 'use strict';const station=document.getElementById('listening-station');if(!station)return;
 const base=document.querySelector('meta[name=hansgal-base]')?.content||'',de=document.documentElement.lang==='de',t=(a,b)=>de?b:a,$=id=>document.getElementById(id);
 const plain=s=>{const d=document.createElement('div');d.innerHTML=s||'';return d.textContent;};const norm=s=>plain(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 try{const results=await Promise.all([fetch(base+'/app/site-data'+(de?'-de':'')+'.json'),fetch(base+'/app/runtime-config.json')]);if(results.some(r=>!r.ok))throw Error('Listening data unavailable');const [data,config]=await Promise.all(results.map(r=>r.json()));
 const tracks=[],records=new Map();let category='',current=-1;
 const popupMode=new URLSearchParams(location.search).get('player')==='1';let floating=null,pendingTransfer=false;
 if(popupMode){document.body.classList.add('listening-window');document.title=t('Hans Gál · Listening player','Hans Gál · Hörplayer');}
 config.audioOrder.forEach((id,index)=>{const r=data.audio_sample.find(r=>r.id===id);if(!r)return;const works=data.catalogue_audio_sample.filter(x=>x.audio_sample_id===id).map(x=>x.catalogue_id),categories=new Set(data.catalogue_category.filter(x=>works.includes(x.catalogue_id)).map(x=>x.category_id));const search=[r.title,r.opus_no,r.details,...data.catalogue.filter(w=>works.includes(w.id)).flatMap(w=>[w.title,w.description,w.orchestration]),...data.category.filter(c=>categories.has(c.id)).map(c=>c.name)].join(' ');records.set(id,{r,works,categories,search:norm(search)});r.filename.split('|').filter(s=>s.includes('#')).forEach((s,i)=>{const n=s.indexOf('#');tracks.push({id,index,i,r,title:r.track_titles?.split('\n')[i]||s.slice(0,n),filename:s.slice(n+1)});});});
 const today=Math.floor(Date.now()/86400000),daily=((today*37)%tracks.length+tracks.length)%tracks.length;const day=tracks[daily];$('daily-title').textContent=plain(day.r.title);$('daily-track').textContent=(day.r.opus_no==='Op. -'?'':day.r.opus_no+' · ')+plain(day.title);
 const player=$('listening-player');$('close-listening').onclick=()=>{player.pause();if(popupMode){window.close();return;}$('listening-now').hidden=true;};function select(n,play=true){if(!Number.isInteger(n)||!tracks.length)return;current=(n+tracks.length)%tracks.length;if(!popupMode&&floating&&!floating.closed){floating.postMessage({type:'hansgal-select',n:current,play},location.origin);$('player-message').textContent=t('Playing in the separate player window.','Wiedergabe im separaten Player-Fenster.');return;}const track=tracks[current];$('listening-now').hidden=false;$('now-title').textContent=plain(track.r.title);$('now-track').textContent=plain(track.title);player.src=base+'/storage/audiosamples/'+encodeURIComponent(track.filename);$('player-message').textContent='';const work=records.get(track.id).works[0];$('now-work').hidden=!work;if(work)$('now-work').href=base+(de?'/de':'')+'/works/show/'+work+'/';station.querySelectorAll('[data-track]').forEach(a=>{const active=a.closest('[data-audio-id]').dataset.audioId===track.id&&+a.dataset.track===track.i;a.setAttribute('aria-current',String(active));});history.replaceState(null,'',location.pathname+'?chosenwork='+track.index+'&chosenfile='+track.i+(popupMode?'&player=1':''));if(play)player.play().catch(()=>$('player-message').textContent=t('Press play to start this excerpt.','Drücken Sie auf Wiedergabe, um diese Hörprobe zu starten.'));}
 $('play-daily').onclick=()=>select(daily);$('surprise-listening').onclick=()=>select(Math.floor(Math.random()*tracks.length));$('previous-excerpt').onclick=()=>select(current-1);$('next-excerpt').onclick=()=>select(current+1);player.addEventListener('ended',()=>{if($('continuous-listening').checked)select(current+1);});player.addEventListener('error',()=>$('player-message').textContent=t('This excerpt could not be loaded. Please try again or choose another.','Diese Hörprobe konnte nicht geladen werden. Bitte versuchen Sie es erneut oder wählen Sie eine andere.'));
 station.querySelectorAll('[data-track]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();select(tracks.findIndex(f=>f.id===a.closest('[data-audio-id]').dataset.audioId&&f.i===+a.dataset.track));}));
 function filter(){const query=norm($('listening-search').value);let count=0;station.querySelectorAll('[data-audio-id]').forEach(card=>{const r=records.get(card.dataset.audioId),show=(!category||r.categories.has(category))&&(!query||r.search.includes(query));card.hidden=!show;if(show)count++;});$('listening-count').textContent=count+' '+t('works to explore','Werke zum Entdecken')+(count?'':t(' — try another search.',' — versuchen Sie einen anderen Suchbegriff.'));}
 station.querySelectorAll('[data-listening-category]').forEach(button=>button.addEventListener('click',()=>{category=button.dataset.listeningCategory;station.querySelectorAll('[data-listening-category]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filter();}));$('listening-search').addEventListener('input',filter);filter();
 const params=new URLSearchParams(location.search);if(params.has('chosenwork')){const n=tracks.findIndex(f=>f.index===+params.get('chosenwork')&&f.i===+(params.get('chosenfile')||0));if(n>=0){select(n,false);station.querySelector('[data-audio-id="'+tracks[n].id+'"] details').open=true;}}

 const panel=$('listening-now'),minimise=$('minimise-listening'),miniPlay=$('mini-play');
 minimise.onclick=()=>{const small=panel.classList.toggle('is-minimised');minimise.setAttribute('aria-expanded',String(!small));minimise.textContent=small?t('Expand','Vergrößern'):t('Minimise','Verkleinern');miniPlay.hidden=!small;updateMini();};
 const updateMini=()=>miniPlay.textContent=player.paused?t('Play','Wiedergabe'):t('Pause','Pause');
 player.addEventListener('play',updateMini);player.addEventListener('pause',updateMini);
 miniPlay.onclick=()=>{if(player.paused)player.play().catch(()=>{$('player-message').textContent=t('Press play to start.','Drücken Sie auf Wiedergabe.');});else player.pause();};
 $('popout-listening').onclick=()=>{
  if(current<0)return;
  if(floating&&!floating.closed){floating.focus();return;}
  const track=tracks[current],url=new URL(location.href);
  url.search=new URLSearchParams({player:'1',chosenwork:track.index,chosenfile:track.i}).toString();
  floating=window.open(url.href,'HansGalListening','popup=yes,width=560,height=420,resizable=yes,scrollbars=yes');
  pendingTransfer=!!floating;
  $('player-message').textContent=floating?t('Opening the separate player…','Separater Player wird geöffnet …'):t('The player window was blocked. Allow pop-ups for this site, then try again. Your current player is still available.','Das Player-Fenster wurde blockiert. Erlauben Sie Pop-ups für diese Website und versuchen Sie es erneut. Der aktuelle Player bleibt verfügbar.');
 };
 window.addEventListener('message',event=>{
  if(event.origin!==location.origin||!event.data||typeof event.data!=='object')return;
  const message=event.data;
  if(!popupMode&&event.source===floating&&message.type==='hansgal-ready'&&pendingTransfer){
   pendingTransfer=false;const transfer={type:'hansgal-select',n:current,time:player.currentTime,play:!player.paused,continuous:$('continuous-listening').checked};
   player.pause();floating.postMessage(transfer,location.origin);panel.hidden=true;
  }
  if(popupMode&&event.source===window.opener&&message.type==='hansgal-select'&&Number.isInteger(message.n)&&message.n>=0&&message.n<tracks.length){
   if(typeof message.continuous==='boolean')$('continuous-listening').checked=message.continuous;
   select(message.n,false);
   const resume=()=>{if(Number.isFinite(message.time)&&message.time>=0)player.currentTime=Math.min(message.time,Number.isFinite(player.duration)?player.duration:message.time);if(message.play)player.play().catch(()=>$('player-message').textContent=t('Press play to continue listening.','Drücken Sie auf Wiedergabe, um weiterzuhören.'));};
   if(player.readyState>=1)resume();else {player.addEventListener('loadedmetadata',resume,{once:true});player.load();}
  }
 });
 if(popupMode){panel.querySelector('.eyebrow').textContent=t('Hans Gál · Listening player','Hans Gál · Hörplayer');$('popout-listening').hidden=true;$('now-work').target='_blank';$('now-work').rel='noopener';window.opener?.postMessage({type:'hansgal-ready'},location.origin);}

 station.dataset.ready='true';
 }catch(error){$('listening-count').textContent=t('The interactive collection could not load. You can still open any work below and listen directly.','Die interaktive Sammlung konnte nicht geladen werden. Sie können unten weiterhin jedes Werk öffnen und direkt anhören.');console.error(error);}
})();
