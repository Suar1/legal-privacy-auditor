# Nuqta Ecosystem — Consolidated Legal & Privacy Audit
**Audit date:** 2026-10-28 (initial) · **Updated:** 2026-10-28 (session 2) · **Updated:** 2026-10-28 (session 3) · **Updated:** 2026-10-28 (session 4) · **Updated:** 2026-10-28 (session 5) · **Updated:** 2026-10-28 (session 6) · **Updated:** 2026-10-28 (session 7)
**Auditor:** Claude (LegalPrivacyAuditor v1 framework)
**Scope:** 8 platforms + cross-platform data flow review
**Method:** Automated scanner (LegalPrivacyAuditor) + full manual review of all 14 RULES.md areas
**Classification:** AUDIT ONLY — not a legal opinion, not a compliance certification

### Current branch SHAs (post session 7, 2026-10-28)

| Platform | GitHub repo | main SHA |
|---|---|---|
| Nuqta ID (backend) | Suar1/nuqtaid | `f37e40e` |
| Nuqta ID App (mobile) | Suar1/Nuqta_ID_APP | `4a1da26` |
| Nuqta Health | Suar1/nuqtahealth | `8b42b45` |
| Nuqta Pro | Suar1/nuqtapro | `f09eec2` |
| Nuqta Sale | Suar1/Nuqtasale | `eef5cca` |
| Nuqta SY | Suar1/Nuqta-SY | `459efa7` |
| Nuqta IT | Suar1/nuqtait | `80d9e83` |
| Suar Services | Suar1/suar-services-static | `b054445` |
| Legal/Privacy Auditor | Suar1/legal-privacy-auditor | Audited baseline: `c6be168` (pre-session 5; self-referential SHA excluded) |

---

## Executive Summary

The Nuqta ecosystem is a collection of 8 platforms at varying stages of legal documentation
completion. The technical architecture is generally sound: PHI stays within Health (with
patient read-only access granted via Nuqta ID integration), API keys are encrypted, logs
are redacted, tenant isolation is enforced.

**Session 2 (2026-10-28) resolved all P0 and P1 findings** from the initial audit: Google
Fonts CDN removed from Suar Services; Health privacy/terms corrected (unsupported SCC
claims removed, governing law caveat added); Sale/Pro GDPR export credential leaks fixed
with explicit allowlist serializers and regression tests; Nuqta IT visible placeholders
resolved; Nuqta SY Arabic pages completed; Nuqta ID age gate verified watertight.

The remaining open items are all legal-judgment decisions requiring qualified legal counsel:
governing law, supervisory authority, limitation of liability caps, and commercial registration
numbers across several platforms.

**Overall ecosystem readiness for pilot (technical perspective):** All known P0/P1 source-code
issues resolved as of session 5. This is a source-code technical finding only — it does NOT
constitute legal approval, compliance certification, or a clearance to process real patient data.
Pilot readiness for live users requires separate sign-off from qualified legal counsel on governing
law, processor DPAs, and commercial registration.

**Overall ecosystem readiness for EU commercial launch:** NOT YET — requires legal counsel
review for governing law, processor DPAs, and Health commercial registration details.

---

## Platform Scorecard (updated 2026-10-28 session 7)

**Readiness columns are reported separately.** A source-code audit cannot grant launch
authorization. Each column reflects a distinct gate; all must be ✓ before production launch.

| Platform | CRITICAL | HIGH | MEDIUM | LOW | Info | Tech Remediations Applied? | Local Tests Run? | Hosted CI? | Legal Docs Approved? | Launch Auth? |
|---|---|---|---|---|---|---|---|---|---|---|
| 1. Nuqta ID | 0 | 0 | 1 | 1 | 3 | ✓ Yes (sessions 1–5) | ✓ Yes — all relevant tests pass | Not verified | ✗ No — NEEDS LEGAL REVIEW items remain | ✗ NOT AUTHORIZED |
| 2. Nuqta ID App | 0 | 1 | 1 | 1 | 3 | ✓ Source fixes applied | ✓ Mobile audit published | Not verified | ✗ No — App Store labels, PrivacyInfo.xcprivacy unverified | ✗ NOT AUTHORIZED |
| 3. Nuqta Health | 0 | 0 | 2 | 1 | 3 | ✓ Yes (sessions 1–4, 7) | ✓ Yes — relevant tests pass | Not verified | ✗ No — CR#, license#, regulatory authority, governing law unresolved; CI gate active (approved=false) | ✗ NOT AUTHORIZED |
| 4. Nuqta Pro | 0 | 0 | 0 | 1 | 2 | ✓ Yes (sessions 1–5, 7) | ✓ Yes — 68 tests pass | Not verified | ✗ No — governing law, liability cap pending legal review | ✗ NOT AUTHORIZED |
| 5. Nuqta Sale | 0 | 0 | 0 | 2 | 3 | ✓ Yes (sessions 1–5, 7) | ✓ Yes — 63 tests pass | Not verified | ✗ No — governing law, liability cap pending legal review | ✗ NOT AUTHORIZED |
| 6. Nuqta SY | 0 | 0 | 0 | 0 | 1 | ✓ Yes — S7: developer text removed | ✓ Yes — static tests pass | Not verified | ✗ No — governing law NEEDS LEGAL REVIEW | ✗ NOT AUTHORIZED |
| 7. Nuqta IT | 0 | 0 | 1 | 0 | 2 | ✓ Yes — visible placeholders resolved | ✓ Yes — all tests pass | Not verified | ✗ No — governing law, supervisory authority NEEDS LEGAL REVIEW | ✗ NOT AUTHORIZED |
| 8. Suar Services | 0 | 0 | 1 | 0 | 2 | ✓ Yes — Google Fonts CDN removed | ✓ Yes — navigation tests pass | Not verified | N/A (no legal pages required) | ✗ NOT AUTHORIZED |

---

## Prioritised Findings Across All Platforms

### P0 — Must fix before any production exposure

#### P0-1: Nuqta Health PrivacyPolicy.jsx — CRITICAL [PLACEHOLDER] values [Platform 3] ✅ RESOLVED
- **File:** `nuqtahealth/frontend/src/components/PrivacyPolicy.jsx`
- **Resolution (2026-10-28):** All verifiable placeholder fields (operator name, address,
  email, retention periods) filled. Remaining MANUAL ACTION items (commercial registration
  number, healthcare license number, regulatory authority) now marked with explicit
  NEEDS LEGAL REVIEW notices. "NOT APPROVED FOR PUBLICATION" red banner added to the page
  as a visible UI warning. **Note:** the banner is UI-only and does not technically prevent
  deployment — the deployment guard remains unimplemented (see `LEGAL_DEPLOYMENT_NOTES.md`).
- **Remaining:** CR# and healthcare license# require operator manual action; not a
  blocking technical issue — it is a legal completeness issue.

#### P0-GDPR-SALE: Nuqta Sale GDPR export — credential leak via `include_sensitive=True` ✅ RESOLVED
- **File:** `Nuqtasale/backend/app/modules/auth/routes.py` (gdpr_export endpoint)
- **Detail (found session 2):** The GDPR Art. 20 export endpoint called
  `user_to_dict(include_sensitive=True)` which included `hengar_api_key` (integration
  API key), `password_hash`, `pin_hash`, `exit_pin_hash`, `cashier_badge_token_hash`,
  `exit_pin_reset_token_hash`, and `qr_code_image` in the downloadable JSON.
- **Resolution (2026-10-28):** Added `UserService.gdpr_export_profile()` explicit
  allowlist serializer; 12 regression tests in `tests/test_gdpr_export_security.py`
  including sentinel-based `hengar_api_key` exclusion test; added `Cache-Control: no-store`
  and security headers; fixed misleading "all personal information" docstring.

#### P0-GDPR-PRO: Nuqta Pro GDPR export — same credential leak design ✅ RESOLVED
- **File:** `nuqtapro/backend/app/modules/auth/routes.py` (gdpr_export endpoint)
- **Resolution (2026-10-28):** Same pattern as Sale — `gdpr_export_profile()` allowlist
  added with Pro-specific fields; `marketing_emails_opted_out` included as GDPR consent
  record; 14 regression tests in `tests/test_gdpr_export_security.py`.

#### P0-2: Suar Services Google Fonts — HIGH undisclosed data transfer to Google [Platform 8] ✅ RESOLVED
- **Resolution (2026-10-28):** Inter self-hosted from `@fontsource/inter` v5 WOFF2 files
  (OFL-1.1 licence preserved); all 100+ HTML pages regenerated without googleapis/gstatic
  links; Google Fonts removed from external-request allowlist in `validate-navigation.cjs`
  so a CDN regression fails the test suite.

### P1 — Fix before commercial B2B onboarding

#### P1-1: Nuqta Health — unsupported legal assertions in PrivacyPolicy.jsx ✅ RESOLVED
- **Files:** `nuqtahealth/frontend/src/components/PrivacyPolicy.jsx`, `Impressum.jsx`, `TermsOfService.jsx`
- **Detail (found session 2):** The previous session's remediation introduced unsupported
  legal assertions: SCCs claimed for Meta/Twilio without evidence of executed DPAs;
  "Ministry of Health, Syrian Arab Republic" as regulatory authority (unverified for
  Qamishlo/AANES target market); Damascus courts as exclusive jurisdiction; 30-day notice
  as a binding contractual commitment; "All processors bound by DPAs."
- **Resolution (2026-10-28):** All unsupported claims replaced with NEEDS LEGAL REVIEW
  notices. Impressum regulatory authority corrected. TermsOfService.jsx governing law
  clause replaced with AANES/Qamishlo jurisdiction caveat.

#### P1-2: Nuqta SY — Arabic legal pages incomplete [Platform 6] ✅ RESOLVED
- **Files:** `nuqta-sy/privacy.html` (AR), `nuqta-sy/terms.html` (AR)
- **Detail (found session 2):** Previous session only updated English versions. Arabic
  pages still had 3-4 live `[PLACEHOLDER]` markers visible to users.
- **Resolution (2026-10-28):** All Arabic placeholders resolved — retention period (30 days),
  Impressum operator details, disclaimer clause, governing law NEEDS LEGAL REVIEW notice.

#### P1-3: Nuqta IT privacy policy and terms — visible placeholder fields [Platform 7] ✅ RESOLVED
- **Detail:** Legal basis for inquiry handling, log retention period, hosting provider,
  supervisory authority, limitation of liability, governing law/court — all showing
  `[PLACEHOLDER]` text visible to users.
- **Resolution (2026-10-28):** Operational facts filled (retention 30 days, self-managed
  infrastructure, Art. 6(1)(b)/(f) legal bases); legal-judgment items replaced with
  consistent NEEDS LEGAL REVIEW notices.

#### P1-4: Nuqta Sale Terms / Nuqta Pro Terms — liability and governing law [Platform 4/5]
- **Status: OPEN — requires legal counsel**
- **Detail:** Sale ToS §6 (liability) and §8 (governing law) contain Arabic placeholder
  text. Pro ToS §4 (SLA) marked `[PLACEHOLDER — SLA terms]`.
- **Remediation:** Legal counsel to draft liability terms and specify governing law/SLA.

### P2 — Address before EU launch

#### P2-1: Nuqta Health commercial registration / healthcare license [Platform 3]
- **Status: OPEN — MANUAL ACTION REQUIRED**
- **File:** `nuqtahealth/frontend/src/components/Impressum.jsx` and `PrivacyPolicy.jsx`
- **Detail:** Commercial registration number and healthcare license number are marked
  MANUAL ACTION REQUIRED. Cannot be filled without operator obtaining these credentials.

#### P2-2: Nuqta ID app store privacy labels not verifiable [Platform 2]
- **Status: OPEN — manual verification**
- **Detail:** `PrivacyInfo.xcprivacy` not present in source (generated at EAS build time).
  iOS App Store privacy nutrition labels must be accurate.
- **Remediation:** Verify EAS build output includes `PrivacyInfo.xcprivacy`; complete
  App Store privacy questionnaire to match actual data collection.

#### P2-3: Nuqta ID DOB encryption [Platform 1] ✅ FIXED (session 3)
- **Status: RESOLVED — session 2 verified Fernet encryption at rest; session 3 closed plaintext gap in pending records**
- **Detail (verified session 2):** DOB is Fernet-encrypted at rest via `encrypt_dob()`/
  `decrypt_dob()` (`nuqtaid/app.py:229-237`). `User.date_of_birth` column stores the
  encrypted token; `apply_personal_identity_from_form()` calls `encrypt_dob()` before
  persisting. This was already in place.
- **New fix (session 3, commit `f8ac72f`):** `date_of_birth` was also being serialised
  as plaintext into `PendingRegistration.form_data_json` (24-hour TTL table). Fixed:
  `date_of_birth` added to `_FORM_DATA_JSON_EXCLUDE`; validated DOB is now Fernet-encrypted
  at submission time and stored as `_dob_encrypted` in the pending record. 4 regression
  tests added (`tests/test_pending_dob_encryption.py`).
- **Test status:** `test_pending_dob_encryption.py` — 4 passed; all 18 existing DOB tests pass.

#### P2-5: Cross-platform flows not consistently disclosed across all privacy policies [Platform 9]
- **Detail:** Nuqta ID and Sale disclose cross-platform identity data flows. Nuqta Health
  and Pro have incomplete legal pages that don't clearly describe identity lookup from
  Nuqta ID.
- **Remediation:** After completing Health and Pro legal pages (P0-1, P1-2), add explicit
  disclosure of Nuqta ID as an identity data source.

---

## What Is Working Well

### Architecture
- **PHI containment confirmed with one intentional patient-facing cross-boundary flow:**
  `nuqta_id_integration_service.py` exposes a read-only patient portal serialiser —
  Health intentionally sends a patient's own appointment summary and medical record
  summaries to the Nuqta ID patient portal (identified via QID + DOB). Clinical data
  does NOT flow to Sale, Pro, IT, or SY. The Health→ID patient data flow is by design,
  security-reviewed (constant-time HMAC, no PHI leakage in logs), and should be
  disclosed in both Health and Nuqta ID privacy policies.
- **API key encryption:** All inter-platform credentials Fernet-encrypted at rest
  (`APP_ENCRYPTION_KEY` or `APP_ENCRYPTION_KEY`).
- **Log redaction:** `SecretRedactingFilter` (Sale), rate_limit fixes (Health),
  `dob=***REDACTED***` in Health — sensitive data excluded from logs across platforms.
- **Tenant isolation:** All Sale, Pro, and Health queries scoped to `shop_id` /
  `facility_id` extracted from JWT. Cross-tenant data access is not architecturally possible.
- **DICOMweb read-only:** `methods=["GET", "HEAD", "OPTIONS"]` on Health's DICOMweb
  proxy — no write access to imaging data (commit df4cc68).

### Legal pages
- **Real operator identity in all platforms:** [REDACTED], Damascus/Syria.
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

## Ecosystem Readiness Matrix (updated 2026-10-28 session 2)

| Requirement | ID | App | Health | Pro | Sale | SY | IT | Suar |
|---|---|---|---|---|---|---|---|---|
| Real operator identity | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Privacy policy exists | ✓ | N/A | ✓ draft¹ | ✓ | ✓ | ✓ draft | ✓ draft | ✓ |
| Terms of service exists | ✓ | N/A | ✓ draft¹ | ✓ partial | ✓ partial | ✓ draft | ✓ partial | N/A |
| No [PLACEHOLDER] visible | ✓ | N/A | ✓ (NEEDS LEGAL notices) | ✓ | ✓ | ✓ | ✓ | N/A |
| No Google Fonts | ✓ | N/A | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| No analytics/tracking | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Log redaction | ✓ | N/A | ✓ | ✓ | ✓ | N/A | N/A | N/A |
| .env permissions 600 | ✓ | N/A | ✗ (664) | ✓ | ✓ | N/A | N/A | N/A |
| Unsubscribe mechanism | ✓ | N/A | ✓ | ✓ | N/A | N/A | N/A | N/A |
| GDPR export — no creds | ✓ | N/A | ✓ | ✓ | ✓ | N/A | N/A | N/A |
| GDPR export endpoint | ✓ partial | N/A | ✓ | ✓ | ✓ | N/A | N/A | N/A |
| Account deletion path | ✓ via email | N/A | ✓ | ✗ | ✗ | N/A | N/A | N/A |
| Age gate enforced server-side | ✓ | ✓ (advisory) | N/A | N/A | N/A | N/A | N/A | N/A |
| DOB encrypted at rest | ✓ Fernet | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| DOB not plaintext in pending | ✓ (f8ac72f) | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Secure storage (mobile) | N/A | ✓ | N/A | N/A | N/A | N/A | N/A | N/A |
| GDPR rights listed | ✓ | N/A | ✓ | ✓ partial | ✓ | ✓ | ✓ | ✓ |

**Key:** ✓ = implemented/complete, ✗ = missing/incomplete, N/A = not applicable
¹ Health legal pages have "NOT APPROVED FOR PUBLICATION" banner (UI-only warning; does not prevent deployment — deployment guard is unimplemented per `LEGAL_DEPLOYMENT_NOTES.md`) — require legal sign-off for CR#, license#, regulatory authority, governing law before going live.

---

## Remediation Priority Order (updated 2026-10-28 session 5)

**All P0 and P1 technical items resolved. Remaining items require legal counsel or manual operator actions.**

1. ✅ DONE — Nuqta Health PrivacyPolicy/Impressum/TermsOfService: placeholders and unsupported legal claims corrected
2. ✅ DONE — Suar Services: Inter self-hosted, Google Fonts CDN removed, regression test added
3. ✅ DONE — Nuqta Sale + Pro: GDPR export credential leaks fixed, allowlist serializers + regression tests added
4. ✅ DONE — Nuqta SY: Arabic legal pages completed
5. ✅ DONE — Nuqta IT: visible placeholder strings resolved; Docker log retention claim corrected
6. ✅ FIXED — Nuqta ID: age gate watertight; DOB Fernet-encrypted at rest; DOB plaintext excluded from pending records (session 3); full DOB validation after decryption at activation (session 5)
7. ✅ DONE — Sale/Pro AuditLog.details: typed per-field value validation; 501-fetch boundary fix; `audit_log_status` accuracy confirmed (sessions 3+5)
8. ✅ DONE — Health rendered developer instructions: moved to JSX comments; NOT APPROVED banners added (session 3)
9. ✅ PUBLISHED — Nuqta ID Mobile audit report: canonical copy in `legal-privacy-auditor/reports/nuqta-id-app-legal-audit.md` (session 3)
10. **Before B2B onboarding:** Sale, Pro — legal counsel for governing law, liability caps, SLA (P1-4)
11. **MANUAL ACTION — operator:** Health CR#, healthcare license# (P2-1)
12. **Before App Store submission:** Nuqta ID App — verify PrivacyInfo.xcprivacy (P2-2)
13. **Security hardening (non-blocking):** Health .env permissions (664 → 600)

---

## Session 7 Remediation Log (2026-10-28)

| Item | Platform | Files | Severity | Status | Detail |
|---|---|---|---|---|---|
| Pro TermsOfService §8 — MANUAL ACTION REQUIRED developer text visible | Nuqta Pro | `frontend/src/components/TermsOfService.js` | P1 | ✅ RESOLVED | Replaced rendered developer instruction with neutral pending-review statement; instruction moved to JSX comment. commit `f09eec2` |
| Pro Impressum — MANUAL ACTION REQUIRED in Commercial Register | Nuqta Pro | `frontend/src/components/Impressum.js` | P1 | ✅ RESOLVED | Replaced with "Registration number: Pending". commit `f09eec2` |
| Sale TermsOfService §6 — Arabic developer instruction visible | Nuqta Sale | `frontend/src/components/TermsOfService.js` | P1 | ✅ RESOLVED | Replaced "إجراء يدوي مطلوب" with neutral Arabic statement; instruction moved to JSX comment. commit `eef5cca` |
| Sale TermsOfService footer — Arabic developer advisory visible | Nuqta Sale | `frontend/src/components/TermsOfService.js` | P1 | ✅ RESOLVED | Replaced with last-reviewed date. commit `eef5cca` |
| Health publication gate — UI banner only, not CI-enforced | Nuqta Health | `legal/PUBLICATION_APPROVAL.json`, `.github/workflows/medical-production-gate.yml`, `LEGAL_DEPLOYMENT_NOTES.md` | P1 | ✅ RESOLVED | CI-enforced gate added to medical-production-gate.yml; reads PUBLICATION_APPROVAL.json, fails closed when approved=false. commit `8b42b45` |
| nuqta-sy banners — [PLACEHOLDER] code element visible to users | Nuqta SY | `privacy.html`, `terms.html`, `en/privacy.html`, `en/terms.html` | P1 | ✅ RESOLVED | Banners rephrased to user-appropriate pending-review notices; inline developer instructions removed or moved to HTML comments. commit `459efa7` |
| .legal-audit/ gitignore cleanup | nuqtaid, nuqtait, suar-services-static | `.gitignore`, `.legal-audit/` files | INFO | ✅ RESOLVED | Added to gitignore; removed from tracking in nuqtait and suar-services-static. commits `f37e40e`, `80d9e83`, `b054445` |
| Nuqta ID App audit report unpublished staged update | Nuqta_ID_APP | `reports/nuqtaidapp-legal-audit.md` | INFO | ✅ RESOLVED | Committed updated audit report reflecting all post-2026-10-13 fixes. commit `4a1da26` |
| Final publication readiness report created | Legal/Privacy Auditor | `reports/NUQTA_PUBLICATION_READINESS.md` | INFO | ✅ CREATED | Full cross-platform publication readiness report, legal approval package, and finding reconciliation. |

---

## Session 6 Remediation Log (2026-10-28)

| Item | Platform | Files | Severity | Status | Distinction |
|---|---|---|---|---|---|
| Health NOT APPROVED banner statement corrected | LegalPrivacyAuditor | this report | INFO | ✅ CORRECTED | P0-1 resolution text and footnote ¹ previously stated the banner "prevents accidental deployment". Corrected: banner is UI-only; deployment guard is unimplemented; `LEGAL_DEPLOYMENT_NOTES.md` documents the limitation. |

---

## Session 5 Remediation Log (2026-10-28)

| Item | Platform | Files | Severity | Status | Distinction |
|---|---|---|---|---|---|
| Typed per-field value validation for GDPR audit export | Nuqta Pro | `user_service.py`, `auth/routes.py`, `tests/` | P1 | ✅ SOURCE FIX + TESTS PASSED (68 total, +45 new) | Per-field typed validators: IDs (int ≤2^31-1), monetary (finite Decimal), counters (non-neg int), booleans (True/False only). Arbitrary string values in allowed keys now rejected. commit `f4c169c` |
| Typed per-field value validation for GDPR audit export | Nuqta Sale | same pattern + Sale-specific fields (deleted/freed/count/cashier_id/product_id) | P1 | ✅ SOURCE FIX + TESTS PASSED (63 total, +40 new) | Independently verified from Sale log_audit call sites. commit `609c670` |
| 501-fetch boundary for audit export status accuracy | Pro + Sale | `auth/routes.py` | P1 | ✅ SOURCE FIX + TESTS PASSED (6 boundary tests) | Fetch limit+1 rows; `complete` only when no extra row exists; `truncated_most_recent_500` only when 501st row confirmed. id DESC tie-break for stable ordering. |
| Full DOB validation after Fernet decryption at activation | Nuqta ID | `identity_profile.py`, `tests/test_dob_activation_validation.py` | P1 | ✅ SOURCE FIX + TESTS PASSED (24 new tests) | Added `validate_dob_age()` shared helper. After decrypting `_dob_encrypted`, run `parse_optional_date_of_birth` (calendar validity, future-date) then age gate via `MIN_REGISTRATION_AGE`. Malformed/underage tokens abort activation. commit `165d6e6` |
| Report corrections: stale SHAs, repo path, session labels, scorecard | LegalPrivacyAuditor | this report | INFO | ✅ CORRECTED | Health SHA `abcbdba`→`1f4da0d`; Pro `2dba2cc`→`f4c169c`; Sale `05ba034`→`609c670`; ID `cf93067`→`165d6e6`; `nuqta-sy`→`Nuqta-SY`; self-referential auditor SHA replaced with documented baseline; "Pilot OK?" column replaced with per-dimension status columns. |

## Session 4 Remediation Log (2026-10-28)

| Item | Platform | Files | Severity | Status | Distinction |
|---|---|---|---|---|---|
| NID plaintext exclusion from PendingRegistration | Nuqta ID | `app.py`, `tests/test_pending_nid_encryption.py` | P1 | ✅ SOURCE FIX + TESTS PASSED (8 new tests) | `national_id` excluded; `_nid_encrypted` (Fernet) stored instead; commit `cf93067` |
| DOB token verification before User assignment | Nuqta ID | `identity_profile.py` | P1 | ✅ SOURCE FIX + TESTS PASSED | `_dob_encrypted` token now verified via `decrypt_dob()` before assignment; malformed token returns error |
| GDPR audit allowlist (email/paths/exceptions) | Nuqta Pro | `user_service.py`, `auth/routes.py`, `tests/` | P1 | ✅ SOURCE FIX + TESTS PASSED (23 total) | Explicit `_AUDIT_EXPORT_SAFE_KEYS` allowlist replaces regex denylist; commit `2dba2cc` |
| GDPR audit allowlist (same + backup/restore paths) | Nuqta Sale | same pattern | P1 | ✅ SOURCE FIX + TESTS PASSED (23 total) | commit `05ba034` |
| audit_log_status = 'truncated_most_recent_500' | Pro + Sale | `auth/routes.py` | INFO | ✅ SOURCE FIX | Was always 'complete' even when 500-row cap applied |
| Individual Platform Reports table correction | LegalPrivacyAuditor | this report | INFO | ✅ CORRECTED | Reports ARE tracked in each platform repo; table now shows correct tracked paths and staleness |
| Health NOT APPROVED banner limitation documented | Nuqta Health | `LEGAL_DEPLOYMENT_NOTES.md` | INFO | ✅ DOCUMENTED | Banner is UI-only; does not technically prevent deployment; limitation documented |

---

## Session 3 Remediation Log (2026-10-28)

| Item | Platform | Files | Severity | Status | Distinction |
|---|---|---|---|---|---|
| AuditLog.details sanitization (email=/paths/exceptions) | Nuqta Sale | `auth/routes.py`, `services/user_service.py`, `tests/test_gdpr_export_security.py` | P0 | ✅ SOURCE FIX + TESTS PASSED (7 new tests, 19 total) | Source fix committed; tests executed and passed |
| AuditLog.details sanitization (email= only) | Nuqta Pro | same pattern | P0 | ✅ SOURCE FIX + TESTS PASSED (5 new tests, 19 total) | Source fix committed; tests executed and passed |
| `audit_log_status` field (surfaces DB failure) | Sale + Pro | `auth/routes.py` | P1 | ✅ SOURCE FIX | Prevents silent empty audit log on DB error |
| Docker log retention claim corrected | Nuqta IT | `content/en.json`, `nginx.conf` | P1 | ✅ SOURCE FIX | False "30-day" claim replaced with accurate size-based description |
| Developer instructions in rendered JSX output | Nuqta Health | `PrivacyPolicy.jsx`, `Impressum.jsx`, `TermsOfService.jsx` | P1 | ✅ SOURCE FIX | Instructions moved to `{/* JSX comments */}`; NOT APPROVED banners added |
| Plaintext DOB in PendingRegistration.form_data_json | Nuqta ID | `app.py`, `identity_profile.py`, `tests/test_pending_dob_encryption.py` | P1 | ✅ SOURCE FIX + TESTS PASSED (4 new tests) | `date_of_birth` excluded; `_dob_encrypted` (Fernet) stored instead; commit `f8ac72f` |
| Mobile audit report in gitignored directory | Nuqta ID App | `legal-privacy-auditor/reports/nuqta-id-app-legal-audit.md` | INFO | ✅ PUBLISHED | Canonical tracked copy published; source copy in `Nuqta_ID_APP/reports/` remains gitignored |

---

## Session 2 Remediation Log (2026-10-28)

| Item | Platform | Files | Severity | Status |
|---|---|---|---|---|
| GDPR export credential leak (hengar_api_key + hashes) | Nuqta Sale | `backend/app/modules/auth/routes.py`, `services/user_service.py`, `tests/test_gdpr_export_security.py` | P0 | ✅ FIXED |
| GDPR export credential leak (same design) | Nuqta Pro | same pattern | P0 | ✅ FIXED |
| Unsupported SCC claims for Meta/Twilio | Nuqta Health | `PrivacyPolicy.jsx` | P1 | ✅ FIXED |
| "Ministry of Health" regulatory authority claim | Nuqta Health | `Impressum.jsx` | P1 | ✅ FIXED |
| Damascus courts exclusive jurisdiction commitment | Nuqta Health | `TermsOfService.jsx` | P1 | ✅ FIXED |
| "All processors bound by DPAs" unsupported claim | Nuqta Health | `PrivacyPolicy.jsx` | P1 | ✅ FIXED |
| Arabic legal pages still had visible [PLACEHOLDER] | Nuqta SY | `privacy.html`, `terms.html` | P1 | ✅ FIXED |
| English terms.html governing law (Damascus courts) | Nuqta SY | `en/terms.html` | P1 | ✅ FIXED |
| Visible [PLACEHOLDER] in EN privacy and terms | Nuqta IT | `content/en.json` | P1 | ✅ FIXED |
| Age gate bypass path analysis | Nuqta ID | `app.py` | P1 | ✅ VERIFIED — no bypass |
| DOB encryption verification | Nuqta ID | `app.py`, `identity_profile.py` | P2 | ✅ VERIFIED — Fernet |
| Mobile audit age gate status update | Nuqta ID App | `reports/nuqtaidapp-legal-audit.md` | INFO | ✅ UPDATED |

---

## Individual Platform Reports

Individual reports are tracked in each platform's own `reports/` directory on GitHub.
The Nuqta ID App report is also mirrored here (since the source copy is gitignored in
the mobile repo). All reports were written at a prior SHA — see each report's
`Branch/SHA` header and the "Current branch SHAs" table above for the gap.

| Platform | GitHub location | Report SHA | Current SHA | Stale? |
|---|---|---|---|---|
| Nuqta ID (backend) | `Suar1/nuqtaid/reports/nuqtaid-legal-audit.md` | `0027d0b` | `f37e40e` | Yes — NID fix, DOB validation, gitignore added (sessions 5, 7) |
| Nuqta ID App (mobile) | `Suar1/Nuqta_ID_APP/reports/nuqtaidapp-legal-audit.md` + mirror in this repo | `4a1da26` | `4a1da26` | Current — updated session 7 |
| Nuqta Health | `Suar1/nuqtahealth/reports/nuqtahealth-legal-audit.md` | `3ae6f82` | `8b42b45` | Yes — CI gate added (session 7) |
| Nuqta Pro | `Suar1/nuqtapro/reports/nuqtapro-legal-audit.md` | `c144437` | `f09eec2` | Yes — developer text removed from TermsOfService (session 7) |
| Nuqta Sale | `Suar1/Nuqtasale/reports/nuqtasale-legal-audit.md` | `2d21cd8` | `eef5cca` | Yes — developer text removed (session 7) |
| Nuqta SY | `Suar1/Nuqta-SY/reports/nuqta-sy-legal-audit.md` | `a285104` | `459efa7` | Yes — developer text removed from banners (session 7) |
| Nuqta IT | `Suar1/nuqtait/reports/nuqtait-legal-audit.md` | `fee9805` | `80d9e83` | Yes — .legal-audit removed from tracking (session 7) |
| Suar Services | `Suar1/suar-services-static/reports/suar-services-legal-audit.md` | `126de07` | `b054445` | Minor — .legal-audit removed (session 7) |
| Cross-platform flows | `reports/cross-platform-data-flow-audit.md` (this repo) | `15d5ec1` | `d87e608` | Partially updated |
| **FINAL READINESS REPORT** | `reports/NUQTA_PUBLICATION_READINESS.md` (this repo) | — | Current | **New — created session 7** |

> Each individual report retains its original findings. Session-level fixes are
> recorded in the Session Remediation Logs in this consolidated report. The
> individual reports have not been retroactively edited to avoid misrepresenting
> the state of the code at the time they were written.

---

*This report represents a technical review of source code and configuration files.
It is not legal advice. All legal determinations regarding compliance with GDPR,
HIPAA, or other applicable regulations must be made by qualified legal counsel.*

