"""Sync-Konflikte: 3-Wege-Abgleich (Regeln) und zwei Geräte mit Offline-Phase gegen eine nachgebildete Supabase-Datenbank."""
import json, base64, time, threading
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(); pg.goto(URL); pg.wait_for_timeout(500)
    M = lambda k, bb, l, r, lw=False: json.loads(pg.evaluate("([k,b,l,r,lw]) => FC._merge(k, b, l, r, lw)", [k, None if bb is None else json.dumps(bb), json.dumps(l), json.dumps(r), lw]))
    # Tagebuch: zwei Geräte tragen am selben Tag etwas ein
    base = {"2026-11-03": {"items": [{"t": "Frühstück", "k": 300, "p": 20, "c": 1}], "water": 2}}
    l = {"2026-11-03": {"items": [{"t": "Frühstück", "k": 300, "p": 20, "c": 1}, {"t": "Apfel", "k": 80, "p": 0, "c": 0.3}], "water": 2}}
    r = {"2026-11-03": {"items": [{"t": "Frühstück", "k": 300, "p": 20, "c": 1}, {"t": "Quark", "k": 150, "p": 25, "c": 0.8}], "water": 4}}
    m = M("fc_diary", base, l, r)
    ck("Tagebuch: Einträge beider Geräte bleiben", [x["t"] for x in m["2026-11-03"]["items"]] == ["Frühstück", "Quark", "Apfel"], str(m))
    ck("Tagebuch: Wasser vom Gerät, das es geändert hat", m["2026-11-03"]["water"] == 4)
    # Löschen auf einem Gerät, Hinzufügen auf dem anderen
    l2 = {"2026-11-03": {"items": [], "water": 2}}
    m = M("fc_diary", base, l2, r)
    ck("Tagebuch: Löschen bleibt gelöscht, neuer Eintrag kommt dazu", [x["t"] for x in m["2026-11-03"]["items"]] == ["Quark"], str(m))
    # Gleiches Essen zweimal am Tag (Multimenge)
    two = {"2026-11-03": {"items": [{"t": "Apfel", "k": 80, "p": 0}, {"t": "Apfel", "k": 80, "p": 0}], "water": 0}}
    m = M("fc_diary", {"2026-11-03": {"items": [{"t": "Apfel", "k": 80, "p": 0}], "water": 0}}, two, {"2026-11-03": {"items": [{"t": "Apfel", "k": 80, "p": 0}], "water": 0}})
    ck("Tagebuch: doppelte Einträge bleiben doppelt", len(m["2026-11-03"]["items"]) == 2)
    # Verschiedene Tage
    m = M("fc_diary", {}, {"2026-11-02": {"items": [], "water": 1}}, {"2026-11-03": {"items": [], "water": 3}})
    ck("Tagebuch: Tage beider Geräte", sorted(m) == ["2026-11-02", "2026-11-03"])
    # Trainingstage und Trainings (Datum sortiert)
    m = M("fc_sessions", ["2026-11-01"], ["2026-11-01", "2026-11-05"], ["2026-11-01", "2026-11-03"])
    ck("Trainingstage vereint und sortiert", m == ["2026-11-01", "2026-11-03", "2026-11-05"], str(m))
    wk = lambda d, mi: {"date": d, "min": mi, "sets": [], "effort": "", "q": 0}
    m = M("fc_wk", [wk("2026-11-01", 30)], [wk("2026-11-01", 30), wk("2026-11-05", 25)], [wk("2026-11-01", 30), wk("2026-11-03", 28)])
    ck("Trainings vereint, chronologisch", [x["date"] for x in m] == ["2026-11-01", "2026-11-03", "2026-11-05"])
    # Messwerte: pro Datum, Felder zusammenführen
    m = M("fc_log", [{"date": "2026-11-01", "weight": 80}], [{"date": "2026-11-01", "weight": 80, "waist": 90}], [{"date": "2026-11-01", "weight": 79.5}])
    ck("Messwerte: ein Eintrag pro Datum, beide Felder", m == [{"date": "2026-11-01", "weight": 79.5, "waist": 90}], str(m))
    # Warenkorb nach Rezept-ID
    m = M("fc_cart", [{"id": "a", "n": 1}], [{"id": "a", "n": 3}], [{"id": "a", "n": 1}, {"id": "b", "n": 2}])
    ck("Warenkorb: Menge geändert und neues Rezept", sorted((x["id"], x["n"]) for x in m) == [("a", 3), ("b", 2)], str(m))
    # Einstellungen: Feld für Feld, Widerspruch nach Zeit
    m = M("fc_settings", {"sets": 2, "rest": 90}, {"sets": 3, "rest": 90}, {"sets": 2, "rest": 60})
    ck("Einstellungen: beide Änderungen", m == {"sets": 3, "rest": 60}, str(m))
    ck("Widerspruch: neuere Datenbank gewinnt", M("fc_settings", {"sets": 2}, {"sets": 3}, {"sets": 4}, False)["sets"] == 4)
    ck("Widerspruch: neueres Gerät gewinnt", M("fc_settings", {"sets": 2}, {"sets": 3}, {"sets": 4}, True)["sets"] == 3)
    ck("Trainingstage-Raster positionsweise", M("fc_settings", {"tdays": [1, 0, 1, 0, 1, 0, 0]}, {"tdays": [1, 1, 1, 0, 1, 0, 0]}, {"tdays": [1, 0, 1, 0, 1, 0, 1]})["tdays"] == [1, 1, 1, 0, 1, 0, 1])
    ck("ohne gemeinsamen Stand: nichts geht verloren", M("fc_sessions", None, ["2026-11-01"], ["2026-11-02"]) == ["2026-11-01", "2026-11-02"])
    pg.close()

    # ---------- zwei Geräte gegen eine nachgebildete Datenbank ----------
    DB = {}; LOCK = threading.Lock(); OFF = {"A": False, "B": False}
    UID = "11111111-2222-3333-4444-555555555555"
    def b64(o): return base64.urlsafe_b64encode(json.dumps(o).encode()).decode().rstrip("=")
    JWT = b64({"alg": "HS256"}) + "." + b64({"sub": UID}) + ".sig"
    SB = "https://beispiel.supabase.co"
    def device(name):
        c = b.new_context(viewport={"width": 390, "height": 844})
        def route(rt):
            u, meth = rt.request.url, rt.request.method
            if OFF[name]: return rt.abort("internetdisconnected")
            if "/auth/v1/token" in u: return rt.fulfill(status=200, content_type="application/json", body=json.dumps({"access_token": JWT, "refresh_token": "rt", "expires_in": 3600}))
            if "/rest/v1/kv" in u and meth == "GET":
                with LOCK: rows = list(DB.values())
                return rt.fulfill(status=200, content_type="application/json", body=json.dumps(rows))
            if "/rest/v1/kv" in u and meth == "POST":
                with LOCK:
                    for row in json.loads(rt.request.post_data): DB[row["k"]] = row
                return rt.fulfill(status=201, body="")
            return rt.fulfill(status=404, body="")
        c.route(SB + "/**", route)
        cfg = {"url": SB, "key": "anon", "email": "a@b.de", "rt": "rt", "at": JWT, "exp": int(time.time() * 1000) + 3600000}
        c.add_init_script("if (!localStorage.getItem('fc__sb')) localStorage.setItem('fc__sb', %s);" % json.dumps(json.dumps(cfg)))
        pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(1500)
        return pg, errs
    A, ea = device("A")
    A.evaluate("() => { logEat(RECIPES[0], 1); sessions.push('2026-11-01'); store.set('fc_sessions', sessions); }"); A.wait_for_timeout(2500)
    ck("A hat hochgeladen", "fc_diary" in DB and "fc_sessions" in DB, str(sorted(DB)))
    B, eb = device("B")
    ck("B hat A's Eintrag", B.evaluate("dayGet().items.length") == 1)
    # A geht offline und trägt etwas ein, B trägt online etwas anderes ein
    OFF["A"] = True
    A.evaluate("() => { logEat(RECIPES[1], 1); sessions.push('2026-11-02'); store.set('fc_sessions', sessions); }"); A.wait_for_timeout(2000)
    B.evaluate("() => { logEat(RECIPES[2], 1); sessions.push('2026-11-03'); store.set('fc_sessions', sessions); }"); B.wait_for_timeout(2500)
    ck("A ist offline", A.evaluate("FC.state()") == "offline", A.evaluate("FC.state()"))
    OFF["A"] = False
    A.evaluate("window.dispatchEvent(new Event('online'))"); A.wait_for_timeout(3000)
    diary = json.loads(DB["fc_diary"]["v"]); day = list(diary.values())[0]
    titles = sorted(x["t"] for x in day["items"])
    want = sorted(A.evaluate("[RECIPES[0].title, RECIPES[1].title, RECIPES[2].title]"))
    ck("Datenbank: Einträge beider Geräte", titles == want, str(titles))
    ck("Datenbank: Trainingstage beider Geräte", json.loads(DB["fc_sessions"]["v"]) == ["2026-11-01", "2026-11-02", "2026-11-03"], DB["fc_sessions"]["v"])
    A.reload(); A.wait_for_timeout(1500)
    ck("A nach Neuladen: alle drei Einträge", A.evaluate("dayGet().items.length") == 3)
    B.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); B.wait_for_timeout(1500); B.reload(); B.wait_for_timeout(1500)
    ck("B nach Abgleich: alle drei Einträge", B.evaluate("dayGet().items.length") == 3)
    # Die App schreibt nach einem Sync aus ihrem alten Speicherstand: nichts darf verloren gehen
    with LOCK:
        d = json.loads(DB["fc_diary"]["v"]); k = list(d)[0]; d[k]["items"].append({"t": "Von außen", "k": 10, "p": 1, "c": 0})
        DB["fc_diary"] = {"k": "fc_diary", "t": int(time.time() * 1000) + 5000, "v": json.dumps(d)}
    A.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); A.wait_for_timeout(800)
    A.evaluate("() => { const day = dayEns(); day.water += 1; saveToday(); }"); A.wait_for_timeout(2500)
    d = json.loads(DB["fc_diary"]["v"]); day = list(d.values())[0]
    ck("Alter App-Stand überschreibt neuen Sync-Stand nicht", any(x["t"] == "Von außen" for x in day["items"]) and day["water"] >= 1, str([x["t"] for x in day["items"]]))
    ck("keine Fehler", not ea and not eb, str(ea[:2] + eb[:2]))
    b.close()
print("FAILS", fails)
