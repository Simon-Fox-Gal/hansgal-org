"""Report missing language fields without treating English fallback as translated."""
import argparse, hashlib, html, json, pathlib, re
from i18n import FIELDS
ROOT=pathlib.Path(__file__).resolve().parents[1]
TRANSLATABLE={**FIELDS,'page_text':['value']}

def inventory(language):
    items=[]
    for table,fields in TRANSLATABLE.items():
        for row in json.loads((ROOT/'content'/f'{table}.json').read_text(encoding='utf8')):
            for field in fields:
                source=row.get(field) or ''
                plain=html.unescape(re.sub(r'<[^>]*>','',source)).strip()
                if not plain:continue
                target=row.get(field+'_'+language) or ''
                items.append({'table':table,'id':row['id'],'field':field,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'status':'translated' if target.strip() else 'pending'})
    return items

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('language',choices=['de','fr','ja']);parser.add_argument('--require-complete',action='store_true');parser.add_argument('--output',type=pathlib.Path)
    args=parser.parse_args();items=inventory(args.language)
    report={'language':args.language,'total':len(items),'translated':sum(r['status']=='translated' for r in items),'pending':sum(r['status']=='pending' for r in items),'items':items}
    if args.output:args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='items'}))
    if args.require_complete and report['pending']:raise SystemExit('Translation incomplete; do not publish this language as complete.')
