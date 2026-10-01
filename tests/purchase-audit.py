"""Require complete audit coverage and render every reviewed purchase destination."""
import json,pathlib,html
root=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads((root/path).read_text(encoding='utf8'))
audit=read('docs/purchase-audit.json')
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
    for language in ('','de/'):
     page=(root/'dist'/language/route/r['id']/'index.html').read_text(encoding='utf8')
     assert 'href="'+html.escape(url,quote=True)+'"' in page,(r['id'],language,url)
    total+=1
print(f'PASS: all {len(audit["works"])} works and {len(audit["recordings"])} recordings audited once; every structured purchase URL has evidence and renders in both languages: {total}')
