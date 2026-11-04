"""Training auf dem Handy: Jetzt/Danach-Zeilen, Erledigt-Zeile zum Aufklappen, Symbol-Knöpfe, kein Scrollen für Fertig."""
import sys
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
errs = []; fails = []


def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)


def snap(pg):
    return pg.evaluate("""() => ({
      phase: W.phase, ex: W.ex,
      now: [...document.querySelectorAll('#steps .steplist.now li')].map(l => ({ cls: l.className, name: l.querySelector('b').innerText })),
      sum: document.querySelector('#steps .stepsdone summary') ? document.querySelector('#steps .stepsdone summary').innerText : '',
      open: document.querySelector('#steps .stepsdone') ? document.querySelector('#steps .stepsdone').open : null,
      fin: document.querySelectorAll('#steps .stepsdone li').length,
      btns: [...document.querySelectorAll('#actions .btn')].map(b => ({ t: b.innerText.trim(), a: b.getAttribute('aria-label') || '', act: b.dataset.act || '', icon: b.classList.contains('icon') })),
      title: document.getElementById('title').innerText
    })""")


with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True)
    pg = c.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(URL); pg.wait_for_function("window.__fcReady === true", timeout=15000); pg.wait_for_timeout(400)
    pg.evaluate("settings.sets = 2; renderEx(); render()")
    names = pg.evaluate("EX.map(e => e.name)")
    pg.click('#panel-heute [data-act="start"]'); pg.wait_for_timeout(300)

    s = snap(pg)
    ck("Aufwärmen: zwei Zeilen (Als nächstes, Danach)", len(s["now"]) == 2 and s["now"][0]["name"] == names[0] and s["now"][1]["name"] == names[1], str(s["now"]))
    ck("Aufwärmen: keine Erledigt-Zeile", s["sum"] == "")

    pg.evaluate("act('next')"); pg.wait_for_timeout(300)
    s = snap(pg)
    ck("Übung 1: Jetzt-Zeile ist aktuelle Übung", s["now"][0]["cls"].find("cur") >= 0 and s["now"][0]["name"] == names[0])
    ck("Übung 1: Titel ist der Übungsname ohne Vorspann", s["title"] == names[0], s["title"])
    labels = [x["t"] for x in s["btns"]]
    ck("Kein Ansage- und kein Technik-Knopf", not any(("Ansage" in (x["t"] + x["a"])) or ("Technik" in (x["t"] + x["a"])) or ("Anzeige" in (x["t"] + x["a"])) for x in s["btns"]), str(labels))
    sec = [x for x in s["btns"] if x["icon"]]
    ck("Nebenknöpfe sind reine Symbole mit Beschriftung für Screenreader", len(sec) >= 3 and all(x["t"] == "" and x["a"] for x in sec), str([(x["a"], x["t"]) for x in sec]))
    fb = pg.evaluate("(() => { const e = document.querySelector('#actions .btn.primary'); const r = e.getBoundingClientRect(); return [Math.round(r.bottom), innerHeight, document.documentElement.scrollWidth, innerWidth]; })()")
    ck("Fertig liegt ohne Scrollen im Bild", fb[0] <= fb[1], str(fb))
    ck("Kein seitliches Scrollen", fb[2] <= fb[3], str(fb))
    small = pg.evaluate("[...document.querySelectorAll('#actions .btn')].filter(e => { const r = e.getBoundingClientRect(); return r.width < 44 || r.height < 44; }).length")
    ck("Alle Knöpfe mindestens 44 px", small == 0, str(small))

    # Satz 1 und 2 der ersten Übung fertig -> Übung 1 wandert in "Erledigt"
    pg.evaluate("act('done')"); pg.wait_for_timeout(300)
    s = snap(pg)
    ck("Pause: Austauschen nur als Symbol", s["phase"] == "rest" and any(x["a"] == "Austauschen" and x["t"] == "" and x["icon"] for x in s["btns"]), str([(x["a"], x["t"]) for x in s["btns"]]))
    ck("Pause: Titel zeigt die nächste Übung", s["title"] in names, s["title"])
    pg.evaluate("act('next')"); pg.wait_for_timeout(300)
    pg.evaluate("act('done')"); pg.wait_for_timeout(400)
    s = snap(pg)
    ck("Nach Übung 1: Erledigt (1) eingeklappt", s["sum"].startswith("Erledigt (1)") and s["open"] is False, s["sum"])
    ck("Nach Übung 1: Jetzt/Danach rücken weiter", s["now"][0]["name"] == names[1] and s["now"][1]["name"] == names[2], str(s["now"]))
    pg.click("#steps .stepsdone summary"); pg.wait_for_timeout(200)
    s = snap(pg)
    ck("Erledigt lässt sich aufklappen", s["open"] is True and s["fin"] == 1 and names[0] in pg.inner_text("#steps .stepsdone"))
    pg.evaluate("act('next')"); pg.wait_for_timeout(300)
    s = snap(pg)
    ck("Aufgeklappt bleibt beim Weiterschalten offen", s["open"] is True)

    for _ in range(60):
        if pg.evaluate("W.phase") in ("done", "idle"): break
        pg.evaluate("act('done')"); pg.wait_for_timeout(80)
    s = snap(pg)
    ck("Am Ende: Erledigt (6) und keine offene Zeile", s["sum"].startswith("Erledigt (6)") and len(s["now"]) == 0, s["sum"] + " " + str(s["now"]))

    b.close()
    ck("Keine Konsolenfehler", not errs, "; ".join(errs[:3]))
print("FAILS:", fails)
sys.exit(1 if fails else 0)
