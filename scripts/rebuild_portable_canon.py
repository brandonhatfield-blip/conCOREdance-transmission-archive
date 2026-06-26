#!/usr/bin/env python3
"""Backfill portable ConCOREdance canon artifacts for existing transmissions."""

from __future__ import annotations

import json
import re
from pathlib import Path

from publish_transmission import ARCHIVE_ROOT, MANIFEST_PATH, render_canon_index, write_pdf


TRANSMISSION_ROOT = Path("transmissions")


def parse_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown
    _, front, body = markdown.split("---", 2)
    metadata: dict[str, str] = {}
    for line in front.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, body.strip()


def parse_sections(markdown_body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "Body"
    sections[current] = []
    for line in markdown_body.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if line.startswith("# "):
            continue
        sections.setdefault(current, []).append(line.rstrip())
    return {key: "\n".join(value).strip() for key, value in sections.items()}


def data_from_entry(entry: dict[str, object]) -> dict[str, str]:
    transmission_id = str(entry.get("id", ""))
    year = str(entry.get("date", "")).split("-", 1)[0]
    markdown_path = TRANSMISSION_ROOT / year / f"{transmission_id}.md"
    metadata: dict[str, str] = {}
    sections: dict[str, str] = {}
    if markdown_path.exists():
        metadata, body = parse_front_matter(markdown_path.read_text(encoding="utf-8"))
        sections = parse_sections(body)

    return {
        "ID": transmission_id,
        "Title": metadata.get("title") or str(entry.get("title", "")),
        "Date": metadata.get("date") or str(entry.get("date", "")),
        "Status": metadata.get("status") or str(entry.get("status", "Active Canon")),
        "Type": metadata.get("type") or str(entry.get("type", "Transmission")),
        "Layer": metadata.get("layer") or str(entry.get("layer", "")),
        "From": metadata.get("from") or str(entry.get("from", "")),
        "To": metadata.get("to") or str(entry.get("to", "")),
        "Authorized By": metadata.get("authorized_by") or str(entry.get("authorized_by", "")),
        "Summary": sections.get("Summary") or str(entry.get("summary", "")),
        "Body": sections.get("Body") or str(entry.get("summary", "")),
        "Decisions": sections.get("Decisions", ""),
        "Next Actions": sections.get("Next Actions", ""),
        "Assets": sections.get("Assets", ""),
    }


def backfill_entry(entry: dict[str, object]) -> dict[str, object]:
    transmission_id = str(entry.get("id", ""))
    year = str(entry.get("date", "")).split("-", 1)[0]
    archive_path = str(entry.get("path", "")).strip()
    archive_path = archive_path if archive_path.endswith("/") else f"{archive_path}/"
    if not archive_path.strip("/"):
        archive_path = f"{year}/{transmission_id}/"

    entry["html_path"] = str(entry.get("html_path") or f"{archive_path}index.html")
    entry["pdf_path"] = str(entry.get("pdf_path") or f"{archive_path}transmission.pdf")
    entry["markdown_path"] = str(entry.get("markdown_path") or f"transmissions/{year}/{transmission_id}.md")

    data = data_from_entry(entry)
    write_pdf(data, ARCHIVE_ROOT / str(entry["pdf_path"]))

    metadata_path = entry.get("metadata_path")
    if metadata_path:
        full_metadata_path = ARCHIVE_ROOT / str(metadata_path)
        if full_metadata_path.exists():
            metadata = json.loads(full_metadata_path.read_text(encoding="utf-8"))
            metadata.update(
                {
                    "html_path": entry["html_path"],
                    "pdf_path": entry["pdf_path"],
                    "markdown_path": entry["markdown_path"],
                }
            )
            full_metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return entry


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["entries"] = [backfill_entry(entry) for entry in manifest.get("entries", [])]
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    render_canon_index(manifest)
    print(f"Backfilled {len(manifest.get('entries', []))} canon entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
