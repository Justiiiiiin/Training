"""Krankmeldung: Heute zeigt die Krank-Karte, Serie bleibt bei 3 Krankheitstagen, kaputte Daten werden bereinigt."""
import sys, time
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fcenv import APP_URL
from playwright.sync_api import sync_playwright
fails = []
def ck(n, ok, info=""):
    print(("OK   " if ok else "FAIL ") + n, "" if ok else info)
    if not ok: fails.append(n)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_context(viewport={"width": 390, "height": 844}).new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script("localStorage.getItem('fc_goals')||0; if(!localStorage.getItem('fc__t')){localStorage.setItem('fc__t','1');localStorage.setItem('fc_goals',JSON.stringify({kcal:1900,sick:{'bad':1,'2026-01-01':'x'}}))}")
    pg.goto(APP_URL)
    for _ in range(80):
        if pg.evaluate("window.__fcReady===true"): break
        time.sleep(0.15)
    ck("S0 kaputte Einträge bereinigt", pg.evaluate("JSON.stringify(GOALS.sick)") == '{"2026-01-01":1}', pg.evaluate("JSON.stringify(GOALS.sick)"))
    pg.evaluate("showTab('heute')")
    pg.click('[data-sick="1"]'); pg.wait_for_timeout(300)
    ck("S1 Krank-Karte", "krankgemeldet" in pg.inner_text("#panel-heute"))
    ck("S1 kein Training starten", pg.locator('#panel-heute [data-act="start"]').count() == 0)
    ck("S1 gespeichert", pg.evaluate("isSick()"))
    pg.click('[data-sick="0"]'); pg.wait_for_timeout(300)
    ck("S2 wieder fit", not pg.evaluate("isSick()") and "krankgemeldet" not in pg.inner_text("#panel-heute"))
    pg.evaluate("document.querySelector('.sickmore').open=true"); pg.wait_for_timeout(100)
    y = pg.evaluate("shiftDay(todayISO(),-1)")
    pg.click('[data-sickday="%s"]' % y); pg.wait_for_timeout(300)
    ck("S4 gestern krank, Liste bleibt offen", pg.evaluate("isSick(%r)" % y) and pg.evaluate("document.querySelector('.sickmore').open") and not pg.evaluate("isSick()"))
    pg.click('[data-sickday="%s"]' % y); pg.wait_for_timeout(300)
    ck("S4 wieder abgewählt", not pg.evaluate("isSick(%r)" % y))
    # Serie: Vorwoche 2 Einheiten, davor Woche mit 3 Krankheitstagen, davor 2 Einheiten => 2
    r = pg.evaluate("""(()=>{const ws=weekStartISO(todayISO());const w1=shiftDay(ws,-7),w2=shiftDay(ws,-14),w3=shiftDay(ws,-21);
      sessions.length=0; sessions.push(w1,shiftDay(w1,2),w3,shiftDay(w3,2)); GOALS.sick={}; const a=weekStreak();
      [0,1,2].forEach(i=>GOALS.sick[shiftDay(w2,i)]=1); const b=weekStreak(); GOALS.sick={}; sessions.length=0; return [a,b]})()""")
    ck("S3 Serie ohne Krankheit bricht, mit Krankheit bleibt", r == [1, 2], r)
    ck("keine Fehler", not errs, errs)
    b.close()
print("FAILS", fails); sys.exit(1 if fails else 0)
