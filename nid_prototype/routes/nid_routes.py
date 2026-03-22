"""
NID API routes.
All endpoints documented with OpenAPI-compatible docstrings for Swagger UI.
"""

from flask import Blueprint, request, jsonify, g
from mock_data.citizens import CITIZENS, CONSENT_TOKENS
from middleware.auth import require_auth, validate_consent_token, generate_query_id, utcnow_iso, expiry_iso

nid_bp = Blueprint("nid", __name__, url_prefix="/v1/nid")


@nid_bp.route("/verify", methods=["POST"])
@require_auth(allowed_scopes=["verify", "kyc_basic", "kyc_photo"])
def verify():
    """
    Verify NID validity.
    ---
    tags:
      - NID Core
    summary: Verify if a National ID is valid
    description: |
      The simplest call — returns only a boolean. No personal data is returned.
      Requires a citizen-issued consent token with scope `verify`.

      **Consent tokens for testing:**
      - `ct_verify_ram` — active NID
      - `ct_verify_anita` — active NID, no photo on file
      - `ct_verify_suspended` — suspended NID (valid=false)
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
        description: "Bearer <app_id>  e.g. Bearer dev_test_key"
      - in: header
        name: X-Consent-Token
        required: true
        schema:
          type: string
        description: "Citizen-issued consent token e.g. ct_verify_ram"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [nid, purpose]
            properties:
              nid:
                type: string
                example: "1234-5678-9012"
              purpose:
                type: string
                example: "account_opening"
    responses:
      200:
        description: Verification result
        content:
          application/json:
            schema:
              type: object
              properties:
                valid:
                  type: boolean
                query_id:
                  type: string
                timestamp:
                  type: string
                consent_expiry:
                  type: string
                nid_status:
                  type: string
      400:
        description: Bad request
      401:
        description: Unauthorized
      403:
        description: Consent error
    """
    body = request.get_json(silent=True) or {}
    nid = body.get("nid", "").strip()
    purpose = body.get("purpose", "unspecified")

    if not nid:
        return jsonify({"error": "nid_required"}), 400

    consent_token = request.headers.get("X-Consent-Token", "")
    consent, err = validate_consent_token(consent_token, "verify", g.app["app_id"])
    if err:
        return jsonify({
            "error": err,
            "hint": "Obtain a consent token at GET /v1/nid/consent/initiate",
            "consent_url": f"https://consent.nid.gov.np/approve?app={g.app['app_id']}&scope=verify"
        }), 403

    # Check consent NID matches requested NID
    if consent["nid"] != nid:
        return jsonify({"error": "consent_nid_mismatch", "hint": "Consent token is for a different NID"}), 403

    citizen = CITIZENS.get(nid)
    if not citizen:
        return jsonify({
            "valid": False,
            "query_id": generate_query_id(),
            "timestamp": utcnow_iso(),
            "nid_status": "not_found",
            "consent_expiry": consent["expires_at"],
        }), 200

    valid = citizen["status"] == "active"
    return jsonify({
        "valid": valid,
        "query_id": generate_query_id(),
        "timestamp": utcnow_iso(),
        "nid_status": citizen["status"],
        "consent_expiry": consent["expires_at"],
        "data_quality_warnings": citizen["issues"] if citizen["issues"] else None,
    }), 200


@nid_bp.route("/kyc_basic", methods=["POST"])
@require_auth(allowed_scopes=["kyc_basic", "kyc_photo"])
def kyc_basic():
    """
    Fetch basic KYC demographics.
    ---
    tags:
      - NID Core
    summary: Retrieve citizen demographics for KYC
    description: |
      Returns name, DOB, gender, and address. Only returns fields
      that were explicitly requested AND consented to by the citizen.

      **Consent tokens for testing:**
      - `ct_kyc_ram` — complete record, all fields present
      - `ct_kyc_bikash` — partial record (missing tole, phone)
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
        description: "Bearer <app_id>"
      - in: header
        name: X-Consent-Token
        required: true
        schema:
          type: string
        description: "Citizen consent token with scope kyc_basic"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [nid, purpose]
            properties:
              nid:
                type: string
                example: "1234-5678-9012"
              purpose:
                type: string
                example: "loan_origination"
              fields_requested:
                type: array
                items:
                  type: string
                example: ["full_name", "dob", "address", "gender"]
                description: "Subset of allowed fields. If omitted, all consented fields returned."
    responses:
      200:
        description: KYC data
      400:
        description: Bad request
      403:
        description: Consent / scope error
    """
    body = request.get_json(silent=True) or {}
    nid = body.get("nid", "").strip()
    purpose = body.get("purpose", "unspecified")
    fields_requested = body.get("fields_requested", ["full_name", "dob", "gender", "address"])

    if not nid:
        return jsonify({"error": "nid_required"}), 400

    consent_token = request.headers.get("X-Consent-Token", "")
    consent, err = validate_consent_token(consent_token, "kyc_basic", g.app["app_id"])
    if err:
        return jsonify({"error": err, "consent_url": f"https://consent.nid.gov.np/approve?app={g.app['app_id']}&scope=kyc_basic"}), 403

    if consent["nid"] != nid:
        return jsonify({"error": "consent_nid_mismatch"}), 403

    citizen = CITIZENS.get(nid)
    if not citizen:
        return jsonify({"error": "nid_not_found"}), 404

    if citizen["status"] != "active":
        return jsonify({"error": "nid_not_active", "nid_status": citizen["status"]}), 403

    # Only return requested fields — privacy by design
    allowed_kyc_fields = {"full_name", "full_name_devanagari", "dob", "gender", "address"}
    data = {}
    for field in fields_requested:
        if field in allowed_kyc_fields and field in citizen:
            data[field] = citizen[field]

    return jsonify({
        "query_id": generate_query_id(),
        "data": data,
        "data_freshness": citizen["data_freshness"],
        "consent_scope": "kyc_basic",
        "consent_expiry": consent["expires_at"],
        "data_quality_warnings": citizen["issues"] if citizen["issues"] else None,
        "timestamp": utcnow_iso(),
    }), 200


@nid_bp.route("/kyc_photo", methods=["POST"])
@require_auth(allowed_scopes=["kyc_photo"])
def kyc_photo():
    """
    Biometric photo match for KYC.
    ---
    tags:
      - NID Core
    summary: Verify citizen identity via photo/biometric match
    description: |
      Simulates a biometric face-match against the NID photo on file.
      In production this calls a face-matching service. Here it returns
      a mock confidence score based on data availability.

      **Consent tokens for testing:**
      - `ct_photo_ram` — biometric enrolled, returns high confidence
      - Use NID `5555-6666-7777` (Anita) — no photo on file, returns error
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
      - in: header
        name: X-Consent-Token
        required: true
        schema:
          type: string
        description: "Consent token with scope kyc_photo"
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [nid, purpose]
            properties:
              nid:
                type: string
                example: "1234-5678-9012"
              purpose:
                type: string
                example: "high_value_loan"
              selfie_base64:
                type: string
                description: "Base64-encoded selfie image (mocked — any string accepted)"
                example: "data:image/jpeg;base64,/9j/4AAQ..."
    responses:
      200:
        description: Biometric match result
      403:
        description: Consent error or no photo on file
    """
    body = request.get_json(silent=True) or {}
    nid = body.get("nid", "").strip()

    if not nid:
        return jsonify({"error": "nid_required"}), 400

    consent_token = request.headers.get("X-Consent-Token", "")
    consent, err = validate_consent_token(consent_token, "kyc_photo", g.app["app_id"])
    if err:
        return jsonify({"error": err}), 403

    if consent["nid"] != nid:
        return jsonify({"error": "consent_nid_mismatch"}), 403

    citizen = CITIZENS.get(nid)
    if not citizen:
        return jsonify({"error": "nid_not_found"}), 404

    if not citizen.get("photo_on_file"):
        return jsonify({
            "error": "no_photo_on_file",
            "hint": "This citizen has not had their photo captured in the NID system yet.",
            "data_quality_issue": True,
        }), 422

    if not citizen.get("biometric_enrolled"):
        return jsonify({
            "match": False,
            "confidence": 0.0,
            "error": "biometric_not_enrolled",
            "hint": "Citizen must visit NID enrollment center to complete biometric capture.",
        }), 422

    # Mock biometric match — always succeeds with high confidence for enrolled citizens
    return jsonify({
        "query_id": generate_query_id(),
        "match": True,
        "confidence": 0.94,        # mock confidence score
        "liveness_check": "passed",
        "match_method": "face_embedding_cosine_similarity",
        "timestamp": utcnow_iso(),
        "consent_expiry": consent["expires_at"],
        "note": "[MOCK] In production, selfie_base64 would be compared against NID photo store.",
    }), 200


@nid_bp.route("/citizen_login", methods=["POST"])
@require_auth(allowed_scopes=["citizen_login"])
def citizen_login():
    """
    Citizen SSO login token.
    ---
    tags:
      - NID Core
    summary: Issue a citizen login session token (SSO)
    description: |
      No personal data is returned — only a session token that confirms
      the citizen successfully authenticated via their NID + OTP.
      Apps use this for single sign-on without storing citizen credentials.

      **Consent tokens for testing:**
      - `ct_login_sita`
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
      - in: header
        name: X-Consent-Token
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [nid, otp]
            properties:
              nid:
                type: string
                example: "9876-5432-1098"
              otp:
                type: string
                description: "6-digit OTP sent to citizen's registered phone (any 6 digits accepted in mock)"
                example: "482910"
    responses:
      200:
        description: Login session token issued
      403:
        description: Consent or OTP error
    """
    body = request.get_json(silent=True) or {}
    nid = body.get("nid", "").strip()
    otp = body.get("otp", "").strip()

    if not nid or not otp:
        return jsonify({"error": "nid_and_otp_required"}), 400

    if len(otp) != 6 or not otp.isdigit():
        return jsonify({"error": "invalid_otp_format", "hint": "OTP must be 6 digits"}), 400

    consent_token = request.headers.get("X-Consent-Token", "")
    consent, err = validate_consent_token(consent_token, "citizen_login", g.app["app_id"])
    if err:
        return jsonify({"error": err}), 403

    if consent["nid"] != nid:
        return jsonify({"error": "consent_nid_mismatch"}), 403

    citizen = CITIZENS.get(nid)
    if not citizen or citizen["status"] != "active":
        return jsonify({"error": "nid_invalid_or_inactive"}), 403

    import uuid
    session_token = "sess_" + uuid.uuid4().hex

    return jsonify({
        "authenticated": True,
        "session_token": session_token,
        "session_expiry": expiry_iso(60),
        "query_id": generate_query_id(),
        "timestamp": utcnow_iso(),
        "note": "[MOCK] OTP not verified in prototype — any 6-digit OTP accepted.",
    }), 200


@nid_bp.route("/consent/initiate", methods=["GET"])
def consent_initiate():
    """
    Initiate citizen consent flow.
    ---
    tags:
      - Consent
    summary: Get the consent URL for a citizen to approve
    description: |
      In production, this redirects the citizen to the NID consent portal.
      Here it returns the URL and a list of available test consent tokens
      to use in sandbox mode.
    parameters:
      - in: query
        name: app_id
        required: true
        schema:
          type: string
        example: dev_test_key
      - in: query
        name: scope
        required: true
        schema:
          type: string
          enum: [verify, kyc_basic, kyc_photo, citizen_login]
        example: kyc_basic
      - in: query
        name: nid
        required: false
        schema:
          type: string
        example: "1234-5678-9012"
    responses:
      200:
        description: Consent flow details and sandbox tokens
    """
    app_id = request.args.get("app_id", "")
    scope = request.args.get("scope", "")
    nid = request.args.get("nid", "")

    # Return sandbox tokens that match the requested scope
    matching_tokens = {
        k: v for k, v in CONSENT_TOKENS.items()
        if v["scope"] == scope and (not nid or v["nid"] == nid)
    }

    return jsonify({
        "consent_url": f"https://consent.nid.gov.np/approve?app={app_id}&scope={scope}&nid={nid}",
        "note": "[SANDBOX] In production the citizen would visit this URL and approve. Use a token below instead.",
        "available_sandbox_tokens": {
            k: {"nid": v["nid"], "scope": v["scope"], "app_id": v["app_id"]}
            for k, v in matching_tokens.items()
            if v["app_id"] == app_id or app_id == "dev_test_key"
        },
        "scopes_explained": {
            "verify": "Is this NID valid? Yes/No only.",
            "kyc_basic": "Name, DOB, gender, address.",
            "kyc_photo": "Biometric face match against NID photo.",
            "citizen_login": "SSO session — no data returned.",
        }
    }), 200


@nid_bp.route("/audit/my_queries", methods=["GET"])
@require_auth(allowed_scopes=["verify", "kyc_basic", "kyc_photo", "citizen_login"])
def audit_my_queries():
    """
    View query audit log for this app.
    ---
    tags:
      - Audit
    summary: Retrieve this app's recent NID query log
    description: |
      Every NID query is logged. Apps can view their own query history.
      Citizens can view who queried their NID via the citizen portal.
      (Mock returns static sample data.)
    parameters:
      - in: header
        name: Authorization
        required: true
        schema:
          type: string
    responses:
      200:
        description: Audit log entries
    """
    return jsonify({
        "app_id": g.app["app_id"],
        "total_queries_this_month": 1_247,
        "recent_queries": [
            {"query_id": "q_8f3a2b1c", "endpoint": "/verify",    "timestamp": "2025-03-22T09:14:22Z", "purpose": "account_opening",  "result": "valid"},
            {"query_id": "q_7c2d9e4f", "endpoint": "/kyc_basic", "timestamp": "2025-03-22T08:55:11Z", "purpose": "loan_origination", "result": "data_returned"},
            {"query_id": "q_1a9f3c8d", "endpoint": "/verify",    "timestamp": "2025-03-21T16:30:44Z", "purpose": "account_opening",  "result": "valid"},
        ],
        "note": "[MOCK] Production would return real query log from audit DB.",
    }), 200
