from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,i=""):
    print(("OK   " if c else "FAIL ")+n,str(i)[:140]); 
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":390,"height":844}); pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500)
    pg.evaluate("""()=>{ DIARY['2026-10-31']={items:[{t:'Quark mit Erdbeeren',k:210,p:25,c:1},{t:'Reispfanne <b>',k:600,p:40,c:2,det:['a']}],water:0}; saveToday(); openEat(); }"""); pg.wait_for_timeout(300)
    ck("Chips da", pg.evaluate("document.querySelectorAll('[data-eatagain]').length")==2)
    ck("kein HTML in Chip", pg.evaluate("!document.querySelector('.recentrow b')"))
    n0=pg.evaluate("dayGet().items.length"); pg.click('[data-eatagain="0"]'); pg.wait_for_timeout(300)
    ck("nochmal eingetragen", pg.evaluate("dayGet().items.length")==n0+1 and pg.evaluate("dayGet().items.slice(-1)[0].k")>0, pg.evaluate("JSON.stringify(dayGet().items.slice(-1)[0])"))
    pg.evaluate("document.getElementById('dlg-eat').close()")
    ck("keine Fehler", not errs, errs[:2]); print("FAILS",fails); b.close()
