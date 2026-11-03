from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500); pg.evaluate("openEat()"); pg.wait_for_timeout(400)
    ck("Namensfeld getrennt von Zutaten", pg.evaluate("!!document.getElementById('calc-name0') && !!document.getElementById('calc-in')"))
    pg.fill("#calc-name0","Spaghetti Bolognese"); pg.fill("#calc-in","100 g Nudeln, 200 g Hackfleisch, 400 g stückige Tomaten, 1 Zwiebel, 1 EL Tomatenmark"); pg.click("[data-calcgo]"); pg.wait_for_timeout(300)
    tot=pg.inner_text(".calctot"); print(tot[:90])
    ck("Name uebernommen", pg.evaluate("CALC.name")=="Spaghetti Bolognese")
    pg.click(".mydsave summary"); pg.fill("#myd-w","700"); pg.click("[data-mydsave]"); pg.wait_for_timeout(300)
    ck("gespeichert", pg.evaluate("MYD.length")==1 and pg.evaluate("MYD[0].w")==700, pg.evaluate("JSON.stringify(MYD[0]).slice(0,120)"))
    ck("Liste sichtbar", "Spaghetti Bolognese" in pg.inner_text("#dlg-eat") and "pro 100 g" in pg.inner_text("#dlg-eat"))
    pg.fill('.myd-g[data-i="0"]',"250"); pg.wait_for_timeout(100)
    prev=pg.inner_text("#mydv0"); print(prev)
    k=pg.evaluate("MYD[0].k"); ck("Vorschau passt", str(round(k*250/700)) in prev.replace(".",""), prev)
    pg.click('[data-mydeat="0"]'); pg.wait_for_timeout(300)
    ck("Tagebuch", pg.evaluate("dayGet().items.some(x=>x.t==='Spaghetti Bolognese (250 g)')"), pg.evaluate("JSON.stringify(dayGet().items.slice(-1))"))
    # Eingabe ueber Rechner
    pg.fill("#calc-name0",""); pg.fill("#calc-in","300 g Spaghetti Bolognese"); pg.click("[data-calcgo]"); pg.wait_for_timeout(300)
    ck("Rechner erkennt gespeichertes Gericht", pg.evaluate("CALC.rows[0].kind")=="dish" and abs(pg.evaluate("CALC.rows[0].k")-k*300/700)<2, pg.evaluate("JSON.stringify(CALC.rows[0])"))
    # Schaetzung ohne Gewicht
    pg.fill("#calc-name0","Reispfanne"); pg.fill("#calc-in","100 g Reis, 200 g Hähnchen, 1 Paprika"); pg.click("[data-calcgo]"); pg.wait_for_timeout(300)
    pg.click(".mydsave summary"); pg.click("[data-mydsave]"); pg.wait_for_timeout(300)
    ck("geschaetzt gespeichert", pg.evaluate("MYD[0].est")==True and pg.evaluate("MYD[0].w")>200, pg.evaluate("MYD[0].w"))
    pg.reload(); pg.wait_for_timeout(500)
    ck("persistiert", pg.evaluate("MYD.length")==2)
    pg.evaluate("openEat()"); pg.wait_for_timeout(300)
    pg.click('[data-mydel="0"]'); pg.wait_for_timeout(300)
    ck("geloescht", pg.evaluate("MYD.length")==1)
    pg.evaluate("localStorage.setItem('fc_dishes', JSON.stringify([{name:5},{name:'x',k:'a',p:1,w:100},{name:'ok',k:100,p:5,w:200,c:1}]))"); pg.reload(); pg.wait_for_timeout(500)
    ck("kaputte Daten bereinigt", pg.evaluate("MYD.length")==1 and pg.evaluate("MYD[0].name")=="ok")
    ck("fc_dishes in KEYS", pg.evaluate("FC.KEYS ? FC.KEYS.includes('fc_dishes') : true"))
    pg.evaluate("openEat()"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/myd.png")
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"))
    ck("keine Fehler", not errs, str(errs[:3])); print("FAILS",fails); b.close()
