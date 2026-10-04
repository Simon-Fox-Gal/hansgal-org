/* One page-bound player: track identity is a filename, never a list position. */
(function () {
  'use strict';
  const $=id=>document.getElementById(id), data=$('audio-page-data'), panel=$('listening-now');
  if(!data||!panel)return;
  const base=document.querySelector('meta[name=hansgal-base]')?.content||'';
  const de=document.documentElement.lang==='de', t=(en,ger)=>de?ger:en;
  const plain=s=>{const el=document.createElement('div');el.innerHTML=s||'';return el.textContent;};
  const norm=s=>plain(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const records=JSON.parse(data.textContent), tracks=[];
  for(const r of records)for(const f of r.files)tracks.push({...f,record:r});
  const byFile=new Map(tracks.map((track,i)=>[track.filename,{track,i}]));
  const links=[...document.querySelectorAll('a[data-sample]')], station=$('listening-station');
  const player=$('listening-player'), params=new URLSearchParams(location.search);
  const popup=params.get('player')==='1';let current=-1,floating=null,pendingTransfer=false;
  const asset=file=>base+'/storage/audiosamples/'+encodeURIComponent(file);
  const pageLink=path=>base+(de?'/de':'')+path;
  function select(filename,play=true,remember=true){
    const found=byFile.get(filename);
    // Unknown/obsolete requests must never select an unrelated last track.
    if(!found)return false;
    const {track,i}=found;current=i;
    if(!popup&&floating&&!floating.closed){floating.postMessage({type:'hansgal-select',filename,play},location.origin);return true;}
    panel.hidden=false;
    $('now-title').textContent=plain(track.record.title);$('now-track').textContent=plain(track.title);
    const c=track.credit||{};
    $('now-credit').textContent=[c.preview?t('Unreleased recording · preview','Unveröffentlichte Aufnahme · Vorschau'):'',c.performers,c.label,c.copyright].filter(Boolean).join(' · ');
    $('now-cover').src=base+(c.cover||'/app/audio-placeholder.svg');
    $('now-cover').alt=c.cover?plain(c.album_title):'';
    $('now-recording').hidden=!c.link;
    if(c.link){$('now-recording').href=pageLink(c.link);$('now-recording').textContent=plain(c.album_title)+' →';}
    $('now-work').hidden=!track.record.work_id;
    if(track.record.work_id)$('now-work').href=pageLink('/works/show/'+track.record.work_id+'/');
    player.src=asset(filename);$('player-message').textContent='';
    for(const link of links)link.setAttribute('aria-current',String(link.dataset.sample===filename));
    if(remember){const q=new URLSearchParams(location.search);q.delete('chosenwork');q.delete('chosenfile');q.set('sample',filename);history.replaceState(null,'',location.pathname+'?'+q+location.hash);}
    // Called synchronously by the click handler, preserving browser play permission.
    if(play)player.play().catch(()=>$('player-message').textContent=t('Press play to start this excerpt.','Drücken Sie auf Wiedergabe, um diese Hörprobe zu starten.'));
    return true;
  }
  for(const link of links)link.addEventListener('click',event=>{if(event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();select(link.dataset.sample);});
  const step=delta=>{if(current>=0&&tracks.length)select(tracks[(current+delta+tracks.length)%tracks.length].filename);};
  $('previous-excerpt').onclick=()=>step(-1);$('next-excerpt').onclick=()=>step(1);
  $('close-listening').onclick=()=>{player.pause();if(popup)window.close();else panel.hidden=true;};
  player.addEventListener('ended',()=>{if($('continuous-listening').checked)step(1);});
  player.addEventListener('error',()=>$('player-message').textContent=t('This excerpt could not be loaded. Please try again.','Diese Hörprobe konnte nicht geladen werden. Bitte versuchen Sie es erneut.'));
  const mini=$('mini-play'),minimise=$('minimise-listening');
  function updateMini(){mini.textContent=player.paused?t('Play','Wiedergabe'):t('Pause','Pause');}
  minimise.onclick=()=>{const small=panel.classList.toggle('is-minimised');minimise.setAttribute('aria-expanded',String(!small));minimise.textContent=small?t('Expand','Vergrößern'):t('Minimise','Verkleinern');mini.hidden=!small;updateMini();};
  player.addEventListener('play',updateMini);player.addEventListener('pause',updateMini);
  mini.onclick=()=>{if(player.paused)player.play().catch(()=>{});else player.pause();};
  $('popout-listening').onclick=()=>{
    if(current<0)return;if(floating&&!floating.closed){floating.focus();return;}
    const url=pageLink('/audiosamples/')+'?'+new URLSearchParams({player:'1',sample:tracks[current].filename});
    floating=window.open(url,'HansGalListening','popup=yes,width=560,height=520,resizable=yes,scrollbars=yes');pendingTransfer=!!floating;
    $('player-message').textContent=floating?t('Opening the separate player…','Separater Player wird geöffnet …'):t('Allow pop-ups to open the separate player.','Erlauben Sie Pop-ups, um den separaten Player zu öffnen.');
  };
  window.addEventListener('message',event=>{
    if(event.origin!==location.origin||!event.data||typeof event.data!=='object')return;
    const msg=event.data;
    if(!popup&&event.source===floating&&msg.type==='hansgal-ready'&&pendingTransfer){
      pendingTransfer=false;const transfer={type:'hansgal-select',filename:tracks[current].filename,time:player.currentTime,play:!player.paused,continuous:$('continuous-listening').checked};
      player.pause();floating.postMessage(transfer,location.origin);panel.hidden=true;
    }
    if(popup&&event.source===window.opener&&msg.type==='hansgal-select'&&byFile.has(msg.filename)){
      if(typeof msg.continuous==='boolean')$('continuous-listening').checked=msg.continuous;
      select(msg.filename,false);
      const resume=()=>{if(Number.isFinite(msg.time)&&msg.time>=0)player.currentTime=Math.min(msg.time,Number.isFinite(player.duration)?player.duration:msg.time);if(msg.play)player.play().catch(()=>{});};
      if(player.readyState>=1)resume();else{player.addEventListener('loadedmetadata',resume,{once:true});player.load();}
    }
  });
  if(station&&tracks.length){
    const daily=(Math.floor(Date.now()/86400000)*37)%tracks.length,day=tracks[daily];
    $('daily-title').textContent=plain(day.record.title);$('daily-track').textContent=plain(day.title);
    $('play-daily').onclick=()=>select(day.filename);$('surprise-listening').onclick=()=>select(tracks[Math.floor(Math.random()*tracks.length)].filename);
    let category='';const rows=new Map(records.map(r=>[r.id,r]));
    function filter(){let count=0;const query=norm($('listening-search').value);for(const card of station.querySelectorAll('article[data-audio-id]')){const r=rows.get(card.dataset.audioId);const show=(!category||r.categories.includes(category))&&(!query||norm(r.search).includes(query));card.hidden=!show;if(show)count++;}$('listening-count').textContent=count+' '+t('entries to explore','Einträge zum Entdecken');}
    for(const b of station.querySelectorAll('[data-listening-category]'))b.addEventListener('click',()=>{category=b.dataset.listeningCategory;for(const other of station.querySelectorAll('[data-listening-category]'))other.setAttribute('aria-pressed',String(other===b));filter();});
    $('listening-search').addEventListener('input',filter);filter();station.dataset.ready='true';
  }
  let requested=params.get('sample');
  if(!requested&&params.has('chosenfile')){
    const row=params.has('chosenwork')?records.find(r=>r.playback_index===Number(params.get('chosenwork'))):(!station?records[0]:null);
    requested=row?.files.find(f=>f.index===Number(params.get('chosenfile')))?.filename;
  }
  if(requested&&select(requested,false,false)){
    const link=links.find(a=>a.dataset.sample===requested);if(link?.closest('details'))link.closest('details').open=true;
    const section=$('audiosamples_content');if(section){section.style.display='block';$('audio-samples')?.setAttribute('aria-expanded','true');}
  }else if(params.has('sample')||params.has('chosenfile')){panel.hidden=false;$('player-message').textContent=t('This excerpt is not available on this page. Choose a track below.','Diese Hörprobe ist auf dieser Seite nicht verfügbar. Wählen Sie unten einen Titel.');}
  if(panel.dataset.startVisible==='true'&&!params.has('sample')&&!params.has('chosenfile')&&tracks.length)select(tracks[0].filename,false,false);
  if(location.hash==='#audio-samples'&&$('audiosamples_content')){$('audiosamples_content').style.display='block';$('audio-samples')?.setAttribute('aria-expanded','true');}
  if(popup){document.body.classList.add('listening-window');panel.hidden=false;$('popout-listening').hidden=true;for(const id of ['now-work','now-recording']){$(id).target='_blank';$(id).rel='noopener';}window.opener?.postMessage({type:'hansgal-ready'},location.origin);}
  panel.dataset.ready='true';
})();
