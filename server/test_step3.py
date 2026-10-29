#!/usr/bin/env python3
"""Step 3 API test suite — run against live server on localhost:4000"""
import json, subprocess, sys

BASE = "http://localhost:4000"

def curl(args, data=None):
    cmd = ["curl", "-s"] + args
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    body = json.loads(r.stdout) if r.stdout.strip() else None
    return body, r.returncode

def post(path, data):
    return curl([f"{BASE}{path}", "-X", "POST"], data)

def get(path, token=None):
    args = [f"{BASE}{path}"]
    if token:
        args += ["-H", f"Authorization: Bearer {token}"]
    return curl(args)

def put(path, data, token):
    cmd = [
        "curl", "-s", f"{BASE}{path}", "-X", "PUT",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not r.stdout.strip():
        return None, r.returncode
    try:
        body = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None, r.returncode
    return body, r.returncode

def get_status(path, extra_args=None):
    args = [f"{BASE}{path}", "-o", "/dev/null", "-w", "%{http_code}"]
    if extra_args:
        args += extra_args
    r = subprocess.run(["curl", "-s"] + args, capture_output=True, text=True)
    return r.stdout.strip()

results = []

def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail[:120]))
    print(f"  {status} {name}" + (f"  {detail[:80]}" if detail else ""))

# --- Auth Tests ---

# 1. Signup
body, rc = post("/api/auth/signup", {"email": "api_test_3@test.com", "password": "StrongPass1!"})
test("01. Signup (210 Created)",
     body is not None and body.get("token") and body.get("userId"),
     f"rc={rc} body={str(body)[:80]}")
token = body["token"] if body else ""

# 2. Login
body, rc = post("/api/auth/login", {"email": "api_test_3@test.com", "password": "StrongPass1!"})
test("02. Login (200 OK)",
     body is not None and body.get("token"),
     f"rc={rc}")

# 3. Login - wrong password -> 401
status = get_status("/api/auth/login", ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps({"email": "api_test_3@test.com", "password": "WrongPass99!"})])
test("03. Wrong password (401)", status == "401", f"got {status}")

# 4. Login - nonexistent -> 401
status = get_status("/api/auth/login", ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps({"email": "nonexist@test.com", "password": "StrongPass1!"})])
test("04. Nonexistent user (401)", status == "401", f"got {status}")

# 5. Signup - short password -> 400
status = get_status("/api/auth/signup", ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps({"email": "short@test.com", "password": "abc"})])
test("05. Short password (400)", status == "400", f"got {status}")

# 6. Signup - bad email -> 400
status = get_status("/api/auth/signup", ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps({"email": "notemail", "password": "StrongPass1!"})])
test("06. Bad email (400)", status == "400", f"got {status}")

# 7. Signup - duplicate -> 409
body2, rc2 = post("/api/auth/signup", {"email": "api_test_3@test.com", "password": "StrongPass1!"})
test("07. Duplicate email (409)",
     body2 is not None and body2.get("error") and "already" in body2["error"].lower(),
     f"rc={rc2} error={body2.get('error','')}")

# 8. Signup - lowercase enforcement
body3, rc3 = post("/api/auth/signup", {"email": "UPPER_CASE@test.com", "password": "StrongPass1!"})
body_profile, _ = get("/api/profile", token=body3.get("token",""))
test("08. Lowercase email persisted",
     body_profile is not None and body_profile.get("email") == "upper_case@test.com",
     f"email={body_profile.get('email','')}")

# --- Profile Tests ---

# 9. Get profile - no auth -> 401
status = get_status("/api/profile")
test("09. Get profile no auth (401)", status == "401", f"got {status}")

# 10. Get profile - with auth -> 200
body, rc = get("/api/profile", token=token)
test("10. Get profile auth (200)",
     body is not None and body.get("email") == "api_test_3@test.com" and "contact" in body,
     f"rc={rc} email={body.get('email','')} contact={bool(body.get('contact'))}")

# 11. Bad JWT -> 401
status = get_status("/api/profile", ["-H", "Authorization: Bearer invalid.token.here"])
test("11. Bad JWT (401)", status == "401", f"got {status}")

# 12. Update profile (full)
body, rc = put("/api/profile", {
    "firstName": "Jane",
    "lastName": "Smith",
    "phone": "(555) 123-4567",
    "addressLine1": "742 Evergreen Terrace",
    "city": "Springfield",
    "state": "OR",
    "zipCode": "97477"
}, token)
test("12. Update profile (200)",
     body is not None and body.get("contact",{}).get("firstName") == "Jane",
     f"rc={rc} firstName={body.get('contact',{}).get('firstName','')}")

# 13. Verify update persisted
body, rc = get("/api/profile", token=token)
c = body.get("contact", {})
expected = {"firstName":"Jane","lastName":"Smith","phone":"(555) 123-4567","addressLine1":"742 Evergreen Terrace","city":"Springfield","state":"OR","zipCode":"97477"}
all_match = all(c.get(k) == v for k, v in expected.items())
test("13. Update persisted", all_match, f"contact={json.dumps(c)[:100]}")

# 14. Partial update (merge)
body, rc = put("/api/profile", {"city": "Portland"}, token)
test("14. Partial update (merge)",
     body.get("contact",{}).get("city") == "Portland" and body.get("contact",{}).get("firstName") == "Jane",
     f"city={body.get('contact',{}).get('city')} fn={body.get('contact',{}).get('firstName')}")

# 15. Empty body update (idempotent)
body, rc = put("/api/profile", {}, token)
test("15. Empty body update",
     body is not None and body.get("contact",{}).get("city") == "Portland",
     f"rc={rc}")

# 16. Empty token -> 401
status = get_status("/api/profile", ["-H", "Authorization: Bearer "])
test("16. Empty token (401)", status == "401", f"got {status}")

# --- Summary ---
passed = sum(1 for s in results if s[1] == "PASS")
failed = sum(1 for s in results if s[1] != "PASS")
print(f"\n{'='*70}")
print(f"STEP 3 TEST RESULTS: {passed} PASSED, {failed} FAILED, {len(results)} TOTAL")
print(f"{'='*70}")
sys.exit(0 if failed == 0 else 1)
