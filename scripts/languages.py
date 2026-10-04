"""Language routing and interface dictionaries, shared by the build and its checks."""
import functools,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'locales/languages.json').read_text(encoding='utf8'))
LANGUAGES=CONFIG['languages']
PUBLISHED=CONFIG['published']
def prefix(language):
    if language not in LANGUAGES:raise ValueError('Unsupported language: '+language)
    return '' if language=='en' else '/'+language
@functools.lru_cache
def labels(language):
    path=ROOT/'locales'/f'ui-{language}.json'
    return json.loads(path.read_text(encoding='utf8')) if path.exists() else {}
def text(language,en,de=None,strict=False):
    if language=='en':return en
    if language=='de' and de is not None:return de
    result=labels(language).get(en)
    if result is not None:return result
    if strict:raise ValueError(f'Missing {language} interface translation: {en!r}')
    return en
