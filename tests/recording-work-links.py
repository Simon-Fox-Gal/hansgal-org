"""Recording repertoire and attributed excerpts must be discoverable from works."""
import json,pathlib,re
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/'content'/f'{n}.json').read_text(encoding='utf8'))
works={r['id'] for r in load('catalogue')};records={r['id'] for r in load('recording')}
relations=[(r['catalogue_id'],r['recording_id']) for r in load('catalogue_recordings')]
assert len(relations)==len(set(relations)), 'Duplicate work/recording relationships'
audit=json.loads((ROOT/'docs/recording-work-audit.json').read_text())
assert {r['recording_id'] for r in audit['recordings']}<=records
for recording in audit['recordings']:
 for work in recording['catalogue_ids']:assert (work,recording['recording_id']) in relations
audio={r['id']:r for r in load('audio_sample')};credits={r['filename']:r for r in load('audio_credit')}
for relation in load('catalogue_audio_sample'):
 for track in audio[relation['audio_sample_id']]['filename'].split('|'):
  recording=credits.get(track.split('#',1)[1],{}).get('recording_id')
  if recording:assert (relation['catalogue_id'],recording) in relations, ('Attributed recording missing from work',relation,recording)
class WorkPage(HTMLParser):
 def __init__(self,markup):super().__init__();self.depth=0;self.recordings=[];self.feed(markup)
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='div' and (self.depth or attrs.get('id')=='recordings_content'):self.depth+=1
  if self.depth and tag=='a':
   match=re.search(r'/recordings/(\d+)/$',attrs.get('href',''))
   if match:self.recordings.append(match[1])
 def handle_endtag(self,tag):
  if tag=='div' and self.depth:self.depth-=1
checked=0
for prefix in ('','de/','fr/','ja/'):
 for work in works:
  page=WorkPage((ROOT/'dist'/prefix/'works/show'/work/'index.html').read_text(encoding='utf8'))
  expected={r for w,r in relations if w==work and r in records}
  assert set(page.recordings)==expected,(prefix,work,'missing/unexpected recording card')
  assert len(page.recordings)==len(set(page.recordings)),(prefix,work,'duplicate recording card')
  checked+=len(expected)
print(f'PASS: all {len(works)} work pages in all four languages render their exact recording relationships ({checked} cards); all attributed clips link back to their albums.')
