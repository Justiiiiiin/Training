"""Offline-Speicher: ein Eintrag pro Datei über mehrere Versionen, offline kommt die neueste Fassung."""
import os, re, shutil, subprocess, tempfile, time
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)
D = tempfile.mkdtemp(prefix="fc-sw-")
site = os.path.join(D, "site")
shutil.copytree(fcenv.APP_DIR, site, ignore=shutil.ignore_patterns(".git", "tests", "tools", "docs", "__pycache__"))
def setver(v, marker):
    p = os.path.join(site, "index.html"); s = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(re.sub(r'(id="appver"[^>]*>)[^<]*', r"\g<1>" + v, s))
    a = os.path.join(site, "js", "start.js"); s = open(a, encoding="utf-8").read()
    s = re.sub(r"\nwindow\.__ver = .*", "", s) + "\nwindow.__ver = %r;\n" % marker
    open(a, "w", encoding="utf-8").write(s)
srv = subprocess.Popen(["python3", "-m", "http.server", "8124", "-d", site], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
URL = "http://127.0.0.1:8124/index.html"
Q = "caches.open('fc-offline-v3').then(c => c.keys()).then(r => r.map(x => new URL(x.url).pathname + new URL(x.url).search))"
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); c = b.new_context(); pg = c.new_page()
        sizes = []
        for v in ["v9.1", "v9.2", "v9.3"]:
            setver(v, v); pg.goto(URL); pg.wait_for_timeout(2000); pg.reload(); pg.wait_for_timeout(2000)
            sizes.append(len(pg.evaluate(Q)))
        keys = pg.evaluate(Q)
        ck("Speicher wächst nicht mit neuen Versionen", sizes[0] == sizes[1] == sizes[2], str(sizes))
        ck("keine Einträge mit ?v=", not [k for k in keys if "?" in k], str([k for k in keys if "?" in k][:3]))
        ck("neueste Version geladen", pg.evaluate("window.__ver") == "v9.3")
        c.set_offline(True); pg.reload(); pg.wait_for_timeout(2500)
        ck("offline: neueste Skripte aus dem Speicher", pg.evaluate("window.__ver") == "v9.3" and pg.evaluate("window.__fcReady === true"), str(pg.evaluate("window.__ver")))
        ck("offline: Version im Kopf passt", "v9.3" in pg.inner_text("#appver"))
        b.close()
finally:
    srv.terminate(); shutil.rmtree(D, ignore_errors=True)
print("FAILS", fails)
