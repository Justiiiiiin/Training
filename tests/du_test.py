"""Du: gesperrter Bereich (Pflege, Haare und Bart). Inhalt liegt nur verschlüsselt in du.enc.json.
Der Test baut eine Kopie der App mit einem eigenen Testinhalt und Testcode, der echte Code kommt nie vor."""
import functools, http.server, json, os, shutil, subprocess, tempfile, threading, time
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

CODE = "testcode-12345"
tmp = tempfile.mkdtemp(prefix="fc-du-")
for f in ("index.html", "styles.css", "sw.js", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png", "apple-touch-icon.png"):
    shutil.copy(os.path.join(fcenv.ROOT, f), tmp)
for d in ("js", "fonts"):
    shutil.copytree(os.path.join(fcenv.ROOT, d), os.path.join(tmp, d))
src = os.path.join(tmp, "src.json")
json.dump({"pflege": '<div class="card" data-nofold><h3>Deine Routine</h3><p>TESTINHALT-PFLEGE</p></div>',
           "haare": '<div class="card" data-nofold><h3>Dein Haarschnitt</h3><p>TESTINHALT-HAARE</p></div>'}, open(src, "w"))
subprocess.run(["node", os.path.join(fcenv.ROOT, "tools", "du_encrypt.js"), src, os.path.join(tmp, "du.enc.json")], check=True, env=dict(os.environ, DU_CODE=CODE), capture_output=True)
os.remove(src)
# fetch() von file:// ist im Browser gesperrt, deshalb kleiner lokaler Server (wie in pwa_test.py)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=tmp))
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:%d/index.html" % srv.server_address[1]

# Die echte Datei im Repo: gültiges Format, kein Klartext
real = open(os.path.join(fcenv.ROOT, "du.enc.json"), encoding="utf-8").read()
rj = json.loads(real)
ck("du.enc.json: Format v1, PBKDF2 mit mindestens 300000 Runden", rj.get("v") == 1 and rj.get("iter", 0) >= 300000 and all(isinstance(rj.get(k), str) for k in ("salt", "iv", "ct")))
ck("du.enc.json: kein Klartext", not any(w in real for w in ("Isana", "Textured", "Balea", "Leon", "Friseur")))
ck("Service Worker kennt du.enc.json", "du.enc.json" in open(os.path.join(fcenv.ROOT, "sw.js"), encoding="utf-8").read())
quelltext = "".join(open(os.path.join(fcenv.ROOT, f), encoding="utf-8").read() for f in ("js/app.js", "js/start.js", "index.html"))
ck("Quellcode: keine Pflege-Inhalte im Klartext", not any(w in quelltext for w in ("Isana", "Textured Crop", "xskincare", "hautwahrheit")))

def ready(pg):
    t = time.time()
    while time.time() - t < 20 and not pg.evaluate("window.__fcReady === true"): pg.wait_for_timeout(100)
def waitjs(pg, js, ms=15000):
    """wait_for_function wertet Text aus und scheitert an der Content-Security-Policy, darum hier abfragen."""
    t = time.time()
    while time.time() - t < ms / 1000:
        if pg.evaluate(js): return True
        pg.wait_for_timeout(100)
    raise AssertionError("Zeitüberschreitung: " + js)
def opendu(pg):
    pg.click('.gbtn[data-group="du"]'); pg.wait_for_timeout(300)

with sync_playwright() as p:
    b = p.chromium.launch()
    for vw, vh, big in ((390, 844, False), (320, 640, True)):
        tag = " (%d px%s)" % (vw, ", große Schrift" if big else "")
        c = b.new_context(viewport={"width": vw, "height": vh}); pg = c.new_page()
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
        pg.goto(URL); ready(pg)
        if big: pg.evaluate("document.documentElement.setAttribute('data-big','1')")
        opendu(pg)
        ck("Gesperrt: Sperrseite statt Inhalt" + tag, "Gesperrt" in pg.inner_text("#panel-pflege") and "TESTINHALT" not in pg.evaluate("document.body.textContent"))
        ck("Gesperrt: Titel Du, Unterseiten Pflege und Haare und Bart" + tag, pg.inner_text("#pagetitle").strip() == "Du" and pg.evaluate("[...document.querySelectorAll('#subnav .tab')].map(e=>e.textContent.trim()).join(',')") == "Pflege,Haare und Bart")
        ck("Gesperrt: Feld hat mindestens 16 px Schrift (kein iOS-Zoom)" + tag, pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#panel-pflege .du-code')).fontSize)") >= 16)
        ck("Kein seitlicher Überlauf (gesperrt)" + tag, pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0)
        pg.click("#panel-pflege [data-duunlock]"); pg.wait_for_timeout(200)
        ck("Leere Eingabe: Hinweis" + tag, "Code ein" in pg.inner_text("#panel-pflege .du-msg"))
        pg.fill("#panel-pflege .du-code", "falscher-code"); pg.click("#panel-pflege [data-duunlock]")
        waitjs(pg, "document.querySelector('#panel-pflege .du-msg').textContent.includes('stimmt nicht')")
        ck("Falscher Code: bleibt gesperrt" + tag, "TESTINHALT" not in pg.evaluate("document.body.textContent") and pg.evaluate("localStorage.getItem('fc__du')") is None)
        pg.fill("#panel-pflege .du-code", CODE); pg.press("#panel-pflege .du-code", "Enter")
        waitjs(pg, "document.getElementById('panel-pflege').textContent.includes('TESTINHALT-PFLEGE')")
        ck("Richtiger Code (Enter): Pflege offen" + tag, pg.is_visible("#panel-pflege") and "Deine Routine" in pg.inner_text("#panel-pflege"))
        pg.click('#subnav .tab[data-tab="haare"]'); pg.wait_for_timeout(250)
        ck("Haare und Bart offen" + tag, "TESTINHALT-HAARE" in pg.inner_text("#panel-haare"))
        ck("Code nicht im Speicher abgelegt, nur der Schlüssel" + tag, CODE not in (pg.evaluate("JSON.stringify(localStorage)")))
        ck("Gemerkter Schlüssel nicht in der Sicherung" + tag, "fc__du" not in pg.evaluate("FC.exportAll()"))
        ck("Kein seitlicher Überlauf (offen)" + tag, pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 0)
        pg.reload(); ready(pg); opendu(pg)
        waitjs(pg, "document.getElementById('panel-pflege').textContent.includes('TESTINHALT-PFLEGE')")
        ck("Nach Neustart: durch gemerkten Schlüssel offen" + tag, True)
        pg.click("#panel-pflege [data-dulock]"); pg.wait_for_timeout(200)
        ck("Sperren: wieder gesperrt, Schlüssel gelöscht" + tag, "Gesperrt" in pg.inner_text("#panel-pflege") and pg.evaluate("localStorage.getItem('fc__du')") is None and "TESTINHALT" not in pg.evaluate("document.body.textContent"))
        pg.reload(); ready(pg); opendu(pg); pg.wait_for_timeout(800)
        ck("Nach Neustart und Sperren: bleibt gesperrt" + tag, "Gesperrt" in pg.inner_text("#panel-pflege"))
        pg.uncheck("#panel-pflege .du-keep"); pg.fill("#panel-pflege .du-code", CODE); pg.click("#panel-pflege [data-duunlock]")
        waitjs(pg, "document.getElementById('panel-pflege').textContent.includes('TESTINHALT-PFLEGE')")
        pg.reload(); ready(pg); opendu(pg); pg.wait_for_timeout(800)
        ck("Ohne Merken: nach Neustart wieder gesperrt" + tag, "Gesperrt" in pg.inner_text("#panel-pflege"))
        ck("Keine Fehler in der Konsole" + tag, not errs, errs)
        c.close()
    # Manipulierter Geheimtext darf nichts öffnen
    bad = json.load(open(os.path.join(tmp, "du.enc.json"))); ct = bad["ct"]; bad["ct"] = ("A" if ct[0] != "A" else "B") + ct[1:]
    json.dump(bad, open(os.path.join(tmp, "du.enc.json"), "w"))
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page(); pg.goto(URL); ready(pg); opendu(pg)
    pg.fill("#panel-pflege .du-code", CODE); pg.click("#panel-pflege [data-duunlock]"); pg.wait_for_timeout(1500)
    ck("Manipulierte Datei öffnet nichts", "TESTINHALT" not in pg.evaluate("document.body.textContent") and "Gesperrt" in pg.inner_text("#panel-pflege"))
    c.close(); b.close()
srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)
print("FAILS:", len(fails), fails)
raise SystemExit(1 if fails else 0)
