/* Fitness Coach: Content-Security-Policy. Läuft als erstes Skript im <head>.
   Erlaubt nur Skripte, Schriften und Bilder von hier, Verbindungen nur hierher und zu Supabase. Eingeschleuster Code
   (z. B. onerror-Attribute aus manipulierten Daten) wird dann nicht ausgeführt, und ein Token könnte nicht an fremde
   Server geschickt werden. Gilt auf GitHub Pages, lokal und unter file://, nicht im Claude-Artifact (dort gelten die
   Regeln der Umgebung, und deren Laufzeit braucht eigene Verbindungen). */
(function () {
  var h = location.hostname, ours = location.protocol === "file:" || /(^|\.)github\.io$/.test(h) || h === "localhost" || h === "127.0.0.1";
  if (!ours || (window.claude && typeof window.claude.use === "function")) return;
  var m = document.createElement("meta");
  m.httpEquiv = "Content-Security-Policy";
  m.content = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob:",
    "font-src 'self'",
    "connect-src 'self' https://*.supabase.co http://127.0.0.1:* http://localhost:*",
    "worker-src 'self'",
    "manifest-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'none'"
  ].join("; ");
  document.head.appendChild(m);
})();
