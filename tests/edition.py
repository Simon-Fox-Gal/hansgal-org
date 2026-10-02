"""Verify the redesign preserves authored content, routes and both languages."""
import json,pathlib,re,sys,subprocess
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n import localize
from build import stripcslashes
class Text(HTMLParser):
 def __init__(self,source):
  super().__init__(convert_charrefs=True);self.parts=[];self.skip=0;self.feed(source)
 def handle_starttag(self,tag,attrs):
  if tag in ('head','script','style'):self.skip+=1
  if tag in ('p','div','br','li','td','tr','h1','h2','h3'):self.parts.append(' ')
 def handle_endtag(self,tag):
  if tag in ('head','script','style'):self.skip=max(0,self.skip-1)
  if tag in ('p','div','li','td','tr','h1','h2','h3'):self.parts.append(' ')
 def handle_data(self,data):
  if not self.skip:self.parts.append(data)
def plain(s):return re.sub(r'\s+',' ',''.join(Text(stripcslashes(s or '')).parts)).strip()
tables={name:json.loads((ROOT/'content'/f'{name}.json').read_text(encoding='utf8')) for name in ['menu','recording','catalogue']}
checked=0
for lang,prefix in [('en',''),('de','de/')]:
 data=localize(tables) if lang=='de' else tables
 for table,fields in [('menu',['body']),('recording',['detail','review']),('catalogue',['movements','orchestration','availability','first_performance','other_performances','further_details','other_versions'])]:
  for row in data[table]:
   route=(row['mainmenu']+'/'+row['id']) if table=='menu' else ('recordings/' if table=='recording' else 'works/show/')+row['id']
   markup=(ROOT/'dist'/prefix/route/'index.html').read_text(encoding='utf8');rendered=plain(markup)
   assert 'app/edition.css' in markup,(lang,route,'missing design')
   assert 'id="main-content"' in markup and 'id="site-navigation"' in markup
   assert 'name="viewport"' in markup
   for field in fields:
    source=plain(row.get(field))
    assert not source or source in rendered,(lang,route,field,'authored text omitted')
    checked+=1
logo=ROOT/'public/gfx/images/hansgal-logo-website.png'
original=subprocess.check_output(['git','show','a97f4436f213652afe4486c32b0659fd4ca9483f:public/gfx/images/hansgal-logo-website.png'],cwd=ROOT)
assert logo.read_bytes()==original,'Logo changed'
if '--unchanged-content' in sys.argv:
 changed=subprocess.check_output(['git','diff','a97f4436f213652afe4486c32b0659fd4ca9483f','--name-only','--','content','public'],cwd=ROOT,text=True)
 assert not changed.strip(),'Authored content or preserved assets changed'
print(f'PASS: {checked} authored fields present in English/German rendered pages; common design, navigation and viewport; original logo preserved. Requested source comparison passed.')
