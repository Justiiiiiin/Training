# -*- coding: utf-8 -*-
"""Mittag/Abend: Wraps und Brote, Nudelgerichte, Aufläufe."""
from gen_core import *
from gen_main import V, D

NAME = {"haehn": "Hähnchen", "pute": "Putenbrust", "schnitzel": "Schnitzel", "haehnst": "Mini-Steaks",
        "phack": "Putenhack", "rhack": "Rinderhack", "ghack": "Hackfleisch", "paufs": "Putenaufschnitt", "schink": "Schinken"}


def wraps():
    cont = {"wrap": ("Wrap", dict(wrap=1), "Den Wrap mit dem Dip bestreichen, Gemüse und {f} darauf verteilen, fest einrollen und halbieren."),
            "broetchen": ("Brötchen", dict(broetchen=1), "Das Brötchen aufschneiden, mit dem Dip bestreichen und mit Gemüse und {f} belegen."),
            "brot": ("Belegtes Brot", dict(brot=2), "Die Brotscheiben mit dem Dip bestreichen und mit Gemüse und {f} belegen.")}
    warm = [("haehn", 130), ("pute", 130), ("haehnst", 120), ("schnitzel", 120), ("phack", 110), ("rhack", 110)]
    cold = [("paufs", 90), ("schink", 80)]
    for ci, (ck, (cn, cd, cstep)) in enumerate(cont.items()):
        for mi, (m, g) in enumerate(warm + cold):
            for di, (dn, dd, ds) in enumerate(D):
                if (mi * 2 + di + ci) % 5:
                    continue
                vd, vs = V[(mi + di + ci) % len(V)]
                i = join(ing(**{m: g}), ing(**cd), ing(**vd), ing(**dd))
                if m in MEAT:
                    art = MEAT[m][2]
                    i = join(i, ing(oel=meat_oel(m)), ing(paprikap=1, kreuz=0.5) if art == "hack" else "")
                    extra = " Mit Paprikapulver und Kreuzkümmel würzen." if art == "hack" else (" Mit Salz und Pfeffer würzen." if art == "stk" else "")
                    steps = [vs, meat_step(m) + extra, ds, cstep.format(f="Fleisch")]
                    tags, t = "a", 20
                else:
                    steps = [vs, ds, cstep.format(f="Aufschnitt")]
                    tags, t = "ka", 10
                title = f"{cn} mit {NAME[m]} und {dn}-Dip"
                add(title, "M", t, tags, i, steps)


def nudeln():
    # (a) Bolognese
    SO = [("klassisch", dict(karo=1, zwie=1, knob=1, stueck=200, tmark=1, T="Oregano, Salz und Pfeffer"), "Karotte raspeln, Zwiebel würfeln und Knoblauch fein hacken.", "Mit der Bolognese"),
          ("mit Paprika", dict(pap=1, zwie=1, knob=1, stueck=200, tmark=1, T="Oregano, Salz und Pfeffer"), "Paprika und Zwiebel würfeln, Knoblauch fein hacken.", ""),
          ("mit frischen Tomaten", dict(tom=2, zwie=1, knob=1, stueck=150, tmark=1, T="Basilikum, Salz und Pfeffer"), "Tomaten und Zwiebel würfeln, Knoblauch fein hacken.", "")]
    for m, g, extra in [("rhack", 120, {}), ("phack", 130, {}), ("ghack", 110, {}), ("rhack", 80, dict(linse=30))]:
        for sn, sd, sp, _ in SO:
            pre = MEAT[m][0]
            lin = bool(extra)
            ti = f"{'Linsen-' if lin else ''}{pre}-Bolognese " + (f"{sn} und Vollkornnudeln" if sn.startswith("mit") else f"{sn} mit Vollkornnudeln")
            i = join(ing(**{m: g, "nudel": 80, "oel": 0.5, "parm": 10}), ing(**sd), ing(**extra))
            steps = [CARB["nudel"][3], sp,
                     meat_step(m) + (" Die Linsen mit 150 ml Wasser dazugeben." if lin else ""),
                     "Gemüse und Tomatenmark zugeben und 3 Minuten mitbraten. Stückige Tomaten zugeben und " + ("20 Minuten, bis die Linsen weich sind," if lin else "15 Minuten") + " bei niedriger Hitze köcheln lassen, bei Bedarf etwas Wasser nachgießen. Würzen.",
                     "Die Nudeln mit der Soße mischen und mit Parmesan bestreuen."]
            add(ti, "M", 35 if not lin else 40, "pa", i, steps)
    # (b) Tomatensoße mit Fleisch
    TS = [("Tomaten-Rucola-Parmesan", dict(tom=3, ruc=30, parm=10, knob=1, T="Salz und Pfeffer"), "Tomaten in Stücke schneiden, Knoblauch fein hacken.",
           "Knoblauch und Tomaten zum Fleisch geben und 6 Minuten schmoren. Mit Salz und Pfeffer würzen.", "Die Nudeln untermischen, Rucola und Parmesan darauf verteilen."),
          ("Paprika-Mozzarella", dict(pap=2, zwie=1, stueck=150, moz=40, T="Oregano, Salz und Pfeffer"), "Paprika und Zwiebel in Stücke schneiden, Mozzarella zupfen.",
           "Paprika und Zwiebel zum Fleisch geben, 4 Minuten braten, die stückigen Tomaten zugeben und 8 Minuten köcheln.", "Die Nudeln untermischen und den Mozzarella darauf schmelzen lassen."),
          ("Tomaten-Basilikum", dict(stueck=200, tom=1, zwie=1, knob=1, moz=30, T="Basilikum, Salz und Pfeffer"), "Zwiebel würfeln, Knoblauch hacken, Tomate in Stücke schneiden.",
           "Zwiebel und Knoblauch zum Fleisch geben, 2 Minuten braten, Tomaten zugeben und 8 Minuten köcheln.", "Die Nudeln untermischen, Mozzarella zupfen und Basilikum darauf verteilen."),
          ("Arrabbiata", dict(stueck=200, zwie=1, knob=2, paprikap=1, parm=10, T="Chiliflocken, Salz und Pfeffer"), "Zwiebel würfeln, Knoblauch fein hacken.",
           "Zwiebel, Knoblauch und Paprikapulver zum Fleisch geben, 2 Minuten braten, stückige Tomaten zugeben und 10 Minuten köcheln. Mit Chili würzen.", "Die Nudeln untermischen und Parmesan darüberhobeln.")]
    for si, (sn, sd, sp, sc, ss) in enumerate(TS):
        for mi, m in enumerate(["haehn", "pute", "haehnst", "schnitzel", "phack"]):
            if (mi + si) % 3 == 2:
                continue
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g - 20, "nudel": 80, "oel": meat_oel(m)}), ing(**sd))
            add(f"{pre}-Nudeln mit {sn}-Soße", "M", 25, "pa", i, [CARB["nudel"][3], sp, meat_step(m), sc, ss])
    # (c) Spinat-Quark-Nudeln
    for mi, (m, g) in enumerate([("haehn", 130), ("pute", 130), ("schink", 70), ("ei", 2)]):
        for vi, (vn, vd, vs) in enumerate([("Tomate", dict(tom=2), "Tomaten würfeln."), ("Paprika", dict(pap=1), "Paprika würfeln.")]):
            if (mi + vi) % 2:
                continue
            fleisch = [meat_step(m)] if m in MEAT else (["Den Schinken in Streifen schneiden."] if m == "schink" else ["Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und vierteln."])
            i = join(ing(**{m: g, "nudel": 80, "spin": 150, "speisequark": 80, "knob": 1, "parm": 10}), ing(**vd), ing(oel=0.5 if m in ("haehn", "pute") else 0.5), ing(T="Salz, Pfeffer und Muskat"))
            nm = {"haehn": "Hähnchen", "pute": "Pute", "schink": "Schinken", "ei": "Ei"}[m]
            add(f"Spinat-Quark-Nudeln mit {nm} und {vn}", "M", 25, "p", i,
                [CARB["nudel"][3], vs + " Knoblauch fein hacken."] + fleisch +
                ["Spinat mit dem Knoblauch in einer Pfanne zusammenfallen lassen (Tiefkühlspinat 5 bis 7 Minuten garen) und das Gemüse kurz mitbraten.",
                 f"Quark unterrühren, mit Salz, Pfeffer und Muskat würzen und die Nudeln untermischen. {({'haehn': 'Das Hähnchen', 'pute': 'Die Pute', 'schink': 'Den Schinken', 'ei': 'Die Eier'})[m]} und den Parmesan daraufgeben."])
    # (d) Carbonara-Art mit Ei, voll gegart
    for mi, (m, g) in enumerate([("schink", 60), ("paufs", 60), ("lyoner", 50), ("haehn", 100)]):
        for vi, (vn, vd, vs) in enumerate([("Tomate und Rucola", dict(tom=2, ruc=30), "Tomaten würfeln."), ("Paprika und Tomate", dict(pap=1, tom=1), "Paprika und Tomate würfeln."), ("Tomate", dict(tom=3), "Tomaten würfeln.")]):
            if (mi + vi) % 2:
                continue
            nm = {"schink": "Schinken", "paufs": "Putenaufschnitt", "lyoner": "Lyoner", "haehn": "Hähnchen"}[m]
            i = join(ing(**{m: g, "nudel": 80, "ei": 1, "parm": 15, "oel": 0.5}), ing(**vd), ing(T="Pfeffer"))
            first = "Hähnchen in Streifen schneiden und im Öl 5 bis 7 Minuten braten, bis es durch ist." if m == "haehn" else f"{nm} in Streifen schneiden und im Öl 3 Minuten anbraten."
            add(f"{nm}-Nudeln mit {vn} in Parmesan-Ei-Soße", "M", 25, "p", i,
                [CARB["nudel"][3], "Ei mit dem fein geriebenen Parmesan und Pfeffer verquirlen. " + vs, first + " Das Gemüse kurz mitbraten.",
                 "Die Nudeln abgießen (eine Tasse Nudelwasser aufheben) und in die Pfanne geben. Die Pfanne vom Herd ziehen, die Eiermasse unterrühren und bei niedriger Hitze unter Rühren 1 bis 2 Minuten erwärmen, bis die Soße gestockt und das Ei ganz fest ist. Bei Bedarf etwas Nudelwasser zugeben."])
    # (e) Paprika-Quark-Soße
    for mi, m in enumerate(["haehn", "pute", "phack", "schnitzel", "haehnst"]):
        for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=2, zwie=1), "Paprika und Zwiebel in Streifen schneiden."), ("Paprika-Tomaten", dict(pap=1, tom=2, zwie=1), "Paprika, Tomaten und Zwiebel in Stücke schneiden.")]):
            if (mi + vi) % 2:
                continue
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g - 20, "nudel": 80, "speisequark": 100, "paprikap": 1, "oel": meat_oel(m)}), ing(**vd), ing(T="Salz und Pfeffer"))
            add(f"{pre}-Nudeln mit {vn}-Quark-Soße", "M", 25, "p", i,
                [CARB["nudel"][3], vs, meat_step(m), "Das Gemüse mit Paprikapulver zum Fleisch geben und 6 Minuten schmoren. Die Pfanne vom Herd ziehen, den Quark unterrühren (nicht mehr kochen) und würzen.",
                 "Die Nudeln untermischen."])
    # (f) Nudelsalat
    for mi, (m, g) in enumerate([("haehn", 110), ("pute", 110), ("paufs", 80), ("schink", 70), ("ei", 2)]):
        for di, (dn, dd, ds) in enumerate(D):
            if (mi * 2 + di) % 5:
                continue
            vd, vs = V[(mi + di) % len(V)]
            nm = {"haehn": "Hähnchen", "pute": "Pute", "paufs": "Putenaufschnitt", "schink": "Schinken", "ei": "Ei"}[m]
            if m in ("haehn", "pute"):
                first = ["Das Fleisch in Würfel schneiden und im Öl 6 bis 8 Minuten braten, bis es durch und innen nicht mehr rosa ist, dann abkühlen lassen."]; extra = ing(oel=1)
            elif m == "ei":
                first = ["Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und vierteln."]; extra = ""
            else:
                first = [f"{nm} in Streifen schneiden."]; extra = ""
            i = join(ing(**{m: g, "nudel": 70}), ing(**vd), ing(**dd), extra)
            add(f"Nudelsalat mit {nm} und {dn}-Dressing", "M", 25, "pa", i,
                [CARB["nudel"][3] + " Abgießen und kalt abspülen.", vs] + first + [ds, "Alles in einer Schüssel mischen und mindestens 15 Minuten durchziehen lassen."])
    # (g) Aglio e Olio
    for m in ["haehn", "pute"]:
        for vn, vd, vs in [("Tomate und Rucola", dict(tom=3, ruc=30), "Tomaten halbieren."), ("Paprika und Tomate", dict(pap=1, tom=2), "Paprika und Tomaten in Stücke schneiden.")]:
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g - 20, "nudel": 80, "oel": 2, "knob": 2, "parm": 10}), ing(**vd), ing(T="Chiliflocken, Salz und Pfeffer"))
            add(f"{pre}-Nudeln Aglio e Olio mit {vn}", "M", 25, "", i,
                [CARB["nudel"][3] + " Etwas Nudelwasser aufheben.", vs + " Knoblauch in dünne Scheiben schneiden.", meat_step(m), "Knoblauch und Chili zum Fleisch geben und 1 Minute mitbraten (der Knoblauch soll nicht braun werden). Gemüse zugeben und 3 Minuten schmoren.",
                 "Die Nudeln mit einem Schuss Nudelwasser untermischen und mit Parmesan bestreuen."])


def sahnenudeln():
    """Nudeln mit Sahne: Tomaten-Sahne-Soße mit Burrata obendrauf, Parmesan-Sahne-Soße, überbackene Sahne-Nudeln und Zitronen-Nudeln mit Burrata.
    Burrata kommt immer erst zum Schluss auf den Teller (nicht erhitzen). Eine Kugel (125 g) reicht für zwei Portionen."""
    nw = CARB["nudel"][3] + " Etwas Nudelwasser aufheben."
    tipb = "Eine Kugel Burrata (125 g) reicht für zwei Portionen. Nach dem Öffnen bald essen (siehe Packung)."
    kurz = {"schink": ("Schinken", 60, "Den Schinken in Würfel schneiden und im Öl 2 Minuten anbraten.", 0.5)}

    def fleisch(m, g_fleisch):
        """(Titelwort, Menge, Brat-Schritt, Öl in TL) für Fleisch aus MEAT oder Schinken."""
        if m in kurz:
            n, g, st, o = kurz[m]
            return n, g_fleisch or g, st, o
        pre, g, art = MEAT[m]
        return pre, g_fleisch or g, meat_step(m), meat_oel(m)

    # (a) Tomaten-Sahne-Soße mit Burrata
    soss = ("Die stückigen Tomaten zugeben, mit dem Löffel etwas zerdrücken und 6 Minuten köcheln lassen. "
            "Die Sahne einrühren und 2 Minuten sanft kochen, mit Salz, Pfeffer und Basilikum abschmecken.")
    for vn, vd, vp, vc, top, sa in [
        ("Rucola", dict(tom=1, ruc=20), "Zwiebel würfeln, Knoblauch fein hacken, Tomate in Stücke schneiden.",
         "Zwiebel im Öl 3 Minuten glasig dünsten, Knoblauch kurz mitbraten. ",
         "Die Nudeln mit der Soße mischen, bei Bedarf einen Schuss Nudelwasser zugeben. Auf Tellern verteilen, die Burrata darauf zerzupfen und Rucola und Parmesan darübergeben.", 30),
        ("Paprika", dict(pap=1), "Zwiebel würfeln, Knoblauch fein hacken, Paprika in Stücke schneiden.",
         "Zwiebel und Paprika im Öl 4 Minuten anbraten, Knoblauch kurz mitbraten. ",
         "Die Nudeln mit der Soße mischen, bei Bedarf einen Schuss Nudelwasser zugeben. Auf Tellern verteilen, die Burrata darauf zerzupfen und mit dem Parmesan bestreuen.", 25)]:
        i = join(ing(nudel=60, burrata=60, parm=15, oel=0.5), ing(zwie=0.5, knob=1, stueck=200, sahne=sa, T="Basilikum, Salz und Pfeffer"), ing(**vd))
        add(f"Tomaten-Sahne-Nudeln mit Burrata und {vn}", "M", 25, "", i, [nw, vp, vc + soss, top], tipb)
    for m in ["haehn", "pute", "schink", "haehnst"]:
        pre, g, st, o = fleisch(m, 80 if m != "schink" else 60)
        i = join(ing(**{m: g, "nudel": 60, "burrata": 60, "oel": 0.5}), ing(zwie=0.5, knob=1, stueck=200, sahne=25, tom=1, T="Basilikum, Salz und Pfeffer"))
        add(f"{pre}-Nudeln in Tomaten-Sahne-Soße mit Burrata", "M", 30, "", i,
            [nw, "Zwiebel würfeln, Knoblauch fein hacken, Tomate in Stücke schneiden.", st,
             "Zwiebel und Knoblauch zum Fleisch geben und 3 Minuten mitbraten. " + soss,
             "Die Nudeln mit der Soße mischen, bei Bedarf einen Schuss Nudelwasser zugeben. Auf Tellern verteilen und die Burrata darauf zerzupfen."], tipb)

    # (b) Parmesan-Sahne-Soße
    for m in ["haehn", "pute", "schink"]:
        pre, g, st, o = fleisch(m, 90 if m != "schink" else 70)
        i = join(ing(**{m: g, "nudel": 70, "sahne": 40, "parm": 15, "oel": o}), ing(zwie=0.5, knob=1, tom=2, ruc=20, T="Muskat, Salz und Pfeffer"))
        add(f"{pre}-Nudeln in Parmesan-Sahne-Soße mit Tomate und Rucola", "M", 25, "p", i,
            [nw, "Zwiebel würfeln, Knoblauch fein hacken, Tomaten in Stücke schneiden.", st,
             "Zwiebel und Knoblauch zum Fleisch geben und 2 Minuten mitbraten. Die Sahne zugießen und bei niedriger Hitze 2 Minuten köcheln lassen. Den Parmesan einrühren, bis er geschmolzen ist, und mit Muskat, Salz und Pfeffer würzen.",
             "Die Tomaten zugeben und 2 Minuten ziehen lassen. Die Nudeln untermischen, bei Bedarf einen Schuss Nudelwasser zugeben, und den Rucola daraufgeben."])

    # (c) Überbackene Tomaten-Sahne-Nudeln
    for m in ["haehn", "pute", "schink"]:
        pre, g, st, o = fleisch(m, 80 if m != "schink" else 60)
        nm = {"Hähnchen": "Hähnchen", "Puten": "Pute", "Schinken": "Schinken"}[pre]
        i = join(ing(**{m: g, "nudel": 60, "moz": 40, "oel": o}), ing(zwie=0.5, knob=1, stueck=200, sahne=30, tom=1, T="Oregano, Salz und Pfeffer"))
        add(f"Überbackene Tomaten-Sahne-Nudeln mit {nm} und Mozzarella", "M", 40, "p", i,
            ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. Die Nudeln 3 Minuten kürzer als auf der Packung angegeben kochen.", "Zwiebel würfeln, Knoblauch fein hacken, Tomate in Stücke schneiden, Mozzarella zupfen.", st,
             "Zwiebel und Knoblauch zum Fleisch geben und 3 Minuten mitbraten. Stückige Tomaten, Tomate und Sahne zugeben, 5 Minuten köcheln lassen und mit Oregano, Salz und Pfeffer abschmecken.",
             "Nudeln und Soße in einer Auflaufform mischen, den Mozzarella darauf verteilen und 15 bis 20 Minuten backen, bis der Käse goldbraun ist."])

    # (d) Zitronen-Nudeln mit Burrata
    for m, g_f in [(None, 0), ("haehn", 90)]:
        if m:
            pre, g, st, o = fleisch(m, g_f)
            titel = f"{pre}-Zitronen-Nudeln mit Rucola, Tomate und Burrata"
            i = join(ing(**{m: g, "nudel": 70, "burrata": 50, "parm": 10, "oel": o + 0.5}), ing(tom=2, ruc=30, zitrone=2, knob=1, T="Chiliflocken, Salz und Pfeffer"))
            steps = [nw, "Tomaten in Stücke schneiden, Knoblauch fein hacken.", st,
                     "Knoblauch und Chili zum Fleisch geben und 1 Minute mitbraten (der Knoblauch soll nicht braun werden). Tomaten zugeben und 3 Minuten schmoren."]
        else:
            titel = "Zitronen-Nudeln mit Rucola, Tomate und Burrata"
            i = join(ing(nudel=70, burrata=75, parm=15, oel=1), ing(tom=3, ruc=30, zitrone=2, knob=1, T="Chiliflocken, Salz und Pfeffer"))
            steps = [nw, "Tomaten in Stücke schneiden, Knoblauch fein hacken.",
                     "Knoblauch und Chili im Öl 1 Minute anbraten (der Knoblauch soll nicht braun werden). Tomaten zugeben und 3 Minuten schmoren."]
        add(titel, "M", 25, "", i, steps + ["Die Nudeln mit Zitronensaft und einem Schuss Nudelwasser untermischen, bis eine leicht cremige Soße entsteht. Den Rucola unterheben.",
                                           "Auf Tellern verteilen, die Burrata darauf zerzupfen und den Parmesan darüberhobeln."], tipb)


def auflaeufe():
    # (a) Nudelauflauf
    for mi, m in enumerate(["haehn", "pute", "phack", "rhack", "schink"]):
        for si, (sn, sd, sp, cheese) in enumerate([("Paprika und Mozzarella", dict(pap=1, zwie=1, stueck=200, knob=1), "Paprika und Zwiebel in Stücke schneiden, Knoblauch hacken.", dict(moz=50)),
                                                    ("Tomate und Gouda", dict(tom=2, zwie=1, stueck=150, knob=1), "Tomaten und Zwiebel in Stücke schneiden, Knoblauch hacken.", dict(gouda=30)),
                                                    ("Rucola und Parmesan", dict(pap=1, tom=1, stueck=150, ruc=30), "Paprika und Tomate in Stücke schneiden.", dict(moz=40, parm=10))]):
            if (mi + si) % 3 == 2:
                continue
            nm = {"haehn": "Hähnchen", "pute": "Puten", "phack": "Putenhack", "rhack": "Rinderhack", "schink": "Schinken"}[m]
            if m == "schink":
                g = 70; fleisch = "Den Schinken in Streifen schneiden."; oel = 0
            else:
                g = MEAT[m][1] - 20; fleisch = meat_step(m); oel = meat_oel(m)
            i = join(ing(**{m: g, "nudel": 70}), ing(**sd), ing(**cheese), ing(T="Oregano, Salz und Pfeffer"), ing(oel=oel) if oel else "")
            ruc = "Rucola erst nach dem Backen darauflegen. " if "ruc" in sd else ""
            add(f"{nm}-Nudelauflauf mit {sn}", "M", 45, "p", i,
                ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. Nudeln 3 Minuten kürzer als auf der Packung angegeben kochen.", sp, fleisch,
                 ("Schinken" if m == "schink" else "Fleisch") + ", Gemüse, stückige Tomaten, Nudeln und Gewürze in einer Auflaufform mischen. Mit dem Käse belegen.",
                 "20 bis 25 Minuten backen, bis der Käse goldbraun ist. " + ruc.strip()])
    # (b) Reis-Auflauf
    for mi, m in enumerate(["haehn", "pute", "phack", "rhack", "schnitzel"]):
        for si, (sn, sd, sp) in enumerate([("Paprika", dict(pap=2, zwie=1, tom=1), "Paprika, Zwiebel und Tomate in Stücke schneiden."), ("Tomate", dict(tom=3, zwie=1, pap=0.5), "Tomaten, Zwiebel und Paprika in Stücke schneiden.")]):
            if (mi + si) % 2:
                continue
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g - 20, "reis": 50, "oel": meat_oel(m), "moz": 50, "knob": 1}), ing(**sd), ing(T="Oregano, Salz und Pfeffer"))
            add(f"Reis-Auflauf mit {NAME[m]} und {sn} unter Mozzarella", "M", 40, "p", i,
                ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. Reis nach Packungsanleitung kochen.", sp + " Knoblauch fein hacken.", meat_step(m),
                 "Fleisch, Gemüse, Reis, Knoblauch und Gewürze in einer Auflaufform mischen und mit Mozzarella belegen.", "20 bis 25 Minuten backen, bis der Käse goldbraun ist."])
    # (c) gefüllte Paprika und Tomaten
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for ci, c in enumerate(["reis"]):
            for chi, (cn, cheese) in enumerate([("Mozzarella", dict(moz=40)), ("Gouda", dict(gouda=30))]):
                pre, g, art = MEAT[m]
                cw = CARB[c][0]
                i = join(ing(**{m: g, c: 50, "pap": 2, "zwie": 1, "stueck": 150, "tmark": 1, "oel": 0.5}), ing(**cheese), ing(T="Paprikapulver, Salz und Pfeffer"))
                add(f"Gefüllte Paprika mit {pre}, {cw} und {cn}", "M", 50, "p", i,
                    [CARB[c][3], "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Paprika halbieren, entkernen und mit der Schnittfläche nach oben in eine Form legen. Zwiebel würfeln.", meat_step(m),
                     f"Zwiebel, Tomatenmark und Gewürze zum Hack geben, 2 Minuten braten, mit dem {cw} mischen und in die Paprikahälften füllen. Die stückigen Tomaten um die Paprika gießen.",
                     "Mit dem Käse belegen und 25 bis 30 Minuten backen, bis die Paprika weich sind."])
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        pre, g, art = MEAT[m]
        i = join(ing(**{m: g, "reis": 50, "tom": 4, "zwie": 1, "knob": 1, "moz": 40, "oel": 0.5}), ing(T="Oregano, Salz und Pfeffer"))
        add(f"Gefüllte Tomaten mit {pre} und Reis", "M", 45, "", i,
            [CARB["reis"][3], "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Von den Tomaten einen Deckel abschneiden und die Tomaten mit einem Löffel aushöhlen. Das Innere klein schneiden.", meat_step(m),
             "Zwiebel und Knoblauch fein würfeln, mit dem Tomateninneren zum Hack geben, 3 Minuten braten und mit dem Reis, Oregano, Salz und Pfeffer mischen.", "Die Tomaten füllen, Mozzarella daraufgeben und 20 bis 25 Minuten backen."])
    # (d) Auflauf ohne Beilage: Fleisch, Tomate, Mozzarella
    for mi, m in enumerate(["haehn", "pute", "schnitzel", "phack", "haehnst"]):
        for vi, (vn, vd, vs) in enumerate([("Tomaten", dict(tom=4, zwie=1), "Tomaten in Scheiben, Zwiebel in Ringe schneiden."), ("Paprika-Tomaten", dict(pap=1, tom=2, zwie=1), "Paprika in Streifen, Tomaten in Scheiben und die Zwiebel in Ringe schneiden.")]):
            pre, g, art = MEAT[m]
            if art == "hack" and vi:
                continue
            i = join(ing(**{m: g, "moz": 60, "brot": 1, "oel": meat_oel(m)}), ing(**vd), ing(T="Oregano, Salz und Pfeffer"))
            add(f"{pre}-Auflauf mit {vn} und Mozzarella", "M", 40, "", i,
                ["Ofen auf 200 °C Ober- und Unterhitze vorheizen.", vs, meat_step(m),
                 "Fleisch in eine Auflaufform geben, Gemüse darüber verteilen, würzen und mit Mozzarella belegen.", "20 Minuten backen, bis der Käse goldbraun ist. Dazu eine Scheibe Vollkornbrot essen."])
    # (e) Hack-Gemüse-Auflauf mit Gouda-Haube
    for mi, m in enumerate(["rhack", "phack", "ghack"]):
        for vi, (vn, vd, vs) in enumerate([("Paprika-Tomaten", dict(pap=2, tom=2, zwie=1, knob=1), "Paprika, Tomaten und Zwiebel würfeln, Knoblauch hacken."), ("Paprika", dict(pap=2, zwie=1, stueck=200, knob=1), "Paprika und Zwiebel würfeln, Knoblauch hacken.")]):
            pre, g, art = MEAT[m]
            i = join(ing(**{m: g, "nudel": 50, "gouda": 40, "tmark": 1, "oel": 0.5}), ing(**vd), ing(T="Paprikapulver, Salz und Pfeffer"))
            add(f"{pre}-Gemüse-Auflauf mit {vn} und Gouda-Haube", "M", 45, "p", i,
                ["Nudeln 3 Minuten kürzer als auf der Packung angegeben kochen.", "Ofen auf 200 °C Ober- und Unterhitze vorheizen. " + vs, meat_step(m),
                 "Gemüse und Tomatenmark zum Hack geben, 5 Minuten braten, mit den Nudeln mischen und würzen. In eine Form füllen.", "Den Gouda reiben, darüberstreuen und 20 Minuten backen."])
