from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
SETUP="""()=>{
  const mk=(id,meal,k,g)=>({id,title:id,meal,time:5,kcal:300,protein:20,cost:0.5,veg:0,diet:'vegetarisch',tags:[],contains:[],ing:[[g,'g','Magerquark',null,k]],steps:['x']});
  if(!byId('t300')) { RECIPES.push(mk('t300','Frühstück','quark',300)); RECIPES.push(mk('t200','Frühstück','quark',200)); RECIPES.push(mk('tmain','Mittag/Abend','quark',300)); }
  GOALS.hh=1; DIARY={}; GOALS.buys=[];
}"""
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    pg.evaluate(SETUP)
    ev=lambda: pg.evaluate("(()=>{const E=buyEstimate(); return E.packs.filter(x=>x.k==='quark').map(x=>({d:x.d,n:x.n,cost:Math.round(x.cost*100)/100,uses:x.uses.length}))})()")
    # Dein Beispiel: 300 g Montag, 200 g Donnerstag -> eine Packung
    pg.evaluate("""()=>{ DIARY['2026-10-05']={items:[{id:'t300',t:'t300',k:1,p:1,c:0.3}],water:0}; DIARY['2026-10-08']={items:[{id:'t200',t:'t200',k:1,p:1,c:0.2}],water:0}; }""")
    r=ev(); ck("300 g Mo + 200 g Do = eine Packung", len(r)==1 and r[0]['n']==1 and r[0]['uses']==2 and abs(r[0]['cost']-0.99)<0.01, r)
    # zu spaet -> zwei Packungen
    pg.evaluate("""()=>{ DIARY['2026-10-08']=undefined; delete DIARY['2026-10-08']; DIARY['2026-10-12']={items:[{id:'t200',t:'t200',k:1,p:1,c:0.2}],water:0}; }""")
    r=ev(); ck("Donnerstag knapp danach, aber ueber Haltbarkeit -> zwei Packungen", len(r)==2 and abs(sum(x['cost'] for x in r)-1.98)<0.01, r)
    # Randfall: genau am letzten Tag (4 Tage) noch erlaubt
    pg.evaluate("""()=>{ delete DIARY['2026-10-12']; DIARY['2026-10-09']={items:[{id:'t200',t:'t200',k:1,p:1,c:0.2}],water:0}; }""")
    r=ev(); ck("am 4. Tag noch dieselbe Packung", len(r)==1, r)
    pg.evaluate("""()=>{ delete DIARY['2026-10-09']; DIARY['2026-10-10']={items:[{id:'t200',t:'t200',k:1,p:1,c:0.2}],water:0}; }""")
    r=ev(); ck("am 5. Tag neue Packung", len(r)==2, r)
    # mehr als eine Packung, Rest wird weiterverwendet
    pg.evaluate("""()=>{ DIARY={}; DIARY['2026-10-05']={items:[{id:'t300',t:'t300 ×3',n:3,k:1,p:1,c:1}],water:0}; DIARY['2026-10-07']={items:[{id:'t200',t:'t200',k:1,p:1,c:0.2}],water:0}; }""")
    r=ev(); ck("900 g = 2 Packungen, Rest 100 g, +200 g -> 3. Packung", sum(x['n'] for x in r)==3, r)
    # Portionen aus Titel ohne n-Feld
    pg.evaluate("""()=>{ DIARY={}; DIARY['2026-10-05']={items:[{id:'t300',t:'t300 ×2',k:1,p:1,c:1}],water:0}; }""")
    r=ev(); ck("×2 aus Titel gelesen (600 g = 2 Packungen)", sum(x['n'] for x in r)==2, r)
    # Haushalt: Hauptgerichte x Personen, Fruehstueck nicht
    pg.evaluate("""()=>{ DIARY={}; GOALS.hh=2; DIARY['2026-10-05']={items:[{id:'tmain',t:'tmain',k:1,p:1,c:0.3},{id:'t200',t:'t200',k:1,p:1,c:0.2}],water:0}; }""")
    r=ev(); ck("Hauptgericht zaehlt doppelt (600 g), Fruehstueck einfach (200 g) = 800 g = 2 Packungen", sum(x['n'] for x in r)==2, r)
    pg.evaluate("GOALS.hh=1")
    # Fremde Eintraege (Rechner) zaehlen als Preislistenpreis
    pg.evaluate("""()=>{ DIARY={}; DIARY['2026-10-05']={items:[{t:'Eigenes',k:500,p:20,c:1.5}],water:0}; }""")
    ck("Rechner-Eintraege zaehlen anteilig", abs(pg.evaluate("estRange('2026-10-01','2026-10-31')")-1.5)<0.01)
    # Zutaten aus der echten Rezeptliste
    pg.evaluate("""()=>{ DIARY={}; GOALS.hh=2; const ids=['haehnchen-reis-pfanne','chili-con-carne-mit-reis','skyr-bowl-mit-erdbeeren-und-haferflocken']; ids.forEach((id,i)=>{ DIARY['2026-10-0'+(i+1)]={items:[{id,n:1,t:'x',k:1,p:1,c:1}],water:0}; }); }""")
    E=pg.evaluate("(()=>{const E=buyEstimate(); return E.packs.map(x=>x.k)})()")
    ck("echte Rezepte ergeben Packungen", len(E)>=6, E)
    ck("Vorrat (Öl, Gewürze) nicht dabei", not any(k in E for k in ['oel','honig','curry','kurkuma','soja','senf']), E)
    # UI
    pg.evaluate(SETUP)
    pg.evaluate("""()=>{ DIARY['2026-10-05']={items:[{id:'t300',n:1,t:'t300',k:1,p:1,c:0.3}],water:0}; DIARY['2026-10-08']={items:[{id:'t200',n:1,t:'t200',k:1,p:1,c:0.2}],water:0}; SPM='2026-10'; saveToday(); showTab('einkauf'); renderShop(); }""")
    pg.wait_for_timeout(300)
    t=pg.inner_text("#spendcard")
    ck("Karte zeigt geschaetzten Einkauf", "Einkauf geschätzt, 1 Packung" in t, t[:200].replace("\n"," | "))
    ck("Betrag 0,99", "0,99" in t)
    pg.evaluate("document.getElementById('estbox').open=true"); pg.wait_for_timeout(200)
    t=pg.inner_text("#estbox")
    ck("Aufschluesselung nennt beide Tage", "300 g" in t and "200 g" in t and "zusammen 1 Packung" in t, t[:300].replace("\n"," | "))
    ck("Magerquark genannt", "Magerquark" in t)
    # Haushalt umschalten
    pg.click('#spendcard [data-hh="2"]'); pg.wait_for_timeout(300)
    ck("hh gespeichert", pg.evaluate("GOALS.hh===2 && JSON.parse(localStorage.getItem('fc_goals')).hh===2"))
    ck("Details bleiben offen nach Klick", pg.evaluate("document.getElementById('estbox').open"))
    ck("Segment-Knopf gedrueckt", pg.evaluate("document.querySelector('#spendcard [data-hh=\"2\"]').getAttribute('aria-pressed')")=="true")
    # Verfallene Reste
    pg.evaluate("""()=>{ GOALS.hh=1; DIARY={}; DIARY['2026-10-05']={items:[{id:'t300',n:1,t:'t300',k:1,p:1,c:0.3}],water:0}; saveToday(); renderShop(); document.getElementById('estbox').open=true; }""")
    t=pg.inner_text("#estbox")
    ck("verfallener Rest wird genannt", "Nicht mehr haltbar übrig geblieben" in t and "Magerquark" in t, t[-300:].replace("\n"," | "))
    # laufender Monat: offene Packung noch nicht verfallen
    pg.evaluate("""()=>{ const d=todayISO(); DIARY={}; DIARY[d]={items:[{id:'t300',n:1,t:'t300',k:1,p:1,c:0.3}],water:0}; SPM=d.slice(0,7); saveToday(); renderShop(); document.getElementById('estbox').open=true; }""")
    t=pg.inner_text("#estbox")
    ck("heutige offene Packung gilt nicht als verfallen", "Es ist nichts Haltbares verfallen" in t, t[-200:].replace("\n"," | "))
    # Monatsnavigation
    pg.evaluate("""()=>{ DIARY={}; DIARY['2026-10-05']={items:[{id:'t300',n:1,t:'t300',k:1,p:1,c:0.3}],water:0}; SPM=todayISO().slice(0,7); saveToday(); renderShop(); }""")
    ck("aktueller Monat ohne Eintraege: Hinweis", "sobald Rezepte" in pg.inner_text("#spendcard"))
    pg.click('#spendcard [data-spm="-1"]'); pg.wait_for_timeout(300)
    ck("Vormonat zeigt Schaetzung", "Einkauf geschätzt, 1 Packung" in pg.inner_text("#spendcard"))
    # manuelle Einkaeufe funktionieren weiter
    pg.fill('#buy-a','38,40'); pg.click('[data-buyadd]'); pg.wait_for_timeout(300)
    ck("echter Einkauf eingetragen", pg.evaluate("GOALS.buys.length")==1 and "38,40" in pg.inner_text("#spendcard"))
    ck("Block Tatsaechliche Einkaeufe", "Tatsächliche Einkäufe" in pg.inner_text("#spendcard"))
    # Wochenrueckblick
    pg.evaluate("""()=>{ GOALS.buys=[]; REVW='2026-10-05'; saveToday(); showTab('fortschritt'); renderCharts(); }""")
    pg.wait_for_timeout(300)
    t=pg.inner_text("#panel-fortschritt")
    ck("Wochenrueckblick zeigt Schaetzung", "Einkauf geschätzt" in t, t[t.find("Ausgaben"):t.find("Ausgaben")+120].replace("\n"," "))
    # Hygiene: kaputte Daten
    pg.evaluate("localStorage.setItem('fc_goals', JSON.stringify({hh:'x'}))"); pg.reload(); pg.wait_for_timeout(600)
    ck("hh Typ falsch -> 2", pg.evaluate("GOALS.hh")==2)
    pg.evaluate("localStorage.setItem('fc_goals', JSON.stringify({hh:9}))"); pg.reload(); pg.wait_for_timeout(600)
    ck("hh ausser Bereich -> 2", pg.evaluate("GOALS.hh")==2)
    pg.evaluate("localStorage.setItem('fc_diary', JSON.stringify({'2026-10-05':{items:[{id:'gibtsnicht',t:'x',k:1,p:1,c:2},{id:null,c:'a'},5,null]},'kaputt':1}))"); pg.reload(); pg.wait_for_timeout(600)
    pg.evaluate("showTab('einkauf'); renderShop()")
    ck("kaputtes Tagebuch bricht nichts", pg.evaluate("!!document.querySelector('#spendcard')"))
    # eatRecipe speichert n
    pg.evaluate("""()=>{ DIARY={}; logEat(RECIPES[0], 3); }""")
    ck("logEat speichert n", pg.evaluate("Object.values(DIARY).some(d=>d.items.some(i=>i.n===3))"))
    pg.evaluate("showTab('einkauf'); renderShop()")
    ck("kein Ueberlauf 390px", pg.evaluate("document.documentElement.scrollWidth")<=390)
    ck("Knoepfe gross genug", pg.evaluate("[...document.querySelectorAll('#spendcard button')].filter(e=>e.offsetParent).every(e=>e.getBoundingClientRect().height>=30)"), pg.evaluate("[...document.querySelectorAll('#spendcard button')].filter(e=>e.offsetParent&&e.getBoundingClientRect().height<30).map(e=>e.textContent+':'+e.getBoundingClientRect().height)"))
    ck("keine JS-Fehler", not errs, errs[:3])
    b.close()
print("FAILS:",fails)
