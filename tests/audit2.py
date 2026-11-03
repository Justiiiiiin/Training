import json
from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
KEYS=["fc_settings","fc_levels","fc_log","fc_sessions","fc_body","fc_shop","fc_exc","fc_rad","fc_radplans","fc_cart","fc_budget","fc_chk","fc_goals","fc_diary","fc_wk"]
BAD=['null','{','[]','{}','123','"x"','true','[1,2]','{"a":1}','[null]','{"sets":"abc","rest":-5,"hold":0}']
fails={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for k in KEYS:
        for v in BAD:
            c=b.new_context(viewport={"width":1360,"height":900})
            c.add_init_script("try{localStorage.setItem(%s,%s)}catch(e){}"%(json.dumps(k),json.dumps(v)))
            pg=c.new_page(); errs=[]
            pg.on("pageerror",lambda e:errs.append(str(e)))
            pg.goto(URL); pg.wait_for_timeout(250)
            for t in ["heute","uebungen","rezepte","rad","einkauf","ernaehrung","tipps","fortschritt"]:
                try: pg.evaluate("t=>showTab(t)",t)
                except Exception as e: errs.append("showTab "+t+": "+str(e)[:80])
            try: pg.evaluate("()=>{radRoll&&0}")
            except Exception as e: pass
            alive=pg.evaluate("document.querySelectorAll('.gbtn').length")
            if errs or not alive: fails.setdefault(k,{})[v]=(errs[:2],alive)
            c.close()
    b.close()
for k,v in fails.items():
    print(k)
    for val,e in v.items(): print("   ",val,"->",e)
print("done, failing keys:",len(fails))
