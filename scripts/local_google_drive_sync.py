#!/usr/bin/env python3
"""Sync allowlisted Google Drive for desktop files into the local repo."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_DEFAULT_CONFIG = "config/google_drive_sync.json"


@dataclass(frozen=True)
class FileRecord:
    source_path: Path
    target_path: Path
    source_relative: str
    target_relative: str
    size: int
    modified_time: str
    sha256: str


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(path)


def resolve_under(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes configured root: {relative}") from exc
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iso_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def is_excluded(relative: str, name: str, config: dict[str, Any]) -> bool:
    if name in set(config.get("exclude_names", [])):
        return True
    return any(relative == prefix or relative.startswith(prefix) for prefix in config.get("exclude_prefixes", []))


def iter_mapping_files(source_root: Path, repo_root: Path, mapping: dict[str, str], config: dict[str, Any]) -> list[FileRecord]:
    source_base = resolve_under(source_root, mapping["source"])
    target_base = resolve_under(repo_root, mapping["target"])
    records: list[FileRecord] = []

    if source_base.is_file():
        source_files = [source_base]
        mapping_source_root = source_base.parent
        mapping_target_root = target_base.parent
    else:
        source_files = sorted(path for path in source_base.rglob("*") if path.is_file())
        mapping_source_root = source_base
        mapping_target_root = target_base

    for source_path in source_files:
        relative_to_mapping = source_path.relative_to(mapping_source_root).as_posix()
        source_relative = source_path.relative_to(source_root).as_posix()
        if is_excluded(source_relative, source_path.name, config):
            continue
        target_path = (mapping_target_root / relative_to_mapping).resolve()
        try:
            target_path.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValueError(f"target escapes repository root: {target_path}") from exc
        stat = source_path.stat()
        records.append(
            FileRecord(
                source_path=source_path,
                target_path=target_path,
                source_relative=source_relative,
                target_relative=target_path.relative_to(repo_root).as_posix(),
                size=stat.st_size,
                modified_time=iso_mtime(source_path),
                sha256=sha256_file(source_path),
            )
        )
    return records


def collect_records(config: dict[str, Any]) -> list[FileRecord]:
    source_root = Path(config["source_root"]).expanduser().resolve()
    repo_root = Path(config["repo_root"]).expanduser().resolve()
    if not source_root.exists():
        raise FileNotFoundError(f"Drive source root not found: {source_root}")
    if not repo_root.exists():
        raise FileNotFoundError(f"Repository root not found: {repo_root}")

    records: list[FileRecord] = []
    for mapping in config["mappings"]:
        records.extend(iter_mapping_files(source_root, repo_root, mapping, config))
    return sorted(records, key=lambda record: record.target_relative)


def load_previous_hashes(manifest_path: Path) -> dict[str, str]:
    if not manifest_path.exists():
        return {}
    manifest = load_json(manifest_path)
    return {
        item["target_path"]: item["sha256"]
        for item in manifest.get("files", [])
        if "target_path" in item and "sha256" in item
    }


def classify(records: list[FileRecord], previous_hashes: dict[str, str]) -> dict[str, list[FileRecord]]:
    created: list[FileRecord] = []
    updated: list[FileRecord] = []
    unchanged: list[FileRecord] = []
    protected: list[FileRecord] = []
    for record in records:
        if not record.target_path.exists():
            created.append(record)
            continue

        target_hash = sha256_file(record.target_path)
        if target_hash == record.sha256:
            unchanged.append(record)
            continue

        previous_hash = previous_hashes.get(record.target_relative)
        if previous_hash and previous_hash != record.sha256:
            updated.append(record)
        else:
            protected.append(record)
    return {"created": created, "updated": updated, "unchanged": unchanged, "protected": protected}


def copy_records(records: list[FileRecord]) -> None:
    for record in records:
        record.target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(record.source_path, record.target_path)


def git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)


def maybe_commit(repo_root: Path, config: dict[str, Any], changed_paths: list[str]) -> str | None:
    if not changed_paths:
        return None
    status = git(["status", "--short", "--", *changed_paths], repo_root)
    if status.returncode != 0:
        raise RuntimeError(status.stderr.strip())
    if not status.stdout.strip():
        return None
    add = git(["add", "--", *changed_paths], repo_root)
    if add.returncode != 0:
        raise RuntimeError(add.stderr.strip())
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit = git(["commit", "-m", f"{config['commit_message_prefix']}: {now}"], repo_root)
    if commit.returncode != 0:
        raise RuntimeError(commit.stderr.strip() or commit.stdout.strip())
    return git(["rev-parse", "HEAD"], repo_root).stdout.strip()


def record_to_manifest(record: FileRecord) -> dict[str, Any]:
    return {
        "source_path": record.source_relative,
        "target_path": record.target_relative,
        "size": record.size,
        "modified_time": record.modified_time,
        "sha256": record.sha256,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=REPO_DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    invocation_root = Path.cwd().resolve()
    config_path = resolve_under(invocation_root, args.config)
    config = load_json(config_path)
    repo_root = Path(config["repo_root"]).expanduser().resolve()

    manifest_path = resolve_under(repo_root, config["manifest_path"])
    records = collect_records(config)
    previous_hashes = load_previous_hashes(manifest_path)
    buckets = classify(records, previous_hashes)
    changed = buckets["created"] + buckets["updated"]
    manifest = {
        "source_root": config["source_root"],
        "repo_root": config["repo_root"],
        "delete_missing": bool(config.get("delete_missing", False)),
        "file_count": len(records),
        "files": [record_to_manifest(record) for record in records],
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "source_root": config["source_root"],
        "repo_root": config["repo_root"],
        "created": [record.target_relative for record in buckets["created"]],
        "updated": [record.target_relative for record in buckets["updated"]],
        "protected": [record.target_relative for record in buckets["protected"]],
        "unchanged_count": len(buckets["unchanged"]),
        "manifest_path": str(manifest_path),
        "commit_sha": None,
    }

    if not args.dry_run:
        copy_records(changed)
        write_json(manifest_path, manifest)

    changed_paths = [record.target_relative for record in changed]
    changed_paths.append(config["manifest_path"])
    if args.commit and not args.dry_run:
        report["commit_sha"] = maybe_commit(repo_root, config, changed_paths)

    report_dir = Path(config["report_dir"]).expanduser()
    report_name = f"google_drive_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    if not args.dry_run:
        write_json(report_dir / report_name, report)

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"local_google_drive_sync: {exc}", file=sys.stderr)
        raise SystemExit(1)
