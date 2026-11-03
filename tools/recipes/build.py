# -*- coding: utf-8 -*-
"""Rezeptsammlung: berechnet Kalorien und Eiweiß aus einer Zutatentabelle und prüft Vielfalt und Gesundheit."""
import json, re, sys, os, itertools, collections, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))

# key: (Name, Mehrzahl, Einheit, Gramm je Einheit, kcal/100g, Eiweiß/100g, Merkmale, Gruppe)
# Einheit: g oder ml = Menge direkt, Stk/EL/TL = Anzahl mit Gramm je Einheit
DB = {
 "haehn": ("Hähnchenbrust", None, "g", 1, 106, 22, "Geflügel", "fleisch"),
 "pute": ("Putenbrust", None, "g", 1, 105, 23, "Geflügel", "fleisch"),
 "ghack": ("Hackfleisch (gemischt)", None, "g", 1, 250, 17, "Rindfleisch,Schwein", "fleisch"),
 "phack": ("Putenhack", None, "g", 1, 130, 20, "Geflügel", "fleisch"),
 "rhack": ("Rinderhack (mager)", None, "g", 1, 175, 20, "Rindfleisch", "fleisch"),
 "schink": ("Kochschinken", None, "g", 1, 105, 20, "Schwein,verarbeitet", "fleisch"),
 "paufs": ("Putenbrust-Aufschnitt", None, "g", 1, 100, 19, "Geflügel,verarbeitet", "fleisch"),
 "ei": ("Ei", "Eier", "Stk", 51, 143, 12.6, "Ei", "ei"),
 "skyr": ("Skyr", None, "g", 1, 63, 11, "Milch", "milch"),
 "quark": ("Magerquark", None, "g", 1, 67, 12, "Milch", "milch"),
 "jog35": ("Naturjoghurt", None, "g", 1, 70, 4, "Milch", "milch"),
 "milch": ("Milch (1,5 %)", None, "ml", 1, 47, 3.4, "Milch", "milch"),
 "moz": ("Mozzarella", None, "g", 1, 250, 18, "Käse,Milch", "milch"),
 "gouda": ("Gouda", None, "g", 1, 350, 25, "Käse,Milch", "milch"),
 "parm": ("Parmesan", None, "g", 1, 400, 35, "Käse,Milch", "milch"),
 "speisequark": ("Speisequark 20 %", None, "g", 1, 105, 11.5, "Milch", "milch"),
 "jogGr": ("Griechischer Joghurt (10 %)", None, "g", 1, 133, 5.5, "Milch", "milch"),
 "butter": ("Butter (ungesalzen)", None, "g", 1, 741, 0.7, "Milch", "fett"),
 "haehnst": ("Hähnchen-Mini-Steaks", None, "g", 1, 110, 22, "Geflügel", "fleisch"),
 "lyoner": ("Delikatess-Lyoner", None, "g", 1, 260, 12, "Schwein,verarbeitet", "fleisch"),
 "hafer": ("Haferflocken", None, "g", 1, 370, 13.5, "", "stärke"),
 "chia": ("Chia-Samen", None, "g", 1, 486, 17, "", "sonst"),
 "mandel": ("Mandeln", None, "g", 1, 580, 21, "Nüsse", "nuss"),
 "brot": ("Scheibe Vollkornbrot", "Scheiben Vollkornbrot", "Stk", 50, 230, 8, "", "stärke"),
 "wrap": ("Vollkorn-Wrap", "Vollkorn-Wraps", "Stk", 62, 280, 9, "", "stärke"),
 "broetchen": ("Vollkornbrötchen", "Vollkornbrötchen", "Stk", 60, 240, 9, "", "stärke"),
 "nudel": ("Vollkornnudeln (Rohgewicht)", None, "g", 1, 350, 12.5, "", "stärke"),
 "reis": ("Reis (Rohgewicht)", None, "g", 1, 350, 7, "", "stärke"),
 "couscous": ("Couscous (Rohgewicht)", None, "g", 1, 360, 12.5, "", "stärke"),
 "honig": ("Honig", None, "TL", 7, 300, 0.3, "Honig", "sonst"),
 "oel": ("Rapsöl", None, "TL", 4, 880, 0, "", "fett"),
 "soja": ("Sojasauce", None, "EL", 15, 60, 6, "", "sonst"),
 "tmark": ("Tomatenmark", None, "EL", 15, 85, 4.5, "", "sonst"),
 "stueck": ("stückige Tomaten (Dose)", None, "g", 1, 24, 1.2, "", "gemüse"),
 "tom": ("Tomate", "Tomaten", "Stk", 100, 18, 0.9, "", "gemüse"),
 "gurke": ("Gurke", None, "g", 1, 12, 0.6, "", "gemüse"),
 "pap": ("Paprika", "Paprika", "Stk", 150, 28, 1, "", "gemüse"),
 "zwie": ("Zwiebel", "Zwiebeln", "Stk", 80, 40, 1.2, "", "gemüse"),
 "karo": ("Karotte", "Karotten", "Stk", 80, 35, 0.9, "", "gemüse"),
 "eisb": ("Eisbergsalat", None, "g", 1, 14, 0.9, "", "gemüse"),
 "spin": ("Spinat (frisch oder Tiefkühl)", None, "g", 1, 23, 2.9, "", "gemüse"),
 "ruc": ("Rucola", None, "g", 1, 25, 2.6, "", "gemüse"),
 "sgurke": ("Saure Gurke", "Saure Gurken", "Stk", 40, 15, 0.5, "", "gemüse"),
 "knob": ("Knoblauchzehe", "Knoblauchzehen", "Stk", 3, 150, 6, "", "sonst"),
 "banane": ("Banane", "Bananen", "Stk", 100, 90, 1.1, "", "obst"),
 "erdb": ("Erdbeeren (frisch oder Tiefkühl)", None, "g", 1, 35, 0.7, "", "obst"),
 "kiche": ("Kichererbsen (Dose, abgetropft)", None, "g", 1, 125, 7, "Hülsenfrüchte", "hülse"),
 "bohne": ("Kidneybohnen (Dose, abgetropft)", None, "g", 1, 105, 7, "Hülsenfrüchte", "hülse"),
 "linse": ("rote Linsen (trocken)", None, "g", 1, 350, 25, "Hülsenfrüchte", "hülse"),
 "kokos": ("leichte Kokosmilch", None, "ml", 1, 75, 0.8, "", "sonst"),
 "bruehe": ("Gemüsebrühe", None, "ml", 1, 5, 0.3, "", "sonst"),
 "zitrone": ("Zitronensaft", None, "EL", 15, 25, 0.4, "", "sonst"),
 "senf": ("Senf", None, "TL", 5, 100, 6, "", "sonst"),
 "kakao": ("Kakao", None, "TL", 5, 355, 20, "", "sonst"),
 "schnitzel": ("Schweineschnitzel", None, "g", 1, 110, 21, "Schwein", "fleisch"),
 "curry": ("Currypulver", None, "TL", 3, 325, 14, "", "sonst"),
 "garam": ("Garam Masala", None, "TL", 3, 330, 14, "", "sonst"),
 "paprikap": ("Paprikapulver", None, "TL", 3, 290, 14, "", "sonst"),
 "kurkuma": ("Kurkuma", None, "TL", 3, 310, 10, "", "sonst"),
 "kreuz": ("Kreuzkümmel (Kumin)", None, "TL", 2, 375, 18, "", "sonst"),
}

# ======================= Lidl-Preise (Richtwerte, Stand Nov 2026) =======================
# key: (Packungsgröße in g bzw. ml, Preis in €, Abteilung, Packungsbeschreibung, lose?, Vorrat?)
# Quellen: aktuelle Lidl-Prospektpreise und Supermarktcheck-Meldungen (Hähnchen, Quark, Skyr, Joghurt, Gouda, Haferflocken, Tomaten-Dose);
# alle anderen Werte sind geschätzte Marktpreise. Preise schwanken, Angebote und Lidl Plus drücken sie oft.
PRICE = {
 "haehn": (600, 5.49, "Fleisch & Wurst", "Schale 600 g", 0, 0),
 "pute": (500, 4.99, "Fleisch & Wurst", "Schale 500 g", 0, 0),
 "phack": (400, 3.29, "Fleisch & Wurst", "Packung 400 g", 0, 0),
 "rhack": (500, 4.69, "Fleisch & Wurst", "Packung 500 g", 0, 0),
 "ghack": (500, 3.49, "Fleisch & Wurst", "Packung 500 g", 0, 0),
 "schink": (150, 1.69, "Fleisch & Wurst", "Packung 150 g", 0, 0),
 "paufs": (100, 1.39, "Fleisch & Wurst", "Packung 100 g", 0, 0),
 "ei": (510, 2.99, "Kühlregal", "10er-Packung", 0, 0),
 "skyr": (500, 1.15, "Kühlregal", "Becher 500 g", 0, 0),
 "quark": (500, 0.99, "Kühlregal", "Becher 500 g", 0, 0),
 "jog35": (500, 0.79, "Kühlregal", "Becher 500 g", 0, 0),
 "milch": (1000, 0.95, "Kühlregal", "Packung 1 l", 0, 0),
 "moz": (125, 0.85, "Kühlregal", "Kugel 125 g", 0, 0),
 "gouda": (450, 4.29, "Kühlregal", "Stück 450 g", 0, 0),
 "parm": (125, 3.29, "Kühlregal", "Stück 125 g", 0, 0),
 "speisequark": (500, 1.38, "Kühlregal", "Becher 500 g", 0, 0),
 "jogGr": (1000, 2.19, "Kühlregal", "Becher 1 kg", 0, 0),
 "butter": (375, 1.59, "Kühlregal", "Packung 375 g (XXL-Aktion)", 0, 0),
 "haehnst": (400, 4.99, "Fleisch & Wurst", "Packung 400 g", 0, 0),
 "lyoner": (200, 0.89, "Fleisch & Wurst", "Packung 200 g", 0, 0),
 "hafer": (500, 0.59, "Nudeln, Reis & Trockenes", "Packung 500 g", 0, 0),
 "chia": (200, 2.29, "Nudeln, Reis & Trockenes", "Packung 200 g", 0, 0),
 "mandel": (200, 3.19, "Nudeln, Reis & Trockenes", "Packung 200 g", 0, 0),
 "brot": (500, 1.19, "Brot & Backwaren", "Packung 500 g (ca. 10 Scheiben)", 0, 0),
 "wrap": (372, 1.39, "Brot & Backwaren", "6er-Packung", 0, 0),
 "broetchen": (60, 0.25, "Brot & Backwaren", "Stück", 0, 0),
 "nudel": (500, 1.15, "Nudeln, Reis & Trockenes", "Packung 500 g", 0, 0),
 "reis": (1000, 1.89, "Nudeln, Reis & Trockenes", "Beutel 1 kg", 0, 0),
 "couscous": (500, 1.29, "Nudeln, Reis & Trockenes", "Packung 500 g", 0, 0),
 "honig": (500, 3.19, "Vorrat", "Glas 500 g", 0, 1),
 "oel": (920, 1.99, "Vorrat", "Flasche 1 l", 0, 1),
 "soja": (150, 1.29, "Vorrat", "Flasche 150 ml", 0, 1),
 "tmark": (200, 0.79, "Vorrat", "Tube 200 g", 0, 1),
 "stueck": (400, 0.79, "Nudeln, Reis & Trockenes", "Dose 400 g", 0, 0),
 "tom": (1000, 3.29, "Obst & Gemüse", "lose", 1, 0),
 "gurke": (400, 1.09, "Obst & Gemüse", "Salatgurke", 0, 0),
 "pap": (1000, 3.99, "Obst & Gemüse", "lose", 1, 0),
 "zwie": (1000, 1.29, "Obst & Gemüse", "Netz 1 kg", 0, 0),
 "karo": (1000, 1.09, "Obst & Gemüse", "Netz 1 kg", 0, 0),
 "eisb": (500, 1.19, "Obst & Gemüse", "Kopf", 0, 0),
 "spin": (450, 1.29, "Tiefkühl", "Beutel 450 g (TK)", 0, 0),
 "ruc": (100, 1.19, "Obst & Gemüse", "Schale 100 g", 0, 0),
 "sgurke": (320, 1.19, "Nudeln, Reis & Trockenes", "Glas (ca. 8 Stück)", 0, 0),
 "knob": (120, 0.99, "Obst & Gemüse", "Netz mit 3 Knollen", 0, 0),
 "banane": (1000, 1.49, "Obst & Gemüse", "lose", 1, 0),
 "erdb": (500, 1.99, "Tiefkühl", "Beutel 500 g (TK)", 0, 0),
 "kiche": (265, 0.79, "Nudeln, Reis & Trockenes", "Dose 400 g", 0, 0),
 "bohne": (265, 0.69, "Nudeln, Reis & Trockenes", "Dose 400 g", 0, 0),
 "linse": (500, 1.29, "Nudeln, Reis & Trockenes", "Packung 500 g", 0, 0),
 "kokos": (400, 1.19, "Nudeln, Reis & Trockenes", "Dose 400 ml", 0, 0),
 "bruehe": (5000, 1.29, "Vorrat", "Brühe-Pulver", 0, 1),
 "zitrone": (200, 0.99, "Vorrat", "Flasche 200 ml", 0, 1),
 "senf": (200, 0.69, "Vorrat", "Glas 200 ml", 0, 1),
 "kakao": (125, 1.29, "Vorrat", "Backkakao 125 g", 0, 1),
 "schnitzel": (400, 3.19, "Fleisch & Wurst", "Packung 400 g", 0, 0),
 "curry": (40, 0.99, "Vorrat", "Gewürzdose 40 g", 0, 1),
 "garam": (35, 0.99, "Vorrat", "Gewürzdose 35 g", 0, 1),
 "paprikap": (50, 0.99, "Vorrat", "Gewürzdose 50 g", 0, 1),
 "kurkuma": (35, 0.99, "Vorrat", "Gewürzdose 35 g", 0, 1),
 "kreuz": (35, 0.99, "Vorrat", "Gewürzdose 35 g", 0, 1),
}
assert set(PRICE) == set(DB), set(DB) ^ set(PRICE)
MEAL = {"F": "Frühstück", "M": "Mittag/Abend", "S": "Snack"}
TAG = {"k": "Ohne Kochen", "p": "Meal-Prep", "g": "Günstig", "a": "Für die Arbeit", "l": "Leicht"}
SHOWN_CONTAINS = ["Hülsenfrüchte", "Rindfleisch", "Schwein", "Geflügel", "Ei", "Nüsse"]

R = []
TARGET = 300
def r(title, meal, time, tags, ing, steps, tip=None):
    R.append(dict(title=title, meal=MEAL[meal], time=time, tags=tags, ing=ing, steps=[s.strip() for s in steps.split("|")], tip=tip))

# ======================= FRÜHSTÜCK (23) =======================
r("Skyr-Bowl mit Erdbeeren und Haferflocken", "F", 3, "kg", "skyr:250;hafer:40;erdb:100;honig:1",
  "Skyr in eine Schüssel geben.|Haferflocken und Erdbeeren darauf verteilen.|Mit Honig beträufeln und umrühren.",
  "Magerquark hat etwas mehr Eiweiß als Skyr und ist meist günstiger.")
r("Skyr mit Banane und Mandeln", "F", 2, "kgl", "skyr:200;banane:1;mandel:10",
  "Banane in Scheiben schneiden und die Mandeln grob hacken.|Skyr in eine Schale geben und Banane und Mandeln daraufgeben.",
  "Klein, aber mit rund 25 g Eiweiß: passt, wenn du morgens wenig Appetit hast.")
r("Quark mit Erdbeeren", "F", 3, "kgl", "quark:200;erdb:150;honig:1",
  "Erdbeeren in Stücke schneiden oder auftauen lassen.|Quark glatt rühren und die Erdbeeren unterheben.|Mit Honig süßen.")
r("Bananen-Quark-Creme", "F", 3, "kgl", "quark:200;banane:1;~Zimt",
  "Banane mit einer Gabel zerdrücken.|Quark unterrühren, bis eine Creme entsteht.|Mit Zimt bestäuben.")
r("Erdbeer-Skyr-Smoothie", "F", 5, "kla", "skyr:200;milch:200;erdb:100;banane:0.5",
  "Alle Zutaten in einen Mixer geben.|Etwa 30 Sekunden cremig mixen.|Sofort trinken oder in eine Flasche füllen.",
  "Trinkbar und schnell: praktisch, wenn morgens wenig geht.")
r("Bananen-Haferflocken-Shake", "F", 5, "k", "milch:250;quark:150;banane:1;hafer:30",
  "Alle Zutaten in einen Mixer geben.|Eine Minute mixen, bis keine Flocken mehr zu sehen sind.|Gleich trinken.")
r("Vollkornbrot mit Gouda und Gurke", "F", 3, "kga", "brot:2;gouda:40;gurke:100;~Pfeffer",
  "Brot mit dem Gouda belegen.|Gurke in Scheiben schneiden und darauflegen.|Mit Pfeffer würzen.")
r("Eierbrot mit Tomate", "F", 10, "ga", "brot:2;ei:2;tom:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten in kochendem Wasser hart kochen (gern am Vortag), abschrecken und pellen.|Tomate und Eier in Scheiben schneiden.|Auf dem Brot verteilen und würzen.")
r("Mini-Rührei auf Brot", "F", 8, "g", "ei:2;gouda:20;brot:1;oel:1;~Salz und Pfeffer",
  "Eier verquirlen und mit dem geriebenen Gouda mischen.|Öl in einer Pfanne erhitzen und die Eimasse bei mittlerer Hitze stocken lassen, bis sie ganz fest ist.|Auf dem Brot servieren.")
r("Rührei mit Paprika und Brot", "F", 10, "g", "ei:3;pap:1;oel:1;brot:2;~Salz und Pfeffer",
  "Paprika klein schneiden und im Öl etwa 3 Minuten anbraten.|Eier verquirlen, würzen und dazugeben.|Bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.|Mit dem Brot essen.")
r("Spinat-Omelett mit Mozzarella", "F", 12, "g", "ei:3;spin:100;moz:60;oel:1;~Salz und Pfeffer",
  "Spinat im Öl in einer Pfanne zusammenfallen lassen und herausnehmen.|Eier verquirlen, würzen und in die Pfanne geben, bei mittlerer Hitze stocken lassen.|Spinat und Mozzarella auf eine Hälfte legen, zuklappen und eine Minute ziehen lassen.")
r("Paprika-Omelett mit Gouda", "F", 12, "g", "ei:3;pap:1;zwie:0.5;gouda:30;oel:1;~Salz und Pfeffer",
  "Paprika und Zwiebel klein schneiden und im Öl 4 Minuten anbraten.|Eier verquirlen, würzen und dazugeben.|Gouda darüberstreuen, zuklappen und stocken lassen, bis das Ei fest ist.")
r("Proteinpfannkuchen mit Banane", "F", 15, "g", "banane:1;ei:2;quark:100;hafer:40;oel:1",
  "Alles außer dem Öl mit dem Stabmixer glatt mixen.|Eine beschichtete Pfanne mit dem Öl auf mittlere Hitze bringen.|Den Teig portionsweise ausbacken und nach etwa 2 Minuten wenden.")
r("French Toast mit Erdbeeren", "F", 15, "g", "brot:2;ei:2;milch:80;erdb:100;oel:1;honig:1",
  "Eier mit der Milch verquirlen.|Brot kurz darin wenden, bis es die Masse aufgesogen hat.|Im Öl bei mittlerer Hitze von beiden Seiten goldbraun braten, bis das Ei fest ist.|Mit Erdbeeren und Honig servieren.")
r("Spiegeleier auf Brot mit Tomate und Rucola", "F", 10, "g", "brot:2;ei:2;tom:1;ruc:20;oel:1;~Salz und Pfeffer",
  "Eier im Öl zu Spiegeleiern braten, bis das Eiweiß ganz fest ist.|Brot mit Tomatenscheiben und Rucola belegen.|Die Spiegeleier daraufsetzen und würzen.")
r("Pizza-Omelett mit Tomate und Mozzarella", "F", 12, "g", "ei:3;tom:1;moz:40;zwie:0.5;oel:1;~Oregano, Salz und Pfeffer",
  "Zwiebel klein schneiden und im Öl 2 Minuten anbraten.|Eier verquirlen, würzen und in die Pfanne geben, bei mittlerer Hitze fast stocken lassen.|Tomate in Scheiben und Mozzarella darauf verteilen, zuklappen und eine Minute ziehen lassen, bis der Käse schmilzt.")
r("Overnight Oats (dein Rezept)", "F", 5, "kpga", "hafer:100;chia:20;milch:150;quark:100;jog35:50;erdb:100;banane:1;honig:1;mandel:10",
  "Haferflocken, Chia, Milch, Quark und Joghurt im Glas verrühren.|Erdbeeren und die Hälfte der Banane in Stücken unterheben.|Abgedeckt über Nacht in den Kühlschrank stellen.|Vor dem Essen mit der restlichen Banane, Honig und den Mandeln toppen.",
  "Für dein Ziel sehr gut: rund 40 g Eiweiß und etwa 20 g Ballaststoffe halten lange satt. Mit rund 850 kcal ist es aber eine große Mahlzeit. Spar bei Bedarf Kalorien mit 70 g statt 100 g Haferflocken und ohne Honig.")
r("Overnight Oats light mit Erdbeeren", "F", 5, "kpga", "hafer:60;chia:10;milch:100;quark:100;erdb:100;banane:0.5;mandel:10",
  "Haferflocken, Chia, Milch und Quark im Glas verrühren.|Erdbeeren unterheben und über Nacht abgedeckt in den Kühlschrank stellen.|Mit Banane und Mandeln toppen.",
  "Die leichtere Variante deines Rezepts mit gut 500 kcal.")
r("Protein-Porridge mit Banane und Mandeln", "F", 8, "g", "hafer:60;milch:250;quark:100;banane:1;mandel:10;honig:1;~Zimt",
  "Haferflocken mit der Milch unter Rühren 3 bis 5 Minuten köcheln, bis der Brei cremig ist.|Vom Herd nehmen und den Quark unterrühren.|Mit Banane, Mandeln, Honig und Zimt toppen.")
r("Rührei-Wrap mit Gouda", "F", 10, "ga", "ei:3;wrap:1;gouda:30;tom:1;eisb:30;oel:1;~Salz und Pfeffer",
  "Eier verquirlen und im Öl bei mittlerer Hitze stocken lassen, bis sie ganz fest sind.|Wrap mit Salat, Tomatenscheiben und Gouda belegen.|Das Rührei daraufgeben und einrollen.")
r("Eier-Schinken-Toast", "F", 10, "g", "brot:2;ei:2;schink:40;gurke:50;oel:1;~Pfeffer",
  "Eier im Öl zu Spiegeleiern braten, bis das Eiweiß ganz fest ist.|Brot mit Schinken und Gurkenscheiben belegen.|Die Eier daraufsetzen und mit Pfeffer würzen.")
r("Haferflocken-Bananen-Muffins", "F", 30, "pga", "hafer:60;banane:1;ei:1;quark:75;mandel:10;~Zimt",
  "Ofen auf 180 °C Ober- und Unterhitze vorheizen.|Banane zerdrücken und mit Ei, Quark und Zimt verrühren. Haferflocken und gehackte Mandeln unterheben.|Den Teig in 2 Muffinförmchen pro Portion füllen.|20 bis 25 Minuten backen, bis sie fest sind, und abkühlen lassen.",
  "Eine Portion sind etwa 2 Muffins. Für einen Vorrat stell die Portionen im Regler ein.")
r("Erdbeer-Quark-Toast", "F", 5, "kg", "brot:2;quark:150;erdb:100;honig:1",
  "Quark auf dem Brot verstreichen.|Erdbeeren in Scheiben darauflegen.|Mit Honig beträufeln.")

# ======================= SNACKS (21) =======================
r("Quark-Kakao-Creme", "S", 3, "kg", "quark:200;kakao:1;honig:1;~Zimt",
  "Alles in einer Schüssel glatt rühren.",
  "Quark enthält viel Casein. Die Fachgesellschaft ISSN nennt 30 bis 40 g Casein vor dem Schlafen als sinnvoll. Dafür brauchst du etwa 250 g Quark.")
r("Hartgekochte Eier", "S", 10, "pg", "ei:2;~Salz",
  "Eier in kochendes Wasser legen und mindestens 8 Minuten kochen, bis Eiweiß und Eigelb fest sind.|Kalt abschrecken.|Im Kühlschrank aufbewahren und innerhalb weniger Tage essen.")
r("Tomate-Mozzarella", "S", 3, "k", "moz:80;tom:1;oel:1;~Basilikum, Salz und Pfeffer",
  "Mozzarella und Tomate in Scheiben schneiden.|Abwechselnd auf einen Teller legen.|Mit Öl, Basilikum, Salz und Pfeffer würzen.")
r("Skyr mit Mandeln und Zimt", "S", 2, "k", "skyr:150;mandel:20;~Zimt",
  "Mandeln grob hacken.|Über den Skyr streuen und mit Zimt bestäuben.",
  "Die DGE empfiehlt täglich etwa eine kleine Handvoll Nüsse (rund 25 g).")
r("Skyr mit Erdbeeren", "S", 2, "kg", "skyr:200;erdb:100",
  "Erdbeeren in Stücke schneiden oder auftauen lassen.|Mit dem Skyr mischen.")
r("Erdbeer-Quark-Shake", "S", 5, "kl", "milch:200;quark:150;erdb:100",
  "Alle Zutaten in einen Mixer geben.|Eine halbe Minute mixen und gleich trinken.")
r("Gurke mit Kräuterquark-Dip", "S", 5, "kga", "gurke:200;quark:150;zitrone:1;~Kräuter, Salz und Pfeffer",
  "Quark mit Zitronensaft, Kräutern, Salz und Pfeffer glatt rühren.|Gurke in Sticks schneiden und eintauchen.")
r("Paprika-Sticks mit Quark-Joghurt-Dip", "S", 5, "kga", "pap:1;quark:100;jog35:50;~Kräuter, Salz und Pfeffer",
  "Quark und Joghurt mit den Gewürzen verrühren.|Paprika in Streifen schneiden und eintauchen.")
r("Schinken-Gurken-Röllchen", "S", 5, "k", "schink:60;gurke:100;quark:50;~Pfeffer",
  "Quark auf die Schinkenscheiben streichen.|Gurke in Streifen schneiden und in den Schinken einrollen.|Mit Pfeffer würzen.")
r("Gouda mit Gurke und Tomate", "S", 3, "ka", "gouda:40;gurke:100;tom:1",
  "Gouda in Würfel, Gurke und Tomate in Stücke schneiden.|Zusammen auf einem Teller anrichten.")
r("Brot mit Quark und Tomate", "S", 3, "kg", "brot:1;quark:100;tom:1;~Salz und Pfeffer",
  "Quark mit Salz und Pfeffer würzen und aufs Brot streichen.|Mit Tomatenscheiben belegen.")
r("Mini-Pizza auf Brot", "S", 12, "g", "brot:2;stueck:60;moz:50;~Oregano",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Brot mit den Tomaten bestreichen, mit Oregano würzen und mit Mozzarella belegen.|8 bis 10 Minuten überbacken, bis der Käse zerlaufen ist.")
r("Wrap-Röllchen mit Putenaufschnitt", "S", 8, "ka", "wrap:1;quark:60;paufs:50;eisb:30;gurke:50",
  "Quark auf dem Wrap verstreichen.|Mit Aufschnitt, Salat und Gurkenstreifen belegen.|Fest aufrollen und schräg halbieren.")
r("Ei-Rucola-Brot mit Senf", "S", 12, "ga", "brot:1;ei:2;ruc:30;senf:1;~Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Brot mit Senf bestreichen und mit Rucola belegen.|Eier in Scheiben darauflegen und mit Pfeffer würzen.")
r("Tomaten-Gurken-Salat mit Joghurt und Parmesan", "S", 8, "kga", "gurke:150;tom:2;zwie:0.5;jog35:100;parm:10;~Salz, Pfeffer und Kräuter",
  "Gurke und Tomaten in Stücke schneiden, Zwiebel fein würfeln.|Mit Joghurt, Salz, Pfeffer und Kräutern mischen.|Mit gehobeltem Parmesan bestreuen.")
r("Eier-Muffins mit Paprika und Spinat", "S", 25, "pa", "ei:3;pap:0.5;spin:50;gouda:20;~Salz und Pfeffer",
  "Ofen auf 180 °C Ober- und Unterhitze vorheizen.|Paprika klein schneiden, Spinat grob hacken und in 3 Muffinförmchen verteilen.|Eier mit Gouda, Salz und Pfeffer verquirlen und darübergießen.|15 bis 20 Minuten backen, bis die Masse fest ist.")
r("Gurken-Mozzarella-Spieße", "S", 5, "k", "gurke:150;moz:60;tom:1;~Basilikum",
  "Gurke in Stücke, Mozzarella in Würfel und Tomate in Spalten schneiden.|Abwechselnd auf Spieße stecken.")
r("Eiersalat auf Brot", "S", 15, "ga", "ei:2;jog35:30;senf:1;brot:1;sgurke:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Eier mit einer Gabel zerdrücken und mit Joghurt, Senf, klein geschnittener Saurer Gurke, Salz und Pfeffer mischen.|Auf dem Brot servieren.")
r("Skyr-Schoko-Pudding", "S", 3, "kg", "skyr:200;kakao:2;honig:1",
  "Alles glatt rühren.|Kurz kühl stellen.")
r("Erdbeer-Skyr-Eis", "S", 5, "g", "skyr:150;erdb:150;honig:1",
  "Skyr, gefrorene Erdbeeren und Honig mit dem Stabmixer pürieren.|Sofort essen oder eine Stunde ins Gefrierfach stellen.")
r("Eier-Gurken-Salat", "S", 12, "ga", "ei:2;gurke:150;jog35:50;zitrone:1;~Salz, Pfeffer und Kräuter",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Eier und Gurke würfeln.|Mit Joghurt, Zitronensaft, Salz, Pfeffer und Kräutern mischen.")

# ======================= MITTAG UND ABEND (56) =======================
# --- Hähnchen (14)
r("Hähnchen-Reis-Pfanne", "M", 20, "p", "haehn:150;reis:70;pap:1;zwie:1;oel:1;soja:1",
  "Reis nach Packungsanleitung kochen.|Hähnchen in Streifen im Öl rundherum anbraten, bis es innen ganz durch ist und nichts Rosa mehr zu sehen ist.|Paprika und Zwiebel in Stücken dazugeben und einige Minuten mitbraten.|Reis unterrühren und mit Sojasauce abschmecken.",
  "Geflügel muss im Kern mindestens 70 °C erreichen.")
r("Hähnchen-Wrap", "M", 15, "a", "haehn:120;oel:1;jog35:40;wrap:1;eisb:40;gurke:60;tom:1;~Salz und Pfeffer",
  "Hähnchen in Streifen im Öl rundherum anbraten, bis es innen ganz durch ist.|Wrap mit dem Joghurt bestreichen und mit Salat, Gurke und Tomate belegen.|Das Hähnchen daraufgeben und einrollen.")
r("Ofenhähnchen mit Paprika und Couscous", "M", 35, "p", "haehn:150;pap:2;zwie:1;tom:2;oel:1;couscous:60;~Paprikapulver, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Paprika, Zwiebel und Tomaten in Stücke schneiden und mit Öl und Gewürzen auf einem Blech mischen.|Hähnchen würzen und dazulegen. 25 bis 30 Minuten backen, einmal wenden, bis es innen durch ist.|Couscous mit der gleichen Menge heißem Wasser übergießen, zugedeckt 5 Minuten quellen lassen und auflockern.")
r("Hähnchen-Nudelpfanne in Tomatensauce", "M", 25, "p", "haehn:130;nudel:70;stueck:200;zwie:1;knob:1;oel:1;parm:10;~Oregano, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Hähnchen würfeln und im Öl rundherum anbraten, bis es innen durch ist. Zwiebel und Knoblauch kurz mitbraten.|Tomaten zugeben und 8 Minuten köcheln lassen, würzen.|Nudeln untermischen und mit Parmesan bestreuen.")
r("Hähnchen-Rucola-Nudeln mit Parmesan", "M", 20, "", "haehn:130;nudel:70;ruc:50;parm:20;tom:2;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Hähnchen in Streifen im Öl anbraten, bis es innen ganz durch ist.|Tomaten in Stücken kurz mitbraten.|Nudeln, Rucola und Parmesan untermischen.")
r("Hähnchen-Salat mit Rucola und Parmesan", "M", 15, "a", "haehn:150;ruc:80;tom:2;gurke:100;parm:15;brot:1;oel:1;zitrone:1;~Salz und Pfeffer",
  "Hähnchen im Öl rundherum anbraten, bis es innen ganz durch ist, und in Streifen schneiden.|Rucola, Tomaten und Gurke in Stücken mit Zitronensaft, Salz und Pfeffer mischen.|Das Hähnchen und den Parmesan (gehobelt) darauf verteilen.|Mit dem Brot essen.")
r("Hähnchen-Bowl mit Joghurt-Sauce", "M", 25, "pa", "haehn:140;reis:60;gurke:100;tom:1;zwie:0.5;jog35:80;zitrone:1;oel:1;~Salz, Pfeffer und Paprikapulver",
  "Reis nach Packungsanleitung kochen.|Hähnchen würzen und im Öl rundherum anbraten, bis es innen ganz durch ist, dann in Scheiben schneiden.|Joghurt mit Zitronensaft, Salz und Pfeffer verrühren.|Reis, Gurke, Tomate, Zwiebel (in Ringen) und Hähnchen in einer Schale anrichten und die Sauce darübergeben.")
r("Überbackenes Hähnchen mit Tomate und Mozzarella", "M", 30, "", "haehn:150;tom:2;moz:60;stueck:100;nudel:60;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Nudeln nach Packungsanleitung kochen.|Hähnchen würzen und in eine Auflaufform legen, Tomatensauce darübergeben.|Tomatenscheiben und Mozzarella darauflegen und 20 Minuten backen, bis das Hähnchen innen durch ist.|Mit den Nudeln servieren.")
r("Hähnchen-Burrito mit Reis", "M", 25, "", "wrap:1;haehn:100;reis:40;pap:1;zwie:0.5;tom:1;gouda:25;oel:1;~Paprikapulver, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hähnchen in Streifen mit Paprika und Zwiebel im Öl anbraten, bis das Hähnchen innen ganz durch ist.|Wrap mit Reis, der Pfanne, Tomatenwürfeln und Gouda füllen.|Einrollen und bei Bedarf kurz in der Pfanne von beiden Seiten anbraten.")
r("Cheeseburger-Nudeln mit Hack und Saurer Gurke", "M", 25, "g", "ghack:100;nudel:70;stueck:150;gouda:30;sgurke:2;zwie:1;senf:1;~Paprikapulver, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Zwiebel klein schneiden, mit dem Hack in einer Pfanne krümelig durchbraten, bis nichts Rosa mehr zu sehen ist, und würzen.|Tomaten und Senf zugeben und 5 Minuten köcheln lassen.|Nudeln untermischen, Gouda darüberreiben und schmelzen lassen. Saure Gurken in Scheiben dazu.",
  "Schmeckt wie ein Cheeseburger, ist aber mit Gemüse und Vollkorn deutlich sättigender. Gemischtes Hack ist meist die günstigste Variante.")
r("Hähnchen-Sandwich mit Joghurt-Senf", "M", 15, "a", "brot:2;haehn:100;eisb:40;tom:1;sgurke:1;jog35:30;senf:1;oel:1;~Salz und Pfeffer",
  "Hähnchen im Öl rundherum anbraten, bis es innen ganz durch ist, und in Scheiben schneiden.|Joghurt mit Senf verrühren und aufs Brot streichen.|Mit Salat, Tomate, Saurer Gurke und Hähnchen belegen.")
r("Ofen-Nuggets mit Gurken-Dip", "M", 30, "", "haehn:150;hafer:30;ei:1;parm:10;oel:1;quark:80;gurke:100;pap:1;zitrone:1;~Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Hähnchen in Stücke schneiden. Haferflocken mit Parmesan, Salz und Pfeffer mischen, Ei verquirlen.|Die Stücke erst im Ei, dann in der Haferflocken-Mischung wenden und mit dem Öl beträufeln.|15 bis 20 Minuten backen, bis sie innen durch und goldbraun sind.|Quark mit klein geschnittener Gurke und Zitronensaft verrühren und mit Paprikastreifen dazu servieren.")
r("Hähnchen-Paprika-Pfanne mit Tzatziki", "M", 25, "", "haehn:150;zwie:1;oel:1;pap:1;couscous:50;jog35:100;gurke:100;knob:1;~Salz, Pfeffer und Paprikapulver",
  "Couscous mit der gleichen Menge heißem Wasser übergießen und zugedeckt quellen lassen.|Hähnchen in dünnen Streifen mit Zwiebel und Paprika im Öl scharf anbraten, bis es innen ganz durch ist.|Joghurt mit geriebener Gurke, Knoblauch, Salz und Pfeffer zum Tzatziki verrühren.|Alles zusammen anrichten.",
  "Magere Hähnchenbrust statt fettigem Gyros-Fleisch: kaum Fett, aber gleiches Würzgefühl.")
r("Tomaten-Hähnchen-Suppe", "M", 25, "pa", "stueck:300;haehn:120;zwie:1;knob:1;bruehe:300;reis:30;oel:1;parm:10;~Salz und Pfeffer",
  "Zwiebel und Knoblauch klein schneiden und im Öl anbraten.|Tomaten, Brühe und Reis zugeben und 10 Minuten köcheln lassen.|Hähnchen in kleinen Würfeln dazugeben und weitere 8 bis 10 Minuten garen, bis es innen durch ist.|Mit Parmesan, Salz und Pfeffer abschmecken.")

# --- Pute (6)
r("Puten-Paprika-Geschnetzeltes mit Reis", "M", 25, "p", "pute:150;pap:2;zwie:1;jog35:60;reis:60;oel:1;~Paprikapulver, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Pute in Streifen im Öl rundherum anbraten, bis sie innen durch ist.|Paprika und Zwiebel dazugeben und 5 Minuten mitbraten.|Joghurt unterrühren (nicht mehr kochen) und würzen. Mit dem Reis servieren.")
r("Putenhack-Paprika-Pfanne mit Couscous", "M", 25, "p", "phack:120;pap:2;zwie:1;stueck:100;couscous:60;oel:1;~Paprikapulver, Salz und Pfeffer",
  "Couscous mit der gleichen Menge heißem Wasser übergießen und zugedeckt quellen lassen.|Zwiebel im Öl anbraten, Hack dazugeben und krümelig durchbraten, bis nichts Rosa mehr zu sehen ist.|Paprika in Stücken und Tomaten zugeben und 8 Minuten garen, würzen.|Mit dem Couscous servieren.")
r("Puten-Wrap mit Eisbergsalat", "M", 15, "a", "wrap:1;pute:100;eisb:50;tom:1;sgurke:1;jog35:40;senf:1;oel:1;~Salz und Pfeffer",
  "Pute in Streifen im Öl rundherum anbraten, bis sie innen ganz durch ist.|Joghurt mit Senf verrühren und auf den Wrap streichen.|Mit Salat, Tomate, klein geschnittener Saurer Gurke und der Pute belegen und einrollen.")
r("Putenburger mit Salat", "M", 25, "", "phack:130;broetchen:1;eisb:40;tom:1;sgurke:2;zwie:0.5;oel:1;senf:1;~Salz und Pfeffer",
  "Hack mit Salz, Pfeffer und Senf verkneten und zu einem flachen Patty formen.|Im Öl von jeder Seite 5 bis 6 Minuten braten, bis es durch ist und nichts Rosa mehr zu sehen ist.|Brötchen aufschneiden und kurz anrösten.|Mit Salat, Tomate, Zwiebelringen, Saurer Gurke und dem Patty belegen.")
r("Puten-Reispfanne mit Tomate und Ei", "M", 20, "", "pute:120;reis:60;tom:2;ei:1;zwie:1;soja:1;oel:1;~Pfeffer",
  "Reis nach Packungsanleitung kochen.|Pute in Streifen im Öl anbraten, bis sie innen ganz durch ist. Zwiebel und Tomaten in Stücken kurz mitbraten.|Das Ei am Rand der Pfanne verrühren und fest werden lassen.|Reis und Sojasauce untermischen.")
r("Putenbrust mit Tomaten-Rucola-Couscous", "M", 20, "a", "pute:150;couscous:60;tom:2;ruc:40;gurke:100;zitrone:1;oel:1;~Salz und Pfeffer",
  "Couscous mit der gleichen Menge heißem Wasser übergießen und zugedeckt 5 Minuten quellen lassen.|Pute würzen und im Öl von beiden Seiten braten, bis sie innen ganz durch ist, dann in Scheiben schneiden.|Tomaten und Gurke würfeln und mit Rucola, Zitronensaft und dem Couscous mischen.|Die Pute darauflegen.")

# --- Rind (7)
r("Spaghetti Bolognese mit Vollkornnudeln", "M", 30, "p", "rhack:120;nudel:60;stueck:200;karo:1;zwie:1;tmark:1;knob:1;oel:1;parm:10;~Oregano, Salz und Pfeffer",
  "Zwiebel, Karotte und Knoblauch klein schneiden und im Öl 5 Minuten anbraten.|Hack dazugeben und krümelig durchbraten, bis nichts Rosa mehr zu sehen ist. Tomatenmark kurz mitrösten.|Tomaten zugeben und 15 Minuten köcheln lassen, würzen.|Nudeln kochen, mit der Sauce mischen und mit Parmesan bestreuen.")
r("Hackbällchen in Tomatensauce mit Reis", "M", 30, "p", "rhack:110;hafer:15;milch:30;stueck:200;zwie:1;knob:1;reis:55;~Oregano, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hack mit Haferflocken, Milch, der Hälfte der geriebenen Zwiebel, Salz und Pfeffer verkneten und zu kleinen Bällchen formen.|Restliche Zwiebel und Knoblauch anbraten, Tomaten zugeben und die Bällchen einlegen.|Zugedeckt 15 Minuten köcheln lassen, bis sie durch sind und innen nichts Rosa mehr zu sehen ist. Mit dem Reis servieren.")
r("Gefüllte Paprika mit Hack und Reis", "M", 40, "", "pap:2;rhack:120;reis:40;zwie:1;stueck:150;moz:40;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Reis nach Packungsanleitung kochen.|Paprika halbieren und entkernen. Hack mit Zwiebel anbraten, bis nichts Rosa mehr zu sehen ist, mit dem Reis mischen und würzen.|Paprika damit füllen, in eine Form setzen und die Tomaten daneben geben.|Mit Mozzarella belegen und 25 Minuten backen.")
r("Hamburger mit Salat und Saurer Gurke", "M", 25, "", "rhack:130;broetchen:1;eisb:40;tom:1;sgurke:2;zwie:0.5;gouda:20;~Salz und Pfeffer",
  "Hack mit Salz und Pfeffer zu einem flachen Patty formen.|In einer Pfanne von jeder Seite 5 bis 6 Minuten braten, bis es durch ist. Zum Schluss den Gouda darauflegen.|Brötchen aufschneiden und kurz anrösten.|Mit Salat, Tomate, Zwiebelringen, Saurer Gurke und dem Patty belegen.")
r("Chili con Carne mit Reis", "M", 35, "p", "rhack:100;bohne:100;stueck:200;pap:1;zwie:1;tmark:1;knob:1;reis:50;~Paprikapulver, Chili, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Knoblauch anbraten, Hack dazugeben und krümelig durchbraten, bis nichts Rosa mehr zu sehen ist.|Tomatenmark, Paprika in Stücken, Tomaten und Bohnen zugeben und 20 Minuten köcheln.|Würzen und mit dem Reis servieren.",
  "Enthält Hülsenfrüchte. Wenn du die nicht magst, schließ sie im Filter aus.")
r("Taco-Wrap mit Hack, Salat und Gouda", "M", 20, "", "wrap:1;rhack:100;eisb:50;tom:1;pap:1;gouda:25;zwie:0.5;jog35:30;~Paprikapulver, Salz und Pfeffer",
  "Hack mit Zwiebel in einer Pfanne krümelig durchbraten, bis nichts Rosa mehr zu sehen ist, und würzen.|Wrap mit Joghurt bestreichen und mit Salat, Tomate und Paprika belegen.|Hack und Gouda daraufgeben und einrollen.")
r("Hack-Spinat-Nudeln mit Mozzarella", "M", 25, "", "rhack:100;nudel:60;spin:100;stueck:100;moz:40;zwie:1;knob:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Hack mit Zwiebel und Knoblauch krümelig durchbraten, bis nichts Rosa mehr zu sehen ist.|Tomaten und Spinat zugeben und 5 Minuten garen.|Nudeln untermischen, Mozzarella (gerupft) daraufgeben und schmelzen lassen.")

# --- Vegetarisch mit Ei und Käse (12)
r("Shakshuka mit Brot", "M", 20, "g", "ei:3;stueck:250;pap:1;zwie:1;knob:1;oel:1;brot:1;~Paprikapulver, Salz und Pfeffer",
  "Zwiebel, Knoblauch und Paprika klein schneiden und im Öl 5 Minuten anbraten.|Tomaten und Gewürze zugeben und 8 Minuten köcheln lassen.|Drei Mulden formen, Eier hineingleiten lassen, Deckel drauf.|5 bis 8 Minuten garen, bis Eiweiß und Eigelb fest sind. Mit dem Brot essen.")
r("Gebratener Reis mit Ei und Paprika", "M", 20, "g", "reis:60;ei:3;pap:1.5;zwie:1;soja:1;oel:1;~Pfeffer",
  "Reis nach Packungsanleitung kochen (gern vom Vortag, gut abgekühlt).|Zwiebel und Paprika im Öl 4 Minuten anbraten.|Reis dazugeben, Eier darüberschlagen und rühren, bis sie ganz fest sind.|Mit Sojasauce und Pfeffer würzen.")
r("Pizza-Wraps mit Tomate und Mozzarella", "M", 15, "g", "wrap:2;stueck:80;moz:80;pap:1;tom:1;~Oregano",
  "Ofen auf 220 °C Ober- und Unterhitze vorheizen.|Wraps auf ein Blech legen, mit der Tomatensauce bestreichen und mit Paprika, Tomate und Mozzarella belegen.|Mit Oregano bestreuen und 8 bis 10 Minuten knusprig backen.")
r("Nudelauflauf mit Tomate, Paprika und Mozzarella", "M", 40, "p", "nudel:70;stueck:200;pap:1;moz:70;parm:10;zwie:1;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Nudeln 2 Minuten kürzer als angegeben kochen.|Zwiebel klein schneiden und mit Tomaten, Paprika in Stücken und Gewürzen mischen.|Nudeln unterheben, in eine Form geben und mit Mozzarella und Parmesan bestreuen.|20 bis 25 Minuten backen, bis der Käse goldbraun ist.")
r("Quark-Spinat-Nudeln", "M", 20, "g", "nudel:80;quark:150;spin:150;knob:1;zwie:1;parm:15;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen und eine Tasse Nudelwasser aufheben.|Zwiebel und Knoblauch im Öl anbraten, Spinat zugeben und zusammenfallen lassen.|Quark mit einem Schuss Nudelwasser glatt rühren, würzen und mit den Nudeln und dem Spinat mischen.|Mit Parmesan bestreuen.")
r("Tomaten-Risotto mit Parmesan und Spiegelei", "M", 30, "", "reis:65;tom:2;stueck:100;zwie:1;bruehe:350;parm:25;ei:2;oel:2;~Pfeffer",
  "Zwiebel klein schneiden und in einem Teelöffel Öl glasig anbraten. Reis kurz mitrösten.|Brühe nach und nach zugeben und unter Rühren 18 bis 20 Minuten garen, bis der Reis weich ist.|Frische Tomaten in Stücken und die stückigen Tomaten die letzten 5 Minuten unterrühren, dann den Parmesan.|Eier im restlichen Öl zu Spiegeleiern braten, bis das Eiweiß fest ist, und daraufsetzen.")
r("Pasta mit Tomaten, Rucola und Mozzarella", "M", 20, "", "nudel:80;tom:3;ruc:40;moz:80;knob:1;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Knoblauch und Tomaten in Stücken im Öl 5 Minuten schmoren.|Nudeln mit den Tomaten mischen, Rucola und Mozzarella (gerupft) unterheben.")
r("Eier-Salat-Bowl mit Eisbergsalat", "M", 20, "a", "eisb:150;ei:3;tom:2;gurke:100;brot:2;jog35:60;senf:1;zitrone:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Joghurt mit Senf, Zitronensaft, Salz und Pfeffer zum Dressing verrühren.|Salat, Tomaten und Gurke in einer Schale mischen, Eier in Vierteln darauflegen.|Dressing darübergeben und das Brot dazu essen.")
r("Caprese-Sandwich mit Rucola", "M", 8, "ka", "brot:2;moz:80;tom:2;ruc:30;oel:1;~Salz und Pfeffer",
  "Brot mit dem Öl beträufeln.|Mit Mozzarella, Tomatenscheiben und Rucola belegen.|Würzen und zuklappen.")
r("Käse-Omelett mit Salat", "M", 15, "", "ei:3;gouda:30;eisb:80;tom:1;gurke:80;brot:1;oel:1;~Salz und Pfeffer",
  "Eier verquirlen, würzen und im Öl stocken lassen, bis sie fest sind. Mit dem Gouda zuklappen.|Salat, Tomate und Gurke in Stücken mischen.|Omelett mit Salat und Brot servieren.")
r("Kräuterquark mit Vollkornbrot", "M", 5, "kga", "brot:2;quark:200;gurke:100;pap:1;tom:1;oel:1;~Kräuter, Salz und Pfeffer",
  "Quark mit Kräutern, Öl, Salz und Pfeffer verrühren.|Gurke, Paprika und Tomate in Stücke schneiden.|Den Quark auf das Brot streichen oder dazu essen.")
r("Abendbrot mit Ei und Gouda", "M", 5, "kga", "brot:2;ei:1;gouda:40;gurke:100;tom:1;~Pfeffer und Kräuter",
  "Brot mit dem Gouda belegen.|Das hart gekochte Ei (am besten vom Vortag) in Scheiben schneiden, Gurke und Tomate dazulegen.|Mit Pfeffer und Kräutern würzen.")

# --- Hülsenfrüchte (6)
r("Linsen-Curry", "M", 25, "pg", "linse:80;stueck:200;kokos:100;zwie:1;knob:1;oel:1;curry:2;~Salz",
  "Zwiebel und Knoblauch klein schneiden und im Öl glasig anbraten.|Currypulver kurz mitrösten.|Gespülte Linsen, Tomaten, Kokosmilch und etwa 150 ml Wasser zugeben.|Etwa 15 Minuten köcheln, bis die Linsen weich sind, und salzen.",
  "Hülsenfrüchte sollten laut Deutscher Gesellschaft für Ernährung mindestens einmal pro Woche auf den Tisch.")
r("Linsen-Bolognese mit Vollkornnudeln", "M", 25, "pg", "linse:60;nudel:70;stueck:200;karo:1;zwie:1;knob:1;tmark:1;oel:1;~Oregano, Salz und Pfeffer",
  "Zwiebel, Karotte und Knoblauch klein schneiden und im Öl 5 Minuten anbraten.|Tomatenmark kurz mitrösten.|Gespülte Linsen, Tomaten und etwa 200 ml Wasser zugeben und 15 Minuten köcheln lassen.|Nudeln kochen, die Sauce würzen und über die Nudeln geben.",
  "Mit etwas Parmesan bestreut schmeckt sie noch besser, dann ist sie aber nicht mehr vegan.")
r("Kichererbsen-Salat mit Mozzarella", "M", 10, "kga", "kiche:150;gurke:100;tom:2;zwie:0.5;moz:60;oel:1;zitrone:1;~Salz und Pfeffer",
  "Kichererbsen abspülen und abtropfen lassen.|Gurke und Tomaten würfeln, Zwiebel fein schneiden.|Mit Öl, Zitronensaft, Salz und Pfeffer mischen und Mozzarella (gewürfelt) unterheben.")
r("Chili sin Carne mit Reis", "M", 30, "pg", "bohne:120;kiche:60;stueck:200;pap:1;zwie:1;tmark:1;knob:1;reis:50;gouda:20;~Paprikapulver, Chili, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Knoblauch anbraten, Paprika in Stücken, Tomatenmark, Tomaten, Bohnen und Kichererbsen zugeben.|20 Minuten köcheln lassen und würzen.|Mit Reis servieren und mit dem Gouda bestreuen.")
r("Linsen-Tomaten-Suppe mit Parmesan", "M", 25, "pg", "linse:70;stueck:250;zwie:1;knob:1;bruehe:300;oel:1;parm:10;~Salz und Pfeffer",
  "Zwiebel und Knoblauch im Öl anbraten.|Linsen, Tomaten und Brühe zugeben und 15 bis 20 Minuten köcheln lassen, bis die Linsen weich sind.|Mit Salz und Pfeffer abschmecken und mit Parmesan bestreuen.")
r("Bohnen-Gouda-Quesadilla", "M", 15, "g", "wrap:1;bohne:80;gouda:40;pap:1;tom:1;~Paprikapulver, Salz und Pfeffer",
  "Bohnen grob zerdrücken und mit Paprikapulver, Salz und Pfeffer würzen.|Eine Wraphälfte mit Bohnen, Paprika in Streifen, Tomate und Gouda belegen und zuklappen.|Ohne Öl von beiden Seiten in einer Pfanne knusprig braten, bis der Käse schmilzt.")

# --- Salate und Bowls (7)
r("Nudelsalat mit Gurke, Tomate und Mozzarella", "M", 20, "pa", "nudel:70;gurke:100;tom:2;moz:60;jog35:60;zwie:0.5;zitrone:1;senf:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen und abkühlen lassen.|Joghurt mit Zitronensaft, Senf, Salz und Pfeffer verrühren.|Gurke und Tomaten würfeln, Zwiebel fein schneiden und mit Mozzarella und den Nudeln mischen.|Dressing unterheben und eine Stunde durchziehen lassen.")
r("Hähnchen-Nudelsalat mit Paprika", "M", 25, "pa", "nudel:60;haehn:120;pap:1;gurke:100;sgurke:2;jog35:60;senf:1;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen und abkühlen lassen.|Hähnchen in Würfeln im Öl anbraten, bis es innen ganz durch ist, und abkühlen lassen.|Joghurt mit Senf, Salz und Pfeffer verrühren.|Alles mit Paprika, Gurke und klein geschnittener Saurer Gurke mischen.")
r("Hack-Paprika-Reispfanne", "M", 25, "g", "ghack:100;reis:60;pap:2;zwie:1;tmark:1;soja:1;knob:1;~Paprikapulver und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Knoblauch klein schneiden, mit dem Hack in einer Pfanne krümelig durchbraten, bis nichts Rosa mehr zu sehen ist.|Paprika in Würfeln und Tomatenmark zugeben und 6 Minuten braten.|Reis und Sojasauce untermischen und würzen.",
  "Eine günstige Pfanne, die sich gut für zwei Portionen kochen lässt.")
r("Eisbergsalat-Bowl mit Putenaufschnitt und Ei", "M", 20, "a", "eisb:150;paufs:60;ei:2;tom:1;gurke:100;jog35:70;senf:1;brot:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Joghurt mit Senf, Salz und Pfeffer zum Dressing verrühren.|Salat, Tomate, Gurke und Aufschnitt in einer Schale anrichten, Eier in Vierteln darauflegen.|Dressing darübergeben und das Brot dazu essen.")
r("Mediterraner Hähnchen-Salat mit Mozzarella", "M", 20, "a", "haehn:120;gurke:150;tom:2;zwie:0.5;pap:1;moz:50;oel:1;zitrone:1;brot:1;~Oregano, Salz und Pfeffer",
  "Hähnchen würzen und im Öl rundherum anbraten, bis es innen ganz durch ist, dann in Streifen schneiden.|Gurke, Tomaten und Paprika in Stücken, Zwiebel in Ringen mit Zitronensaft und Oregano mischen.|Mozzarella und Hähnchen darauflegen und mit dem Brot essen.")
r("Herzhafte Quark-Bowl mit Ei und Gemüse", "M", 15, "ga", "quark:200;gurke:100;tom:1;pap:1;ei:2;brot:1;~Kräuter, Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Quark mit Kräutern, Salz und Pfeffer in eine Schale geben.|Gurke, Tomate und Paprika in Stücken und die Eier in Vierteln darauf anrichten.|Mit dem Brot essen.")
r("Puten-Salat mit Rucola und Joghurt-Dressing", "M", 20, "a", "pute:120;ruc:60;eisb:60;tom:2;gurke:100;jog35:60;zitrone:1;oel:1;brot:1;~Salz und Pfeffer",
  "Pute würzen und im Öl von beiden Seiten braten, bis sie innen ganz durch ist, dann in Streifen schneiden.|Joghurt mit Zitronensaft, Salz und Pfeffer verrühren.|Rucola, Salat, Tomaten und Gurke mischen, die Pute darauflegen und das Dressing darübergeben.|Mit dem Brot essen.")

# --- Suppen (3)
r("Cremige Tomatensuppe mit Parmesan und Brot", "M", 25, "pg", "stueck:400;zwie:1;knob:1;bruehe:200;quark:100;parm:15;brot:2;oel:1;~Salz und Pfeffer",
  "Zwiebel und Knoblauch im Öl glasig anbraten.|Tomaten und Brühe zugeben und 10 Minuten köcheln lassen, dann fein pürieren.|Quark unterrühren (nicht mehr kochen) und würzen.|Mit Parmesan bestreuen und mit dem Brot essen.")
r("Frikadellen mit Tomaten-Gurken-Salat", "M", 25, "g", "ghack:120;ei:1;zwie:0.5;hafer:20;senf:1;oel:1;tom:2;gurke:100;brot:1;~Salz und Pfeffer",
  "Hack mit Ei, klein geschnittener Zwiebel, Haferflocken, Senf, Salz und Pfeffer gut verkneten und zu flachen Frikadellen formen.|Im Öl bei mittlerer Hitze von jeder Seite 6 bis 7 Minuten braten, bis sie innen ganz durch sind.|Tomaten und Gurke in Stücke schneiden und mit Salz und Pfeffer mischen.|Mit dem Brot essen.",
  "Die Haferflocken ersetzen das Brötchen im Teig und binden zusätzlich Saft.")
r("Hähnchen-Reis-Suppe mit Paprika", "M", 25, "pg", "bruehe:400;haehn:120;reis:40;pap:1;zwie:1;~Salz und Pfeffer",
  "Zwiebel und Paprika in Stücken mit der Brühe aufkochen, den Reis zugeben und 10 Minuten köcheln lassen.|Hähnchen in kleinen Würfeln dazugeben und weitere 8 bis 10 Minuten garen, bis es innen durch ist.|Mit Salz und Pfeffer abschmecken.")

# --- Nudeln (1)
r("Spaghetti Carbonara light mit Tomatensalat", "M", 20, "", "nudel:70;ei:2;schink:40;parm:20;zwie:0.5;tom:2;~Pfeffer",
  "Nudeln nach Packungsanleitung kochen und eine Tasse Nudelwasser aufheben.|Schinken und Zwiebel klein schneiden, ohne Öl anbraten.|Eier mit Parmesan und Pfeffer verrühren.|Die heißen Nudeln mit der Pfanne mischen, vom Herd nehmen, die Eimischung mit einem Schuss Nudelwasser unterrühren, bis eine cremige Sauce entsteht.|Tomaten in Stücken mit Pfeffer als Salat dazu essen.")

# ======================= NEU: Vor der Arbeit (schnelle Frühstücke) =======================
r("Skyr-Haferbrei mit Banane und Mandeln", "F", 8, "", "hafer:50;milch:200;banane:1;skyr:100;mandel:10;~Zimt",
  "Haferflocken mit der Milch im Topf unter Rühren aufkochen und 3 Minuten quellen lassen.|Banane in Stücken zerdrücken und unterrühren.|Den Brei in eine Schüssel geben, Skyr daraufsetzen, Mandeln hacken und mit Zimt darüberstreuen.",
  "Warm macht er auch an kalten Morgen satt. Skyr erst am Ende zugeben, so bleibt er cremig.")
r("Brötchen mit Rührei und Gouda", "F", 8, "a", "broetchen:1;ei:2;gouda:20;tom:1;oel:1;~Salz und Pfeffer",
  "Eier verquirlen und im Öl bei mittlerer Hitze unter Rühren stocken lassen, bis nichts Flüssiges mehr zu sehen ist.|Brötchen aufschneiden, mit Gouda und Tomatenscheiben belegen.|Das Rührei daraufgeben und zuklappen.",
  "Lässt sich in Papier gewickelt gut mit zur Arbeit nehmen.")
r("Quark-Pfannkuchen mit Erdbeeren", "F", 15, "", "quark:150;ei:2;hafer:40;oel:1;erdb:100;honig:1",
  "Erdbeeren mit einem Esslöffel Wasser im Topf kurz aufkochen, mindestens 2 Minuten sprudelnd, und abkühlen lassen.|Quark, Eier und Haferflocken zu einem glatten Teig verrühren.|Das Öl in einer Pfanne erhitzen, den Teig in zwei kleinen Portionen bei mittlerer Hitze von jeder Seite 3 bis 4 Minuten backen.|Mit den Erdbeeren und dem Honig servieren.",
  "Viel Eiweiß ohne Mehl. Die Pfannkuchen sind weich, wende sie erst, wenn der Rand fest ist.")
r("Tassen-Omelett aus der Mikrowelle", "F", 5, "", "ei:3;milch:30;gouda:20;tom:1;~Salz und Pfeffer",
  "Eier mit der Milch in einer großen mikrowellengeeigneten Schüssel oder Tasse verquirlen, Gouda und Tomate in kleinen Stücken unterrühren, würzen.|Bei 600 bis 800 Watt 1 Minute erhitzen, durchrühren und weitere 45 bis 60 Sekunden erhitzen, bis das Ei ganz fest ist.|Kurz stehen lassen und aus der Tasse essen.",
  "Der schnellste warme Start, wenn es vor der Arbeit eilig ist. Das Ei muss durch und fest sein.")
r("Putenbrötchen mit Quark-Senf-Aufstrich", "F", 5, "ka", "broetchen:1;paufs:50;quark:50;gurke:80;senf:1;~Pfeffer",
  "Quark mit Senf und Pfeffer verrühren.|Brötchen aufschneiden und mit dem Aufstrich bestreichen.|Mit Putenaufschnitt und Gurkenscheiben belegen.",
  "Der Quark macht das Brötchen saftig und bringt zusätzliches Eiweiß.")
r("Overnight Oats mit Quark, Banane und Honig", "F", 5, "kpa", "hafer:60;chia:10;milch:120;quark:150;banane:1;honig:1",
  "Haferflocken, Chia, Milch und Quark im Glas verrühren.|Abgedeckt über Nacht in den Kühlschrank stellen.|Vor dem Essen die Banane in Scheiben und den Honig daraufgeben.",
  "Am Abend vorbereitet ist das Frühstück morgens in einer Minute fertig und passt in eine Tasche.")
r("Frühstücks-Wrap mit Quark, Ei und Tomate", "F", 10, "a", "wrap:1;ei:2;quark:50;tom:1;oel:1;~Salz und Pfeffer",
  "Eier im Öl rühren, bis sie ganz fest sind.|Wrap mit dem Quark bestreichen und mit Tomatenscheiben belegen.|Rührei daraufgeben, würzen, einrollen und halbieren.")
r("Ei im Brot mit Mozzarella und Tomate", "F", 10, "", "brot:2;ei:2;moz:30;oel:1;tom:1;~Salz und Pfeffer",
  "In jede Brotscheibe mit einem Glas ein Loch drücken oder schneiden.|Öl in der Pfanne erhitzen, die Brotscheiben und die ausgestochenen Kreise hineinlegen und in jedes Loch ein Ei schlagen.|Bei mittlerer Hitze 3 Minuten braten, wenden und mit Mozzarella in Stücken belegen, bis das Eigelb und das Eiweiß fest sind.|Mit Tomatenscheiben servieren.")

# ======================= NEU: Pause und Snack zum Mitnehmen =======================
r("Pizza-Muffins aus Ei mit Tomate und Mozzarella", "S", 25, "pa", "ei:2;tom:1;moz:30;milch:20;~Oregano, Salz und Pfeffer",
  "Ofen auf 180 °C Ober- und Unterhitze vorheizen und zwei Mulden einer Muffinform fetten.|Eier mit der Milch und den Gewürzen verquirlen, Tomate und Mozzarella in kleinen Stücken unterrühren.|In die Mulden füllen und 15 bis 18 Minuten backen, bis die Muffins gestockt und leicht gebräunt sind.",
  "Für mehrere Tage verdoppelst du die Menge. Gekühlt halten sich die Muffins 2 bis 3 Tage, kalt oder aufgewärmt essen.")
r("Haferriegel mit Banane, Quark und Kakao", "S", 30, "pa", "hafer:40;banane:1;ei:1;quark:50;kakao:1",
  "Ofen auf 180 °C Ober- und Unterhitze vorheizen.|Banane zerdrücken und mit Ei, Quark, Haferflocken und Kakao verrühren.|Den Teig etwa 2 cm dick auf ein Blech mit Backpapier streichen und 18 bis 20 Minuten backen.|Abkühlen lassen und in Riegel schneiden.",
  "Hält sich gekühlt 2 bis 3 Tage und passt in die Jackentasche.")
r("Kleiner Bohnen-Wrap mit Quark", "S", 5, "ka", "wrap:1;bohne:60;quark:40;tom:1;~Paprikapulver, Salz und Pfeffer",
  "Bohnen abtropfen lassen und mit der Gabel grob zerdrücken.|Wrap mit Quark bestreichen, Bohnen und Tomatenscheiben darauf verteilen und würzen.|Einrollen und halbieren.")
r("Kichererbsen-Aufstrich mit Gurke auf Brot", "S", 10, "ka", "kiche:100;zitrone:1;oel:1;knob:0.5;brot:1;gurke:50;~Salz, Pfeffer und Paprikapulver",
  "Kichererbsen mit Zitronensaft, Öl, Knoblauch und Gewürzen fein pürieren oder mit der Gabel sehr fein zerdrücken.|Brot dick bestreichen und mit Gurkenscheiben belegen.",
  "Der Aufstrich hält abgedeckt 3 bis 4 Tage im Kühlschrank.")
r("Putenbrot mit Quark und Gurke", "S", 5, "ka", "brot:2;quark:40;paufs:40;gurke:60;~Pfeffer",
  "Die Brotscheiben mit Quark bestreichen.|Mit Putenaufschnitt und Gurkenscheiben belegen, pfeffern und zusammenklappen.")
r("Quark-Haferglas mit Banane", "S", 3, "ka", "quark:150;jog35:50;hafer:30;banane:1;~Zimt",
  "Quark und Joghurt im Glas glatt rühren.|Haferflocken unterheben, Banane in Scheiben darauflegen und mit Zimt bestreuen.",
  "Wenn du es morgens zubereitest und zur Arbeit mitnimmst, ziehen die Haferflocken bis zur Pause schön an.")
r("Brotzeit-Box mit Ei, Putenaufschnitt und Gurke", "S", 5, "ka", "ei:1;paufs:40;brot:1;gurke:60;tom:1;sgurke:1",
  "Das Ei vorher hart kochen (mindestens 8 Minuten) und pellen.|Alles in Stücke schneiden und in einer Box verpacken.|Das Brot dazulegen.",
  "Kalt gedacht, kein Aufwärmen nötig. Koch gleich mehrere Eier für die ganze Woche vor.")
r("Schinken-Käse-Brötchen mit Gurke", "S", 3, "ka", "broetchen:1;schink:40;gouda:15;gurke:60;senf:1",
  "Brötchen aufschneiden und mit Senf bestreichen.|Mit Schinken, Gouda und Gurkenscheiben belegen.")
r("Mozzarella-Brötchen mit Tomate und Rucola", "S", 5, "ka", "broetchen:1;moz:50;tom:1;ruc:10;~Salz und Pfeffer",
  "Brötchen aufschneiden.|Mozzarella und Tomate in Scheiben schneiden, mit Rucola auf dem Brötchen verteilen und würzen.")

# ======================= NEU: Mittag und Abend =======================
r("Reissalat mit Hähnchen, Paprika und Gurke", "M", 25, "pa", "haehn:130;reis:60;pap:1;gurke:80;zwie:0.5;oel:1;zitrone:1;senf:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen und abkühlen lassen.|Hähnchen in Würfeln im Öl rundherum anbraten, bis es innen ganz durch ist, und auskühlen lassen.|Paprika, Gurke und Zwiebel klein schneiden, mit Zitronensaft, Senf, Salz und Pfeffer anmachen.|Alles mit Reis und Hähnchen vermengen.",
  "Als Box zur Arbeit gut geeignet. Gekühlt aufbewahren und spätestens am nächsten Tag essen.")
r("Hähnchen-Brötchen mit Quark-Senf-Creme", "M", 15, "a", "haehn:100;oel:0.5;broetchen:2;quark:40;ruc:20;tom:1;senf:1;~Salz und Pfeffer",
  "Hähnchen in dünne Streifen schneiden und im Öl rundherum anbraten, bis es innen ganz durch ist.|Quark mit Senf, Salz und Pfeffer verrühren.|Brötchen aufschneiden, mit der Creme bestreichen, mit Rucola, Tomatenscheiben und Hähnchen belegen.")
r("Burrito-Wrap mit Hack und Bohnen", "M", 25, "pa", "ghack:80;bohne:80;wrap:1;tmark:1;zwie:1;pap:1;~Paprikapulver, Salz und Pfeffer",
  "Zwiebel und Paprika klein schneiden und mit dem Hack krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Bohnen und Tomatenmark zugeben, würzen und 5 Minuten köcheln lassen.|Die Füllung auf den Wrap geben, einrollen und in Folie wickeln.",
  "Schmeckt warm und kalt. Gewickelt hält er im Kühlschrank 2 Tage.")
r("Asia-Nudelpfanne mit Hähnchen und Paprika", "M", 20, "", "haehn:130;nudel:70;pap:1;zwie:1;knob:1;soja:2;honig:1;oel:1",
  "Nudeln nach Packungsanleitung kochen.|Hähnchen in Streifen im Öl rundherum anbraten, bis es innen durch ist. Paprika und Zwiebel in Streifen sowie klein geschnittenen Knoblauch zugeben und 4 Minuten mitbraten.|Sojasauce und Honig verrühren, mit den Nudeln in die Pfanne geben und alles gut vermengen.")
r("Putenhack-Reis-Bowl mit Gurke und Joghurt", "M", 20, "p", "phack:130;reis:60;gurke:100;jog35:50;pap:1;oel:1;curry:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Putenhack mit Curry im Öl krümelig durchbraten, bis nichts Rosa mehr zu sehen ist. Paprika in Würfeln kurz mitbraten.|Gurke würfeln. Reis, Hack und Gurke in eine Schüssel geben und mit Joghurt toppen.")
r("Hack-Quesadilla mit Paprika und Gouda", "M", 20, "a", "wrap:1;ghack:80;pap:1;gouda:30;zwie:0.5;tmark:1;~Paprikapulver, Salz und Pfeffer",
  "Hack mit klein geschnittener Zwiebel und Paprika in einer Pfanne krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Tomatenmark und Gewürze zugeben.|Den Wrap in eine Pfanne legen, auf einer Hälfte Füllung und Gouda verteilen und zuklappen.|Von jeder Seite 2 bis 3 Minuten braten, bis der Käse geschmolzen ist.")
r("Nudel-Hack-Auflauf mit Tomate und Mozzarella", "M", 45, "p", "ghack:90;nudel:60;stueck:200;zwie:1;moz:40;parm:10;knob:1;~Oregano, Salz und Pfeffer",
  "Nudeln 2 Minuten kürzer als auf der Packung angegeben kochen. Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Hack mit Zwiebel und Knoblauch krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Tomaten und Gewürze zugeben und 5 Minuten köcheln lassen.|Nudeln und Sauce in eine Form geben, mit Mozzarella und Parmesan bestreuen und 20 Minuten überbacken.",
  "Ein Auflauf für mehrere Tage: gekühlt 2 Tage haltbar, vor dem Essen vollständig erhitzen.")
r("Hack-Kichererbsen-Eintopf mit Tomate", "M", 30, "p", "ghack:80;kiche:120;stueck:250;zwie:1;pap:1;tmark:1;knob:1;~Paprikapulver, Kreuzkümmel, Salz und Pfeffer",
  "Hack mit Zwiebel und Knoblauch krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Paprika in Würfeln und Tomatenmark zugeben und 2 Minuten mitbraten.|Tomaten, Kichererbsen und Gewürze zugeben und 15 Minuten köcheln lassen.",
  "Eintöpfe wie dieser schmecken am nächsten Tag noch besser und lassen sich gut einfrieren.")
r("Hähnchen-Curry mit Kokosmilch und Reis", "M", 30, "", "haehn:130;kokos:150;reis:60;pap:1;zwie:1;curry:2;knob:1;oel:1;stueck:100",
  "Reis nach Packungsanleitung kochen.|Hähnchen in Würfeln im Öl rundherum anbraten, bis es innen ganz durch ist. Zwiebel, Paprika und Knoblauch zugeben und 3 Minuten mitbraten.|Curry kurz mitrösten, Tomaten und Kokosmilch zugießen und 10 Minuten köcheln lassen.|Mit dem Reis servieren.")
r("Mexikanische Bohnen-Eier-Pfanne mit Brot", "M", 20, "g", "bohne:120;ei:2;stueck:150;zwie:1;pap:1;oel:1;brot:1;~Paprikapulver, Salz und Pfeffer",
  "Zwiebel und Paprika klein schneiden und im Öl 4 Minuten anbraten.|Tomaten, Bohnen und Gewürze zugeben und 6 Minuten köcheln lassen.|Zwei Mulden formen, die Eier hineinschlagen und mit Deckel 6 bis 8 Minuten garen, bis Eiweiß und Eigelb fest sind.|Mit dem Brot essen.")
r("Hähnchen-Nudeln mit Paprika-Quark-Sauce", "M", 25, "", "haehn:120;nudel:70;pap:2;quark:80;knob:1;oel:1;parm:10;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen und etwas Kochwasser aufheben.|Hähnchen in Streifen im Öl rundherum anbraten, bis es innen durch ist. Paprika in Würfeln und Knoblauch 5 Minuten mitbraten.|Quark mit einem Schuss Kochwasser glatt rühren, mit den Nudeln und der Pfanne vermengen, kurz erwärmen, nicht kochen.|Mit Parmesan bestreuen.")
r("Knusprige Putenbrust mit Haferkruste und Salat", "M", 25, "", "pute:130;ei:1;hafer:25;parm:10;oel:1;eisb:100;tom:1;gurke:80;zitrone:1;~Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Pute flach klopfen und würzen. Ei verquirlen, Haferflocken mit Parmesan mischen.|Pute erst im Ei, dann in der Haferflockenmischung wenden, auf einem Blech mit Öl beträufeln und 15 bis 18 Minuten backen, bis sie innen ganz durch ist.|Salat, Tomate und Gurke mit Zitronensaft anmachen und dazu essen.")
r("Kichererbsen-Wrap mit Quark-Dip", "M", 20, "a", "wrap:1;kiche:120;quark:80;gurke:60;tom:1;ruc:20;zitrone:1;oel:1;~Paprikapulver, Salz und Pfeffer",
  "Kichererbsen im Öl mit Paprikapulver 5 Minuten anbraten.|Quark mit Zitronensaft, Salz und Pfeffer verrühren.|Wrap mit dem Dip bestreichen, mit Gurke, Tomate, Rucola und Kichererbsen füllen und einrollen.")
r("Hack-Paprika-Suppe mit Nudeln", "M", 35, "p", "ghack:100;pap:2;zwie:1;stueck:200;bruehe:400;tmark:1;nudel:30;~Paprikapulver, Salz und Pfeffer",
  "Hack mit Zwiebel krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Paprika in Würfeln, Tomatenmark und Paprikapulver zugeben und kurz mitbraten.|Tomaten und Brühe zugießen, 15 Minuten köcheln lassen, die Nudeln zugeben und weitere 8 bis 10 Minuten garen.",
  "Die Suppe ist günstig und lässt sich gut vorkochen und einfrieren.")
r("Joghurt-Hähnchen aus dem Ofen mit Reis und Gurkensalat", "M", 35, "", "haehn:140;jog35:60;curry:1;reis:60;gurke:120;tom:1;zitrone:1;oel:1;~Salz und Pfeffer",
  "Hähnchen mit Joghurt, Curry, Salz und Pfeffer mindestens 15 Minuten marinieren. Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Reis nach Packungsanleitung kochen.|Hähnchen auf ein geöltes Blech legen und 20 bis 25 Minuten backen, bis es innen ganz durch ist.|Gurke und Tomate würfeln, mit Zitronensaft und Salz anmachen.")
r("Hack-Paprika-Pfanne mit Rührei", "M", 20, "g", "ghack:100;ei:2;pap:2;zwie:1;~Paprikapulver, Salz und Pfeffer",
  "Hack mit Zwiebel krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Paprika in Streifen zugeben und 5 Minuten mitbraten, würzen.|Die Eier darüber verquirlen und unter Rühren stocken lassen, bis sie fest sind.")
r("Kichererbsen-Reispfanne mit Ei", "M", 20, "g", "kiche:120;reis:60;ei:2;pap:1;zwie:1;tom:1;soja:1;oel:1;~Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Paprika klein schneiden und im Öl 4 Minuten anbraten. Kichererbsen zugeben und 3 Minuten mitbraten.|Die Eier am Rand verrühren und fest werden lassen, dann alles mit Reis und Sojasauce vermengen.|Tomate in Stücken zum Schluss unterheben.")
r("Putenhack-Bällchen mit Joghurt-Sauce und Couscous", "M", 25, "", "phack:130;ei:0.5;hafer:15;couscous:60;jog35:60;gurke:80;tom:1;zwie:0.5;oel:1;~Salz und Pfeffer",
  "Putenhack mit Ei, Haferflocken, klein geschnittener Zwiebel und Gewürzen verkneten und zu kleinen Bällchen formen.|Im Öl bei mittlerer Hitze rundherum 8 bis 10 Minuten braten, bis sie innen ganz durch sind.|Couscous mit der gleichen Menge heißem Wasser übergießen und 5 Minuten quellen lassen.|Gurke und Tomate würfeln, mit dem Joghurt vermischen und dazu servieren.")
r("Hähnchen-Caesar-Salat mit Joghurt-Dressing", "M", 20, "a", "haehn:120;ei:1;eisb:150;parm:15;brot:1;jog35:40;zitrone:1;senf:1;oel:0.5;~Salz und Pfeffer",
  "Ei 8 Minuten hart kochen, pellen und vierteln.|Hähnchen in Streifen im Öl rundherum anbraten, bis es innen ganz durch ist. Brot würfeln und in der Pfanne rösten.|Joghurt mit Zitronensaft, Senf, Salz und Pfeffer zum Dressing verrühren.|Salat mit Hähnchen, Ei, Brotwürfeln und Parmesan mischen und das Dressing darübergeben.")
r("Tomaten-Hähnchen-Reis-Auflauf", "M", 40, "p", "haehn:130;reis:60;stueck:200;pap:1;zwie:1;moz:40;oel:1;~Oregano, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen. Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Hähnchen in Würfeln mit Zwiebel und Paprika im Öl anbraten, bis das Fleisch außen gar ist.|Alles mit Reis, Tomaten und Gewürzen in eine Form geben, mit Mozzarella bestreuen und 20 Minuten überbacken, bis das Hähnchen innen ganz durch ist.",
  "Zum Vorkochen: gekühlt 2 Tage haltbar, vor dem Essen vollständig erhitzen.")
r("Eier-Nudeln mit Tomate, Rucola und Parmesan", "M", 20, "g", "nudel:70;ei:2;tom:2;ruc:30;parm:15;oel:1;knob:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Knoblauch und Tomatenstücke im Öl 3 Minuten anbraten. Die Nudeln zugeben.|Eier verquirlen, in die Pfanne geben und unter Rühren fest werden lassen.|Mit Rucola und Parmesan servieren.")
r("Hackbraten-Muffins mit Salat", "M", 35, "pa", "ghack:120;ei:1;hafer:25;zwie:0.5;senf:1;tmark:1;eisb:100;tom:1;gurke:60;~Salz und Pfeffer",
  "Ofen auf 190 °C Ober- und Unterhitze vorheizen.|Hack mit Ei, Haferflocken, klein geschnittener Zwiebel, Senf, Tomatenmark und Gewürzen verkneten und in zwei große Muffinmulden drücken.|20 bis 25 Minuten backen, bis sie innen ganz durch sind und nichts Rosa mehr zu sehen ist.|Mit Salat, Tomate und Gurke essen.",
  "Kalt wie warm gut, am nächsten Tag in der Box zur Arbeit.")
r("Honig-Senf-Hähnchen mit Paprika und Couscous", "M", 30, "", "haehn:130;senf:1;honig:1;pap:2;zwie:1;couscous:60;oel:1;~Salz und Pfeffer",
  "Senf mit Honig verrühren und das gewürzte Hähnchen damit bestreichen. Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Paprika und Zwiebel in Stücken mit dem Öl auf einem Blech mischen, das Hähnchen dazulegen und 20 bis 25 Minuten backen, bis es innen ganz durch ist.|Couscous mit der gleichen Menge heißem Wasser übergießen, 5 Minuten quellen lassen und lockern.")

# ======================= NEU (Runde 3) =======================
r("Eier-Wrap-Röllchen mit Putenaufschnitt und Gurke", "F", 10, "a", "wrap:1;ei:2;paufs:30;gurke:60;senf:1;oel:1;~Salz und Pfeffer",
  "Eier verquirlen und im Öl bei mittlerer Hitze zu einem dünnen Omelett braten, bis nichts Flüssiges mehr zu sehen ist.|Wrap mit Senf bestreichen, Omelett, Putenaufschnitt und Gurkenstreifen darauflegen.|Eng einrollen und halbieren.")
r("Quark-Haferbrei mit Banane und Honig", "F", 8, "", "hafer:50;quark:150;honig:1;banane:1;~150 ml Wasser, Zimt",
  "Haferflocken mit dem Wasser im Topf unter Rühren aufkochen und 3 Minuten quellen lassen. Vom Herd nehmen und etwas abkühlen lassen.|Quark unterrühren, Banane in Scheiben und Honig darübergeben und mit Zimt bestreuen.",
  "Den Quark erst nach dem Abkühlen unterrühren, sonst flockt er aus.")
r("Frühstücks-Quesadilla mit Ei und Mozzarella", "F", 10, "a", "wrap:1;ei:2;moz:30;pap:0.5;oel:1;~Salz und Pfeffer",
  "Eier im Öl rühren, bis sie ganz fest sind.|Wrap in die Pfanne legen, auf einer Hälfte Rührei, Mozzarella und Paprika in Streifen verteilen und zuklappen.|Von jeder Seite 2 Minuten braten, bis der Käse geschmolzen ist.")
r("Quark-Brötchen mit Tomate, Rucola und Gouda", "F", 5, "ka", "broetchen:1;quark:60;tom:1;ruc:15;gouda:20;~Salz und Pfeffer",
  "Brötchen aufschneiden und mit Quark bestreichen.|Mit Tomatenscheiben, Gouda und Rucola belegen und würzen.")
r("Eiermuffins mit Schinken und Gouda zum Mitnehmen", "F", 25, "pa", "ei:3;schink:30;gouda:20;milch:30;oel:0.5;~Pfeffer",
  "Ofen auf 180 °C Ober- und Unterhitze vorheizen und drei Mulden einer Muffinform mit Öl einfetten.|Eier mit Milch und Pfeffer verquirlen, Schinken in kleinen Stücken und Gouda unterrühren.|In die Mulden füllen und 15 bis 18 Minuten backen, bis sie gestockt sind.",
  "Gekühlt halten sie 2 bis 3 Tage. Kalt essen oder kurz aufwärmen.")
r("Putenstreifen mit Joghurt-Gurken-Dip", "S", 15, "pa", "pute:100;jog35:60;gurke:100;oel:1;~Paprikapulver, Salz und Pfeffer",
  "Pute in Streifen schneiden, würzen und im Öl rundherum anbraten, bis sie innen ganz durch ist.|Gurke klein würfeln und mit Joghurt, Salz und Pfeffer zum Dip verrühren.|Die Streifen dazu essen, kalt oder warm.")
r("Käse-Gurken-Wrap mit Quark", "S", 5, "ka", "wrap:1;quark:50;gouda:20;gurke:60;~Pfeffer",
  "Wrap mit Quark bestreichen.|Gouda in Scheiben und Gurke in Streifen darauflegen, pfeffern und einrollen.")
r("Hartgekochte Eier mit Quark-Senf-Dip", "S", 10, "kpa", "ei:2;quark:60;senf:1;sgurke:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Quark mit Senf, Salz und Pfeffer verrühren, Saure Gurke fein würfeln und untermischen.|Die Eier zum Dippen dazu essen.")
r("Skyr-Haferkekse mit Banane und Kakao", "S", 25, "pa", "hafer:50;skyr:100;banane:1;kakao:1",
  "Ofen auf 180 °C Ober- und Unterhitze vorheizen.|Banane zerdrücken und mit Skyr, Haferflocken und Kakao zu einem festen Teig verrühren.|Mit einem Löffel vier Häufchen auf ein Blech mit Backpapier setzen, flach drücken und 15 bis 18 Minuten backen.",
  "Halten sich gekühlt 2 bis 3 Tage und passen gut in die Jackentasche.")
r("Knusprige Ofen-Kichererbsen", "S", 30, "p", "kiche:150;oel:1;~Paprikapulver, Salz",
  "Ofen auf 220 °C Ober- und Unterhitze vorheizen.|Kichererbsen abtropfen, gut trocken tupfen und mit Öl und Gewürzen mischen.|Auf einem Blech 20 bis 25 Minuten backen, zwischendurch einmal schütteln, bis sie knusprig sind.",
  "Am besten am selben Tag essen, sonst werden sie weich.")
r("Mozzarella-Wrap mit Rucola und Tomate", "S", 5, "ka", "wrap:1;moz:35;tom:1;ruc:15;~Salz und Pfeffer",
  "Mozzarella und Tomate in Scheiben schneiden.|Mit Rucola auf dem Wrap verteilen, würzen und einrollen.")
r("Schweineschnitzel mit Tomaten-Gurken-Salat und Couscous", "M", 25, "", "schnitzel:140;oel:1;couscous:60;tom:2;gurke:100;zitrone:1;~Salz und Pfeffer",
  "Couscous mit der gleichen Menge heißem Wasser übergießen und 5 Minuten quellen lassen.|Schnitzel würzen und im Öl bei mittlerer Hitze von jeder Seite 4 bis 5 Minuten braten, bis es innen ganz durch ist.|Tomaten und Gurke würfeln und mit Zitronensaft, Salz und Pfeffer anmachen.",
  "Schweineschnitzel ist oft günstiger als Hähnchenbrust und liefert ähnlich viel Eiweiß.")
r("Schnitzel-Brötchen mit Salat und Senf", "M", 20, "a", "schnitzel:120;broetchen:1;eisb:60;tom:1;senf:1;oel:1;~Salz und Pfeffer",
  "Schnitzel würzen und im Öl von jeder Seite 4 bis 5 Minuten braten, bis es innen ganz durch ist.|Brötchen aufschneiden und mit Senf bestreichen.|Mit Salat, Tomatenscheiben und dem aufgeschnittenen Schnitzel belegen.")
r("Schnitzel-Nudeln in Tomatensauce", "M", 25, "", "schnitzel:120;nudel:70;stueck:200;zwie:1;knob:1;oel:1;parm:10;~Oregano, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Schnitzel in Streifen schneiden und im Öl rundherum anbraten, bis es innen ganz durch ist. Zwiebel und Knoblauch klein schneiden und kurz mitbraten.|Tomaten und Gewürze zugeben und 8 Minuten köcheln lassen.|Nudeln untermischen und mit Parmesan bestreuen.")
r("Paprika-Schnitzel-Pfanne mit Reis", "M", 25, "", "schnitzel:130;pap:2;zwie:1;reis:60;tmark:1;oel:1;~Paprikapulver, Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Schnitzel in Streifen im Öl rundherum anbraten, bis es innen ganz durch ist. Zwiebel und Paprika in Streifen zugeben und 5 Minuten mitbraten.|Tomatenmark, Paprikapulver und einen Schuss Wasser unterrühren und 3 Minuten köcheln lassen.|Mit dem Reis servieren.")
r("Linsen-Hack-Pfanne mit Paprika", "M", 25, "g", "ghack:70;linse:50;pap:1;zwie:1;stueck:150;tmark:1;bruehe:200;~Paprikapulver, Salz und Pfeffer",
  "Hack mit klein geschnittener Zwiebel in einer Pfanne krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Paprika in Würfeln und Tomatenmark zugeben und 2 Minuten mitbraten.|Linsen, Tomaten, Brühe und Gewürze zugeben und 15 bis 18 Minuten köcheln lassen, bis die Linsen weich sind.",
  "Rote Linsen müssen nicht eingeweicht werden. Die Pfanne ist günstig und lässt sich gut vorkochen.")
r("Eier-Reis-Bowl mit Schinken und Gurke", "M", 15, "g", "reis:70;ei:2;schink:40;gurke:100;soja:1;oel:1;zwie:0.5;~Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebel klein schneiden und im Öl 2 Minuten anbraten. Schinken in Streifen kurz mitbraten, die Eier darüber verquirlen und unter Rühren fest werden lassen.|Reis mit Sojasauce vermengen, Ei-Mischung und Gurkenscheiben daraufgeben.")
r("Hähnchen-Linsen-Pfanne mit Tomate", "M", 25, "", "haehn:120;linse:50;stueck:200;zwie:1;knob:1;curry:1;oel:1;bruehe:200;~Salz und Pfeffer",
  "Hähnchen in Würfeln im Öl rundherum anbraten, bis es außen gar ist. Zwiebel und Knoblauch klein schneiden und kurz mitbraten.|Curry, Linsen, Tomaten und Brühe zugeben und 15 bis 18 Minuten köcheln lassen, bis die Linsen weich und das Hähnchen innen ganz durch ist.")
r("Pizza-Nudelpfanne mit Putenaufschnitt", "M", 20, "", "nudel:70;stueck:200;paufs:50;moz:40;zwie:1;pap:1;~Oregano, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Zwiebel und Paprika klein schneiden und in einer Pfanne 4 Minuten anbraten. Tomaten und Oregano zugeben und 5 Minuten köcheln lassen.|Putenaufschnitt in Streifen und die Nudeln unterheben, Mozzarella in Stücken darauflegen und mit Deckel schmelzen lassen.")
r("Enchiladas aus dem Ofen mit Hack und Bohnen", "M", 35, "p", "wrap:1;ghack:60;bohne:50;reis:20;stueck:150;gouda:20;zwie:0.5;~Paprikapulver, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Reis nach Packungsanleitung kochen.|Hack mit klein geschnittener Zwiebel krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Bohnen, Reis und die Hälfte der Tomaten zugeben, würzen.|Füllung in den Wrap einrollen, in eine Form legen, mit den restlichen Tomaten und dem Gouda bedecken und 15 Minuten überbacken.")
r("Kichererbsen-Tomatensuppe mit Ei", "M", 25, "pg", "kiche:120;stueck:250;zwie:1;knob:1;bruehe:300;ei:1;curry:1;parm:10;~Salz und Pfeffer",
  "Zwiebel und Knoblauch klein schneiden und in einem Topf mit einem Schuss Wasser 3 Minuten dünsten.|Curry, Tomaten, Kichererbsen und Brühe zugeben und 12 Minuten köcheln lassen.|Das Ei in die leicht köchelnde Suppe schlagen und 3 bis 4 Minuten garen, bis es fest ist.|Mit Parmesan bestreuen.")
r("Putenfrikadellen-Wrap mit Joghurt-Gurkensalat", "M", 25, "a", "phack:100;ei:0.5;hafer:15;wrap:1;jog35:50;gurke:100;tom:1;oel:1;~Salz und Pfeffer",
  "Putenhack mit Ei, Haferflocken, Salz und Pfeffer verkneten und zu zwei flachen Frikadellen formen.|Im Öl bei mittlerer Hitze von jeder Seite 5 bis 6 Minuten braten, bis sie innen ganz durch sind.|Gurke und Tomate würfeln und mit Joghurt vermischen.|Frikadellen in Stücken mit dem Salat in den Wrap geben und einrollen.")
r("Linsen-Nudelsuppe mit Tomate", "M", 30, "pg", "linse:60;nudel:30;stueck:200;zwie:1;knob:1;bruehe:400;tmark:1;parm:10;~Salz und Pfeffer",
  "Zwiebel und Knoblauch klein schneiden und mit Tomatenmark 2 Minuten anrösten.|Linsen, Tomaten und Brühe zugeben und 10 Minuten köcheln lassen.|Nudeln zugeben und weitere 8 bis 10 Minuten garen.|Mit Parmesan bestreuen.",
  "Wird beim Stehen dicker. Mit etwas Wasser verdünnen.")
r("Hähnchen-Fajita-Wrap", "M", 20, "a", "haehn:120;pap:2;zwie:1;wrap:1;jog35:40;oel:1;~Paprikapulver, Kreuzkümmel, Salz und Pfeffer",
  "Hähnchen, Paprika und Zwiebel in Streifen schneiden.|Das Hähnchen mit den Gewürzen im Öl rundherum anbraten, bis es innen ganz durch ist. Paprika und Zwiebel zugeben und 5 Minuten mitbraten.|Wrap mit Joghurt bestreichen, die Füllung daraufgeben und einrollen.")
r("Bolognese-Nudelauflauf mit Quark-Haube", "M", 40, "p", "ghack:80;nudel:60;stueck:200;zwie:1;quark:100;gouda:20;knob:1;~Oregano, Salz und Pfeffer",
  "Nudeln 2 Minuten kürzer als auf der Packung angegeben kochen. Ofen auf 200 °C Ober- und Unterhitze vorheizen.|Hack mit Zwiebel und Knoblauch krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Tomaten und Gewürze zugeben und 5 Minuten köcheln lassen.|Nudeln und Sauce in eine Form geben. Quark mit Salz und Pfeffer glatt rühren, darauf verteilen, mit Gouda bestreuen und 20 Minuten überbacken.",
  "Gekühlt 2 Tage haltbar, vor dem Essen vollständig erhitzen.")
r("Gefüllte Tomaten mit Hack und Couscous", "M", 35, "", "tom:3;ghack:80;couscous:40;zwie:0.5;moz:30;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Von den Tomaten einen Deckel abschneiden und mit einem Löffel aushöhlen.|Couscous mit der gleichen Menge heißem Wasser übergießen und 5 Minuten quellen lassen.|Hack mit klein geschnittener Zwiebel krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Mit Couscous und dem Fruchtfleisch mischen und würzen.|In die Tomaten füllen, mit Mozzarella belegen und 15 bis 18 Minuten backen.")
r("Hack-Bohnen-Eintopf mit Nudeln", "M", 30, "pg", "ghack:70;bohne:100;nudel:40;stueck:200;zwie:1;bruehe:300;tmark:1;~Paprikapulver, Salz und Pfeffer",
  "Hack mit Zwiebel krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Tomatenmark zugeben und 2 Minuten mitbraten.|Tomaten, Bohnen, Brühe und Gewürze zugeben und 10 Minuten köcheln lassen.|Nudeln zugeben und weitere 8 bis 10 Minuten garen.",
  "Ein Eintopf für zwei Tage, der sich gut einfrieren lässt.")


# ======================= NEU (Runde 4): Hähnchen =======================
r("Butter Chicken mit Reis", "M", 35, "p", "haehn:150;butter:10;zwie:1;knob:2;stueck:200;jogGr:60;garam:1;paprikap:1;reis:60;~Salz",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Knoblauch klein schneiden und in der Butter 3 Minuten andünsten. Garam Masala und Paprikapulver kurz mitrösten.|Hähnchen in Würfel schneiden, dazugeben und rundum anbraten. Stückige Tomaten zugeben und 10 Minuten köcheln, bis das Fleisch im Kern durch ist.|Vom Herd nehmen, Joghurt unterrühren (nicht mehr kochen) und mit Salz abschmecken.",
  "Garam Masala ist eine fertige Gewürzmischung und gehört in jedes indische Gericht. Ein Teelöffel reicht.")
r("Hähnchen Tikka aus dem Ofen mit Couscous und Paprika", "M", 35, "a", "haehn:170;jogGr:70;paprikap:1;kurkuma:1;zitrone:1;pap:1;zwie:1;couscous:60;~Salz",
  "Joghurt mit Paprikapulver, Kurkuma, Zitronensaft und Salz verrühren, das Hähnchen in Stücken darin 15 Minuten marinieren. Ofen auf 220 °C Ober- und Unterhitze vorheizen.|Paprika und Zwiebel in Stücke schneiden und mit dem Hähnchen auf ein Blech geben.|20 bis 25 Minuten backen, bis das Fleisch im Kern durch und nicht mehr rosa ist.|Couscous mit heißem Wasser übergießen, 5 Minuten quellen lassen und dazu servieren.")
r("Hähnchen-Linsen-Curry mit Kokosmilch", "M", 35, "pg", "haehn:120;linse:50;kokos:150;curry:1;kurkuma:1;zwie:1;pap:1;stueck:150;oel:1;~Salz",
  "Zwiebel und Paprika klein schneiden und im Öl 4 Minuten anbraten. Curry und Kurkuma kurz mitrösten.|Hähnchen in Würfeln zugeben und rundum anbraten.|Linsen, stückige Tomaten, Kokosmilch und 200 ml Wasser zugeben und 15 Minuten köcheln, bis die Linsen weich und das Hähnchen durch ist.|Mit Salz abschmecken.",
  "Rote Linsen brauchen keine Einweichzeit und machen die Soße von selbst cremig.")
r("Hähnchen-Paprika-Rahmpfanne mit Nudeln", "M", 25, "", "haehn:150;pap:2;zwie:1;nudel:70;speisequark:80;bruehe:100;paprikap:1;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Hähnchen in Streifen im Öl rundum anbraten, bis es durch ist. Paprika und Zwiebel in Streifen zugeben und 5 Minuten braten.|Brühe angießen und aufkochen, die Pfanne vom Herd nehmen. Quark und Paprikapulver unterrühren.|Mit Salz und Pfeffer abschmecken und die Nudeln untermischen.",
  "Der Quark kommt erst nach dem Kochen in die Pfanne, sonst flockt er aus.")
r("Hähnchen-Fajita-Pfanne mit Wrap", "M", 20, "a", "haehn:150;pap:2;zwie:1;wrap:1;jogGr:50;tom:1;eisb:40;oel:1;paprikap:1;~Salz und Pfeffer",
  "Hähnchen, Paprika und Zwiebel in Streifen schneiden.|Das Hähnchen im Öl 5 Minuten anbraten, dann Paprika, Zwiebel und Paprikapulver zugeben und weitere 5 Minuten braten, bis nichts Rosa mehr zu sehen ist.|Den Wrap kurz in der Pfanne erwärmen.|Mit Salat, Tomatenwürfeln und Joghurt füllen und die Fajita-Pfanne dazu essen.")
r("Hähnchen-Burrito-Bowl mit Reis und Bohnen", "M", 30, "ap", "haehn:140;bohne:100;reis:60;tom:2;pap:1;eisb:40;gouda:20;oel:1;paprikap:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hähnchen in Streifen im Öl anbraten, Paprika in Streifen dazugeben, mit Paprikapulver, Salz und Pfeffer würzen und braten, bis das Fleisch durch ist.|Bohnen und Tomatenwürfel kurz miterhitzen.|Reis, Füllung und Salat in eine Schüssel geben und mit Gouda bestreuen.")
r("Hähnchen-Teriyaki-Pfanne mit Reis", "M", 25, "", "haehn:150;soja:1.5;honig:1;pap:2;zwie:1;knob:1;reis:70;oel:1;~Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hähnchen in Streifen im Öl anbraten, bis es rundum gar ist.|Paprika, Zwiebel und Knoblauch in Streifen zugeben und 4 Minuten braten.|Sojasauce, Honig und 3 EL Wasser dazugeben und einkochen lassen, bis die Soße glänzt. Zum Reis servieren.",
  "Sojasauce ist salzig: Salze deshalb nicht extra nach.")
r("Hähnchen mit Haferflocken-Panade und Gurkensalat", "M", 30, "", "haehn:160;ei:1;hafer:30;senf:1;gurke:200;tom:1;jogGr:40;oel:1;couscous:40;~Salz und Pfeffer",
  "Hähnchen flach klopfen, mit Salz und Pfeffer würzen und mit Senf bestreichen. Ei verquirlen, Haferflocken auf einen Teller geben.|Das Hähnchen erst im Ei, dann in den Haferflocken wenden.|Im Öl bei mittlerer Hitze von jeder Seite 5 bis 6 Minuten braten, bis die Panade goldbraun und das Fleisch durch ist.|Gurke und Tomate würfeln, mit Joghurt, Salz und Pfeffer mischen. Couscous mit heißem Wasser quellen lassen und dazu essen.")
r("Hähnchen Caprese aus dem Ofen mit Nudeln", "M", 35, "", "haehn:150;tom:2;moz:60;nudel:70;stueck:100;knob:1;oel:1;~Basilikum, Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Nudeln nach Packungsanleitung kochen.|Das Hähnchen würzen, im Öl 2 Minuten pro Seite anbraten und in eine Auflaufform legen. Stückige Tomaten mit Knoblauch daneben geben.|Tomatenscheiben und Mozzarella darauflegen und 15 bis 20 Minuten backen, bis das Hähnchen im Kern durch ist.|Mit Basilikum bestreuen und zu den Nudeln servieren.")
r("Hähnchen-Gemüse-Pfanne mit Couscous", "M", 25, "a", "haehn:150;pap:2;zwie:1;tom:1;couscous:60;oel:1;paprikap:1;zitrone:1;~Salz und Pfeffer",
  "Couscous mit heißem Wasser übergießen und 5 Minuten quellen lassen.|Hähnchen in Würfeln im Öl rundum anbraten. Paprika und Zwiebel in Stücken zugeben und 6 Minuten mitbraten.|Tomate in Stücken, Paprikapulver und Zitronensaft zugeben und kurz erwärmen. Das Fleisch muss durch sein.|Mit Salz und Pfeffer abschmecken und mit dem Couscous mischen.")
r("Hähnchen-Rucola-Couscous-Salat", "M", 20, "ka", "haehn:140;couscous:50;tom:2;gurke:100;ruc:30;zitrone:1;oel:1;~Salz und Pfeffer",
  "Couscous mit heißem Wasser übergießen, 5 Minuten quellen lassen und abkühlen lassen.|Hähnchen in Würfeln im Öl braten, bis es durch ist.|Tomaten und Gurke würfeln und mit Zitronensaft, Salz und Pfeffer zum Couscous geben.|Hähnchen und Rucola unterheben.")
r("Hähnchen-Gurken-Wrap mit Senf-Joghurt", "M", 15, "ka", "haehnst:150;wrap:2;gurke:100;tom:1;eisb:40;jogGr:50;senf:1;~Salz und Pfeffer",
  "Joghurt mit Senf, Salz und Pfeffer verrühren.|Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Streifen schneiden.|Wraps mit Soße bestreichen, mit Salat, Gurke und Tomate belegen.|Fleisch darauf legen, einrollen und halbieren.")
r("Hähnchenspieße mit Paprika und Zwiebel, Joghurt-Dip und Reis", "M", 35, "", "haehn:160;pap:2;zwie:1;jogGr:60;reis:60;oel:1;knob:1;paprikap:1;~Salz und Pfeffer",
  "Ofen auf 220 °C vorheizen. Reis nach Packungsanleitung kochen.|Hähnchen, Paprika und Zwiebel in große Stücke schneiden, mit Öl, Paprikapulver, Salz und Pfeffer mischen und abwechselnd auf Spieße stecken.|20 Minuten backen, zwischendurch wenden, bis das Fleisch im Kern durch ist.|Joghurt mit Knoblauch, Salz und Pfeffer verrühren und zu Spießen und Reis servieren.")
r("Ofentomaten-Hähnchen mit Rucola auf Couscous", "M", 35, "", "haehn:150;tom:3;zwie:1;knob:1;ruc:30;couscous:60;parm:10;oel:1;~Salz und Pfeffer",
  "Ofen auf 200 °C Ober- und Unterhitze vorheizen. Tomaten und Zwiebel in Stücke schneiden.|Hähnchen, Tomaten, Zwiebel und Knoblauch mit Öl, Salz und Pfeffer in eine Form geben und 25 Minuten backen, bis das Fleisch im Kern durch ist.|Couscous mit heißem Wasser übergießen und 5 Minuten quellen lassen.|Alles auf dem Couscous anrichten, Rucola und Parmesan darübergeben.")
r("Paprika-Hähnchen-Gulasch mit Reis", "M", 40, "p", "haehn:160;pap:2;zwie:2;tmark:1;paprikap:2;stueck:100;bruehe:100;reis:60;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebeln und Paprika in Stücke schneiden. Hähnchen in Würfeln im Öl anbraten.|Zwiebeln, Paprika und Tomatenmark zugeben, 3 Minuten braten, dann Paprikapulver, stückige Tomaten und Brühe zugeben.|20 Minuten bei mittlerer Hitze köcheln, bis das Fleisch weich und durch ist, und mit Salz und Pfeffer abschmecken.")
r("Hähnchen-Bowl mit Kichererbsen, Gurke und Tomate", "M", 20, "ka", "haehn:130;kiche:100;gurke:100;tom:1;reis:40;jogGr:40;zitrone:1;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen und abkühlen lassen.|Hähnchen in Würfeln im Öl braten, bis es durch ist.|Gurke und Tomate würfeln, Kichererbsen abtropfen.|Alles auf dem Reis anrichten, Joghurt mit Zitronensaft, Salz und Pfeffer verrühren und darübergeben.")
r("Hähnchen-Pizza-Wrap", "M", 20, "a", "haehn:130;wrap:1;tmark:1;moz:50;tom:1;pap:1;zwie:0.5;oel:1;~Oregano, Salz und Pfeffer",
  "Ofen auf 220 °C vorheizen. Das Hähnchen in kleine Würfel schneiden und im Öl braten, bis es durch ist.|Den Wrap mit Tomatenmark bestreichen, mit Hähnchen, Tomatenscheiben, Paprika, Zwiebel und Mozzarella belegen.|8 bis 10 Minuten backen, bis der Käse geschmolzen und der Rand knusprig ist.|Mit Oregano bestreuen.")
r("Hähnchenbrust mit Tomaten-Zwiebel-Salsa und Reis", "M", 25, "", "haehn:160;tom:3;zwie:1;zitrone:1;reis:70;oel:1;~Salz, Pfeffer und Paprikapulver",
  "Reis nach Packungsanleitung kochen.|Tomaten und Zwiebel fein würfeln, mit Zitronensaft, Salz und Pfeffer zur Salsa mischen.|Hähnchen mit Salz, Pfeffer und Paprikapulver würzen und im Öl von jeder Seite 5 bis 6 Minuten braten, bis es durch ist.|In Scheiben schneiden und mit Salsa und Reis servieren.")
r("Hähnchen-Quesadilla mit Bohnen und Gouda", "M", 20, "a", "haehn:120;wrap:2;gouda:20;bohne:50;zwie:0.5;tom:1;oel:0.5;~Salz und Pfeffer",
  "Hähnchen in Streifen im Öl braten, bis es durch ist. Zwiebel in Streifen mitbraten.|Bohnen zugeben und kurz erwärmen.|Wrap mit Füllung, Tomatenscheiben und Gouda belegen und mit dem zweiten Wrap abdecken.|In der Pfanne ohne zusätzliches Fett von jeder Seite 2 bis 3 Minuten braten, bis der Käse geschmolzen ist.")
r("Hähnchen-Tomaten-Nudelsuppe", "M", 30, "p", "haehn:130;stueck:200;nudel:50;zwie:1;pap:1;bruehe:300;knob:1;oel:1;~Salz, Pfeffer und Oregano",
  "Zwiebel, Paprika und Knoblauch klein schneiden und im Öl 4 Minuten anbraten.|Hähnchen in Würfeln zugeben und rundum anbraten.|Stückige Tomaten und Brühe zugeben und 10 Minuten köcheln, bis das Fleisch durch ist.|Nudeln zugeben und nach Packungsanleitung garen. Würzen.")
r("Hähnchen-Paprika-Auflauf mit Mozzarella und Couscous", "M", 40, "p", "haehn:150;pap:2;zwie:1;couscous:60;stueck:150;moz:60;bruehe:100;knob:1;~Salz, Pfeffer und Oregano",
  "Ofen auf 200 °C vorheizen. Couscous in einer Auflaufform mit heißer Brühe übergießen.|Hähnchen, Paprika und Zwiebel in Stücke schneiden und auf dem Couscous verteilen.|Stückige Tomaten mit Knoblauch, Salz, Pfeffer und Oregano darübergeben, Mozzarella zerzupfen und obenauf legen.|25 Minuten backen, bis das Hähnchen durch und der Käse goldbraun ist.")
r("Würziges Hähnchen mit Kreuzkümmel, Reis und Gurken-Tomaten-Salat", "M", 30, "", "haehn:160;kreuz:1;paprikap:1;reis:60;gurke:150;tom:2;zitrone:1;jogGr:30;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hähnchen mit Kreuzkümmel, Paprikapulver, Salz und Pfeffer einreiben und im Öl von jeder Seite 5 bis 6 Minuten braten, bis es durch ist.|Gurke und Tomaten würfeln und mit Zitronensaft, Joghurt, Salz und Pfeffer mischen.|Das Fleisch in Scheiben schneiden und mit Reis und Salat servieren.")


# ======================= NEU (Runde 4): Pute =======================
r("Puten-Curry mit Kokosmilch und Reis", "M", 30, "p", "pute:150;kokos:150;curry:1;kurkuma:1;pap:1;zwie:1;stueck:100;reis:60;oel:1;~Salz",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Paprika klein schneiden und im Öl 4 Minuten anbraten. Curry und Kurkuma kurz mitrösten.|Putenbrust in Würfeln zugeben und rundum anbraten.|Kokosmilch und stückige Tomaten zugeben und 10 Minuten köcheln, bis das Fleisch durch ist. Mit Salz abschmecken.")
r("Putengeschnetzeltes in Paprika-Rahm mit Nudeln", "M", 25, "", "pute:150;pap:2;zwie:1;speisequark:60;bruehe:100;nudel:70;paprikap:1;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Pute in Streifen im Öl rundum anbraten, bis sie durch ist. Paprika und Zwiebel in Streifen zugeben und 5 Minuten braten.|Brühe angießen und kurz einkochen, dann die Pfanne vom Herd nehmen. Quark und Paprikapulver unterrühren.|Mit Salz und Pfeffer abschmecken und die Nudeln untermischen.")
r("Asia-Putenpfanne mit Paprika und Reis", "M", 25, "", "pute:150;pap:2;zwie:1;soja:1.5;knob:1;reis:60;oel:1;~Pfeffer",
  "Reis nach Packungsanleitung kochen.|Pute, Paprika und Zwiebel in Streifen schneiden.|Die Pute im Öl rundum anbraten, bis sie durch ist, dann Paprika, Zwiebel und Knoblauch 4 Minuten mitbraten.|Sojasauce und 3 EL Wasser zugeben, kurz einkochen und zum Reis servieren.",
  "Sojasauce ist salzig: Salze deshalb nicht extra nach.")
r("Puten-Tomaten-Pfanne mit Mozzarella und Couscous", "M", 25, "", "pute:150;tom:3;moz:50;couscous:50;zwie:0.5;knob:1;oel:1;~Basilikum, Salz und Pfeffer",
  "Couscous mit heißem Wasser übergießen und 5 Minuten quellen lassen.|Pute in Würfeln im Öl anbraten, bis sie durch ist. Zwiebel und Knoblauch zugeben.|Tomaten in Stücken 3 Minuten mitschmoren, Mozzarella zerzupfen und unterheben, bis er schmilzt.|Mit Basilikum, Salz und Pfeffer würzen und auf dem Couscous servieren.")
r("Putenspieße mit Paprika, Joghurt-Dip und Couscous", "M", 35, "", "pute:160;pap:2;zwie:1;jogGr:60;couscous:50;oel:1;knob:1;~Salz und Pfeffer",
  "Ofen auf 220 °C vorheizen.|Pute, Paprika und Zwiebel in große Stücke schneiden, mit Öl, Salz und Pfeffer mischen und abwechselnd auf Spieße stecken.|20 Minuten backen, zwischendurch wenden, bis die Pute im Kern durch ist.|Couscous mit heißem Wasser quellen lassen. Joghurt mit Knoblauch, Salz und Pfeffer verrühren und dazu servieren.")
r("Putenhack-Chili mit Bohnen und Reis", "M", 35, "pg", "phack:120;bohne:100;stueck:200;pap:1;zwie:1;tmark:1;reis:40;paprikap:1;kreuz:1;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Paprika klein schneiden und im Öl anbraten. Putenhack zugeben und krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Tomatenmark, Paprikapulver und Kreuzkümmel kurz mitrösten, dann Tomaten, Bohnen und 100 ml Wasser zugeben.|15 Minuten köcheln und mit Salz und Pfeffer abschmecken.",
  "Schmeckt am zweiten Tag noch besser. Gekühlt 2 Tage haltbar, vor dem Essen vollständig erhitzen.")
r("Puten-Tomaten-Auflauf mit Nudeln und Gouda", "M", 40, "p", "pute:130;nudel:60;stueck:200;pap:1;zwie:1;gouda:30;knob:1;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Nudeln 2 Minuten kürzer als auf der Packung angegeben kochen.|Pute in Würfeln, Paprika und Zwiebel anbraten, bis die Pute durch ist. Stückige Tomaten, Knoblauch und Gewürze zugeben.|Mit den Nudeln in eine Auflaufform geben und mit Gouda bestreuen.|15 bis 20 Minuten backen, bis der Käse goldbraun ist.")
r("Puten-Salat-Wrap mit Honig-Senf-Dressing", "M", 15, "ka", "pute:120;wrap:1;eisb:60;tom:1;gurke:80;senf:1;jogGr:40;honig:0.5;~Salz und Pfeffer",
  "Joghurt mit Senf, Honig, Salz und Pfeffer verrühren.|Die Pute in einer Pfanne ohne Fett braten, bis sie durch ist, oder fertig gegarte Pute verwenden. In Streifen schneiden.|Salat, Tomate und Gurke auf dem Wrap verteilen und das Dressing daraufgeben.|Pute darauflegen, einrollen und halbieren.")
r("Paprika-Putenbrust mit Tomatenreis", "M", 30, "", "pute:160;reis:60;tmark:1;tom:2;pap:1;zwie:0.5;paprikap:1;oel:1;~Salz und Pfeffer",
  "Reis mit Tomatenmark und 150 ml Wasser nach Packungsanleitung kochen.|Pute mit Paprikapulver, Salz und Pfeffer würzen und im Öl von jeder Seite 5 bis 6 Minuten braten, bis sie durch ist.|Paprika, Zwiebel und Tomaten würfeln und die letzten 3 Minuten mitbraten.|Pute in Scheiben schneiden und mit dem Reis servieren.")
r("Putenstreifen in Honig-Soja-Soße mit Couscous und Gurke", "M", 20, "", "pute:150;soja:1;honig:1;couscous:60;gurke:150;pap:1;oel:1;~Pfeffer",
  "Couscous mit heißem Wasser übergießen und 5 Minuten quellen lassen.|Pute in Streifen im Öl braten, bis sie durch ist, Paprika in Streifen 3 Minuten mitbraten.|Sojasauce, Honig und 3 EL Wasser zugeben und einkochen, bis die Soße glänzt.|Mit Couscous und Gurkenscheiben servieren.")
r("Puten-Bolognese mit Karotte und Nudeln", "M", 35, "pg", "phack:130;nudel:70;stueck:200;zwie:1;karo:1;tmark:1;knob:1;oel:1;~Oregano, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Zwiebel, Karotte und Knoblauch fein würfeln und im Öl 4 Minuten anbraten.|Putenhack zugeben und krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Tomatenmark kurz mitrösten.|Stückige Tomaten und Oregano zugeben und 15 Minuten köcheln, bis die Karotte weich ist. Mit den Nudeln mischen.",
  "Die Karotte wird in der Soße so weich, dass sie kaum auffällt.")
r("Puten-Taco-Bowl mit Bohnen, Reis und Salat", "M", 25, "a", "phack:130;bohne:80;reis:40;tom:2;eisb:50;gouda:20;paprikap:1;kreuz:1;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Putenhack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Paprikapulver, Kreuzkümmel, Salz und Pfeffer zugeben, Bohnen kurz miterhitzen.|Tomaten würfeln, Salat in Streifen schneiden.|Reis, Hack, Salat und Tomaten in eine Schüssel geben und mit Gouda bestreuen.")

# ======================= NEU (Runde 4): Hack =======================
r("Rinderhack-Gemüse-Pfanne mit Reis", "M", 25, "", "rhack:120;pap:2;zwie:1;stueck:100;reis:50;tmark:1;paprikap:1;oel:0.5;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Paprika und Zwiebel in Stücken zugeben und 5 Minuten braten, dann Tomatenmark, Paprikapulver und stückige Tomaten zugeben.|5 Minuten köcheln und mit Salz und Pfeffer abschmecken. Zum Reis servieren.")
r("Lasagne-Pfanne mit Hack, Tomate und Mozzarella", "M", 30, "", "rhack:100;nudel:60;stueck:250;zwie:1;moz:50;knob:1;oel:0.5;~Oregano, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Zwiebel und Knoblauch im Öl andünsten, Hack zugeben und krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Stückige Tomaten und Oregano zugeben und 10 Minuten köcheln.|Nudeln unterheben, Mozzarella zerzupfen und obenauf legen, Deckel auflegen, bis der Käse geschmolzen ist.")
r("Orientalische Hackbällchen mit Joghurt-Dip und Couscous", "M", 35, "", "rhack:130;hafer:15;zwie:0.5;paprikap:1;kreuz:1;couscous:50;gurke:150;tom:1;jogGr:50;oel:1;~Salz und Pfeffer",
  "Hack mit Haferflocken, fein gehackter Zwiebel, Paprikapulver, Kreuzkümmel, Salz und Pfeffer verkneten und zu kleinen Bällchen formen.|Im Öl rundum 8 bis 10 Minuten braten, bis sie innen nicht mehr rosa sind.|Couscous mit heißem Wasser quellen lassen. Gurke und Tomate würfeln.|Joghurt mit Salz und Pfeffer verrühren und alles zusammen servieren.")
r("Hack-Bohnen-Reis-Pfanne mit Tomate", "M", 25, "p", "rhack:100;bohne:80;reis:50;tom:2;zwie:1;pap:1;oel:0.5;paprikap:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Zwiebel und Paprika in Stücken zugeben und 4 Minuten braten.|Bohnen, Tomatenstücke und Paprikapulver zugeben und 5 Minuten schmoren.|Mit dem Reis mischen und abschmecken.")
r("Sloppy Joe mit Hack und Salat", "M", 25, "", "rhack:120;broetchen:1;stueck:150;zwie:1;tmark:1;senf:1;eisb:50;sgurke:1;oel:0.5;~Salz und Pfeffer",
  "Zwiebel fein würfeln und im Öl andünsten, Hack zugeben und krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Tomatenmark, Senf und stückige Tomaten zugeben und 10 Minuten einkochen lassen, bis die Soße dick ist.|Brötchen aufschneiden und kurz toasten.|Mit Salat und Saurer Gurke belegen und die Hack-Soße daraufgeben.")
r("Hackgulasch mit Paprika und Nudeln", "M", 35, "p", "rhack:120;pap:2;zwie:1;tmark:1;paprikap:2;stueck:100;nudel:60;bruehe:100;oel:0.5;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Zwiebel und Paprika in Stücken zugeben.|Tomatenmark und Paprikapulver kurz mitrösten, dann stückige Tomaten und Brühe zugeben.|15 Minuten köcheln, mit Salz und Pfeffer abschmecken und zu den Nudeln servieren.")
r("Hack-Paprika-Tomaten-Auflauf mit Mozzarella", "M", 40, "", "rhack:130;pap:2;tom:2;zwie:1;moz:50;oel:0.5;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist, und würzen.|Paprika, Tomaten und Zwiebel in Stücke schneiden und in eine Auflaufform geben.|Hack darauf verteilen, mit Mozzarella belegen.|20 bis 25 Minuten backen, bis der Käse goldbraun ist.",
  "Ohne Beilage und deshalb kohlenhydratarm. Dazu passt ein Stück Brot.")
r("Burger-Bowl mit Hack, Salat und Gouda", "M", 25, "", "rhack:130;eisb:120;tom:1;sgurke:2;gouda:25;reis:40;senf:1;oel:0.5;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hack mit Salz und Pfeffer zu flachen Pattys formen und im Öl von jeder Seite 4 bis 5 Minuten braten, bis sie durch sind. Gouda zum Schluss darauflegen.|Salat in Streifen schneiden, Tomate und Saure Gurken würfeln.|Alles mit Reis in einer Schüssel anrichten und mit Senf beträufeln.")
r("Hack-Pizza auf Wrap", "M", 20, "a", "wrap:1;rhack:80;tmark:1;moz:50;tom:1;pap:1;zwie:0.5;oel:0.5;~Oregano, Salz und Pfeffer",
  "Ofen auf 220 °C vorheizen. Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Wrap mit Tomatenmark bestreichen und mit Hack, Tomatenscheiben, Paprika, Zwiebel und Mozzarella belegen.|8 bis 10 Minuten backen, bis der Rand knusprig und der Käse geschmolzen ist.|Mit Oregano bestreuen.")
r("Spaghetti mit Hackbällchen und Tomatensoße", "M", 35, "", "rhack:120;nudel:80;stueck:200;zwie:1;knob:1;hafer:10;oel:0.5;~Oregano, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Hack mit Haferflocken, Salz und Pfeffer verkneten und zu kleinen Bällchen formen.|Bällchen im Öl rundum anbraten, Zwiebel und Knoblauch zugeben, dann stückige Tomaten und Oregano.|10 Minuten köcheln, bis die Bällchen innen nicht mehr rosa sind, und zu den Nudeln servieren.")
r("Gefüllte Paprika mit Hack, Couscous und Mozzarella", "M", 40, "", "pap:2;rhack:100;couscous:40;moz:40;tmark:1;zwie:0.5;stueck:100;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Paprika halbieren und entkernen.|Hack mit gehackter Zwiebel anbraten, bis nichts Rosa mehr zu sehen ist. Couscous mit heißem Wasser quellen lassen und untermischen. Tomatenmark und Gewürze zugeben.|Paprikahälften füllen, in eine Form setzen, stückige Tomaten daneben gießen und mit Mozzarella belegen.|25 Minuten backen, bis die Paprika weich und der Käse goldbraun ist.")
r("Hack-Taco-Salat mit Bohnen und Joghurt-Dressing", "M", 20, "a", "rhack:120;eisb:120;tom:2;bohne:60;gouda:20;jogGr:30;paprikap:1;kreuz:1;oel:0.5;~Salz und Pfeffer",
  "Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Paprikapulver, Kreuzkümmel, Salz und Pfeffer zugeben, Bohnen kurz miterhitzen.|Salat in Streifen schneiden und Tomaten würfeln.|Salat, Tomaten und warmen Hack in einer Schüssel mischen.|Joghurt mit etwas Wasser, Salz und Pfeffer verrühren, darübergeben und Gouda darüberstreuen.")
r("Orientalische Hackpfanne mit Kichererbsen und Joghurt", "M", 30, "", "rhack:100;kiche:100;pap:1;zwie:1;stueck:100;jogGr:50;kreuz:1;paprikap:1;oel:1;~Salz und Pfeffer",
  "Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Zwiebel und Paprika in Stücken zugeben und 4 Minuten braten.|Kreuzkümmel und Paprikapulver kurz mitrösten, Kichererbsen und stückige Tomaten zugeben.|10 Minuten schmoren und mit Salz und Pfeffer abschmecken.|Mit einem Klecks Joghurt servieren.")
r("Asiatische Hackpfanne mit Paprika und Reis", "M", 25, "", "ghack:90;pap:2;zwie:1;soja:1;knob:1;reis:50;oel:0.5;~Pfeffer",
  "Reis nach Packungsanleitung kochen.|Hack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Das ausgetretene Fett abgießen.|Paprika, Zwiebel und Knoblauch in Stücken zugeben und 5 Minuten braten.|Sojasauce und 3 EL Wasser zugeben, kurz einkochen und zum Reis servieren.")

# ======================= NEU (Runde 4): Mini-Steaks, Schnitzel und Lyoner =======================
r("Mini-Steaks mit Paprika-Zwiebel-Gemüse und Reis", "M", 25, "", "haehnst:160;pap:2;zwie:1;reis:60;oel:1;paprikap:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind.|Paprika und Zwiebel in Streifen im Öl mit Paprikapulver 6 Minuten braten.|Mit Salz und Pfeffer würzen und alles zusammen servieren.")
r("Mini-Steak-Bowl mit Couscous, Gurke und Tomate", "M", 20, "a", "haehnst:140;couscous:50;gurke:150;tom:2;jogGr:40;zitrone:1;oel:0.5;~Salz und Pfeffer",
  "Couscous mit heißem Wasser übergießen und 5 Minuten quellen lassen.|Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Streifen schneiden.|Gurke und Tomaten würfeln und mit Couscous, Zitronensaft, Salz und Pfeffer mischen.|Fleisch darauflegen und Joghurt daraufgeben.")
r("Mini-Steaks mit Tomaten-Mozzarella-Gratin", "M", 30, "", "haehnst:150;tom:3;moz:50;couscous:40;knob:1;oel:0.5;~Basilikum, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Couscous mit heißem Wasser quellen lassen.|Mini-Steaks nach Packungsanleitung kurz anbraten.|Tomatenscheiben mit Knoblauch und Salz in eine Form legen, Steaks daraufsetzen und mit Mozzarella belegen.|10 bis 12 Minuten backen, bis der Käse geschmolzen und das Fleisch durch ist. Mit Basilikum und Couscous servieren.")
r("Schnitzel in Paprika-Quark-Soße mit Nudeln", "M", 25, "", "schnitzel:150;pap:2;zwie:1;speisequark:50;nudel:60;paprikap:1;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Schnitzel in Streifen im Öl braten, bis sie durch sind. Paprika und Zwiebel in Streifen zugeben und 5 Minuten braten.|Pfanne vom Herd nehmen, Quark und Paprikapulver unterrühren und abschmecken.|Mit den Nudeln mischen.")
r("Schnitzel Caprese mit Rucola und Nudeln", "M", 30, "", "schnitzel:150;tom:2;moz:50;ruc:30;nudel:60;oel:1;~Basilikum, Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen. Ofen auf 200 °C vorheizen.|Schnitzel würzen und im Öl von jeder Seite 3 Minuten anbraten, in eine Form legen.|Mit Tomatenscheiben und Mozzarella belegen und 8 bis 10 Minuten überbacken, bis der Käse geschmolzen ist und das Fleisch durch ist.|Mit Rucola und Nudeln servieren.")
r("Schnitzel in Haferflockenkruste mit Tomaten-Gurken-Salat", "M", 30, "", "schnitzel:150;ei:1;hafer:30;tom:2;gurke:100;senf:1;oel:1;~Salz und Pfeffer",
  "Schnitzel flach klopfen, würzen und mit Senf bestreichen. Ei verquirlen, Haferflocken auf einen Teller geben.|Schnitzel erst im Ei, dann in den Haferflocken wenden.|Im Öl bei mittlerer Hitze von jeder Seite 4 bis 5 Minuten braten, bis die Kruste goldbraun und das Fleisch durch ist.|Tomaten und Gurke würfeln, mit Salz und Pfeffer als Salat dazu servieren.")
r("Lyoner-Pfanne mit Rührei, Paprika und Brot", "M", 15, "g", "lyoner:60;ei:2;pap:2;zwie:0.5;brot:1;oel:1;~Salz und Pfeffer",
  "Lyoner in Würfel schneiden, Paprika und Zwiebel in Streifen.|Alles im Öl 5 Minuten braten.|Eier verquirlen, würzen und dazugeben. Bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.|Mit dem Brot essen.")
r("Lyoner-Wurstsalat mit Ei, Gurke und Saurer Gurke", "M", 15, "kg", "lyoner:70;ei:2;sgurke:2;gurke:150;zwie:0.5;senf:1;jogGr:30;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Lyoner in Streifen, Gurke in Scheiben, Saure Gurken und Zwiebel fein schneiden.|Senf mit Joghurt, Salz und Pfeffer zum Dressing verrühren.|Alles vermengen und mindestens 10 Minuten ziehen lassen.")


# ======================= NEU (Runde 4): vegetarisch, Hülsenfrüchte, Eier =======================
r("Kichererbsen-Curry mit Spiegelei und Reis", "M", 30, "p", "kiche:120;kokos:100;curry:1;garam:1;pap:1;zwie:1;stueck:150;reis:30;ei:2;oel:0.5;~Salz",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Paprika klein schneiden und im Öl 4 Minuten anbraten. Curry und Garam Masala kurz mitrösten.|Kichererbsen, stückige Tomaten und Kokosmilch zugeben und 12 Minuten köcheln. Mit Salz abschmecken.|Spiegeleier in einer zweiten Pfanne ohne zusätzliches Fett braten, bis das Eiweiß ganz fest ist, und auf dem Curry servieren.")
r("Rotes Linsen-Dal mit Reis und Joghurt", "M", 30, "pg", "linse:70;reis:50;zwie:1;stueck:150;kurkuma:1;garam:1;kreuz:1;knob:1;jogGr:50;oel:1;~Salz",
  "Reis nach Packungsanleitung kochen.|Zwiebel und Knoblauch im Öl andünsten, Kurkuma, Kreuzkümmel und Garam Masala kurz mitrösten.|Linsen, stückige Tomaten und 300 ml Wasser zugeben und 15 Minuten köcheln, bis die Linsen weich sind. Mit Salz abschmecken.|Mit Reis und einem Klecks Joghurt servieren.",
  "Rote Linsen brauchen keine Einweichzeit. Das Dal lässt sich gut einfrieren.")
r("Menemen mit Ei, Paprika, Tomate und Brot", "M", 20, "g", "ei:3;pap:1;tom:2;zwie:1;brot:2;oel:1;~Salz und Pfeffer",
  "Zwiebel und Paprika klein schneiden und im Öl 4 Minuten anbraten.|Tomaten in Stücken zugeben und 5 Minuten einkochen.|Eier verquirlen, würzen und in die Pfanne geben, bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.|Mit dem Brot essen.")
r("Frittata mit Paprika, Tomate, Mozzarella und Rucola", "M", 25, "g", "ei:4;pap:1;tom:1;moz:50;ruc:20;oel:1;~Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Paprika klein schneiden und in einer ofenfesten Pfanne im Öl 4 Minuten anbraten.|Eier verquirlen, würzen und darübergießen. Tomatenscheiben und zerzupften Mozzarella darauf verteilen.|2 Minuten auf dem Herd anstocken lassen, dann 10 Minuten im Ofen backen, bis das Ei ganz fest ist.|Mit Rucola bestreuen.",
  "Kalt in Stücken schmeckt sie auch am nächsten Tag und passt in die Brotdose.")
r("Rucola-Frittata mit Tomate und Parmesan", "M", 25, "g", "ei:3;ruc:30;tom:2;parm:15;zwie:0.5;oel:1;~Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Zwiebel und Tomaten in Stücke schneiden und in einer ofenfesten Pfanne im Öl 3 Minuten anbraten.|Eier mit dem Parmesan verquirlen, würzen und darübergießen.|2 Minuten anstocken lassen, dann 8 bis 10 Minuten im Ofen backen, bis das Ei ganz fest ist.|Rucola daraufgeben.")
r("Kichererbsen-Ei-Salat mit Gurke und Joghurt", "M", 20, "kg", "kiche:150;ei:2;gurke:150;tom:2;jogGr:40;zitrone:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen, abschrecken und pellen.|Kichererbsen abtropfen. Gurke und Tomaten würfeln.|Joghurt mit Zitronensaft, Salz und Pfeffer verrühren.|Alles mischen, Eier in Stücken daraufgeben.")
r("Bohnen-Mozzarella-Salat mit Tomate und Rucola", "M", 15, "kg", "bohne:150;moz:60;tom:2;zwie:0.5;ruc:20;oel:1;zitrone:1;~Salz und Pfeffer",
  "Bohnen abtropfen. Tomaten würfeln, Zwiebel fein schneiden, Mozzarella zerzupfen.|Alles mit Öl, Zitronensaft, Salz und Pfeffer mischen.|Rucola zum Schluss daraufgeben.")
r("Linsen-Paprika-Eintopf", "M", 35, "pg", "linse:80;pap:2;zwie:1;stueck:200;bruehe:300;paprikap:1;kreuz:1;knob:1;oel:1;~Salz und Pfeffer",
  "Zwiebel, Paprika und Knoblauch klein schneiden und im Öl 5 Minuten anbraten.|Paprikapulver und Kreuzkümmel kurz mitrösten, Linsen, stückige Tomaten und Brühe zugeben.|20 Minuten köcheln, bis die Linsen weich sind. Mit Salz und Pfeffer abschmecken.",
  "Gekühlt 2 Tage haltbar, vor dem Essen vollständig erhitzen.")
r("Kichererbsen-Tomaten-Pfanne mit Ei und Rucola", "M", 20, "g", "kiche:150;tom:3;zwie:1;ei:2;ruc:20;knob:1;paprikap:1;oel:1;~Salz und Pfeffer",
  "Zwiebel und Knoblauch im Öl andünsten, Paprikapulver kurz mitrösten.|Tomaten in Stücken und Kichererbsen zugeben und 8 Minuten schmoren.|Zwei Mulden formen, Eier hineingeben und zugedeckt stocken lassen, bis das Eiweiß ganz fest ist.|Mit Rucola bestreuen.")
r("Bohnen-Reis-Bowl mit Ei und Tomaten-Salsa", "M", 25, "", "bohne:120;reis:50;ei:2;tom:2;zwie:0.5;zitrone:1;oel:1;paprikap:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen.|Tomaten und Zwiebel würfeln und mit Zitronensaft, Salz und Pfeffer zur Salsa mischen.|Bohnen mit Paprikapulver kurz erhitzen. Eier im Öl zu Spiegeleiern braten, bis das Eiweiß fest ist.|Reis, Bohnen, Salsa und Eier in einer Schüssel anrichten.")
r("Pasta e Fagioli mit Parmesan", "M", 30, "pg", "bohne:120;nudel:50;stueck:200;zwie:1;knob:1;parm:15;bruehe:200;oel:1;~Oregano, Salz und Pfeffer",
  "Zwiebel und Knoblauch im Öl andünsten.|Stückige Tomaten, Bohnen, Brühe und Oregano zugeben und 10 Minuten köcheln.|Nudeln zugeben und nach Packungsanleitung garen, bis sie weich sind.|Mit Salz und Pfeffer abschmecken und mit Parmesan bestreuen.")
r("Reis-Omelett mit Paprika und Tomate", "M", 20, "g", "ei:3;reis:40;pap:1;tom:1;zwie:0.5;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen (oder Reste vom Vortag verwenden).|Paprika und Zwiebel klein schneiden und im Öl 4 Minuten anbraten, Tomate in Würfeln kurz mitbraten.|Eier verquirlen, würzen, mit dem Reis mischen und in die Pfanne geben.|Bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.")
r("Linsen-Bowl mit Paprika, Gurke und Joghurt", "M", 25, "pa", "linse:70;gurke:100;pap:1;tom:1;jogGr:60;zitrone:1;kreuz:1;oel:1;~Salz und Pfeffer",
  "Linsen in 300 ml Wasser 12 bis 15 Minuten weich kochen und abgießen.|Paprika, Gurke und Tomate würfeln.|Linsen mit Kreuzkümmel, Zitronensaft, Öl, Salz und Pfeffer anmachen und mit dem Gemüse mischen.|Joghurt daraufgeben.",
  "Hält sich gekühlt 2 Tage und ist kalt eine gute Brotdosen-Mahlzeit.")
r("Gefüllte Paprika mit Quark und Ei", "M", 35, "", "pap:2;quark:100;ei:2;gouda:20;zwie:0.5;brot:1;~Schnittlauch, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Paprika halbieren und entkernen.|Quark mit Eiern, fein gehackter Zwiebel, Salz und Pfeffer verrühren und in die Paprikahälften füllen.|Mit Gouda bestreuen und 25 Minuten backen, bis die Füllung fest ist.|Mit dem Brot servieren.")
r("Kichererbsen-Pfanne mit Paprika und Joghurt", "M", 25, "g", "kiche:150;pap:2;zwie:1;jogGr:60;kurkuma:1;kreuz:1;knob:1;oel:1;brot:1;~Salz und Pfeffer",
  "Zwiebel, Paprika und Knoblauch im Öl 5 Minuten anbraten.|Kurkuma und Kreuzkümmel kurz mitrösten, Kichererbsen zugeben und 6 Minuten braten.|Mit Salz und Pfeffer abschmecken und mit Joghurt und Brot servieren.")
r("Tex-Mex-Rührei mit Bohnen, Paprika und Brot", "M", 15, "g", "ei:3;bohne:60;pap:1;tom:1;gouda:15;brot:1;oel:1;paprikap:1;~Salz und Pfeffer",
  "Paprika in Stücken im Öl 4 Minuten anbraten, Bohnen und Paprikapulver zugeben.|Eier verquirlen, würzen und dazugeben, bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.|Mit Tomatenwürfeln und Gouda bestreuen und mit dem Brot essen.")
r("Quark-Nudeln mit Tomate und Rucola", "M", 20, "g", "nudel:80;quark:100;tom:3;ruc:30;parm:15;knob:1;oel:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen. Etwas Nudelwasser aufheben.|Knoblauch und Tomaten in Stücken im Öl 4 Minuten schmoren.|Quark mit etwas Nudelwasser glatt rühren und mit den Nudeln und den Tomaten mischen (nicht mehr kochen).|Rucola und Parmesan daraufgeben.")
r("Puten-Käse-Toast mit Tomate und Rucola", "M", 15, "ga", "brot:2;paufs:60;tom:2;moz:40;ruc:20;senf:1;~Oregano und Pfeffer",
  "Ofen auf 200 °C vorheizen. Brot dünn mit Senf bestreichen.|Mit Putenaufschnitt, Tomatenscheiben und Mozzarella belegen.|8 bis 10 Minuten überbacken, bis der Käse geschmolzen ist.|Mit Rucola und Oregano bestreuen, mit Pfeffer würzen.")
r("Griechischer Joghurt mit Putenstreifen, Gurke und Brot", "M", 15, "ka", "pute:130;jogGr:100;gurke:150;tom:1;brot:2;knob:1;~Salz und Pfeffer",
  "Pute in Streifen in einer Pfanne ohne Fett braten, bis sie durch ist, oder fertig gegarte Pute verwenden.|Gurke und Tomate würfeln.|Joghurt mit Knoblauch, Salz und Pfeffer verrühren.|Alles mit dem Brot servieren.")

# ======================= NEU (Runde 4): Suppen und Eintöpfe =======================
r("Tomaten-Reis-Suppe mit Hackbällchen", "M", 35, "p", "rhack:100;reis:30;stueck:250;zwie:1;bruehe:300;paprikap:1;~Salz und Pfeffer",
  "Hack mit Salz und Pfeffer zu kleinen Bällchen formen.|Zwiebel fein würfeln, mit stückigen Tomaten, Brühe und Paprikapulver aufkochen.|Bällchen und Reis zugeben und 15 Minuten köcheln, bis der Reis weich ist und die Bällchen innen nicht mehr rosa sind.|Abschmecken.")
r("Bohnensuppe mit Putenhack und Paprika", "M", 30, "pg", "phack:100;bohne:100;stueck:200;pap:1;zwie:1;bruehe:300;paprikap:1;oel:0.5;~Salz und Pfeffer",
  "Zwiebel und Paprika klein schneiden und im Öl andünsten. Putenhack zugeben und krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Stückige Tomaten, Bohnen, Brühe und Paprikapulver zugeben.|15 Minuten köcheln und abschmecken.")
r("Putensuppe mit Nudeln, Paprika und Tomate", "M", 30, "p", "pute:120;nudel:40;pap:1;stueck:200;bruehe:300;zwie:1;oel:0.5;~Salz, Pfeffer und Oregano",
  "Zwiebel und Paprika klein schneiden und im Öl andünsten.|Pute in Würfeln zugeben und anbraten.|Stückige Tomaten und Brühe zugeben und 10 Minuten köcheln, bis die Pute durch ist.|Nudeln zugeben und nach Packungsanleitung garen. Würzen.")
r("Kichererbsen-Hack-Suppe mit Tomate", "M", 30, "pg", "rhack:80;kiche:100;stueck:200;zwie:1;bruehe:300;kreuz:1;paprikap:1;~Salz und Pfeffer",
  "Hack mit der Zwiebel im Topf krümelig anbraten, bis nichts Rosa mehr zu sehen ist.|Kreuzkümmel und Paprikapulver kurz mitrösten.|Kichererbsen, stückige Tomaten und Brühe zugeben und 15 Minuten köcheln.|Abschmecken.")

# ======================= NEU (Runde 4): Salate =======================
r("Couscous-Salat mit Kichererbsen, Gurke und Mozzarella", "M", 20, "kap", "couscous:50;kiche:100;gurke:150;tom:2;moz:50;zitrone:1;oel:1;~Salz und Pfeffer",
  "Couscous mit heißem Wasser übergießen, 5 Minuten quellen lassen und abkühlen lassen.|Gurke und Tomaten würfeln, Mozzarella würfeln, Kichererbsen abtropfen.|Alles mit Zitronensaft, Öl, Salz und Pfeffer vermengen.")
r("Eisbergsalat mit Mini-Steaks und Joghurt-Dressing", "M", 20, "a", "haehnst:140;eisb:150;tom:2;gurke:100;jogGr:40;brot:1;zitrone:1;~Salz und Pfeffer",
  "Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Streifen schneiden.|Salat in Streifen schneiden, Tomaten und Gurke würfeln.|Joghurt mit Zitronensaft, Salz und Pfeffer verrühren.|Alles anrichten, Fleisch und Dressing daraufgeben und mit dem Brot essen.")
r("Tomaten-Mozzarella-Salat mit Putenstreifen und Gurke", "M", 20, "a", "pute:130;tom:3;moz:50;gurke:100;oel:1;~Basilikum, Salz und Pfeffer",
  "Pute in Streifen im Öl braten, bis sie durch ist.|Tomaten, Gurke und Mozzarella in Scheiben schneiden.|Alles anrichten, die Pute daraufgeben und mit Basilikum, Salz und Pfeffer würzen.")
r("Reissalat mit Putenhack, Gurke und Tomate", "M", 25, "pa", "phack:120;reis:50;gurke:150;tom:2;paprikap:1;zitrone:1;oel:1;~Salz und Pfeffer",
  "Reis nach Packungsanleitung kochen und abkühlen lassen.|Putenhack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist, und mit Paprikapulver würzen.|Gurke und Tomaten würfeln.|Alles mit Zitronensaft, Salz und Pfeffer mischen.")
r("Nudelsalat mit Putenaufschnitt, Gurke und Paprika", "M", 20, "kap", "nudel:60;paufs:80;gurke:150;pap:1;tom:1;jogGr:40;senf:1;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen, abschrecken und abkühlen lassen.|Aufschnitt in Streifen, Gurke, Paprika und Tomate würfeln.|Joghurt mit Senf, Salz und Pfeffer verrühren.|Alles vermengen und kurz ziehen lassen.")
r("Gemischter Salat mit Rührei und Schinken", "M", 15, "g", "ei:3;schink:60;eisb:100;tom:2;gurke:100;brot:1;oel:1;~Salz und Pfeffer",
  "Eier verquirlen, würzen und im Öl bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.|Salat, Tomaten und Gurke klein schneiden, Schinken in Streifen.|Alles anrichten und mit dem Brot essen.")


# ======================= NEU (Runde 4): Frühstück =======================
r("Griechischer Joghurt mit Erdbeeren, Mandeln und Honig", "F", 3, "kg", "jogGr:200;erdb:100;mandel:10;honig:1",
  "Erdbeeren in Stücke schneiden oder auftauen lassen.|Joghurt in eine Schale geben und Erdbeeren und gehackte Mandeln daraufgeben.|Mit Honig beträufeln.")
r("Griechischer Joghurt mit Banane und Haferflocken", "F", 3, "k", "jogGr:200;banane:1;hafer:30;~Zimt",
  "Banane in Scheiben schneiden.|Joghurt in eine Schale geben, Haferflocken und Banane darauf verteilen.|Mit Zimt bestäuben.")
r("Quark-Erdbeer-Smoothie", "F", 5, "kla", "quark:200;erdb:150;banane:0.5;milch:100",
  "Alle Zutaten in einen Mixer geben.|Etwa 30 Sekunden mixen, bis alles cremig ist.|Sofort trinken oder in eine Flasche füllen.")
r("Rührei mit Lyoner und Tomate auf Brot", "F", 10, "g", "ei:3;lyoner:30;tom:1;brot:1;oel:1;~Salz und Pfeffer",
  "Lyoner in Würfel schneiden und im Öl 2 Minuten anbraten.|Eier verquirlen, würzen und dazugeben, bei mittlerer Hitze stocken lassen, bis das Ei ganz fest ist.|Tomate in Scheiben schneiden und mit dem Brot zum Rührei servieren.")
r("Butter-Rührei auf Vollkornbrot", "F", 8, "g", "ei:3;butter:5;brot:2;~Schnittlauch, Salz und Pfeffer",
  "Butter in einer Pfanne bei niedriger Hitze zerlassen.|Eier verquirlen, würzen und in die Pfanne geben, unter Rühren langsam stocken lassen, bis das Ei ganz fest ist.|Auf dem Brot anrichten und mit Schnittlauch bestreuen.")
r("Quark-Pfannkuchen-Röllchen mit Erdbeeren", "F", 20, "g", "ei:2;hafer:40;milch:100;speisequark:100;erdb:100;butter:5",
  "Eier, Haferflocken und Milch mit dem Stabmixer zu einem glatten Teig mixen und 5 Minuten quellen lassen.|Butter in einer Pfanne erhitzen und aus dem Teig 2 dünne Pfannkuchen backen, bis sie fest sind.|Quark daraufstreichen, Erdbeeren darauflegen und einrollen.")
r("Hafer-Pfannkuchen mit Skyr und Banane", "F", 20, "g", "hafer:50;ei:2;milch:100;skyr:150;banane:1;butter:5",
  "Haferflocken, Eier und Milch glatt mixen.|Butter in einer Pfanne erhitzen und den Teig portionsweise ausbacken, nach 2 Minuten wenden, bis alles fest ist.|Banane in Scheiben schneiden und mit dem Skyr auf den Pfannkuchen servieren.")
r("Rührei-Brötchen mit Schinken und Tomate", "F", 10, "g", "broetchen:1;ei:2;schink:40;tom:1;butter:5;~Salz und Pfeffer",
  "Butter in der Pfanne zerlassen, Schinkenwürfel kurz anbraten.|Eier verquirlen, würzen und dazugeben, stocken lassen, bis das Ei ganz fest ist.|Brötchen aufschneiden und mit Tomatenscheiben und Rührei belegen.")
r("Quark-Toast mit Banane und Honig", "F", 5, "kg", "brot:2;quark:100;banane:1;honig:1;~Zimt",
  "Brot nach Wunsch toasten.|Quark daraufstreichen.|Banane in Scheiben darauflegen, mit Honig beträufeln und mit Zimt bestäuben.")
r("Skyr-Toast mit Erdbeeren und Mandeln", "F", 5, "k", "brot:2;skyr:150;erdb:100;mandel:5",
  "Brot nach Wunsch toasten.|Skyr daraufstreichen.|Erdbeeren in Scheiben darauflegen und mit gehackten Mandeln bestreuen.")
r("Frühstücks-Wrap mit Rührei, Schinken und Tomate", "F", 10, "ga", "wrap:1;ei:3;schink:40;tom:1;eisb:30;butter:5;~Salz und Pfeffer",
  "Butter in der Pfanne zerlassen, Schinkenwürfel kurz anbraten.|Eier verquirlen, würzen und dazugeben, stocken lassen, bis das Ei ganz fest ist.|Wrap kurz erwärmen, mit Salat und Tomate belegen und das Rührei daraufgeben.|Einrollen und halbieren.")
r("Rührei-Wrap mit Putenaufschnitt und Paprika", "F", 10, "ga", "wrap:1;ei:3;paufs:40;pap:1;oel:1;~Salz und Pfeffer",
  "Paprika in Streifen im Öl 3 Minuten anbraten.|Eier verquirlen, würzen und dazugeben, stocken lassen, bis das Ei ganz fest ist.|Wrap kurz erwärmen, mit Putenaufschnitt und Rührei belegen.|Einrollen und halbieren.")
r("Frühstücks-Pizza auf Brot mit Tomate und Putenaufschnitt", "F", 12, "g", "brot:2;tmark:1;moz:40;tom:1;paufs:40;~Oregano",
  "Ofen auf 200 °C vorheizen. Brot mit Tomatenmark bestreichen.|Mit Tomatenscheiben, Putenaufschnitt und Mozzarella belegen.|8 bis 10 Minuten überbacken, bis der Käse geschmolzen ist, und mit Oregano bestreuen.")
r("Erdbeer-Porridge mit Quark", "F", 10, "g", "hafer:50;milch:200;erdb:100;quark:100;honig:1",
  "Haferflocken mit der Milch in einem Topf unter Rühren 4 Minuten bei mittlerer Hitze kochen.|Erdbeeren in Stücken unterheben, kurz erwärmen.|Quark daraufgeben und mit Honig süßen.")
r("Schoko-Bananen-Overnight-Oats mit Quark", "F", 5, "kpa", "hafer:50;milch:150;quark:100;banane:1;kakao:1;chia:10",
  "Haferflocken, Chia, Milch, Quark und Kakao im Glas verrühren.|Die Hälfte der Banane in Stücken unterheben.|Abgedeckt über Nacht in den Kühlschrank stellen und am Morgen mit der restlichen Banane belegen.")
r("Skyr-Haferglas mit Erdbeeren und Mandeln", "F", 4, "kga", "skyr:200;hafer:30;erdb:100;mandel:10",
  "Skyr und Haferflocken im Glas verrühren.|Erdbeeren in Stücken und gehackte Mandeln darauf verteilen.|Abgedeckt mitnehmen.")
r("Eierbrot mit Senf und Gurke", "F", 10, "ga", "brot:2;ei:2;gurke:100;senf:1;~Salz und Pfeffer",
  "Eier mindestens 8 Minuten hart kochen (gern am Vortag), abschrecken und pellen.|Brot mit Senf bestreichen.|Gurke und Eier in Scheiben darauflegen und würzen.")
r("Schinken-Gouda-Omelett mit Tomate", "F", 12, "g", "ei:3;schink:40;gouda:20;tom:1;oel:1;~Salz und Pfeffer",
  "Eier verquirlen und würzen. Öl in einer Pfanne erhitzen und die Eier bei mittlerer Hitze fast stocken lassen.|Schinken, Gouda und Tomatenscheiben auf eine Hälfte legen.|Zuklappen und 1 Minute ziehen lassen, bis das Ei ganz fest ist.")
r("Ei-Quark-Aufstrich auf Brot mit Saurer Gurke und Rucola", "F", 12, "gpa", "brot:2;ei:1;quark:80;sgurke:2;ruc:15;~Schnittlauch, Salz und Pfeffer",
  "Ei mindestens 8 Minuten hart kochen, abschrecken und pellen.|Ei mit einer Gabel zerdrücken, Quark und gehackte Saure Gurke unterrühren und würzen.|Auf das Brot streichen und mit Rucola belegen.")
r("Joghurt-Bananen-Brot mit Honig", "F", 4, "k", "brot:2;jogGr:100;banane:1;honig:0.5;~Zimt",
  "Brot mit Joghurt bestreichen.|Banane in Scheiben darauflegen.|Mit Honig beträufeln und mit Zimt bestäuben.")
r("Haferbrei mit Skyr und Erdbeeren", "F", 10, "g", "hafer:40;milch:200;skyr:150;erdb:100;~Zimt",
  "Haferflocken mit der Milch unter Rühren 4 Minuten bei mittlerer Hitze kochen.|Etwas abkühlen lassen, Skyr unterrühren (nicht mehr kochen).|Erdbeeren in Stücken daraufgeben und mit Zimt bestäuben.")

# ======================= NEU (Runde 4): Snacks =======================
r("Griechischer Joghurt mit Honig und Mandeln", "S", 2, "k", "jogGr:150;honig:1;mandel:10",
  "Joghurt in eine Schale geben.|Mandeln grob hacken und daraufstreuen.|Mit Honig beträufeln.")
r("Quark mit Banane und Kakao", "S", 3, "kgl", "quark:200;banane:0.5;kakao:1",
  "Banane mit einer Gabel zerdrücken.|Quark und Kakao unterrühren, bis eine Creme entsteht.")
r("Putenbrot mit Saurer Gurke und Senf", "S", 4, "kag", "brot:1;paufs:80;sgurke:2;senf:1",
  "Brot dünn mit Senf bestreichen.|Mit Putenaufschnitt und Saurer Gurke in Scheiben belegen.")
r("Mozzarella-Schinken-Spieße mit Tomate", "S", 5, "ka", "moz:50;schink:40;tom:1",
  "Tomate in Stücke schneiden, Mozzarella würfeln und Schinken in Streifen schneiden.|Abwechselnd auf Spieße stecken.")
r("Lyoner-Brot mit Senf und Saurer Gurke", "S", 4, "kg", "brot:1;lyoner:40;senf:1;sgurke:1",
  "Brot dünn mit Senf bestreichen.|Mit Lyoner und Saurer Gurke in Scheiben belegen.")
r("Mini-Steak-Happen mit Joghurt-Dip", "S", 10, "a", "haehnst:80;jogGr:40;gurke:50;~Salz und Pfeffer",
  "Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Stücke schneiden.|Joghurt mit Salz und Pfeffer verrühren.|Gurke in Sticks schneiden und alles zusammen in die Dose geben.")
r("Quark-Dip mit Tomate und Brot", "S", 4, "kg", "brot:1;speisequark:100;tom:1;~Kräuter, Salz und Pfeffer",
  "Quark mit Kräutern, Salz und Pfeffer verrühren.|Tomate in Scheiben schneiden.|Brot mit Quark bestreichen und mit Tomate belegen.")
r("Gefrorener Erdbeer-Quark-Joghurt", "S", 5, "kp", "quark:100;jogGr:100;erdb:100;honig:1",
  "Alle Zutaten glatt verrühren.|In ein verschließbares Gefäß füllen und mindestens 2 Stunden ins Gefrierfach stellen.|Vor dem Essen 10 Minuten antauen lassen.")
r("Schinken-Rucola-Brötchen mit Tomate", "S", 5, "ka", "broetchen:1;schink:40;tom:1;ruc:15",
  "Brötchen aufschneiden.|Mit Schinken, Tomatenscheiben und Rucola belegen.")
r("Mini-Wrap mit Quark, Schinken und Gurke", "S", 6, "ka", "wrap:1;quark:60;schink:40;gurke:50",
  "Quark auf dem Wrap verstreichen.|Schinken und Gurke in Streifen darauflegen.|Einrollen und halbieren.")
r("Bananen-Quark-Eis mit Kakao", "S", 5, "kp", "quark:150;banane:1;kakao:1",
  "Banane in Scheiben schneiden und 2 Stunden einfrieren.|Mit Quark und Kakao im Mixer cremig mixen.|Sofort essen.")
r("Mandel-Quark mit Erdbeeren", "S", 3, "kg", "quark:150;erdb:80;mandel:10",
  "Erdbeeren in Stücke schneiden oder auftauen lassen.|Quark in eine Schale geben, Erdbeeren und gehackte Mandeln daraufgeben.")
r("Kalte Gurken-Joghurt-Suppe", "S", 8, "kl", "jogGr:100;quark:80;gurke:150;knob:1;~Dill, Salz und Pfeffer",
  "Gurke grob schneiden, Knoblauch schälen.|Alles mit Joghurt und Quark im Mixer glatt pürieren.|Mit Salz, Pfeffer und Dill abschmecken und gekühlt essen.")
r("Mini-Frikadellen mit Gurken-Dip", "S", 20, "pa", "rhack:80;hafer:10;jogGr:40;gurke:80;paprikap:1;oel:0.5;~Salz und Pfeffer",
  "Hack mit Haferflocken, Paprikapulver, Salz und Pfeffer verkneten und zu kleinen Bällchen formen.|Im Öl rundum 8 bis 10 Minuten braten, bis sie innen nicht mehr rosa sind.|Gurke raspeln oder würfeln und mit Joghurt, Salz und Pfeffer zum Dip verrühren.")
r("Bohnen-Dip mit Quark und Gurkensticks", "S", 8, "k", "bohne:100;quark:50;knob:1;paprikap:1;zitrone:1;gurke:150;~Salz",
  "Bohnen abtropfen und mit Quark, Knoblauch, Paprikapulver und Zitronensaft pürieren.|Mit Salz abschmecken.|Gurke in Sticks schneiden und zum Dippen servieren.")
r("Skyr-Kakao-Dessert mit Erdbeeren", "S", 4, "kgl", "skyr:150;kakao:1;erdb:80;honig:0.5",
  "Skyr mit Kakao und Honig glatt rühren.|Erdbeeren in Stücken daraufgeben.")
r("Banane-Quark-Pfannküchlein", "S", 15, "g", "banane:1;ei:1;quark:80;hafer:20;butter:3",
  "Banane zerdrücken, mit Ei, Quark und Haferflocken zu einem Teig verrühren.|Butter in einer Pfanne erhitzen und aus dem Teig 3 kleine Küchlein backen, nach 2 Minuten wenden, bis alles fest ist.")
r("Crostini mit Tomate, Quark und Parmesan", "S", 10, "g", "brot:1;tom:1;parm:10;speisequark:60;knob:0.5;~Basilikum und Pfeffer",
  "Brot kurz toasten und mit der Knoblauchzehe einreiben.|Quark daraufstreichen und mit Tomatenscheiben belegen.|Parmesan darüberhobeln, mit Basilikum und Pfeffer würzen.")
r("Joghurt-Parmesan-Dip mit Paprika und Gurke", "S", 6, "k", "jogGr:60;parm:10;pap:1;gurke:80;quark:50;~Pfeffer",
  "Joghurt, Quark und fein geriebenen Parmesan verrühren, mit Pfeffer würzen.|Paprika und Gurke in Sticks schneiden.|Zum Dippen servieren.")
r("Schinken-Ei-Röllchen mit Paprika", "S", 10, "ga", "ei:2;schink:30;pap:0.5;oel:0.5;~Salz und Pfeffer",
  "Eier verquirlen, würzen und im Öl zu einem dünnen Omelett braten, bis das Ei ganz fest ist.|Schinken und Paprikastreifen daraufgeben.|Aufrollen und in Stücke schneiden.")
r("Lyoner-Gurken-Röllchen mit Quark", "S", 6, "kg", "lyoner:50;quark:50;gurke:80;~Pfeffer",
  "Quark mit Pfeffer verrühren und auf die Lyoner-Scheiben streichen.|Gurkenstreifen darauflegen und aufrollen.")
r("Mini-Steak-Mini-Wrap", "S", 10, "a", "haehnst:80;wrap:1;eisb:30;jogGr:30;~Salz und Pfeffer",
  "Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Streifen schneiden.|Wrap mit Joghurt bestreichen, Salat und Fleisch darauf verteilen.|Einrollen und halbieren.")

# ======================= NEU (Runde 4): noch ein paar Hauptgerichte =======================
r("Mini-Steak-Nudeln mit Tomate, Rucola und Parmesan", "M", 25, "", "haehnst:140;nudel:70;tom:3;ruc:30;parm:10;knob:1;oel:0.5;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Streifen schneiden.|Knoblauch und Tomaten in Stücken im Öl 3 Minuten schmoren.|Alles mit den Nudeln mischen, Rucola und Parmesan daraufgeben.")
r("Putenhack-Gemüse-Auflauf mit Couscous", "M", 40, "p", "phack:130;pap:2;tom:2;zwie:1;couscous:40;moz:40;oel:0.5;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Putenhack im Öl krümelig anbraten, bis nichts Rosa mehr zu sehen ist. Couscous mit heißem Wasser quellen lassen.|Paprika, Tomaten und Zwiebel in Stücke schneiden und mit Couscous und Hack in eine Form geben, würzen.|Mit Mozzarella belegen und 20 bis 25 Minuten backen, bis der Käse goldbraun ist.")
r("Lyoner-Nudelpfanne mit Tomate und Ei", "M", 25, "g", "lyoner:60;nudel:60;stueck:200;pap:1;zwie:1;ei:1;parm:10;oel:0.5;~Salz und Pfeffer",
  "Nudeln nach Packungsanleitung kochen.|Lyoner in Würfeln mit Paprika und Zwiebel im Öl 5 Minuten braten.|Stückige Tomaten zugeben und 5 Minuten köcheln. Das Ei verquirlen, unterrühren und stocken lassen, bis es ganz fest ist.|Nudeln untermischen und mit Parmesan bestreuen.")
r("Hähnchen-Blech mit Paprika, Tomate und Zwiebel", "M", 35, "", "haehn:160;pap:2;zwie:1;tom:2;brot:1;oel:1;paprikap:1;~Salz und Pfeffer",
  "Ofen auf 220 °C vorheizen.|Hähnchen in Stücke schneiden, Paprika, Tomaten und Zwiebel in Stücke schneiden. Alles mit Öl, Paprikapulver, Salz und Pfeffer mischen und auf ein Blech geben.|20 bis 25 Minuten backen, bis das Hähnchen im Kern durch und nicht mehr rosa ist.|Mit dem Brot servieren.")
r("Schnitzel-Tomaten-Auflauf mit Couscous und Mozzarella", "M", 40, "", "schnitzel:150;tom:3;pap:1;couscous:40;moz:40;zwie:0.5;knob:1;~Oregano, Salz und Pfeffer",
  "Ofen auf 200 °C vorheizen. Couscous mit heißem Wasser übergießen und 5 Minuten quellen lassen.|Schnitzel in Streifen schneiden, Tomaten, Paprika und Zwiebel in Stücke. Alles mit Couscous, Knoblauch und Gewürzen in eine Form geben.|Mit Mozzarella belegen und 25 Minuten backen, bis das Fleisch durch und der Käse goldbraun ist.")

# ======================= Berechnung =======================
def slug(t):
    t = unicodedata.normalize("NFKD", t.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss"))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")

def fmt_amount(v):
    return int(v) if float(v).is_integer() else v

out = []
for rec in R:
    kcal = prot = veg = cost = 0.0
    keys, flags, items = [], set(), []
    for part in rec["ing"].split(";"):
        part = part.strip()
        if part.startswith("~"):
            items.append([None, "", part[1:], None, None]); continue
        k, a = part.split(":")
        a = float(a)
        name, pl, unit, per, kc, pr, fl, grp = DB[k]
        grams = a * per
        kcal += grams * kc / 100; prot += grams * pr / 100
        pk = PRICE[k]; cost += grams * pk[1] / pk[0]
        if grp == "gemüse": veg += grams
        keys.append(k)
        for f in fl.split(","):
            if f: flags.add(f)
        if unit in ("g", "ml", "EL", "TL"):
            items.append([fmt_amount(a), unit, name, None, k])
        else:
            items.append([fmt_amount(a), "", name, pl, k])
    meat = {"Geflügel", "Rindfleisch", "Schwein"} & flags
    diet = "omni" if meat else ("vegetarisch" if flags & {"Ei", "Milch", "Käse", "Honig"} else "vegan")
    tags = [TAG[c] for c in rec["tags"]]
    contains = [c for c in SHOWN_CONTAINS if c in flags]
    note = None
    if "Meal-Prep" in tags and set(keys) & {"reis", "nudel", "couscous"}:
        note = "Zum Vorkochen: Reis, Nudeln und Couscous nach dem Kochen schnell abkühlen, im Kühlschrank aufbewahren, am besten am nächsten Tag essen (spätestens nach 2 Tagen) und vollständig erhitzen."
    out.append(dict(id=slug(rec["title"]), title=rec["title"], meal=rec["meal"], time=rec["time"],
                    kcal=int(round(kcal / 5.0) * 5), protein=int(round(prot)), cost=round(cost, 2), veg=int(round(veg / 10.0) * 10),
                    diet=diet, tags=tags, contains=contains, ing=items, steps=rec["steps"],
                    tip=rec["tip"], note=note, _keys=keys, _flags=sorted(flags), _meat=sorted(meat)))

# „Günstig“ richtet sich jetzt nach den berechneten Lidl-Kosten
CHEAP = {"Frühstück": 1.00, "Mittag/Abend": 2.00, "Snack": 0.80}
for o in out:
    o["tags"] = [t for t in o["tags"] if t != "Günstig"]
    if o["cost"] <= CHEAP[o["meal"]]: o["tags"].append("Günstig")

# ======================= Prüfung =======================
problems = []
ids = [o["id"] for o in out]
assert len(set(ids)) == len(ids), "doppelte IDs"
assert len(out) == TARGET, len(out)
BANNED = ["gyros", "fisch", "thunfisch", "lachs", "tofu", "kartoffel", "hüttenkäse", "pilz", "brokkoli", "zucchini", "radieschen"]
for o in out:
    text = (o["title"] + " " + " ".join(i[2] for i in o["ing"]) + " " + " ".join(o["steps"])).lower()
    for b in BANNED:
        if b in text: problems.append(f"Unerwünscht ({b}): {o['title']}")
    # Karotte nur in gekochten Soßen
    if "karo" in o["_keys"] and not re.search(r"bolognese|chili", o["title"].lower()):
        problems.append(f"Karotte nicht in Soße: {o['title']}")
    lim = {"Frühstück": (150, 650), "Mittag/Abend": (330, 700), "Snack": (100, 400)}[o["meal"]]
    if not lim[0] <= o["kcal"] <= lim[1]: problems.append(f"kcal außerhalb {lim}: {o['title']} = {o['kcal']}")
    pmin = {"Frühstück": 13, "Mittag/Abend": 23, "Snack": 9}[o["meal"]]
    if o["protein"] < pmin: problems.append(f"Eiweiß unter {pmin} g: {o['title']} = {o['protein']}")
    if o["meal"] == "Mittag/Abend" and o["veg"] < 100: problems.append(f"Gemüse unter 100 g: {o['title']} = {o['veg']}")

stat = collections.Counter(o["meal"] for o in out)
src = collections.Counter()
for o in out:
    k = set(o["_keys"])
    if k & {"haehn"}: src["Hähnchen"] += 1
    elif k & {"pute", "phack"}: src["Pute"] += 1
    elif k & {"rhack", "ghack"}: src["Hack (Rind/Schwein)"] += 1
    elif k & {"linse", "kiche", "bohne"}: src["Hülsenfrüchte"] += 1
    elif k & {"ei"}: src["Ei"] += 1
    elif k & {"skyr", "quark"}: src["Quark/Skyr"] += 1
    elif k & {"moz", "gouda", "parm", "schink", "paufs"}: src["Käse/Aufschnitt"] += 1
    else: src["sonstige"] += 1
processed = [o["title"] for o in out if "verarbeitet" in "".join(o["_flags"])]
mains = [o for o in out if o["meal"] == "Mittag/Abend"]
# Ähnlichkeit
sim = []
for a, b in itertools.combinations(out, 2):
    A, B = set(a["_keys"]), set(b["_keys"])
    if len(A) >= 4 and len(A & B) / len(A | B) >= 0.8: sim.append((a["title"], b["title"], round(len(A & B) / len(A | B), 2)))
cheese_heavy = [o["title"] for o in out if sum(float(p.split(":")[1]) for p in R[ids.index(o["id"])]["ing"].split(";") if p.split(":")[0] in ("moz", "gouda", "parm")) > 80]

def avg(l): return sum(l) / len(l)
if "--report" in sys.argv or True:
    print("Anzahl:", len(out), dict(stat))
    print("Hauptquelle Eiweiß:", dict(src))
    print("Verarbeitetes Fleisch:", len(processed), processed)
    print("Ø kcal je Mahlzeit: Frühstück %d, Mittag/Abend %d, Snack %d" % tuple(avg([o["kcal"] for o in out if o["meal"] == m]) for m in ["Frühstück", "Mittag/Abend", "Snack"]))
    print("Ø Eiweiß: Frühstück %.0f, Mittag/Abend %.0f, Snack %.0f" % tuple(avg([o["protein"] for o in out if o["meal"] == m]) for m in ["Frühstück", "Mittag/Abend", "Snack"]))
    print("Hauptgerichte mit ≥150 g Gemüse: %d von %d; ≥100 g: %d" % (sum(o["veg"] >= 150 for o in mains), len(mains), sum(o["veg"] >= 100 for o in mains)))
    print("Vegetarisch/vegan gesamt: %d, vegan %d" % (sum(o["diet"] != "omni" for o in out), sum(o["diet"] == "vegan" for o in out)))
    print("Mit Hülsenfrüchten:", sum("Hülsenfrüchte" in o["contains"] for o in out), "| Rind:", sum("Rindfleisch" in o["contains"] for o in out), "| Nüsse:", sum("Nüsse" in o["contains"] for o in out))
    print("Tag-Zähler:", dict(collections.Counter(t for o in out for t in o["tags"])))
    cs = sorted(o["cost"] for o in out)
    print("Kosten je Portion: min %.2f, Median %.2f, max %.2f; Ø Frühstück %.2f, Mittag/Abend %.2f, Snack %.2f" % (cs[0], cs[len(cs)//2], cs[-1], *[avg([o["cost"] for o in out if o["meal"] == m]) for m in ["Frühstück", "Mittag/Abend", "Snack"]]))
    for o in sorted(out, key=lambda o: -o["cost"])[:8]: print("  teuer:", o["title"], o["cost"], o["protein"], "g")
    for o in sorted(out, key=lambda o: o["cost"])[:5]: print("  billig:", o["title"], o["cost"])
    print("Sehr ähnliche Paare:", sim)
    print("Käsereich (>80 g):", cheese_heavy)
    print("Probleme:", len(problems))
    for p in problems: print("  -", p)

pub = [{k: v for k, v in o.items() if not k.startswith("_") and v is not None} for o in out]
PJ = {k: dict(pack=v[0], price=v[1], sec=v[2], label=v[3], loose=v[4], staple=v[5], per=DB[k][3], u=DB[k][2], n=DB[k][0], pl=DB[k][1], p=DB[k][5], kcal=DB[k][4]) for k, v in PRICE.items()}
json.dump(PJ, open(os.path.join(HERE, "prices.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump(pub, open(os.path.join(HERE, "recipes.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=None)
json.dump(out, open(os.path.join(HERE, "recipes_full.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("geschrieben:", len(pub))

# ======================= Beispieltage =======================
DAYS_DEF = [
 ("Arbeitstag mit kleinem Frühstück", ["skyr-mit-banane-und-mandeln", "haehnchen-wrap", "erdbeer-quark-shake", "spaghetti-bolognese-mit-vollkornnudeln", "quark-kakao-creme"]),
 ("Arbeitstag ohne Frühstück", ["overnight-oats-dein-rezept", "gouda-mit-gurke-und-tomate", "haehnchen-reis-pfanne", "skyr-mit-erdbeeren", "quark-kakao-creme"]),
 ("Wochenende mit Frühstück", ["ruehrei-mit-paprika-und-brot", "linsen-curry", "skyr-mit-mandeln-und-zimt", "nudelauflauf-mit-tomate-paprika-und-mozzarella", "quark-kakao-creme"]),
]
byid = {o["id"]: o for o in out}
days = []
for name, idl in DAYS_DEF:
    for i in idl: assert i in byid, i
    days.append(dict(name=name, items=[dict(id=i, title=byid[i]["title"], meal=byid[i]["meal"], kcal=byid[i]["kcal"], protein=byid[i]["protein"]) for i in idl],
                     kcal=sum(byid[i]["kcal"] for i in idl), protein=sum(byid[i]["protein"] for i in idl)))
json.dump(days, open(os.path.join(HERE, "days.json"), "w", encoding="utf-8"), ensure_ascii=False)
for d in days: print("Tag:", d["name"], d["kcal"], "kcal", d["protein"], "g Eiweiß")
