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
    ck("Tab da", pg.evaluate("GROUPS.find(g=>g.id==='essen').tabs.includes('vorkochen')"))
    pg.evaluate("showTab('vorkochen')"); pg.wait_for_timeout(300)
    t=pg.inner_text("#panel-vorkochen")
    ck("Plan gerendert", "Vorkochplan" in t and "Sonntag: Reihenfolge" in t, t[:80].replace("\n"," "))
    ck("2 Hauptgerichte + Fruehstueck + Snack", pg.evaluate("prepCalc().items.length")==4, pg.evaluate("prepCalc().items.map(i=>i.kind+': '+i.r.title+' x'+i.n)"))
    ck("Woche 6 Tage", pg.evaluate("document.querySelectorAll('.prepweek li:not(.wk-all)').length")==6)
    ck("keine Ausschluesse", pg.evaluate("prepCalc().items.every(i=>!isExc(i.r))"))
    ck("kein Spinat", pg.evaluate("prepCalc().items.every(i=>!hasSpin(i.r))"))
    ck("Einkauf berechnet", pg.evaluate("prepCalc().calc.total")>3, str(pg.evaluate("prepCalc().calc.total")))
    ck("Mains verschieden", pg.evaluate("new Set(PREP.main).size===PREP.main.length && (PREP.main.length<2 || mainKind(byId(PREP.main[0]))!==mainKind(byId(PREP.main[1])))"))
    # Personen
    n0=pg.evaluate("prepCalc().items[0].n")
    pg.click('[data-prepopt="people"][data-d="1"]'); pg.wait_for_timeout(200)
    ck("Personen 3 -> Portionen skalieren", pg.evaluate("prepCalc().items[0].n")==n0//2*3, str(pg.evaluate("[PREP.people, prepCalc().items[0].n]")))
    pg.click('[data-prepopt="days"][data-v="4"]'); pg.wait_for_timeout(200)
    ck("4 Tage", pg.evaluate("document.querySelectorAll('.prepweek li:not(.wk-all)').length")==4)
    pg.click('[data-prepopt="n"][data-v="3"]'); pg.wait_for_timeout(200)
    ck("3 Hauptgerichte", pg.evaluate("PREP.main.length")==3, str(pg.evaluate("PREP.main")))
    pg.click('[data-prepopt="brk"]'); pg.wait_for_timeout(200)
    ck("ohne Fruehstueck", pg.evaluate("prepCalc().items.every(i=>i.kind!=='Frühstück')"))
    old=pg.evaluate("PREP.main[0]")
    pg.click('[data-prepgen="m0"]'); pg.wait_for_timeout(200)
    ck("anderes Gericht", pg.evaluate("PREP.main[0]")!=old)
    pg.click('[data-prepgen="all"]'); pg.wait_for_timeout(200)
    ck("neu gewuerfelt, Anzahl stimmt", pg.evaluate("PREP.main.length")==3)
    # Einkaufsliste
    pg.evaluate("CART=[]; saveCart()")
    pg.click('[data-prepcart]'); pg.wait_for_timeout(200)
    ck("Warenkorb gefuellt", pg.evaluate("CART.length")>=3, str(pg.evaluate("CART")))
    # Wochenwahl
    w0=pg.evaluate("PREP.week"); m0=pg.evaluate("JSON.stringify(PREP.main)")
    ck("Zurueck gesperrt in aktueller Woche", pg.evaluate("document.querySelector('[data-prepweek=\"-1\"]').disabled") or pg.evaluate("PREP.week")>=pg.evaluate("weekStartISO(todayISO())"))
    pg.click('[data-prepweek="1"]'); pg.wait_for_timeout(250)
    w1=pg.evaluate("PREP.week"); m1=pg.evaluate("JSON.stringify(PREP.main)")
    ck("naechste Woche gewaehlt", w1>w0 and "ab" in pg.inner_text("#panel-vorkochen") or w1>w0, w0+" -> "+w1)
    ck("Label", any(x in pg.inner_text(".weekpick") for x in ["Nächste Woche","Diese Woche","In 2 Wochen"]), pg.inner_text(".weekpick").replace("\n"," "))
    pg.click('[data-prepweek="-1"]'); pg.wait_for_timeout(250)
    ck("zurueck, Plan blieb gleich", pg.evaluate("PREP.week")==w0 and pg.evaluate("JSON.stringify(PREP.main)")==m0)
    for _ in range(7): 
        if pg.evaluate("!document.querySelector('[data-prepweek=\"1\"]').disabled"): pg.click('[data-prepweek="1"]'); pg.wait_for_timeout(100)
    ck("maximal 4 Wochen voraus", pg.evaluate("PREP.week")==pg.evaluate("shiftDay(weekStartISO(todayISO()),28)"), pg.evaluate("PREP.week"))
    pg.click('[data-prepweek="-1"]'); pg.click('[data-prepweek="-1"]'); pg.click('[data-prepweek="-1"]'); pg.click('[data-prepweek="-1"]'); pg.wait_for_timeout(200)
    ck("Pläne gespeichert", pg.evaluate("Object.keys(PREP.plans).length")>=2, pg.evaluate("Object.keys(PREP.plans).join(',')"))
    # Haken
    pg.evaluate("document.getElementById('prepsteps').open=true")
    pg.click('[data-prepchk="setup"]'); pg.wait_for_timeout(100)
    ck("Schritt abgehakt", pg.evaluate("PREP.done.setup===true"))
    # Persistenz
    pg.reload(); pg.wait_for_timeout(600)
    ck("persistiert", pg.evaluate("PREP.main.length")==3 and pg.evaluate("PREP.people")==3 and pg.evaluate("PREP.days")==4, str(pg.evaluate("JSON.stringify(PREP)")[:140]))
    # Heute-Karte: Sonntag / Wochentag
    for wd,label in [(6,"Vorkochtag"),(1,"aus der Box")]:
        r=pg.evaluate("""(wd)=>{ const D=Date; const base=new Date('2026-11-0'+(wd===6?1:3)+'T10:00:00'); // 1.11.2026 = Sonntag, 3.11 = Dienstag
          window.__RD=D; window.Date=class extends D{ constructor(...a){ if(a.length) super(...a); else super(base.getTime()); } static now(){return base.getTime();} };
          if(wd===6) PREP.week=''; else PREP.week='2026-11-02'; renderToday(); const t=document.getElementById('panel-heute').innerText; return t; }""",wd)
        ck("Heute: "+label, label.lower() in r.lower() or (wd==1 and "Box" in r), r[:0])
        pg.evaluate("window.Date=window.__RD")
    # Kaputte Daten
    pg.evaluate("localStorage.setItem('fc_prep', JSON.stringify({people:'x', main:['bogus', 5], days:99, b:5}))")
    pg.reload(); pg.wait_for_timeout(600)
    ck("kaputte Prep bereinigt", pg.evaluate("PREP.people===2 && PREP.days===6 && PREP.main.length===0 && PREP.b===''"), pg.evaluate("JSON.stringify(PREP)"))
    pg.evaluate("showTab('vorkochen')"); pg.wait_for_timeout(300)
    ck("rendert nach Reparatur", "Vorkochplan" in pg.inner_text("#panel-vorkochen"))
    # Mobil 320
    pg.set_viewport_size({"width":320,"height":700}); pg.evaluate("showTab('vorkochen')"); pg.wait_for_timeout(300)
    ck("kein Ueberlauf 320", pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"), str(pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/prep320.png", full_page=False)
    ck("keine Fehler", not errs, str(errs[:3]))
    print("FAILS",fails); b.close()
