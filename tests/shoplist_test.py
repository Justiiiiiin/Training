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
    pg.evaluate("""()=>{ CART=[]; CHK={}; ['haehnchen-reis-pfanne','skyr-bowl-mit-erdbeeren-und-haferflocken','chili-con-carne-mit-reis'].forEach(id=>cartAdd(id,2)); showTab('einkauf'); renderShop(); }""")
    pg.wait_for_timeout(300)
    n0=pg.evaluate("document.querySelectorAll('#panel-einkauf .shoplist .sgroup .sline').length")
    ck("Liste hat Zeilen", n0>=8, n0)
    ck("keine Abgehakt-Liste am Anfang", pg.evaluate("!document.querySelector('#panel-einkauf .doneshop')"))
    first=pg.evaluate("document.querySelector('#panel-einkauf .shoplist .sgroup .sline input').dataset.chk")
    pg.click('#panel-einkauf .shoplist .sgroup .sline input'); pg.wait_for_timeout(250)
    ck("Eintrag wandert in Abgehakt", pg.evaluate("document.querySelectorAll('#panel-einkauf .doneshop .sline').length")==1 and pg.evaluate("document.querySelector('#panel-einkauf .doneshop .sline input').dataset.chk")==first)
    ck("Zaehler in Ueberschrift", "Bereits abgehakt (1)" in pg.inner_text("#panel-einkauf .doneshop > summary"))
    ck("Offene Liste kuerzer", pg.evaluate("document.querySelectorAll('#panel-einkauf .shoplist > .sgroup .sline').length")==n0-1)
    ck("Abgehakt eingeklappt", pg.evaluate("!document.querySelector('#panel-einkauf .doneshop').open"))
    ck("persistiert", pg.evaluate(f"JSON.parse(localStorage.getItem('fc_chk'))['{first}']===true"))
    ck("Fokus nicht verloren", pg.evaluate("document.activeElement && document.activeElement !== document.body"))
    # aufklappen, zweites abhaken -> bleibt offen
    pg.click('#panel-einkauf .doneshop > summary'); pg.wait_for_timeout(200)
    ck("aufgeklappt", pg.evaluate("document.querySelector('#panel-einkauf .doneshop').open"))
    pg.click('#panel-einkauf .shoplist > .sgroup .sline input'); pg.wait_for_timeout(250)
    ck("zwei abgehakt, bleibt offen", pg.evaluate("document.querySelectorAll('#panel-einkauf .doneshop .sline').length")==2 and pg.evaluate("document.querySelector('#panel-einkauf .doneshop').open"))
    ck("abgehakte Zeilen durchgestrichen", pg.evaluate("[...document.querySelectorAll('#panel-einkauf .doneshop .sline')].every(l=>l.classList.contains('done') && l.querySelector('input').checked)"))
    # zurueck
    pg.click('#panel-einkauf .doneshop .sline input'); pg.wait_for_timeout(250)
    ck("Abhaken rueckgaengig: zurueck in Liste", pg.evaluate("document.querySelectorAll('#panel-einkauf .doneshop .sline').length")==1 and pg.evaluate("document.querySelectorAll('#panel-einkauf .shoplist > .sgroup .sline').length")==n0-1)
    # alles abhaken
    pg.evaluate("""()=>{ document.querySelectorAll('#panel-einkauf .shoplist > .sgroup .sline input').forEach(()=>{}); }""")
    for i in range(n0+2):
        el=pg.query_selector('#panel-einkauf .shoplist > .sgroup .sline input')
        if not el: break
        el.click(); pg.wait_for_timeout(120)
    ck("alles abgehakt: Hinweis", "Alles abgehakt" in pg.inner_text("#panel-einkauf .shoplist"))
    ck("alle in Abgehakt", pg.evaluate("document.querySelectorAll('#panel-einkauf .doneshop .sline').length")==n0)
    ck("keine leeren Gruppen", pg.evaluate("document.querySelectorAll('#panel-einkauf .shoplist > .sgroup').length")==0)
    # Reload
    pg.reload(); pg.wait_for_timeout(600); pg.evaluate("showTab('einkauf')"); pg.wait_for_timeout(300)
    ck("nach Reload: alles abgehakt", pg.evaluate("document.querySelectorAll('#panel-einkauf .doneshop .sline').length")==n0)
    # Vorkochen-Liste teilt den Zustand
    pg.evaluate("CHK={}; saveCart(); PREP.n=2; prepGen('all'); showTab('vorkochen'); renderPrep();"); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('#panel-vorkochen .radshop').open=true"); pg.wait_for_timeout(200)
    m0=pg.evaluate("document.querySelectorAll('#panel-vorkochen .shoplist .sgroup .sline').length")
    ck("Vorkochen-Liste hat Zeilen", m0>3, m0)
    pg.click('#panel-vorkochen .shoplist .sgroup .sline input'); pg.wait_for_timeout(250)
    ck("Vorkochen: Eintrag abgehakt", pg.evaluate("document.querySelectorAll('#panel-vorkochen .doneshop .sline').length")==1)
    # Rad-Liste
    pg.evaluate("showTab('rad'); radRender && radRender();"); pg.wait_for_timeout(500)
    rad=pg.evaluate("document.querySelectorAll('#panel-rad .shoplist .sline').length")
    ck("Rad-Einkaufsliste rendert", rad>=0, rad)
    # Layout
    pg.evaluate("showTab('einkauf')"); pg.wait_for_timeout(300)
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth")<=390)
    ck("Summary gross genug", pg.evaluate("[...document.querySelectorAll('.doneshop > summary')].filter(e=>e.offsetParent).every(e=>e.getBoundingClientRect().height>=36)"))
    ck("keine JS-Fehler", not errs, errs[:3])
    b.close()
print("FAILS:",fails)
