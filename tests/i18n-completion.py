"""Check the embedded German prose and standalone documents missed by table fields."""
import json,pathlib,re,sys
from html.parser import HTMLParser
from urllib.parse import urlsplit,urljoin
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n import localize
from build import STANDALONE_GERMAN
class Links(HTMLParser):
 def __init__(self,text):super().__init__();self.images=[];self.links=[];self.lang=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang')
  if tag=='img':self.images.append(a.get('src'))
  if tag=='a':self.links.append(a)
report=json.loads((ROOT/'docs/build-report.json').read_text(encoding='utf8'));base=report['base_path']
for route in STANDALONE_GERMAN:
 source=ROOT/'public'/route.lstrip('/');original=source.read_text(encoding='utf8')
 assert source.read_bytes()==(ROOT/'dist'/route.lstrip('/')).read_bytes(),'Original asset changed'
 localized=(ROOT/'dist/de'/route.lstrip('/')).read_text(encoding='utf8');page=Links(localized)
 assert page.lang=='de'
 assert {a['data-language']:a['href'] for a in page.links if 'data-language' in a}=={'en':base+route,'de':base+'/de'+route}
 assert page.images==[base+urljoin(route,s) for s in Links(original).images]
 for src in page.images:assert (ROOT/'dist'/urlsplit(src).path.removeprefix(base).lstrip('/')).exists(),src
 if route.endswith('levetzowpoem.html'):
  assert original.split('<p><u>Ecloga',1)[1]==localized.split('<p><u>Ecloga',1)[1],'Original poem altered'
 assert 'charset=utf-8' in localized
biography=(ROOT/'dist/de/hansgal/1/index.html').read_text(encoding='utf8')
assert 'Gáls Leben in Daten' in biography and "Chronology of G" not in biography
works=json.loads((ROOT/'content/catalogue.json').read_text(encoding='utf8'))
translated=localize({'catalogue':works})['catalogue']
for before,after in zip(works,translated):
 assert re.findall(r'\d+',before.get('publisher') or '')==re.findall(r'\d+',after.get('publisher') or '')
assert any(r['publisher']=='Unveröffentlicht' for r in translated)
coverage=json.loads((ROOT/'docs/translation-coverage.json').read_text(encoding='utf8'))
assert not any(i['status']=='pending' for i in coverage['items'])
assert 'Werk auswählen' in (ROOT/'dist/de/audiosamples/index.html').read_text(encoding='utf8')
assert 'SUCHERGEBNIS' in (ROOT/'dist/de/search/index.html').read_text(encoding='utf8')
print('PASS: completed table inventory, embedded labels, sidebar captions, standalone German routes, unchanged source poem/images/assets and publisher identifiers.')
