"""Tests for scripts/workspace_scan.py."""

import importlib.util
import json
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workspace_scan.py"
spec = importlib.util.spec_from_file_location("workspace_scan", SCRIPT)
ws = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ws)


def test_scan_expands_containers_and_reads_git(tmp_path, capsys):
    proj = tmp_path / "developments" / "tool-a"
    proj.mkdir(parents=True)
    (proj / "README.md").write_text("# Tool A\n\nA small tool.\n")
    (proj / "pattern-retry.py").write_text("x = 1\n")
    (proj / "nb.py").write_text("# Databricks notebook source\nprint(1)\n")
    (proj / "node_modules").mkdir()
    (proj / "node_modules" / "junk.js").write_text("")
    subprocess.run(["git", "init", "-q", str(proj)], check=True)
    subprocess.run(["git", "-C", str(proj), "add", "."], check=True)
    subprocess.run(["git", "-C", str(proj), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"], check=True)
    (tmp_path / "notes").mkdir()

    assert ws.main(["--root", str(tmp_path), "--expand", "developments"]) == 0
    data = json.loads(capsys.readouterr().out)
    dirs = {d["dir"]: d for d in data["dirs"]}
    assert set(dirs) == {"developments/tool-a", "notes"}
    a = dirs["developments/tool-a"]
    assert a["is_git"] and a["commits_7d"] == 1 and a["last_commit"].endswith("init")
    assert a["description"] == "A small tool."
    assert a["notebooks"] == 1
    assert "pattern-retry.py" in a["candidate_assets"]
    assert a["file_count"] == 3  # node_modules skipped


def test_missing_root(tmp_path):
    assert ws.main(["--root", str(tmp_path / "nope")]) == 2
