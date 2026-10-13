"""Folio contracts across every work/language, including sparse catalogue entries."""
import json
import html
from pathlib import Path
import re
import sys
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from folio import present, folio_duration, folio_title
from i18n import localize
from build import stripcslashes

class Page(HTMLParser):
    def __init__(self,markup):
        super().__init__();self.tags=[];self.feed(markup)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
    def matches(self,cls):return [a for _,a in self.tags if cls in a.get('class','').split()]

for value in (None,'',' ','0',0,'<p>&nbsp;<br></p>'):
    assert not present(value),value
for value in ('1931–32','full evening','<img src="a.jpg">','Op. 0'):
    assert present(value),value
assert folio_duration(None)==folio_duration('0')==''
assert folio_duration('47')=='47′'
assert folio_duration("47'")=="47'"
assert folio_title('Die Heilige Ente［聖なるあひる］','Die Heilige Ente')=='Die Heilige Ente<span class="folio-translation">［聖なるあひる］</span>'
assert folio_title('Sinfonie Nr. 2 F-Dur','Symphony No. 2 (F major)')=='Sinfonie Nr. 2 F-Dur'
assert folio_title('A work (in F major)','')=='A work (in F major)'

tables={p.stem:json.loads(p.read_text(encoding='utf8')) for p in (ROOT/'content').glob('*.json') if p.stem in ['catalogue','catalogue_recordings','catalogue_audio_sample','audio_sample','catalogue_image','page_text']}
total=0
for lang in ('en','de','fr','ja'):
    data=localize(tables,lang) if lang!='en' else tables
    audio={r['id']:r for r in data['audio_sample']}
    for w in data['catalogue']:
        route=ROOT/'dist'/('' if lang=='en' else lang)/'works/show'/w['id']/'index.html'
        text=route.read_text(encoding='utf8');page=Page(text)
        assert len(page.matches('work-folio'))==1,(lang,w['id'])
        for field,cls in [('opus_no','folio-opus'),('year_of_composition','folio-date'),('duration','folio-duration')]:
            assert len(page.matches(cls))==int(present(w[field])),(lang,w['id'],field)
        tabs=[a for _,a in page.tags if 'data-panel' in a]
        panels=page.matches('folio-panel')
        assert len(tabs)==len(panels)
        assert {a['data-panel'] for a in tabs}=={a['id'] for a in panels}
        assert all('hidden' not in a for a in panels),'Progressive HTML must expose all content without JS'
        ids=[a['id'] for _,a in page.tags if 'id' in a]
        # Old recording HTML includes repeated pasted-mail LPMetadata IDs.
        # Preserve authored markup; require uniqueness for all template-owned controls.
        owned={'top','wrapper','main-content','site-navigation','site-search','player','copyright','listening-now','listening-player','audio-page-data','downloadable-score','score-added-status','freedownloads_content'}
        owned.update(a['id'] for a in tabs+panels)
        owned.update(x for x in ids if x.startswith(('now-','folio-')))
        assert all(ids.count(x)==1 for x in owned if x in ids),(lang,w['id'],'duplicate control IDs')
        relationships=[r for r in tables['catalogue_audio_sample'] if r['catalogue_id']==w['id']]
        files=[]
        for rel in relationships:
            files.extend(s.split('#',1)[1] for s in audio[rel['audio_sample_id']]['filename'].split('|') if '#' in s)
        links=page.matches('listening-track')
        assert [a['data-sample'] for a in links]==files,(lang,w['id'],'audio changed or duplicated')
        first=page.matches('folio-play')
        assert len(first)==bool(files)
        if files:assert first[0]['data-sample']==files[0]
        else:assert 'no-first-listen' in text and not page.matches('folio-first')
        recs=[r for r in tables['catalogue_recordings'] if r['catalogue_id']==w['id']]
        assert len(page.matches('folio-record'))==len(recs),(lang,w['id'],'recording omitted or duplicated')
        assert len(page.matches('folio-facts'))<=1
        # Publication facts are intentionally repeated beside the actual offers.
        music=text.split('<section id="music"',1)[1].split('</dl>',1)[0]
        for field in ('publisher','availability'):
            if present(w.get(field)):
                clean=lambda s:re.sub(r'\s+','',html.unescape(re.sub(r'<[^>]*>','',s)))
                assert clean(stripcslashes(w[field])) in clean(music),(lang,w['id'],field,'publication information absent from Scores & texts')
        assert 'work-folio.css' in text and 'work-folio.js' in text
        total+=1
    labels=[r for r in tables['page_text'] if 144<=int(r['id'])<=168]
    assert len(labels)==25 and all(r['value'+('' if lang=='en' else '_'+lang)] for r in labels)
print(f'PASS: {total} Folio pages; conditional opus/date/duration, populated panels, stable audio identity, recording counts, unique IDs, progressive HTML and four-language labels.')
