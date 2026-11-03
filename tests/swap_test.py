from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":1200,"height":900}); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    ck("Standard: Rucksack-Rudern aktiv", pg.evaluate("EX.find(e=>e.slot==='row').id")=="rowbp")
    ck("6 Plaetze", pg.evaluate("EX.length")==6)
    ck("alle Varianten haben 3D", pg.evaluate("EXALL.filter(e=>!e.gear).every(e=>V3A[e.id] && V3A[e.id].length===e.ladder.length)"), pg.evaluate("EXALL.filter(e=>!e.gear).filter(e=>!(V3A[e.id]&&V3A[e.id].length===e.ladder.length)).map(e=>e.id)"))
    ck("alle Varianten MAPX", pg.evaluate("EXALL.every(e=>MAPX[e.id])"))
    pg.evaluate("showTab('uebungen')"); pg.wait_for_timeout(200)
    ck("Austauschen-Buttons", pg.evaluate("document.querySelectorAll('#panel-uebungen [data-swapopen]').length")==6)
    pg.click('#panel-uebungen [data-swapopen="row"]'); pg.wait_for_timeout(400)
    ck("Dialog offen", pg.evaluate("document.getElementById('dlg-swap').open"))
    ck("4 Reihen-Varianten", pg.evaluate("document.querySelectorAll('#dlg-swap .swopt:not(.locked)').length")==4, pg.inner_text("#dlg-swap h3"))
    ck("Hinweis Tisch", "Tisch" in pg.inner_text("#dlg-swap"))
    # nur heute -> Superman
    pg.click('#dlg-swap [data-swap="rowsup"][data-mode="day"]'); pg.wait_for_timeout(300)
    ck("heute: rowsup", pg.evaluate("EX.find(e=>e.slot==='row').id")=="rowsup")
    ck("nicht dauerhaft", pg.evaluate("settings.alt.row")=="rowbp")
    # dauerhaft -> Tisch
    pg.click('#dlg-swap [data-swap="row"][data-mode="perm"]'); pg.wait_for_timeout(300)
    ck("dauerhaft row (heute-Wahl entfernt)", pg.evaluate("EX.find(e=>e.slot==='row').id")=="row" and pg.evaluate("settings.alt.row")=="row")
    pg.evaluate("document.getElementById('dlg-swap').close()")
    # 3D aus Dialog
    pg.evaluate("openV3('rowtowel',1)"); pg.wait_for_timeout(700)
    ck("3D Titel", pg.inner_text("#v3-title")=="Handtuch-Rudern an der Tür", pg.inner_text("#v3-title"))
    ck("3D Hier arbeitet", "Rücken" in pg.inner_text("#v3-txt"), pg.inner_text("#v3-txt")[:120].replace("\n"," "))
    ck("3D Varianten-Leiste", pg.evaluate("document.querySelectorAll('#v3-alts [data-v3alt]').length")==4)
    pg.click('#v3-alts [data-v3alt="rowbp"]'); pg.wait_for_timeout(500)
    ck("3D wechselt", pg.inner_text("#v3-title")=="Rucksack-Rudern", pg.inner_text("#v3-title"))
    ck("Schritt-Zaehler", "von" in pg.inner_text("#v3-phase"), pg.inner_text("#v3-phase"))
    pg.evaluate("document.getElementById('dlg-3d').close()")
    # Training mit Rucksack-Rudern, Log
    pg.evaluate("settings.alt.row='rowbp'; applyAlts(); settings.sets=1; renderEx(); render()")
    r=pg.evaluate("""()=>{ startWorkout(); beginWork(); const ids=[]; for(let i=0;i<40 && W.phase!=='done';i++){ if(W.phase==='work'&&EX[W.ex].type!=='hold') setDone(9); else act('done'); if(W.phase==='rest'||W.phase==='prep') skipTimer(); } return WK[WK.length-1].sets.map(s=>s.ex).join(','); }""")
    ck("Log mit rowbp", "rowbp" in r, r)
    ck("Volumen zaehlt Ruecken", pg.evaluate("weekSets(weekStartISO(todayISO())).back")>0)
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(300)
    ck("Zusammenfassung zeigt Rucksack", "Rucksack" in pg.evaluate("(openSummary(WK.length-1), document.getElementById('dlg-sum').innerText)"))
    pg.evaluate("document.getElementById('dlg-sum').close()")
    # Persistenz + kaputte Daten
    pg.evaluate("localStorage.setItem('fc_settings', JSON.stringify({alt:{row:'bogus', squat:'rowbp', push:'pushfp'}}))")
    pg.reload(); pg.wait_for_timeout(600)
    ck("Kaputte alt bereinigt", pg.evaluate("JSON.stringify(settings.alt)")=='{"push":"pushfp"}', pg.evaluate("JSON.stringify(settings.alt)"))
    ck("push=pushfp aktiv", pg.evaluate("EX.find(e=>e.slot==='push').id")=="pushfp")
    ck("row faellt auf Basis", pg.evaluate("EX.find(e=>e.slot==='row').id")=="row")
    # Coach-3D im Training mit Alternative
    pg.evaluate("startWorkout()"); pg.wait_for_timeout(500)
    ck("keine Fehler", not errs, str(errs[:3]))
    print("FAILS",fails); b.close()
