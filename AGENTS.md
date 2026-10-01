# Hans Gál website editing

Read docs/WEBMASTER.md before making editorial changes. Preserve stable IDs, old URL paths, hidden flags and the established visual design. The private editorial inbox is the source of request scope and approval, not public GitHub issues. Never publish private notes, editor email addresses, credentials or preservation archives.

Run `node tests/catalogue.test.cjs`, `python scripts/build.py --base-path /hansgal-org`, and `python scripts/verify.py`. Use `--preservation` as an additional check only when no source content was intentionally edited. Do not update preservation fingerprints or legacy fixtures to make tests pass. No deployment or content-write permissions may be added to CI as part of a routine content edit.
