# -*- coding: utf-8 -*-
"""Mittag/Abend: Salate, Eiergerichte, Hülsenfrucht-Gerichte."""
from gen_core import *
from gen_main import V, D
from gen_main2 import NAME


def cooked_protein(m, g):
    """Zutatenstück und Schritt für ein Fleisch, das für Salate gebraten und abgekühlt wird."""
    if m in MEAT:
        return ing(**{m: g, "oel": meat_oel(m)}), meat_step(m) + " Kurz abkühlen lassen."
    if m == "ei":
        return ing(ei=g), "Die Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und vierteln."
    if m == "moz":
        return ing(moz=g), "Den Mozzarella abtropfen lassen und in Scheiben schneiden."
    if m == "gouda":
        return ing(gouda=g), "Den Gouda in kleine Würfel schneiden."
    return ing(**{m: g}), f"{NAME[m]} in Streifen schneiden."


WORD = {"haehn": "Hähnchen", "pute": "Pute", "schnitzel": "Schnitzel", "haehnst": "Mini-Steaks", "ei": "Ei", "moz": "Mozzarella", "gouda": "Gouda",
        "paufs": "Putenaufschnitt", "schink": "Schinken", "phack": "Putenhack", "rhack": "Rinderhack", "ghack": "Hack"}


def salate():
    # (1) Caesar-Art
    for mi, (m, g) in enumerate([("haehn", 130), ("pute", 130), ("haehnst", 120), ("schnitzel", 120)]):
        for di in (8, 0, 1, 7):
            if (mi + di) % 3 == 1:
                continue
            dn, dd, ds = D[di]
            ci, cs = cooked_protein(m, g)
            i = join(ci, ing(eisb=100, ruc=30, tom=1, brot=1, parm=10), ing(**dd), ing(T="Pfeffer"))
            add(f"Caesar-Salat mit {WORD[m]}, Brot-Croutons und {dn}-Dressing", "M", 25, "a", i,
                ["Eisbergsalat in Streifen schneiden, Rucola zupfen und die Tomate in Spalten schneiden.", cs + " Das Brot in Würfel schneiden und in einer trockenen Pfanne knusprig rösten.", ds,
                 "Salat, Fleisch und Croutons anrichten, mit dem Dressing beträufeln und den Parmesan darüberhobeln."])
    # (2) Taco-Salat
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for bi, b in enumerate(["bohne", "kiche"]):
            for di, dn in enumerate(["Paprika-Joghurt", "Kreuzkümmel-Quark"]):
                pre, g, art = MEAT[m]
                dd, ds = {"Paprika-Joghurt": (dict(jogGr=50, paprikap=1, zitrone=1), "Joghurt mit Paprikapulver, Zitronensaft und Salz verrühren."),
                          "Kreuzkümmel-Quark": (dict(quark=60, kreuz=0.5, zitrone=1), "Quark mit Kreuzkümmel, Zitronensaft, Salz und einem Schuss Wasser glatt rühren.")}[dn]
                if (mi + bi + di) % 2:
                    continue
                i = join(ing(**{m: g - 20, b: 100, "eisb": 80, "tom": 2, "pap": 1, "gouda": 20, "paprikap": 1, "kreuz": 0.5, "oel": 0.5}), ing(**dd), ing(T="Salz und Pfeffer"))
                add(f"Taco-Salat mit {pre} und {'Bohnen' if b == 'bohne' else 'Kichererbsen'} ({dn}-Dressing)", "M", 25, "a", i,
                    ["Eisbergsalat in Streifen schneiden, Tomaten und Paprika würfeln, die Hülsenfrüchte abtropfen.", meat_step(m) + " Mit Paprikapulver, Kreuzkümmel, Salz und Pfeffer würzen.", ds,
                     "Salat, Gemüse und Hülsenfrüchte in einer Schüssel mischen, das warme Hack darauf verteilen, den Gouda reiben und darüberstreuen. Mit dem Dressing beträufeln."])
    # (3) Kichererbsen-Salat
    for mi, (m, g) in enumerate([("ei", 2), ("moz", 80), ("schink", 70), ("haehn", 100), ("paufs", 80)]):
        for di in (0, 1, 7, 6):
            if (mi + di) % 2:
                continue
            dn, dd, ds = D[di]
            ci, cs = cooked_protein(m, g)
            kg = 170 if m == "schink" else 150
            i = join(ci, ing(kiche=kg, gurke=150, tom=2, zwie=0.5), ing(**dd), ing(T="Salz und Pfeffer"))
            add(f"Kichererbsen-Salat mit {WORD[m]}, Gurke und {dn}-Dressing", "M", 20, "ka" if m not in ("haehn", "ei") else "a", i,
                ["Kichererbsen abtropfen, Gurke und Tomaten würfeln, die Zwiebel in feine Ringe schneiden.", cs, ds, "Alles in einer Schüssel mischen und 10 Minuten durchziehen lassen."])
    # (4) Bohnen-Salat
    for mi, (m, g) in enumerate([("schink", 70), ("haehn", 100), ("ei", 2), ("gouda", 40), ("paufs", 80)]):
        for di in (3, 1, 6):
            if (mi + di) % 2:
                continue
            dn, dd, ds = D[di]
            ci, cs = cooked_protein(m, g)
            i = join(ci, ing(bohne=150, pap=1, zwie=0.5, tom=1, gurke=100), ing(**dd), ing(T="Salz und Pfeffer"))
            add(f"Bohnensalat mit {WORD[m]}, Paprika und {dn}-Dressing", "M", 20, "ka" if m not in ("haehn", "ei") else "a", i,
                ["Bohnen abtropfen, Paprika, Tomate und Gurke würfeln, die Zwiebel in feine Ringe schneiden.", cs, ds, "Alles vermischen und 10 Minuten durchziehen lassen."])
    # (5) Couscous-Salat
    for mi, (m, g) in enumerate([("haehn", 110), ("pute", 110), ("paufs", 90), ("moz", 80), ("ei", 2)]):
        for di in (0, 5, 3, 7):
            if (mi + di) % 2:
                continue
            dn, dd, ds = D[di]
            ci, cs = cooked_protein(m, g)
            vd, vs = V[(mi + di) % len(V)]
            i = join(ci, ing(couscous=60), ing(**vd), ing(**dd), ing(T="Salz und Pfeffer"))
            add(f"Couscous-Salat mit {WORD[m]} und {dn}-Dressing", "M", 20, "pa", i,
                [CARB["couscous"][3], vs, cs, ds, "Couscous, Gemüse und Fleisch mischen, mit dem Dressing beträufeln und kurz durchziehen lassen."])
    # (6) Rucola-Mozzarella
    for mi, (m, g) in enumerate([("pute", 100), ("schink", 70), ("ei", 2), ("haehn", 100)]):
        ci, cs = cooked_protein(m, g)
        i = join(ci, ing(ruc=50, tom=2, moz=100, brot=2, oel=1), ing(T="Basilikum, Salz und Pfeffer"))
        add(f"Rucola-Mozzarella-Salat mit {WORD[m]} und Brot", "M", 20, "a", i,
            ["Rucola zupfen, Tomaten in Scheiben und den Mozzarella in Stücke schneiden.", cs, "Alles anrichten, mit Öl, Salz, Pfeffer und Basilikum würzen und das Brot dazu essen."])


def eier():
    # (1) Shakshuka-Art
    SPI = [("Kreuzkümmel", dict(kreuz=1, paprikap=1), "Kreuzkümmel und Paprikapulver"), ("Paprika", dict(paprikap=2), "Paprikapulver"), ("Curry", dict(curry=1.5), "Curry"), ("Garam Masala", dict(garam=1.5), "Garam Masala")]
    ADD = [("Putenhack", dict(phack=60, oel=0.5), "Das Hack in einer Pfanne krümelig anbraten, bis nichts Rosa mehr zu sehen ist.", "dem gebratenen Putenhack"),
           ("Schinken", dict(schink=40), "Den Schinken in Streifen schneiden.", "dem Schinken"),
           ("Mozzarella", dict(moz=40), "Den Mozzarella zupfen.", "dem Mozzarella"), ("Gouda", dict(gouda=25), "Den Gouda reiben.", "dem Gouda"),
           ("Joghurt", dict(jogGr=60), "Den Joghurt glatt rühren.", "einem Klecks Joghurt")]
    for si, (sn, sd, sw) in enumerate(SPI):
        for ai, (an, ad, ast, aphr) in enumerate(ADD):
            # Curry und Garam Masala passen zu Joghurt und Hack, nicht zu Käse; Kreuzkümmel und Paprika zu allem außer Joghurt
            if (ai not in (0, 4)) if si >= 2 else (ai == 4 or (si + ai) % 2):
                continue
            i = join(ing(ei=3, stueck=200, pap=1, zwie=1, knob=1, brot=2, oel=0.5), ing(**sd), ing(**ad), ing(T="Salz und Pfeffer"))
            add(f"Shakshuka mit {sn} und {an}", "M", 30, "", i,
                [ast + " Paprika und Zwiebel würfeln, Knoblauch hacken.", "Paprika, Zwiebel und Knoblauch mit " + sw + " im Öl 5 Minuten braten. Stückige Tomaten zugeben und 8 Minuten köcheln, mit Salz und Pfeffer abschmecken.",
                 "Mit einem Löffel drei Mulden in die Soße drücken und die Eier hineingleiten lassen. Zugedeckt bei niedriger Hitze 8 bis 10 Minuten garen, bis Eiweiß und Eigelb fest sind.", f"Mit {aphr} " + ("garnieren" if an == "Joghurt" else "bestreuen") + " und mit dem Brot essen."])
    # (2) Frittata
    for mi, (m, g) in enumerate([("schink", 50), ("paufs", 60), ("phack", 60)]):
        for vi, (vn, vd, vs) in enumerate([("Paprika und Tomate", dict(pap=1, tom=1, zwie=0.5), "Paprika, Tomate und Zwiebel klein schneiden."), ("Spinat und Tomate", dict(spin=100, tom=1, zwie=0.5), "Tomate und Zwiebel klein schneiden."), ("Paprika und Rucola", dict(pap=1, ruc=20, zwie=0.5), "Paprika und Zwiebel klein schneiden, den Rucola zupfen.")]):
            for ci, (cn, cd) in enumerate([("Gouda", dict(gouda=25)), ("Mozzarella", dict(moz=40)), ("Parmesan", dict(parm=10, moz=20))]):
                if (mi + vi + ci) % 3:
                    continue
                ci_, cs = cooked_protein(m, g)
                i = join(ing(ei=3, brot=1, oel=1), ci_, ing(**vd), ing(**cd), ing(T="Salz und Pfeffer"))
                add(f"Frittata mit {nl(WORD[m], vn, cn)}", "M", 25, "ga", i,
                    ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. " + vs, cs.replace(" Kurz abkühlen lassen.", ""), "Das Gemüse im Öl in einer ofenfesten Pfanne 4 Minuten anbraten" + (", bis der Spinat zusammengefallen ist" if "spin" in vd else "") + (" (den Rucola erst zum Schluss untermischen)" if "ruc" in vd else "") + ". Die Eier verquirlen, würzen und mit dem Fleisch darübergießen.",
                     "Mit dem Käse belegen und im Ofen 12 bis 15 Minuten backen, bis die Eier ganz fest sind. Mit einer Scheibe Vollkornbrot essen."])
    # (3) Rührei-Pfannen
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1, zwie=1, tom=1), "Paprika, Zwiebel und Tomate klein schneiden."), ("Tomate und Rucola", dict(tom=2, zwie=0.5, ruc=20), "Tomaten und Zwiebel klein schneiden, den Rucola zupfen.")]):
            if (mi + vi) % 2:
                continue
            pre, g, art = MEAT[m]
            i = join(ing(**{m: 70, "ei": 3, "wrap": 1, "oel": 0.5}), ing(**vd), ing(T="Paprikapulver, Salz und Pfeffer"))
            add(f"Rührei-Pfanne mit {nl(pre, vn, 'Wrap')}", "M", 20, "", i,
                [vs, meat_step(m), "Gemüse zum Hack geben und 3 Minuten mitbraten. Die Eier verquirlen, würzen und dazugeben. Unter Rühren stocken lassen, bis das Ei ganz fest ist.", "Den Wrap kurz in der Pfanne erwärmen und die Rührei-Pfanne darin einrollen oder dazu essen."])
    # (4) Gebratener Reis mit Ei
    for mi, (m, g) in enumerate([("haehn", 100), ("schink", 60), ("phack", 90), ("pute", 100), ("paufs", 80)]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1, zwie=1, gurke=100), "Paprika und Zwiebel würfeln, die Gurke in Scheiben schneiden."), ("Paprika und Tomate", dict(pap=1, zwie=1, tom=1), "Paprika, Zwiebel und Tomate würfeln.")]):
            if (mi + vi) % 2:
                continue
            ci_, cs = cooked_protein(m, g)
            i = join(ing(reis=70, ei=2, soja=1, oel=1), ci_, ing(**vd), ing(T="Pfeffer"))
            add(f"Gebratener Reis mit {nl(WORD[m], 'Ei', vn)}", "M", 25, "pa", i,
                [CARB["reis"][3] + " Am besten schon am Vortag kochen und kalt stellen.", vs, cs.replace(" Kurz abkühlen lassen.", ""),
                 "Gemüse zum Fleisch geben und 3 Minuten braten, den Reis zugeben und 4 Minuten mitbraten. Alles an den Rand schieben, die Eier in die Mitte geben und unter Rühren fest werden lassen. Mit Sojasauce und Pfeffer würzen."])


def huelsen():
    # (1) Linsen-Dal
    for si, (sn, sd, sw) in enumerate([("Curry", dict(curry=2), "Curry"), ("Kreuzkümmel und Kurkuma", dict(kreuz=1, kurkuma=1), "Kreuzkümmel und Kurkuma"), ("Garam Masala", dict(garam=1.5, kurkuma=0.5), "Garam Masala und Kurkuma")]):
        for bi, (bn, bd, bs) in enumerate([("Reis", dict(reis=60), CARB["reis"][3]), ("Vollkornbrot", dict(brot=2), "Das Brot bereitstellen."), ("Wrap", dict(wrap=1), "Den Wrap kurz in der Pfanne erwärmen.")]):
            for ti, (tn, td, ts) in enumerate([("Joghurt", dict(jogGr=60), "Joghurt glatt rühren."), ("Ei", dict(ei=2), "Die Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und halbieren."), ("Gurken-Quark", dict(speisequark=60, gurke=100), "Gurke fein würfeln und mit dem Quark verrühren.")]):
                if (si + bi + ti) % 3:
                    continue
                i = join(ing(linse=70, kokos=100, tom=2, zwie=1, knob=1, bruehe=200, oel=0.5), ing(**sd), ing(**bd), ing(**td), ing(T="Salz und Pfeffer"))
                add(f"Linsen-Dal mit {nl(sn, bn, tn)}", "M", 35, "pa", i,
                    [bs, "Tomaten und Zwiebel würfeln, Knoblauch fein hacken. " + ts, "Zwiebel und Knoblauch mit " + sw + " in einem Topf in etwas Öl 2 Minuten anrösten. Linsen, Tomaten, Kokosmilch und Brühe zugeben.", "15 bis 20 Minuten köcheln lassen, bis die Linsen weich sind, und mit Salz und Pfeffer abschmecken.", f"Mit {bn} und {tn} servieren."])
    # (2) Kichererbsen-Curry
    for ti, (tn, td, ts) in enumerate([("Ei", dict(ei=2), "Die Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und halbieren."), ("Joghurt", dict(jogGr=80), "Joghurt glatt rühren."), ("Hähnchen", dict(haehn=90, oel=0.5), "Das Hähnchen in mundgerechte Stücke schneiden.")]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1, zwie=1), "Paprika und Zwiebel würfeln."), ("Tomate", dict(tom=2, zwie=1), "Tomaten und Zwiebel würfeln."), ("Spinat", dict(spin=100, zwie=1), "Die Zwiebel würfeln.")]):
            if (ti + vi) % 2:
                continue
            i = join(ing(kiche=170, kokos=100, reis=60, curry=2, knob=1, zitrone=1, oel=0.5), ing(**vd), ing(**td), ing(T="Salz und Pfeffer"))
            huhn = tn == "Hähnchen"
            anbraten = "Zwiebel, Gemüse, Knoblauch und Curry in einem Topf 4 Minuten anbraten" + (", bis der Spinat zusammengefallen ist." if "spin" in vd else ".")
            add(f"Kichererbsen-Curry mit {nl(vn, 'Reis', tn)}", "M", 30, "pa", i,
                [CARB["reis"][3], vs + " Knoblauch fein hacken. " + ts]
                + (["Das Hähnchen im Topf in heißem Öl 6 bis 8 Minuten rundum braten, bis es durch und innen nicht mehr rosa ist, und herausnehmen."] if huhn else [])
                + [anbraten, ("Kichererbsen, Kokosmilch und das Hähnchen" if huhn else "Kichererbsen und Kokosmilch") + " zugeben und 10 Minuten köcheln. Mit Zitronensaft, Salz und Pfeffer abschmecken.",
                   "Mit dem Reis servieren." if huhn else f"Mit Reis und {tn} servieren."])
    # (3) Bohnen-Quesadilla
    for ci, (cn, cd) in enumerate([("Mozzarella", dict(moz=50)), ("Gouda", dict(gouda=35))]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1, zwie=0.5, tom=1), "Paprika, Zwiebel und Tomate klein schneiden."), ("Tomate", dict(tom=2, zwie=0.5, pap=0.5), "Tomaten, Zwiebel und Paprika klein schneiden."), ("Rucola", dict(pap=1, tom=1, ruc=30), "Paprika und Tomate klein schneiden, den Rucola zupfen.")]):
            for di, (dn, dd) in enumerate([("Joghurt", dict(jogGr=50, paprikap=1)), ("Quark", dict(quark=60, kreuz=0.5))]):
                if (ci + vi + di) % 2:
                    continue
                i = join(ing(wrap=1, bohne=120, oel=0.5), ing(**cd), ing(**vd), ing(**dd), ing(T="Salz und Pfeffer"))
                add(f"Bohnen-Quesadilla mit {nl(cn, vn, dn + '-Dip')}", "M", 20, "a", i,
                    [vs + " Die Bohnen abtropfen und mit einer Gabel grob zerdrücken.", "Bohnen, " + ("Gemüse (ohne den Rucola)" if "ruc" in vd else "Gemüse") + " und Käse auf der Hälfte jedes Wraps verteilen, würzen und die Wraps zuklappen.",
                     "In einer Pfanne mit etwas Öl von jeder Seite 3 bis 4 Minuten braten, bis der Käse geschmolzen und der Wrap goldbraun ist.", "Mit dem Dip aus " + ("Joghurt und Paprikapulver" if di == 0 else "Quark und Kreuzkümmel") + " servieren" + (" und den Rucola dazugeben." if "ruc" in vd else ".")])
    # (4) Kichererbsen-Pfanne mit Ei
    for si, (sn, sd, sw) in enumerate([("Kreuzkümmel", dict(kreuz=1.5, paprikap=0.5), "Kreuzkümmel"), ("Paprikapulver", dict(paprikap=2), "Paprikapulver"), ("Curry", dict(curry=2), "Curry")]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=2, zwie=1), "Paprika und Zwiebel würfeln."), ("Tomate", dict(tom=3, zwie=1, pap=0.5), "Tomaten, Zwiebel und Paprika würfeln.")]):
            i = join(ing(kiche=150, ei=2, brot=2, oel=1), ing(**sd), ing(**vd), ing(T="Salz und Pfeffer"))
            add(f"Kichererbsen-Pfanne mit {nl(sn, vn, 'Spiegelei')}", "M", 25, "", i,
                [vs, "Gemüse mit " + sw + " im Öl 5 Minuten anbraten. Die abgetropften Kichererbsen zugeben und 5 Minuten mitbraten, würzen.", "Die Kichererbsen an den Rand schieben und die Eier als Spiegeleier braten, bis das Eiweiß ganz fest ist (Deckel auflegen, dann wird auch das Eigelb fest).", "Mit dem Brot servieren."])
    # (5) Linsen-Gemüse-Pfanne mit Käse
    for ci, (cn, cd) in enumerate([("Gouda", dict(gouda=30)), ("Mozzarella", dict(moz=50))]):
        for vi, (vn, vd, vs) in enumerate([("Paprika und Tomate", dict(pap=2, tom=2, zwie=1), "Paprika, Tomaten und Zwiebel würfeln."), ("Paprika und Rucola", dict(pap=2, ruc=30, zwie=1, stueck=100), "Paprika und Zwiebel würfeln, den Rucola zupfen.")]):
            i = join(ing(linse=60, reis=30, bruehe=300, oel=1, paprikap=1.5, kreuz=0.5), ing(**vd), ing(**cd), ing(T="Salz und Pfeffer"))
            add(f"Linsen-Gemüse-Pfanne mit {nl(vn, cn)}", "M", 30, "pa", i,
                [vs, "Das Gemüse mit den Gewürzen im Öl 4 Minuten anbraten. Linsen, Reis und Brühe zugeben.", "Zugedeckt 15 Minuten köcheln, bis Linsen und Reis weich sind, bei Bedarf Wasser nachgießen.", f"Mit {cn} bestreuen und zugedeckt schmelzen lassen" + (", den Rucola erst zum Servieren dazugeben." if "ruc" in vd else ".")])
