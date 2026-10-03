"""Check every embedded player against catalogue relationships, not list ranks."""
import json,pathlib,re,subprocess,html
ROOT=pathlib.Path(__file__).resolve().parents[1]
def load(n):return json.loads((ROOT/'content'/f'{n}.json').read_text(encoding='utf8'))
audio={r['id']:r for r in load('audio_sample')};credits={c['filename']:c for c in load('audio_credit')}
def files(r):return [s.split('#',1)[1] for s in r['filename'].split('|')]
checked=0
for prefix in ('','de/'):
 for kind,table,key,rel_table in [('works/show','catalogue','catalogue_id','catalogue_audio_sample'),('recordings','recording','recording_id','recording_audio_sample')]:
  for row in load(table):
   expected=[]
   for rel in load(rel_table):
    if rel[key]!=row['id'] or rel['audio_sample_id'] not in audio:continue
    expected.extend(f for f in files(audio[rel['audio_sample_id']]) if kind!='recordings' or not credits.get(f) or credits[f]['recording_id']==row['id'])
   page=(ROOT/'dist'/prefix/kind/row['id']/'index.html').read_text(encoding='utf8')
   links=re.findall(r'<a class="listening-track"[^>]+>',page)
   actual=[html.unescape(re.search(r'data-sample="([^"]+)"',link)[1]) for link in links]
   assert actual==expected,(prefix,kind,row['id'],'wrong track mapping')
   if not expected:continue
   embedded=json.loads(re.search(r'<script type="application/json" id="audio-page-data">(.*?)</script>',page,re.S)[1])
   assert [f['filename'] for r in embedded for f in r['files']]==expected
   assert page.count('id="listening-player"')==1
   for link,fn in zip(links,expected):assert re.search(r'href="([^"]+)"',link)[1].endswith('/storage/audiosamples/'+fn)
   checked+=len(expected)
 # Each listening card shares precisely the same files and credits.
 page=(ROOT/'dist'/prefix/'audiosamples/index.html').read_text(encoding='utf8')
 embedded=json.loads(re.search(r'<script type="application/json" id="audio-page-data">(.*?)</script>',page,re.S)[1])
 assert {r['id']: [f['filename'] for f in r['files']] for r in embedded}=={id:files(r) for id,r in audio.items()}
 for r in embedded:
  for f in r['files']:assert f['credit']==credits.get(f['filename'],{})
# Preserve all earlier selections except the explicitly replaced Op.33 songs 1–2.
base=json.loads(subprocess.check_output(['git','show','b3f3504:content/audio_sample.json'],cwd=ROOT))
assert [r for r in load('audio_sample') if r['id']!='24']==[r for r in base if r['id']!='24']
old33=next(r for r in base if r['id']=='24');new33=audio['24']
assert new33['filename'].split('|')[2:]==old33['filename'].split('|')[2:]
assert {k:v for k,v in new33.items() if k not in ('filename','track_titles','track_titles_de')}=={k:v for k,v in old33.items() if k not in ('filename','track_titles','track_titles_de')}
changes=subprocess.check_output(['git','diff','b3f3504','--name-status','--','public/storage/audiosamples'],cwd=ROOT).decode().splitlines()
allowed={f'A\tpublic/storage/audiosamples/gal-bis2543-cd1-t{n}.mp3' for n in (27,28)}
assert set(changes)<=allowed
print(f'PASS: {checked} work/album track links in both languages match source relationships and embedded playlists; no index-based navigation; only the authorized Op.33 replacements.')
