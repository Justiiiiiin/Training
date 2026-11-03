from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":1360,"height":1000},color_scheme="light")
    pg=c.new_page(); pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.add_init_script("""window.__spoken=[]; window.SpeechSynthesisUtterance=function(t){this.text=t;window.__spoken.push(t)}; try{speechSynthesis.speak=function(u){setTimeout(()=>{u.onend&&u.onend()},10)}; speechSynthesis.cancel=function(){}}catch(e){}""")
    pg.goto(URL); pg.wait_for_timeout(700)
    print("aktiver Tab:", pg.inner_text('.gbtn[aria-selected="true"]'), "| heute sichtbar:", pg.is_visible('#panel-heute'))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v11-heute-leer.png")
    # Essen eintragen per Vorschlag
    pg.click('[data-plan="0"]'); pg.wait_for_timeout(200)
    pg.click('[data-eatopen]'); pg.wait_for_timeout(500)
    pg.fill('#eatq','Wrap'); pg.dispatch_event('#eatq','input'); pg.wait_for_timeout(200)
    pg.click('#dlg-eat [data-eat] >> nth=0'); pg.wait_for_timeout(200)
    pg.fill('#e-name','Eigene Oats'); pg.fill('#e-k','700'); pg.fill('#e-p','35'); pg.click('#eatform button[type=submit]'); pg.wait_for_timeout(300)
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v11-eatdialog.png")
    pg.evaluate("closeDialog(document.querySelector('#dlg-eat'))"); pg.wait_for_timeout(400)
    print("Heute gesamt:", pg.evaluate("JSON.stringify(dsum())"), "Einträge:", pg.evaluate("dayGet().items.length"))
    # Wasser
    pg.click('.gl >> nth=2'); pg.wait_for_timeout(100); print("Wasser:", pg.evaluate("dayGet().water"))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v11-heute.png", full_page=True)
    # Training mit Wiederholungen (Chips + Zahlwort)
    pg.evaluate("window.__spoken.length=0")
    pg.evaluate("act('start')"); pg.wait_for_timeout(100); pg.evaluate("act('next')"); pg.wait_for_timeout(300)
    for i in range(80):
        ph=pg.evaluate("W.phase"); ex=pg.evaluate("EX[W.ex].type||'reps'")
        if ph=="work" and ex!="hold":
            lo,hi=pg.evaluate("repRange(EX[W.ex])"); pg.click('[data-reps="%d"]'%hi)
        elif ph=="work": pg.evaluate("act('done')")
        elif ph=="hold": pg.evaluate("act('done')")
        elif ph in ("rest","prep"): pg.evaluate("act('next')")
        pg.wait_for_timeout(250)
        if pg.evaluate("W.phase")=="done": break
    pg.wait_for_timeout(600)
    print("Phase:", pg.evaluate("W.phase"), "| Sätze geloggt:", pg.evaluate("WK.length && WK[WK.length-1].sets.length"), "| Summary offen:", pg.evaluate("document.querySelector('#dlg-sum').open"))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v11-summary.png")
    print("Sätze:", pg.evaluate("JSON.stringify(WK[WK.length-1].sets.slice(0,6))"))
    print("Gesprochen:", pg.evaluate("JSON.stringify(__spoken.slice(0,8))"))
    # Stufe hoch
    if pg.locator('[data-lvlup]').count(): 
        before=pg.evaluate("JSON.stringify(levels)"); pg.click('[data-lvlup] >> nth=0'); print("Stufe vorher/nachher:", before, pg.evaluate("JSON.stringify(levels)"))
    pg.click('#dlg-sum [data-effort="genau"]'); print("Effort:", pg.evaluate("WK[WK.length-1].effort"))
    pg.evaluate("closeDialog(document.querySelector('#dlg-sum'))"); pg.wait_for_timeout(400)
    # Fortschritt mit Daten
    pg.evaluate("""log=[{date:'2026-10-05',weight:81.4,waist:96},{date:'2026-10-12',weight:80.9,waist:95.5},{date:'2026-10-19',weight:80.6,waist:95},{date:'2026-10-26',weight:80.8,waist:94.5},{date:'2026-11-01',weight:79.9,waist:94}]; sessions=['2026-10-05','2026-10-07','2026-10-09','2026-10-12','2026-10-14','2026-10-19','2026-10-21','2026-10-23','2026-10-26','2026-10-28','2026-11-02']; renderProgress(); renderToday();""")
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(500); pg.screenshot(path=__import__("fcenv").SHOTS + "/v11-fortschritt.png", full_page=True)
    print("Serie:", pg.evaluate("weekStreak()"))
    # Ziele ändern -> Rad nutzt sie
    pg.evaluate("document.querySelector('#b-settings').click()"); pg.wait_for_timeout(500)
    pg.fill('#s-kcal','2200'); pg.dispatch_event('#s-kcal','change'); pg.fill('#s-protein','150'); pg.dispatch_event('#s-protein','change')
    print("Ziele:", pg.evaluate("JSON.stringify(GOALS)"), "protTarget:", pg.evaluate("protTarget()"))
    c.close()
    c=b.new_context(viewport={"width":390,"height":844},color_scheme="dark",device_scale_factor=2)
    pg=c.new_page(); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(600); pg.evaluate("sessions=['2026-10-26','2026-10-28','2026-11-02']; DIARY[todayISO()]={items:[{t:'Test',k:900,p:60,c:3}],water:3}; renderToday()")
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v11-m-heute.png")
    print("overflow:", pg.evaluate("document.documentElement.scrollWidth>innerWidth"))
    c.close(); b.close()
print("errors:",errs)
