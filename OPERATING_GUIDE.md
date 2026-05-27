# ConCOREdance Transmission Archive Operating Guide

This guide explains the normal transmission workflow for Neal, Gregory, and Cody.

The short version:

```text
GitHub Issue -> review -> canonize label -> Markdown canon + visual archive -> mark complete
```

## Roles

**Gregory**

Creates structured transmission issues and preserves the voice, doctrine, and creative intent.

**Neal**

Reviews the issue, decides whether it is ready for canon, and confirms the final archive entry.

**Cody**

Maintains the automation, archive structure, templates, and implementation integrity.

## Create a Transmission Issue

1. Open a new GitHub Issue.
2. Use the transmission request format.
3. Include the required fields:

```text
ID:
Date:
Type:
Layer:
Status:
From:
To:
Tags:
Summary:
Body:
```

`Title:` is optional. If it is missing, the automation uses the GitHub issue title.

4. Add optional sections when useful:

```text
Decisions:
Next Actions:
Assets:
```

5. Save the issue.

## Review the Issue

Before canonizing, Neal should confirm:

- The ID uses `CC-TX-YYYY-MM-DD-###`.
- The `Date` matches the date embedded in the ID.
- The summary is clear.
- The body is complete enough to become historical record.
- Decisions and next actions are included when relevant.
- The issue should become permanent canon.

If the issue is not ready, use a normal comment or apply `needs-revision`.

## Canonize an Approved Issue

When the issue is ready, apply one approval label:

```text
canonize
approved
Active Canon
```

The GitHub Action will automatically:

1. Read the issue content.
2. Create a Markdown canon file:

```text
transmissions/YYYY/CC-TX-YYYY-MM-DD-###.md
```

3. Create the visual archive entry:

```text
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/transmission.html
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/metadata.json
```

4. Update:

```text
01_Transmission_Archive/archive_manifest.json
01_Transmission_Archive/index.html
```

5. Add the `canonized` label to the issue.
6. Comment on the issue with the generated paths.

## Confirm the Result

After the workflow finishes, Neal should check:

1. The issue has the `canonized` label.
2. The generated Markdown file exists under `transmissions/YYYY/`.
3. The visual transmission page exists under `01_Transmission_Archive/YYYY/`.
4. The live archive index includes the new transmission.
5. The page title, summary, body, decisions, and next actions look right.

Live archive:

```text
https://concoredance.seekingharmony.net/01_Transmission_Archive/
```

GitHub Pages may take a minute to update after the commit lands.

## Mark the Issue Complete

Once the Markdown and visual archive entries are confirmed:

1. Mark the GitHub Issue complete or close it.
2. Leave the `canonized` label in place.
3. Do not delete the issue. The issue remains the drafting and discussion record.

## Blocking Labels

These labels prevent canonization:

```text
canonized
do-not-canonize
needs-revision
```

Use `needs-revision` when a transmission should pause before becoming permanent.

Use `do-not-canonize` when an issue should remain discussion only.

## What Lives Where

**GitHub Issues**

Drafting space, collaboration history, and review trail.

**transmissions/**

Durable Markdown canon. This is the plain-text historical record.

**01_Transmission_Archive/**

Public visual archive. This is the reader-facing archive experience.

## If Something Fails

Open the GitHub Actions run named `Transmission Canonizer`.

Common causes:

- Missing `ID`, `Date`, `Summary`, or `Body`.
- ID does not match `CC-TX-YYYY-MM-DD-###`.
- `Date` does not match the date embedded in the ID.
- The issue already has `canonized`, `needs-revision`, or `do-not-canonize`.

Fix the issue body or labels, then apply the approval label again.
