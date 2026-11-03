# Fitness Coach: Hinweise für Claude Code

Persönliche Fitness- und Ernährungs-App für Einsteiger, Deutsch (Du-Form, einfache Sprache). Läuft als Webseite (`index.html` mit `styles.css` und `js/`) auf GitHub Pages und wird auf dem iPhone als Home-Bildschirm-App benutzt.
Live: https://justiiiiiin.github.io/Training/

## Aufbau

- Im Kopf von `index.html` steht eine Content-Security-Policy (nur Skripte von hier, Verbindungen nur hierher und zu `*.supabase.co`). Deshalb keine Inline-Skripte und keine `on…`-Attribute verwenden, Ereignisse per `addEventListener`.
- `js/zoom.js` (erstes Skript im Kopf) sperrt Pinch- und Doppeltipp-Zoom sofort beim Laden, auch auf iOS und als Home-Bildschirm-App (Gesten- und Touch-Ereignisse; Android über `touch-action` in `styles.css`). Eingabefelder brauchen mindestens 16 px, sonst zoomt iOS beim Antippen. Größere Schrift gibt es über Einstellungen > Textgröße.
- `index.html`: nur HTML, keine Inline-Skripte. `styles.css`: das gesamte CSS (inkl. `@font-face` für `fonts/`).
- `js/`: klassische Skripte, die sich den globalen Bereich teilen. `sync.js` und `boot.js` stehen am Ende von `index.html`. `boot.js` lädt nach dem ersten Abgleich der Reihe nach `data.js` (Übungen, Rezepte, Preise, Tipps), `app.js` (Zustand, Oberfläche, Logik), `v3.js` (3D-Ansicht) und `start.js` (Start, setzt `window.__fcReady`), jeweils mit `?v=<Versionslabel>`.
- Der Sync-Block (`js/sync.js`, `window.FC`): Speicher über localStorage, optional Supabase (Tabelle `kv`). Schema und Row-Level-Security der Tabelle stehen in `docs/supabase.sql`.
- `sw.js`: Service Worker (Netz zuerst, Offline-Rückfall, Cache `fc-offline-v3`). Neue Dateien gehören in seine Liste `FILES`. `manifest.webmanifest` und die Icons gehören zur Installation auf dem Home-Bildschirm.
- Daten in `js/data.js`: `RECIPES` (300 Rezepte), `DAYS`, `PRICE` (Lidl-Richtwerte) werden aus `tools/recipes/` eingesetzt. Übungen: `EX`, `EXALT`, `EXFUT`, `GEAR`. 3D-Animationen: `V3A`.
- Wichtige Stellen: `sanitizeState()` (prüft alle gespeicherten Daten), `showTab()`/`GROUPS`/`TABN` (Navigation), `renderEx`, `renderAusblick`, `prepCalc`/`prepGen` (Vorkochen), `shopCalc` (Einkaufsliste), `buyEstimate` (Ausgaben), `cParse` (Kalorien-Rechner mit `CEXTRA`, `CDISH`).
- Gespeichert wird alles in localStorage-Schlüsseln `fc_*` (zum Beispiel `fc_settings`, `fc_diary`, `fc_goals`). Ändere nie ihre Bedeutung, ohne `sanitizeState` mitzuziehen.

## Befehle

```bash
pip install -r tests/requirements.txt && python3 -m playwright install chromium
bash tests/run_all.sh                 # alle Tests, parallel, mit Zusammenfassung
python3 tests/calc_test.py            # ein einzelner Test
python3 tools/stamp.py                # Versionslabel hochzählen (v3.N · Datum), nur beim Veröffentlichen
```

Syntaxcheck (der zweite Befehl findet doppelte Namen über Dateigrenzen hinweg):

```bash
for f in js/*.js sw.js; do node --check "$f"; done
cat js/data.js js/app.js js/v3.js js/start.js > /tmp/all.js && node --check /tmp/all.js
```

Rezepte ändern: `tools/recipes/build.py` bearbeiten, dann `python3 tools/recipes/build.py` (prüft Kalorien, Eiweiß, Vielfalt, schreibt die JSON-Dateien) und `python3 tools/recipes/inject.py` (setzt sie in `js/data.js` ein).

## Tests

Alle Tests laufen mit Playwright (Chromium) gegen `index.html`, ohne Server, außer `pwa_test.py` (lokaler Server). Pfade kommen aus `tests/fcenv.py`. Mit `FC_URL` oder `FC_APP_DIR` lässt sich eine andere Version prüfen. Der Audit `audit2.py` geht alle Tabs durch (Überlauf, Kontrast, Tap-Ziele) und dauert länger.
`update_test.py` und `swupdate_test.py` (Update-Banner und Service Worker) fehlen hier, weil sie handgebaute Fixtures brauchen.
Bekannte Eigenheit: `Overnight Oats (dein Rezept)` hat 845 kcal und wird von `build.py` absichtlich als Ausnahme gemeldet.

## Fallstricke

- Der Code läuft von oben nach unten, Datei für Datei. Top-level-`const` und `let` müssen vor ihrer ersten Benutzung stehen, auch indirekt über Funktionen, die beim Start laufen (`sanitizeState` läuft mitten in `app.js`). Funktionen aus einer späteren Datei gibt es beim Laden einer früheren noch nicht. Doppelte Namen fallen mit dem zusammengefügten `node --check` auf.
- Im Rechner (`cParse`) prüft `CDISH` (Gerichte) vor `CFOODS` (Zutaten), und ein einzelnes Wort in `CDISH` trifft auch als Teil eines längeren Wortes. Nimm dort nur eindeutige oder mehrwortige Schlüssel.
- Beim Hinzufügen von Übungen ohne 3D-Animation (`V3A`) muss die Oberfläche das berücksichtigen (siehe `techBtn`, `coachFig`).
- `index.html` wird bei Veröffentlichung nur durch `tools/stamp.py` versioniert. Das Label steht in `#appver`, der Update-Check vergleicht es, und `boot.js` hängt es an die Skript-Adressen (frischer Cache nach Updates).
- Texte stehen auf Deutsch mit echten Umlauten. Keine langen Gedankenstriche in Texten.

## So bitte arbeiten

- Verhalten nicht verändern, wenn es nur um eine Prüfung geht. Erst die Funde nach Schwere auflisten, dann in kleinen Commits beheben, nach jedem Schritt `bash tests/run_all.sh`.
- Keine neuen Abhängigkeiten, Build-Schritte oder Aufteilung der Datei ohne Rückfrage.
- Veröffentlichen direkt auf `main` (committen und pushen, kein Pull Request): GitHub Pages veröffentlicht von `main`. Ändert sich die App selbst, vorher `python3 tools/stamp.py`, sonst meldet die App kein Update.
- Die App ist öffentlich auf GitHub Pages. Keine Zugangsdaten, Schlüssel oder persönlichen Daten ins Repo.

## Was ich besonders prüfen lassen möchte

1. Sicherheit: Viele Stellen setzen HTML per `innerHTML` ein. Wo kommen Daten aus Speicher, Import oder Sync, und sind sie überall mit `esc()` oder `sanitizeState` abgesichert?
2. Sync: Wo liegen Supabase-URL und Schlüssel (localStorage `fc__sb`, nicht im Code)? Ist die Tabelle `kv` per Row-Level-Security geschützt? Was passiert bei Konflikten und Offline-Betrieb?
3. Fehlerbehandlung: Was passiert bei kaputten oder fehlenden gespeicherten Daten, vollem Speicher oder gesperrtem localStorage?
4. Zugänglichkeit und Bedienung auf dem Handy (Tap-Ziele, Fokus, Kontrast, Zoom-Sperre, Safe-Area).
5. Leistung: Start, Rendern der Rezepte, Animationen.
6. Doppelte oder tote Codeteile und widersprüchliche Daten (Zutaten, Preise, Rezepte).
7. Was sich in der Datei sauber trennen ließe, ohne das Verhalten zu ändern. Nur als Vorschlag.

Nicht prüfbar ohne echtes Gerät: iOS-Verhalten (Safe-Area, Teilen-Menü, Kalender-Import, Update-Banner im installierten Zustand). Das testet der Besitzer selbst.
