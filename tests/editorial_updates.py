"""Exact field exceptions to the immutable migration preservation check.

Hashes record the published editorial revision, without private inbox content.
Everything outside this explicit set remains covered by the original baseline.
"""
import hashlib,json,pathlib
EXCEPTIONS=json.loads((pathlib.Path(__file__).parent/'editorial-updates.json').read_text(encoding='utf8'))
def approved(path,id,key,value):
 expected=EXCEPTIONS.get(path,{}).get(str(id),{}).get(key)
 return expected==hashlib.sha256(json.dumps(value,ensure_ascii=True).encode()).hexdigest()
