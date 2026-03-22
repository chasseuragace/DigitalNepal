# UC-01 — Citizen (नागरिक)
**Nepal Digital Infrastructure · Use Case Document**
*NID API + NRB Fintech Sandbox*

---

## User Profile

| | |
|---|---|
| **Who** | Any Nepali citizen with a National ID card |
| **Age range** | 16+ (NID eligible) |
| **Digital literacy** | Low to high — system must work for both |
| **Primary language** | Nepali (Devanagari) + some English |
| **Key concern** | "Who is looking at my personal data, and why?" |

The citizen is the only user type who does not initiate requests — they *respond* to them. Every other actor in the system (bank, cooperative, developer, government) must go through citizen consent before receiving any personal data. This makes the citizen the most important user type to design for, even though they interact with the system least frequently.

---

## Use Cases

---

### UC-01.1 — Consent to bank KYC for account opening

**Trigger:** Citizen wants to open a bank account. Bank asks for identity verification.

**Preconditions:**
- Citizen has a valid, active NID card
- Bank is a registered NID API consumer (Tier 2 or Tier 3 app)

**Main flow:**
1. Citizen provides NID number to bank teller or app
2. Bank app redirects citizen to the NID consent portal
3. Citizen sees: *"Nabil Bank is requesting your name, date of birth, and address for account opening. This consent expires in 30 minutes."*
4. Citizen authenticates via OTP sent to registered phone number
5. Citizen taps "Approve"
6. Bank receives consent token — valid for one `/kyc_basic` call within the approved scope
7. Bank completes account opening
8. Citizen receives SMS: *"Your NID data was shared with Nabil Bank on [date/time]. Scope: name, DOB, address."*

**Alternative flows:**
- **1a. NID suspended:** Bank receives `valid: false`, informs citizen, process stops
- **4a. Wrong OTP:** Citizen gets 3 attempts, then 15-minute lockout
- **5a. Citizen declines:** Bank receives `consent_denied`, no data shared

**Postconditions:**
- Citizen's query log updated — Nabil Bank entry visible in citizen portal
- Consent token single-use — cannot be replayed by bank

**Data shared:** Full name, date of birth, gender, address (ward level)
**Data NOT shared:** Phone number, photo, tax ID, passport number, biometric hash

---

### UC-01.2 — Citizen reviews who has accessed their NID data

**Trigger:** Citizen receives unexpected SMS notification about an NID data access, or wants to audit past consents.

**Preconditions:**
- Citizen has smartphone or access to a browser
- Citizen knows their NID number and registered phone

**Main flow:**
1. Citizen visits `mydata.nid.gov.np` or opens the NID mobile app
2. Authenticates via NID number + OTP
3. Views query log:
   ```
   Nabil Bank KYC        kyc_basic    22 Mar 2026  09:14   account opening
   eSewa Wallet          verify       18 Mar 2026  14:32   wallet top-up
   Kathmandu Co-op       kyc_basic    05 Feb 2026  11:08   membership
   ```
4. Citizen taps "Nabil Bank KYC" — sees exactly which fields were returned
5. Citizen can tap "Revoke future access" for any app — app loses consent

**Alternative flows:**
- **3a. Citizen does not recognise an entry:** Can flag it as suspicious — triggers NID authority review
- **5a. Revocation:** Existing data already shared cannot be un-shared (clearly communicated), but future queries from that app are blocked

**Key design principle:** The log uses plain Nepali language, not technical field names. "तपाईंको नाम, जन्म मिति र ठेगाना" not "full_name, dob, address".

---

### UC-01.3 — Citizen SSO login to a government portal

**Trigger:** Citizen needs to apply for a passport renewal, business registration, or land transfer — any e-government service.

**Main flow:**
1. Citizen visits a government portal (e.g., `passport.gov.np`)
2. Clicks "Login with NID" button
3. Redirected to NID consent portal — scope is `citizen_login` (no data shared)
4. Authenticates via OTP
5. Session token issued — citizen is logged into the government portal
6. No personal data transferred to the portal — portal only knows the citizen is authenticated

**What makes this different from UC-01.1:**
- Scope is `citizen_login`, not `kyc_basic`
- Zero personal fields returned — not even name
- The portal gets only a session token confirming authentication
- Citizen can use the same NID login across every government portal without creating separate usernames/passwords

**Benefit to citizen:** One credential for all government services. No more separate logins for IRD, passport office, land registry, company registrar.

---

### UC-01.4 — Citizen disputes a data quality error

**Trigger:** Citizen attempts KYC with a bank. Bank reports `data_quality_warnings: ["missing_tole"]` — the NID record has an incomplete address.

**Main flow:**
1. Bank informs citizen their NID record has incomplete data
2. Citizen visits nearest NID enrollment centre (or uses mobile app where available)
3. Presents NID card + supporting document (ward office letter, utility bill)
4. Enrollment officer updates record
5. `data_freshness` field updated to today's date
6. Future KYC calls return complete data

**Estimated affected population:** ~40% of NID holders have at least one incomplete field based on Phase 0 audit projections.

**Design implication:** The bank-facing API must never *block* a transaction due to incomplete NID data alone — it must *surface* the warning and let the bank decide. Blocking would penalise citizens for government data quality failures they did not cause.

---

### UC-01.5 — Citizen whose NID has been suspended requests reinstatement

**Trigger:** Citizen's NID was suspended (e.g., reported lost, administrative error, identity dispute). They are being blocked from services.

**Main flow:**
1. Citizen visits District Administration Office (DAO) or NID authority
2. Submits reinstatement request with supporting documents
3. NID status updated to `active` after verification
4. All previously blocked services resume automatically — no re-consent required

**Key risk:** A suspended NID blocks the citizen from *every* digital service simultaneously. This concentration of dependency means the suspension process must have a clear, fast appeals mechanism — ideally resolvable at DAO level within 5 working days without requiring a Kathmandu trip.

---

## Pain Points the System Must Avoid

| Pain point | Risk | Mitigation |
|---|---|---|
| Citizen doesn't understand consent request | Approves everything blindly | Plain Nepali language, specific field names shown |
| OTP goes to unregistered/old phone number | Citizen locked out | Fallback: biometric at enrollment centre |
| Citizen can't revoke consent | Trust collapses | Revocation must be one-tap in citizen portal |
| NID data error blocks services | Citizen penalised for govt failure | `data_quality_warnings` surfaces issue, doesn't block |
| Citizen unaware of data access | Surveillance fear | SMS notification on every successful query |
| NID portal unavailable | Single point of failure | 99.9% SLA mandatory — citizen depends on it |

---

## Acceptance Criteria (Citizen Perspective)

- [ ] Citizen receives SMS within 60 seconds of any NID data access
- [ ] Consent portal available in Nepali (Devanagari) and English
- [ ] Consent portal loads in under 3 seconds on 3G (Nepal's common connection)
- [ ] Citizen can view full query history within 2 taps from home screen
- [ ] Citizen can revoke app access without calling anyone or visiting an office
- [ ] `data_quality_warnings` shown to citizen in plain language, with instructions for remediation
- [ ] Citizen with suspended NID receives clear reason for suspension and next steps

---

*Document version: 0.1 · System: NID API · Related: UC-02 (Financial Institution), UC-04 (Government Officer)*
