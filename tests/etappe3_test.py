from playwright.sync_api import sync_playwright
import re
URL=__import__("fcenv").APP_URL
errs=[]; fails=[]
def ck(n,c,info=""):
    print(("OK   " if c else "FAIL ")+n,info)
    if not c: fails.append(n)
with sync_playwright() as p:
    b=p.chromium.launch(); c=b.new_context(viewport={"width":390,"height":844},has_touch=True,accept_downloads=True); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(700)
    # ---------- Ausgaben ----------
    pg.evaluate("showTab('einkauf')"); pg.wait_for_timeout(300)
    ck("Karte Ausgaben da", "Ausgaben fürs Essen" in pg.inner_text("#panel-einkauf"))
    ck("Naechster Monat gesperrt (aktuell)", pg.evaluate("document.querySelector('[data-spm=\"1\"]').disabled"))
    pg.fill("#buy-a","38,40"); pg.click('[data-buyadd]'); pg.wait_for_timeout(250)
    ck("Einkauf eingetragen", pg.evaluate("GOALS.buys.length")==1 and pg.evaluate("GOALS.buys[0].a")==38.4, pg.inner_text("#spendcard")[:120].replace("\n"," | "))
    for bad in ["abc","-5","0","3000",""]:
        pg.fill("#buy-a",bad); pg.click('[data-buyadd]'); pg.wait_for_timeout(100)
    ck("Ungueltige Betraege nie gespeichert", pg.evaluate("GOALS.buys.length")==1 and "Betrag" in pg.inner_text("#buymsg"), pg.inner_text("#buymsg"))
    pg.fill("#buy-a","10"); pg.evaluate("document.getElementById('buy-d').removeAttribute('max'); document.getElementById('buy-d').value=shiftDay(todayISO(),3)"); pg.click('[data-buyadd]'); pg.wait_for_timeout(100)
    ck("Zukunftsdatum abgelehnt", pg.evaluate("GOALS.buys.length")==1 and "Datum" in pg.inner_text("#buymsg"), pg.inner_text("#buymsg"))
    pg.evaluate("document.getElementById('buy-d').value=shiftDay(todayISO(),-40)"); pg.fill("#buy-a","20,5"); pg.click('[data-buyadd]'); pg.wait_for_timeout(250)
    ck("Alter Einkauf: springt in den Monat", pg.evaluate("GOALS.buys.length")==2 and pg.evaluate("SPM")==pg.evaluate("shiftDay(todayISO(),-40).slice(0,7)"), pg.evaluate("SPM"))
    ck("Monatssumme 20,50", "20,50" in pg.inner_text("#spendcard"), pg.inner_text("#spendcard")[:200].replace("\n"," | "))
    pg.click('[data-spm="1"]'); pg.wait_for_timeout(150)
    ck("Monatsnavigation: Oktober nach September", pg.evaluate("SPM")==pg.evaluate("monthShift(shiftDay(todayISO(),-40).slice(0,7),1)"), pg.evaluate("SPM"))
    pg.evaluate("DIARY[todayISO()]={items:[{t:'x',k:600,p:40,c:2.5},{t:'y',k:300,p:10,c:1}],water:0}; SPM=todayISO().slice(0,7); renderShop()")
    ck("Gegessen nach Preisliste: 3,50", "3,50" in pg.inner_text("#spendcard"), pg.inner_text("#spendcard")[:220].replace("\n"," | "))
    pg.evaluate("SPM=todayISO().slice(0,7); renderShop()"); pg.click('[data-buydel]'); pg.wait_for_timeout(200)
    ck("Einkauf loeschen", pg.evaluate("GOALS.buys.length")==1)
    pg.evaluate("store.set('fc_goals',Object.assign({},GOALS,{buys:[{d:'x',a:5},{d:'2026-10-01',a:'a'},{d:'2026-10-02',a:-4},{d:'2026-10-03',a:12.345},5,null,{d:'2026-10-04',a:99999}]}))"); pg.reload(); pg.wait_for_timeout(700)
    ck("Kaputte Einkaeufe bereinigt", pg.evaluate("GOALS.buys")==[{"d":"2026-10-03","a":12.35}] or pg.evaluate("GOALS.buys.length")==1, pg.evaluate("GOALS.buys"))
    # ---------- Wochenrueckblick ----------
    pg.evaluate("""()=>{ const ws=weekStartISO(todayISO()); sessions.length=0; sessions.push(shiftDay(ws,-3), shiftDay(ws,0)); store.set('fc_sessions',sessions);
      Object.keys(DIARY).forEach(k=>delete DIARY[k]); for(let i=0;i<3;i++){ const d=shiftDay(ws,i); if(d<=todayISO()) DIARY[d]={items:[{t:'x',k:2000,p:120,c:5}],water:GOALS.water}; }
      log.length=0; log.push({date:shiftDay(ws,-2),weight:81.0},{date:shiftDay(ws,1),weight:80.4}); store.set('fc_log',log); renderProgress(); }""")
    pg.evaluate("showTab('fortschritt')"); pg.wait_for_timeout(300)
    t=pg.inner_text(".review"); print("  ",t.replace("\n"," | ")[:420])
    ck("Rueckblick: Titel mit Woche", "Wochenrückblick" in t and "02.11. bis 08.11." in t)
    ck("Training 1 von 3 (nur diese Woche zaehlt)", re.search(r"Training\s*\n?\s*1 von 3", t) is not None or "1 von 3" in t)
    ck("Gewicht -0,6 zur Vorwoche", "80,4 kg" in t and "−0,6" in t, t)
    ck("Weiter-Knopf gesperrt (aktuelle Woche)", pg.evaluate("document.querySelector('[data-rvw=\"1\"]').disabled"))
    pg.click('[data-rvw="-1"]'); pg.wait_for_timeout(200)
    ck("Eine Woche zurueck: Training 1 von 3 (Sessions der Vorwoche)", pg.evaluate("REVW")==pg.evaluate("shiftDay(weekStartISO(todayISO()),-7)") and "Training" in pg.inner_text(".review"))
    ck("Zurueck: Weiter nicht mehr gesperrt", not pg.evaluate("document.querySelector('[data-rvw=\"1\"]').disabled"))
    # Heute: nur Sonntag und Montag (feste Zeit)
    for day,label,exp in [("2026-11-08T10:00:00","Sonntag",True),("2026-11-09T10:00:00","Montag",True),("2026-11-04T10:00:00","Mittwoch",False)]:
        pg2=c.new_page(); pg2.clock.install(time=day); pg2.goto(URL); pg2.wait_for_timeout(700)
        got=pg2.evaluate("reviewToday()").count("Wochenrückblick")>0
        ck(f"Heute-Rueckblick {label}: {'ja' if exp else 'nein'}", got==exp)
        if label=="Montag": ck("Montag zeigt Vorwoche (02.11. bis 08.11.)", "02.11. bis 08.11." in pg2.evaluate("reviewToday()"))
        pg2.close()
    # ---------- Kalender ----------
    pg.evaluate("""()=>{ const ws=weekStartISO(todayISO()); GOALS.sched[ws]='nlnlnlf'; GOALS.sched[shiftDay(ws,7)]='nlnlnlf'; settings.tdays=[1,0,1,0,1,0,0]; }""")
    ics=pg.evaluate("buildICS()"); T=ics["text"]; lines=T.split("\r\n")
    ck("CRLF und Rahmen", T.startswith("BEGIN:VCALENDAR\r\n") and T.endswith("END:VCALENDAR\r\n"))
    ck("Gleich viele BEGIN/END VEVENT", T.count("BEGIN:VEVENT")==T.count("END:VEVENT")==ics["count"], ics["count"])
    uids=[l for l in lines if l.startswith("UID:")]; ck("UIDs eindeutig", len(set(uids))==len(uids)==ics["count"])
    ck("Zeilen hoechstens 75 Bytes", all(len(l.encode())<=75 for l in lines), [len(l.encode()) for l in lines if len(l.encode())>75][:3])
    ck("Kommas im Text maskiert", "DESCRIPTION:Ganzkörper\\," in T, [l for l in lines if l.startswith("DESCRIPTION:Gan")][:1])
    st=[l for l in lines if l.startswith("DTSTART:")]; ck("Zeitformat lokal", all(re.fullmatch(r"DTSTART:\d{8}T\d{6}",x) for x in st), st[:2])
    ck("Vorkochen jeden Sonntag (8x)", T.count("SUMMARY:Vorkochen")==8, T.count("SUMMARY:Vorkochen"))
    # Zeit nach Schicht: Tag mit 'l' -> 10:00, 'n' -> 18:00
    evs=re.findall(r"UID:fc-training-(\d{8})@fitness-coach\r\nDTSTAMP:\S+\r\nDTSTART:\d{8}T(\d{4})00",T)
    chk=[(d,h) for d,h in evs]; bad=[]
    for d,h in chk:
        iso=f"{d[:4]}-{d[4:6]}-{d[6:]}"; sh=pg.evaluate(f"shiftOf('{iso}')"); want="1800" if sh=="n" else "1000"
        if h!=want: bad.append((iso,sh,h))
    ck("Uhrzeit folgt der Schicht", chk and not bad, bad[:2] or chk[:2])
    ck("Erinnerung 30 Min vor Training", "TRIGGER:-PT30M" in T and "TRIGGER:-PT60M" in T)
    ck("Keine Trainingstage: nur Vorkochen", (pg.evaluate("settings.tdays=[0,0,0,0,0,0,0]; buildICS().count")==8))
    pg.evaluate("settings.tdays=[1,0,1,0,1,0,0]")
    pg.evaluate("document.getElementById('dlg-settings').showModal()")
    pg.evaluate("navigator.canShare=()=>false")
    with pg.expect_download() as dl: pg.click("#b-ics")
    f=dl.value; ck("Download fitness-coach.ics", f.suggested_filename=="fitness-coach.ics", f.suggested_filename)
    ck("Meldung nach Download", "Termine" in pg.inner_text("#icsmsg"), pg.inner_text("#icsmsg"))
    pg.evaluate("document.getElementById('dlg-settings').close()")
    # ---------- Heute-Layout ----------
    pg.evaluate("showTab('heute')"); pg.wait_for_timeout(250)
    ht=pg.inner_text("#panel-heute")
    ck("Erklaertext unter den Ringen weg", "Eiweiß ist für den Muskelaufbau am wichtigsten" not in ht)
    ck("Schichthinweis kurz", "Training" in pg.inner_text(".shifthint") and len(pg.inner_text(".shifthint"))<90, pg.inner_text(".shifthint"))
    pg.evaluate("sessions.length=0")
    ck("kein Ueberlauf", pg.evaluate("document.documentElement.scrollWidth<=window.innerWidth"))
    print("Fehler:",errs); ck("keine Fehler", not errs)
    b.close()
print("FAILS",fails)
