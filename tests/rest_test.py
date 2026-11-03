from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    ck("eco Standard an", pg.evaluate("PREP.eco===true"))
    pg.evaluate("showTab('vorkochen')"); pg.wait_for_timeout(400)
    ck("Chip Reste sparsam", pg.evaluate("!!document.querySelector('[data-prepopt=eco]')") and pg.evaluate("document.querySelector('[data-prepopt=eco]').getAttribute('aria-pressed')")=="true")
    ck("Reste-Karte da", "Reste" in pg.inner_text("#panel-vorkochen"))
    # Messung: Reste mit/ohne eco
    js="""(eco)=>{ PREP.eco=eco; const W=[],P=[]; let t0=performance.now(); for(let i=0;i<60;i++){ PREP.main=[];PREP.b='';PREP.s='';prepGen('all'); const c=prepCalc(); W.push(restWaste(c.calc)); P.push(c.items.filter(x=>x.kind==='Hauptgericht').reduce((a,x)=>a+x.r.protein,0)/PREP.main.length); } const ms=(performance.now()-t0)/60; return {w:W.reduce((a,x)=>a+x,0)/W.length, p:P.reduce((a,x)=>a+x,0)/P.length, ms}; }"""
    on=pg.evaluate(js,True); off=pg.evaluate(js,False)
    print(on,off)
    ck("weniger Reste mit eco", on['w']<off['w']*0.75, f"{on['w']:.2f} vs {off['w']:.2f}")
    ck("Eiweiss bleibt (max -3 g)", on['p']>=off['p']-3, f"{on['p']:.1f} vs {off['p']:.1f}")
    ck("Generieren schnell (<150 ms)", on['ms']<150, on['ms'])
    pg.evaluate("PREP.eco=true; PREP.main=[];prepGen('all')")
    ck("n Hauptgerichte eindeutig", pg.evaluate("new Set(PREP.main).size===PREP.n && PREP.main.length===PREP.n"))
    ck("b und s gesetzt", pg.evaluate("!!byId(PREP.b)&&!!byId(PREP.s)"))
    for n in (1,3):
        pg.evaluate(f"PREP.n={n}; PREP.main=[]; prepGen('all')")
        ck(f"n={n}: Hauptgerichte", pg.evaluate("PREP.main.length")==n)
    pg.evaluate("PREP.n=2; PREP.main=[]; prepGen('all'); prepGen('m0'); prepGen('m1'); prepGen('b'); prepGen('s')")
    ck("Einzel-Neuwuerfeln ok", pg.evaluate("PREP.main.length===2 && !!byId(PREP.b) && !!byId(PREP.s)"))
    # Konkretes Beispiel: Quark-Reste
    pg.evaluate("""()=>{ const q=RECIPES.filter(r=>r.ing.some(i=>i[4]==='quark')); window.__q=q.map(r=>r.id); }""")
    ids=pg.evaluate("""()=>{ const cand=RECIPES.filter(r=>r.meal==='Mittag/Abend'&&r.tags.includes('Meal-Prep')&&r.ing.some(i=>i[4]==='quark')); PREP.people=1;PREP.days=3;PREP.n=1;PREP.brk=false;PREP.snk=false; for(const r of cand){ PREP.main=[r.id]; const c=prepCalc(); const l=restLines(c.calc).find(x=>x.k==='quark'); if(l) return [r.id,Math.round(l.left)]; } return null; }""")
    print(ids)
    if ids:
        pg.evaluate("renderPrep()"); pg.wait_for_timeout(200)
        t=pg.inner_text("#panel-vorkochen")
        ck("Reste-Karte nennt Quark mit Menge", "Quark" in t and "Rest ca." in t and "Offen hält es etwa bis" in t)
        ck("Einfrier-Hinweis bei Quark", "sonst einfrieren" in t)
        ck("Idee-Buttons oeffnen Rezept", pg.evaluate("document.querySelectorAll('#panel-vorkochen .restideas [data-recipe]').length")>0)
        btn=pg.query_selector('#panel-vorkochen .restideas [data-recipe]')
        if btn:
            btn.click(); pg.wait_for_timeout(400)
            ck("Rezept-Dialog", pg.evaluate("document.getElementById('dlg-recipe').open"))
            pg.evaluate("document.getElementById('dlg-recipe').close()")
    pg.evaluate("PREP.people=2;PREP.days=6;PREP.n=2;PREP.brk=true;PREP.snk=true;PREP.main=[];prepGen('all');renderPrep()")
    # Chip toggle
    pg.click('[data-prepopt=eco]'); pg.wait_for_timeout(300)
    ck("eco aus", pg.evaluate("PREP.eco===false") and pg.evaluate("JSON.parse(localStorage.getItem('fc_prep')).eco===false"))
    ck("Hinweis aus", "ist aus" in pg.inner_text("#panel-vorkochen") or "kaum etwas übrig" in pg.inner_text("#panel-vorkochen"))
    pg.click('[data-prepopt=eco]'); pg.wait_for_timeout(300)
    ck("eco wieder an", pg.evaluate("PREP.eco===true"))
    # kaputte Daten
    pg.evaluate("localStorage.setItem('fc_prep', JSON.stringify({eco:'x'}))"); pg.reload(); pg.wait_for_timeout(600)
    ck("eco falscher Typ -> true", pg.evaluate("PREP.eco===true"))
    pg.evaluate("localStorage.setItem('fc_prep', JSON.stringify({eco:false}))"); pg.reload(); pg.wait_for_timeout(600)
    ck("eco false bleibt", pg.evaluate("PREP.eco===false"))
    pg.evaluate("showTab('vorkochen')"); pg.wait_for_timeout(300)
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth")<=390)
    ck("keine JS-Fehler", not errs, errs[:3])
    b.close()
print("FAILS:",fails)
