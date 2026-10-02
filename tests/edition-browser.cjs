/* Optional browser regression: NODE_PATH must resolve Playwright. No external writes. */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'msedge'});
 const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 const base=process.env.SITE_BASE||'http://127.0.0.1:5185/hansgal-org';
 async function go(route){await page.goto(base+route);await page.waitForFunction(()=>document.documentElement.dataset.hansgalReady==='true');}
 await go('/');await page.getByRole('button',{name:'Menu',exact:true}).click();assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'true');await page.keyboard.press('Escape');assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'false');
 await go('/works/');await page.locator('input[name=title]').fill('piano');await page.getByRole('button',{name:'Find works',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.catalogue-results').dataset.resultCount);
 const count=Number(await page.locator('.catalogue-results').getAttribute('data-result-count'));assert(count>0&&count<179);
 await page.locator('[data-sort=title][data-direction=DESC]').click();await page.waitForFunction(()=>new URLSearchParams(location.search).get('orderby')==='DESC');assert.equal(await page.locator('.catalogue-results').getAttribute('data-result-count'),String(count));assert.equal(await page.locator('input[name=title]').inputValue(),'piano');assert.equal(await page.locator('thead th').count(),5);assert.equal(await page.locator('tbody tr').count(),count);
 await page.locator('[data-language=de]').click();await page.waitForFunction(()=>document.documentElement.dataset.hansgalReady==='true');assert.equal(await page.locator('input[name=title]').inputValue(),'piano');assert.equal(new URL(page.url()).searchParams.get('orderby'),'DESC');
 await page.locator('#reset-catalogue').click();await page.waitForFunction(()=>document.querySelector('.catalogue-results').dataset.resultCount==='179');
 await go('/recordings/');await page.locator('#recording-search').fill('Eisnacht');assert.equal(await page.locator('.albumlist .item:visible').count(),1);await page.locator('#recording-view-toggle').click();assert(await page.locator('.recording-browser').evaluate(e=>e.classList.contains('flow-view')));await page.locator('.albumlist .item:visible').click();await page.waitForFunction(()=>document.documentElement.dataset.hansgalReady==='true');assert.equal(await page.locator('#webshop').getAttribute('data-recording-id'),'98');
 await page.locator('.album-art').click();assert(await page.locator('dialog').isVisible());await page.keyboard.press('Escape');assert(!await page.locator('dialog').isVisible());
 await go('/hansgal/55/');assert(!await page.locator('.chapter-nav details').evaluate(e=>e.open));await page.locator('.chapter-nav summary').click();assert(await page.locator('.chapter-nav nav').isVisible());
 await go('/works/show/149/');await page.locator('[data-add-score="149"]').click();assert.match(await page.locator('#score-added-status').textContent(),/Added/);await go('/score-basket/');await page.waitForFunction(()=>document.getElementById('score-basket').textContent.includes('Three Vocal Quartets'));assert.match(await page.locator('#score-basket').textContent(),/10/);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:/Download selected scores/i}).click();const pdf=await download;assert(pdf.suggestedFilename().endsWith('.pdf'));assert.equal(await pdf.failure(),null);
 await go('/audiosamples/');await page.locator('[name=chosenwork]').selectOption({index:1});await page.waitForSelector('#audio-selection audio');assert.match(await page.locator('#audio-selection audio').getAttribute('src'),/storage\/audiosamples/);
 await go('/search?keyword=piano');assert((await page.locator('#search-results a').count())>0);
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS: mobile navigation; filter/sort/language state; all-work reset; recording search/view/navigation; image dialog; chapter navigation; £10 basket and free PDF download; audio selection; site search. No browser errors.');
})().catch(e=>{console.error(e);process.exit(1)});
