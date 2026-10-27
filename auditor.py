#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime
import glob
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import yaml

RULE_VERSION = "2026-10-02.1"
TEXT_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html", ".htm",
    ".css", ".scss", ".py", ".rb", ".php", ".java", ".kt", ".swift",
    ".go", ".rs", ".cs", ".json", ".yaml", ".yml", ".toml", ".xml",
    ".md", ".env", ".sh", ".conf", ".ini", ".properties"
}
SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt",
    ".venv", "venv", "coverage", "Pods", ".gradle", "target", ".legal-audit"
}
TRACKERS = {
    "google-analytics.com", "googletagmanager.com", "segment.com", "segment.io",
    "mixpanel.com", "hotjar.com", "clarity.ms", "sentry.io", "amplitude.com",
    "posthog.com"
}
URL_RE = re.compile(r'https?://[^\s"\'<>)]+' , re.I)
SECRET_RULES = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("generic_api_key", re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|client[_-]?secret|access[_-]?token)\b\s*[:=]\s*[\"']([^\"']{12,})[\"']")),
    ("jwt", re.compile(r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b")),
]
SENSITIVE_WORDS = (
    "password", "passwd", "authorization", "access_token", "refresh_token",
    "ssn", "date_of_birth", "dob", "health", "diagnosis", "medication",
    "card_number", "cvv", "cvc"
)


def iter_text_files(repo: Path):
    for p in repo.rglob("*"):
        if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.name.startswith(".env") or p.suffix.lower() in TEXT_EXT or p.name in {"Dockerfile", "Makefile", "Gemfile", "Podfile"}:
            try:
                if p.stat().st_size <= 2_000_000:
                    yield p
            except OSError:
                pass


def rel(repo: Path, path: Path) -> str:
    return str(path.relative_to(repo))


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def evidence(repo: Path, path: Path, text: str, match) -> dict:
    return {"file": rel(repo, path), "line": line_number(text, match.start())}


def discover(repo: Path) -> dict:
    manifests = [
        name for name in (
            "package.json", "pyproject.toml", "requirements.txt", "Gemfile",
            "composer.json", "pom.xml", "build.gradle", "go.mod", "Cargo.toml",
            "Dockerfile", "docker-compose.yml", "compose.yaml"
        ) if (repo / name).exists()
    ]
    joined = " ".join(
        (repo / name).read_text(errors="ignore")[:250000]
        for name in manifests if (repo / name).is_file()
    )
    frameworks = []
    for token, name in (
        ("next", "Next.js"), ("react", "React"), ("vue", "Vue"),
        ("svelte", "Svelte"), ("django", "Django"), ("flask", "Flask"),
        ("fastapi", "FastAPI"), ("laravel", "Laravel"), ("rails", "Rails"),
        ("express", "Express"), ("expo", "Expo/React Native"), ("flutter", "Flutter")
    ):
        if token in joined.lower():
            frameworks.append(name)
    return {
        "repo": str(repo),
        "manifests": manifests,
        "frameworks": sorted(set(frameworks)),
        "has_git": (repo / ".git").exists(),
    }


def load_config(path: Path, repo: Path) -> dict:
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        "project": {"name": repo.name, "type": "other", "jurisdictions": []},
        "company": {},
        "age_policy": {},
        "features": {},
        "audit": {
            "mode": "audit-only",
            "allow_code_changes": False,
            "allow_dependency_changes": False,
            "allow_database_migrations": False,
            "create_git_commit": False,
        },
        "third_parties": {"approved": []},
    }


def config_findings(cfg: dict) -> list[dict]:
    findings = []
    for section in ("company", "age_policy"):
        for key, value in (cfg.get(section) or {}).items():
            if value is None:
                findings.append({
                    "rule_id": "config_missing_value",
                    "severity": "INFO",
                    "status": "MANUAL ACTION REQUIRED",
                    "title": f"Missing configuration value: {section}.{key}",
                    "message": "Value is null. The auditor will not guess this legal/company fact.",
                    "evidence": [{"file": "legal-audit.yaml", "symbol": f"{section}.{key}"}],
                    "manual_action": f"Provide an authoritative value for {section}.{key}, or document that it is intentionally not applicable.",
                })
    return findings


def scan(repo: Path, cfg: dict, include_paths: set[str] | None = None) -> dict:
    findings = config_findings(cfg)
    external_requests = []
    cookies_storage = []
    secrets = []

    for path in iter_text_files(repo):
        rpath = rel(repo, path)
        if include_paths is not None and rpath not in include_paths:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        low = text.lower()

        for match in URL_RE.finditer(text):
            raw = match.group(0).rstrip(".,;")
            host = (urlparse(raw).hostname or "").lower()
            if not host:
                continue
            tracking = any(host == d or host.endswith("." + d) for d in TRACKERS)
            external_requests.append({
                "domain": host,
                "file": rpath,
                "line": line_number(text, match.start()),
                "tracking_candidate": tracking,
            })
            if tracking:
                findings.append({
                    "rule_id": "tracking_reference",
                    "severity": "MEDIUM",
                    "status": "NEEDS LEGAL REVIEW",
                    "title": f"Tracking/telemetry reference: {host}",
                    "message": "Tracking/telemetry reference detected. Verify initialization and network activity are consent-gated where required.",
                    "evidence": [evidence(repo, path, text, match)],
                })

        for secret_type, regex in SECRET_RULES:
            for match in regex.finditer(text):
                findings.append({
                    "rule_id": "committed_secret",
                    "severity": "CRITICAL",
                    "status": "MANUAL ACTION REQUIRED",
                    "title": f"Potential exposed secret: {secret_type}",
                    "message": "Potential credential material found. The value is intentionally not included in output.",
                    "evidence": [evidence(repo, path, text, match)],
                })
                secrets.append({
                    "type_provider": secret_type,
                    "location": f"{rpath}:{line_number(text, match.start())}",
                    "exposure": "repository/client exposure possible",
                    "required_action": "Confirm validity; rotate/revoke if real; move to secret storage.",
                })

        cookie_regex = re.compile(r"(?i)(document\.cookie\s*=|setcookie\s*\(|res\.cookie\s*\(|cookies?\.(?:set|set_cookie)\s*\()")
        for match in cookie_regex.finditer(text):
            snippet = text[match.start():match.start() + 300].lower()
            flags = {
                "secure": "secure" in snippet,
                "httponly": "httponly" in snippet,
                "samesite": "samesite" in snippet,
            }
            cookies_storage.append({
                "name": "unknown",
                "set_by": f"{rpath}:{line_number(text, match.start())}",
                "purpose": "inspect in context",
                "category": "unknown",
                "before_consent": "unknown",
                "flags": flags,
            })
            if "document.cookie" not in match.group(0).lower() and (not flags["secure"] or not flags["samesite"]):
                findings.append({
                    "rule_id": "cookie_flags",
                    "severity": "HIGH",
                    "status": "NEEDS LEGAL REVIEW",
                    "title": "Server cookie may lack Secure/SameSite flags",
                    "message": f"Observed nearby cookie flags: {flags}. Inspect runtime configuration before concluding.",
                    "evidence": [evidence(repo, path, text, match)],
                })

        storage_regex = re.compile(r"(?i)\b(localStorage|sessionStorage)\.(setItem|getItem)\s*\(")
        for match in storage_regex.finditer(text):
            cookies_storage.append({
                "name": match.group(1),
                "set_by": f"{rpath}:{line_number(text, match.start())}",
                "purpose": "inspect key/value in context",
                "category": "browser storage",
                "before_consent": "unknown",
            })

        logging_regex = re.compile(r"(?i)(console\.(?:log|info|debug|error)|logger\.(?:info|debug|warn|error)|print)\s*\(([^\n]{0,300})")
        for match in logging_regex.finditer(text):
            hits = sorted({word for word in SENSITIVE_WORDS if word in match.group(2).lower()})
            if hits:
                findings.append({
                    "rule_id": "sensitive_logging",
                    "severity": "HIGH",
                    "status": "MANUAL ACTION REQUIRED",
                    "title": "Potential sensitive data in logs",
                    "message": "Logging statement references potentially sensitive fields: " + ", ".join(hits),
                    "evidence": [evidence(repo, path, text, match)],
                })

        payment_regex = re.compile(r"(?i)\b(card_number|cardnumber|credit_card|cvv|cvc|pan)\b")
        for match in payment_regex.finditer(text):
            provider = any(x in low for x in ("stripe", "adyen", "braintree", "paypal"))
            findings.append({
                "rule_id": "raw_payment_card_storage",
                "severity": "HIGH" if provider else "CRITICAL",
                "status": "NEEDS LEGAL REVIEW",
                "title": "Payment-card data handling requires review",
                "message": "Confirm provider tokenization/hosted collection and that PAN/CVV are never stored or logged.",
                "evidence": [evidence(repo, path, text, match)],
            })
            break

        upload_regex = re.compile(r"(?i)(app\.(post|put|patch)\s*\([^\n]*(upload|file)|@(?:app|router)\.(post|put|patch)\([^\n]*(upload|file))")
        for match in upload_regex.finditer(text):
            window = text[max(0, match.start() - 700):match.start()].lower()
            if not any(k in window for k in ("auth", "login_required", "permission", "authorize", "jwt", "session")):
                findings.append({
                    "rule_id": "public_upload_without_auth",
                    "severity": "HIGH",
                    "status": "MANUAL ACTION REQUIRED",
                    "title": "Upload endpoint may lack nearby authorization guard",
                    "message": "Heuristic only. Inspect the route and middleware before concluding.",
                    "evidence": [evidence(repo, path, text, match)],
                })

    unique = []
    seen = set()
    for finding in findings:
        ev = finding["evidence"][0]
        key = (
            finding["rule_id"],
            ev.get("file"),
            ev.get("line"),
            ev.get("symbol"),
        )
        if key not in seen:
            seen.add(key)
            unique.append(finding)

    return {
        "discovery": discover(repo),
        "findings": unique,
        "inventories": {
            "external_requests": external_requests,
            "cookies_storage": cookies_storage,
            "secrets": secrets,
            "third_party_processors": [],
            "sensitive_data": [],
        },
    }


def file_hashes(repo: Path) -> dict:
    result = {}
    for path in iter_text_files(repo):
        try:
            result[rel(repo, path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            pass
    return result


def changed_files(repo: Path) -> set[str] | None:
    state_path = repo / ".legal-audit" / "state.json"
    if not state_path.exists():
        return None
    old = json.loads(state_path.read_text(encoding="utf-8")).get("files_checked", {})
    current = file_hashes(repo)
    return (
        {k for k, v in current.items() if old.get(k) != v}
        | (set(old) - set(current))
    )


def save_state(repo: Path, result: dict) -> None:
    directory = repo / ".legal-audit"
    directory.mkdir(exist_ok=True)
    state = {
        "rule_version": RULE_VERSION,
        "scan_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "files_checked": file_hashes(repo),
        "findings": result["findings"],
        "inventories": result["inventories"],
    }
    (directory / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    (directory / "scan.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


def write_reports(repo: Path, cfg: dict, result: dict) -> tuple[Path, Path]:
    out = repo / "reports"
    out.mkdir(exist_ok=True)
    project_name = cfg.get("project", {}).get("name", repo.name)
    slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")
    md_path = out / f"{slug}-legal-audit.md"
    json_path = out / f"{slug}-legal-audit.json"

    payload = {
        "project": cfg.get("project", {}),
        **result,
        "manual_actions": [
            f for f in result["findings"]
            if f.get("manual_action") or f.get("status") == "MANUAL ACTION REQUIRED"
        ],
        "statement": "Technical audit only; no claim of legal compliance.",
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# {project_name} — Technical Legal/Privacy Audit",
        "",
        "> Technical repository audit only. This report is not legal certification.",
        "",
        f"- Findings: {len(result['findings'])}",
        f"- Frameworks: {', '.join(result['discovery']['frameworks']) or 'not deterministically identified'}",
        "",
        "## Findings",
    ]

    for finding in result["findings"]:
        ev = finding["evidence"][0]
        location = f"{ev.get('file', '?')}:{ev.get('line', ev.get('symbol', '?'))}"
        lines += [
            "",
            f"### {finding['title']}",
            f"- Severity: {finding['severity']}",
            f"- Status: {finding['status']}",
            f"- Evidence: {location}",
            f"- Found: {finding['message']}",
            "- Changed: none by deterministic scanner",
            "- Verification: contextual review/re-scan required",
            f"- You still need to: {finding.get('manual_action', 'Review source context and decide whether a technical change is required.')}",
        ]

    lines += [
        "",
        "## Third-party processors",
        "| Provider | Code location | Data sent | Purpose | Browser/server | Consent dependency |",
        "|---|---|---|---|---|---|",
        "",
        "## External requests",
        "| Domain | Trigger | Potentially exposed data | Required? | Consent controlled? |",
        "|---|---|---|---|---|",
    ]
    for row in result["inventories"]["external_requests"]:
        lines.append(
            f"| {row['domain']} | {row['file']}:{row['line']} | unknown | unknown | "
            f"{'review' if row['tracking_candidate'] else 'unknown'} |"
        )

    lines += [
        "",
        "## Cookies/storage",
        "| Name | Set by | Purpose | Category | Before consent? |",
        "|---|---|---|---|---|",
    ]
    for row in result["inventories"]["cookies_storage"]:
        lines.append(
            f"| {row['name']} | {row['set_by']} | {row['purpose']} | "
            f"{row['category']} | {row['before_consent']} |"
        )

    lines += [
        "",
        "## Secrets",
        "Never output the actual secret.",
        "",
        "| Type/provider | Location | Exposure | Required action |",
        "|---|---|---|---|",
    ]
    for row in result["inventories"]["secrets"]:
        lines.append(
            f"| {row['type_provider']} | {row['location']} | "
            f"{row['exposure']} | {row['required_action']} |"
        )

    lines += ["", "## Manual compliance actions"]
    manual = [
        f for f in result["findings"]
        if f.get("manual_action") or f.get("status") == "MANUAL ACTION REQUIRED"
    ]
    lines += [
        f"- {f.get('manual_action') or f['title']}" for f in manual
    ] or ["- None generated by deterministic scan."]

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def verify(repo: Path) -> dict:
    commands = []
    if (repo / "package.json").exists():
        commands += [
            ["npm", "test"],
            ["npm", "run", "lint"],
            ["npm", "run", "typecheck"],
            ["npm", "run", "build"],
        ]
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists():
        commands.append(["pytest", "-q"])

    results = []
    for command in commands:
        try:
            proc = subprocess.run(
                command,
                cwd=repo,
                text=True,
                capture_output=True,
                timeout=300,
            )
            results.append({
                "command": " ".join(command),
                "exit_code": proc.returncode,
                "stdout": proc.stdout[-4000:],
                "stderr": proc.stderr[-4000:],
            })
        except Exception as exc:
            results.append({
                "command": " ".join(command),
                "exit_code": 999,
                "stderr": str(exc),
            })

    if (repo / ".git").exists():
        proc = subprocess.run(
            ["git", "diff", "--check"],
            cwd=repo,
            text=True,
            capture_output=True,
        )
        results.append({
            "command": "git diff --check",
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        })

    return {
        "ok": bool(results) and all(r["exit_code"] == 0 for r in results),
        "results": results,
    }


def do_scan(args) -> None:
    repo = Path(args.repo).resolve()
    cfg_path = Path(args.config).resolve() if args.config else repo / "legal-audit.yaml"
    cfg = load_config(cfg_path, repo)

    delta = None if args.full else changed_files(repo)
    include_paths = delta if delta else None
    result = scan(repo, cfg, include_paths)

    result["incremental"] = {
        "full": args.full or delta is None,
        "changed_files": sorted(delta) if delta is not None else [],
    }
    save_state(repo, result)
    md_path, json_path = write_reports(repo, cfg, result)

    print(json.dumps({
        "findings": len(result["findings"]),
        "markdown_report": str(md_path),
        "json_report": str(json_path),
        "incremental": result["incremental"],
    }, indent=2))


def do_organization(args) -> None:
    repos = []
    for pattern in args.patterns:
        repos.extend(
            Path(p).resolve()
            for p in glob.glob(pattern)
            if Path(p).is_dir()
        )

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    rows = []
    shared_domains = {}
    for repo in sorted(set(repos)):
        cfg_path = repo / "legal-audit.yaml"
        if not cfg_path.exists():
            continue
        cfg = load_config(cfg_path, repo)
        result = scan(repo, cfg)
        write_reports(repo, cfg, result)
        name = cfg.get("project", {}).get("name", repo.name)
        rows.append((name, len(result["findings"])))
        for req in result["inventories"]["external_requests"]:
            shared_domains.setdefault(req["domain"], set()).add(name)

    lines = [
        "# Organization summary",
        "",
        "> Technical repository audit summary; not legal certification.",
        "",
        "| Project | Findings |",
        "|---|---:|",
    ]
    lines += [f"| {name} | {count} |" for name, count in rows]
    lines += ["", "## Shared external domains"]
    shared = [
        (domain, projects)
        for domain, projects in shared_domains.items()
        if len(projects) > 1
    ]
    lines += [
        f"- {domain}: {', '.join(sorted(projects))}"
        for domain, projects in sorted(shared)
    ] or ["- None detected across more than one audited repository."]

    (output / "organization-summary.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="legal-privacy-auditor")
    sub = parser.add_subparsers(dest="command", required=True)

    scan_parser = sub.add_parser("scan")
    scan_parser.add_argument("repo")
    scan_parser.add_argument("--config")
    scan_parser.add_argument("--full", action="store_true")
    scan_parser.set_defaults(fn=do_scan)

    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("repo")
    verify_parser.set_defaults(
        fn=lambda a: print(json.dumps(verify(Path(a.repo).resolve()), indent=2))
    )

    org_parser = sub.add_parser("organization")
    org_parser.add_argument("patterns", nargs="+")
    org_parser.add_argument("--output", default="reports")
    org_parser.set_defaults(fn=do_organization)

    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
