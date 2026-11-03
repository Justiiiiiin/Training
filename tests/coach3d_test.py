from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h,n in [(390,844,"mob"),(1300,900,"desk")]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=w<500); pg=c.new_page()
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.goto(URL); pg.wait_for_timeout(500)
        print(n,"vor Start: Figur sichtbar",pg.is_visible("#coachfig"))
        pg.evaluate("showTab('uebungen')"); pg.evaluate("startWorkout(); beginWork()"); pg.wait_for_timeout(1400)
        print(" im Training: sichtbar",pg.is_visible("#coachfig"),"| Anim",pg.evaluate("V3Mini.G.id+':'+V3Mini.G.idx"),"| laeuft",pg.evaluate("!!V3Mini.G.raf"))
        pg.evaluate("window.scrollTo(0,0)"); pg.screenshot(path=__import__("fcenv").SHOTS + f"/coach3d_{n}.png")
        pg.evaluate("act('done')"); pg.wait_for_timeout(400)
        print(" Pause -> naechste Uebung:",pg.evaluate("V3Mini.G.id+':'+V3Mini.G.idx"))
        pg.evaluate("stopWorkout()"); pg.wait_for_timeout(300)
        print(" nach Stopp: sichtbar",pg.is_visible("#coachfig"),"laeuft",pg.evaluate("!!V3Mini.G.raf"))
        c.close()
    b.close()
print("ERRORS",errs)
