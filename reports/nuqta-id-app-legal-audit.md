# Nuqta ID Mobile App — Technical Legal/Privacy Audit

> Technical repository audit only. Not legal certification. No compliance claim is made or implied.

**Audit date:** 2026-10-28 (session 2: DOB plaintext exclusion recorded; report published to tracked location)
**Auditor:** LegalPrivacyAuditor agent (Claude Sonnet 4.6)
**Repository:** `/home/suar/Nuqta_ID_APP` — GitHub: `Suar1/Nuqta_ID_APP`
**Branch/SHA (mobile app):** main @ 046c45c
**Related backend (nuqtaid):** main @ f8ac72f (DOB plaintext exclusion committed 2026-10-28 session 2)
**Stack:** Expo (React Native), React 19, TypeScript. iOS + Android + static web.
**Commits since October 13 baseline:** 8 significant commits — legal pages, age gate, auth remediations.

> **Published location:** `legal-privacy-auditor/reports/nuqta-id-app-legal-audit.md` (tracked).
> The source copy in `Nuqta_ID_APP/reports/` is gitignored; this is the canonical tracked version.

---

## Summary of changes since 2026-10-13

**FIXED since last audit:**
- Privacy Policy and Terms of Service screens added to app in all 4 languages (AR/EN/CKB/KMR) — commit 92ac886
- Legal contact details filled in privacy/terms pages — commit 14e1acc
- Privacy/Terms links added to welcome screen, registration screen, and settings
- `age-gate.ts` utility added — client-side advisory age check
- Android: `SYSTEM_ALERT_WINDOW` removed from manifest with security comment
- Auth layout uses proper loading state before redirect
- Document crop: console.error reduced in scope
- **Server-side age gate gap CLOSED** (2026-10-28 session 1): `nuqtaid/app.py` `/submit`
  endpoint now requires `date_of_birth` unconditionally. Omitting the field returns a
  validation error; the age check can no longer be bypassed by submitting no DOB.
  Regression tests added in `nuqtaid/tests/test_age_gate_enforcement.py` (5 tests, all pass).
- **DOB plaintext exclusion** (2026-10-28 session 2): `date_of_birth` added to
  `_FORM_DATA_JSON_EXCLUDE` in `nuqtaid/app.py`. The validated, age-gated DOB is now
  Fernet-encrypted at the point of form submission and stored as `_dob_encrypted` in
  `PendingRegistration.form_data_json`; the plaintext field is never written to the DB.
  `apply_personal_identity_from_form` reads the pre-encrypted token directly. Commit
  `f8ac72f`; 4 regression tests pass (`tests/test_pending_dob_encryption.py`).

---

## 1. Children / Age Controls

### Status: FIXED — server-side gap closed 2026-10-28

Client-side age-gate utility in `src/lib/age-gate.ts`:
- `MIN_AGE = 18` configurable constant.
- `meetsMinimumAge()` calculates age from DOB — explicitly returns `true` when DOB is absent, noting "server-side guard is the authoritative check."
- Client-side check is advisory only.

**Server-side enforcement (FIXED 2026-10-28):** `nuqtaid/app.py` `/submit` now requires
`date_of_birth` unconditionally. The previous conditional `if raw_dob:` allowed bypassing
the age gate by omitting the field. The fix makes the gate hard: no DOB = registration error.
`MIN_REGISTRATION_AGE` env var (default 18) is respected. Five regression tests pass.

No `childDirected` flag or equivalent in `app.json`. No parental consent flow.

Privacy policy states "The service is intended for users aged 18 and over."

### Evidence
- `src/lib/age-gate.ts:8,40-43` — `MIN_AGE = 18`; `meetsMinimumAge()` indeterminate when no DOB
- `nuqtaid/app.py:5402-5428` — server-side age gate, DOB now required
- `nuqtaid/tests/test_age_gate_enforcement.py` — 5 regression tests (all pass)
- `app.json` — no child-directed advertising flag

### You still need to
- Confirm App Store/Play Store listings do not declare this as suitable for users under 18.

---

## 2. Third-Party Resources

### Status: GOOD — NEEDS LEGAL REVIEW for EAS processor

No third-party analytics, tracking, CDN, CAPTCHA, social login, maps, or AI SDKs integrated at runtime. All dependencies are bundled. Outbound connections:

1. **First-party API** — `nuqta.id/api/mobile/v1` (configurable via `EXPO_PUBLIC_NUQTA_API_BASE_URL`).
2. **First-party imaging** — `nuqta.health` with strict allowlist in `src/services/health/imaging-api.ts`.
3. **EAS (Expo Application Services)** — Project ID `0b50f92d-5385-43a3-8c7c-da748536e01b` in `app.json`. EAS receives app bundle and device metadata at build/update time (not user runtime).

### Evidence
- `src/services/api/config.ts` — sole API base URL
- `src/services/health/imaging-api.ts:44-48` — strict `nuqta.health` allowlist
- `package.json` — no analytics/tracking dependencies
- `app.json:47-49` — EAS project ID

### You still need to
- Disclose EAS (Expo Application Services) as an infrastructure processor in the privacy policy.
- Confirm `nuqta.id` and `nuqta.health` backend services do not embed third-party trackers.

---

## 3. Analytics / Session Replay

### Status: NOT APPLICABLE

No analytics, session replay, crash reporting, or telemetry SDK found. Single `console.error` in `document-crop.tsx` logs to local device console only — not remote.

---

## 4. Cookies / Browser Storage

### Status: GOOD

No browser cookies or localStorage on native code paths. All persistent data uses `expo-secure-store` with `WHEN_UNLOCKED_THIS_DEVICE_ONLY`:

- Auth tokens: `nuqta_access_token`, `nuqta_refresh_token`, `nuqta_token_type`, `nuqta_access_token_expires_at` — `src/services/auth/token-storage.ts:17-18`.
- Local document metadata: `nuqta_local_docs_meta_v1` — `src/services/documents/local-documents.ts:36`.
- Preferences (theme, language): stored in SecureStore — `src/context/preferences-context.tsx`.

For the static web build (if deployed), web-specific storage paths exist but no cookie/localStorage use was found in audited code paths.

---

## 5. Commercial Email / Unsubscribe

### Status: NOT APPLICABLE

Mobile client does not send email or manage email subscriptions. See nuqtaid backend audit for unsubscribe implementation.

---

## 6. Recurring Subscriptions / Trials

### Status: NOT APPLICABLE

No payment processing, in-app purchases, or subscription flows found.

---

## 7. UGC / Copyright / DMCA

### Status: LOW RISK — MANUAL ACTION REQUIRED

- **Profile photo:** User can select from library (`expo-image-picker`) and upload via `PUT /me/photo` API.
- **Local documents (gov ID, driving licence):** Photos stored exclusively on-device in app's private sandbox. Explicitly documented as never uploaded to any API or service (`src/services/documents/local-documents.ts:5-7`).
- No DMCA or copyright notice in app.

### Evidence
- `src/app/(tabs)/settings/edit-profile.tsx:95` — profile photo library picker
- `src/components/documents/documents-section.tsx:137,143` — camera/library for local documents
- `src/services/documents/local-documents.ts:5-7` — local-only storage comment

### You still need to
- Confirm upload endpoint on backend validates file type and size (see nuqtaid backend audit).
- Assess whether abuse/takedown contact is needed for user-uploaded profile photos.

---

## 8. Privacy / Terms / Impressum

### Status: SUBSTANTIALLY IMPROVED — NEEDS LEGAL REVIEW for content

Since Oct 13 audit:
- In-app Privacy Policy screen (`src/app/(tabs)/settings/privacy-policy.tsx`) — localized in EN/AR/CKB/KMR.
- In-app Terms of Service screen (`src/app/(tabs)/settings/terms-of-service.tsx`) — localized in EN/AR/CKB/KMR.
- Links to Privacy Policy and Terms visible on welcome screen (`welcome.tsx:150-160`) and registration screen (`register/type.tsx:155-160`).
- Privacy content includes GDPR legal basis citations in locale strings (`src/locales/en.json:546`).

**Legal content notes:**
- Privacy Policy says "Contact: info@nuqta.id" — confirm this is monitored and capable of handling data subject requests.
- Privacy Policy references `nuqta.id/api/mobile/v1/profile/export` for data export — confirm the backend endpoint is reachable from mobile app.
- Impressum is not present in the mobile app — this may be acceptable if the app store listing and/or the web service contains the Impressum.

### Evidence
- `src/app/(tabs)/settings/privacy-policy.tsx` — in-app Privacy Policy
- `src/app/(tabs)/settings/terms-of-service.tsx` — in-app Terms of Service
- `src/app/(auth)/welcome.tsx:150-160` — links on welcome screen
- `src/locales/en.json:546` — GDPR legal basis in content

### You still need to
- Verify App Store (iOS) and Play Store (Android) privacy labels are complete and accurate.
- Confirm `info@nuqta.id` is monitored for data subject requests arriving via app.

---

## 9. GDPR/ePrivacy Technical Controls

### Status: PARTIALLY IMPLEMENTED — MANUAL ACTION REQUIRED

**Implemented:**
- Privacy Policy with GDPR rights disclosure (Arts. 15-22) visible before and after registration.
- Consent disclosure shown at registration step.
- Logout implemented (`logoutCurrentSession()` in `auth-service.ts`) — clears SecureStore tokens.
- Privacy locale strings include rights disclosure and contact information.

**Still missing:**
- No in-app data export request flow — policy references `nuqta.id/api/mobile/v1/profile/export` (backend endpoint must serve this).
- No in-app account deletion flow — policy references email contact.
- No consent state tracking for in-app actions beyond what is managed by the backend.

### Evidence
- `src/locales/en.json:553` — GDPR rights disclosure in privacy policy
- `src/services/auth/auth-service.ts:27-32` — logout clears session
- `src/services/auth/token-storage.ts:84-90` — `clearTokens()` clears SecureStore

### You still need to
- Consider adding an in-app data export and account deletion request flow (delegates to backend).
- Confirm backend handles data subject requests received via `info@nuqta.id`.

---

## 10. Secrets / Sensitive Data

### Status: LOW RISK — scanner false positives confirmed

**Scanner findings (all confirmed false positives):**
- `__tests__/token-storage-test.ts:30,37` — `accessToken: 'access-token'` and `refreshToken: 'refresh-token'` are mock test strings, not real credentials. Scanner matched generic_api_key pattern against test fixture strings.
- `src/app/document-fullscreen.tsx:4` — `pan` refers to `Gesture.Pan()` gesture handler, not a payment PAN.

**No real secrets committed to repository.** `.env.example` contains only public API URLs. `EXPO_PUBLIC_` variables are intentionally public.

**Positive security controls:**
- `android:usesCleartextTraffic="false"` in AndroidManifest.
- `android:allowBackup="false"` — prevents ADB backup of app data.
- `ITSAppUsesNonExemptEncryption: false` in iOS Info.plist — confirms no US export restrictions (verify this is accurate).

### Evidence
- `__tests__/token-storage-test.ts:30,37` — confirmed test mock strings
- `src/app/document-fullscreen.tsx:4,54,79` — `pan` = `Gesture.Pan()` gesture
- `android/app/src/main/AndroidManifest.xml` — `allowBackup=false`, `usesCleartextTraffic=false`
- `.env.example` — only public API URLs

### You still need to
- Verify `ITSAppUsesNonExemptEncryption: false` is accurate (confirm app uses only standard OS encryption APIs).

---

## 11. Logging / Error Reporting

### Status: GOOD

Single `console.error('[crop] save error', e)` in `document-crop.tsx:571` — logs error object to local device console only. No PII in logged data. No remote log/crash service.

---

## 12. Authorization / Security Affecting Privacy

### Status: GOOD

- Auth tokens stored in `expo-secure-store` with `WHEN_UNLOCKED_THIS_DEVICE_ONLY` — platform secure storage (iOS Keychain, Android Keystore).
- `android:allowBackup="false"` — app data excluded from ADB/device backups.
- `android:usesCleartextTraffic="false"` — no HTTP cleartext.
- `SYSTEM_ALERT_WINDOW` permission removed with comment: "enables overlay attacks on sensitive screens."
- No hardcoded credentials, API keys, or secrets in source.
- Deep link scheme `nuqtaidmobile://` — Expo Router handles routing; no sensitive parameters in URL paths detected.
- Medical imaging: `imaging-api.ts` strict `nuqta.health` allowlist prevents URL injection.

**Backup rules concern:**
- `AndroidManifest.xml` references `@xml/secure_store_backup_rules` and `@xml/secure_store_data_extraction_rules` — these XML files are generated by the `expo-secure-store` Expo plugin at EAS build time. They are **not present in the repository**. Verify they are correctly generated during build and exclude app-private data from backups.

**iOS PrivacyInfo.xcprivacy:**
- No app-level `PrivacyInfo.xcprivacy` file was found in the project (only in node_modules). Apple requires this file for App Store submissions with required reason APIs. The `expo-secure-store` plugin provides its own, but the app-level declaration may be required.

### Evidence
- `src/services/auth/token-storage.ts:17-18` — `WHEN_UNLOCKED_THIS_DEVICE_ONLY`
- `android/app/src/main/AndroidManifest.xml` — `allowBackup=false`, no `SYSTEM_ALERT_WINDOW`
- `src/services/health/imaging-api.ts:44-48` — URL allowlist

### You still need to
- **MANUAL ACTION REQUIRED:** Verify EAS build generates `secure_store_backup_rules.xml` and `secure_store_data_extraction_rules.xml` that exclude app data from device backups.
- **MANUAL ACTION REQUIRED:** Verify App Store submission includes a correct `PrivacyInfo.xcprivacy` with all required reason APIs declared.
- Confirm deep link handlers validate input before processing (Expo Router does this by default).

---

## 13. Payments

### Status: NOT APPLICABLE

No payment processing or in-app purchases found.

---

## 14. Mobile Privacy Controls

### Status: SUBSTANTIALLY IMPLEMENTED — NEEDS VERIFICATION at platform level

**iOS (app.json `infoPlist` section):**
- `NSCameraUsageDescription` — camera for documents/photos.
- `NSPhotoLibraryUsageDescription` — photo library for profile photo.
- `NSPhotoLibraryAddUsageDescription` — saves processed ID documents.
- `NSFaceIDUsageDescription` — Face ID for authentication.
- `ITSAppUsesNonExemptEncryption: false` — encryption declaration.

**Concern:** Face ID usage description is declared but Face ID authentication was not found in the audited source code. If Face ID is not yet implemented, this declaration should be removed to avoid requesting unnecessary permission.

**Android (AndroidManifest.xml):**
- `INTERNET`, `VIBRATE`, `CAMERA` — declared permissions.
- `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE` — limited to `maxSdkVersion=32` (Android 12 and below only — correct for newer storage APIs).
- `CAMERA` declared but scanner screen (`scanner.tsx`) shows a mock viewfinder. Verify camera permission is only requested at runtime when actually needed.

**Push Notifications:** No push notification setup found (`expo-notifications` not in dependencies). No push token storage or FCM/APNs configuration found.

**Device identifiers:** No IDFA, GAID, or `expo-device` unique ID collection found in source.

**App Store/Play Store privacy labels:**
- Status: NOT VERIFIED — cannot verify store listings from source code alone.

### Evidence
- `app.json:14-28` — iOS permissions
- `android/app/src/main/AndroidManifest.xml` — Android permissions
- `package.json` — no expo-notifications dependency

### You still need to
- **MANUAL ACTION REQUIRED:** Complete App Store Privacy Nutrition Label and Play Store Data Safety form, ensuring all data collection, sharing, and storage is correctly declared.
- **MANUAL ACTION REQUIRED:** Create and submit app-level `PrivacyInfo.xcprivacy` for iOS App Store submission.
- Remove `NSFaceIDUsageDescription` from `app.json` if Face ID authentication is not yet implemented.
- Verify CAMERA permission is requested at runtime only when the user initiates a document scan.
- Confirm EAS-generated backup exclusion rules are correct at build time.

---

## Permissions Summary

| Platform | Permission | Declared | Runtime request | Justification |
|---|---|---|---|---|
| iOS | Camera | Yes | Via expo-image-picker | Document/profile photo capture |
| iOS | Photo Library Read | Yes | Via expo-image-picker | Profile photo upload, local document import |
| iOS | Photo Library Write | Yes | Via expo-image-picker | Save processed documents |
| iOS | Face ID | Yes | Implicit | **Verify Face ID is implemented** |
| Android | INTERNET | Yes | Not required | API communication |
| Android | CAMERA | Yes | Runtime via expo-image-picker | Document/profile photo |
| Android | READ/WRITE_EXTERNAL_STORAGE | Yes (maxSdkVersion=32) | Runtime | Legacy Android storage |
| Android | VIBRATE | Yes | Not required | Haptic feedback |

---

## Secrets

| Type | Location | Exposure | Action |
|---|---|---|---|
| Mock access-token string | `__tests__/token-storage-test.ts:30` | Test fixture only — not real | No action needed — confirmed mock |
| Mock refresh-token string | `__tests__/token-storage-test.ts:37` | Test fixture only — not real | No action needed — confirmed mock |
| EAS project ID | `app.json:47-49` | Public identifier — not a secret | Disclose EAS as infrastructure processor |

---

## Manual Compliance Actions

1. **App Store Privacy Label** — Complete Apple App Store Privacy Nutrition Label and Google Play Data Safety section accurately.
2. **PrivacyInfo.xcprivacy** — Create and include an app-level `PrivacyInfo.xcprivacy` for iOS App Store submission declaring all required reason APIs.
3. **Face ID declaration** — Remove `NSFaceIDUsageDescription` from `app.json` if Face ID is not yet implemented; add it back when Face ID authentication is implemented.
4. **EAS backup rules verification** — Confirm the expo-secure-store plugin generates correct backup exclusion rules at EAS build time.
5. **EAS processor disclosure** — Disclose EAS (Expo Application Services) as an infrastructure processor in the privacy policy.
6. **Age gate** — RESOLVED (2026-10-28 session 1): server-side DOB is now required unconditionally; `nuqtaid/app.py:5402-5428` enforces hard gate; 5 regression tests pass. Client-side check (`age-gate.ts`) remains advisory as intended.
   **DOB plaintext** — RESOLVED (2026-10-28 session 2): plaintext DOB excluded from `PendingRegistration.form_data_json`; encrypted at submission as `_dob_encrypted` (commit `f8ac72f`); 4 regression tests pass.
7. **In-app data export** — Consider adding an in-app button to request data export (delegates to backend endpoint).
8. **In-app account deletion** — Consider adding an in-app account deletion request flow (delegates to backend/email).
9. **Camera permission timing** — Confirm CAMERA permission is requested at runtime only when the user initiates a scan.

---

## Final Table

| Area | Severity | Status | Evidence | Manual action |
|---|---|---|---|---|
| 1. Children / age controls | LOW | FIXED (server-side + DOB plaintext) | `src/lib/age-gate.ts` advisory; `nuqtaid/app.py:5402-5428` server hard gate; DOB encrypted at submission (f8ac72f); 9 regression tests | App Store age rating declaration (manual) |
| 2. Third-party resources | INFO | NEEDS LEGAL REVIEW | `app.json` EAS ID; `package.json` — no SDKs | Disclose EAS as processor |
| 3. Analytics / session replay | INFO | NOT APPLICABLE | None found | — |
| 4. Cookies / browser storage | INFO | GOOD | SecureStore `WHEN_UNLOCKED_THIS_DEVICE_ONLY` | — |
| 5. Commercial email | INFO | NOT APPLICABLE | Not applicable to mobile client | — |
| 6. Subscriptions | INFO | NOT APPLICABLE | None found | — |
| 7. UGC / copyright | LOW | MANUAL ACTION REQUIRED | `edit-profile.tsx:95`; `documents-section.tsx:137` | Backend validates uploads; no DMCA |
| 8. Privacy / Terms | MEDIUM | SUBSTANTIALLY IMPROVED | `settings/privacy-policy.tsx`; `settings/terms-of-service.tsx` | App store privacy labels; DPO contact |
| 9. GDPR/ePrivacy controls | MEDIUM | PARTIALLY IMPLEMENTED | GDPR rights in locale strings; no in-app export/delete | Add in-app export/deletion flows |
| 10. Secrets | INFO | GOOD (scanner FP) | `__tests__/token-storage-test.ts` — confirmed mocks | None — confirmed false positives |
| 11. Logging | INFO | GOOD | Single local console.error | — |
| 12. Authorization / security | MEDIUM | NEEDS VERIFICATION | SecureStore; allowBackup=false; backup rules missing from repo | Verify EAS-generated backup rules; PrivacyInfo.xcprivacy |
| 13. Payments | INFO | NOT APPLICABLE | None found | — |
| 14. Mobile privacy | HIGH | MANUAL ACTION REQUIRED | iOS permissions; Android manifest; no app PrivacyInfo | App Store privacy label; PrivacyInfo.xcprivacy; Face ID check |
