# UC-04 — Government Officer / Ministry Staff
**Nepal Digital Infrastructure · Use Case Document**
*MOICS · NID Authority · District Administration Offices · Line Ministries*

---

## User Profile

| | |
|---|---|
| **Who** | Civil servants responsible for operating, regulating, and building on top of the NID API and NRB sandbox |
| **Roles** | NID system administrator, district enrollment officer, ministry IT officer, inter-ministry integration lead |
| **Motivation** | Deliver e-government services, reduce citizen queue time, reduce paper, reduce fraud |
| **Current pain** | Fragmented systems, no interoperability between ministries, manual verification bottlenecks |
| **Key concern** | "If this system goes down, I'm the one who gets blamed." |
| **Secondary concern** | "Will I still have a job if everything is automated?" |

Government officers are both operators and consumers of the system. They run the enrollment centres, manage the NID database, approve app registrations, and build internal portals on top of the API. Unlike private sector developers, they have limited technical flexibility — they work within procurement rules, approvals chains, and legacy IT environments.

The "will I still have a job" concern is real and must be acknowledged. The NID API does not eliminate government jobs — it shifts them from document shuffling to exception handling, data quality management, and citizen support. This framing needs to be explicit in the internal communications around the rollout.

---

## Use Cases — NID Authority (MOICS)

---

### UC-04.1 — NID system administrator manages app registrations

**Trigger:** A bank or fintech startup applies for production NID API access.

**Actor:** NID API administrator at MOICS

**Main flow:**
1. Application arrives via developer portal — includes company PAN, director NID, scope request, business description
2. Director NID automatically verified by system (NID API calls itself)
3. Administrator reviews application in admin dashboard:
   - Company details
   - Requested scopes (verify / kyc_basic / kyc_photo / citizen_login)
   - Business justification for each scope
4. Administrator approves/rejects/requests clarification
5. If approved: production `app_id` issued, scopes set, rate limits configured
6. Applicant notified via email

**Decision criteria for scope approval:**

| Scope | Approval requirement |
|---|---|
| `verify` | Any registered company — low risk |
| `kyc_basic` | Requires legitimate business justification (lending, onboarding) |
| `kyc_photo` | Restricted to financial institutions with NRB license |
| `citizen_login` | Any registered company — no data returned |

**Monitoring responsibilities:**
- Review monthly usage reports — flag anomalous query patterns
- Receive alerts when an app exceeds rate limits repeatedly
- Suspend app access if complaints received from citizens (via UC-01.2 flagging)

---

### UC-04.2 — Enrollment officer updates a citizen's incomplete NID record

**Trigger:** Citizen arrives at DAO with evidence that their NID record has an error (wrong address, missing tole, outdated DOB).

**Actor:** District Administration Office (DAO) enrollment officer

**Main flow:**
1. Citizen presents NID card + supporting document (ward office letter, birth certificate)
2. Officer accesses enrollment admin system
3. Pulls up citizen's NID record — sees current data and any `data_quality_warnings` flags
4. Makes correction with officer's employee ID logged as the author of the change
5. Sets `data_freshness` to today's date
6. Change enters a 24-hour review queue — reviewed by senior officer or auto-approved for low-risk changes (e.g., tole name)
7. Citizen receives SMS: *"Your NID record has been updated. Tole: Baneshwor."*

**Sensitive changes (require senior officer approval):**
- Date of birth correction
- Name correction
- Province/district change
- Biometric re-enrollment

**Audit requirement:** Every change logged with: officer ID, date/time, before/after values, supporting document reference. Cannot be deleted — only superseded by a subsequent correction.

**Design principle:** The system must make it easy to fix errors and hard to commit fraud. A single officer should not be able to make a sensitive change without a second review — this is the segregation-of-duties requirement.

---

### UC-04.3 — NID authority monitors system health and privacy compliance

**Trigger:** Routine monitoring, or response to a citizen complaint about unexpected data access.

**Actor:** NID Authority privacy officer

**Dashboard views:**
- API uptime and response time (last 24h, 7d, 30d)
- Total queries by app (daily, weekly)
- Queries by scope type distribution
- Citizen complaint queue (from UC-01.2 flagging)
- Apps approaching or exceeding rate limits
- Data quality warning rates by district (identifies enrollment centres that need support)

**Citizen complaint investigation flow:**
1. Citizen flags an unrecognised NID query via citizen portal
2. Privacy officer sees complaint in dashboard with: app ID, query timestamp, purpose field, query ID
3. Officer contacts registered app owner for explanation
4. If no satisfactory response within 5 days: app access suspended pending investigation
5. Officer files incident report
6. If fraudulent: refer to cybercrime unit

**Annual audit:** Every app's query volume reviewed. Apps with very low usage (< 10 queries/year) or suspiciously uniform query patterns are flagged for review.

---

## Use Cases — Line Ministry (e-Government Integration)

---

### UC-04.4 — Passport office integrates NID login (citizen SSO)

**Trigger:** Department of Passports wants to modernise its online application portal. Currently requires a separate login. Wants to use NID as the identity layer.

**Actor:** Department of Passports IT team + MOICS integration lead

**Main flow:**
1. Department registers as NID consumer with scope: `citizen_login` only
2. IT team implements the "Login with NID" button (standard OAuth2 redirect)
3. When citizen clicks: consent portal launches, citizen authenticates
4. Session token returned — Passport portal creates a session without receiving any personal data
5. Citizen sees their existing passport application pre-filled from the passport DB (not from NID)

**Key principle:** The NID citizen_login scope is not a data-sharing mechanism — it is an authentication mechanism. The passport portal is responsible for its own data. NID just confirms "yes, this is who they say they are."

**Rollout approach:**
- Phase 1: Login with NID as an *additional* option alongside existing username/password
- Phase 2: NID login becomes the *default* — username/password retained as fallback
- Phase 3: Username/password deprecated

**Inter-ministry coordination requirement:** MOICS publishes an "NID Integration Playbook" for all ministries — standard redirect URL, error handling, session management. Each ministry does not need to independently figure this out.

---

### UC-04.5 — Inland Revenue Department integrates NID for taxpayer verification

**Trigger:** IRD wants to reduce duplicate taxpayer registrations and verify that PAN applications correspond to real, verified identities.

**Actor:** IRD IT team

**Integration points:**

1. **New PAN application:** Applicant provides NID number → IRD calls `/verify` → confirms identity before issuing PAN. One NID number = one PAN. Eliminates duplicate PANs.

2. **Tax return pre-fill:** With citizen consent, IRD calls `/kyc_basic` to pre-fill name and address on digital tax return form. Reduces errors from manual entry.

3. **Employer payroll verification:** When employer files TDS returns with employee NIDs, IRD bulk-verifies via `/verify` that all NID numbers are valid and active.

**Sensitive design note:** IRD must never store NID data beyond what's strictly needed. The `query_id` is sufficient for audit — IRD does not need to store the citizen's full name and address from the NID API separately if they already have it from the PAN registration.

---

### UC-04.6 — NRB examiner uses sandbox data for supervision

**Trigger:** NRB examiner reviews a fintech company's sandbox transaction history as part of a Tier 2 license application review.

**Actor:** NRB fintech supervision officer

**Main flow:**
1. Company applies for Tier 2 upgrade from Tier 1
2. Examiner accesses NRB admin panel — views company's full Tier 1 transaction history
3. Checks: transaction volumes, AML flag rate, repatriation compliance rate, director NID verification status
4. Reviews AML flag handling: did company's system respond correctly to flagged transactions?
5. Checks for structuring patterns: multiple transactions just under $10,000 within short windows
6. If clean: approves Tier 2 upgrade, sets corridor approvals (Wise + Payoneer initially)
7. Sets a 3-month review checkpoint

**Red flags that delay/reject Tier 2:**
- AML flags consistently not acted upon
- Transaction descriptions too vague ("payment", "services" with no detail)
- Director NID mismatch between registration and later verification
- Volume growth rate inconsistent with stated business model

---

## Pain Points the System Must Avoid

| Pain point | Risk | Mitigation |
|---|---|---|
| Admin dashboard too complex | Officers stop using it | Mobile-friendly, Nepali UI, role-based views |
| Audit log too large to use | Investigations impossible | Filterable by date, app, citizen, officer ID |
| Enrollment officer can't fix errors | Citizens give up | Simple correction workflow with clear escalation paths |
| No training for DAO staff | Inconsistent quality | Standard training module in Nepali, refreshable online |
| System change breaks ministry integrations | Trust collapse | 90-day deprecation notice + integration playbook |
| Officer blamed for system downtime | Morale / accountability issue | Clear SLA ownership — MOICS owns uptime, not DAO |

---

## Roles and Permissions Matrix

| Role | Can view query logs | Can approve apps | Can suspend apps | Can edit NID records | Can view all citizens |
|---|---|---|---|---|---|
| NID sys admin | All | Yes | Yes | No | Yes (audit only) |
| Privacy officer | All | No | Yes (pending review) | No | Yes (complaint investigation) |
| DAO enrollment officer | Own district | No | No | Yes (with audit trail) | Own district |
| Senior DAO officer | Own district | No | No | Yes (sensitive changes) | Own district |
| Ministry IT officer | Own ministry queries | No | No | No | No |
| NRB examiner | NRB sandbox only | Tier 2/3 upgrade | No | No | No |

---

## Acceptance Criteria (Government Officer Perspective)

- [ ] Admin dashboard available in Nepali
- [ ] All audit log entries exportable to Excel/CSV for ministry reporting
- [ ] Enrollment officer workflow completable on a basic Android tablet
- [ ] DAO officer can process a data correction in under 10 minutes
- [ ] Privacy officer can investigate a citizen complaint to resolution in under 5 working days
- [ ] MOICS receives automated alert within 5 minutes of API uptime dropping below 99%
- [ ] All admin actions logged with officer ID — no action is anonymous
- [ ] Integration playbook for ministries published before Phase 3 ecosystem launch

---

*Document version: 0.1 · System: NID API · Related: UC-01 (Citizen), UC-02 (Financial Institution), UC-05 (NRB Regulator)*
