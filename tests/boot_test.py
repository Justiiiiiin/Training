"""Start: Ladegerüst statt halber Oberfläche, Skripte laden bei hängendem Sync schon vor, Startfehler bleibt sichtbar."""
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

    # 3) Fehlt data.js ganz: Hinweis mit Neu laden ist sichtbar (nicht hinter dem Gerüst versteckt)
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    pg.route("**/js/data.js*", lambda r: r.abort())
    pg.goto(fcenv.APP_URL); pg.wait_for_selector("#startfail", timeout=10000)
    ck("Startfehler sichtbar", pg.is_visible("#startfail"))
    ck("Startfehler zeigt die Oberfläche", pg.evaluate("document.documentElement.hasAttribute('data-ready')"))
    c.close()

    # 4) Mit Sync und hängendem Netz: alle Skripte sind schon da, bevor der Abgleich fertig ist
    c = b.new_context(viewport={"width": 390, "height": 844})
    c.add_init_script("localStorage.setItem('fc__sb', %s);" % json.dumps(SB))
    pend = []
    c.route("https://x.supabase.co/**", lambda r: pend.append(r))
    pg = c.new_page(); done = set()
    pg.on("requestfinished", lambda r: done.add(r.url.split("/")[-1].split("?")[0]))
    pg.goto(fcenv.APP_URL, wait_until="domcontentloaded"); pg.wait_for_timeout(1500)
    started = pg.evaluate("window.__fcReady === true")
    ck("Sync hängt: App wartet noch", not started)
    ck("Sync hängt: Skripte trotzdem schon geladen", {"data.js", "app.js", "v3.js", "start.js"} <= done, sorted(done))
    ck("Vorladen per link rel=preload", pg.evaluate("document.querySelectorAll('link[rel=preload][as=script]').length") == 4)
    for r in pend:
        try: r.abort()
        except Exception: pass
    pg.wait_for_timeout(300)
    c.close()
    b.close()

print("FAILS", fails)
