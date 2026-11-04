from playwright.sync_api import sync_playwright
import json
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
base=json.load(open(__import__("fcenv").RECIPES_JSON,encoding="utf-8")); B={r["id"]:r for r in base}
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(700)
    cur=pg.evaluate("RECIPES.map(r=>[r.id,r.cost,r.tags])")
    bad=[(i,c0,B[i]["cost"]) for i,c0,t in cur if abs(c0-B[i]["cost"])>0.011]
    ck("Ohne eigene Preise: Kosten wie im Bauplan (1000)", not bad and len(cur)==1000, bad[:3])
    badt=[i for i,c0,t in cur if ("Günstig" in t)!=("Günstig" in B[i]["tags"])]
    ck("Guenstig-Markierung wie im Bauplan", not badt, badt[:3])
    pg.evaluate("showTab('einkauf')"); pg.wait_for_timeout(300)
    ck("Karte Meine Preise da", pg.evaluate("!!document.getElementById('pricebox')"))
    pg.evaluate("document.getElementById('pricebox').open=true"); pg.wait_for_timeout(100)
    n=pg.evaluate("document.querySelectorAll('[data-price]').length"); ck("Ein Feld je Zutat", n==pg.evaluate("Object.keys(PRICE).length"), n)
    r0=pg.evaluate("RECIPES.find(r=>r.id==='haehnchen-reis-pfanne').cost"); old=pg.evaluate("PRICE.haehn.price")
    pg.fill('[data-price="haehn"]', "10,98"); pg.dispatch_event('[data-price="haehn"]','change'); pg.wait_for_timeout(300)
    r1=pg.evaluate("RECIPES.find(r=>r.id==='haehnchen-reis-pfanne').cost")
    ck("Preis Hähnchen verdoppelt: Rezept teurer", r1>r0+0.5, f"{r0} -> {r1}")
    ck("Gespeichert in Einstellungen", pg.evaluate("settings.prices.haehn")==10.98)
    ck("Karte bleibt offen und markiert", pg.evaluate("document.getElementById('pricebox').open") and pg.evaluate("document.querySelectorAll('.prow.mod').length")==1)
    ck("Zaehler in Ueberschrift", "1 angepasst" in pg.inner_text("#pricebox summary"))
    pg.reload(); pg.wait_for_timeout(700)
    ck("Nach Reload noch da", pg.evaluate("PRICE.haehn.price")==10.98 and pg.evaluate("RECIPES.find(r=>r.id==='haehnchen-reis-pfanne').cost")==r1)
    pg.evaluate("showTab('einkauf')")
    # zurueck auf Richtwert eintippen loescht Override
    pg.evaluate("document.getElementById('pricebox').open=true; PRICEOPEN=true")
    pg.fill('[data-price="haehn"]', "5,49"); pg.dispatch_event('[data-price="haehn"]','change'); pg.wait_for_timeout(250)
    ck("Richtwert eingetippt: Override weg", pg.evaluate("settings.prices.haehn")==None and pg.evaluate("RECIPES.find(r=>r.id==='haehnchen-reis-pfanne').cost")==r0)
    # Unsinn
    for val in ["abc","-3","0","1000","", "0,01"]:
        pg.fill('[data-price="reis"]', val); pg.dispatch_event('[data-price="reis"]','change'); pg.wait_for_timeout(120)
    ck("Unsinn wird nie gespeichert (ausser leer=Reset)", pg.evaluate("settings.prices.reis")==None, pg.evaluate("settings.prices.reis"))
    pg.fill('[data-price="reis"]', "3"); pg.dispatch_event('[data-price="reis"]','change'); pg.wait_for_timeout(200)
    ck("Reis 3 EUR gespeichert", pg.evaluate("settings.prices.reis")==3)
    # Guenstig-Tag folgt dem Preis
    g0=pg.evaluate("RECIPES.filter(r=>r.tags.includes('Günstig')).length")
    pg.evaluate("settings.prices.haehn=30; applyPrices()"); g1=pg.evaluate("RECIPES.filter(r=>r.tags.includes('Günstig')).length")
    ck("Teure Zutat: weniger Guenstig-Rezepte", g1<g0, f"{g0}->{g1}")
    # Einkaufsliste rechnet mit
    pg.evaluate("CART.length=0; CART.push({id:'haehnchen-reis-pfanne',n:2}); renderShop()"); t1=pg.evaluate("shopCalc(CART).total")
    pg.evaluate("settings.prices.haehn=5.49; applyPrices(); renderShop()"); t0=pg.evaluate("shopCalc(CART).total")
    ck("Einkaufssumme folgt dem Preis", t1>t0+5, f"{t0} -> {t1}")
    # Zuruecksetzen
    pg.evaluate("document.getElementById('pricebox').open=true"); pg.click('[data-pricereset]'); pg.wait_for_timeout(250)
    ck("Alle zuruecksetzen", pg.evaluate("Object.keys(settings.prices).length")==0 and pg.evaluate("PRICE.reis.price")==pg.evaluate("PRICE0.reis"))
    # kaputte Speicherdaten
    pg.evaluate("store.set('fc_settings',Object.assign({},settings,{prices:{haehn:'x',reis:-1,gibtsnicht:5,ei:1.5,wrap:null}}))"); pg.reload(); pg.wait_for_timeout(700)
    ck("Kaputte Preise bereinigt (nur ei bleibt)", pg.evaluate("Object.keys(settings.prices)")==["ei"], pg.evaluate("Object.keys(settings.prices)"))
    pg.evaluate("store.set('fc_settings',Object.assign({},settings,{prices:'kaputt'}))"); pg.reload(); pg.wait_for_timeout(700)
    ck("prices als Text: App startet", pg.evaluate("typeof settings.prices")=="object" and pg.evaluate("RECIPES.length")==1000)
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth"))
    pg.evaluate("showTab('einkauf'); document.getElementById('pricebox').open=true; document.getElementById('pricebox').scrollIntoView()"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/v316_prices.png")
    print("Fehler:",errs); ck("keine Fehler", not errs)
    b.close()
print("FAILS",fails)
