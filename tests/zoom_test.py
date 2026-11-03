from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True,is_mobile=True,device_scale_factor=2); pg=c.new_page(); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(600)
    print("Viewport-Meta:",pg.evaluate("document.querySelector('meta[name=viewport]').content"))
    print("touch-action body/button/div:",pg.evaluate("[document.body,document.querySelector('button'),document.querySelector('.card')].map(e=>getComputedStyle(e).touchAction)"))
    small=pg.evaluate("""()=>{const bad=[];document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=range]),select,textarea').forEach(e=>{const fs=parseFloat(getComputedStyle(e).fontSize); if(fs<16) bad.push([e.id||e.tagName,fs])});return bad}""")
    print("Eingabefelder unter 16 px (sichtbare Tabs durchgeblättert):",small)
    for t in ["rezepte","einkauf","vorkochen","ernaehrung","fortschritt","heute"]:
        pg.evaluate(f"showTab('{t}')"); pg.wait_for_timeout(150)
        bad=pg.evaluate("""()=>{const bad=[];document.querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=range]),select,textarea').forEach(e=>{const fs=parseFloat(getComputedStyle(e).fontSize); if(fs<16) bad.push([e.id||e.tagName,fs])});return bad}""")
        if bad: print("  ",t,bad)
    pg.evaluate("openSettings&&openSettings()") if False else None
    print("visualViewport scale:",pg.evaluate("window.visualViewport.scale"))
    print("Fehler:",errs)
    b.close()
