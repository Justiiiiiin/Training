"""Supabase-Sync: liest nur die eigenen Zeilen (user_id aus dem Token) und meldet bei 429 nicht ab."""
import json, base64, time
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

UID = "11111111-2222-3333-4444-555555555555"
def b64(o): return base64.urlsafe_b64encode(json.dumps(o).encode()).decode().rstrip("=")
JWT = b64({"alg": "HS256"}) + "." + b64({"sub": UID, "role": "authenticated"}) + ".sig"
SB = "https://beispiel.supabase.co"

def run(token_status=200, logout=False):
    seen = []
    with sync_playwright() as p:
        b = p.chromium.launch(); c = b.new_context(); errs = []
        def route(r):
            u = r.request.url; seen.append((r.request.method, u))
            if "/auth/v1/token" in u:
                if token_status != 200: return r.fulfill(status=token_status, content_type="application/json", body="{}")
                return r.fulfill(status=200, content_type="application/json", body=json.dumps({"access_token": JWT, "refresh_token": "rt", "expires_in": 3600}))
            if "/rest/v1/kv" in u and r.request.method == "GET":
                return r.fulfill(status=200, content_type="application/json", body="[]")
            return r.fulfill(status=201, content_type="application/json", body="")
        c.route(SB + "/**", route)
        cfg = {"url": SB, "key": "anon", "email": "a@b.de", "rt": "rt", "at": JWT, "exp": int(time.time() * 1000) + 3600000}
        c.add_init_script("if (!sessionStorage.getItem('seeded')) { sessionStorage.setItem('seeded', '1'); localStorage.setItem('fc__sb', %s); }" % json.dumps(json.dumps(cfg)))
        pg = c.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1500)
        st = pg.evaluate("FC.state()")
        if logout:
            pg.click("#b-settings") if pg.is_visible("#b-settings") else pg.evaluate("openSettings()")
            pg.evaluate("document.getElementById('sbbox').open = true"); pg.wait_for_timeout(200)
            pg.click("#sb-logout")
            try: pg.wait_for_function("localStorage.getItem('fc__sb') === null", timeout=8000)
            except Exception: pass
            pg.wait_for_timeout(300)
            st = pg.evaluate("localStorage.getItem('fc__sb')")
        b.close()
    return seen, st, errs

seen, st, errs = run()
gets = [u for m, u in seen if m == "GET" and "/rest/v1/kv" in u]
ck("Lesen filtert auf eigene user_id", gets and all("user_id=eq." + UID in u for u in gets), str(gets[:1]))
ck("Sync verbunden", st == "ok", st)
ck("keine Fehler", not errs, str(errs[:2]))
seen, st, errs = run(429)
ck("429 beim Token-Erneuern: keine Abmeldung", st != "login", st)
seen, st, errs = run(logout=True)
lo = [u for m, u in seen if m == "POST" and "/auth/v1/logout" in u]
ck("Abmelden beendet die Sitzung beim Server (nur dieses Gerät)", len(lo) == 1 and "scope=local" in lo[0], str(lo))
ck("Abmelden löscht die lokale Verbindung", st is None, str(st))
print("FAILS", fails)
