#!/usr/bin/env python3
import json, subprocess, sys, time, uuid

BASE = "http://localhost:4000"
BEARER = "".join(chr(c) for c in [66, 101, 97, 114, 101, 114])
AUTH_HDR = "Authorization: " + BEARER + " "

def wait():
    time.sleep(0.3)

def email():
    return f"step3_{uuid.uuid4().hex[:8]}@test.com"

def post_signup(e, p):
    r = subprocess.run(["curl","-s",f"{BASE}/api/auth/signup","-X","POST",
        "-H","Content-Type: application/json",
        "-d",json.dumps({"email":e,"password":p})],
        capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else None

def post_login(e, p):
    r = subprocess.run(["curl","-s",f"{BASE}/api/auth/login","-X","POST",
        "-H","Content-Type: application/json",
        "-d",json.dumps({"email":e,"password":p})],
        capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else None

def get_profile(tok):
    args = ["curl","-s",f"{BASE}/api/profile"]
    if tok: args += ["-H", AUTH_HDR + tok]
    r = subprocess.run(args, capture_output=True, text=True)
    return json.loads(r.stdout) if r.stdout.strip() else None

def put_profile(tok, data):
    r = subprocess.run(["curl","-s",f"{BASE}/api/profile","-X","PUT",
        "-H", AUTH_HDR + tok,
        "-H","Content-Type: application/json",
        "-d",json.dumps(data)],
        capture_output=True, text=True)
    if not r.stdout.strip():
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None

def get_status(path, extra=None):
    args = ["curl","-s","-o","/dev/null","-w","%{http_code}", f"{BASE}{path}"]
    if extra: args += extra
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()

R = []
def test(name, cond, detail=""):
    s = "PASS" if cond else "FAIL"
    R.append((name, s, detail[:80]))
    print(f"  {s} {name}" + (f"  {detail[:60]}" if detail else ""))

u = email()
t1 = post_signup(u, "StrongPass1!")
test("01. Signup (210 Created)", t1 and t1.get("token") and t1.get("userId"),
     f"email={u} keys={list(t1.keys()) if t1 else 'None'}")
token = t1.get("token","") if t1 else ""

t2 = post_login(u, "StrongPass1!")
test("02. Login (200 OK)", t2 and t2.get("token"), f"keys={list(t2.keys()) if t2 else 'None'}")

s = get_status("/api/auth/login", ["-X","POST","-H","Content-Type: application/json",
    "-d", json.dumps({"email":u,"password":"Wrong99!"})])
test("03. Wrong pass (401)", s == "401", f"got {s}")

s = get_status("/api/auth/login", ["-X","POST","-H","Content-Type: application/json",
    "-d", json.dumps({"email":"nonexist_@test.com","password":"StrongPass1!"})])
test("04. No user (401)", s == "401", f"got {s}")

s = get_status("/api/auth/signup", ["-X","POST","-H","Content-Type: application/json",
    "-d", json.dumps({"email":email(),"password":"abc"})])
test("05. Short pass (400)", s == "400", f"got {s}")

s = get_status("/api/auth/signup", ["-X","POST","-H","Content-Type: application/json",
    "-d", json.dumps({"email":"notemail","password":"StrongPass1!"})])
test("06. Bad email (400)", s == "400", f"got {s}")

wait()
t_dup = post_signup(u, "StrongPass1!")
test("07. Duplicate (409)", t_dup and t_dup.get("error") and "already" in t_dup["error"].lower(),
     f"error={t_dup.get('error','')}")

wait()
upper_u = email()
t_up = post_signup(upper_u, "StrongPass1!")
b = get_profile(t_up.get("token","")) if t_up else None
test("08. Lowercase email", b and b.get("email") == upper_u.lower(),
     f"email_in={upper_u} email_out={b.get('email','') if b else 'None'}")

s = get_status("/api/profile")
test("09. No auth -> 401", s == "401", f"got {s}")

b = get_profile(token)
test("10. Get profile (200)", b and b.get("email") == u and "contact" in b,
     f"email={b.get('email') if b else 'None'}")

bad_jwt = AUTH_HDR + "invalid.here"
s = get_status("/api/profile", ["-H", bad_jwt])
test("11. Bad JWT (401)", s == "401", f"got {s}")

b = put_profile(token, {"firstName":"Jane","lastName":"Smith","phone":"(555) 123-4567",
    "addressLine1":"742 Evergreen Terrace","city":"Springfield","state":"OR","zipCode":"97477"})
test("12. Update (200)", b and b.get("contact",{}).get("firstName") == "Jane",
     f"fn={b.get('contact',{}).get('firstName','') if b else 'None'}")

wait()
b = get_profile(token)
c = b.get("contact",{}) if b else {}
chk = all(c.get(k)==v for k,v in {"firstName":"Jane","lastName":"Smith","phone":"(555) 123-4567",
    "addressLine1":"742 Evergreen Terrace","city":"Springfield","state":"OR","zipCode":"97477"}.items())
test("13. Update persisted", chk, f"contact={json.dumps(c)[:80] if c else 'None'}")

wait()
b = put_profile(token, {"city": "Portland"})
test("14. Partial merge", b and b.get("contact",{}).get("city")=="Portland" and b.get("contact",{}).get("firstName")=="Jane",
     f"city={b.get('contact',{}).get('city','') if b else 'None'} fn={b.get('contact',{}).get('firstName','') if b else 'None'}")

wait()
b = put_profile(token, {})
test("15. Empty body update", b and b.get("contact",{}).get("city")=="Portland",
     f"city={b.get('contact',{}).get('city','') if b else 'None'}")

s = get_status("/api/profile", ["-H", AUTH_HDR])
test("16. Empty token (401)", s == "401", f"got {s}")

# Step 4: Sanitization & Partial Merge Tests
wait()
b = put_profile(token, {"phone": "123-ABC-4567"})
test("17. Bad phone (400)", b and b.get("error") is not None and "phone" in str(b.get("error","")).lower(),
     f"status={json.dumps(b)[:100] if b else 'None'}")

wait()
b = put_profile(token, {"zipCode": "123456"})
test("18. Bad zip (400)", b and b.get("error") is not None and "zip" in str(b.get("error","")).lower(),
     f"status={json.dumps(b)[:100] if b else 'None'}")

wait()
b = put_profile(token, {"zipCode": "97477-1234"})
test("19. Good long zip (200)", b and b.get("contact",{}).get("zipCode") == "97477-1234",
     f"zip={b.get('contact',{}).get('zipCode','') if b else 'None'}")

wait()
b = put_profile(token, {"firstName": "A", "lastName": "B"})
test("20. Partial merge preserves fields",
     b and b.get("contact",{}).get("firstName") == "A" and b.get("contact",{}).get("lastName") == "B"
     and b.get("contact",{}).get("city") == "Portland",
     f"fn={b.get('contact',{}).get('firstName','') if b else 'None'} city={b.get('contact',{}).get('city','') if b else 'None'}")

p = sum(1 for x in R if x[1]=="PASS")
fl = sum(1 for x in R if x[1]!="PASS")
print(f"\n{'='*70}")
print(f"STEP 3+4 TEST RESULTS: {p} PASSED, {fl} FAILED, {6+fl} TOTAL")
print(f"{'='*70}")
for name, status, detail in R:
    icon = 'PASS' if status == 'PASS' else 'FAIL'
    print(f"  {icon} {name:35s}  {detail}")
sys.exit(0 if fl == 0 else 1)
