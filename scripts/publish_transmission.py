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
from datetime import datetime
from pathlib import Path
from typing import Any


ARCHIVE_ROOT = Path("01_Transmission_Archive")
MANIFEST_PATH = ARCHIVE_ROOT / "archive_manifest.json"
INDEX_PATH = ARCHIVE_ROOT / "index.html"
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
        raise PublishError(f"Missing required field(s): {', '.join(missing)}")
    return parsed


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
    return {
        "id": data["ID"],
        "title": data["Title"],
        "date": data["Date"],
        "status": data["Status"],
        "type": data["Type"],
        "layer": data["Layer"],
        "from": data["From"],
        "to": data["To"],
        "summary": data["Summary"],
        "tags": tags,
        "path": str(rel_dir / "transmission.html"),
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
        summary=html.escape(data["Summary"]),
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
            "canonical_structure": "ConCOREdance/01_Transmission_Archive/index.html + archive_manifest.json + yearly transmission folders",
            "entries": [],
        }
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def update_manifest(entry: dict[str, Any]) -> dict[str, Any]:
    manifest = load_manifest()
    entries = [item for item in manifest.get("entries", []) if item.get("id") != entry["id"]]
    entries.append(entry)
    entries.sort(key=lambda item: (item.get("date", ""), item.get("id", "")))
    manifest["entries"] = entries
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def render_index(manifest: dict[str, Any]) -> None:
    card_template = INDEX_CARD_TEMPLATE.read_text(encoding="utf-8")
    cards = []
    for entry in manifest.get("entries", []):
        cards.append(
            card_template.format(
                path=html.escape(entry["path"], quote=True),
                id=html.escape(entry["id"]),
                type=html.escape(entry["type"]),
                title=html.escape(entry["title"]),
                summary=html.escape(entry["summary"]),
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
    <div class="meta-grid"><span>Manifest v1.0</span><span>|</span><span>{count} {plural}</span><span>|</span><span>Active Canon</span><span>|</span><a href="team/">Project Team</a><span>|</span><a href="assets/">Asset Library</a><span>|</span><a href="doctrine/">Doctrine</a></div>
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

    (full_dir / "transmission.html").write_text(render_transmission(data, tags), encoding="utf-8")

    entry = metadata_for(data, tags, rel_dir)
    (full_dir / "metadata.json").write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")

    manifest = update_manifest(entry)
    render_index(manifest)

    return {
        "transmission_id": data["ID"],
        "transmission_title": data["Title"],
        "transmission_summary": data["Summary"],
        "transmission_path": str(rel_dir / "transmission.html"),
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
