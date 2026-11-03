from playwright.sync_api import sync_playwright
import json
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
def openplan(pg):
    pg.evaluate("showTab('heute')"); pg.wait_for_timeout(250); pg.evaluate("PLANOPEN=true; document.getElementById('plancol').open=true"); pg.wait_for_timeout(100)
def labs(pg): return pg.evaluate("[...document.querySelectorAll('.pl-when')].map(e=>e.textContent)")
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600); openplan(pg)
    ck("Standard Sonntag frei, sonst frueh", pg.evaluate("shGet(weekStartISO(todayISO()))")=="nnnnnnf", pg.evaluate("shGet(weekStartISO(todayISO()))"))
    ck("Segment Schicht heute da", pg.evaluate("document.querySelectorAll('[data-shift]').length")==3)
    ck("Hinweiszeile da", "Heute" in pg.inner_text(".shifthint"), pg.inner_text(".shifthint"))
    pg.evaluate("shSet(todayISO(),'n'); shAfter()"); pg.wait_for_timeout(200)
    lab=labs(pg); print("  frueh:",lab)
    # Spaet
    pg.click('[data-shift="l"]'); pg.wait_for_timeout(300)
    lab=labs(pg); ck("Spaet: 3 Slots, Labels", len(lab)==3 and lab[2].startswith("Nach der Arbeit"), lab)
    ck("Spaet gespeichert", pg.evaluate("shiftOf(todayISO())")=="l" and pg.evaluate("dayEns().plan.late")==True)
    ck("Spaet markiert (aria-pressed)", pg.get_attribute('[data-shift="l"]','aria-pressed')=="true")
    ck("Hinweis Spaetschicht", "vormittags" in pg.inner_text(".shifthint"), pg.inner_text(".shifthint"))
    res=pg.evaluate("""()=>{const o={bad:0,len:{},prot:[]};for(let i=0;i<200;i++){const ids=makeDayPlan(false);o.len[ids.length]=(o.len[ids.length]||0)+1;const R=ids.map(byId);
      if(R[0].meal!=='Mittag/Abend'||R[0].time>35||R[0].protein<35||R[1].ing.some(x=>PLAN_HARD.includes(x[4]))||R[2].time>20) o.bad++; o.prot.push(R.reduce((a,r)=>a+r.protein,0));}
      o.avg=Math.round(o.prot.reduce((a,b)=>a+b,0)/o.prot.length); delete o.prot; o.target=protGoal(); return o}""")
    ck("Spaet-Plaene im Rahmen (200)", res["bad"]==0 and res["len"]=={"3":200}, res)
    # Frei
    pg.click('[data-shift="f"]'); pg.wait_for_timeout(300)
    lab=labs(pg); ck("Frei: Labels Fruehstueck", lab[0]=="Frühstück" and pg.evaluate("dayEns().plan.free")==True, lab)
    # Frueh
    pg.click('[data-shift="n"]'); pg.wait_for_timeout(300)
    lab=labs(pg); ck("Frueh: normale Labels", lab[0]=="Vor der Arbeit" and pg.evaluate("dayEns().plan.late")==False, lab)
    # Dialog
    pg.click('[data-shiftedit]'); pg.wait_for_timeout(500)
    ck("Dialog offen, 14 Tageszeilen", pg.evaluate("document.getElementById('dlg-shift').open") and pg.evaluate("document.querySelectorAll('#dlg-shift .shrow').length")==14)
    pg.click('#dlg-shift [data-shwk]:nth-of-type(2)'); pg.wait_for_timeout(300)
    ws=pg.evaluate("weekStartISO(todayISO())"); ck("Mo bis Sa spaet", pg.evaluate("GOALS.sched[weekStartISO(todayISO())]")=="llllllf", pg.evaluate("GOALS.sched[weekStartISO(todayISO())]"))
    ck("Heutiger Plan folgt (Spaet)", pg.evaluate("shiftOf(todayISO())")=="l" or pg.evaluate("shIdx(todayISO())")==6)
    # Einzeltag: Dienstag der naechsten Woche frei
    nxt=pg.evaluate("shiftDay(weekStartISO(todayISO()),7)")
    pg.click(f'#dlg-shift [data-shd="{pg.evaluate("shiftDay(weekStartISO(todayISO()),8)")}:f"]'); pg.wait_for_timeout(200)
    ck("Naechste Woche: Di frei, Rest geerbt", pg.evaluate(f"shGet('{nxt}')")=="lfllllf", pg.evaluate(f"shGet('{nxt}')"))
    ck("Woche ohne Eintrag erbt (uebernaechste)", pg.evaluate(f"shGet(shiftDay('{nxt}',7))")=="lfllllf")
    pg.click('#dlg-shift .dlg-head [data-close]'); pg.wait_for_timeout(500)
    ck("Dialog zu", not pg.evaluate("document.getElementById('dlg-shift').open"))
    pg.reload(); pg.wait_for_timeout(700)
    ck("Reload: bleibt", pg.evaluate(f"shGet('{nxt}')")=="lfllllf")
    # Migration alt (v3.13: GOALS.shift)
    pg.evaluate("store.set('fc_goals',Object.assign({},GOALS,{shift:'late',sched:{}}))"); pg.reload(); pg.wait_for_timeout(700)
    ck("Migration shift=late -> diese Woche spaet", pg.evaluate("shGet(weekStartISO(todayISO()))")=="llllllf" and pg.evaluate("GOALS.shift")==None, pg.evaluate("shGet(weekStartISO(todayISO()))"))
    # kaputt
    pg.evaluate("store.set('fc_goals',Object.assign({},GOALS,{sched:{'x':'zzz','2026-11-02':'abc','2026-11-09':'lllllll', '2026-11-16':5}}))"); pg.reload(); pg.wait_for_timeout(700)
    ck("Kaputte Schichten bereinigt", pg.evaluate("Object.keys(GOALS.sched)")==["2026-11-09"], pg.evaluate("Object.keys(GOALS.sched)"))
    pg.evaluate("store.set('fc_goals','kaputt')"); pg.reload(); pg.wait_for_timeout(700)
    ck("Komplett kaputte Ziele: App startet", pg.evaluate("typeof shiftOf(todayISO())")=="string")
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth"))
    openplan(pg); pg.screenshot(path="shots/v314_plan.png")
    pg.evaluate("showTab('heute'); document.querySelector('[data-shiftedit]').click()"); pg.wait_for_timeout(500); pg.screenshot(path="shots/v314_shiftdlg.png")
    print("Fehler:",errs); ck("keine Fehler", not errs)
    b.close()
print("FAILS",fails)
