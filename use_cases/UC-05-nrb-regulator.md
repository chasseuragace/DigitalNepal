# UC-05 — NRB as Regulator
**Nepal Digital Infrastructure · Use Case Document**
*Nepal Rastra Bank · Financial Intelligence Unit · Fintech Supervision Division*

---

## User Profile

| | |
|---|---|
| **Who** | NRB officers responsible for fintech licensing, AML compliance, FX regulation, and systemic risk monitoring |
| **Divisions** | Fintech Supervision Division · Financial Intelligence Unit (FIU) · Foreign Exchange Management Department · Payment Systems Department |
| **Motivation** | Expand formal financial sector without creating systemic risk or enabling money laundering |
| **Current pain** | No visibility into informal payment channels · Cannot supervise fintech at scale with current manual processes · FX rules written for a pre-digital era |
| **Key concern** | "If we open this up and something goes wrong, the Governor will be blamed." |
| **Secondary concern** | "How do we supervise 500 companies when we currently struggle to supervise 50 banks?" |

NRB's role in this system is fundamentally different from all other user types. NRB is not a consumer of the API — NRB is the *authority* that makes the NRB sandbox legally operational. Without a specific circular from NRB's Foreign Exchange Management Department, every transaction through the sandbox is technically in violation of the Foreign Exchange (Regulation) Act 2019. This is why the political mandate (finance minister directive) is the most critical dependency in the entire roadmap.

The secondary concern — supervision at scale — is actually the strongest argument for the sandbox. The sandbox provides NRB with more visibility into fintech transactions than they currently have for informal channels. It is, paradoxically, a supervision tool as much as a business enablement tool.

---

## Use Cases — NRB Fintech Supervision

---

### UC-05.1 — NRB issues the sandbox circular

**Trigger:** Finance ministry directive instructing NRB to issue fintech sandbox regulatory framework.

**Actor:** NRB Governor's Office · Foreign Exchange Management Department · Legal Division

**This is a regulatory action, not a software action. The steps are:**

1. **Legal review** (Month 1–2): NRB Legal Division drafts circular language within existing Foreign Exchange (Regulation) Act 2019 — sandbox operates as a "regulatory exemption" framework under Section 36 (regulatory discretion clause) rather than requiring amendment of the Act
2. **Stakeholder consultation** (Month 2–3): Draft shared with Nepal Bankers' Association, fintech associations, selected startups for comment
3. **Board approval**: NRB Board formally approves circular
4. **Publication**: Circular published in Nepal Gazette — legal force from publication date

**Circular must specify:**
- Definition of "sandbox participant" — who qualifies
- Tier definitions (Tier 1: test-only, Tier 2: up to NPR 5M/month, Tier 3: full license)
- Approved payment corridors per tier
- Repatriation requirements (90 days)
- Reporting obligations (monthly to NRB)
- AML obligations (FIU notification thresholds)
- Grounds for suspension or termination
- Graduation path from sandbox to full fintech license

**Key drafting principle:** The circular must define thresholds in NPR, not USD — to avoid exchange-rate-linked ambiguity. "NPR 5,545,000 per month" (equivalent to $41,700 at March 2026 rate), with an annual review mechanism to adjust.

---

### UC-05.2 — NRB reviews a Tier 2 license application

**Trigger:** A sandbox company with 90+ days of clean Tier 1 transaction history applies for Tier 2 upgrade.

**Actor:** NRB Fintech Supervision Division officer

**Main flow:**
1. Application received via NRB admin portal — includes 90-day Tier 1 transaction report
2. Officer reviews:
   - **Volume profile:** Is transaction growth consistent with stated business model?
   - **AML performance:** What % of transactions were flagged? How were flags handled?
   - **Director NID:** Verified status — still active?
   - **Repatriation compliance:** Were all test repatriations completed within the 90-day window?
   - **Customer base:** B2B (lower risk) vs B2C (higher risk, more AML exposure)
3. Officer checks Financial Intelligence Unit database — director/company not on watchlists
4. If clean: Tier 2 approved with conditions:
   - Monthly transaction report due by 7th of following month
   - FIU notification required for any single transaction > $10,000
   - AML escalation protocol submitted and approved
5. If concerns: request for additional information (14-day response window)
6. If rejected: written reason, 30-day appeal period

**Review SLA:** NRB commits to a decision within 10 working days of complete application. This SLA must be written into the circular — without it, NRB can indefinitely stall approvals (the historical pattern).

---

### UC-05.3 — NRB FIU investigates a suspicious transaction pattern

**Trigger:** AML engine flags a pattern: a Tier 2 company has 8 transactions of $9,400–$9,800 across 10 days.

**Actor:** NRB Financial Intelligence Unit (FIU) officer

**Main flow:**
1. AML engine generates alert: `structuring_risk` flag on 8 transactions, same company, same approximate amount
2. FIU officer receives alert in FIU dashboard
3. Officer pulls full transaction history for the company:
   - Transaction IDs, timestamps, amounts, descriptions, corridors
   - Counterparty details (as available from corridor provider)
4. Officer assesses: is this structuring (deliberate fragmentation to avoid $10,000 reporting threshold)?
5. **Structuring confirmed path:**
   - Transactions placed `under_review` — frozen pending investigation
   - Company's Tier 2 access suspended
   - FIU files Suspicious Transaction Report (STR) with Nepal FIU
   - Director's NID flagged — `nid_status` change triggers alert to NID authority
6. **Benign explanation path:**
   - Company provides explanation (e.g., multiple subscription payments from the same client, each below $10,000 because that's the Stripe charge limit for the pricing tier)
   - FIU reviews — if satisfactory, transactions cleared, access restored
   - Flag recorded in company file for future monitoring

**Key data requirement:** The NRB sandbox must retain transaction records for minimum 5 years — the standard AML retention period under Nepal's Asset (Money) Laundering Prevention Act 2008.

---

### UC-05.4 — NRB monitors systemic risk across the entire sandbox

**Trigger:** Monthly NRB board meeting requires a fintech sector overview.

**Actor:** NRB Fintech Supervision Division chief

**Dashboard data required:**

| Metric | Frequency | Alert threshold |
|---|---|---|
| Total inbound USD across all Tier 2/3 participants | Real-time | N/A (monitoring only) |
| Total participants by tier | Daily | N/A |
| AML flag rate across ecosystem | Weekly | > 5% triggers review |
| Repatriation compliance rate | Monthly | < 95% triggers review |
| New Tier 1 registrations | Weekly | Sudden spike may indicate coordination |
| Corridor breakdown (Stripe vs Wise vs Payoneer) | Monthly | Single corridor > 80% = concentration risk |
| Failed/rejected payments by corridor | Daily | Corridor issue detection |

**Systemic risk flag:** If total sandbox inbound volume exceeds 0.5% of monthly formal remittance inflow, NRB board is briefed — not to restrict, but to assess whether sandbox limits need adjustment.

**Annual report:** NRB publishes an annual fintech sandbox report — total participants, total volume, AML actions taken, corridor performance. This transparency is explicitly part of the sandbox framework design and builds public trust.

---

### UC-05.5 — NRB suspends a sandbox participant for non-compliance

**Trigger:** Tier 2 participant fails to submit monthly report 3 months in a row.

**Actor:** NRB Fintech Supervision Division

**Main flow:**
1. System auto-sends warning after first missed report (Day 8)
2. System auto-sends second warning after second missed report (Day 38)
3. After third missed report: Supervisor reviews — is this a technical issue or deliberate?
4. Technical issue (company's system broken): 14-day grace period + technical assistance offer
5. Deliberate non-compliance: Access suspended — company can still view their data but cannot process new transactions
6. Written notice issued with 30-day remedy period
7. If no remedy: Tier 2 license revoked, company returned to Tier 1 (test-only)
8. Serious violations (fraud, AML evasion): Permanent ban + referral to cybercrime unit

**Graduated response principle:** Suspension is the last resort, not the first. NRB's goal is a thriving formal fintech sector, not a gatekeeping exercise. The graduated response — warning, grace period, suspension, revocation — reflects this.

---

### UC-05.6 — NRB publishes the exchange rate and calibrates conversion

**Trigger:** Daily NRB mid-rate publication.

**Actor:** NRB Foreign Exchange Management Department (automated)

**Main flow:**
1. NRB publishes daily mid-rate at 09:00 Nepal Standard Time
2. NRB sandbox system fetches updated rate automatically
3. All sandbox simulations from 09:00 use the new rate
4. Rate visible at `GET /v1/nrb/exchange_rate` — buy rate, sell rate, mid-rate
5. Historical rates retained in sandbox for 1 year — companies can reconcile past transactions

**NRN remittance pricing note:** The sandbox uses NRB mid-rate for simulations. In production, actual corridor providers (Wise, Payoneer, Stripe) set their own rates. The sandbox should document this distinction clearly — the NPR amount in a simulation will differ from the actual NPR amount received via a live Wise transfer.

---

## What NRB Gets From This System (The Supervision Argument)

This is the framing that convinces a conservative NRB governor. The sandbox is not about removing NRB's control — it increases NRB's visibility.

| Today (informal channels) | With NRB sandbox |
|---|---|
| NRB has zero visibility into hawala flows | Every transaction logged and visible to NRB |
| No AML checks on informal payments | AML rules engine on every transaction |
| Cannot track which companies receive foreign payments | Full company register with NID-verified directors |
| Cannot measure fintech sector size | Real-time dashboard of sector volume |
| Developers use workarounds NRB can't audit | All activity within NRB's supervised framework |
| Tax evasion on foreign income common | IRD can see sandbox transactions — income traceable |

The informal channel is the alternative to the sandbox — not the absence of fintech. The choice is between supervised fintech with an audit trail, and unsupervised fintech with no audit trail. This framing must be in every conversation with NRB leadership.

---

## NRB Capacity Requirements

The sandbox creates new supervisory obligations. NRB must plan for:

| Function | Current staffing | Additional needed |
|---|---|---|
| Tier 2/3 application review | 0 (no sandbox today) | 2 officers |
| Monthly report review | 0 | 1 officer (automated tools do the bulk) |
| FIU AML monitoring | Existing FIU team | 1 dedicated fintech analyst |
| Technical sandbox operation | 0 | 1 technical officer (liaison with MOICS/vendor) |
| Annual report + policy | 0 | 0.5 FTE (existing staff part-time) |

Total: approximately 4–5 additional staff. This is not a large ask. For context, the UK's FCA sandbox team was 12 people managing 500+ firms.

---

## Acceptance Criteria (NRB Regulator Perspective)

- [ ] Circular drafted and legally reviewed within 60 days of Cabinet directive
- [ ] NRB board approval process completed within 90 days of Cabinet directive
- [ ] Tier 2 application SLA of 10 working days written into circular — legally binding
- [ ] FIU alert system operational on Day 1 of Tier 2 launch
- [ ] All transaction records retained for minimum 5 years
- [ ] Monthly sector dashboard available to NRB board
- [ ] Annual public transparency report committed to in circular
- [ ] NRB has ability to suspend any participant unilaterally within 1 hour via admin panel
- [ ] Corridor provider (Stripe/Wise/Payoneer) data-sharing agreements signed before Tier 3 launch

---

*Document version: 0.1 · System: NRB Sandbox · Related: UC-02 (Financial Institution), UC-03 (Developer/Fintech), UC-06 (Auditor/Oversight)*
