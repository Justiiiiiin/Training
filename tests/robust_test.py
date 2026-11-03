"""Kaputte oder fremde gespeicherte Daten (Import, Sync, alte Versionen): kein Absturz, kein eingeschleustes HTML."""
import json
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

X = '"><img src=x onerror=__x.push(1)>'
VISIT = r"""async () => {
  const errs = [];
  const tryit = (n, f) => { try { f(); } catch (e) { errs.push(n + ": " + e.message); } };
  for (const t of Object.keys(TABN)) tryit("tab " + t, () => showTab(t));
  tryit("eat", () => openEat());
  tryit("eathist", () => { HISTN = 999; renderEatHist(); });
  tryit("sum", () => WK.length && openSummary(WK.length - 1));
  tryit("charts", () => renderCharts());
  await new Promise((r) => setTimeout(r, 200));
  return { errs, xss: window.__x.length + document.querySelectorAll("img[src=x]").length };
}"""
CASES = {
  "Warenkorb mit unbekanntem Rezept": {"fc_cart": [{"id": "gibt-es-nicht", "n": 1}]},
  "Rad-Plan: days ist Text": {"fc_radplans": {"day": {"days": "x"}}},
  "Rad-Plan: slots ist Zahl": {"fc_radplans": {"day": {"days": [{"name": "Heute", "slots": 5}]}}},
  "Rad-Plan: Tag ist null": {"fc_radplans": {"week": {"days": [None]}}},
  "Rad: falscher Modus": {"fc_rad": {"mode": "zzz", "people": "x"}},
  "Training: Sätze mit null": {"fc_wk": [{"date": "2026-11-01", "sets": [None, 5, "x"], "min": 3}]},
  "Tagesplan: falsche Form": {"fc_diary": {"2026-11-03": {"items": [], "water": 0, "plan": {"ids": "x", "done": 5}}}},
  "Tagesplan: Zahl": {"fc_diary": {"2026-11-03": {"items": [], "water": 0, "plan": 7}}},
  "HTML im Trainingsdatum": {"fc_wk": [{"date": "2026-11-01" + X, "min": 20, "sets": [{"ex": "squat", "lvl": 0, "set": 1, "reps": 10, "secs": None}]}]},
  "HTML in Trainingswerten": {"fc_wk": [{"date": "2026-11-01", "min": X, "effort": X, "sets": [{"ex": "squat", "lvl": X, "set": 1, "reps": X, "secs": X}]}]},
}
with sync_playwright() as p:
    b = p.chromium.launch()
    # gültigen Rad-Plan erzeugen, damit Name und Label mit HTML geprüft werden können
    c = b.new_context(); pg = c.new_page(); pg.goto(URL); pg.wait_for_timeout(500)
    rpl = pg.evaluate("(() => { RAD.mode = 'week'; return radBuild(); })()"); c.close()
    for d in rpl["days"]:
        d["name"] += X
        for s in d["slots"]: s["label"] += X
    CASES["HTML im Rad-Plan"] = {"fc_rad": {"mode": "week"}, "fc_radplans": {"week": rpl}}
    for name, data in CASES.items():
        c = b.new_context(viewport={"width": 390, "height": 844})
        seed = "".join("localStorage.setItem(%s,%s);" % (json.dumps(k), json.dumps(json.dumps(v))) for k, v in data.items())
        c.add_init_script("window.__x=[]; if(!sessionStorage.getItem('seeded')){sessionStorage.setItem('seeded','1');" + seed + "}")
        pg = c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(600)
        r = pg.evaluate(VISIT)
        ck(name + ": kein Absturz", not errs and not r["errs"], str(errs[:2] + r["errs"][:2]))
        ck(name + ": kein HTML ausgeführt", r["xss"] == 0, str(r["xss"]))
        ck(name + ": App vollständig gestartet", pg.evaluate("!!document.querySelector('#panel-heute .card') && window.__fcReady === true && !document.getElementById('startfail')"))
        c.close()
    # Speicher voll: Hinweis statt stillem Datenverlust, App läuft weiter
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500)
    ck("Vorher kein Hinweis", not pg.evaluate("!!(document.getElementById('toast') && !document.getElementById('toast').hidden)"))
    pg.evaluate("() => { Storage.prototype.setItem = function () { throw new DOMException('voll', 'QuotaExceededError'); }; return 1; }")
    pg.evaluate("logEat(RECIPES[0], 1)"); pg.wait_for_timeout(200)
    t = pg.evaluate("(document.getElementById('toast') || {}).textContent || ''")
    ck("Speicher voll: Hinweis erscheint", "Speicher" in t and "Sicherung" in t, t[:80])
    ck("Speicher voll: Eintrag bleibt in der Sitzung", pg.evaluate("dayGet().items.length") == 1)
    ck("Speicher voll: kein Absturz", not errs, str(errs[:2]))
    c.close()
    # Fehler mitten im Start: Hinweis mit Neu laden und Sicherung statt halber App
    c = b.new_context(viewport={"width": 390, "height": 844}, permissions=["clipboard-read", "clipboard-write"])
    c.add_init_script("localStorage.setItem('fc_sessions', JSON.stringify(['2026-11-01'])); Intl.NumberFormat = function () { throw new Error('kaputt'); };")
    pg = c.new_page(); pg.goto(URL); pg.wait_for_timeout(600)
    ck("Startfehler: Hinweis sichtbar", pg.is_visible("#startfail"), pg.evaluate("(document.getElementById('startfail') || {}).textContent || ''")[:120])
    ck("Startfehler: Fehlertext genannt", "kaputt" in pg.inner_text("#startfail"))
    pg.click("#startfail >> text=Sicherung kopieren"); pg.wait_for_timeout(300)
    clip = pg.evaluate("navigator.clipboard.readText()")
    ck("Startfehler: Sicherung kopierbar", '"fitness-coach"' in clip and "fc_sessions" in clip, clip[:60])
    c.close()
    b.close()
print("FAILS", fails)
