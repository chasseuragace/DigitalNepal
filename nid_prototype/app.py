"""
Nepal Digital Infrastructure Prototype
NID API + NRB Fintech Sandbox

Run:  python app.py
Docs: http://localhost:5000/docs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, redirect

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# ── Register blueprints ──────────────────────────────────────────────────────
from routes.nid_routes import nid_bp
from routes.nrb_routes import nrb_bp

app.register_blueprint(nid_bp)
app.register_blueprint(nrb_bp)

# ── Swagger spec (hand-rolled, no flasgger dependency) ───────────────────────
SWAGGER_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Nepal Digital Infrastructure API",
        "version": "0.1.0-prototype",
        "description": (
            "**Prototype** of two foundational systems for Nepal's digital economy:\n\n"
            "1. **NID API** — National Identity API (Priority 1)\n"
            "   Consent-gated citizen identity verification. All data is mock.\n\n"
            "2. **NRB Sandbox** — Fintech Payment Sandbox (Priority 2)\n"
            "   Simulated foreign payment corridors with AML checking.\n\n"
            "---\n"
            "### Quick start\n\n"
            "**NID API** — use `Authorization: Bearer dev_test_key` for all endpoints.\n"
            "Then pick a consent token from `/v1/nid/consent/initiate`.\n\n"
            "**NRB Sandbox** — use one of these sandbox keys:\n"
            "- `sk_test_np_hamro_saas` (Tier 1, test only)\n"
            "- `sk_live_np_nabil_fx` (Tier 2, $41,700/mo limit)\n"
            "- `sk_live_np_esewa_fx` (Tier 3, unlimited)\n\n"
            "---\n"
            "### Test NIDs\n"
            "| NID | Name | Status | Notes |\n"
            "|---|---|---|---|\n"
            "| 1234-5678-9012 | Ram Bahadur Thapa | active | Complete record |\n"
            "| 9876-5432-1098 | Sita Kumari Sharma | active | Complete record |\n"
            "| 4567-8901-2345 | Bikash Raj Adhikari | active | Missing tole + phone |\n"
            "| 2222-3333-4444 | Gopal Prasad Neupane | suspended | Suspended NID |\n"
            "| 5555-6666-7777 | Anita Gurung | active | No photo on file |\n"
        ),
        "contact": {
            "name": "Nepal Digital Infrastructure Prototype",
            "url": "https://github.com/nepal-digital-infra"
        },
        "license": {"name": "MIT"}
    },
    "servers": [{"url": "http://localhost:5000", "description": "Local prototype"}],
    "tags": [
        {"name": "NID Core",    "description": "National Identity verification endpoints"},
        {"name": "Consent",     "description": "Citizen consent flow"},
        {"name": "Audit",       "description": "Query audit trail"},
        {"name": "NRB Sandbox", "description": "Fintech payment sandbox"},
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "NID: use app_id (e.g. dev_test_key). NRB: use sandbox_key."
            }
        }
    },
    "security": [{"BearerAuth": []}],
    "paths": {
        "/v1/nid/verify": {
            "post": {
                "tags": ["NID Core"],
                "summary": "Verify NID validity",
                "description": "Returns true/false only. No personal data. Requires consent token with scope `verify`.\n\n**Test:** Bearer `dev_test_key` + X-Consent-Token: `ct_verify_ram`",
                "security": [{"BearerAuth": []}],
                "parameters": [{"in": "header", "name": "X-Consent-Token", "required": True, "schema": {"type": "string"}, "example": "ct_verify_ram"}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["nid", "purpose"],
                        "properties": {
                            "nid":     {"type": "string", "example": "1234-5678-9012"},
                            "purpose": {"type": "string", "example": "account_opening"}
                        }
                    }}}
                },
                "responses": {
                    "200": {"description": "Verification result"},
                    "401": {"description": "Invalid Bearer token"},
                    "403": {"description": "Consent error"},
                }
            }
        },
        "/v1/nid/kyc_basic": {
            "post": {
                "tags": ["NID Core"],
                "summary": "KYC demographics lookup",
                "description": "Returns name, DOB, gender, address. Only consented fields returned.\n\n**Test:** Bearer `dev_test_key` + X-Consent-Token: `ct_kyc_ram`",
                "security": [{"BearerAuth": []}],
                "parameters": [{"in": "header", "name": "X-Consent-Token", "required": True, "schema": {"type": "string"}, "example": "ct_kyc_ram"}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["nid", "purpose"],
                        "properties": {
                            "nid":              {"type": "string", "example": "1234-5678-9012"},
                            "purpose":          {"type": "string", "example": "loan_origination"},
                            "fields_requested": {"type": "array", "items": {"type": "string"}, "example": ["full_name", "dob", "address", "gender"]}
                        }
                    }}}
                },
                "responses": {
                    "200": {"description": "KYC data"},
                    "403": {"description": "Consent or scope error"},
                    "404": {"description": "NID not found"},
                }
            }
        },
        "/v1/nid/kyc_photo": {
            "post": {
                "tags": ["NID Core"],
                "summary": "Biometric photo match",
                "description": "Mock face-match against NID photo. Returns confidence score.\n\n**Test:** Bearer `dev_test_key` + X-Consent-Token: `ct_photo_ram`",
                "security": [{"BearerAuth": []}],
                "parameters": [{"in": "header", "name": "X-Consent-Token", "required": True, "schema": {"type": "string"}, "example": "ct_photo_ram"}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["nid", "purpose"],
                        "properties": {
                            "nid":           {"type": "string", "example": "1234-5678-9012"},
                            "purpose":       {"type": "string", "example": "high_value_loan"},
                            "selfie_base64": {"type": "string", "example": "data:image/jpeg;base64,/9j/..."}
                        }
                    }}}
                },
                "responses": {
                    "200": {"description": "Biometric match result"},
                    "422": {"description": "No photo on file or biometric not enrolled"},
                }
            }
        },
        "/v1/nid/citizen_login": {
            "post": {
                "tags": ["NID Core"],
                "summary": "Citizen SSO login",
                "description": "Issues a session token. No personal data returned.\n\n**Test:** Bearer `esewa_wallet_prod` + X-Consent-Token: `ct_login_sita`",
                "security": [{"BearerAuth": []}],
                "parameters": [{"in": "header", "name": "X-Consent-Token", "required": True, "schema": {"type": "string"}, "example": "ct_login_sita"}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["nid", "otp"],
                        "properties": {
                            "nid": {"type": "string", "example": "9876-5432-1098"},
                            "otp": {"type": "string", "example": "482910"}
                        }
                    }}}
                },
                "responses": {"200": {"description": "Session token"}}
            }
        },
        "/v1/nid/consent/initiate": {
            "get": {
                "tags": ["Consent"],
                "summary": "Get consent URL + sandbox tokens",
                "description": "Returns the citizen consent portal URL and available sandbox consent tokens for testing.",
                "parameters": [
                    {"in": "query", "name": "app_id", "required": True,  "schema": {"type": "string"}, "example": "dev_test_key"},
                    {"in": "query", "name": "scope",  "required": True,  "schema": {"type": "string", "enum": ["verify", "kyc_basic", "kyc_photo", "citizen_login"]}, "example": "kyc_basic"},
                    {"in": "query", "name": "nid",    "required": False, "schema": {"type": "string"}, "example": "1234-5678-9012"},
                ],
                "responses": {"200": {"description": "Consent flow details"}}
            }
        },
        "/v1/nid/audit/my_queries": {
            "get": {
                "tags": ["Audit"],
                "summary": "This app's query audit log",
                "description": "Every NID query is logged. Citizens can also view who queried their NID.\n\n**Test:** Bearer `dev_test_key`",
                "security": [{"BearerAuth": []}],
                "responses": {"200": {"description": "Audit log"}}
            }
        },
        "/v1/nrb/companies/register": {
            "post": {
                "tags": ["NRB Sandbox"],
                "summary": "Register a company in NRB sandbox",
                "description": "Tier 1 = instant, test only. Tier 2 = NRB approval (mocked as instant).\n\nValid director NIDs: `1234-5678-9012`, `9876-5432-1098`",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["company_name", "pan_number", "director_nid", "business_model"],
                        "properties": {
                            "company_name":      {"type": "string", "example": "My Startup Pvt Ltd"},
                            "pan_number":        {"type": "string", "example": "600123456"},
                            "director_nid":      {"type": "string", "example": "1234-5678-9012"},
                            "requested_tier":    {"type": "string", "enum": ["tier_1", "tier_2"], "default": "tier_1"},
                            "business_model":    {"type": "string", "enum": ["saas_export", "remittance", "payment_aggregator", "freelance_platform", "other"]},
                            "monthly_volume_npr":{"type": "number", "example": 500000},
                        }
                    }}}
                },
                "responses": {
                    "201": {"description": "Registered, sandbox key issued"},
                    "422": {"description": "Director NID invalid"},
                }
            }
        },
        "/v1/nrb/simulate/inbound": {
            "post": {
                "tags": ["NRB Sandbox"],
                "summary": "Simulate inbound foreign payment",
                "description": "Runs AML check, FX conversion, sets repatriation deadline.\n\n**AML triggers:** $9k–$9,999 → structuring_risk | >$5k → high_value | <$1 → micro_transaction\n\n**Test keys:** `sk_test_np_hamro_saas`, `sk_live_np_nabil_fx`, `sk_live_np_esewa_fx`",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["amount_usd", "description"],
                        "properties": {
                            "amount_usd":             {"type": "number", "example": 299.00},
                            "currency":               {"type": "string", "default": "USD"},
                            "description":            {"type": "string", "example": "SaaS subscription - Acme Corp USA"},
                            "corridor":               {"type": "string", "enum": ["stripe", "wise", "payoneer", "swift"], "example": "stripe"},
                            "stripe_payment_intent":  {"type": "string", "example": "pi_test_3J8fKa..."},
                        }
                    }}}
                },
                "responses": {
                    "200": {"description": "Transaction result with AML check"},
                    "402": {"description": "Monthly limit exceeded"},
                    "403": {"description": "Corridor not approved"},
                }
            }
        },
        "/v1/nrb/transactions": {
            "get": {
                "tags": ["NRB Sandbox"],
                "summary": "List transactions for this sandbox key",
                "description": "Pre-loaded test data for `sk_live_np_nabil_fx` (2 txns, 1 flagged) and `sk_live_np_esewa_fx` (1 txn).",
                "security": [{"BearerAuth": []}],
                "parameters": [{"in": "query", "name": "status", "schema": {"type": "string", "enum": ["completed", "under_review", "all"]}, "default": "all"}],
                "responses": {"200": {"description": "Transaction list"}}
            }
        },
        "/v1/nrb/aml/check": {
            "post": {
                "tags": ["NRB Sandbox"],
                "summary": "Standalone AML amount check",
                "description": "Test the AML rules engine without creating a transaction.",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {
                        "type": "object", "required": ["amount_usd"],
                        "properties": {"amount_usd": {"type": "number", "example": 9500.00}}
                    }}}
                },
                "responses": {"200": {"description": "AML check result"}}
            }
        },
        "/v1/nrb/exchange_rate": {
            "get": {
                "tags": ["NRB Sandbox"],
                "summary": "Current NRB mid-rate USD/NPR",
                "responses": {"200": {"description": "Exchange rate"}}
            }
        },
    }
}


@app.route("/openapi.json")
def openapi_spec():
    return jsonify(SWAGGER_SPEC)


@app.route("/docs")
def swagger_ui():
    """Swagger UI — served as inline HTML, no CDN needed."""
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Nepal Digital Infrastructure API</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
  <style>
    body { margin: 0; background: #fafafa; }
    .topbar { display: none !important; }
    .swagger-ui .info .title { font-size: 24px; }
  </style>
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
<script>
  SwaggerUIBundle({
    url: "/openapi.json",
    dom_id: "#swagger-ui",
    presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
    layout: "BaseLayout",
    deepLinking: true,
    defaultModelsExpandDepth: 0,
    defaultModelExpandDepth: 2,
  });
</script>
</body>
</html>"""
    from flask import Response
    return Response(html, mimetype="text/html")


@app.route("/")
def index():
    return redirect("/docs")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Nepal Digital Infrastructure Prototype", "version": "0.1.0"})


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Nepal Digital Infrastructure API — Prototype")
    print("="*60)
    print("  Swagger UI : http://localhost:5000/docs")
    print("  OpenAPI    : http://localhost:5000/openapi.json")
    print("  Health     : http://localhost:5000/health")
    print("="*60)
    print("\n  NID Test tokens: dev_test_key")
    print("  NRB Test keys:   sk_test_np_hamro_saas")
    print("                   sk_live_np_nabil_fx")
    print("                   sk_live_np_esewa_fx\n")
    app.run(debug=True, port=5000)
