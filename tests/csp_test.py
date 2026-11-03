"""Content-Security-Policy: keine Inline-Skripte, eingeschleuste Handler laufen nicht, App läuft vollständig."""
import os, re
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)
html = open(fcenv.APP_FILE, encoding="utf-8").read()
sw = open(os.path.join(fcenv.APP_DIR, "sw.js"), encoding="utf-8").read()
ck("index.html ohne Inline-Skripte", not re.search(r"<script(?![^>]*\bsrc=)[^>]*>", html))
ck("index.html ohne on…-Attribute", not re.search(r"\son[a-z]+=", html))
ck("csp.js als erstes Skript", html.index('src="js/csp.js"') < html.index("<script", html.index('src="js/csp.js"') + 1))
srcs = re.findall(r'<script src="([^"]+)"', html)
boot = open(os.path.join(fcenv.APP_DIR, "js", "boot.js"), encoding="utf-8").read()
lazy = re.findall(r'"(js/[a-z0-9]+\.js)"', boot[boot.index("FC_FILES"):])
ck("alle Skripte im Offline-Speicher", all('"%s"' % f in sw for f in srcs + lazy + ["styles.css"]), str(srcs + lazy))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844}); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("window.__x = []; document.addEventListener('securitypolicyviolation', e => (window.__v = window.__v || []).push(e.violatedDirective))")
    pg.goto(fcenv.APP_URL); pg.wait_for_timeout(1200)
    pol = pg.evaluate("(document.querySelector('meta[http-equiv=Content-Security-Policy]') || {}).content || ''")
    ck("CSP gesetzt", "script-src 'self'" in pol and "object-src 'none'" in pol, pol[:80])
    ck("App vollständig gestartet", pg.evaluate("window.__fcReady === true && !document.getElementById('startfail')"))
    for t in ["heute", "uebungen", "tipps", "ausblick", "rezepte", "rad", "vorkochen", "einkauf", "ernaehrung", "fortschritt"]:
        pg.evaluate(f"showTab('{t}')"); pg.wait_for_timeout(100)
    pg.evaluate("openRecipe(RECIPES[0].id)"); pg.wait_for_timeout(200)
    ck("normale Bedienung ohne CSP-Verstöße", not pg.evaluate("window.__v || []"), str(pg.evaluate("window.__v || []")))
    pg.evaluate("document.body.insertAdjacentHTML('beforeend', '<img src=x onerror=__x.push(1)>')"); pg.wait_for_timeout(300)
    ck("eingeschleuster onerror-Handler läuft nicht", pg.evaluate("window.__x.length") == 0)
    ck("Verbindung zu fremdem Server blockiert", pg.evaluate("fetch('https://example.com/x').then(() => 'durch', () => 'blockiert')") == "blockiert")
    ck("keine Fehler", not errs, str(errs[:2]))
    b.close()
print("FAILS", fails)
