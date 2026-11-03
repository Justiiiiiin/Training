from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(500); pg.evaluate("showTab('heute')"); pg.wait_for_timeout(300)
    def slots(): return pg.evaluate("[...document.querySelectorAll('.pslot')].map(e=>e.querySelector('.pl-when').textContent+' | '+e.querySelector('.pl-title').textContent)")
    print(slots())
    pg.evaluate("scrollTo(0,document.body.scrollHeight)"); pg.screenshot(path="shots/plan_mob.png",full_page=True)
    # Statistik der Plaene
    st=pg.evaluate("""()=>{const out={};for(const pause of ['small','meal']){GOALS.pause=pause;let P=0,K=0,C=0,n=200,four=0,kinds={};for(let i=0;i<n;i++){const ids=makeDayPlan(false);const r=ids.map(byId);if(ids.length===4)four++;P+=r.reduce((a,x)=>a+x.protein,0);K+=r.reduce((a,x)=>a+x.kcal,0);C+=r.reduce((a,x)=>a+x.cost,0);r.slice(0,3).forEach((x,k)=>{const key=k+':'+x.meal;kinds[key]=(kinds[key]||0)+1})}out[pause]={p:Math.round(P/n),k:Math.round(K/n),c:Math.round(C/n*100)/100,four,kinds}}GOALS.pause='small';return out}""")
    print(st)
    # Eintragen
    if not pg.evaluate("document.getElementById('plancol').open"): pg.click('#plancol > summary'); pg.wait_for_timeout(200)
    ck_open=pg.evaluate("PLANOPEN")
    pg.click('[data-plan="0"]'); pg.wait_for_timeout(200); print('Plan bleibt offen:',pg.evaluate("document.getElementById('plancol').open"),ck_open)
    print("nach Eintragen 0:",pg.evaluate("dayGet().items.map(x=>x.t)"),pg.evaluate("dayGet().plan.done"))
    pg.click('[data-planre="1"]'); pg.wait_for_timeout(200); print("slot1 neu:",slots()[1])
    pg.click('[data-planall="all"]'); pg.wait_for_timeout(200); print("alles:",pg.evaluate("dayGet().items.length"),pg.evaluate("dayGet().plan.done"))
    # Loeschen setzt Slot zurueck
    pg.evaluate("document.querySelector('[data-eatdel=\"0\"]').click()"); pg.wait_for_timeout(200); print("nach Loeschen done:",pg.evaluate("dayGet().plan.done"))
    # Toggles
    pg.click("#plan-small"); pg.wait_for_timeout(200); print("Pause=",pg.evaluate("GOALS.pause"),slots()[1])
    pg.click('[data-shift="f"]'); pg.wait_for_timeout(200); print("frei:",slots())
    pg.click('[data-planall="new"]'); pg.wait_for_timeout(200); print("neu:",slots())
    # Ausschluesse
    pg.evaluate("EXC=['Ei','Geflügel','Rindfleisch','Schwein','Hülsenfrüchte','Nüsse']; planNew(); renderToday()"); pg.wait_for_timeout(200); print("alles ausgeschlossen:",slots())
    # kaputte Plan-Daten
    pg.evaluate("dayEns().plan={ids:['gibtsnicht'],done:[false]}; renderToday()"); pg.wait_for_timeout(200); print("kaputt repariert:",len(slots()))
    # Persistenz
    pg.evaluate("EXC=[]; planNew()"); s1=slots(); pg.reload(); pg.wait_for_timeout(600); print("bleibt nach Reload:",s1==slots())
    pg.close(); b.close()
print("ERRORS",errs[:6])
