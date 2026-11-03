"""Schriften kommen aus dem Repo (fonts/), keine Anfrage an Google, Service Worker hält sie offline vor."""
import os, re
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)
html = open(fcenv.APP_FILE, encoding="utf-8").read()
sw = open(os.path.join(fcenv.APP_DIR, "sw.js"), encoding="utf-8").read()
ck("kein Google Fonts im HTML", "fonts.googleapis" not in html and "fonts.gstatic" not in html)
files = re.findall(r"url\((fonts/[^)]+\.woff2)\)", html)
ck("@font-face verweist auf lokale Dateien", len(files) == 4, str(files))
ck("alle Schriftdateien vorhanden", all(os.path.isfile(os.path.join(fcenv.APP_DIR, f)) for f in files))
ck("Service Worker speichert alle Schriften", all('"%s"' % f in sw for f in files))
ck("Lizenztexte liegen bei", all(os.path.isfile(os.path.join(fcenv.APP_DIR, "fonts", f)) for f in ["OFL-BricolageGrotesque.txt", "OFL-HankenGrotesk.txt"]))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); ext = []; cons = []
    pg.on("request", lambda r: ext.append(r.url) if not r.url.startswith(("file:", "data:", "blob:")) else None)
    pg.on("console", lambda m: cons.append(m.text) if m.type == "error" else None)
    pg.goto(fcenv.APP_URL); pg.wait_for_timeout(1000)
    ck("keine Anfragen nach außen beim Start", not ext, str(ext[:3]))
    ck("Hanken Grotesk geladen", pg.evaluate("document.fonts.ready.then(() => document.fonts.check('16px \"Hanken Grotesk\"') && Array.from(document.fonts).some(f => f.family.includes('Hanken') && f.status === 'loaded'))"))
    ck("Bricolage Grotesque geladen", pg.evaluate("Array.from(document.fonts).some(f => f.family.includes('Bricolage') && f.status === 'loaded')"))
    ck("keine Konsolenfehler", not cons, str(cons[:2]))
    b.close()
print("FAILS", fails)
