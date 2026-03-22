# Nepal Digital Foundation
## A pitch to the RSP team
### Two systems · 18 months · NPR 98–137M · Everything else becomes possible

---

---

# Slide 1 — The one sentence

> "I built a working prototype of the two digital systems that make every other promise in your bacha patra actually possible to deliver."

---

---

# Slide 2 — The problem

## Your manifesto promises cannot be delivered without this

| Promise (bacha patra) | What it requires that doesn't exist |
|---|---|
| One-stop investment portal (point 24) | A way to verify investor identity digitally |
| Cooperative reform (points 29–31) | A way to verify member identity across cooperatives |
| Agricultural land consolidation (point 43) | Verified digital land ownership linked to real people |
| IT and knowledge export (point 35) | A legal way for software companies to receive foreign payments |
| Borderless/weightless trade (point 35) | International payment gateways accessible to Nepali companies |
| Digital e-governance (point 9) | A single citizen login that works across all government portals |

**None of these are possible without two things:**
1. A digital identity layer — knowing who a citizen actually is
2. A legal payment layer — allowing software companies to receive foreign revenue

**Both of these are missing today. This prototype builds them.**

---

---

# Slide 3 — What Nepal has today

## The starting point is worse than most people realise

```
Internet:        ~95% transits through India (BSNL/Airtel)
                 Zero independent submarine cable access

Data centres:    3 small Tier-1/2 DCs in Kathmandu
                 No Tier-3 certified facility in Nepal

NID system:      Card exists. Database exists.
                 Zero APIs. Zero digital verification.
                 ~40% of records have incomplete data.

Payment access:  Stripe — blocked
                 PayPal — blocked
                 Wise — grey zone
                 20,000 engineers routing payments
                 through Indian accounts or hawala

Software cos:    Cannot legally receive foreign revenue
                 No receipts. No tax trail. No scale.
```

**The informal channel is the alternative — not "nothing".**
Hawala, Indian bank accounts, grey-zone routing — this exists today at scale.
The question is whether Nepal wants it supervised or unsupervised.

---

---

# Slide 4 — What we are building (not what we are talking about)

## This is already running. On a laptop. Right now.

```
nepal_digital_prototype/
├── NID API          — identity verification system
│   ├── /verify      — is this NID valid? (boolean only)
│   ├── /kyc_basic   — name, DOB, address (citizen-consented)
│   ├── /kyc_photo   — biometric face match
│   └── /login       — SSO across all government portals
│
└── NRB Sandbox      — fintech payment sandbox
    ├── /register    — company onboarding (instant for Tier 1)
    ├── /simulate    — test foreign payment + AML check
    ├── /transactions — transaction history
    └── /aml/check   — AML rules engine
```

**19 tests. 19 passing.**
Built on Python + Flask. Open source. No external dependencies.
Runs with: `pip install flask && python app.py`
Swagger UI at: `http://localhost:5000/docs`

---

---

# Slide 5 — The NID API: what it does

## National Identity as a Service

**The core design principle:**
The NID database already exists. We are not rebuilding it.
We are building a consent-controlled API layer on top of it.

```
                    ┌─────────────────────────┐
Bank / Cooperative  │                         │
Govt Portal    ───▶ │   API Gateway           │
Fintech App         │   OAuth 2.0 / PKCE      │──▶  NID
Developer           │   Consent enforcement   │     Database
                    │   Rate limiting         │     (read-only)
                    │   Audit logging         │
                    └─────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Citizen decides  │
                    │  who gets what    │
                    └───────────────────┘
```

**Four scopes — four levels of access:**

| Scope | What is returned | Who can use it |
|---|---|---|
| `verify` | Valid: yes/no. Nothing else. | Any registered company |
| `kyc_basic` | Name, DOB, address | Companies with KYC justification |
| `kyc_photo` | Biometric face match result | Banks and financial institutions only |
| `citizen_login` | Session token. Zero data. | Any registered company |

**The citizen controls every query.**
No consent token = no data. This is enforced at the API layer, not in policy.

---

---

# Slide 6 — The NID API: live demo

## What you will see when I open the laptop

**Test 1 — Valid NID:**
```json
POST /v1/nid/verify
Bearer: dev_test_key
X-Consent-Token: ct_verify_ram

→ { "valid": true, "nid_status": "active" }
```

**Test 2 — Suspended NID (a bank cannot open an account for this person):**
```json
X-Consent-Token: ct_verify_suspended

→ { "valid": false, "nid_status": "suspended" }
```
*No bribe is possible. The system enforces it.*

**Test 3 — Data quality warning (40% of Nepal's NID records look like this):**
```json
POST /v1/nid/kyc_basic
X-Consent-Token: ct_kyc_bikash

→ {
    "data": { "full_name": "Bikash Raj Adhikari", "dob": "1979-12-03" },
    "data_quality_warnings": ["missing_tole", "missing_phone"]
  }
```
*The system is honest about what it doesn't know.*

**Test 4 — AML flag (structuring risk):**
```json
POST /v1/nrb/aml/check
{ "amount_usd": 9500 }

→ { "aml_status": "flagged", "compliance_flags": ["structuring_risk", "high_value"] }
```
*Every transaction checked automatically. No officer required.*

**Test 5 — Company registered in 30 seconds:**
```json
POST /v1/nrb/companies/register
{ "company_name": "My Startup Pvt Ltd", "director_nid": "1234-5678-9012",
  "business_model": "saas_export", "requested_tier": "tier_1" }

→ { "sandbox_key": "sk_test_np_my_startup_...", "tier": "tier_1", "status": "active" }
```
*Today this takes 6 months and a lawyer.*

---

---

# Slide 7 — The NRB Sandbox: what it does

## Making foreign payments legal — not theoretical

**The current reality for 20,000 Nepali software engineers:**

```
Nepali engineer ships software to US client
         │
         ▼
Client pays via Stripe
         │
         ▼  ← BLOCKED. Stripe not available in Nepal.
         │
Engineer uses friend's Indian bank account
         │
         ▼
Money arrives in India
         │
         ▼
Hawala brings cash to Kathmandu
         │
         ▼
No receipt. No tax trail. Cannot scale. Technically illegal.
```

**The sandbox replaces this with:**

```
Nepali company registered in NRB sandbox (30 seconds)
         │
         ▼
Client pays via Stripe / Wise / Payoneer
         │
         ▼
AML check runs automatically on every transaction
         │
         ▼
NPR conversion at NRB mid-rate
         │
         ▼
Repatriation within 90 days
         │
         ▼
Receipt generated. IRD can see income. Tax filed. Company can scale.
```

**Three tiers — graduated risk:**

| Tier | Approval | Limit | Corridors |
|---|---|---|---|
| Tier 1 | Instant, automatic | Test only | Mock (sandbox) |
| Tier 2 | NRB review, 2–5 days | $41,700/month (~NPR 5.5M) | Wise + Payoneer |
| Tier 3 | After 3 months Tier 2 | Unlimited | Stripe + Swift + all |

---

---

# Slide 8 — Why this costs less than you think

## Total investment: NPR 98–137 million over 18 months

```
NID API
  Phase 0 — database audit          NPR  8–12M   (3 months)
  Phase 1 — core API + sandbox      NPR 35–50M   (6 months)
  Phase 2 — consent + biometric     NPR 25–35M   (6 months)
  Phase 3 — ops Year 1              NPR 10–15M   (ongoing)

NRB Sandbox
  Regulatory track                  NPR   ~5M    (mostly people, not software)
  Platform build                    NPR 15–25M   (6 months)
  Operations + compliance           NPR  ongoing

TOTAL                               NPR 98–137M  (18 months)
```

**For context:**

| Comparison | Cost |
|---|---|
| 1 km of Kathmandu ring road | NPR 200–300M |
| Both systems combined | NPR 98–137M |
| Annual maintenance of one stalled hydropower project | > NPR 200M |
| Pakistan SaaS sandbox (comparable) | ~NPR 150M equivalent |
| India Aadhaar API (2010–2012 build) | ~NPR 2B equivalent |

**Nepal builds on 15 years of Aadhaar lessons — at 7% of the cost.**

---

---

# Slide 9 — The roadmap (honest version)

## What happens when, and what blocks what

```
MONTH    1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18
─────────────────────────────────────────────────────────────────────────────────

GOVERNANCE
Cabinet mandate      [===]
NRB circular         [===|====]
Data protection law  [=========|====|==]

NID API
Phase 0 audit        [=======]
Phase 1 core API               [===========]          ◆ 3 banks live
Phase 2 consent                             [===========]
Phase 3 ecosystem                                        [===========] ◆ open

NRB SANDBOX
Regulatory draft     [===|====]
Tier 1 sandbox                 [=======]   ◆ devs
Tier 2 live FX                             [=========]
Tier 3 + Stripe                                         [=========] ◆ Stripe NP

UNLOCKS
Cooperative KYC                                    [===========]
Investment portal                                      [=========]
IT export economy                                           [=======]

RISK WINDOWS
⚠ NRB stall risk         [===|====]  ← finance minister must act here
⚠ NID data quality       [===|====]  ← Phase 0 defines the true scope
⚠ Procurement capture    [=======]   ← open tender + public GitHub mandatory
```

**Critical path item:** The entire roadmap depends on a Cabinet directive in Month 1 naming MOICS (NID API) and NRB (sandbox) as accountable owners with named individuals. Without this, nothing moves.

---

---

# Slide 10 — What we are asking for

## Three asks. Total cost of the asks: zero.

---

### Ask 1 — A meeting (not a decision)

Arrange a technical briefing with:
- NRB Governor's office
- IT Secretary (MOICS)
- A 4-person technical team from each

**Purpose:** Share this prototype. Get their response.
**Cost:** One afternoon.
**Risk:** None.

---

### Ask 2 — Named ownership in the 100-day plan

Include in the 100-day action plan:
- "NID API: owned by MOICS, Director [name], Phase 0 tender published by Day 60"
- "NRB Sandbox: owned by NRB, Deputy Governor [name], circular drafted by Day 45"

**Why this matters:** Without named individuals, no one is accountable.
Every Nepali government IT project that failed, failed here.
**Cost:** Zero.
**Risk:** Zero.

---

### Ask 3 — NPR 5 million for Phase 0

A small, open tender for a 4-person team to audit the NID database.
3 months. Public GitHub. Output: a published data quality report.

**Why Phase 0 first:** You cannot build an API on a database you haven't audited.
The Phase 0 report creates the first public accountability baseline.
**Cost:** NPR 5M (can be approved by IT secretary — does not require Cabinet).
**Timeline:** Can begin within 30 days of mandate.

---

---

# Slide 11 — What the system does for each stakeholder

## Every person in this room has a constituent who benefits

| Stakeholder | Before | After |
|---|---|---|
| **Citizen applying for a bank account** | 45 minutes at a branch with photocopies | 30 seconds digital verification |
| **Cooperative secretary** | Cannot verify if a member has loans elsewhere | NID-linked member identity — cross-cooperative visibility possible |
| **Nepali software engineer** | Routes revenue through India via hawala | Legal Stripe/Wise access, receipts, tax trail |
| **NRN sending remittances** | Pays 5–8% fees via informal channels | Regulated corridor, lower fees, NID-verified recipient |
| **Bank loan officer** | Manual document check, fraud risk | Biometric-grade KYC in under 1 minute |
| **CIAA investigator** | Government IT is a black box | Open-source code, full audit trail, named officer on every action |
| **IRD tax collector** | Foreign IT income invisible | All sandbox transactions visible — income traceable |
| **Citizen worried about surveillance** | No idea who is looking at their data | SMS notification on every query, revocable consent, query log |

---

---

# Slide 12 — Why open source matters here specifically

## This is not a technical preference. It is an anti-corruption decision.

Every Nepali government IT project in the last 20 years has shared three properties:
1. Closed source — no one outside could verify what was built
2. Inflated contracts — no way to compare what was paid vs. what was delivered
3. No accountability — when it failed, no individual was responsible

**This project will be different in three ways:**

**Public GitHub from day one.**
Every commit timestamped. Every line of code visible.
Any journalist, OAG auditor, or CIAA officer can hand it to an engineer and ask:
*"Does this match what was paid for?"*
For the first time in Nepali government IT history, the answer is checkable.

**Milestones tied to verifiable deliverables.**
Payment on Phase 0: when audit report is published.
Payment on Phase 1: when API passes OpenAPI validation and 3 pilot banks are live.
Not on "completion of identity system." On a specific, testable outcome.

**Named individuals accountable.**
MOICS Director owns the NID API.
NRB Deputy Governor owns the sandbox.
If either is not delivered, we know who did not deliver it.

---

---

# Slide 13 — The comparison that matters

## Pakistan vs Nepal — same problem, different response

| | Pakistan (2021) | Nepal (today) |
|---|---|---|
| **Problem** | Engineers routing payments through informal channels | Same |
| **Action taken** | SBP issued fintech sandbox circular | Circular discussed since 2019. Not issued. |
| **Finance minister involvement** | Explicit public statement backing sandbox | Needed. Not yet done. |
| **Time from circular to Stripe** | 14 months | — |
| **Result** | Stripe now available in Pakistan | Stripe still blocked in Nepal |

**The difference was not technical. The difference was political will.**
SBP (Pakistan's equivalent of NRB) was as conservative as NRB.
The finance minister's statement changed the political calculus.
One statement. 14 months. Stripe in Pakistan.

**Nepal is 14 months away from the same outcome.**
The circular language is drafted. The sandbox is built.
The only missing ingredient is the same one Pakistan had.

---

---

# Slide 14 — The four honest risks

## Saying these out loud is part of the pitch

---

**Risk 1 — NID data quality (HIGH)**
~40% of NID records are expected to have incomplete data.
Phase 0 will tell us exactly how bad it is.
This adds 2–3 months and NPR 10–15M if severe.
It does not stop the project — it scopes it correctly.

---

**Risk 2 — NRB institutional resistance (HIGH)**
NRB has discussed a fintech sandbox since 2019. Nothing happened.
The finance minister must issue a directive before Month 1.
Without it, the NRB sandbox track stalls indefinitely.
This is the single most likely failure mode for the entire roadmap.

---

**Risk 3 — Procurement capture (MEDIUM)**
Both systems combined are ~NPR 130M in contracts.
Nepal's IT procurement history has significant problems.
Mitigation: open-source mandate written into tender specifications.
Public GitHub means any engineer can audit what was delivered.

---

**Risk 4 — No data protection law (MEDIUM)**
Without it, the consent architecture is good intentions — not enforceable rights.
The ordinance must be drafted in parallel with the build.
Not in Year 2. In Month 1.

---

---

# Slide 15 — What success looks like in 18 months

## Measurable. Not aspirational.

**NID API:**
- [ ] Phase 0 audit report published publicly
- [ ] 3 pilot banks live on production NID API (end of Month 9)
- [ ] 10 cooperative KYC integrations live (end of Month 12)
- [ ] NID API ecosystem open to all registered companies (end of Month 18)
- [ ] Data protection ordinance enacted (Month 10–11)

**NRB Sandbox:**
- [ ] Sandbox circular published in Nepal Gazette (Month 3–5)
- [ ] Tier 1 sandbox open to all Nepali developers (Month 7)
- [ ] Tier 2 live — real FX via Wise and Payoneer (Month 8–12)
- [ ] Stripe accessible in Nepal (Month 15–16)

**Downstream effects (not guaranteed, but likely):**
- IRD begins seeing IT export income in tax filings for the first time
- Cooperative KYC fraud materially reduced — member identity verified
- NRN remittance through formal channels increases as friction reduces
- Nepal's ranking on World Bank Doing Business Index improves (digital registration)

**The number that matters in 5 years:**
Every NPR 1 invested in this infrastructure generates tax-visible IT export revenue.
That is the multiplier that makes the $100 billion economy argument real —
not the hydropower projects, not the data centres.
The digital identity and payment foundation that lets a Nepali engineer
get paid legally for software they write is the actual engine.

---

---

# Slide 16 — The ask, one more time

## Simple. Specific. Actionable today.

---

> **Ask 1:** Arrange a technical meeting with NRB and MOICS.
> Show them the prototype. Get their response.

---

> **Ask 2:** Name owners in the 100-day plan.
> MOICS owns the NID API. NRB owns the sandbox.
> Named individuals. Named deadlines.

---

> **Ask 3:** Approve NPR 5M for Phase 0.
> Open tender. 4-person team. 3 months.
> Published audit report. Public GitHub from day one.

---

### The prototype is built.
### The roadmap is written.
### The use cases are documented.
### The code is ready to hand to NRB's technical team today.

**The ball is in your court.**

---

---

*Pitch deck version: 0.1 · March 2026*
*Working prototype: Python/Flask · 19/19 tests passing · Available for technical review*
*Full documentation: roadmap · use cases (6 user types, 33 use cases) · API specification*
