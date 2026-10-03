"""Independent integrity checks for the bilingual catalogue and score delivery."""
import hashlib, io, json, pathlib, re, subprocess, zipfile
from editorial_updates import approved
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]
BASELINE='af4fa61b3e29f82fd19256fb56cce9528c5c8987'
def load(path):return json.loads((ROOT/path).read_text(encoding='utf8'))

# The original editorial values remain intact. Existing German display fields
# were explicitly authorized for completion; no other old field may change.
paths=subprocess.check_output(['git','ls-tree','--name-only',BASELINE,'content/'],cwd=ROOT,text=True).splitlines()
original_count=0
for path in paths:
    if not path.endswith('.json') or path.endswith('asset-manifest.json'):continue
    old=json.loads(subprocess.check_output(['git','show',BASELINE+':'+path],cwd=ROOT))
    new=load(path)
    if not isinstance(old,list) or not old or not isinstance(old[0],dict):
        assert old==new,path
        continue
    assert len(new)>=len(old),f'{path}: original rows omitted'
    # New editorial records may be appended; original row order and values
    # remain checked below. Reject reused IDs and repeated new relations.
    if 'id' in old[0]:
        assert len({r['id'] for r in new})==len(new),f'{path}: duplicate ID'
    else:
        seen={json.dumps(r,sort_keys=True) for r in new[:len(old)]}
        for row in new[len(old):]:
            key=json.dumps(row,sort_keys=True)
            assert key not in seen,f'{path}: duplicate appended relation'
            seen.add(key)
    # Visual CMS ordering may reorder whole arrays or renumber rank fields.
    # Match by stable ID for those arrays; keep every non-order field checked.
    if path in ('content/faqs.json','content/photos_category.json'):
        current_by_id={r['id']:r for r in new}
        pairs=[(r,current_by_id[r['id']]) for r in old]
    else:
        pairs=zip(old,new)
    for before,after in pairs:
        for key,value in before.items():
            if (path in ('content/recording.json','content/audio_sample.json') and key=='sequence') or (path=='content/photos.json' and key=='sorrend'):
                assert str(after[key]).isdigit(),f'{path}: invalid display order'
                continue
            if path=='content/catalogue.json' and key in ('title_de','description_de'):continue
            if approved(path,before.get('id'),key,after[key]):continue
            assert after[key]==value,f'{path} {before.get("id")} {key}: unintended alteration'
        original_count+=1

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.lang=None;self.links=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html' and self.lang is None:self.lang=a.get('lang')
        if tag=='a':self.links.append(a)

report=load('docs/build-report.json');base=report['base_path'];routes={r['path']:r for r in report['routes']}
for path,row in routes.items():
    if path.startswith('/de') or 'redirect' in row or row['template'] in ('audio-player','recordings_content'):continue
    counterpart='/de'+path
    assert counterpart in routes,('missing German route',path)
    for lang,target in [('en',path),('de',counterpart)]:
        page=Page((ROOT/'dist'/routes[target]['file']).read_text(encoding='utf8'))
        assert page.lang==lang,(target,page.lang)
        switches={a['data-language']:a['href'] for a in page.links if 'data-language' in a}
        assert switches=={'en':base+path,'de':base+'/de'+path},target

manifest={r['path']:r for r in load('content/asset-manifest.json')}
available=[]
for row in load('content/catalogue.json'):
    assert row['title_de'],('missing work title',row['id'])
    if row['score_available']!='yes':continue
    available.append(row['id'])
    path=row['score_file'];assert re.fullmatch(r'/storage/scores/[^/]+\.pdf',path)
    data=(ROOT/'public'/path.lstrip('/')).read_bytes()
    assert data.startswith(b'%PDF-')
    record=manifest.get(path) or manifest.get(path.lstrip('/'))
    assert record and record['sha256']==hashlib.sha256(data).hexdigest()
    amount=row.get('score_suggested_donation')
    if amount not in (None,''):
        assert re.fullmatch(r'\d+(\.\d{1,2})?',amount),('invalid suggestion',row['id'])

recording_ids={x['id'] for x in load('content/recording.json')}
audio_ids={x['id'] for x in load('content/audio_sample.json')}
catalogue_ids={x['id'] for x in load('content/catalogue.json')}
recording_works={r['catalogue_id'] for r in load('content/catalogue_recordings.json') if r['catalogue_id'] in catalogue_ids and r['recording_id'] in recording_ids}
audio_works={r['catalogue_id'] for r in load('content/catalogue_audio_sample.json') if r['catalogue_id'] in catalogue_ids and r['audio_sample_id'] in audio_ids}
for prefix,labels in [('', ('Downloadable score available','Recordings available','Audio samples available')), ('de/', ('Noten zum Herunterladen verfügbar','Aufnahmen verfügbar','Hörproben verfügbar'))]:
    markup=(ROOT/'dist'/prefix/'works/index.html').read_text(encoding='utf8')
    assert markup.count('availability-mark availability-score')==len(available),(prefix,'score indicators')
    assert markup.count('availability-mark availability-recording')==len(recording_works),(prefix,'recording indicators')
    assert markup.count('availability-mark availability-audio')==len(audio_works),(prefix,'audio indicators')
    for work_id in available:
        target=base+('/de' if prefix else '')+f'/works/show/{work_id}/#downloadable-score'
        assert f'href="{target}"' in markup,(prefix,work_id,'score indicator target')
        assert f'aria-label="{labels[0]}"' in markup,(prefix,work_id,'score indicator label')
    for work_id,label,fragment in [(x,labels[1],'recordings') for x in recording_works]+[(x,labels[2],'audio-samples') for x in audio_works]:
        target=base+('/de' if prefix else '')+f'/works/show/{work_id}/#{fragment}'
        assert f'href="{target}"' in markup,(prefix,work_id,fragment,'indicator target')
        assert f'aria-label="{label}"' in markup,(prefix,work_id,fragment,'indicator label')

# Exercise the actual browser ZIP implementation, then decode with Python's
# independent standard-library reader (names, CRCs and exact bytes).
script="""const zip=require('./app/score-zip.js');
(async()=>{const b=zip([{name:'Gál-1.pdf',bytes:new Uint8Array([37,80,68,70,0,255,17])},{name:'second.pdf',bytes:new TextEncoder().encode('second score')}]);process.stdout.write(Buffer.from(await b.arrayBuffer()).toString('base64'));})();"""
import base64
archive=base64.b64decode(subprocess.check_output(['node','-e',script],cwd=ROOT))
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    assert z.namelist()==['Gál-1.pdf','second.pdf']
    assert z.testzip() is None
    assert z.read('Gál-1.pdf')==bytes([37,80,68,70,0,255,17])
    assert z.read('second.pdf')==b'second score'
print(f'PASS: {original_count} original rows preserved; bilingual route pairs; score integrity {available}; two-file ZIP integrity.')
