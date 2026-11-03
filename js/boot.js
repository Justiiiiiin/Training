/* Fitness Coach: Start. Bricht der Hauptcode beim Start ab, bleibt sonst eine halbe App ohne Meldung. Dann Hinweis mit Neu laden und Sicherung. */
function fcStartFailed(msg) {
  if (document.getElementById("startfail")) return;
  var box = document.createElement("div"); box.id = "startfail"; box.className = "startfail"; box.setAttribute("role", "alert");
  var p = document.createElement("p"); p.textContent = "Beim Start ist ein Fehler aufgetreten. Deine Daten sind noch gespeichert. Lade die App neu. Klappt es dann immer noch nicht, kopiere zur Sicherheit eine Sicherung.";
  var d = document.createElement("p"); d.className = "small muted"; d.textContent = "Fehler: " + msg;
  var row = document.createElement("div"); row.className = "row";
  var b1 = document.createElement("button"); b1.type = "button"; b1.className = "btn primary"; b1.textContent = "Neu laden";
  b1.addEventListener("click", function () { location.reload(); });
  var b2 = document.createElement("button"); b2.type = "button"; b2.className = "btn"; b2.textContent = "Sicherung kopieren";
  var m = document.createElement("p"); m.className = "small"; m.setAttribute("aria-live", "polite");
  b2.addEventListener("click", function () {
    var t = FC.exportAll();
    var manual = function () { var ta = document.createElement("textarea"); ta.rows = 4; ta.readOnly = true; ta.value = t; ta.style.width = "100%"; m.textContent = "Markiere den Text und kopiere ihn von Hand."; m.appendChild(ta); ta.select(); };
    try { navigator.clipboard.writeText(t).then(function () { m.textContent = "Sicherung kopiert. Füge sie in eine Notiz ein."; }, manual); } catch (e) { manual(); }
  });
  row.appendChild(b1); row.appendChild(b2); box.appendChild(p); box.appendChild(d); box.appendChild(row); box.appendChild(m);
  document.body.appendChild(box);
}
/* Lädt den Hauptcode in fester Reihenfolge (async = false). ?v= mit dem Versionslabel umgeht veraltete Browser-Caches nach einem Update. */
var FC_FILES = ["js/data.js", "js/app.js", "js/v3.js", "js/start.js"];
function fcLoad(files, done) {
  var v = encodeURIComponent(((document.getElementById("appver") || {}).textContent || "").trim()), left = files.length, failed = "";
  files.forEach(function (f) {
    var el = document.createElement("script"); el.src = f + (v ? "?v=" + v : ""); el.async = false;
    el.onload = function () { if (--left === 0) done(failed); };
    el.onerror = function () { failed = failed || ("Datei " + f + " konnte nicht geladen werden"); if (--left === 0) done(failed); };
    document.body.appendChild(el);
  });
}
FC.boot(function () {
  var first = "";
  var onErr = function (e) { if (!first && e && e.message) first = String(e.message); };
  window.addEventListener("error", onErr);
  fcLoad(FC_FILES, function (failed) {
    window.removeEventListener("error", onErr);
    FC.paint();
    if (!window.__fcReady) fcStartFailed(first || failed || "unbekannt");
  });
});
