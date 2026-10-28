# Nuqta Ecosystem — Cross-Platform Data Flow Audit
**Audit date:** 2026-10-28  
**Auditor:** Claude (LegalPrivacyAuditor v1 framework — manual cross-platform review)  
**Scope:** All data flows between Nuqta ecosystem platforms; disclosure consistency across privacy policies

---

## Summary

| Finding | Severity | Status |
|---|---|---|
| Health privacy policy has unfilled [PLACEHOLDER] values | CRITICAL | OPEN (from Platform 3 audit) |
| Nuqta ID ↔ Health PHI data minimisation | INFO | ADEQUATE |
| Nuqta ID → Sale/Pro customer data fetch | INFO | ADEQUATE |
| Cross-platform disclosure consistency | MEDIUM | PARTIALLY CONSISTENT |
| ID admin settings reference Health integration (placeholder only) | INFO | NOT ACTIVE |

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
| Nuqta Health | YES but PLACEHOLDER | PrivacyPolicy.jsx mentions integrations but has unfilled `[PLACEHOLDER]` values for processor details |
| Nuqta Pro | PARTIAL | Mentions Nuqta ID integration in some places but privacy policy is incomplete (ToS has `[PLACEHOLDER — SLA terms]`) |
| Nuqta Sale | YES | PrivacyPolicy.js lists Nuqta ID as a processor |
| Nuqta SY | YES | Explicitly states each sub-platform has its own policy |
| Nuqta IT | N/A | No cross-platform integration |
| Suar Services | N/A | No cross-platform integration |

**MEDIUM gap:** Nuqta Health's `PrivacyPolicy.jsx` still has `[PLACEHOLDER]` for several sections including operator identity and registration details. This is the most critical cross-platform disclosure gap since Health processes the most sensitive data (PHI, DOB, national IDs).

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

### CRITICAL (carried from Platform 3) — Health privacy policy placeholders
Nuqta Health's `frontend/src/components/PrivacyPolicy.jsx` contains unfilled `[PLACEHOLDER]`
markers for operator identity, commercial registration number, regulatory authority, and
VAT number. For a platform processing PHI (Special Category Data), this is the most
critical documentation gap in the ecosystem. Full details in the Nuqta Health audit report.

### MEDIUM — Cross-platform data flows not consistently disclosed
Nuqta ID's privacy policy has the best disclosure of cross-platform data sharing.
Nuqta Sale explicitly lists Nuqta ID as a processor. Nuqta Pro and Nuqta Health's
legal pages have incomplete content. Users of Health and Pro cannot easily understand
that their identity data may be fetched from Nuqta ID for record linking.

**Remediation:** Each platform's privacy policy should explicitly name Nuqta ID as
an identity data source (where applicable) and describe the data exchanged and
the trigger event (e.g., "when a facility links your patient record to your Nuqta ID").

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

The main gap is documentation completeness: health privacy policy placeholders and
incomplete disclosures in Pro/Health legal pages must be resolved before launch.

