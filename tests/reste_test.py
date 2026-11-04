"""Reste im Wochenplan (Glücksrad): Eine angebrochene Packung (z. B. 200 g von 500 g Magerquark am Montag) bekommt ein späteres Gericht innerhalb der Haltbarkeit, das den Rest verbraucht."""
import json, time
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

def wait_ready(pg, ms=20000):
    t = time.time()
    while time.time() - t < ms / 1000:
        if pg.evaluate("window.__fcReady === true"): return True
        pg.wait_for_timeout(100)
    return False

SETUP = """() => {
  window.__seed = (a) => () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const base = RECIPES.find((r) => r.meal === 'Mittag/Abend' && r.tags.includes('Günstig') && !hasSpin(r) && !isExc(r));
  const mk = (id, ing) => { const r = JSON.parse(JSON.stringify(base)); r.id = id; r.title = id; r.ing = ing; return r; };
  window.__F = mk('t-fill', [[80, 'g', 'Vollkornnudeln (Rohgewicht)', null, 'nudel']]);
  window.__Q1 = mk('t-q1', [[100, 'g', 'Magerquark', null, 'quark']]);   // 2 Personen: 200 g
  RECIPES.push(window.__F, window.__Q1);
  RAD.mode = 'week'; RAD.people = 2; RAD.reste = true; RAD.cheap = true; RAD.noSpinat = true; RAD.maxDay = 0;
  window.__plan = (lockDays) => ({ days: DAYN.map((n, i) => ({ name: n, slots: [{ label: 'Abendessen', k: 'Mittag/Abend', work: false, id: i === 0 ? 't-q1' : 't-fill', locked: !!(lockDays && lockDays.includes(i)) }] })) });
  window.__q = (plan) => restChains(plan).filter((c) => c.k === 'quark').map((c) => ({ day: c.day, left: c.left, uses: c.uses.map((u) => [u.d, u.s, Math.round(u.amt), u.from]) }));
  return base.id;
}"""

with sync_playwright() as p:
    b = p.chromium.launch(); c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e))); pg.on("console", lambda m: m.type == "error" and errs.append(m.text))
    pg.goto(fcenv.APP_URL); ck("Start läuft durch", wait_ready(pg))
    pg.evaluate(SETUP)

    # 1) Dein Beispiel: Montag 200 g von 500 g Magerquark, Rest 300 g
    ch = pg.evaluate("() => __q(__plan())")
    ck("Montag: eine Packung, 200 g verbraucht, 300 g Rest", len(ch) == 1 and ch[0]["day"] == 0 and round(ch[0]["left"]) == 300, ch)

    # 2) Der Plan sucht ein Folgegericht innerhalb der Haltbarkeit (Quark: 4 Tage offen, also bis Freitag)
    res = pg.evaluate("""() => { const out = []; for (let s = 1; s <= 30; s++) { Math.random = __seed(s); const pl = __plan(); const before = planWaste(pl); radReste(pl); const after = planWaste(pl);
      const ch = __q(pl)[0]; const later = ch ? ch.uses.filter((u) => u[3]).map((u) => u[0]) : [];
      out.push({ before, after, later, sat: pl.days.slice(5).some((d) => d.slots[0].id.startsWith('t-q') ) }); } return out; }""")
    ck("Folgegericht gefunden (alle 30 Würfe)", all(len(r["later"]) >= 1 for r in res), [r["later"] for r in res][:6])
    ck("Folgegericht liegt zwischen Dienstag und Freitag", all(all(1 <= d <= 4 for d in r["later"]) for r in res), sorted({d for r in res for d in r["later"]}))
    ck("Verschwendung sinkt", all(r["after"] < r["before"] - 0.05 for r in res), (round(res[0]["before"], 2), round(res[0]["after"], 2)))
    ck("Samstag und Sonntag bleiben unverändert", not any(r["sat"] for r in res))

    # 3) Fixierte Plätze bleiben, außerhalb der Haltbarkeit wird nichts eingesetzt
    r = pg.evaluate("""() => { Math.random = __seed(5); const pl = __plan([1, 2, 3, 4]); const ids = pl.days.map((d) => d.slots[0].id); radReste(pl); return { same: pl.days.every((d, i) => d.slots[0].id === ids[i]) }; }""")
    ck("Fixierte Tage (Di bis Fr) bleiben, Sa und So liegen außerhalb der Haltbarkeit", r["same"], r)

    # 4) Hinweise im Plan: Montag nennt den Rest und den Tag, das Folgegericht nennt den Montag
    r = pg.evaluate("""() => { Math.random = __seed(7); const pl = __plan(); radReste(pl); const n = restNotes(pl); const ch = __q(pl)[0]; const u = ch.uses.find((x) => x[3]);
      return { mon: n['0:0'] || [], fol: n[u[0] + ':0'] || [], day: DAYN[u[0]] }; }""")
    ck("Hinweis am Montag: Rest und Folgetag", r["mon"] and "Magerquark 200 g von 500 g" in r["mon"][0] and r["day"] in r["mon"][0], r["mon"])
    ck("Hinweis am Folgetag: Rest von Montag wird verbraucht", r["fol"] and "von Montag" in r["fol"][0] and "verbraucht" in r["fol"][0], r["fol"])

    # 5) Ohne die Option passiert nichts
    r = pg.evaluate("""() => { RAD.reste = false; const pl = __plan(); const ids = pl.days.map((d) => d.slots[0].id); radReste(pl); const same = pl.days.every((d, i) => d.slots[0].id === ids[i]); const notes = Object.keys(restNotes(pl)).length; RAD.reste = true; return { same, notes }; }""")
    ck("Reste verwerten aus: Plan bleibt, keine Hinweise", r["same"] and r["notes"] == 0, r)

    # 6) Echte Wochenpläne: weniger Reste, Eiweißziel nicht schlechter, schnell genug
    r = pg.evaluate("""() => { const run = (on) => { RAD.reste = on; let w = 0, good = 0, days = 0, ms = 0; for (let s = 1; s <= 40; s++) { Math.random = __seed(1000 + s); const t = performance.now(); const pl = radBuild(null); ms += performance.now() - t;
        w += planWaste(pl); pl.days.forEach((d) => { days++; if (dayScore(d.slots.map((y) => byId(y.id))) === 0) good++; }); } return { w, good: good / days, ms: ms / 40 }; };
      const a = run(false), b = run(true); RAD.reste = true; return { a, b }; }""")
    ck("Wochenpläne: Reste-Wert sinkt deutlich", r["b"]["w"] < r["a"]["w"] * 0.85, "ohne %.2f, mit %.2f" % (r["a"]["w"], r["b"]["w"]))
    ck("Wochenpläne: Tage mit erreichtem Ziel nicht schlechter", r["b"]["good"] >= r["a"]["good"] - 0.01, "%.3f gegen %.3f" % (r["b"]["good"], r["a"]["good"]))
    ck("Wochenplan wird schnell gebaut (unter 300 ms)", r["b"]["ms"] < 300, "%.0f ms" % r["b"]["ms"])

    # 7) Anzeige: Hinweise erscheinen im Plan, nichts läuft über
    n = pg.evaluate("""() => { let cnt = 0, over = 0; for (let s = 1; s <= 12; s++) { Math.random = __seed(50 + s); RPL.week = radBuild(null); rad.shown = new Set(); RPL.week.days.forEach((d, di) => d.slots.forEach((y, yi) => rad.shown.add(di + ':' + yi))); radRender(); cnt += document.querySelectorAll('#radres .rrest').length; if (document.documentElement.scrollWidth > innerWidth + 1) over++; } return { cnt, over }; }""")
    ck("Hinweise im Plan sichtbar", n["cnt"] > 0, n)
    ck("kein seitlicher Überlauf", n["over"] == 0, n)

    # 8) Chip „Reste verwerten“ ist da und schaltet um
    pg.evaluate("() => { RAD.mode = 'week'; showTab('rad', true); renderRadOpts(); }")
    ck("Chip Reste verwerten vorhanden", pg.is_visible("[data-ropt=reste]"))
    on0 = pg.evaluate("RAD.reste"); pg.click("[data-ropt=reste]"); on1 = pg.evaluate("RAD.reste")
    ck("Chip schaltet um", on0 is True and on1 is False, (on0, on1))
    ck("keine JS-Fehler", not errs, errs[:2])
    c.close(); b.close()
print("FAILS", fails)
