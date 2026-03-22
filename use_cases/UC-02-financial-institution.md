# UC-02 — Financial Institution
**Nepal Digital Infrastructure · Use Case Document**
*Banks · Cooperatives · Microfinance Institutions (MFIs)*

---

## User Profile

| | |
|---|---|
| **Who** | Loan officers, teller staff, compliance managers, IT teams at banks / cooperatives / MFIs |
| **Institution types** | Class A–D banks, cooperatives (50+ crore turnover), microfinance institutions |
| **Motivation** | Reduce KYC cost and time, reduce fraud, comply with NRB regulations |
| **Current pain** | Manual document verification, duplicate KYC across branches, cooperative fraud from unverified members |
| **Key concern** | "Is this data legally defensible if we get audited?" |

Financial institutions are the highest-volume consumers of the NID API. A large bank may make tens of thousands of verification calls per month. A rural cooperative may make a handful, but each one represents a real lending decision with real money at stake.

---

## Use Cases — NID API

---

### UC-02.1 — Bank account opening (digital onboarding)

**Trigger:** Customer applies for a bank account online or at a branch.

**Actor:** Bank KYC system (automated), teller (branch)

**Preconditions:**
- Bank is registered as a Tier 2 or Tier 3 NID API consumer
- Customer provides NID number and completes consent flow (see UC-01.1)

**Main flow:**
1. Bank system calls `POST /v1/nid/verify` with customer's NID number
2. Receives `valid: true`, `nid_status: active`
3. Bank system calls `POST /v1/nid/kyc_basic` with consent token
4. Receives: full name, DOB, gender, address (ward level), `data_freshness` date
5. System pre-fills account opening form — customer confirms/corrects
6. Account opened; NID query logged in bank's audit trail with `query_id`

**Alternative flows:**
- **2a. `valid: false`, `nid_status: suspended`:** Bank rejects application, informs customer to contact DAO
- **4a. `data_quality_warnings: ["missing_tole"]`:** Bank surfaces warning, asks customer to provide tole manually — does not block account opening
- **4b. `data_freshness` is more than 3 years ago:** Bank flags for manual review; address may be outdated

**Postconditions:**
- Bank's compliance record includes `query_id` — defensible audit trail
- No NID data stored by bank beyond what's needed for account (data minimisation)

**Business value:**
- Manual document collection: ~45 minutes per customer
- NID API verification: ~30 seconds
- Estimated cost saving: NPR 800–1,200 per account opening

---

### UC-02.2 — Loan origination with biometric verification

**Trigger:** Customer applies for a loan above a threshold (e.g., NPR 500,000) requiring enhanced KYC.

**Actor:** Loan officer + bank KYC system

**Preconditions:**
- Bank has `kyc_photo` scope approved (Tier 3 app)
- Customer has biometric enrolled in NID system

**Main flow:**
1. Loan officer collects NID number and initiates consent flow for `kyc_photo` scope
2. Customer completes OTP + photo consent
3. Bank system calls `POST /v1/nid/kyc_photo` with selfie captured on branch tablet
4. Receives: `match: true`, `confidence: 0.94`, `liveness_check: passed`
5. Loan officer proceeds with loan assessment
6. All three query IDs (`verify`, `kyc_basic`, `kyc_photo`) linked in loan file

**Alternative flows:**
- **4a. `confidence` below 0.75:** System flags for manual review by branch manager — does not auto-reject
- **4b. `biometric_not_enrolled`:** Customer directed to NID enrollment centre; loan application paused
- **4c. `no_photo_on_file`:** Same as 4b — biometric path unavailable, bank uses manual document verification as fallback

**Key design note:** The biometric match result (`match: true/false`, `confidence` score) is logged in the bank's system but the actual photo is never received by the bank — it stays in the NID system. This is a significant privacy protection.

---

### UC-02.3 — Cooperative member KYC and duplicate membership check

**Trigger:** New member applies to join a savings cooperative. Cooperative must verify identity and check for duplicate memberships.

**Actor:** Cooperative secretary / membership officer

**Context:** Nepal's cooperative crisis (NPR 275B+ at risk) was partly driven by members borrowing from multiple cooperatives simultaneously without any cross-cooperative visibility. The NID API enables cooperatives to verify real identity — the credit bureau (Priority 3 system) will eventually enable cross-cooperative debt checking.

**Main flow:**
1. Applicant provides NID number
2. Secretary initiates consent flow via cooperative's registered app (`hamro_saas_sandbox` equivalent)
3. Calls `POST /v1/nid/kyc_basic` — verifies name, DOB, address
4. Cooperative system checks internal records: has this NID number been used before?
5. If clean: member registered with NID number as verified identifier
6. If duplicate: cooperative rejects or escalates to committee

**Alternative flows:**
- **3a. `data_quality_warnings: ["missing_tole", "missing_phone"]`:** Cooperative records available data, requests member to update NID at DAO before loan eligibility
- **5a. NID number already exists in system:** Flags as potential duplicate — may be same person re-applying or identity theft; escalate to committee

**Postconditions:**
- Every cooperative member now has a verified, unique NID-linked identity
- Future credit bureau integration will use this NID as the cross-cooperative identifier

**Business value:** Prevents the most common cooperative fraud pattern — using different name variations (Ram B. Thapa vs. Ram Bahadur Thapa) to obscure multiple memberships.

---

### UC-02.4 — Microfinance group loan with collective consent

**Trigger:** A group of 5 borrowers applies for a group lending scheme (samuhik karja). MFI must verify all 5.

**Actor:** MFI field officer

**Main flow:**
1. Field officer visits borrower group in village
2. Each member provides NID number; field officer enters into MFI mobile app
3. App sends 5 OTPs — each member receives OTP on their registered phone
4. Field officer collects OTPs from each member (or members tap their own phones)
5. App makes 5 sequential `verify` calls, then 5 `kyc_basic` calls
6. All 5 verified — group loan file created with NID-linked members

**Alternative flows:**
- **5a. One member's NID invalid:** Group loan cannot proceed until that member's NID is resolved — field officer advises on process
- **5b. Member has no registered phone:** Fallback to enrollment centre visit; MFI may choose to proceed with other 4 and defer

**Key design requirement:** MFI app must work offline with queued requests — field officers often have intermittent connectivity. Consent tokens must have a grace period (e.g., 2 hours) to accommodate this.

**NRB regulation link:** Per the NRB sandbox framework, MFIs using NID-verified KYC qualify for the simplified tier of NRB reporting — reduced compliance burden as an incentive to adopt.

---

## Use Cases — NRB Sandbox (for banks and MFIs)

---

### UC-02.5 — Bank onboards to NRB sandbox for remittance testing

**Trigger:** Bank wants to test a new remittance product allowing overseas Nepalis to send money directly to NID-verified accounts.

**Main flow:**
1. Bank's IT team registers via `POST /v1/nrb/companies/register` with `requested_tier: tier_2`, `business_model: remittance`
2. Director's NID verified via NID API during registration
3. Bank receives `sk_live_np_...` key with `approved_corridors: ["wise", "payoneer"]`
4. Bank tests inbound flows via `POST /v1/nrb/simulate/inbound`
5. Tests AML edge cases: sends $9,500 — observes `structuring_risk` flag
6. Integrates AML flag handling into bank's operations workflow
7. Applies for Stripe corridor addition via NRB portal

**Postconditions:**
- Bank's compliance team has tested AML handling before going live
- All test transactions logged — submittable as evidence for NRB technical audit

---

## Pain Points the System Must Avoid

| Pain point | Risk | Mitigation |
|---|---|---|
| API downtime during business hours | Branch operations halt | 99.9% SLA + status page + graceful fallback to manual |
| Stale `data_freshness` not flagged | Loan approved on outdated address | Surface `data_freshness` prominently; bank configures threshold |
| `query_id` not stored by bank | Not legally defensible in dispute | Bank integration guide must mandate `query_id` storage |
| Rate limit hit during peak (month-end) | KYC bottleneck | Rate limits set at 1,000 req/min — most banks need far less |
| Biometric not enrolled for rural borrowers | Loan process blocked | `biometric_not_enrolled` response must include enrollment centre location lookup |

---

## Integration Checklist (for bank IT teams)

- [ ] Store `query_id` from every API response in loan/account record
- [ ] Handle `data_quality_warnings` array — never silently ignore it
- [ ] Implement consent redirect flow (OAuth2 PKCE) — do not attempt to pass NID numbers without citizen consent
- [ ] Honour `data_freshness` — set a business rule threshold (e.g., flag if > 2 years)
- [ ] Never store raw biometric data — only store `match: true/false` and `confidence` score
- [ ] Implement graceful fallback to manual verification if API returns 5xx
- [ ] Subscribe to NID API status page for maintenance notifications

---

## Acceptance Criteria (Financial Institution Perspective)

- [ ] `/verify` response time < 500ms at p95 under normal load
- [ ] `/kyc_basic` response time < 800ms at p95
- [ ] `query_id` present in every successful and failed response
- [ ] `data_quality_warnings` present in response when applicable — never silently omitted
- [ ] API returns meaningful error codes, not generic 500s
- [ ] Sandbox environment available 24/7 with synthetic data — no production data in sandbox
- [ ] Integration documentation available in English and Nepali
- [ ] NRB sandbox AML engine behaviour documented with all rule thresholds

---

*Document version: 0.1 · System: NID API + NRB Sandbox · Related: UC-01 (Citizen), UC-03 (Developer/Fintech), UC-05 (NRB Regulator)*
