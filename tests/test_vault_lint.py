"""Tests for scripts/vault_lint.py. Run: uv run --with pytest pytest -q tests"""

import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "vault_lint.py"
spec = importlib.util.spec_from_file_location("vault_lint", SCRIPT)
vl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vl)

TODAY = date(2026, 11, 26)


def write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    for d in ("00-inbox", "10-mocs", "20-notes", "30-templates", "50-logs/2026", "raw/2026-11", "assets"):
        (tmp_path / d).mkdir(parents=True)
    write(tmp_path, "CLAUDE.md", "# vault\n")
    write(tmp_path, "00-inbox/clip.md", "raw clip [[does-not-exist]]")
    write(tmp_path, "assets/diagram.png", "png")
    write(tmp_path, "raw/2026-11/source-article.md", "original text")
    write(tmp_path, "20-notes/concept-attention.md", """---
type: concept
domain: ml
confidence: solid
sources: ["raw/2026-11/source-article.md"]
last_verified: 2026-11-01
---
# Attention
Links to [[guide-serving|serving guide]], [[concept-kv-cache#Details]], ![[diagram.png]]
and [[raw/2026-11/source-article]]. A missing one: [[concept-missing]].
Code is ignored: `[[not-a-link]]`
```python
x = "[[also-not-a-link]]"
```
""")
    write(tmp_path, "20-notes/guide-serving.md", """---
type: guide
domain: ml
last_verified: 2025-01-01
---
# Serving
See [[concept-attention]].
""")
    write(tmp_path, "20-notes/concept-kv-cache.md", """---
type: concept
domain: ml
---
# KV cache
""")
    write(tmp_path, "20-notes/Bad Name.md", "no frontmatter here")
    write(tmp_path, "10-mocs/MOC-ML.md", "---\ntype: moc\ndomain: ml\nupdated: 2026-11-01\n---\n- [[concept-attention]]\n- [[guide-serving]]\n")
    write(tmp_path, "30-templates/concept.md", "---\ntype: concept\n---\n[[]] {{title}} [[template-link]]")
    write(tmp_path, "index.md", "# Index\n- [[concept-attention]]\n")
    write(tmp_path, "50-logs/2026/2026-W47.md", "- Next: old step\n")
    write(tmp_path, "50-logs/2026/2026-W48.md", "## Monday\n  - Next: finish the lint hook\n")
    return tmp_path


def test_frontmatter_parsing():
    fm, body = vl.split_frontmatter("---\ntype: paper\nauthors:\n  - A\n  - B\ntags: [x, y]\nq: \"hi\"\n---\nbody")
    assert fm == {"type": "paper", "authors": ["A", "B"], "tags": ["x", "y"], "q": "hi"}
    assert body == "body"
    assert vl.split_frontmatter("no fm")[0] is None


def test_links_ignore_code_and_parse_aliases():
    links = vl.extract_links("[[a|alias]] [[b#h]] ![[c.png]] `[[d]]`\n```\n[[e]]\n```\n[[{{title}}]]")
    assert links == ["a", "b", "c.png"]


def test_broken_links_and_resolution(vault):
    report = vl.lint_vault(vault, 300, 3, TODAY)
    errors = {e["path"]: e["issues"] for e in report["errors"]}
    attention = errors["20-notes/concept-attention.md"]
    assert attention == ["broken links: [[concept-missing]]"]
    assert report["stats"]["broken_link_count"] == 1  # inbox + templates not linted


def test_required_fields_and_missing_frontmatter(vault):
    errors = {e["path"]: e["issues"] for e in vl.lint_vault(vault, 300, 3, TODAY)["errors"]}
    assert errors["20-notes/Bad Name.md"] == ["missing frontmatter"]
    assert "20-notes/concept-kv-cache.md" in errors
    assert any("confidence" in i for i in errors["20-notes/concept-kv-cache.md"])


def test_graph_and_freshness(vault):
    r = vl.lint_vault(vault, 300, 3, TODAY)
    assert "20-notes/concept-kv-cache.md" not in r["orphans"]  # linked from attention
    assert "20-notes/Bad Name.md" in r["orphans"]
    stale = {s["path"]: s for s in r["stale"]}
    assert stale["20-notes/guide-serving.md"]["basis"] == "last_verified"
    assert "20-notes/concept-attention.md" not in stale
    assert "20-notes/guide-serving.md" in r["missing_sources"]
    assert "20-notes/concept-attention.md" not in r["missing_sources"]
    assert "20-notes/guide-serving.md" in r["not_in_index"]
    assert {"path": "20-notes/Bad Name.md", "issue": "not lowercase-kebab-case"} in r["naming"]
    assert r["stats"]["inbox_items"] == 1


def test_single_file_mode_exit_codes(vault, capsys):
    bad = vl.main(["--vault", str(vault), "--file", str(vault / "20-notes/concept-attention.md"), "--format", "text"])
    assert bad == 1
    assert "concept-missing" in capsys.readouterr().out
    good = vl.main(["--vault", str(vault), "--file", str(vault / "20-notes/guide-serving.md")])
    assert good == 0
    # Files outside the vault or in skipped dirs are ignored.
    assert vl.main(["--vault", str(vault), "--file", str(vault / "30-templates/concept.md")]) == 0
    assert vl.main(["--vault", str(vault), "--file", "/etc/hosts"]) == 0


def test_summary_mode(vault, tmp_path_factory, capsys):
    assert vl.main(["--vault", str(vault), "--summary"]) == 0
    out = capsys.readouterr().out
    assert "1 inbox item(s)" in out
    assert "finish the lint hook" in out and "2026-W48" in out
    not_vault = tmp_path_factory.mktemp("plain")
    assert vl.main(["--vault", str(not_vault), "--summary"]) == 0
    assert capsys.readouterr().out == ""


def test_json_output_is_valid(vault, capsys):
    assert vl.main(["--vault", str(vault)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["stats"]["has_index"] is True and data["stats"]["has_log"] is False
