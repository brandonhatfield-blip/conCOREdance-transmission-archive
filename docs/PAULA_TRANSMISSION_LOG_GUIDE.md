# Paula Transmission Log Guide

Paula, this guide is the working standard for ConCOREdance transmission logs.

The transmission archive is public project memory. A transmission should read like a polished historical record, not a chat transcript, commit diary, debug log, or tool report.

## What Cody Expects

A good transmission log should answer five questions clearly:

1. What changed?
2. Why did it matter?
3. What project doctrine or decision did it advance?
4. How was it verified?
5. What should happen next?

Write for Neal, Gregory, Cody, and future contributors who need the project memory without reconstructing the whole work session.

## Voice

Use ConCOREdance canon voice:

- clear
- calm
- specific
- clinically and architecturally grounded
- public-facing
- respectful of Gregory's design intent
- concise enough to scan

Avoid:

- backstage process details
- tool names
- credential details
- authentication mechanics
- local machine problems
- personality imitation
- chatty self-explanation
- implementation trivia that does not affect the project record

Do not mention AI systems, prompt generation, model behavior, or internal tooling. If an asset exists, describe it as an archive asset or personnel image. The archive records the project, not the machinery behind the project.

## Required Fields

Every transmission request must include:

```text
ID:
Title:
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

Optional but expected for implementation work:

```text
Decisions:
Next Actions:
Assets:
```

## Field Parameters

**ID**

Use `CC-TX-YYYY-MM-DD-###`.

The date in the ID must match the `Date` field.

**Title**

Keep it under 80 characters when possible.

Good:

```text
Vault Persistence Test Infrastructure Pass
```

Avoid:

```text
What I Did Today After Several Problems With Git and Local Setup
```

**Type**

Use a stable category:

- `Programming Directive`
- `Implementation Log`
- `Orientation Log`
- `Decision Log`
- `Design Doctrine`
- `Infrastructure Log`
- `Review Log`

**Layer**

Name the project layer, not the activity mechanics.

Examples:

- `Clinical Workflow / Persistence`
- `Archive Infrastructure`
- `Visual Shell / Interaction Architecture`
- `Personnel / Project Onboarding`
- `Testing / Vault Integrity`

**From / To**

Use project roles or names. Keep it simple.

Examples:

```text
From: Paula Accord
To: Cody Valle
```

```text
From: Cody Valle
To: Neal and Gregory
```

**Tags**

Use 5 to 9 lowercase tags. Prefer hyphenated tags.

Good:

```text
testing, vault-persistence, swift, clinical-workflow, archive
```

Avoid vague tags like:

```text
stuff, update, work, notes
```

**Summary**

Use one sentence, ideally 25 to 45 words.

The summary appears on index cards, so it must not be huge.

**Body**

Use 3 to 6 short paragraphs.

Each paragraph should usually stay under 90 words.

Use bullets only when a list is genuinely easier to scan.

Do not paste long code snippets, command output, stack traces, logs, or file diffs into the body.

**Decisions**

Use 3 to 6 bullets.

Each bullet should be a durable project decision, not a description of effort.

Good:

```text
- VaultStore URL injection is the minimum refactor needed for test isolation.
```

Avoid:

```text
- I tried a few things and then Cody helped with a lock file.
```

**Next Actions**

Use 3 to 6 bullets.

Each bullet should start with a verb.

Good:

```text
- Add editable continuity signal controls to the active-session rail.
```

**Assets**

Use one asset per line:

```text
Assets:
- assets/conCOREdance-session.png | Active session workspace
```

For assets inside the transmission folder, use:

```text
assets/file-name.png
```

For shared archive assets, use a path that is correct from the final transmission page. Example from `01_Transmission_Archive/2026/CC-TX-.../transmission.html`:

```text
../../assets/personnel/paula_accord_headshot.png
```

Before publishing, confirm every image path opens locally.

## Public Record Boundaries

Include:

- product decisions
- implementation outcomes
- files or systems affected at a high level
- verification performed
- remaining risks or review needs
- next project actions

Do not include:

- personal access tokens
- credential storage details
- exact authentication setup
- local lock-file cleanup
- failed image-generation attempts
- tool names or model names
- rejected prompts
- temporary files
- private workspace paths unless the path is itself the durable project location
- anything that reads like a private operations transcript

If something operational matters, summarize it as a project-safe outcome.

Good:

```text
Archive publishing access was confirmed for Paula's contributor workflow.
```

Avoid:

```text
The remote was configured with a PAT stored in the sandbox credential store.
```

## Visual And HTML Safety

The publisher handles normal paragraphs, simple bullets, decisions, next actions, tags, and assets. Help it succeed by keeping the source clean.

Do:

- Keep summaries short.
- Keep bullet text under roughly 140 characters when possible.
- Break long explanations into multiple paragraphs.
- Use normal spaces and punctuation.
- Use `**bold**` sparingly.
- Use image captions under 90 characters.
- Use PNG or JPEG assets with predictable names.
- Use `conCOREdance` in filenames and `ConCOREdance` in prose.

Do not:

- Use raw HTML in transmission fields.
- Use tables.
- Use deeply nested bullets.
- Paste long URLs into visible body text.
- Paste command output.
- Paste long code blocks.
- Use unbroken strings longer than a normal sentence.
- Rename image files after publishing without updating every reference.

Overflow usually comes from long unbroken text, raw HTML, large code blocks, or enormous captions. If a line cannot wrap naturally, it probably does not belong in the transmission.

## Asset Checklist

Before publishing an entry with images:

1. Put transmission-specific images in:

```text
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/assets/
```

2. Use lowercase, hyphenated filenames where possible:

```text
conCOREdance-session.png
paula-accord.png
```

3. Avoid spaces in filenames.

4. Confirm the file exists at the exact path used in `Assets:`.

5. Open the generated `transmission.html` locally and confirm no broken image icon appears.

6. Check the archive index after publishing.

## Verification Checklist

Before asking Cody or Neal to review:

1. Markdown canon file exists:

```text
transmissions/YYYY/CC-TX-YYYY-MM-DD-###.md
```

2. Public archive page exists:

```text
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/transmission.html
```

3. Metadata exists:

```text
01_Transmission_Archive/YYYY/CC-TX-YYYY-MM-DD-###/metadata.json
```

4. `archive_manifest.json` contains the entry.

5. `01_Transmission_Archive/index.html` contains the entry.

6. The local page opens without:

- broken images
- text overflowing cards
- raw markdown showing in HTML
- huge captions
- wrong product spelling
- private process details

7. Search the entry for forbidden or risky terms before committing:

```text
AI
prompt
credential
token
PAT
sandbox
lock file
model
tool
```

Some words may be valid in older archive entries, but new Paula-authored transmissions should avoid them unless Cody explicitly approves.

## Preferred Transmission Shape

Use this structure for implementation logs:

```text
ID: CC-TX-YYYY-MM-DD-###
Title: Short Implementation Pass Name
Date: YYYY-MM-DD
Type: Implementation Log
Layer: Product Layer / Technical Layer
Status: Active Canon
From: Paula Accord
To: Cody Valle
Tags: swift, testing, vault-persistence, clinical-workflow, archive
Summary: One polished sentence that explains the outcome and why it matters.
Body:
Paragraph 1: State the completed pass and its project purpose.

Paragraph 2: Describe the main implementation changes at a high level.

Paragraph 3: Describe verification and any important constraints.

Paragraph 4: State what remains for the next pass.
Decisions:
- Durable decision one.
- Durable decision two.
- Durable decision three.
Next Actions:
- Next concrete action.
- Next concrete action.
- Next concrete action.
Assets:
- assets/example.png | Short caption
```

## Cody's Specific Ask

Paula, the best help you can give is bounded, testable, integration-friendly work.

Prioritize:

- vault persistence tests
- complete-session flow
- editable continuity signals
- note draft copy/export controls
- accessibility and resizing review

Keep the transmission log calm and canonical. Send the messy context to Cody separately if it matters. The archive should remember the work, not the backstage panic.
