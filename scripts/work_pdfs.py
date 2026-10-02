"""Build bilingual, printable work notes directly from the catalogue tables."""
import html,pathlib,re
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,HRFlowable

ROOT=pathlib.Path(__file__).resolve().parents[1]
PLUM=colors.HexColor('#792858');INK=colors.HexColor('#29252a');GREEN=colors.HexColor('#215d42')
for name,file in [('Edition','Vera.ttf'),('Edition-Bold','VeraBd.ttf'),('Edition-Italic','VeraIt.ttf'),('Edition-BoldItalic','VeraBI.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(pathlib.Path(reportlab.__file__).parent/'fonts'/file)))
pdfmetrics.registerFontFamily('Edition',normal='Edition',bold='Edition-Bold',italic='Edition-Italic',boldItalic='Edition-BoldItalic')

class Copy(HTMLParser):
 def __init__(self,source,site):
  super().__init__(convert_charrefs=True);self.parts=[];self.skip=0;self.site=site;self.anchor=[];self.feed(source or '')
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('script','style'):self.skip+=1
  if self.skip:return
  if tag in ('p','div','br','li','tr','h1','h2','h3','blockquote'):self.parts.append('\n')
  if tag=='td':self.parts.append(' ')
  if tag in ('b','strong'):self.parts.append('<b>')
  if tag in ('i','em'):self.parts.append('<i>')
  if tag=='a':
   url=urljoin(self.site,a.get('href',''))
   ok=urlsplit(url).scheme in ('http','https','mailto');self.anchor.append(ok)
   if ok:self.parts.append('<link href="'+html.escape(url,quote=True)+'" color="#792858">')
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip=max(0,self.skip-1);return
  if self.skip:return
  if tag in ('b','strong'):self.parts.append('</b>')
  if tag in ('i','em'):self.parts.append('</i>')
  if tag=='a' and self.anchor:
   if self.anchor.pop():self.parts.append('</link>')
  if tag in ('p','div','li','tr','h1','h2','h3','blockquote'):self.parts.append('\n')
 def handle_data(self,s):
  if not self.skip:self.parts.append(html.escape(s))

def plain(s):return html.unescape(re.sub('<[^>]*>','',s or '')).strip()
def download_filename(value):
 title=re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', plain(value))
 title=re.sub(r'\s+', ' ',title).strip(' .-')[:160].rstrip(' .-')
 return 'Hans Gál - '+(title or 'Work notes')+'.pdf'

def paragraphs(value,style,site,strip):
 # Legacy HTML is occasionally unbalanced. Reflow text safely while retaining
 # every textual value; append explicit link labels separately below.
 parser=Copy(strip(value),site)
 text=''.join(parser.parts)
 # Keep source paragraph breaks but discard malformed inline nesting before
 # handing text to ReportLab's stricter XML parser.
 text=re.sub(r'</?(?:b|i|link)\b[^>]*>','',text)
 return [Paragraph(line,style) for line in re.split(r'\n\s*\n|\n',text) if plain(line).strip()]

def build_work_pdfs(tables,out,language,base_path,strip):
 de=language=='de';t=lambda en,deutsch:deutsch if de else en
 site='https://simon-fox-gal.github.io'+base_path+'/'
 folder=out/'storage/work-notes'/language;folder.mkdir(parents=True,exist_ok=True)
 body=ParagraphStyle('body',fontName='Edition',fontSize=10.5,leading=15.5,textColor=INK,spaceAfter=7,splitLongWords=True)
 title=ParagraphStyle('title',parent=body,fontName='Edition',fontSize=25,leading=31,textColor=PLUM,spaceAfter=14)
 sub=ParagraphStyle('subtitle',parent=body,fontSize=12,leading=18,textColor=GREEN,spaceAfter=16)
 heading=ParagraphStyle('section',parent=body,fontName='Edition-Bold',fontSize=12,leading=17,textColor=PLUM,spaceBefore=17,spaceAfter=8,keepWithNext=True)
 small=ParagraphStyle('small',parent=body,fontSize=9,leading=13,textColor=GREEN)
 recordings={r['id']:r for r in tables['recording']}
 for row in tables['catalogue']:
  work_url=site+('de/' if de else '')+'works/show/'+row['id']+'/'
  story=[Paragraph(t('HANS GÁL · WORK NOTES','HANS GÁL · WERKINFORMATION'),small),Spacer(1,12)]
  story+=paragraphs(row['title'],title,site,strip)
  desc=strip(row.get('description') or '')
  if row.get('opus_no') not in (None,'','0'):desc+=' · Opus '+row['opus_no']
  if row.get('year_of_composition') not in (None,'','0'):desc+=' · '+row['year_of_composition']
  story+=paragraphs(desc,sub,site,strip)
  story.append(HRFlowable(width='100%',thickness=1,color=PLUM,spaceAfter=14))
  def section(en,ger,value):
   content=paragraphs(value,body,site,strip)
   if content:story.append(Paragraph(t(en,ger),heading));story.extend(content)
  section('Movements','Sätze',row.get('movements'))
  section('Instrumentation','Besetzung',row.get('orchestration'))
  if row.get('duration') not in (None,'','0'):section('Duration','Dauer',row['duration'].rstrip("'′ ")+' '+t('minutes','Minuten'))
  section('Publisher','Verlag',row.get('publisher'))
  section('Availability','Verfügbarkeit',row.get('availability'))
  section('Other versions','Weitere Fassungen',row.get('other_versions'))
  section('First performance','Uraufführung',row.get('first_performance'))
  section('Other performances','Weitere Aufführungen',row.get('other_performances'))
  section('About the work','Über das Werk',row.get('further_details'))
  section('Downloads','Downloads',row.get('free_downloads'))
  for field,en,ger in [('purchase_url','Printed music','Gedruckte Noten'),('hire_url','Hire materials','Leihmaterial'),('score_purchase_download_url','Digital sheet music','Digitale Noten')]:
   for url in (row.get(field) or '').splitlines():
    if url.strip():story.append(Paragraph('<link href="'+html.escape(url.strip(),quote=True)+'" color="#792858">'+t(en,ger)+'</link>',body))
  if row.get('score_available')=='yes' and row.get('score_file'):
   section('Available score','Verfügbare Noten',row.get('score_note'))
   score=urljoin(site,row['score_file'].lstrip('/'))
   story.append(Paragraph('<link href="'+html.escape(score,quote=True)+'" color="#792858">'+t('Download score','Noten herunterladen')+'</link>',body))
   story.append(Paragraph(t('Suggested donation','Empfohlene Spende')+': £'+str(row.get('score_suggested_donation') or '0')+t(' (a £0 download is also available).',' (ein Download für £0 ist ebenfalls möglich).'),body))
  ids=list(dict.fromkeys(r['recording_id'] for r in tables['catalogue_recordings'] if r['catalogue_id']==row['id'] and r['recording_id'] in recordings))
  if ids:
   story.append(Paragraph(t('Recordings','Aufnahmen'),heading))
   for id in ids:
    record=recordings[id];url=site+('de/' if de else '')+'recordings/'+id+'/'
    story.append(Paragraph('<link href="'+url+'" color="#792858"><b>'+html.escape(plain(strip(record['title'])))+'</b></link>',body))
    story+=paragraphs(record['detail'],body,site,strip);story.append(Spacer(1,7))
  story.append(Spacer(1,15));story.append(Paragraph('<link href="'+work_url+'" color="#215d42">'+t('View this work online','Dieses Werk online ansehen')+'</link>',small))
  footer=Paragraph('Hans Gál · '+html.escape(plain(strip(row['title']))),ParagraphStyle('footer',fontName='Edition',fontSize=8,leading=11,textColor=GREEN))
  footer_width=A4[0]-118
  _,footer_height=footer.wrap(footer_width,A4[1])
  footer_line=28+footer_height+8
  def furniture(canvas,doc):
   canvas.saveState();canvas.setTitle(plain(strip(row['title']))+' · Hans Gál');canvas.setAuthor('The Hans Gál Society')
   canvas.drawImage(str(ROOT/'public/gfx/images/hansgal-logo-website.png'),42,A4[1]-69,width=157,height=58.5,mask='auto',preserveAspectRatio=True)
   canvas.setStrokeColor(PLUM);canvas.setLineWidth(.6);canvas.line(42,footer_line,A4[0]-42,footer_line)
   canvas.setFont('Edition',8);canvas.setFillColor(GREEN);footer.drawOn(canvas,42,28);canvas.drawRightString(A4[0]-42,28,str(doc.page));canvas.restoreState()
  doc=SimpleDocTemplate(str(folder/(row['id']+'.pdf')),pagesize=A4,rightMargin=46,leftMargin=46,topMargin=91,bottomMargin=footer_line+16,pageCompression=1,invariant=1)
  doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
 return len(tables['catalogue'])
