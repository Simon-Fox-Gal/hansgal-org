/* Progressive enhancement: every section remains available without JavaScript. */
(() => {
  'use strict';
  const root = document.querySelector('.work-folio');
  if (!root) return;
  const nav = root.querySelector('.folio-tabs');
  const tabs = [...nav.querySelectorAll('[data-panel]')];
  const panels = tabs.map(tab => document.getElementById(tab.dataset.panel));
  const aliases = {listen:'audiosamples_content','audio-samples':'audiosamples_content',recordings:'recordings_content','downloadable-score':'music',freedownloads_content:'music',images:'images_content'};
  function activate(tab, focus=false) {
    tabs.forEach((t,i) => {
      const selected = t === tab;
      t.setAttribute('aria-selected', String(selected));
      t.tabIndex = selected ? 0 : -1;
      panels[i].hidden = !selected;
    });
    if (focus) tab.focus();
  }
  function fromLocation() {
    const hash = decodeURIComponent(location.hash.slice(1));
    const target = aliases[hash] || hash;
    const tab = tabs.find(t => t.dataset.panel === target) || (!hash && new URLSearchParams(location.search).has('sample') ? tabs.find(t => t.dataset.panel === 'audiosamples_content') : null) || tabs[0];
    activate(tab);
    if (hash && document.getElementById(hash) && document.getElementById(hash).closest('.folio-panel')) {
      requestAnimationFrame(() => document.getElementById(hash).scrollIntoView({block:'start'}));
    }
  }
  nav.setAttribute('role','tablist');
  tabs.forEach((tab,i) => {
    tab.setAttribute('role','tab');
    tab.setAttribute('aria-controls',panels[i].id);
    panels[i].setAttribute('role','tabpanel');
    panels[i].setAttribute('aria-labelledby',tab.id);
    panels[i].tabIndex=0;
    tab.addEventListener('click', e => {
      if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      activate(tab);
      history.pushState(null,'',tab.getAttribute('href'));
    });
    tab.addEventListener('keydown', e => {
      let n=i;
      if(e.key==='ArrowRight') n=(i+1)%tabs.length;
      else if(e.key==='ArrowLeft') n=(i+tabs.length-1)%tabs.length;
      else if(e.key==='Home') n=0;
      else if(e.key==='End') n=tabs.length-1;
      else return;
      e.preventDefault();activate(tabs[n],true);
      history.replaceState(null,'',tabs[n].getAttribute('href'));
    });
  });
  root.classList.add('folio-enhanced');
  fromLocation();
  addEventListener('hashchange',fromLocation);
  addEventListener('popstate',fromLocation);
  const player=document.getElementById('listening-now');
  if(!player) return;
  const credit=document.getElementById('now-credit');
  const toggle=document.getElementById('folio-credits');
  const size=()=>document.body.style.setProperty('--folio-player-height',player.hidden?'0px':Math.ceil(player.getBoundingClientRect().height)+'px');
  new ResizeObserver(size).observe(player);
  new MutationObserver(size).observe(player,{attributes:true,attributeFilter:['hidden','class']});
  toggle.addEventListener('click',()=>{
    const open=player.classList.toggle('credits-open');
    toggle.setAttribute('aria-expanded',String(open));
    toggle.textContent=open?toggle.dataset.closeLabel:toggle.dataset.openLabel;
  });
  new MutationObserver(()=>{
    player.classList.remove('credits-open');
    toggle.setAttribute('aria-expanded','false');
    toggle.textContent=toggle.dataset.openLabel;
    toggle.hidden=!credit.textContent.trim();
  }).observe(credit,{childList:true,subtree:true,characterData:true});
  size();
})();
