"""Check the editorial features against their source data, including every PDF."""
import json,pathlib,re,sys,subprocess,html
from html.parser import HTMLParser
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import localize
from build import stripcslashes
def load(name):return json.loads((ROOT/'content'/f'{name}.json').read_text(encoding='utf8'))
class Text(HTMLParser):
 def __init__(self,s):super().__init__();self.parts=[];self.skip=0;self.feed(s)
 def handle_starttag(self,t,a):
  if t in ('head','style','script'):self.skip+=1
  if t in ('p','div','br','li','tr','td'):self.parts.append(' ')
 def handle_endtag(self,t):
  if t in ('head','style','script'):self.skip-=1
  if t in ('p','div','li','tr','td'):self.parts.append(' ')
 def handle_data(self,d):
  if not self.skip:self.parts.append(d)
def plain(s):return ''.join(Text(stripcslashes(s or '')).parts)
def compact(s):return re.sub(r'\s+','',s).replace('\xad','')
tables={name:load(name) for name in ['catalogue','recording','menu','catalogue_recordings']};checked=0
for lang in ['en','de']:
 data=localize(tables) if lang=='de' else tables;prefix='de/' if lang=='de' else ''
 for r in data['catalogue']:
  file=ROOT/'dist/storage/work-notes'/lang/(r['id']+'.pdf');pdf=PdfReader(file);text=compact(' '.join(re.sub(r'^Hans Gál · (?:Work|Werk) \d+\s*\n\d+\s*\n','',page.extract_text()) for page in pdf.pages))
  for field in ['title','description','movements','orchestration','availability','first_performance','other_performances','further_details','other_versions','publisher','free_downloads']:
   source=compact(plain(r.get(field)))
   assert not source or source in text,(lang,r['id'],field,'PDF text missing')
  recordings={row['id']:row for row in data['recording']}
  for rel in data['catalogue_recordings']:
   if rel['catalogue_id']==r['id'] and rel['recording_id'] in recordings:assert compact(plain(recordings[rel['recording_id']]['title'])) in text,(lang,r['id'],'recording')
  markup=(ROOT/'dist'/prefix/'works/show'/r['id']/'index.html').read_text(encoding='utf8')
  assert f'/storage/work-notes/{lang}/{r["id"]}.pdf' in markup
  if not r.get('year_of_composition') or r['year_of_composition']=='0':assert '(0)' not in markup
  checked+=1
 audio=(ROOT/'dist'/prefix/'audiosamples/index.html').read_text(encoding='utf8')
 assert audio.count('data-audio-id=')==75 and audio.count('data-track=')==230
 assert 'recordingcovers' not in audio
 events=next(r['body'] for r in data['menu'] if r['id']=='68');past=events.index('VERGANGENE VERANSTALTUNGEN' if lang=='de' else 'PAST EVENTS')
 assert events.index('Großer Saal')>past and events.index('Peterskirche Heidelberg')<past
 assert events.count('www.gewandhausorchester.de/veranstaltung/choere-9954/')==2
order=[r['id'] for r in sorted(tables['recording'],key=lambda r:(int(r['sequence']),-int(r['id'])))];assert order.index('98')==order.index('99')+1
assert len(list((ROOT/'dist/storage/work-notes').rglob('*.pdf')))==checked==358
# Compare all source rows with the pre-edit main. Fields outside the explicit
# requested set must be byte-for-byte equal as values, including relationships.
allowed={'menu':{'1':{'title','title_de'},'2':{'title','title_de'},'9':{'title','title_de'},'11':{'title','title_de'},'12':{'title','title_de','body','body_de'},'28':{'title'},'29':{'title'},'45':{'title'},'51':{'title'},'52':{'title'},'53':{'title'},'54':{'title'},'55':{'title'},**{id:{'body','body_de'} for id in ['22','67','68','78','80']}},'recording':{**{id:{'release_year'} for id in ['98','97','95','90','93','91','92']},'98':{'sequence','release_year'}}}
for file in (ROOT/'content').glob('*.json'):
 if file.stem=='asset-manifest':continue
 old=json.loads(subprocess.check_output(['git','show','e0114a57edad40116784d9827de775fac839f177:content/'+file.name],cwd=ROOT));new=load(file.stem)
 if file.stem not in allowed:assert old==new,file.name;continue
 assert [r['id'] for r in old]==[r['id'] for r in new]
 for before,after in zip(old,new):
  for key in before.keys()|after.keys():
   if key not in allowed[file.stem].get(before['id'],set()):assert before.get(key)==after.get(key),(file.name,before['id'],key)
print(f'PASS: {checked} PDFs contain source work details and every linked recording; all excerpts retained; event placement and recording order; no unrelated source-field changes, omitted rows or duplicate IDs.')
