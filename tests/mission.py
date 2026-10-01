"""Independent integrity checks for the bilingual catalogue and score delivery."""
import hashlib, io, json, pathlib, re, subprocess, zipfile
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
    for before,after in zip(old,new):
        for key,value in before.items():
            if path=='content/catalogue.json' and key in ('title_de','description_de'):continue
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
