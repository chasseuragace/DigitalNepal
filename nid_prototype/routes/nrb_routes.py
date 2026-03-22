"""
NRB Fintech Sandbox API routes.
Simulates the payment sandbox for fintech companies seeking FX approval.
"""

from flask import Blueprint, request, jsonify, g
from mock_data.sandbox import SANDBOX_COMPANIES, TRANSACTIONS, run_aml_check, EXCHANGE_RATE_USD_NPR
from mock_data.citizens import CITIZENS
from middleware.auth import generate_query_id, generate_transaction_id, utcnow_iso, expiry_iso

nrb_bp = Blueprint("nrb", __name__, url_prefix="/v1/nrb")

# Simple sandbox key auth (separate from NID Bearer tokens)
def get_sandbox_company():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, "missing_sandbox_key"
    key = auth.replace("Bearer ", "").strip()
    company = SANDBOX_COMPANIES.get(key)
    if not company:
        return None, "invalid_sandbox_key"
    if company["status"] != "active":
        return None, "company_suspended"
    return company, None


@nrb_bp.route("/companies/register", methods=["POST"])
def register_company():
    """
    Register a company in the NRB fintech sandbox.
    ---
    tags:
      - NRB Sandbox
    summary: Register a company for fintech sandbox access
    description: |
      Tier 1 registration is instant — no NRB approval needed, test data only.
      Tier 2 requires NRB review (simulated as instant approval in sandbox).

      Director NID is verified via the NID API (mocked here — use a valid NID from the NID system).

      **Valid director NIDs:** 1234-5678-9012, 9876-5432-1098, 5555-6666-7777
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [company_name, pan_number, director_nid, business_model]
            properties:
              company_name:
                type: string
                example: "My Startup Pvt Ltd"
              pan_number:
                type: string
                example: "600123456"
              director_nid:
                type: string
                example: "1234-5678-9012"
              requested_tier:
                type: string
                enum: [tier_1, tier_2]
                default: tier_1
              business_model:
                type: string
                enum: [saas_export, remittance, payment_aggregator, freelance_platform, other]
                example: saas_export
              monthly_volume_npr:
                type: number
                example: 500000
    responses:
      201:
        description: Company registered, sandbox key issued
      400:
        description: Validation error
      422:
        description: Director NID invalid
    """
    body = request.get_json(silent=True) or {}
    company_name    = body.get("company_name", "").strip()
    pan_number      = body.get("pan_number", "").strip()
    director_nid    = body.get("director_nid", "").strip()
    requested_tier  = body.get("requested_tier", "tier_1")
    business_model  = body.get("business_model", "other")
    monthly_volume  = body.get("monthly_volume_npr", 0)

    if not company_name or not pan_number or not director_nid:
        return jsonify({"error": "company_name, pan_number, and director_nid are required"}), 400

    # Verify director NID exists (mock NID API call)
    citizen = CITIZENS.get(director_nid)
    if not citizen:
        return jsonify({
            "error": "director_nid_invalid",
            "hint": "NID not found in the NID system. Use: 1234-5678-9012, 9876-5432-1098, or 5555-6666-7777"
        }), 422
    if citizen["status"] != "active":
        return jsonify({"error": "director_nid_inactive", "nid_status": citizen["status"]}), 422

    import uuid, re
    slug = re.sub(r"[^a-z0-9]", "_", company_name.lower())[:20]
    sandbox_key = f"sk_{'test' if requested_tier == 'tier_1' else 'live'}_np_{slug}_{uuid.uuid4().hex[:6]}"

    tier_1_limits = {"monthly_limit_usd": 0, "test_only": True, "approved_corridors": []}
    tier_2_limits = {"monthly_limit_usd": 41_700, "test_only": False,
                     "approved_corridors": ["wise", "payoneer"],
                     "nrb_approval_note": "[MOCK] Tier 2 approval is instant in sandbox; takes 4-8 weeks in production."}

    limits = tier_1_limits if requested_tier == "tier_1" else tier_2_limits

    return jsonify({
        "sandbox_key": sandbox_key,
        "company_name": company_name,
        "tier": requested_tier,
        "status": "active",
        "director_verified": True,
        "director_name": citizen["full_name"],
        "registered_at": utcnow_iso(),
        **limits,
        "next_steps": (
            "Use sandbox_key as Bearer token in NRB sandbox endpoints. "
            "Tier 1: call /v1/nrb/simulate/inbound to test payment flows. "
            "Tier 2: real transaction limits apply."
            if requested_tier == "tier_1"
            else "You can now receive real inbound payments up to $41,700/month via approved corridors."
        ),
    }), 201


@nrb_bp.route("/simulate/inbound", methods=["POST"])
def simulate_inbound():
    """
    Simulate an inbound foreign payment.
    ---
    tags:
      - NRB Sandbox
    summary: Simulate receiving a foreign currency payment
    description: |
      Simulates an inbound USD/EUR payment, runs AML checks,
      calculates NPR conversion at NRB mid-rate, and sets repatriation deadline.

      **Test with pre-registered sandbox keys:**
      - `sk_test_np_hamro_saas` — Tier 1 (test mode, no real FX)
      - `sk_live_np_nabil_fx` — Tier 2 (live limits apply)
      - `sk_live_np_esewa_fx` — Tier 3 (unlimited)

      **AML triggers:**
      - Amount $9,000–$9,999 → structuring_risk flag
      - Amount > $5,000 → high_value flag
      - Amount < $1.00 → micro_transaction flag
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
        description: "Bearer <sandbox_key>"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [amount_usd, description]
            properties:
              amount_usd:
                type: number
                example: 299.00
              currency:
                type: string
                default: USD
                example: USD
              description:
                type: string
                example: "SaaS subscription - Acme Corp USA"
              corridor:
                type: string
                enum: [stripe, wise, payoneer, swift]
                example: stripe
              stripe_payment_intent:
                type: string
                example: "pi_test_3J8fKa..."
    responses:
      200:
        description: Simulated transaction result with AML check
      402:
        description: Monthly limit exceeded
      403:
        description: Corridor not approved for this tier
    """
    company, err = get_sandbox_company()
    if err:
        return jsonify({"error": err, "hint": "Use Bearer <sandbox_key> from /v1/nrb/companies/register"}), 401

    body = request.get_json(silent=True) or {}
    amount_usd  = float(body.get("amount_usd", 0))
    currency    = body.get("currency", "USD")
    description = body.get("description", "")
    corridor    = body.get("corridor", "stripe")

    if amount_usd <= 0:
        return jsonify({"error": "amount_usd must be positive"}), 400

    # Tier 1 — test mode only
    if company["tier"] == "tier_1":
        aml = run_aml_check(amount_usd)
        amount_npr = round(amount_usd * EXCHANGE_RATE_USD_NPR, 2)
        import datetime
        deadline = (datetime.datetime.utcnow() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        return jsonify({
            "mode": "TEST — no real money moved",
            "transaction_id": generate_transaction_id(),
            "amount_usd": amount_usd,
            "amount_npr": amount_npr,
            "exchange_rate": EXCHANGE_RATE_USD_NPR,
            "corridor": corridor,
            "description": description,
            "aml_status": aml["aml_status"],
            "compliance_flags": aml["compliance_flags"],
            "repatriation_deadline": deadline,
            "timestamp": utcnow_iso(),
            "note": "Tier 1 sandbox: upgrade to Tier 2 for live transactions.",
        }), 200

    # Tier 2/3 — check corridor approval
    if corridor not in company.get("approved_corridors", []):
        return jsonify({
            "error": "corridor_not_approved",
            "corridor": corridor,
            "approved_corridors": company["approved_corridors"],
            "hint": "Apply for corridor approval via NRB portal.",
        }), 403

    # Check monthly limit (Tier 2)
    if company["monthly_limit_usd"] is not None:
        remaining = company["monthly_limit_usd"] - company["monthly_used_usd"]
        if amount_usd > remaining:
            return jsonify({
                "error": "monthly_limit_exceeded",
                "limit_usd": company["monthly_limit_usd"],
                "used_usd": company["monthly_used_usd"],
                "remaining_usd": remaining,
                "requested_usd": amount_usd,
                "hint": "Apply to NRB for Tier 3 license for unlimited transactions.",
            }), 402

    aml = run_aml_check(amount_usd)
    amount_npr = round(amount_usd * EXCHANGE_RATE_USD_NPR, 2)
    import datetime
    deadline = (datetime.datetime.utcnow() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")

    return jsonify({
        "transaction_id": generate_transaction_id(),
        "status": "under_review" if aml["aml_status"] == "flagged" else "completed",
        "amount_usd": amount_usd,
        "amount_npr": amount_npr,
        "exchange_rate_npr_usd": EXCHANGE_RATE_USD_NPR,
        "currency": currency,
        "corridor": corridor,
        "description": description,
        "aml_status": aml["aml_status"],
        "compliance_flags": aml["compliance_flags"],
        "aml_note": "Transaction held for NRB review." if aml["aml_status"] == "flagged" else None,
        "repatriation_deadline": deadline,
        "company_monthly_used_usd": round(company["monthly_used_usd"] + amount_usd, 2),
        "timestamp": utcnow_iso(),
    }), 200


@nrb_bp.route("/transactions", methods=["GET"])
def list_transactions():
    """
    List transactions for this sandbox key.
    ---
    tags:
      - NRB Sandbox
    summary: View transaction history
    description: |
      Returns all simulated transactions for the authenticated sandbox key.
      Includes AML status and repatriation deadlines.

      **Pre-loaded test transactions available for:**
      - `sk_live_np_nabil_fx` — 2 transactions (1 flagged)
      - `sk_live_np_esewa_fx` — 1 transaction
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
        description: "Bearer <sandbox_key>"
      - in: query
        name: status
        schema:
          type: string
          enum: [completed, under_review, all]
        default: all
    responses:
      200:
        description: Transaction list
    """
    company, err = get_sandbox_company()
    if err:
        return jsonify({"error": err}), 401

    status_filter = request.args.get("status", "all")
    txns = [t for t in TRANSACTIONS if t["sandbox_key"] == company["sandbox_key"]]
    if status_filter != "all":
        txns = [t for t in txns if t["status"] == status_filter]

    return jsonify({
        "sandbox_key": company["sandbox_key"],
        "company_name": company["company_name"],
        "tier": company["tier"],
        "total": len(txns),
        "transactions": txns,
        "monthly_summary": {
            "used_usd": company["monthly_used_usd"],
            "limit_usd": company["monthly_limit_usd"],
            "remaining_usd": (
                company["monthly_limit_usd"] - company["monthly_used_usd"]
                if company["monthly_limit_usd"] else None
            ),
        },
    }), 200


@nrb_bp.route("/aml/check", methods=["POST"])
def aml_check():
    """
    Run a standalone AML check on an amount.
    ---
    tags:
      - NRB Sandbox
    summary: Check an amount against AML rules
    description: |
      Runs the AML rules engine against a given USD amount without
      creating a transaction. Useful for testing your integration's
      AML handling before going live.

      **Rule triggers:**
      - $9,000–$9,999 → `structuring_risk`
      - > $5,000 → `high_value`
      - < $1.00 → `micro_transaction`
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [amount_usd]
            properties:
              amount_usd:
                type: number
                example: 9500.00
    responses:
      200:
        description: AML check result
    """
    body = request.get_json(silent=True) or {}
    amount_usd = float(body.get("amount_usd", 0))
    result = run_aml_check(amount_usd)
    return jsonify({
        "amount_usd": amount_usd,
        "amount_npr_equivalent": round(amount_usd * EXCHANGE_RATE_USD_NPR, 2),
        **result,
        "rules_applied": [
            {"rule_id": "R001", "name": "structuring_risk",  "threshold": "$9,000–$9,999"},
            {"rule_id": "R002", "name": "high_value",        "threshold": "> $5,000"},
            {"rule_id": "R003", "name": "micro_transaction", "threshold": "< $1.00"},
        ],
        "timestamp": utcnow_iso(),
    }), 200


@nrb_bp.route("/exchange_rate", methods=["GET"])
def exchange_rate():
    """
    Get current NRB mid-rate.
    ---
    tags:
      - NRB Sandbox
    summary: Current NRB exchange rate (USD/NPR)
    description: Returns the mock NRB mid-rate used for all sandbox conversions.
    responses:
      200:
        description: Exchange rate data
    """
    return jsonify({
        "base": "USD",
        "quote": "NPR",
        "mid_rate": EXCHANGE_RATE_USD_NPR,
        "buy_rate": round(EXCHANGE_RATE_USD_NPR - 0.50, 2),
        "sell_rate": round(EXCHANGE_RATE_USD_NPR + 0.50, 2),
        "source": "NRB mock mid-rate",
        "timestamp": utcnow_iso(),
        "note": "[MOCK] Production would fetch live NRB published rate.",
    }), 200
