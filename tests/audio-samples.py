"""Recording attribution, retained audio, and the October 2026 sample release."""
import collections, hashlib, html, json, pathlib, re, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='482bfcdbb1da487978ed17a73c7e95d61a6cc7c1'
def read(name):return json.loads((ROOT/'content'/f'{name}.json').read_text(encoding='utf8'))
def before(name):return json.loads(subprocess.check_output(['git','show',BASE+':content/'+name+'.json'],cwd=ROOT))
samples=read('audio_sample'); old=before('audio_sample'); credits=read('audio_credit')
by_id={r['id']:r for r in samples}; by_file={r['filename']:r for r in credits}
files=[f.split('#',1)[1] for r in samples for f in r['filename'].split('|')]
assert len(files)==len(set(files)), 'Duplicate listening excerpts'
new=[f for f in files if f.startswith('gal-')]
assert len(new)==291 and all(f in by_file for f in new)
assert len(by_file)==len(credits), 'Duplicate credit records'
for ident in ('22','84','40','88'):
 assert by_id[ident]['filename']==next(r['filename'] for r in old if r['id']==ident), 'Symphony excerpts changed'
assert {by_file[f.split('#',1)[1]]['recording_id'] for f in by_id['84']['filename'].split('|')}=={'57'}
for ident,rec in [('40','55'),('88','59')]:
 assert {by_file[f.split('#',1)[1]]['recording_id'] for f in by_id[ident]['filename'].split('|')}=={rec}
# Every old media file still exists with exactly its original bytes.
for asset in before('asset-manifest'):
 if asset['path'].startswith('/storage/audiosamples/'):
  assert hashlib.sha256((ROOT/'public'/asset['path'].lstrip('/')).read_bytes()).hexdigest()==asset['sha256']
for row in old:
 if not any(f.startswith('gal-') for f in by_id[row['id']]['filename'].split('#')[1:]) and row['id'] not in ('22','84','40','88'):
  assert {k:v for k,v in by_id[row['id']].items() if not k.endswith(('_fr','_ja'))}==row, ('Unreplaced work changed',row['id'])
op33=[f.split('#',1)[1] for f in by_id['24']['filename'].split('|')]
assert op33==[f'gal-bis2543-cd1-t{n}.mp3' for n in range(27,32)]
assert all(by_file[f]['recording_id']=='85' and by_file[f]['album']=='BIS2543' for f in op33)
book=[c for c in credits if c['album']=='TOCC0251']
assert len(book)==20 and all(c['label']=='Toccata Press · 2014' and c['link']=='/booksandarticles/67/' for c in book)
assert all('gal-tocc0251' not in by_id[i]['filename'] for i in ('76','38','46','47','51','77'))
preview=[c for c in credits if c['preview']]
assert len(preview)==33 and all(c['album']=='ENTE' and not c['recording_id'] for c in preview)
records={r['id']:r for r in read('recording')}
for c in credits:
 assert c['filename'] in files
 if c['recording_id']:
  assert c['recording_id'] in records
  assert c['cover']=='/storage/recordingcovers/'+records[c['recording_id']]['cover']
 if c['cover']:assert (ROOT/'public'/c['cover'].lstrip('/')).is_file()
 assert not re.search(r'[CDEG]:[\\/]|MASTER|Pending|Confirm|review credits|recording-details PDF',json.dumps(c,ensure_ascii=False)), 'Private preparation text in credits'
config=json.loads((ROOT/'dist/app/runtime-config.json').read_text())
assert config['audioOrder'][:len(old)]==[r['id'] for r in sorted(old,key=lambda r:(int(r['sequence']),r['opus_no']))]
for prefix in ('','de/'):
 page=(ROOT/'dist'/prefix/'audiosamples/index.html').read_text(encoding='utf8')
 assert page.count('data-track=')==len(files)
 for fn in new:assert fn in page
 for rec in records:
  page=(ROOT/'dist'/prefix/'recordings'/rec/'index.html').read_text(encoding='utf8')
  for fn in re.findall(r'data-sample="([^"]+)"',page):
   assert fn not in by_file or by_file[fn]['recording_id']==rec, ('Wrong recording on album page',rec,fn)
print('PASS: 291 unique new excerpts, all five Op.33 songs from BIS2543, 15 unchanged symphony clips, all original audio bytes, 33 unreleased previews, correct book/CD links and per-album track filtering; no private source paths.')
