"""Verify hosted audio, then retire only the exact migration inventory after its deadline."""
import argparse,concurrent.futures,datetime,hashlib,json,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
args=argparse.ArgumentParser();args.add_argument('--check-only',action='store_true');opt=args.parse_args()
config=json.loads((ROOT/'config/audio-hosting.json').read_text());assets=json.loads((ROOT/'config/audio-assets.json').read_text())
base=config['base_url'].rstrip('/');assert base=='https://simon-fox-gal.github.io/hansgal-audio/storage/audiosamples'
deadline=datetime.datetime.fromisoformat(config['retire_not_before'].replace('Z','+00:00'))
if not opt.check_only:assert datetime.datetime.now(datetime.timezone.utc)>=deadline,'Retirement deadline has not arrived'
for a in assets:
 p=(ROOT/'public'/a['path'].lstrip('/')).resolve();assert p.is_relative_to((ROOT/'public/storage/audiosamples').resolve())
 if p.exists():assert p.stat().st_size==a['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],'Local audio changed: '+a['path']
def verify(a):
 name=pathlib.PurePosixPath(a['path']).name
 with urllib.request.urlopen(base+'/'+urllib.parse.quote(name),timeout=90) as r:
  assert r.status==200;digest=hashlib.sha256();count=0
  while chunk:=r.read(1024*1024):digest.update(chunk);count+=len(chunk)
 assert count==a['bytes'] and digest.hexdigest()==a['sha256'],'Hosted audio mismatch: '+name
 return name
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for i,name in enumerate(pool.map(verify,assets),1):
  if i%50==0 or i==len(assets):print(f'Verified {i}/{len(assets)}',flush=True)
if opt.check_only:print('Hosted inventory verified; no local files removed.');raise SystemExit(0)
paths={a['path'] for a in assets};p=ROOT/'content/asset-manifest.json';manifest=json.loads(p.read_text());remaining=[a for a in manifest if a['path'] not in paths]
for a in assets:(ROOT/'public'/a['path'].lstrip('/')).unlink(missing_ok=True)
p.write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
print('Retired verified original copies. Run required build/tests, review the scoped diff, publish and verify before reporting completion.')
