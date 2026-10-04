# Editorial maintenance

The online private CMS owns editorial requests, approval preferences and the audit trail. This public repository owns the website's approved content and presentation. The site still has no database server: Python renders static HTML; browser JavaScript searches and sorts JSON. The CMS's private inbox uses separate managed storage.

## Editing content

Read the latest main branch before preparing each change. Apply only requested fields and retain their existing types (string or null), record IDs, source HTML, relationship rows and hidden flags. Direct edits include previous values and a base commit: conflicting values require clarification. New IDs must be unused decimal strings. Never delete an old route without an explicitly reviewed equivalent redirect.

Common files:

- `content/page_text.json`: editable bilingual wording formerly fixed in templates. Preserve IDs, page groups and paths; edit only `value` and `value_de`. The private editor groups these blocks by page alongside existing menu pages. `tests/page-text.py` records the initial lossless migration; later intentional copy edits should update its expectation through normal editorial review.

- `content/menu.json`: page titles, lead and body text, navigation group, hidden flag.
- `content/catalogue.json`: works and bilingual search fields; associated `catalogue_*` tables hold categories, recordings, images and audio links.
- `content/recording.json`: title, cover filename, detail HTML, review/context HTML and display sequence. Cover files go in `public/storage/recordingcovers/`. Add the cover path, byte size and SHA-256 to `content/asset-manifest.json`.
- `content/properties.json`, `heading.json`, `faqs.json`, `photos.json`: site text and other collections.
- `templates/`: layout and fixed page content. The biography index's existing links use the current menu titles and hidden flags; new visible biography pages are added automatically. Its introductory text remains editable in the template.
- `public/`: media and preserved standalone documents. Do not modify unrelated asset bytes.

The private listening preview (menu record 82 and `ente_private_audio/`) is excluded. Do not restore it, its six clips, comments/submission tables, hosting credentials, raw exports or backups. Keep the seven other unlinked pages and their public URLs.

## Recording research

For a request to add a CD, verify the exact release with the label or artists, then create a complete entry: cover with a legitimate source, performers, label/catalogue number, release date, track list, linked works, purchase/listening links, attributed review excerpts or summaries, review URLs, and factual context. Do not manufacture unavailable facts or critical quotations. Keep direct quotations brief and within source copyright limits. Save evidence in the private proposal and appropriate source links in the public entry.

## Validation and publication

1. Work on a dedicated branch. Preserve private inbox notes and contact details outside public commits and pull requests.
2. Run the checks from AGENTS.md. `verify.py` checks stable IDs, routes, assets and relationships; pre-existing orphan relations are documented and tolerated. `--preservation` additionally checks the unchanged migration baseline. The frozen 99-case catalogue dataset remains immutable; current and edited-data tests are separate.
3. Build and inspect affected rendered pages. Include unchanged surrounding pages and navigation. Search and sort edited works. Captured legacy sorting ranks apply only when the ordering fields still match the preservation baseline; edited catalogues use the shared live comparator for initial rendering and browser interaction.
4. Submit a private inbox proposal identifying the base SHA, exact branch SHA, all changes, sources and checks. A public pull request may show the website changes, but never private editorial conversation. The inbox displays before-and-after previews.
5. Checked approval requests must await approval of that exact revision, with one approval email to the requesting editor. Unchecked requests authorize automatic publication after checks. Reserve approval email delivery before using Gmail; reconcile an uncertain send before retrying.
6. Immediately before merging, claim/re-read the request and verify authorization and current main. The proposal commit and validated base must still match. Call the inbox's `begin_publish`, then merge only that commit. Changed proposals invalidate old approvals.
7. Wait for the normal GitHub Pages workflow to succeed, read back the affected hosted pages and record the merged SHA and verification. An interrupted merge/deploy must be reconciled before retry to avoid duplicate work. Only verified deployments become Published.

The browsing bridge is inert on the ordinary website. In the authorized CMS frame it reports the current URL, recording/work/page reference and selected text. It contains no credentials and grants no publishing ability. Any future change of CMS origin requires an explicit update to its allowlist.

No production hansgal.org cutover, DNS change, permission expansion, or replacement of the website's original design is authorized by a routine editorial request.
