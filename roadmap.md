# Nepal Digital Infrastructure — Tentative Roadmap
**NID API (Priority 1) + NRB Fintech Sandbox (Priority 2)**
*18-month delivery plan · All dates tentative · Political mandate is the critical path*

---

## Summary

| | Detail |
|---|---|
| Total budget | NPR 98–137 million |
| Duration | 18 months |
| Systems | NID API + NRB Fintech Sandbox |
| Owner (NID) | Ministry of Communication & IT (MOICS) |
| Owner (NRB) | Nepal Rastra Bank |
| Prerequisite | Cabinet directive with named ministry ownership |

---

## Governance & Mandate

### Months 1–3 — Political setup
- Cabinet directive issued naming MOICS (NID API) and NRB (sandbox) as accountable owners
- Open tender drafted for NID Phase 0 audit team (4-person, 3-month contract)
- Finance minister issues public statement backing NRB sandbox circular — this is the single most important political action in the entire roadmap

### Months 1–2 — Procurement
- Open tender specification published (mandate public GitHub repository requirement)
- Technical evaluation committee formed with private sector members
- Vendor selected via transparent scoring

### Months 1–11 — Data Protection Law *(parallel track)*
- **Months 1–5:** Draft data protection ordinance through parliament
- **Months 6–9:** Public consultation and revision
- **Month 10–11:** Enacted into law

> **Why this cannot wait:** Without legal teeth around citizen consent, the NID API's privacy architecture is good intentions, not enforceable rights. India built Aadhaar without this and spent years retrofitting protections. Nepal can avoid that mistake by drafting in parallel with the build.

---

## NID API — National Identity as a Service

### Phase 0 · Months 1–3 · NPR 8–12M
**NID Database Audit & Schema Mapping**

- Audit existing NID database schema — field types, completeness, encoding consistency
- Security penetration test of existing NID infrastructure
- Define canonical data model for API output
- Draft consent framework and legal basis
- Produce data quality report

**Team:** 2 senior engineers + 1 legal + 1 security specialist

> ⚠️ **Risk — Data Quality:** Approximately 40% of Nepal's NID records are expected to have inconsistent romanization, missing ward numbers, or mismatched DOB vs. certificate data. If the audit confirms this, a data remediation workstream adds 2–3 months and NPR 10–15M to Phase 1. This is not a reason to stop — it is a reason to scope Phase 0 seriously.

---

### Phase 1 · Months 4–9 · NPR 35–50M
**Core API + Developer Sandbox**

**What gets built:**
- OAuth 2.0 / PKCE authentication server
- Three production endpoints:
  - `POST /v1/nid/verify` — boolean validity check only
  - `POST /v1/nid/kyc_basic` — name, DOB, gender, address (consent-gated)
  - `POST /v1/nid/citizen_login` — SSO session token, no data returned
- Rate limiting: 1,000 requests/minute per app key
- Audit logging: every query logged with purpose, app ID, timestamp
- Developer portal with sandbox mode (fake NIDs, mock responses)
- Citizen consent portal (web) — citizen approves scope per app

**Team:** 6 engineers + 1 PM + 1 security lead

**Stack:** Go or Node.js API · PostgreSQL audit DB · Redis rate limiter · Keycloak OAuth

**Deployment:** On-prem NTC datacenter with cloud backup

**🔷 Milestone — End of Month 9:** 3 pilot banks live on production NID API

---

### Phase 2 · Months 9–14 · NPR 25–35M
**Consent Portal + Biometric + 10 Pilot Apps**

**What gets built:**
- Granular citizen consent UI — citizen sees exactly which app requested what data
- Citizen data access log — "who has queried my NID and when"
- `POST /v1/nid/kyc_photo` — biometric face match against NID photo store
- Mobile-optimised consent flow
- Onboard 10 pilot integrations: banks, fintech apps, cooperative KYC systems

**Team:** Same core team + 2 mobile developers + 1 UX designer

> ⚠️ **Risk — Photo Quality:** The biometric endpoint depends on photo quality in the existing NID records. Citizens without photos on file (~est. 15–20%) will need to visit enrollment centres. Surface `data_quality_warnings` in API responses so consuming apps handle this gracefully.

---

### Phase 3 · Months 13–18 · NPR 10–15M (operations Year 1)
**Ecosystem Open — Any Registered Company**

**What changes:**
- Public API documentation (OpenAPI 3.0 spec on GitHub)
- Self-service app registration portal for developers
- Tiered access: sandbox free and instant · production requires approval
- SLA: 99.9% uptime · < 200ms p95 latency
- Data protection regulation now in force — consent framework has legal teeth

**🔷 Milestone — End of Month 18:** NID-as-a-service fully live · Any registered Nepali company can build identity verification, KYC, or citizen login features

---

## NRB Fintech Sandbox

### Months 1–5 — Regulatory Track · NPR ~5M (mostly people, not software)

**Month 1–2:** Draft FX rule changes as NRB circulars:
- Rule 1: Registered sandbox companies may receive USD/EUR via virtual accounts
- Rule 2: Repatriation within 90 days via approved corridors (Wise, Payoneer, Stripe)
- Rule 3: Software/SaaS revenue classified as "service export" — no import duty
- Rule 4: Monthly caps: $41,700/month (Tier 2), unlimited (Tier 3)

**Month 3–5:** Cabinet + NRB sign-off

> ⚠️ **Risk — NRB Institutional Resistance:** NRB has discussed a fintech sandbox since 2019 without acting. The finance minister must issue a directive making it politically costly to delay. Pakistan's SBP sandbox circular came with an explicit finance minister statement — Nepal needs the same. This is the single most likely thing to derail the entire sandbox track.

---

### Tier 1 Sandbox · Months 4–7 · NPR 15–25M
**Developer Portal + Mock Payment Rails**

**What gets built:**
- Company registration portal — instant approval for Tier 1, no NRB sign-off needed
- Director identity verified via NID API (live integration)
- Simulated payment rails: mock Stripe, Wise, Payoneer API responses
- AML rules engine running on every simulated transaction
- Monthly reporting dashboard auto-generates NRB compliance reports

**🔷 Milestone — End of Month 7:** Tier 1 sandbox open to all Nepali developers

---

### Tier 2 Live · Months 8–12
**Real FX — Wise + Payoneer Corridors Active**

- NRB-approved companies transact real foreign payments up to $41,700/month
- AML engine runs live — flags structuring risk, high-value transactions
- Repatriation tracking with 90-day deadline enforcement
- Tier 2 companies can apply for Stripe corridor addition

---

### Tier 3 + Stripe · Months 12–16
**Unlimited, Full Corridor Access**

- Stripe, Swift, Wise, Payoneer all active
- No monthly cap for Tier 3 licensed companies
- Full NID KYC integration at onboarding (kyc_basic + kyc_photo)
- NRN (Non-Resident Nepali) companies can register remotely

**🔷 Milestone — End of Month 15:** Stripe accessible in Nepal · Nepali SaaS companies can legally charge foreign clients

---

## What Gets Unlocked (Dependent Systems)

These systems cannot be built until the foundations above exist. They are listed here to show *why* the NID API and NRB sandbox are prerequisites — not nice-to-haves.

| System | Depends on | Earliest start |
|---|---|---|
| Cooperative member KYC | NID API Phase 1 live | Month 9 |
| One-stop FDI investment portal | NID API Phase 1 + NRB Tier 2 | Month 10 |
| Digital land registry (pilot) | NID API Phase 2 (kyc_photo) | Month 14 |
| IT export economy (SaaS revenue) | NRB Tier 3 + Stripe | Month 16 |
| Agricultural fintech / crop insurance | NID API ecosystem open | Month 18+ |

---

## Budget Summary

| Track | Phase | Timeline | Cost (NPR M) |
|---|---|---|---|
| NID API | Phase 0 — audit | M1–3 | 8–12 |
| NID API | Phase 1 — core build | M4–9 | 35–50 |
| NID API | Phase 2 — consent + biometric | M9–14 | 25–35 |
| NID API | Phase 3 — ops Year 1 | M13–18 | 10–15 |
| NRB Sandbox | Regulatory track | M1–5 | ~5 |
| NRB Sandbox | Platform build | M4–12 | 15–25 |
| NRB Sandbox | Operations + compliance | M8–18 | ongoing |
| **Total** | | **18 months** | **98–137** |

> For context: one kilometre of Kathmandu ring road costs approximately NPR 200–300 million. Both systems combined cost less than half a kilometre of road — and they unlock the digital economy for an entire generation of Nepali entrepreneurs and engineers.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| NID DB data quality (~40% incomplete records) | High | Scope + cost increase | Phase 0 audit is mandatory, not optional |
| NRB institutional resistance | High | 6–12 month delay | Finance minister directive before Month 1 |
| Procurement capture (inflated tender) | Medium | System ships broken | Open-source mandate + public GitHub + private sector evaluators |
| No data protection law | Medium | Legal exposure, low trust | Parallel drafting from Month 1 — cannot be deferred |
| NID API downtime cascades | Medium | All KYC-dependent services stop | 99.9% SLA, hot standby, geographically separate DR site |
| Brain drain — engineers leave before sector matures | Medium | Talent gap | NRB sandbox itself creates the reason to stay |

---

## Design Principles (Non-Negotiable)

**Consent before data.** Every NID query requires a citizen-issued consent token scoped to a specific app and purpose. Citizens can revoke at any time.

**Minimum data.** `/verify` returns boolean only. `/kyc_basic` returns only the fields explicitly requested. Apps cannot receive data they did not ask for.

**Full audit trail.** Every query logged: which app, which citizen (anonymised in logs), what purpose, what time. Citizens can view their own query history.

**Open source.** All code on a public GitHub repository from day one. Any citizen, journalist, or researcher can read and audit it. This is both a trust mechanism and a procurement accountability mechanism.

**Data quality honesty.** The API surfaces `data_quality_warnings` when records are incomplete. Consuming apps are responsible for handling partial data — the system does not hide its own gaps.

---

*Prototype available: working Python/Flask implementation with Swagger UI · 19/19 tests passing*
*Contact for technical review or demo*