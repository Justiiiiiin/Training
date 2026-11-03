# Fitness Coach: Hinweise für Claude Code

Persönliche Fitness- und Ernährungs-App für Einsteiger, Deutsch (Du-Form, einfache Sprache). Läuft als einzelne Webseite (`index.html`, ca. 740 KB) auf GitHub Pages und wird auf dem iPhone als Home-Bildschirm-App benutzt. Ausprobiert wird auch als Claude-Artifact.
Live: https://justiiiiiin.github.io/Training/

## Aufbau

- `index.html`: CSS inline, HTML, dann der gesamte Code. Der Hauptcode steht in `<script type="text/plain" id="fc-main">` und wird per `textContent` ausgeführt. Ein `<script>`-Tag darin würde die Seite zerstören, schreibe also nie `</script>` in Strings.
- Davor liegt ein kleiner Sync-Block (`window.FC`): Speicher über localStorage, optional Supabase (Tabelle `kv`) oder die Artifact-Datenbank. Schema und Row-Level-Security der Tabelle stehen in `docs/supabase.sql`.
- `sw.js`: Service Worker (Netz zuerst, Offline-Rückfall, Cache `fc-offline-v2`). `manifest.webmanifest` und die Icons gehören zur Installation auf dem Home-Bildschirm.
- Daten im Code: `RECIPES` (300 Rezepte), `DAYS`, `PRICE` (Lidl-Richtwerte) werden aus `tools/recipes/` eingesetzt. Übungen: `EX`, `EXALT`, `EXFUT`, `GEAR`. 3D-Animationen: `V3A`.
- Wichtige Stellen: `sanitizeState()` (prüft alle gespeicherten Daten), `showTab()`/`GROUPS`/`TABN` (Navigation), `renderEx`, `renderAusblick`, `prepCalc`/`prepGen` (Vorkochen), `shopCalc` (Einkaufsliste), `buyEstimate` (Ausgaben), `cParse` (Kalorien-Rechner mit `CEXTRA`, `CDISH`).
- Gespeichert wird alles in localStorage-Schlüsseln `fc_*` (zum Beispiel `fc_settings`, `fc_diary`, `fc_goals`). Ändere nie ihre Bedeutung, ohne `sanitizeState` mitzuziehen.

## Befehle

```bash
pip install -r tests/requirements.txt && python3 -m playwright install chromium
bash tests/run_all.sh                 # alle Tests, parallel, mit Zusammenfassung
python3 tests/calc_test.py            # ein einzelner Test
python3 tools/stamp.py                # Versionslabel hochzählen (v3.N · Datum), nur beim Veröffentlichen
```

Syntaxcheck des Hauptcodes (der steht ja in einem `text/plain`-Block):

```bash
python3 - <<'PY'
import re
s = open("index.html", encoding="utf-8").read()
open("/tmp/main.js", "w", encoding="utf-8").write(re.search(r'<script type="text/plain" id="fc-main">(.*?)</script>', s, re.S).group(1))
PY
node --check /tmp/main.js
```

Rezepte ändern: `tools/recipes/build.py` bearbeiten, dann `python3 tools/recipes/build.py` (prüft Kalorien, Eiweiß, Vielfalt, schreibt die JSON-Dateien) und `python3 tools/recipes/inject.py` (setzt sie in `index.html` ein).

## Tests

Alle Tests laufen mit Playwright (Chromium) gegen `index.html`, ohne Server, außer `pwa_test.py` (lokaler Server). Pfade kommen aus `tests/fcenv.py`. Mit `FC_URL` oder `FC_APP_DIR` lässt sich eine andere Version prüfen. Der Audit `audit2.py` geht alle Tabs durch (Überlauf, Kontrast, Tap-Ziele) und dauert länger.
`update_test.py` und `swupdate_test.py` (Update-Banner und Service Worker) fehlen hier, weil sie handgebaute Fixtures brauchen.
Bekannte Eigenheit: `Overnight Oats (dein Rezept)` hat 845 kcal und wird von `build.py` absichtlich als Ausnahme gemeldet.

## Fallstricke

- Der Code läuft von oben nach unten. Top-level-`const` und `let` müssen vor ihrer ersten Benutzung stehen, auch indirekt über Funktionen, die beim Start laufen (`sanitizeState` läuft mitten in der Datei). Doppelte Namen fallen mit `node --check` auf.
- Im Rechner (`cParse`) prüft `CDISH` (Gerichte) vor `CFOODS` (Zutaten), und ein einzelnes Wort in `CDISH` trifft auch als Teil eines längeren Wortes. Nimm dort nur eindeutige oder mehrwortige Schlüssel.
- Beim Hinzufügen von Übungen ohne 3D-Animation (`V3A`) muss die Oberfläche das berücksichtigen (siehe `techBtn`, `coachFig`).
- `index.html` wird bei Veröffentlichung nur durch `tools/stamp.py` versioniert. Das Label steht in `#appver` und der Update-Check vergleicht es.
- Texte stehen auf Deutsch mit echten Umlauten. Keine langen Gedankenstriche in Texten.

## So bitte arbeiten

- Verhalten nicht verändern, wenn es nur um eine Prüfung geht. Erst die Funde nach Schwere auflisten, dann in kleinen Commits beheben, nach jedem Schritt `bash tests/run_all.sh`.
- Keine neuen Abhängigkeiten, Build-Schritte oder Aufteilung der Datei ohne Rückfrage.
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
