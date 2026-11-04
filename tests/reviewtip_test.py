"""Wochenrückblick: ein Satz "Fürs nächste Mal" mit der größten Lücke der Woche."""
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
    pg.evaluate("() => { GOALS.protein = 128; GOALS.kcal = 1900; window.__r = (o) => Object.assign({ nPast: 7, trained: 3, goal: 3, prot: 130, kcal: 1900, nEaten: 7, water: 7, sp: { bought: 0, est: 0, eaten: 0 } }, o || {}); }")
    tip = lambda o: pg.evaluate("(o) => reviewTip(__r(o))", o)
    ck("alles im Plan", tip({}).startswith("Alles im Plan"), tip({}))
    ck("zu wenig Training: Kurz-Einheit genannt", "Kurz-Einheit" in tip({"trained": 1}), tip({"trained": 1}))
    x = tip({"prot": 100})
    ck("zu wenig Eiweiß: Lücke und Quark-Menge", "28 g Eiweiß" in x and "230 g Magerquark" in x, x)
    ck("Training geht vor Eiweiß", "Kurz-Einheit" in tip({"trained": 0, "prot": 90}))
    ck("zu wenig eingetragen", "Abendessen" in tip({"nEaten": 3}), tip({"nEaten": 3}))
    ck("zu viele Kalorien: 400 über Ziel", "400 kcal" in tip({"kcal": 2300}), tip({"kcal": 2300}))
    ck("zu wenig Wasser", "nur an 2 Tagen" in tip({"water": 2}), tip({"water": 2}))
    x = tip({"sp": {"bought": 60, "est": 40, "eaten": 30}})
    ck("mehr eingekauft als geschätzt: Hinweis auf Reste verwerten", "Reste verwerten" in x and "60,00" in x, x)
    ck("Woche kaum begonnen: kein Tipp", tip({"nPast": 1}) == "")
    ck("ohne Eiweiß-Einträge kein Fehler", isinstance(tip({"prot": None, "kcal": None, "nEaten": 0}), str))
    h = pg.evaluate("() => reviewHTML(weekStartISO(shiftDay(todayISO(), -7)), false)")
    ck("Rückblick-Karte zeigt „Fürs nächste Mal“", "Fürs nächste Mal" in h and 'class="small review-tip"' in h)
    pg.evaluate("() => { showTab('fortschritt', true); }")
    pg.wait_for_timeout(300)
    ck("Fortschritt ohne Fehler", not errs, errs[:2])
    c.close(); b.close()
print("FAILS", fails)
