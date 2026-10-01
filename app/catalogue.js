/* Port of the original CatalogueDAO read logic; usable in browsers and Node tests. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.HansgalCatalogue = api;
})(typeof window === 'undefined' ? globalThis : window, function () {
  function decode(s) {
    if (typeof document !== 'undefined') {
      const t = document.createElement('textarea'); t.innerHTML = String(s ?? ''); return t.value;
    }
    // Numeric and named entities appearing in catalogue search fields.
    const names = {amp:'&',lt:'<',gt:'>',quot:'"',apos:"'",nbsp:' ',auml:'ä',ouml:'ö',uuml:'ü',Auml:'Ä',Ouml:'Ö',Uuml:'Ü',aacute:'á',Aacute:'Á',eacute:'é',Eacute:'É',szlig:'ß',egrave:'è',agrave:'à',acirc:'â',ecirc:'ê',ocirc:'ô',ccedil:'ç',iuml:'ï',ntilde:'ñ',ndash:'–',mdash:'—',rsquo:'’',lsquo:'‘'};
    return String(s ?? '').replace(/&(#x[\da-f]+|#\d+|[a-z]+);/gi,(m,k)=>k[0]==='#'?String.fromCodePoint(k[1].toLowerCase()==='x'?parseInt(k.slice(2),16):Number(k.slice(1))):(names[k]??m));
  }
  function unaccent(s, map) { return [...String(s??'')].map(c=>map[c]??c).join(''); }
  function like(value, pattern) {
    const p=String(pattern).split('').map(c=>c==='%'?'.*':c==='_'?'.':c.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('');
    try {return new RegExp(p,'i').test(String(value??''));} catch {return false;}
  }
  function numberPrefix(value, term) {
    // Source REGEXP anchors at the start and forbids a further digit; brackets
    // around parentheses in the PHP implementation make opus 90(3) literal.
    try { return new RegExp('^'+String(term).replace(/[()]/g,'\\$&')+'([^0-9]|$)','i').test(String(value??'')); }
    catch {return false;}
  }
  function select(data, form={}, accentMap={}, orders={}) {
    const title=form.submitbutton?form.title:'';
    const opus=form.submitbutton?form.opus_number:'';
    const publisher=form.submitbutton?form.publisher:'';
    const words=unaccent(title,accentMap).split(/\W+/).filter(Boolean).map(s=>s.toLowerCase());
    const category=new Map();
    for(const r of data.catalogue_category) {
      if(!category.has(r.catalogue_id))category.set(r.catalogue_id,new Set());
      category.get(r.catalogue_id).add(r.category_id);
    }
    const rows=data.catalogue.filter(r=> {
      const cs=category.get(r.id)||new Set();
      if(form.genre&&!cs.has(String(form.genre)))return false;
      if(form.instrument&&!cs.has(String(form.instrument)))return false;
      if(opus&&opus!=='Search Opus No.'&&!numberPrefix(r.opus_no,opus))return false;
      if(form.year&&form.year!=='Search Year'&&!numberPrefix(r.year_of_composition,form.year))return false;
      if(publisher&&publisher!=='Search Publisher'&&!publisher.split(/\s+/).every(w=>like(unaccent(r.publisher,accentMap),unaccent(w,accentMap))))return false;
      if(form.duration&&form.duration!=='Search Duration'&&!String(form.duration).split(/\s+/).every(w=>like(r.duration,w)))return false;
      if(words.length) {
        const fields=['title','description','title_de','description_de','hidden_terms'].map(k=>r[k]??'').join('');
        const text=unaccent(decode(fields),accentMap).toLowerCase();
        if(!words.every(w=>text.includes(w)))return false;
      }
      return true;
    });
    const columns=['opus_no','title','description','year_of_composition','publisher'];
    const column=columns.includes(form.ordercolumn)?form.ordercolumn:'opus_no';
    const direction=form.orderby==='DESC'?'DESC':'ASC';
    const basis=orders.__basis;
    const keys=['id','opus_no','title','description','year_of_composition','publisher'];
    const unchanged=!basis || (basis.length===data.catalogue.length && basis.every((row,i)=>keys.every((k,j)=>(data.catalogue[i][k]??null)===(row[j]??null))));
    const rank=new Map((unchanged?(orders[column+'-'+direction]||[]):[]).map((id,i)=>[id,i]));
    const collator=new Intl.Collator('en',{sensitivity:'base'});
    const sign=direction==='DESC'?-1:1;
    const filterCategory=String(form.genre||form.instrument||'');
    const joinRank=new Map(data.catalogue_category.filter(r=>r.category_id===filterCategory).map((r,i)=>[r.catalogue_id,i]));
    const unpublished=r=>!r.publisher||r.publisher.toLowerCase()==='unpublished';
    function cmp(a,b,k,numeric=false) {
      const av=a[k]??'',bv=b[k]??'';
      if((av==='')!==(bv===''))return av===''?1:-1;
      if(numeric){const d=(parseInt(av,10)||0)-(parseInt(bv,10)||0);if(d)return sign*d;}
      return sign*collator.compare(av,bv);
    }
    rows.sort((a,b)=> {
      // A category join changes input order for fully tied MySQL sort keys.
      // Preserve the original junction-record order for those tied rows.
      const other=column==='opus_no'?'year_of_composition':'opus_no';
      const tied=a[column]===b[column]&&(!['opus_no','year_of_composition'].includes(column)||(a[other]===b[other]&&unpublished(a)===unpublished(b)));
      if(filterCategory&&tied&&joinRank.has(a.id)&&joinRank.has(b.id))return joinRank.get(a.id)-joinRank.get(b.id);
      // Captured source collation ranks guarantee the same initial ordering,
      // including database ties. A future edited dataset can omit the ranks.
      if(rank.has(a.id)&&rank.has(b.id))return rank.get(a.id)-rank.get(b.id);
      let d=cmp(a,b,column,['opus_no','year_of_composition'].includes(column));
      if(d)return d;
      if(['opus_no','year_of_composition'].includes(column)) {
        d=Number(unpublished(a))-Number(unpublished(b));if(d)return d;
        d=cmp(a,b,column==='opus_no'?'year_of_composition':'opus_no',true);if(d)return d;
      }
      return 0;
    });
    return rows;
  }
  return {select,decode,unaccent,like,numberPrefix};
});
