"""
Mock NID citizen database.
Simulates ~60% complete records (realistic for Nepal's NID rollout).
"""

CITIZENS = {
    "1234-5678-9012": {
        "nid": "1234-5678-9012",
        "status": "active",
        "full_name": "Ram Bahadur Thapa",
        "full_name_devanagari": "राम बहादुर थापा",
        "dob": "1988-04-15",
        "gender": "M",
        "address": {
            "province": "Bagmati",
            "district": "Kathmandu",
            "municipality": "Kathmandu Metropolitan City",
            "ward": 12,
            "tole": "Baneshwor"
        },
        "phone": "9841234567",
        "photo_on_file": True,
        "data_freshness": "2024-11-08",
        "biometric_enrolled": True,
        "issues": []
    },
    "9876-5432-1098": {
        "nid": "9876-5432-1098",
        "status": "active",
        "full_name": "Sita Kumari Sharma",
        "full_name_devanagari": "सीता कुमारी शर्मा",
        "dob": "1995-08-22",
        "gender": "F",
        "address": {
            "province": "Gandaki",
            "district": "Kaski",
            "municipality": "Pokhara Metropolitan City",
            "ward": 6,
            "tole": "Lakeside"
        },
        "phone": "9856789012",
        "photo_on_file": True,
        "data_freshness": "2023-03-14",
        "biometric_enrolled": True,
        "issues": []
    },
    "4567-8901-2345": {
        "nid": "4567-8901-2345",
        "status": "active",
        "full_name": "Bikash Raj Adhikari",
        "full_name_devanagari": "विकाश राज अधिकारी",
        "dob": "1979-12-03",
        "gender": "M",
        "address": {
            "province": "Madhesh",
            "district": "Sarlahi",
            "municipality": "Malangwa",
            "ward": 3,
            "tole": None   # missing — illustrates data quality issue
        },
        "phone": None,     # missing phone — common in older records
        "photo_on_file": True,
        "data_freshness": "2022-07-19",
        "biometric_enrolled": False,   # not yet enrolled
        "issues": ["missing_tole", "missing_phone"]
    },
    "2222-3333-4444": {
        "nid": "2222-3333-4444",
        "status": "suspended",   # suspended record
        "full_name": "Gopal Prasad Neupane",
        "full_name_devanagari": "गोपाल प्रसाद न्यौपाने",
        "dob": "1965-06-10",
        "gender": "M",
        "address": {
            "province": "Lumbini",
            "district": "Rupandehi",
            "municipality": "Butwal",
            "ward": 11,
            "tole": "Traffic Chowk"
        },
        "phone": "9857001122",
        "photo_on_file": True,
        "data_freshness": "2021-02-28",
        "biometric_enrolled": True,
        "issues": ["suspended"]
    },
    "5555-6666-7777": {
        "nid": "5555-6666-7777",
        "status": "active",
        "full_name": "Anita Gurung",
        "full_name_devanagari": "अनिता गुरुङ",
        "dob": "2001-01-30",
        "gender": "F",
        "address": {
            "province": "Koshi",
            "district": "Morang",
            "municipality": "Biratnagar Metropolitan City",
            "ward": 5,
            "tole": "Rangeli Road"
        },
        "phone": "9842345678",
        "photo_on_file": False,  # no photo — data quality issue
        "data_freshness": "2024-09-01",
        "biometric_enrolled": False,
        "issues": ["no_photo"]
    },
}

# Simulate registered apps with their allowed scopes
REGISTERED_APPS = {
    "nabil_bank_kyc_prod": {
        "name": "Nabil Bank KYC System",
        "allowed_scopes": ["verify", "kyc_basic", "kyc_photo"],
        "tier": "production",
        "active": True
    },
    "esewa_wallet_prod": {
        "name": "eSewa Digital Wallet",
        "allowed_scopes": ["verify", "citizen_login"],
        "tier": "production",
        "active": True
    },
    "hamro_saas_sandbox": {
        "name": "Hamro SaaS - Sandbox",
        "allowed_scopes": ["verify", "kyc_basic"],
        "tier": "sandbox",
        "active": True
    },
    "dev_test_key": {
        "name": "Developer Test Key",
        "allowed_scopes": ["verify", "kyc_basic", "kyc_photo", "citizen_login"],
        "tier": "sandbox",
        "active": True
    },
}

# Simulate pre-approved consent tokens (normally citizen would approve via portal)
# format: consent_token -> { nid, scope, app_id, expires_at }
import datetime

def make_expiry(minutes=30):
    return (datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)).isoformat() + "Z"

CONSENT_TOKENS = {
    # dev_test_key tokens — use these in Swagger UI / quick testing
    "ct_verify_ram":       {"nid": "1234-5678-9012", "scope": "verify",        "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_kyc_ram":          {"nid": "1234-5678-9012", "scope": "kyc_basic",     "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_photo_ram":        {"nid": "1234-5678-9012", "scope": "kyc_photo",     "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_verify_anita":     {"nid": "5555-6666-7777", "scope": "verify",        "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_photo_anita":      {"nid": "5555-6666-7777", "scope": "kyc_photo",     "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_verify_suspended": {"nid": "2222-3333-4444", "scope": "verify",        "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_login_sita_dev":   {"nid": "9876-5432-1098", "scope": "citizen_login", "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    "ct_kyc_bikash_dev":   {"nid": "4567-8901-2345", "scope": "kyc_basic",     "app_id": "dev_test_key",        "expires_at": make_expiry(120)},
    # App-specific tokens (demonstrate app_id enforcement)
    "ct_login_sita":       {"nid": "9876-5432-1098", "scope": "citizen_login", "app_id": "esewa_wallet_prod",   "expires_at": make_expiry(120)},
    "ct_kyc_bikash":       {"nid": "4567-8901-2345", "scope": "kyc_basic",     "app_id": "hamro_saas_sandbox",  "expires_at": make_expiry(120)},
    "ct_kyc_ram_nabil":    {"nid": "1234-5678-9012", "scope": "kyc_basic",     "app_id": "nabil_bank_kyc_prod", "expires_at": make_expiry(120)},
}
