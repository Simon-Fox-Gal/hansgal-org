/* Folio reading tools. Authored HTML remains complete without JavaScript. */
(() => {
 'use strict';
 const labels=document.getElementById('reference-labels');if(!labels)return;
 const ui=JSON.parse(labels.textContent), root=document.querySelector('.reference-folio'), source=root?.querySelector('[data-reference-source]');
 const page=root?.dataset.referencePage||'', groups=[];
 const node=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const generated=e=>{e.dataset.refUi='';return e;};
 const text=e=>(e.textContent||'').replace(/\s+/g,' ').trim();
 const fold=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase();
 let serial=0;
 function tabs(panels,names,defaultIndex=0){
  if(panels.length<2)return;
  const nav=generated(node('nav','ref-tabs'));nav.setAttribute('aria-label',ui.nav);nav.setAttribute('role','tablist');panels[0].before(nav);
  const links=panels.map((panel,i)=>{
   panel.id ||= 'ref-panel-'+(++serial);panel.classList.add('ref-panel');panel.setAttribute('role','tabpanel');
   const a=node('a','',names[i]);a.href='#'+panel.id;a.id=panel.id+'-tab';a.setAttribute('role','tab');a.setAttribute('aria-controls',panel.id);panel.setAttribute('aria-labelledby',a.id);panel.tabIndex=0;nav.append(a);return a;
  });
  const activate=(index,focus=false)=>{panels.forEach((p,i)=>{p.hidden=i!==index;links[i].setAttribute('aria-selected',String(i===index));links[i].tabIndex=i===index?0:-1;});if(focus)links[index].focus();};
  links.forEach((a,i)=>{
   a.addEventListener('click',e=>{if(e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();activate(i);history.pushState(null,'',a.getAttribute('href'));});
   a.addEventListener('keydown',e=>{let n=i;if(e.key==='ArrowRight')n=(i+1)%links.length;else if(e.key==='ArrowLeft')n=(i+links.length-1)%links.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=links.length-1;else return;e.preventDefault();activate(n,true);history.replaceState(null,'',links[n].getAttribute('href'));});
  });
  groups.push({panels,activate,defaultIndex});activate(defaultIndex);return nav;
 }
 function group(elements,id){
  const panel=node('section','ref-panel');panel.id=id;elements[0].before(panel);elements.forEach(e=>panel.append(e));return panel;
 }
 function revealHash(scroll=false){
  let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}
  const target=id&&document.getElementById(id);
  for(const g of groups){const n=target?g.panels.findIndex(p=>p===target||p.contains(target)):-1;if(n>=0)g.activate(n);else if(!id)g.activate(g.defaultIndex);}
  if(target){let p=target;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}if(scroll)requestAnimationFrame(()=>target.scrollIntoView({block:'start'}));}
 }
 function disclosure(element,heading,open=false){
  if(!heading)return element;
  const d=node('details','ref-disclosure'),s=node('summary');d.open=open;
  if(heading.hasAttribute('data-ref-ui'))generated(s);
  if(element.id){d.id=element.id;element.removeAttribute('id');}
  if(heading.id){s.id=heading.id;heading.removeAttribute('id');}
  const label=node('span','ref-summary-text');while(heading.firstChild)label.append(heading.firstChild);label.querySelectorAll('br').forEach(b=>b.replaceWith(document.createTextNode(' ')));s.append(label);heading.remove();
  element.before(d);d.append(s,element);element.classList.add('ref-disclosure-body');return d;
 }
 function searchEntries(host,entries,{years=false}={}){
  if(!entries.length)return;
  const controls=generated(node('div','ref-find')),label=node('label','',ui.find),input=node('input'),clear=node('button','ref-clear',ui.clear),status=node('p','ref-result-count');
  input.type='search';input.id='ref-search-'+(++serial);input.autocomplete='off';label.htmlFor=input.id;clear.type='button';status.setAttribute('role','status');
  const row=node('div','ref-find-row');row.append(input,clear);controls.append(label,row,status);host.prepend(controls);
  let select;
  if(years){const yearLabel=node('label','ref-year',ui.year);select=node('select');select.append(new Option(ui.all,''));[...new Set(entries.map(e=>e.dataset.year).filter(Boolean))].sort().reverse().forEach(y=>select.append(new Option(y,y)));yearLabel.append(select);row.insertBefore(yearLabel,clear);}
  const empty=generated(node('p','ref-empty',ui.none));empty.hidden=true;controls.after(empty);
  const update=()=>{const q=fold(input.value.trim()),year=select?.value;let n=0;entries.forEach(e=>{e.hidden=!(fold(text(e)).includes(q)&&(!year||e.dataset.year===year));if(!e.hidden)n++;if(e.tagName==='DETAILS'&&q)e.open=!e.hidden;});host.querySelectorAll('.ref-year-group').forEach((g,i)=>{g.hidden=![...g.querySelectorAll('.ref-entry')].some(e=>!e.hidden);g.open=Boolean(q||year)||i===0;});status.textContent=n+' / '+entries.length+' '+ui.results;empty.hidden=n>0;};
  input.addEventListener('input',update);select?.addEventListener('change',update);clear.addEventListener('click',()=>{input.value='';if(select)select.value='';entries.forEach(e=>{if(e.tagName==='DETAILS')e.open=false;});update();input.focus();});update();
 }
 // Old reference lists used font tags, table cells and repeated line breaks as paragraphs.
 // Keep every inline node/link/image; replace only that presentation scaffolding.
 function entries(host){
  host.querySelectorAll('font,span:not([id]):not([lang]),o\\:p').forEach(e=>e.replaceWith(...e.childNodes));
  const fragment=document.createDocumentFragment(),result=[];let row=node('article','ref-entry'),lastBreak=false;
  const flush=()=>{for(const side of ['firstChild','lastChild']){while(row[side]&&(row[side].nodeType===3&&!row[side].textContent.trim()||row[side].nodeName==='BR'))row[side].remove();}if(text(row)||row.querySelector('img')){fragment.append(row);result.push(row);}else if(row.querySelector('a'))fragment.append(...row.childNodes);row=node('article','ref-entry');lastBreak=false;};
  const walk=e=>{
   if(e.nodeType===3){if(e.textContent.trim())lastBreak=false;row.append(e);return;}
   if(e.nodeType!==1){row.append(e);return;}
   if(e.tagName==='BR'){if(lastBreak)flush();else{row.append(e);lastBreak=true;}return;}
   if(e.tagName==='LI'){flush();row.append(...e.childNodes);flush();return;}
   if(/^(P|DIV|SECTION|ARTICLE|BLOCKQUOTE|TABLE|TBODY|TR|TD|UL|OL|LI|CENTER)$/.test(e.tagName)){flush();[...e.childNodes].forEach(walk);flush();if(e.id){const anchor=node('span');anchor.id=e.id;fragment.append(anchor);}return;}
   if(/^H[1-6]$/.test(e.tagName)){flush();fragment.append(e);return;}
   if(['SCRIPT','STYLE','LINK'].includes(e.tagName)){flush();fragment.append(e);return;}
   lastBreak=false;row.append(e);
  };
  [...host.childNodes].forEach(walk);flush();host.replaceChildren(fragment);host.classList.add('ref-entries');return result;
 }
 function rangeContents(start,end,container){const r=document.createRange();r.setStartBefore(start);end?r.setEndBefore(end):r.setEnd(container,container.childNodes.length);return r.extractContents();}
 if(source){
  if(page==='news-68'){
   const lastCurrent=source.querySelector('#wigmore-hall-2027');
   const walker=document.createTreeWalker(source,NodeFilter.SHOW_TEXT);let boundary;while(walker.nextNode()){if(/^(PAST EVENTS|VERGANGENE VERANSTALTUNGEN|ÉVÉNEMENTS PASSÉS|過去の催し)/.test(walker.currentNode.textContent.trim())){boundary=walker.currentNode;break;}}
   if(boundary){
    const r=document.createRange();r.setStartBefore(boundary);r.setEnd(source,source.childNodes.length);const old=r.extractContents();
    const latest=node('section','ref-current'),archive=node('section','ref-archive');latest.id='current-events';archive.id='event-archive';latest.append(...source.childNodes);archive.append(old);source.append(latest,archive);
    if(lastCurrent){
    const first=node('article','ref-event');const before=document.createRange();before.setStart(latest,0);before.setEndBefore(lastCurrent);first.append(before.extractContents());latest.prepend(first);lastCurrent.classList.add('ref-event');latest.append(lastCurrent);
    [...latest.children].filter(e=>e!==first&&e!==lastCurrent&&!text(e)&&!e.querySelector('a,img')).forEach(e=>e.remove());
    const context=[...first.querySelectorAll('div[style]')].find(d=>d.style.backgroundColor);if(context)disclosure(context,context.querySelector('b'));
    const eventLink=first.querySelector('a[href*="ekihd.de"]'),event=eventLink?.parentElement;
    if(event){event.classList.add('ref-event-facts');const b=event.querySelector('b');if(b){const h=node('h2','ref-event-title');h.append(...b.childNodes);b.replaceWith(h);event.prepend(h);}}
    const intro=first.querySelector('div>b');if(intro&&/FORTHCOMING|KOMMENDE|ÉVÉNEMENTS|今後/.test(text(intro)))intro.parentElement.classList.add('ref-event-kicker');
    const paras=[...lastCurrent.children];const from=paras.find(e=>e.tagName==='P'&&e.querySelector('b')&&paras.indexOf(e)>2);
    if(from){const more=node('div','ref-event-more');more.append(rangeContents(from,null,lastCurrent));lastCurrent.append(more);const h=generated(node('h3','',ui.details));more.prepend(h);disclosure(more,h);}
    }
    const oldEntries=entries(archive);let year='';oldEntries.forEach(e=>{const match=text(e).match(/(?:^|[^0-9])(20\d{2}|19\d{2})(?=[^0-9]|$)/);if(match)year=match[1];e.dataset.year=year;});
    const yearGroups=new Map();oldEntries.filter(e=>e.dataset.year).forEach(e=>{let g=yearGroups.get(e.dataset.year);if(!g){g=node('details','ref-disclosure ref-year-group');const s=generated(node('summary','',e.dataset.year));g.append(s);e.before(g);yearGroups.set(e.dataset.year,g);}g.append(e);});oldEntries.filter(e=>!e.dataset.year).forEach(e=>e.className='ref-entry-heading');
    searchEntries(archive,oldEntries.filter(e=>e.dataset.year),{years:true});tabs([latest,archive],[ui.latest,ui.archive]);
   }
  }else if(page==='publishers-25'){
   const headings=['main-publishers','uk-hire','historic-imprints'].map(id=>source.querySelector('#'+id)).filter(Boolean);
   const cards=[...source.querySelectorAll('.hgs-publisher-card')].map(card=>disclosure(card,card.querySelector('h3')));
   headings.forEach(h=>searchEntries(h,cards.filter(c=>h.contains(c))));
   // Keep the original introduction and practical guidance together, below a compact disclosure.
   const intro=[...source.querySelectorAll('.hgs-publishers-hero,.hgs-section')].filter(e=>!headings.includes(e)&&!e.id.includes('society-help'));
    if(intro.length){const guidance=group(intro,'publisher-guidance'),heading=generated(node('h2','',ui.guidance));guidance.prepend(heading);const d=disclosure(guidance,heading);headings[headings.length-1].after(d);}
   tabs(headings,[ui.publishers,ui.hire,ui.historic]);
  }else if(page==='publishers-63'){
   const cards=[...source.querySelectorAll('.record-label-card')].map(card=>disclosure(card,card.querySelector('h2')));searchEntries(source,cards);
  }else if(page.startsWith('bibliography-')||page.startsWith('booksandarticles-')){
   const purchase=source.querySelector('.book-purchases');purchase?.remove();
   const items=entries(source);const headings=items.filter(e=>{const s=text(e);return s.length<65&&!e.querySelector('i,em,a,img')&&(/[A-ZÀ-ÖØ-Þ]/.test(s)&&s===s.toUpperCase()||/^(伝記|研究出版物|研究論文)$/.test(s));});headings.forEach(e=>{e.className='ref-entry-heading';});
   const plates=items.filter(e=>!text(e)&&e.querySelector('img'));plates.forEach(e=>e.className='ref-book-plates');
   if(purchase){source.prepend(purchase);disclosure(purchase,purchase.querySelector('h2'));}
   searchEntries(source,items.filter(e=>!headings.includes(e)&&!plates.includes(e)));
  }else if(page==='faqs-80'){
   const questions=[...source.children].filter(e=>e.tagName==='STRONG'),tail=source.querySelector('h2');
   questions.forEach((heading,i)=>{const holder=node('div','ref-answer');heading.before(holder);holder.append(rangeContents(heading,questions[i+1]||tail,source));disclosure(holder,heading);});
   const items=[...source.querySelectorAll('.ref-disclosure')];searchEntries(source,items);
  }else if(page==='hansgalsociety-32'||page==='donate-79'){
   const sections=[...source.querySelectorAll('.hgs-society-page > section')];
   if(sections.length){
    const overview=sections.filter(e=>!e.id&&!e.getAttribute('aria-labelledby')?.includes('privacy')||e.classList.contains('hgs-top-card')||e.id==='hgs-funds');
    const panels=[group(overview,'society-overview')];const names=[page==='donate-79'?ui.funds:ui.overview];
    for(const [id,label] of [['hgs-donate',page==='donate-79'?ui.donate:ui.support],['hgs-giftaid',ui.gift],['hgs-contact',ui.contact]]){const s=sections.find(e=>e.id===id);if(s){panels.push(s);names.push(label);}}
    const privacy=sections.find(e=>e.getAttribute('aria-labelledby')==='hgs-privacy-title');if(privacy){privacy.id='society-privacy';panels.push(privacy);names.push(ui.privacy);}
    tabs(panels,names);
   }
  }else if(page==='news-78'){
   const headings=[...source.querySelectorAll('h2')];const panels=headings.map((h,i)=>{const p=node('section');p.id='releases-'+text(h);h.before(p);p.append(rangeContents(h,headings[i+1],source));return p;});tabs(panels,headings.map(text));
  }else if(page==='news-76'){
   // This is historical publication material, not a stream of new releases.
   source.classList.add('ref-publication-archive');
   const bold=[...source.querySelectorAll('b,strong')],starts=[/^Music Behind Barbed Wire/,/^(Piano Quartet in A|Klavierquartett in A)/,/^Hans Gál: Ein Jahrhundert Musik/,/^Vier Miniaturen/].map(pattern=>bold.find(e=>pattern.test(text(e)))).filter(Boolean);
   if(starts.length===4){const prefix=document.createRange();prefix.setStart(source,0);prefix.setEndBefore(starts[0]);const intro=prefix.extractContents();const cards=starts.map((h,i)=>{const c=node('article','ref-publication');c.append(rangeContents(h,starts[i+1],source));return {c,h};});source.replaceChildren(intro,...cards.map(r=>r.c));cards.forEach(({c,h})=>disclosure(c,h));}
   const review=source.querySelector('.reviewText');if(review){const h=generated(node('h3','',ui.details));review.prepend(h);disclosure(review,h);}
  }
 }
 const photos=[...document.querySelectorAll('.photos-page>.photo-group')];if(photos.length){photos.forEach((p,i)=>p.id='photo-category-'+(p.querySelector('[rel]')?.getAttribute('rel').replace('group','')||i));tabs(photos,photos.map(p=>text(p.querySelector('h2'))+' · '+p.querySelectorAll('.imagesItem').length));}
 const station=document.getElementById('listening-station');
 if(station){
  const hero=station.querySelector('.listening-hero'),library=station.querySelector('.listening-library');
  if(hero&&library){const browse=node('section'),discover=node('section');discover.id='discover-excerpts';browse.id='browse-excerpts';hero.before(discover);discover.append(hero);const start=discover.nextSibling;const r=document.createRange();r.setStartBefore(start);r.setEndAfter(library);browse.append(r.extractContents());discover.after(browse);tabs([discover,browse],[ui.discover,ui.browse],location.search?1:0);}
 }
 const results=document.getElementById('search-results');let searchSections=[];if(results)new MutationObserver(()=>{const sections=[...results.querySelectorAll(':scope>section')];if(sections.length&&sections.some((s,i)=>s!==searchSections[i])){searchSections=sections;document.querySelector('.ref-search-tabs')?.remove();const firstMatch=Math.max(0,sections.findIndex(s=>s.querySelector('article')));const nav=tabs(sections,sections.map(s=>text(s.querySelector('h2'))),firstMatch);if(nav){nav.classList.add('ref-search-tabs');results.before(nav);}}}).observe(results,{childList:true});
 document.addEventListener('click',e=>{const a=e.target.closest('a[href^="#"]');if(a&&!a.matches('[role=tab]'))setTimeout(()=>revealHash(true),0);});
 addEventListener('hashchange',()=>revealHash(true));addEventListener('popstate',()=>revealHash());
 revealHash(Boolean(location.hash));document.documentElement.dataset.referenceReady='true';
 let printed=[];addEventListener('beforeprint',()=>{printed=[...document.querySelectorAll('.folio-reference details:not([open])')];printed.forEach(d=>d.open=true);});addEventListener('afterprint',()=>{printed.forEach(d=>d.open=false);printed=[];});
})();
