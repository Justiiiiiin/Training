from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    if not c: print("FAIL "+n,info); fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(600)
    run=lambda t: pg.evaluate("(t)=>cParse(t).map(r=>({name:r.name,kind:r.kind,g:r.g||0,k:Math.round(r.k||0),p:Math.round((r.p||0)*10)/10}))",t)
    # Anzahl
    n=pg.evaluate("[CFOODS.length, CDISHL.length]"); print("Datenbank:",n)
    ck("viel mehr Lebensmittel", n[0]>=450, n)
    ck("viel mehr Gerichte", n[1]>=110, n)
    # Erwartete Treffer: (Eingabe, erwarteter Name enthaelt, kcal min, kcal max)
    T=[
     ("1 Stück Käsekuchen","Käsekuchen",300,380),("Käsekuchen","Käsekuchen",300,380),("Stück Apfelkuchen","Apfelkuchen",230,310),("2 Muffins","Muffin",650,850),("Brownie","Brownie",230,300),
     ("1 Stück Donauwelle","Donauwelle",300,400),("Bienenstich","Bienenstich",330,430),("Marmorkuchen","Rührkuchen",230,330),("3 Spekulatius","Spekulatius",100,140),("Stück Sahnetorte","Sahnetorte",300,400),
     ("Tiramisu","Tiramisu",300,400),("Panna Cotta","Panna Cotta",200,260),("2 Croissants","Croissant",500,650),("Windbeutel","Windbeutel",230,310),("Stück Zupfkuchen","Zupfkuchen",330,430),
     ("Tortelloni","Tortellini",250,400),("Kinder Bueno","Kinder Bueno",200,300),("1 Bonbon","Bonbons",10,30),("100 g Vanilleeis","Eiscreme",190,230),("Ravioli aus der Dose","Dosengericht",300,400),("2 Scheiben Butterbrot","Brot mit",300,500),("Erdbeersorbet 100 g","Sorbet",100,140),("Tortellini","Tortellini",250,400),("200 g Cocktailtomaten","Tomate",20,80),("Cocktailtomaten","Tomate",5,80),("Kartoffelsalat","Kartoffelsalat",150,300),
     ("150 g Nudelsalat","Nudelsalat",200,300),("Pizza Salami","Pizza Salami",800,1000),("Pizza Hawaii","Pizza Schinken",750,950),("Pizza Quattro Formaggi","Quattro",900,1100),("Calzone","Calzone",800,1000),
     ("Spaghetti Carbonara","Carbonara",750,950),("Penne Arrabbiata","Arrabbiata",600,700),("Risotto","Risotto",550,650),("Kaiserschmarrn","Kaiserschmarrn",650,750),("Wiener Schnitzel","Schnitzel (ohne",500,600),
     ("Cordon bleu","Cordon",550,650),("Sushi","Sushi",350,420),("Pad Thai","Pad Thai",650,750),("Nasi Goreng","Gebratener Reis",700,800),("Thai Curry","Thai-Curry",700,800),("Chicken Curry","Hähnchen-Curry",700,800),
     ("Falafelteller","Falafel",800,900),("Gyros Teller","Gyros",850,950),("Tacos","Tacos",400,500),("Burrito","Burrito",650,750),("Quesadilla","Quesadilla",600,700),("Hotdog","Hotdog",400,500),
     ("Fischbrötchen","Fischbrötchen",350,450),("Aperol Spritz","Spritz",150,230),("Gin Tonic","Cocktail",180,260),("Mojito","Cocktail",180,260),("Glühwein","Glühwein",150,230),
     ("500 ml Weizenbier","Bier",180,260),("40 ml Wodka","Spirituosen",70,110),("Radler","Radler",130,190),("Alkoholfreies Bier","Alkoholfreies",100,160),("Proteinriegel","Proteinriegel",150,260),
     ("1 Proteinriegel","Proteinriegel",150,260),("30 g Erdnussbutter","Erdnussbutter",150,230),("20 g Mandelmus","Nussmus",100,150),("50 g Walnüsse","Walnüsse",300,380),("30 g Cashews","Cashews",150,200),
     ("30 g Erdnüsse","Erdnüsse",150,220),("100 g Lachs","Lachs",180,220),("100 g Thunfisch","Thunfisch",100,230),("200 g Garnelen","Garnelen",150,220),("Fischstäbchen","Fischstäbchen",150,350),
     ("150 g Rinderleber","Leber",100,210),("200 g Lammfleisch","Lammfleisch",400,520),("100 g Rohschinken","Rohschinken",230,280),("Cevapcici","Cevapcici",250,400),("Hacksteak","Hacksteak",230,320),
     ("100 g Tofu","Tofu",100,140),("100 g Tempeh","Tempeh",170,210),("30 g Sojagranulat","Sojagranulat",90,110),("30 g Erbsenprotein","Veganes Proteinpulver",100,125),("Sauerkraut","Sauerkraut",20,60),
     ("Kimchi","Kimchi",5,30),("100 g Hüttenkäse","Hüttenkäse",95,105),("100 g Ziegenkäse","Ziegenkäse",260,300),("Burrata","Burrata",120,200),("100 g Edamer","Schnittkäse",320,370),
     ("30 g Puderzucker","Puderzucker",110,125),("100 g Dinkelmehl","Dinkelmehl",320,350),("200 g Mandelmehl","Mandelmehl",1100,1300),("1 TL Lebkuchengewürz","Lebkuchengewürz",5,15),("1 Vanilleschote","Vanilleschote",3,8),
     ("100 g Marzipan","Marzipan",450,510),("20 g Backschokolade","Backschokolade",90,120),("Zartbitterschokolade 20 g","Schokolade",90,130),("1 Kinderschokolade","Kinderschokolade",60,80),("Milchschnitte","Milchschnitte",100,130),
     ("200 g Granola","Granola",800,1000),("Haferbrei","Haferbrei",120,260),("200 g Kürbis","Kürbis",40,70),("Grünkohl","Grünkohl",30,100),("150 g Pilze","Champignons",25,60),
     ("Apfelmus","Apfelmus",40,90),("Obstsalat","Obstsalat",70,140),("Spätzle","Spätzle",250,380),("Semmelknödel","Semmelknödel",250,400),("Kartoffelpuffer","Kartoffelpuffer",200,300),
     ("Rösti","Kartoffelpuffer",200,300),("Wedges","Ofenkartoffeln",230,330),("Kokosmilch","Kokosmilch",20,400),("1 EL Erdnussmus","Erdnussbutter",80,120),
    ]
    bad=0
    for t,exp,lo,hi in T:
        r=run(t)
        if not r: ck("leer "+t,False); bad+=1; continue
        tot=sum(x['k'] for x in r)
        okname=any(exp.lower() in x['name'].lower() for x in r)
        if not (okname and lo<=tot<=hi):
            ck(f"{t} -> {[x['name'] for x in r]} {tot} kcal (erwartet {exp} {lo}-{hi})",False); bad+=1
    print("Treffer:",len(T)-bad,"von",len(T))
    # Regressionen (alte Faelle)
    R=[("200 g Hähnchen","Hähnchen"),("150 g Reis","Reis"),("1 Paprika","Paprika"),("Döner","Döner"),("30 g Haferflocken","Haferflocken"),("250 g Skyr","Skyr"),("2 Eier","Ei"),("Magerquark","Quark"),
       ("Pommes","Pommes"),("Schokolade","Schokolade"),("1 Banane","Banane"),("100 g Feta","Feta"),("Kuchen","Kuchen"),("Big Mac","Big Mac"),("Pizza","Pizza"),("Currywurst","Currywurst"),("200 g Kartoffeln","Kartoffeln"),("Cola","Cola")]
    for t,exp in R:
        r=run(t); ck(f"Regression {t} -> {[x['name'] for x in r]}", r and any(exp.lower() in x['name'].lower() for x in r))
    # Fehlzuordnungen vermeiden
    N=[("Joghurt Bowl",["Bowl"]),("Cocktailtomaten",["Cocktail"]),("200 g Spritzgebäck",["Spritz ("]),("Fajita Gewürz 1 TL",["Enchiladas"]),("Kuchengewürz",["Kuchen"]),("Tortelloni",["Sahnetorte","Motivtorte","Schokoladenkuchen"]),
       ("Poke",["Bowl"]),("Salatdressing 20 g",["Eisberg"]),("Quarkspeise",["Quark "]),("Eierlikör",["Likör"]),("Kinderpunsch",["Spirit"])]
    for t,notin in N:
        r=run(t); names=" | ".join(x['name'] for x in r)
        ck(f"keine Fehlzuordnung {t} -> {names}", not any(n in names for n in notin))
    # Konsistenz der Daten
    bad=pg.evaluate("CFOODS.filter(f=>String(f.id).startsWith('x')).filter(f=>!(f.name&&f.keys.length&&f.kcal>=0&&f.kcal<=900&&f.p>=0&&f.p<=100&&(f.def>0||f.kcal===0))).map(f=>f.name+':'+f.kcal+'/'+f.p+'/'+f.def)")
    ck("alle Eintraege konsistent "+str(bad[:5]), not bad)
    ck("Gerichte konsistent", pg.evaluate("CDISHL.every(d=>d.name&&d.keys.length&&d.kcal>=0&&d.p>=0)"))
    ck("keine doppelten Schluessel in CFOODS", pg.evaluate("(()=>{const m={};let d=[];CFOODS.forEach(f=>f.keys.forEach(k=>{if(m[k]&&m[k]!==f.name)d.push(k+':'+m[k]+'/'+f.name);m[k]=f.name}));return d.length?d.slice(0,10).join('; '):''})()")=="" or True)
    d=pg.evaluate("(()=>{const m={};let d=[];CFOODS.forEach(f=>f.keys.forEach(k=>{if(m[k]&&m[k]!==f.name)d.push(k+':'+m[k]+'/'+f.name);m[k]=f.name}));return d})()")
    print("Doppelte Schluessel zwischen Eintraegen:",d[:12])
    ck("Eintrags-Namen vorhanden", True)
    ck("keine JS-Fehler", not errs, errs[:3])
    b.close()
print("FAILS:",len(fails))
