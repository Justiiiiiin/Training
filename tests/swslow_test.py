"""Service Worker bei hängendem Netz (Start aus dem Speicher statt 18 s) und bei Serverfehlern 5xx (Rückfall auf den Speicher)."""
import os, shutil, tempfile, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

D = tempfile.mkdtemp(prefix="fc-slow-")
site = os.path.join(D, "site")
shutil.copytree(fcenv.APP_DIR, site, ignore=shutil.ignore_patterns(".git", "tests", "tools", "docs", "__pycache__"))
STALL = [False]
ERR = [False]
class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=site, **k)
    def log_message(self, *a): pass
    def do_GET(self):
        if STALL[0]: time.sleep(25)   # Verbindung steht, aber es kommt nichts
        if ERR[0]:                    # Hoster antwortet mit Serverfehler
            self.send_error(503); return
        try: super().do_GET()
        except Exception: pass
srv = ThreadingHTTPServer(("127.0.0.1", 8125), H)
srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = "http://127.0.0.1:8125/index.html"

def ready(pg, ms):
    t = time.time()
    while time.time() - t < ms / 1000:
        try:
            if pg.evaluate("window.__fcReady === true"): return round(time.time() - t, 1)
        except Exception: pass
        pg.wait_for_timeout(200)
    return None

try:
    with sync_playwright() as p:
        b = p.chromium.launch(); c = b.new_context(); pg = c.new_page()
        pg.goto(URL); ck("erster Start online", ready(pg, 15000) is not None)
        pg.wait_for_timeout(1500)
        pg.reload(); pg.wait_for_timeout(1500)   # ab jetzt steuert der Service Worker die Seite
        # Serverfehler 503 (zuerst, solange keine hängenden Verbindungen den Pool des Browsers belegen)
        ERR[0] = True
        pg.close(); pg = c.new_page()
        pg.goto(URL, wait_until="commit", timeout=30000)
        r = ready(pg, 20000)
        ck("Serverfehler 503: App startet aus dem Speicher", r is not None, "%s s" % r)
        ck("Serverfehler 503: schnell (unter 3 s)", r is not None and r < 3, "%s s" % r)
        ck("Serverfehler 503: kein Fehlerhinweis", pg.evaluate("!document.getElementById('startfail')"))
        ERR[0] = False
        STALL[0] = True
        pg.close(); pg = c.new_page()
        t = time.time()
        pg.goto(URL, wait_until="commit", timeout=60000)
        r = ready(pg, 40000)
        ck("Netz hängt: App startet aus dem Speicher", r is not None, "%s s" % r)
        ck("Netz hängt: nicht jede Datei wartet einzeln 4,5 s (unter 10 s)", r is not None and r < 10, "%s s" % r)
        b.close()
finally:
    STALL[0] = False
    srv.shutdown(); shutil.rmtree(D, ignore_errors=True)
print("FAILS", fails)
