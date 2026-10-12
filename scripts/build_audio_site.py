"""Reproduce the separate Pages media site from the unchanged public audio inventory."""
import hashlib,json,pathlib,shutil,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
out=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else (ROOT/'audio-site').resolve()
assert not out.is_relative_to((ROOT/'public').resolve())
assets=json.loads((ROOT/'config/audio-assets.json').read_text());out.mkdir(parents=True,exist_ok=True)
for a in assets:
 src=ROOT/'public'/a['path'].lstrip('/');assert hashlib.sha256(src.read_bytes()).hexdigest()==a['sha256'];dst=out/a['path'].lstrip('/');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
(out/'.nojekyll').write_text('')
(out/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><title>Hans Gál Society — audio excerpts</title><h1>Hans Gál Society</h1><p>Audio excerpts supporting the Hans Gál website.</p><p><a href="https://hansgal.org/audiosamples/">Listen on hansgal.org</a></p></html>\n')
(out/'audio-assets.json').write_text(json.dumps(assets,indent=2)+'\n')
(out/'README.md').write_text('# Hans Gál audio excerpts\n\nPublic audio excerpts used by https://hansgal.org/. Recording copyrights and credits remain on the corresponding work, recording and listening pages.\n\nGitHub Pages: main branch, repository root; `.nojekyll` serves original files directly. Asset filenames, bytes and hashes must be preserved. Publish and verify new excerpts here before referencing them from hansgal.org.\n')
print(f'Prepared {len(assets)} media files; {sum(a["bytes"] for a in assets)} audio bytes at {out}')
