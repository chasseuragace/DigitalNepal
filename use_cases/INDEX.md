# Nepal Digital Infrastructure — Use Case Index
**NID API (Priority 1) + NRB Fintech Sandbox (Priority 2)**

---

## Overview

This document set covers all user perspectives for Nepal's two foundational digital infrastructure systems. Each use case document is written from the perspective of a specific user type — their goals, their pain points, the flows they experience, and the acceptance criteria that matter to them.

Six user types are documented. Every one of them must be served well for the system to succeed. Optimising for one at the expense of another will cause the ecosystem to fail.

---

## Document Index

| Document | User type | Primary system | Key concern |
|---|---|---|---|
| [UC-01](./UC-01-citizen.md) | Citizen | NID API | "Who is looking at my data?" |
| [UC-02](./UC-02-financial-institution.md) | Bank / Cooperative / MFI | NID API + NRB Sandbox | "Is this legally defensible?" |
| [UC-03](./UC-03-developer-fintech.md) | Developer / Fintech startup | NID API + NRB Sandbox | "Can I build a business on this?" |
| [UC-04](./UC-04-government-officer.md) | Government officer / Ministry | NID API | "If this goes down, who gets blamed?" |
| [UC-05](./UC-05-nrb-regulator.md) | NRB (regulator) | NRB Sandbox | "What if something goes wrong?" |
| [UC-06](./UC-06-auditor-oversight.md) | Auditor / Civil society / Press | NID API + NRB Sandbox | "Is this system being abused?" |

---

## Use Case Summary Matrix

### NID API use cases

| ID | Use case | Actor | Scope used |
|---|---|---|---|
| UC-01.1 | Consent to bank KYC | Citizen | kyc_basic |
| UC-01.2 | Review who accessed my NID data | Citizen | (citizen portal) |
| UC-01.3 | SSO login to government portal | Citizen | citizen_login |
| UC-01.4 | Dispute a data quality error | Citizen | (enrollment centre) |
| UC-01.5 | Request NID reinstatement | Citizen | (DAO process) |
| UC-02.1 | Account opening (digital KYC) | Bank | verify + kyc_basic |
| UC-02.2 | Loan origination (biometric) | Bank | kyc_photo |
| UC-02.3 | Cooperative member verification | Cooperative | verify + kyc_basic |
| UC-02.4 | Group loan (MFI field officer) | MFI | verify + kyc_basic |
| UC-03.1 | Developer explores API | Developer | (sandbox) |
| UC-03.2 | Fintech integrates NID login | Fintech | kyc_basic + citizen_login |
| UC-03.3 | Cooperative management SaaS | Developer | verify + kyc_basic |
| UC-04.1 | Manage app registrations | NID admin | (admin portal) |
| UC-04.2 | Update incomplete NID record | DAO officer | (enrollment system) |
| UC-04.3 | Monitor system and privacy | Privacy officer | (admin portal) |
| UC-04.4 | Passport portal NID login | Ministry IT | citizen_login |
| UC-04.5 | IRD taxpayer verification | IRD IT | verify + kyc_basic |
| UC-06.1 | Audit NID procurement | OAG | (public records) |
| UC-06.2 | Investigate API abuse | CIAA | (formal request) |
| UC-06.4 | Report on query volumes | Journalist | (RTI + transparency report) |
| UC-06.5 | Audit consent mechanism | Digital rights NGO | (sandbox + source code) |
| UC-06.6 | Document Phase 0 findings | Civil society | (published audit report) |

### NRB Sandbox use cases

| ID | Use case | Actor | Tier |
|---|---|---|---|
| UC-02.5 | Bank tests remittance product | Bank | Tier 1 → 2 |
| UC-03.4 | SaaS founder gets legal FX | Startup | Tier 1 → 2 |
| UC-03.5 | Developer tests AML edge cases | Developer | Tier 1 (sandbox) |
| UC-03.6 | NRN registers remotely | NRN developer | Tier 1 |
| UC-04.6 | NRB examiner reviews application | NRB officer | (admin portal) |
| UC-05.1 | NRB issues sandbox circular | NRB Legal | (regulatory action) |
| UC-05.2 | NRB reviews Tier 2 application | NRB supervisor | Tier 2 approval |
| UC-05.3 | FIU investigates suspicious pattern | NRB FIU | (investigation) |
| UC-05.4 | NRB monitors systemic risk | NRB board | (dashboard) |
| UC-05.5 | NRB suspends non-compliant participant | NRB supervisor | (enforcement) |
| UC-05.6 | NRB publishes exchange rate | NRB (automated) | (system) |
| UC-06.3 | Parliamentary committee hearing | MPs + NRB | (transparency report) |

---

## Cross-Cutting Themes

Reading across all six documents, four themes appear repeatedly. These are not features of individual use cases — they are system properties that every use case depends on.

### 1. Consent is the load-bearing structure

Every NID API use case passes through citizen consent. If consent is hard to give, citizens won't give it and adoption fails. If consent is hard to understand, citizens give it without knowing what they've agreed to. If consent cannot be revoked, citizens stop trusting the system. The consent portal UX is not a minor detail — it is the foundation.

### 2. Data quality is the silent failure mode

The Phase 0 audit will find that roughly 40% of NID records have at least one incomplete or inaccurate field. Every use case that returns `data_quality_warnings` — UC-01.4, UC-02.1, UC-02.4, UC-03.2 — depends on the consuming system handling those warnings gracefully rather than silently ignoring them or blocking transactions. Data quality is not a launch blocker; it is an ongoing operational responsibility that lasts the lifetime of the system.

### 3. Open-source is both a trust mechanism and an anti-corruption mechanism

In six different use cases across four different user types — developer (UC-03.1), journalist (UC-06.4), digital rights NGO (UC-06.5), OAG (UC-06.1) — the first question is "can I see the code?" The open-source mandate answers that question before it's asked. It reduces the cost of trust-building for every stakeholder who would otherwise have to take the government's word for how the system works.

### 4. The informal channel is the real alternative

In both the NID API context (manual document verification, physically present at branch) and the NRB sandbox context (hawala, Indian bank accounts, grey-zone routing), the alternative to using the new system is not "nothing" — it is an existing informal system that is slower, more expensive, more prone to fraud, and completely invisible to regulators. Every use case framing should make this comparison explicit: not "this system vs. no system" but "this system vs. the informal system that exists today."

---

## Acceptance Criteria Rollup

The following are acceptance criteria that appear across multiple user documents and must be treated as system-wide requirements.

| Criterion | Referenced in |
|---|---|
| SMS notification to citizen within 60 seconds of NID data access | UC-01, UC-04 |
| Consent portal loads in under 3 seconds on 3G | UC-01, UC-03 |
| `/verify` response time < 500ms at p95 | UC-02, UC-03 |
| `query_id` present in every API response | UC-02, UC-06 |
| `data_quality_warnings` never silently omitted | UC-01, UC-02, UC-03 |
| Annual transparency report published by both NID Authority and NRB | UC-05, UC-06 |
| GitHub repository public from first commit | UC-03, UC-06 |
| Audit logs retained for minimum 7 years | UC-05, UC-06 |
| Third-party security audit before Phase 3 launch | UC-03, UC-06 |
| Admin actions logged with officer ID — no anonymous actions | UC-04, UC-06 |
| NRB Tier 2 application SLA: 10 working days | UC-03, UC-05 |
| Citizen can revoke app consent without visiting an office | UC-01, UC-06 |

---

## Relationship to Prototype

The working Python/Flask prototype (`nid_prototype/`) implements the core flows for UC-01.1, UC-01.3, UC-02.1, UC-02.2, UC-03.1, UC-03.2, UC-03.4, UC-03.5, and UC-05.6. The mock data (5 citizen records, 4 registered apps, 11 consent tokens, 3 sandbox companies, 3 pre-loaded transactions) is seeded to cover the key alternative flows documented here: suspended NID, partial data quality warnings, no photo on file, biometric not enrolled, AML flagging at structuring threshold.

Use case flows not yet implemented in the prototype: enrollment officer correction flow (UC-04.2), citizen query history portal (UC-01.2), NRB admin dashboard (UC-05.2, UC-05.3), and the consent portal UI itself (currently mocked via static tokens).

---

*Document set version: 0.1 · 6 user types · 33 use cases · Systems: NID API + NRB Fintech Sandbox*
