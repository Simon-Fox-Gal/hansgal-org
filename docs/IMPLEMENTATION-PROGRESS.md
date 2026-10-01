# Website and editorial CMS mission

## Scope and authorization

User-authorized improvement mission, 1 October 2026. Preserve the established visual design, content, stable IDs, English URLs, authentication, approval choices and nightly editorial workflow. Publish only to the existing GitHub Pages review site and existing private CMS. Do not change original hosting or DNS. Never publish excluded private listening material, private inbox records or credentials.

## Staged implementation plan

1. Inspect public and private source, deployment and workflow; record baseline.
2. Repair recording destinations; regression-check every recording and project-path navigation.
3. Add durable private uploads, screenshot paste, attachment previews and HTML source/preview controls through the existing approval workflow.
4. Inventory authored content and original work titles; implement stable bilingual routes, metadata, switching, CMS fields and reviewed German content with coverage tracking.
5. Verify the supplied vocal-quartet score and catalogue identity; implement optional-donation basket and CMS management using existing payment destinations.
6. Audit work and recording purchase/listening links, recording evidence and unavailable exact matches.
7. Run repository and CMS checks, inspect hosted behavior, publish verified milestones and report source-preservation pass/fail and outstanding decisions.

Each verified milestone receives a commit. This file records resume state; private CMS source remains in its private Sites source repository, never copied into this public repository.

## Baseline inspected

- Public main: `af4fa61b3e29f82fd19256fb56cce9528c5c8987`.
- Public source: Python/Jinja static renderer, JSON content, browser catalogue filtering. Existing Pages workflow builds main under `/hansgal-org`.
- Read `AGENTS.md` and `docs/WEBMASTER.md`; frozen preservation fixtures must not be rewritten.
- Existing private CMS source opened at `630ee63809557f59143e937aa03fa88333fcf765`; authenticated editor checks, D1 inbox, exact-revision approval and publication lease protocol retained.
- Existing nightly editorial schedule remains enabled and unchanged.
- Supplied score verified against work 149 and visually inspected; exact authorized bytes retained.

## Progress / verification

### Published milestones

- Recording repair merged through PR #2, main `04645a23793568c50f98923516580c03b5bfa945`. Hosted regression PASS: all 78 recording destinations and 6,162 links on the actual Pages review site.
- Existing private CMS published with private source commit `b268e7e8e0ff25b0d70f36b0cc5f38c2d4db51ce`. Added authenticated durable R2 uploads, file signature checks, bounded 25 MB uploads, private previews, immutable attachment references in requests, and HTML source/rendered-preview modes.
- CMS validation PASS: TypeScript/build; existing workflow integration; upload byte/SHA integrity, identity/origin rejection, spoofed/unsupported-file rejection, durable request attachment references. Browser paste PASS locally and hosted; local source/preview round trip preserved exact text. Existing approval and nightly workflow retained. No real approval emails or payments sent.

### Foundation milestone (now published; historical implementation notes)

- Bilingual route foundation creates English and `/de` equivalents, metadata, language links and remembered entry preference. Authored content remains in separate fields; untranslated fields still fall back to English, so bilingual publication is NOT complete.
- All 179 catalogue German titles and descriptions populated. Original-language provenance uncertainties are explicitly listed in `docs/title-review.json`; these display translations are not claims of newly discovered German originals.
- Inventory: `docs/translation-coverage.json`, 1,598 non-empty authored fields. Long prose translation remains pending.
- Initial score verified: work 149, 1934, SATB/piano; supplied PDF is 21 pages, comprising Blick ins Dunkel and Weite Reise, with Marienidyll marked lost. Title page, first score page and full-page contact sheet inspected. Exact bytes retained and manifest entry added.
- Optional-donation basket implemented locally, with individual PDF links, multi-selection ZIP support and existing Society PayPal/bank/cheque destinations. Owner specified £10 on 1 October 2026; suggested amount is now `10.00`, editable down to zero. Local browser verification PASS; hosted basket verification awaits publication.
- Explicit owner approval received for publishing the supplied 21-page PDF to this public repository and review-site basket after automatic review initially blocked that upload. Local browser PASS: add score, retain basket across English/German switch, £0 download, and zero-amount PayPal prevention. Positive PayPal handoff PASS: correct Society recipient, chosen GBP amount, PayPal/card choices and UTF-8 description. No payment made. Independent two-file ZIP decoder PASS.
- English/German CMS tabs implemented locally after the upload milestone; not yet published.
- PASS on current public build: 1,268 routes, 1,283 assets, 230 audio references, catalogue regressions and recording regressions. These checks do not establish complete translation coverage or correct payment handoff.

## Outstanding decisions

- RESOLVED: owner specified £10 for work 149; downloads remain free at £0.
- Ambiguous original-language work titles: inventory before translating; flag unresolved titles rather than inventing originals.
- Exact purchase formats and editions: verify externally; retain unavailable statuses explicitly.

## Resume next

Continue translation and original-title provenance review, score-basket verification, complete purchase-link audit, bilingual CMS verification, then publish verified remaining milestones. Initial plan checkpoint: `535595b78bc7069716870579c5bb61070119e31f`. Git CLI writes are unavailable; use the connected GitHub API for checkpoints. Public source checkout is `work/hansgal-org`; private CMS checkout is `work/cms` in this mission workspace. Never copy the private CMS source into the public repository.

- Owner decision: suggested donation for the approved work 149 PDF is £10. Applied as `10.00` GBP; zero-donation downloads remain supported.

### Latest verified foundation checkpoint

- £10 suggestion verified in German basket; changing to £0 still downloads immediately. Payment navigation stays in the same tab to avoid popup blocking.
- `tests/mission.py` PASS: 1,652 original rows retain every pre-existing field except authorized German title/description updates; every page has its language equivalent and switch; PDF hash and independently decoded ZIP bytes match.
- German FAQ, category names, menu headings and biography introduction translated. Dynamic interface messages translated; full long-form content remains pending.
- Purchase-link fields and rendering added for printed scores, rental materials, score PDFs, CDs, audio downloads and listening. Existing historical text retained. Audit in `docs/purchase-audit.json` is still pending; no unchecked product links added.
- Private CMS language/score/link controls pass TypeScript; publication pending integration checks.

### 1 October: visible feature publication
- CMS source `5dfd9438a984c54e853d0665ac984d15e265920f`: new-record proposals for all 16 collections, visible uploads and screenshot paste at the top of record editing, preserved attachment references into review dialogs, bilingual controls, and sandboxed Browse and comment preview. Local browser selection/navigation/new draft/paste PASS; creation, upload and approval integration PASS. Deployment in progress.
- Public feature build PASS: catalogue 99 baseline scenarios plus edited-data cases, 78 recording destinations / 6162 links, 1652 preserved source rows, bilingual routes, approved score bytes, independently decoded two-file ZIP. Publishing the score basket and language framework as a review milestone; full German prose and purchase audit remain in progress, not complete.
- German photo captions, audio descriptions and movement labels, plus seven biography sections, added. Coverage regenerated from current content; embedded popup texts remain explicitly pending.

### 1 October: hosted features and catalogue translation milestone

- Public PR #3 merged at `948a8a891993c70539f5bea5b820e0acd14f52a7`; Pages run 36900985098 succeeded. Hosted recording regression PASS for 78 destinations and 6,162 links. Hosted score PDF SHA-256 matches the approved original; add-to-basket, £10 suggestion, £0 download and English/German basket selection PASS. PayPal handoff reached the official service but its CAPTCHA prevented further hosted inspection; no payment made.
- Private CMS deployment of `5dfd9438a984c54e853d0665ac984d15e265920f` succeeded. Hosted Browse preview and page-comment dialog PASS; New record and bilingual fields visible. Local paste retains the attachment into the review dialog. All 16 collections pass creation/overwrite-rejection tests. New-record default fields are included in the follow-up source fix.
- Catalogue German fields now cover titles, descriptions, movements, orchestration, availability, other versions, work notes and performance details. Existing bilingual Das Lied der Nacht libretto retained. Translated quotations labelled. Historic availability wording is translated, not represented as a new stock check.
- Original source truncations in works 154, 157 and 169, and contradictory Canadian geography in work 12, retained and flagged in translation coverage. No invented corrections.
- Eleven exact purchase/release matches recorded with evidence: nine recordings and two works. Format-specific links added only where verified. Remaining purchase audits are pending.
- Page titles now identify the localized work/recording/page. Basket custom donation persists across language switching for the same selection.
- Build, catalogue tests, route/asset/relationship verification and source-preservation tests PASS. Original 1,652 rows and pre-existing English fields retained; authorized German display fields updated. Full-site translation remains incomplete: recording text, remaining long page prose, embedded popups and standalone captions require work. Coverage is not a claim of editorial approval of uncertain source titles.

### 1 October: page translation checkpoint

- PR #4 deployed successfully at `4fa1cdee5d6328c467628611e3e6016e981d1f64` (Pages run 36904932601). Hosted German title search PASS; custom basket amount £3.25 retained on switching to German, then restored to £10.
- Private CMS follow-up `2976c2c5aa57f0ca276aba042c240e3aca879d69` deployed successfully; includes complete default values in new-record proposals.
- Added German early-life, education, early works, war, first-opera and postwar biography sections; membership, contact, general FAQ, sketchbook and performance-fund pages; bibliographic entries preserve official publication titles while explanatory prose is localized. In total 23 page bodies now have German variants, with all original links and media preserved. Empty HTML-only lead fields are shared unchanged.
- Language-switch links now use the current search/sort URL at click time. Focused regression PASS for query, sort and fragment preservation. Basket page title corrected for canonical route without trailing slash.
- Build, route/asset/relationship and 1,652-row source-preservation checks PASS. Full translation and purchase audits remain in progress; coverage retains pending entries rather than treating English fallback as complete.

### 1 October: family, opera and donation text

- PR #5 deployed successfully at `89f9b8643d55c0613ab2eea8779ce4d4ac376192`, Pages run 36906722838.
- Added family/marriage and Die Heilige Ente biography chapters and the donation page. German donation UI, validation messages and Gift Aid declaration text retain the original payment destination, account identifiers, fund values and payment rules. No payment or email sent.
- English/German donation regression PASS: exact recipient/fund/amount, bank/cheque GBP restriction and rejection of zero for the PayPal handoff. Score-basket downloads still accept zero independently. Local rendered German form inspected; EUR-to-bank selection correctly becomes GBP. Further local alert interaction was blocked by a browser-driver timeout, not treated as a passed UI check.
- All 26 translated menu bodies retain their original links and media. Existing broken constitution link to `/admin/hansgalsociety/index/36` has no matching content record in the preserved source; retained and flagged rather than inventing a replacement document.
- Remaining authored HTML attributes and embedded popup text still need a final language sweep alongside remaining page prose and recording text. Full translation is not yet complete.

### 1 October: recording descriptions and further biography

- PR #6 deployed successfully at `39472ca615c3cfd1d83c58ff524f4f7392ccb7d3`, Pages run 36908135961.
- All 78 recording titles and descriptions now have German display text. Original release titles remain alongside changed title translations. Musical descriptions translated with original performer/ensemble names, dates, opus/catalogue numbers and link/media targets preserved. Empty review placeholders shared; substantial reviews remain pending.
- Added biography chapters on Das Lied der Nacht and the 1920s. Historical quotations are labelled as translations of the supplied English wording, not asserted to reproduce a recovered German original.
- Source issues retained for editorial review: recording 34's Sinfonietta opus, 78's performer spelling and 88's viola-suite opus; obvious German-display typographical corrections in 60, 61, 83 and 84 are supported by the same records' title/body, with original English fields unchanged.
- Source preservation PASS: all 1,652 original rows; no new duplicate IDs or broken relationships. Recording translation numeric sequences and media/link targets checked before application. Remaining long reviews/pages, embedded text and full purchase audit are still outstanding.

### 1 October: hosted CMS recheck and biography completion

- PR #7 deployed successfully at `b1d0e8c26b4bc1cd8fa980678242e53be3dbf776`, Pages run 36910045345.
- Hosted CMS recheck PASS after closing a stalled donation-test browser tab: Browse preview renders, page-comment dialog opens, New record opens, clipboard PNG uploads privately and displays filename/thumbnail/details, source-to-preview-to-source preserves exact HTML, and the uploaded attachment survives into the new-record review dialog. Test draft discarded without saving to inbox or sending email.
- Added the remaining biography chapters covering recognition, scholarship, Mainz, dismissal, Die beiden Klaas, return to Vienna, emigration and internment. Contact and Society page bodies now translated; donation declaration/messages localized on both Society and donation pages. Empty family-tree body preserved.
- Corrected reversible UTF-8/Windows-1252 decoding artifacts found in German text of seven previously translated biography chapters and a shared musical title. Original English fields and URLs remain unchanged.
- Full translation remains incomplete: 56 inventory fields pending, plus embedded popup/attribute/caption sweep. Full purchase audit remains pending. This checkpoint is not a claim that those remaining mission requirements are complete.

### 1 October: popup notes, initial reviews and publisher evidence

- PR #8 deployed successfully at `671984c2812dca71ec5476444683a9bae4ca1eab`, Pages run 36911900902.
- All 19 unique biography popup notes translated across 51 occurrences; all resulting scripts parse. Dedicated `popup-translation-coverage.json` records source hashes and historical ambiguities. Original English bodies, links and media preserved.
- Seven recording reviews translated (16, 19, 22, 24, 28, 32, 48), with translated quotations identified. Review 16 contains historical claims conflicting with the biography (award age and length of internment); preserved as the critic's words and flagged here for editorial review, not endorsed as newly checked facts.
- Hosted catalogue PASS: German Vokalquartette query returns work149; descending year sort has 1986, 1983, 1983, 1982, 1982, 1979; switching language preserves current search and sort and returns the English equivalent of the same work. Original arrow-sort behavior resets text search, as in the preserved legacy UI; language switching itself retains the current query.
- Six further publisher work matches investigated. Added exact Simrock EE5318 / ISMN 9790221121097 violin-sonata product page (work138). Five other Boosey purchase pages lack exact edition/format checkout and remain partially verified, with no guessed links. Publisher crawler limitations include UE/Boosey 403 and Breitkopf 429; indexed primary-source evidence distinguished from stock verification.
- Full translation and all-record purchase audit are still in progress; 49 inventory fields remain pending, plus HTML-attribute and standalone-caption checks.
