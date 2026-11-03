from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h,name in [(390,844,"mob"),(1300,900,"desk")]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=w<500); pg=c.new_page()
        pg.on("pageerror",lambda e:errs.append(name+": "+str(e))); pg.on("console",lambda m: errs.append(name+": "+m.text) if m.type=="error" else None)
        pg.goto(URL); pg.wait_for_timeout(600)
        ids=pg.evaluate("['mic','micfab','cmd','heard','s-hands','l-hands','miclabel'].filter(i=>document.getElementById(i))")
        ck(f"{name}: keine Mikrofon-/Befehlselemente", ids==[], ids)
        names=pg.evaluate("['SR','handle','setMic','toggleMic','runCmd','setupRec','voiceFilters','parseCount','radVoice','dictation','listening'].filter(n=>{try{return typeof eval(n)!=='undefined'}catch(e){return false}})")
        ck(f"{name}: keine Sprach-Funktionen mehr", names==[], names)
        txt=pg.evaluate("document.body.innerText.toLowerCase()")
        ck(f"{name}: kein Text zu Sprachbefehlen", not any(k in txt for k in ["sprachbefehl","diktat","mikrofon","dauerhaft zuhören"]))
        pg.evaluate("document.getElementById('dlg-settings').showModal()"); pg.wait_for_timeout(200)
        st=pg.inner_text("#dlg-settings").lower()
        ck(f"{name}: Einstellungen ohne Befehlsliste", not any(k in st for k in ["sprachbefehle","„start“","diktat","mikrofon","zuhören"]) and "ansagen im training sprechen" in st)
        pg.evaluate("document.getElementById('dlg-settings').close()")
        for t in ["heute","uebungen","tipps","rezepte","rad","vorkochen","einkauf","ernaehrung","fortschritt"]:
            pg.evaluate(f"showTab('{t}')"); pg.wait_for_timeout(120)
        ck(f"{name}: alle Tabs ohne Fehler", not errs, errs[:2])
        ck(f"{name}: kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth"))
        # Training laeuft per Knopf, Ansagen (Text) bleiben
        pg.evaluate("showTab('uebungen')"); pg.click('[data-act="start"]'); pg.wait_for_timeout(200)
        pg.evaluate("act('next')"); pg.wait_for_timeout(300)
        ck(f"{name}: Training per Knopf/act", pg.evaluate("W.phase")=="work", pg.evaluate("W.phase"))
        cap=pg.inner_text("#caption"); ck(f"{name}: Ansagetext sichtbar", len(cap)>10 and "Sag " not in cap, cap[:90])
        ck(f"{name}: Fertig-Knopf", pg.evaluate("!!document.querySelector('#actions [data-act=\"done\"]')"))
        pg.evaluate("stopWorkout()")
        # Rezept ausblenden zeigt Hinweiszeile
        pg.evaluate("showTab('rezepte'); openRecipe(RECIPES[2].id)"); pg.wait_for_timeout(400)
        pg.click('#dlg-recipe [data-hide]'); pg.wait_for_timeout(300)
        ck(f"{name}: Hinweiszeile beim Ausblenden", pg.evaluate("!document.getElementById('toast').hidden") and "ausgeblendet" in pg.inner_text("#toast"), pg.inner_text("#toast"))
        pg.evaluate("EXC.length=0; store.set('fc_exc',EXC); renderRecipes()")
        # alte Einstellung mit handsfree stoert nicht
        pg.evaluate("store.set('fc_settings',Object.assign({},settings,{handsfree:true}))"); pg.reload(); pg.wait_for_timeout(600)
        ck(f"{name}: alte handsfree-Einstellung harmlos", pg.evaluate("typeof settings.sets")=="number")
        pg.screenshot(path=__import__("fcenv").SHOTS + f"/v320_{name}.png")
        c.close()
    b.close()
print("Fehler:",errs); ck("keine Fehler", not errs); print("FAILS",fails)
