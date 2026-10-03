"""Bilingual editorial fields; shared identifiers, facts and assets never localize."""
FIELDS={
 'menu':['title','lead','body'],'catalogue':['title','description','movements','further_details','orchestration','availability','first_performance','other_performances','other_versions','free_downloads','score_note','score_file_titles'],
 'recording':['title','detail','review'],'photos':['title'],'faqs':['question','answer'],
 'properties':['value'],'heading':['body'],'category':['name'],'audio_sample':['title','details','track_titles'],
 'thumbnail':['title'],'photos_category':['name'],
}
UI={
 'Select a work':'Werk auswählen','SEARCH RESULT':'SUCHERGEBNIS',
 'If you have any comments about our website, or wish to get in touch for any reason, please feel free to contact us using the form below:':'Wenn Sie Anmerkungen zu unserer Website haben oder aus einem anderen Grund mit uns in Verbindung treten möchten, nutzen Sie bitte das folgende Formular:',
 "value='Submit'":"value='Absenden'",
 'JavaScript is needed for the basket. Individual score PDFs remain available on each work’s page.':'Für den Notenkorb wird JavaScript benötigt. Einzelne Noten-PDFs können weiterhin auf der jeweiligen Werkseite heruntergeladen werden.',
 'Reflections — Brahms and Gál: Piano Quartets, Confringo Klavierquartett (2026)':'Reflections — Brahms und Gál: Klavierquartette, Confringo Klavierquartett (2026)',
 'Hans Gál: Music for Voices, Volume Three (2025)':'Hans Gál: Vokalmusik, Folge drei (Music for Voices, Volume Three), 2025',
 'Hans Gál: Music for Viola, Volume Two (2025)':'Hans Gál: Musik für Viola, Folge zwei (Music for Viola, Volume Two), 2025',
 'ABOUT HANS G&Aacute;L':'ÜBER HANS GÁL','NEWS':'AKTUELLES','WORKS':'WERKE','RECORDINGS':'AUFNAHMEN',
 'BOOKS/ARTICLES':'BÜCHER/ARTIKEL','AUDIO SAMPLES':'HÖRPROBEN','PUBLISHERS':'VERLAGE','BIBLIOGRAPHY':'BIBLIOGRAFIE',
 'PHOTOS':'FOTOS','CONTACTS':'KONTAKT','HANS G&Aacute;L SOCIETY':'HANS-GÁL-GESELLSCHAFT','COMMENTS':'KOMMENTARE','DONATE':'SPENDEN',
 'PERFORMANCES':'AUFFÜHRUNGEN','IMAGES':'BILDER','FREE DOWNLOADS':'KOSTENLOSE DOWNLOADS',
 'Duration:':'Dauer:','Publisher:':'Verlag:','First performance:':'Uraufführung:','Other performances:':'Weitere Aufführungen:',
 'Please choose a sample':'Bitte wählen Sie eine Hörprobe','Audio Sample(s)':'Hörprobe(n)','Switch to:':'Ansicht wechseln:',
 'Cover List':'Coverliste','Cover Flow':'Coverkarussell','No results.':'Keine Ergebnisse.','No result':'Kein Ergebnis',
 'Download PDF':'PDF herunterladen','Add to basket':'Zum Notenkorb hinzufügen','View basket':'Notenkorb ansehen',
 'Downloadable score':'Noten zum Herunterladen','Basket':'Notenkorb','Loading scores…':'Noten werden geladen…',
 'Select a genre and/or instrument and click "Display":':'Wählen Sie eine Gattung und/oder ein Instrument und klicken Sie auf „Anzeigen“:',
 'All genres':'Alle Gattungen','All instruments':'Alle Instrumente','value="Display"':'value="Anzeigen"',
 'Search Op.':'Opus suchen','Search Title':'Titel suchen','Search Yr':'Jahr suchen','Search Publisher':'Verlag suchen',
 'value="Go"':'value="Suchen"','>Title<':'>Titel<','>Description<':'>Besetzung / Beschreibung<','>Year<':'>Jahr<','>Publisher<':'>Verlag<',
 'value="Search"':'value="Suche"',"this.value=='Search'":"this.value=='Suche'","this.value='Search'":"this.value='Suche'",
 "Chronology of G&aacute;l's life":'Gáls Leben in Daten','Family tree':'Stammbaum',
 'Your browser does not support the HTML5 Audio element.':'Ihr Browser unterstützt dieses Audioformat nicht.',
 'A not-for-profit information site for the composer Hans Gál (1890-1987), jointly managed by The Hans Gál Society and Gál\'s family.':'Eine gemeinnützige Informationsseite über den Komponisten Hans Gál (1890–1987), gemeinsam betreut von der Hans-Gál-Gesellschaft und Gáls Familie.',
}
def localize(tables):
 import copy
 result=copy.deepcopy(tables)
 for table,fields in FIELDS.items():
  for row in result.get(table,[]):
   for field in fields:
    if row.get(field+'_de') not in (None,''):row[field]=row[field+'_de']
 # Publisher identities and dates remain shared editorial data; only the
 # surrounding availability wording is localized in the German display copy.
 for row in result.get('catalogue',[]):
  if row.get('publisher'):
   value=row['publisher']
   for en,de in [('First published by','Zuerst veröffentlicht bei'),('Suite only:','Nur die Suite:'),('orch. Parts:','Orchesterstimmen:'),('pending publication by','Veröffentlichung vorgesehen bei'),('Pending publication by','Veröffentlichung vorgesehen bei'),('now also','jetzt auch'),('now private','jetzt in Privatbesitz'),('now','jetzt'),('Unpublished','Unveröffentlicht'),('successors','Nachfolger'),('Vienna','Wien')]:
    value=value.replace(en,de)
   row['publisher']=value
 return result

def translate_template(source):
 # Only template source is processed; authored content uses its own locale fields.
 for en,de in sorted(UI.items(),key=lambda pair:-len(pair[0])):source=source.replace(en,de)
 return source
