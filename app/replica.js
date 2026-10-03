/* Static equivalents of the original Hansgal UI. Content remains in JSON. */
(function () {
  'use strict';
  const base=document.querySelector('meta[name="hansgal-base"]')?.content||'';
  const language=document.documentElement.lang==='de'?'de':'en';
  const t=(en,de)=>language==='de'?de:en;
  const href=p=>base+(language==='de'&&!/^\/(app|storage|gfx|imageflow)\//.test(p)?'/de':'')+p;
  const path=decodeURI(location.pathname).slice(base.length).replace(/^\/de(?=\/|$)/,'').replace(/\/$/,'')||'/';
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const strip=s=>String(s??'').replace(/\\([nrtvabf]|x[0-9a-f]{1,2}|[0-7]{1,3}|.)/gi,(_,x)=>({n:'\n',r:'\r',t:'\t',v:'\v',a:'\x07',b:'\b',f:'\f'}[x]??(x.startsWith('x')?String.fromCharCode(parseInt(x.slice(1),16)):/^[0-7]+$/.test(x)?String.fromCharCode(parseInt(x,8)):x)));
  const read=async name=>{const r=await fetch(href('/app/'+name+(name==='site-data'&&language==='de'?'-de':'')+'.json'));if(!r.ok)throw Error('Unable to load '+name);return r.json();};
  let data,config,accent,orders;
  const ready=Promise.all([read('site-data'),read('runtime-config'),read('accent-map'),read('catalogue-orders')]).then(v=>{[data,config,accent,orders]=v;});
  const files=r=>String(r?.filename||'').split('|').filter(s=>s.includes('#')).map((s,i)=>({title:r?.track_titles?.split('\n')[i]||s.slice(0,s.indexOf('#')),filename:s.slice(s.indexOf('#')+1)}));
  function localMarkup(markup) {
    return String(markup??'').replace(/((?:href|src)\s*=\s*["'])(?:https?:\/\/(?:www\.)?hansgal\.(?:org|com))?(\/[^"']*)/gi,(_,a,b)=>a+href(b));
  }
  function lightboxes() {
    if(window.jQuery?.fn.fancybox)window.jQuery('a.imagesItem').fancybox({speedIn:600,speedOut:200,overlayShow:true,hideOnContentClick:true});
  }
  function player(container,filename,play=false) {
    let a=container.querySelector('audio');
    if(!a){a=document.createElement('audio');a.controls=true;a.preload='metadata';container.append(a);}
    a.src=href('/storage/audiosamples/'+filename);
    if(play)a.play().catch(()=>{});
    return a;
  }
  function remember(params) {
    const q=new URLSearchParams(Object.entries(params).filter(([,v])=>v!==''&&v!=null));
    history.replaceState(null,'',location.pathname+(q.size?'?'+q:'')+location.hash);
  }
  function renderWorks(form) {
    const rows=window.HansgalCatalogue.select(data,form,accent,orders.orders||{});
    const table=document.querySelector('table.catalogue-results');
    if(!table)return;
    const body=table.tBodies[0];
    const recordingWorks=new Set(data.catalogue_recordings.filter(x=>data.recording.some(r=>r.id===x.recording_id)).map(x=>x.catalogue_id));
    const audioWorks=new Set(data.catalogue_audio_sample.filter(x=>data.audio_sample.some(r=>r.id===x.audio_sample_id)).map(x=>x.catalogue_id));
    const icon=(kind,label,target,svg)=>'<a class="availability-mark availability-'+kind+'" href="'+href('/works/show/'+target)+'" aria-label="'+label+'" title="'+label+'"><svg viewBox="0 0 28 28" aria-hidden="true">'+svg+'</svg></a>';
    const scoreSvg='<path class="icon-page" d="M6 2.5h10l6 6V25.5H6Z"/><path class="icon-line" d="M16 2.5v6h6M11.5 12.5v7.2a2.5 2.5 0 1 1-1.5-2.3m1.5-4.9 5-1.2v6.5a2.5 2.5 0 1 1-1.5-2.3"/>';
    const recordingSvg='<circle class="icon-disc" cx="14" cy="14" r="10.5"/><circle class="icon-line" cx="14" cy="14" r="3.2"/><circle class="icon-hole" cx="14" cy="14" r="1"/><path class="icon-shine" d="M6.3 7.8a10 10 0 0 1 4-3l2.1 6.2a3.4 3.4 0 0 0-1.5 1.2Zm15.4 12.4a10 10 0 0 1-4 3L15.6 17a3.4 3.4 0 0 0 1.5-1.2Z"/>';
    const audioSvg='<path class="icon-speaker" d="M3.5 11h4l5-4v14l-5-4h-4Z"/><path class="icon-line" d="M16 10.4a5.2 5.2 0 0 1 0 7.2M19.1 7.7a8.7 8.7 0 0 1 0 12.6"/>';
    const marks=r=>'<span class="availability-marks">'+(r.score_available==='yes'&&r.score_file?icon('score',t('Downloadable score available','Noten zum Herunterladen verfügbar'),r.id+'/#downloadable-score',scoreSvg):'')+(recordingWorks.has(r.id)?icon('recording',t('Recordings available','Aufnahmen verfügbar'),r.id+'/#recordings',recordingSvg):'')+(audioWorks.has(r.id)?icon('audio',t('Audio samples available','Hörproben verfügbar'),r.id+'/#audio-samples',audioSvg):'')+'</span>';
    body.innerHTML=rows.map((r,i)=>'<tr class="'+(i%2?'dark':'light')+'"><td>'+(r.opus_no??'')+'</td><td><a href="'+href('/works/show/'+r.id)+'">'+strip(r.title)+'</a></td><td>'+(r.description??'')+'</td><td>'+(r.year_of_composition&&r.year_of_composition!=='0'?r.year_of_composition:'')+'</td><td>'+(r.publisher??'')+'</td><td>'+marks(r)+'</td></tr>').join('');
    if(!rows.length)body.innerHTML='<tr class="light"><td colspan="6">'+t('No result','Kein Ergebnis')+'</td></tr>';
    table.dataset.resultCount=String(rows.length);
    const labels=[t('Opus','Opus'),t('Title','Titel'),t('Description','Beschreibung'),t('Year','Jahr'),t('Publisher','Verlag'),t('Available','Verfügbar')];
    Array.from(table.rows).slice(1).forEach(row=>Array.from(row.cells).forEach((cell,i)=>cell.dataset.label=labels[i]));
    const count=document.getElementById('catalogue-count');if(count)count.textContent=rows.length+' '+t('works','Werke');
    table.querySelectorAll('[data-sort]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.sort===form.ordercolumn&&b.dataset.direction===form.orderby)));
    remember(form);
  }
  async function submit(id,button='') {
    await ready;
    const form=document.getElementById(id);
    if(id==='worksform') {
      const values=Object.fromEntries(new FormData(form));
      values.submitbutton=button||'Go';
      // All controls participate in filtering and sorting together.
      renderWorks(values);
    } else if(id==='audioform')selectAudio(form.elements.chosenwork.value);
    else if(id==='audiofile')selectSample(form);
  }
  function selectAudio(index,sample=null,play=false) {
    const old=document.getElementById('audio-selection');if(old)old.remove();
    if(index==='') {remember({});return;}
    const record=data.audio_sample.find(r=>r.id===config.audioOrder[Number(index)]);if(!record)return;
    const tracks=files(record), selected=sample==null?-1:Number(sample);
    const area=document.createElement('div');area.id='audio-selection';
    area.innerHTML='<br /><audio controls="controls" preload="metadata"></audio><br />'+t('Please choose a sample','Bitte wählen Sie eine Hörprobe')+'<br /><form id="audiofile"><input type="hidden" name="chosenwork" value="'+esc(index)+'">'+tracks.map((f,i)=>'<label><input type="radio" name="chosenfile" value="'+i+'"'+(selected===i?' checked':'')+' onchange="Hansgal.submit(\'audiofile\')">'+f.title+'</label><br>').join('')+'</form>'+(record.opus_no!=='Op. -'?'<br />'+record.opus_no+'<br />':'')+localMarkup(record.details);
    document.getElementById('audioform').parentElement.append(area);
    player(area,tracks[Math.max(0,selected)]?.filename,play);
    remember({chosenwork:index,chosenfile:selected<0?'':selected});
  }
  function selectSample(form) {
    const selected=form.elements.chosenfile.value;
    if(path==='/audiosamples'){selectAudio(form.elements.chosenwork.value,selected,true);return;}
    const id=path.split('/').pop();
    const relation=data.catalogue_audio_sample.find(r=>r.catalogue_id===id);
    const record=data.audio_sample.find(r=>r.id===relation?.audio_sample_id);
    const track=files(record)[Number(selected)];if(!track)return;
    let target=document.getElementById('work-audio');
    if(!target){target=document.createElement('div');target.id='work-audio';form.before(target);}
    player(target,track.filename,true);remember({chosenfile:selected});
  }
  function viewMode(mode) {
    try{sessionStorage.setItem('hansgal-recording-view',mode);}catch{}
    const browser=document.querySelector('.recording-browser');if(!browser)return;
    browser.classList.toggle('flow-view',mode==='coverflow');
    if(mode==='coverflow')browser.open=true;
    const button=document.getElementById('recording-view-toggle');
    if(button){button.textContent=mode==='coverflow'?t('Grid view','Rasteransicht'):t('Horizontal view','Horizontale Ansicht');button.setAttribute('aria-pressed',String(mode==='coverflow'));}
  }
  function search(keyword) {
    const target=document.getElementById('search-results');if(!target)return;
    const k=window.HansgalCatalogue.unaccent(keyword,accent).toLowerCase();
    const match=(r,fields)=>fields.some(f=>window.HansgalCatalogue.like(window.HansgalCatalogue.unaccent(r[f],accent).toLowerCase(),k));
    const plain=s=>{const d=document.createElement('div');d.innerHTML=strip(s);return d.textContent||'';};
    const sections=[['ARTICLES',data.menu,['title','lead','body'],'body',r=>'/'+r.mainmenu+'/'+r.id],['AUDIO SAMPLES',config.audioOrder.map(id=>data.audio_sample.find(r=>r.id===id)),['title','details'],'details',r=>'/audiosamples?chosenwork='+config.audioOrder.indexOf(r.id)],['WORKS',data.catalogue,['title','description','title_de','description_de','hidden_terms','publisher','further_details','free_downloads','other_versions'],'description',r=>'/works/show/'+r.id],['PHOTOS',data.photos,['title'],'title',r=>'/storage/photos/'+r.filename],['RECORDINGS',data.recording,['title','detail','review'],'detail',r=>'/recordings/'+r.id]];
    if(!keyword.trim()){target.innerHTML='<p>'+t('Enter a word, title or name to explore the archive.','Geben Sie ein Wort, einen Titel oder einen Namen ein, um das Archiv zu durchsuchen.')+'</p>';return;}
    target.innerHTML=sections.map(([heading,rows,fields,desc,route])=> {
      const hits=rows.filter(r=>match(r,fields));
      const title={ARTICLES:t('Articles','Artikel'),'AUDIO SAMPLES':t('Audio samples','Hörproben'),WORKS:t('Works','Werke'),PHOTOS:t('Photographs','Fotografien'),RECORDINGS:t('Recordings','Aufnahmen')}[heading];
      return '<section><h2>'+title+' <small>('+hits.length+')</small></h2>'+(hits.length?hits.map(r=>'<article><h3><a '+(heading==='PHOTOS'?'class="imagesItem" rel="group'+r.photos_category_id+'" ':'')+'href="'+href(route(r))+'">'+strip(r.title)+'</a></h3>'+(heading==='PHOTOS'?'':'<p>'+esc(plain(r[desc]).slice(0,210))+(plain(r[desc]).length>210?'…':'')+'</p>')+'</article>').join(''):'<p>'+t('No result.','Kein Ergebnis.')+'</p>')+'</section>';
    }).join('');lightboxes();
  }
  window.Hansgal={
    init:lightboxes,initFancybox:lightboxes,submit,
    order:async (column,direction)=>{document.getElementById('ordercolumn').value=column;document.getElementById('orderby').value=direction;await submit('worksform');},
    showBlock:id=>{const e=document.getElementById(id);if(e){const open=getComputedStyle(e).display==='none';e.style.display=open?'block':'none';document.querySelector('[aria-controls="'+id+'"]')?.setAttribute('aria-expanded',String(open));}},
    showSmallPhoto:id=>{const e=document.getElementById('thumb'+id);if(e)e.style.display='block';},
    hideSmallPhoto:id=>{const e=document.getElementById('thumb'+id);if(e)e.style.display='none';},
    playAS:async (id,filename)=>{await ready;const d=document.getElementById('detail_'+id);const open=d&&getComputedStyle(d).display==='none';if(d)d.style.display=open?'block':'none';if(open){const r=data.audio_sample.find(r=>r.id===String(id));window.Hansgal.playASItem(filename||files(r)[0]?.filename,id,0);}},
    playASItem:async (filename,id,index)=>{await ready;if(!files(data.audio_sample.find(r=>r.id===String(id))).some(f=>f.filename===filename))return;player(document.getElementById('player'),filename,true);document.querySelectorAll('span.nowplaying').forEach(e=>e.innerHTML='');const s=document.getElementById('nowplaying_'+id+'_'+index);if(s)s.innerHTML='<i>'+t('Now playing...','Wird abgespielt …')+'</i>';},
    getRecordingInfo:async id=>{await ready;if(data.recording.some(r=>r.id===String(id)))location.assign(href('/recordings/'+encodeURIComponent(id)+'/'));},
    viewMode
  };
  function init() {
    lightboxes();
    const searchForm=document.querySelector('.searchbox form');
    if(searchForm){searchForm.method='get';searchForm.onsubmit=e=>{e.preventDefault();location.href=href('/search?keyword='+encodeURIComponent(searchForm.elements.keyword.value));};}
    const params=Object.fromEntries(new URLSearchParams(location.search));
    if(path==='/works') {
      const form=document.getElementById('worksform');form.onsubmit=e=>{e.preventDefault();submit('worksform',e.submitter?.value||'Go');};
      for(const [k,v] of Object.entries(params))if(form.elements[k]&&k!=='submitbutton')form.elements[k].value=v;
      form.querySelectorAll('select').forEach(select=>select.addEventListener('change',()=>submit('worksform')));
      if(Object.keys(params).length)renderWorks(params);
    }
    if(path==='/audiosamples'&&!document.getElementById('listening-station')) {
      document.getElementById('audioform').onsubmit=e=>{e.preventDefault();submit('audioform');};
      if(params.chosenwork!==undefined){document.querySelector('[name=chosenwork]').value=params.chosenwork;selectAudio(params.chosenwork,params.chosenfile??null);}
    }
    if(path==='/recordings'||/^\/recordings\/\d+$/.test(path))viewMode(params.view||(()=>{try{return sessionStorage.getItem('hansgal-recording-view');}catch{return null;}})()||'coverlist');
    if(path==='/search')search(params.keyword||'');
    if(path==='/comments') {
      const form=document.querySelector('.article form');
      if(form)form.onsubmit=e=>{e.preventDefault();let note=document.getElementById('comment-review-note');if(!note){note=document.createElement('p');note.id='comment-review-note';note.setAttribute('role','status');form.after(note);}note.textContent=t('This review copy does not send or store comments. Please use the Contacts page to get in touch.','Diese Vorschau sendet und speichert keine Kommentare. Bitte nutzen Sie die Kontaktseite.');};
    }
    document.documentElement.dataset.hansgalReady='true';
  }
  ready.then(init).catch(error=>{console.error(error);document.documentElement.dataset.hansgalReady='error';});
})();
