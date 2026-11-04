"""Ausblick: Karte "Deine Pfade" mit Fortschrittsbalken pro Übung und dem Klimmzug-Weg."""
import time
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

with sync_playwright() as p:
    b = p.chromium.launch(); c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.goto(fcenv.APP_URL)
    t = time.time()
    while time.time() - t < 20 and not pg.evaluate("window.__fcReady === true"): pg.wait_for_timeout(100)
    pg.evaluate("() => showTab('ausblick', true)"); pg.wait_for_timeout(300)
    n = pg.evaluate("document.querySelectorAll('#panel-ausblick .paths > li').length")
    ck("Karte Deine Pfade: 6 Übungen und der Klimmzug-Weg", n == 7 and "Deine Pfade" in pg.inner_text("#panel-ausblick"), n)
    ck("Karte ist nicht eingeklappt", pg.is_visible("#panel-ausblick .paths"))
    first = pg.evaluate("[...document.querySelectorAll('#panel-ausblick .paths > li')].map((li) => li.querySelector('.vname').textContent + ' ' + li.querySelector('.vnum').textContent)")
    ck("Startwerte: Stufe von Anzahl", first[0].startswith("Kniebeuge") and first[0].replace(" ", "").endswith(("2von5", "1von5")), first)
    r = pg.evaluate("""() => { levels.squat = 2; settings.ms = { mhang30: todayISO(), mneg: todayISO() }; renderAusblick(); const li = document.querySelector('#panel-ausblick .paths > li');
      const bar = li.querySelector('.vbar'); const k = [...document.querySelectorAll('#panel-ausblick .paths > li')].pop();
      return { num: li.querySelector('.vnum').textContent, w: li.querySelector('.vbar i').style.width, now: li.querySelector('.vbar').getAttribute('aria-valuenow'), max: bar.getAttribute('aria-valuemax'), kname: k.querySelector('.vname').textContent, knum: k.querySelector('.vnum').textContent, ksub: k.querySelector('.vsub').textContent }; }""")
    ck("Kniebeuge Stufe 3 von 5, Balken 60 %", r["num"].replace(" ", "") == "3von5" and r["w"] == "60%" and r["now"] == "3" and r["max"] == "5", r)
    ck("Klimmzug-Weg: 2 von 3, nächster Schritt genannt", r["kname"] == "Klimmzug" and r["knum"].replace(" ", "") == "2von3" and "erste Klimmzug" in r["ksub"] and r["ksub"].count("erste Klimmzug") == 1, r)
    r = pg.evaluate("""() => { settings.ms = { mhang30: todayISO(), mneg: todayISO(), mpull: todayISO() }; renderAusblick(); const k = [...document.querySelectorAll('#panel-ausblick .paths > li')].pop(); return { sub: k.querySelector('.vsub').textContent, cls: k.querySelector('.vbar i').className }; }""")
    ck("Klimmzug erreicht: Ziel erreicht, grüner Balken", "Ziel erreicht" in r["sub"] and r["cls"] == "good", r)
    r = pg.evaluate("""() => { levels.squat = 4; renderAusblick(); const li = document.querySelector('#panel-ausblick .paths > li'); return { sub: li.querySelector('.vsub').textContent, cls: li.querySelector('.vbar i').className }; }""")
    ck("Schwerste Stufe: Ziel erreicht", "Ziel erreicht" in r["sub"] and r["cls"] == "good", r)
    r = pg.evaluate("""() => { levels.squat = 1; WK.length = 0; WK.push({ sets: [{ ex: 'squat', lvl: 1 }] }); const keep = window.evalEx; window.evalEx = () => ({ status: 'up' }); renderAusblick();
      const li = document.querySelector('#panel-ausblick .paths > li'); const t = li.textContent; window.evalEx = keep; return t; }""")
    ck("Bereit für die nächste Stufe wird gezeigt", "Bereit für die nächste Stufe" in r, r[-120:])
    ok = pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    ck("kein seitlicher Überlauf", ok)
    ck("keine JS-Fehler", not errs, errs[:2])
    c.close(); b.close()
print("FAILS", fails)
