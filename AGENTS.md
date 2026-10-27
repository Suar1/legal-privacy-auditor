# LegalPrivacyAuditor agent contract

Use this contract when Codex or another coding agent runs the auditor.

## Required sequence

1. Read the target repository legal-audit.yaml.
2. Run the deterministic scanner before modifying application code.
3. Inspect every cited implementation in source context. Heuristics are not final findings by themselves.
4. Apply the configured mode:
   - audit-only: no application changes.
   - fix-safe: only clearly technical, low-risk changes allowed by configuration.
   - fix-review: larger changes may be prepared, but flag them for developer review.
5. Never invent legal name, postal address, privacy/DPO contact, copyright contact, DMCA agent, age threshold, retention period, jurisdiction, or other legal/company fact.
6. Never delete production/user data, weaken authentication/authorization, expose secrets, or move secrets into browser-visible variables.
7. Privacy/security controls that can be bypassed by a client require backend enforcement.
8. After changes, re-scan the original issue and run available tests, lint, type checking, build, security tooling, and git diff --check.
9. Never report FIXED when relevant verification failed.
10. Never state that an application is GDPR/COPPA/otherwise legally compliant.

## Evidence

Every confirmed finding needs concrete repository evidence: file path and line/symbol/component/function/class/route/API endpoint/model/config variable when available.

Scan every implementation, not only the first match. Never output actual secret values.

## Required review areas

Read RULES.md and review all 14 areas, including areas where the deterministic scanner has no match.

## Reporting

Write:
- reports/<project>-legal-audit.md
- reports/<project>-legal-audit.json

Severity: CRITICAL, HIGH, MEDIUM, LOW, INFO.

Status: FIXED, PARTIALLY FIXED, NOT APPLICABLE, MANUAL ACTION REQUIRED, NEEDS LEGAL REVIEW.
