# ConCOREdance Canon

The Transmission Archive is the institutional memory of ConCOREdance.
This index is optimized for AI collaborators and human maintainers who need a portable source of truth.

## Current Active Canon

### CC-TX-2026-06-26-002 - Portable Canon and Model-Agnostic Institutional Memory

- Status: Active Canon
- Layer: Transmission Archive / Institutional Memory
- Abstract: ConCOREdance distinguishes institutional memory from model memory by making each transmission portable across HTML, PDF, and AI-optimized Markdown, with CANON.md serving as the living model-agnostic index.
- HTML: [archive/2026/CC-TX-2026-06-26-002/index.html](archive/2026/CC-TX-2026-06-26-002/index.html)
- PDF: [archive/2026/CC-TX-2026-06-26-002/transmission.pdf](archive/2026/CC-TX-2026-06-26-002/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-06-26-002.md](transmissions/2026/CC-TX-2026-06-26-002.md)

### CC-TX-2026-06-26-001 - Ada Vance Team Welcome

- Status: Active Canon
- Layer: Personnel / Project Onboarding
- Abstract: Ada Vance is welcomed to the ConCOREdance team as Chief Research & Interoperability Officer, grounding the project's future-facing architecture in evidence, standards, and ecosystem reality.
- HTML: [archive/2026/CC-TX-2026-06-26-001/index.html](archive/2026/CC-TX-2026-06-26-001/index.html)
- PDF: [archive/2026/CC-TX-2026-06-26-001/transmission.pdf](archive/2026/CC-TX-2026-06-26-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-06-26-001.md](transmissions/2026/CC-TX-2026-06-26-001.md)

### CC-TX-2026-06-25-001 - The Choreography Layer: ConCOREdance as an Intelligent Coordination Platform

- Status: Active Canon
- Layer: Platform Architecture / Foundational Philosophy
- Abstract: A foundational architectural realization emerged during discussion of scheduling, signatures, Google Workspace, Microsoft 365, data ownership, and therapist workflow fragmentation.

The central insight:

**The problem facing therapists is not a lack of tools. The problem is a lack of coordination between tools.**

ConCOREdance should not primarily position itself as another EHR, document repository, calendar application, or practice management platform.

ConCOREdance should position itself as an intelligent coordination layer.
- HTML: [archive/2026/CC-TX-2026-06-25-001/index.html](archive/2026/CC-TX-2026-06-25-001/index.html)
- PDF: [archive/2026/CC-TX-2026-06-25-001/transmission.pdf](archive/2026/CC-TX-2026-06-25-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-06-25-001.md](transmissions/2026/CC-TX-2026-06-25-001.md)

### CC-TX-2026-06-21-001 - Print to ConCOREdance — Universal Clinical Document Import

- Status: Active Canon
- Layer: Document Import / Portability
- Abstract: ConCOREdance establishes Print to ConCOREdance as a signature universal import feature, allowing therapists to receive PDFs from browsers, EHRs, and other printable macOS applications into a fast encrypted review tray.
- HTML: [archive/2026/CC-TX-2026-06-21-001/index.html](archive/2026/CC-TX-2026-06-21-001/index.html)
- PDF: [archive/2026/CC-TX-2026-06-21-001/transmission.pdf](archive/2026/CC-TX-2026-06-21-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-06-21-001.md](transmissions/2026/CC-TX-2026-06-21-001.md)

### CC-TX-2026-06-13-001 - Native Alpha Functional Workspace Expansion

- Status: Active Canon
- Layer: Native macOS Alpha / Clinical Workflow
- Abstract: Cody advanced the native macOS prototype from a visually strong shell into a broader working alpha, connecting core sidebar areas to real vault-derived workflows and verifying the build with 57 passing tests.
- HTML: [archive/2026/CC-TX-2026-06-13-001/index.html](archive/2026/CC-TX-2026-06-13-001/index.html)
- PDF: [archive/2026/CC-TX-2026-06-13-001/transmission.pdf](archive/2026/CC-TX-2026-06-13-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-06-13-001.md](transmissions/2026/CC-TX-2026-06-13-001.md)

### CC-TX-2026-05-28-005 - Export Path Hardening and Test Isolation Pass

- Status: Active Canon
- Layer: Session Workspace / Export Reliability
- Abstract: Cody completed a follow-through pass on Paula's draft export work, making the export destination configurable, recording the last exported file URL, and moving export tests out of the real Downloads folder. `swift build` and `Tools/run-tests.sh` both pass; the suite now contains 49 tests with 0 failures.
- HTML: [archive/2026/CC-TX-2026-05-28-005/index.html](archive/2026/CC-TX-2026-05-28-005/index.html)
- PDF: [archive/2026/CC-TX-2026-05-28-005/transmission.pdf](archive/2026/CC-TX-2026-05-28-005/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-28-005.md](transmissions/2026/CC-TX-2026-05-28-005.md)

### CC-TX-2026-05-28-004 - Pass 4 — Copy to Clipboard and .txt Export from GeneratedDraftPreview

- Status: Active Canon
- Layer: Session Workspace / Document Export
- Abstract: Pass 4 added copy-to-clipboard and `.txt` file export directly from the `GeneratedDraftPreview` card in the active session workspace. A new `exportNoteDraft(for:)` method on VaultStore handles the file write, following the `exportBackup()` pattern. A Copy button uses `NSPasteboard` with a 1.8-second "Copied" confirmation state. Two new XCTest methods cover the observable store side effects of the export path. Cody verified the pass with `swift build` and `Tools/run-tests.sh`; 48 tests passed with 0 failures.
- HTML: [archive/2026/CC-TX-2026-05-28-004/index.html](archive/2026/CC-TX-2026-05-28-004/index.html)
- PDF: [archive/2026/CC-TX-2026-05-28-004/transmission.pdf](archive/2026/CC-TX-2026-05-28-004/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-28-004.md](transmissions/2026/CC-TX-2026-05-28-004.md)

### CC-TX-2026-05-28-003 - Pass 3 — Inline-Editable Continuity Signals

- Status: Active Canon
- Layer: Session Workspace / Continuity Rail
- Abstract: Pass 3 made the continuity signals in the right rail inline-editable within the active session workspace. A single new VaultStore method handles the mutation. `ContinuitySignalRow` gained optional edit mode via an `onUpdate` closure; read-only display (home dashboard, empty states) is unchanged. Three new XCTest methods cover persistence, field isolation, and timestamp correctness. Cody verified the pass with `swift build` and `Tools/run-tests.sh`; 46 tests passed with 0 failures.
- HTML: [archive/2026/CC-TX-2026-05-28-003/index.html](archive/2026/CC-TX-2026-05-28-003/index.html)
- PDF: [archive/2026/CC-TX-2026-05-28-003/transmission.pdf](archive/2026/CC-TX-2026-05-28-003/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-28-003.md](transmissions/2026/CC-TX-2026-05-28-003.md)

### CC-TX-2026-05-28-002 - Pass 1 — Test Infrastructure and Verification Constraint

- Status: Active Canon
- Layer: Testing / Archive Infrastructure
- Abstract: Pass 1 established the first Swift test infrastructure for ConCOREdance. A test target was added to Package.swift, VaultStore was made URL-injectable for isolation, VaultCryptoError gained Equatable conformance, and 38 XCTest methods were written across three suites. `swift build` passes; `swift test` is currently blocked in Cody's local environment because the selected Command Line Tools install cannot resolve XCTest and does not expose xcodebuild.
- HTML: [archive/2026/CC-TX-2026-05-28-002/index.html](archive/2026/CC-TX-2026-05-28-002/index.html)
- PDF: [archive/2026/CC-TX-2026-05-28-002/transmission.pdf](archive/2026/CC-TX-2026-05-28-002/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-28-002.md](transmissions/2026/CC-TX-2026-05-28-002.md)

### CC-TX-2026-05-28-001 - Paula Accord Programming Consultant Orientation

- Status: Active Canon
- Layer: Personnel / Project Onboarding
- Abstract: Paula Accord has joined ConCOREdance as a programming consultant, oriented to the transmission archive, current SwiftUI prototype, implementation doctrine, and near-term engineering queue.
- HTML: [archive/2026/CC-TX-2026-05-28-001/index.html](archive/2026/CC-TX-2026-05-28-001/index.html)
- PDF: [archive/2026/CC-TX-2026-05-28-001/transmission.pdf](archive/2026/CC-TX-2026-05-28-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-28-001.md](transmissions/2026/CC-TX-2026-05-28-001.md)

### CC-TX-2026-05-27-007 - Workflow Spine Implementation & Naming Correction Pass

- Status: Active Canon
- Layer: Product Architecture / Clinical Workflow
- Abstract: Completed the first functional workflow spine for the ConCOREdance SwiftUI prototype, including selectable fixture sessions, an active-session workspace, locally persisted draft state, generated progress-note preview, session-aware continuity rail, save-state visibility, and corrected ConCOREdance asset naming.
- HTML: [archive/2026/CC-TX-2026-05-27-007/index.html](archive/2026/CC-TX-2026-05-27-007/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-007/transmission.pdf](archive/2026/CC-TX-2026-05-27-007/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-007.md](transmissions/2026/CC-TX-2026-05-27-007.md)

### CC-TX-2026-05-27-006 - Workflow Spine & Clinical Object Model Implementation Pass

- Status: Active Canon
- Layer: Product Architecture / Clinical Workflow
- Abstract: The ConCOREdance shell has reached its first atmospheric and interaction milestone. The next programming pass should move the project from visual shell toward functional clinical product by implementing the workflow spine: a real session lifecycle, a foundational clinical object model, local persistence, draft document generation, and visible continuity handoff between session work and archive memory.
- HTML: [archive/2026/CC-TX-2026-05-27-006/index.html](archive/2026/CC-TX-2026-05-27-006/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-006/transmission.pdf](archive/2026/CC-TX-2026-05-27-006/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-006.md](transmissions/2026/CC-TX-2026-05-27-006.md)

### CC-TX-2026-05-27-005 - Atmospheric Continuity & Adaptive Panels Implementation Pass

- Status: Active Canon
- Layer: Visual Shell / Interaction Architecture
- Abstract: Completed the next SwiftUI shell pass focused on atmospheric cohesion, adaptive narrative panels, identity rail refinement, continuity visibility, and screenshot-backed verification.
- HTML: [archive/2026/CC-TX-2026-05-27-005/index.html](archive/2026/CC-TX-2026-05-27-005/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-005/transmission.pdf](archive/2026/CC-TX-2026-05-27-005/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-005.md](transmissions/2026/CC-TX-2026-05-27-005.md)

### CC-TX-2026-05-27-004 - Implement Transmission Canonization Workflow

- Status: Active Canon
- Layer: Archive Automation
- Abstract: Implement a workflow that converts approved GitHub transmission issues into permanent markdown files within the repository.
- HTML: [archive/2026/CC-TX-2026-05-27-004/index.html](archive/2026/CC-TX-2026-05-27-004/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-004/transmission.pdf](archive/2026/CC-TX-2026-05-27-004/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-004.md](transmissions/2026/CC-TX-2026-05-27-004.md)

### CC-TX-2026-05-27-003 - Next Programming Pass — Atmospheric Continuity & Adaptive Panels

- Status: Active Canon
- Layer: Visual Shell / Interaction Architecture
- Abstract: Directive for the next implementation pass focusing on atmospheric cohesion, adaptive content expansion behavior, and refinement of the ConCOREdance shell identity.
- HTML: [archive/2026/CC-TX-2026-05-27-003/index.html](archive/2026/CC-TX-2026-05-27-003/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-003/transmission.pdf](archive/2026/CC-TX-2026-05-27-003/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-003.md](transmissions/2026/CC-TX-2026-05-27-003.md)

### CC-TX-2026-05-27-002 - Foundational Gratitude Transmission to Cody Valle

- Status: Active Canon
- Layer: Continuity / Collaboration
- Abstract: Formal acknowledgement and appreciation for Cody Valle’s foundational engineering and collaborative work in establishing the operational architecture now enabling active ConCOREdance transmissions.
- HTML: [archive/2026/CC-TX-2026-05-27-002/index.html](archive/2026/CC-TX-2026-05-27-002/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-002/transmission.pdf](archive/2026/CC-TX-2026-05-27-002/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-002.md](transmissions/2026/CC-TX-2026-05-27-002.md)

### CC-TX-2026-05-27-001 - Transmission Pipeline Validation Pass

- Status: Active Canon
- Layer: Infrastructure / Collaboration
- Abstract: Initial supervised transmission issued to validate end-to-end GitHub Issue workflow for ConCOREdance collaborative operations.
- HTML: [archive/2026/CC-TX-2026-05-27-001/index.html](archive/2026/CC-TX-2026-05-27-001/index.html)
- PDF: [archive/2026/CC-TX-2026-05-27-001/transmission.pdf](archive/2026/CC-TX-2026-05-27-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-27-001.md](transmissions/2026/CC-TX-2026-05-27-001.md)

### CC-TX-2026-05-26-002 - Public Transmission Archive Deployment Successful

- Status: Active Canon
- Layer: Continuity Infrastructure
- Abstract: Documents the migration to GitHub, launch of the public GitHub Pages archive, and establishment of the transmission archive as live continuity infrastructure.
- HTML: [archive/2026/CC-TX-2026-05-26-002/index.html](archive/2026/CC-TX-2026-05-26-002/index.html)
- PDF: [archive/2026/CC-TX-2026-05-26-002/transmission.pdf](archive/2026/CC-TX-2026-05-26-002/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-26-002.md](transmissions/2026/CC-TX-2026-05-26-002.md)

### CC-TX-2026-05-26-001 - How to Use the Concordance Transmission Template

- Status: Active Canon
- Layer: Operations
- Abstract: The official instructions for Cody on how to use the transmission template as the communication standard for ConCOREdance.
- HTML: [archive/2026/CC-TX-2026-05-26-001/index.html](archive/2026/CC-TX-2026-05-26-001/index.html)
- PDF: [archive/2026/CC-TX-2026-05-26-001/transmission.pdf](archive/2026/CC-TX-2026-05-26-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-26-001.md](transmissions/2026/CC-TX-2026-05-26-001.md)

### CC-TX-2026-05-24-003 - Snapshot Rendering Path Verified

- Status: Active Canon
- Layer: Visual Shell
- Abstract: Cody reports that coded UI snapshots render successfully and the ConCOREdance shell architecture is structurally aligned.
- HTML: [archive/2026/CC-TX-2026-05-24-003/index.html](archive/2026/CC-TX-2026-05-24-003/index.html)
- PDF: [archive/2026/CC-TX-2026-05-24-003/transmission.pdf](archive/2026/CC-TX-2026-05-24-003/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-24-003.md](transmissions/2026/CC-TX-2026-05-24-003.md)

### CC-TX-2026-05-24-002 - Cody Vale Implementation Role Definition

- Status: Active Canon
- Layer: Implementation Operations
- Abstract: Gregory defines Cody Vale's implementation remit across systems architecture, automation, infrastructure reliability, archive tooling, and deployment operations.
- HTML: [archive/2026/CC-TX-2026-05-24-002/index.html](archive/2026/CC-TX-2026-05-24-002/index.html)
- PDF: [archive/2026/CC-TX-2026-05-24-002/transmission.pdf](archive/2026/CC-TX-2026-05-24-002/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-24-002.md](transmissions/2026/CC-TX-2026-05-24-002.md)

### CC-TX-2026-05-24-001 - Cody Vale Joins the Implementation Team

- Status: Active Canon
- Layer: Implementation Leadership
- Abstract: Brandon formalizes Cody Vale's role as Lead Implementation Engineer for the ConCOREdance initiative.
- HTML: [archive/2026/CC-TX-2026-05-24-001/index.html](archive/2026/CC-TX-2026-05-24-001/index.html)
- PDF: [archive/2026/CC-TX-2026-05-24-001/transmission.pdf](archive/2026/CC-TX-2026-05-24-001/transmission.pdf)
- Markdown: [transmissions/2026/CC-TX-2026-05-24-001.md](transmissions/2026/CC-TX-2026-05-24-001.md)
