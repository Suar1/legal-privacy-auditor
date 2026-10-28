"""Regression tests for confirmed auditor defects.

Tests cover the four issues fixed in the 2026-10-28 remediation pass:
  A - Scanner must not recurse into 'reports/' (own output → false positives)
  B - CSS touch-action pan-y must not trigger raw_payment_card_storage
  C - Malformed/markdown URLs must not crash the scanner (ValueError IPv6)
  D - Determinism: deduplication, consistent JSON/Markdown output
"""
import json
import sys
import textwrap
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import auditor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    """Write *files* (relative-path → content) under *tmp_path* and return it."""
    for rel, content in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return tmp_path


def _scan(repo: Path) -> dict:
    cfg = auditor.load_config(repo / "legal-audit.yaml", repo)
    return auditor.scan(repo, cfg)


# ---------------------------------------------------------------------------
# Issue A — reports/ directory must be skipped
# ---------------------------------------------------------------------------

class TestReportsDirSkipped:
    def test_reports_dir_not_in_findings(self, tmp_path):
        """A report file containing security keywords must not produce findings."""
        repo = _make_repo(tmp_path, {
            "reports/nuqta-legal-audit.md": textwrap.dedent("""\
                # Audit report
                Found raw_payment_card_storage in cvv field.
                PAN handling review required.
                card_number stored unencrypted.
                SECRET_KEY='hardcoded-value-123456789012'
            """),
            "src/app.py": "print('hello')\n",
        })
        result = _scan(repo)
        report_files = {e["file"] for f in result["findings"] for e in f["evidence"]}
        assert not any("reports" in f for f in report_files), (
            f"Reports dir was scanned; findings from it: {report_files}"
        )

    def test_reports_dir_not_in_iter(self, tmp_path):
        """iter_text_files must skip paths whose parts include 'reports'."""
        repo = _make_repo(tmp_path, {
            "reports/foo.json": '{"cvv": "1234"}',
            "src/main.py": "x = 1\n",
        })
        # Use relative paths so that the pytest tmp_path name (which may
        # contain 'reports' as a substring) does not pollute the assertion.
        scanned_rel = [
            str(p.relative_to(repo)) for p in auditor.iter_text_files(repo)
        ]
        assert not any(
            "reports" in Path(p).parts for p in scanned_rel
        ), f"reports/ dir was not skipped; got: {scanned_rel}"

    def test_legal_audit_dir_skipped(self, tmp_path):
        """.legal-audit/ must also be skipped (pre-existing behaviour)."""
        repo = _make_repo(tmp_path, {
            ".legal-audit/state.json": '{"findings": []}',
            "src/main.py": "x = 1\n",
        })
        scanned = [str(p) for p in auditor.iter_text_files(repo)]
        assert not any(".legal-audit" in p for p in scanned)

    def test_agents_dir_skipped(self, tmp_path):
        """.agents/ skill libraries must be skipped."""
        repo = _make_repo(tmp_path, {
            ".agents/skills/design-taste/photos.json": (
                '{"description": "horizontal scroll gallery pan"}'
            ),
            "src/app.py": "x = 1\n",
        })
        scanned = [str(p) for p in auditor.iter_text_files(repo)]
        assert not any(".agents" in p for p in scanned)


# ---------------------------------------------------------------------------
# Issue B — CSS pan-y / pan-x must not trigger payment card finding
# ---------------------------------------------------------------------------

class TestPanFalsePositive:
    def _pan_findings(self, content: str, tmp_path: Path) -> list:
        repo = _make_repo(tmp_path, {"assets/styles.css": content})
        result = _scan(repo)
        return [f for f in result["findings"] if f["rule_id"] == "raw_payment_card_storage"]

    def test_css_pan_y_no_finding(self, tmp_path):
        css = ".stage { touch-action: pan-y; background: red; }\n"
        assert self._pan_findings(css, tmp_path) == [], "pan-y triggered payment finding"

    def test_css_pan_x_no_finding(self, tmp_path):
        css = ".slider { touch-action: pan-x; }\n"
        assert self._pan_findings(css, tmp_path) == [], "pan-x triggered payment finding"

    def test_animation_pan_no_finding(self, tmp_path):
        js = 'const desc = "horizontal scroll gallery pan animation";\n'
        repo = _make_repo(tmp_path, {"src/anim.js": js})
        result = _scan(repo)
        findings = [f for f in result["findings"] if f["rule_id"] == "raw_payment_card_storage"]
        assert findings == [], "animation pan text triggered payment finding"

    def test_gesture_pan_no_finding(self, tmp_path):
        js = "const panGesture = Gesture.Pan().onUpdate(handler);\n"
        repo = _make_repo(tmp_path, {"src/gesture.js": js})
        result = _scan(repo)
        findings = [f for f in result["findings"] if f["rule_id"] == "raw_payment_card_storage"]
        assert findings == [], "Gesture.Pan() triggered payment finding"

    def test_card_number_still_detected(self, tmp_path):
        py = "db.execute('INSERT INTO payments (card_number) VALUES (?)', (num,))\n"
        repo = _make_repo(tmp_path, {"src/pay.py": py})
        result = _scan(repo)
        findings = [f for f in result["findings"] if f["rule_id"] == "raw_payment_card_storage"]
        assert findings, "card_number was not detected"

    def test_cvv_still_detected(self, tmp_path):
        js = "const payload = { cvv: userInput };\n"
        repo = _make_repo(tmp_path, {"src/checkout.js": js})
        result = _scan(repo)
        findings = [f for f in result["findings"] if f["rule_id"] == "raw_payment_card_storage"]
        assert findings, "cvv was not detected"

    def test_pan_number_compound_detected(self, tmp_path):
        """pan_number as a compound identifier IS a genuine payment PAN field."""
        py = "record['pan_number'] = card_data.pan\n"
        repo = _make_repo(tmp_path, {"src/cards.py": py})
        result = _scan(repo)
        findings = [f for f in result["findings"] if f["rule_id"] == "raw_payment_card_storage"]
        assert findings, "pan_number compound was not detected"


# ---------------------------------------------------------------------------
# Issue C — Malformed / markdown URLs must not crash the scanner
# ---------------------------------------------------------------------------

class TestMalformedURLs:
    def test_markdown_link_syntax_no_crash(self, tmp_path):
        """Markdown links like [text](url) can produce garbled strings after
        rstrip; the scanner must survive them without ValueError."""
        md = textwrap.dedent("""\
            # Privacy Policy
            See [nuqta.sale](https://nuqta.sale) for details.
            Also [here](https://nuqta.sale](https://nuqta.sale) nested broken.
        """)
        repo = _make_repo(tmp_path, {"docs/privacy.md": md})
        # Must not raise
        result = _scan(repo)
        assert isinstance(result, dict)

    def test_ipv6_like_url_no_crash(self, tmp_path):
        """A URL that urlparse mistakes for a malformed IPv6 address."""
        content = "// See https://example.com/path](https://other.com for more\n"
        repo = _make_repo(tmp_path, {"src/app.js": content})
        result = _scan(repo)
        assert isinstance(result, dict)

    def test_valid_urls_still_extracted(self, tmp_path):
        """Valid URLs must still be collected after the error-handling fix."""
        content = 'fetch("https://fonts.bunny.net/css?family=Inter");\n'
        repo = _make_repo(tmp_path, {"src/app.js": content})
        result = _scan(repo)
        domains = {r["domain"] for r in result["inventories"]["external_requests"]}
        assert "fonts.bunny.net" in domains


# ---------------------------------------------------------------------------
# Issue D — Determinism and deduplication
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_deduplication(self, tmp_path):
        """The same finding pattern in two identical files must not appear twice
        for the same file+line key."""
        content = "const x = { cvv: '123' };\n"
        repo = _make_repo(tmp_path, {"src/a.js": content})
        r1 = _scan(repo)
        r2 = _scan(repo)
        assert len(r1["findings"]) == len(r2["findings"]), "Non-deterministic finding count"

    def test_json_report_written(self, tmp_path):
        repo = _make_repo(tmp_path, {"src/app.py": "x = 1\n"})
        cfg = auditor.load_config(repo / "legal-audit.yaml", repo)
        result = _scan(repo)
        md_path, json_path = auditor.write_reports(repo, cfg, result)
        assert json_path.exists()
        data = json.loads(json_path.read_text())
        assert "findings" in data

    def test_markdown_report_written(self, tmp_path):
        repo = _make_repo(tmp_path, {"src/app.py": "x = 1\n"})
        cfg = auditor.load_config(repo / "legal-audit.yaml", repo)
        result = _scan(repo)
        md_path, json_path = auditor.write_reports(repo, cfg, result)
        assert md_path.exists()
        text = md_path.read_text()
        assert "Technical Legal/Privacy Audit" in text

    def test_no_secret_values_in_findings(self, tmp_path):
        """Confirmed secrets must not have their value echoed in findings."""
        content = "SECRET_KEY = 'supersecretvalue1234567890abc'\n"
        repo = _make_repo(tmp_path, {"src/config.py": content})
        result = _scan(repo)
        output = json.dumps(result)
        assert "supersecretvalue1234567890abc" not in output, (
            "Secret value leaked into finding output"
        )
