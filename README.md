# LegalPrivacyAuditor

Reusable technical privacy/legal audit framework for web and mobile repositories.

It combines deterministic repository scanning, project-level configuration, ChatGPT/Codex reasoning, verification gates, Markdown/JSON reporting, and incremental scan state.

It is a technical audit tool. It must never claim that an application is legally compliant.

## Install

    cd legal-privacy-auditor
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt

## Audit one repository

    python auditor.py scan /srv/projects/nuqtahealth --config /srv/projects/nuqtahealth/legal-audit.yaml
    python auditor.py verify /srv/projects/nuqtahealth

Use --full to force a complete rescan.

## Codex on your server

    ./run-codex.sh /srv/projects/nuqtahealth /srv/projects/nuqtahealth/legal-audit.yaml

The script runs deterministic evidence collection first and then invokes codex exec inside the target repository. AGENTS.md defines the persistent safety/reporting contract.

## ChatGPT

When ChatGPT has access to the GitHub repository, use CHATGPT.md as the orchestration contract. Make application changes on a dedicated branch/PR. Deterministic output under .legal-audit/ remains the evidence baseline.

## Multiple repositories

    python auditor.py organization '/srv/projects/nuqta*' --output reports

## Modes

- audit-only: report only.
- fix-safe: low-risk technical fixes allowed by configuration.
- fix-review: larger changes may be prepared but require developer review.

Unknown legal/company values become manual-action findings and are never guessed.
