from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":1360,"height":1000},color_scheme="light")
    pg=c.new_page(); pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate("CART=[{id:'quark-mit-erdbeeren',n:1},{id:'haehnchen-reis-pfanne',n:1},{id:'frikadellen-mit-tomaten-gurken-salat',n:1},{id:'ei-rucola-brot-mit-senf',n:1}]; renderShop()")
    pg.evaluate("showTab('einkauf')"); pg.wait_for_timeout(400)
    print("Reste-Hinweise:"); [print(" -",t.replace("\n"," ")) for t in pg.locator('.srest').all_inner_texts()]
    pg.evaluate("document.querySelector('.slist').scrollIntoView()"); pg.screenshot(path=__import__("fcenv").SHOTS + "/v10-liste.png")
    pg.evaluate("document.querySelector('.stg').scrollIntoView({block:'center'})"); pg.screenshot(path=__import__("fcenv").SHOTS + "/v10-store.png")
    # Rezept mit Erdbeeren
    pg.evaluate("showTab('rezepte')"); pg.fill('#rsearch','Erdbeer'); pg.dispatch_event('#rsearch','input'); pg.wait_for_timeout(300)
    pg.click('.rcard >> nth=0'); pg.wait_for_timeout(500); print("Erdbeer-Hinweis im Dialog:", pg.locator('#dlg-recipe .note:has-text("Tiefkühl-Erdbeeren")').count())
    pg.evaluate("closeDialog(document.querySelector('#dlg-recipe'))"); pg.wait_for_timeout(300)
    pg.evaluate("showTab('ernaehrung')"); pg.wait_for_timeout(300)
    print("Oats-Sicherheit:", pg.locator('text=Deine gefrorenen Erdbeeren').count(), "| Sicher essen:", pg.locator('text=Tiefkühl-Beeren vor dem Essen').count())
    c.close(); b.close()
print("errors:",errs)
