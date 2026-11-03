from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":1200,"height":900}); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(500)
    print("Uebungen:",pg.evaluate("EX.map(e=>e.name+' ('+e.ladder.length+')')"))
    print("Minuten:",pg.evaluate("estMinutes()"))
    pg.evaluate("showTab('uebungen')"); pg.wait_for_timeout(200)
    print("Phase:",pg.inner_text("#panel-uebungen .card >> nth=0")[:160].replace("\n"," | "))
    # Trainingstage
    pg.evaluate("document.getElementById('b-settings').click()"); pg.wait_for_timeout(300)
    print("Tage-Buttons:",pg.evaluate("document.querySelectorAll('.dbtn').length"))
    pg.click('.dbtn[data-day="1"]'); pg.click('.dbtn[data-day="2"]'); pg.wait_for_timeout(200)
    print("Tage:",pg.evaluate("settings.tdays"),"| Hinweis:",pg.inner_text("#tdays-note"))
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300); pg.evaluate("showTab('heute')"); pg.wait_for_timeout(200)
    print("Heute ring:",pg.evaluate("document.querySelector('.rings').innerText.replace(/\\n/g,' ')"))
    # Saetze-Empfehlung
    pg.evaluate("sessions=['2026-10-01']; showTab('uebungen')"); pg.wait_for_timeout(200)
    print("Woche:",pg.evaluate("weekNo()"),"| Button:",pg.evaluate("!!document.querySelector('[data-setsrec]')"))
    pg.click('[data-setsrec]'); pg.wait_for_timeout(200); print("Saetze nach Klick:",pg.evaluate("settings.sets"))
    # Workout mit 6 Uebungen durchspielen
    r=pg.evaluate("""()=>{ settings.sets=2; startWorkout(); beginWork(); let n=0; for(let i=0;i<60 && W.phase!=='done';i++){ act('done'); if(W.phase==='rest'||W.phase==='prep') skipTimer(); n++; } return {phase:W.phase,wk:WK.length,last:WK.length?WK[WK.length-1].sets.map(s=>s.ex).filter((v,i,a)=>a.indexOf(v)===i):[]} }""")
    print("Workout:",r)
    pg.evaluate("openV3('pike',3)"); pg.wait_for_timeout(600); print("3D Pike:",pg.inner_text("#v3-title"),"|",pg.inner_text("#v3-phase"))
    print("ERRORS",errs[:5]); b.close()
