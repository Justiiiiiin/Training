from playwright.sync_api import sync_playwright
import subprocess, time, signal, os
srv=subprocess.Popen(["python3","-m","http.server","8123","--bind","127.0.0.1"],cwd=__import__("fcenv").APP_DIR,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
try:
    with sync_playwright() as p:
        b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
        pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto("http://127.0.0.1:8123/index.html"); pg.wait_for_timeout(1500)
        ck("Manifest-Link gesetzt", pg.evaluate("!!document.querySelector('link[rel=manifest]')"))
        ck("Manifest laedt", pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json()).then(j=>j.display)")=="standalone")
        st=pg.evaluate("navigator.serviceWorker.ready.then(r=>!!r.active)"); ck("Service Worker aktiv", st)
        pg.wait_for_timeout(800)
        keys=pg.evaluate("caches.keys()"); ck("Cache angelegt", keys==["fc-offline-v3"], keys)
        files=pg.evaluate("caches.open('fc-offline-v3').then(c=>c.keys()).then(k=>k.map(r=>new URL(r.url).pathname))"); print("  im Cache:",files)
        ck("index.html im Cache", "/index.html" in files)
        ver=pg.evaluate("document.getElementById('appver').textContent")
        # Offline neu laden
        pg.reload(); pg.wait_for_timeout(800)   # SW kontrolliert jetzt die Seite
        c.set_offline(True)
        pg.reload(); pg.wait_for_timeout(1500)
        ck("Offline: Seite laedt aus dem Cache", pg.evaluate("document.getElementById('appver').textContent")==ver, ver)
        ck("Offline: App rendert (Heute)", "Heute" in pg.inner_text("#pagetitle") or "Guten" in pg.inner_text("#pagetitle"), pg.inner_text("#pagetitle"))
        pg.evaluate("showTab('rezepte')"); pg.wait_for_timeout(300)
        ck("Offline: 1000 Rezepte", "1000" in pg.inner_text("#rcount"), pg.inner_text("#rcount"))
        c.set_offline(False)
        pg.reload(); pg.wait_for_timeout(1000)
        ck("Wieder online: laedt", pg.evaluate("!!document.getElementById('appver')"))
        # Verbindung kopieren/einfuegen (ohne Netz-Login): Felder fuellen
        pg.evaluate("showTab('heute')")
        pg.evaluate("document.getElementById('dlg-settings').showModal()")
        ck("Installationshinweis sichtbar", pg.is_visible("#instbox") and "Noch nicht installiert" in pg.inner_text("#instinfo"), pg.inner_text("#instinfo")[:60])
        pg.evaluate("document.getElementById('sbbox').open=true")
        pg.fill("#sb-paste", 'FCSB:{"url":"https://abc.supabase.co","key":"anon123","mail":"a@b.de"}'); pg.wait_for_timeout(200)
        ck("Verbindung einfuegen fuellt Felder", pg.input_value("#sb-url")=="https://abc.supabase.co" and pg.input_value("#sb-key")=="anon123" and pg.input_value("#sb-mail")=="a@b.de")
        pg.fill("#sb-paste", 'FCSB:kaputt'); pg.wait_for_timeout(200)
        ck("Kaputte Verbindung: Meldung", "nicht nach" in pg.inner_text("#sbmsg"), pg.inner_text("#sbmsg"))
        print("Fehler:",errs); ck("keine Fehler", not errs)
        b.close()
finally:
    srv.send_signal(signal.SIGTERM)
print("FAILS",fails)
