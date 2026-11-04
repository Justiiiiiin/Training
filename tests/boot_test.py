"""Start: Ladegerüst statt halber Oberfläche, fehlende Datei beim Start wird einmal automatisch neu versucht, Startfehler bleibt sichtbar und nennt die Datei."""
import json, threading, time
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

def wait_ready(pg, ms=20000):
    """Per evaluate abfragen: wait_for_function nutzt eval und wird von der Content-Security-Policy der Seite blockiert."""
    t = time.time()
    while time.time() - t < ms / 1000:
        if pg.evaluate("window.__fcReady === true"): return True
        pg.wait_for_timeout(100)
    return False

SB = json.dumps({"url": "https://x.supabase.co", "key": "k", "rt": "r", "email": "a@b.de"})
with sync_playwright() as p:
    b = p.chromium.launch()

    # 1) Normaler Start: html[data-ready] gesetzt, Oberfläche sichtbar, Gerüst weg
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(fcenv.APP_URL); ck("Start läuft durch", wait_ready(pg))
    ck("data-ready nach dem Start", pg.evaluate("document.documentElement.hasAttribute('data-ready')"))
    ck("Oberfläche sichtbar", pg.evaluate("getComputedStyle(document.querySelector('.layout')).display !== 'none' && getComputedStyle(document.querySelector('#gnav')).display !== 'none'"))
    ck("Ladegerüst weg", pg.evaluate("getComputedStyle(document.querySelector('.bootskel')).display === 'none'"))
    ck("keine JS-Fehler", not errs, errs[:2])
    c.close()

    # 2) Solange data.js hängt: keine halbe Oberfläche, nur das Gerüst; danach normal
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    held = []
    pg.route("**/js/data.js*", lambda r: held.append(r))
    pg.goto(fcenv.APP_URL, wait_until="domcontentloaded"); pg.wait_for_timeout(600)
    ck("ohne data.js: Layout und Navigation versteckt", pg.evaluate("getComputedStyle(document.querySelector('.layout')).display === 'none' && getComputedStyle(document.querySelector('#gnav')).display === 'none'"))
    ck("ohne data.js: Gerüst sichtbar", pg.evaluate("getComputedStyle(document.querySelector('.bootskel')).display !== 'none'"))
    for r in held: r.continue_()
    ck("Start läuft nach data.js durch", wait_ready(pg))
    ck("nach data.js: Oberfläche da", pg.evaluate("getComputedStyle(document.querySelector('.layout')).display !== 'none'"))
    c.close()

    # 3) Fehlt data.js ganz: nach einem automatischen Neuversuch erscheint der Hinweis (sichtbar, nennt die Datei)
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    pg.route("**/js/data.js*", lambda r: r.abort())
    pg.goto(fcenv.APP_URL); pg.wait_for_selector("#startfail", timeout=15000)
    ck("Startfehler sichtbar", pg.is_visible("#startfail"))
    ck("Startfehler zeigt die Oberfläche", pg.evaluate("document.documentElement.hasAttribute('data-ready')"))
    ck("Startfehler nennt die fehlende Datei", "data.js" in pg.inner_text("#startfail"), pg.inner_text("#startfail")[-80:])
    c.close()

    # 3b) v3.js fehlt nur beim ersten Mal (Netzaussetzer): die App lädt einmal selbst neu und startet
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    n = [0]
    def flaky(r):
        n[0] += 1
        r.abort() if n[0] == 1 else r.continue_()
    pg.route("**/js/v3.js*", flaky)
    pg.goto(fcenv.APP_URL)
    ck("v3.js einmal weg: App startet nach Neuversuch", wait_ready(pg, 20000), "Anfragen: %d" % n[0])
    ck("v3.js einmal weg: kein Fehlerhinweis", pg.evaluate("!document.getElementById('startfail')"))
    ck("v3.js einmal weg: genau ein Neuversuch", n[0] == 2, n[0])
    ck("v3.js einmal weg: Sperre nach Erfolg gelöscht", pg.evaluate("sessionStorage.getItem('fc__retry') === null"))
    c.close()

    # 3c) v3.js fehlt dauerhaft: nur ein Neuversuch (keine Schleife), Hinweis nennt v3.js statt der Folgefehler
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    m = [0]
    def gone(r):
        m[0] += 1; r.abort()
    pg.route("**/js/v3.js*", gone)
    pg.goto(fcenv.APP_URL); pg.wait_for_selector("#startfail", timeout=15000)
    pg.wait_for_timeout(1500)
    ck("v3.js dauerhaft weg: Hinweis sichtbar", pg.is_visible("#startfail"))
    ck("v3.js dauerhaft weg: Hinweis nennt v3.js", "v3.js" in pg.inner_text("#startfail"), pg.inner_text("#startfail")[-80:])
    ck("v3.js dauerhaft weg: keine Schleife (2 Versuche)", m[0] == 2, m[0])
    c.close()

    # 4) Mit Sync und hängendem Netz: App wartet, startet nach dem Abbruch des Abgleichs von selbst
    c = b.new_context(viewport={"width": 390, "height": 844})
    c.add_init_script("localStorage.setItem('fc__sb', %s);" % json.dumps(SB))
    pend = []
    c.route("https://x.supabase.co/**", lambda r: pend.append(r))
    pg = c.new_page()
    pg.goto(fcenv.APP_URL, wait_until="domcontentloaded"); pg.wait_for_timeout(1500)
    ck("Sync hängt: App wartet noch", not pg.evaluate("window.__fcReady === true"))
    ck("Sync hängt: Ladegerüst sichtbar", pg.evaluate("getComputedStyle(document.querySelector('.bootskel')).display !== 'none'"))
    for r in pend:
        try: r.abort()
        except Exception: pass
    ck("Sync abgebrochen: App startet", wait_ready(pg, 15000))
    pg.wait_for_timeout(300)
    c.close()
    b.close()

print("FAILS", fails)
