#!/usr/bin/env bash
set -euo pipefail

repo="${1:-.}"
config="${2:-$repo/legal-audit.yaml}"
root="$(cd "$(dirname "$0")" && pwd)"

python3 "$root/auditor.py" scan "$repo" --config "$config"

if ! command -v codex >/dev/null 2>&1; then
  echo "Codex CLI not found. Deterministic scan completed." >&2
  exit 0
fi

prompt="$(cat <<PROMPT
Run LegalPrivacyAuditor against $repo using $config.

Read and obey:
- $root/AGENTS.md
- $root/RULES.md

Use $repo/.legal-audit/scan.json as baseline evidence, then inspect source context before confirming findings.

Apply only changes permitted by legal-audit.yaml.
Never invent legal/company facts.
Never output secret values.
After changes, re-scan the original issue and run available tests, lint, type checking, build, security tooling and git diff --check.
Never mark a finding FIXED when relevant verification failed.
Write/update both Markdown and JSON reports under $repo/reports/.
Never claim legal compliance.
PROMPT
)"

cd "$repo"
codex exec "$prompt"
