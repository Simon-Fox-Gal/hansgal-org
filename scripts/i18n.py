"""Bilingual editorial fields; shared identifiers, facts and assets never localize."""
FIELDS={
 'menu':['title','lead','body'],'catalogue':['title','description','movements','further_details','orchestration','availability','first_performance','other_performances','other_versions','score_note'],
 'recording':['title','detail','review'],'photos':['title'],'faqs':['question','answer'],
 'properties':['value'],'heading':['body'],'category':['name'],'audio_sample':['title','details'],
 'thumbnail':['title'],'photos_category':['name'],
}
UI={
 'ABOUT HANS G&Aacute;L':'ÜBER HANS GÁL','NEWS':'AKTUELLES','WORKS':'WERKE','RECORDINGS':'AUFNAHMEN',
 'BOOKS/ARTICLES':'BÜCHER/ARTIKEL','AUDIO SAMPLES':'HÖRPROBEN','PUBLISHERS':'VERLAGE','BIBLIOGRAPHY':'BIBLIOGRAFIE',
 'PHOTOS':'FOTOS','CONTACTS':'KONTAKT','HANS G&Aacute;L SOCIETY':'HANS-GÁL-GESELLSCHAFT','COMMENTS':'KOMMENTARE','DONATE':'SPENDEN',
 'PERFORMANCES':'AUFFÜHRUNGEN','IMAGES':'BILDER','FREE DOWNLOADS':'KOSTENLOSE DOWNLOADS',
 'Duration:':'Dauer:','Publisher:':'Verlag:','First performance:':'Uraufführung:','Other performances:':'Weitere Aufführungen:',
 'Please choose a sample':'Bitte wählen Sie eine Hörprobe','Audio Sample(s)':'Hörprobe(n)','Switch to:':'Ansicht wechseln:',
 'Cover List':'Coverliste','Cover Flow':'Coverkarussell','No results.':'Keine Ergebnisse.','No result':'Kein Ergebnis',
 'Download PDF':'PDF herunterladen','Add to score basket':'Zum Notenkorb hinzufügen','View score basket':'Notenkorb ansehen',
 'Downloadable score':'Noten zum Herunterladen','Score basket':'Notenkorb','Loading scores…':'Noten werden geladen…',
}
def localize(tables):
 import copy
 result=copy.deepcopy(tables)
 for table,fields in FIELDS.items():
  for row in result.get(table,[]):
   for field in fields:
    if row.get(field+'_de') not in (None,''):row[field]=row[field+'_de']
 return result

def translate_template(source):
 # Only template source is processed; authored content uses its own locale fields.
 for en,de in sorted(UI.items(),key=lambda pair:-len(pair[0])):source=source.replace(en,de)
 return source
