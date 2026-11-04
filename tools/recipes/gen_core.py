# -*- coding: utf-8 -*-
"""Bausteine für die erzeugten Rezepte: Fleisch, Beilagen und häufige Arbeitsschritte.

Jede Rezeptfamilie (gen_main.py, gen_fs.py) setzt daraus Zutaten, Schritte und Titel zusammen.
Alle Mengen gelten für eine Portion und sind Rohgewicht (Fleisch, Reis, Nudeln)."""

import re, unicodedata

USED = set()          # schon vergebene Titel (als Slug, so wie build.py die IDs bildet)
SKIPPED = []          # Titel, die doppelt gewesen wären
OUT = []              # (title, meal, time, tags, ing, steps, tip)


def ing(**kw):
    """ing(haehn=160, reis=70, T="Salz und Pfeffer") -> "haehn:160;reis:70;~Salz und Pfeffer"."""
    parts = []
    for k, v in kw.items():
        if k == "T":
            parts.append("~" + v)
        else:
            parts.append(f"{k}:{v:g}" if isinstance(v, (int, float)) else f"{k}:{v}")
    return ";".join(parts)


def join(*chunks):
    """Fügt Zutatenstücke (Strings) zusammen und fasst gleiche Schlüssel zusammen (Mengen addiert)."""
    amounts, order, texts = {}, [], []
    for c in chunks:
        for p in c.split(";"):
            p = p.strip()
            if not p:
                continue
            if p.startswith("~"):
                texts.append(p[1:]); continue
            k, a = p.split(":")
            if k not in amounts:
                order.append(k); amounts[k] = 0.0
            amounts[k] += float(a)
    res = [f"{k}:{amounts[k]:g}" for k in order]
    texts = list(dict.fromkeys(texts))
    texts = [t for t in texts if not any(t != u and t in u for u in texts)]  # "Pfeffer" entfällt, wenn schon "Salz und Pfeffer" dasteht
    if texts:
        res.append("~" + ", ".join(texts))
    return ";".join(res)


def slug(t):
    t = unicodedata.normalize("NFKD", t.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss"))
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


DB = {}               # setzt build.py (Zutatentabelle), damit die Mengen geprüft und angepasst werden können
# Zutat: (Schritt, Mindestmenge). Wird eine Mahlzeit zu energiereich, werden diese Mengen schrittweise gekürzt.
FIT = {"oel": (0.5, 0.5), "reis": (10, 40), "nudel": (10, 50), "brot": (1, 1), "wrap": (1, 1), "moz": (10, 20), "gouda": (10, 20),
       "parm": (5, 10), "rhack": (10, 90), "phack": (10, 100), "ghack": (10, 85), "linse": (10, 50), "kiche": (10, 120), "bohne": (10, 100), "kokos": (25, 75),
       "hafer": (5, 15), "jogGr": (10, 40), "honig": (0.5, 0.5), "mandel": (5, 5), "butter": (2, 2), "lyoner": (10, 30), "broetchen": (1, 1), "ei": (0.5, 1)}
LIMIT = {"M": 640, "F": 600, "S": 360}
MINPROT = {"M": 23, "F": 13, "S": 9}   # wie die Prüfung in build.py: wer darunter liegt, wird gar nicht erst erzeugt
LOWPROT = []          # Titel, die wegen zu wenig Eiweiß weggefallen sind
BADTASTE = []         # Titel, die wegen unpassender Kombination weggefallen sind
KAESE_MILD = {"moz", "gouda"}
WUERZ_STARK = {"kokos", "curry", "garam", "kurkuma"}
LIGHT = {"M": 460, "F": 320, "S": 190}


def _parse(s):
    out = []
    for p in s.split(";"):
        if p.startswith("~"):
            out.append((None, p[1:]))
        elif p:
            k, a = p.split(":"); out.append((k, float(a)))
    return out


def _unparse(parts):
    return ";".join("~" + a if k is None else f"{k}:{a:g}" for k, a in parts)


def _kcal(k, a):
    name, pl, unit, per, kc, pr, fl, grp = DB[k]
    return a * per * kc / 100.0


def _protein(parts):
    total = 0.0
    for k, a in parts:
        if k:
            name, pl, unit, per, kc, pr, fl, grp = DB[k]
            total += a * per * pr / 100.0
    return total


def fit(ingredients, meal):
    """Kürzt Beilagen, Fett, Käse und Hack in kleinen Schritten, bis die Mahlzeit im Rahmen liegt."""
    parts = _parse(ingredients)
    for _ in range(60):
        if sum(_kcal(k, a) for k, a in parts if k) <= LIMIT[meal]:
            break
        best = None
        for i, (k, a) in enumerate(parts):
            if k in FIT and a - FIT[k][0] >= FIT[k][1] - 1e-9:
                kc = _kcal(k, FIT[k][0])
                if best is None or kc > best[0]:
                    best = (kc, i)
        if best is None:
            break
        i = best[1]; k, a = parts[i]; parts[i] = (k, a - FIT[k][0])
    return _unparse(parts), sum(_kcal(k, a) for k, a in parts if k)


def unpassend(keys):
    """Kombinationen, die selten gut schmecken: milder Käse zu Curry oder Kokos, Parmesan zu Curry, Kokos oder Honig."""
    if keys & KAESE_MILD and keys & WUERZ_STARK:
        return True
    return "parm" in keys and bool(keys & (WUERZ_STARK | {"honig"}))


def add(title, meal, time, tags, ingredients, steps, tip=None):
    if slug(title) in USED:
        SKIPPED.append(title); return False
    if unpassend({k for k, _ in _parse(ingredients) if k}):
        BADTASTE.append(title); return False
    USED.add(slug(title))
    if DB:
        ingredients, kc = fit(ingredients, meal)
        if round(_protein(_parse(ingredients))) < MINPROT[meal]:
            LOWPROT.append(title); USED.discard(slug(title)); return False
        if kc <= LIGHT[meal] and "l" not in tags:
            tags += "l"
    OUT.append((title, meal, int(time), tags, ingredients, "|".join(steps) if isinstance(steps, (list, tuple)) else steps, tip))
    return True


# ---------------- Fleisch ----------------
# key: (Vorsilbe im Titel, Menge g, Art)
MEAT = {
    "haehn": ("Hähnchen", 160, "stk"),
    "pute": ("Puten", 160, "stk"),
    "schnitzel": ("Schnitzel", 150, "stk"),
    "haehnst": ("Mini-Steak", 150, "steak"),
    "phack": ("Putenhack", 140, "hack"),
    "rhack": ("Rinderhack", 130, "hack"),
    "ghack": ("Hack", 120, "hack"),
}


def meat_step(k, oel=True):
    art = MEAT[k][2]
    if art == "hack":
        return "Hack in der heißen Pfanne mit etwas Öl 5 bis 7 Minuten krümelig anbraten, bis nichts Rosa mehr zu sehen ist." if oel else "Hack in einer heißen Pfanne 5 bis 7 Minuten krümelig anbraten, bis nichts Rosa mehr zu sehen ist."
    if art == "steak":
        return "Die Mini-Steaks nach Packungsanleitung braten, bis sie durch sind, und in Streifen schneiden."
    return "Das Fleisch in mundgerechte Stücke schneiden und im heißen Öl 6 bis 8 Minuten rundum braten, bis es durch und innen nicht mehr rosa ist."


def meat_oel(k):
    """Öl in TL für das Anbraten (Hack und Mini-Steaks brauchen kaum Öl)."""
    art = MEAT[k][2]
    return {"hack": 0.5, "steak": 0.5}.get(art, 1)


# ---------------- Beilagen ----------------
# key: (Wort im Titel, Menge g roh, Zeit min, Schritt)
CARB = {
    "reis": ("Reis", 70, 15, "Reis nach Packungsanleitung kochen."),
    "nudel": ("Nudeln", 80, 12, "Nudeln nach Packungsanleitung in Salzwasser bissfest kochen."),
}


def round5(x):
    return int(5 * round(x / 5.0))


def nl(*parts):
    """Zählt Namen auf: nl("Banane und Erdbeeren", "Kakao") -> "Banane, Erdbeeren und Kakao"."""
    words = []
    for p in parts:
        words += [w for w in p.split(" und ") if w]
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + " und " + words[-1]


SIDE_MIT = {"Brot": "Mit Brot servieren.", "Brötchen": "Mit einem Brötchen servieren.", "Wrap": "Mit dem Wrap servieren."}
