/* Fitness Coach: Offline-Betrieb. Mit Netz kommt immer die neueste Version, ohne Netz die zuletzt geladene. */
const CACHE = "fc-offline-v3";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "icon.svg", "styles.css",
  "js/zoom.js", "js/sync.js", "js/boot.js", "js/data.js", "js/app.js", "js/v3.js", "js/start.js",
  "fonts/hanken-grotesk-latin.woff2", "fonts/hanken-grotesk-latin-ext.woff2", "fonts/bricolage-grotesque-latin.woff2", "fonts/bricolage-grotesque-latin-ext.woff2"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES.map((f) => new Request(f, { cache: "reload" })))).then(() => self.skipWaiting()));
});

/* Ein Eintrag pro Datei: ohne ?v=… gespeichert, damit der Speicher nicht mit jeder Version wächst und offline immer die neueste Fassung kommt */
const keyOf = (url) => { const u = new URL(url); u.search = ""; u.hash = ""; return u.href; };

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const ks = await caches.keys(), old = ks.filter((k) => k !== CACHE);
    await Promise.all(old.map((k) => caches.delete(k)));
    /* ältere Einträge mit ?v=… aufräumen */
    const c = await caches.open(CACHE), reqs = await c.keys();
    await Promise.all(reqs.filter((r) => new URL(r.url).search).map((r) => c.delete(r)));
    await self.clients.claim();
    /* Hat eine ältere Version dieses Offline-Speichers die Seite womöglich veraltet gehalten, lade offene Fenster einmal neu. */
    if (old.length) {
      const cs = await self.clients.matchAll({ type: "window" });
      cs.forEach((c) => { try { c.navigate(c.url); } catch (err) {} });
    }
  })());
});

/* Hängt das Netz (Empfang da, aber es kommt nichts durch), wartet nicht jede Datei einzeln 4,5 s: Nach einer Zeitüberschreitung gilt 45 s lang nur noch 1,2 s, sofern die Datei im Speicher liegt. */
let slowUntil = 0;
async function netFirst(req) {
  const c = await caches.open(CACHE);
  const key = keyOf(req.url);
  const wait = Date.now() < slowUntil && (await c.match(key)) ? 1200 : 4500;
  try {
    /* bewusst eine frische Anfrage über die Adresse: manche Browser vertragen sich schlecht mit dem Navigations-Request samt Zusatzoptionen */
    const r = await Promise.race([
      fetch(req.url, { cache: "no-cache", credentials: "same-origin" }),
      new Promise((_, no) => setTimeout(() => no(new Error("timeout")), wait))
    ]);
    if (r && r.ok) c.put(key, r.clone());
    return r;
  } catch (err) {
    if (err && err.message === "timeout") slowUntil = Date.now() + 45000;
    const hit = (await c.match(key)) || (req.mode === "navigate" ? (await c.match("index.html")) || (await c.match("./")) : null);
    return hit || Response.error();
  }
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const u = new URL(req.url);
  if (u.searchParams.has("fcv")) return;   /* Versionsabfrage der Seite: direkt zum Netz */
  if (u.origin === location.origin) e.respondWith(netFirst(req));
});
