from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
def run(pg,t):
    return pg.evaluate("(t)=>{ const r=cParse(t); CALC.rows=r; const T=cTotals(); return {rows:r.map(x=>[x.kind,x.name,x.g||x.qty,Math.round(x.k||0),Math.round((x.p||0)*10)/10,x.note||'']), k:Math.round(T.k), p:Math.round(T.p*10)/10, open:T.open}; }",t)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(); pg.on("pageerror",lambda e:errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(500)
    def g(t): r=run(pg,t); return r["rows"][0][2], r["k"], r["p"], r["rows"][0][5], r
    cases=[("2 Eier",102),("2 gekochte Eier",102),("1 hartgekochtes Ei",51),("3 Eier Größe L",180),("2 Eier Gr. M",102),("2 XL Eier",138),("3 Eier (M)",153),("1 kleines Ei",43),("2 Eier Größe S",86),("ein großes Ei",60),("60 g Ei",60),("2 Eier Größe XL",138),("Eier",51)]
    for t,w in cases:
        gw,k,pr,note,_=g(t); ck(f"{t!r}: {w} g", gw==w, f"{gw} g, {k} kcal, {pr} g Eiweiß {note}")
    gw,k,pr,note,_=g("3 Eier Größe L"); ck("3 L-Eier etwa 257 kcal", 250<=k<=265 and 22<=pr<=23.5, (k,pr))
    gw,k,pr,note,_=g("2 Eigelb"); ck("2 Eigelb: 34 g, ca. 109 kcal", gw==34 and 105<=k<=112, (gw,k,pr))
    gw,k,pr,note,_=g("3 Eiweiß"); ck("3 Eiweiß: 99 g, ca. 51 kcal, 10,8 g", gw==99 and 49<=k<=53 and 10<=pr<=11.5, (gw,k,pr))
    gw,k,pr,note,r=g("2 Eiklar"); ck("Eiklar erkannt", r["rows"][0][0]=="food" and gw==66, r["rows"][0])
    r=run(pg,"1 Eiweißriegel"); ck("Eiweissriegel ist kein Eiklar", "Eiweiß (vom Ei)" not in str(r["rows"]), r["rows"])
    r=run(pg,"1 Eiweißbrot"); ck("Eiweissbrot ist kein Eiklar", "Eiweiß (vom Ei)" not in str(r["rows"]), r["rows"])
    r=run(pg,"2 Eier und 2 Scheiben Vollkornbrot mit Käse"); ck("Mischung weiter erkannt", r["open"]==0 and len(r["rows"])==3)
    r=run(pg,"2 Eier, 1 l Milch"); ck("1 l Milch wird nicht zur Eigroesse", r["rows"][0][2]==102 and "Milch" in r["rows"][1][1], r["rows"])
    # Rezepte: 3 Eier im Rührei
    rr=pg.evaluate("RECIPES.find(x=>x.id==='ruehrei-mit-paprika-und-brot')"); print("  Ruehrei mit Paprika und Brot:",rr["kcal"],"kcal",rr["protein"],"g")
    ck("Rezeptwerte aus neuer Eitabelle (Ei M)", 500<=rr["kcal"]<=545 and 27<=rr["protein"]<=30, (rr["kcal"],rr["protein"]))
    ck("Ei in der Preisliste: 51 g (M) je Ei, 2,99 fuer 10", pg.evaluate("PRICE.ei.per")==51 and pg.evaluate("PRICE.ei.pack")==510 and abs(pg.evaluate("RECIPES.find(x=>x.id==='hartgekochte-eier').cost")-0.6)<0.01)
    ck("1000 Rezepte, Kosten wie Bauplan", pg.evaluate("RECIPES.length")==1000)
    print("Fehler:",errs); ck("keine Fehler", not errs)
    b.close()
print("FAILS",fails)
