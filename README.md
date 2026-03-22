# Nepal Digital Infrastructure — Prototype

**Two foundational systems Nepal doesn't have yet. Built to show they're possible.**

A working Python prototype of the NID API (National Identity verification) and the NRB Fintech Sandbox (foreign payment access for Nepali software companies). Not a concept paper. Not a deck. A running server with a Swagger UI, 19 passing tests, and mock data covering the real edge cases — suspended NIDs, incomplete records, AML structuring risk, biometric failures.

---

## Why this exists

Nepal's economy digitisation promises — cooperative reform, one-stop investment portals, IT exports, agricultural land consolidation — all require two things that don't exist today:

1. **A digital identity layer.** A way for a bank, cooperative, or government portal to verify who a citizen actually is, without 45 minutes of photocopies.

2. **A legal payment layer.** A way for Nepali software companies to receive foreign payments through Stripe, Wise, or Payoneer without routing money through Indian bank accounts or hawala.

Both are missing. This prototype builds them.

It was built as part of a broader analysis of RSP's economic manifesto and what the digital foundation of the $100B economy actually requires. The full documentation — roadmap, use cases for six user types, pitch deck — is in this repository.

---

## What's inside

```
nid_prototype/
├── app.py                   Main Flask app + Swagger UI + OpenAPI spec
├── routes/
│   ├── nid_routes.py        All /v1/nid/* endpoints
│   └── nrb_routes.py        All /v1/nrb/* endpoints
├── mock_data/
│   ├── citizens.py          5 mock NIDs, apps, consent tokens
│   └── sandbox.py           Companies, transactions, AML rules
├── middleware/
│   └── auth.py              OAuth2 mock, consent validation
└── README.md                This file
```

---

## Run it in 60 seconds

```bash
pip install flask
cd nid_prototype
python app.py
```

Open **http://localhost:5000/docs** — Swagger UI loads with every endpoint documented, example requests pre-filled, and test credentials ready to use.

---

## Try it immediately — no setup beyond pip install

### NID API — verify a citizen's identity

```bash
curl -X POST http://localhost:5000/v1/nid/verify \
  -H "Authorization: Bearer dev_test_key" \
  -H "X-Consent-Token: ct_verify_ram" \
  -H "Content-Type: application/json" \
  -d '{"nid": "1234-5678-9012", "purpose": "account_opening"}'
```

```json
{
  "valid": true,
  "nid_status": "active",
  "query_id": "q_8f3a2b1c",
  "timestamp": "2026-03-23T09:14:22Z"
}
```

Now try the suspended NID — a bank cannot open an account for this person:

```bash
curl -X POST http://localhost:5000/v1/nid/verify \
  -H "Authorization: Bearer dev_test_key" \
  -H "X-Consent-Token: ct_verify_suspended" \
  -H "Content-Type: application/json" \
  -d '{"nid": "2222-3333-4444", "purpose": "account_opening"}'
```

```json
{
  "valid": false,
  "nid_status": "suspended"
}
```

No bribe possible. The system enforces it.

---

### NRB Sandbox — simulate a foreign payment

```bash
curl -X POST http://localhost:5000/v1/nrb/simulate/inbound \
  -H "Authorization: Bearer sk_live_np_esewa_fx" \
  -H "Content-Type: application/json" \
  -d '{"amount_usd": 299.00, "description": "SaaS subscription - Acme Corp", "corridor": "stripe"}'
```

```json
{
  "transaction_id": "txn_9c3d7e2a",
  "status": "completed",
  "amount_usd": 299.0,
  "amount_npr": 39886.6,
  "exchange_rate_npr_usd": 133.4,
  "aml_status": "clear",
  "repatriation_deadline": "2026-06-20"
}
```

Now trigger the AML structuring flag — amounts just under $10,000:

```bash
curl -X POST http://localhost:5000/v1/nrb/aml/check \
  -H "Content-Type: application/json" \
  -d '{"amount_usd": 9500}'
```

```json
{
  "aml_status": "flagged",
  "compliance_flags": ["structuring_risk", "high_value"]
}
```

Every transaction checked automatically. No officer required.

---

## Test credentials

### NID API — Bearer tokens

| Token | App | Allowed scopes |
|---|---|---|
| `dev_test_key` | Developer sandbox | All scopes |
| `nabil_bank_kyc_prod` | Nabil Bank | verify, kyc_basic, kyc_photo |
| `esewa_wallet_prod` | eSewa | verify, citizen_login |

### NID API — Consent tokens (X-Consent-Token header)

| Token | NID | Scope | Scenario |
|---|---|---|---|
| `ct_verify_ram` | 1234-5678-9012 | verify | Active, complete record |
| `ct_kyc_ram` | 1234-5678-9012 | kyc_basic | Full demographics |
| `ct_photo_ram` | 1234-5678-9012 | kyc_photo | Biometric enrolled |
| `ct_verify_suspended` | 2222-3333-4444 | verify | Returns valid=false |
| `ct_kyc_bikash_dev` | 4567-8901-2345 | kyc_basic | Data quality warnings |
| `ct_photo_anita` | 5555-6666-7777 | kyc_photo | No photo on file |
| `ct_login_sita_dev` | 9876-5432-1098 | citizen_login | SSO session token |

### NRB Sandbox — sandbox keys

| Key | Tier | Limits |
|---|---|---|
| `sk_test_np_hamro_saas` | Tier 1 | Test only, no real FX |
| `sk_live_np_nabil_fx` | Tier 2 | $41,700/month, Wise + Payoneer |
| `sk_live_np_esewa_fx` | Tier 3 | Unlimited, all corridors |

---

## All endpoints

### NID API (`/v1/nid/`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/verify` | Is this NID valid? Boolean only — no personal data |
| POST | `/kyc_basic` | Name, DOB, gender, address — citizen-consented |
| POST | `/kyc_photo` | Biometric face match — financial institutions only |
| POST | `/citizen_login` | SSO session token — zero data returned |
| GET | `/consent/initiate` | Get consent URL + available sandbox tokens |
| GET | `/audit/my_queries` | This app's query audit log |

### NRB Sandbox (`/v1/nrb/`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/companies/register` | Register company, get sandbox key (instant for Tier 1) |
| POST | `/simulate/inbound` | Simulate foreign payment + AML check + FX conversion |
| GET | `/transactions` | List transactions for this sandbox key |
| POST | `/aml/check` | Run AML rules on an amount without creating a transaction |
| GET | `/exchange_rate` | NRB mid-rate USD/NPR |

---

## Test citizens

| NID | Name | Status | Notes |
|---|---|---|---|
| 1234-5678-9012 | Ram Bahadur Thapa | Active | Complete record |
| 9876-5432-1098 | Sita Kumari Sharma | Active | Complete record |
| 4567-8901-2345 | Bikash Raj Adhikari | Active | Missing tole + phone (data quality warning) |
| 2222-3333-4444 | Gopal Prasad Neupane | Suspended | Returns valid=false |
| 5555-6666-7777 | Anita Gurung | Active | No photo on file — kyc_photo returns error |

The 40% incomplete record rate (Bikash, Anita) reflects the realistic state of Nepal's NID database, where approximately 40% of records have at least one missing field. The API surfaces these as `data_quality_warnings` rather than blocking transactions — the consuming system decides how to handle it.

---

## Design decisions worth reading

**Consent before data.** Every NID query requires a citizen-issued consent token scoped to a specific app, purpose, and time window. This is enforced at the API layer — not in policy. A request without a valid consent token gets `{"error": "consent_token_required"}`. No data is returned regardless of who is asking.

**Minimum data by default.** `/verify` returns a boolean. Nothing else. `/kyc_basic` returns only the fields explicitly requested by the consuming app. Apps cannot receive more than they asked for, and cannot ask for more than the citizen consented to.

**Data quality is honest, not hidden.** The `data_quality_warnings` field tells the consuming app exactly what's missing or stale. `data_freshness` tells them when the record was last updated. A 4-year-old address gets surfaced — the app decides what to do, not the API.

**AML runs on everything.** Every NRB sandbox transaction passes through the AML rules engine. Structuring risk ($9,000–$9,999), high-value (>$5,000), and micro-transactions (<$1.00) are all flagged automatically. The flag does not block the transaction — it routes it appropriately.

**The informal channel is the real alternative.** The NRB sandbox is not competing with "no foreign payments." It is competing with hawala, Indian bank accounts, and grey-zone Payoneer routing. Every design decision is made with that comparison in mind.

---

## The full documentation set

| Document | What it covers |
|---|---|
| `docs/roadmap.md` | 18-month delivery plan, budget, risk register |
| `docs/use_cases/INDEX.md` | Master index of 33 use cases across 6 user types |
| `docs/use_cases/UC-01-citizen.md` | Citizen perspective — consent, data disputes, SSO |
| `docs/use_cases/UC-02-financial-institution.md` | Banks, cooperatives, MFIs |
| `docs/use_cases/UC-03-developer-fintech.md` | Developers and SaaS startups |
| `docs/use_cases/UC-04-government-officer.md` | MOICS, DAO enrollment, ministry IT |
| `docs/use_cases/UC-05-nrb-regulator.md` | NRB supervision and AML |
| `docs/use_cases/UC-06-auditor-oversight.md` | CIAA, OAG, journalists, civil society |
| `docs/pitch_deck.md` | Pitch deck for RSP policymakers |

---

## What this is not

This is not a production system. There is no real NID database behind it, no real NRB connection, and no real money moving. It is a prototype built to demonstrate that these systems are architecturally straightforward to build, and to make the conversation with policymakers concrete rather than theoretical.

The goal is not to ship this code. The goal is to get the right people in a room with a running server and a specific three-item ask — and to make "we don't know if this is possible" no longer a reason to delay.

---

## Contributing

If you're a Nepali developer who wants to see this become real — open an issue, start a discussion, or reach out directly. The most useful contributions right now are not code. They are connections to the people inside MOICS, NRB, or the RSP policy team who can turn a prototype into a mandate.

If you're an international DPI practitioner (Aadhaar team, MOSIP contributors, GovStack, X-Road) and you see patterns here worth commenting on — that feedback is equally welcome.

---

## License

MIT. Use it, fork it, build on it.

---

*Built in Kathmandu, March 2026.*
*The code is the easy part.*
