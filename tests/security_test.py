"""Sicherheit: Rahmen (Clickjacking), Projekt-URL, Zusammenführen mit __proto__, Schadtext im Speicher (XSS)."""
import functools, http.server, json, os, threading, time
from playwright.sync_api import sync_playwright
import fcenv
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)
def ready(pg):
    t = time.time()
    while time.time() - t < 20 and not pg.evaluate("window.__fcReady === true"): pg.wait_for_timeout(100)

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Q, directory=fcenv.ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:%d/" % srv.server_address[1]

P = "\"'><img src=x data-zz=1>ZZXSS"
seed = {
 "fc_diary": {"2026-11-19": {"items": [{"t": P, "k": 100, "p": 10, "c": 1, "m": P, "id": P}], "water": 0, "note": P}},
 "fc_log": [{"date": "2026-11-19", "weight": 80, "waist": 90, "note": P}],
 "fc_dishes": [{"id": P, "name": P, "k": 100, "p": 10, "w": 100}],
 "fc_sessions": [P], "fc_exc": [P], "fc_fav": [P], "fc_shop": {P: True}, "fc_chk": {P: True},
 "fc_settings": {"name": P, "alt": {P: P}, "ms": {P: P}, "gear": {P: True}},
 "fc_wk": [{"date": "2026-11-19", "min": 5, "sets": [{"ex": P, "lvl": 0, "set": 1, "reps": 5}]}],
 "fc_prep": {"week": P, "done": {P: True}, "main": [P], "b": P, "s": P},
 "fc_rad": {"meal": P}, "fc_goals": {"note": P, "kcal": 2000}, "fc_body": {"weight": 80, "name": P},
}
spy = """(()=>{const bad=(h)=>/<img src=x data-zz/.test(String(h));
 const d=Object.getOwnPropertyDescriptor(Element.prototype,'innerHTML');
 Object.defineProperty(Element.prototype,'innerHTML',{set(v){ if(bad(v)) (window.__hits=window.__hits||[]).push(String(v).slice(0,80)); d.set.call(this,v);}, get(){return d.get.call(this);}});
 const ia=Element.prototype.insertAdjacentHTML;
 Element.prototype.insertAdjacentHTML=function(p,h){ if(bad(h)) (window.__hits=window.__hits||[]).push(String(h).slice(0,80)); return ia.call(this,p,h); };})();"""

with sync_playwright() as p:
    b = p.chromium.launch()
    # 1) Clickjacking: im fremden Rahmen bleibt die Seite leer
    c = b.new_context(viewport={"width": 390, "height": 844}); pg = c.new_page()
    pg.route("**/outer.html", lambda r: r.fulfill(content_type="text/html", body='<iframe id="f" src="/index.html" style="width:390px;height:800px"></iframe>'))
    pg.goto(BASE + "outer.html"); pg.wait_for_timeout(1200)
    fr = pg.frame_locator("#f")
    disp = pg.evaluate("document.getElementById('f').contentDocument.documentElement.style.display")
    ck("Im Rahmen (iframe) wird nichts angezeigt", disp == "none", disp)
    pg.goto(BASE + "index.html"); ready(pg)
    ck("Direkt geöffnet wird die App angezeigt", pg.evaluate("getComputedStyle(document.documentElement).display") != "none")
    # 2) Projekt-URL nur *.supabase.co
    for u in ("https://evil.example.com", "https://x.supabase.co.evil.com", "http://x.supabase.co", "https://supabase.co@evil.com"):
        r = pg.evaluate("async (u) => { try { await FC.sbLogin(u, 'k', 'a@b.de', 'pw', false); return 'ok'; } catch (e) { return e.message; } }", u)
        ck("Projekt-URL abgelehnt: " + u, "Projekt-URL" in r, r[:60])
    # 3) Zusammenführen mit __proto__
    r = pg.evaluate("""() => { const o = JSON.parse(FC._merge('fc_settings', '{"a":0}', '{"a":2}', '{"__proto__":{"polluted":"yes"},"a":1}', true)); return [({}).polluted === undefined, o.polluted === undefined, Object.keys(o).join()]; }""")
    ck("__proto__ aus der Datenbank verseucht nichts", r[0] and r[1] and "__proto__" not in r[2], r)
    c.close()
    # 4) Schadtext in allen Speichern wird überall entschärft
    c = b.new_context(viewport={"width": 390, "height": 844})
    c.add_init_script("".join("try{localStorage.setItem(%s,%s)}catch(e){};" % (json.dumps(k), json.dumps(json.dumps(v))) for k, v in seed.items()))
    c.add_init_script(spy)
    pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
    pg.goto(BASE + "index.html"); ready(pg)
    for t in ["heute", "uebungen", "tipps", "ausblick", "rezepte", "rad", "vorkochen", "einkauf", "ernaehrung", "fortschritt", "pflege", "haare"]:
        pg.evaluate("t=>showTab(t)", t); pg.wait_for_timeout(120)
    ck("Schadtext: nirgends als HTML eingesetzt", pg.evaluate("window.__hits||[]") == [], pg.evaluate("window.__hits||[]"))
    ck("Schadtext: kein fremdes Element im DOM", pg.evaluate("document.querySelectorAll('img[src=x],[data-zz]').length") == 0)
    ck("Schadtext: erreicht die Seite nur als Text", pg.evaluate("document.body.innerHTML.includes('ZZXSS')"))
    ck("Schadtext: keine Skriptfehler", not errs, errs)
    c.close(); b.close()
srv.shutdown()
print("FAILS:", len(fails), fails)
raise SystemExit(1 if fails else 0)
