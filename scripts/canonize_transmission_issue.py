#!/usr/bin/env python3
"""Canonize an approved ConCOREdance GitHub issue as durable Markdown.

This script is dependency-free so it can run in GitHub Actions with the stock
Python runtime. Markdown is the long-lived source record; the workflow can then
render the same issue into the public HTML archive.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TRANSMISSION_ROOT = Path("transmissions")
FIELD_NAMES = [
    "ID",
    "Title",
    "Date",
    "Type",
    "Layer",
    "Status",
    "From",
    "To",
    "Authorized By",
    "Tags",
    "Summary",
    "Body",
    "Decisions",
    "Next Actions",
    "Assets",
]

REQUIRED_FIELDS = [
    "ID",
    "Date",
    "Authorized By",
    "Summary",
    "Body",
]

ID_PATTERN = re.compile(r"^CC-TX-(\d{4})-(\d{2})-(\d{2})-(\d{3})$")
CANON_LABELS = {"canonize", "approved", "active canon"}
BLOCK_LABELS = {"canonized", "do-not-canonize", "needs-revision"}


class CanonizeError(RuntimeError):
    pass


def read_event(event_path: Path) -> dict[str, Any]:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    if not issue:
        raise CanonizeError("GitHub event does not contain an issue payload.")
    if (issue.get("pull_request") or {}).get("url"):
        raise CanonizeError("Pull requests are not canonized by this workflow.")
    return event


def normalize_label(line: str) -> str | None:
    stripped = line.strip()
    for field in FIELD_NAMES:
        if re.match(rf"^{re.escape(field)}\s*:", stripped, flags=re.IGNORECASE):
            return field
    return None


def parse_request(text: str) -> dict[str, str]:
    data: dict[str, list[str]] = {}
    current: str | None = None

    for raw_line in text.splitlines():
        label = normalize_label(raw_line)
        if label:
            current = label
            _, value = raw_line.split(":", 1)
            data.setdefault(current, [])
            if value.strip():
                data[current].append(value.strip())
            continue
        if current:
            data.setdefault(current, []).append(raw_line.rstrip())

    parsed = {key: "\n".join(value).strip() for key, value in data.items()}
    missing = [field for field in REQUIRED_FIELDS if not parsed.get(field)]
    if missing:
        raise CanonizeError(f"Missing required field(s): {', '.join(missing)}")
    return parsed


def labels_from_issue(issue: dict[str, Any]) -> set[str]:
    return {
        str(label.get("name", "")).strip().lower()
        for label in issue.get("labels", [])
        if str(label.get("name", "")).strip()
    }


def should_canonize(event: dict[str, Any]) -> bool:
    action = event.get("action")
    issue = event.get("issue") or {}
    labels = labels_from_issue(issue)
    if labels & BLOCK_LABELS:
        return False
    if action == "labeled":
        label = str((event.get("label") or {}).get("name", "")).strip().lower()
        return label in CANON_LABELS
    if action == "closed":
        return bool(labels & CANON_LABELS)
    return False


def split_tags(raw: str) -> list[str]:
    tags = [
        chunk.strip(" -*\t")
        for chunk in re.split(r"[,;\n]", raw)
        if chunk.strip(" -*\t")
    ]
    return tags


def markdown_list(raw: str) -> str:
    items = [line.strip(" -*\t") for line in raw.splitlines() if line.strip(" -*\t")]
    if not items:
        return "_None recorded._"
    return "\n".join(f"- {item}" for item in items)


def yaml_scalar(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(yaml_scalar(value) for value in values) + "]"


def issue_title(issue: dict[str, Any]) -> str:
    title = str(issue.get("title") or "").strip()
    title = re.sub(r"^Transmission Request:\s*", "", title, flags=re.IGNORECASE).strip()
    if not title:
        raise CanonizeError("Issue title is empty and no Title field was provided.")
    return title


def validate(data: dict[str, str]) -> tuple[str, Path]:
    match = ID_PATTERN.match(data["ID"])
    if not match:
        raise CanonizeError("ID must match CC-TX-YYYY-MM-DD-###.")

    year, month, day, _ = match.groups()
    id_date = f"{year}-{month}-{day}"
    date_value = data.get("Date") or id_date
    if date_value != id_date:
        raise CanonizeError(f"Date must match the date embedded in ID: {id_date}.")

    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError as exc:
        raise CanonizeError("Date must be a valid YYYY-MM-DD date.") from exc

    return year, TRANSMISSION_ROOT / year / f"{data['ID']}.md"


def render_markdown(data: dict[str, str], issue: dict[str, Any], path: Path) -> str:
    tags = split_tags(data.get("Tags", ""))
    issue_number = issue.get("number")
    issue_url = issue.get("html_url", "")
    canonized_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    front_matter = [
        "---",
        f"id: {yaml_scalar(data['ID'])}",
        f"title: {yaml_scalar(data['Title'])}",
        f"date: {yaml_scalar(data.get('Date', ''))}",
        f"type: {yaml_scalar(data.get('Type', 'Transmission'))}",
        f"layer: {yaml_scalar(data.get('Layer', 'Archive Canon'))}",
        f"status: {yaml_scalar(data.get('Status', 'Active Canon'))}",
        f"from: {yaml_scalar(data.get('From', ''))}",
        f"to: {yaml_scalar(data.get('To', ''))}",
        f"authorized_by: {yaml_scalar(data.get('Authorized By', ''))}",
        f"tags: {yaml_list(tags)}",
        f"source_issue: {issue_number}",
        f"source_url: {yaml_scalar(issue_url)}",
        f"canonical_path: {yaml_scalar(str(path))}",
        f"canonized_at: {yaml_scalar(canonized_at)}",
        "---",
        "",
    ]

    sections = [
        f"# {data['Title']}",
        "",
        f"**ID:** {data['ID']}",
        f"**Status:** {data.get('Status', 'Active Canon')}",
        f"**Authorized By:** {data.get('Authorized By', 'Not recorded')}",
        f"**Source Issue:** #{issue_number}",
        "",
        "## Summary",
        "",
        data["Summary"],
        "",
        "## Body",
        "",
        data["Body"],
        "",
        "## Decisions",
        "",
        markdown_list(data.get("Decisions", "")),
        "",
        "## Next Actions",
        "",
        markdown_list(data.get("Next Actions", "")),
    ]

    assets = data.get("Assets", "").strip()
    if assets:
        sections.extend(["", "## Assets", "", markdown_list(assets)])

    sections.extend(
        [
            "",
            "## Provenance",
            "",
            f"- Canonized from GitHub Issue #{issue_number}: {issue_url}",
            f"- Authorized by: {data.get('Authorized By', 'Not recorded')}",
            f"- Canonized at: {canonized_at}",
        ]
    )

    return "\n".join(front_matter + sections).rstrip() + "\n"


def write_outputs(result: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as fh:
        for key, value in result.items():
            delimiter = f"EOF_{key.upper()}"
            fh.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")


def canonize(event_path: Path) -> dict[str, str]:
    event = read_event(event_path)
    issue = event["issue"]
    if not should_canonize(event):
        raise CanonizeError("Issue is not in an approved canonization state.")

    body = issue.get("body") or ""
    if not body.strip():
        raise CanonizeError("Issue body is empty.")

    data = parse_request(body)
    data["Title"] = data.get("Title") or issue_title(issue)
    year, path = validate(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(data, issue, path), encoding="utf-8")

    result = {
        "transmission_id": data["ID"],
        "transmission_title": data["Title"],
        "transmission_year": year,
        "transmission_path": str(path),
        "issue_number": str(issue.get("number", "")),
    }
    write_outputs(result)
    return result


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Canonize an approved transmission issue.")
    parser.add_argument("--issue-event", type=Path, required=True, help="Path to GitHub issue event JSON.")
    parser.add_argument("--output-json", type=Path, help="Optional path for a JSON result file.")
    args = parser.parse_args(argv)

    try:
        result = canonize(args.issue_event)
        if args.output_json:
            args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    except CanonizeError as exc:
        print(f"Transmission canonization failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
