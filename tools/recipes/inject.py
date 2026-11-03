"""Setzt recipes.json, days.json und prices.json in index.html ein (Ersatz fuer RECIPES, DAYS und PRICE).

Ablauf: python3 tools/recipes/build.py   (erzeugt die JSON-Dateien und prueft die Rezepte)
        python3 tools/recipes/inject.py  (schreibt sie nach index.html)
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(os.path.dirname(os.path.dirname(HERE)), "index.html")
load = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))
R, D, P = load("recipes.json"), load("days.json"), load("prices.json")
s = open(INDEX, encoding="utf-8").read()
i = s.index("const RECIPES = ["); j = s.index("\nconst DAYS = ")
s = s[:i] + "const RECIPES = [\n" + ",\n".join("  " + json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in R) + "\n];\n" + s[j:]
def line(name, obj):
    global s
    m = re.search(r"^const " + name + r" = .*;$", s, re.M)
    assert m, name
    s = s[:m.start()] + "const " + name + " = " + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";" + s[m.end():]
line("DAYS", D); line("PRICE", P)
if os.environ.get("FC_DRY"):
    print("trocken:", len(R), "Rezepte"); raise SystemExit
open(INDEX, "w", encoding="utf-8").write(s)
print("eingesetzt:", len(R), "Rezepte")
