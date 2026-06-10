# Google Drive GitHub Continuity Synchronization Layer

Issue: #7

Status: proposed implementation architecture

## Objective

Maintain Google Drive as the active collaborative workspace while preserving GitHub as the canonical archive, version history, and public continuity layer for ConCOREdance.

The sync layer should move deliberate project artifacts from Drive into GitHub without creating duplicate commit noise, breaking folder hierarchy, or requiring a paid automation platform.

## Recommended Architecture

Use a Google Apps Script project attached to the ConCOREdance Google Drive workspace.

The Apps Script job:

1. Scans one or more configured Drive folders.
2. Builds a stable relative path for each supported file.
3. Computes a content hash for each exported artifact.
4. Compares the hash against stored sync state in `PropertiesService`.
5. Creates or updates matching files in GitHub through the GitHub Contents API.
6. Writes a compact sync report back to Apps Script logs and optional Drive log files.

GitHub remains the canonical archive once a file is synced. Drive remains the working surface.

## Folder Mapping

Suggested starting mappings:

| Google Drive Folder | GitHub Path | Notes |
| --- | --- | --- |
| `ConCOREdance/01_Transmission_Archive` | `01_Transmission_Archive` | Public visual archive |
| `ConCOREdance/transmissions` | `transmissions` | Durable Markdown canon |
| `ConCOREdance/docs` | `docs` | Operating documentation |
| `ConCOREdance/examples` | `examples` | Request templates and samples |

Avoid syncing broad parent folders such as an entire practice drive. The sync should be allowlisted, not global.

## Supported File Types

Initial pass:

- `.md`
- `.txt`
- `.json`
- `.html`
- `.css`
- `.js`
- `.png`
- `.jpg`
- `.jpeg`
- `.pdf`

Google-native documents should be exported intentionally:

| Drive MIME Type | GitHub Output |
| --- | --- |
| Google Docs | `.md` or `.html` |
| Google Sheets | `.csv` |
| Google Slides | `.pdf` |

Do not sync Google-native files blindly until output format is decided per folder.

## Duplicate Commit Prevention

Every synced file should use a stable state key:

```text
<drive_file_id>:<github_path>
```

State value:

```json
{
  "sha256": "content hash",
  "driveModifiedTime": "timestamp",
  "githubPath": "target path",
  "lastCommitSha": "commit sha"
}
```

If the content hash has not changed, skip the file even if the Drive modified timestamp changed.

## Commit Strategy

Use one commit per sync run when possible.

Commit message format:

```text
Sync Drive archive updates: YYYY-MM-DD HH:mm

- updated: docs/example.md
- created: transmissions/2026/CC-TX-2026-06-10-001.md
- skipped unchanged: 41
```

The GitHub Contents API creates one commit per file. If atomic multi-file commits become necessary, upgrade to Git Trees API later. For the proof of concept, file-level commits are acceptable if unchanged files are skipped aggressively.

## Authentication And Security

Use GitHub fine-grained personal access token or GitHub App token with minimum repository permissions:

- Contents: read/write
- Metadata: read

Store the token in Apps Script `PropertiesService` under:

```text
GITHUB_TOKEN
```

Do not store tokens in Drive files, synced files, source control, or issue bodies.

Recommended additional properties:

```text
GITHUB_OWNER=brandonhatfield-blip
GITHUB_REPO=conCOREdance-transmission-archive
GITHUB_BRANCH=main
DRIVE_ROOT_FOLDER_ID=<folder id>
SYNC_DRY_RUN=true
```

Start in dry-run mode until path mapping and hash detection are confirmed.

## POC Flow

1. Configure one Drive folder containing a small test Markdown file.
2. Run `syncConCOREdanceDriveToGitHub()` in dry-run mode.
3. Confirm the script logs the expected GitHub path and hash.
4. Disable dry-run.
5. Run again and confirm the file is created in GitHub.
6. Run a third time without changing the file and confirm it is skipped.
7. Edit the Drive file, rerun, and confirm a single update occurs.

## Scheduled Sync

Use an Apps Script time-driven trigger:

- every 6 hours during development, or
- daily once stable.

Manual run should remain available for Neal/Cody-controlled sync moments.

## Canon Boundary

Syncing a file to GitHub does not automatically make it Active Canon.

Transmission canon should continue to use the existing GitHub Issue and label workflow:

```text
GitHub Issue -> review -> canonize label -> Markdown canon + visual archive
```

Drive sync should support workspace continuity, not bypass review.

## Failure Handling

The sync should stop safely on:

- missing GitHub token
- unknown folder mapping
- unsupported MIME type
- GitHub API 401/403
- path collision
- file larger than GitHub Contents API practical limits

Each failure should include:

- Drive file name
- Drive file ID
- intended GitHub path
- safe error summary

Never log token values.

## Implementation Roadmap

### Phase 1: Proof Of Concept

- Add Apps Script skeleton.
- Support Markdown/text/json/html/image/pdf binary upload.
- Support dry-run mode.
- Support hash-based skip logic.
- Sync one allowlisted folder.

### Phase 2: Archive Folder Mapping

- Add multiple folder mappings.
- Preserve hierarchy under each mapping.
- Add folder-level include/exclude rules.
- Add sync report generation.

### Phase 3: Canon-Aware Guardrails

- Add warning when syncing into `transmissions/` outside issue workflow.
- Add optional branch target such as `drive-sync/YYYY-MM-DD`.
- Add PR creation only if needed and supervised.

### Phase 4: Operational Hardening

- Add rollback notes.
- Add GitHub API backoff.
- Add file-size limits.
- Add documented Apps Script setup guide with screenshots or exact menu steps.

## Open Decisions

- Whether Google Docs should export as Markdown or HTML by default.
- Whether Drive sync should target `main` directly or a supervised branch.
- Whether PDFs from clinical resources belong in this archive repo or a separate resource repository.
- Whether sync reports should be kept in GitHub, Drive, or only Apps Script logs.
