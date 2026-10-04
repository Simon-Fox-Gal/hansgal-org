"""Render the Hans Gál replica as static files. No database or web backend."""
from __future__ import annotations
import argparse, copy, hashlib, html, json, pathlib, re, shutil, subprocess
from collections import OrderedDict
from urllib.parse import urlsplit, unquote, quote, urljoin
from jinja2 import Environment, FileSystemLoader, ChainableUndefined
from i18n import localize, translate_template
from work_pdfs import build_work_pdfs, download_filename
from contacts import context as contact_context
from languages import LANGUAGES, PUBLISHED, prefix, labels, text as translated_text

ROOT = pathlib.Path(__file__).resolve().parents[1]
STANDALONE_GERMAN={
 '/storage/sketchbook/galpictures.html':[
  ('Sketches','Skizzen'),
  ("From \n        G&aacute;l's sketchbook, 1903",'Aus G&aacute;ls Skizzenbuch, 1903'),
 ],
 '/storage/texts/levetzowpoem.html':[
  ('Levetzow poem','Gedicht von Levetzow'),
  ('Text \n        of a poem by Levetzow,','Text eines Gedichts von Levetzow,'),
  ("commemorating the G&aacute;ls' visit to Corsica",'zur Erinnerung an den Besuch der Familie G&aacute;l auf Korsika'),
 ],
}
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

def editorial_fragment(value):
    """Discard embedded document chrome/CSS; retain authored text and controls."""
    scripts=[]
    def keep_script(match):
        scripts.append(match[0]);return f'<!--EDITORIAL_SCRIPT_{len(scripts)-1}-->'
    value=re.sub(r'<script\b[^>]*>.*?</script\s*>',keep_script,value,flags=re.I|re.S)
    value=re.sub(r'<head\b[^>]*>.*?</head\s*>','',value,flags=re.I|re.S)
    value=re.sub(r'<style\b[^>]*>.*?</style\s*>','',value,flags=re.I|re.S)
    value=re.sub(r'<!doctype[^>]*>|</?(?:html|body)\b[^>]*>','',value,flags=re.I)
    value=re.sub(r'<(/?)h1\b',r'<\1h2',value,flags=re.I)
    for i,script in enumerate(scripts):value=value.replace(f'<!--EDITORIAL_SCRIPT_{i}-->',script)
    return value

def audio_row(row):
    r=copy.deepcopy(row)
    r['files']=[{'title':s.split('#',1)[0], 'filename':s.split('#',1)[1], 'fileroot':'/storage/audiosamples/'+s.split('#',1)[1].removesuffix('.mp3')} for s in r['filename'].split('|') if '#' in s]
    labels=(r.get('track_titles') or '').splitlines()
    if labels:
        if len(labels)!=len(r['files']):raise ValueError('Audio track title count differs: '+r['id'])
        for f,label in zip(r['files'],labels):f['title']=label
    return r

def make_site(base_path='', review=True, language='en', active_languages=None, incomplete=False):
    active_languages=active_languages or PUBLISHED
    lang_prefix=prefix(language)
    tr=lambda en,de=None:translated_text(language,en,de,strict=language in ('fr','ja') and not incomplete)
    base_path='/' + base_path.strip('/') if base_path.strip('/') else ''
    out=ROOT/'dist'
    if language=='en' and out.exists():
        assert out.resolve() == (ROOT/'dist').resolve() and out.resolve().is_relative_to(ROOT.resolve())
        shutil.rmtree(out)
    if language=='en':
        shutil.copytree(ROOT/'public',out)
        shutil.copytree(ROOT/'app',out/'app',dirs_exist_ok=True)
    # ImageFlow keeps its original animation. Reflections are now canvas images
    # supplied by replica.js, so the old PHP image service is unnecessary.
    flowfile=out/'imageflow/imageflow.js'
    flow=flowfile.read_text(encoding='utf8')
    flow=flow.replace("src =  '/imageflow/reflect'+version+'.php?img='+src+thisObject.reflectionGET+'&bgc=eeeeee';",'src = src; // The static renderer supplies the complete reflection image.')
    flow=re.sub(r'domReady\(function\(\)\s*\{\s*var instanceOne = new ImageFlow\(\);\s*instanceOne.init\(\{ ImageFlowID:\'coverflow\' \}\);\s*\}\);','// Initialized by replica.js after static data loads.',flow)
    flowfile.write_text(flow,encoding='utf8')
    if base_path and language=='en':
        for css in out.rglob('*.css'):
            value=css.read_text(encoding='utf8')
            value=re.sub(r'(url\(\s*["\']?)(/(?!/))',lambda m:m[1]+base_path+'/',value)
            css.write_text(value,encoding='utf8')
    tables={p.stem:json.loads(p.read_text(encoding='utf8')) for p in (ROOT/'content').glob('*.json') if p.stem not in ('asset-manifest','legacy-routes','catalogue-order','catalogue-orders','accent-map')}
    if language!='en':tables=localize(tables,language)
    build_work_pdfs(tables,out,language,base_path,stripcslashes)
    by_id={k:{r.get('id'):r for r in v} for k,v in tables.items()}
    class LocaleLoader(FileSystemLoader):
        def get_source(self,environment,template):
            source,filename,uptodate=super().get_source(environment,template)
            return (translate_template(source,language) if language!='en' else source),filename,uptodate
    env=Environment(loader=LocaleLoader(ROOT/'templates'),autoescape=False,undefined=ChainableUndefined,keep_trailing_newline=True,finalize=lambda v:'' if v is None else v)
    env.globals['language']=language
    env.globals['duration_label']=lambda value:tr('full evening') if language in ('fr','ja') and value=='full evening' else str(value or '')+"'"
    # The player needs one copy of the current-language track and credit data,
    # not the full editorial row (and the same credits again in source groups).
    def player_data(rows):
        keys=('id','title','opus_no','work_id','playback_index','categories','search')
        credit_keys=('performers','label','copyright','cover','album_title','link','preview')
        return [dict({k:r.get(k) for k in keys},files=[dict(title=f['title'],filename=f['filename'],index=f['index'],credit={k:f.get('credit',{}).get(k) for k in credit_keys}) for f in r['files']]) for r in rows]
    env.filters['player_data']=player_data
    env.policies['json.dumps_kwargs']={'sort_keys':True,'ensure_ascii':False,'separators':(',',':')}
    env.globals['page_text']=lambda id: html.escape((by_id['page_text'][id].get('value'+('_'+language if language!='en' else '')) or by_id['page_text'][id]['value']),quote=True)
    env.filters['stripcslashes']=stripcslashes
    env.filters['work_pdf_filename']=lambda value:download_filename(stripcslashes(value))
    env.globals['php_truth']=php_truth
    props={x['name']:x for x in tables['properties']}
    recordings=sorted(tables['recording'],key=lambda r:(int(r['sequence']),-int(r['id'])))
    audio=sorted(tables['audio_sample'],key=lambda r:(int(r['sequence']),r['opus_no']))
    audio=[audio_row(r) for r in audio]
    credit_by_file={r['filename']:r for r in tables.get('audio_credit',[])}
    # Keep the original index-based listening bookmarks stable as new works arrive.
    playback_order=[r for r in audio if int(r['id'])<=88]+[r for r in audio if int(r['id'])>88]
    for index,r in enumerate(playback_order):r['playback_index']=index
    def credit_groups(r):
        groups=OrderedDict()
        for f in r['files']:
            c=credit_by_file.get(f['filename'],{})
            f['credit']=c
            key=c.get('album','')
            group=groups.setdefault(key,{'credit':c,'files':[]})
            group['files'].append(f)
        for group in groups.values():
            artists={f['credit'].get('performers','') for f in group['files']}
            group['performers']=next(iter(artists)) if len(artists)==1 else ''
        r['sources']=list(groups.values())
        r['has_credits']=any(f['credit'] for f in r['files'])
        r['work_id']=next((x['catalogue_id'] for x in tables['catalogue_audio_sample'] if x['audio_sample_id']==r['id']),'')
        work_ids=[x['catalogue_id'] for x in tables['catalogue_audio_sample'] if x['audio_sample_id']==r['id']]
        r['categories']=list({x['category_id'] for x in tables['catalogue_category'] if x['catalogue_id'] in work_ids}|({r['listening_category']} if r.get('listening_category') else set()))
        r['search']=' '.join(dict.fromkeys(str(v or '') for v in [r['title'],r['opus_no'],r['details']]+[f['credit'].get(k,'') for f in r['files'] for k in ('album_title','performers','label','album')]+[v for w in tables['catalogue'] if w['id'] in work_ids for v in [w['title'],w.get('title_original',''),w['description'],w['orchestration']]]))
        for i,f in enumerate(r['files']):f.setdefault('index',i)
        return r
    audio=[credit_groups(r) for r in audio]
    audios={r['id']:r for r in audio}
    source_assets={r['path'] for r in load('asset-manifest')}
    route_rows=load('legacy-routes')
    generated={}
    aliases={r['path']:r['redirect'] for r in route_rows if 'redirect' in r}
    aliases.update({'/biography/15-nazitakeover.html':'/hansgal/45','/works/op53.html':'/works/show/61'})

    def related(table,left,id,right,objects):
        # Missing parents are retained in source data; the old join omitted them.
        return [objects[r[right]] for r in tables[table] if r[left]==id and r[right] in objects]

    def purchase_links(row):
        labels={'purchase_url':('Printed music / publisher product page','Gedruckte Noten / Verlagsproduktseite'),
                'hire_url':('Hire materials','Leihmaterial'), 'score_purchase_download_url':('Buy digital sheet music','Digitale Noten kaufen'),
                'cd_url':('Physical CD','CD'), 'download_url':('Buy audio download','Audio-Download kaufen'), 'listen_url':('Listen','Anhören')}
        links=[]
        for field,label in labels.items():
            for value in (row.get(field) or '').splitlines():
                value=value.strip()
                if not value:continue
                u=urlsplit(value)
                if u.scheme not in ('https','http') or not u.hostname or u.username or u.password:
                    raise ValueError(f'Invalid public purchase URL: {row.get("id")} {field}')
                display_label=tr(*label)
                if field=='cd_url' and row.get('cd_format')=='Hybrid SACD':
                    display_label=tr('Hybrid SACD / CD','Hybrid-SACD / CD')
                if field=='cd_url' and row.get('cd_format')=='Used CD':
                    display_label=tr('Used CD','Gebrauchte CD')
                links.append({'url':value,'host':u.hostname.removeprefix('www.'),'label':display_label})
        return links

    def score_downloads(row):
        paths=[value.strip() for value in (row.get('score_file') or '').splitlines() if value.strip()]
        titles=(row.get('score_file_titles') or '').splitlines()
        return [{'path':path,'title':titles[i].strip() if i<len(titles) and titles[i].strip() else ('Download PDF' if len(paths)==1 else f'Download PDF {i+1}')} for i,path in enumerate(paths)]

    def context(route):
        section=route.split('/')[1] if route!='/' else ''
        c=dict(props,language=language,tr=tr,route=route,mainmenu=section,viewmode='coverlist',chosenfile='',chosenwork='',autoplay='',genre='',instrument='',keywords={},audiosamples=[],recordings=[],thumbnails=[],thumb=False,piktorgram='',title='',lead='',body='')
        for s in ['hansgal','news','works','recordings','booksandarticles','audiosamples','publishers','bibliography','photos','faq','contacts','hansgalsociety','comments','donate']:
            c['selected'+s]=' id="selected"' if section==s else ''
        return c

    # Root-relative URLs resolve both at /hansgal-org on Pages and at / on the future domain.
    local_hosts={'hansgal.org','www.hansgal.org','hansgal.com','www.hansgal.com','production.hansgal.org','hansgal.musicessences.com'}
    def url(value):
        value=html.unescape(value)
        u=urlsplit(value)
        if u.hostname in local_hosts:
            value=u.path or '/'
            if u.query: value+='?'+u.query
            if u.fragment: value+='#'+u.fragment
        if value.startswith('/') and not value.startswith('//'):
            if language!='en' and ((language=='de' and urlsplit(value).path in STANDALONE_GERMAN) or value=='/' or re.match(r'^/(?:hansgal|news|works|recordings|booksandarticles|audiosamples|publishers|bibliography|photos|faqs?|contacts|hansgalsociety|comments|donate|search|score-basket)(?:/|\?|$)',value)):
                value=lang_prefix+value
            return base_path+value
        if value.startswith(('storage/','gfx/','imageflow/')):
            return url('/'+value)
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
        localized=lang_prefix+route
        markup=markup.replace('<html xmlns=',f'<html lang="{language}" xmlns=').replace('content="hu"',f'content="{language}"')
        title_match=re.search(r'<h1[^>]*>(.*?)</h1>',markup,re.S) or re.search(r'<div class="title">(.*?)</div>',markup,re.S)
        page_title=html.unescape(re.sub('<[^>]*>','',title_match[1])) if title_match else 'Hans Gál Society'
        match=re.match(r'^/(works/show|recordings|hansgal|news|booksandarticles|publishers|bibliography|hansgalsociety)/(\d+)/?$',route)
        if match:
            table='catalogue' if match[1]=='works/show' else 'recording' if match[1]=='recordings' else 'menu'
            page_title=html.unescape(re.sub('<[^>]*>','',by_id[table].get(match[2],{}).get('title') or page_title))
        if route.rstrip('/')=='/score-basket':page_title=tr('Your score basket','Ihr Notenkorb')
        markup=markup.replace('<title></title>','<title>'+html.escape(page_title)+' · Hans Gál</title>',1)
        head='<meta name="hansgal-base" content="'+base_path+'" />\n<link rel="canonical" href="https://hansgal.org'+html.escape(localized,quote=True)+'" />\n'
        for lang,language_prefix in [(l,prefix(l)) for l in active_languages]+[('x-default','')]:head+='<link rel="alternate" hreflang="'+lang+'" href="https://hansgal.org'+html.escape(language_prefix+route,quote=True)+'" />\n'
        head+='<script defer src="'+base_path+'/app/language.js"></script>\n'
        head+='<script defer src="'+base_path+'/app/editorial-bridge.js"></script>\n'
        markup=markup.replace('</head>',head+'</head>',1)
        markup=markup.replace('<head>','<head><script src="'+base_path+'/app/locale-'+language+'.js"></script>',1)
        switch='<nav aria-label="Language / Sprache / Langue / 言語" style="text-align:right;padding:4px 12px">'+' · '.join('<a data-language="'+l+'" lang="'+l+'" href="'+base_path+prefix(l)+route+'">'+LANGUAGES[l]+'</a>' for l in active_languages)+'</nav>'
        if '<!-- LANGUAGE_SWITCH -->' in markup:markup=markup.replace('<!-- LANGUAGE_SWITCH -->',switch,1)
        elif '<div id="wrapper">' in markup:markup=markup.replace('<div id="wrapper">','<div id="wrapper">'+switch,1)
        return markup

    def save(route,markup,template='generated',fragment=False):
        assert route.startswith('/') and '..' not in pathlib.PurePosixPath(route).parts
        local_route=lang_prefix+route
        target=out/local_route.lstrip('/')/'index.html' if local_route!='/' else out/'index.html'
        target.parent.mkdir(parents=True,exist_ok=True)
        final=transform(markup,route)
        target.write_text(final,encoding='utf8',newline='\n')
        generated[local_route]={'path':local_route,'file':target.relative_to(out).as_posix(),'template':template,'sha256':hashlib.sha256(final.encode()).hexdigest()}

    def page(route,template,**kwargs):
        c=context(route);c.update(kwargs)
        content=env.get_template(template+'.html').render(**c)
        c['CONTENT']=content
        save(route,env.get_template('default-layout.html').render(**c),template)

    page('/','main',featured_recordings=recordings[:3])
    page('/score-basket','score-basket')
    page('/hansgal','hansgal_index',biography_intro=by_id['heading']['1']['body'],biography_menu=by_id['menu'],biography_extra=[r for r in tables['menu'] if r['mainmenu']=='hansgal' and r['hidden']!='yes' and r['id'] not in ['1', '2', '9', '11', '27', '28', '29', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56']])
    for menu in tables['menu']:
        section=menu['mainmenu']; id=menu['id']; route=f'/{section}/{id}'
        c={k:editorial_fragment(stripcslashes(menu[k])) for k in ('title','lead','body')}
        if '<!-- SHARED_CONTACT_PANEL -->' in c['body']:
            c['body']=c['body'].replace('<!-- SHARED_CONTACT_PANEL -->',env.get_template('contact-panel.html').render(**contact_context(language)))
        c['submenus']=[r for r in tables['menu'] if r['mainmenu']==section]
        c['thumbnails']=[r for r in tables['thumbnail'] if r['menu_id']==id]
        if section=='hansgal':
            candidate=f'storage/pictureundersubmenus/thumb_hansgal_{id}.jpg'
            c['thumb']=candidate if (ROOT/'public'/candidate).is_file() else False
            text=ROOT/'public/storage/textsundersubmenus'/f'hansgal_{id}.html'
            c['piktorgram']=stripcslashes(text.read_text(encoding='utf8')) if text.exists() else ''
            if language!='en':c['piktorgram']=translate_template(c['piktorgram'],language)
        else:
            c['thumb']=f'/storage/pictureundersubmenus/thumb_{section}.jpg' in source_assets
        if section=='hansgal' and id=='55':
            c['audiosamples']=audio
            c['discover_player']=True
        page(route,'hansgal' if section=='hansgal' else 'staticpage',**c)
    # The initial ordering is captured from the source rather than guessed from a locale.
    order=load('catalogue-order') if (ROOT/'content/catalogue-order.json').exists() else [r['id'] for r in tables['catalogue']]
    basis=load('catalogue-orders')['orders'].get('__basis')
    current=[[r.get(k) for k in ('id','opus_no','title','description','year_of_composition','publisher')] for r in tables['catalogue']]
    if basis != current:
        payload=json.dumps({'data':tables,'accent':load('accent-map'),'orders':load('catalogue-orders')['orders']})
        result=subprocess.run(['node',str(ROOT/'scripts/catalogue-order.cjs')],input=payload,text=True,encoding='utf8',capture_output=True,check=True)
        order=json.loads(result.stdout)
    recording_work_ids={r['catalogue_id'] for r in tables['catalogue_recordings'] if r['recording_id'] in by_id['recording']}
    audio_work_ids={r['catalogue_id'] for r in tables['catalogue_audio_sample'] if r['audio_sample_id'] in audios}
    catalogue=[]
    for id in order:
        row=copy.deepcopy(by_id['catalogue'][id])
        row['_has_recordings']=id in recording_work_ids
        row['_has_audio_samples']=id in audio_work_ids
        catalogue.append(row)
    page('/works','works',catalogues=catalogue,works_lead=props['works_lead']['value'],genres=[r for r in tables['category'] if r['type']=='Genre'],instruments=[r for r in tables['category'] if r['type']=='Instrument'])
    for work in tables['catalogue']:
        id=work['id']; w=copy.deepcopy(work)
        if len(w['free_downloads'] or '')<10:w['free_downloads']=False
        page('/works/show/'+id,'works_catalogue',catalogue=w,score_downloads=score_downloads(w),purchase_links=purchase_links(w),recordings=related('catalogue_recordings','catalogue_id',id,'recording_id',by_id['recording']),audiosamples=related('catalogue_audio_sample','catalogue_id',id,'audio_sample_id',audios),images=[r for r in tables['catalogue_image'] if r['catalogue_id']==id])
    for id in [None]+[r['id'] for r in recordings]:
        route='/recordings'+('/'+id if id else '')
        rec=by_id['recording'][id] if id else recordings[0]
        samples=related('recording_audio_sample','recording_id',id,'audio_sample_id',audios) if id else []
        # A work can contain excerpts from more than one recording (Symphony I,
        # for example). An album page must only play its own recording.
        samples=[credit_groups(dict(copy.deepcopy(r),files=[f for f in copy.deepcopy(r['files']) if not f['credit'] or f['credit'].get('recording_id')==id])) for r in samples]
        samples=[r for r in samples if r['files']]
        page(route,'recordings',recording=rec,recordings=recordings,audiosamples=samples,purchase_links=purchase_links(rec))
        if id:
            c=context(route);c.update(recording=rec,recordings=recordings,audiosamples=samples,purchase_links=purchase_links(rec),album_fragment=True)
            save('/recordings/getalbuminfo/'+id,env.get_template('recordings_content.html').render(**c),'recordings_content',True)
    photos=OrderedDict((cat['name'],sorted([r for r in tables['photos'] if r['photos_category_id']==cat['id']],key=lambda r:int(r['sorrend']))) for cat in tables['photos_category'])
    page('/photos','photos',photos=photos)
    def opus_key(r):
        match=re.search(r'(\d+)(.*)',r['opus_no'])
        return (int(match[1]),match[2],r['title']) if match else (10000,'',r['title'])
    audio_display=sorted(copy.deepcopy(audio),key=opus_key)
    page('/audiosamples','audiosamples',audiosamples=audio_display)
    for r in audio:
        for f in r['files']:
            markup='<audio controls="controls" autoplay="autoplay" src="/storage/audiosamples/'+html.escape(f['filename'],quote=True)+'">'+f['title']+'</audio>'
            save('/audiosamples/play/'+r['id']+'/'+f['filename'],markup,'audio-player',True)
    for r in tables.get('audio_legacy_route',[]):
        route='/audiosamples/play/'+r['audio_sample_id']+'/'+r['filename']
        if lang_prefix+route not in generated:
            markup='<audio controls src="/storage/audiosamples/'+html.escape(r['filename'],quote=True)+'">'+html.escape(r['title'])+'</audio>'
            save(route,markup,'audio-player',True)
    page('/comments','comments')
    page('/search','search')
    if language=='de':
        # Preserve the original English asset bytes and URLs. German standalone
        # pages reuse the same layout, images and original German/Latin poem.
        for route,replacements in STANDALONE_GERMAN.items():
            markup=(ROOT/'public'/route.lstrip('/')).read_text(encoding='utf8')
            for before,after in replacements:
                if before not in markup:raise ValueError('Missing standalone phrase: '+before)
                markup=markup.replace(before,after)
            markup=markup.replace('<html>','<html lang="de">',1).replace('charset=iso-8859-1','charset=utf-8')
            # These obsolete ImageStyler rollovers are unused in the preserved
            # document bodies; their image files are absent from the source.
            markup=re.sub(r'<script\b[^>]*>[\s\S]*?</script>','',markup,flags=re.I)
            markup=re.sub(r'\s+background="\.\./newimages/backgrnd\.gif"','',markup)
            def absolute_asset(match):
                value=match[3]
                if not urlsplit(value).scheme and not value.startswith(('/', '#')):value=urljoin(route,value)
                return match[1]+'='+match[2]+html.escape(value,quote=True)+match[2]
            markup=re.sub(r'''\b(href|src|background)\s*=\s*(["'])(.*?)\2''',absolute_asset,markup,flags=re.I|re.S)
            # Legacy background attributes are not part of the normal renderer.
            markup=re.sub(r'''\bbackground="(/[^"<>]+)"''',lambda m:'background="'+base_path+m[1]+'"',markup)
            nav='<nav aria-label="Language / Sprache" style="text-align:right"><a data-language="en" lang="en" href="'+base_path+route+'">English</a> · <a data-language="de" lang="de" href="'+base_path+'/de'+route+'">Deutsch</a></nav>'
            markup=transform(markup,route)
            # Add links after URL rewriting to avoid applying the base twice.
            markup=re.sub(r'(<body\b[^>]*>)',lambda m:m[1]+nav,markup,count=1,flags=re.I)
            target=out/'de'/route.lstrip('/');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(markup,encoding='utf8')
            generated['/de'+route]={'path':'/de'+route,'file':target.relative_to(out).as_posix(),'template':'standalone-german','sha256':hashlib.sha256(markup.encode()).hexdigest()}
    for mode in ('coverlist','coverflow'):
        aliases['/recordings/changeview/'+mode]='/recordings?view='+mode
    for route,target in aliases.items():
        destination=url(target)
        markup='<!doctype html><html><head><meta charset="utf-8"><meta name="robots" content="'+('noindex,nofollow' if review else 'index,follow')+'"><meta http-equiv="refresh" content="0;url='+html.escape(destination,quote=True)+'"><link rel="canonical" href="https://hansgal.org'+html.escape(target,quote=True)+'"></head><body><a href="'+html.escape(destination,quote=True)+'">Continue</a><script>location.replace('+json.dumps(destination)+'+location.hash)</script></body></html>'
        # Already rewritten above; do not apply the base path twice.
        local_route=lang_prefix+route
        targetfile=out/local_route.lstrip('/') if route.endswith('.html') else out/local_route.lstrip('/')/'index.html';targetfile.parent.mkdir(parents=True,exist_ok=True);targetfile.write_text(markup,encoding='utf8')
        generated[local_route]={'path':local_route,'file':targetfile.relative_to(out).as_posix(),'redirect':lang_prefix+target}
    # Original source-only endpoints not in the crawler still need extensionless routes.
    # Keep the old German search aliases and score fields used by existing
    # clients; other editions' editorial prose belongs only in its own file.
    runtime_tables={name:[{k:v for k,v in row.items() if not k.endswith(('_fr','_ja')) and (not k.endswith('_de') or k in ('title_de','description_de','score_note_de','score_file_titles_de'))} for row in rows] for name,rows in tables.items()}
    (out/('app/site-data'+('-'+language if language!='en' else '')+'.json')).write_text(json.dumps(runtime_tables,ensure_ascii=False,separators=(',',':')),encoding='utf8')
    (out/('app/locale-'+language+'.js')).write_text('window.HansgalLocale='+json.dumps({'language':language,'labels':labels(language)},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+';',encoding='utf8')
    (out/'app/runtime-config.json').write_text(json.dumps({'basePath':base_path,'review':review,'audioOrder':[r['id'] for r in playback_order],'recordingOrder':[r['id'] for r in recordings]}),encoding='utf8')
    for file in ('accent-map','catalogue-orders'):
        if (ROOT/'content'/f'{file}.json').exists(): shutil.copyfile(ROOT/'content'/f'{file}.json',out/'app'/f'{file}.json')
    (out/'.nojekyll').touch()
    (out/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if review else 'User-agent: *\nAllow: /\nSitemap: https://hansgal.org/sitemap.xml\n',encoding='utf8')
    hidden={'/'+r['mainmenu']+'/'+r['id'] for r in tables['menu'] if r['hidden']=='yes'}
    sitemap_paths=[p for p in generated if p not in hidden and not any(x in p for x in ('/getalbuminfo/','/play/','/changeview/')) and p not in aliases]
    (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://hansgal.org'+html.escape(p)+'</loc></url>' for p in sitemap_paths)+'</urlset>',encoding='utf8')
    missing=[r['path'] for r in route_rows if r['path'] not in generated and not (out/r['path'].lstrip('/')).exists()]
    if language!='en':
        previous=json.loads((ROOT/'docs/build-report.json').read_text(encoding='utf8'))
        generated={**{r['path']:r for r in previous['routes']},**generated}
        hidden.update(prefix(l)+'/'+r['mainmenu']+'/'+r['id'] for l in active_languages for r in tables['menu'] if r['hidden']=='yes')
        sitemap_paths=[p for p,r in generated.items() if p not in hidden and not any(x in p for x in ('/getalbuminfo/','/play/','/changeview/')) and 'redirect' not in r]
        (out/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://hansgal.org'+html.escape(p)+'</loc></url>' for p in sitemap_paths)+'</urlset>',encoding='utf8')
    report={'routes':list(generated.values()),'missing_captured_paths':missing,'base_path':base_path,'review':review,'total_bytes':sum(p.stat().st_size for p in out.rglob('*') if p.is_file())}
    (ROOT/'docs/build-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps({'generated_routes':len(generated),'missing_captured_paths':missing,'bytes':report['total_bytes'],'base_path':base_path}))
    if missing: raise SystemExit('Captured routes are missing from build')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base-path',default='');p.add_argument('--production',action='store_true')
    p.add_argument('--languages',nargs='+',choices=list(LANGUAGES),default=PUBLISHED)
    p.add_argument('--allow-incomplete-preview',action='store_true')
    args=p.parse_args()
    if args.allow_incomplete_preview and args.production:p.error('Incomplete translations cannot be published.')
    if args.languages[0]!='en' or len(args.languages)!=len(set(args.languages)):p.error('Build English first and include each language only once.')
    if not args.allow_incomplete_preview:
        from translation_inventory import inventory
        for language in args.languages:
            if language in ('fr','ja') and any(i['status']=='pending' for i in inventory(language)):p.error(language+' translations are incomplete; publication blocked.')
    for language in args.languages:make_site(args.base_path,not args.production,language,args.languages,args.allow_incomplete_preview)
