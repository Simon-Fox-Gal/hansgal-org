"""Shared chapter order, illustration identities and accessible biography notes."""
import html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHAPTER_IDS=['1','2','9','11','27','28','29','38','39','40','41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56']
GROUPS=[(0,7,'beginnings'),(7,17,'recognition'),(17,24,'exile'),(24,26,'legacy')]

def labels(language):
 return json.loads((ROOT/'config/biography-labels.json').read_text(encoding='utf8'))[language]

def clean_title(value):
 return re.sub(r'^\s*\d+\s*[.．]\s*','',html.unescape(value or ''))

def chapters(tables):
 rows={r['id']:r for r in tables['menu']}
 return [dict(rows[id],number=i+1,heading=clean_title(rows[id]['title'])) for i,id in enumerate(CHAPTER_IDS) if rows[id]['hidden']!='yes']

def groups(rows,ui):
 return [dict(title=ui[key],chapters=[r for r in rows if start<r['number']<=end]) for start,end,key in GROUPS]

def illustrations(tables,id):
 matches=json.loads((ROOT/'config/biography-images.json').read_text())
 photos={r['id']:r for r in tables['photos']}
 images=[]
 for row in tables['thumbnail']:
  if row['menu_id']!=id:continue
  caption=row.get('title') or photos.get(matches.get(row['filename']),{}).get('title')
  if not caption:raise ValueError('Missing biography image caption: '+row['filename'])
  images.append(dict(src='/storage/thumbnails/'+row['filename'],caption=caption))
 return images

def reading_body(source,note_source=None):
 """Make the old popup notes linkable without executing authored JavaScript."""
 notes=[]
 def decode(value):
  def escaped(m):
   s=m[1]
   if s.startswith(('u','x')):return chr(int(s[1:],16))
   return {'n':'\n','r':'\r','t':'\t','b':'\b','f':'\f','v':'\v','0':'\0'}.get(s,s)
  return re.sub(r'\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|[\"\'\\/nrtbfv0])',escaped,value)
 variables={m[1]:decode(m[2]) for m in re.finditer(r'var\s+(\w+)\s*=\s*"((?:\\.|[^"\\])*)"',note_source if note_source is not None else source,re.S)}
 def note_link(m):
  value=html.unescape(m[2]);match=re.fullmatch(r"javascript:text\s*\(\s*'([^']*)'\s*,\s*(\w+)\s*\)",value)
  if not match:return m[0]
  title,key=match.groups()
  if key not in variables:raise ValueError('Missing note: '+key)
  if not any(n['id']==key for n in notes):notes.append(dict(id=key,title=title,body=variables[key]))
  return 'href='+m[1]+'#note-'+key+m[1]
 body=re.sub(r'href=([\"\'])(.*?)\1',note_link,source,flags=re.I|re.S)
 body=re.sub(r'<script\b[^>]*>.*?</script\s*>','',body,flags=re.S|re.I)
 return body,notes
