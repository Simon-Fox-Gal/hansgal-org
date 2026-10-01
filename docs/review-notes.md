# Review notes

## Scope and equivalence

The first review version keeps the old presentation. It renders the 179 work records, 78 recording records, 48 menu pages (including seven unlinked pages), 106 photographs and 75 audio records describing 230 excerpt references. The original page templates, public files and content fields supply the build. No editorial rewriting or redesign was requested or performed.

The build also supplies recording fragments, audio-player URLs, section redirects, site search and view-switch URLs. The known older links `/biography/15-nazitakeover.html` and `/works/op53.html` have compatibility redirects to their corresponding current pages. A review base path is added on GitHub Pages; the original paths are available beneath it. Directory-based Pages hosting may append a trailing slash. The future custom domain uses the same paths without the review prefix.

## Intentional technical differences

1. Catalogue searches and selections run in JavaScript over JSON. No PHP or MySQL is deployed. Search state can be represented in query parameters for refreshable review links.
2. Flash audio players use the same original MP3 files in native HTML audio controls. Browser autoplay rules still apply.
3. Cover Flow retains the original ImageFlow animation and controls. Reflections are drawn in a browser canvas because the old PHP reflection service returns server errors for some covers.
4. Review pages request `noindex,nofollow`; canonical links point to the corresponding hansgal.org paths. Those indexing controls must change at production cutover.
5. The separate `/comments` form is present for review but does not send or store submissions. It clearly says so when submitted. The main navigation's COMMENTS link still goes to Contacts, exactly as on the original. Comment storage requires an agreed service or the later CMS backend. No comments from the private database are published.
6. Thirty-two legacy public filenames contain non-UTF-8 bytes. The portable working copy uses the equivalent Latin-1 characters while preserving file contents. The raw byte names remain in the preservation tar. These unlinked audio-guide and related file URLs require special attention if old raw-byte links are discovered; GitHub Pages does not provide arbitrary server rewrite rules.

## Catalogue behavior

The source's title search checks English and German title/description fields and hidden terms. It decodes HTML entities, uses the original accent mapping, and requires every search word. Opus/year matching is anchored and requires a non-digit or end after the search term. Publisher words are combined with AND. Category filters intersect genre and instrument memberships.

All five columns support ascending and descending sorts. Blank opus/year fields remain last; numeric portions, full values, publication status and secondary fields follow the original rules. Captured source ranks preserve the original database collation for the unchanged dataset, including its ties. Category joins retain junction order for tied rows. The old controller clears some text fields on category changes and sort clicks; that behavior is preserved.

The checked-in tests compare 99 requests against independently captured live responses: every category, all ten sorts, combined filters, bilingual/accented searches, opus boundaries, publisher searches and no-result cases. The source did not define a final unique tiebreaker, so tied rows outside the tested cases may depend on the old database's execution plan.

## Existing source defects

The link audit distinguishes missing source assets from migrated assets. Original missing thumbnails, biography illustration paths and catalogue images remain missing. Invalid links that contain explanatory text instead of URLs, an obsolete admin link, an email graphic reference and a malformed external link are recorded. Original encoding artifacts and orphaned relationship rows remain in the source data. They have not been silently edited.

At the owner's request, one private preview page and its six audio clips are excluded from this replica. The private preservation archive includes historical backups, hosting configuration and submission data. They are deliberately outside this public website repository.

## Before adding the CMS

Use the content JSON as the editable data model and validate IDs and relationships before each build. Make the biography index derive its navigation from menu records while preserving its current layout. Replace or regenerate the captured collation ranks when catalogue data changes; the initial review dataset is intentionally frozen to the verified source. Decide how comment submissions should be handled. Add authenticated editing, preview, publishing review, media management and rollback as a separate phase.

## Before the live-domain cutover

Review the replica, address any agreed source defects, and verify historic links and aliases. Build at the domain root in production mode, then arrange DNS and host-level redirects separately. This task does not switch hansgal.org or the related domain aliases.
