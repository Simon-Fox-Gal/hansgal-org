"""Illustrated Folio books generated from the same localized biography as the site."""
import copy,html,io,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (BaseDocTemplate,PageTemplate,Frame,Spacer,PageBreak,
    KeepTogether,Image,Table,TableStyle,HRFlowable,CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfdoc import PDFString
from reportlab.pdfgen.canvas import Canvas
from pdf_typography import Paragraph
from pdf_folio import register_fonts,INK,PLUM,GREEN,MUTED,CREAM,LINE
from biography import labels,chapters,illustrations,reading_body,GROUPS
from languages import prefix

ROOT=Path(__file__).resolve().parents[1]
PAGE=(170*mm,240*mm)
MARGIN=46
WIDTH=PAGE[0]-2*MARGIN

class BookCopy(HTMLParser):
 """Convert legacy HTML to balanced, linked, styled paragraphs, preserving text."""
 def __init__(self,source,site,chapter_id=''):
  super().__init__(convert_charrefs=True)
  self.blocks=[];self.parts=[];self.skip=0;self.quote=0;self.italic=0;self.bold=0;self.link=[];self.site=site;self.chapter_id=chapter_id
  self.feed(source or '');self.flush()
 def flush(self):
  value=''.join(self.parts).strip();self.parts=[]
  if html.unescape(re.sub('<[^>]*>','',value)).strip():self.blocks.append(('quote' if self.quote else 'body',value))
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('script','style','head'):self.skip+=1
  if self.skip:return
  if tag in ('p','div','br','li','tr','h1','h2','h3','blockquote'):self.flush()
  if tag=='blockquote':self.quote+=1
  if tag in ('i','em'):self.italic+=1
  if tag in ('b','strong'):self.bold+=1
  if tag=='a':
   href=a.get('href','')
   if href.startswith('#note-'):href='#c'+self.chapter_id+'-'+href[1:]
   elif href=='#top':href=''
   else:href=urljoin(self.site,href)
   if urlsplit(href).hostname in ('hansgal.org','www.hansgal.org','hansgal.musicessences.com'):
    path=urlsplit(href).path
    if re.match(r'^/(?:works|hansgal|recordings|booksandarticles)/',path):href=urljoin(self.site,path.lstrip('/'))
   self.link.append(href if href.startswith('#c') or urlsplit(href).scheme in ('https','http','mailto') else '')
 def handle_endtag(self,tag):
  if tag in ('script','style','head'):self.skip=max(0,self.skip-1);return
  if self.skip:return
  if tag in ('p','div','li','tr','h1','h2','h3','blockquote'):self.flush()
  if tag=='blockquote':self.quote=max(0,self.quote-1)
  if tag in ('i','em'):self.italic=max(0,self.italic-1)
  if tag in ('b','strong'):self.bold=max(0,self.bold-1)
  if tag=='a' and self.link:self.link.pop()
 def handle_data(self,value):
  if self.skip:return
  text=html.escape(re.sub(r'\s+',' ',value))
  if self.italic:text='<i>'+text+'</i>'
  if self.bold:text='<b>'+text+'</b>'
  if self.link and self.link[-1]:text='<link href="'+html.escape(self.link[-1],quote=True)+'" color="#792858">'+text+'</link>'
  self.parts.append(text)

def printable_image(src,maxwidth,maxheight):
 path=ROOT/'public'/src.lstrip('/')
 with PILImage.open(path) as im:
  im=im.convert('RGB');width,height=im.size
  scale=min(maxwidth/width,maxheight/height)
  im.thumbnail((1400,1400));stream=io.BytesIO();im.save(stream,format='JPEG',quality=91,optimize=True);stream.seek(0)
 return Image(stream,width=width*scale,height=height*scale,hAlign='CENTER')

class Book(BaseDocTemplate):
 def __init__(self,path,ui,styles,language,**kw):
  super().__init__(str(path),pagesize=PAGE,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=60,bottomMargin=53,
   title='Hans Gál · '+ui['book_title'],author=ui['edition'],subject=ui['book_subtitle'],pageCompression=1,**kw)
  self.ui=ui;self.styles=styles;self.language=language;self.current='';self.chapter_pages={}
  frame=Frame(MARGIN,53,WIDTH,PAGE[1]-113,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id='text')
  self.addPageTemplates(PageTemplate(id='book',frames=[frame],onPageEnd=self.furniture))
 def beforeDocument(self):self.current='';self.chapter_pages={}
 def afterFlowable(self,flow):
  if hasattr(flow,'bookmark'):
   key,title=flow.bookmark
   self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,0,False)
   if getattr(flow,'toc',False):self.notify('TOCEntry',(0,title,self.page,key));self.chapter_pages[key]=self.page
   self.current=title
 def furniture(self,c,doc):
  c._doc.Catalog.Lang=PDFString(self.language)
  if doc.page==1:return
  c.saveState();c.setStrokeColor(LINE);c.setLineWidth(.5);c.line(MARGIN,40,PAGE[0]-MARGIN,40)
  style=self.styles['running'];p=Paragraph(html.escape(self.current or self.ui['book_subtitle']),style)
  w,h=p.wrap(WIDTH-25,32);p.drawOn(c,MARGIN,PAGE[1]-32-h)
  c.setFont(self.styles['small'].fontName,8.5);c.setFillColor(GREEN);c.drawString(MARGIN,26,'Hans Gál');c.drawRightString(PAGE[0]-MARGIN,26,str(doc.page))
  c.linkRect('', 'contents',(PAGE[0]-MARGIN-28,20,PAGE[0]-MARGIN,39),relative=0,thickness=0)
  c.restoreState()

class Cover(Spacer):
 def __init__(self,ui,styles):super().__init__(WIDTH,PAGE[1]-114);self.ui=ui;self.styles=styles
 def draw(self):
  c=self.canv;ui=self.ui;c.saveState();c.setFillColor(CREAM);c.rect(-MARGIN,-54,PAGE[0],PAGE[1],fill=1,stroke=0)
  y=self.height-3
  def para(value,style,y):
   p=Paragraph(html.escape(value),style);w,h=p.wrap(WIDTH,150);p.drawOn(c,0,y-h);return y-h
  y=para(ui['edition'],self.styles['kicker'],y)-20
  y=para('Hans Gál',self.styles['covername'],y)-12
  y=para(ui['book_title'],self.styles['covertitle'],y)-12
  c.setStrokeColor(PLUM);c.setLineWidth(1);c.line(0,y,WIDTH,y);y-=16
  p=ROOT/'public/storage/photos/235d5fd74ea55c801cfc39f299ebb398.jpg'
  height=min(270,y-68);width=height*369/500;x=WIDTH-width
  c.drawImage(ImageReader(str(p)),x,y-height,width,height,mask='auto')
  para('1890',self.styles['dates'],y-14);para('1987',self.styles['dates'],y-45)
  p=Paragraph(html.escape(ui['book_subtitle']),self.styles['small']);w,h=p.wrap(max(100,x-18),100);p.drawOn(c,0,y-height+38)
  p=Paragraph(html.escape(ui['language']),self.styles['small']);w,h=p.wrap(100,30);p.drawOn(c,0,y-height+12)
  para(ui['photo'],self.styles['credit'],y-height-7)
  c.restoreState()

class LayoutProbe(BaseDocTemplate):
 """Measure chapter endings before choosing a restrained typesetting adjustment."""
 def __init__(self):
  super().__init__(io.BytesIO(),pagesize=PAGE)
  self.used=[]
  self.addPageTemplates(PageTemplate(id='probe',frames=[Frame(MARGIN,53,WIDTH,PAGE[1]-113,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)]))
 def afterPage(self):self.used.append(PAGE[1]-60-self.frame._y)

class ProbeCanvas(Canvas):
 def save(self):pass  # Layout only; cross-chapter links resolve in the final book.

class ClosingParagraph(Paragraph):
 def split(self,width,height):
  if getattr(self,'_keep_all_lines',False):return []
  parts=super().split(width,height)
  if len(parts)==2 and height>75:
   tail=parts[1].wrap(width,1000)[1]
   if tail<130:
    parts=super().split(width,max(self.style.leading*2,height-(130-tail)))
    if len(parts)==2:parts[1]._keep_all_lines=True
  return parts

def measure(flowables):
 probe=LayoutProbe();probe.build(copy.deepcopy(flowables),canvasmaker=ProbeCanvas);return probe.used

def balance_ending(flowables):
 """Avoid a chapter ending with a stray couple of lines on a fresh page."""
 heights=measure(flowables)
 if len(heights)<2 or heights[-1]>=150:return flowables
 for factor in (.97,.94,.91):
  candidate=copy.deepcopy(flowables)
  for p in candidate:
   if isinstance(p,Paragraph) and p.style.name in ('body','quote'):
    p.style=copy.copy(p.style);p.style.leading*=factor;p.style.spaceAfter*=factor
  new=measure(candidate)
  if len(new)<len(heights):return candidate
 # If copy-fitting would be conspicuous, keep the final short paragraphs together.
 for count in range(2,min(6,len(flowables))):
  tail=flowables[-count:]
  if not all(isinstance(p,Paragraph) for p in tail):break
  total=sum(p.wrap(WIDTH,1000)[1]+p.getSpaceAfter()+p.getSpaceBefore() for p in tail)
  if total>350:break
  candidate=flowables[:-count]+[KeepTogether(tail)]
  if measure(candidate)[-1]>=150:return candidate
 candidate=copy.deepcopy(flowables)
 if isinstance(candidate[-1],Paragraph):
  candidate[-1].__class__=ClosingParagraph
  if measure(candidate)[-1]>=120:return candidate
 return flowables

def build_biography_pdf(tables,out,language,strip):
 register_fonts();ui=labels(language);ja=language=='ja';font='Edition-Japanese' if ja else 'Folio-Serif';sans='Edition-Japanese' if ja else 'Edition';bold='Edition-Japanese' if ja else 'Edition-Bold'
 # Gelasio's upstream regular face is intentionally used without synthesized italics.
 # Explicit source emphasis falls back to the embedded italic sans family.
 pdfmetrics.registerFontFamily('Folio-Serif',normal='Folio-Serif',bold='Edition-Bold',italic='Edition-Italic',boldItalic='Edition-BoldItalic')
 body=ParagraphStyle('body',fontName=font,fontSize=11.5 if not ja else 10.7,leading=17.5 if not ja else 18.5,textColor=INK,spaceAfter=9,allowWidows=0,allowOrphans=0,wordWrap='CJK' if ja else None,rightIndent=12 if ja else 0)
 styles={'body':body}
 def s(name,**kw):styles[name]=ParagraphStyle(name,parent=body,**kw);return styles[name]
 s('quote',fontSize=11.4,leading=17.5,leftIndent=17,rightIndent=17,spaceBefore=5,spaceAfter=12,textColor=GREEN)
 s('kicker',fontName=bold,fontSize=9,leading=14,textColor=PLUM,spaceAfter=12,keepWithNext=True)
 s('title',fontSize=30,leading=38,spaceAfter=24,keepWithNext=True)
 s('heading',fontSize=20,leading=27,spaceAfter=16,spaceBefore=18,keepWithNext=True)
 s('notehead',fontName=bold,fontSize=11,leading=16,spaceBefore=14,spaceAfter=6,keepWithNext=True)
 s('small',fontName=sans,fontSize=9,leading=13.5,textColor=MUTED,spaceAfter=8)
 s('caption',fontName=sans,fontSize=8.8,leading=13,textColor=MUTED,spaceBefore=8,spaceAfter=12)
 s('running',fontName=sans,fontSize=7.5,leading=11,textColor=MUTED,spaceAfter=0)
 s('toc',fontName=sans,fontSize=10.6,leading=16,spaceBefore=7,spaceAfter=4,rightIndent=22)
 s('covername',fontSize=51,leading=57,spaceAfter=0)
 s('covertitle',fontSize=25 if ja else 29,leading=37,spaceAfter=0)
 s('dates',fontName=sans,fontSize=20,leading=28,textColor=GREEN)
 s('credit',fontName=sans,fontSize=7,leading=10,textColor=MUTED)
 folder=out/'storage/biography';folder.mkdir(parents=True,exist_ok=True);path=folder/('Hans-Gal-Biography-'+language+'.pdf')
 doc=Book(path,ui,styles,language);story=[Cover(ui,styles),PageBreak()];site='https://hansgal.org'+prefix(language)+'/'
 def title(text,key,toc=False):
  p=Paragraph(html.escape(text),styles['title']);p.bookmark=(key,text);p.toc=toc;return p
 story+=[title(ui['contents'],'contents')]
 toc=TableOfContents();toc.levelStyles=[styles['toc']];toc.dotsMinLevel=0;story+=[toc,PageBreak()]
 story+=[title(ui['introduction'],'introduction',True)]
 intro=next(r['body'] for r in tables['heading'] if r['id']=='1')
 story += [Paragraph(value,styles[kind]) for kind,value in BookCopy(strip(intro),site).blocks]
 story += [Spacer(1,16),HRFlowable(width='100%',thickness=.6,color=PLUM),Spacer(1,16),Paragraph(ui['book_note'],styles['small']),Paragraph('<link href="'+site+'hansgal/" color="#792858">hansgal.org</link>',styles['small'])]
 rows=chapters(tables)
 for row in rows:
  id=row['id'];chapter_story=[Paragraph(ui['chapter']+' '+str(row['number']).zfill(2),styles['kicker']),title(row['heading'],'chapter-'+id,True)]
  body,notes=reading_body(strip(row['body']),row['body'])
  for kind,value in BookCopy(body,site,id).blocks:chapter_story.append(Paragraph(value,styles[kind]))
  if notes:
   chapter_story += [Paragraph(ui['notes'],styles['heading'])]
   for note in notes:
    chapter_story.append(Paragraph('<a name="c'+id+'-note-'+note['id']+'"/>'+html.escape(note['title']),styles['notehead']))
    chapter_story += [Paragraph(value,styles[kind]) for kind,value in BookCopy(note['body'],site,id).blocks]
  story += [PageBreak()]+balance_ending(chapter_story)
  images=illustrations(tables,id)
  if images:
   columns=3 if len(images)>=3 else len(images)
   gallery=[Paragraph(ui['illustrations'],styles['heading'])]
   for start in range(0,len(images),columns):
    pair=images[start:start+columns];col=WIDTH/columns
    cells=[]
    for item in pair:
     picture=printable_image(item['src'],col-(12 if columns>1 else 0),190 if columns>1 else 280)
     cells.append([picture,Paragraph(html.escape(item['caption']),styles['caption'])])
    table=Table([cells],colWidths=[col]*len(pair),hAlign='LEFT',spaceAfter=10)
    table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),12 if columns>1 else 0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    gallery.append(table)
   story.append(KeepTogether(gallery))
 story += [Spacer(1,24),HRFlowable(width='25%',hAlign='LEFT',thickness=1,color=PLUM),Paragraph(ui['resources'],styles['heading'])]
 for id,key in [('26','chronology'),('12','family'),('59','sketchbook')]:story.append(Paragraph('<link href="'+site+'hansgal/'+id+'/" color="#792858">'+ui[key]+'</link>',styles['body']))
 doc.multiBuild(story)
 print('Biography PDF:',language,path.stat().st_size,'bytes;',len(rows),'chapters')
 return path
