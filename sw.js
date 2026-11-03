/* Fitness Coach: Offline-Betrieb. Mit Netz kommt immer die neueste Version, ohne Netz die zuletzt geladene. */
const CACHE = "fc-offline-v1";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "icon.svg"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});

const FONTS = ["fonts.googleapis.com", "fonts.gstatic.com"];

async function netFirst(req) {
  const c = await caches.open(CACHE);
  try {
    const r = await Promise.race([
      fetch(req, { cache: "no-cache" }),
      new Promise((_, no) => setTimeout(() => no(new Error("timeout")), 3500))
    ]);
    if (r && r.ok) c.put(req, r.clone());
    return r;
  } catch (err) {
    const hit = (await c.match(req, { ignoreSearch: true })) || (req.mode === "navigate" ? (await c.match("index.html")) || (await c.match("./")) : null);
    return hit || Response.error();
  }
}

async function cacheFirst(req) {
  const c = await caches.open(CACHE), hit = await c.match(req);
  if (hit) return hit;
  try {
    const r = await fetch(req);
    if (r && (r.ok || r.type === "opaque")) c.put(req, r.clone());
    return r;
  } catch (err) { return Response.error(); }
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const u = new URL(req.url);
  if (u.origin === location.origin) e.respondWith(netFirst(req));
  else if (FONTS.includes(u.hostname)) e.respondWith(cacheFirst(req));
});
