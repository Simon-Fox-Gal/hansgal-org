"""Render the Hans Gál replica as static files. No database or web backend."""
from __future__ import annotations
import argparse, copy, hashlib, html, json, pathlib, re, shutil
from collections import OrderedDict
from urllib.parse import urlsplit, unquote, quote
from jinja2 import Environment, FileSystemLoader, ChainableUndefined

ROOT = pathlib.Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT/'content'/f'{name}.json').read_text(encoding='utf8'))

def stripcslashes(value):
    """PHP presentation filter used by the original site, without changing source JSON."""
    def sub(m):
        s=m[1]
        if s.startswith('x'): return chr(int(s[1:],16))
        if re.fullmatch('[0-7]{1,3}',s): return chr(int(s,8))
        return {'n':'\n','r':'\r','t':'\t','v':'\v','a':'\a','b':'\b','f':'\f'}.get(s,s)
    return re.sub(r'\\(x[0-9a-fA-F]{1,2}|[0-7]{1,3}|.)',sub,str(value or ''))

def php_truth(value):
    return bool(value) and value != '0'

def audio_row(row):
    r=copy.deepcopy(row)
    r['files']=[{'title':s.split('#',1)[0], 'filename':s.split('#',1)[1], 'fileroot':'/storage/audiosamples/'+s.split('#',1)[1].removesuffix('.mp3')} for s in r['filename'].split('|') if '#' in s]
    return r

def make_site(base_path='', review=True):
    base_path='/' + base_path.strip('/') if base_path.strip('/') else ''
    out=ROOT/'dist'
    if out.exists():
        assert out.resolve() == (ROOT/'dist').resolve() and out.resolve().is_relative_to(ROOT.resolve())
        shutil.rmtree(out)
    shutil.copytree(ROOT/'public',out)
    shutil.copytree(ROOT/'app',out/'app',dirs_exist_ok=True)
    # ImageFlow keeps its original animation. Reflections are now canvas images
    # supplied by replica.js, so the old PHP image service is unnecessary.
    flowfile=out/'imageflow/imageflow.js'
    flow=flowfile.read_text(encoding='utf8')
    flow=flow.replace("src =  '/imageflow/reflect'+version+'.php?img='+src+thisObject.reflectionGET+'&bgc=eeeeee';",'src = src; // The static renderer supplies the complete reflection image.')
    flow=re.sub(r'domReady\(function\(\)\s*\{\s*var instanceOne = new ImageFlow\(\);\s*instanceOne.init\(\{ ImageFlowID:\'coverflow\' \}\);\s*\}\);','// Initialized by replica.js after static data loads.',flow)
    flowfile.write_text(flow,encoding='utf8')
    if base_path:
        for css in out.rglob('*.css'):
            value=css.read_text(encoding='utf8')
            value=re.sub(r'(url\(\s*["\']?)(/(?!/))',lambda m:m[1]+base_path+'/',value)
            css.write_text(value,encoding='utf8')
    tables={p.stem:json.loads(p.read_text(encoding='utf8')) for p in (ROOT/'content').glob('*.json') if p.stem not in ('asset-manifest','legacy-routes','catalogue-order','catalogue-orders','accent-map')}
    by_id={k:{r.get('id'):r for r in v} for k,v in tables.items()}
    env=Environment(loader=FileSystemLoader(ROOT/'templates'),autoescape=False,undefined=ChainableUndefined,keep_trailing_newline=True,finalize=lambda v:'' if v is None else v)
    env.filters['stripcslashes']=stripcslashes
    env.globals['php_truth']=php_truth
    props={x['name']:x for x in tables['properties']}
    recordings=sorted(tables['recording'],key=lambda r:(int(r['sequence']),-int(r['id'])))
    audio=sorted(tables['audio_sample'],key=lambda r:(int(r['sequence']),r['opus_no']))
    audio=[audio_row(r) for r in audio]
    audios={r['id']:r for r in audio}
    source_assets={r['path'] for r in load('asset-manifest')}
    route_rows=load('legacy-routes')
    generated={}
    aliases={r['path']:r['redirect'] for r in route_rows if 'redirect' in r}
    aliases.update({'/biography/15-nazitakeover.html':'/hansgal/45','/works/op53.html':'/works/show/61'})

    def related(table,left,id,right,objects):
        # Missing parents are retained in source data; the old join omitted them.
        return [objects[r[right]] for r in tables[table] if r[left]==id and r[right] in objects]

    def context(route):
        section=route.split('/')[1] if route!='/' else ''
        c=dict(props,route=route,mainmenu=section,viewmode='coverlist',chosenfile='',chosenwork='',autoplay='',genre='',instrument='',keywords={},audiosamples=[],recordings=[],thumbnails=[],thumb=False,piktorgram='',title='',lead='',body='')
        for s in ['hansgal','news','works','recordings','booksandarticles','audiosamples','publishers','bibliography','photos','faq','contacts','hansgalsociety','comments','donate']:
            c['selected'+s]=' id="selected"' if section==s else ''
        return c

    # Root-relative URLs resolve both at /hansgal-org on Pages and at / on the future domain.
    local_hosts={'hansgal.org','www.hansgal.org','hansgal.com','www.hansgal.com','production.hansgal.org'}
    def url(value):
        value=html.unescape(value)
        u=urlsplit(value)
        if u.hostname in local_hosts:
            value=u.path or '/'
            if u.query: value+='?'+u.query
            if u.fragment: value+='#'+u.fragment
        if value.startswith('/') and not value.startswith('//'):
            return base_path+value
        if value.startswith(('storage/','gfx/','imageflow/')):
            return base_path+'/'+value
        return value

    def transform(markup,route):
        markup=markup.replace('/gfx/js/hansgal.js','/app/replica.js')
        # POST selection changes become browser-side state on a static host.
        markup=re.sub(r'''onchange="\$\('#(worksform|audioform|audiofile)'\)\.submit\(\)"''',lambda m:'onchange="Hansgal.submit(\''+m[1]+'\')"',markup)
        markup=re.sub(r'''\b(href|src|action|poster|data)\s*=\s*(["'])(.*?)\2''',lambda m:m[1]+'='+m[2]+html.escape(url(m[3]),quote=True)+m[2],markup,flags=re.I|re.S)
        if base_path:
            markup=re.sub(r'''(location\.href\s*=\s*["'])(/[^"']*)''',lambda m:m[1]+base_path+m[2],markup)
        robots='noindex,nofollow' if review else 'index,follow'
        markup=markup.replace('content="index,follow"','content="'+robots+'"')
        # Preserve path identity for eventual production canonical URLs.
        head='<meta name="hansgal-base" content="'+base_path+'" />\n<link rel="canonical" href="https://hansgal.org'+html.escape(route,quote=True)+'" />\n'
        markup=markup.replace('</head>',head+'</head>')
        return markup

    def save(route,markup,template='generated',fragment=False):
        assert route.startswith('/') and '..' not in pathlib.PurePosixPath(route).parts
        target=out/route.lstrip('/')/'index.html' if route!='/' else out/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        final=transform(markup,route)
        target.write_text(final,encoding='utf8')
        generated[route]={'path':route,'file':target.relative_to(out).as_posix(),'template':template,'sha256':hashlib.sha256(final.encode()).hexdigest()}

    def page(route,template,**kwargs):
        c=context(route);c.update(kwargs)
        content=env.get_template(template+'.html').render(**c)
        c['CONTENT']=content
        save(route,env.get_template('default-layout.html').render(**c),template)

    page('/','main')
    page('/hansgal','hansgal_index')
    for menu in tables['menu']:
        section=menu['mainmenu']; id=menu['id']; route=f'/{section}/{id}'
        c={k:stripcslashes(menu[k]) for k in ('title','lead','body')}
        c['submenus']=[r for r in tables['menu'] if r['mainmenu']==section]
        c['thumbnails']=[r for r in tables['thumbnail'] if r['menu_id']==id]
        if section=='hansgal':
            c['thumb']=f'storage/pictureundersubmenus/thumb_hansgal_{id}.jpg'
            text=ROOT/'public/storage/textsundersubmenus'/f'hansgal_{id}.html'
            c['piktorgram']=stripcslashes(text.read_text(encoding='utf8')) if text.exists() else ''
        else:
            c['thumb']=f'/storage/pictureundersubmenus/thumb_{section}.jpg' in source_assets
        page(route,'hansgal' if section=='hansgal' else 'staticpage',**c)
    # The initial ordering is captured from the source rather than guessed from a locale.
    order=load('catalogue-order') if (ROOT/'content/catalogue-order.json').exists() else [r['id'] for r in tables['catalogue']]
    catalogue=[by_id['catalogue'][id] for id in order]
    page('/works','works',catalogues=catalogue,works_lead=props['works_lead']['value'],genres=[r for r in tables['category'] if r['type']=='Genre'],instruments=[r for r in tables['category'] if r['type']=='Instrument'])
    for work in tables['catalogue']:
        id=work['id']; w=copy.deepcopy(work)
        if len(w['free_downloads'] or '')<10:w['free_downloads']=False
        page('/works/show/'+id,'works_catalogue',catalogue=w,recordings=related('catalogue_recordings','catalogue_id',id,'recording_id',by_id['recording']),audiosamples=related('catalogue_audio_sample','catalogue_id',id,'audio_sample_id',audios),images=[r for r in tables['catalogue_image'] if r['catalogue_id']==id])
    for id in [None]+[r['id'] for r in recordings]:
        route='/recordings'+('/'+id if id else '')
        rec=by_id['recording'][id] if id else recordings[0]
        samples=related('recording_audio_sample','recording_id',id,'audio_sample_id',audios) if id else []
        page(route,'recordings',recording=rec,recordings=recordings,audiosamples=samples)
        if id:
            c=context(route);c.update(recording=rec,recordings=recordings,audiosamples=samples)
            save('/recordings/getalbuminfo/'+id,env.get_template('recordings_content.html').render(**c),'recordings_content',True)
    photos=OrderedDict((cat['name'],sorted([r for r in tables['photos'] if r['photos_category_id']==cat['id']],key=lambda r:int(r['sorrend']))) for cat in tables['photos_category'])
    page('/photos','photos',photos=photos)
    audio_display=copy.deepcopy(audio)
    for r in audio_display:
        if re.search(r'\d',r['opus_no']):r['title']=r['opus_no']+' '+r['title']
    page('/audiosamples','audiosamples',audiosamples=audio_display)
    for r in audio:
        for f in r['files']:
            markup='<audio controls="controls" autoplay="autoplay" src="/storage/audiosamples/'+html.escape(f['filename'],quote=True)+'">'+f['title']+'</audio>'
            save('/audiosamples/play/'+r['id']+'/'+f['filename'],markup,'audio-player',True)
    page('/comments','comments')
    page('/search','search')
    for mode in ('coverlist','coverflow'):
        aliases['/recordings/changeview/'+mode]='/recordings?view='+mode
    for route,target in aliases.items():
        destination=url(target)
        markup='<!doctype html><html><head><meta charset="utf-8"><meta name="robots" content="'+('noindex,nofollow' if review else 'index,follow')+'"><meta http-equiv="refresh" content="0;url='+html.escape(destination,quote=True)+'"><link rel="canonical" href="https://hansgal.org'+html.escape(target,quote=True)+'"></head><body><a href="'+html.escape(destination,quote=True)+'">Continue</a><script>location.replace('+json.dumps(destination)+'+location.hash)</script></body></html>'
        # Already rewritten above; do not apply the base path twice.
        targetfile=out/route.lstrip('/') if route.endswith('.html') else out/route.lstrip('/')/'index.html';targetfile.parent.mkdir(parents=True,exist_ok=True);targetfile.write_text(markup,encoding='utf8')
        generated[route]={'path':route,'file':targetfile.relative_to(out).as_posix(),'redirect':target}
    # Original source-only endpoints not in the crawler still need extensionless routes.
    (out/'app/site-data.json').write_text(json.dumps(tables,ensure_ascii=True,separators=(',',':')),encoding='utf8')
    (out/'app/runtime-config.json').write_text(json.dumps({'basePath':base_path,'review':review,'audioOrder':[r['id'] for r in audio],'recordingOrder':[r['id'] for r in recordings]}),encoding='utf8')
    for file in ('accent-map','catalogue-orders'):
        if (ROOT/'content'/f'{file}.json').exists(): shutil.copyfile(ROOT/'content'/f'{file}.json',out/'app'/f'{file}.json')
    (out/'.nojekyll').touch()
    (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if review else 'User-agent: *\nAllow: /\nSitemap: https://hansgal.org/sitemap.xml\n',encoding='utf8')
    hidden={'/'+r['mainmenu']+'/'+r['id'] for r in tables['menu'] if r['hidden']=='yes'}
    sitemap_paths=[p for p in generated if p not in hidden and not any(x in p for x in ('/getalbuminfo/','/play/','/changeview/')) and p not in aliases]
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://hansgal.org'+html.escape(p)+'</loc></url>' for p in sitemap_paths)+'</urlset>',encoding='utf8')
    missing=[r['path'] for r in route_rows if r['path'] not in generated and not (out/r['path'].lstrip('/')).exists()]
    report={'routes':list(generated.values()),'missing_captured_paths':missing,'base_path':base_path,'review':review,'total_bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}
    (ROOT/'docs/build-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({'generated_routes':len(generated),'missing_captured_paths':missing,'bytes':report['total_bytes'],'base_path':base_path}))
    if missing: raise SystemExit('Captured routes are missing from build')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base-path',default='');p.add_argument('--production',action='store_true')
    args=p.parse_args();make_site(args.base_path,not args.production)

