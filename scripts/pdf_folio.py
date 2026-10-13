"""Flowing Folio work notes: the same content in four printable editions."""
import html
import io
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Spacer, Table,
    TableStyle, HRFlowable, PageBreakIfNotEmpty as PageBreak, CondPageBreak, KeepTogether, Image,
    BalancedColumns)

from languages import prefix, text as translated_text
from folio import present, folio_duration
from score_links import score_link_label
from pdf_typography import Paragraph

ROOT = Path(__file__).resolve().parents[1]
INK = colors.HexColor('#29252a')
PLUM = colors.HexColor('#792858')
GREEN = colors.HexColor('#215d42')
MUTED = colors.HexColor('#625c60')
LINE = colors.HexColor('#d7ccc8')
CREAM = colors.HexColor('#f8f5ee')
WIDTH = A4[0] - 88


@lru_cache
def register_fonts():
    # Gelasio is an open, Georgia-compatible serif. The variable font's default
    # instance is regular; the unmodified upstream font and OFL are vendored.
    pdfmetrics.registerFont(TTFont('Folio-Serif', str(ROOT/'vendor/fonts/Gelasio-variable.ttf')))
    pdfmetrics.registerFont(TTFont('Edition-Japanese', str(ROOT/'vendor/fonts/NotoSansJP-Regular.ttf')))
    pdfmetrics.registerFontFamily('Edition-Japanese', normal='Edition-Japanese',
        bold='Edition-Japanese', italic='Edition-Japanese', boldItalic='Edition-Japanese')


@lru_cache(maxsize=150)
def cover_bytes(name):
    path = ROOT/'public/storage/recordingcovers'/name
    if not path.is_file():
        return None
    with PILImage.open(path) as image:
        image = image.convert('RGB')
        image.thumbnail((360, 360))
        target = io.BytesIO()
        image.save(target, format='JPEG', quality=87, optimize=True)
        return target.getvalue(), image.size


def build_folio_pdfs(tables, out, language, base_path, strip, paragraphs, plain):
    register_fonts()
    japanese = language == 'ja'
    font = 'Edition-Japanese' if japanese else 'Edition'
    bold = 'Edition-Japanese' if japanese else 'Edition-Bold'
    serif = 'Edition-Japanese' if japanese else 'Folio-Serif'
    t = lambda en, de=None: translated_text(language, en, de, strict=language in ('fr','ja'))
    site = ('https://simon-fox-gal.github.io'+base_path if base_path else 'https://hansgal.org')+'/'
    lang_path = prefix(language).strip('/') + ('/' if language != 'en' else '')
    folder = out/'storage/work-notes'/language
    folder.mkdir(parents=True, exist_ok=True)
    body = ParagraphStyle('body', fontName=font, fontSize=11, leading=16.3,
        textColor=INK, spaceAfter=7, splitLongWords=True,
        wordWrap='CJK' if japanese else None, rightIndent=20 if japanese else 0)
    styles = {
        'body': body,
        'title': ParagraphStyle('title', parent=body, fontName=serif,
            fontSize=32, leading=39, spaceAfter=14),
        'translation': ParagraphStyle('translation', parent=body,
            fontSize=16, leading=23, textColor=GREEN, spaceAfter=14),
        'subtitle': ParagraphStyle('subtitle', parent=body, fontSize=12,
            leading=18, textColor=MUTED, spaceAfter=14),
        'label': ParagraphStyle('label', parent=body, fontName=bold,
            fontSize=8.4 if not japanese else 9, leading=12.5,
            textColor=PLUM, spaceAfter=7, keepWithNext=True),
        'fact': ParagraphStyle('fact', parent=body, fontSize=10.3,
            leading=15.3, spaceAfter=13),
        'heading': ParagraphStyle('heading', parent=body, fontName=serif,
            fontSize=25, leading=32, textColor=INK,
            spaceBefore=8, spaceAfter=16, keepWithNext=True),
        'record': ParagraphStyle('record', parent=body, fontName=serif,
            fontSize=19, leading=25, spaceAfter=8, keepWithNext=True),
        'small': ParagraphStyle('small', parent=body, fontSize=9,
            leading=13, textColor=MUTED),
        'link': ParagraphStyle('link', parent=body, fontName=bold,
            fontSize=9.3, leading=14, textColor=PLUM, spaceAfter=10),
    }

    def p(value, style='body'):
        result = paragraphs(value, styles[style], site, strip)
        if style == 'body':
            quote = ParagraphStyle('quotation',parent=body,fontName=serif,
                fontSize=12 if japanese else 14,leading=19,textColor=GREEN,spaceBefore=7,spaceAfter=14)
            result = [Paragraph(item.text,quote) if plain(item.text).lstrip().startswith(('"','“','«','「'))
                and len(plain(item.text))>100 else item for item in result]
        return result

    def display_title(value):
        # Instrumentation remains verbatim, in a readable subtitle rather than
        # competing with the identifying title. This is typography, not editing.
        parts = re.split(r'( for | für | pour )', value, maxsplit=1)
        title_style = ParagraphStyle('display-title',parent=styles['title'],fontName='Folio-Serif' if not japanese or original else serif,
            fontSize=37 if len(parts[0])<45 else 29,leading=44 if len(parts[0])<45 else 36,wordWrap=None)
        result = paragraphs(parts[0],title_style,site,lambda s:s)
        if len(parts)>1:
            result += paragraphs(''.join(parts[1:]).strip(),styles['subtitle'],site,lambda s:s)
        return result

    def label(en, de):
        return Paragraph(html.escape(t(en, de)), styles['label'])

    def link(text, url):
        return Paragraph('<link href="'+html.escape(url, quote=True)+'" color="#792858">'
            +html.escape(text)+'</link>', styles['link'])

    def section(en, de, value, style='body'):
        contents = p(value, style)
        return [label(en, de), *contents] if contents else []

    def section_rule():
        rule=HRFlowable(width='100%',thickness=.7,color=PLUM,spaceAfter=16)
        rule.keepWithNext=True
        return rule

    recordings = {r['id']: r for r in tables['recording']}
    for row in tables['catalogue']:
        work_url = site+lang_path+'works/show/'+row['id']+'/'
        work_title = plain(strip(row['title']))
        story = [Paragraph('HANS GÁL', styles['label'])]
        original = plain(strip(row.get('title_original') or ''))
        # Keep the exact original title and its supplied bracketed translation.
        if original and work_title.startswith(original) and work_title[len(original):].strip().startswith(('(', '[', '［')):
            story += display_title(original)
            story += p(work_title[len(original):], 'translation')
        else:
            story += display_title(work_title)
        if present(row.get('description')):
            story += p(row['description'], 'subtitle')
        metadata = []
        for en, de, value in [
            ('Catalogue', 'Werkverzeichnis', 'Op. '+str(row['opus_no']) if present(row.get('opus_no')) else ''),
            ('Composed', 'Komponiert', row.get('year_of_composition')),
            ('Duration', 'Dauer', t('full evening', 'abendfüllend') if row.get('duration')=='full evening' else folio_duration(row.get('duration')))]:
            if present(value):
                metadata.append([label(en,de), Paragraph(html.escape(str(value)),
                    ParagraphStyle('meta',parent=body,fontName=bold,fontSize=11.5,leading=16,textColor=GREEN,spaceAfter=0))])
        if metadata:
            band = Table([metadata], colWidths=[WIDTH/len(metadata)]*len(metadata))
            band.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),CREAM),('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),13),('RIGHTPADDING',(0,0),(-1,-1),13),
                ('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11)]))
            story += [band, Spacer(1,22)]
        else:
            story += [HRFlowable(width='100%',thickness=.5,color=LINE),Spacer(1,20)]

        facts = []
        for field,en,de in [('publisher','Publisher','Verlag'),('availability','Availability','Verfügbarkeit'),
                ('first_performance','First performance','Uraufführung'),('other_versions','Other versions','Weitere Fassungen')]:
            if present(row.get(field)):
                facts += section(en,de,row[field],'fact')
        for field in ('purchase_url','hire_url','score_purchase_download_url'):
            for url in (row.get(field) or '').splitlines():
                if url.strip():
                    from urllib.parse import urlsplit
                    facts.append(link(score_link_label(url.strip(),field,t)+' · '+urlsplit(url.strip()).netloc.removeprefix('www.'),url.strip()))
        narrative = []
        for field,en,de in [('further_details','About the work','Über das Werk'),
                ('movements','Movements','Sätze'),('orchestration','Instrumentation','Besetzung')]:
            if present(row.get(field)):
                narrative += section(en,de,row[field])
        if facts and narrative and len(plain(strip(row.get('further_details') or '')))>2200:
            # Extended essays use the full measure after a compact facts grid.
            # A narrow continuation column would waste paper and hinder reading.
            story += [BalancedColumns(facts,nCols=2,innerPadding=24,needed=120),
                Spacer(1,14),HRFlowable(width='100%',thickness=.5,color=LINE,spaceAfter=18)]
            story += narrative
        elif facts and narrative:
            # Both cells can split. Long notes never shrink, clip, or disappear.
            columns = Table([[facts,narrative]],colWidths=[159,WIDTH-159],
                splitByRow=1,splitInRow=1,hAlign='LEFT')
            columns.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                ('BACKGROUND',(0,0),(0,-1),CREAM),('LEFTPADDING',(0,0),(0,-1),14),
                ('RIGHTPADDING',(0,0),(0,-1),14),('LEFTPADDING',(1,0),(1,-1),25),
                ('RIGHTPADDING',(1,0),(1,-1),0),('TOPPADDING',(0,0),(-1,-1),15),
                ('BOTTOMPADDING',(0,0),(-1,-1),9)]))
            first_space=A4[1]-72-90-sum(item.wrap(WIDTH,2000)[1]+item.getSpaceBefore()+item.getSpaceAfter() for item in story)
            if columns.wrap(WIDTH,2000)[1]>first_space:
                # Don't carry a spent, empty sidebar onto a second page.
                # Reflow facts above an extended note instead.
                story += [BalancedColumns(facts,nCols=2,innerPadding=24,needed=120),
                    HRFlowable(width='100%',thickness=.5,color=LINE,spaceBefore=12,spaceAfter=18)]
                story += narrative
            else:
                columns.spaceAfter=14
                story.append(columns)
        else:
            story += narrative or facts
        story += section('Downloads','Downloads',row.get('free_downloads'))
        if row.get('score_available')=='yes' and row.get('score_file'):
            story += section('Available score','Verfügbare Noten',row.get('score_note'))
            paths = [v.strip() for v in row['score_file'].splitlines() if v.strip()]
            titles = (row.get('score_file_titles') or '').splitlines()
            from urllib.parse import urljoin
            for index,path in enumerate(paths):
                title = titles[index].strip() if index<len(titles) and titles[index].strip() else t('Download score','Noten herunterladen')+((' '+str(index+1)) if len(paths)>1 else '')
                story.append(link(title,urljoin(site,path.lstrip('/'))))
            story += p(t('Suggested donation','Empfohlene Spende')+': £'+str(row.get('score_suggested_donation') or '0')
                +t(' (a £0 download is also available).',' (ein Download für £0 ist ebenfalls möglich).'))

        performances = p(row.get('other_performances'))
        if performances:
            story += [PageBreak() if len(plain(strip(row.get('other_performances'))))>1000 else CondPageBreak(220),Paragraph(t('Other performances','Weitere Aufführungen'),styles['heading']),
                section_rule()]
            story.append(BalancedColumns(performances,nCols=2,innerPadding=22,
                leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,needed=120))

        ids = list(dict.fromkeys(r['recording_id'] for r in tables['catalogue_recordings']
            if r['catalogue_id']==row['id'] and r['recording_id'] in recordings))
        if ids:
            story += [PageBreak(),Paragraph(t('Recordings','Aufnahmen'),styles['heading']),
                section_rule()]
            for index,id in enumerate(ids):
                record = recordings[id]
                url = site+lang_path+'recordings/'+id+'/'
                title = Paragraph('<link href="'+url+'" color="#29252a">'
                    +html.escape(plain(strip(record['title'])))+'</link>',styles['record'])
                content = p(record.get('detail'))
                head = [Paragraph(f'{index+1:02d}',styles['label']),title]
                cover = cover_bytes(record.get('cover') or '')
                if cover:
                    # Let short album metadata sit beside the artwork; leave
                    # long programme lists to flow across the page below it.
                    used = 0
                    while content and used<2:
                        _, height = content[0].wrap(WIDTH-104,1000)
                        if height>33:break
                        head.append(content.pop(0));used+=1
                    data,(w,h) = cover
                    image = Image(io.BytesIO(data),width=82*w/max(w,h),height=82*h/max(w,h))
                    image.hAlign='LEFT'
                    block = Table([[image,head]],colWidths=[104,WIDTH-104])
                    block.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                        ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),
                        ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
                    header = [block,Spacer(1,13)]
                else:
                    header = head
                # Do not orphan a cover/title at the foot of a page.
                if len(content)>12:
                    record_body=ParagraphStyle('programme',parent=body,fontSize=10.2,leading=14.5,spaceAfter=2)
                    columns=[Paragraph(item.text,record_body) for item in content]
                    # Attach the album link to the last programme paragraph so
                    # it cannot become a page by itself.
                    columns[-1]=Paragraph(content[-1].text+'<br/><link href="'+url+'" color="#792858">'
                        +html.escape(t('View recording','Aufnahme ansehen'))+'</link>',record_body)
                    if index:
                        heights=[item.wrap((WIDTH-22)/2,2000)[1]+item.getSpaceAfter() for item in columns]
                        balanced=min(max(sum(heights[:i]),sum(heights[i:])) for i in range(1,len(heights)))
                        estimate=sum(item.wrap(WIDTH,2000)[1]+item.getSpaceAfter() for item in header)+balanced+4
                        if estimate<650:story.append(CondPageBreak(estimate))
                    story.append(KeepTogether(header))
                    story.append(BalancedColumns(columns,nCols=2,innerPadding=22,
                        leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,needed=125))
                elif content and sum(item.wrap(WIDTH,2000)[1]+item.getSpaceAfter() for item in content)<400:
                    story.append(KeepTogether(header+content+[link(t('View recording','Aufnahme ansehen'),url)]))
                elif content:
                    story.append(KeepTogether(header+[content[0]]))
                    if len(content)>1:
                        story += content[1:-1]
                        story.append(KeepTogether([content[-1],link(t('View recording','Aufnahme ansehen'),url)]))
                    else:
                        story.append(link(t('View recording','Aufnahme ansehen'),url))
                else:
                    story.append(KeepTogether(header+[link(t('View recording','Aufnahme ansehen'),url)]))
                if index+1<len(ids):
                    story += [HRFlowable(width='100%',thickness=.5,color=LINE,spaceAfter=17),CondPageBreak(150)]

        footer_style = ParagraphStyle('footer',parent=styles['small'],fontSize=7.2,leading=10,textColor=MUTED)
        footer = Paragraph('Hans Gál · '+html.escape(work_title),footer_style)
        _,footer_height = footer.wrap(WIDTH-40,A4[1])
        footer_line = 27+footer_height+10
        def furniture(canvas,doc):
            canvas.saveState()
            canvas.setTitle(work_title+' · Hans Gál')
            canvas.setAuthor('The Hans Gál Society')
            canvas.setSubject('Folio work notes / '+language)
            canvas.setFillColor(PLUM);canvas.setFont(bold,8)
            canvas.drawString(44,A4[1]-36,'THE HANS GÁL SOCIETY')
            canvas.setFillColor(MUTED);canvas.setFont(font,8)
            canvas.drawRightString(A4[0]-44,A4[1]-36,t('HANS GÁL · WORK NOTES','HANS GÁL · WERKINFORMATION'))
            canvas.setStrokeColor(PLUM);canvas.setLineWidth(.5)
            canvas.line(44,A4[1]-52,A4[0]-44,A4[1]-52)
            canvas.setStrokeColor(LINE);canvas.line(44,footer_line,A4[0]-44,footer_line)
            footer.drawOn(canvas,44,27)
            canvas.setFillColor(PLUM);canvas.setFont(font,7.2)
            canvas.drawString(44,14,t('View this work online','Dieses Werk online ansehen'))
            canvas.setFont(font,8);canvas.drawRightString(A4[0]-44,27,str(doc.page))
            canvas.linkURL(work_url,(44,12,A4[0]-85,footer_line),relative=0)
            canvas.restoreState()
        doc = SimpleDocTemplate(str(folder/(row['id']+'.pdf')),pagesize=A4,
            rightMargin=38,leftMargin=38,topMargin=72,bottomMargin=footer_line+14,
            pageCompression=1,invariant=1)
        doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
    return len(tables['catalogue'])
