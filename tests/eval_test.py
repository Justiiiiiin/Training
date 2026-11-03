from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
SETUP="""(cfg)=>{
  log.length=0; Object.keys(DIARY).forEach(k=>delete DIARY[k]);
  const t=todayISO();
  for(let i=0;i<cfg.nw;i++){ const day=Math.round(i*(27/Math.max(1,cfg.nw-1))); const d=shiftDay(t,-27+day); log.push({date:d,weight:Math.round((cfg.w0+cfg.perDay*day+((i%2)?0.1:-0.1))*10)/10}); }
  for(let i=0;i<cfg.nd;i++){ const d=shiftDay(t,-i); DIARY[d]={items:[{t:'x',k:cfg.kcal,p:cfg.prot,c:0}],water:0}; }
  GOALS.kcal=cfg.goal; renderProgress(); return coachEval();
}"""
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600); pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(200)
    def run(cfg): 
        r=pg.evaluate(SETUP,cfg); pg.wait_for_timeout(100); return r, pg.inner_text(".coacheval")
    r,t=run(dict(nw=0,nd=0,w0=82,perDay=0,kcal=1900,prot=130,goal=1900))
    ck("Keine Daten: Hinweis", "Noch zu wenig Daten" in t, t[:90].replace("\n"," "))
    r,t=run(dict(nw=3,nd=20,w0=82,perDay=-0.05,kcal=1900,prot=130,goal=1900)); ck("3 Gewichte: zu wenig", r.get("rate") is None and "Noch zu wenig" in t, t[:70])
    r,t=run(dict(nw=8,nd=6,w0=82,perDay=-0.05,kcal=1900,prot=130,goal=1900)); ck("Nur 6 Essenstage: zu wenig", r.get("rate") is None)
    r,t=run(dict(nw=8,nd=20,w0=82,perDay=-0.05,kcal=1900,prot=130,goal=1900))
    print("  Tempo ok:",{k:(round(v,2) if isinstance(v,float) else v) for k,v in r.items()}); print("  ",t.replace("\n"," | ")[:420])
    ck("Rate etwa -0,35 kg/Woche", -0.45<r["rate"]<-0.25, r["rate"])
    ck("Verbrauch etwa 2285", 2150<r["tdee"]<2400, r["tdee"])
    ck("Tempo passt: kein Vorschlag", "Das Tempo passt gut" in t and "setzen" not in t)
    r,t=run(dict(nw=8,nd=20,w0=84,perDay=-0.15,kcal=1900,prot=130,goal=1900))
    ck("Zu schnell: Warnung + Vorschlag hoeher", "schneller als empfohlen" in t and "setzen" in t, t[-260:].replace("\n"," | "))
    btn=pg.get_attribute('[data-setkcal]','data-setkcal'); ck("Vorschlag hoeher, max +200 begrenzt", 1900<int(btn)<=2100, btn)
    pg.click('[data-setkcal]'); pg.wait_for_timeout(200); ck("Knopf setzt Kalorienziel", pg.evaluate("GOALS.kcal")==int(btn), pg.evaluate("GOALS.kcal"))
    r,t=run(dict(nw=8,nd=20,w0=82,perDay=0,kcal=1900,prot=100,goal=1900))
    ck("Stagnation: Vorschlag runter, nicht unter Untergrenze", "bleibt etwa gleich" in t and pg.evaluate("Math.max(1600,Math.round(prof.weight*22))")<=int(pg.get_attribute('[data-setkcal]','data-setkcal'))<1900, pg.get_attribute('[data-setkcal]','data-setkcal'))
    ck("Eiweissmangel erwaehnt", "Eiweiß liegt im Schnitt" in t)
    r,t=run(dict(nw=8,nd=20,w0=80,perDay=0.04,kcal=2300,prot=130,goal=2300))
    ck("Gewicht steigt: Hinweis + Vorschlag", "steigt" in t and "setzen" in t)
    r,t=run(dict(nw=8,nd=20,w0=70,perDay=0.0,kcal=2200,prot=130,goal=1600))
    sug=pg.evaluate("document.querySelector('[data-setkcal]')?.dataset.setkcal||null"); print("  Ziel 1600 niedrig, Stagnation ->",sug)
    ck("Ziel nahe Untergrenze: kein weiteres Senken", sug is None and "Untergrenze" in pg.inner_text(".coacheval"), sug)
    # Tage unter 1000 kcal zaehlen nicht
    r=pg.evaluate(SETUP,dict(nw=8,nd=12,w0=82,perDay=-0.05,kcal=900,prot=50,goal=1900)); ck("Tage unter 1000 kcal ignoriert", r.get("rate") is None, r.get("eatenDays"))
    # kaputte Daten (ueber den Speicher, damit die Bereinigung greift)
    pg.evaluate("store.set('fc_log',[{date:'xx',weight:'a'},{date:shiftDay(todayISO(),-2),weight:null},{date:shiftDay(todayISO(),-3),weight:'80',waist:NaN},{date:shiftDay(todayISO(),-4),weight:81.5}]); store.set('fc_diary',{'2026-01-01':{items:[{t:'a',k:NaN,p:null}],water:0}})"); pg.reload(); pg.wait_for_timeout(800)
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(250)
    ck("Kaputte Eintraege: kein Absturz", "Auswertung" in pg.inner_text("#charts"))
    ck("Log bereinigt (nur gueltige Zahlen)", pg.evaluate("log.every(x=>/^\\d{4}-\\d{2}-\\d{2}$/.test(x.date)&&(x.weight==null||isFinite(x.weight)))") and pg.evaluate("log.length")==3, pg.evaluate("log.length"))
    # Uebungskarten + Verlauf
    pg.evaluate("""()=>{ WK.length=0; const t=todayISO(); levels.squat=1; 
      WK.push({date:shiftDay(t,-6),min:20,sets:[{ex:'squat',lvl:1,set:1,reps:12,secs:null},{ex:'squat',lvl:1,set:2,reps:11,secs:null},{ex:'push',lvl:1,set:1,reps:8,secs:null}],effort:'',q:0});
      WK.push({date:shiftDay(t,-2),min:20,sets:[{ex:'squat',lvl:1,set:1,reps:15,secs:null},{ex:'squat',lvl:1,set:2,reps:15,secs:null},{ex:'push',lvl:1,set:1,reps:9,secs:null}],effort:'',q:0});
      renderEx(); renderProgress(); }""")
    pg.evaluate("showTab('uebungen')"); pg.wait_for_timeout(250)
    ck("Karte Kniebeugen: zuletzt + bereit", "Zuletzt:" in pg.inner_text("#panel-uebungen") and "Bereit für die nächste Stufe" in pg.inner_text("#panel-uebungen"))
    ck("Liegestuetze: zuletzt, nicht bereit", pg.evaluate("exHintHTML(EX.find(e=>e.id==='push'))").count("Bereit")==0 and "Zuletzt" in pg.evaluate("exHintHTML(EX.find(e=>e.id==='push'))"))
    pg.evaluate("document.querySelector('[data-lvlup=\"squat\"]').click()"); pg.wait_for_timeout(200)
    ck("Stufe hoch klappt", pg.evaluate("levels.squat")==2, pg.evaluate("levels.squat"))
    ck("Danach: nicht mehr bereit (neue Stufe, kein Verlauf)", "Bereit" not in pg.evaluate("exHintHTML(EX.find(e=>e.id==='squat'))"))
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(250)
    txt=pg.inner_text("#charts"); ck("Leistungskarte da", "Leistung pro Übung" in txt)
    ck("Rekord markiert", "Rekord" in txt, txt[txt.find("Leistung"):][:230].replace("\n"," | "))
    n0=pg.evaluate("document.querySelectorAll('[data-perf]').length"); pg.click('[data-perf="push"]'); pg.wait_for_timeout(150)
    ck("Chips wechseln die Uebung", pg.evaluate("PERF")=="push" and n0>=2, n0)
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth"))
    pg.screenshot(path=__import__("fcenv").SHOTS + "/v315_eval.png", full_page=False)
    print("Fehler:",errs); ck("keine Fehler", not errs)
    b.close()
print("FAILS",fails)
