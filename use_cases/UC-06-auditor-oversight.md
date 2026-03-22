# UC-06 — Auditor / Oversight Body / Civil Society
**Nepal Digital Infrastructure · Use Case Document**
*CIAA · OAG · Parliamentary Committee · Journalists · Civil Society Organisations*

---

## User Profile

| | |
|---|---|
| **Who** | External oversight actors who monitor whether the system is operating with integrity and serving the public interest |
| **Types** | Commission for Investigation of Abuse of Authority (CIAA) · Office of the Auditor General (OAG) · Parliamentary Public Accounts Committee · Investigative journalists · Civil society / digital rights organisations |
| **Motivation** | Ensure public funds are spent well, system is not abused, citizen rights are protected |
| **Current pain** | Government IT systems are black boxes — no access, no audit trail, no accountability |
| **Key concern** | "Is this system being used to surveil citizens or favour politically connected companies?" |
| **Secondary concern** | "Was the procurement clean? Is the code what was paid for?" |

This user type is unusual in that they do not interact with the system through APIs or admin panels in normal operation. They interact with it through: public documentation, freedom of information requests, parliamentary hearings, media reporting, and — in the case of serious concerns — formal investigations.

Designing for auditability from the start is not optional. Nepal has a long history of government IT projects that were opaque by design, enabling corruption at every layer: procurement, development, and operation. The open-source mandate and public audit trail are not just privacy features — they are anti-corruption features.

---

## Use Cases

---

### UC-06.1 — Auditor General reviews NID API procurement

**Trigger:** Annual OAG audit of MOICS IT expenditure. NID API project is included in scope.

**Actor:** OAG audit team

**What the OAG should be able to verify:**

1. **Procurement trail:**
   - Tender specification published on PPMO portal
   - Evaluation criteria publicly stated (not post-hoc)
   - Winning bid within reasonable range of market rate
   - Evaluation committee minutes available and complete
   - No single-source procurement without documented justification

2. **Deliverables vs contract:**
   - Contract specified deliverables in testable terms (e.g., "API passing OpenAPI 3.0 validation" not "identity system")
   - Actual deliverables match contract
   - Payment milestones tied to verifiable delivery events (Phase 0 report, sandbox launch, production go-live)

3. **Code audit:**
   - GitHub repository publicly accessible
   - Commits timestamped and attributed — cannot be backdated
   - No significant unexplained code that was not in the original scope
   - Security audit report published

4. **Operational expenditure:**
   - Server costs consistent with stated capacity
   - Staff costs consistent with stated team size
   - No unexplained vendor payments

**Key enabler:** The open-source mandate means OAG can hand the GitHub repository to any competent software engineer and ask "does this match what was paid for?" This is unprecedented for Nepali government IT. It converts a previously un-auditable domain into an auditable one.

---

### UC-06.2 — CIAA investigates suspected abuse of NID API access

**Trigger:** CIAA receives a complaint that a politically connected company received NID API approval for `kyc_photo` scope without legitimate justification, and has been querying citizen data without consent.

**Actor:** CIAA investigation officer

**Investigable evidence trail:**

1. **App registration record:** When was the app registered? Who reviewed the application? Which officer approved it? What was the stated justification for `kyc_photo` scope?

2. **Query audit log:** How many queries has this app made? Against which NIDs? Were all queries accompanied by valid consent tokens? Were consent tokens single-use (as designed)?

3. **Citizen complaints:** Have any citizens flagged unexpected queries from this app in the citizen portal (UC-01.2)?

4. **Consent token integrity:** Were consent tokens generated through the legitimate consent portal, or forged? (Cryptographically verifiable — tokens are signed with NID Authority's key)

5. **Officer trail:** Which MOICS officer approved the scope? Was that officer's approval consistent with the approval criteria matrix (UC-04.1)?

**If consent tokens were bypassed:**
The system is designed so that queries without a valid consent token return `{"error": "consent_token_required"}` — no data is returned. If a company is somehow receiving citizen data without consent, this represents a security breach, not just a policy violation. CIAA and Nepal Police Cybercrime Bureau would both be involved.

**CIAA access requirement:** CIAA must have the ability to formally request the full query audit log for a specific company and time period. This request process should be: written request → NID Authority legal review → disclosure within 10 working days. Not a real-time access portal — that would itself be a surveillance risk.

---

### UC-06.3 — Parliamentary committee questions NRB on sandbox outcomes

**Trigger:** Finance Committee of the House of Representatives holds a hearing on fintech regulatory developments. NRB Governor is called to testify.

**What the committee needs:**

1. **Sector overview:**
   - How many companies are in each tier?
   - What is the total monthly foreign currency inflow through the sandbox?
   - How does this compare to estimated informal hawala flows?
   - What is the AML flag rate and how many have resulted in FIU referrals?

2. **Consumer protection:**
   - Have any Nepali customers lost money due to a sandbox participant failure?
   - What is the redress mechanism if they do?
   - Has NRB's supervision model kept pace with sandbox growth?

3. **Public benefit test:**
   - Are small companies (< 5 employees) accessing the sandbox, or is it dominated by large incumbents?
   - Is the sandbox contributing to IT export growth?
   - What is the revenue collected by the government (tax on sandbox company income)?

4. **Risk register:**
   - Has the sandbox created any systemic risk NRB was not anticipating?
   - Are there corridors or business models NRB wishes it had excluded from the framework?

**NRB's preparation:** The annual transparency report (UC-05.4) is the primary source material for parliamentary testimony. If NRB publishes a thorough annual report, parliamentary hearings become a review exercise rather than a confrontation.

---

### UC-06.4 — Investigative journalist reports on NID API query volumes

**Trigger:** Journalist at Setopati or The Record is investigating whether a large bank has been querying citizen NID data in excess of what's needed for normal KYC operations.

**What is publicly available (by design):**
- The fact that the NID API exists and which companies are registered (company name, tier, approved scopes — not internal app keys)
- Aggregate monthly query volume statistics by category (not per-company)
- The NID Authority's annual transparency report
- The GitHub repository — all code is public

**What requires a formal FOI request:**
- Per-company query volumes (commercially sensitive but requestable by CIAA/OAG)
- Individual query logs (citizen privacy protection — only the citizen themselves can access their own log)

**What is never available:**
- Individual citizen query logs to journalists (privacy protection)
- Internal consent token data

**Journalist's path for this investigation:**
1. File RTI (Right to Information) request with MOICS for per-company aggregate query volumes
2. If NID Authority has published its annual transparency report, journalist has aggregate data already
3. Cross-reference with news: if Bank X has 500,000 customers but made 2,000,000 NID queries in a month, something is anomalous
4. File follow-up RTI for the specific approval that gave Bank X unrestricted query access

**Design principle:** The system should make this kind of journalism *possible*. The aggregate statistics and annual report are not just NRB governance tools — they are the raw material for civil society oversight.

---

### UC-06.5 — Digital rights NGO audits the consent mechanism

**Trigger:** A digital rights organisation (equivalent to Access Now or EFF) wants to verify that the citizen consent architecture works as described and is not trivially bypassable.

**Actor:** NGO technical researcher

**What they can do without any special access:**

1. **Read the source code:** GitHub repository is public. Researcher can verify:
   - Consent tokens are cryptographically signed (cannot be forged)
   - Consent tokens are single-use (replayed tokens are rejected)
   - Scope enforcement is implemented server-side (client cannot request more than consented)
   - Audit logs cannot be deleted (append-only design)

2. **Test the sandbox:** Using `dev_test_key`, researcher can verify:
   - Requesting data without a consent token returns an error
   - Using a consent token for a different scope than requested returns an error
   - Using an expired consent token returns an error
   - A consent token issued to App A cannot be used by App B

3. **Penetration test (with written permission from NID Authority):**
   - Attempt to forge consent tokens
   - Attempt to access data beyond the consented scope
   - Attempt to replay used consent tokens
   - Attempt SQL injection / API abuse

4. **Review the data protection framework:**
   - Is the data protection law in force?
   - Does it provide for penalties that are proportionate to the harm (not trivial fines)?
   - Is there a data protection commissioner with genuine independence?

**Design principle:** A system that can only be trusted because you believe the government's word is not a trustworthy system. The open-source design allows independent verification. The consent architecture is publicly documented. The penetration test pathway exists. These are not features added for auditors — they are features that make the system worth trusting in the first place.

---

### UC-06.6 — Citizen journalist documents the Phase 0 NID database audit findings

**Trigger:** MOICS publishes the Phase 0 audit report (as required by the open procurement mandate).

**What the report must contain:**
- Total NID records audited
- Data quality breakdown: % complete, % with missing fields, breakdown by field type and by district
- Security findings summary (critical findings redacted for security, but count and severity disclosed)
- Recommended remediation actions and estimated cost
- Timeline for remediation

**What civil society can do with this data:**
- Identify which districts have the worst NID data quality — advocate for targeted enrollment drives
- Understand the scope of the remediation problem — hold MOICS accountable to the timeline
- Compare subsequent quarterly updates against baseline — track whether data quality is actually improving

**Accountability mechanism:** The Phase 0 report creates a public baseline. Six months later, MOICS must publish a follow-up showing remediation progress. This is the accountability loop: baseline → action → verification → next baseline.

---

## System Design Requirements for Auditability

These are requirements that must be built into the system from the start. They cannot be retrofitted.

### Append-only audit logs
Every query, every consent grant, every admin action is written to an append-only log. No record can be deleted — only marked as superseded by a later record. This means: no covering up of past queries, even by system administrators.

### Cryptographically signed consent tokens
Consent tokens must be signed with the NID Authority's private key. Anyone with the public key (published) can verify a token's authenticity. This makes it technically impossible to fabricate a consent token — and technically provable that a given query was legitimately consented to.

### Public GitHub repository with commit history
All source code, from the first commit, publicly visible. Commits timestamped by GitHub's servers — cannot be retrospectively altered. Security-sensitive configuration (API keys, credentials) must never be committed — enforced by automated scanning.

### Annual transparency report (mandatory, not discretionary)
NID Authority and NRB both publish annual reports. Publication is required by the circular/regulation — it is not left to the discretion of the secretary or governor. Reports include: total queries, total participants, AML actions, citizen complaints and outcomes, data quality improvement metrics.

### Third-party security audit before Phase 3 launch
Before the ecosystem is opened to all registered companies, an independent security audit must be conducted. Findings (excluding exploitable details) published publicly. This is the most expensive auditability feature (~NPR 3–5M) and the most important.

---

## Acceptance Criteria (Oversight Perspective)

- [ ] GitHub repository public from first commit — no private development period
- [ ] Phase 0 audit report published within 2 weeks of completion
- [ ] Annual transparency report published by both NID Authority and NRB — first report due 12 months after production launch
- [ ] RTI response time for aggregate query data: 10 working days
- [ ] Audit log records retained for minimum 7 years
- [ ] Consent tokens cryptographically signed and publicly verifiable
- [ ] Third-party security audit completed and summary published before Phase 3 ecosystem launch
- [ ] CIAA formal request pathway documented and response SLA (10 working days) committed in circular
- [ ] Sandbox company register (names, tiers, approved scopes) publicly accessible — not just available on request

---

*Document version: 0.1 · System: NID API + NRB Sandbox · Related: UC-04 (Government Officer), UC-05 (NRB Regulator)*
