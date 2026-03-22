"""
Mock NRB Fintech Sandbox data.
Simulates registered companies, transactions, and AML rules.
"""

import datetime

SANDBOX_COMPANIES = {
    "sk_test_np_hamro_saas": {
        "sandbox_key": "sk_test_np_hamro_saas",
        "company_name": "Hamro SaaS Pvt Ltd",
        "pan_number": "600123456",
        "director_nid": "1234-5678-9012",
        "tier": "tier_1",
        "status": "active",
        "business_model": "saas_export",
        "monthly_limit_usd": 0,        # tier_1 = test only
        "monthly_used_usd": 0.0,
        "registered_at": "2025-01-15T10:00:00Z",
        "approved_corridors": [],       # no live corridors for tier_1
    },
    "sk_live_np_nabil_fx": {
        "sandbox_key": "sk_live_np_nabil_fx",
        "company_name": "Nabil Remittance Services",
        "pan_number": "600987654",
        "director_nid": "9876-5432-1098",
        "tier": "tier_2",
        "status": "active",
        "business_model": "remittance",
        "monthly_limit_usd": 41_700,   # ~NPR 5M at current rate
        "monthly_used_usd": 12_450.00,
        "registered_at": "2024-11-01T08:30:00Z",
        "approved_corridors": ["wise", "payoneer"],
    },
    "sk_live_np_esewa_fx": {
        "sandbox_key": "sk_live_np_esewa_fx",
        "company_name": "eSewa Money Transfer",
        "pan_number": "600111222",
        "director_nid": "9876-5432-1098",
        "tier": "tier_3",
        "status": "active",
        "business_model": "payment_aggregator",
        "monthly_limit_usd": None,     # tier_3 = unlimited
        "monthly_used_usd": 284_320.00,
        "registered_at": "2024-06-15T09:00:00Z",
        "approved_corridors": ["stripe", "wise", "payoneer", "swift"],
    },
}

# Simulated transaction history
TRANSACTIONS = [
    {
        "transaction_id": "txn_4f8a2c1b",
        "sandbox_key": "sk_live_np_nabil_fx",
        "type": "inbound",
        "amount_usd": 1_500.00,
        "amount_npr": 200_100.00,
        "exchange_rate": 133.40,
        "description": "Family remittance from UAE",
        "corridor": "wise",
        "aml_status": "clear",
        "compliance_flags": [],
        "repatriation_deadline": "2025-06-20",
        "created_at": "2025-03-20T14:22:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "txn_9c3d7e2a",
        "sandbox_key": "sk_live_np_esewa_fx",
        "type": "inbound",
        "amount_usd": 299.00,
        "amount_npr": 39_886.60,
        "exchange_rate": 133.40,
        "description": "SaaS subscription - Acme Corp USA",
        "corridor": "stripe",
        "aml_status": "clear",
        "compliance_flags": [],
        "repatriation_deadline": "2025-06-22",
        "created_at": "2025-03-22T09:14:00Z",
        "status": "completed",
    },
    {
        "transaction_id": "txn_flagged_01",
        "sandbox_key": "sk_live_np_nabil_fx",
        "type": "inbound",
        "amount_usd": 9_800.00,  # just under $10K reporting threshold — suspicious
        "amount_npr": 1_307_320.00,
        "exchange_rate": 133.40,
        "description": "Consultancy payment",
        "corridor": "wise",
        "aml_status": "flagged",
        "compliance_flags": ["structuring_risk", "high_value"],
        "repatriation_deadline": "2025-06-18",
        "created_at": "2025-03-18T11:05:00Z",
        "status": "under_review",
    },
]

# AML rules engine — simple rule set
AML_RULES = [
    {
        "rule_id": "R001",
        "name": "structuring_risk",
        "description": "Amount just under $10,000 reporting threshold",
        "condition": lambda usd: 9_000 <= usd < 10_000,
    },
    {
        "rule_id": "R002",
        "name": "high_value",
        "description": "Single transaction over $5,000",
        "condition": lambda usd: usd > 5_000,
    },
    {
        "rule_id": "R003",
        "name": "micro_transaction",
        "description": "Very small transaction — possible test/probe",
        "condition": lambda usd: usd < 1.00,
    },
]

def run_aml_check(amount_usd: float) -> dict:
    flags = []
    for rule in AML_RULES:
        if rule["condition"](amount_usd):
            flags.append(rule["name"])
    return {
        "aml_status": "flagged" if flags else "clear",
        "compliance_flags": flags,
    }

# Mock NPR/USD exchange rate (NRB mid-rate)
EXCHANGE_RATE_USD_NPR = 133.40
