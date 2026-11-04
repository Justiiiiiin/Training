"""Rechnet alle Nährwerte unabhängig nach (Rezepte aus der Zutatentabelle, Plausibilität der Tabellen selbst).

1. Jedes Rezept: kcal, Eiweiß, Kosten und Gemüsemenge werden aus PRICE neu berechnet und mit den gespeicherten Werten verglichen.
2. Jede Zutat in PRICE liegt in einem Bereich, der zu üblichen Tabellen (BLS, USDA) passt. Fleisch, Reis, Nudeln gelten roh bzw. trocken.
3. Physik: Eiweiß liefert 4 kcal pro Gramm, also darf Eiweiß mal 4 nie über den Kalorien liegen (gilt auch für den Kalorien-Rechner).
4. Hygiene: Rezepte mit rohem Fleisch nennen "durch" oder "nicht mehr rosa" oder die Packungsanleitung."""
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
errs = []; fails = []


def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)


# Schlüssel: (kcal von, bis, Eiweiß von, bis) je 100 g bzw. 100 ml, Quelle: BLS 3.02 und USDA FoodData Central, grob gerundet
REF = {
    "haehn": (95, 125, 21, 24), "pute": (95, 125, 21, 25), "ghack": (220, 290, 15, 19), "phack": (110, 160, 18, 22), "rhack": (150, 200, 18, 22),
    "schink": (95, 125, 18, 22), "paufs": (85, 115, 17, 22), "ei": (130, 160, 12, 13.5), "skyr": (55, 70, 10, 12), "quark": (60, 75, 11, 14),
    "jog35": (60, 80, 3.3, 4.5), "milch": (44, 50, 3.2, 3.6), "moz": (230, 270, 17, 20), "gouda": (320, 400, 22, 27), "parm": (380, 440, 32, 38),
    "speisequark": (95, 125, 10, 13), "jogGr": (110, 150, 4.5, 7), "butter": (720, 760, 0.5, 1), "haehnst": (100, 125, 20, 23), "lyoner": (240, 290, 10, 14),
    "hafer": (360, 380, 12, 14), "chia": (470, 500, 15, 20), "mandel": (570, 610, 19, 22), "brot": (200, 250, 6, 9), "wrap": (270, 320, 8, 10),
    "broetchen": (220, 270, 8, 10), "nudel": (340, 360, 11.5, 14), "reis": (345, 365, 6.5, 8), "couscous": (350, 375, 11.5, 14), "honig": (295, 320, 0, 0.6),
    "oel": (880, 900, 0, 0.1), "soja": (50, 80, 5, 9), "tmark": (70, 110, 4, 5.5), "stueck": (20, 32, 0.9, 1.5), "tom": (15, 22, 0.8, 1.1),
    "gurke": (10, 16, 0.5, 0.8), "pap": (20, 40, 0.8, 1.3), "zwie": (28, 42, 1.0, 1.4), "karo": (30, 42, 0.8, 1.0), "eisb": (11, 16, 0.7, 1.1),
    "spin": (18, 27, 2.5, 3.2), "ruc": (20, 30, 2.3, 2.8), "sgurke": (10, 20, 0.3, 0.9), "knob": (130, 160, 5.5, 7), "banane": (85, 95, 1.0, 1.3),
    "erdb": (30, 40, 0.6, 0.9), "kiche": (115, 135, 6.5, 8), "bohne": (95, 125, 6, 8.5), "linse": (330, 360, 23, 26), "kokos": (60, 90, 0.4, 1.0),
    "bruehe": (0, 10, 0, 0.6), "zitrone": (20, 35, 0.3, 0.5), "senf": (60, 120, 4, 8), "kakao": (330, 400, 17, 25), "schnitzel": (100, 125, 20, 23),
    "curry": (290, 350, 10, 15), "garam": (300, 360, 10, 16), "paprikap": (280, 330, 12, 15), "kurkuma": (300, 330, 7, 10), "kreuz": (360, 400, 17, 19)}
# Gramm je Einheit (Stück, EL, TL): nur Werte, die realistisch sind
PER = {"ei": (48, 60), "brot": (35, 60), "wrap": (55, 70), "broetchen": (50, 70), "tom": (80, 130), "pap": (120, 200), "zwie": (60, 100), "karo": (60, 100),
       "sgurke": (25, 50), "knob": (2, 5), "banane": (80, 130), "honig": (5, 10), "oel": (4, 5), "soja": (13, 17), "tmark": (12, 20), "zitrone": (13, 17),
       "senf": (4, 6), "kakao": (3, 6), "curry": (2, 4), "garam": (2, 4), "paprikap": (2, 4), "kurkuma": (2, 4), "kreuz": (1.5, 3)}
MEAT = ["haehn", "pute", "phack", "rhack", "ghack", "schnitzel", "haehnst"]

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_function("window.__fcReady", timeout=20000)

    # 1. Rezepte neu rechnen
    res = pg.evaluate("""() => {
      const bad = [], ids = new Set(); let n = 0, maxdk = 0, maxdp = 0;
      const p0 = {}; Object.keys(PRICE).forEach(k => p0[k] = PRICE0[k]);
      RECIPES.forEach(r => {
        n++; if (ids.has(r.id)) bad.push('doppelte ID ' + r.id); ids.add(r.id);
        let k = 0, pr = 0, c = 0, v = 0;
        r.ing.forEach(i => { const key = i[4]; if (!key) return; const P = PRICE[key]; if (!P) { bad.push(r.id + ': unbekannte Zutat ' + key); return; }
          const g = i[0] * P.per; k += g * P.kcal / 100; pr += g * P.p / 100; c += g * P0price(key, P) / P.pack; if (['tom','gurke','pap','zwie','karo','eisb','spin','ruc','sgurke','stueck'].includes(key)) v += g; });
        function P0price(key, P) { return p0[key]; }
        // Abweichung vom ungerundeten Wert: höchstens die halbe Rundungsstufe (auf der .5-Grenze runden Python und JS verschieden)
        const E = 0.01, dk = Math.abs(k - r.kcal), dp = Math.abs(pr - r.protein), dc = Math.abs(Math.round(c * 100) / 100 - r.cost), dv = Math.abs(v - r.veg);
        maxdk = Math.max(maxdk, dk); maxdp = Math.max(maxdp, dp);
        if (dk > 2.5 + E || r.kcal % 5) bad.push(r.id + ': kcal ' + r.kcal + ' statt ' + k.toFixed(1));
        if (dp > 0.5 + E) bad.push(r.id + ': Eiweiß ' + r.protein + ' statt ' + pr.toFixed(2));
        if (dc > 0.011) bad.push(r.id + ': Kosten ' + r.cost + ' statt ' + c.toFixed(2));
        if (dv > 5 + E || r.veg % 10) bad.push(r.id + ': Gemüse ' + r.veg + ' statt ' + v.toFixed(0));
        if (pr * 4 > k + 10) bad.push(r.id + ': Eiweiß-kcal größer als kcal');
      });
      return { n, bad, maxdk, maxdp, uniqTitles: new Set(RECIPES.map(r => r.title)).size };
    }""")
    ck("1000 Rezepte", res["n"] == 1000, res["n"])
    ck("alle Titel verschieden", res["uniqTitles"] == 1000, res["uniqTitles"])
    ck("kcal, Eiweiß, Kosten und Gemüse stimmen bei allen Rezepten mit der Neuberechnung überein", not res["bad"], res["bad"][:5])

    # 1b. Grenzen je Mahlzeit (die bekannte Ausnahme Overnight Oats ist erlaubt)
    lim = pg.evaluate("""() => RECIPES.filter(r => r.id !== 'overnight-oats-dein-rezept').filter(r => {
      const L = { 'Frühstück': [150, 650, 13], 'Mittag/Abend': [330, 700, 23], 'Snack': [100, 400, 9] }[r.meal];
      return r.kcal < L[0] || r.kcal > L[1] || r.protein < L[2] || (r.meal === 'Mittag/Abend' && r.veg < 100);
    }).map(r => r.id + ' ' + r.kcal + ' kcal ' + r.protein + ' g ' + r.veg + ' g Gemüse')""")
    ck("alle Rezepte liegen in den Grenzen für Kalorien, Eiweiß und Gemüse", not lim, lim[:5])

    # 2. Zutatentabelle gegen Referenzbereiche
    tab = pg.evaluate("() => Object.keys(PRICE).map(k => [k, PRICE[k].kcal, PRICE[k].p, PRICE[k].per, PRICE[k].u])")
    miss = [k for k, *_ in tab if k not in REF]
    ck("jede Zutat hat einen Referenzbereich", not miss, miss)
    off = []
    for k, kc, pr, per, u in tab:
        if k not in REF: continue
        a, bb, c, d = REF[k]
        if not (a <= kc <= bb): off.append(f"{k}: {kc} kcal außerhalb {a}-{bb}")
        if not (c <= pr <= d): off.append(f"{k}: {pr} g Eiweiß außerhalb {c}-{d}")
        if k in PER and u not in ("g", "ml") and not (PER[k][0] <= per <= PER[k][1]): off.append(f"{k}: {per} g je Einheit außerhalb {PER[k]}")
    ck("alle Zutatenwerte liegen in üblichen Tabellenbereichen", not off, off)

    # 3. Kalorien-Rechner: Tabellen plausibel
    ex = pg.evaluate("""() => { const o = [];
      CEXTRA.forEach(x => { if (x[3] * 4 > x[2] * 1.05 + 5) o.push('CEXTRA ' + x[1] + ': ' + x[3] + ' g Eiweiß bei ' + x[2] + ' kcal'); if (x[2] > 900 || x[2] < 0 || x[3] < 0 || x[3] > 100) o.push('CEXTRA ' + x[1] + ' unmöglich'); });
      CDISH.forEach(x => { const k = x[2], p = x[3]; if (p * 4 > k * 1.05 + 5) o.push('CDISH ' + x[1] + ': ' + p + ' g Eiweiß bei ' + k + ' kcal'); });
      return { o, nx: CEXTRA.length, nd: CDISH.length }; }""")
    ck(f"Rechner: {ex['nx']} Lebensmittel und {ex['nd']} Gerichte ohne unmögliche Werte", not ex["o"], ex["o"][:5])

    # 4. Hygiene: rohes Fleisch nur mit Garhinweis
    hy = pg.evaluate("""(MEAT) => RECIPES.filter(r => r.ing.some(i => MEAT.includes(i[4])) && !r.steps.some(s => /rosa|durch|Packungsanleitung|gar /i.test(s))).map(r => r.id)""", MEAT)
    ck("Rezepte mit rohem Fleisch nennen, wann es gar ist", not hy, hy[:5])
    hy2 = pg.evaluate("""() => RECIPES.filter(r => /Ei\\b|Eier/.test(r.ing.map(i => i[2]).join(' ')) && /Overnight/.test(r.title)).length""")

    # 5. Hinweis zu Rohgewicht im Rezept und im Rechner
    pg.evaluate("openRecipe('haehnchen-curry-kokos-pfanne-mit-reis')"); pg.wait_for_timeout(200)
    ck("Rezept zeigt den Hinweis zu Rohgewicht", "roh gewogen" in pg.inner_text("#dlg-recipe"))
    pg.evaluate("closeDialog(document.querySelector('#dlg-recipe'))")
    r = pg.evaluate("() => { const x = cParse('200 g Hähnchenbrust'); const y = cParse('200 g gebratene Hähnchenbrust'); return [Math.round(x[0].p), x[0].note, Math.round(y[0].p), y[0].note]; }")
    ck("200 g rohes Hähnchen = 45 g Eiweiß, mit Hinweis", r[0] in (44, 45) and "roh" in r[1], r)
    ck("200 g gegartes Hähnchen = rund 58 bis 60 g Eiweiß", 56 <= r[2] <= 62, r)

    print("Fehler:", errs); ck("keine Fehler", not errs)
    b.close()
print("FAILS", fails)
