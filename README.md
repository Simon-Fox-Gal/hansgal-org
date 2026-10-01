# Hans Gál website — replica for review

This is the first static replica of **hansgal.org**. It preserves the original pages, design, wording, record IDs and URL paths, while replacing PHP/MySQL page generation with JSON, templates and browser JavaScript.

The live hansgal.org site and its DNS have not been changed. The preservation archive remains separate in Google Drive; it is not part of this repository.

## Review

The review site is built for `https://simon-fox-gal.github.io/hansgal-org/`. Its pages request that search engines do not index them. This is a public review URL, not an access-controlled site.

Start with `/works`: combine genre and instrument filters, search English or German title terms, try opus `3` and `90(3)`, and use both directions of every column sort. Then open a work, expand its sections, select audio excerpts, browse recordings in both views, and open photographs.

## Run locally

Requires Python 3.11 or later and Node.js for the catalogue tests.

```sh
python -m pip install -r requirements.txt
python scripts/build.py
node tests/catalogue.test.cjs
python scripts/serve.py
```

Open `http://127.0.0.1:4173/`. The server is only a local static preview; the deployed site needs no Python, PHP or database server.

For GitHub Pages, build with `python scripts/build.py --base-path /hansgal-org`. A future domain cutover uses an empty base path and `--production`; the domain, redirects and indexing must be reviewed before that cutover.

## Content and the future CMS

- `content/` holds the original public content fields and relationships as JSON, retaining IDs, nulls, bilingual fields, hidden flags and source HTML. Unlinked menu pages keep their direct URLs and remain absent from navigation.
- `templates/` contains presentation templates translated from the original Smarty templates to Jinja. The biography index retains its rendered original markup.
- `public/` holds original public media, documents, fonts, styles and browser libraries.
- `app/` replaces database-backed reading and selection with browser code.
- `scripts/` builds and serves the static output. `dist/` is generated and is not committed.
- `tests/` contains 99 independently captured catalogue input/result fixtures from the old website.
- `docs/` records migration checks and known differences.

The later CMS should edit the JSON and media, then run this build. It must preserve record IDs, relationships and old paths. Authentication, editorial workflows, validation and publishing controls are not implemented in this review phase. The catalogue's captured collation ranks and the biography index must be integrated with editing before the CMS is enabled; they are documented in `docs/review-notes.md`.

## Verification

The migration comparison passed for all 313 included captured HTML content pages after normalizing whitespace and excluding scripts/styles. All fields in the 16 selected content tables match the preserved source JSON. The 99 catalogue cases match the live site's result IDs and ordering. Original copied asset bytes are checked by SHA-256.

These are preservation and functional checks, not a claim that the old site had no defects. Existing missing images, invalid links and text encoding artifacts remain recorded. See `docs/source-comparison.json`, `docs/link-audit.json` and `docs/review-notes.md`.

## Rights

Content, photographs, recordings and scores retain their existing rights. No new blanket licence is granted. Bundled third-party libraries retain their original copyright and licence notices, including ImageFlow's Attribution–Noncommercial licence.
