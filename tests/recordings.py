"""All recording destinations, thumbnail identities and project-path regressions.

Run after build.py. Optional --host checks the same generated destinations online.
"""
import argparse, json, pathlib
from html.parser import HTMLParser
from urllib.request import urlopen

ROOT = pathlib.Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.links = {}; self.recording = None; self.cover = None
        self.current = None; self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id') == 'webshop': self.recording = a.get('data-recording-id')
        if tag == 'a':
            self.current = a.get('data-recording-link')
            if self.current:
                assert self.current not in self.links, 'Duplicate thumbnail destination'
                self.links[self.current] = [a.get('href'), None]
                assert 'onclick' not in a, 'Thumbnail must use native navigation'
        if tag == 'img' and self.current: self.links[self.current][1] = a.get('src')
    def handle_endtag(self, tag):
        if tag == 'a': self.current = None

def main():
    p = argparse.ArgumentParser(); p.add_argument('--host'); args = p.parse_args()
    rows = json.loads((ROOT/'content/recording.json').read_text(encoding='utf8'))
    base = json.loads((ROOT/'dist/app/runtime-config.json').read_text())['basePath']
    ids = {r['id'] for r in rows}
    for ident in [None] + sorted(ids):
        route = '/recordings/' + (ident+'/' if ident else '')
        if args.host:
            with urlopen(args.host.rstrip('/')+route, timeout=30) as response:
                text = response.read().decode('utf8')
        else: text = (ROOT/'dist'/route.strip('/')/'index.html').read_text(encoding='utf8')
        page = Page(text)
        assert page.recording == (ident or sorted(rows,key=lambda r:(int(r['sequence']),-int(r['id'])))[0]['id']), route
        assert set(page.links) == ids, route
        for r in rows:
            assert page.links[r['id']] == [base+'/recordings/'+r['id']+'/',base+'/storage/recordingcovers/'+r['cover']], (route,r['id'])
    print(f'PASS: {len(ids)} recording destinations and all {(len(ids)+1)*len(ids)} thumbnail links; base={base}; hosted={bool(args.host)}')
if __name__ == '__main__': main()
