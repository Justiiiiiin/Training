# -*- coding: utf-8 -*-
"""Frühstück und Snacks aus Bausteinen. run() fügt am Ende genau so viele hinzu, dass insgesamt 700 erzeugte Rezepte entstehen."""
import gen_core
from gen_core import *

TOTAL = 700

FR = {"banane": (dict(banane=1), "Banane", "Die Banane in Scheiben schneiden."),
      "erdb": (dict(erdb=150), "Erdbeeren", "Erdbeeren in Stücke schneiden oder auftauen lassen."),
      "beide": (dict(banane=0.5, erdb=80), "Banane und Erdbeeren", "Banane in Scheiben und Erdbeeren in Stücke schneiden.")}
FR_S = {"banane": (dict(banane=0.5), "Banane", "Die Banane in Scheiben schneiden."),
        "erdb": (dict(erdb=100), "Erdbeeren", "Erdbeeren in Stücke schneiden oder auftauen lassen."),
        "beide": (dict(banane=0.5, erdb=60), "Banane und Erdbeeren", "Banane in Scheiben und Erdbeeren in Stücke schneiden.")}
TOP = [("Haferflocken", dict(hafer=30), "Haferflocken darüberstreuen."),
       ("Haferflocken und Mandeln", dict(hafer=30, mandel=10), "Haferflocken und gehackte Mandeln darüberstreuen."),
       ("Chia und Honig", dict(chia=10, honig=1), "Chia-Samen daraufstreuen und mit Honig beträufeln."),
       ("Kakao und Mandeln", dict(kakao=1, mandel=10), "Kakao daraufsieben und gehackte Mandeln darüberstreuen."),
       ("Honig und Zimt", dict(honig=1, T="Zimt"), "Mit Honig beträufeln und mit Zimt bestäuben."),
       ("Haferflocken und Kakao", dict(hafer=20, kakao=1), "Haferflocken und Kakao daraufgeben."),
       ("Mandeln", dict(mandel=15), "Gehackte Mandeln daraufstreuen."),
       ("Chia und Haferflocken", dict(chia=10, hafer=20), "Chia-Samen und Haferflocken daraufgeben.")]
BASES = [("Skyr", dict(skyr=200)), ("Quark", dict(quark=200)), ("Speisequark", dict(speisequark=170)), ("Skyr-Quark", dict(skyr=100, quark=100)),
         ("Joghurt-Quark", dict(jogGr=120, quark=100)), ("Naturjoghurt-Quark", dict(jog35=150, quark=100))]


def fruehstueck():
    # (1) Bowls
    for bi, (bn, bd) in enumerate(BASES):
        for fi, (fk, (fd, fn, fs)) in enumerate(FR.items()):
            for ti, (tn, td, ts) in enumerate(TOP):
                if (bi + fi * 2 + ti) % 4:
                    continue
                add(f"{bn}-Bowl mit {nl(fn, tn)}", "F", 4, "kg", join(ing(**bd), ing(**fd), ing(**td)),
                    [fs, f"{bn} in eine Schüssel geben und die Frucht darauf verteilen.", ts])
    # (2) Overnight Oats
    for pi, (pn, pd) in enumerate([("Skyr", dict(skyr=100)), ("Quark", dict(quark=100)), ("Speisequark", dict(speisequark=90))]):
        for fi, (fk, (fd, fn, fs)) in enumerate(FR.items()):
            for li, (ln, ld, ls) in enumerate([("Kakao", dict(kakao=1), "Kakao"), ("Zimt", dict(T="Zimt"), "Zimt"), ("Honig und Mandeln", dict(honig=1, mandel=10), "Honig und gehackten Mandeln"), ("Chia", dict(chia=10), "Chia-Samen")]):
                if (pi + fi + li) % 2:
                    continue
                add(f"Overnight Oats mit {nl(pn, fn, ln)}", "F", 5, "kpa", join(ing(hafer=50, milch=120), ing(**pd), ing(**fd), ing(**ld)),
                    [f"Haferflocken, Milch und {pn} im Glas verrühren" + (" und die Chia-Samen unterrühren." if "chia" in ld else (", mit Zimt würzen." if "T" in ld else (" und den Kakao unterrühren." if "kakao" in ld else "."))),
                     fs + " Die Frucht unterheben.", "Abgedeckt über Nacht (mindestens 4 Stunden) in den Kühlschrank stellen.",
                     "Am Morgen " + ("mit Honig und gehackten Mandeln toppen." if "honig" in ld else "umrühren und direkt essen.")])
    # (3) Porridge
    for pi, (pn, pd) in enumerate([("Quark", dict(quark=100)), ("Skyr", dict(skyr=100))]):
        for fi, (fk, (fd, fn, fs)) in enumerate(FR.items()):
            for li, (ln, ld, ls) in enumerate([("Honig", dict(honig=1), "Mit Honig süßen."), ("Mandeln und Zimt", dict(mandel=10, T="Zimt"), "Mit gehackten Mandeln und Zimt toppen."), ("Kakao", dict(kakao=1), "Den Kakao unterrühren.")]):
                if (pi + fi + li) % 3 == 2:
                    continue
                add(f"Porridge mit {nl(pn, fn, ln)}", "F", 8, "g", join(ing(hafer=50, milch=250), ing(**pd), ing(**fd), ing(**ld)),
                    ["Haferflocken mit der Milch unter Rühren 4 bis 5 Minuten bei mittlerer Hitze köcheln, bis der Brei cremig ist.", fs, f"Den Topf vom Herd nehmen, kurz abkühlen lassen und {pn} unterrühren (nicht mehr kochen).", f"Frucht daraufgeben. {ls}"])
    # (4) Brotfrühstück
    BR = [("Gouda", dict(gouda=40), "Das Brot mit dem Gouda belegen."), ("Mozzarella", dict(moz=50), "Das Brot mit Mozzarellascheiben belegen."), ("Kochschinken", dict(schink=50), "Das Brot mit dem Schinken belegen."),
          ("Putenaufschnitt", dict(paufs=60), "Das Brot mit dem Putenaufschnitt belegen."), ("Lyoner", dict(lyoner=40), "Das Brot mit der Lyoner belegen."),
          ("Ei", dict(ei=2), "Eier mindestens 8 Minuten hart kochen (gern am Vortag), abschrecken, pellen und in Scheiben schneiden. Das Brot damit belegen."),
          ("Speisequark", dict(speisequark=80, T="Salz und Pfeffer"), "Den Quark mit Salz und Pfeffer verrühren und auf dem Brot verstreichen."),
          ("Kräuter-Skyr", dict(skyr=100, T="Kräuter, Salz und Pfeffer"), "Den Skyr mit Kräutern, Salz und Pfeffer verrühren und auf dem Brot verstreichen."),
          ("Gouda und Schinken", dict(gouda=25, schink=30), "Das Brot mit Schinken und Gouda belegen.")]
    VG = [("Gurke", dict(gurke=100), "Die Gurke in Scheiben schneiden."), ("Tomate", dict(tom=1), "Die Tomate in Scheiben schneiden."), ("Tomate und Rucola", dict(tom=1, ruc=15), "Die Tomate in Scheiben schneiden, den Rucola zupfen."),
          ("Paprika", dict(pap=0.5), "Die Paprika in Streifen schneiden."), ("Saurer Gurke", dict(sgurke=2), "Die Saure Gurke in Scheiben schneiden.")]
    for bi, (bn, bd, bs) in enumerate(BR):
        for vi, (vn, vd, vs) in enumerate(VG):
            if (bi + vi * 2) % 3:
                continue
            kalt = "k" if bn != "Ei" else ""
            add(f"Vollkornbrot mit {nl(bn, vn)}", "F", 4 if bn != "Ei" else 12, kalt + "ga", join(ing(brot=2), ing(**bd), ing(**vd)), [vs, bs, "Mit Pfeffer würzen."] if bn != "Ei" else [bs.split(". ")[0] + ".", vs, "Das Brot mit Eiern und Gemüse belegen und würzen."])
    # (5) Rührei und Omelett
    for vi, (vn, vd, vs) in enumerate([("Paprika", dict(pap=1), "Paprika klein schneiden."), ("Tomate und Zwiebel", dict(tom=1, zwie=0.5), "Tomate und Zwiebel klein schneiden."), ("Spinat", dict(spin=80), "Den Spinat (Tiefkühlspinat vorher auftauen) bereitstellen."), ("Tomate und Rucola", dict(tom=1, ruc=20), "Die Tomate klein schneiden, den Rucola zupfen.")]):
        for fi, (fn, fd, fs) in enumerate([("Schinken", dict(schink=30), "Schinken in Streifen"), ("Gouda", dict(gouda=20), "Gouda gerieben"), ("Mozzarella", dict(moz=40), "Mozzarella gezupft"), ("Putenaufschnitt", dict(paufs=40), "Putenaufschnitt in Streifen")]):
            for si, (sn, sd) in enumerate([("Brot", dict(brot=2)), ("Brötchen", dict(broetchen=1)), ("Wrap", dict(wrap=1))]):
                if (vi + fi + si) % 3:
                    continue
                add(f"Rührei mit {nl(vn, fn, sn)}", "F", 10, "ga", join(ing(ei=3, oel=1), ing(**vd), ing(**fd), ing(**sd), ing(T="Salz und Pfeffer")),
                    [vs, "Das Gemüse im Öl 3 Minuten anbraten" + (" (den Rucola erst am Ende dazugeben)." if "ruc" in vd else "."), f"Die Eier verquirlen, würzen und dazugeben. Unter Rühren bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist. {fs} untermischen.", SIDE_MIT[sn]])
    for vi, (vn, vd, vs) in enumerate([("Paprika und Zwiebel", dict(pap=1, zwie=0.5), "Paprika und Zwiebel klein schneiden."), ("Tomate", dict(tom=2), "Tomaten in Scheiben schneiden."), ("Spinat", dict(spin=100), "Den Spinat bereitstellen.")]):
        for fi, (fn, fd) in enumerate([("Schinken und Gouda", dict(schink=30, gouda=20)), ("Mozzarella", dict(moz=50)), ("Putenaufschnitt und Parmesan", dict(paufs=40, parm=10))]):
            if (vi + fi) % 2:
                continue
            add(f"Gefülltes Omelett mit {nl(vn, fn)}", "F", 12, "g", join(ing(ei=3, oel=1, brot=1), ing(**vd), ing(**fd), ing(T="Salz und Pfeffer")),
                [vs, "Das Gemüse im Öl 3 Minuten anbraten und herausnehmen (Spinat zusammenfallen lassen).", "Die Eier verquirlen, würzen und in die Pfanne geben. Bei mittlerer Hitze fast stocken lassen.", f"Gemüse und {fn} auf eine Hälfte legen, zuklappen und 1 bis 2 Minuten ziehen lassen, bis das Ei ganz fest ist.", "Mit einer Scheibe Brot essen."])
    # (6) Ei-Muffins
    for fi, (fn, fd) in enumerate([("Schinken", dict(schink=30)), ("Putenaufschnitt", dict(paufs=40)), ("Mozzarella", dict(moz=40))]):
        for vi, (vn, vd) in enumerate([("Paprika", dict(pap=0.5, zwie=0.25)), ("Tomate", dict(tom=1, zwie=0.25))]):
            add(f"Ei-Muffins mit {nl(fn, vn)}", "F", 25, "pga", join(ing(ei=3, gouda=20), ing(**fd), ing(**vd), ing(T="Salz und Pfeffer")),
                ["Ofen auf 180 °C Ober- und Unterhitze vorheizen. Eine Muffinform einfetten oder mit Papierförmchen auslegen.", "Gemüse und Fleisch (oder Mozzarella) klein schneiden und in den Mulden verteilen.", "Die Eier verquirlen, würzen, mit dem Gouda mischen und darübergießen. Pro Portion reichen etwa 3 Mulden.",
                 "18 bis 20 Minuten backen, bis die Eier ganz fest sind. Die Muffins halten sich gekühlt 2 Tage und schmecken auch kalt."])
    # (7) Pfannkuchen und French Toast
    for ti, (tn, td, ts) in enumerate([("Erdbeeren", dict(erdb=100), "Mit den Erdbeeren servieren."), ("Honig", dict(honig=1), "Mit Honig beträufeln."), ("Kakao und Skyr", dict(kakao=1, skyr=80), "Skyr mit Kakao verrühren und dazu essen."), ("Joghurt und Honig", dict(jogGr=60, honig=1), "Mit Joghurt und Honig servieren."), ("Mandeln", dict(mandel=10), "Mit gehackten Mandeln bestreuen.")]):
        for bi, (bn, bd) in enumerate([("Bananen", dict(banane=1, ei=1, hafer=40, quark=100)), ("Quark", dict(ei=2, hafer=40, quark=120))]):
            add(f"Hafer-{bn}-Pfannkuchen mit {tn}", "F", 15, "g", join(ing(oel=1), ing(**bd), ing(**td)),
                ["Alle Zutaten für den Teig mit dem Stabmixer oder in einer Schüssel glatt verrühren (die Haferflocken dürfen vorher kurz quellen).", "Eine beschichtete Pfanne mit dem Öl auf mittlere Hitze bringen und kleine Pfannkuchen ausbacken, nach etwa 2 Minuten wenden, bis sie fest sind.", ts])
    for ti, (tn, td, ts) in enumerate([("Banane und Honig", dict(banane=1, honig=1), "Banane in Scheiben schneiden."), ("Erdbeeren und Quark", dict(erdb=100, quark=80), "Erdbeeren in Stücke schneiden."), ("Zimt und Skyr", dict(skyr=100, T="Zimt"), "Skyr mit Zimt verrühren.")]):
        add(f"French Toast mit {tn}", "F", 15, "g", join(ing(brot=2, ei=2, milch=80, oel=1), ing(**td)),
            ["Eier mit der Milch verquirlen.", ts, "Das Brot kurz in der Eiermilch wenden, bis es sie aufgesogen hat.", "Im Öl bei mittlerer Hitze von beiden Seiten goldbraun braten, bis das Ei ganz fest ist.", f"Mit {tn} servieren."])
    # (8) Shakes
    for bi, (bn, bd) in enumerate([("Skyr", dict(skyr=150)), ("Quark", dict(quark=150)), ("Speisequark", dict(speisequark=130))]):
        for fi, (fk, (fd, fn, fs)) in enumerate(FR.items()):
            for li, (ln, ld) in enumerate([("Haferflocken", dict(hafer=30)), ("Kakao", dict(kakao=1, honig=1)), ("Mandeln", dict(mandel=10))]):
                if (bi + fi + li) % 3:
                    continue
                add(f"{ {'Banane': 'Bananen', 'Erdbeeren': 'Erdbeer', 'Banane und Erdbeeren': 'Bananen-Erdbeer'}[fn] }-{bn}-Shake mit {ln}", "F", 5, "kla", join(ing(milch=200), ing(**bd), ing(**{k: v * (1.5 if k in ("banane", "erdb") else 1) for k, v in fd.items()}), ing(**ld)),
                    ["Alle Zutaten in einen Mixer geben.", "Etwa 30 Sekunden cremig mixen, bis keine Flocken mehr zu sehen sind.", "Sofort trinken oder in eine Flasche füllen."])


def snacks():
    # (1) Dips mit Gemüsesticks
    DIPB = [("Quark", dict(quark=130)), ("Speisequark", dict(speisequark=110)), ("Joghurt-Quark", dict(jogGr=60, quark=70)), ("Bohnen-Quark", dict(bohne=60, quark=50)), ("Kichererbsen-Quark", dict(kiche=70, quark=50))]
    DIPF = [("Kreuzkümmel", dict(kreuz=0.5, zitrone=1, T="Salz")), ("Paprika", dict(paprikap=1, zitrone=0.5, T="Salz")), ("Curry", dict(curry=1, T="Salz")), ("Knoblauch", dict(knob=0.5, zitrone=1, T="Kräuter, Salz und Pfeffer")),
            ("Senf", dict(senf=1, T="Pfeffer")), ("Parmesan", dict(parm=10, T="Pfeffer")), ("Saurer Gurke", dict(sgurke=1, T="Pfeffer"))]
    DIPV = [("Gurkensticks", dict(gurke=150), "Die Gurke in Sticks schneiden."), ("Paprikasticks", dict(pap=1), "Die Paprika in Sticks schneiden."), ("Gurken-Paprika-Sticks", dict(gurke=80, pap=0.5), "Gurke und Paprika in Sticks schneiden.")]
    for bi, (bn, bd) in enumerate(DIPB):
        for fi, (fn, fd) in enumerate(DIPF):
            for vi, (vn, vd, vs) in enumerate(DIPV):
                if (bi + fi * 2 + vi) % 3:
                    continue
                mix = "Die Hülsenfrüchte abtropfen und mit dem Quark und den Gewürzen fein pürieren." if "bohne" in bd or "kiche" in bd else "Alles glatt verrühren."
                add(f"{bn}-Dip mit {fn} und {vn}", "S", 8, "k" + ("a" if bi % 2 == 0 else ""), join(ing(**bd), ing(**fd), ing(**vd)), [mix, vs, "Zum Dippen servieren."])
    # (2) Röllchen und Spieße
    for mi, (m, g, mn) in enumerate([("schink", 50, "Schinken"), ("paufs", 60, "Putenaufschnitt"), ("lyoner", 50, "Lyoner")]):
        for fi, (fn, fd, fs) in enumerate([("Quark", dict(speisequark=50), "Den Quark mit Pfeffer verrühren und auf den Scheiben verstreichen."), ("Joghurt-Senf", dict(jogGr=40, senf=0.5), "Joghurt und Senf verrühren und auf den Scheiben verstreichen."), ("Parmesan-Quark", dict(quark=50, parm=10), "Quark mit fein geriebenem Parmesan und Pfeffer verrühren und auf den Scheiben verstreichen.")]):
            for vi, (vn, vd, vs) in enumerate([("Gurke", dict(gurke=80), "Die Gurke in Streifen schneiden."), ("Paprika", dict(pap=0.5), "Die Paprika in Streifen schneiden."), ("Rucola", dict(ruc=20), "Den Rucola zupfen."), ("Saurer Gurke", dict(sgurke=2), "Die Saure Gurke in Streifen schneiden.")]):
                if (mi + fi + vi) % 2:
                    continue
                add(f"{mn}-Röllchen mit {fn} und {vn}", "S", 6, "ka", join(ing(**{m: g}), ing(**fd), ing(**vd), ing(T="Pfeffer")), [vs, fs, "Das Gemüse auf die Scheiben legen und fest aufrollen. Nach Wunsch in Stücke schneiden."])
    for mi, (m, g, mn) in enumerate([("schink", 40, "Schinken"), ("paufs", 50, "Putenaufschnitt"), ("ei", 1, "Ei"), ("gouda", 30, "Gouda")]):
        for vi, (vn, vd, vs) in enumerate([("Tomate", dict(tom=1), "Die Tomate in Stücke schneiden."), ("Gurke und Tomate", dict(gurke=60, tom=1), "Gurke und Tomate in Stücke schneiden.")]):
            pre = "Eier mindestens 8 Minuten hart kochen, abschrecken, pellen und vierteln. " if m == "ei" else ""
            add(f"Mozzarella-Spieße mit {nl(mn, vn)}", "S", 6, "ka", join(ing(moz=60), ing(**{m: g}), ing(**vd), ing(T="Basilikum und Pfeffer")), [pre + vs, "Den Mozzarella würfeln, Fleisch (oder Gouda) in Stücke schneiden.", "Abwechselnd auf Spieße stecken und mit Basilikum und Pfeffer bestreuen."])
    # (3) Cremes
    for bi, (bn, bd) in enumerate([("Skyr", dict(skyr=150)), ("Quark", dict(quark=150)), ("Speisequark", dict(speisequark=130)), ("Joghurt-Quark", dict(jogGr=70, quark=80))]):
        for fi, (fk, (fd, fn, fs)) in enumerate(FR_S.items()):
            for ti, (tn, td, ts) in enumerate([("Kakao", dict(kakao=1), "Den Kakao unterrühren."), ("Zimt und Honig", dict(honig=0.5, T="Zimt"), "Mit Zimt und Honig abschmecken."), ("Mandeln", dict(mandel=10), "Gehackte Mandeln daraufstreuen.")]):
                if (bi + fi + ti) % 2:
                    continue
                add(f"{bn}-Creme mit {nl(fn, tn)}", "S", 4, "kgl", join(ing(**bd), ing(**fd), ing(**td)), [fs, f"{bn} glatt rühren und die Frucht unterheben oder daraufgeben.", ts])
    for bi, (bn, bd) in enumerate([("Quark", dict(quark=150)), ("Skyr", dict(skyr=150))]):
        for fi, (fk, (fd, fn, fs)) in enumerate(FR_S.items()):
            add(f"Gefrorenes {bn}-Eis mit {fn}", "S", 5, "kp", join(ing(**bd), ing(**fd), ing(honig=1)), [fs, "Alles im Mixer cremig mixen (Bananen vorher einfrieren, dann wird es eisig).", "In ein Gefäß füllen, mindestens 2 Stunden einfrieren und vor dem Essen 10 Minuten antauen lassen."])
    # (4) Eier-Snacks
    for ti, (tn, td, ts) in enumerate([("Paprikapulver", dict(paprikap=0.5), "mit Paprikapulver und Salz bestreuen"), ("Senf", dict(senf=1), "mit Senf anrichten"), ("Joghurt-Dip", dict(jogGr=40, T="Kräuter"), "mit dem Joghurt-Dip servieren")]):
        for vi, (vn, vd, vs) in enumerate([("Gurke", dict(gurke=100), "Gurke in Scheiben"), ("Tomate", dict(tom=1), "Tomate in Spalten"), ("Paprika", dict(pap=0.5), "Paprika in Streifen")]):
            add(f"Hartgekochte Eier mit {tn} und {vn}", "S", 12, "a", join(ing(ei=2), ing(**td), ing(**vd), ing(T="Salz")), ["Eier mindestens 8 Minuten hart kochen (gern am Vortag), abschrecken und pellen.", f"{vs} schneiden.", f"Eier halbieren und {ts}. Das Gemüse dazu essen."])
    for fi, (fn, fd) in enumerate([("Saurer Gurke", dict(sgurke=2)), ("Gurke", dict(gurke=60)), ("Tomate", dict(tom=0.5))]):
        for bi, (bn, bd) in enumerate([("Quark", dict(quark=50)), ("Joghurt", dict(jogGr=40))]):
            add(f"Eiersalat mit {bn} und {fn} auf Brot", "S", 12, "ga", join(ing(ei=2, brot=1), ing(**fd), ing(**bd), ing(senf=0.5, T="Salz und Pfeffer")),
                ["Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.", "Die Eier mit einer Gabel zerdrücken, mit Quark (oder Joghurt), Senf, klein geschnittenem Gemüse, Salz und Pfeffer vermischen.", "Auf das Brot streichen."])
    # (5) Mini-Brote und Mini-Wraps
    MB = [("Speisequark und Tomate", dict(speisequark=60, tom=1), "Den Quark auf {a} {c} streichen und die Tomate in Scheiben darauflegen."),
          ("Putenaufschnitt und Gurke", dict(paufs=50, gurke=60), "Aufschnitt und Gurkenscheiben auf {a} {c} legen."),
          ("Mozzarella und Tomate", dict(moz=40, tom=1, T="Basilikum und Pfeffer"), "Mozzarella- und Tomatenscheiben auf {a} {c} legen und mit Basilikum und Pfeffer würzen."),
          ("Schinken und Saurer Gurke", dict(schink=40, sgurke=1, senf=0.5), "{A} {c} mit Senf bestreichen und mit Schinken und Saurer Gurke belegen."),
          ("Gouda und Paprika", dict(gouda=25, pap=0.5), "{A} {c} mit Gouda und Paprikastreifen belegen."),
          ("Skyr und Gurke", dict(skyr=70, gurke=60, T="Kräuter, Salz und Pfeffer"), "Den Skyr würzen, auf {a} {c} streichen und mit Gurke belegen."),
          ("Lyoner und Senf", dict(lyoner=45, senf=0.5, sgurke=1), "{A} {c} mit Senf bestreichen und mit Lyoner und Saurer Gurke belegen."),
          ("Ei und Rucola", dict(ei=1, ruc=15, T="Salz und Pfeffer"), "Das Ei mindestens 8 Minuten hart kochen, pellen, in Scheiben schneiden und mit Rucola auf {a} {c} legen.")]
    for ci, (cn, cd, cw, art) in enumerate([("Vollkornbrot", dict(brot=1), "Brot", "das"), ("Vollkornbrötchen", dict(broetchen=1), "Brötchen", "das"), ("Mini-Wrap", dict(wrap=1), "Wrap", "den")]):
        for mi, (mn, md, ms) in enumerate(MB):
            if (ci + mi) % 2:
                continue
            st = [ms.format(a=art, A=art.capitalize(), c=cw)] + (["Den Wrap einrollen und halbieren."] if cw == "Wrap" else [])
            add(f"{cn} mit {mn}", "S", 12 if "ei" in md else 6, "a" if "ei" in md else "ka", join(ing(**cd), ing(**md)), st)
    # (6) Fleisch-Happen
    for mi, (m, g, mn) in enumerate([("haehn", 100, "Hähnchen"), ("pute", 100, "Puten")]):
        for di, (dn, dd) in enumerate([("Joghurt-Kräuter", dict(jogGr=50, T="Kräuter, Salz und Pfeffer")), ("Paprika-Joghurt", dict(jogGr=50, paprikap=1)), ("Gurken-Quark", dict(quark=50, gurke=50, T="Salz und Pfeffer"))]):
            add(f"{mn}-Nuggets mit Haferkruste und {dn}-Dip", "S", 25, "a", join(ing(**{m: g, "hafer": 15, "ei": 0.5, "paprikap": 1, "oel": 1}), ing(**dd)),
                ["Ofen auf 200 °C Ober- und Unterhitze vorheizen.", "Das Fleisch in mundgerechte Stücke schneiden. Das Ei verquirlen, die Haferflocken mit Paprikapulver und Salz mischen.", "Die Stücke erst im Ei, dann in den Haferflocken wenden und auf ein geöltes Blech legen.",
                 "12 bis 15 Minuten backen, bis das Fleisch durch ist, einmal wenden. Den Dip verrühren und dazu essen."])
    for mi, (m, g) in enumerate([("rhack", 80), ("phack", 90)]):
        for di, (dn, dd) in enumerate([("Joghurt-Gurken", dict(jogGr=40, gurke=80, T="Salz und Pfeffer")), ("Paprika-Quark", dict(quark=50, pap=0.5, paprikap=0.5)), ("Tomaten-Senf", dict(tom=1, senf=1, quark=40))]):
            add(f"Mini-Frikadellen ({MEAT[m][0]}) mit {dn}-Dip", "S", 20, "pa", join(ing(**{m: g, "hafer": 10, "paprikap": 1, "oel": 0.5}), ing(**dd)),
                ["Hack mit Haferflocken, Paprikapulver, Salz und Pfeffer verkneten und zu kleinen Bällchen formen.", "Im Öl rundum 8 bis 10 Minuten braten, bis sie innen nicht mehr rosa sind.", "Den Dip aus den Zutaten verrühren (Gurke oder Tomate klein schneiden) und dazu essen."])
    for mi, m in enumerate(["haehn", "pute", "haehnst"]):
        for di, (dn, dd) in enumerate([("Honig-Senf", dict(senf=1, honig=1)), ("Joghurt", dict(jogGr=50, T="Kräuter"))]):
            g = 90
            st = ["Das Fleisch in Würfel schneiden, auf Spieße stecken und im Öl 6 bis 8 Minuten rundum braten, bis es durch und innen nicht mehr rosa ist."] if m != "haehnst" else ["Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Stücke schneiden."]
            add(f"{MEAT[m][0]}-Spieße mit {dn}-Dip und Gurke", "S", 15, "a", join(ing(**{m: g, "gurke": 80, "oel": 0.5}), ing(**dd)), st + ["Den Dip verrühren, die Gurke in Sticks schneiden und alles zusammen servieren."])
    # (7) Hülsenfrucht-Snacks
    for si, (sn, sd) in enumerate([("Paprika", dict(paprikap=1)), ("Kreuzkümmel", dict(kreuz=1)), ("Curry", dict(curry=1))]):
        for di, (dn, dd) in enumerate([("Joghurt", dict(jogGr=60)), ("Quark", dict(quark=70))]):
            add(f"Ofen-Kichererbsen mit {sn} und {dn}-Dip", "S", 35, "pa", join(ing(kiche=120, oel=0.5), ing(**sd), ing(**dd), ing(T="Salz")),
                ["Ofen auf 200 °C Ober- und Unterhitze vorheizen. Die Kichererbsen abtropfen und gut trocken tupfen.", "Mit Öl, Gewürz und Salz mischen und auf einem Blech verteilen.", "25 bis 30 Minuten backen, zwischendurch einmal schütteln, bis sie knusprig sind.", "Dazu den Dip aus Joghurt (oder Quark) und etwas Salz reichen."])
    for bi, (bn, bd, bs) in enumerate([("Paprika", dict(pap=0.5), "Paprika in Streifen"), ("Tomate", dict(tom=1), "Tomate in Scheiben"), ("Gurke", dict(gurke=60), "Gurke in Scheiben")]):
        add(f"Bohnen-Aufstrich auf Brot mit {bn}", "S", 8, "kg", join(ing(bohne=80, quark=40, brot=1, knob=0.5, paprikap=0.5, zitrone=1), ing(**bd), ing(T="Salz und Pfeffer")),
            ["Die Bohnen abtropfen und mit Quark, Knoblauch, Paprikapulver und Zitronensaft pürieren, mit Salz und Pfeffer abschmecken.", f"{bs} schneiden.", "Den Aufstrich auf das Brot streichen und mit dem Gemüse belegen."])


def thin(items, keep):
    """wählt `keep` gleichmäßig verteilte Einträge aus"""
    if keep >= len(items):
        return list(items)
    return [items[int(i * len(items) / keep)] for i in range(keep)]


def run():
    before = len(gen_core.OUT)
    fruehstueck()
    snacks()
    fs = gen_core.OUT[before:]
    del gen_core.OUT[before:]
    need = TOTAL - before
    F = [x for x in fs if x[1] == "F"]
    S = [x for x in fs if x[1] == "S"]
    # etwa 51 % Frühstück, 49 % Snacks
    kf = min(len(F), round(need * 0.52))
    ks = min(len(S), need - kf)
    kf = min(len(F), need - ks)
    gen_core.OUT.extend(thin(F, kf) + thin(S, ks))
    print(f"Erzeugt: Mittag/Abend {before}, Frühstück {kf} (von {len(F)}), Snack {ks} (von {len(S)}), zusammen {len(gen_core.OUT)}")
