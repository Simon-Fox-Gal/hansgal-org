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

### Current unpublished work

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
