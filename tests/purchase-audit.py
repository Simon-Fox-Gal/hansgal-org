"""Require complete audit coverage and render every reviewed purchase destination."""
import json,pathlib,html,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit
root=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads((root/path).read_text(encoding='utf8'))
audit=read('docs/purchase-audit.json')
sys.path.insert(0,str(root/'scripts'))
from score_links import OFFERS,score_link_label
from languages import text as translated_text
class Anchors(HTMLParser):
 def __init__(self,source):super().__init__();self.links=[];self.feed(source)
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.links.append(dict(attrs))
total=0
for table,section,route,fields in [('catalogue','works','works/show',('purchase_url','hire_url','score_purchase_download_url')),('recording','recordings','recordings',('cd_url','download_url','listen_url'))]:
 rows=read('content/'+table+'.json');items=audit[section]
 assert len(items)==len(rows) and len({x['id'] for x in items})==len(items)
 assert {x['id'] for x in items}=={r['id'] for r in rows}
 byid={x['id']:x for x in items}
 for r in rows:
  item=byid[r['id']]
  assert item['status'] in ('verified','partially_verified','not_found'),item
  assert item.get('note') and item.get('checked_date'),item
  for field in fields:
   for url in r.get(field,'').splitlines():
    if not url:continue
    assert url.startswith(('https://','http://')),url
    assert url in item['sources'],(r['id'],url,'missing audit evidence')
    for language in ('','de/','fr/','ja/'):
     page=(root/'dist'/language/route/r['id']/'index.html').read_text(encoding='utf8')
     assert 'href="'+html.escape(url,quote=True)+'"' in page,(r['id'],language,url)
    total+=1
sales=read('docs/sales-link-audit-2026-10-05.json')
works=read('content/catalogue.json')
assert len(sales['entries'])==99
assert len({(i['work_id'],i['field'],i['original_url']) for i in sales['entries']})==99
used={u for r in works for f in ('purchase_url','score_purchase_download_url') for u in r.get(f,'').splitlines()}
assert set(OFFERS)<=used,'Stale offer metadata'
for r in works:
 for language in ('en','de','fr','ja'):
  folder='' if language=='en' else language
  source=(root/'dist'/folder/'works/show'/r['id']/'index.html').read_text(encoding='utf8')
  links=Anchors(source).links
  for a in links:
   host=urlsplit(a.get('href','')).hostname
   if host and host not in ('hansgal.org','www.hansgal.org','hansgal.com','www.hansgal.com'):
    assert a.get('target')=='_blank',(r['id'],language,a)
    assert {'noopener','noreferrer'}<=set(a.get('rel','').split()),a
  for f in ('purchase_url','score_purchase_download_url'):
   for u in r.get(f,'').splitlines():
    label=score_link_label(u,f,lambda en,de:translated_text(language,en,de,strict=True))
    assert html.escape(label) in source,(r['id'],language,label)
 if r['id'] in sales['changed_work_ids']:
  regions={OFFERS.get(u,{}).get('region') for f in ('purchase_url','score_purchase_download_url') for u in r.get(f,'').splitlines()}
  assert {'UK','EU'}<=regions,(r['id'],regions)
print(f'PASS: all {len(audit["works"])} works and {len(audit["recordings"])} recordings audited once; {total} purchase URLs render in four languages. All external work links open safely in new tabs; replacement works have UK and EU offers; information-only links are labelled accurately.')
