from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    c=b.new_context(viewport={"width":1360,"height":900},color_scheme="light")
    pg=c.new_page(); pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    print("recipes",pg.evaluate("RECIPES.length"),"gyros",pg.evaluate("RECIPES.filter(r=>/gyros/i.test(r.title+JSON.stringify(r.ing)+JSON.stringify(r.steps))).length"),
          "spinat",pg.evaluate("RECIPES.filter(hasSpin).length"))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-uebungen.png")
    pg.evaluate("showTab('rezepte')"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-rezepte.png")
    pg.evaluate("showTab('rad')"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-rad-idle.png")
    # Feasibility of plans
    res=pg.evaluate("""()=>{const out={};
      for (const bf of [true,false]){ let ok=0,n=200,pr=[],kc=[]; for(let i=0;i<n;i++){const specs=slotSpecs(bf,false);const recs=planDay(specs,null,new Set());const sc=dayScore(recs); if(sc===0) ok++; pr.push(recs.reduce((a,r)=>a+r.protein,0)); kc.push(recs.reduce((a,r)=>a+r.kcal,0));}
        out[bf?'mitFr':'ohneFr']={ok,n,minP:Math.min(...pr),avgP:pr.reduce((a,b)=>a+b)/n,minK:Math.min(...kc),maxK:Math.max(...kc)}}
      return out}""")
    print(res)
    # Skip-Modus: Woche drehen
    pg.click('[data-rmode="week"]'); pg.click('#spin'); pg.wait_for_timeout(500); pg.click('#skipspin'); pg.wait_for_timeout(1500)
    print("busy",pg.evaluate("rad.busy"), pg.inner_text('#radstatus'))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-rad-week.png",full_page=True)
    pg.click('[data-rmode="day"]'); pg.click('#spin'); pg.wait_for_timeout(700); pg.click('#skipspin'); pg.wait_for_timeout(800)
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-rad-day.png")
    print("day titles", pg.evaluate("RPL.day.days[0].slots.map(s=>byId(s.id).title)"))
    # Mahlzeit
    pg.click('[data-rmode="meal"]'); pg.click('#spin'); pg.wait_for_timeout(5200)
    print("meal:", pg.inner_text('#radstatus'), "busy",pg.evaluate("rad.busy"))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-rad-meal.png")
    # Sperren und neu drehen
    pg.click('[data-rlock="0:0"]'); pg.click('#spin'); pg.wait_for_timeout(300)
    print("locked kept", pg.evaluate("RPL.meal.days[0].slots[0].locked"))
    pg.wait_for_timeout(4500)
    pg.evaluate("rad.skip=true"); pg.wait_for_timeout(1200)
    # reload keeps plan
    pg.reload(); pg.wait_for_timeout(600); pg.evaluate("showTab('rad')"); pg.wait_for_timeout(300)
    print("persisted rows", pg.locator('.rslot').count())
    pg.evaluate("document.querySelector('#spin').click()"); pg.wait_for_timeout(300)
    # Rezept öffnen aus Rad
    pg.evaluate("rad.skip=true"); pg.wait_for_timeout(2500)
    pg.click('.rtitle >> nth=0'); pg.wait_for_timeout(500); print("dialog", pg.evaluate("document.querySelector('#dlg-recipe').open")); pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-dialog.png")
    c.close()
    # dark + mobile
    c=b.new_context(viewport={"width":390,"height":844},color_scheme="dark",device_scale_factor=2)
    pg=c.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(600); pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-m-top.png")
    pg.evaluate("showTab('rezepte')"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-m-rezepte.png")
    pg.evaluate("showTab('rad')"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/v6-m-rad.png")
    ov=pg.evaluate("document.documentElement.scrollWidth>innerWidth"); print("overflow mobile",ov)
    c.close(); b.close()
print("errors:",errs)
