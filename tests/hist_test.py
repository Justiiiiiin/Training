from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500)
    pg.evaluate("""()=>{ DIARY['2026-10-30']={items:[{t:'Quark mit Erdbeeren',k:210,p:25,c:1.04,id:RECIPES[0].id},{t:'Reispfanne',k:600,p:40,c:2.1,det:['150 g Reis (Rohgewicht): 525 kcal, 10,5 g Eiweiß','200 g Hähnchenbrust: 212 kcal, 44 g Eiweiß']}],water:2}; saveToday(); }""")
    pg.evaluate("openEat()"); pg.wait_for_timeout(300)
    pg.fill("#calc-name0","Test"); pg.fill("#calc-in","200 g Hähnchen, 150 g Reis"); pg.click("[data-calcgo]"); pg.wait_for_timeout(200); pg.click("[data-calcadd]"); pg.wait_for_timeout(300)
    ck("det am Eintrag", pg.evaluate("dayGet().items.slice(-1)[0].det.length")>=2, pg.evaluate("JSON.stringify(dayGet().items.slice(-1)[0].det)"))
    pg.evaluate("document.getElementById('dlg-eat').close()")
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(300)
    t=pg.inner_text("#eathist"); print(t[:300].replace("\n"," | "))
    ck("Tagebuch zeigt Tage", "Essens-Tagebuch" in t and "30.10." in t)
    ck("Details sichtbar nach Aufklappen", pg.evaluate("(()=>{ const d=[...document.querySelectorAll('.hday')].find(x=>x.innerText.includes('30.10.')); d.open=true; return d.innerText.includes('150 g Reis'); })()"))
    ck("Rezept ansehen", pg.evaluate("!!document.querySelector('#eathist [data-recipe]')"))
    n=pg.evaluate("DIARY['2026-10-30'].items.length")
    pg.click('#eathist [data-hdel="2026-10-30:0"]'); pg.wait_for_timeout(200)
    ck("Loeschen", pg.evaluate("DIARY['2026-10-30'].items.length")==n-1)
    pg.evaluate("showTab('heute')"); pg.wait_for_timeout(200); pg.click("[data-histgo]"); pg.wait_for_timeout(400)
    ck("Link von Heute", pg.evaluate("CUR")=="fortschritt")
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth"))
    pg.screenshot(path="shots/hist.png")
    ck("keine Fehler", not errs, str(errs[:3])); print("FAILS",fails); b.close()
