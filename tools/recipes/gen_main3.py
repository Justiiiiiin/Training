# -*- coding: utf-8 -*-
"""Mittag/Abend: Suppen und Eintöpfe, Ofengerichte, Hackgerichte."""
from gen_core import *
from gen_main import V, D
from gen_main2 import NAME


def suppen():
    BR = "Brühe (am besten aus Brühepulver) aufkochen."
    # (a) Rote Linsensuppe mit Einlage
    SP = [("Curry", dict(curry=1.5, zwie=1, knob=1), "Curry"), ("Kreuzkümmel", dict(kreuz=1.5, zwie=1, knob=1), "Kreuzkümmel"),
          ("Paprika", dict(paprikap=2, zwie=1, knob=1), "Paprikapulver"), ("Garam Masala", dict(garam=1.5, zwie=1, knob=1), "Garam Masala")]
    EIN = [("Hähnchen", dict(haehn=100, oel=1)), ("Putenhack", dict(phack=100, oel=0.5)), ("Rinderhack", dict(rhack=90, oel=0.5)), ("Schinken und Joghurt", dict(jogGr=50, schink=50)), ("Ei", dict(ei=2))]
    for si, (sn, sd, sw) in enumerate(SP):
        for ei, (en, ed) in enumerate(EIN):
            if (si + ei) % 2:
                continue
            gem = dict(pap=1, stueck=150) if si % 2 == 0 else dict(tom=2, pap=1)
            key = [k for k in ed if k not in ("oel",)][0]
            if key in ("haehn", "phack", "rhack"):
                einl = ("Das Hähnchen in kleine Würfel schneiden und im Öl 5 bis 7 Minuten braten, bis es durch ist." if key == "haehn" else "Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist.")
            elif key == "jogGr":
                einl = "Den Schinken in Streifen schneiden."
            else:
                einl = "Die Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und halbieren."
            i = join(ing(linse=50, brot=1, bruehe=400), ing(**sd), ing(**gem), ing(**ed), ing(oel=0.5) if "oel" not in ed else "", ing(T="Salz und Pfeffer"))
            add(f"Rote Linsensuppe mit {nl(sn, en)}", "M", 35, "pa", i,
                [("Zwiebel, Paprika und Tomaten" if "tom" in gem else "Zwiebel und Paprika") + " in Stücke schneiden, Knoblauch fein hacken.", "Zwiebel und Knoblauch mit " + sw + " in einem Topf in etwas Öl 2 Minuten anrösten. Linsen, Gemüse und Brühe zugeben.",
                 "Alles 15 bis 20 Minuten köcheln, bis die Linsen weich sind, dann grob pürieren. Würzen.", einl,
                 ("Die Suppe mit der Einlage servieren, Joghurt daraufgeben. " if key == "jogGr" else "Die Suppe mit der Einlage servieren. ") + "Dazu eine Scheibe Vollkornbrot essen."])
    # (b) Kichererbsen-Eintopf
    for si, (sn, sd, sw) in enumerate([("Kreuzkümmel", dict(kreuz=1, paprikap=1), "Kreuzkümmel und Paprikapulver"), ("Curry", dict(curry=2), "Curry"), ("Garam Masala", dict(garam=1.5, kurkuma=0.5), "Garam Masala und Kurkuma")]):
        for ei, m in enumerate(["haehn", "phack", "rhack", "ghack", "pute"]):
            if (si + ei) % 2:
                continue
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g - 40, "kiche": 150, "pap": 1, "zwie": 1, "stueck": 200, "bruehe": 150, "brot": 1, "oel": meat_oel(m)}), ing(**sd), ing(T="Salz und Pfeffer"))
            add(f"Kichererbsen-Eintopf mit {NAME[m]} und {sn}", "M", 35, "pa", i,
                ["Paprika und Zwiebel in Stücke schneiden, die Kichererbsen abtropfen.", meat_step(m), "Paprika und Zwiebel mit " + sw + " zum Fleisch geben und 4 Minuten mitbraten.",
                 "Kichererbsen, stückige Tomaten und Brühe zugeben und 15 Minuten köcheln lassen. Mit Salz und Pfeffer abschmecken.", "Dazu eine Scheibe Vollkornbrot essen."])
    # (c) Chili (hier darf die Karotte rein)
    for mi, m in enumerate(["rhack", "phack", "ghack", "haehn"]):
        for ci, c in enumerate(["reis", "brot"]):
            for ki, karo in enumerate([False, True]):
                if (mi + ci + ki) % 2:
                    continue
                pre, g, art = MEAT[m]
                cw = {"reis": "Reis", "brot": "Vollkornbrot"}[c]
                cg = {"reis": 60, "brot": 2}[c]
                cstep = {"reis": CARB["reis"][3], "brot": "Das Brot dazu bereitstellen."}[c]
                i = join(ing(**{m: g - 20, c: cg, "bohne": 120, "pap": 1, "zwie": 1, "stueck": 200, "tmark": 1, "paprikap": 1.5, "kreuz": 0.5, "oel": meat_oel(m)}), ing(karo=1) if karo else "", ing(T="Chiliflocken, Salz und Pfeffer"))
                add(f"{pre}-Chili mit {'Karotte, ' if karo else ''}Kidneybohnen und {cw}", "M", 40, "pa", i,
                    [cstep, "Paprika und Zwiebel würfeln" + (", die Karotte raspeln" if karo else "") + ", die Bohnen abtropfen.", meat_step(m),
                     "Gemüse, Tomatenmark, Paprikapulver und Kreuzkümmel zugeben und 4 Minuten mitbraten. Bohnen und stückige Tomaten zugeben.", "20 Minuten bei niedriger Hitze köcheln, bei Bedarf Wasser nachgießen. Mit Chili, Salz und Pfeffer abschmecken."])
    # (d) Tomatensuppe
    for ei, (en, ed, es) in enumerate([("Putenhack-Bällchen", dict(phack=120, hafer=10), "Hack mit Haferflocken, Salz und Pfeffer verkneten, kleine Bällchen formen und in der Suppe 10 Minuten gar ziehen lassen, bis sie innen nicht mehr rosa sind."),
                                        ("Rinderhack-Bällchen", dict(rhack=110, hafer=10), "Hack mit Haferflocken, Salz und Pfeffer verkneten, kleine Bällchen formen und in der Suppe 10 Minuten gar ziehen lassen, bis sie innen nicht mehr rosa sind."),
                                        ("Hähnchenstreifen", dict(haehn=120, oel=1), "Hähnchen in Streifen schneiden, im Öl 6 bis 8 Minuten braten, bis es durch ist, und in die fertige Suppe geben."),
                                        ("Mozzarella und Schinken", dict(moz=60, schink=60), "Mozzarella zupfen und den Schinken in Streifen schneiden. Beides in die Schalen geben und die heiße Suppe darübergießen.")]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1, zwie=1, knob=1), "Paprika und Zwiebel würfeln, Knoblauch hacken."), ("Tomate", dict(tom=2, zwie=1, knob=1), "Tomaten und Zwiebel würfeln, Knoblauch hacken.")]):
            i = join(ing(stueck=300, bruehe=200, brot=1, tmark=1), ing(**vd), ing(**ed), ing(oel=0.5) if "oel" not in ed else "", ing(T="Basilikum, Salz und Pfeffer"))
            add(("Paprika-Tomatensuppe" if vn == "Paprika" else "Tomatensuppe") + f" mit {en}", "M", 30, "pa", i,
                [vs, "Gemüse im Topf in etwas Öl 3 Minuten anbraten, Tomatenmark, stückige Tomaten und Brühe zugeben und 15 Minuten köcheln.", "Die Suppe pürieren und würzen.", es, "Mit einer Scheibe Vollkornbrot servieren."])
    # (e) Reis- oder Nudelsuppe mit Hähnchen
    for ci, c in enumerate(["reis", "nudel"]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1, zwie=1), "Paprika und Zwiebel würfeln."), ("Tomate", dict(tom=2, zwie=1), "Tomaten und Zwiebel würfeln."), ("Paprika und Tomate", dict(pap=1, tom=1, zwie=1), "Paprika, Tomate und Zwiebel würfeln.")]):
            for m in ["haehn", "pute"]:
                if (ci + vi) % 2 and m == "pute":
                    continue
                cw = CARB[c][0]
                i = join(ing(**{m: 110, c: 40, "bruehe": 450, "oel": 1}), ing(**vd), ing(T="Petersilie, Salz und Pfeffer"))
                add(f"{NAME[m]}-{'Reis' if c == 'reis' else 'Nudel'}-Suppe mit {vn}", "M", 30, "pa", i,
                    [vs, "Das Fleisch in kleine Würfel schneiden und im Topf im Öl 4 Minuten anbraten.", "Gemüse und Brühe zugeben, aufkochen und " + cw + " einrühren. 12 bis 15 Minuten köcheln, bis alles gar ist und das Fleisch durch ist.", "Mit Petersilie, Salz und Pfeffer abschmecken."])
    # (f) Kokos-Curry-Suppe
    for m in ["haehn", "pute", "phack"]:
        for vn, vd, vs in [("Paprika", dict(pap=2, zwie=1), "Paprika und Zwiebel in Streifen schneiden."), ("Tomate", dict(tom=2, pap=1, zwie=1), "Tomaten, Paprika und Zwiebel in Stücke schneiden.")]:
            if m == "phack" and vn == "Tomate":
                continue
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g - 40, "reis": 30, "kokos": 150, "bruehe": 250, "curry": 2, "knob": 1, "zitrone": 1, "oel": meat_oel(m)}), ing(**vd), ing(T="Salz und Pfeffer"))
            add(f"Kokos-Curry-Suppe mit {NAME[m]} und {vn}", "M", 30, "pa", i,
                [vs + " Knoblauch fein hacken.", meat_step(m), "Gemüse, Knoblauch und Curry zugeben und 3 Minuten mitbraten. Kokosmilch, Brühe und Reis zugeben und 15 Minuten köcheln, bis der Reis gar ist.", "Mit Zitronensaft, Salz und Pfeffer abschmecken."])


def ofen():
    SPICE = [("Paprika-Oregano", dict(paprikap=2), "Mit Öl, Paprikapulver, Oregano, Salz und Pfeffer mischen."),
             ("Kreuzkümmel-Paprika", dict(kreuz=1, paprikap=1), "Mit Öl, Kreuzkümmel, Paprikapulver, Salz und Pfeffer mischen."),
             ("Curry-Kurkuma", dict(curry=1.5, kurkuma=0.5), "Mit Öl, Curry, Kurkuma, Salz und Pfeffer mischen."),
             ("Senf-Honig", dict(senf=1, honig=1), "Mit Öl, Senf, Honig, Salz und Pfeffer mischen."),
             ("Knoblauch-Zitrone", dict(knob=1, zitrone=1), "Mit Öl, Knoblauch, Zitronensaft, Salz und Pfeffer mischen."),
             ("Garam-Masala", dict(garam=1.5), "Mit Öl, Garam Masala, Salz und Pfeffer mischen.")]
    SIDE = [("Nudeln", dict(nudel=60), "Die Nudeln nach Packungsanleitung kochen und zum Blech servieren."),
            ("Reis", dict(reis=60), "Den Reis nach Packungsanleitung kochen und zum Blech servieren."),
            ("Vollkornbrot", dict(brot=2), "Das Brot zum Blech servieren.")]
    for mi, m in enumerate(["haehn", "pute", "schnitzel", "haehnst"]):
        for si, (sn, sd, ss) in enumerate(SPICE):
            for bi, (bn, bd, bs) in enumerate(SIDE):
                if (mi + si + bi) % 3:
                    continue
                pre, g, art = MEAT[m]
                veg = dict(pap=2, zwie=1, tom=2) if si % 2 == 0 else dict(pap=1, zwie=1, tom=3)
                i = join(ing(**{m: g + 10, "oel": 1.5}), ing(**veg), ing(**sd), ing(**bd), ing(T="Salz und Pfeffer"))
                add(f"{pre}-Blech mit {sn}-Würzung und {bn}", "M", 40, "p" if bn != "Vollkornbrot" else "", i,
                    ["Ofen auf 220 °C Ober- und Unterhitze vorheizen.", "Fleisch in Stücke, Paprika, Tomaten und Zwiebel in Spalten oder Stücke schneiden.",
                     ss + " Alles auf einem Blech mit Backpapier verteilen.", "20 bis 25 Minuten backen, bis das Fleisch durch und innen nicht mehr rosa ist, und einmal wenden." if art != "steak" else "Die Mini-Steaks zwischen das Gemüse legen und nach Packungsanleitung 20 Minuten backen, bis sie durch sind.",
                     bs])
    # Mini-Hackbraten aus dem Muffinblech
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for vi, (vn, vd) in enumerate([("Paprika und Tomate", dict(pap=2, tom=2, zwie=0.5)), ("Paprika und Rucola", dict(pap=2, ruc=30, zwie=0.5))]):
            for ci, c in enumerate(["nudel", "reis"]):
                if (mi + vi + ci) % 2:
                    continue
                pre, g, art = MEAT[m]
                i = join(ing(**{m: g, c: 60, "ei": 0.5, "hafer": 15, "senf": 1, "paprikap": 1}), ing(**vd), ing(T="Salz und Pfeffer"))
                add(f"Mini-Hackbraten ({pre}) mit {nl(vn, CARB[c][0])}", "M", 40, "p", i,
                    ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. " + CARB[c][3], "Hack mit Ei, Haferflocken, Senf, Paprikapulver, der fein gewürfelten halben Zwiebel, Salz und Pfeffer verkneten und in zwei Mulden eines Muffinblechs oder in kleinen Förmchen andrücken.",
                     ("Paprika und Tomaten in Stücke schneiden. Das Gemüse neben den Hackbraten auf ein Blech geben und mit Salz und Pfeffer würzen." if "tom" in vd else "Die Paprika in Stücke schneiden, neben den Hackbraten auf ein Blech geben und würzen. Den Rucola zupfen und erst zum Servieren dazugeben."),
                     "Alles 25 Minuten backen, bis der Hackbraten innen nicht mehr rosa ist.", f"Mit {CARB[c][0]} servieren."])


def haeckse():
    # (a) Bällchen in Tomatensoße
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for ci, c in enumerate(["nudel", "reis"]):
            for si, (sn, sd, sp) in enumerate([("Paprika-Tomatensoße", dict(pap=1, zwie=1, stueck=200, knob=1), "Paprika und Zwiebel würfeln, Knoblauch hacken."), ("Tomaten-Basilikum-Soße", dict(tom=2, zwie=1, stueck=150, knob=1), "Tomaten und Zwiebel würfeln, Knoblauch hacken.")]):
                pre, g, art = MEAT[m]
                i = join(ing(**{m: g, c: CARB[c][1], "hafer": 10, "senf": 0.5, "oel": 1, "moz": 20}), ing(**sd), ing(T="Oregano, Salz und Pfeffer"))
                add(f"{pre}-Bällchen in {sn} mit {CARB[c][0]}", "M", 35, "pa", i,
                    [CARB[c][3], sp, "Hack mit Haferflocken, Senf, Salz und Pfeffer verkneten und zu kleinen Bällchen formen. Im Öl rundum 5 Minuten anbraten.",
                     "Gemüse zu den Bällchen geben, 3 Minuten mitbraten, die stückigen Tomaten zugeben und 10 Minuten zugedeckt köcheln, bis die Bällchen innen nicht mehr rosa sind.", f"Mit {CARB[c][0]} servieren und mit Mozzarella bestreuen."])
    # (b) Frikadellen mit Dip und Salat
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for di, (dn, dd, ds) in enumerate(D):
            if (mi + di) % 3:
                continue
            vd, vs = V[(mi + di) % len(V)]
            pre, g, art = MEAT[m]
            s = ["brot", "reis"][(mi + di) % 2]
            i = join(ing(**{m: g, "hafer": 15, "ei": 0.5, "zwie": 0.5, "senf": 1, "oel": 1, s: 2 if s == "brot" else 50}), ing(**vd), ing(**dd), ing(T="Salz und Pfeffer"))
            add(f"{pre}-Frikadellen mit {dn}-Dip und Salat", "M", 30, "pa", i,
                [vs, (CARB["reis"][3] if s == "reis" else "Das Brot bereitstellen."),
                 "Hack mit Haferflocken, Ei, der fein gewürfelten Zwiebel, Senf, Salz und Pfeffer verkneten und zu flachen Frikadellen formen.", "Im Öl bei mittlerer Hitze 5 bis 6 Minuten pro Seite braten, bis sie innen nicht mehr rosa sind.", ds, "Frikadellen mit Salat, Dip und " + ("Reis" if s == "reis" else "Brot") + " servieren."])
    # (c) Burger-Bowl und Burger
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for bi, (bn, bd) in enumerate([("ohne Brötchen", dict(eisb=60, gurke=50)), ("im Vollkornbrötchen", dict(broetchen=1, eisb=40, gurke=50))]):
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g, "gouda": 30, "tom": 2, "sgurke": 2, "senf": 1, "oel": 0.5}), ing(**bd), ing(T="Salz und Pfeffer"))
            end = "Das Brötchen aufschneiden, mit Senf, Salat, Tomate, Saurer Gurke, Patty und Gouda belegen." if bi else "Salat, Tomaten, Gurke und Saure Gurke in einer Schale anrichten, Patty darauflegen und mit Senf beträufeln."
            add(f"{pre}-Burger {bn} mit Gouda und Saurer Gurke", "M", 25, "", i,
                ["Eisbergsalat in Streifen, Tomaten in Scheiben und Gurke sowie Saure Gurken in Scheiben schneiden.", "Hack mit Salz und Pfeffer würzen und zu zwei flachen Patties formen.",
                 "Die Patties im Öl 4 bis 5 Minuten pro Seite braten, bis sie durch sind (innen nicht mehr rosa). Zum Schluss mit Gouda belegen und kurz schmelzen lassen.", end])
    # (d) Köfte-Spieße
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for ci, c in enumerate(["reis", "brot"]):
            pre, g, art = MEAT[m]
            cw = "Vollkornbrot" if c == "brot" else CARB[c][0]
            i = join(ing(**{m: g, c: 2 if c == "brot" else 60, "zwie": 0.5, "kreuz": 1, "paprikap": 1, "jog35": 80, "gurke": 100, "tom": 2, "oel": 1}), ing(T="Petersilie, Salz und Pfeffer"))
            add(f"{pre}-Köfte mit {cw}, Gurken-Tomaten-Salat und Joghurt", "M", 30, "p", i,
                ["Das Brot bereitstellen." if c == "brot" else CARB[c][3], "Hack mit der fein gewürfelten Zwiebel, Kreuzkümmel, Paprikapulver, Salz und Pfeffer gut verkneten und zu länglichen Röllchen formen.",
                 "Die Röllchen im Öl rundum 8 bis 10 Minuten braten, bis sie innen nicht mehr rosa sind.", "Gurke und Tomaten würfeln und mit Salz, Pfeffer und Petersilie mischen. Joghurt glatt rühren.", f"Köfte mit {cw}, Salat und Joghurt servieren."])
    # (e) Hähnchen mit Haferkruste (gebacken)
    for di, (dn, dd, ds) in enumerate(D):
        for ci, c in enumerate(["reis", "brot"]):
            if (di + ci) % 2:
                continue
            vd, vs = V[di % len(V)]
            i = join(ing(haehn=150, hafer=25, ei=1, paprikap=1, oel=1), ing(**vd), ing(**dd), ing(reis=60) if c == "reis" else ing(brot=2), ing(T="Salz und Pfeffer"))
            add(f"Hähnchen mit Haferkruste, {dn}-Dip und Salat", "M", 35, "", i,
                ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. " + (CARB["reis"][3] if c == "reis" else ""), vs,
                 "Hähnchen in Streifen schneiden und salzen. Ei verquirlen, Haferflocken mit Paprikapulver und Pfeffer mischen. Die Streifen erst im Ei, dann in den Haferflocken wenden und fest andrücken.",
                 "Auf einem geölten Blech 15 bis 18 Minuten backen, einmal wenden, bis das Fleisch durch und die Kruste goldbraun ist.", ds, "Mit Salat, Dip und " + ("Reis" if c == "reis" else "Brot") + " servieren."])


def brokkoli():
    """Brokkoli: Nudeln in Parmesan-Sahne-Soße, Pfannen mit Reis, Nudelauflauf, Tomaten-Nudeln, Omelett und Suppe."""
    teil = "Den Brokkoli in kleine Röschen teilen, den Strunk schälen und in Scheiben schneiden."
    wort = {"haehn": "Hähnchen", "pute": "Pute", "schink": "Schinken"}

    def fl(m, g=None):
        """(Titelwort, Menge, Brat-Schritt, Öl in TL) für Fleisch aus MEAT oder Schinken."""
        if m == "schink":
            return "Schinken", g or 60, "Den Schinken in Würfel schneiden und im Öl 2 Minuten anbraten.", 0.5
        pre, g0, art = MEAT[m]
        return pre, g or g0, meat_step(m), meat_oel(m)

    # (a) Nudeln mit Brokkoli in Parmesan-Sahne-Soße
    for m in ["haehn", "pute", "schink"]:
        pre, g, st, o = fl(m, 90 if m != "schink" else 60)
        i = join(ing(**{m: g, "nudel": 70, "brok": 150, "sahne": 30, "parm": 15, "oel": o}), ing(zwie=0.5, knob=1, T="Muskat, Salz und Pfeffer"))
        add(f"{pre}-Nudeln mit Brokkoli in Parmesan-Sahne-Soße", "M", 30, "p", i,
            [teil + " Die Nudeln nach Packungsanleitung in Salzwasser kochen, den Brokkoli in den letzten 3 Minuten mitkochen. Etwas Nudelwasser aufheben, dann abgießen.",
             "Zwiebel würfeln, Knoblauch fein hacken.", st,
             "Zwiebel und Knoblauch zum Fleisch geben und 2 Minuten mitbraten. Die Sahne zugießen und bei niedriger Hitze 2 Minuten köcheln lassen. Den Parmesan einrühren, bis er geschmolzen ist, und mit Muskat, Salz und Pfeffer würzen.",
             "Nudeln und Brokkoli untermischen, bei Bedarf einen Schuss Nudelwasser zugeben."])

    # (b) Brokkoli-Pfanne mit Honig-Senf-Soße und Reis
    for m in ["haehn", "pute", "haehnst", "schnitzel"]:
        pre, g, st, o = fl(m, MEAT[m][1] - 20)
        i = join(ing(**{m: g, "reis": 70, "brok": 150, "zwie": 0.5, "knob": 1, "senf": 1.5, "honig": 1, "bruehe": 100, "oel": o}), ing(T="Salz und Pfeffer"))
        add(f"{pre}-Brokkoli-Pfanne mit Honig-Senf-Soße und Reis", "M", 30, "pa", i,
            [CARB["reis"][3], teil + " Zwiebel in Streifen schneiden, Knoblauch fein hacken.", st,
             "Zwiebel, Brokkoli und Knoblauch zum Fleisch geben und 3 Minuten mitbraten. Senf, Honig und Brühe zugeben und zugedeckt 5 Minuten garen, bis der Brokkoli bissfest ist. Dann ohne Deckel 2 Minuten einkochen lassen und mit Salz und Pfeffer abschmecken.",
             "Mit dem Reis servieren."])

    # (c) Hack-Brokkoli-Pfanne mit Tomaten und Reis
    for m in ["rhack", "phack"]:
        pre, g, st, o = fl(m)
        i = join(ing(**{m: g, "reis": 70, "brok": 150, "stueck": 100, "zwie": 0.5, "knob": 1, "paprikap": 1, "oel": o}), ing(T="Salz und Pfeffer"))
        add(f"{pre}-Brokkoli-Pfanne mit Tomaten und Reis", "M", 30, "pa", i,
            [CARB["reis"][3], teil + " Zwiebel würfeln, Knoblauch fein hacken.", st,
             "Zwiebel, Knoblauch und Paprikapulver zum Hack geben und 2 Minuten mitbraten. Brokkoli und stückige Tomaten zugeben und zugedeckt 8 Minuten garen, bis der Brokkoli bissfest ist. Mit Salz und Pfeffer würzen.",
             "Mit dem Reis servieren."])

    # (d) Brokkoli-Nudelauflauf
    for m, kn, kg in [("haehn", "Gouda", dict(gouda=30)), ("pute", "Mozzarella", dict(moz=40)), ("schink", "Gouda", dict(gouda=30))]:
        pre, g, st, o = fl(m, 80 if m != "schink" else 60)
        i = join(ing(**{m: g, "nudel": 60, "brok": 150, "sahne": 40, "zwie": 0.5, "knob": 1, "oel": o}), ing(**kg), ing(T="Muskat, Salz und Pfeffer"))
        add(f"Brokkoli-Nudelauflauf mit {wort[m]} und {kn}", "M", 40, "p", i,
            ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. " + teil + " Die Nudeln 3 Minuten kürzer als auf der Packung angegeben kochen, den Brokkoli in den letzten 2 Minuten mitkochen, dann abgießen.",
             "Zwiebel würfeln, Knoblauch fein hacken.", st,
             "Zwiebel und Knoblauch zum Fleisch geben und 2 Minuten mitbraten. Die Sahne zugießen, aufkochen und mit Muskat, Salz und Pfeffer abschmecken.",
             "Nudeln, Brokkoli und die Soße in einer Auflaufform mischen, den Käse darauf verteilen und 15 bis 20 Minuten backen, bis er goldbraun ist."])

    # (e) vegetarisch: Brokkoli-Tomaten-Nudeln
    add("Brokkoli-Tomaten-Nudeln mit Mozzarella und Parmesan", "M", 25, "p",
        join(ing(nudel=70, brok=150, tom=2, moz=60, parm=15, knob=1, oel=1), ing(T="Basilikum, Salz und Pfeffer")),
        [teil + " Die Nudeln nach Packungsanleitung in Salzwasser kochen, den Brokkoli in den letzten 3 Minuten mitkochen, dann abgießen.",
         "Tomaten in Stücke schneiden, Knoblauch fein hacken, Mozzarella zupfen.",
         "Knoblauch im Öl 1 Minute anbraten, die Tomaten zugeben und 4 Minuten schmoren.",
         "Nudeln und Brokkoli untermischen, den Mozzarella darauf verteilen und zugedeckt 2 Minuten schmelzen lassen. Mit Parmesan und Basilikum servieren."])

    # (f) Omelett
    add("Brokkoli-Omelett mit Mozzarella, Tomate und Brot", "M", 20, "",
        join(ing(ei=3, brok=100, moz=40, tom=1, brot=1, oel=1), ing(T="Salz und Pfeffer")),
        ["Den Brokkoli in kleine Röschen teilen und 3 Minuten in Salzwasser kochen, abgießen. Die Tomate in Scheiben schneiden, den Mozzarella zupfen.",
         "Eier verquirlen und würzen. Das Öl in einer Pfanne erhitzen, den Brokkoli kurz anbraten und die Eier zugeben. Bei mittlerer Hitze fast stocken lassen.",
         "Tomate und Mozzarella darauf verteilen, zuklappen und 1 Minute ziehen lassen, bis das Ei ganz fest ist.", "Mit dem Brot servieren."])

    # (g) Brokkoli-Sahne-Suppe mit Fleisch
    for m in ["haehn", "pute"]:
        pre, g, st, o = fl(m, 90)
        i = join(ing(**{m: g, "brok": 250, "zwie": 0.5, "knob": 1, "bruehe": 400, "sahne": 40, "parm": 15, "brot": 1, "oel": o}), ing(T="Muskat, Salz und Pfeffer"))
        add(f"Brokkoli-Sahne-Suppe mit {wort[m]} und Parmesan", "M", 30, "p", i,
            ["Den Brokkoli in Röschen teilen, den Strunk schälen und würfeln. Zwiebel würfeln, Knoblauch fein hacken.", st + " Das Fleisch herausnehmen und beiseitestellen.",
             "Zwiebel und Knoblauch im selben Topf 2 Minuten andünsten. Brokkoli und Brühe (am besten aus Brühepulver) zugeben und 8 Minuten köcheln lassen.",
             "Die Suppe mit dem Stabmixer pürieren (ein paar Röschen dürfen stückig bleiben), die Sahne einrühren und mit Muskat, Salz und Pfeffer abschmecken.",
             "Das Fleisch in die Suppe geben und kurz erwärmen. Mit Parmesan bestreuen und mit dem Brot servieren."])


def kartoffelbrei():
    """Kartoffelbrei (aus frischen Kartoffeln, mit Milch und Butter) zu Fleisch und Gemüse. Pommes bleiben gesperrt (BANNED in build.py)."""
    brei = dict(kart=250, milch=50, butter=5)
    k1 = "Die Kartoffeln schälen, in gleich große Stücke schneiden und in Salzwasser 15 bis 20 Minuten kochen, bis sie ganz weich sind."
    k2 = "Die Kartoffeln abgießen, mit der Milch und der Butter zu Brei stampfen und mit Salz und Muskat abschmecken."
    tipk = "Mehligkochende Kartoffeln werden besonders cremig. Die Milch darf ruhig warm sein."
    brok = "Den Brokkoli in Röschen teilen, den Strunk schälen und in Scheiben schneiden. In Salzwasser 4 bis 5 Minuten bissfest garen und abgießen."

    # (a) Fleisch mit Kartoffelbrei und Brokkoli
    for m in ["haehn", "pute", "schnitzel", "haehnst"]:
        pre, g, art = MEAT[m]
        i = join(ing(**{m: g - 20, "brok": 150, "oel": meat_oel(m)}), ing(**brei), ing(T="Salz, Pfeffer und Muskat"))
        add(f"{NAME[m]} mit Kartoffelbrei und Brokkoli", "M", 35, "", i, [k1, meat_step(m), brok, k2, "Fleisch, Brokkoli und Kartoffelbrei anrichten."], tipk)

    # (b) Fleisch in Senf-Sahne-Soße
    for m in ["haehn", "schnitzel"]:
        pre, g, art = MEAT[m]
        i = join(ing(**{m: g - 20, "brok": 150, "zwie": 0.5, "sahne": 30, "senf": 1, "oel": meat_oel(m)}), ing(**brei), ing(T="Salz, Pfeffer und Muskat"))
        add(f"{NAME[m]} in Senf-Sahne-Soße mit Kartoffelbrei und Brokkoli", "M", 35, "", i,
            [k1, meat_step(m), brok,
             "Die Zwiebel würfeln, zum Fleisch geben und 2 Minuten mitbraten. Sahne und Senf einrühren, 3 Minuten sanft köcheln lassen und mit Salz und Pfeffer abschmecken.",
             k2, "Fleisch mit der Soße, Brokkoli und Kartoffelbrei anrichten."], tipk)

    # (c) Hackbällchen in Tomatensoße
    for m in ["rhack", "phack"]:
        pre, g, art = MEAT[m]
        i = join(ing(**{m: g, "hafer": 10, "senf": 0.5, "oel": 1, "stueck": 200, "zwie": 1, "knob": 1}), ing(**brei), ing(T="Oregano, Salz, Pfeffer und Muskat"))
        add(f"{pre}-Bällchen in Tomatensoße mit Kartoffelbrei", "M", 40, "", i,
            [k1, "Zwiebel würfeln, Knoblauch fein hacken.",
             "Hack mit Haferflocken, Senf, Salz und Pfeffer verkneten, zu kleinen Bällchen formen und im Öl rundum 5 Minuten anbraten.",
             "Zwiebel und Knoblauch zugeben und 2 Minuten mitbraten. Die stückigen Tomaten zugeben und 10 Minuten zugedeckt köcheln, bis die Bällchen innen nicht mehr rosa sind. Mit Oregano, Salz und Pfeffer würzen.",
             k2, "Die Bällchen mit der Soße auf dem Kartoffelbrei servieren."], tipk)

    # (d) Fleisch mit Paprika-Zwiebel-Gemüse
    for m in ["haehn", "pute"]:
        pre, g, art = MEAT[m]
        i = join(ing(**{m: g - 20, "pap": 2, "zwie": 1, "paprikap": 1, "oel": meat_oel(m)}), ing(**brei), ing(T="Salz, Pfeffer und Muskat"))
        add(f"{NAME[m]} mit Paprika-Zwiebel-Gemüse und Kartoffelbrei", "M", 35, "", i,
            [k1, "Paprika in Streifen, Zwiebel in Ringe schneiden.", meat_step(m),
             "Paprika, Zwiebel und Paprikapulver zum Fleisch geben und 6 Minuten mitbraten, bis das Gemüse weich ist. Mit Salz und Pfeffer abschmecken.",
             k2, "Fleisch und Gemüse mit dem Kartoffelbrei anrichten."], tipk)
