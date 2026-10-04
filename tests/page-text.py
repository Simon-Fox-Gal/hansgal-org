"""The CMS text migration preserves each bilingual template phrase exactly."""
import ast,json,pathlib,re,subprocess
root=pathlib.Path(__file__).resolve().parents[1]
rows=json.loads((root/'content/page_text.json').read_text(encoding='utf8'))
assert len({r['id'] for r in rows})==len(rows)
by_id={r['id']:r for r in rows};seen=[]
pattern=re.compile(r'''\btr\(\s*((?:'(?:\\.|[^'\\])*')|(?:"(?:\\.|[^"\\])*"))\s*,\s*((?:'(?:\\.|[^'\\])*')|(?:"(?:\\.|[^"\\])*"))\s*\)''')
for path in sorted((root/'templates').glob('*.html')):
 old=subprocess.check_output(['git','show','a54d16857820c4fcdd103eb9aae50b8404d7693f:templates/'+path.name],cwd=root).decode('utf8')
 source=path.read_text(encoding='utf8');ids=re.findall(r"page_text\('([0-9]+)'\)",source)
 expected=[(ast.literal_eval(m[1]),ast.literal_eval(m[2])) for m in pattern.finditer(old)]
 assert expected==[(by_id[i]['value'],by_id[i]['value_de']) for i in ids],path.name
 iterator=iter(ids)
 assert pattern.sub(lambda m:"page_text('"+next(iterator)+"')",old)==source,path.name
 seen+=ids
assert sorted(seen)==sorted(by_id),'Missing or duplicated template reference'
print(f'PASS: all {len(rows)} English/German text pairs preserved, each used exactly once; no other template changes.')
