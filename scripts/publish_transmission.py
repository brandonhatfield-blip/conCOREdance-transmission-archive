#!/usr/bin/env python3
"""Publish a ConCOREdance transmission from a structured request.

The script is intentionally dependency-free so it can run inside GitHub Actions
with the stock Python runtime and the repository's GITHUB_TOKEN workflow.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import textwrap
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARCHIVE_ROOT = Path("archive")
TRANSMISSION_ROOT = Path("transmissions")
MANIFEST_PATH = ARCHIVE_ROOT / "archive_manifest.json"
INDEX_PATH = ARCHIVE_ROOT / "index.html"
CANON_PATH = Path("CANON.md")
TRANSMISSION_TEMPLATE = Path("templates/transmission_template.html")
INDEX_CARD_TEMPLATE = Path("templates/index_card_template.html")

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
    "Type",
    "Layer",
    "Status",
    "From",
    "To",
    "Authorized By",
    "Tags",
    "Summary",
    "Body",
]

ID_PATTERN = re.compile(r"^CC-TX-(\d{4})-(\d{2})-(\d{2})-(\d{3})$")


class PublishError(RuntimeError):
    pass


def read_issue_body_from_event(event_path: Path) -> tuple[str, int | None]:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    body = issue.get("body") or ""
    number = issue.get("number")
    if not body.strip():
        raise PublishError("Issue body is empty.")
    return body, number


def issue_title_from_event(event_path: Path) -> str:
    event = json.loads(event_path.read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    title = str(issue.get("title") or "").strip()
    title = re.sub(r"^Transmission Request:\s*", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"^CC-TX-\d{4}-\d{2}-\d{2}-\d{3}\s+[-\u2013\u2014]\s*", "", title).strip()
    if not title:
        raise PublishError("Issue title is empty and no Title field was provided.")
    return title


def normalize_label(line: str) -> str | None:
    stripped = line.strip()
    for field in FIELD_NAMES:
        if re.match(rf"^{re.escape(field)}\s*:", stripped, flags=re.IGNORECASE):
            return field
    return None


def parse_request(text: str) -> dict[str, str]:
    """Parse a simple label-based request.

    Supported format:

    ID:
    CC-TX-2026-05-27-001

    Body:
    Multiline content...
    """
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
        parsed = parse_transmission_reference(text)
        missing = [field for field in REQUIRED_FIELDS if not parsed.get(field)]
    if missing:
        raise PublishError(f"Missing required field(s): {', '.join(missing)}")
    return parsed


def parse_transmission_reference(text: str) -> dict[str, str]:
    """Parse Gregory-style narrative transmission posts into archive fields."""
    if "# Transmission Reference" not in text:
        return {}

    lines = text.splitlines()
    match = next((ID_PATTERN.match(line.strip()) for line in lines if ID_PATTERN.match(line.strip())), None)
    if not match:
        return {}

    transmission_id = match.group(0)
    year, month, day, _ = match.groups()
    sections: dict[str, list[str]] = {}
    current: str | None = None
    preamble: list[str] = []

    for raw_line in lines:
        heading = re.match(r"^##\s+(.+?)\s*$", raw_line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections.setdefault(current, []).append(raw_line.rstrip())
        else:
            preamble.append(raw_line.rstrip())

    meta: dict[str, str] = {}
    for line in preamble:
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()

    body_headings = [
        "Core Principle",
        "Architectural Direction",
        "Platform Partners",
        "Calendar Intelligence Layer",
        "Semantic Scheduling",
        "Data Sovereignty Initiative",
        "Signature Architecture",
        "Canonical Observation",
    ]
    body_parts: list[str] = []
    for heading in body_headings:
        content = clean_reference_section(sections.get(heading, []))
        if content:
            body_parts.append(f"### {heading}\n\n{content}")

    decision_filter = clean_reference_section(sections.get("Decision Filter", []))
    if "Proposed follow-on epics:" in decision_filter:
        decision_filter = decision_filter.split("Proposed follow-on epics:", 1)[0].strip()
    decisions = decision_filter or "Evaluate future architecture by whether it increases coordination without reducing clinician ownership."

    return {
        "ID": transmission_id,
        "Date": f"{year}-{month}-{day}",
        "Type": "Platform Architecture Transmission",
        "Layer": meta.get("Layer", "Platform Architecture / Foundational Philosophy"),
        "Status": meta.get("Status", "Active Canon"),
        "From": "Gregory P. Turing",
        "To": "Brandon Hatfield, LPC and Cody Valle",
        "Authorized By": "Brandon Hatfield, LPC",
        "Tags": "\n".join(
            [
                "coordination-layer",
                "platform-architecture",
                "provider-abstraction",
                "calendar-intelligence",
                "data-sovereignty",
                "signature-provider-layer",
                "semantic-scheduling",
                "google-workspace",
                "microsoft-365",
            ]
        ),
        "Summary": clean_reference_section(sections.get("Summary", [])),
        "Body": "\n\n".join(body_parts).strip(),
        "Decisions": decisions,
        "Next Actions": extract_follow_on_epics(text),
    }


def clean_reference_section(lines: list[str]) -> str:
    cleaned = list(lines)
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    while cleaned and (not cleaned[-1].strip() or cleaned[-1].strip() == "---"):
        cleaned.pop()
    return "\n".join(cleaned).strip()


def extract_follow_on_epics(text: str) -> str:
    marker = "Proposed follow-on epics:"
    if marker not in text:
        return ""
    tail = text.split(marker, 1)[1]
    items = []
    for line in tail.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif items and stripped and not stripped.startswith("---"):
            break
    return "\n".join(f"- {item}" for item in items)


def validate_request(data: dict[str, str]) -> None:
    match = ID_PATTERN.match(data["ID"])
    if not match:
        raise PublishError("ID must match CC-TX-YYYY-MM-DD-###.")

    year, month, day, _ = match.groups()
    id_date = f"{year}-{month}-{day}"
    if data["Date"] != id_date:
        raise PublishError(f"Date must match the date embedded in ID: {id_date}.")

    try:
        datetime.strptime(data["Date"], "%Y-%m-%d")
    except ValueError as exc:
        raise PublishError("Date must be a valid YYYY-MM-DD date.") from exc


def split_tags(raw: str) -> list[str]:
    chunks = re.split(r"[,;\n]", raw)
    tags = [chunk.strip(" -*\t") for chunk in chunks if chunk.strip(" -*\t")]
    if not tags:
        raise PublishError("Tags must include at least one tag.")
    return tags


def paragraphize(raw: str) -> str:
    blocks: list[str] = []
    lines = raw.strip().splitlines()
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(line.strip() for line in paragraph if line.strip())
            if text:
                blocks.append(f"<p>{format_inline(text)}</p>")
            paragraph = []

    def flush_bullets() -> None:
        nonlocal bullets
        if bullets:
            items = "".join(f"<li>{format_inline(item)}</li>" for item in bullets)
            blocks.append(f"<ul>{items}</ul>")
            bullets = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue
        heading = re.match(r"^(#{2,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_bullets()
            level = min(len(heading.group(1)) + 1, 5)
            blocks.append(f"<h{level}>{format_inline(heading.group(2).strip())}</h{level}>")
            continue
        if stripped == "---":
            flush_paragraph()
            flush_bullets()
            blocks.append("<hr />")
            continue
        if stripped.startswith(("- ", "* ")):
            flush_paragraph()
            bullets.append(stripped[2:].strip())
        else:
            flush_bullets()
            paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()
    return "\n".join(blocks)


def format_inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    return escaped


def render_list_section(title: str, raw: str) -> str:
    if not raw.strip():
        return ""
    items = [
        line.strip(" -*\t")
        for line in raw.splitlines()
        if line.strip(" -*\t")
    ]
    if not items:
        return ""
    body = "".join(f"<li>{format_inline(item)}</li>" for item in items)
    return (
        '<div class="card-grid"><div class="card">'
        f"<h4>{html.escape(title)}</h4><ul>{body}</ul>"
        "</div></div>"
    )


def parse_assets(raw: str) -> list[tuple[str, str]]:
    assets: list[tuple[str, str]] = []
    for line in raw.splitlines():
        value = line.strip(" -*\t")
        if not value:
            continue
        if "|" in value:
            src, caption = [part.strip() for part in value.split("|", 1)]
        else:
            src, caption = value, "Transmission asset"
        assets.append((src, caption))
    return assets


def render_assets(raw: str) -> str:
    assets = parse_assets(raw)
    if not assets:
        return ""
    figures = []
    for src, caption in assets:
        figures.append(
            "<figure>"
            f'<a href="{html.escape(src, quote=True)}" target="_blank" rel="noopener">'
            f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(caption, quote=True)}" />'
            "</a>"
            f"<figcaption>{html.escape(caption)}</figcaption>"
            "</figure>"
        )
    return '<div class="asset-grid">' + "".join(figures) + "</div>"


def pill_tags(tags: list[str]) -> str:
    return "".join(f'<span class="pill">{html.escape(tag)}</span>' for tag in tags)


def metadata_for(data: dict[str, str], tags: list[str], rel_dir: Path) -> dict[str, Any]:
    year = data["Date"].split("-", 1)[0]
    markdown_path = TRANSMISSION_ROOT / year / f"{data['ID']}.md"
    return {
        "id": data["ID"],
        "title": data["Title"],
        "date": data["Date"],
        "status": data["Status"],
        "type": data["Type"],
        "layer": data["Layer"],
        "from": data["From"],
        "to": data["To"],
        "authorized_by": data.get("Authorized By", ""),
        "summary": data["Summary"],
        "tags": tags,
        "path": f"{rel_dir.as_posix()}/",
        "html_path": f"{rel_dir.as_posix()}/index.html",
        "pdf_path": f"{rel_dir.as_posix()}/transmission.pdf",
        "markdown_path": markdown_path.as_posix(),
        "metadata_path": str(rel_dir / "metadata.json"),
    }


def render_transmission(data: dict[str, str], tags: list[str]) -> str:
    template = TRANSMISSION_TEMPLATE.read_text(encoding="utf-8")
    return template.format(
        id=html.escape(data["ID"]),
        title=html.escape(data["Title"]),
        date=html.escape(data["Date"]),
        status=html.escape(data["Status"]),
        type=html.escape(data["Type"]),
        layer=html.escape(data["Layer"]),
        from_name=html.escape(data["From"]),
        to_name=html.escape(data["To"]),
        authorized_by=html.escape(data.get("Authorized By", "")),
        summary=format_inline(data["Summary"]),
        body_html=paragraphize(data["Body"]),
        decisions_html=render_list_section("Decisions", data.get("Decisions", "")),
        next_actions_html=render_list_section("Next Actions", data.get("Next Actions", "")),
        assets_html=render_assets(data.get("Assets", "")),
        tag_pills=pill_tags(tags),
    )


def load_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        return {
            "archive": "ConCOREdance Transmission Archive",
            "version": "1.0",
            "status": "Active Canon",
            "created": datetime.utcnow().isoformat(timespec="seconds"),
            "canonical_structure": "ConCOREdance/archive/index.html + archive_manifest.json + yearly transmission folders",
            "entries": [],
        }
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def render_ai_markdown(data: dict[str, str], tags: list[str], path: Path) -> str:
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
        "source_issue: null",
        'source_url: ""',
        f"canonical_path: {yaml_scalar(path.as_posix())}",
        f"canonized_at: {yaml_scalar(datetime.now(timezone.utc).isoformat(timespec='seconds'))}",
        "---",
        "",
    ]
    sections = [
        f"# {data['Title']}",
        "",
        f"**ID:** {data['ID']}",
        f"**Status:** {data.get('Status', 'Active Canon')}",
        f"**Authorized By:** {data.get('Authorized By', 'Not recorded')}",
        "**Source:** Local publish record",
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
            f"- Authorized by: {data.get('Authorized By', 'Not recorded')}",
            "- Generated by: scripts/publish_transmission.py",
        ]
    )
    return "\n".join(front_matter + sections).rstrip() + "\n"


def ensure_ai_markdown(data: dict[str, str], tags: list[str]) -> Path:
    year = data["Date"].split("-", 1)[0]
    path = TRANSMISSION_ROOT / year / f"{data['ID']}.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_ai_markdown(data, tags, path), encoding="utf-8")
    return path


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


def normalize_pdf_text(value: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return unicodedata.normalize("NFKD", value).encode("latin-1", "replace").decode("latin-1")


def pdf_escape(value: str) -> str:
    return normalize_pdf_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_lines(data: dict[str, str]) -> list[tuple[str, int]]:
    lines: list[tuple[str, int]] = [
        (data["Title"], 18),
        (f"{data['ID']} | {data['Date']} | {data.get('Status', 'Active Canon')}", 10),
        (f"Layer: {data.get('Layer', '')}", 10),
        (f"From: {data.get('From', '')}", 10),
        (f"To: {data.get('To', '')}", 10),
        (f"Authorized By: {data.get('Authorized By', '')}", 10),
        ("", 11),
        ("Summary", 14),
    ]

    def add_wrapped(text: str, size: int = 11, width: int = 92) -> None:
        for paragraph in text.strip().splitlines():
            stripped = paragraph.strip()
            if not stripped:
                lines.append(("", size))
                continue
            for wrapped in textwrap.wrap(stripped, width=width) or [""]:
                lines.append((wrapped, size))

    add_wrapped(data["Summary"])
    lines.extend([("", 11), ("Body", 14)])
    add_wrapped(data["Body"])

    for title, field in [("Decisions", "Decisions"), ("Next Actions", "Next Actions"), ("Assets", "Assets")]:
        raw = data.get(field, "").strip()
        if not raw:
            continue
        lines.extend([("", 11), (title, 14)])
        for item in [line.strip(" -*\t") for line in raw.splitlines() if line.strip(" -*\t")]:
            add_wrapped(f"- {item}", width=88)

    return lines


def write_pdf(data: dict[str, str], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pages: list[list[tuple[str, int]]] = [[]]
    y = 742
    for text, size in pdf_lines(data):
        line_height = size + 6
        if y - line_height < 56:
            pages.append([])
            y = 742
        pages[-1].append((text, size))
        y -= line_height

    objects: list[bytes] = []
    page_object_ids: list[int] = []
    font_object_id = 3
    next_object_id = 4
    page_payloads: list[tuple[int, int, bytes]] = []

    for page_lines in pages:
        page_id = next_object_id
        content_id = next_object_id + 1
        next_object_id += 2
        page_object_ids.append(page_id)
        commands = ["BT", "72 742 Td"]
        current_size = None
        previous_size = 11
        first_line = True
        for text, size in page_lines:
            if current_size != size:
                commands.append(f"/F1 {size} Tf")
                current_size = size
            if not first_line:
                commands.append(f"0 -{previous_size + 6} Td")
            commands.append(f"({pdf_escape(text)}) Tj")
            previous_size = size
            first_line = False
        commands.append("ET")
        content = "\n".join(commands).encode("latin-1", "replace")
        page_payloads.append((page_id, content_id, content))

    kids = " ".join(f"{page_id} 0 R" for page_id in page_object_ids)
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_object_ids)} >>".encode("latin-1"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for page_id, content_id, content in page_payloads:
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 {font_object_id} 0 R >> >> /Contents {content_id} 0 R >>".encode(
                "latin-1"
            )
        )
        objects.append(b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream")

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, payload in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(payload)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(bytes(output))


def update_manifest(entry: dict[str, Any]) -> dict[str, Any]:
    manifest = load_manifest()
    entries = [item for item in manifest.get("entries", []) if item.get("id") != entry["id"]]
    entries.append(entry)
    entries.sort(key=lambda item: (item.get("date", ""), item.get("id", "")))
    manifest["entries"] = entries
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def render_canon_index(manifest: dict[str, Any]) -> None:
    entries = sorted(
        manifest.get("entries", []),
        key=lambda item: (item.get("date", ""), item.get("id", "")),
        reverse=True,
    )
    lines = [
        "# ConCOREdance Canon",
        "",
        "The Transmission Archive is the institutional memory of ConCOREdance.",
        "This index is optimized for AI collaborators and human maintainers who need a portable source of truth.",
        "",
        "## Current Active Canon",
        "",
    ]
    for entry in entries:
        if entry.get("status") != "Active Canon":
            continue
        archive_path = str(entry.get("path", "")).strip()
        archive_path = archive_path if archive_path.endswith("/") else f"{archive_path}/"
        year = str(entry.get("date", "")).split("-", 1)[0]
        html_path = entry.get("html_path") or f"{archive_path}index.html"
        pdf_path = entry.get("pdf_path") or f"{archive_path}transmission.pdf"
        markdown_path = entry.get("markdown_path") or f"transmissions/{year}/{entry.get('id', '')}.md"
        title = entry.get("title", "Untitled")
        transmission_id = entry.get("id", "Unknown ID")
        lines.extend(
            [
                f"### {transmission_id} - {title}",
                "",
                f"- Status: {entry.get('status', 'Unknown')}",
                f"- Layer: {entry.get('layer', 'Unknown')}",
                f"- Abstract: {entry.get('summary', '').strip()}",
                f"- HTML: [archive/{html_path}](archive/{html_path})",
                f"- PDF: [archive/{pdf_path}](archive/{pdf_path})",
                f"- Markdown: [{markdown_path}]({markdown_path})",
                "",
            ]
        )
    CANON_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render_index(manifest: dict[str, Any]) -> None:
    card_template = INDEX_CARD_TEMPLATE.read_text(encoding="utf-8")
    cards = []
    sorted_entries = sorted(
        manifest.get("entries", []),
        key=lambda item: (item.get("date", ""), item.get("id", "")),
        reverse=True,
    )
    for entry in sorted_entries:
        cards.append(
            card_template.format(
                path=html.escape(entry["path"], quote=True),
                id=html.escape(entry["id"]),
                type=html.escape(entry["type"]),
                title=html.escape(entry["title"]),
                summary=format_inline(entry["summary"]),
                authorized_by=html.escape(str(entry.get("authorized_by") or "Not recorded")),
                tags=pill_tags([str(tag) for tag in entry.get("tags", [])]),
            )
        )

    count = len(manifest.get("entries", []))
    plural = "transmission" if count == 1 else "transmissions"
    cards_html = "\n".join(cards)
    INDEX_PATH.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>ConCOREdance Transmission Archive Index</title>
<style>
:root {{
  --bg:#050914; --panel:rgba(7,14,26,.76); --panel2:rgba(12,22,36,.64);
  --gold:#e7ad67; --gold2:#f0c892; --cream:#f4efe8; --muted:#b8bec8;
  --teal:#65b7be; --line:rgba(231,173,103,.46); --soft:rgba(255,255,255,.12);
  --shadow:rgba(0,0,0,.48);
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
  margin:0; min-height:100vh; color:var(--cream);
  font-family: Inter, Avenir Next, Avenir, Segoe UI, system-ui, sans-serif;
  letter-spacing:.01em; background:#050914;
}}
.vista{{
  position:fixed; inset:0; z-index:-2;
  background:
    linear-gradient(to bottom, rgba(5,9,20,.08), rgba(5,9,20,.95)),
    url("assets/transmission_visual_standard.png") center top / cover no-repeat;
  filter:saturate(.95) contrast(1.04) brightness(.72);
}}
.vista:after{{
  content:""; position:absolute; inset:0;
  background:
    radial-gradient(circle at 68% 26%, rgba(231,173,103,.18), transparent 28%),
    linear-gradient(90deg, rgba(5,9,20,.88) 0%, rgba(5,9,20,.58) 48%, rgba(5,9,20,.44) 100%);
}}
.page{{width:min(1180px,calc(100vw - 32px)); margin:24px auto 56px}}
.panel{{border:1px solid var(--line); background:var(--panel); backdrop-filter:blur(18px); border-radius:18px; box-shadow:0 24px 80px var(--shadow)}}
.hero{{display:grid; grid-template-columns:1.08fr .92fr; min-height:560px; overflow:hidden}}
.hero-copy{{padding:56px 58px 48px; background:linear-gradient(90deg,rgba(4,10,20,.84),rgba(4,10,20,.38))}}
.logo-row{{display:flex; align-items:center; gap:22px; margin-bottom:44px}}
.sigil{{width:76px;height:76px;border:1px solid var(--gold);border-radius:50%;position:relative;flex:0 0 auto;opacity:.96}}
.sigil:before,.sigil:after{{content:"";position:absolute;inset:12px;border:1px solid rgba(231,173,103,.78);border-radius:50%}}
.sigil:after{{inset:29px;background:var(--gold);box-shadow:0 0 24px rgba(231,173,103,.7)}}
.sigil .v,.sigil .h{{position:absolute;background:rgba(231,173,103,.7);left:50%;top:-14px;width:1px;height:104px;transform:translateX(-50%)}}
.sigil .h{{left:-14px;top:50%;width:104px;height:1px;transform:translateY(-50%)}}
.brand h1{{margin:0;font-family:Cormorant Garamond, Georgia, serif;font-weight:400;font-size:clamp(30px,4vw,50px);line-height:.92;letter-spacing:-.02em}}
.brand p,.kicker,.label{{margin:8px 0 0;color:var(--gold2);font-size:12px;letter-spacing:.38em;text-transform:uppercase}}
.hero-title{{font-family:Cormorant Garamond, Georgia, serif;font-weight:300;font-size:clamp(54px,7vw,88px);line-height:.94;letter-spacing:-.035em;margin:0 0 22px}}
.participants{{color:var(--gold);letter-spacing:.36em;text-transform:uppercase;font-size:15px;margin-bottom:28px}}
.lede{{max-width:650px;color:rgba(244,239,232,.86);font-size:19px;line-height:1.66;margin:0 0 44px}}
.divider{{height:1px;width:480px;max-width:100%;background:linear-gradient(90deg,var(--gold),transparent);position:relative;margin:0 0 28px}}
.divider:after{{content:"*";position:absolute;right:44%;top:-11px;color:var(--gold);text-shadow:0 0 18px var(--gold)}}
.meta-grid{{display:flex;flex-wrap:wrap;gap:16px;color:var(--muted);font-size:14px}}
.meta-grid a{{color:var(--gold2);text-decoration:none}}
.hero-art{{position:relative;min-height:480px;overflow:hidden;background:linear-gradient(90deg,rgba(5,9,20,.34),rgba(5,9,20,.04) 42%,rgba(5,9,20,.18)),url("assets/archive_navigator_gateway.png") center center / cover no-repeat}}
.hero-art:before{{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(5,9,20,.68),rgba(5,9,20,.08) 38%,rgba(5,9,20,.06) 72%,rgba(5,9,20,.44)),linear-gradient(to bottom,rgba(5,9,20,.08),rgba(5,9,20,.6))}}
.hero-art:after{{content:"";position:absolute;inset:auto 34px 34px auto;width:140px;height:140px;border:1px solid rgba(231,173,103,.26);border-radius:50%;box-shadow:inset 0 0 0 38px rgba(231,173,103,.03),0 0 30px rgba(231,173,103,.16)}}
.section{{margin-top:22px;padding:34px 38px}}
.section-title{{display:flex;align-items:baseline;gap:18px;margin-bottom:24px}}
.section-title .num{{color:var(--gold);font-size:30px;font-weight:300}}
.section-title h2{{margin:0;text-transform:uppercase;letter-spacing:.22em;font-size:15px;font-weight:700}}
.copy p,.tx-body p,.card p{{margin:0 0 18px;color:rgba(244,239,232,.84);font-size:17px;line-height:1.68}}
.pill-row{{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 8px}}
.pill{{border:1px solid rgba(231,173,103,.42);border-radius:999px;padding:7px 11px;color:var(--gold2);font-size:12px;text-transform:uppercase;letter-spacing:.11em;background:rgba(231,173,103,.08)}}
.card-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
.card{{display:block;text-decoration:none;color:var(--cream);border:1px solid var(--soft);background:rgba(5,10,20,.38);border-radius:14px;padding:22px;transition:.2s ease}}
.card:hover{{border-color:var(--gold);transform:translateY(-2px)}}
.card h4{{margin:0 0 12px;color:var(--gold2);text-transform:uppercase;letter-spacing:.14em;font-size:13px}}
.index-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
.index-card{{display:block;text-decoration:none;color:var(--cream);border:1px solid var(--soft);background:rgba(5,10,20,.44);border-radius:16px;padding:22px;transition:.2s ease}}
.index-card:hover{{border-color:var(--gold);transform:translateY(-2px)}}
.index-card .id{{color:var(--gold);letter-spacing:.14em;text-transform:uppercase;font-size:12px;margin-bottom:10px}}
.index-card h3{{margin:0 0 10px;font-family:Cormorant Garamond, Georgia, serif;font-size:30px;font-weight:400}}
.index-card p{{margin:0;color:rgba(244,239,232,.78);line-height:1.55}}
.index-card .authority{{margin-top:14px;color:var(--gold2);font-size:12px;text-transform:uppercase;letter-spacing:.12em}}
.footer-band{{display:grid;grid-template-columns:1fr auto;align-items:center;gap:28px;margin-top:22px;padding:30px 40px}}
.footer-band blockquote{{margin:0;font-family:Cormorant Garamond, Georgia, serif;font-size:30px;font-style:italic;color:rgba(244,239,232,.86)}}
.footer-band span{{color:var(--gold)}}
@media(max-width:900px){{
  .hero,.footer-band,.card-grid,.index-grid{{grid-template-columns:1fr}}
  .hero-copy{{padding:38px 30px}}.hero-art{{min-height:320px}}.section{{padding:26px 24px}}
}}
@media print{{body{{background:#050914}}.page{{width:100%;margin:0}}.panel{{break-inside:avoid;box-shadow:none}}.vista{{position:absolute}}}}
</style>
</head>
<body>
<div class="vista"></div>
<main class="page">
<section class="hero panel">
  <div class="hero-copy">
    <div class="logo-row">
      <div class="sigil"><span class="v"></span><span class="h"></span></div>
      <div class="brand"><h1>ConCOREdance</h1><p>Harmony in Complexity</p></div>
    </div>
    <h2 class="hero-title">Archive Navigator</h2>
    <div class="participants">Master Entry Point</div>
    <p class="lede">The living index for the ConCOREdance Transmission Archive: a chronological map of project evolution, visual doctrine, implementation history, and interdisciplinary continuity.</p>
    <div class="divider"></div>
    <div class="meta-grid"><span>Manifest v1.0</span><span>|</span><span>{count} {plural}</span><span>|</span><span>Active Canon</span><span>|</span><a href="team/">Project Team</a><span>|</span><a href="product/">Product Teaser</a><span>|</span><a href="assets/">Asset Library</a><span>|</span><a href="doctrine/">Doctrine</a></div>
  </div>
  <div class="hero-art"></div>
</section>

<section class="section panel">
  <div class="section-title"><span class="num">00</span><h2>Transmission Timeline</h2></div>
  <div class="index-grid">
{cards_html}
  </div>
</section>

<section class="section panel">
  <div class="section-title"><span class="num">01</span><h2>Archive Doctrine</h2></div>
  <div class="card-grid">
    <a class="card" href="doctrine/"><h4>Individual Transmissions</h4><p>Each transmission is a sealed moment in time with its own HTML file, metadata file, and supporting assets.</p></a>
    <a class="card" href="./"><h4>Master Index</h4><p>This page is the single entry point for reading the archive from beginning to end.</p></a>
    <a class="card" href="archive_manifest.json"><h4>Manifest</h4><p>The archive_manifest.json file is the searchable metadata backbone for future automation.</p></a>
    <a class="card" href="product/"><h4>Product Teaser</h4><p>A living early one-page, proposed feature list, and product roadmap for ConCOREdance.</p></a>
    <a class="card" href="assets/"><h4>Asset Library</h4><p>Mockups, screenshots, posters, and transmission visuals are gathered into a browsable archive shelf.</p></a>
  </div>
</section>

<section class="footer-band panel">
  <blockquote>"Every major milestone becomes a transmission." <span>- Archive Rule #1</span></blockquote>
  <div class="logo-row" style="margin:0">
    <div class="sigil" style="width:62px;height:62px"><span class="v"></span><span class="h"></span></div>
    <div class="brand"><h1 style="font-size:34px">ConCOREdance</h1><p>Harmony in Complexity</p></div>
  </div>
</section>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def write_outputs(result: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as fh:
            for key, value in result.items():
                delimiter = f"EOF_{key.upper()}"
                fh.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")


def publish(data: dict[str, str]) -> dict[str, str]:
    validate_request(data)
    tags = split_tags(data["Tags"])
    year = data["Date"].split("-", 1)[0]
    rel_dir = Path(year) / data["ID"]
    full_dir = ARCHIVE_ROOT / rel_dir
    full_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = ensure_ai_markdown(data, tags)

    rendered = render_transmission(data, tags)
    (full_dir / "index.html").write_text(rendered, encoding="utf-8")
    (full_dir / "transmission.html").write_text(rendered, encoding="utf-8")
    write_pdf(data, full_dir / "transmission.pdf")

    entry = metadata_for(data, tags, rel_dir)
    (full_dir / "metadata.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")

    manifest = update_manifest(entry)
    render_index(manifest)
    render_canon_index(manifest)

    return {
        "transmission_id": data["ID"],
        "transmission_title": data["Title"],
        "transmission_summary": data["Summary"],
        "transmission_path": f"{rel_dir.as_posix()}/",
        "pdf_path": f"{rel_dir.as_posix()}/transmission.pdf",
        "markdown_path": markdown_path.as_posix(),
        "metadata_path": str(rel_dir / "metadata.json"),
        "transmission_dir": str(rel_dir),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Publish a ConCOREdance transmission.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--issue-event", type=Path, help="Path to GitHub issue event JSON.")
    source.add_argument("--request-file", type=Path, help="Path to a structured request Markdown file.")
    parser.add_argument("--output-json", type=Path, help="Optional path for a JSON result file.")
    args = parser.parse_args(argv)

    try:
        if args.issue_event:
            body, issue_number = read_issue_body_from_event(args.issue_event)
            fallback_title = issue_title_from_event(args.issue_event)
        else:
            body = args.request_file.read_text(encoding="utf-8")
            issue_number = None
            fallback_title = None

        data = parse_request(body)
        if not data.get("Title") and fallback_title:
            data["Title"] = fallback_title
        result = publish(data)
        if issue_number is not None:
            result["issue_number"] = str(issue_number)
        write_outputs(result)
        if args.output_json:
            args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    except PublishError as exc:
        print(f"Transmission publish failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
