# ConCOREdance Transmission Publisher Spec

The Transmission Publisher lets Gregory or another authorized collaborator create archive entries by opening a structured GitHub Issue and applying the `transmission-request` label.

The trusted write operation happens inside GitHub Actions using the repository `GITHUB_TOKEN`, but publication remains supervised. The action prepares a draft pull request instead of committing directly to `main`.

## Workflow

1. Open a new GitHub Issue.
2. Paste the structured request format.
3. Add the label `transmission-request`.
4. GitHub Actions runs `scripts/publish_transmission.py`.
5. The script creates the transmission folder, writes `transmission.html` and `metadata.json`, updates `archive_manifest.json`, and regenerates `index.html`.
6. The workflow commits the generated files to a temporary branch named `tx/<ID>`.
7. The workflow opens or updates a draft pull request titled `Draft Transmission: <ID>`.
8. A human reviewer approves and merges the PR when the transmission is ready to become canonical.

The issue is labeled `draft-pr-created` and receives a comment linking to the draft PR. It is not closed automatically.

## Canonical Markdown Workflow

Approved issues can also become durable Markdown source records. This is separate from the HTML draft publisher so canonical written memory and public archive presentation can evolve independently.

To canonize an issue, apply one of these labels:

```text
canonize
approved
Active Canon
```

The canonizer writes durable Markdown:

```text
transmissions/YYYY/CC-TX-YYYY-MM-DD-###.md
```

It also renders the same approved issue into the public visual archive:

```text
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/transmission.html
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/metadata.json
01_Transmission_Archive/archive_manifest.json
01_Transmission_Archive/index.html
```

It then commits both layers to `main`, labels the issue `canonized`, and comments with the canonical and public archive paths. The workflow refuses to run when an issue has `canonized`, `do-not-canonize`, or `needs-revision`.

## Required Fields

```text
ID:
Title:
Date:
Type:
Layer:
Status:
From:
To:
Authorized By:
Tags:
Summary:
Body:
```

`Authorized By:` records the person who approved the transmission for canon. This is distinct from `From:`, which records who authored or sent the transmission.

## Optional Fields

```text
Decisions:
Next Actions:
Assets:
```

## ID Format

Use:

```text
CC-TX-YYYY-MM-DD-###
```

Example:

```text
CC-TX-2026-05-27-001
```

The `Date` field must match the date embedded in the ID.

## Tags

Tags may be comma-separated or listed on separate lines.

```text
Tags:
Automation Architecture, Archive Tooling, Deployment Operations
```

## Body Formatting

The body supports simple paragraphs and bullet lists.

```text
Body:
This paragraph becomes a transmission paragraph.

- This becomes a list item.
- This also becomes a list item.
```

Use `**bold text**` for strong emphasis.

## Assets

Assets are optional. Use one asset per line.

```text
Assets:
../../assets/example.png | Example caption
https://example.com/image.png | External reference
```

The publisher does not upload external image files from issues. Assets must already be reachable from the final page or be committed separately.

## Draft PR Branch

Generated branches use:

```text
tx/CC-TX-YYYY-MM-DD-###
```

Example:

```text
tx/CC-TX-2026-05-27-001
```

If the issue is edited and the workflow runs again, the same branch and draft PR are updated.

## Current Archive Root

```text
01_Transmission_Archive/
```

Do not move or flatten the archive root.

## Live URL

```text
https://concoredance.seekingharmony.net/01_Transmission_Archive/
```

The live URL updates only after the draft PR is reviewed and merged.
