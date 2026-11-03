from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
def run(pg,t):
    return pg.evaluate("(t)=>{ const r=cParse(t); CALC.rows=r; const T=cTotals(); return {rows:r.map(x=>[x.kind,x.name,x.g||x.qty,Math.round(x.k||0)]), k:Math.round(T.k), p:Math.round(T.p*10)/10, c:T.c, open:T.open}; }",t)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500)
    r=run(pg,"200 g Hähnchen, 150 g Reis, 1 Paprika"); print(r)
    ck("Haehnchen+Reis+Paprika", abs(r["k"]-779)<8 and abs(r["p"]-56)<2, str(r["k"]))
    r=run(pg,"2 Eier und 2 Scheiben Vollkornbrot mit Käse"); print(r); ck("Eier+Brot+Kaese erkannt", r["open"]==0 and len(r["rows"])==3)
    r=run(pg,"Döner"); print(r); ck("Doener", r["k"]==750 and r["rows"][0][0]=="dish")
    r=run(pg,"2 Döner"); ck("2 Doener", r["k"]==1500, str(r))
    r=run(pg,"200 g gekochter Reis"); print(r); ck("gekocht", 250<r["k"]<270, str(r["k"]))
    r=run(pg,"1,5 kg Kartoffeln"); print(r); ck("Dezimal kg", r["rows"][0][1]=="Kartoffeln" and r["rows"][0][2]==1500, str(r))
    r=run(pg,"3 EL Olivenöl, 1 TL Honig"); print(r); ck("EL/TL", r["open"]==0 and r["rows"][0][3]>300, str(r))
    r=run(pg,"Zauberpilz 100 g"); print(r); ck("unbekannt", r["open"]==1)
    r=run(pg,"Spaghetti mit Hackfleisch und Tomatensauce"); print(r); ck("Spaghetti Hack Sauce", r["open"]==0 and len(r["rows"])==3, str(r["rows"]))
    r=run(pg,"250g Skyr, 1 Banane, 30g Haferflocken"); print(r); ck("Skyr-Bowl", r["open"]==0 and 340<r["k"]<380, str(r["k"]))
    r=run(pg,"½ Paprika"); ck("Halb", r["rows"][0][2]==75, str(r))
    r=run(pg,"100 g Feta, 1 Kiwi, 2 Bratwurst, 200 g Linzensuppe"); print(r); ck("neue Lebensmittel + Tippfehler", r["open"]==0, str(r["rows"]))
    r=run(pg,"Qwertzuiop Blorp"); ck("Unbekanntes -> Kategorien", r["open"]==1)
    # UI-Ablauf
    pg.evaluate("openEat()"); pg.wait_for_timeout(400)
    pg.fill("#calc-in","200 g Hähnchen, 150 g Reis, Zauberpilz 100 g"); pg.click("[data-calcgo]"); pg.wait_for_timeout(300)
    ck("Kategorie-Knoepfe", pg.evaluate("document.querySelectorAll('[data-calccat]').length")==8)
    pg.click('[data-calccat][data-c="Gemüse"]'); pg.wait_for_timeout(300)
    ck("Gemuese gerechnet", "grob geschätzt" in pg.inner_text(".calcrows") and "ohne" not in pg.inner_text(".calctot"), pg.inner_text(".calctot")[:90])
    pg.fill("#calc-srv","2"); pg.fill("#calc-name","Test-Pfanne")
    pg.click("[data-calcadd]"); pg.wait_for_timeout(300)
    ck("Tagebuch-Eintrag", pg.evaluate("dayGet().items.some(x=>x.t.startsWith('Test-Pfanne (1 von 2)'))"), pg.evaluate("JSON.stringify(dayGet().items.slice(-1))"))
    ck("kein Claude-Knopf", pg.evaluate("!document.querySelector('[data-calcai]')"))
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"))
    pg.fill("#calc-in","Pizza"); pg.click("[data-calcgo]"); pg.wait_for_timeout(300); pg.screenshot(path=__import__("fcenv").SHOTS + "/calc.png")
    ck("keine Fehler", not errs, str(errs[:3])); print("FAILS",fails); b.close()
