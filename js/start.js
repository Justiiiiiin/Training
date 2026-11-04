/* Fitness Coach: Start (läuft zuletzt). Klassisches Skript, teilt sich den globalen Bereich mit den anderen Dateien in js/ (Reihenfolge siehe js/boot.js). */
/* ======================= Start ======================= */
$("#b-settings").innerHTML = ic("gear"); $("#b-settings2").innerHTML = ic("gear") + "<span>Einstellungen</span>";
$("#x-settings").innerHTML = ic("close");
applyPrices(); bindV3(); renderEx(); renderRecipes(); renderNutrition(); renderTips(); renderAusblick(); renderSources(); renderProgress(); bindSettings(); render(); bindGoals(); renderToday();
function radShowAll() { rad.shown = new Set(); const P = RPL[RAD.mode]; if (P) P.days.forEach((d, di) => d.slots.forEach((x, si) => rad.shown.add(di + ":" + si))); }
Object.keys(RPL).forEach((k) => { if (!RPL[k] || !RPL[k].days || RPL[k].days.some((d) => d.slots.some((x) => !byId(x.id)))) delete RPL[k]; });
radShowAll(); renderRadOpts(); radIdle(); radRender(); renderShop();
window.addEventListener("resize", drawWheel);
if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawWheel);
window.matchMedia && matchMedia("(prefers-color-scheme: dark)").addEventListener && matchMedia("(prefers-color-scheme: dark)").addEventListener("change", drawWheel);
$$("[data-ic]").forEach((el) => { el.innerHTML = ic(el.dataset.ic); });
if (canCheckUpdate()) {
  setTimeout(() => { checkUpdate(true).catch(() => {}); }, 3000);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") checkUpdate(false).catch(() => {}); });
  setInterval(() => { if (document.visibilityState === "visible") checkUpdate(false).catch(() => {}); }, 15 * 60 * 1000);
}
if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
  const mf = document.createElement("link"); mf.rel = "manifest"; mf.href = "manifest.webmanifest"; document.head.appendChild(mf);
  window.addEventListener("load", () => { navigator.serviceWorker.register("sw.js").catch(() => {}); });
  if (standalone() && navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
}
applyTextSize();
showTab("heute", true); window.addEventListener("resize", () => { moveBoth(); });
if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { moveBoth(); });
document.documentElement.setAttribute("data-ready", "1");
window.__fcReady = true; /* Start komplett durchgelaufen (sonst zeigt der Startblock unten einen Hinweis) */
