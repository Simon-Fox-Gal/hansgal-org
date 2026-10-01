"""Verify the review build without needing the private archive."""
import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf8'))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
provenance=read('docs/content-fingerprints.json')
for table,expected in provenance.items():
    records=read('content/'+table+'.json')
    assert len(records)==expected['count'],table+' row count changed'
    assert digest(records)==expected['sha256'],table+' source content changed'
    ids=[r['id'] for r in records if 'id' in r]
    assert len(ids)==len(set(ids)),table+' has duplicate IDs'
assets=read('content/asset-manifest.json')
assert len({r['path'] for r in assets})==len(assets),'duplicate asset paths'
for a in assets:
    p=ROOT/'public'/a['path'].lstrip('/')
    assert p.is_file(),a['path']+' missing'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],a['path']+' changed'
build=read('docs/build-report.json')
assert not build['missing_captured_paths'],'legacy routes missing'
assert len({r['path'] for r in build['routes']})==len(build['routes']),'duplicate routes'
for r in build['routes']:
    assert (ROOT/'dist'/r['file']).is_file(),r['path']+' missing'
for table,pattern in [('catalogue','/works/show/{}'),('recording','/recordings/{}')]:
    for r in read('content/'+table+'.json'):
        assert (ROOT/'dist'/pattern.format(r['id']).lstrip('/')/'index.html').is_file()
for r in read('content/menu.json'):
    assert (ROOT/'dist'/r['mainmenu']/r['id']/'index.html').is_file()
audio=read('content/audio_sample.json');audio_files=[]
for row in audio:
    for item in row['filename'].split('|'):
        filename=item.split('#',1)[1];audio_files.append(filename)
        assert (ROOT/'dist/storage/audiosamples'/filename).is_file(),filename
assert len(audio_files)==230
for p in (ROOT/'dist').rglob('*'):
    assert p.suffix.lower() not in ('.php','.sql','.log','.env'),str(p)+' must not be public'
runtime=read('dist/app/site-data.json')
assert not {'comments','temp','cctemp'}&set(runtime),'private/working tables published'
assert build['total_bytes']<1_000_000_000,'Pages size limit exceeded'
print(f'PASS: {len(provenance)} content tables, {len(assets)} original assets, {len(build["routes"])} routes, 230 audio references. No omitted or duplicated approved records, changed source fields, or changed original asset bytes.')
