/* Fitness Coach: Speicher und Sync (localStorage, optional eigene Supabase-Datenbank). */
window.FC = (function () {
  "use strict";
  var KEYS = ["fc_settings", "fc_levels", "fc_log", "fc_sessions", "fc_body", "fc_shop", "fc_exc", "fc_rad", "fc_radplans", "fc_cart", "fc_budget", "fc_chk", "fc_goals", "fc_diary", "fc_wk", "fc_fav", "fc_prep", "fc_dishes"];
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  /* Schreibfehler (Speicher voll oder gesperrt) werden gezählt und der App gemeldet, statt still zu verschwinden */
  var saveFails = 0, onSaveFail = null;
  function lsSet(k, v) {
    try { localStorage.setItem(k, v); return true; }
    catch (e) { saveFails++; if (onSaveFail) { try { onSaveFail(); } catch (e2) {} } return false; }
  }
  function lsDel(k) { try { localStorage.removeItem(k); } catch (e) {} }
  function sbCfg() { try { var c = JSON.parse(lsGet("fc__sb") || "null"); return c && c.url && c.key && c.rt ? c : null; } catch (e) { return null; } }
  var mode = sbCfg() ? "sb" : "local";
  var mem = {}, ts = {}, pushed = {}, dirty = new Set(), pulledOnce = false;
  var base = {}, view = {};   /* base: letzter gemeinsamer Stand je geändertem Schlüssel (für den 3-Wege-Abgleich), view: was die App zuletzt gelesen oder geschrieben hat */
  var R = null, pulling = false, busy = false, flushTimer = 0, retryTimer = 0, mainStarted = false, watching = false;
  var state = mode === "local" ? "local" : "connecting";
  try { ts = JSON.parse(lsGet("fc__ts") || "{}") || {}; if (typeof ts !== "object" || Array.isArray(ts)) ts = {}; } catch (e) { ts = {}; }
  try { base = JSON.parse(lsGet("fc__base") || "{}") || {}; if (typeof base !== "object" || Array.isArray(base)) base = {}; } catch (e) { base = {}; }
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
  function saveBase() { if (Object.keys(base).length) lsSet("fc__base", JSON.stringify(base)); else lsDel("fc__base"); }
  function raw(k) { return Object.prototype.hasOwnProperty.call(mem, k) ? mem[k] : lsGet(k); }
  function setRaw(k, s) { mem[k] = s; lsSet(k, s); }
  function saveTs() { lsSet("fc__ts", JSON.stringify(ts)); }
  var TXT = {
    local: "Nur auf diesem Gerät gespeichert.",
    connecting: "Verbinde mit deiner Datenbank …",
    ok: "Synchronisiert. Deine Daten liegen privat in deiner Datenbank.",
    saving: "Speichert …",
    offline: "Gerade keine Verbindung. Änderungen werden nachgeholt, sobald es wieder klappt.",
    login: "Die Anmeldung ist abgelaufen. Melde dich unter Einstellungen neu an."
  };
  var SHORT = { local: "", connecting: "Verbinde …", ok: "Synchronisiert", saving: "Speichert …", offline: "Offline, wird nachgeholt", login: "Bitte neu anmelden" };
  function setState(s) { state = s; paint(); }
  function paint() {
    var c = document.getElementById("syncst"), i = document.getElementById("syncinfo");
    if (c) { c.textContent = SHORT[state] || ""; c.dataset.state = state; c.hidden = !SHORT[state]; }
    if (i) i.textContent = TXT[state] || "";
  }
  function delay(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function withTimeout(p, ms) { return Promise.race([Promise.resolve(p), delay(ms).then(function () { return null; })]); }

  /* ---------- Backend: eigene Supabase-Datenbank ---------- */
  async function sbAuth(url, key, path, body) {
    var r = await fetch(url + "/auth/v1/" + path, { method: "POST", headers: { apikey: key, "Content-Type": "application/json" }, body: JSON.stringify(body) });
    var j = {}; try { j = await r.json(); } catch (e) {}
    if (!r.ok) { var m = j.error_description || j.msg || j.message || ("Fehler " + r.status); var er = new Error(m); er.status = r.status; throw er; }
    return j;
  }
  var loggedOut = false;
  function sbStore(c, j) { if (loggedOut) return; c.at = j.access_token; c.rt = j.refresh_token || c.rt; c.exp = Date.now() + (j.expires_in || 3600) * 1000; lsSet("fc__sb", JSON.stringify(c)); }
  async function sbRefresh() {
    var c = sbCfg(); if (!c) throw new Error("login");
    try { var j = await sbAuth(c.url, c.key, "token?grant_type=refresh_token", { refresh_token: c.rt }); sbStore(c, j); }
    catch (e) { if (e.status >= 400 && e.status < 500 && e.status !== 429) { var err = new Error("login"); err.login = true; throw err; } throw e; }
  }
  async function sbFetch(path, opt, retried) {
    var c = sbCfg(); if (!c) { var e0 = new Error("login"); e0.login = true; throw e0; }
    if (!c.at || Date.now() > (c.exp || 0) - 60000) { await sbRefresh(); c = sbCfg(); }
    var h = { apikey: c.key, Authorization: "Bearer " + c.at, "Content-Type": "application/json" };
    if (opt.headers) for (var k in opt.headers) h[k] = opt.headers[k];
    var r = await fetch(c.url + path, { method: opt.method || "GET", headers: h, body: opt.body });
    if (r.status === 401 && !retried) { await sbRefresh(); return sbFetch(path, opt, true); }
    if (!r.ok) throw new Error("http " + r.status);
    return r;
  }
  /* Nutzer-ID aus dem Zugangs-Token (JWT). Dient als zweite Sicherung neben Row-Level-Security. */
  function sbUid() {
    try {
      var c = sbCfg(), b = String(c && c.at || "").split(".")[1];
      if (!b) return "";
      b = b.replace(/-/g, "+").replace(/_/g, "/"); while (b.length % 4) b += "=";
      var j = JSON.parse(atob(b));
      return typeof j.sub === "string" && /^[0-9a-f-]{36}$/i.test(j.sub) ? j.sub : "";
    } catch (e) { return ""; }
  }
  function sbBackend() {
    var iv = 0;
    return {
      name: "sb",
      connect: async function () { await sbRefresh(); return true; },
      listAll: async function () {
        var uid = sbUid();
        var r = await sbFetch("/rest/v1/kv?select=k,t,v" + (uid ? "&user_id=eq." + uid : ""), {}), rows = await r.json(), out = {};
        if (!Array.isArray(rows)) rows = [];
        rows.forEach(function (x) { if (KEYS.indexOf(x.k) >= 0 && typeof x.v === "string" && x.t != null) out[x.k] = { t: Number(x.t), v: x.v }; });
        return out;
      },
      put: async function (k, t, s) {
        await sbFetch("/rest/v1/kv?on_conflict=user_id,k", { method: "POST", headers: { Prefer: "resolution=merge-duplicates,return=minimal" }, body: JSON.stringify([{ k: k, t: t, v: s }]) });
      },
      watch: function (onChange) {
        if (iv) return;
        iv = setInterval(function () { if (document.visibilityState === "visible") onChange(); }, 30000);
      }
    };
  }

  /* ---------- Zusammenführen statt Überschreiben (3-Wege-Abgleich) ----------
     b = gemeinsamer Stand, l = dieses Gerät, r = Datenbank. Was nur eine Seite geändert hat, wird übernommen.
     Objekte: Feld für Feld (Löschungen zählen). Listen von Texten und von Einträgen mit date, d oder t (Tagebuch,
     Trainings, Einkäufe): als Multimenge, Hinzugefügtes beider Seiten bleibt. Andere Listen und einzelne Werte:
     bei echtem Widerspruch gewinnt die neuere Seite (lw = dieses Gerät ist neuer). */
  var KEYED = { fc_log: "date", fc_cart: "id", fc_dishes: "id" };
  function isObj(x) { return x !== null && typeof x === "object" && !Array.isArray(x); }
  function sj(x) {
    if (Array.isArray(x)) return "[" + x.map(sj).join(",") + "]";
    if (isObj(x)) return "{" + Object.keys(x).sort().map(function (k) { return JSON.stringify(k) + ":" + sj(x[k]); }).join(",") + "}";
    var j = JSON.stringify(x); return j === undefined ? "null" : j;
  }
  function same(a, b) { return a === undefined || b === undefined ? a === b : sj(a) === sj(b); }
  function dateOf(x) { return typeof x === "string" ? x : isObj(x) ? (typeof x.date === "string" ? x.date : typeof x.d === "string" ? x.d : null) : null; }
  function setLike(a) { return a.every(function (x) { return typeof x === "string" || (isObj(x) && (typeof x.date === "string" || typeof x.d === "string" || typeof x.t === "string")); }); }
  function mergeArr(b, l, r, lw) {
    if (!setLike(l) || !setLike(r)) {
      if (l.length === r.length) return l.map(function (x, i) { return merge3(b && b.length === l.length ? b[i] : undefined, x, r[i], lw); });
      return lw ? l : r;
    }
    var cnt = function (a) { var m = {}; (a || []).forEach(function (x) { var k = sj(x); m[k] = (m[k] || 0) + 1; }); return m; };
    var cb = cnt(b), cl = cnt(l), cr = cnt(r), out = [], done = {};
    var want = function (k) { return b ? Math.max(0, (cr[k] || 0) + (cl[k] || 0) - (cb[k] || 0)) : Math.max(cr[k] || 0, cl[k] || 0); };
    r.concat(l).forEach(function (x) { var k = sj(x); if ((done[k] || 0) < want(k)) { out.push(x); done[k] = (done[k] || 0) + 1; } });
    var dated = out.length && out.every(function (x) { return /^\d{4}-\d{2}-\d{2}/.test(dateOf(x) || ""); });
    if (dated) out = out.map(function (x, i) { return [x, i]; }).sort(function (p, q) { var a = dateOf(p[0]), c = dateOf(q[0]); return a < c ? -1 : a > c ? 1 : p[1] - q[1]; }).map(function (p) { return p[0]; });
    return out;
  }
  function merge3(b, l, r, lw) {
    if (same(l, r)) return r;
    if (b !== undefined && same(l, b)) return r;
    if (b !== undefined && same(r, b)) return l;
    if (isObj(l) && isObj(r)) {
      var bo = isObj(b) ? b : null, o = {};
      Object.keys(r).concat(Object.keys(l).filter(function (k) { return !has(r, k); })).forEach(function (k) {
        var hb = !!bo && has(bo, k), hl = has(l, k), hr = has(r, k);
        if (k === "plan" && hl && hr) { o[k] = hb && same(l[k], bo[k]) ? r[k] : hb && same(r[k], bo[k]) ? l[k] : (lw ? l[k] : r[k]); return; }
        if (hl && hr) o[k] = merge3(hb ? bo[k] : undefined, l[k], r[k], lw);
        else if (hl) { if (!(hb && same(l[k], bo[k]))) o[k] = l[k]; }
        else if (!(hb && same(r[k], bo[k]))) o[k] = r[k];
      });
      return o;
    }
    if (Array.isArray(l) && Array.isArray(r)) return mergeArr(Array.isArray(b) ? b : null, l, r, lw);
    return lw ? l : r;
  }
  function byKey(a, f) { var o = {}; (Array.isArray(a) ? a : []).forEach(function (x) { if (isObj(x) && typeof x[f] === "string") o[x[f]] = x; }); return o; }
  function mergeStr(k, bs, ls, rs, lw) {
    try {
      var b = bs == null ? undefined : JSON.parse(bs), l = JSON.parse(ls), r = JSON.parse(rs), out;
      var f = KEYED[k];
      if (f && Array.isArray(l) && Array.isArray(r)) {
        var m = merge3(b === undefined ? undefined : byKey(b, f), byKey(l, f), byKey(r, f), lw);
        out = Object.keys(m).sort().map(function (x) { return m[x]; });
        if (f === "id") { var order = r.concat(l).map(function (x) { return isObj(x) ? x.id : null; }); out.sort(function (p, q) { return order.indexOf(p.id) - order.indexOf(q.id); }); }
      } else out = merge3(b, l, r, lw);
      return JSON.stringify(out);
    } catch (e) { return lw ? ls : rs; }
  }

  /* ---------- gemeinsamer Abgleich ---------- */
  function fail(e) {
    if (e && e.login) setState("login"); else setState("offline");
    if (!(e && e.login)) retryTimer = setTimeout(flush, 15000);
  }
  async function pullAll() {
    if (!R || pulling) return false;
    pulling = true;
    try {
      var rem = await R.listAll(), changed = false;
      KEYS.forEach(function (k) {
        var m = rem[k]; if (!m) return;
        try { JSON.parse(m.v); } catch (e) { return; }
        var loc = raw(k), lt = ts[k] || 0;
        if (loc === m.v) { pushed[k] = m.v; if (m.t > lt) ts[k] = m.t; if (has(base, k)) delete base[k]; return; }
        var mine = loc != null && has(base, k);   /* dieses Gerät hat seit dem letzten Abgleich etwas geändert */
        if (m.t > lt && !mine) { setRaw(k, m.v); ts[k] = m.t; pushed[k] = m.v; if (has(base, k)) delete base[k]; changed = true; return; }
        if (loc == null) return;
        /* beide Seiten haben sich verändert (oder die Datenbank hat einen älteren, anderen Stand): zusammenführen */
        var b0 = has(base, k) ? base[k] : (has(pushed, k) ? pushed[k] : null);
        var merged = mergeStr(k, b0, loc, m.v, lt > m.t);
        if (merged === m.v) { setRaw(k, m.v); ts[k] = m.t; pushed[k] = m.v; delete base[k]; dirty.delete(k); changed = true; return; }
        if (merged !== loc) { setRaw(k, merged); changed = true; }
        base[k] = m.v; pushed[k] = m.v; ts[k] = Math.max(Date.now(), lt, m.t + 1); dirty.add(k);
      });
      KEYS.forEach(function (k) {
        var m = rem[k], s = raw(k);
        if (s == null) return;
        if (!m || (ts[k] || 0) > m.t) { if (!(ts[k] > 0)) ts[k] = 1; dirty.add(k); }
      });
      saveTs(); saveBase(); pulledOnce = true; lsSet("fc__synced", "1");
      return changed;
    } finally { pulling = false; }
  }
  async function push(k) {
    var s = raw(k); if (s == null) return;
    if (pushed[k] !== s) { await R.put(k, ts[k] || Date.now(), s); pushed[k] = s; }
    if (raw(k) === s && has(base, k)) { delete base[k]; saveBase(); }
  }
  async function flush() {
    if (!R || busy || !pulledOnce) return;
    clearTimeout(flushTimer); clearTimeout(retryTimer); retryTimer = 0;
    if (!dirty.size) { setState("ok"); return; }
    busy = true; setState("saving");
    var err = null, fresh = false;
    try {
      /* erst lesen, dann schreiben: Änderungen anderer Geräte werden zusammengeführt statt überschrieben */
      try { fresh = await pullAll(); } catch (e) { err = e; }
      while (!err && dirty.size) {
        var k = dirty.values().next().value; dirty.delete(k);
        try { await push(k); } catch (e) { dirty.add(k); err = e; break; }
      }
    } finally { busy = false; }
    if (err) fail(err);
    else if (dirty.size) schedule();
    else setState("ok");
    if (fresh && mainStarted && !err) reloadWhenIdle();
  }
  function schedule() { clearTimeout(flushTimer); flushTimer = setTimeout(flush, 1200); }
  function save(k, s, force) {
    var cur = raw(k), synced = KEYS.indexOf(k) >= 0 && mode !== "local";
    if (synced && !force && mainStarted && has(view, k) && view[k] != null && cur != null && cur !== view[k]) {
      /* Der Sync hat diesen Bereich verändert, seit die App ihn gelesen hat: App-Änderung und Sync-Stand zusammenführen */
      var app = s; s = mergeStr(k, view[k], app, cur, true); view[k] = app;
    } else view[k] = s;
    setRaw(k, s);
    if (!synced) return;
    if (!pulledOnce && !lsGet("fc__synced")) return; /* neues Gerät: erst abgleichen, damit leere Startwerte nichts überschreiben */
    if (!has(base, k)) { base[k] = cur; saveBase(); }   /* Stand vor der ersten eigenen Änderung seit dem letzten Abgleich */
    ts[k] = Date.now(); saveTs();
    dirty.add(k);
    if (R) { if (state !== "saving") setState("saving"); schedule(); }
  }
  function idle() {
    try {
      var a = document.activeElement;
      return !(typeof isActive === "function" && isActive()) && !document.querySelector("dialog[open]") && !(a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)) && !(typeof rad !== "undefined" && rad.busy);
    } catch (e) { return true; }
  }
  var reloading = false;
  async function reloadWhenIdle() {
    if (reloading) return; reloading = true;
    for (var i = 0; i < 600; i++) {
      if (idle()) {
        if (dirty.size) { await flush(); if (dirty.size && !lsGet("fc__ts")) { reloading = false; return; } }
        location.reload(); return;
      }
      await delay(4000);
    }
    reloading = false;
  }
  function onRemoteChange() {
    if (pulling) return;
    pullAll().then(function (ch) { if (ch && mainStarted) reloadWhenIdle(); }).catch(function () {});
  }
  async function start() {
    try {
      R = sbBackend();
      await R.connect();
      var ch = await pullAll();
      setState(dirty.size ? "saving" : "ok");
      return ch;
    } catch (e) {
      if (e && e.login) { setState("login"); return false; }
      /* offline: später erneut versuchen */
      setState("offline");
      clearTimeout(retryTimer);
      retryTimer = setTimeout(function () {
        if (pulledOnce) return flush();
        R = null;
        start().then(function (ch) { if (R && pulledOnce) { R.watch(onRemoteChange); if (ch && mainStarted) reloadWhenIdle(); else if (dirty.size) flush(); } });
      }, 15000);
      return false;
    }
  }
  async function boot(runMain) {
    if (mode === "local") { mainStarted = true; runMain(); return; }
    var p = start();
    var done = await Promise.race([p.then(function () { return true; }), delay(7000).then(function () { return false; })]);
    KEYS.forEach(function (k) { view[k] = raw(k); });
    mainStarted = true; runMain(); paint();
    p.then(function (ch) {
      if (!R) return;
      R.watch(onRemoteChange);
      if (!done && ch) reloadWhenIdle(); else if (dirty.size) flush();
    });
    document.addEventListener("visibilitychange", function () {
      if (!R) return;
      if (document.visibilityState === "hidden") { if (dirty.size) flush(); }
      else pullAll().then(function (ch) { if (ch) reloadWhenIdle(); else if (dirty.size) flush(); }).catch(function () {});
    });
    window.addEventListener("pagehide", function () { if (dirty.size) flush(); });
    window.addEventListener("online", function () { if (R && dirty.size) flush(); });
  }
  async function syncNow() {
    if (mode === "local") return;
    if (!R) { setState("connecting"); await start(); if (!R) return; R.watch(onRemoteChange); }
    var ch = await pullAll().catch(function (e) { fail(e); return false; });
    if (ch) return reloadWhenIdle();
    await flush();
  }
  /* Anmeldung bei der eigenen Datenbank (Supabase) */
  async function sbLogin(url, key, email, pw, signup) {
    loggedOut = false;
    url = String(url || "").trim().replace(/\/+$/, ""); key = String(key || "").trim(); email = String(email || "").trim();
    if (!/^(https:\/\/[^\s/]+|http:\/\/(127\.0\.0\.1|localhost)(:\d+)?)$/.test(url)) throw new Error("Die Projekt-URL sieht nicht richtig aus. Sie beginnt mit https:// und endet auf .supabase.co.");
    if (!key || !email || !pw) throw new Error("Bitte alle Felder ausfüllen.");
    var j;
    if (signup) {
      j = await sbAuth(url, key, "signup", { email: email, password: pw });
      if (!j.access_token) throw new Error("Konto angelegt. Bestätige noch die E-Mail, die Supabase dir geschickt hat, und melde dich dann an.");
    } else j = await sbAuth(url, key, "token?grant_type=password", { email: email, password: pw });
    var c = { url: url, key: key, email: email };
    sbStore(c, j);
    return true;
  }
  /* Abmelden: Sitzung auch beim Server beenden (nur dieses Gerät, scope=local), dann lokal vergessen */
  async function sbLogout() {
    var c = sbCfg();
    if (c) {
      try {
        if (!c.at || Date.now() > (c.exp || 0) - 60000) { await withTimeout(sbRefresh(), 5000); c = sbCfg() || c; }
        await withTimeout(fetch(c.url + "/auth/v1/logout?scope=local", { method: "POST", headers: { apikey: c.key, Authorization: "Bearer " + c.at } }), 5000);
      } catch (e) {}
    }
    loggedOut = true; lsDel("fc__sb"); lsDel("fc__ts"); lsDel("fc__synced");
  }
  function sbInfo() { var c = sbCfg(); return c ? { url: c.url, email: c.email, key: c.key } : null; }
  function exportAll() {
    var out = {};
    KEYS.forEach(function (k) { var s = raw(k); if (s != null) { try { out[k] = JSON.parse(s); } catch (e) {} } });
    return JSON.stringify({ app: "fitness-coach", v: 1, data: out });
  }
  async function importAll(text) {
    var o; try { o = JSON.parse(text); } catch (e) { throw new Error("Das ist keine gültige Sicherung."); }
    if (!o || o.app !== "fitness-coach" || !o.data || typeof o.data !== "object") throw new Error("Das ist keine Sicherung aus dieser App.");
    var n = 0;
    KEYS.forEach(function (k) { if (Object.prototype.hasOwnProperty.call(o.data, k)) { save(k, JSON.stringify(o.data[k]), true); n++; } });
    if (!n) throw new Error("In der Sicherung waren keine Daten.");
    if (R) await flush();
    return n;
  }
  return { KEYS: KEYS, mode: mode, raw: raw, save: save, boot: boot, paint: paint, syncNow: syncNow, exportAll: exportAll, importAll: importAll,
    sbLogin: sbLogin, sbLogout: sbLogout, sbInfo: sbInfo, state: function () { return state; }, dirtyCount: function () { return dirty.size; },
    _merge: mergeStr,
    onSaveFail: function (fn) { onSaveFail = fn; if (saveFails && fn) { try { fn(); } catch (e) {} } } };
})();
