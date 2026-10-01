"""Validate editable content; --preservation additionally proves original content equality."""
import argparse,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf8'))
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()
args=argparse.ArgumentParser()
args.add_argument('--preservation',action='store_true')
preserve=args.parse_args().preservation
provenance=read('docs/content-fingerprints.json')
baseline=read('docs/content-baseline.json')
tables={t:read('content/'+t+'.json') for t in provenance}
for table,records in tables.items():
 assert isinstance(records,list),table+' must be a list'
 ids=[r['id'] for r in records if 'id' in r]
 assert len(ids)==len(set(ids)),table+' has duplicate IDs'
 assert all(isinstance(v,(str,type(None))) for r in records for v in r.values()),table+' has a non-text field'
 assert set(baseline['ids'][table])<=set(ids),table+' lost a preserved record ID; retain its URL or explicitly review a redirect'
 if preserve:
  assert len(records)==provenance[table]['count'],table+' row count changed'
  assert digest(records)==provenance[table]['sha256'],table+' source content changed'
for table,field,parent in baseline['relationships']:
 for row in tables[table]:
  value=row.get(field)
  if value and value not in {r['id'] for r in tables[parent]}:
   assert [table,row.get('id'),field,value] in baseline['existing_orphans'],'New missing relationship: '+str([table,row.get('id'),field,value])
assert all(r['id']!='82' for r in tables['menu']),'Private preview must remain excluded'
assets=read('content/asset-manifest.json')
assert len({r['path'] for r in assets})==len(assets),'duplicate asset paths'
for a in assets:
 p=(ROOT/'public'/a['path'].lstrip('/')).resolve()
 assert p.is_relative_to((ROOT/'public').resolve()),'asset path escapes public'
 assert p.is_file(),a['path']+' missing'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],a['path']+' hash mismatch'
build=read('docs/build-report.json')
assert not build['missing_captured_paths'],'legacy routes missing'
assert len({r['path'] for r in build['routes']})==len(build['routes']),'duplicate routes'
for r in build['routes']:
 assert (ROOT/'dist'/r['file']).is_file(),r['path']+' missing'
for table,pattern in [('catalogue','/works/show/{}'),('recording','/recordings/{}')]:
 for r in tables[table]:assert (ROOT/'dist'/pattern.format(r['id']).lstrip('/')/'index.html').is_file()
for r in tables['menu']:assert (ROOT/'dist'/r['mainmenu']/r['id']/'index.html').is_file()
audio_files=[]
for row in tables['audio_sample']:
 for item in row['filename'].split('|'):
  assert '#' in item,'Malformed audio sample'
  filename=item.split('#',1)[1];audio_files.append(filename)
  assert (ROOT/'dist/storage/audiosamples'/filename).is_file(),filename
if preserve:assert len(audio_files)==230
for p in (ROOT/'dist').rglob('*'):
 assert p.suffix.lower() not in ('.php','.sql','.log','.env'),str(p)+' must not be public'
runtime=read('dist/app/site-data.json')
assert not {'comments','temp','cctemp'}&set(runtime),'private/working tables published'
assert not (ROOT/'dist/hansgalsociety/82').exists(),'Excluded private page published'
assert not (ROOT/'dist/ente_private_audio').exists(),'Excluded private audio published'
assert build['total_bytes']<1_000_000_000,'Pages size limit exceeded'
mode='original content unchanged' if preserve else 'editable content and preserved routes validated'
print(f'PASS: {len(provenance)} tables, {len(assets)} assets, {len(build["routes"])} routes, {len(audio_files)} audio references; {mode}. No duplicate IDs or new broken relationships.')

