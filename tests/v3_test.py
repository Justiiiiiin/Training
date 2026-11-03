from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h,name in [(1300,900,"desk"),(390,844,"mob")]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=(w<500)); pg=c.new_page()
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.goto(URL); pg.wait_for_timeout(500)
        pg.evaluate("showTab('uebungen')"); pg.wait_for_timeout(300)
        n_info=pg.evaluate("document.querySelectorAll('[data-v3]').length"); print(name,"3D-Knoepfe",n_info)
        pg.click('button.infobtn[data-v3="push"]'); pg.wait_for_timeout(1200)
        print(" dialog offen",pg.evaluate("document.getElementById('dlg-3d').open"),"| titel",pg.inner_text("#v3-title"),"| aktive Stufe",pg.evaluate("document.querySelector('#v3-vars [aria-pressed=true]').textContent"))
        pg.screenshot(path=__import__("fcenv").SHOTS + f"/v3_{name}_push.png")
        # jede Stufe jeder Uebung/Extras per UI
        ids=pg.evaluate("[...new Set([...document.querySelectorAll('[data-v3]')].map(e=>e.dataset.v3))]"); print(" ids",ids)
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        bad=[]; total=0
        for gid in ids:
            cnt=pg.evaluate("(g)=>V3A[g].length",gid)
            for i in range(cnt):
                pg.evaluate("([g,i])=>openV3(g,i)",[gid,i]); pg.wait_for_timeout(250); total+=1
                s=pg.evaluate("""()=>{const cv=document.getElementById('v3-cv');const d=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;let n=0;const bg=[d[0],d[1],d[2]];for(let k=0;k<d.length;k+=4*37){if(Math.abs(d[k]-bg[0])+Math.abs(d[k+1]-bg[1])+Math.abs(d[k+2]-bg[2])>40)n++}return {n,phase:document.getElementById('v3-phase').textContent,w:cv.clientWidth,h:cv.clientHeight}}""")
                if s["n"]<30 or not s["phase"]: bad.append((gid,i,s))
                pg.keyboard.press("Escape"); pg.wait_for_timeout(120)
        print(" Stufen getestet",total,"auffaellig",bad[:5])
        # Steuerung
        pg.evaluate("openV3('squat',2)"); pg.wait_for_timeout(500)
        pg.click("#v3-play"); a=pg.evaluate("V3View.G.playing"); pg.click("#v3-speed"); pg.click("[data-v3view=front]"); pg.click("[data-v3view=top]"); pg.click("#v3-auto")
        pg.fill("#v3-scrub","500") if False else pg.evaluate("(()=>{const s=document.getElementById('v3-scrub');s.value=500;s.dispatchEvent(new Event('input'))})()")
        print(" pause",a,"speed",pg.inner_text("#v3-speed"),"yaw/pitch",pg.evaluate("[V3View.G.yaw,V3View.G.pitch]"))
        pg.screenshot(path=__import__("fcenv").SHOTS + f"/v3_{name}_top.png")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        # Training: Technik-Knopf
        pg.evaluate("showTab('heute')"); pg.evaluate("act('start')"); pg.evaluate("beginWork()"); pg.wait_for_timeout(300)
        print(" Technik-Knopf im Training:",pg.evaluate("!!document.querySelector('#actions [data-v3]')"))
        pg.evaluate("stopWorkout()")
        print(" overflow",pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth"))
        c.close()
    b.close()
print("ERRORS",errs[:6])
