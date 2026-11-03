from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(500)
    pg.evaluate("showTab('rezepte')"); pg.wait_for_timeout(300)
    n0=pg.evaluate("filtered().length"); print("Rezepte:",n0,pg.evaluate("RECIPES.length"))
    pg.evaluate("document.getElementById('fmore').open=true; document.getElementById('ingex')&&(document.getElementById('ingex').open=true)")
    print("Zutaten-Chips:",pg.evaluate("document.querySelectorAll('[data-excz]').length"))
    pg.click('[data-excz="mandel"]'); pg.wait_for_timeout(200)
    n1=pg.evaluate("filtered().length"); print("ohne Mandeln:",n1,"| Mandel-Rezepte uebrig:",pg.evaluate("filtered().filter(r=>r.ing.some(i=>i[4]==='mandel')).length"),"|",pg.inner_text("#rcount"))
    pg.click('[data-excz="honig"]'); pg.click('[data-excz="banane"]'); pg.wait_for_timeout(200); print("ohne Honig+Banane:",pg.evaluate("filtered().length"),"|",pg.inner_text("#rcount"))
    pg.click('[data-excz="mandel"]'); pg.click('[data-excz="honig"]'); pg.click('[data-excz="banane"]'); pg.wait_for_timeout(200); print("zurueck:",pg.evaluate("filtered().length")==n0)
    # Rad und Plan beachten Ausschluss
    r=pg.evaluate("""()=>{toggleExc('z:ei'); let bad=0; for(let i=0;i<50;i++){ const ids=makeDayPlan(false); if(ids.some(id=>byId(id).ing.some(x=>x[4]==='ei'))) bad++; } const pool=radPool('Mittag/Abend',false).filter(r=>r.ing.some(x=>x[4]==='ei')).length; toggleExc('z:ei'); return {bad,pool}}""")
    print("Plan/Rad ohne Ei:",r)
    # Dialog: Favorit, Ausblenden, Kochmodus
    pg.evaluate("openRecipe(RECIPES.find(r=>r.title.includes('Hähnchen-Fajita')).id)"); pg.wait_for_timeout(500)
    pg.click('[data-fav]'); pg.wait_for_timeout(200)
    print("Fav:",pg.evaluate("FAV"),"pressed",pg.get_attribute('[data-fav]','aria-pressed'))
    pg.click('[data-cook]'); pg.wait_for_timeout(700)
    print("Kochmodus offen:",pg.evaluate("document.getElementById('dlg-cook').open"),"|",pg.inner_text("#dlg-cook .kicker"))
    pg.click('[data-ckgo="1"]'); pg.wait_for_timeout(150); print("Schritt:",pg.inner_text("#dlg-cook .kicker"),"|",pg.inner_text("#dlg-cook .cktext")[:60])
    has=pg.evaluate("!!document.querySelector('[data-cktimer]')"); print("Timer-Knopf:",has)
    pg.evaluate("ckGo(1)"); pg.wait_for_timeout(150); print("Weiter:",pg.inner_text("#dlg-cook .kicker"))
    for i in range(6): pg.evaluate("ckGo(1)")
    print("Ende:",pg.inner_text("#dlg-cook .kicker"))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/cook_end.png")
    pg.evaluate("CK.i=2; ckDraw(); ckTimer(1)"); pg.wait_for_timeout(1500); print("Timer:",pg.inner_text("#cktimer"))
    pg.click('[data-ckclose]'); pg.wait_for_timeout(400); print("geschlossen:",not pg.evaluate("document.getElementById('dlg-cook').open"),"| Timer weg:",pg.evaluate("CK.timer===0"))
    # Nicht mehr vorschlagen
    pg.evaluate("openRecipe(RECIPES[5].id)"); pg.wait_for_timeout(500); pg.click('[data-hide]'); pg.wait_for_timeout(500)
    print("ausgeblendet:",pg.evaluate("EXC.filter(x=>x.startsWith('r:'))"),"| im Filter sichtbar:",pg.evaluate("filtered().some(r=>r.id===RECIPES[5].id)"),"|",pg.inner_text("#rcount"))
    # Fav-Filter
    pg.evaluate("F.fav=true; renderRecipes()"); print("Nur Favoriten:",pg.evaluate("filtered().length"))
    pg.evaluate("F.fav=false; renderRecipes()")
    # Sync-Schluessel
    print("fc_fav in KEYS:",pg.evaluate("FC.KEYS.includes('fc_fav')"),"| Export:",pg.evaluate("'fc_fav' in JSON.parse(FC.exportAll()).data"))
    print("overflow",pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth"))
    print("ERRORS",errs[:5]); b.close()
