# Nuqta Ecosystem — Final Publication Readiness Report

**Report date:** 2026-10-28 (Session 7 — final remediation pass)
**Prepared by:** Claude Sonnet 4.6 (LegalPrivacyAuditor)
**Scope:** 8 platforms, 9 repositories
**Method:** Source-level audit reconciled against all prior session reports
**Classification:** Technical source review only — not a legal opinion, not compliance certification

---

## Platform Matrix

| Platform | Security | Privacy | Legal Content | GitHub Published | Publication Approval |
|---|---|---|---|---|---|
| Nuqta ID (backend) | GOOD — all P0/P1 fixed sessions 1–5 | Complete | Complete (NEEDS LEGAL REVIEW notices in place) | `f37e40e` | NOT APPROVED — legal items outstanding |
| Nuqta ID App (mobile) | GOOD — SYSTEM_ALERT_WINDOW removed, SecureStore hardened | Improved — 4-lang privacy/terms screens | Substantially improved; App Store labels manual | `4a1da26` | NOT APPROVED — PrivacyInfo.xcprivacy; App Store declarations |
| Nuqta Health | GOOD — PHI containment, DICOMweb read-only | Complete with special-category disclosures | Draft with NOT APPROVED banner + CI gate | `8b42b45` | NOT APPROVED — CI gate active (approved=false); 7 items outstanding |
| Nuqta Pro | GOOD — GDPR export, typed validators, allowlist | Complete, accurate | No user-visible developer text (fixed S7) | `f09eec2` | NOT APPROVED — governing law, liability cap pending legal review |
| Nuqta Sale | GOOD — GDPR export, typed validators, allowlist | Complete, accurate | No user-visible developer text (fixed S7) | `eef5cca` | NOT APPROVED — governing law, liability cap pending legal review |
| Nuqta SY | N/A (static site) | Complete — AR + EN | No user-visible developer text (fixed S7) | `459efa7` | NOT APPROVED — governing law pending legal review |
| Nuqta IT | N/A (static site) | Complete — EN + AR | NEEDS LEGAL REVIEW notices in place | `80d9e83` | NOT APPROVED — governing law, supervisory authority pending |
| Suar Services | N/A (static site) | Complete | No legal pages required (non-commercial info site) | `b054445` | NOT APPLICABLE for now |

---

## Session 7 Work — Finding Reconciliation

### S7-001: Pro TermsOfService §8 — MANUAL ACTION REQUIRED developer text visible to users
- **Original finding:** Rendered `<strong>MANUAL ACTION REQUIRED</strong>` in liability section
- **Fix:** Replaced with neutral "pending legal review" user-facing statement; developer instructions moved to JSX comment
- **Commit:** `f09eec2` (nuqtapro)
- **Status:** RESOLVED

### S7-002: Pro Impressum — MANUAL ACTION REQUIRED text visible in Commercial Register section
- **Original finding:** Rendered `<strong>MANUAL ACTION REQUIRED</strong>` in Impressum page
- **Fix:** Replaced with "Registration number: Pending — commercial registration in progress"
- **Commit:** `f09eec2` (nuqtapro)
- **Status:** RESOLVED

### S7-003: Sale TermsOfService §6 — Arabic developer instruction visible to users
- **Original finding:** Arabic "إجراء يدوي مطلوب: يجب أن يراجع مستشار قانوني مؤهل" visible in rendered output
- **Fix:** Replaced with neutral Arabic statement that liability cap is under legal review; developer instruction moved to JSX comment
- **Commit:** `eef5cca` (Nuqtasale)
- **Status:** RESOLVED

### S7-004: Sale TermsOfService footer — Arabic developer advisory visible to users
- **Original finding:** "يُنصح بمراجعة محامٍ متخصص لاستكمال هذه الشروط" visible in footer to all users
- **Fix:** Replaced with last-reviewed date; developer note moved to JSX comment
- **Commit:** `eef5cca` (Nuqtasale)
- **Status:** RESOLVED

### S7-005: Health publication gate — UI banner only, not enforceable
- **Original finding:** "NOT APPROVED FOR PUBLICATION" banner is a UI element; does not block deployment
- **Fix:** Created `legal/PUBLICATION_APPROVAL.json` (approved=false, 7 required items tracked). Added legal-gate CI step to `medical-production-gate.yml` — runs BEFORE migrations and tests; fails closed when approved=false. Updated `LEGAL_DEPLOYMENT_NOTES.md` to document the active gate.
- **Commit:** `8b42b45` (nuqtahealth)
- **Status:** RESOLVED — enforceable CI gate active; default state blocks deployment

### S7-006: nuqta-sy privacy/terms — [PLACEHOLDER] code element and developer text visible to users
- **Original finding:** Yellow notice banners contained `<code>[PLACEHOLDER]</code>` developer artifact; commercial registration section had `MANUAL ACTION REQUIRED` / `إجراء يدوي مطلوب` visible; Arabic §3 had inline `CONFIRM WITH LEGAL COUNSEL` English text
- **Fix:** Banners rephrased to user-appropriate "pending legal review" notices; commercial registration fields changed to "Pending — registration in progress"; inline developer instructions removed
- **Commit:** `459efa7` (nuqta-sy)
- **Status:** RESOLVED

### S7-007: nuqtaid .legal-audit/ directory untracked, no gitignore entry
- **Fix:** Added `.legal-audit/` to nuqtaid `.gitignore`
- **Commit:** `f37e40e` (nuqtaid)
- **Status:** RESOLVED

### S7-008: nuqtait and suar-services-static .legal-audit/ scanner state tracked in git
- **Fix:** Removed `.legal-audit/scan.json` and `.legal-audit/state.json` from tracking via `git rm --cached`; added `.legal-audit/` to each repo's `.gitignore`
- **Commits:** `80d9e83` (nuqtait), `b054445` (suar-services-static)
- **Status:** RESOLVED

### S7-009: Nuqta ID App — staged audit report update unpublished
- **Finding:** An updated `reports/nuqtaidapp-legal-audit.md` was staged but not committed
- **Fix:** Committed and pushed the updated report reflecting all fixes since the 2026-10-13 baseline (age gate closed, privacy/terms screens added, SYSTEM_ALERT_WINDOW removed)
- **Commit:** `4a1da26` (Nuqta_ID_APP)
- **Status:** RESOLVED

---

## Historical Findings (Sessions 1–6) — Status Reconciliation

All P0 and P1 findings from sessions 1–6 are confirmed resolved. Full detail in
`reports/nuqta-ecosystem-privacy-audit.md` session logs. Summary:

| ID | Finding | Session | Platform | Status |
|---|---|---|---|---|
| P0-1 | Health PrivacyPolicy critical placeholders | 1 | nuqtahealth | RESOLVED |
| P0-GDPR-SALE | Sale GDPR export credential leak (hengar_api_key) | 2 | Nuqtasale | RESOLVED |
| P0-GDPR-PRO | Pro GDPR export credential leak | 2 | nuqtapro | RESOLVED |
| P0-2 | Suar Services Google Fonts CDN → EU data transfer | 2 | suar-services-static | RESOLVED |
| P1-1 | Health unsupported legal assertions (SCCs, Damascus courts) | 2 | nuqtahealth | RESOLVED |
| P1-2 | Nuqta SY Arabic pages incomplete | 2 | nuqta-sy | RESOLVED |
| P1-3 | Nuqta IT visible placeholder fields | 2 | nuqtait | RESOLVED |
| P1-4 | Pro/Sale liability + governing law (partial) | 7 | nuqtapro / Nuqtasale | PARTIALLY RESOLVED — developer text removed; legal decisions outstanding |
| P2-1 | Health commercial registration / license# | ongoing | nuqtahealth | CI-GATED — requires operator action |
| P2-2 | ID App PrivacyInfo.xcprivacy | ongoing | Nuqta_ID_APP | OPEN — App Store submission step |
| P2-3 | ID DOB encryption in pending records | 3 | nuqtaid | RESOLVED |
| P2-5 | Cross-platform flows disclosure | ongoing | all | PARTIALLY ADDRESSED — cross-platform flows documented in Health and ID policies |
| S3-x | AuditLog.details sanitization | 3 | nuqtapro / Nuqtasale | RESOLVED |
| S4-x | NID encryption in PendingRegistration | 4 | nuqtaid | RESOLVED |
| S5-x | Typed per-field validators for GDPR audit export | 5 | nuqtapro / Nuqtasale | RESOLVED |
| S5-x | DOB full validation after Fernet decryption | 5 | nuqtaid | RESOLVED |
| S6-x | Health banner documentation corrected | 6 | legal-privacy-auditor | RESOLVED |
| S7-x | All items above | 7 | multiple | See S7-001 through S7-009 |

---

## Security and Privacy Summary

**Total historical findings reviewed:** 38 (across sessions 1–7)
**Confirmed P0/P1 technical defects fixed:** 14
**Historical findings closed (verified already fixed):** 11
**Still open — require legal counsel or operator action:** 9 (see Legal Approval Package below)
**Unresolved technical defects:** 0 known

**Security posture confirmed:**
- PHI containment: Health only; intentional Health→ID patient portal flow (constant-time HMAC, no PHI in logs)
- GDPR export: Pro/Sale/ID all use explicit allowlist serializers; no credential exposure
- Tenant isolation: All platforms — queries scoped to `shop_id`/`facility_id` from JWT
- Log redaction: SecretRedactingFilter (Sale), rate_limit fix (Health), DOB redacted in Health logs
- Age gate: ID backend hard gate (DOB required unconditionally), 5 regression tests
- Encryption: DOB and national_id Fernet-encrypted in pending records (ID), API keys Fernet-encrypted at rest

---

## Legal Pages Status

| Platform | Privacy Policy | Terms of Service | Impressum/Legal Notice | Developer Text Visible? | Approval Banner/Gate |
|---|---|---|---|---|---|
| Nuqta ID | Complete | Complete | Not required | No | NEEDS LEGAL REVIEW notices in place |
| Nuqta ID App | 4-language screens | 4-language screens | Not required | No | App Store labels manual |
| Nuqta Health | Complete draft | Complete draft | Complete draft | No (JSX comments only) | CI gate active (approved=false) |
| Nuqta Pro | Complete | Complete (liability cap pending) | Complete | No | No gate — legal review needed |
| Nuqta Sale | Complete | Complete (liability cap pending) | Complete | No | No gate — legal review needed |
| Nuqta SY | Complete (AR+EN) | Complete (AR+EN, governing law pending) | Embedded in privacy | No | Pending review notice |
| Nuqta IT | Complete (EN+AR) | Complete (governing law pending) | Not separate — operator info in policy | No | NEEDS LEGAL REVIEW notices in place |
| Suar Services | Complete | Not required | Not currently required | N/A | N/A |

---

## CI and Verification

| Platform | Local Tests | Hosted CI | Legal Gate | Notes |
|---|---|---|---|---|
| Nuqta Health | NOT RUN this session | medical-production-gate.yml active on GitHub | ACTIVE — `legal/PUBLICATION_APPROVAL.json`, approved=false | New legal-gate step added to CI |
| Nuqta Pro | NOT RUN | ci.yml on GitHub | NONE (no hard gate) | Liability + governing law need legal review |
| Nuqta Sale | NOT RUN | ci.yml on GitHub | NONE | Same as Pro |
| All others | NOT RUN | Varies | N/A | Source-only review this session |

No local application execution, test runs, Docker operations, or production deployments were performed.
All verification is source-level code review and commit inspection.

---

## Final Legal Approval Package

The following items are genuinely outstanding and require external action before publication.
These cannot be resolved by source code changes alone.

### Category A — Operator Must Provide (no legal counsel required)

| Item | Platform(s) | Where to enter | Notes |
|---|---|---|---|
| Syrian commercial registration number | Health, SY, Pro (Impressum), IT | `nuqtahealth/frontend/src/components/PrivacyPolicy.jsx` §1 + `Impressum.jsx`; `nuqta-sy/privacy.html` §7; `nuqta-sy/en/privacy.html` §7; `nuqtapro/frontend/src/components/Impressum.js` | Obtain from Syrian Ministry of Economy; enter once received |
| Transactional email SMTP provider name | Health | `nuqtahealth/frontend/src/components/PrivacyPolicy.jsx` processor table "Provider to be named" | Identify the actual SMTP relay used (Mailgun, SendGrid, Postfix, etc.) |

### Category B — Legal Counsel Required (qualified legal professional)

| Item | Platform(s) | Section | Proposed wording available? |
|---|---|---|---|
| Healthcare license number and applicable regulatory authority for Qamishlo/AANES | Health | `Impressum.jsx` §4 | No — requires operator to obtain license and confirm applicable authority |
| Governing law and dispute resolution forum | Health, Pro, Sale, SY, IT | Health `TermsOfService.jsx` §7; Pro `TermsOfService.js` §10; Sale `TermsOfService.js` §8; SY `en/terms.html` §5; IT `content/en.json` terms §5 | Partial — operator's registered address is Damascus; Syrian/AANES law applicability needs counsel |
| Limitation of liability clause and maximum liability cap | Health, Pro, Sale | Health `TermsOfService.jsx` §6; Pro `TermsOfService.js` §8; Sale `TermsOfService.js` §6 | No — jurisdiction-specific; requires lawyer to draft |
| Subscription agreement terms (pricing, billing, cancellation) | Health | `TermsOfService.jsx` §2 "Subscription agreement terms to be added" | No — business decision + legal review |
| Advance notice period for Terms changes | Health | `TermsOfService.jsx` §8 | Partial — 30 days is reasonable; needs legal confirmation as binding commitment |
| Supervisory authority for data subject complaints | Health (§8 Rights), IT (§7) | Both privacy policies | Partial — EU users: local DPA; non-EU: confirm applicable authority with counsel |

### Category C — App Store (platform declaration steps, not source changes)

| Item | Platform | Action |
|---|---|---|
| Apple PrivacyInfo.xcprivacy | Nuqta ID App | Create and include in EAS build; declare all required reason APIs |
| App Store Privacy Nutrition Labels | Nuqta ID App | Complete Apple App Privacy questionnaire; complete Google Play Data Safety section |
| Age rating confirmation | Nuqta ID App | Confirm app store listings do not declare suitability for users under 18 |

### Category D — Security Hardening (non-blocking, do before production)

| Item | Platform | Action |
|---|---|---|
| `.env` permissions | nuqtahealth | `chmod 600 backend/.env` on production server (currently 664) |

---

## Publication Decision

**PUBLICATION BLOCKED — SPECIFIC MANDATORY REQUIREMENTS OUTSTANDING**

All known technical P0/P1 security and privacy defects have been resolved in source. However:

1. **Nuqta Health** has an active CI gate (`approved=false`) blocking deployment until all 7 required legal approvals are recorded in `legal/PUBLICATION_APPROVAL.json`.
2. **Pro and Sale** have outstanding governing law and liability cap clauses requiring legal counsel — no hard gate is currently in place for these platforms beyond the existing NEEDS LEGAL REVIEW notices.
3. **All platforms** have commercial registration pending (Category A — operator action).
4. **Nuqta ID App** requires App Store privacy declarations before submission.

Technical source preparation is complete to the maximum extent achievable without legal counsel and operator-provided facts.

---

*This report is a technical source-code review. It is not legal advice. All determinations
regarding GDPR compliance, healthcare data regulations, or any other legal requirement must
be made by qualified legal counsel. No production deployment has been performed.*
