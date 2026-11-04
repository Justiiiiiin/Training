"""Layout-Runde (v3.44): Kreis in Kreis auf Heute, Schicht-Pillen, schlanke Rezept-Filter,
vier Essen-Tabs, Richtwerte bei Fortschritt, 2 x 2 Werte, Aktions-Kacheln, Einkauf leer, Zahnrad oben."""
import sys
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
fails, errs = [], []


def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c:
        fails.append(n)


def ready(pg):
    for _ in range(80):
        if pg.evaluate("window.__fcReady===true"):
            return
        pg.wait_for_timeout(150)


def box(pg, sel):
    return pg.evaluate("s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}}", sel)


def noscroll(pg):
    return pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth+1")


with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    pg = c.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(URL)
    ready(pg)

    # 1 Titel der Trainingskarte
    ck("L1 Titel Ganzkoerper-Training", pg.evaluate("document.getElementById('title').textContent") == "Ganzkörper-Training", pg.evaluate("document.getElementById('title').textContent"))

    # 2 Ein Kreis: außen Eiweiß, innen Kalorien, in der Mitte die Trainingspunkte
    pg.evaluate("showTab('heute')"); pg.wait_for_timeout(300)
    n = pg.evaluate("trainDays()")
    ck("L2 genau ein Kreis (svg)", pg.evaluate("document.querySelectorAll('.rings svg.rg').length") == 1)
    ck("L2 zwei Ringe mit Spur und Balken", pg.evaluate("document.querySelectorAll('.rings .rg circle').length") == 4)
    ck("L2 Punkte = Trainingstage", pg.evaluate("document.querySelectorAll('.rings .tdots .td').length") == n, n)
    ck("L2 innerer Ring dünner als äußerer", pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.rg .o')).strokeWidth)") > pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.rg .i')).strokeWidth)"))
    ck("L2 Punkte liegen im inneren Ring", pg.evaluate("""()=>{const d=document.querySelector('.tdots').getBoundingClientRect(),s=document.querySelector('.rg').getBoundingClientRect();
        const cx=s.x+s.width/2, cy=s.y+s.height/2, R=s.width*0.3175; const pts=[[d.left,d.top],[d.right,d.top],[d.left,d.bottom],[d.right,d.bottom]];
        return pts.every(q=>Math.hypot(q[0]-cx,q[1]-cy)<=R+1)}"""))
    txt = pg.inner_text(".rings").replace("\n", " ")
    ck("L2 Zahlen daneben", "Eiweiß" in txt and "Kalorien" in txt and "Training" in txt and "von" in txt, txt)
    ck("L2 .rings sichtbar, nicht breiter als Bildschirm", noscroll(pg) and box(pg, ".rings")["w"] <= 390)
    # Werte ändern: Eiweiß und Kalorien füllen den Ring, Trainings füllen die Punkte
    pg.evaluate("sessions.push(todayISO()); dayEns().items.push({t:'Test',p:40,k:600,c:2,m:'x'}); saveToday(); renderToday()")
    pg.wait_for_timeout(200)
    ck("L2 ein Training = ein gefüllter Punkt", pg.evaluate("document.querySelectorAll('.tdots .td.on').length") == pg.evaluate("Math.min(weekCountISO(weekStartISO(todayISO())),trainDays())"))
    off = pg.evaluate("[...document.querySelectorAll('.rgb')].map(e=>parseFloat(e.style.strokeDashoffset)/parseFloat(e.style.strokeDasharray))")
    ck("L2 Ringe teilweise gefüllt", all(0 < o < 1 for o in off), off)
    pg.evaluate("dayEns().items.push({t:'Viel',p:10,k:2000,c:2,m:'x'}); saveToday(); renderToday()"); pg.wait_for_timeout(150)
    ck("L2 über dem Kalorienziel: Hinweis als Text", "über dem Ziel" in pg.inner_text(".rleg"), pg.inner_text(".rleg").replace("\n", " "))
    ck("L2 Kalorienring warnt", "warn" in pg.evaluate("document.querySelector('.rg .rgb.i').style.stroke"))
    pg.evaluate("sessions.pop(); dayEns().items.length=0; saveToday(); renderToday()")

    # 3 Schicht-Hinweis als Pillen
    ck("L3 zwei Pillen", pg.evaluate("document.querySelectorAll('.shifthint .tag').length") == 2)
    t3 = pg.inner_text(".shifthint").replace("\n", " ")
    ck("L3 Text kurz und enthält Heute", "Heute" in t3 and len(t3) < 90, t3)

    # 4 Rezepte: Sortierung in der Filterkarte, eine schmale Zeile für die Zahl
    pg.evaluate("showTab('rezepte')"); pg.wait_for_timeout(300)
    ck("L4 Sortierung liegt in der Filterkarte", pg.evaluate("!!document.querySelector('#filters #rsort')"))
    ck("L4 kein zweiter Balken mehr", pg.evaluate("document.querySelector('.fbar')===null"))
    first = box(pg, ".rcard")
    ck("L4 erstes Rezept beginnt über 470 px", first is not None and first["y"] < 470, first)
    sb = box(pg, "#rsort"); mb = pg.evaluate("(()=>{const r=document.querySelector('#fmore > summary').getBoundingClientRect();return {y:r.y,h:r.height}})()")
    ck("L4 Weitere Filter und Sortierung in einer Zeile", abs((sb["y"] + sb["h"] / 2) - (mb["y"] + mb["h"] / 2)) < 12, [sb, mb])
    pg.select_option("#rsort", "time"); pg.wait_for_timeout(250)
    tm = pg.evaluate("[...document.querySelectorAll('.rcard .rsub')].slice(0,6).map(e=>parseInt(e.textContent.split(',')[1]))")
    ck("L4 Sortierung nach Zeit wirkt", tm == sorted(tm), tm)
    ck("L4 Auswahl bleibt nach dem Neuzeichnen", pg.evaluate("document.getElementById('rsort').value") == "time" and pg.evaluate("document.activeElement.id") == "rsort")
    ck("L4 Treffer-Zeile", "von" in pg.inner_text("#rcount"), pg.inner_text("#rcount"))
    pg.select_option("#rsort", "protein")

    # 5 Tabs
    sub = lambda: pg.evaluate("[...document.querySelectorAll('#subnav .tab')].map(x=>x.textContent).join()")
    ck("L5 Essen: vier Tabs", sub() == "Rezepte,Glücksrad,Vorkochen,Einkauf", sub())
    ws = pg.evaluate("[...document.querySelectorAll('#subnav .tab')].map(x=>Math.round(x.getBoundingClientRect().width))")
    ck("L5 vier gleich breite Tabs", max(ws) - min(ws) <= 2, ws)
    pg.evaluate("showTab('ernaehrung')"); pg.wait_for_timeout(300)
    ck("L5 Richtwerte gehört zu Fortschritt", pg.inner_text('.gbtn[aria-selected="true"]').strip() == "Fortschritt" and sub() == "Verlauf,Richtwerte", sub())
    ck("L5 Richtwerte sichtbar", pg.is_visible("#panel-ernaehrung") and "Richtwerte für dich" in pg.inner_text("#panel-ernaehrung"))
    pg.click('#subnav .tab[data-tab="fortschritt"]'); pg.wait_for_timeout(300)
    ck("L5 Verlauf per Tab erreichbar", pg.is_visible("#panel-fortschritt"))
    pg.click('.gbtn[data-group="essen"]'); pg.wait_for_timeout(300)
    ck("L5 Gruppe Essen zeigt wieder Essen", sub().startswith("Rezepte"), sub())

    # 6 Richtwerte: 2 x 2
    pg.evaluate("showTab('ernaehrung')"); pg.wait_for_timeout(300)
    st = pg.evaluate("[...document.querySelectorAll('#calc .stat')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y)]})")
    ck("L6 vier Werte in zwei Spalten", len(st) == 4 and st[0][1] == st[1][1] and st[2][1] == st[3][1] and st[0][0] < st[1][0] and st[2][1] > st[0][1], st)

    # 7 Fortschritt ohne Verlauf: Kacheln sind Aktionen
    pg.evaluate("log.length=0; showTab('fortschritt')"); pg.wait_for_timeout(300)
    ck("L7 zwei Aktions-Kacheln", pg.evaluate("document.querySelectorAll('#stats .statact').length") == 2, pg.inner_text("#stats").replace("\n", " "))
    ck("L7 kein Strich als Wert", "–" not in pg.inner_text("#stats"))
    pg.click('#stats .statact[data-focusf="f-weight"]'); pg.wait_for_timeout(500)
    ck("L7 Tipp springt ins Gewichtsfeld", pg.evaluate("document.activeElement.id") == "f-weight")
    pg.evaluate("log.push({date:'2026-10-01',weight:82}); renderProgress()"); pg.wait_for_timeout(100)
    ck("L7 ein Wert: Hinweis auf zweite Messung", "Noch ein Gewicht" in pg.inner_text("#stats"), pg.inner_text("#stats").replace("\n", " "))
    pg.evaluate("log.push({date:'2026-10-20',weight:80.5}); renderProgress()"); pg.wait_for_timeout(100)
    ck("L7 zwei Werte: Änderung steht da", "−1,5" in pg.inner_text("#stats") or "-1,5" in pg.inner_text("#stats"), pg.inner_text("#stats").replace("\n", " "))
    pg.evaluate("log.length=0")

    # 8 Einkauf leer
    pg.evaluate("showTab('einkauf')"); pg.wait_for_timeout(300)
    ck("L8 ein Hauptknopf", pg.evaluate("document.querySelectorAll('.empty-in .btn.primary').length") == 1)
    ck("L8 zwei Textlinks", pg.evaluate("document.querySelectorAll('.empty-in .linkbtn').length") == 2)
    lb = pg.evaluate("[...document.querySelectorAll('.empty-in .linkbtn')].map(e=>{const r=e.getBoundingClientRect();return Math.round(r.height)})")
    ck("L8 Links mit Tippfläche ab 24 px", all(h >= 24 for h in lb), lb)
    pg.click('.empty-in .linkbtn[data-tab="rad"]'); pg.wait_for_timeout(300)
    ck("L8 Link führt zum Glücksrad", pg.is_visible("#panel-rad"))

    # 9 Zahnrad oben, Version daneben, vier gleiche Spalten unten
    pg.evaluate("showTab('heute')"); pg.wait_for_timeout(300)
    ck("L9 kein schwebender Einstellungsknopf mehr", pg.evaluate("document.querySelector('.setfab')===null && document.getElementById('b-settings2')===null"))
    g = box(pg, "#b-settings"); v = box(pg, "#appver")
    ck("L9 Zahnrad oben rechts sichtbar", g is not None and g["w"] >= 44 and g["y"] < 60 and g["x"] + g["w"] > 340, g)
    ck("L9 Version links vom Zahnrad", v["x"] + v["w"] <= g["x"] + 2 and v["x"] > 150, [v, g])
    ck("L9 Version und Zahnrad auf einer Höhe", abs((v["y"] + v["h"] / 2) - (g["y"] + g["h"] / 2)) <= 6, [v, g])
    gw = pg.evaluate("[...document.querySelectorAll('#gnav .gbtn')].map(e=>Math.round(e.getBoundingClientRect().width))")
    ck("L9 vier gleich breite Leistenknöpfe", len(gw) == 4 and max(gw) - min(gw) <= 1, gw)
    pg.click("#b-settings"); pg.wait_for_timeout(400)
    ck("L9 Zahnrad öffnet die Einstellungen", pg.evaluate("document.getElementById('dlg-settings').open"))
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)

    # Überlauf auf 320 px und bei großer Schrift
    c2 = b.new_context(viewport={"width": 320, "height": 640}, has_touch=True, is_mobile=True)
    p2 = c2.new_page(); p2.on("pageerror", lambda e: errs.append(str(e)))
    p2.goto(URL); ready(p2)
    for tab in ["heute", "rezepte", "rad", "einkauf", "ernaehrung", "fortschritt"]:
        p2.evaluate("t=>showTab(t)", tab); p2.wait_for_timeout(250)
        ck("kein seitlicher Überlauf bei 320 px: " + tab, noscroll(p2))
    p2.evaluate("showTab('heute')"); p2.wait_for_timeout(250)
    gv, vv = box(p2, "#b-settings"), box(p2, "#appver")
    bb = box(p2, ".brand h1")
    ck("320 px: Version überdeckt den Namen nicht", vv["x"] >= bb["x"] + bb["w"] - 1 and vv["x"] + vv["w"] <= gv["x"] + 2, [bb, vv, gv])
    p2.evaluate("document.documentElement.setAttribute('data-big','')"); p2.wait_for_timeout(250)
    for tab in ["heute", "rezepte", "ernaehrung", "fortschritt"]:
        p2.evaluate("t=>showTab(t)", tab); p2.wait_for_timeout(250)
        ck("große Schrift, kein Überlauf: " + tab, noscroll(p2))
    c2.close()

    ck("keine Fehler", not errs, errs)
    b.close()
print("FAILS", fails)
sys.exit(1 if fails else 0)
