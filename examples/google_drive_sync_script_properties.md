# Google Drive Sync Apps Script Properties

Use these Script Properties for the proof-of-concept sync job.

```text
GITHUB_TOKEN=<fine-grained token with Contents read/write>
GITHUB_OWNER=brandonhatfield-blip
GITHUB_REPO=conCOREdance-transmission-archive
GITHUB_BRANCH=main
DRIVE_ROOT_FOLDER_ID=<Google Drive folder id>
GITHUB_TARGET_PREFIX=drive-sync-poc
SYNC_DRY_RUN=true
```

Start with `SYNC_DRY_RUN=true`.

Only set `SYNC_DRY_RUN=false` after:

- the Drive folder is allowlisted correctly,
- the logged GitHub paths are correct,
- unsupported file types are being skipped as expected,
- and the first test folder contains no private or non-canonical material.

The proof of concept should target a temporary prefix such as `drive-sync-poc` before any production archive path.
