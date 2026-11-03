/* Fitness Coach: Offline-Betrieb. Mit Netz kommt immer die neueste Version, ohne Netz die zuletzt geladene. */
const CACHE = "fc-offline-v3";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "icon.svg", "styles.css",
  "js/sync.js", "js/boot.js", "js/data.js", "js/app.js", "js/v3.js", "js/start.js",
  "fonts/hanken-grotesk-latin.woff2", "fonts/hanken-grotesk-latin-ext.woff2", "fonts/bricolage-grotesque-latin.woff2", "fonts/bricolage-grotesque-latin-ext.woff2"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES.map((f) => new Request(f, { cache: "reload" })))).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const ks = await caches.keys(), old = ks.filter((k) => k !== CACHE);
    await Promise.all(old.map((k) => caches.delete(k)));
    await self.clients.claim();
    /* Hat eine ältere Version dieses Offline-Speichers die Seite womöglich veraltet gehalten, lade offene Fenster einmal neu. */
    if (old.length) {
      const cs = await self.clients.matchAll({ type: "window" });
      cs.forEach((c) => { try { c.navigate(c.url); } catch (err) {} });
    }
  })());
});

async function netFirst(req) {
  const c = await caches.open(CACHE);
  try {
    /* bewusst eine frische Anfrage über die Adresse: manche Browser vertragen sich schlecht mit dem Navigations-Request samt Zusatzoptionen */
    const r = await Promise.race([
      fetch(req.url, { cache: "no-cache", credentials: "same-origin" }),
      new Promise((_, no) => setTimeout(() => no(new Error("timeout")), 4500))
    ]);
    if (r && r.ok) c.put(req.url, r.clone());
    return r;
  } catch (err) {
    const hit = (await c.match(req.url, { ignoreSearch: true })) || (req.mode === "navigate" ? (await c.match("index.html")) || (await c.match("./")) : null);
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
