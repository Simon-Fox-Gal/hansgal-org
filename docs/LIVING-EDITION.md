# The Living Edition

The approved public-site redesign uses a generous literary composition, warm ivory, plum from the existing identity, and forest green for wayfinding. Chapter 25's clarity, flowing melody, polyphonic structure and expressive restraint inform the hierarchy and spacing.

The original header logo remains byte-for-byte unchanged. It is displayed at 350–370 px on large screens, 290–310 px on intermediate screens, and up to 250 px on phones. Its white masthead gives the layered mark room. No separate decorative flower is repeated: the portraits and recording artwork supply the visual interest.

## Scope

- Shared masthead, native section navigation, search, language selection, score basket and footer across English and German.
- New homepage with the original portrait, pathways into the archive and the first three recordings in the existing editorial order.
- Chapter index and responsive chapter navigation; large readable article layouts.
- Works catalogue with labelled filters, visible sort controls, mobile result rows and filter state retained when sorting or switching language.
- Work details, score panels, keyboard-operable expandable sections and original purchase links.
- Recording collection with cover grid, text filtering and horizontal browsing; recording details with prominent original cover artwork, complete programme/review text and purchase/listening links.
- Photo galleries and a keyboard-accessible native image dialog; audio samples, search, contact, reference, Society and donation pages use the same design system.

Authored content records, IDs, relationships, hidden flags, media bytes, donation settings and established routes are unchanged. Historical standalone HTML documents and PDFs remain archival assets in their original formats. Eight sketchbook images now resolve to their already-preserved local files instead of the obsolete musicessences.com host. Missing biography sidebar thumbnails are no longer requested.

## Implementation

`app/edition.css` owns the presentation, with Georgia headings and familiar sans-serif body text. `app/edition.js` provides progressive mobile navigation, chapter disclosure, recording filtering and image viewing. The existing catalogue selector, audio, language, score-download and private CMS bridge continue to operate. The old ImageFlow animation is replaced by a native scrolling cover collection; legacy cover-view URLs and preferences still select the equivalent view.

Main reading text is 20 px on desktop and approximately 19 px on phones, with generous line spacing. Primary controls are at least 50 px high; catalogue sort controls are 44 px. The stylesheet supports narrow screens, reduced motion, visible keyboard focus and printing. Navigation and reading links remain available without JavaScript.

## Verification

Run the existing checks from AGENTS.md, plus:

```
python tests/edition.py
```

For this design-only revision, `python tests/edition.py --unchanged-content` additionally compares all content and public asset paths against the approved pre-redesign commit `a97f4436f213652afe4486c32b0659fd4ca9483f`. Omit this option for subsequent authorized editorial changes.

The optional `tests/edition-browser.cjs` requires Playwright. `SITE_BASE` selects the preview URL; `BROWSER_CHANNEL` defaults to installed Edge. It checks mobile navigation, combined search/sort state, language switching, recording filters and navigation, image and chapter controls, score-basket addition, the actual free PDF download, audio selection and site search. It sends no payment or message.

Release checks on 2 October 2026 passed: 632 rendered pages at both 1440 px and 320 px (1,264 page views), with no page overflow or JavaScript errors; seven principal views at 200% text size; keyboard image navigation; and reading/navigation with JavaScript disabled. The existing 99-case catalogue regression, bilingual integrity checks, 6,480 recording destinations, 299 structured purchase URLs, audio references and donation tests passed. All 1,278 generated routes remain available. The source comparison found no omitted checked field text, duplicate record IDs, new broken relationships, or changed content/media bytes.

Known inherited asset gaps: the old Society contact email image, a catalogue image for work 132, and an external Grammy illustration on recording 61 were already unavailable. Their original authored references are preserved; they are not new artwork or content supplied by this redesign. See the pre-existing link audit for the archived local references.

Deployment remains GitHub Pages at the existing public review URL. No domain, DNS, CMS hosting, CI permissions or payment destinations are changed.
