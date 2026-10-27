# Web/mobile legal and privacy technical ruleset

This is a technical audit ruleset, not legal advice or certification.

## 1. Children / age controls
Identify age collection, age gates, DOB handling, parental-consent flows, child-directed behavior and backend enforcement.

## 2. Third-party resources
Inventory remotely loaded fonts, scripts, SDKs, CDNs, CAPTCHA, maps, embeds, AI services and other processors.

## 3. Analytics / session replay
Find every analytics, telemetry and replay implementation. Verify optional tracking does not initialize or transmit before the applicable consent signal. Mask sensitive replay fields.

## 4. Cookies / browser storage
Inventory cookies, localStorage and sessionStorage. Review purpose, category, pre-consent behavior, Secure, HttpOnly and SameSite settings where applicable.

## 5. Commercial email / unsubscribe
Locate marketing-email paths, list membership, unsubscribe handling and suppression enforcement. Enforce unsubscribe server-side.

## 6. Recurring subscriptions / trials
Locate checkout, renewal, cancellation, trial and pricing logic. Flag legal/business wording decisions for review.

## 7. UGC / copyright / DMCA
Locate user uploads/publication, moderation, takedown/contact mechanisms and copyright handling. Never fabricate a DMCA agent/contact.

## 8. Privacy / Terms / Impressum
Find policy pages and application links. Missing authoritative company/contact information is manual action.

## 9. GDPR/ePrivacy technical controls
Review consent state, minimization, access/export/delete workflows, retention mechanisms, processor calls and backend authorization. Do not claim GDPR compliance.

## 10. Secrets / sensitive data
Find committed credentials, client-exposed secrets and sensitive categories. Never print secret values.

## 11. Logging / error reporting
Find logs/error telemetry that may contain credentials, identifiers, health data, DOB, payment data or request bodies.

## 12. Authorization/security affecting privacy
Review object-level authorization, public endpoints, uploads/downloads, admin routes, tenant boundaries and backend validation.

## 13. Payments
Identify payment providers and handling. Raw PAN/CVV must not be stored or logged. Prefer hosted/tokenized provider flows.

## 14. Mobile privacy controls
Review mobile permissions, device identifiers, push tokens, deep links, secure storage, SDKs, platform privacy declarations and sensitive data in logs/backups.

## Evidence/remediation discipline

Every finding needs evidence. Inspect all implementations. Prefer minimal auditable changes. Never delete user data or weaken authentication. Re-scan and verify after changes. Failed verification prevents FIXED.
