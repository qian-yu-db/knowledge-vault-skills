#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Portable workspace scanner for /project-status --reindex.

Collects facts only (activity dates, git state, size, description, candidate
reusable assets). Classification is left to the skill, which reads the vault's
CLAUDE.md for category rules. Works on macOS and Linux (no GNU find needed).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".vscode", "dist", "build", ".mypy_cache"}
ASSET_HINTS = ("pattern-", "template-", "example-")


def walk(root: Path, depth: int):
    base = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root):
        level = len(Path(dirpath).parts) - base
        dirnames[:] = [d for d in dirnames if d not in SKIP and not d.startswith(".")] if level < depth - 1 else []
        for name in filenames:
            if not name.startswith("."):
                yield Path(dirpath) / name


def git(path: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def describe(path: Path) -> str:
    for name in ("README.md", "CLAUDE.md", "AGENTS.md"):
        f = path / name
        if f.is_file():
            lines = [l.strip() for l in f.read_text(encoding="utf-8", errors="replace").splitlines()[:15]]
            text = [l for l in lines if l and not l.startswith(("#", "<!--", "---", "```"))]
            if text:
                return text[0][:200]
    return ""


def is_notebook(f: Path) -> bool:
    if f.suffix == ".ipynb":
        return True
    if f.suffix == ".py":
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                return "Databricks notebook source" in fh.readline()
        except OSError:
            return False
    return False


def scan_dir(path: Path, root: Path, depth: int) -> dict:
    files = list(walk(path, depth))
    latest = max((f.stat().st_mtime for f in files if f.exists()), default=path.stat().st_mtime)
    notebooks = [f for f in files if is_notebook(f)]
    assets = [f for f in files if f.name.startswith(ASSET_HINTS) or f.suffix in (".mermaid", ".mmd")]
    is_git = (path / ".git").exists()
    entry = {
        "dir": path.relative_to(root).as_posix(),
        "last_modified": datetime.fromtimestamp(latest, tz=timezone.utc).date().isoformat(),
        "days_since_modified": int((datetime.now(timezone.utc).timestamp() - latest) // 86400),
        "file_count": len(files),
        "is_git": is_git,
        "description": describe(path),
        "notebooks": len(notebooks),
        "candidate_assets": [f.relative_to(path).as_posix() for f in (notebooks + assets)[:10]],
    }
    if is_git:
        entry["last_commit"] = git(path, "log", "-1", "--format=%cs %s")
        commits = git(path, "rev-list", "--count", "--since=7 days ago", "HEAD")
        entry["commits_7d"] = int(commits) if commits.isdigit() else 0
    return entry


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=os.environ.get("CLAUDE_PLUGIN_OPTION_WORKSPACE_ROOT") or "~/workspace")
    ap.add_argument("--depth", type=int, default=3, help="max directory depth to inspect per project")
    ap.add_argument("--expand", action="append", default=[],
                    help="container dir whose subfolders are separate projects (repeatable)")
    args = ap.parse_args(argv)

    root = Path(os.path.expanduser(args.root)).resolve()
    if not root.is_dir():
        print(f"Workspace root not found: {root}", file=sys.stderr)
        return 2
    expand = set(args.expand)
    targets = []
    for child in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if child.name in expand:
            targets.extend(sorted(p for p in child.iterdir() if p.is_dir() and not p.name.startswith(".")))
        else:
            targets.append(child)
    print(json.dumps({"root": str(root), "scanned": len(targets),
                      "dirs": [scan_dir(t, root, args.depth) for t in targets]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
