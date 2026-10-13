"""Build four-language, printable Folio notes directly from the catalogue tables."""
import html,pathlib,re
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
import reportlab
from reportlab import rl_config
rl_config.useA85=0  # Binary PDF streams avoid redundant ASCII expansion.
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pdf_typography import Paragraph
for name,file in [('Edition','Vera.ttf'),('Edition-Bold','VeraBd.ttf'),('Edition-Italic','VeraIt.ttf'),('Edition-BoldItalic','VeraBI.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(pathlib.Path(reportlab.__file__).parent/'fonts'/file)))
pdfmetrics.registerFontFamily('Edition',normal='Edition',bold='Edition-Bold',italic='Edition-Italic',boldItalic='Edition-BoldItalic')

class Copy(HTMLParser):
 def __init__(self,source,site):
  super().__init__(convert_charrefs=True);self.parts=[];self.skip=0;self.site=site;self.anchor=[];self.feed(source or '')
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ('head','script','style'):self.skip+=1
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
  if tag in ('head','script','style'):self.skip=max(0,self.skip-1);return
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
 from pdf_folio import build_folio_pdfs
 return build_folio_pdfs(tables,out,language,base_path,strip,paragraphs,plain)
