"""Readback checks for all biography routes, books, notes and illustrations."""
import json,pathlib,re,sys
from html.parser import HTMLParser
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from biography import chapters,illustrations,reading_body,labels
from biography_pdfs import BookCopy
from build import stripcslashes
from i18n import localize
class Text(HTMLParser):
 def __init__(self,value):super().__init__(convert_charrefs=True);self.bits=[];self.skip=0;self.feed(value)
 def handle_starttag(self,tag,attrs):
  if tag in ('script','head','style'):self.skip+=1
 def handle_endtag(self,tag):
  if tag in ('script','head','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip:self.bits.append(s)
def norm(value):return re.sub(r'\s+','',value)
def plain(value):return ''.join(Text(value).bits)
data={p.stem:json.loads(p.read_text(encoding='utf8')) for p in (ROOT/'content').glob('*.json') if p.stem in ['menu','heading','photos','thumbnail']}
for lang in ('en','de','fr','ja'):
 tables=localize(data,lang) if lang!='en' else data;rows=chapters(tables);path=ROOT/'dist/storage/biography'/('Hans-Gal-Biography-'+lang+'.pdf');reader=PdfReader(path);pref='' if lang=='en' else lang+'/'
 assert len(rows)==26
 assert len(reader.outline)==28,(lang,'bookmarks')
 assert reader.trailer['/Root'].get('/Lang')==lang
 pages=[page.extract_text() for page in reader.pages]
 assert all(p.strip() for p in pages),(lang,'blank page')
 destinations={k:reader.get_destination_page_number(v) for k,v in reader.named_destinations.items()}
 # ReportLab uses direct outline destinations rather than a name tree.
 chapter_starts=[reader.get_destination_page_number(d) for d in reader.outline[2:]]
 assert len(set(chapter_starts))==26
 count=0;note_count=0
 for index,row in enumerate(rows):
  id=row['id'];markup=(ROOT/'dist'/pref/'hansgal'/id/'index.html').read_text(encoding='utf8')
  assert 'class="bio-toolbar"' in markup and 'biography.css' in markup
  assert re.search('href="[^\"]*/storage/biography/Hans-Gal-Biography-'+lang+r'\.pdf"',markup)
  assert 'javascript:text' not in markup
  body,notes=reading_body(stripcslashes(row['body']),row['body']);note_count+=len(notes)
  authored=norm(plain(body));visible=norm(plain(re.search(r'<article id="chapter-text"[^>]*>(.*?)</article>',markup,re.S)[1]))
  assert authored==visible,(lang,id,'web text mismatch')
  for n in notes:assert norm(plain(n['body'])) in norm(plain(markup)),(lang,id,'note omitted')
  start=chapter_starts[index];end=chapter_starts[index+1] if index+1<len(rows) else len(pages)
  # Remove running chapter headings and furniture from the extracted content.
  content=[]
  for number in range(start,end):
   lines=pages[number].splitlines()
   # Running heading, Society mark and page number follow the page's body.
   marker=next(i for i,line in enumerate(lines) if line=='Hans Gál')
   content.append('\n'.join(lines[:marker-1]))
  content=norm('\n'.join(content));cursor=0
  expected=BookCopy(body,'https://hansgal.org/',id).blocks
  for note in notes:expected+=BookCopy(note['body'],'https://hansgal.org/',id).blocks
  for kind,value in expected:
   text=norm(plain(value));position=content.find(text,cursor)
   assert position>=0,(lang,id,'PDF paragraph missing',text[:100])
   cursor=position+len(text)
  for image in illustrations(tables,id):
   assert image['src'] in markup and norm(plain(image['caption'])) in content,(lang,id,'image/caption omitted')
   count+=1
 assert count==34,(lang,count)
 assert note_count==18,(lang,note_count)
 print('PASS:',lang,len(rows),'chapters;',len(pages),'pages;',count,'illustrations;',note_count,'linked notes; exact web prose and complete ordered PDF paragraphs.')
