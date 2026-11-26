#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic linter for a knowledge-vault Obsidian vault.

Counts, links, frontmatter and freshness are computed here so the LLM only has
to make judgment calls. Stdlib only, so it is fast enough to run from hooks.

Modes:
  (default)      full vault report (JSON, or --format text)
  --file PATH    check one note (frontmatter, required fields, broken links);
                 exit 1 when it has errors
  --summary      short plain-text status for session start; prints nothing
                 when the target is not a vault
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

NOTES_DIR = "20-notes"
INBOX_DIR = "00-inbox"
LOGS_DIR = "50-logs"
# Never linted. Still indexed as link targets.
SKIP_DIRS = {".git", ".obsidian", ".trash", ".claude", "30-templates", "40-archive",
             "assets", "raw", "node_modules", INBOX_DIR}

REQUIRED_FIELDS = {
    "paper": ["status", "year", "authors"],
    "model-card": ["model_name", "task", "framework", "status"],
    "experiment": ["project", "status", "date"],
    "code-pattern": ["language", "domain"],
    "concept": ["domain", "confidence"],
    "reading": ["domain", "source"],
    "guide": ["domain"],
    "synthesis": ["question", "sources"],
    "databricks-feature": ["product_area", "last_verified"],
    "customer": ["customer_name", "status"],
    "moc": ["domain", "updated"],
}
# Types compiled from external material; these should record provenance.
COMPILED_TYPES = {"paper", "concept", "reading", "guide", "code-pattern",
                  "databricks-feature", "synthesis"}
STALE_DAYS = {"databricks-feature": 90, "code-pattern": 90}
DEFAULT_STALE_DAYS = 180
TYPE_PREFIXES = ("paper-", "concept-", "guide-", "pattern-", "code-pattern-", "model-card-",
                 "experiment-", "reading-", "databricks-feature-", "synthesis-", "project-")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

LINK_RE = re.compile(r"!?\[\[([^\]\|#\^]*)(?:[#\^][^\]\|]*)?(?:\|[^\]]*)?\]\]")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
TEMPLATE_VAR_RE = re.compile(r"\{\{[^}]*\}\}")
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


# --------------------------------------------------------------------------- parsing

def split_frontmatter(text: str) -> tuple[dict | None, str]:
    """Return (frontmatter dict or None, body). Minimal YAML: scalars and lists."""
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None, text
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            break
    else:
        return None, text
    fm: dict = {}
    key = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s*(.*)$", raw) or re.match(r"^-\s+(.*)$", raw)
        if item and key is not None:
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z0-9_\-]+):\s*(.*)$", raw)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            if val.startswith("[") and val.endswith("]"):
                fm[key] = [_scalar(v) for v in val[1:-1].split(",") if v.strip()]
            else:
                fm[key] = _scalar(val)
    return fm, "\n".join(lines[end + 1:])


def _scalar(val: str):
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        return val[1:-1]
    return val


def is_empty(val) -> bool:
    if val is None:
        return True
    if isinstance(val, list):
        return not any(str(v).strip() for v in val)
    return not str(val).strip()


def strip_code(body: str) -> str:
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", body))


def extract_links(body: str) -> list[str]:
    clean = TEMPLATE_VAR_RE.sub("", strip_code(body))
    return [m.group(1).strip() for m in LINK_RE.finditer(clean) if m.group(1).strip()]


def word_count(body: str) -> int:
    return len(re.findall(r"\w+", strip_code(body)))


def parse_date(val) -> date | None:
    m = DATE_RE.search(str(val or ""))
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


# --------------------------------------------------------------------------- vault model

def find_vault(explicit: str | None) -> Path:
    candidate = explicit or os.environ.get("CLAUDE_PLUGIN_OPTION_VAULT_PATH") or os.getcwd()
    return Path(os.path.expanduser(candidate)).resolve()


def looks_like_vault(root: Path) -> bool:
    return (root / NOTES_DIR).is_dir() and ((root / INBOX_DIR).is_dir() or (root / "CLAUDE.md").is_file())


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if not name.startswith("."):
                yield Path(dirpath) / name


def build_targets(root: Path) -> tuple[set[str], set[str]]:
    """Link-resolvable names (Obsidian resolves by basename, case-insensitively)."""
    names, paths = set(), set()
    for f in iter_files(root):
        rel = f.relative_to(root).as_posix()
        if f.suffix == ".md":
            names.add(f.stem.lower())
            paths.add(rel[:-3].lower())
        else:
            names.add(f.name.lower())
            paths.add(rel.lower())
    return names, paths


def resolves(target: str, names: set[str], paths: set[str]) -> bool:
    t = target.strip().lstrip("/").lower()
    if t.endswith(".md"):
        t = t[:-3]
    return t in names or t in paths or t.rsplit("/", 1)[-1] in names


def lintable(rel: Path) -> bool:
    return rel.suffix == ".md" and not any(part in SKIP_DIRS for part in rel.parts[:-1])


# --------------------------------------------------------------------------- checks

def check_note(path: Path, root: Path, names: set[str], paths: set[str]) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    rel = path.relative_to(root).as_posix()
    links = extract_links(body)
    errors, warnings = [], []
    note_type = (fm or {}).get("type")
    note_type = note_type if isinstance(note_type, str) else None

    in_knowledge = rel.startswith(f"{NOTES_DIR}/") or rel.startswith("10-mocs/") or rel.startswith("02-customers/")
    if fm is None and in_knowledge:
        errors.append("missing frontmatter")
    if fm is not None and in_knowledge and not note_type:
        errors.append("frontmatter has no `type`")
    for field in REQUIRED_FIELDS.get(note_type or "", []):
        if is_empty((fm or {}).get(field)):
            errors.append(f"missing required field `{field}` for type `{note_type}`")
    broken = sorted({l for l in links if not resolves(l, names, paths)})
    if broken:
        errors.append("broken links: " + ", ".join(f"[[{b}]]" for b in broken))
    if note_type in COMPILED_TYPES and rel.startswith(f"{NOTES_DIR}/") and is_empty((fm or {}).get("sources")):
        warnings.append("no `sources` recorded (provenance)")

    return {
        "path": rel,
        "type": note_type,
        "words": word_count(body),
        "links_out": sorted(set(links)),
        "broken_links": broken,
        "last_verified": str(parse_date((fm or {}).get("last_verified")) or ""),
        "errors": errors,
        "warnings": warnings,
        "mtime": path.stat().st_mtime,
    }


def lint_vault(root: Path, thin_words: int, min_links: int, today: date) -> dict:
    names, paths = build_targets(root)
    notes = [check_note(root / rel, root, names, paths)
             for rel in sorted(f.relative_to(root) for f in iter_files(root)) if lintable(rel)]

    inbound: dict[str, set[str]] = {}
    for n in notes:
        for l in n["links_out"]:
            key = l.lower().removesuffix(".md").rsplit("/", 1)[-1]
            inbound.setdefault(key, set()).add(n["path"])

    index_links: set[str] | None = None
    index_file = root / "index.md"
    if index_file.is_file():
        _, ib = split_frontmatter(index_file.read_text(encoding="utf-8", errors="replace"))
        index_links = {l.lower().removesuffix(".md").rsplit("/", 1)[-1] for l in extract_links(ib)}

    report = {k: [] for k in ("errors", "orphans", "thin", "poorly_linked", "stale",
                               "naming", "missing_sources", "not_in_index")}
    by_type: dict[str, int] = {}
    for n in notes:
        p = n["path"]
        stem = Path(p).stem
        if n["errors"]:
            report["errors"].append({"path": p, "issues": n["errors"]})
        if p.startswith("10-mocs/") and not stem.startswith("MOC-"):
            report["naming"].append({"path": p, "issue": "MOC filename should start with `MOC-`"})
        if not p.startswith(f"{NOTES_DIR}/"):
            continue
        by_type[n["type"] or "untyped"] = by_type.get(n["type"] or "untyped", 0) + 1
        if not KEBAB.match(stem):
            report["naming"].append({"path": p, "issue": "not lowercase-kebab-case"})
        elif not stem.startswith(TYPE_PREFIXES):
            report["naming"].append({"path": p, "issue": "no type prefix (e.g. concept-, guide-)"})
        refs = inbound.get(stem.lower(), set()) - {p}
        if not refs:
            report["orphans"].append(p)
        if n["words"] < thin_words:
            report["thin"].append({"path": p, "words": n["words"]})
        if len(n["links_out"]) < min_links:
            report["poorly_linked"].append({"path": p, "links_out": len(n["links_out"])})
        limit = STALE_DAYS.get(n["type"] or "", DEFAULT_STALE_DAYS)
        verified = parse_date(n["last_verified"])
        age = (today - verified).days if verified else int((time.time() - n["mtime"]) // 86400)
        if age > limit:
            report["stale"].append({"path": p, "type": n["type"], "days": age,
                                    "basis": "last_verified" if verified else "file mtime"})
        if "no `sources` recorded (provenance)" in n["warnings"]:
            report["missing_sources"].append(p)
        if index_links is not None and stem.lower() not in index_links:
            report["not_in_index"].append(p)

    knowledge = [n for n in notes if n["path"].startswith(f"{NOTES_DIR}/")]
    most_linked = sorted(((len(inbound.get(Path(n["path"]).stem.lower(), set()) - {n["path"]}), n["path"])
                          for n in knowledge), reverse=True)[:10]
    inbox = root / INBOX_DIR
    report["stats"] = {
        "vault": str(root),
        "date": today.isoformat(),
        "notes_total": len(notes),
        "knowledge_notes": len(knowledge),
        "by_type": dict(sorted(by_type.items())),
        "inbox_items": sum(1 for f in inbox.iterdir() if f.is_file() and not f.name.startswith(".")) if inbox.is_dir() else 0,
        "broken_link_count": sum(len(n["broken_links"]) for n in notes),
        "orphan_rate": round(len(report["orphans"]) / len(knowledge), 3) if knowledge else 0.0,
        "has_index": index_links is not None,
        "has_log": (root / "log.md").is_file(),
        "most_linked": [{"path": p, "inbound": c} for c, p in most_linked if c],
    }
    return report


def last_next_action(root: Path) -> str | None:
    logs = sorted((root / LOGS_DIR).glob("*/*-W*.md")) if (root / LOGS_DIR).is_dir() else []
    for log in reversed(logs):
        hits = re.findall(r"^\s*-\s*Next:\s*(.+)$", log.read_text(encoding="utf-8", errors="replace"), re.M)
        if hits:
            text = hits[-1].strip()
            text = text if len(text) <= 300 else text[:297].rstrip() + "..."
            return f"{text} (from {log.relative_to(root).as_posix()})"
    return None


# --------------------------------------------------------------------------- output

def render_text(r: dict) -> str:
    s = r["stats"]
    out = [f"Vault: {s['vault']}  ({s['date']})",
           f"Notes: {s['notes_total']} total, {s['knowledge_notes']} in {NOTES_DIR}/  |  inbox: {s['inbox_items']}",
           f"By type: {', '.join(f'{k}={v}' for k, v in s['by_type'].items()) or 'none'}",
           f"Broken links: {s['broken_link_count']}  |  orphan rate: {s['orphan_rate']:.0%}",
           ""]
    sections = [("Errors", r["errors"], lambda e: f"{e['path']}: {'; '.join(e['issues'])}"),
                ("Orphans", r["orphans"], str),
                ("Thin notes", r["thin"], lambda e: f"{e['path']} ({e['words']} words)"),
                ("Poorly linked", r["poorly_linked"], lambda e: f"{e['path']} ({e['links_out']} links)"),
                ("Stale", r["stale"], lambda e: f"{e['path']} ({e['days']}d via {e['basis']})"),
                ("Naming", r["naming"], lambda e: f"{e['path']}: {e['issue']}"),
                ("Missing sources", r["missing_sources"], str),
                ("Not in index.md", r["not_in_index"], str)]
    for title, items, fmt in sections:
        out.append(f"## {title} ({len(items)})")
        out.extend(f"- {fmt(i)}" for i in items[:50])
        if len(items) > 50:
            out.append(f"- ... {len(items) - 50} more")
        out.append("")
    return "\n".join(out)


def render_summary(root: Path, r: dict) -> str:
    s = r["stats"]
    parts = [f"Knowledge vault at {root}: {s['knowledge_notes']} notes, {s['inbox_items']} inbox item(s) waiting"]
    if r["errors"]:
        parts.append(f"{len(r['errors'])} note(s) with errors ({s['broken_link_count']} broken links)")
    if r["stale"]:
        parts.append(f"{len(r['stale'])} stale note(s)")
    line = "; ".join(parts) + "."
    nxt = last_next_action(root)
    if nxt:
        line += f" Last session's next step: {nxt}."
    if not s["has_index"] or not s["has_log"]:
        line += " index.md/log.md missing: suggest /knowledge-vault:setup-vault to upgrade."
    return line


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", help="vault root (default: $CLAUDE_PLUGIN_OPTION_VAULT_PATH, then cwd)")
    ap.add_argument("--file", help="lint a single note and exit 1 on errors")
    ap.add_argument("--summary", action="store_true", help="one-line status for session start")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    ap.add_argument("--thin-words", type=int, default=300)
    ap.add_argument("--min-links", type=int, default=3)
    args = ap.parse_args(argv)

    root = find_vault(args.vault)
    if not looks_like_vault(root):
        if args.summary:
            return 0
        print(f"Not a knowledge vault (no {NOTES_DIR}/ with {INBOX_DIR}/ or CLAUDE.md): {root}", file=sys.stderr)
        return 2

    if args.file:
        path = Path(os.path.expanduser(args.file)).resolve()
        try:
            rel = path.relative_to(root)
        except ValueError:
            return 0
        if not path.is_file() or not lintable(rel):
            return 0
        names, paths = build_targets(root)
        n = check_note(path, root, names, paths)
        if args.format == "json":
            print(json.dumps({k: n[k] for k in ("path", "errors", "warnings")}, indent=2))
        else:
            for e in n["errors"]:
                print(f"{n['path']}: ERROR {e}")
            for w in n["warnings"]:
                print(f"{n['path']}: warning {w}")
        return 1 if n["errors"] else 0

    report = lint_vault(root, args.thin_words, args.min_links, date.today())
    if args.summary:
        print(render_summary(root, report))
    elif args.format == "text":
        print(render_text(report))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
