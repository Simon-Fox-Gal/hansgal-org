# Separate audio hosting

The proposed public media repository is `Simon-Fox-Gal/hansgal-audio`, with GitHub Pages serving the main branch at its root. The player base is configured in `config/audio-hosting.json` and rendered as `hansgal-audio-base` metadata. Work, recording, listening, pop-out and legacy player pages retain their identities. Links and three player implementations use the configured media base. Recording credits and copyrights remain on hansgal.org.

## Publish in two stages

1. Create the public audio repository and enable Pages for main / root. Generate its content with `python scripts/build_audio_site.py /absolute/output/directory`, upload the complete generated tree, and wait for its deployment. Every media file must retain its exact bytes and filename.
2. Run `python scripts/retire_local_audio.py --check-only` to verify all hosted bytes. Verify HTTP byte-range requests and browser playback/seek on a work page, the listening page and pop-out player. Only after these pass, publish this player migration. Leave all original media copies in the website through the transition deadline.

## Deferred retirement

Not before 14 October 2026 at 06:00 Europe/London (BST; 05:00 UTC), run `python scripts/retire_local_audio.py`. It verifies the whole remote inventory and refuses to remove changed local files. Any verification failure stops the operation before deletion. It removes only the inventory's originals and their local asset-manifest entries. The remote integrity inventory remains permanently in `config/audio-assets.json`.

After retirement, run the required checks and publish the narrowly scoped change through a dedicated branch and pull request. Preserve unrelated edits on current main. Verify deployed players, hosted files, and the reduced published-site size. Keep historical Git objects; rewriting repository history is outside this operation.

Existing open tabs may continue using original file URLs until retirement. They may need to refresh before starting another excerpt after those addresses are removed. New and refreshed tabs use the new host. A stalled or unverified migration must not trigger retirement.

## Future maintenance

Publish new audio to the media site before adding listening links. Extend its `audio-assets.json` and the website's `config/audio-assets.json` with byte sizes and SHA-256 values. Local source copies remain optional after the transition; catalogue and asset checks accept the retained external inventory. The three historical Flash-player test files are unrelated and stay on hansgal.org.
