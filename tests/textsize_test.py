"""Zoom ohne WCAG-Verstoß: keine Zoom-Sperre im Viewport-Meta, dafür Textgröße bis 200 % ohne seitliches Überlaufen."""
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)
TABS = ["heute", "uebungen", "tipps", "ausblick", "rezepte", "rad", "vorkochen", "einkauf", "ernaehrung", "fortschritt"]
OVER = """() => { const W = innerWidth, bad = [];
  document.querySelectorAll('#panel-' + CUR + ' *, .gnav *, .tabs *, .top *').forEach(e => {
    if (e.closest('.rcard .tags')) return;   /* absichtlich einzeilig mit Ausblendung */
    const r = e.getBoundingClientRect(); if (r.width && (r.right > W + 1 || r.left < -1) && !e.closest('.tabs')) bad.push(e.tagName + '.' + e.className); });
  return { sw: document.documentElement.scrollWidth, bad: [...new Set(bad)].slice(0, 4) }; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True); pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(600)
    meta = pg.evaluate("document.querySelector('meta[name=viewport]').content")
    ck("Viewport ohne user-scalable=no und maximum-scale", "user-scalable" not in meta and "maximum-scale" not in meta, meta)
    ck("Pinch bleibt per touch-action gesperrt", pg.evaluate("getComputedStyle(document.documentElement).touchAction") == "pan-x pan-y")
    ck("Standard: normale Größe", pg.evaluate("document.documentElement.style.fontSize") == "" and pg.evaluate("settings.text") == 100)
    pg.evaluate("openSettings()"); pg.wait_for_timeout(300)
    pg.select_option("#s-text", "200"); pg.wait_for_timeout(200)
    ck("Einstellung wirkt sofort", pg.evaluate("getComputedStyle(document.documentElement).fontSize") == "32px")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    pg.reload(); pg.wait_for_timeout(700)
    ck("Einstellung bleibt nach Neuladen", pg.evaluate("getComputedStyle(document.documentElement).fontSize") == "32px")
    for t in TABS:
        pg.evaluate(f"showTab('{t}')"); pg.wait_for_timeout(200)
        r = pg.evaluate(OVER)
        ck("200 %: " + t + " ohne Überlauf", r["sw"] <= 390 and not r["bad"], str(r))
    for n, js in [("Einstellungen", "openSettings()"), ("Essen", "openEat()"), ("Rezept", "openRecipe(RECIPES[0].id)")]:
        pg.evaluate(js); pg.wait_for_timeout(400)
        ck("200 %: Dialog " + n + " ohne Überlauf", pg.evaluate("(()=>{const d=document.querySelector('dialog[open]'); return d.scrollWidth <= d.clientWidth + 1 && document.documentElement.scrollWidth <= 390})()"))
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    pg.evaluate("localStorage.setItem('fc_settings', JSON.stringify(Object.assign({}, settings, {text: 999})))"); pg.reload(); pg.wait_for_timeout(600)
    ck("Ungültiger Wert wird zu 100 %", pg.evaluate("settings.text") == 100 and pg.evaluate("document.documentElement.style.fontSize") == "")
    # iOS: Zoom-Sperre greift sofort (vor dem Hauptcode) über Gesten- und Touch-Ereignisse
    c2 = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    pz = c2.new_page(); pz.route("**/js/app.js*", lambda r: r.abort()); pz.goto(URL); pz.wait_for_timeout(500)
    ck("Sperre aktiv, auch wenn der Hauptcode noch nicht da ist", pz.evaluate("typeof renderToday") == "undefined")
    ck("gesturestart wird abgefangen", pz.evaluate("(() => { const e = new Event('gesturestart', { cancelable: true }); document.dispatchEvent(e); return e.defaultPrevented; })()"))
    ck("Pinch per touchmove (scale 2) wird abgefangen", pz.evaluate("(() => { const e = new Event('touchmove', { cancelable: true }); Object.defineProperty(e, 'scale', { value: 2 }); document.dispatchEvent(e); return e.defaultPrevented; })()"))
    ck("normales Scrollen (scale 1) bleibt frei", not pz.evaluate("(() => { const e = new Event('touchmove', { cancelable: true }); Object.defineProperty(e, 'scale', { value: 1 }); document.dispatchEvent(e); return e.defaultPrevented; })()"))
    c2.close()
    # Kein Eingabefeld unter 16 px (sonst zoomt iOS beim Antippen), auch in den Dialogen
    pg.evaluate("settings.text = 100; applyTextSize(); logEat(RECIPES[0], 1); MYD.unshift({id:'1',name:'Gericht',k:500,p:30,c:2,w:400,est:false,lg:250,text:'200 g Reis'}); mydSave()")
    Q = "() => Array.from(document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=range]), select, textarea')).filter(e => e.offsetParent !== null || e.closest('dialog[open]')).filter(e => parseFloat(getComputedStyle(e).fontSize) < 16).map(e => e.id || e.className || e.tagName)"
    small = []
    for t in TABS:
        pg.evaluate(f"showTab('{t}')"); pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)"); small += pg.evaluate(Q)
    for js in ["openEat()", "openSettings()", "openRecipe(RECIPES[0].id)", "openCook(RECIPES[0].id)"]:
        pg.evaluate(js); pg.wait_for_timeout(250); pg.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)"); small += pg.evaluate(Q)
        pg.evaluate("document.querySelectorAll('dialog[open]').forEach(d => d.close())")
    ck("alle Eingabefelder mindestens 16 px", not small, str(small[:5]))
    ck("keine Fehler", not errs, str(errs[:2]))
    b.close()
print("FAILS", fails)
