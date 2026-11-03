import sys
from playwright.sync_api import sync_playwright
url = __import__("fcenv").APP_URL
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 900, "height": 1000})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(url)
    pg.wait_for_timeout(500)
    ph = lambda: pg.evaluate("W.phase")
    pg.evaluate("act('start')"); print("nach Start:", ph())
    pg.evaluate("act('next')"); print("nach weiter:", ph(), pg.evaluate("EX[W.ex].name"))
    pg.evaluate("act('done')"); print("nach fertig:", ph())
    pg.evaluate("act('pause')"); print("pausiert:", pg.evaluate("tm.running"))
    pg.evaluate("act('resume')"); print("fortgesetzt:", pg.evaluate("tm.running"))
    pg.evaluate("act('next')"); print("Satz:", pg.evaluate("[W.ex, W.set, W.phase]"))
    pg.evaluate("act('back')"); print("zurueck:", pg.evaluate("[W.ex, W.set, W.phase]"))
    n = 0
    while ph() != "done" and n < 80:
        pg.evaluate("act(W.phase==='hold'||W.phase==='work' ? 'done' : 'next')"); n += 1
    print("Ende:", ph(), "Schritte", n, "Sessions", pg.evaluate("sessions.length"))
    pg.evaluate("saveEntry({weight:79.5}); saveEntry({waist:92})")
    print("Log:", pg.evaluate("JSON.stringify(log)"))
    pg.evaluate("act('stop')")
    pg.evaluate("act('start'); act('next')")
    pg.evaluate("showTab('fortschritt')")
    pg.screenshot(path=__import__("fcenv").SHOTS + "/desktop.png")
    m = b.new_page(viewport={"width": 390, "height": 844})
    m.goto(url); m.wait_for_timeout(300)
    m.evaluate("act('start'); act('next')")
    m.screenshot(path=__import__("fcenv").SHOTS + "/mobile.png")
    print("Fehler:", errs)
    b.close()
