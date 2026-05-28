ID:
CC-TX-2026-05-27-001

Title:
Transmission Publisher Infrastructure Established

Date:
2026-05-27

Type:
Implementation Log

Layer:
Publication Infrastructure

Status:
Active Canon

From:
Cody Vale

To:
Gregory P. Turing / Brandon Hatfield, LPC

Authorized By:
Neal / Brandon Hatfield, LPC

Tags:
Automation Architecture, Archive Tooling, Deployment Operations

Summary:
The ConCOREdance Transmission Archive gains a GitHub Actions publisher that converts structured issue requests into supervised draft transmission pull requests.

Body:
The archive now supports structured continuity preparation through GitHub Issues and GitHub Actions.

Gregory can create a transmission request without needing direct connector write permissions. The repository prepares the generated archive package internally, then presents it as a draft pull request for human editorial review.

Decisions:
- Use GitHub Issues as the request interface.
- Use GitHub Actions as the trusted draft publisher.
- Require human review and merge before canonical publication.
- Keep the archive root and visual doctrine unchanged.
- Generate both human-readable HTML and machine-readable metadata.

Next Actions:
- Create the issue.
- Add the transmission-request label.
- Review the generated draft PR.
- Merge only after the transmission is approved as canonical.

Assets:
