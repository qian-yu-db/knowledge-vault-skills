#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Headless smoke runner for the eval cases in evals/.

Use it where `claude plugin eval` can't authenticate, e.g. when Claude Code uses a
managed apiKeyHelper that needs your real HOME. It runs ordinary `claude -p` sessions
(normal auth), loads this plugin via --plugin-dir, and isolates each run from your
personal setup:
  --setting-sources project   no user settings, plugins, hooks or personal skills
  --strict-mcp-config         no MCP servers
  a fresh temp workspace      seeded by the case's scaffold script

It reuses the same case files (prompt.md, case.yaml, graders/*.md). Supported
graders: tool_used, regex (last_message | trace | files), file_exists, and llm
(one `claude -p` judge vote). --baseline also runs each case without the plugin and
reports the delta. Graders on the Skill tool, or marked `arm: with-only`, count only
in the plugin arm.

  uv run --script evals/run_smoke.py                       # all cases, plugin arm only
  uv run --script evals/run_smoke.py --case 'query-*' --baseline --keep
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EVALS = Path(__file__).resolve().parent
PLUGIN = EVALS.parent
RESULTS = EVALS / "results"
ISOLATION = ["--setting-sources", "project", "--strict-mcp-config", "--no-session-persistence"]


# --------------------------------------------------------------------------- case files

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Small YAML subset: scalars, inline lists, quoted strings."""
    if not text.startswith("---"):
        return {}, text.strip()
    _, fm_text, body = text.split("---", 2)
    fm: dict = {}
    for line in fm_text.strip().splitlines():
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            items = re.findall(r'"([^"]*)"|\'([^\']*)\'|([^,\s][^,]*)', val[1:-1])
            fm[key] = [next(x for x in grp if x).strip() for grp in items]
        elif len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            fm[key] = val[1:-1]
        elif re.fullmatch(r"-?\d+", val):
            fm[key] = int(val)
        elif val in ("true", "false"):
            fm[key] = val == "true"
        else:
            fm[key] = val
    return fm, body.strip()


def load_case(case_dir: Path) -> dict:
    fm, prompt = parse_frontmatter((case_dir / "prompt.md").read_text())
    scaffold = None
    case_yaml = case_dir / "case.yaml"
    if case_yaml.is_file():
        m = re.search(r"scaffold_script:\s*(\S+)", case_yaml.read_text())
        scaffold = case_dir / m.group(1) if m else None
    graders = []
    for g in sorted((case_dir / "graders").glob("*.md")):
        gfm, body = parse_frontmatter(g.read_text())
        gfm.setdefault("criteria", body)
        gfm["name"] = g.stem
        graders.append(gfm)
    return {"name": case_dir.name, "dir": case_dir, "prompt": prompt, "fm": fm,
            "scaffold": scaffold, "graders": graders}


def discover(patterns: list[str]) -> list[dict]:
    dirs = sorted(d for d in EVALS.iterdir() if (d / "prompt.md").is_file())
    if patterns:
        dirs = [d for d in dirs if any(fnmatch.fnmatch(d.name, p) for p in patterns)]
    return [load_case(d) for d in dirs]


# --------------------------------------------------------------------------- running

def snapshot(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def run_case(case: dict, with_plugin: bool, keep: bool) -> dict:
    work = Path(tempfile.mkdtemp(prefix=f"kv-smoke-{case['name']}-"))
    try:
        if case["scaffold"]:
            subprocess.run(["bash", str(case["scaffold"])], cwd=work, check=True, timeout=120)
        before = snapshot(work)
        fm = case["fm"]
        cmd = ["claude", "-p", case["prompt"], "--output-format", "stream-json", "--verbose",
               "--max-turns", str(fm.get("max_turns", 10)), *ISOLATION]
        if fm.get("allowed_tools"):
            cmd += ["--allowedTools", *fm["allowed_tools"]]
        if fm.get("model"):
            cmd += ["--model", fm["model"]]
        if with_plugin:
            cmd += ["--plugin-dir", str(PLUGIN)]
        started = time.time()
        try:
            proc = subprocess.run(cmd, cwd=work, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                  timeout=fm.get("timeout_seconds", 300))
            stdout, error = proc.stdout, (proc.stderr.strip()[-500:] if proc.returncode else None)
        except subprocess.TimeoutExpired as exc:
            stdout, error = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""), "timeout"
        events = [json.loads(l) for l in stdout.splitlines() if l.startswith("{")]
        result = next((e for e in reversed(events) if e.get("type") == "result"), {})
        tool_uses = [c for e in events if e.get("type") == "assistant"
                     for c in e.get("message", {}).get("content", []) if c.get("type") == "tool_use"]
        created = sorted(snapshot(work) - before)
        trace_path = work / "trace.jsonl"
        trace_path.write_text(stdout)
        return {
            "workspace": str(work), "error": error or (result.get("subtype") if result.get("is_error") else None),
            "last_message": result.get("result") or "", "trace": stdout, "tool_uses": tool_uses,
            "created": created, "cost": result.get("total_cost_usd") or 0.0,
            "turns": result.get("num_turns"), "seconds": round(time.time() - started, 1),
        }
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)


# --------------------------------------------------------------------------- grading

def judge(criteria: str, response: str) -> tuple[bool, str, float]:
    prompt = ("You are grading an AI assistant's response against a rubric.\n\n"
              f"RUBRIC:\n{criteria}\n\nRESPONSE:\n<<<\n{response}\n>>>\n\n"
              "Reply with PASS or FAIL on the first line, then one sentence of reasoning.")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            proc = subprocess.run(["claude", "-p", prompt, "--output-format", "json", "--max-turns", "1",
                                   *ISOLATION], cwd=tmp, capture_output=True, text=True,
                                  stdin=subprocess.DEVNULL, timeout=240)
        except subprocess.TimeoutExpired:
            return False, "judge timed out", 0.0
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, f"judge error: {proc.stderr.strip()[-200:]}", 0.0
    text = (out.get("result") or "").strip()
    return text.upper().startswith("PASS"), text.splitlines()[-1][:300] if text else "", out.get("total_cost_usd") or 0.0


def grade(g: dict, run: dict) -> tuple[bool, str, float]:
    kind = g.get("type")
    if kind == "tool_used":
        pat = re.compile(g["input_match"]) if g.get("input_match") else None
        n = sum(1 for t in run["tool_uses"] if t.get("name") == g["tool"]
                and (pat is None or pat.search(json.dumps(t.get("input", {})))))
        lo, hi = int(g.get("min", 1)), g.get("max")
        ok = n >= lo and (hi is None or n <= int(hi))
        return ok, f"{g['tool']} calls matching: {n} (min {lo}, max {hi if hi is not None else '∞'})", 0.0
    if kind == "regex":
        target = g.get("target", "last_message")
        text = {"last_message": run["last_message"], "trace": run["trace"], "files": "\n".join(run["created"])}[target]
        flags = re.I if "i" in str(g.get("flags", "")) else 0
        hits = len(re.findall(g["pattern"], text, flags))
        match = str(g.get("match", "contains"))
        ok = hits == 0 if match == "not_contains" else hits == int(match.split(":")[1]) if match.startswith("count:") else hits > 0
        return ok, f"{hits} match(es) in {target}", 0.0
    if kind == "file_exists":
        found = [p for p in run["created"] if fnmatch.fnmatch(p, g["path"])]
        want = g.get("exists", True) not in (False, "false")
        return bool(found) == want, f"created matching {g['path']}: {found[:5]}", 0.0
    if kind == "llm":
        return judge(g["criteria"], run["last_message"])
    return False, f"unsupported grader type {kind!r}", 0.0


def plugin_only(g: dict) -> bool:
    return g.get("arm") == "with-only" or (g.get("type") == "tool_used" and g.get("tool") == "Skill")


def score_arm(case: dict, run: dict, with_plugin: bool) -> dict:
    graded, total, passed, cost = [], 0.0, 0.0, 0.0
    for g in case["graders"]:
        if plugin_only(g) and not with_plugin:
            continue
        ok, why, c = grade(g, run) if not run["error"] else (False, f"run error: {run['error']}", 0.0)
        cost += c
        counts = not plugin_only(g) or with_plugin
        w = float(g.get("weight", 1))
        if counts:
            total += w
            passed += w if ok else 0
        graded.append({"name": g["name"], "type": g["type"], "passed": ok, "detail": why})
    return {"score": round(passed / total, 2) if total else 0.0, "graders": graded, "judge_cost": cost}


# --------------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", action="append", default=[], help="case name glob (repeatable)")
    ap.add_argument("--baseline", action="store_true", help="also run without the plugin and report delta")
    ap.add_argument("--keep", action="store_true", help="keep temp workspaces (path printed)")
    ap.add_argument("--threshold", type=float, default=1.0, help="exit 1 if a plugin-arm score is below this")
    args = ap.parse_args(argv)

    cases = discover(args.case)
    if not cases:
        print("No cases matched.", file=sys.stderr)
        return 2
    report, failed, total_cost = [], False, 0.0
    for case in cases:
        entry = {"case": case["name"], "arms": {}}
        for arm, with_plugin in [("with", True)] + ([("without", False)] if args.baseline else []):
            print(f"▶ {case['name']} [{arm}] …", flush=True)
            run = run_case(case, with_plugin, args.keep)
            scored = score_arm(case, run, with_plugin)
            total_cost += run["cost"] + scored["judge_cost"]
            entry["arms"][arm] = {**scored, "error": run["error"], "turns": run["turns"], "seconds": run["seconds"],
                                  "cost": round(run["cost"] + scored["judge_cost"], 4), "created": run["created"],
                                  "skills": [t["input"].get("skill") for t in run["tool_uses"] if t.get("name") == "Skill"],
                                  "workspace": run["workspace"] if args.keep else None,
                                  "last_message": run["last_message"][:2000]}
            a = entry["arms"][arm]
            print(f"  score {a['score']:.2f}  turns {a['turns']}  {a['seconds']}s  ${a['cost']:.3f}"
                  + (f"  ERROR {a['error']}" if a["error"] else ""))
            for g in a["graders"]:
                print(f"    {'✔' if g['passed'] else '✘'} {g['name']}: {g['detail']}")
            if args.keep:
                print(f"    workspace: {run['workspace']}")
        if args.baseline:
            entry["delta"] = round(entry["arms"]["with"]["score"] - entry["arms"]["without"]["score"], 2)
            print(f"  Δ vs no plugin: {entry['delta']:+.2f}")
        failed |= entry["arms"]["with"]["score"] < args.threshold
        report.append(entry)

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"smoke-{time.strftime('%Y%m%dT%H%M%S')}.json"
    out.write_text(json.dumps({"cases": report, "cost_usd": round(total_cost, 4)}, indent=2))
    print(f"\nTotal cost ≈ ${total_cost:.3f}  ·  results: {out.relative_to(PLUGIN)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
