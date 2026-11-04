# -*- coding: utf-8 -*-
"""Mittag/Abend-Familien: aus Fleisch, Beilage, Gemüse und Würzung entstehen eigene Rezepte (alle selbst formuliert)."""
from gen_core import *


# Rohes Gemüse (Zutaten, Schnitt-Schritt) und Dressings/Dips (Name, Zutaten, Schritt), mehrfach verwendet
V = [
    (dict(gurke=100, tom=1, eisb=40), "Gurke und Tomate in Würfel schneiden, den Eisbergsalat in Streifen schneiden."),
    (dict(pap=1, gurke=100, ruc=20), "Paprika und Gurke in Würfel schneiden, den Rucola grob zupfen."),
    (dict(tom=2, ruc=30, sgurke=2), "Tomaten in Spalten schneiden, Saure Gurken würfeln und den Rucola grob zupfen."),
    (dict(eisb=80, tom=1, pap=0.5), "Eisbergsalat in Streifen schneiden, Tomate und Paprika würfeln."),
    (dict(gurke=150, pap=1, zwie=0.5), "Gurke und Paprika würfeln, die Zwiebel in feine Ringe schneiden."),
]
D = [
    ("Joghurt-Kräuter", dict(jogGr=50, zitrone=1, T="Kräuter, Salz und Pfeffer"), "Joghurt mit Zitronensaft, Kräutern, Salz und Pfeffer verrühren."),
    ("Senf-Zitronen", dict(senf=1, zitrone=1, oel=1, T="Salz und Pfeffer"), "Senf, Zitronensaft, Öl, 1 EL Wasser, Salz und Pfeffer verrühren."),
    ("Honig-Senf", dict(senf=1, honig=1, zitrone=1, oel=1, T="Salz und Pfeffer"), "Senf, Honig, Zitronensaft, Öl, 1 EL Wasser, Salz und Pfeffer verrühren."),
    ("Curry-Joghurt", dict(curry=1, jogGr=50, zitrone=0.5, T="Salz"), "Joghurt mit Curry, Zitronensaft und Salz verrühren."),
    ("Kreuzkümmel-Quark", dict(kreuz=0.5, quark=60, zitrone=1, T="Salz"), "Quark mit Kreuzkümmel, Zitronensaft, Salz und einem Schuss Wasser glatt rühren."),
    ("Gurken-Quark", dict(sgurke=1, speisequark=60, T="Pfeffer"), "Die Saure Gurke fein würfeln und mit dem Quark und etwas Pfeffer verrühren."),
    ("Paprika-Joghurt", dict(paprikap=1, jogGr=50, zitrone=1, T="Salz"), "Joghurt mit Paprikapulver, Zitronensaft und Salz verrühren."),
    ("Tzatziki", dict(jog35=80, knob=0.5, zitrone=0.5, T="Dill, Salz und Pfeffer"), "Knoblauch pressen und mit Joghurt, Zitronensaft, Dill, Salz und Pfeffer verrühren."),
    ("Parmesan-Joghurt", dict(parm=10, jogGr=50, zitrone=1, senf=0.5), "Parmesan fein reiben und mit Joghurt, Zitronensaft und Senf verrühren."),
    ("Kräuter-Quark", dict(quark=60, zitrone=1, T="Schnittlauch, Salz und Pfeffer"), "Quark mit Zitronensaft, Schnittlauch, Salz, Pfeffer und einem Schuss Wasser glatt rühren."),
    ("Knoblauch-Joghurt", dict(jogGr=50, knob=0.5, zitrone=1, T="Salz und Pfeffer"), "Knoblauch pressen und mit Joghurt, Zitronensaft, Salz und Pfeffer verrühren."),
]


def pfannen():
    """Eine Pfanne, ein Fleisch (oder Hack), eine Soße, eine Beilage."""
    P = [
        dict(n="Curry-Kokos", base=dict(zwie=1, pap=1, knob=1, curry=2, kokos=100, zitrone=1, T="Salz und Pfeffer"),
             prep="Zwiebel und Paprika in Stücke schneiden, Knoblauch fein hacken.",
             cook="Zwiebel, Paprika, Knoblauch und Curry zum Fleisch geben und 3 Minuten mitbraten. Kokosmilch zugießen, 5 Minuten köcheln lassen und mit Zitronensaft, Salz und Pfeffer abschmecken.",
             meats=["haehn", "pute", "schnitzel", "phack", "haehnst"], carbs=["reis"]),
        dict(n="Paprika-Tomaten", base=dict(zwie=1, pap=2, knob=1, stueck=150, paprikap=2, T="Salz und Pfeffer"),
             prep="Zwiebel und Paprika in Stücke schneiden, Knoblauch fein hacken.",
             cook="Zwiebel, Paprika, Knoblauch und Paprikapulver zum Fleisch geben und 4 Minuten mitbraten. Stückige Tomaten zugeben und 8 Minuten köcheln lassen, bis die Soße etwas eingedickt ist. Mit Salz und Pfeffer abschmecken.",
             meats=["haehn", "pute", "schnitzel", "rhack", "ghack", "phack"], carbs=["reis", "nudel"]),
        dict(n="Orient", base=dict(tom=2, pap=1, zwie=1, kreuz=1, paprikap=1, jogGr=40, T="Salz, Pfeffer und Petersilie"),
             prep="Tomaten, Paprika und Zwiebel in Stücke schneiden.",
             cook="Zwiebel und Paprika mit Kreuzkümmel und Paprikapulver zum Fleisch geben und 4 Minuten mitbraten. Tomaten zugeben, 5 Minuten schmoren und mit Salz und Pfeffer abschmecken.",
             serve="Mit je einem Klecks Joghurt und etwas Petersilie servieren.",
             meats=["haehn", "pute", "rhack", "phack", "ghack"], carbs=["reis"]),
        dict(n="Honig-Senf", base=dict(pap=2, zwie=1, knob=1, senf=1.5, honig=1, bruehe=100, T="Salz und Pfeffer"),
             prep="Paprika und Zwiebel in Streifen schneiden, Knoblauch fein hacken.",
             cook="Paprika, Zwiebel und Knoblauch zum Fleisch geben und 4 Minuten mitbraten. Senf, Honig und Brühe zugeben und 3 Minuten einkochen lassen, bis die Soße glänzt.",
             meats=["haehn", "pute", "schnitzel", "haehnst", "phack"], carbs=["reis", "nudel"]),
        dict(n="Garam-Tomaten", base=dict(tom=3, zwie=1, knob=1, garam=1.5, jogGr=50, T="Salz und Pfeffer"),
             prep="Tomaten und Zwiebel in Stücke schneiden, Knoblauch fein hacken.",
             cook="Zwiebel, Knoblauch und Garam Masala zum Fleisch geben und 2 Minuten mitbraten. Tomaten zugeben und 8 Minuten köcheln, bis sie weich zerfallen. Den Joghurt zum Schluss unterrühren (nicht mehr kochen) und abschmecken.",
             meats=["haehn", "pute", "rhack", "phack"], carbs=["reis"]),
        dict(n="Tomaten-Mozzarella", base=dict(stueck=200, zwie=1, knob=1, moz=40, T="Oregano, Salz und Pfeffer"),
             prep="Zwiebel in Würfel schneiden, Knoblauch fein hacken, Mozzarella in Stücke zupfen.",
             cook="Zwiebel und Knoblauch zum Fleisch geben und 2 Minuten mitbraten. Stückige Tomaten und Oregano zugeben und 8 Minuten köcheln lassen. Den Mozzarella darauflegen und zugedeckt 2 Minuten schmelzen lassen.",
             meats=["haehn", "pute", "phack", "haehnst", "schnitzel"], carbs=["nudel"]),
        dict(n="Kurkuma-Zitronen", base=dict(kurkuma=1, zitrone=1, pap=1, zwie=1, tom=1, bruehe=100, T="Salz und Pfeffer"),
             prep="Paprika, Zwiebel und Tomate in Stücke schneiden.",
             cook="Zwiebel, Paprika und Kurkuma zum Fleisch geben und 4 Minuten mitbraten. Tomate und Brühe zugeben, 5 Minuten köcheln lassen und mit Zitronensaft, Salz und Pfeffer abschmecken.",
             meats=["haehn", "pute", "haehnst", "phack"], carbs=["reis"]),
        dict(n="Senf-Joghurt", base=dict(senf=1, jogGr=60, zwie=1, pap=1, gurke=100, T="Pfeffer und Dill"),
             prep="Zwiebel und Paprika in Streifen schneiden, Gurke in Scheiben schneiden.",
             cook="Zwiebel und Paprika zum Fleisch geben und 4 Minuten mitbraten. Die Pfanne vom Herd nehmen, Senf und Joghurt unterrühren (nicht mehr kochen) und mit Pfeffer abschmecken.",
             serve="Mit den Gurkenscheiben und Dill servieren.",
             meats=["haehn", "pute", "schnitzel", "haehnst"], carbs=["nudel", "reis"]),
        dict(n="Chili-Bohnen", base=dict(bohne=100, stueck=150, zwie=1, pap=1, paprikap=1, T="Chiliflocken, Salz und Pfeffer"),
             prep="Zwiebel und Paprika in Stücke schneiden, die Bohnen abtropfen.",
             cook="Zwiebel, Paprika und Paprikapulver zum Fleisch geben und 3 Minuten mitbraten. Bohnen und stückige Tomaten zugeben, 10 Minuten köcheln lassen und mit Chili, Salz und Pfeffer abschmecken.",
             meats=["rhack", "ghack", "phack", "haehn"], carbs=["reis"]),
        dict(n="Tomaten-Parmesan", base=dict(tom=3, knob=1, parm=10, zwie=0.5, T="Basilikum, Salz und Pfeffer"),
             prep="Tomaten in Stücke schneiden, Zwiebel würfeln, Knoblauch fein hacken.",
             cook="Zwiebel und Knoblauch zum Fleisch geben und 2 Minuten mitbraten. Tomaten zugeben und 6 Minuten schmoren, bis sie weich sind. Mit Salz und Pfeffer würzen.",
             serve="Parmesan darüberhobeln und mit Basilikum bestreuen.",
             meats=["haehn", "pute", "haehnst", "schnitzel"], carbs=["nudel"]),
    ]
    for p in P:
        for mi, m in enumerate(p["meats"]):
            for ci, c in enumerate(p["carbs"]):
                if len(p["carbs"]) > 1 and (mi + ci) % 2:
                    continue
                pre, g, art = MEAT[m]
                cw, cg, ct, cstep = CARB[c]
                i = join(ing(**{m: g, c: cg, "oel": meat_oel(m)}), ing(**p["base"]))
                serve = (p["serve"] + f" Dazu {cw} reichen.") if "serve" in p else f"Mit {cw} servieren."
                steps = [cstep, p["prep"], meat_step(m), p["cook"], serve]
                add(f"{pre}-{p['n']}-Pfanne mit {cw}", "M", round5(max(ct, 12) + 15), "pa", i, steps)


def bowls():
    """Beilage, Fleisch oder Ei und Hülsenfrucht, rohes Gemüse und ein Dressing."""
    meats = ["haehn", "pute", "haehnst", "schnitzel", "phack", "rhack"]
    n = 0
    for mi, m in enumerate(meats):
        for di, (dn, dd, ds) in enumerate(D):
            if (mi + di) % 2:
                continue
            c = "reis"
            vd, vs = V[(mi * 3 + di) % len(V)]
            pre, g, art = MEAT[m]
            cw, cg, ct, cstep = CARB[c]
            cg = 60
            extra = dict(paprikap=1, kreuz=0.5) if art == "hack" else {}
            season = " Mit Paprikapulver und Kreuzkümmel würzen." if art == "hack" else (" Mit Salz und Pfeffer würzen." if art != "steak" else "")
            i = join(ing(**{m: g, c: cg, "oel": meat_oel(m)}), ing(**vd), ing(**dd), ing(**extra))
            steps = [cstep, vs, meat_step(m) + season, ds, f"{cw} in Schalen verteilen, Gemüse und Fleisch daraufgeben und mit dem Dressing beträufeln."]
            add(f"{pre}-{cw}-Bowl mit {dn}-Dressing", "M", round5(max(ct, 10) + 12), "pa", i, steps)
    # vegetarisch: Kichererbsen und Ei
    for di, (dn, dd, ds) in enumerate(D):
        if di % 2:
            continue
        vd, vs = V[(di + 2) % len(V)]
        c = "reis"
        cw, cg, ct, cstep = CARB[c]
        i = join(ing(kiche=120, ei=2, **{c: 60}), ing(**vd), ing(**dd))
        steps = ["Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.", cstep, vs + " Die Kichererbsen abtropfen.", ds,
                 f"{cw}, Gemüse und Kichererbsen in Schalen verteilen, die Eier halbieren und daraufsetzen. Mit dem Dressing beträufeln."]
        add(f"Kichererbsen-Ei-{cw}-Bowl mit {dn}-Dressing", "M", round5(max(ct, 10) + 10), "pa", i, steps)


def run():
    import gen_main2
    pfannen()
    bowls()
    gen_main2.wraps()
    gen_main2.nudeln()
    gen_main2.sahnenudeln()
    gen_main2.auflaeufe()
    import gen_main3, gen_main4
    gen_main3.suppen()
    gen_main3.ofen()
    gen_main3.haeckse()
    gen_main3.brokkoli()
    gen_main3.kartoffelbrei()
    gen_main4.salate()
    gen_main4.eier()
    gen_main4.huelsen()
