# ChatGPT orchestration contract

When this auditor is used through a connected GitHub repository:

1. Read the target repository and legal-audit.yaml.
2. Read the previous .legal-audit state, scan output, and reports when present.
3. Use deterministic evidence as the baseline, then inspect source context before confirming findings.
4. Apply only changes permitted by the configured audit mode and change flags.
5. Work on a dedicated branch and PR rather than writing directly to the default branch.
6. Verify changed behavior with repository tests/lint/typecheck/build and re-scan the issue.
7. Update Markdown and JSON reports.
8. Never infer missing legal/company facts and never claim legal compliance.

For organization-wide audits, inspect every matching implementation and identify shared risks across projects.
