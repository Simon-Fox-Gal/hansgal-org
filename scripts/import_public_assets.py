"""One-time public-media import, checked against the private archive's hashes.

Routine builds use committed public files and do not contact the old site.
"""
import concurrent.futures,hashlib,json,pathlib,time,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'content/asset-manifest.json').read_text(encoding='utf8'))
def import_one(row):
    path=ROOT/'public'/row['path'].lstrip('/')
    if not path.resolve().is_relative_to((ROOT/'public').resolve()):raise ValueError('Unsafe path')
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']:return None
    source='https://hansgal.org/'+urllib.parse.quote_from_bytes(row['source_path'].encode('utf8','surrogateescape'),safe='/')
    error=''
    for attempt in range(3):
        try:
            req=urllib.request.Request(source,headers={'User-Agent':'HansGalSociety-Migration/1.0'})
            with urllib.request.urlopen(req,timeout=60) as response:data=response.read()
            assert len(data)==row['bytes'],'size differs from archive'
            assert hashlib.sha256(data).hexdigest()==row['sha256'],'SHA-256 differs from archive'
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            return None
        except Exception as e:error=str(e);time.sleep(attempt+1)
    return {'path':row['path'],'error':error}
if __name__=='__main__':
    failures=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for index,result in enumerate(pool.map(import_one,manifest),1):
            if result:failures.append(result)
            if index%100==0:print(f'Checked {index}/{len(manifest)} public files',flush=True)
    if failures:
        print(json.dumps(failures,indent=2,ensure_ascii=True));raise SystemExit('Public asset import did not pass; no unverified files should be committed.')
    print(f'PASS: all {len(manifest)} public files match the preservation archive.')
