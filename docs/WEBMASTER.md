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

## Sheet-music sales links

Keep editable sales URLs in `content/catalogue.json`. `config/score-retailers.json` supplies shared region, edition and catalogue-number labels for HTML and printable work notes. UK/EU describes the retailer's location, not a promise about shipping or taxes. Retain hire links separately; a purchasable piano reduction does not make orchestral parts available for sale.

For a sales-link change, verify the exact title/opus, instrumentation, edition, format, price and order control. A successful HTTP response, a publisher's “Buy now” referral or a generic retailer search page is insufficient. Replace non-orderable offers with matching UK and EU product pages where confirmed. If no direct offer is confirmed, label the link as publisher information/enquiry instead of purchase. Do not infer product unavailability from automated-access restrictions. Record limited checks explicitly. Remove unused URL metadata when replacing links. External work-page links open a new tab.

The complete 5 October 2026 check is in `docs/sales-link-audit-2026-10-05.json`; current work/recording evidence is in `docs/purchase-audit.json`.

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


## Language scope and scheduled maintenance

Follow `docs/TRANSLATION-RULES.md` for all language work. Original work titles with bracketed translations apply across the entire site, including recordings and audio clips, not only catalogue pages.

New editorial requests default to **all published languages**, even when the comment does not explicitly mention translation. Read the request's `languageScope` before implementation. A specific language limits text edits to that language. Missing scope on an older, unproposed request means all unless its original wording explicitly limits the language. Never expand an already-approved proposal without creating a new revision and obtaining any required approval.

Discover the actual published languages from the repository on every run; currently these are English and German. When adding a language, update the private editor's `publishedLanguages` registry and include the new language in maintenance. This rule does not authorize launching additional languages automatically.

Apply the intended semantic change in every selected language. Preserve original work titles, names, opus numbers, dates, recording credits, IDs, links and formatting. Consult approved English and German wording and maintain consistent musical terminology. Do not rewrite unrelated prose. Check translations for omissions, additions, altered facts and misleading terminology. Include every affected language in the proposal, approval preview, verification and publication record. Never report completion while a required translation is outstanding.

The nightly inbox review is scheduled for 04:00 Europe/Bucharest through the Codex task automation. Existing claims, approval preferences, exact-revision approval and verified publication requirements remain in force. Unchecked requests authorize publication after checks; checked requests require approval. Do not resend reserved approval emails or repeat a completed publication. Stay quiet when no action is needed.

On the first maintenance run each calendar month, review translation consistency, including manual edits outside the comments workflow. Compare repository history since the last successful checkpoint with the private request history. Review edits in every language; do not assume that an English version is more recent than an edited German or other version. Honor explicit single-language exceptions. Fix clearly evidenced missed corresponding edits through the normal tested publication workflow; preserve and flag ambiguous or conflicting edits for clarification. Do not perform a wholesale monthly retranslation.

Keep the checkpoint and review record private: date, reviewed commit, published languages, specific-language exceptions, fixes and unresolved questions. On the first review establish a baseline and record pre-existing discrepancies separately. Advance the successful checkpoint only after completing and verifying the review. Do not place private comments or editor information in GitHub. The local task must be available to run; check automation status if a scheduled review has been missed.
