# UC-03 — Developer / Fintech Startup
**Nepal Digital Infrastructure · Use Case Document**
*Software engineers · SaaS founders · Fintech product teams*

---

## User Profile

| | |
|---|---|
| **Who** | Nepali software engineers, startup founders, product managers building on top of the infrastructure |
| **Size** | Solo developers to 20-person startups |
| **Location** | Kathmandu primarily, some distributed |
| **Current problem** | Cannot receive foreign payments legally · Cannot verify user identity without manual document upload · Build KYC from scratch for every product |
| **Key concern** | "Will this API still exist in 12 months? Can I build a business on it?" |
| **Secondary concern** | "How do I test this without touching real citizen data?" |

Developers and fintech startups are the multiplier. Every integration they build extends the value of the infrastructure to new use cases the government never anticipated. The quality of the developer experience — documentation, sandbox stability, error messages, response time — directly determines the size of the ecosystem that forms around these two systems.

---

## Use Cases — NID API (Developer)

---

### UC-03.1 — Developer explores the API for the first time

**Trigger:** Developer reads about NID API launch, wants to evaluate it for a product they're building.

**Main flow:**
1. Developer visits `api.nid.gov.np/docs` — Swagger UI loads
2. Sees all endpoints documented with example requests and responses
3. Uses `dev_test_key` Bearer token — no registration required for sandbox
4. Runs first call in browser via Swagger:
   ```
   POST /v1/nid/verify
   Authorization: Bearer dev_test_key
   X-Consent-Token: ct_verify_ram
   Body: { "nid": "1234-5678-9012", "purpose": "testing" }
   ```
5. Gets back `{ "valid": true, "nid_status": "active", ... }` in under 500ms
6. Tries `ct_verify_suspended` — sees `valid: false` for the suspended NID
7. Tries `/kyc_basic` — sees exactly which fields come back, and `data_quality_warnings`
8. Reads the consent flow documentation — understands the OAuth2 redirect pattern

**Developer experience requirements:**
- Zero-friction sandbox: no registration, no email verification, no waiting
- All test scenarios covered by pre-seeded tokens (valid, suspended, partial data, no photo)
- Error messages are human-readable, not `{"error": "ERR_4029"}`
- OpenAPI spec downloadable for code generation

---

### UC-03.2 — Fintech startup integrates NID login into their wallet app

**Trigger:** Startup building a digital wallet (similar to eSewa) wants to use NID as the identity layer instead of building their own KYC.

**Actor:** Backend engineer + product manager

**Main flow:**

**Step 1 — Register as a production app:**
1. Apply via developer portal with company PAN, director NID, business description
2. NRB/MOICS reviews (automated for Tier 1, 2–5 days for Tier 2)
3. Receive production `app_id` with allowed scopes: `verify`, `kyc_basic`, `citizen_login`

**Step 2 — Implement consent redirect:**
```python
# When user taps "Verify with NID" in your app:
consent_url = (
    "https://consent.nid.gov.np/approve"
    f"?app_id={APP_ID}"
    f"&scope=kyc_basic"
    f"&redirect_uri=https://yourapp.com/callback"
    f"&state={csrf_token}"
)
redirect(consent_url)

# After citizen approves — handle callback:
@app.route("/callback")
def handle_callback():
    consent_token = request.args.get("consent_token")
    state = request.args.get("state")
    verify_csrf(state)
    # Now call NID API with consent_token
    response = nid_client.kyc_basic(
        nid=session["nid"],
        consent_token=consent_token,
        fields=["full_name", "dob", "address"]
    )
    onboard_user(response["data"])
```

**Step 3 — Handle all response states:**
```python
def handle_nid_response(response):
    if response.get("data_quality_warnings"):
        # Don't block — ask user to confirm address manually
        flag_for_review(response["query_id"], response["data_quality_warnings"])
    
    if response.get("data_freshness"):
        age_days = (today - parse(response["data_freshness"])).days
        if age_days > 730:  # 2 years
            request_address_confirmation(user_id)
    
    # Always store query_id for audit
    store_audit_record(response["query_id"], purpose="wallet_onboarding")
```

**Postconditions:**
- User onboarded in under 2 minutes (vs. 2–3 days with manual document upload)
- Startup has legally defensible KYC record with `query_id`
- No NID data stored beyond what's needed — privacy by design

---

### UC-03.3 — Developer builds a cooperative management SaaS

**Trigger:** Developer sees the cooperative crisis and builds a SaaS for cooperative secretaries to manage membership, KYC, and loans — using NID API as the identity layer.

**Main flow:**
1. SaaS app registered with scopes: `verify`, `kyc_basic`
2. Cooperative secretary onboards new member:
   - Enters NID number
   - Member receives OTP, consents
   - SaaS calls `kyc_basic` — name and DOB auto-filled
   - Secretary confirms and saves
3. SaaS maintains its own member database with NID numbers as verified identifiers
4. When member applies for loan, SaaS re-verifies (new consent call) to confirm identity is still active
5. SaaS generates monthly NRB-compliant member report

**Key product insight:** The SaaS charges cooperatives NPR 2,000–5,000/month. The NID API makes the product defensible — no competitor can offer the same identity assurance without it. This is the ecosystem effect: the infrastructure creates a moat for products built on it.

---

## Use Cases — NRB Sandbox (Developer/Fintech)

---

### UC-03.4 — SaaS founder registers for fintech sandbox to accept foreign payments

**Trigger:** Nepali SaaS founder has international customers willing to pay, but cannot legally receive USD. Has been using a friend's Indian bank account. Wants to go legitimate.

**Current reality before sandbox:**
- Freelancers route payments through Payoneer → Indian account → hawala → Nepali cash
- Every step is technically illegal or in a grey zone
- No receipts, no audit trail, no ability to scale

**Main flow:**
1. Founder registers via `POST /v1/nrb/companies/register`:
   ```json
   {
     "company_name": "Hamro Analytics Pvt Ltd",
     "pan_number": "600123456",
     "director_nid": "1234-5678-9012",
     "requested_tier": "tier_1",
     "business_model": "saas_export"
   }
   ```
2. Director NID verified automatically via NID API
3. Receives `sk_test_np_hamro_...` key instantly — Tier 1, no NRB approval
4. Tests payment simulation:
   ```json
   POST /v1/nrb/simulate/inbound
   { "amount_usd": 299.00, "description": "SaaS subscription - Acme Corp", "corridor": "stripe" }
   ```
5. Response shows NPR conversion, AML status `clear`, repatriation deadline
6. Founder integrates Stripe Checkout into product — uses test keys initially
7. After 30 days of successful test transactions, applies for Tier 2 upgrade

**Tier 2 application adds:**
- NRB reviews business model (2–5 working days in production)
- Monthly transaction cap: $41,700 (NPR ~5.5M)
- Approved corridors: Wise + Payoneer initially, Stripe after 3 months of clean transactions

**Postconditions:**
- Founder now legally receives foreign revenue
- Transaction receipts available for tax filing (previously impossible)
- IRD can see the foreign income source — founder can now expense software tools

---

### UC-03.5 — Developer tests AML edge cases before go-live

**Trigger:** Developer's payment integration is ready for production. Wants to validate that their app handles AML flags gracefully.

**Main flow:**
1. Developer calls `POST /v1/nrb/aml/check` with various amounts:
   ```
   $299    → aml_status: clear
   $5,001  → aml_status: flagged, flags: ["high_value"]
   $9,500  → aml_status: flagged, flags: ["structuring_risk", "high_value"]
   $0.50   → aml_status: flagged, flags: ["micro_transaction"]
   ```
2. Developer implements handling:
   ```python
   def handle_payment(amount_usd, description):
       result = nrb_client.simulate_inbound(amount_usd, description)
       
       if result["aml_status"] == "flagged":
           if "structuring_risk" in result["compliance_flags"]:
               notify_compliance_team(result)
               hold_transaction(result["transaction_id"])
           elif "high_value" in result["compliance_flags"]:
               log_for_monthly_nrb_report(result)
               # Don't hold — just log
       
       return result
   ```
3. Developer confirms their app handles `under_review` status gracefully — payment held, user notified, compliance team alerted

**Key design requirement:** The AML rules documentation must be public and versioned. Developers need to know exactly what triggers a flag so they can build appropriate UX (e.g., "This payment requires additional review — we'll notify you within 2 business days").

---

### UC-03.6 — NRN (Non-Resident Nepali) developer registers remotely

**Trigger:** Nepali software engineer working in Germany wants to register a Nepali company and sell SaaS globally, routing legitimate revenue through Nepal.

**Main flow:**
1. Developer visits sandbox portal
2. Selects "NRN remote registration"
3. Uploads: NRN card, company registration document, director NID
4. Director NID verified via `kyc_basic` (works cross-border — consent via OTP to Nepali phone number or email fallback)
5. Receives sandbox key within 24 hours
6. Tests payment flows with EUR as base currency (EUR/NPR conversion at NRB rate)

**Postcondition:** Nepal gains foreign revenue that would otherwise have been booked in Germany. This is the definition of the "knowledge export" promised in RSP's bacha patra.

---

## Developer Experience Requirements

These are not nice-to-haves. A poor developer experience means the ecosystem doesn't form.

### Documentation
- OpenAPI 3.0 spec downloadable and up-to-date at all times
- Every endpoint has: description, all request fields, all response fields, all error codes, one worked example
- Error messages in English (technical audience) with Nepali translations for user-facing messages
- Changelog published for every API version — no silent breaking changes

### Sandbox
- Always available — never taken down for maintenance during business hours
- Synthetic data covers all edge cases: valid NID, suspended NID, partial data, no photo, biometric not enrolled
- Sandbox responses indistinguishable from production responses (same schema, same field names)
- Test AML amounts documented publicly

### SDK / Client libraries
- Phase 3 deliverable: official Python and JavaScript/TypeScript SDK
- SDK wraps consent flow, token management, error handling
- MIT licensed — usable in commercial products

### Rate limits (sandbox vs production)

| Environment | Limit | Notes |
|---|---|---|
| Sandbox | Unlimited | No rate limiting in sandbox |
| Production Tier 1 (sandbox apps) | 100 req/min | |
| Production Tier 2 | 1,000 req/min | |
| Production Tier 3 | 5,000 req/min | Custom negotiated above this |

---

## Acceptance Criteria (Developer Perspective)

- [ ] Sandbox usable within 5 minutes of first visit — zero registration required
- [ ] All error responses follow consistent JSON schema: `{ "error": "error_code", "hint": "human-readable explanation" }`
- [ ] OpenAPI spec passes validator — can be imported directly into Postman or Insomnia
- [ ] SDK available for Python and JavaScript by end of Phase 3
- [ ] Public status page at `status.nid.gov.np` — shows uptime, incidents, planned maintenance
- [ ] Breaking API changes announced minimum 90 days in advance with migration guide
- [ ] NRB sandbox AML rules published as versioned documentation — changes announced 30 days ahead

---

*Document version: 0.1 · System: NID API + NRB Sandbox · Related: UC-01 (Citizen), UC-02 (Financial Institution), UC-05 (NRB Regulator)*
