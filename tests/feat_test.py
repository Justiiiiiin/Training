from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(500)
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(300)
    print("leer:",pg.inner_text("#volcard").replace("\n"," | ")[:200])
    print("Erfolge:",pg.inner_text("#badgecard h3"),pg.inner_text("#badgecard p"))
    # Kurz-Training komplett
    r=pg.evaluate("""()=>{ startWorkout(true); beginWork(); const steps=[]; for(let i=0;i<40 && W.phase!=='done';i++){ if(W.phase==='rest'||W.phase==='prep'||W.phase==='warmup') skipTimer(); else act('done'); steps.push(W.phase+':'+W.ex+'.'+W.set); } return {phase:W.phase, wk:WK.length, q:WK[WK.length-1].q, sets:WK[WK.length-1].sets.length, n:steps.length} }""")
    print("Kurz:",r)
    # Voller Durchlauf mit Auslassen
    r=pg.evaluate("""()=>{ settings.sets=2; startWorkout(); beginWork(); act('skipex'); const ex1=W.ex; act('done'); for(let i=0;i<60 && W.phase!=='done';i++){ if(W.phase==='rest'||W.phase==='prep') skipTimer(); else act('done'); } const l=WK[WK.length-1]; return {ex1, phase:W.phase, exs:[...new Set(l.sets.map(s=>s.ex))], q:l.q} }""")
    print("Auslassen:",r)
    # Letztes Mal
    r=pg.evaluate("""()=>{ const e=EX[0]; const t=lastTxt(e); startWorkout(); beginWork(); return {t, sub:document.getElementById('sub').textContent, cap:document.getElementById('caption').textContent.slice(0,200)} }""")
    print("Letztes Mal:",r); pg.evaluate("stopWorkout()")
    # Volumen nach Training
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(300)
    print("Volumen:",pg.inner_text("#volcard").replace("\n"," | ")[:330])
    print("Erfolge:",pg.inner_text("#badgecard p"),"|",pg.evaluate("[...document.querySelectorAll('#badgecard li.got b')].map(e=>e.textContent)"))
    pg.evaluate("scrollTo(0,0)"); pg.screenshot(path=__import__("fcenv").SHOTS + "/feat_progress.png",full_page=False)
    # Overflow
    print("overflow",pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth"))
    # Sprache
    pg.evaluate("act('startquick')"); pg.wait_for_timeout(200); print("Sprache Kurz:",pg.evaluate("W.quick+':'+W.phase")); pg.evaluate("stopWorkout()")
    print("ERRORS",errs[:5]); b.close()
