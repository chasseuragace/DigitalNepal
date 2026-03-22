# Nepal Digital Infrastructure API — Prototype

A working Python prototype of two foundational systems:

1. **NID API** — National Identity verification (Priority 1)
2. **NRB Sandbox** — Fintech payment sandbox (Priority 2)

---

## Setup & run

```bash
# Python 3.8+ and Flask required
pip install flask

cd nid_prototype
python app.py
```

Then open: **http://localhost:5000/docs**

---

## Quick test credentials

### NID API — Bearer tokens (app_id)
| Token | App | Allowed scopes |
|---|---|---|
| `dev_test_key` | Developer sandbox | All scopes |
| `nabil_bank_kyc_prod` | Nabil Bank | verify, kyc_basic, kyc_photo |
| `esewa_wallet_prod` | eSewa | verify, citizen_login |
| `hamro_saas_sandbox` | Hamro SaaS | verify, kyc_basic |

### NID consent tokens (X-Consent-Token header)
| Token | NID | Scope | Notes |
|---|---|---|---|
| `ct_verify_ram` | 1234-5678-9012 | verify | Active, complete record |
| `ct_kyc_ram` | 1234-5678-9012 | kyc_basic | Full demographics |
| `ct_photo_ram` | 1234-5678-9012 | kyc_photo | Biometric enrolled |
| `ct_verify_suspended` | 2222-3333-4444 | verify | Returns valid=false |
| `ct_kyc_bikash_dev` | 4567-8901-2345 | kyc_basic | Data quality warnings |
| `ct_photo_anita` | 5555-6666-7777 | kyc_photo | No photo on file error |
| `ct_login_sita_dev` | 9876-5432-1098 | citizen_login | SSO session token |

### NRB Sandbox — sandbox keys
| Key | Tier | Limits |
|---|---|---|
| `sk_test_np_hamro_saas` | Tier 1 | Test only, no real FX |
| `sk_live_np_nabil_fx` | Tier 2 | $41,700/month, wise+payoneer |
| `sk_live_np_esewa_fx` | Tier 3 | Unlimited, all corridors |

---

## API endpoints

### NID API
| Method | Path | Description |
|---|---|---|
| POST | `/v1/nid/verify` | Is this NID valid? (boolean only) |
| POST | `/v1/nid/kyc_basic` | Demographics (name, DOB, address) |
| POST | `/v1/nid/kyc_photo` | Biometric face match |
| POST | `/v1/nid/citizen_login` | SSO session token |
| GET  | `/v1/nid/consent/initiate` | Get consent URL + sandbox tokens |
| GET  | `/v1/nid/audit/my_queries` | Query audit log |

### NRB Sandbox
| Method | Path | Description |
|---|---|---|
| POST | `/v1/nrb/companies/register` | Register company, get sandbox key |
| POST | `/v1/nrb/simulate/inbound` | Simulate inbound payment + AML check |
| GET  | `/v1/nrb/transactions` | List transactions |
| POST | `/v1/nrb/aml/check` | Standalone AML rules check |
| GET  | `/v1/nrb/exchange_rate` | NRB mid-rate USD/NPR |

---

## Project structure

```
nid_prototype/
├── app.py                  # Flask app, Swagger spec, routes registration
├── mock_data/
│   ├── citizens.py         # 5 mock NIDs, apps, consent tokens
│   └── sandbox.py          # Companies, transactions, AML rules
├── middleware/
│   └── auth.py             # OAuth2 mock, consent validation
└── routes/
    ├── nid_routes.py       # All /v1/nid/* endpoints
    └── nrb_routes.py       # All /v1/nrb/* endpoints
```

---

## Design decisions

**Consent-before-data**: Every NID query requires a pre-issued consent token tied to a specific (app, citizen, scope) triplet. This enforces citizen control at the API layer, not just in policy.

**Scope minimization**: `/verify` returns boolean only. `/kyc_basic` returns only requested fields. Apps cannot fish for data beyond what they asked for.

**Data quality surfacing**: The `data_quality_warnings` field in responses surfaces real issues in the mock dataset (missing tole, no phone, no photo) — mimicking the ~40% incomplete records in Nepal's actual NID database.

**AML in the sandbox**: The NRB sandbox runs a simple rules engine on every simulated transaction. Amounts near $10,000 trigger `structuring_risk`. This is intentional — Nepal's NRB will need real-time AML flagging from day one.

**No external dependencies**: Runs on stdlib + Flask only. No database, no Redis, no message queue. Everything is in-memory — appropriate for a prototype that needs to run anywhere.
