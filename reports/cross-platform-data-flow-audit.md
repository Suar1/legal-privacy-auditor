# Nuqta Ecosystem — Cross-Platform Data Flow Audit
**Audit date:** 2026-10-28  
**Auditor:** Claude (LegalPrivacyAuditor v1 framework — manual cross-platform review)  
**Scope:** All data flows between Nuqta ecosystem platforms; disclosure consistency across privacy policies

---

## Summary

| Finding | Severity | Status |
|---|---|---|
| Health privacy policy has unfilled [PLACEHOLDER] values | CRITICAL | **RESOLVED 2026-10-28** |
| Nuqta ID ↔ Health PHI data minimisation | INFO | ADEQUATE |
| Nuqta ID → Sale/Pro customer data fetch | INFO | ADEQUATE |
| Cross-platform disclosure consistency | MEDIUM | **SUBSTANTIALLY IMPROVED 2026-10-28** |
| ID admin settings reference Health integration (placeholder only) | INFO | NOT ACTIVE |
| Nuqta ID age gate bypass (DOB not required server-side) | CRITICAL | **RESOLVED 2026-10-28** |
| GDPR Art. 20 data portability — Pro and Sale have no export endpoint | MEDIUM | **RESOLVED 2026-10-28** |
| Suar Services loads Inter font via Google Fonts CDN | MEDIUM | **RESOLVED 2026-10-28** |

---

## Confirmed Data Flows

### Flow 1: Nuqta Health → Nuqta ID (patient registration/linking)
**Direction:** Health reads from ID  
**Service:** `nuqtahealth/backend/app/services/qid_client_service.py`  
**Trigger:** Facility staff searches for a patient using their Nuqta ID public identifier  
**Data fetched from ID:**
```
id, name, first_name, last_name, email, phone, street, city, postal_code,
country, date_of_birth, gender, national_id
```
**Auth:** Bearer token (QID API key, Fernet-encrypted in `AdminSettings.qid_api_key_encrypted`)  
**Privacy assessment:**
- Data fetched is used to pre-fill a patient record — minimised to the `QID_MINIMAL_PRESET_FIELDS` tuple
- DOB is fetched (and used for QR PIN double-factor auth) but redacted in logs (`dob=***REDACTED***`)
- National ID is fetched but stored separately from clinical records
- No health data sent to Nuqta ID in this flow

### Flow 2: Nuqta ID (App) → Nuqta Health (patient's own records)
**Direction:** Nuqta Health exposes an endpoint that Nuqta ID Mobile App calls on behalf of the patient  
**Service:** `nuqtahealth/backend/app/services/nuqta_id_integration_service.py`  
**Trigger:** Patient using the Nuqta ID Mobile App views their health summary  
**Data returned:**
- Medications (filtered by patient-portal visibility rules)
- Appointments (public fields only; clinical notes `notes` field stripped)
- Activity timeline
- Health summary
**Auth:** `NUQTA_ID_INTEGRATION_TOKEN` bearer — verifies the caller is Nuqta ID (not the patient directly)  
**Privacy assessment:**
- Critical privacy design: only patient-portal-visible data is returned
- The module explicitly documents that a field the portal wouldn't show cannot appear here
- No scope/role/override parameter — patient sees their own safe view and nothing more
- Clinical records of OTHER patients cannot be accessed through this flow
- Health → ID: no PHI sent back to Nuqta ID; data is only served to the patient

### Flow 3: Nuqta Sale → Nuqta ID (loyalty linking)
**Direction:** Sale reads from ID  
**Service:** `Nuqtasale/backend/app/services/nuqta_id_client_service.py`  
**Trigger:** Cashier links a shop customer to their Nuqta ID for loyalty program  
**Data fetched from ID:**
```
public_id, full_name, email, phone
```
**Auth:** Bearer token (Nuqta ID API key, Fernet-encrypted in `AdminSettings.nuqta_id_api_key_encrypted`)  
**Privacy assessment:**
- Minimal data fetched: only 4 fields needed for loyalty linking
- Sale stores a local customer snapshot and owns all loyalty data
- This service never writes to Nuqta ID (confirmed in module docstring)
- Dev bypass: `ALLOW_UNVERIFIED_NUQTA_ID_LINKING=true` — must be `false` in production

### Flow 4: Nuqta ID → Nuqta Pro (loyalty data)
**Direction:** Nuqta ID reads loyalty summary/events from Pro  
**Service:** `nuqtapro/backend/app/modules/integrations/routes.py`  
**Endpoints:** `GET /api/integrations/nuqta-id/loyalty/summary`, `/loyalty/events`  
**Trigger:** Nuqta ID Mobile App queries Pro for a user's loyalty status  
**Data returned:** loyalty points summary and event history for the user's QID reference  
**Auth:** `require_nuqta_id_token` decorator — Pro validates the incoming token is Nuqta ID  
**Privacy assessment:**
- Returns only loyalty data scoped to the specific `nuqta_id_reference`
- No customer PII returned beyond what is needed for loyalty display
- Queries filtered by `qid_public_id` match (`Customer.qid_public_id.ilike(...)`)

### Flow 5: Nuqta Pro → Nuqta ID (customer linking)
**Direction:** Pro reads from ID  
**Service:** `nuqtapro/backend/app/services/qid_client_service.py` (same pattern as Health)  
**Trigger:** Shop owner links a customer to their Nuqta ID  
**Data fetched:** same minimal preset (name, email, phone, public_id)  
**Privacy assessment:** Same as Flow 3 assessment

---

## Non-Existent Flows (Confirmed by Code Review)

| Claimed flow | Status |
|---|---|
| Nuqta ID → Nuqta Health (ID pushing data to Health) | NOT ACTIVE — admin config placeholder only, no outbound HTTP calls |
| Nuqta Health → Nuqta Sale / Pro | NO code found |
| Nuqta Sale → Nuqta Health | NO code found |
| Nuqta IT / Nuqta SY ↔ any other platform | NOT APPLICABLE — static sites |
| Zanist ↔ any Nuqta platform | No integration code found |
| Suar Services ↔ any Nuqta platform | NOT APPLICABLE — static site |

Clinical (PHI) data never crosses between platforms. Health's clinical records stay in Health.

---

## Privacy Policy Disclosure Consistency

| Platform | Mentions cross-platform flows | Detail |
|---|---|---|
| Nuqta ID | YES | "خدمات منظومة نقطة قد تتبادل بيانات تعريف محددة من خلال واجهات تكامل وصلاحيات مناسبة" |
| Nuqta Health | YES — **PLACEHOLDERS RESOLVED 2026-10-28** | PrivacyPolicy.jsx, Impressum.jsx, TermsOfService.jsx — all verifiable `[PLACEHOLDER]` values filled; unresolvable items marked MANUAL ACTION REQUIRED |
| Nuqta Pro | **IMPROVED 2026-10-28** | TermsOfService.js, Impressum.js, PrivacyPolicy.js all updated; SLA/liability cap marked MANUAL ACTION REQUIRED; log retention corrected to 14×20 MB |
| Nuqta Sale | YES | PrivacyPolicy.js lists Nuqta ID as a processor |
| Nuqta SY | YES | Explicitly states each sub-platform has its own policy |
| Nuqta IT | N/A | No cross-platform integration |
| Suar Services | N/A | No cross-platform integration |

**SUBSTANTIALLY IMPROVED (2026-10-28):** Nuqta Health's `PrivacyPolicy.jsx`, `Impressum.jsx`, and `TermsOfService.jsx` all had `[PLACEHOLDER]` values resolved in this session. All verifiable facts (operator name, address, GDPR lawful basis, transfer safeguards for Meta/Twilio using SCCs Art. 46(2)(c), supervisory authority text, Bunny Fonts CDN note) were filled. Items requiring manual legal action (CR number, regulatory license number, liability cap) are explicitly marked "MANUAL ACTION REQUIRED" in the file. Nuqta Pro and Nuqta Sale legal pages similarly updated. Nuqta SY static HTML privacy/terms pages completed.

---

## Data Flow Privacy Evaluation

### Lawful basis for cross-platform transfers
- **Health ← ID (Flow 1):** Legitimate interest / performance of healthcare service. Patient provides their QID public identifier to the facility; the facility looks up identity information needed for record creation.
- **ID ← Health (Flow 2):** Patient's own data access right. The patient requests their own health summary via the Nuqta ID app. Basis: data subject's own request.
- **Sale ← ID (Flow 3):** Performance of loyalty service / legitimate interest. Customer provides QID for loyalty linking.
- **ID ← Pro (Flow 4):** Same as Flow 2/3 pattern — loyalty data for the individual.

### PHI containment
- All clinical records stay within Nuqta Health. No PHI flows to ID, Pro, Sale, IT, or SY.
- The `nuqta_id_integration_service.py` design explicitly prevents clinical data leakage by only using patient-portal serialisers.
- The comment "A field the portal would not show a patient cannot appear here" is a robust design principle.

### API key security
- Nuqta ID API keys in Health, Sale, Pro: all Fernet-encrypted in `AdminSettings` table
- Service tokens (Health→ID integration, ID←Pro integration): loaded from `NUQTA_ID_INTEGRATION_TOKEN` config key, never logged, never returned

### Audit logging
- Nuqta Health QR access has full audit logging (`modules/qr/routes.py`)
- JWT security events logged to `security.log` in all backend platforms
- Cross-platform API calls are not specifically audit-logged beyond standard request logs

---

## Findings

### ~~CRITICAL~~ RESOLVED (2026-10-28) — Health privacy policy placeholders
Nuqta Health's `frontend/src/components/PrivacyPolicy.jsx`, `Impressum.jsx`, and
`TermsOfService.jsx` had unfilled `[PLACEHOLDER]` markers for operator identity, commercial
registration number, regulatory authority, VAT number, transfer safeguards, and SLA terms.

**Resolution:** All verifiable facts filled 2026-10-28:
- Operator: [REDACTED], Damascus, Syria; email: info@nuqta.health
- Regulatory authority: Ministry of Health, Syrian Arab Republic
- VAT/Tax ID: Not applicable — operator based in Syria, outside EU/EEA
- Third-party transfers: Meta (WhatsApp Business API) and Twilio (SMS) — transfer safeguard: Standard Contractual Clauses, Art. 46(2)(c) GDPR
- Governing law: Syrian Arab Republic / Damascus courts; 30-day notice period for material changes
- MANUAL ACTION REQUIRED items remaining: CR/HRB number, regulatory license/permit number, liability cap

Full details in the Nuqta Health audit report.

### MEDIUM → SUBSTANTIALLY IMPROVED (2026-10-28) — Cross-platform data flows disclosure
Nuqta ID's privacy policy has the best disclosure of cross-platform data sharing.
Nuqta Sale explicitly lists Nuqta ID as a processor. Nuqta Pro and Nuqta Health's
legal pages were incomplete.

**Resolution (2026-10-28):** Nuqta Health, Pro, Sale, and SY legal pages updated with
operator identity, lawful basis, data categories, and governing law. Remaining gap:
no platform's privacy policy yet explicitly names Nuqta ID as an identity data *source*
with the specific trigger event phrasing ("when a facility links your patient record…").
This should be addressed in the next legal review cycle.

**Residual remediation needed:** Each platform's privacy policy should explicitly name
Nuqta ID as an identity data source (where applicable) and describe the data exchanged
and the trigger event (e.g., "when a facility links your patient record to your Nuqta ID").

### INFO — Dev bypass flag in Nuqta Sale
`Nuqtasale/backend/app/services/nuqta_id_client_service.py`: `ALLOW_UNVERIFIED_NUQTA_ID_LINKING=true`
skips live ID verification. Documented as "Never set to true in production." Should
be verified to be `false` before launch.

### INFO — Nuqta ID admin has Health integration config but no active integration
Nuqta ID stores `nuqta_health_enabled`, `nuqta_health_base_url`, `nuqta_health_token_encrypted`
in `admin_config` but these are never consumed in HTTP calls within the Nuqta ID codebase.
The page is named `admin_nuqta_health_placeholder`. This config is likely reserved for a
future integration direction. No privacy risk from this placeholder.

---

## Architecture Verdict

The cross-platform integration architecture follows good privacy principles:
1. **Minimal data fetching** — only the fields needed for each integration are fetched
2. **PHI containment** — clinical records do not cross platform boundaries
3. **Patient control** — patient sees their own data; facilities cannot access clinical
   records of unlinked patients
4. **API key encryption** — all inter-platform credentials are Fernet-encrypted at rest
5. **Independent privacy policies** — each platform has its own policy as appropriate

The documentation completeness gap is substantially closed as of 2026-10-28. Remaining
pre-launch manual items: commercial registration numbers, regulatory license numbers,
explicit Nuqta ID disclosure in each platform's privacy policy, and liability cap amounts
(all marked "MANUAL ACTION REQUIRED" in source files).

---

## Remediation Log — 2026-10-28

The following changes were made during the 2026-10-28 legal/privacy remediation session:

### 1. Nuqta Health — legal placeholder resolution
- **`PrivacyPolicy.jsx`**: Filled Nuqta ID server location (Syria, self-hosted); Meta WhatsApp Business API transfer safeguard (SCCs Art. 46(2)(c) GDPR); Twilio SMS transfer safeguard (SCCs Art. 46(2)(c) GDPR); supervisory authority text (non-EU operator, reference EDPB member list); GDPR Art. 9(2)(a)/(h) lawful bases. Kept as MANUAL ACTION REQUIRED: CR number, DPO/representative, supervisory authority name.
- **`Impressum.jsx`**: Filled regulatory authority (Ministry of Health, Syrian Arab Republic); VAT/Tax ID (not applicable — operator in Syria); healthcare/informational disclaimer. Kept as MANUAL ACTION REQUIRED: CR/HRB number, registering authority, license/permit number.
- **`TermsOfService.jsx`**: Filled health data law reference (Syrian health law + GDPR for international users); governing law (Syrian Arab Republic / Damascus courts); 30-day material change notice. Kept as MANUAL ACTION REQUIRED: subscription agreement link, liability cap.
- **`nuqta_id_integration_service.py`**: Security review — no defects found. Verified: constant-time HMAC token comparison, linkage-only patient resolution, clinical notes stripped, activity feed sends pointers only, audit log records categories/counts not contents.
- **Commit:** `346d865` on `main`

### 2. Suar Services Static — Google Fonts CDN removal
- **`site/tools/shared-header.mjs`**: Removed 3 Google Fonts CDN `<link>` tags from `renderHeaderAssets()`. All 300+ generated HTML pages now load Inter from self-hosted WOFF2 files only.
- **`site/assets/css/fonts.css`**: Added 8 Inter `@font-face` declarations (weights 400/500/600/700, latin + latin-ext subsets, unicode-range from `@fontsource/inter` v5).
- **`site/assets/fonts/`**: Added 7 Inter WOFF2 files (~24–36 KB each) plus `OFL-Inter.txt` license.
- **`site/tools/validate-navigation.cjs`**: Removed `fonts.googleapis.com` / `fonts.gstatic.com` from external-resource allowlist; any Google Fonts re-introduction now fails the Playwright test.
- **`render-site.mjs`**: Regenerated all 300+ HTML pages (96 updated, 4 already clean).
- **Commit:** `5ee805d` on `main`

### 3. Nuqta ID — age gate bypass closure
- **`app.py` (line ~5402)**: Changed conditional `if raw_dob:` age check to unconditionally require DOB at registration. Missing or empty DOB now returns HTTP 422 with `field='date_of_birth'` error.
- **`tests/test_age_gate_enforcement.py`** (NEW): 5 regression tests — missing DOB rejected, empty DOB rejected, underage rejected, valid adult passes, `MIN_REGISTRATION_AGE` env override respected. All 5 pass.
- **`Nuqta_ID_APP/reports/nuqtaidapp-legal-audit.md`**: Updated audit to mark server-side age gate gap as FIXED.
- **Commit:** `52639b6` on `main`

### 4. Nuqta Pro — GDPR Art. 20 export + legal page cleanup
- **`backend/app/modules/auth/routes.py`**: Added `GET /api/auth/user/gdpr-export` endpoint. Rate-limited 3/hour. Returns JSON download (`nuqtapro-my-data.json`) with profile + last-500 audit log entries. Logs `GDPR_DATA_EXPORT` AuditLog entry. Auth: `@jwt_required()`.
- **`frontend/src/components/TermsOfService.js`**: Filled SLA (no guarantee at this stage), governing law (Syrian Arab Republic / Damascus courts), 30-day notice, data export on termination (contact info@nuqta.pro within 30 days). Kept as MANUAL ACTION REQUIRED: liability cap.
- **`frontend/src/components/Impressum.js`**: Filled VAT (not applicable — Syria); ODR (not obligated note). Kept as MANUAL ACTION REQUIRED: CR number.
- **`frontend/src/components/PrivacyPolicy.js`**: Corrected log retention ("7 rolling files of 10 MB" → "14 rolling files of 20 MB" matching `DEFAULT_BACKUP_COUNT=14`, `DEFAULT_MAX_BYTES=20×1024×1024`).
- **Commit:** `93217e2` on `main`

### 5. Nuqta Sale — GDPR Art. 20 export + legal page cleanup
- **`backend/app/modules/auth/routes.py`**: Added identical GDPR export endpoint (`nuqtasale_gdpr_v1` format, `filename="nuqtasale-my-data.json"`).
- **`frontend/src/components/TermsOfService.js`**: Filled Arabic liability limitation + governing law (Syrian Arab Republic / Damascus courts). Kept as MANUAL ACTION REQUIRED: liability cap amount.
- **Commit:** `0e055ea` on `main`

### 6. Nuqta SY — static HTML legal pages
- **`en/privacy.html`**: Filled legal basis (Art. 6(1)(f) GDPR, note to verify with counsel); log retention (30 days, log rotation); Impressum section (operator details, CR → MANUAL ACTION, VAT → not applicable).
- **`en/terms.html`**: Filled disclaimer (standard "as-is" + general information disclaimer); governing law (Syrian Arab Republic / Damascus courts).
- **Arabic counterparts (`/terms.html`, `/privacy.html`)**: Equivalent changes (done in same session).
- **Commit:** `2cf459e` on `main`

### Commits pending push to GitHub (all on `main`)
| Repo | Commit | Summary |
|---|---|---|
| nuqtahealth | `346d865` | fix: resolve legal placeholder values in Health PrivacyPolicy, Impressum, TermsOfService |
| suar-services-static | `5ee805d` | fix: self-host Inter font, remove Google Fonts CDN from all pages |
| nuqtaid | `52639b6` | fix: require DOB at registration, close age gate bypass; add regression tests |
| nuqtapro | `93217e2` | feat: add GDPR Art.20 data export endpoint; fix legal page placeholders and log retention |
| Nuqtasale | `0e055ea` | feat: add GDPR Art.20 data export endpoint; fix ToS liability and governing law |
| nuqta-sy | `2cf459e` | fix: complete legal page content for EN/AR privacy and terms |

