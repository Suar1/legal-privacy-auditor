# Nuqta Ecosystem — Consolidated Legal & Privacy Audit
**Audit date:** 2026-10-28  
**Auditor:** Claude (LegalPrivacyAuditor v1 framework)  
**Scope:** 8 platforms + cross-platform data flow review  
**Method:** Automated scanner (LegalPrivacyAuditor) + full manual review of all 14 RULES.md areas  
**Classification:** AUDIT ONLY — not a legal opinion, not a compliance certification

---

## Executive Summary

The Nuqta ecosystem is a collection of 8 platforms at varying stages of legal documentation
completion. The technical architecture is generally sound: PHI stays in Health, API keys
are encrypted, logs are redacted, tenant isolation is enforced. The primary gaps are
**documentation placeholders** — unfilled `[PLACEHOLDER]` markers in legal pages —
and one active **technical privacy risk** in Suar Services (Google Fonts loading).

**Overall ecosystem readiness for pilot:** CONDITIONALLY APPROVED  
**Overall ecosystem readiness for EU commercial launch:** NOT YET — requires resolving 4 CRITICAL/HIGH gaps

---

## Platform Scorecard

| Platform | CRITICAL | HIGH | MEDIUM | LOW | Info | Pilot OK? |
|---|---|---|---|---|---|---|
| 1. Nuqta ID | 0 | 0 | 3 | 1 | 3 | ✓ Yes |
| 2. Nuqta ID App | 0 | 1 | 2 | 1 | 3 | ✓ Yes (App Store label needed for iOS) |
| 3. Nuqta Health | 1 | 0 | 3 | 1 | 3 | ✗ No — privacy policy [PLACEHOLDER] critical |
| 4. Nuqta Pro | 0 | 0 | 2 | 1 | 2 | ✓ Yes (with ToS note) |
| 5. Nuqta Sale | 0 | 0 | 2 | 2 | 3 | ✓ Yes |
| 6. Nuqta SY | 0 | 0 | 3 | 0 | 1 | ✓ Yes (draft banners shown) |
| 7. Nuqta IT | 0 | 0 | 3 | 0 | 2 | ✓ Yes (draft pages acceptable) |
| 8. Suar Services | 0 | 1 | 1 | 0 | 2 | ✗ No — Google Fonts GDPR risk |

---

## Prioritised Findings Across All Platforms

### P0 — Must fix before any production exposure

#### P0-1: Nuqta Health PrivacyPolicy.jsx — CRITICAL [PLACEHOLDER] values [Platform 3]
- **File:** `nuqtahealth/frontend/src/components/PrivacyPolicy.jsx:34,228,234,240,249,252,309`
- **Detail:** Operator name, commercial registration number, VAT, regulatory authority,
  and healthcare license number are all `[PLACEHOLDER]`. A platform processing Special
  Category Data (PHI) under GDPR Art. 9 must have a complete, accurate privacy policy
  before any patient data is processed.
- **Remediation:** Fill all `[PLACEHOLDER]` markers with verified legal details.
  Commercial registration and regulatory authority details must be confirmed with a
  qualified legal professional.

#### P0-2: Suar Services Google Fonts — HIGH undisclosed data transfer to Google [Platform 8]
- **Files:** All 300+ HTML pages via shared header template loading
  `https://fonts.googleapis.com/css2?family=Inter:...`
- **Detail:** Inter font is served from `fonts.googleapis.com` — not self-hosted.
  Every page visit transmits visitor IP to Google. The German Datenschutzerklärung
  does not disclose Google as a processor. Site is operated from Munich (VAT DE407508302).
  LG München I (2022) precedent applies.
- **Remediation:** Self-host Inter alongside self-hosted Cairo. Remove `googleapis.com`
  links from shared header. Single-day remediation.

### P1 — Fix before commercial B2B onboarding

#### P1-1: Nuqta Sale Terms of Service — liability and governing law sections [Platform 5]
- **File:** `Nuqtasale/frontend/src/components/TermsOfService.js:87,101`
- **Detail:** Section 6 (liability limitation) and Section 8 (governing law/jurisdiction)
  contain Arabic placeholder text — neither the liability limitation clauses nor the
  governing law are stated.
- **Remediation:** Legal counsel to draft liability terms and specify governing law.

#### P1-2: Nuqta Pro Terms of Service — SLA placeholder [Platform 4]
- **File:** `nuqtapro/frontend/src/components/TermsOfService.js:87`
- **Detail:** Section 4 (SLA terms) marked `[PLACEHOLDER — SLA terms]`.
- **Remediation:** Define SLA commitments or note "as agreed in individual service contracts."

#### P1-3: Nuqta IT privacy policy and terms — 8 placeholder fields [Platform 7]
- **Detail:** Legal basis for inquiry handling, log retention period, hosting provider,
  supervisory authority, limitation of liability, governing law/court.
- **Remediation:** Confirm with legal counsel; configure and document nginx log rotation;
  identify hosting provider DPA.

### P2 — Address before EU launch

#### P2-1: Nuqta Health Impressum — all `[PLACEHOLDER]` fields [Platform 3]
- **File:** `nuqtahealth/frontend/src/components/Impressum.jsx`
- **Detail:** All operator fields (commercial registration, authority, VAT, regulatory
  authority, healthcare license) are placeholder.

#### P2-2: Nuqta SY legal pages — lawful basis, retention, governing law [Platform 6]
- **Detail:** Log retention period, legal basis confirmation, governing law placeholder.
- **Remediation:** Same as IT — confirm with legal counsel.

#### P2-3: Nuqta ID app store privacy labels not verifiable [Platform 2]
- **Detail:** `PrivacyInfo.xcprivacy` not present in source (generated at EAS build time).
  iOS App Store privacy nutrition labels must be accurate.
- **Remediation:** Verify EAS build output includes `PrivacyInfo.xcprivacy` and confirm
  App Store privacy questionnaire matches actual data collection.

#### P2-4: Nuqta ID DOB not Fernet-encrypted [Platform 1]
- **Detail:** National ID numbers are Fernet-encrypted in Nuqta ID's profile store,
  but date of birth (also sensitive, used for QR double-factor auth in Health) is not
  encrypted at the field level.
- **Remediation:** Consider adding field-level encryption for DOB in the profile database.

#### P2-5: Cross-platform flows not consistently disclosed across all privacy policies [Platform 9]
- **Detail:** Nuqta ID and Sale disclose cross-platform identity data flows. Nuqta Health
  and Pro have incomplete legal pages that don't clearly describe identity lookup from
  Nuqta ID.
- **Remediation:** After completing Health and Pro legal pages (P0-1, P1-2), add explicit
  disclosure of Nuqta ID as an identity data source.

---

## What Is Working Well

### Architecture
- **PHI containment confirmed:** Clinical records never cross platform boundaries.
  `nuqta_id_integration_service.py` uses patient-portal serialisers only — no clinical
  leakage possible.
- **API key encryption:** All inter-platform credentials Fernet-encrypted at rest
  (`APP_ENCRYPTION_KEY` or `APP_ENCRYPTION_KEY`).
- **Log redaction:** `SecretRedactingFilter` (Sale), rate_limit fixes (Health),
  `dob=***REDACTED***` in Health — sensitive data excluded from logs across platforms.
- **Tenant isolation:** All Sale, Pro, and Health queries scoped to `shop_id` /
  `facility_id` extracted from JWT. Cross-tenant data access is not architecturally possible.
- **DICOMweb read-only:** `methods=["GET", "HEAD", "OPTIONS"]` on Health's DICOMweb
  proxy — no write access to imaging data (commit df4cc68).

### Legal pages
- **Real operator identity in all platforms:** Suar Mustafa, Damascus/Munich/Syria.
  No platform has entirely fictitious operator details.
- **Bunny Fonts across all platforms except Suar Services:** Google Fonts replaced with
  Bunny Fonts in Nuqta ID, Health, Pro, Sale, SY, IT — reducing EU data transfer risk.
- **Multi-language legal pages:** Nuqta ID (4 languages: AR, EN, KU, SO),
  Suar Services (3: EN, DE, AR), Nuqta IT (2: AR, EN), Nuqta SY (2: AR, EN).
- **HMAC-signed unsubscribe tokens:** Nuqta ID, Health, Pro — CAN-SPAM/GDPR Art. 21
  compliant unsubscribe mechanism for transactional/marketing emails.

### Mobile app (Nuqta ID App)
- **`expo-secure-store` with `WHEN_UNLOCKED_THIS_DEVICE_ONLY`** for all tokens.
- **`android:allowBackup="false"`** — prevents backup of secure data.
- **`usesCleartextTraffic="false"`** — enforces HTTPS.
- **No SYSTEM_ALERT_WINDOW** permission.
- **Documents stored in private sandbox only** — never uploaded to server.

---

## Scanner Framework Observations

### Confirmed framework limitations found during this audit

1. **IPv6 URL false positive** (crash): `URL_RE = re.compile(r'https?://[^\s"\'<>)]+', re.I)`
   greedily captures markdown link syntax from report files, creating invalid URLs that
   cause `urlparse()` to raise `ValueError: Invalid IPv6 URL`. Affected: Nuqta Sale scanner.
   Root cause: `reports/` not in `SKIP_DIRS`.

2. **`pan-y` CSS false positive** (CRITICAL): `touch-action: pan-y` CSS gesture directive
   matched as payment card PAN pattern. Affected: Nuqta IT, Suar Services.

3. **Scanner reading own output** (HIGH/CRITICAL): The scanner processes its own
   `reports/` directory output files, which may contain the words "PAN", "credit_card",
   etc. from the audit text. Affected: every platform with a prior report. Root cause:
   `reports/` not in `SKIP_DIRS`.

4. **"pan" in animation text** (HIGH): "horizontal scroll gallery pan" in
   `suar-services-static/.agents/skills/` matched as payment card pattern.

**Recommended framework fix:** Add `reports/`, `.agents/`, `skills/` to `SKIP_DIRS`.

---

## Ecosystem Readiness Matrix

| Requirement | ID | App | Health | Pro | Sale | SY | IT | Suar |
|---|---|---|---|---|---|---|---|---|
| Real operator identity | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Privacy policy exists | ✓ | N/A | ✗ CRITICAL | ✓ | ✓ | ✓ draft | ✓ draft | ✓ |
| Terms of service exists | ✓ | N/A | ✓ | ✗ partial | ✗ partial | ✓ draft | ✓ partial | N/A |
| No Google Fonts | ✓ | N/A | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ HIGH |
| No analytics/tracking | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Log redaction | ✓ | N/A | ✓ | ✓ | ✓ | N/A | N/A | N/A |
| .env permissions 600 | ✓ | N/A | ✗ (664) | ✓ | ✓ | N/A | N/A | N/A |
| Unsubscribe mechanism | ✓ | N/A | ✓ | ✓ | N/A | N/A | N/A | N/A |
| Data export endpoint | ✓ partial | N/A | ✓ | ✗ | ✗ | N/A | N/A | N/A |
| Account deletion path | ✓ via email | N/A | ✓ | ✗ | ✗ | N/A | N/A | N/A |
| Secure storage (mobile) | N/A | ✓ | N/A | N/A | N/A | N/A | N/A | N/A |
| GDPR rights listed | ✓ | N/A | ✓ | partial | ✓ | ✓ | ✓ | ✓ |

**Key:** ✓ = implemented/complete, ✗ = missing/incomplete, N/A = not applicable

---

## Remediation Priority Order

1. **TODAY:** Nuqta Health — fill `PrivacyPolicy.jsx` and `Impressum.jsx` placeholders (P0-1, P2-1)
2. **TODAY:** Suar Services — self-host Inter font, remove Google Fonts CDN link (P0-2)
3. **Before B2B onboarding:** Nuqta Sale, Pro, IT — legal counsel review for governing law, liability, SLA (P1-1, P1-2, P1-3)
4. **Before EU launch:** Nuqta SY legal pages, cross-platform disclosure (P2-2, P2-5)
5. **Before App Store submission:** Nuqta ID App — verify PrivacyInfo.xcprivacy (P2-3)
6. **Security hardening (non-blocking):** Health .env permissions, ID DOB encryption (P2-4)

---

## Individual Platform Reports

| Platform | Report location |
|---|---|
| Nuqta ID | `/home/suar/nuqtaid/reports/nuqtaid-legal-audit.md` |
| Nuqta ID App | `/home/suar/Nuqta_ID_APP/reports/nuqtaidapp-legal-audit.md` |
| Nuqta Health | `/home/suar/nuqtahealth/reports/nuqtahealth-legal-audit.md` |
| Nuqta Pro | `/home/suar/nuqtapro/reports/nuqtapro-legal-audit.md` |
| Nuqta Sale | `/home/suar/Nuqtasale/reports/nuqtasale-legal-audit.md` |
| Nuqta SY | `/home/suar/nuqta-sy/reports/nuqta-sy-legal-audit.md` |
| Nuqta IT | `/home/suar/nuqtait/reports/nuqtait-legal-audit.md` |
| Suar Services | `/home/suar/suar-services-static/reports/suar-services-legal-audit.md` |
| Cross-platform flows | `/home/suar/docs/audit-2026-10-28/cross-platform-data-flow-audit.md` |

---

*This report represents a technical review of source code and configuration files.
It is not legal advice. All legal determinations regarding compliance with GDPR,
HIPAA, or other applicable regulations must be made by qualified legal counsel.*

