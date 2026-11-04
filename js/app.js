/* Fitness Coach: Zustand, Oberfläche und Logik. Klassisches Skript, teilt sich den globalen Bereich mit den anderen Dateien in js/ (Reihenfolge siehe js/boot.js). */
/* ======================= Speicher und Zustand ======================= */
const store = {
  get(k, d) {
    try {
      const v = FC.raw(k); if (v == null) return d;
      const j = JSON.parse(v);
      const ok = Array.isArray(d) ? Array.isArray(j) : (d !== null && typeof d === "object") ? (j !== null && typeof j === "object" && !Array.isArray(j)) : typeof j === typeof d;
      return ok ? j : d;
    } catch (e) { return d; }
  },
  set(k, v) { try { FC.save(k, JSON.stringify(v)); } catch (e) {} }
};
const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
let settings = Object.assign({ sets: 2, rest: 90, hold: 30, speak: true, tdays: [1, 0, 1, 0, 1, 0, 0], alt: { row: "rowbp" } }, store.get("fc_settings", {}));
let levels = store.get("fc_levels", {});
let log = store.get("fc_log", []);
let sessions = store.get("fc_sessions", []);
let prof = Object.assign({ weight: 80, height: 175 }, store.get("fc_body", {}));
let shop = store.get("fc_shop", {});
const _p2 = (n) => (n < 10 ? "0" : "") + n;
const isoOf = (d) => isNaN(d) ? "Invalid Date" : d.getFullYear() + "-" + _p2(d.getMonth() + 1) + "-" + _p2(d.getDate());
const todayISO = () => isoOf(new Date());
applyAlts();
const lvl = (e) => Math.min(levels[e.id] != null ? levels[e.id] : e.def, e.ladder.length - 1);
const levelName = (e) => e.ladder[lvl(e)];
const nf = (n) => String(n).replace(".", ",");

const ICONS = {
  heart: '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/>',
  mic: '<path d="M12 3a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V6a3 3 0 0 0-3-3z"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
  play: '<path d="M8 5v14l11-7z"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  pause: '<path d="M8 5v14M16 5v14"/>',
  next: '<path d="M5 5l9 7-9 7zM18 5v14"/>',
  back: '<path d="M19 5l-9 7 9 7zM6 5v14"/>',
  repeat: '<path d="M4 12a8 8 0 0 1 14-5.3L20 9M20 4v5h-5M20 12a8 8 0 0 1-14 5.3L4 15M4 20v-5h5"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="2"/>',
  gear: '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  search: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4-4"/>',
  home: '<path d="M4 11.5L12 4l8 7.5"/><path d="M6 10.5V20h12v-9.5"/><path d="M10 20v-5h4v5"/>',
  dumbbell: '<path d="M3.5 9v6M6.5 7v10M17.5 7v10M20.5 9v6M6.5 12h11"/>',
  bowl: '<path d="M3.5 11h17a8.5 8.5 0 0 1-17 0z"/><path d="M8.5 7.5c0-1.5 1.5-1.5 1.5-3M13 7.5c0-1.5 1.5-1.5 1.5-3"/>',
  chart: '<path d="M4 19V5"/><path d="M4 19h16"/><path d="M8 15l3.5-4 3 2.5L19 8"/>',
  speaker: '<path d="M4 10v4h4l5 4V6L8 10z"/><path d="M16.5 9a4 4 0 0 1 0 6"/>'
};
const ic = (n) => '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">' + ICONS[n] + "</svg>";

/* ======================= Sprachausgabe ======================= */
let voiceDe = null, speaking = false, lastSpoke = 0, speakGen = 0, pending = 0;
function pickVoice() { try { voiceDe = speechSynthesis.getVoices().find((v) => /^de/i.test(v.lang)) || null; } catch (e) {} }
if ("speechSynthesis" in window) { pickVoice(); speechSynthesis.onvoiceschanged = pickVoice; }

/* Gesprochen wird nur während des Trainings. Überall sonst erscheint nur Text. */
function say(t, caption, loud) {
  const parts = (Array.isArray(t) ? t : [t]).filter(Boolean);
  $("#caption").textContent = caption || parts.join(" ");
  if (loud === undefined) loud = isActive();
  if (!loud || !settings.speak || !("speechSynthesis" in window)) return;
  try {
    speechSynthesis.cancel();
    const gen = ++speakGen;
    pending = parts.length; speaking = true;
    const fin = () => { if (gen !== speakGen) return; pending--; if (pending <= 0) { speaking = false; lastSpoke = Date.now(); } };
    parts.forEach((p) => {
      const u = new SpeechSynthesisUtterance(p);
      u.lang = "de-DE"; if (voiceDe) u.voice = voiceDe;
      u.onend = fin; u.onerror = fin;
      speechSynthesis.speak(u);
    });
    const est = parts.join(" ").length * 110 + 4000;
    setTimeout(() => { if (gen === speakGen && speaking) { speaking = false; lastSpoke = Date.now(); } }, est);
  } catch (e) { speaking = false; }
}
let actx = null;
function beep() {
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    const o = actx.createOscillator(), g = actx.createGain();
    o.frequency.value = 880; g.gain.value = 0.08; o.connect(g); g.connect(actx.destination);
    o.start(); o.stop(actx.currentTime + 0.25);
  } catch (e) {}
}
function buzz(p) { try { if (navigator.vibrate) navigator.vibrate(p || 25); } catch (e) {} }
let wakeLock = null;
async function wake() { try { if (navigator.wakeLock) wakeLock = await navigator.wakeLock.request("screen"); } catch (e) {} }
function unwake() { try { if (wakeLock) wakeLock.release(); } catch (e) {} wakeLock = null; }

/* ======================= Timer ======================= */
const tm = { id: null, running: false, end: 0, left: 0, total: 0, said10: false, onDone: null };
function startTimer(sec, onDone) {
  clearTimer();
  tm.total = sec; tm.left = sec * 1000; tm.end = Date.now() + tm.left; tm.running = true; tm.onDone = onDone; tm.said10 = false;
  tm.id = setInterval(tick, 200);
  render();
}
function tick() {
  if (!tm.running) return;
  tm.left = tm.end - Date.now();
  if (tm.left <= 0) { const cb = tm.onDone; clearTimer(); beep(); buzz(); if (cb) cb(); else render(); return; }
  if (!tm.said10 && tm.total > 20 && tm.left <= 10000) { tm.said10 = true; say("Noch zehn Sekunden."); }
  renderTimer();
}
function pauseTimer() { if (tm.running) { tm.left = tm.end - Date.now(); tm.running = false; } }
function resumeTimer() { if (tm.id && !tm.running) { tm.end = Date.now() + tm.left; tm.running = true; } }
function clearTimer() { clearInterval(tm.id); tm.id = null; tm.running = false; tm.left = 0; tm.onDone = null; }
function skipTimer() { const cb = tm.onDone; clearTimer(); if (cb) cb(); else render(); }

/* ======================= Trainingsablauf ======================= */
const W = { phase: "idle", ex: 0, set: 1, quick: false };
const setsN = () => (W.quick ? 1 : settings.sets);
const isActive = () => ["warmup", "prep", "work", "hold", "rest"].includes(W.phase);
function nextPos() { return W.set < setsN() ? { ex: W.ex, set: W.set + 1 } : { ex: W.ex + 1, set: 1 }; }
function estMinutes(q) {
  const sets = EX.length * (q ? 1 : settings.sets);
  const sec = (q ? 90 : 180) + sets * 45 + (sets - 1) * settings.rest;
  return Math.round(sec / 60 / 5) * 5;
}
function lastTime(e) {
  const lv = lvl(e);
  for (let i = WK.length - 1; i >= 0; i--) { const m = WK[i].sets.filter((x) => x.ex === e.id && x.lvl === lv && (e.type === "hold" ? x.secs > 0 : x.reps != null)); if (m.length) return e.type === "hold" ? m.map((x) => x.secs + " s") : m.map((x) => x.reps); }
  return null;
}
const lastTxt = (e) => { const l = lastTime(e); return l ? l.join(", ") : ""; };
function instruction() {
  const e = EX[W.ex];
  return e.name + ", Satz " + W.set + " von " + setsN() + ". " + (e.type === "hold" ? "Halten." : e.reps + ".");
}
function instructionLong() {
  const e = EX[W.ex];
  const head = "Übung " + (W.ex + 1) + " von " + EX.length + ": " + e.name + ". Satz " + W.set + " von " + setsN() + ". " + levelName(e) + ".";
  if (e.type === "hold") return head + " Halte " + settings.hold + " Sekunden." + (lastTxt(e) ? " Letztes Mal: " + lastTxt(e) + "." : "");
  const lt = lastTxt(e);
  return head + " " + e.reps + ". " + (lt ? "Letztes Mal: " + lt + ". Versuch eine Wiederholung mehr. " : "") + "Lass 1 bis 3 Wiederholungen übrig. Tippe auf Fertig, wenn du den Satz geschafft hast.";
}
function startWorkout(quick) {
  W.quick = !!quick; W.ex = 0; W.set = 1; W.phase = "warmup";
  SESS = { date: todayISO(), t0: Date.now(), sets: [] };
  wake();
  say(W.quick ? "Kurz-Training. Aufwärmen, anderthalb Minuten." : "Aufwärmen, drei Minuten.", "Aufwärmen: Handgelenke und Schultern kreisen, Hampelmänner, ein paar Dead Bugs und langsame Kniebeugen. Tippe auf Aufwärmen beenden, wenn du früher fertig bist.");
  startTimer(W.quick ? 90 : 180, beginWork);
}
function beginWork() {
  clearTimer();
  const e = EX[W.ex];
  if (SESS) SESS.sets = SESS.sets.filter((x) => !(x.ex === e.id && x.set === W.set));
  if (e.type === "hold") {
    W.phase = "prep";
    say(e.name + ", Satz " + W.set + " von " + setsN() + ". Gleich halten.", "Übung " + (W.ex + 1) + " von " + EX.length + ": " + e.name + ", " + levelName(e) + ". Ich zähle fünf Sekunden, dann halten.");
    startTimer(5, beginHold);
  } else {
    W.phase = "work"; say(instruction(), instructionLong()); render();
  }
}
function beginHold() { W.phase = "hold"; say("Los!", "Halte " + settings.hold + " Sekunden."); startTimer(settings.hold, setDone); }
function setDone(reps) {
  const held = W.phase === "hold" ? Math.max(0, Math.round(tm.total - Math.max(0, tm.left) / 1000)) : null;
  if (SESS && (W.phase === "work" || W.phase === "hold")) { const ce = EX[W.ex]; SESS.sets.push({ ex: ce.id, lvl: lvl(ce), set: W.set, reps: typeof reps === "number" ? reps : null, secs: held }); }
  clearTimer(); buzz(20);
  if (W.ex === EX.length - 1 && W.set === setsN()) return finish();
  const nx = nextPos();
  W.phase = "rest";
  say("Pause. Danach " + EX[nx.ex].name + ".", "Gut gemacht. Pause, " + settings.rest + " Sekunden. Als Nächstes: " + EX[nx.ex].name + ", Satz " + nx.set + ".");
  startTimer(settings.rest, () => { W.ex = nx.ex; W.set = nx.set; beginWork(); });
}
function finish() {
  clearTimer(); W.phase = "done"; buzz([40, 60, 40]);
  sessions.push(todayISO()); store.set("fc_sessions", sessions);
  let recIdx = -1;
  if (SESS && SESS.sets.length) { WK.push({ date: SESS.date, min: Math.max(1, Math.round((Date.now() - SESS.t0) / 60000)), sets: SESS.sets, effort: "", q: W.quick ? 1 : 0 }); recIdx = WK.length - 1; saveToday(); }
  SESS = null;
  unwake();
  say("Geschafft. Jetzt kurz dehnen.", "Geschafft! Dehne jetzt noch zwei Minuten Brust, Oberschenkel und Rücken. Trag danach deine Werte unter Fortschritt ein.", true);
  renderProgress(); render(); renderToday();
  if (recIdx >= 0) openSummary(recIdx);
}
function stopWorkout() {
  const msg = isActive() ? "Training beendet." : tm.id ? "Timer gestoppt." : "Es läuft gerade kein Training.";
  clearTimer(); unwake();
  W.phase = "idle"; W.ex = 0; W.set = 1; SESS = null;
  say(msg);
  render();
}
function act(name) {
  const p = W.phase, active = isActive();
  switch (name) {
    case "start":
      if (active) return say("Das Training läuft schon.");
      return startWorkout();
    case "startquick":
      if (active) return say("Das Training läuft schon.");
      return startWorkout(true);
    case "skipex":
      if (!active || p === "warmup") return say("Gerade gibt es keine Übung zum Auslassen.");
      if (W.ex >= EX.length - 1) { if (SESS && SESS.sets.length) return finish(); return stopWorkout(); }
      clearTimer(); W.ex++; W.set = 1; say("Übung ausgelassen.");
      return beginWork();
    case "done":
    case "next":
      if (p === "warmup") return beginWork();
      if (p === "rest" || p === "prep") return skipTimer();
      if (p === "work" || p === "hold") return setDone();
      return say("Tippe auf Training starten, um zu beginnen.");
    case "back":
      if (!active) return say("Es läuft gerade kein Training.");
      if (p === "warmup") return say("Du bist noch beim Aufwärmen.");
      if (p !== "rest") {
        if (W.set > 1) W.set--;
        else if (W.ex > 0) { W.ex--; W.set = setsN(); }
      }
      return beginWork();
    case "pause":
      if (tm.id) {
        if (tm.running) { pauseTimer(); say("Pausiert.", "Pausiert. Tippe auf Fortsetzen, wenn es weitergeht."); }
        else { resumeTimer(); say("Weiter geht’s."); }
        return render();
      }
      return say(active ? "Okay." : "Es läuft gerade kein Training.", active ? "Kein Problem, ich warte. Tippe auf Fertig, wenn du den Satz geschafft hast." : "");
    case "resume":
      if (tm.id && !tm.running) { resumeTimer(); say("Weiter geht’s."); return render(); }
      return say("Es ist nichts pausiert.");
    case "stop":
      return stopWorkout();
  }
}

/* ======================= Anzeige Coach ======================= */
const PH = { idle: "Bereit", warmup: "Aufwärmen", prep: "Gleich geht’s los", work: "Satz läuft", hold: "Halten", rest: "Pause", done: "Geschafft" };
const fmt = (ms) => { const s = Math.max(0, Math.ceil(ms / 1000)); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
const RING = 552.9;
function renderTimer() {
  const p = W.phase, e = EX[Math.min(W.ex, EX.length - 1)];
  $(".coach").dataset.idle = (p === "idle" && !tm.id) ? "1" : "0";
  syncCoach();
  let frac = 0, big = "Bereit", unit = "ca. " + estMinutes() + " Min";
  if (tm.id) {
    frac = Math.max(0, Math.min(1, tm.left / (tm.total * 1000)));
    big = fmt(tm.left);
    unit = { warmup: "Aufwärmen", rest: "Pause", hold: "Halten", prep: "Gleich" }[p] || "Timer";
  } else if (p === "work") { frac = 1; big = e.short; unit = "Wiederholungen"; }
  else if (p === "done") { frac = 1; big = "Fertig"; unit = "gut gemacht"; }
  const bar = $("#ringbar");
  bar.style.strokeDasharray = RING;
  bar.style.strokeDashoffset = RING * (1 - frac);
  bar.dataset.phase = p;
  const bg = $("#ringbig");
  bg.textContent = big;
  bg.classList.toggle("sm", big.length > 4);
  $("#ringunit").textContent = unit;
}
/* Übungsliste im Training: nur die jetzige und die nächste Übung. Was fertig ist, rutscht in die ausklappbare Zeile „Erledigt“. */
let STEPSDONEOPEN = false, STEPSLAST = -1;
document.addEventListener("toggle", (ev) => { const d = ev.target; if (d && d.classList && d.classList.contains("stepsdone")) STEPSDONEOPEN = d.open; }, true);
function renderSteps() {
  const sets = setsN(), ph = W.phase;
  const started = isActive() && ph !== "warmup";
  const done = ph === "done" ? EX.length * sets : (started ? W.ex * sets + (W.set - 1) + (ph === "rest" ? 1 : 0) : 0);
  const cur = Math.min(EX.length, Math.floor(done / sets));
  const pips = (i) => {
    let s = "";
    for (let k = 1; k <= sets; k++) {
      const idx = i * sets + (k - 1);
      let c = "pip";
      if (idx < done) c += " done"; else if (started && idx === done) c += ph === "rest" ? " next" : " now";
      s += '<span class="' + c + '"></span>';
    }
    return s;
  };
  const row = (i, cls, lab, extra) => '<li class="' + cls + '"><div class="stx"><b>' + EX[i].name + '</b><span class="lvl">' + (lab ? '<span class="steplab">' + lab + "</span> " : "") + levelName(EX[i]) + (extra || "") + '</span></div><div class="pips">' + pips(i) + "</div></li>";
  const fin = [];
  for (let i = 0; i < cur; i++) fin.push(row(i, "fin", ""));
  const rows = [];
  if (cur < EX.length) rows.push(row(cur, "cur", started && ph !== "rest" ? "Jetzt" : "Als Nächstes", lastTxt(EX[cur]) ? " · zuletzt " + lastTxt(EX[cur]) : ""));
  if (cur + 1 < EX.length) rows.push(row(cur + 1, "nxt", "Danach"));
  const slide = STEPSLAST !== -1 && STEPSLAST !== cur;
  STEPSLAST = cur;
  $("#steps").innerHTML = (fin.length ? '<details class="stepsdone"' + (STEPSDONEOPEN ? " open" : "") + "><summary>Erledigt (" + fin.length + ')</summary><ul class="steplist">' + fin.join("") + "</ul></details>" : "") +
    (rows.length ? '<ul class="steplist now' + (slide ? " slide" : "") + '">' + rows.join("") + "</ul>" : "");
}

/* Übung austauschen */
let swapSlot = null;
function drawSwap() {
  const slot = swapSlot, vars = slotVariants(slot), cur = EX[EXBASE.findIndex((b) => b.slot === slot)].id, permId = (settings.alt && settings.alt[slot]) || slot;
  const rowNote = slot === "row" ? '<p class="swnote">Wenn dein Tisch nicht sicher hält, nimm Rucksack-Rudern oder Superman-Rudern. Probiere Handtuch-Rudern nur an einer stabilen Tür, die sich von dir weg öffnet.</p>' : "";
  $("#dlg-swap").innerHTML = '<div class="dlg"><div class="dlg-head"><div><h3>Übung austauschen: ' + SLOTNAME[slot] + '</h3><p class="muted">Wähle, wie du diese Muskelgruppe trainieren willst. „Dauerhaft“ gilt ab jetzt immer, „Nur heute“ nur bis Mitternacht.</p></div><button class="btn icon" data-close aria-label="Schließen">' + ic("close") + "</button></div>" + rowNote +
    '<div class="swlist">' + vars.map((e) => {
      const li = lvl(e), tags = (e.id === cur ? '<span class="swtag">Aktuell</span>' : "") + (e.id === permId && permId !== slot ? '<span class="swtag">Dauerhaft</span>' : "");
      return '<div class="swopt' + (e.id === cur ? " cur" : "") + '"><h4>' + e.name + tags + '</h4><p class="small muted">Du brauchst: ' + e.need + "</p><p>" + e.why + '</p><p class="small">Deine Stufe: ' + (li + 1) + " von " + e.ladder.length + ", " + e.ladder[li] + '</p><div class="row">' + (V3A[e.id] ? '<button class="btn" type="button" data-v3="' + e.id + '" data-i="' + li + '">' + ic("info") + "<span>3D ansehen</span></button>" : "") +
        (e.id !== permId ? '<button class="btn primary" type="button" data-swap="' + e.id + '" data-mode="perm">Dauerhaft nehmen</button>' : "") + (e.id !== cur ? '<button class="btn" type="button" data-swap="' + e.id + '" data-mode="day">Nur heute</button>' : "") + "</div></div>";
    }).join("") + "</div>" + swapLocked(slot) + "</div>";
}
function openSwap(slot, src) { if (!SLOTNAME[slot]) return; swapSlot = slot; drawSwap(); showDialog($("#dlg-swap"), src || null); }
function doSwap(id, mode) {
  const e = exById(id); if (!e) return;
  if (mode === "perm") { settings.alt = settings.alt || {}; settings.alt[e.slot] = id; if (SWAPD.map) delete SWAPD.map[e.slot]; store.set("fc_settings", settings); }
  else { if (SWAPD.date !== todayISO()) SWAPD = { date: todayISO(), map: {} }; SWAPD.map[e.slot] = id; }
  applyAlts(); coachKey = ""; renderEx(); render(); renderToday(); if (swapSlot) drawSwap();
}
function swapBtn() {
  const p = W.phase; if (!["prep", "rest"].includes(p)) return "";
  const e = EX[Math.min(p === "rest" ? nextPos().ex : W.ex, EX.length - 1)];
  return slotVariants(e.slot).length > 1 ? '<button class="btn icon" type="button" data-swapopen="' + e.slot + '" aria-label="Austauschen" title="Austauschen">' + ic("repeat") + "</button>" : "";
}
function renderActions() {
  const p = W.phase, active = isActive(), paused = !!tm.id && !tm.running;
  const btn = (a, label, icon, cls) => '<button class="btn ' + (cls || "") + '" data-act="' + a + '">' + ic(icon) + "<span>" + label + "</span></button>";
  const ibtn = (a, label, icon) => '<button class="btn icon" type="button" data-act="' + a + '" aria-label="' + label + '" title="' + label + '">' + ic(icon) + "</button>";
  let h = "";
  if (!active) {
    h += btn("start", p === "done" ? "Noch mal starten" : "Training starten", "play", "primary lg");
    h += btn("startquick", "Kurz, ca. " + estMinutes(true) + " Min", "play");
    if (tm.id) h += btn("stop", "Timer stoppen", "stop");
  } else {
    if (p === "work" && EX[W.ex].type !== "hold") h += repChips(EX[W.ex]);
    if (p === "work" || p === "hold") h += btn("done", "Fertig", "check", "primary lg");
    else h += btn("next", p === "warmup" ? "Aufwärmen beenden" : "Überspringen", "next", "primary lg");
    h += '<div class="mini">' + (p !== "warmup" ? ibtn("back", "Zurück", "back") + ibtn("skipex", "Auslassen", "next") : "") + (tm.id ? ibtn("pause", paused ? "Fortsetzen" : "Pause", paused ? "play" : "pause") : "") + swapBtn() + ibtn("stop", "Stopp", "stop") + "</div>";
  }
  $("#actions").innerHTML = h;
}
function render() {
  const p = W.phase, paused = !!tm.id && !tm.running;
  const shown = p === "rest" ? nextPos() : { ex: W.ex, set: W.set };
  const e = EX[Math.min(shown.ex, EX.length - 1)];
  const ph = $("#phase");
  ph.dataset.phase = paused ? "idle" : p;
  ph.textContent = paused ? "Pausiert" : PH[p];
  let title = "Ganzkörper-Training", sub = EX.length + " Übungen, " + settings.sets + " Sätze, ca. " + estMinutes() + " Minuten", info = "";
  if (p === "warmup") { title = "Aufwärmen"; sub = "Handgelenke, Schultern, Hampelmänner, Dead Bugs"; }
  else if (p === "done") { title = "Training geschafft"; sub = "Dehnen nicht vergessen und Werte eintragen"; }
  else if (["prep", "work", "hold", "rest"].includes(p)) {
    title = e.name;
    sub = W.quick ? "Kurz-Training" : "";
    info = (p === "rest" ? "Als Nächstes · " : "") + "Übung " + (shown.ex + 1) + "/" + EX.length + ", Satz " + shown.set + "/" + setsN();
  }
  $("#title").textContent = title;
  $("#sub").textContent = sub;
  $("#setinfo").textContent = info;
  renderSteps(); renderActions(); renderTimer(); coachFig();
  if ($("#panel-heute") && !$("#panel-heute").hidden) renderToday();
}

/* ======================= Rezepte ======================= */
const F = { q: "", meal: "", diet: "", time: 0, minProt: false, prep: false, nocook: false, cheap: false, work: false, light: false, fav: false, sort: "protein" };
let EXC = store.get("fc_exc", []);
let FAV = store.get("fc_fav", []);
let MYD = store.get("fc_dishes", []);
const PREPDEF = { people: 2, days: 6, n: 2, brk: true, snk: true, eco: true, week: "", main: [], b: "", s: "", done: {}, plans: {}, autoDay: "" };
let PREP = Object.assign({}, PREPDEF, store.get("fc_prep", {}));
const isExc = (r) => EXC.some((x) => (x.startsWith("z:") ? r.ing.some((i) => i[4] === x.slice(2)) : x.startsWith("r:") ? r.id === x.slice(2) : r.contains.includes(x)));
const zname = (k) => { const n = (PRICE[k] && PRICE[k].n || k).replace(/\s*\(.*?\)/g, "").replace(/^Scheibe /, "").replace(/^stückige /, "Stückige "); return n.charAt(0).toUpperCase() + n.slice(1); };
const excLabel = () => { const cat = EXC.filter((x) => !/^[zr]:/.test(x)), z = EXC.filter((x) => x.startsWith("z:")).map((x) => zname(x.slice(2))), r = EXC.filter((x) => x.startsWith("r:")).length; const all = cat.concat(z); if (r) all.push(r + (r === 1 ? " ausgeblendetes Rezept" : " ausgeblendete Rezepte")); return all.length ? " · ohne " + all.join(", ") : ""; };
function toggleExc(code) { EXC = EXC.includes(code) ? EXC.filter((x) => x !== code) : EXC.concat(code); store.set("fc_exc", EXC); }
const EXC_ALL = ["Hülsenfrüchte", "Rindfleisch", "Schwein", "Geflügel", "Ei", "Nüsse"];
const FDEF = JSON.stringify(F);
const FKEYS = ["meal", "diet", "time", "minProt", "prep", "nocook", "cheap", "work", "light", "fav"];
/* Suchtext je Rezept (Titel und Zutaten, klein geschrieben), nur einmal gebaut statt bei jedem Tastendruck für alle Rezepte */
const RHAY = new WeakMap();
function rHay(r) { let t = RHAY.get(r); if (t === undefined) { t = (r.title + " " + r.ing.map((i) => i[2]).join(" ")).toLowerCase(); RHAY.set(r, t); } return t; }
function filtered() {
  const q = F.q.trim().toLowerCase();
  const list = RECIPES.filter((r) =>
    (!F.meal || r.meal === F.meal) &&
    (!F.diet || (F.diet === "vegan" ? r.diet === "vegan" : r.diet !== "omni")) &&
    (!F.time || r.time <= F.time) &&
    (!F.minProt || r.protein >= 30) &&
    (!F.prep || r.tags.includes("Meal-Prep")) &&
    (!F.nocook || r.tags.includes("Ohne Kochen")) &&
    (!F.cheap || r.tags.includes("Günstig")) &&
    (!F.work || r.tags.includes("Für die Arbeit")) &&
    (!F.light || r.tags.includes("Leicht")) &&
    !isExc(r) &&
    (!F.fav || FAV.includes(r.id)) &&
    (!q || rHay(r).includes(q) || r.tags.some((t) => t.toLowerCase().includes(q))));
  const by = { protein: (a, b) => b.protein - a.protein, kcal: (a, b) => a.kcal - b.kcal, time: (a, b) => a.time - b.time, dens: (a, b) => b.protein / b.kcal - a.protein / a.kcal, cost: (a, b) => a.cost - b.cost, ppe: (a, b) => b.protein / b.cost - a.protein / a.cost, title: (a, b) => a.title.localeCompare(b.title, "de") };
  return list.sort(by[F.sort]);
}
function filterActive() { const base = JSON.parse(FDEF); return FKEYS.some((k) => F[k] !== base[k]) || F.q.trim() !== ""; }
function resetFilters() { const s = F.sort; Object.assign(F, JSON.parse(FDEF)); F.sort = s; renderRecipes(); }
let FOPEN = false;
let IOPEN = false;
let INGKEYS = null;
function ingexHTML() {
  const keys = INGKEYS || (INGKEYS = [...new Set(RECIPES.flatMap((r) => r.ing.map((i) => i[4]).filter(Boolean)))].filter((k) => PRICE[k]).sort((a, b) => zname(a).localeCompare(zname(b), "de")));
  const nz = EXC.filter((x) => x.startsWith("z:")).length, hid = EXC.filter((x) => x.startsWith("r:"));
  return '<details class="more ingex" id="ingex"' + (IOPEN ? " open" : "") + "><summary>Zutaten, die ich nicht mag" + (nz ? '<span class="badge">' + nz + "</span>" : "") + "</summary>" +
    '<p class="small muted">Rezepte mit diesen Zutaten verschwinden aus Liste, Glücksrad und Tagesvorschlag.</p><div class="fgroup">' +
    keys.map((k) => '<button class="fchip" data-excz="' + k + '" aria-pressed="' + EXC.includes("z:" + k) + '">' + zname(k) + "</button>").join("") + "</div>" +
    (hid.length ? '<div class="fgroup"><span class="lbl">Ausgeblendete Rezepte, antippen zum Zurückholen</span>' + hid.map((x) => { const r = byId(x.slice(2)); return r ? '<button class="fchip" data-excr="' + r.id + '">' + r.title + " ×</button>" : ""; }).join("") + "</div>" : "") + "</details>";
}
const SORTS = [["protein", "Meiste Eiweiß"], ["kcal", "Wenig Kalorien"], ["time", "Kurze Zeit"], ["dens", "Eiweiß je Kalorie"], ["cost", "Günstig zuerst"], ["ppe", "Eiweiß je Euro"], ["title", "Name"]];
function renderFilters() {
  const chip = (g, v, label, on) => '<button class="fchip" data-f="' + g + '" data-v="' + v + '" aria-pressed="' + (on ? "true" : "false") + '">' + label + "</button>";
  const tog = (k, label) => '<button class="fchip" data-ft="' + k + '" aria-pressed="' + (F[k] ? "true" : "false") + '">' + label + "</button>";
  const base = JSON.parse(FDEF);
  const nAct = FKEYS.filter((k) => k !== "meal" && F[k] !== base[k]).length + EXC.length;
  $("#filters").innerHTML =
    '<div class="search">' + ic("search") + '<input type="search" id="rsearch" placeholder="Suchen, z. B. Quark, Linsen" value="' + F.q.replace(/"/g, "&quot;") + '" aria-label="Rezepte suchen"></div>' +
    '<div class="fgroup">' + ["Frühstück", "Mittag/Abend", "Snack"].map((m) => chip("meal", m, m, F.meal === m)).join("") + "</div>" +
    '<div class="fline"><details class="more" id="fmore"' + (FOPEN ? " open" : "") + '><summary>Weitere Filter' + (nAct ? '<span class="badge">' + nAct + "</span>" : "") + "</summary>" +
    '<div class="fgroup"><span class="lbl">Ernährung</span>' + chip("diet", "vegetarisch", "Vegetarisch", F.diet === "vegetarisch") + chip("diet", "vegan", "Vegan", F.diet === "vegan") + "</div>" +
    '<div class="fgroup"><span class="lbl">Zeit</span>' + chip("time", "10", "bis 10 Min", F.time === 10) + chip("time", "20", "bis 20 Min", F.time === 20) + "</div>" +
    '<div class="fgroup"><span class="lbl">Extras</span>' + tog("minProt", "Mind. 30 g Eiweiß") + tog("work", "Für die Arbeit") + tog("light", "Leicht") + tog("prep", "Meal-Prep") + tog("nocook", "Ohne Kochen") + tog("cheap", "Günstig") + tog("fav", "♥ Lieblinge") + "</div>" +
    '<div class="fgroup"><span class="lbl">Ohne</span>' + EXC_ALL.map((x) => '<button class="fchip" data-exc="' + x + '" aria-pressed="' + (EXC.includes(x) ? "true" : "false") + '">' + x + "</button>").join("") + "</div>" +
    ingexHTML() +
    (filterActive() ? '<div class="fgroup"><button class="fchip" data-freset="1">Filter zurücksetzen</button></div>' : "") +
    '</details><select id="rsort" class="fsort" aria-label="Sortieren">' + SORTS.map((o) => '<option value="' + o[0] + '"' + (F.sort === o[0] ? " selected" : "") + ">" + o[1] + "</option>").join("") + "</select></div>";
}
document.addEventListener("toggle", (ev) => { if (ev.target && ev.target.id === "pricebox") PRICEOPEN = ev.target.open; if (ev.target && ev.target.id === "fmore") FOPEN = ev.target.open; if (ev.target && ev.target.id === "radmore") ROPEN = ev.target.open; if (ev.target && ev.target.id === "ingex") IOPEN = ev.target.open; }, true);
/* Die Liste zeigt zuerst 48 Rezepte und lädt per Knopf mehr nach. So bleibt sie auch mit 1000 Rezepten schnell. */
const RPAGE = 48;
let rShow = RPAGE, rSig = "";
function rcardHTML(r) {
  return '<button class="rcard" data-recipe="' + r.id + '"><h4>' + (FAV.includes(r.id) ? '<span class="favmark" aria-label="Lieblingsrezept">♥</span> ' : "") + r.title + '</h4>' +
    '<div class="tags"><span class="tag">' + r.meal + '</span>' + (r.diet !== "omni" ? '<span class="tag g">' + (r.diet === "vegan" ? "Vegan" : "Vegetarisch") + "</span>" : "") + r.tags.slice(0, 2).map((t) => '<span class="tag">' + t + "</span>").join("") + "</div>" +
    '<div class="rnum"><span class="pro">' + r.protein + '<small>g Eiweiß</small></span><span class="rsub">' + r.kcal + " kcal, " + r.time + " Min, ca. " + eur(r.cost) + "</span></div></button>";
}
function renderRecipes(more) {
  const list = filtered();
  const sig = JSON.stringify(F) + "|" + EXC.join(","), same = sig === rSig;
  if (!same) { rSig = sig; rShow = RPAGE; }
  const before = rShow;
  if (more) rShow += RPAGE * 2;
  const moreBtn = (rest) => (rest > 0 ? '<div class="rmore"><button class="btn" data-rmore="1">Mehr anzeigen (' + rest + " weitere)</button></div>" : "");
  /* Mehr anzeigen: nur die neuen Karten anhängen, die Liste und die Filter bleiben unberührt */
  if (more && same && $("#rgrid").querySelector(".rmore")) {
    const grid = $("#rgrid"), old = grid.querySelector(".rmore"); old.remove();
    grid.insertAdjacentHTML("beforeend", list.slice(before, rShow).map(rcardHTML).join("") + moreBtn(list.length - Math.min(rShow, list.length)));
    const c = grid.querySelectorAll(".rcard")[before]; if (c) c.focus({ preventScroll: true });
    return;
  }
  $("#rcount").textContent = list.length + " von " + RECIPES.length + " Rezepten" + excLabel();
  const shown = list.slice(0, rShow), rest = list.length - shown.length;
  $("#rgrid").innerHTML = list.length ? shown.map(rcardHTML).join("") + moreBtn(rest)
    : '<div class="card empty"><h3>Keine Treffer</h3><p class="muted">Lockere die Filter etwas.</p><div class="row" style="justify-content:center"><button class="btn" data-freset="1">Filter zurücksetzen</button></div></div>';
  renderFilters();
  if (more) { const c = $("#rgrid").querySelectorAll(".rcard")[before]; if (c) c.focus({ preventScroll: true }); }
}
const RAWKEYS = ["haehn", "pute", "phack", "rhack", "ghack", "schnitzel", "haehnst", "reis", "nudel", "linse"];
let openId = null, portions = 1;
const UNIT_SPOKEN = { g: "Gramm", ml: "Milliliter", EL: "Esslöffel", TL: "Teelöffel" };
function ingText(i, spoken) {
  if (i[0] == null) return i[2];
  let v = i[0] * portions;
  if (i[1] === "g" || i[1] === "ml") v = v >= 50 ? Math.round(v / 5) * 5 : Math.round(v);
  else v = Math.round(v * 2) / 2;
  let n;
  if (spoken) n = v === 0.5 ? "eine halbe" : nf(v);
  else n = v === 0.5 ? "½" : (v % 1 === 0.5 ? Math.floor(v) + "½" : nf(v));
  const unit = i[1] ? " " + (spoken ? UNIT_SPOKEN[i[1]] || i[1] : i[1]) : "";
  const name = (v !== 1 && v !== 0.5 && i[3]) ? i[3] : i[2];
  return n + unit + " " + name;
}
const reduceMotion = () => !!(window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches);
/* Textgröße (Einstellungen, bis 200 %) als Ersatz für Zoom. Die Zoom-Sperre selbst steht in js/zoom.js. */
function applyTextSize() {
  document.documentElement.style.fontSize = settings.text && settings.text !== 100 ? settings.text + "%" : "";
  document.documentElement.toggleAttribute("data-big", settings.text >= 130);
  if (typeof moveBoth === "function") try { moveBoth(); drawWheel(); } catch (e) {}
}
const isSheet = () => !!(window.matchMedia && matchMedia("(max-width: 640px)").matches);
function showDialog(d, src) {
  const was = d.open;
  d._cl = (d._cl || 0) + 1;
  if (!was) { try { d.showModal(); } catch (e) { d.setAttribute("open", ""); } }
  if (was || reduceMotion() || !d.animate) return;
  let frames;
  if (isSheet()) frames = [{ transform: "translateY(36px)", opacity: 0 }, { transform: "none", opacity: 1 }];
  else {
    const r = d.getBoundingClientRect();
    d.style.transformOrigin = src ? (src.getBoundingClientRect().left + src.offsetWidth / 2 - r.left) + "px " + (src.getBoundingClientRect().top + src.offsetHeight / 2 - r.top) + "px" : "50% 50%";
    frames = [{ transform: "scale(0.9)", opacity: 0 }, { transform: "none", opacity: 1 }];
  }
  d.animate(frames, { duration: 320, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)" });
}
function closeDialog(d) {
  if (!d || !d.open) return;
  if (reduceMotion() || !d.animate) return d.close();
  const out = isSheet() ? [{ transform: "none", opacity: 1 }, { transform: "translateY(36px)", opacity: 0 }] : [{ transform: "none", opacity: 1 }, { transform: "scale(0.94)", opacity: 0 }];
  const a = d.animate(out, { duration: 200, easing: "cubic-bezier(0.4, 0, 0.6, 1)" });
  const my = d._cl = (d._cl || 0) + 1;
  const fin = () => { if (d._cl === my && d.open) d.close(); };
  a.onfinish = fin; a.oncancel = fin; setTimeout(fin, 320);
}
function openRecipe(id, read, src) {
  const r = RECIPES.find((x) => x.id === id); if (!r) return;
  if (openId !== id) portions = 1;
  openId = id;
  drawRecipe();
  showDialog($("#dlg-recipe"), src);
  if (read) readRecipe(r);
}
function drawRecipe() {
  const r = RECIPES.find((x) => x.id === openId); if (!r) return;
  $("#dlg-recipe").innerHTML =
    '<div class="dlg"><div class="dlg-head"><div><h3>' + r.title + '</h3><p class="kicker">' + r.meal + ', ' + r.time + ' Min</p></div><button class="btn icon" data-close aria-label="Schließen">' + ic("close") + "</button></div>" +
    '<div class="rmeta"><span class="big">' + Math.round(r.protein * portions) + '<small>g Eiweiß</small></span><span class="big">' + Math.round(r.kcal * portions / 5) * 5 + '<small>' + (portions === 1 ? "kcal" : "kcal gesamt") + '</small></span><span class="big"><small class="pre">ca.</small>' + eur(r.cost * portions).replace("\u00a0€", "") + '<small>€ bei Lidl</small></span></div>' +
    '<div class="tags">' + (r.diet !== "omni" ? '<span class="tag g">' + (r.diet === "vegan" ? "Vegan" : "Vegetarisch") + "</span>" : "") + r.tags.map((t) => '<span class="tag">' + t + "</span>").join("") + (r.veg >= 50 ? '<span class="tag g">Gemüse ca. ' + r.veg + " g</span>" : "") + "</div>" +
    '<div class="row"><span class="small muted">Portionen</span><span class="stepper"><button class="btn icon" data-por="-1" aria-label="Weniger Portionen">−</button><b>' + portions + '</b><button class="btn icon" data-por="1" aria-label="Mehr Portionen">+</button></span></div>' +
    "<h4>Zutaten</h4><ul>" + r.ing.map((i) => "<li>" + ingText(i, false) + "</li>").join("") + "</ul>" +
    (r.ing.some((i) => RAWKEYS.includes(i[4])) ? '<p class="small muted">Fleisch ist roh gewogen, Reis, Nudeln und Linsen trocken. Beim Garen ändert sich das Gewicht, die Nährwerte gelten für die Menge in der Liste.</p>' : "") +
    "<h4>Zubereitung</h4><ol>" + r.steps.map((s) => "<li>" + s + "</li>").join("") + "</ol>" +
    (r.ing.some((i) => i[4] === "erdb") ? '<p class="note"><b>Tiefkühl-Erdbeeren:</b> Erhitze sie vor dem Essen mindestens 2 Minuten auf über 90 °C und lass sie abkühlen. Das empfiehlt das BfR wegen möglicher Viren. Frische Erdbeeren gründlich waschen.</p>' : "") + (r.tip ? '<p class="note">' + r.tip + "</p>" : "") + (r.note ? '<p class="note">' + r.note + "</p>" : "") +
    '<p class="small muted">Nährwerte sind gerundete Richtwerte aus üblichen Tabellen. Marken weichen ab.</p>' +
    '<div class="row"><button class="btn primary" data-cartadd="' + r.id + '">Zur Einkaufsliste</button><button class="btn" data-eatrec="' + r.id + '">Heute gegessen</button></div>' +
    '<div class="row"><button class="btn" type="button" data-cook="' + r.id + '">Kochmodus</button><button class="btn" type="button" data-fav="' + r.id + '" aria-pressed="' + FAV.includes(r.id) + '">' + ic("heart") + "<span>Lieblingsrezept</span></button>" + '<button class="btn" type="button" data-hide="' + r.id + '">Nicht mehr vorschlagen</button></div>' +
    '<div class="row"><button class="btn lg" type="button" data-close>Schließen</button></div></div>';
}
function readRecipe(r) { say(r.title); }
/* Kochmodus: Zutaten abhaken, dann Schritt für Schritt, mit Timer */
const CK = { r: null, i: 0, timer: 0, left: 0, name: "" };
function ckStop() { clearInterval(CK.timer); CK.timer = 0; CK.left = 0; }
function ckMinutes(t) { const m = [...t.matchAll(/(\d+)(?:\s*bis\s*(\d+))?\s*Minuten?/g)]; if (!m.length) return 0; const x = m[m.length - 1]; return parseInt(x[2] || x[1], 10); }
function ckDraw() {
  const r = CK.r; if (!r) return;
  const n = r.steps.length, i = CK.i;
  let body;
  if (i === 0) body = '<h4>Zutaten bereitlegen</h4><ul class="ckings">' + r.ing.map((x, k) => '<li><label><input type="checkbox" data-ckchk="' + k + '"> <span>' + ingText(x, false) + "</span></label></li>").join("") + "</ul>";
  else if (i <= n) { const st = r.steps[i - 1], mins = ckMinutes(st); body = '<p class="cktext">' + st + "</p>" + (mins ? '<div class="row"><button class="btn primary" type="button" data-cktimer="' + mins + '">Timer ' + mins + " Min</button></div>" : "") + '<div class="cktimer" id="cktimer" role="timer" aria-live="off"></div>'; }
  else body = '<h4>Guten Appetit!</h4><p>' + (r.tip ? r.tip : "Lass es dir schmecken.") + '</p><div class="row"><button class="btn primary" data-eatrec="' + r.id + '">Heute gegessen</button><button class="btn" type="button" data-ckclose="1">Fertig</button></div>';
  $("#dlg-cook").innerHTML = '<div class="dlg ck"><div class="dlg-head"><div><h3>' + r.title + '</h3><p class="kicker">' + (i === 0 ? "Vorbereiten" : i <= n ? "Schritt " + i + " von " + n : "Geschafft") + '</p></div><button class="btn icon" data-ckclose="1" aria-label="Kochmodus schließen">' + ic("close") + "</button></div>" +
    '<div class="ckbar"><i style="width:' + Math.round(i / (n + 1) * 100) + '%"></i></div>' + body +
    '<div class="row cknav"><button class="btn lg" type="button" data-ckgo="-1"' + (i === 0 ? " disabled" : "") + '>Zurück</button><button class="btn primary lg" type="button" data-ckgo="1"' + (i > n ? " disabled" : "") + ">" + (i === 0 ? "Los geht’s" : i < n ? "Weiter" : "Fertig") + "</button></div></div>";
}
function openCook(id, src) {
  const r = byId(id); if (!r) return;
  CK.r = r; CK.i = 0; ckStop(); portions = portions || 1; ckDraw(); wake();
  closeDialog($("#dlg-recipe")); setTimeout(() => showDialog($("#dlg-cook"), src), reduceMotion() ? 0 : 120);
}
function ckGo(d) { ckStop(); CK.i = Math.max(0, Math.min(CK.r.steps.length + 1, CK.i + d)); ckDraw(); }
function ckTimer(min) {
  ckStop(); CK.left = min * 60;
  const el = () => $("#cktimer"), show = () => { if (el()) el().textContent = Math.floor(CK.left / 60) + ":" + String(CK.left % 60).padStart(2, "0"); };
  show();
  CK.timer = setInterval(() => { CK.left--; if (CK.left <= 0) { ckStop(); if (el()) el().textContent = "Fertig!"; beep(); buzz([200, 100, 200]); } else show(); }, 1000);
}

/* ======================= Übungen, Ernährung, Tipps ======================= */
const weekNo = () => { if (!sessions.length) return 1; const first = sessions.slice().sort()[0], d = (new Date(todayISO() + "T12:00:00") - new Date(first + "T12:00:00")) / 86400000; return Math.max(1, Math.floor(d / 7) + 1); };
function fatigueHint() {
  const tot = (w) => w.sets.reduce((a, x) => a + (x.reps || 0) + (x.secs || 0) / 5, 0), k = WK.filter((x) => !x.q).slice(-3);
  if (k.length < 3) return "";
  const t2 = tot(k[0]), t1 = tot(k[1]), t0 = tot(k[2]);
  return t0 < t1 && t1 < t2 && t0 < 0.85 * t2 ? '<p class="note">Deine letzten Einheiten wurden schwächer. Prüfe Schlaf, Essen und Stress. Wenn es so bleibt, mach eine Woche mit einem Satz weniger pro Übung. Feste Pausenwochen bringen laut einer Studie von 2024 keinen Vorteil, sie sind nur bei Bedarf sinnvoll.</p>' : "";
}

/* Lange Infokarten einklappen: Titel bleibt sichtbar, Text erst nach Tipp */
function foldCards(root, keep) {
  if (!root) return;
  root.querySelectorAll(":scope > .card, :scope > .grid2 > .card").forEach((card, i) => {
    if (card.hasAttribute("data-nofold") || i < (keep || 0) || card.tagName === "DETAILS") return;
    const h = card.querySelector("h3, h4"); if (!h) return;
    const det = document.createElement("details"), sum = document.createElement("summary"), body = document.createElement("div");
    det.className = card.className + " acc"; sum.innerHTML = '<span class="acct">' + h.innerHTML + "</span>"; body.className = "accbody";
    h.remove();
    while (card.firstChild) body.appendChild(card.firstChild);
    body.querySelectorAll(":scope > div:empty").forEach((d) => d.remove());
    const tx = body.querySelector("p, li"), tt = body.querySelector(".shop") ? "Checkliste zum Abhaken" : tx ? tx.textContent.replace(/\s+/g, " ").trim() : "";
    if (tt) { const sub = document.createElement("span"); sub.className = "accsub"; sub.textContent = tt.length > 72 ? tt.slice(0, 70).replace(/\s\S*$/, "") + " …" : tt; sum.querySelector(".acct").appendChild(sub); }
    det.append(sum, body); card.replaceWith(det);
  });
}
function phaseHTML() {
  const w = weekNo(), rec = w <= 2 ? 2 : 3, cur = settings.sets;
  const txt = w <= 2 ? "Technik lernen. Lass bei jedem Satz noch ein paar Wiederholungen übrig." : w <= 8 ? "Aufbau. Lass 1 bis 3 Wiederholungen übrig, steigere erst die Wiederholungen, dann die Stufe." : "Weiter aufbauen. Klappt alles sauber, nimm die nächste Stufe.";
  return '<div class="card phase" data-nofold><div class="rday-h"><h3>Woche ' + w + '</h3><span class="rtot">' + cur + " Sätze pro Übung</span></div><p>" + txt + "</p>" + (w <= 8 && cur !== rec ? '<div class="row"><button class="btn primary" type="button" data-setsrec="' + rec + '">Auf ' + rec + " Sätze stellen</button></div>" : "") + fatigueHint() + "</div>";
}
/* Hat die letzte Einheit auf dieser Stufe gezeigt, dass die nächste Stufe dran ist? */
function exUp(e) {
  const li = lvl(e);
  for (let i = WK.length - 1; i >= 0; i--) { const w = WK[i], mine = w.sets.filter((x) => x.ex === e.id && x.lvl === li); if (!mine.length) continue; if (!w.q) { const ev = evalEx(e, mine); return !!(ev && ev.status === "up"); } break; }
  return false;
}
function exHintHTML(e) {
  const lt = lastTxt(e), li = lvl(e); if (!lt) return "";
  const up = exUp(e);
  const nxt = e.ladder[li + 1];
  return '<p class="small muted exlast">Zuletzt: ' + lt + "</p>" + (up && nxt ? '<p class="small exready"><b>Bereit für die nächste Stufe:</b> ' + esc(nxt) + '</p><div class="row"><button class="btn sm primary" type="button" data-lvlup="' + e.id + '">Stufe hoch</button></div>' : "");
}
function renderEx() {
  $("#panel-uebungen").innerHTML = phaseHTML() +
    '<div class="card"><h3>So trainierst du</h3><ul>' +
    "<li>Ganzkörper, " + trainDays() + " Mal pro Woche, dazwischen mindestens ein Ruhetag.</li>" +
    "<li>Pausen 60 bis 90 Sekunden. Beende jeden Satz 1 bis 3 Wiederholungen vor dem Versagen.</li>" +
    "<li>Schaffst du bei allen Sätzen die obere Zahl sauber, geh eine Stufe weiter.</li></ul></div>" +
    '<div class="grid2">' + EX.map((e) => {
      const li = lvl(e), nvar = slotVariants(e.slot).length;
      return '<article class="card excard" data-nofold><div class="exhead"><div><h3>' + e.name + '</h3><p class="kicker">' + e.reps + (e.id !== e.slot ? " · Alternative" : "") + '</p></div>' + (V3A[e.id] ? '<button class="btn icon sm infobtn" type="button" data-v3="' + e.id + '" aria-label="So geht’s: 3D-Ansicht für ' + e.name + '" title="3D-Ansicht">' + ic("info") + "</button>" : "") + "</div>" +
        '<div class="exnow"><b>' + levelName(e) + '</b><div class="meter"><span style="width:' + Math.round((li + 1) / e.ladder.length * 100) + '%"></span></div><span class="small muted">Stufe ' + (li + 1) + " von " + e.ladder.length + "</span></div>" +
        exHintHTML(e) +
        '<div class="row"><button class="btn" data-lvl="' + e.id + '" data-d="-1">Leichter</button><button class="btn" data-lvl="' + e.id + '" data-d="1">Schwerer</button>' + (nvar > 1 ? '<button class="btn" type="button" data-swapopen="' + e.slot + '">' + ic("repeat") + "<span>Tauschen</span></button>" : "") + "</div>" +
        '<details class="exmore"><summary>Anleitung und alle Stufen</summary><p>' + e.cue + '</p><ol class="ladder">' + e.ladder.map((n, i) => '<li class="' + (i === li ? "cur" : "") + '">' + n + (i === li ? " (deine Stufe)" : "") + (V3A[e.id] ? '<button class="v3mini" type="button" data-v3="' + e.id + '" data-i="' + i + '" aria-label="3D-Ansicht: ' + n + '">3D</button>' : "") + '</li>').join("") + '</ol><p class="mistake"><b>Häufige Fehler:</b> ' + e.mistakes + '</p><p class="small muted">Du brauchst: ' + e.need + "</p></details></article>";
    }).join("") + "</div>" +
    '<h3 style="margin-top:6px">Zusatz</h3><div class="grid2">' + EXTRAS.map((x) => '<article class="card flat"><h4>' + x.name + '</h4><p class="kicker">' + x.sub + "</p><p>" + x.text + "</p>" + (V3KEY[x.name] ? '<div class="row"><button class="btn" type="button" data-v3="' + V3KEY[x.name] + '">' + ic("info") + "<span>3D-Ansicht</span></button></div>" : "") + "</article>").join("") + "</div>";
  $("#panel-uebungen").insertAdjacentHTML("beforeend", '<article class="card flat" data-nofold><h4>Wie geht es weiter?</h4><p>Neue Übungen, Zusatz-Ausrüstung mit Kauflinks und deine nächsten Ziele findest du im Tab „Ausblick“.</p><div class="row"><button class="btn" type="button" data-goto="ausblick">Ausblick ansehen</button></div></article>');
  foldCards($("#panel-uebungen"));
}
function bodyCalc() {
  const w = prof.weight, h = prof.height;
  return {
    pLo: Math.round(w * 1.6), pHi: Math.round(w * 2.0),
    meal: Math.max(20, Math.round(w * 0.25)),
    lossLo: Math.round(w * 0.005 * 10) / 10, lossHi: Math.round(w * 0.01 * 10) / 10,
    waist: Math.round(h / 2 * 10) / 10
  };
}
function calcStats(c) {
  return '<div class="stat"><span class="big">' + c.pLo + "–" + c.pHi + '<small>g</small></span><span>Eiweiß pro Tag (1,6 bis 2,0 g je kg)</span></div>' +
    '<div class="stat"><span class="big">' + c.meal + "–40" + '<small>g</small></span><span>Eiweiß pro Mahlzeit, über den Tag verteilt</span></div>' +
    '<div class="stat"><span class="big">' + nf(c.lossLo) + "–" + nf(c.lossHi) + '<small>kg</small></span><span>Abnahme pro Woche (0,5 bis 1 % Körpergewicht), starte beim unteren Wert</span></div>' +
    '<div class="stat"><span class="big">' + nf(c.waist) + '<small>cm</small></span><span>Taille unter der halben Körpergröße</span></div>';
}
function dayCard() {
  return '<div class="card"><h3>Wenn du morgens wenig isst</h3>' +
    "<p>Ein großes Frühstück ist kein Muss. Wichtiger ist, dass du über den Tag auf dein Eiweißziel kommst und es auf mehrere Mahlzeiten verteilst. Die Fachgesellschaft ISSN empfiehlt etwa 20 bis 40 g pro Mahlzeit, gleichmäßig über den Tag verteilt, und 30 bis 40 g Casein (zum Beispiel Quark) vor dem Schlafen.</p>" +
    "<ul><li>Mittag und Abend: je 35 bis 45 g Eiweiß</li><li>Zwei Snacks: je 20 bis 25 g</li><li>Optional ein kleines Frühstück: 20 bis 25 g, zum Beispiel Skyr mit Banane</li><li>Vor dem Schlafen: Quark mit 25 bis 30 g Eiweiß</li></ul>" +
    '<div class="grid2">' + DAYS.map((d) => '<div class="card flat"><h4>' + d.name + "</h4><ul>" +
      d.items.map((i) => "<li>" + i.title + " <span class='muted'>(" + i.protein + " g, " + i.kcal + " kcal)</span></li>").join("") +
      "</ul><p><b>" + d.protein + " g Eiweiß</b> und " + d.kcal + " kcal</p></div>").join("") + "</div>" +
    '<p class="note">Die Beispiele zeigen vor allem, wie sich das Eiweiß verteilt. Ob die Kalorien zu deinem Ziel passen, hängt von deinem Verbrauch ab. Passe die Mengen mit dem Portionen-Regler an.</p></div>';
}
function oatsCard() {
  const o = RECIPES.find((r) => r.id === "overnight-oats-dein-rezept");
  return '<div class="card"><h3>Overnight Oats für dein Ziel</h3>' +
    '<div class="stats"><div class="stat"><span class="big">' + o.protein + "<small>g</small></span><span>Eiweiß</span></div>" +
    '<div class="stat"><span class="big">' + o.kcal + "<small>kcal</small></span><span>Energie</span></div>" +
    '<div class="stat"><span class="big">ca. 20<small>g</small></span><span>Ballaststoffe, geschätzt</span></div></div><ul>' +
    "<li><b>Passt gut:</b> Mit rund 40 g Eiweiß liegt die Mahlzeit am oberen Ende der sinnvollen 20 bis 40 g und deckt etwa ein Viertel deines Tagesziels. Das hilft beim Muskelaufbau und sättigt lange.</li>" +
    "<li><b>Passt gut:</b> Haferflocken, Chia, Obst und Mandeln liefern viel Vollkorn und etwa 20 g Ballaststoffe. Die DGE empfiehlt mindestens 30 g am Tag.</li>" +
    "<li><b>Zu beachten:</b> Mit rund 850 kcal ist es eine große Mahlzeit. Zum Abnehmen passt das nur, wenn du den Rest des Tages leichter isst.</li>" +
    "<li><b>Sicherheit:</b> Deine gefrorenen Erdbeeren solltest du vorher erhitzen. Das BfR empfiehlt, Tiefkühl-Beeren mindestens 2 Minuten auf über 90 °C zu erhitzen, weil sie Noro- oder Hepatitis-A-Viren enthalten können. Koch sie kurz auf, lass sie abkühlen und gib sie dann in die Oats.</li>" +
    "<li><b>Einfach anpassen:</b> 70 g statt 100 g Haferflocken und ohne Honig bringen dich auf rund 700 kcal bei etwa 36 g Eiweiß. Eine fertige Variante findest du unter „Overnight Oats light“.</li></ul>" +
    '<p class="note">Gerechnet mit Milch 1,5 % und einer Banane. Du hattest die Banane zweimal genannt, mit zwei Bananen sind es etwa 90 kcal mehr. Alle Werte sind gerundete Tabellenwerte.</p></div>';
}
function renderNutrition() {
  $("#panel-ernaehrung").innerHTML =
    '<div class="card" data-nofold><h3>Richtwerte für dich</h3>' +
    '<div class="form"><label class="field">Gewicht (kg)<input type="number" id="b-weight" min="30" max="250" step="0.5" value="' + prof.weight + '"></label><label class="field">Größe (cm)<input type="number" id="b-height" min="120" max="230" step="1" value="' + prof.height + '"></label></div>' +
    '<div class="stats" id="calc">' + calcStats(bodyCalc()) + "</div>" +
    '<details class="exmore"><summary>Woher kommen die Zahlen?</summary><p class="note">Die Fachgesellschaft ISSN nennt 1,4 bis 2,0 g Eiweiß pro kg und Tag für Trainierende. Eine große Auswertung (Morton 2018) fand oberhalb von etwa 1,6 g pro kg kaum noch zusätzlichen Zuwachs an Muskelmasse. Pro Mahlzeit gelten etwa 0,25 g pro kg oder 20 bis 40 g als sinnvoll. Das Defizit sollte klein bleiben (grob 250 bis 500 Kalorien unter deinem Verbrauch), weil zu schnelles Abnehmen auch Muskeln kostet. Das sind Orientierungswerte und kein medizinischer Rat. Bei Vorerkrankungen sprich vorher mit deinem Arzt.</p></details></div>' +
    dayCard() + oatsCard() + '<div class="grid2"><div class="card"><h3>Die Basis nach DGE</h3><ul>' +
    "<li>Am besten Wasser trinken, rund 1,5 Liter am Tag.</li>" +
    "<li>Mindestens 5 Portionen Obst und Gemüse am Tag, zu jeder Mahlzeit etwas davon. Mit deiner Auswahl (Tomate, Gurke, Paprika, Zwiebel, Salat, Spinat, Rucola, Erdbeeren, Banane) klappt das gut, wenn bei jeder Mahlzeit eine Handvoll dabei ist. Probier gern ab und zu etwas Neues, am einfachsten in Soßen.</li>" +
    "<li>Hülsenfrüchte mindestens einmal pro Woche, täglich eine kleine Handvoll Nüsse (ca. 25 g).</li>" +
    "<li>Vollkorn bei Brot, Nudeln und Reis.</li>" +
    "<li>Milch und Milchprodukte täglich. Die DGE rät außerdem zu Fisch. Du isst keinen: Lein- und Rapsöl sowie Walnüsse liefern pflanzliche Omega-3-Fettsäuren.</li>" +
    "<li>Fleisch und Wurst in Maßen (die DGE nennt etwa 300 g pro Woche).</li>" +
    "<li>Süßes, Salziges und Fettiges eher selten.</li></ul></div>" +
    '<div class="card"><h3>Sicher essen</h3><ul>' +
    "<li>Geflügel im Kern mindestens 70 °C (mindestens 2 Minuten) und nichts Rosa mehr. Rohes Geflügel getrennt schneiden und Hände und Brett danach gründlich waschen.</li>" +
    "<li>Eier kochen, bis Eiweiß und Eigelb fest sind.</li>" +
    "<li>Reis und Nudeln nach dem Kochen rasch abkühlen (flach verteilen), innerhalb von etwa 2 Stunden in den Kühlschrank, am besten am nächsten Tag essen, spätestens nach 2 Tagen und vollständig erhitzen.</li>" +
    "<li>Tiefkühl-Beeren vor dem Essen mindestens 2 Minuten auf über 90 °C erhitzen und abkühlen lassen (BfR). Das gilt auch für Overnight Oats, Quark und Shakes.</li>" +
    "<li>Keine lauwarmen Reste stehen lassen. Die Keime, die sich dann vermehren, überstehen das Kochen.</li></ul></div></div>";
  foldCards($("#panel-ernaehrung"));
}
function renderTips() {
  $("#panel-tipps").innerHTML =
    '<div class="card"><h3>Deine Woche</h3><div class="week">' + weekPlan().map((d) => '<div class="' + (d[2] ? "on" : "") + '"><b>' + d[0] + "</b>" + d[1] + "</div>").join("") + "</div></div>" +
    '<div class="grid2">' + TIPS.map((g) => '<article class="card"><h3>' + g.h + "</h3><ul>" + g.items.map((i) => "<li>" + i + "</li>").join("") + "</ul></article>").join("") + "</div>";
  $("#panel-tipps .card").setAttribute("data-nofold", "");
  foldCards($("#panel-tipps"));
}
const ROAD = [
  { a: 1, b: 2, t: "Technik lernen", sp: "Woche 1 und 2", goal: "Saubere Bewegung vor Schwere. Jede Übung auf der ersten Stufe, ohne Schmerzen und mit Kontrolle.", gear: "Keine Ausrüstung nötig. Eine Matte macht den Boden bequemer." },
  { a: 3, b: 8, t: "Aufbau", sp: "Woche 3 bis 8", goal: "Wiederholungen steigern, Stufen hochgehen und 2 bis 3 Einheiten pro Woche durchziehen. Der Rucksack ist dein Gewicht.", gear: "Bänder fürs Rudern, Liegestützgriffe falls die Handgelenke stören." },
  { a: 9, b: 20, t: "Ausbauen", sp: "Woche 9 bis 20", goal: "Die Stufen werden oben eng. Jetzt kommen mehr Gewicht und neue Hebel dazu: Kurzhanteln, ein dritter Satz, Klimmzug-Vorstufen.", gear: "Kurzhanteln, Parallettes und ein Klimmzugturm." },
  { a: 21, b: 9999, t: "Fortgeschritten", sp: "ab Woche 21", goal: "Erste Klimmzüge, tiefe Liegestütze und Dips, L-Sit-Vorstufen, einbeinige Varianten.", gear: "Alles aus der Phase davor, später optional eine Gewichtsweste." }
];
const maxLog = (k) => log.reduce((m, x) => Math.max(m, x && typeof x[k] === "number" ? x[k] : 0), 0);
const MILES = [
  { id: "m12w", t: "12 Wochen drangeblieben", auto: () => weekNo() >= 12 },
  { id: "m30", t: "30 Trainingseinheiten geschafft", auto: () => sessions.length >= 30 },
  { id: "mpush10", t: "10 Liegestütze am Stück", auto: () => maxLog("pushups") >= 10 },
  { id: "mpush20", t: "20 Liegestütze am Stück", auto: () => maxLog("pushups") >= 20 },
  { id: "mplank60", t: "60 Sekunden Plank", auto: () => maxLog("plank") >= 60 },
  { id: "msquat20", t: "20 saubere Kniebeugen am Stück" },
  { id: "mhang30", t: "30 Sekunden an der Stange hängen" },
  { id: "mneg", t: "Ein negativer Klimmzug über 5 Sekunden" },
  { id: "mpull", t: "Der erste Klimmzug" }
];
const LATER = [
  { name: "Sprungseil", p: [8, 15], note: "Für Ausdauer zwischendurch. Günstig, klein und überall nutzbar.", q: "Springseil Speed Rope", qk: "springseil" },
  { name: "Gymnastikringe", p: [30, 50], note: "Erst nach sauberen Klimmzügen und Dips. Sie wackeln und sind deutlich schwerer.", q: "Gymnastikringe Holz", qk: "gymnastikringe" },
  { name: "Gewichtsweste", p: [50, 100], note: "Erst wenn 20 Liegestütze und mehrere Klimmzüge sauber sitzen.", q: "Gewichtsweste verstellbar 10 kg", qk: "gewichtsweste" },
  { name: "Hantelbank", p: [60, 120], note: "Nur wenn du über 20 kg Kurzhanteln hinausgehst und Platz hast.", q: "Hantelbank verstellbar", qk: "hantelbank" }
];
const ST_TXT = { now: "Jetzt sinnvoll", soon: "Bald", later: "Später", own: "Hast du", never: "Nicht bei dir" };
const buyLinks = (q, qk) => [
  ["Amazon", "https://www.amazon.de/s?k=" + encodeURIComponent(q)],
  ["Otto", "https://www.otto.de/suche/" + encodeURIComponent(q) + "/"],
  ["Kleinanzeigen", "https://www.kleinanzeigen.de/s-" + encodeURIComponent(qk.toLowerCase().replace(/\s+/g, "-")) + "/k0"]
];
const linksHTML = (q, qk) => buyLinks(q, qk).map((l) => '<a class="btn" href="' + l[1] + '" target="_blank" rel="noopener noreferrer">' + l[0] + "</a>").join("");
function gearCtx() {
  const L = (id) => { const e = exById(id); return e ? lvl(e) : 0; };
  const rowBest = Math.max.apply(null, EXALL.filter((e) => e.slot === "row" && !e.gear).map(lvl));
  return { wk: weekNo(), n: sessions.length, push: L("push"), row: rowBest, top: EX.filter((e) => lvl(e) >= e.ladder.length - 1).length };
}
function gearState(g) {
  if (g.never) return { k: "never", t: ST_TXT.never, ok: [], n: 0 };
  if (gearOwned(g.id)) return { k: "own", t: ST_TXT.own, ok: [], n: 0 };
  const c = gearCtx(), ok = g.crit.map((x) => !!x[1](c)), n = ok.filter(Boolean).length;
  const k = !g.crit.length || n === g.crit.length ? "now" : n * 2 >= g.crit.length ? "soon" : "later";
  return { k, t: ST_TXT[k], ok, n };
}
const eurR = (r) => r[0] + " bis " + r[1] + "\u00a0€";
function gearHTML(g) {
  const s = gearState(g);
  if (g.never) return '<article class="card gearcard never" data-nofold><div class="gearhead"><div><h3>' + g.name + '</h3><p class="kicker">Nicht empfohlen</p></div><span class="gchip g-never">' + s.t + "</span></div><p>" + g.why + '</p><p class="note">' + g.note + "</p></article>";
  const own = s.k === "own", unl = EXFUT.filter((e) => e.gear.includes(g.id)).map((e) => e.name);
  const crit = !own && g.crit.length ? '<ul class="gcrit">' + g.crit.map((x, i) => '<li class="' + (s.ok[i] ? "ok" : "no") + '">' + x[0] + "</li>").join("") + '</ul><p class="small muted">' + s.n + " von " + g.crit.length + " Punkten erfüllt. Das sind nur Richtwerte aus deinen Daten, kaufen kannst du jederzeit.</p>" : !own ? '<p class="small muted">Kostet wenig und hilft dir ab sofort.</p>' : "";
  return '<article class="card gearcard st-' + s.k + '" data-nofold data-gearcard="' + g.id + '"><div class="gearhead"><div><h3>' + g.name + '</h3><p class="kicker">' + eurR(g.p) + " neu, gebraucht etwa " + eurR(g.u) + '</p></div><span class="gchip g-' + s.k + '">' + s.t + "</span></div>" +
    "<p>" + g.gives + "</p>" + (g.alt ? '<p class="small muted">Alternative zum Klimmzugturm, du brauchst nur eins von beidem.</p>' : "") + crit +
    '<details class="exmore"><summary>Worauf du beim Kauf achten solltest</summary><ul>' + g.tips.map((t) => "<li>" + t + "</li>").join("") + "</ul>" + (unl.length ? '<p class="small muted">Das schaltet frei: ' + unl.join(", ") + ".</p>" : "") + "</details>" +
    '<div class="row gearrow">' + (own ? "" : linksHTML(g.q, g.qk)) + '<button class="btn gtoggle" type="button" data-gear="' + g.id + '" aria-pressed="' + own + '">' + (own ? "✓ Habe ich" : "Habe ich schon") + "</button></div></article>";
}
function futureHTML(e) {
  const ok = gearOk(e), slotN = SLOTNAME[e.slot];
  return '<details class="swopt fut"><summary><b>' + e.name + '</b><span class="swtag">' + (ok ? "Freigeschaltet" : "Braucht " + gearNames(e)) + '</span></summary><p class="small muted">Ersetzt: ' + slotN + "</p><p>" + e.why + '</p><p>' + e.cue + '</p><ol class="ladder">' + e.ladder.map((n) => "<li>" + n + "</li>").join("") + '</ol><p class="mistake"><b>Häufige Fehler:</b> ' + e.mistakes + "</p>" +
    (ok ? '<div class="row"><button class="btn primary" type="button" data-swapopen="' + e.slot + '">Übung tauschen</button></div>' : "") + "</details>";
}
/* Deine Pfade: pro Übung die Stufe auf dem Weg zur schwersten Stufe, dazu der Klimmzug-Weg aus den Meilensteinen */
const msDone = (m) => (m.auto ? !!m.auto() : !!(settings.ms && settings.ms[m.id]));
function pathRow(name, cur, n, now, goal, ready, next) {
  const pct = Math.round(cur / n * 100);
  return '<li class="vrow path"><span class="vname">' + esc(name) + '</span><span class="vnum">' + cur + "<small> von " + n + "</small></span>" +
    '<span class="vbar" role="progressbar" aria-valuemin="0" aria-valuemax="' + n + '" aria-valuenow="' + cur + '" aria-label="' + esc(name) + ": " + cur + " von " + n + '"><i class="' + (cur >= n ? "good" : "ok") + '" style="width:' + pct + '%"></i></span>' +
    '<span class="vsub muted small">' + (now ? "Jetzt: " + esc(now) + ". " : "") + (next ? "Als Nächstes: " + esc(next) + ". " : "") + (cur >= n ? "Ziel erreicht." : goal ? "Ziel: " + esc(goal) + "." : "") + "</span>" +
    (ready ? '<span class="vsub small exready"><b>Bereit für die nächste Stufe:</b> ' + esc(ready) + "</span>" : "") + "</li>";
}
function pathsHTML() {
  const rows = EX.map((e) => { const li = lvl(e), n = e.ladder.length; return pathRow(e.name, li + 1, n, e.ladder[li], e.ladder[n - 1], li < n - 1 && exUp(e) ? e.ladder[li + 1] : ""); });
  const pull = ["mhang30", "mneg", "mpull"].map((id) => MILES.find((m) => m.id === id)).filter(Boolean);
  if (pull.length === 3) { const done = pull.filter(msDone).length, nxt = pull.find((m) => !msDone(m)); rows.push(pathRow("Klimmzug", done, 3, nxt ? "" : pull[2].t, nxt && nxt !== pull[2] ? pull[2].t : "", "", nxt ? nxt.t : "")); }
  return '<div class="card" data-nofold><h3>Deine Pfade</h3><p class="kicker">Jede Übung hat Stufen. Hier siehst du, wie weit du auf dem Weg zur schwersten Stufe bist.</p><ul class="paths">' + rows.join("") + "</ul></div>";
}
function renderAusblick(keep) {
  const p = $("#panel-ausblick"); if (!p) return;
  const wasOpen = keep ? $$("#panel-ausblick details").map((d) => d.open) : [], y = window.scrollY;
  const wk = weekNo(), ph = ROAD.findIndex((r) => wk >= r.a && wk <= r.b);
  const st = GEAR.filter((g) => !g.never && !g.alt).map((g) => [g, gearState(g)]);
  const todo = st.filter((x) => x[1].k !== "own").sort((a, b) => a[0].prio - b[0].prio);
  const nxt = todo.find((x) => x[1].k === "now") || todo.find((x) => x[1].k === "soon");
  const nxtTxt = nxt ? (nxt[1].k === "now" ? "Als Nächstes sinnvoll: <b>" + nxt[0].name + "</b>." : "Bald sinnvoll: <b>" + nxt[0].name + "</b>.") : "Du bist gerade gut ausgerüstet, es muss nichts Neues sein.";
  const lo = todo.reduce((a, x) => a + x[0].p[0], 0), hi = todo.reduce((a, x) => a + x[0].p[1], 0), ulo = todo.reduce((a, x) => a + x[0].u[0], 0), uhi = todo.reduce((a, x) => a + x[0].u[1], 0);
  const start = todo.filter((x) => ["matte", "baender", "hanteln"].includes(x[0].id)), slo = start.reduce((a, x) => a + x[0].p[0], 0), shi = start.reduce((a, x) => a + x[0].p[1], 0);
  const road = '<div class="card" data-nofold><h3>Dein Weg</h3><p class="kicker">Du bist in Woche ' + wk + '. ' + nxtTxt + '</p><ol class="road">' + ROAD.map((r, i) => '<li class="' + (i === ph ? "cur" : i < ph ? "past" : "") + '"><details' + (i === ph ? " open" : "") + '><summary><b>' + r.t + "</b>" + (i === ph ? '<span class="swtag">Du bist hier</span>' : "") + '<span class="small muted">' + r.sp + "</span></summary><span>" + r.goal + '</span><span class="small muted">Ausrüstung: ' + r.gear + "</span></details></li>").join("") +
    '</ol><p class="note">Die Wochen sind Richtwerte. Wichtiger als der Kalender ist, ob du die obere Wiederholungszahl in allen Sätzen sauber schaffst. Dann geht es eine Stufe weiter.</p></div>';
  const buy = '<div class="card" data-nofold><h3>Ausrüstung im Überblick</h3>' + (todo.length ? '<ul class="buyorder">' + todo.map((x, i) => '<li><b>' + (i + 1) + ". " + x[0].name + '</b><span class="bo2"><span class="small muted">' + eurR(x[0].p) + '</span><span class="gchip g-' + x[1].k + '">' + x[1].t + "</span></span></li>").join("") + "</ul>" +
    '<p>Alles zusammen wären etwa <b>' + eurR([lo, hi]) + "</b> neu, gebraucht etwa " + eurR([ulo, uhi]) + "." + (start.length ? " Du musst nicht alles kaufen: " + start.map((x) => x[0].name).join(", ") + " (zusammen etwa " + eurR([slo, shi]) + ") reichen für viele Monate." : "") + "</p>" : "<p>Du hast alles Wichtige. Super.</p>") +
    '<p class="note">Die Preise sind grobe Richtwerte (Stand November 2026) und ändern sich. Die Knöpfe unten öffnen eine Suche bei Amazon, Otto und Kleinanzeigen, keine festen Produkte. Vergleiche Bewertungen und die Angaben zur Traglast selbst.</p></div>';
  const ms = '<div class="card"><h3>Meilensteine</h3><p class="kicker">Ziele, die du abhaken kannst</p><ul class="msl">' + MILES.map((m) => {
    const done = msDone(m), d = settings.ms && settings.ms[m.id];
    return '<li class="' + (done ? "ok" : "") + '"><span>' + (done ? "✓ " : "○ ") + m.t + "</span>" + (m.auto ? '<span class="small muted">' + (done ? "automatisch erkannt" : "wird automatisch erkannt") + "</span>" : '<button class="btn" type="button" data-ms="' + m.id + '" aria-pressed="' + done + '">' + (done ? "Geschafft" + (d ? " am " + d.slice(8, 10) + "." + d.slice(5, 7) + "." : "") : "Abhaken") + "</button>") + "</li>";
  }).join("") + "</ul></div>";
  const gear = '<h3 class="gearh">Ausrüstung</h3><div class="grid2">' + GEAR.map(gearHTML).join("") + "</div>";
  const fut = '<div class="card"><h3>Das kannst du später trainieren</h3><p class="kicker">Neue Übungen mit Ausrüstung</p><p>Sobald du etwas besitzt und oben auf „Habe ich“ tippst, erscheinen die passenden Übungen im Dialog „Tauschen“ in deinem Plan.</p><div class="swlist">' + EXFUT.map(futureHTML).join("") + "</div></div>";
  const later = '<div class="card"><h3>Noch später</h3><p class="kicker">Nur zum Merken, nichts davon brauchst du jetzt</p><ul class="laterl">' + LATER.map((x) => "<li><b>" + x.name + '</b> <span class="small muted">' + eurR(x.p) + "</span><br>" + x.note + '<div class="row gearrow">' + linksHTML(x.q, x.qk) + "</div></li>").join("") + "</ul></div>";
  p.innerHTML = road + pathsHTML() + buy + gear + ms + fut + later;
  foldCards(p);
  if (keep) { $$("#panel-ausblick details").forEach((d, i) => { if (wasOpen[i]) d.open = true; }); if (window.scrollY !== y) window.scrollTo(0, y); }
}
function toggleGear(id) {
  if (!GEAR.some((g) => g.id === id && !g.never)) return;
  settings.gear = settings.gear && typeof settings.gear === "object" ? settings.gear : {};
  if (settings.gear[id]) {
    if (isActive() && EX.some((e) => e.gear && e.gear.includes(id))) { toast("Beende zuerst dein Training, du nutzt gerade eine Übung dazu."); return; }
    delete settings.gear[id];
  } else settings.gear[id] = true;
  store.set("fc_settings", settings);
  applyAlts(); coachKey = ""; renderAusblick(true); renderEx(); render(); renderToday(); if (swapSlot) drawSwap();
}
function toggleMs(id) {
  if (!MILES.some((m) => m.id === id && !m.auto)) return;
  settings.ms = settings.ms && typeof settings.ms === "object" ? settings.ms : {};
  if (settings.ms[id]) delete settings.ms[id]; else settings.ms[id] = todayISO();
  store.set("fc_settings", settings);
  renderAusblick(true);
}
function swapLocked(slot) {
  const l = lockedVariants(slot); if (!l.length) return "";
  return '<h4 style="margin-top:16px">Mit Zusatz-Ausrüstung</h4><p class="small muted">Diese Übungen schaltest du frei, wenn du die Ausrüstung hast und im Tab „Ausblick“ auf „Habe ich“ tippst.</p><div class="swlist">' + l.map((e) => '<div class="swopt locked"><h4>' + e.name + '</h4><p class="small muted">Braucht: ' + gearNames(e) + "</p><p>" + e.why + "</p></div>").join("") + '</div><div class="row" style="margin-top:10px"><button class="btn" type="button" data-goto="ausblick">Ausrüstung ansehen</button></div>';
}
function renderSources() {
  $("#sources").innerHTML = "<summary>Quellen</summary>" + SOURCES.map((g) => '<h4 style="margin-top:12px">' + g[0] + "</h4><ul>" + g[1].map((s) => "<li>" + (s[1] ? '<a href="' + s[1] + '" target="_blank" rel="noopener">' + s[0] + "</a>" : s[0]) + "</li>").join("") + "</ul>").join("");
}

/* ======================= Fortschritt ======================= */
function saveEntry(part) {
  const d = todayISO();
  let e = log.find((x) => x.date === d);
  if (!e) { e = { date: d }; log.push(e); }
  Object.assign(e, part);
  log.sort((a, b) => a.date.localeCompare(b.date));
  store.set("fc_log", log);
  renderProgress();
}
function weekCount() {
  const lim = new Date(); lim.setDate(lim.getDate() - 6);
  const iso = isoOf(lim);
  return sessions.filter((s) => s >= iso).length;
}
function change(key) {
  const v = log.filter((x) => x[key] != null);
  if (v.length < 2) return null;
  return Math.round((v[v.length - 1][key] - v[0][key]) * 10) / 10;
}
function waistNote() {
  const v = log.filter((x) => x.waist != null);
  if (!v.length) return "Miss deine Taille, dann zeige ich dir hier, wo du im Verhältnis zu deiner Größe liegst.";
  const w = v[v.length - 1].waist, r = w / prof.height;
  const t = r < 0.5 ? "unter der Hälfte deiner Körpergröße" : r < 0.6 ? "etwas über der Hälfte deiner Körpergröße (erhöhter Bereich)" : "deutlich über der Hälfte deiner Körpergröße";
  const who = w < 94 ? "unter 94 cm (niedrigeres Risiko)" : w <= 102 ? "zwischen 94 und 102 cm (erhöhtes Risiko)" : "über 102 cm (deutlich erhöhtes Risiko)";
  return "Letzte Taille " + nf(w) + " cm: Verhältnis zur Größe " + nf(Math.round(r * 100) / 100) + ", also " + t + ". Nach den WHO-Grenzen für Männer " + who + ". Orientierungswerte, keine Diagnose.";
}
const MUSC = [["chest", "Brust"], ["shoulder", "Schultern"], ["tri", "Trizeps"], ["back", "Rücken"], ["bi", "Bizeps"], ["quad", "Oberschenkel"], ["glute", "Po und Beinrückseite"], ["core", "Bauch und Rumpf"]];
const MAPX = { squat: { quad: 1, glute: 0.5 }, push: { chest: 1, shoulder: 0.5, tri: 0.5 }, row: { back: 1, bi: 0.5 }, pike: { shoulder: 1, tri: 0.5 }, bridge: { glute: 1 }, plank: { core: 1 } };
EXALT.forEach((a) => { MAPX[a.id] = a.mx; });
EXFUT.forEach((a) => { MAPX[a.id] = a.mx; });
function weekSets(startISO) {
  const end = shiftDay(startISO, 7), out = {};
  MUSC.forEach((m) => { out[m[0]] = 0; });
  WK.forEach((w) => { if (w.date >= startISO && w.date < end) w.sets.forEach((x) => { const mp = MAPX[x.ex]; if (mp) for (const k in mp) out[k] += mp[k]; }); });
  return out;
}
function lastTrained(key) {
  for (let i = WK.length - 1; i >= 0; i--) if (WK[i].sets.some((x) => MAPX[x.ex] && MAPX[x.ex][key])) return WK[i].date;
  return null;
}
function renderVolume() {
  const ws = weekStartISO(todayISO()), cur = weekSets(ws), prev = weekSets(shiftDay(ws, -7)), today = new Date(todayISO() + "T12:00:00");
  const any = MUSC.some((m) => cur[m[0]] > 0);
  const rows = MUSC.map((m) => {
    const n = cur[m[0]], pv = prev[m[0]], lt = lastTrained(m[0]);
    const days = lt ? Math.round((today - new Date(lt + "T12:00:00")) / 86400000) : null;
    const cls = n >= 10 ? "good" : n >= 6 ? "ok" : "low";
    const sub = (days == null ? "" : days === 0 ? "heute trainiert" : "zuletzt vor " + days + (days === 1 ? " Tag" : " Tagen")) + (pv ? (days == null ? "" : " · ") + "letzte Woche " + nf(pv) : "");
    return '<li class="vrow"><span class="vname">' + m[1] + '</span><span class="vnum">' + nf(n) + '<small> von 10</small></span><span class="vbar" role="img" aria-label="' + nf(n) + ' von 10 Sätzen"><i class="' + cls + '" style="width:' + Math.min(100, Math.round(n / 10 * 100)) + '%"></i></span>' + (sub ? '<span class="vsub muted small">' + sub + "</span>" : "") + "</li>";
  }).join("");
  $("#volcard").innerHTML = "<h3>Sätze pro Muskel diese Woche</h3><p class=\"muted small\">Ziel: etwa 10 pro Muskel und Woche. Mithelfende Muskeln zählen halb.</p>" + (any ? "" : '<p class="note">Noch kein Training diese Woche.</p>') + '<ul class="vol">' + rows + "</ul>";
}
function badgeList() {
  const n = sessions.length, st = weekStreak(), dd = Object.keys(DIARY), pt = protTarget();
  const protDays = dd.filter((k) => DIARY[k].items.reduce((a, x) => a + (x.p || 0), 0) >= pt).length;
  const waterDays = dd.filter((k) => DIARY[k].water >= GOALS.water).length;
  const lvlUp = EXALL.some((e) => levels[e.id] != null && levels[e.id] > e.def);
  const full = WK.some((w) => EXBASE.every((b) => w.sets.some((x) => { const q = exById(x.ex); return q && q.slot === b.slot; })));
  const wts = log.filter((x) => x.weight != null).length;
  return [
    { t: "Erste Einheit", d: "Du hast dein erstes Training geschafft.", v: n, g: 1 },
    { t: "10 Einheiten", d: "Zehn Trainings, das ist eine Gewohnheit im Aufbau.", v: n, g: 10 },
    { t: "25 Einheiten", d: "Fünfundzwanzig Trainings.", v: n, g: 25 },
    { t: "3 Wochen in Folge", d: "Drei Wochen hintereinander mit mindestens 2 Einheiten.", v: st, g: 3 },
    { t: "Eine Stufe weiter", d: "Du bist bei einer Übung auf die nächste Stufe gegangen.", v: lvlUp ? 1 : 0, g: 1 },
    { t: "Alle Übungen an einem Tag", d: "Eine Einheit mit allen " + EX.length + " Übungen.", v: full ? 1 : 0, g: 1 },
    { t: "Kurz, aber dabei", d: "Ein Kurz-Training geschafft, an einem stressigen Tag zählt das.", v: WK.some((w) => w.q) ? 1 : 0, g: 1 },
    { t: "Eiweißziel 5 Tage", d: "An 5 Tagen das Eiweißziel erreicht.", v: protDays, g: 5 },
    { t: "Wasser 3 Tage", d: "An 3 Tagen dein Wasserziel erreicht.", v: waterDays, g: 3 },
    { t: "Trend sichtbar", d: "Mindestens 2 Gewichtswerte eingetragen.", v: wts, g: 2 }
  ];
}
function renderBadges() {
  const l = badgeList(), got = l.filter((b) => b.v >= b.g).length;
  $("#badgecard").innerHTML = "<h3>Erfolge</h3><p class=\"muted\">" + got + " von " + l.length + " erreicht. Alles bleibt auf deinem Gerät, kein Vergleich mit anderen.</p><ul class=\"badges\">" +
    l.map((b) => '<li class="' + (b.v >= b.g ? "got" : "") + '"><b>' + b.t + "</b><span>" + (b.v >= b.g ? b.d : "noch " + (b.g - b.v > 0 ? nf(Math.ceil(b.g - b.v)) : 0) + " bis dahin") + "</span></li>").join("") + "</ul>";
}

/* Essens-Tagebuch: alle eingetragenen Tage ansehen */
let HISTN = 14;
function renderEatHist() {
  const box = $("#eathist"); if (!box) return;
  const days = Object.keys(DIARY).filter((d) => DIARY[d] && DIARY[d].items && DIARY[d].items.length).sort().reverse();
  if (!days.length) { box.innerHTML = '<h3>Essens-Tagebuch</h3><p class="muted">Noch nichts eingetragen. Trag auf „Heute“ ein, was du isst, dann findest du es hier wieder.</p>'; return; }
  const sum = (d) => DIARY[d].items.reduce((a, x) => ({ k: a.k + x.k, p: a.p + x.p, c: a.c + (x.c || 0) }), { k: 0, p: 0, c: 0 });
  const wd = (d) => ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"][new Date(d + "T12:00:00").getDay()];
  const last7 = days.filter((d) => d > shiftDay(todayISO(), -7)), avg = last7.length ? last7.map(sum).reduce((a, x) => ({ k: a.k + x.k / last7.length, p: a.p + x.p / last7.length }), { k: 0, p: 0 }) : null;
  const shown = days.slice(0, HISTN);
  box.innerHTML = '<div class="rday-h"><h3>Essens-Tagebuch</h3><span class="rtot">' + days.length + (days.length === 1 ? " Tag" : " Tage") + "</span></div>" +
    (avg ? '<p class="small muted">Schnitt der letzten 7 Tage mit Einträgen: ' + Math.round(avg.k).toLocaleString("de-DE") + " kcal und " + Math.round(avg.p) + " g Eiweiß pro Tag.</p>" : "") +
    shown.map((d, di) => { const t = sum(d); return '<details class="hday"' + (di === 0 ? " open" : "") + "><summary><span><b>" + wd(d) + ", " + dateDE(d) + "</b></span><span class=\"small muted\">" + t.k.toLocaleString("de-DE") + " kcal · " + t.p + " g Eiweiß" + (t.c ? " · " + eur(t.c) : "") + "</span></summary>" +
      '<ul class="hitems">' + DIARY[d].items.map((x, i) => '<li><div><b>' + esc(x.t) + '</b><span class="small muted"> ' + x.k + " kcal, " + x.p + " g Eiweiß" + (x.c ? ", " + eur(x.c) : "") + "</span>" +
        (x.det && x.det.length ? '<ul class="hdet">' + x.det.map((l) => "<li>" + esc(l) + "</li>").join("") + "</ul>" : "") +
        (x.id && byId(x.id) ? '<button class="btn sm" type="button" data-recipe="' + x.id + '">Rezept ansehen</button>' : "") + '</div><button class="x" type="button" data-hdel="' + d + ":" + i + '" aria-label="Eintrag löschen">×</button></li>').join("") + "</ul></details>"; }).join("") +
    (days.length > HISTN ? '<div class="row"><button class="btn" type="button" data-histmore="1">Ältere Tage anzeigen</button></div>' : "");
}
/* Ohne Verlauf zeigt die Kachel statt eines Strichs, was zu tun ist, und springt zum Eingabefeld */
function chgTile(v, key, field, label, first, second) {
  if (v != null) return '<div class="stat"><span class="big">' + (v > 0 ? "+" : v < 0 ? "−" : "") + nf(Math.abs(v)) + "</span><span>" + label + "</span></div>";
  return '<button type="button" class="stat statact" data-focusf="' + field + '"><span class="big" aria-hidden="true">+</span><span>' + (log.some((x) => x[key] != null) ? second : first) + "</span></button>";
}
function renderProgress() {
  const w = change("weight"), c = change("waist");
  $("#stats").innerHTML =
    '<div class="stat"><span class="big">' + sessions.length + "</span><span>Trainings gesamt</span></div>" +
    '<div class="stat"><span class="big">' + weekCount() + "</span><span>letzte 7 Tage</span></div>" +
    chgTile(w, "weight", "f-weight", "kg seit Start", "Gewicht eintragen", "Noch ein Gewicht für den Verlauf") +
    chgTile(c, "waist", "f-waist", "cm Taille seit Start", "Taille eintragen", "Noch eine Taillenmessung für den Verlauf");
  $("#waistnote").textContent = waistNote();
  renderEatHist(); renderVolume(); renderBadges();
  renderCharts();
  if (!log.length) { $("#logtable").innerHTML = '<p class="muted">Noch keine Einträge. Miss heute Gewicht und Taille und trag sie oben ein.</p>'; return; }
  const rows = log.slice().reverse().map((e) =>
    "<tr><td>" + e.date.slice(8) + "." + e.date.slice(5, 7) + ".</td><td>" + (e.weight != null ? nf(e.weight) : "–") + "</td><td>" + (e.waist != null ? nf(e.waist) : "–") +
    "</td><td>" + (e.pushups != null ? e.pushups : "–") + "</td><td>" + (e.plank != null ? e.plank : "–") + '</td><td><button class="x" data-del="' + e.date + '" aria-label="Eintrag löschen">×</button></td></tr>').join("");
  $("#logtable").innerHTML = "<table><thead><tr><th>Datum</th><th>kg</th><th>Taille</th><th>Liegestütze</th><th>Plank</th><th></th></tr></thead><tbody>" + rows + "</tbody></table>";
}

/* ======================= Tabs ======================= */
const GROUPS = [
  { id: "heute", title: "Heute", tabs: ["heute"] },
  { id: "training", title: "Training", tabs: ["uebungen", "tipps", "ausblick"] },
  { id: "essen", title: "Essen", tabs: ["rezepte", "rad", "vorkochen", "einkauf"] },
  { id: "fortschritt", title: "Fortschritt", tabs: ["fortschritt", "ernaehrung"] }
];
const TABN = { heute: "Heute", uebungen: "Übungen", tipps: "Tipps", ausblick: "Ausblick", rezepte: "Rezepte", rad: "Glücksrad", vorkochen: "Vorkochen", einkauf: "Einkauf", ernaehrung: "Richtwerte", fortschritt: "Verlauf" };
const TABSUB = { uebungen: "Dein Plan mit Stufen für jede Übung", tipps: "Wochenplan und Hinweise für den Alltag", ausblick: "Pläne, Ausrüstung und Kauflinks", rezepte: RECIPES.length + " Rezepte mit Eiweiß und Lidl-Preis", rad: "Lass das Rad entscheiden, was es gibt", vorkochen: "Sonntag kochen, die Woche essen", einkauf: "Liste, Preise und Aufbewahrung", ernaehrung: "Richtwerte und Grundlagen", fortschritt: "Gewicht, Taille und Training im Verlauf" };
const LAST = {};
let CUR = "heute";
const greeting = () => { const h = new Date().getHours(); return h < 11 ? "Guten Morgen" : h < 18 ? "Guten Tag" : "Guten Abend"; };
function moveBoth() {
  const a = $("#tabind"), ab = $('#subnav .tab[aria-selected="true"]'), g = $("#gind"), gb = $('.gbtn[aria-selected="true"]');
  const ra = a && ab ? [ab.offsetWidth, ab.offsetLeft] : null, rg = g && gb ? [gb.offsetWidth, gb.offsetLeft] : null;
  const put = (i, r) => {
    if (i.dataset.init !== "1") { i.style.transition = "none"; i.dataset.init = "1"; i.style.width = r[0] + "px"; i.style.transform = "translateX(" + r[1] + "px)"; void i.offsetWidth; i.style.transition = ""; return; }
    i.style.width = r[0] + "px"; i.style.transform = "translateX(" + r[1] + "px)";
  };
  if (ra) put(a, ra);
  if (rg) put(g, rg);
}
function syncCoach() {
  const g = GROUPS.find((x) => x.tabs.includes(CUR)), run = isActive() || !!tm.id;
  document.body.dataset.group = g.id;
  document.body.dataset.run = run ? "1" : "0";
  document.body.dataset.coach = (g.id === "heute" || g.id === "training" || run) ? "1" : "0";
}
function showTab(name, quiet) {
  const g = GROUPS.find((x) => x.tabs.includes(name)); if (!g) return;
  const prevG = (GROUPS.find((x) => x.tabs.includes(CUR)) || {}).id;
  const prevName = CUR;
  CUR = name; LAST[g.id] = name;
  if (name === "fortschritt" && typeof renderProgress === "function" && !quiet) renderProgress();
  if (name === "uebungen" && typeof renderEx === "function" && !quiet) renderEx();
  if (name === "ausblick" && !quiet) renderAusblick();
  if (name === "vorkochen" && typeof renderPrep === "function" && !quiet) renderPrep();
  $$(".gbtn").forEach((b) => b.setAttribute("aria-selected", b.dataset.group === g.id ? "true" : "false"));
  $$(".panel").forEach((p) => { p.hidden = p.id !== "panel-" + name; });
  const sn = $("#subnav");
  if (g.tabs.length > 1) {
    if (sn.dataset.group !== g.id) { sn.dataset.group = g.id; sn.innerHTML = '<span class="tab-ind" id="tabind"></span>' + g.tabs.map((t) => '<button class="tab" role="tab" data-tab="' + t + '" aria-selected="false">' + TABN[t] + "</button>").join(""); }
    sn.hidden = false;
    $$("#subnav .tab").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === name ? "true" : "false"));
  } else { sn.hidden = true; sn.dataset.group = ""; sn.innerHTML = ""; }
  const now = new Date();
  $("#pagetitle").textContent = name === "heute" ? greeting() : g.title;
  $("#pagesub").textContent = name === "heute" ? WD[now.getDay()] + ", " + now.getDate() + ". " + MON[now.getMonth()] : TABSUB[name];
  syncCoach(); moveBoth();
  if (name === "rad") requestAnimationFrame(drawWheel);
  if (name === "heute") { if (!quiet && prevName !== "heute") RINGANIM = true; renderToday(); }
  if (!quiet) {
    const p = $("#panel-" + name);
    if (p && p.animate && !reduceMotion()) p.animate([{ opacity: 0, transform: "translateY(8px)" }, { opacity: 1, transform: "none" }], { duration: 260, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)" });
    if (prevG !== g.id) window.scrollTo(0, 0);
    const b = $('#subnav .tab[aria-selected="true"]');
    if (b && b.scrollIntoView) { try { b.scrollIntoView({ block: "nearest", inline: "center" }); } catch (e) {} }
  }
}

/* ======================= Glücksrad ======================= */
const RAD = Object.assign({ mode: "day", meal: "Mittag/Abend", bfDay: true, bfWeek: false, noSpinat: true, cheap: true, work: false, maxDay: 0, people: 2, reste: true }, store.get("fc_rad", {}));
let RPL = store.get("fc_radplans", {});
const rad = { seg: [], theta: 0, hi: -1, busy: false, skip: false, shown: new Set() };
const TAU = Math.PI * 2;
const DAYN = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"];
/* Index nach ID, wird neu gebaut, wenn sich die Zahl der Rezepte ändert */
let RBYID = null, RBYIDN = -1;
const byId = (id) => { if (!RBYID || RBYIDN !== RECIPES.length) { RBYID = new Map(RECIPES.map((r) => [r.id, r])); RBYIDN = RECIPES.length; } return RBYID.get(id); };
const hasSpin = (r) => r.ing.some((i) => /spinat/i.test(i[2]));
const shuffle = (a) => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const pickRnd = (a) => a[Math.floor(Math.random() * a.length)];
const saveRad = () => { store.set("fc_rad", RAD); store.set("fc_radplans", RPL); };
const protTarget = () => Math.round(protGoal() * 0.92);

function radPool(kind, work) {
  const base = RECIPES.filter((r) => (!kind || r.meal === kind) && !isExc(r));
  const rules = [
    (r) => (!RAD.noSpinat || !hasSpin(r)) && (!RAD.cheap || r.tags.includes("Günstig")) && (!work || r.tags.includes("Für die Arbeit")),
    (r) => !RAD.noSpinat || !hasSpin(r),
    () => true
  ];
  for (const f of rules) { const l = base.filter(f); if (l.length) return l; }
  return [];
}
function slotSpecs(bf, work) {
  const s = [];
  if (bf) s.push({ k: "Frühstück", label: "Frühstück" });
  s.push({ k: "Mittag/Abend", label: "Mittagessen", work: work });
  s.push({ k: "Snack", label: "Snack am Nachmittag" });
  s.push({ k: "Mittag/Abend", label: "Abendessen" });
  s.push({ k: "Snack", label: "Snack am Abend" });
  return s;
}
const mainKind = (r) => r.contains.find((c) => ["Geflügel", "Rindfleisch", "Schwein", "Hülsenfrüchte"].includes(c)) || (r.contains.includes("Ei") ? "Ei" : "Milch");
function dayScore(recs) {
  const kcal = recs.reduce((a, r) => a + r.kcal, 0), prot = recs.reduce((a, r) => a + r.protein, 0), cost = recs.reduce((a, r) => a + r.cost, 0);
  let s = Math.max(0, protTarget() - prot) * 4 + Math.max(0, kcal - (GOALS.kcal + 250)) / 8 + Math.max(0, (GOALS.kcal - 400) - kcal) / 8 + (RAD.maxDay ? Math.max(0, cost - RAD.maxDay) * 40 : 0);
  const mains = recs.filter((r) => r.meal === "Mittag/Abend");
  if (mains.length > 1 && mainKind(mains[0]) === mainKind(mains[1])) s += 30;
  return s;
}
function planDay(specs, old, used) {
  const pools = specs.map((sp) => radPool(sp.k, sp.work));
  let best = null, bestS = Infinity; const good = [];
  for (let n = 0; n < 400; n++) {
    const pick = [], taken = new Set();
    specs.forEach((sp, i) => {
      const lk = old && old[i] && old[i].locked ? byId(old[i].id) : null;
      if (lk) { pick.push(lk); taken.add(lk.id); return; }
      let c = pools[i].filter((r) => !used.has(r.id) && !taken.has(r.id));
      if (!c.length) c = pools[i].filter((r) => !taken.has(r.id));
      if (!c.length) c = pools[i];
      const r = pickRnd(c); pick.push(r); taken.add(r.id);
    });
    const sc = dayScore(pick);
    if (sc === 0) good.push(pick);
    if (sc < bestS) { bestS = sc; best = pick; }
  }
  return good.length ? pickRnd(good) : best;
}
function radBuild(old) {
  const used = new Set(), days = [];
  const names = RAD.mode === "week" ? DAYN : RAD.mode === "day" ? ["Heute"] : [""];
  names.forEach((nm, di) => {
    let specs;
    if (RAD.mode === "meal") specs = [{ k: RAD.meal === "Egal" ? "" : RAD.meal, label: RAD.meal === "Egal" ? "Mahlzeit" : RAD.meal, work: RAD.work }];
    else specs = slotSpecs(RAD.mode === "week" ? (RAD.bfWeek || di >= 5) : RAD.bfDay, RAD.work && (RAD.mode === "day" || di < 5));
    const od = old && old.days[di] && old.days[di].slots.length === specs.length && old.days[di].slots.every((s, i) => s.label === specs[i].label) ? old.days[di].slots : null;
    let recs;
    if (RAD.mode === "meal") {
      const lk = od && od[0].locked ? byId(od[0].id) : null;
      if (lk) recs = [lk];
      else { const pool = radPool(specs[0].k, specs[0].work); let c = pool.filter((r) => !od || r.id !== od[0].id); if (!c.length) c = pool; recs = [pickRnd(c)]; }
    } else recs = planDay(specs, od, used);
    recs.forEach((r) => used.add(r.id));
    days.push({ name: nm, slots: specs.map((sp, i) => ({ label: sp.label, k: sp.k, work: !!sp.work, id: recs[i].id, locked: !!(od && od[i].locked) })) });
  });
  const plan = { days };
  radReste(plan);
  return plan;
}
function rerollOne(plan, d, s) {
  const day = plan.days[d], sl = day.slots[s];
  const elsewhere = new Set(); plan.days.forEach((x, xi) => x.slots.forEach((y, yi) => { if (!(xi === d && yi === s)) elsewhere.add(y.id); }));
  let pool = radPool(sl.k, sl.work).filter((r) => r.id !== sl.id && !elsewhere.has(r.id));
  if (!pool.length) pool = radPool(sl.k, sl.work).filter((r) => r.id !== sl.id);
  if (!pool.length) return sl.id;
  if (RAD.mode === "meal") return pickRnd(pool).id;
  const scored = pool.map((r) => ({ r, sc: dayScore(day.slots.map((y, yi) => (yi === s ? r : byId(y.id)))) })).sort((a, b) => a.sc - b.sc);
  return pickRnd(scored.slice(0, Math.min(5, scored.length))).r.id;
}

/* Zeichnen */
const mod = (a) => ((a % TAU) + TAU) % TAU;
function drawWheel() {
  const cv = $("#wheel"); if (!cv) return;
  const size = cv.clientWidth; if (!size) return;
  const dpr = window.devicePixelRatio || 1, px = Math.round(size * dpr);
  if (cv.width !== px) { cv.width = px; cv.height = px; }
  const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, size, size);
  const css = getComputedStyle(document.documentElement), col = (v) => css.getPropertyValue(v).trim();
  const n = Math.max(1, rad.seg.length), arc = TAU / n, c = size / 2, R = c - 12;
  const fs = Math.max(10.5, Math.min(15, size / 30));
  g.font = "600 " + fs + "px " + col("--body");
  for (let i = 0; i < n; i++) {
    const a0 = rad.theta + i * arc - Math.PI / 2, win = rad.hi === i;
    g.beginPath(); g.moveTo(c, c); g.arc(c, c, R, a0, a0 + arc); g.closePath();
    g.fillStyle = win ? col("--accent") : (i % 2 ? col("--wheel-b") : col("--wheel-a")); g.fill();
    g.lineWidth = 1.5; g.strokeStyle = col("--bg"); g.stroke();
    const label = rad.seg[i] || "";
    const mid = mod(a0 + arc / 2), flip = mid > Math.PI / 2 && mid < Math.PI * 1.5, sx = flip ? -1 : 1;
    g.save(); g.translate(c, c); g.rotate(a0 + arc / 2 + (flip ? Math.PI : 0));
    g.textAlign = flip ? "left" : "right"; g.textBaseline = "middle"; g.fillStyle = win ? col("--accent-ink") : col("--ink");
    const maxW = R * 0.64, words = label.split(" "), lines = [""];
    words.forEach((w) => { const cur = lines[lines.length - 1], test = cur ? cur + " " + w : w; if (!cur || g.measureText(test).width <= maxW) lines[lines.length - 1] = test; else lines.push(w); });
    let ls = lines.slice(0, 2);
    if (lines.length > 2) ls[1] = lines.slice(1).join(" ");
    ls = ls.map((t) => { if (g.measureText(t).width <= maxW) return t; while (t.length > 3 && g.measureText(t + "…").width > maxW) t = t.slice(0, -1); return t.trimEnd() + "…"; });
    ls.forEach((t, li) => g.fillText(t, sx * (R - 16), (li - (ls.length - 1) / 2) * fs * 1.2));
    g.restore();
  }
  g.beginPath(); g.arc(c, c, R, 0, TAU); g.lineWidth = 3; g.strokeStyle = col("--ink"); g.stroke();
  g.beginPath(); g.moveTo(c - 13, 3); g.lineTo(c + 13, 3); g.lineTo(c, 36); g.closePath();
  g.fillStyle = col("--ink"); g.fill(); g.lineWidth = 3; g.strokeStyle = col("--bg"); g.lineJoin = "round"; g.stroke();
}
function tickSound() {
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    const o = actx.createOscillator(), gn = actx.createGain();
    o.type = "triangle"; o.frequency.value = 1500; gn.gain.value = 0.025; o.connect(gn); gn.connect(actx.destination);
    o.start(); o.stop(actx.currentTime + 0.025);
  } catch (e) {}
}
function spinTo(cands, idx, ms) {
  return new Promise((resolve) => {
    rad.seg = cands.map((r) => r.title); rad.hi = -1;
    const arc = TAU / cands.length, base = -(idx + 0.5) * arc + (Math.random() - 0.5) * 0.7 * arc;
    const t0 = rad.theta, t1 = t0 + TAU * (3 + Math.floor(ms / 1000)) + mod(base - t0), start = performance.now();
    let last = Math.floor(mod(-t0) / arc);
    const step = (now) => {
      const p = Math.min(1, (now - start) / ms), e = 1 - Math.pow(1 - p, 4);
      rad.theta = t0 + (t1 - t0) * e;
      const cur = Math.floor(mod(-rad.theta) / arc);
      if (cur !== last) { last = cur; tickSound(); }
      if (p < 1 && !rad.skip) { drawWheel(); requestAnimationFrame(step); }
      else { rad.theta = mod(t1); rad.hi = idx; drawWheel(); resolve(); }
    };
    requestAnimationFrame(step);
  });
}
function candsFor(sl, id) {
  const pool = shuffle(radPool(sl.k, sl.work).filter((r) => r.id !== id)).slice(0, 7);
  return shuffle(pool.concat(byId(id)));
}
function radIdle() {
  const sk = RAD.mode === "meal" ? (RAD.meal === "Egal" ? "" : RAD.meal) : "Mittag/Abend";
  rad.seg = shuffle(radPool(sk, false).slice()).slice(0, 8).map((r) => r.title); rad.hi = -1;
}

/* Ablauf */
async function radRoll(only) {
  if (rad.busy) return;
  const mode = RAD.mode, old = RPL[mode] || null;
  const needKinds = mode === "meal" ? [RAD.meal === "Egal" ? "" : RAD.meal] : ["Frühstück", "Mittag/Abend", "Snack"];
  if (needKinds.some((k) => !radPool(k, false).length)) { $("#radstatus").textContent = "Mit deinen Ausschlüssen bleibt hier nichts übrig. Nimm in den Rezept-Filtern ein paar Zutaten oder Kategorien wieder heraus."; return; }
  let plan, jobs = [];
  rad.shown = new Set();
  if (only) {
    const [d, s] = only.split(":").map(Number);
    plan = JSON.parse(JSON.stringify(old));
    plan.days.forEach((x, xi) => x.slots.forEach((y, yi) => { if (!(xi === d && yi === s)) rad.shown.add(xi + ":" + yi); }));
    plan.days[d].slots[s].id = rerollOne(plan, d, s);
    jobs.push({ d, s, reveal: [d + ":" + s], ms: 2600 });
  } else {
    plan = radBuild(old);
    plan.days.forEach((x, xi) => x.slots.forEach((y, yi) => { if (y.locked) rad.shown.add(xi + ":" + yi); }));
    if (mode === "week") {
      plan.days.forEach((x, xi) => {
        const open = x.slots.map((y, yi) => (y.locked ? -1 : yi)).filter((i) => i >= 0);
        if (!open.length) return;
        const lead = open.includes(x.slots.length - 2) ? x.slots.length - 2 : open[0];
        jobs.push({ d: xi, s: lead, reveal: open.map((i) => xi + ":" + i), ms: 1500 });
      });
    } else {
      plan.days[0].slots.forEach((y, yi) => { if (!y.locked) jobs.push({ d: 0, s: yi, reveal: ["0:" + yi], ms: mode === "meal" ? 4200 : 2300 }); });
    }
  }
  RPL[mode] = plan; saveRad();
  rad.busy = true; rad.skip = reduceMotion(); radBusyUI(true); radRender();
  for (const j of jobs) {
    const sl = plan.days[j.d].slots[j.s];
    $("#radstatus").textContent = (plan.days[j.d].name && mode === "week" ? plan.days[j.d].name + ": " : "") + (mode === "week" ? "Abendessen" : sl.label) + " wird gedreht";
    const cands = candsFor(sl, sl.id);
    await spinTo(cands, cands.findIndex((r) => r.id === sl.id), j.ms);
    j.reveal.forEach((k) => rad.shown.add(k)); radRender();
    if (!rad.skip) await new Promise((r) => setTimeout(r, 380));
  }
  rad.busy = false; rad.skip = false; radBusyUI(false);
  plan.days.forEach((x, xi) => x.slots.forEach((y, yi) => rad.shown.add(xi + ":" + yi))); radRender();
  const names = plan.days.map((x) => x.slots.map((y) => byId(y.id).title));
  $("#radstatus").textContent = mode === "meal" ? "Es gibt: " + names[0][0] : mode === "day" ? "Dein Tag steht." : "Deine Woche steht.";
  say(mode === "meal" ? "Es gibt " + names[0][0] + "." : mode === "day" ? "Dein Tag: " + plan.days[0].slots.map((y) => y.label + ", " + byId(y.id).title).join(". ") + "." : "Deine Woche steht. Schau auf die Liste.", $("#radstatus").textContent);
  $("#caption").textContent = "";
}
function radBusyUI(b) {
  const sp = $("#spin"); if (sp) sp.disabled = b;
  $("#radbtns").innerHTML = b ? '<button class="btn" id="skipspin">Überspringen</button>' : "";
}

/* Anzeige */
function radRender() {
  const P = RPL[RAD.mode];
  if (!P) { $("#radres").innerHTML = '<div class="card empty"><h3>Noch nichts gedreht</h3><p class="muted">Tippe auf „Drehen“. Das Rad wählt aus deinen Rezepten.</p></div>'; return; }
  const tgt = protTarget(), notes = restNotes(P);
  $("#radres").innerHTML = P.days.map((d, di) => {
    const all = d.slots.every((s, si) => rad.shown.has(di + ":" + si));
    const recs = d.slots.map((s) => byId(s.id));
    const kcal = recs.reduce((a, r) => a + r.kcal, 0), prot = recs.reduce((a, r) => a + r.protein, 0), cost = recs.reduce((a, r) => a + r.cost, 0);
    const tot = RAD.mode === "meal" || !all ? "" : '<span class="rtot' + (prot >= tgt ? " ok" : "") + '">' + kcal.toLocaleString("de-DE") + " kcal, " + prot + " g Eiweiß, ca. " + eur(cost) + (prot >= tgt ? ", Ziel erreicht" : " (Ziel " + tgt + " g)") + "</span>";
    return '<section class="card rday">' + (d.name ? '<div class="rday-h"><h3>' + esc(d.name) + "</h3>" + tot + "</div>" : "") +
      '<ul class="rslots">' + d.slots.map((s, si) => {
        const key = di + ":" + si, r = byId(s.id), on = rad.shown.has(key);
        return '<li class="rslot"><span class="rlab">' + esc(s.label) + "</span>" +
          (on ? '<div class="rbody"><button class="rtitle" data-recipe="' + r.id + '">' + r.title + '</button><span class="rsub">' + r.protein + " g Eiweiß, " + r.kcal + " kcal, " + r.time + " Min, ca. " + eur(r.cost) + "</span>" + (notes[key] || []).slice(0, 2).map((t) => '<span class="rrest">' + esc(t) + "</span>").join("") + "</div>" +
            '<div class="ract"><button class="fchip" data-rlock="' + key + '" aria-pressed="' + (s.locked ? "true" : "false") + '">' + (s.locked ? "Fixiert" : "Fixieren") + '</button><button class="fchip" data-rspin="' + key + '"' + (rad.busy ? " disabled" : "") + ">Neu drehen</button></div>"
            : '<div class="rbody"><span class="rpend">…</span></div><div></div>') + "</li>";
      }).join("") + "</ul>" + (RAD.mode === "meal" ? "" : "") + "</section>";
  }).join("") + radShopHTML(P);
}
let ROPEN = false;
function renderRadOpts() {
  const tog = (k, label) => '<button class="fchip" data-ropt="' + k + '" aria-pressed="' + (RAD[k] ? "true" : "false") + '">' + label + "</button>";
  $$("[data-rmode]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.rmode === RAD.mode ? "true" : "false"));
  let h = "";
  if (RAD.mode === "meal") h += ["Frühstück", "Mittag/Abend", "Snack", "Egal"].map((m) => '<button class="fchip" data-rmeal="' + m + '" aria-pressed="' + (RAD.meal === m ? "true" : "false") + '">' + m + "</button>").join("");
  if (RAD.mode === "day") h += tog("bfDay", "Mit Frühstück");
  if (RAD.mode === "week") h += tog("bfWeek", "Frühstück auch unter der Woche");
  if (RAD.mode === "week") h += tog("reste", "Reste verwerten");
  h += tog("noSpinat", "Ohne Spinat") + tog("cheap", "Günstig") + tog("work", RAD.mode === "meal" ? "Für die Arbeit" : "Mittag zum Mitnehmen");
  const seg = (label, items, attr, cur) => '<div class="segwrap"><span class="small muted">' + label + '</span><div class="seg">' + items.map((x) => '<button class="segb" data-' + attr + '="' + x[0] + '" aria-pressed="' + (cur === x[0]) + '">' + x[1] + "</button>").join("") + "</div></div>";
  const sum = [RAD.mode === "meal" ? RAD.meal : RAD.mode === "day" ? (RAD.bfDay ? "Mit Frühstück" : "Ohne Frühstück") : RAD.bfWeek ? "Frühstück täglich" : "", RAD.mode === "week" && RAD.reste ? "Reste verwerten" : "", RAD.noSpinat ? "Ohne Spinat" : "", RAD.cheap ? "Günstig" : "", RAD.work ? (RAD.mode === "meal" ? "Für die Arbeit" : "Mittag zum Mitnehmen") : "", RAD.mode !== "meal" && RAD.maxDay ? "bis " + RAD.maxDay + " € am Tag" : "", RAD.people + (RAD.people === 1 ? " Person" : " Personen")].filter(Boolean).join(", ");
  h = '<details class="radmore" id="radmore"' + (ROPEN ? " open" : "") + '><summary><span class="rsum"><b>Einstellungen</b><span>' + sum + '</span></span></summary><div class="radbody"><div class="chips">' + h + '</div><div class="radsegs">' + (RAD.mode !== "meal" ? seg("Preis pro Tag", [[0, "Egal"], [6, "bis 6 €"], [5, "bis 5 €"]], "rmax", RAD.maxDay) : "") + seg("Für", [[1, "1 Person"], [2, "2 Personen"]], "rpeople", RAD.people) + '</div><p class="small muted">Die „Ohne“-Filter aus dem Bereich Rezepte gelten auch hier.</p></div></details>';
  $("#radopts").innerHTML = h;
  $("#spin").textContent = "Drehen";
  $("#spin").setAttribute("aria-label", { meal: "Mahlzeit drehen", day: "Tag drehen", week: "Woche drehen" }[RAD.mode]);
}

/* ======================= Einkauf (Lidl-Richtwerte) ======================= */
let CART = store.get("fc_cart", []);
let BUDGET = store.get("fc_budget", 0);
let CHK = store.get("fc_chk", {});
const SECS = ["Obst & Gemüse", "Kühlregal", "Fleisch & Wurst", "Brot & Backwaren", "Nudeln, Reis & Trockenes", "Tiefkühl", "Vorrat"];
const esc = (x) => String(x == null ? "" : x).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const EURF = new Intl.NumberFormat("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const eur = (n) => EURF.format(n) + "\u00a0€";
const saveCart = () => { store.set("fc_cart", CART); store.set("fc_budget", BUDGET); store.set("fc_chk", CHK); };
function needTxt(k, g) {
  const p = PRICE[k], q = g / p.per;
  if (p.u === "g" || p.u === "ml") return "brauchst " + Math.round(g) + " " + p.u;
  const r = Math.round(q * 10) / 10;
  if (p.u === "Stk") return "brauchst " + nf(r) + " " + (r > 1 && p.pl ? p.pl : p.n);
  return "brauchst " + nf(r) + " " + p.u;
}
function shopCalc(entries) {
  const need = {};
  entries.forEach((en) => {
    const r = byId(en.id); if (!r) return;
    r.ing.forEach((i) => { if (i[0] == null || !i[4]) return; need[i[4]] = (need[i[4]] || 0) + i[0] * PRICE[i[4]].per * en.n; });
  });
  const lines = Object.keys(need).map((k) => {
    const p = PRICE[k], g = need[k];
    if (p.loose) { const gg = Math.ceil(g / 100 - 1e-9) * 100; return { k, name: p.n, buy: "ca. " + gg + " g", need: "", cost: gg / 1000 * p.price, sec: p.staple ? "Vorrat" : p.sec, staple: !!p.staple }; }
    const packs = Math.ceil(g / p.pack - 1e-9);
    return { k, name: p.n, buy: packs + " × " + p.label, need: needTxt(k, g), cost: packs * p.price, sec: p.staple ? "Vorrat" : p.sec, staple: !!p.staple, left: packs * p.pack - g };
  });
  return { lines, used: new Set(entries.map((e) => e.id)), total: lines.filter((l) => !l.staple).reduce((a, l) => a + l.cost, 0) };
}
const stFor = (k) => STORE.find((x) => x.keys.includes(k));
let RBYING = null, RBYINGN = -1;
const recipesWith = (k) => { if (!RBYING || RBYINGN !== RECIPES.length) { RBYINGN = RECIPES.length; RBYING = {}; RECIPES.forEach((r) => new Set(r.ing.map((i) => i[4])).forEach((key) => { if (key) (RBYING[key] = RBYING[key] || []).push(r); })); } return RBYING[k] || []; };
function restIdeas(k, left, used) {
  return recipesWith(k).filter((r) => !used.has(r.id) && !isExc(r) && !(RAD.noSpinat && hasSpin(r)) &&
    r.ing.some((i) => i[4] === k && i[0] != null && i[0] * PRICE[k].per <= left + 1e-6)).sort((a, b) => a.cost - b.cost).slice(0, 2);
}
function restHTML(l, used) {
  const p = PRICE[l.k], st = stFor(l.k);
  if (!st || !st.short || l.staple) return "";
  if (l.k === "erdb") return '<span class="srest warnt">Wichtig: ' + st.short + "</span>";
  if (l.left == null || l.left < 0.2 * p.pack) return "";
  let amt = "";
  if (p.u === "g" || p.u === "ml") amt = " ca. " + Math.max(10, Math.round(l.left / 10) * 10) + " " + p.u;
  else if (p.u === "Stk") { const n = Math.floor(l.left / p.per); if (n < 1) return ""; amt = " " + n + " " + (n > 1 && p.pl ? p.pl : p.n); }
  const ideas = restIdeas(l.k, l.left, used);
  return '<span class="srest">Rest' + amt + ": " + st.short + (ideas.length ? " Dazu passt: " + ideas.map((r) => r.title).join(" oder ") + "." : "") + "</span>";
}
let SHOPDONEOPEN = false, SHOPN = 0; const SHOPCALCS = {};
function shopRow(l, calc) {
  return '<label class="sline' + (CHK[l.k] ? " done" : "") + '"><input type="checkbox" data-chk="' + l.k + '"' + (CHK[l.k] ? " checked" : "") + '><span class="sname">' + l.name + '</span><span class="sbuy">' + l.buy + (l.need ? ' <span class="muted">(' + l.need + ")</span>" : "") + '</span><span class="sprice">' + (l.staple ? "" : eur(l.cost)) + "</span>" + restHTML(l, calc.used) + "</label>";
}
function shopListInner(calc) {
  const by = {}, done = [];
  calc.lines.forEach((l) => { if (CHK[l.k]) done.push(l); else (by[l.sec] = by[l.sec] || []).push(l); });
  const byName = (a, b) => a.name.localeCompare(b.name, "de");
  const open = SECS.filter((s) => by[s]).map((s) => '<div class="sgroup"><h4>' + s + (s === "Vorrat" ? ' <span class="muted small">nur kaufen, wenn leer</span>' : "") + "</h4>" + by[s].sort(byName).map((l) => shopRow(l, calc)).join("") + "</div>").join("");
  done.sort((a, b) => SECS.indexOf(a.sec) - SECS.indexOf(b.sec) || byName(a, b));
  const dn = done.length ? '<details class="exmore doneshop"' + (SHOPDONEOPEN ? " open" : "") + "><summary>Bereits abgehakt (" + done.length + ")</summary>" + done.map((l) => shopRow(l, calc)).join("") + "</details>" : "";
  return (open || (done.length ? '<p class="muted small shopall">Alles abgehakt. Gut gemacht.</p>' : "")) + dn;
}
function shopListHTML(calc) {
  const id = ++SHOPN; SHOPCALCS[id] = calc;
  Object.keys(SHOPCALCS).slice(0, -40).forEach((k) => { SHOPCALCS[k] = undefined; });
  return '<div class="shoplist" data-sl="' + id + '">' + shopListInner(calc) + "</div>";
}
function shopRefresh(key) {
  $$("[data-sl]").forEach((b) => { const c = SHOPCALCS[b.dataset.sl]; if (c) b.innerHTML = shopListInner(c); });
  const vis = (sel) => [...document.querySelectorAll(sel)].find((x) => x.offsetParent);
  const nb = key ? vis('[data-chk="' + key + '"]') : null;
  if (nb && !nb.closest("details:not([open])")) nb.focus({ preventScroll: true });
  else { const s = vis(".doneshop > summary"); if (s) s.focus({ preventScroll: true }); }
}
document.addEventListener("toggle", (ev) => { const d = ev.target; if (d && d.classList && d.classList.contains("doneshop")) SHOPDONEOPEN = d.open; }, true);
function cartAdd(id, n) {
  const c = CART.find((x) => x.id === id);
  if (c) c.n = Math.min(24, c.n + n); else CART.push({ id, n });
  saveCart(); renderShop();
}
function planEntries(plan, onlyShown) {
  const m = {};
  plan.days.forEach((d, di) => d.slots.forEach((s, si) => { if (onlyShown && !rad.shown.has(di + ":" + si)) return; m[s.id] = (m[s.id] || 0) + RAD.people; }));
  return Object.keys(m).map((id) => ({ id, n: m[id] }));
}
function radShopHTML(plan) {
  const calc = shopCalc(planEntries(plan, true));
  if (!calc.lines.length) return "";
  return '<section class="card radshop"><div class="rday-h"><h3>Einkauf für ' + RAD.people + (RAD.people === 1 ? " Person" : " Personen") + '</h3><span class="rtot">ca. ' + eur(calc.total) + " bei Lidl" + (RAD.people > 1 ? ", pro Person ca. " + eur(calc.total / RAD.people) : "") + "</span></div>" +
    shopListHTML(calc) +
    '<div class="row"><button class="btn primary" data-cartplan="1">In meine Einkaufsliste</button></div>' +
    '<p class="small muted">Richtwerte für Lidl. Vorrat wie Öl und Gewürze ist nicht mitgerechnet.</p></section>';
}
function protTable() {
  return ["hafer", "linse", "quark", "skyr", "milch", "ei", "gouda", "moz", "ghack", "haehn", "rhack", "pute", "parm", "mandel"]
    .map((k) => ({ name: PRICE[k].n, gpe: PRICE[k].p * PRICE[k].pack / 100 / PRICE[k].price })).sort((a, b) => b.gpe - a.gpe);
}
function storeCardHTML() {
  const groups = [];
  STORE.forEach((x) => { let g = groups.find((y) => y[0] === x.g); if (!g) groups.push(g = [x.g, []]); g[1].push(x); });
  return '<div class="card"><div><h3>Frisch halten und einfrieren</h3><p class="muted">So bleibt der Rest aus der Packung gut. Das sind Faustregeln, das Verbrauchsdatum auf der Packung geht vor. Der Kühlschrank sollte höchstens 7 °C haben, besser 4 bis 5 °C, das Gefrierfach -18 °C. Beschrifte Portionen mit Datum und friere aufgetautes Fleisch nicht noch einmal ein.</p></div>' +
    groups.map((g) => '<details class="stg"' + (g[0] === "Kühlregal" ? " open" : "") + "><summary>" + g[0] + "</summary>" +
      g[1].map((x) => '<div class="sti"><h4>' + x.name + "</h4><p><b>Offen:</b> " + x.open + "</p><p><b>Einfrieren:</b> " + x.freeze + "</p>" + (x.tip ? '<p class="muted">' + x.tip + "</p>" : "") + "</div>").join("") + "</details>").join("") + "</div>";
}
function renderShop() {
  const calc = shopCalc(CART), portions = CART.reduce((a, c) => a + c.n, 0);
  const rows = CART.map((c, i) => {
    const r = byId(c.id);
    return '<li class="crow"><button class="rtitle" data-recipe="' + r.id + '">' + r.title + '</button><span class="stepper"><button class="btn icon sm" data-cart="-1" data-ci="' + i + '" aria-label="Eine Portion weniger">−</button><b>' + c.n + '</b><button class="btn icon sm" data-cart="1" data-ci="' + i + '" aria-label="Eine Portion mehr">+</button></span></li>';
  }).join("");
  let budget = "";
  if (CART.length) {
    const left = BUDGET > 0 ? BUDGET - calc.total : null;
    budget = '<div class="budget"><label class="field">Budget für diesen Einkauf in € (optional)<input type="number" id="budget" min="0" step="1" inputmode="decimal" value="' + (BUDGET > 0 ? BUDGET : "") + '"></label>' +
      (BUDGET > 0 ? '<div class="meter" role="img" aria-label="Anteil des Budgets"><span class="' + (left < 0 ? "over" : "") + '" style="width:' + Math.min(100, Math.round(calc.total / BUDGET * 100)) + '%"></span></div><p class="small ' + (left < 0 ? "warnt" : "muted") + '">' + (left >= 0 ? "Noch " + eur(left) + " Luft." : eur(-left) + " über dem Budget. Tausch teure Gerichte gegen günstigere aus.") + "</p>" : "") + "</div>";
  }
  $("#panel-einkauf").innerHTML =
    '<div class="card shopcard" data-nofold><div><h3>Einkaufsliste</h3><p class="muted small">Richtwerte für Lidl, Stand Nov 2026.</p></div>' +
    (CART.length
      ? '<ul class="crows">' + rows + '</ul><div class="row"><button class="btn sm" data-cartclear="1">Liste leeren</button><button class="btn sm" data-tab="rezepte">Rezept hinzufügen</button><button class="btn sm" data-tab="rad">Vom Glücksrad</button></div>' +
        '<div class="stats"><div class="stat"><span class="big">' + eur(calc.total).replace("\u00a0€", "") + '<small>€</small></span><span>Einkauf gesamt (ca.)</span></div><div class="stat"><span class="big">' + eur(calc.total / portions).replace("\u00a0€", "") + '<small>€</small></span><span>pro Portion im Schnitt</span></div><div class="stat inl"><span class="big">' + portions + '</span><span>Portionen</span></div></div>' + budget
      : '<div class="empty-in"><p class="muted">Noch leer. Wähle Rezepte aus oder lass dir eine Woche planen.</p><div class="row"><button class="btn primary" data-tab="rezepte">Zu den Rezepten</button></div><div class="linkrow"><button class="linkbtn" data-tab="rad">Zum Glücksrad</button><button class="linkbtn" data-tab="vorkochen">Zum Vorkochplan</button></div></div>') + "</div>" +
    (CART.length ? '<div class="card" data-nofold><h3>Was du brauchst</h3><div class="slist">' + shopListHTML(calc) + '</div><p class="small muted">Auf ganze Packungen aufgerundet.</p></div>' : "") +
    spendHTML() +
    '<div class="card"><h3>So sparst du bei Lidl</h3><ul>' +
    "<li><b>Quark und Skyr zuerst.</b> Ein 500-g-Becher kostet etwa einen Euro und liefert rund 55 bis 60 g Eiweiß. Hähnchenbrust bringt pro Euro nur etwa die Hälfte.</li>" +
    "<li><b>Hähnchen nur im Angebot.</b> Im Oktober gab es Brustfilet im Prospekt für 5,19 € pro 600 g (8,65 € pro kg). Dann gleich mehr kaufen und portionsweise einfrieren.</li>" +
    "<li><b>Gemischtes Hack</b> kostet pro Kilo etwas weniger als Hähnchenbrust und liefert pro Euro ähnlich viel Eiweiß, hat aber mehr Fett. Drück das Fett nach dem Braten mit Küchenpapier ab.</li>" +
    "<li><b>Welches Hack?</b> Rezepte mit „Rinderhack“ sind mit fettreduziertem Rinderhack gerechnet (light, rund 5 % Fett, 160 kcal je 100 g). Rezepte mit „Hack“ sind mit gemischtem Hack gerechnet (halb Rind, halb Schwein, 250 kcal je 100 g). Normales Rinderhack aus 100 % Rind hat rund 235 kcal je 100 g.</li>" +
    "<li><b>Günstige Sattmacher:</b> Haferflocken (ca. 0,60 € pro 500 g), Linsen, Nudeln, Reis und Eier. Sie füllen den Teller, ohne das Budget zu belasten.</li>" +
    "<li><b>Tiefkühl statt frisch</b> bei Erdbeeren und Spinat. Tomaten und Paprika lose kaufen und nur so viel, wie du in der Woche isst.</li>" +
    "<li><b>Teuer pro Mahlzeit:</b> Rucola, Aufschnitt, Parmesan und Mandeln. Sparsam einsetzen.</li>" +
    "<li><b>Erst planen, dann kaufen.</b> Schau vorher in Prospekt und Lidl-Plus-App und dreh dann das Rad mit „Günstig“.</li></ul></div>" +
    storeCardHTML() + pricesHTML() +
    '<div class="card"><h3>Eiweiß pro Euro</h3><p class="muted small">So viel Eiweiß bekommst du für 1 € (Rohgewicht, Lidl-Richtwerte). Je höher, desto günstiger.</p><ol class="ptable">' +
    protTable().map((x) => "<li><span>" + x.name + "</span><b>" + Math.round(x.gpe) + " g</b></li>").join("") + "</ol></div>" +
    '<div class="card"><h3>Grundvorrat für den Anfang</h3><div class="shop">' + SHOP.map((g, gi) => "<div><h4>" + g[0] + "</h4>" + g[1].map((n, i) => '<label><input type="checkbox" data-shop="' + gi + "-" + i + '"' + (shop[gi + "-" + i] ? " checked" : "") + "> " + n + "</label>").join("") + "</div>").join("") + "</div></div>";
  foldCards($("#panel-einkauf"));
}

/* ======================= Ziele, Tagebuch, Heute, Protokoll ======================= */
let GOALS = Object.assign({ kcal: 1900, protein: 0, water: 6, pause: "small", sched: {} }, store.get("fc_goals", {}));
let DIARY = store.get("fc_diary", {});
let WK = store.get("fc_wk", []);
/* Gespeicherte Daten prüfen: falsch geformte Einträge werden aussortiert, statt die App zu stoppen */
(function sanitizeState() {
  const isObj = (x) => x !== null && typeof x === "object" && !Array.isArray(x);
  const num = (x, lo, hi, d) => (typeof x === "number" && isFinite(x) ? Math.min(hi, Math.max(lo, Math.round(x))) : d);
  log = log.filter((x) => isObj(x) && typeof x.date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(x.date)).map((x) => { const o = Object.assign({}, x); ["weight", "waist", "pushups", "plank"].forEach((k) => { if (o[k] != null && !(typeof o[k] === "number" && isFinite(o[k]))) o[k] = null; }); return o; });
  sessions = sessions.filter((x) => typeof x === "string");
  EXC = EXC.filter((x) => typeof x === "string"); FAV = FAV.filter((x) => typeof x === "string");
  /* Rezepte, die es nach einem Update nicht mehr gibt, fliegen aus dem Warenkorb (sonst stürzt die Einkaufsliste ab) */
  CART = CART.filter((x) => isObj(x) && typeof x.id === "string" && byId(x.id) && typeof x.n === "number" && isFinite(x.n) && x.n > 0);
  const numOrNull = (x) => (typeof x === "number" && isFinite(x) ? x : null);
  WK = WK.filter((x) => isObj(x) && typeof x.date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(x.date) && Array.isArray(x.sets)).map((x) => ({
    date: x.date, min: num(x.min, 1, 600, 1), q: x.q ? 1 : 0, effort: ["leicht", "genau", "schwer"].includes(x.effort) ? x.effort : "",
    sets: x.sets.filter((s) => isObj(s) && typeof s.ex === "string").map((s) => ({ ex: s.ex, lvl: num(s.lvl, 0, 50, 0), set: num(s.set, 1, 20, 1), reps: numOrNull(s.reps), secs: numOrNull(s.secs) }))
  }));
  Object.keys(DIARY).forEach((k) => {
    const d = DIARY[k];
    if (!isObj(d) || !Array.isArray(d.items)) { delete DIARY[k]; return; }
    d.items = d.items.filter(isObj).map((x) => { const o = Object.assign({}, x, { t: String(x.t == null ? "Eintrag" : x.t).slice(0, 80), k: num(x.k, 0, 20000, 0), p: num(x.p, 0, 2000, 0), c: typeof x.c === "number" && isFinite(x.c) ? x.c : 0 }); if (Array.isArray(x.det)) o.det = x.det.map(String).slice(0, 30); else delete o.det; return o; });
    if (typeof d.water !== "number" || !isFinite(d.water)) d.water = 0;
    if (d.plan !== undefined) {
      const pl = d.plan;
      if (!isObj(pl) || !Array.isArray(pl.ids) || !pl.ids.every((id) => typeof id === "string")) delete d.plan;
      else d.plan = { ids: pl.ids.slice(0, 10), done: pl.ids.slice(0, 10).map((_, i) => !!(Array.isArray(pl.done) && pl.done[i])), free: !!pl.free, late: !!pl.late };
    }
  });
  /* Rad: Einstellungen und gespeicherte Pläne prüfen */
  if (!["day", "week", "meal"].includes(RAD.mode)) RAD.mode = "day";
  if (typeof RAD.meal !== "string" || !["Frühstück", "Mittag/Abend", "Snack", "Egal"].includes(RAD.meal)) RAD.meal = "Mittag/Abend";
  RAD.people = num(RAD.people, 1, 8, 2); RAD.maxDay = num(RAD.maxDay, 0, 100, 0); RAD.reste = RAD.reste !== false;
  if (!isObj(RPL)) RPL = {};
  Object.keys(RPL).forEach((k) => {
    const pl = RPL[k];
    const ok = ["day", "week", "meal"].includes(k) && isObj(pl) && Array.isArray(pl.days) && pl.days.length <= 7 && pl.days.every((d) => isObj(d) && typeof d.name === "string" && Array.isArray(d.slots) && d.slots.every((s) => isObj(s) && typeof s.id === "string" && byId(s.id) && typeof s.label === "string"));
    if (!ok) { delete RPL[k]; return; }
    pl.days = pl.days.map((d) => ({ name: d.name.slice(0, 40), slots: d.slots.slice(0, 8).map((s) => ({ label: s.label.slice(0, 40), k: typeof s.k === "string" ? s.k : "", work: !!s.work, id: s.id, locked: !!s.locked })) }));
  });
  Object.keys(levels).forEach((k) => { if (typeof levels[k] !== "number" || !isFinite(levels[k]) || levels[k] < 0) delete levels[k]; });
  if (!Array.isArray(settings.tdays) || settings.tdays.length !== 7) settings.tdays = [1, 0, 1, 0, 1, 0, 0]; settings.tdays = settings.tdays.map((v) => (v ? 1 : 0));
  if (!isObj(settings.gear)) settings.gear = {}; Object.keys(settings.gear).forEach((k) => { if (settings.gear[k] !== true || !GEAR.some((g) => g.id === k && !g.never)) delete settings.gear[k]; });
  if (!isObj(settings.ms)) settings.ms = {}; Object.keys(settings.ms).forEach((k) => { if (!MILES.some((m) => m.id === k && !m.auto) || !/^\d{4}-\d{2}-\d{2}$/.test(String(settings.ms[k]))) delete settings.ms[k]; });
  if (!isObj(settings.alt)) settings.alt = {}; Object.keys(settings.alt).forEach((k) => { const v = settings.alt[k], e = typeof v === "string" ? exById(v) : null; if (!e || e.slot !== k) delete settings.alt[k]; }); applyAlts();
  MYD = (Array.isArray(MYD) ? MYD : []).filter((d) => isObj(d) && typeof d.name === "string" && [d.k, d.p, d.w].every((x) => typeof x === "number" && isFinite(x)) && d.w > 0 && d.k >= 0 && d.p >= 0).slice(0, 60).map((d) => ({ id: String(d.id || d.name), name: d.name.slice(0, 60), k: d.k, p: d.p, c: typeof d.c === "number" && isFinite(d.c) ? d.c : 0, w: d.w, est: !!d.est, lg: typeof d.lg === "number" && d.lg > 0 ? d.lg : 250, text: typeof d.text === "string" ? d.text.slice(0, 400) : "" }));
  if (!isObj(PREP)) PREP = Object.assign({}, PREPDEF);
  PREP.people = num(PREP.people, 1, 4, 2); PREP.days = num(PREP.days, 3, 6, 6); PREP.n = num(PREP.n, 1, 3, 2); PREP.brk = !!PREP.brk; PREP.snk = !!PREP.snk; PREP.eco = PREP.eco !== false;
  if (typeof PREP.week !== "string") PREP.week = ""; if (!isObj(PREP.done)) PREP.done = {};
  if (!isObj(PREP.plans)) PREP.plans = {}; if (typeof PREP.autoDay !== "string") PREP.autoDay = "";
  Object.keys(PREP.plans).forEach((k) => { const pl = PREP.plans[k]; if (!/^\d{4}-\d{2}-\d{2}$/.test(k) || !isObj(pl) || !Array.isArray(pl.main)) { delete PREP.plans[k]; return; } pl.main = pl.main.filter((id) => typeof id === "string" && byId(id)); pl.b = typeof pl.b === "string" && byId(pl.b) ? pl.b : ""; pl.s = typeof pl.s === "string" && byId(pl.s) ? pl.s : ""; if (!isObj(pl.done)) pl.done = {}; if (!pl.main.length) delete PREP.plans[k]; });
  Object.keys(PREP.plans).sort().slice(0, -8).forEach((k) => delete PREP.plans[k]);
  PREP.main = Array.isArray(PREP.main) ? PREP.main.filter((id) => typeof id === "string" && byId(id)) : []; if (typeof PREP.b !== "string" || !byId(PREP.b)) PREP.b = ""; if (typeof PREP.s !== "string" || !byId(PREP.s)) PREP.s = "";
  settings.text = [100, 115, 130, 150, 175, 200].includes(settings.text) ? settings.text : 100;
  settings.sets = num(settings.sets, 1, 6, 2); settings.rest = num(settings.rest, 10, 600, 90); settings.hold = num(settings.hold, 5, 180, 30);
  prof.weight = num(prof.weight, 30, 300, 80); prof.height = num(prof.height, 100, 230, 175);
  GOALS.kcal = num(GOALS.kcal, 800, 6000, 1900); GOALS.protein = num(GOALS.protein, 0, 400, 0); GOALS.water = num(GOALS.water, 1, 30, 6);
  BUDGET = typeof BUDGET === "number" && isFinite(BUDGET) && BUDGET > 0 ? BUDGET : 0;
})();
let SESS = null, SUMIDX = -1;
const protGoal = () => (GOALS.protein > 0 ? GOALS.protein : Math.round(prof.weight * 1.6));
const saveToday = () => { store.set("fc_goals", GOALS); store.set("fc_diary", DIARY); store.set("fc_wk", WK); };
const dayGet = (d) => DIARY[d || todayISO()] || { items: [], water: 0 };
const dayEns = (d) => { const k = d || todayISO(); return DIARY[k] || (DIARY[k] = { items: [], water: 0 }); };
const dsum = (d) => dayGet(d).items.reduce((a, x) => ({ k: a.k + x.k, p: a.p + x.p, c: a.c + (x.c || 0) }), { k: 0, p: 0, c: 0 });
const WD = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
const MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
const shiftDay = (iso, k) => { const x = new Date(iso + "T12:00:00"); x.setDate(x.getDate() + k); return isoOf(x); };
const weekStartISO = (iso) => { const x = new Date(iso + "T12:00:00"); return shiftDay(iso, -((x.getDay() + 6) % 7)); };
/* Schichtplan: je Woche (Schlüssel = Montag) sieben Zeichen für Mo bis So: n = Früh, l = Spät, f = frei */
const SH_DEF = "nnnnnnf", SH_NAME = { n: "Früh", l: "Spät", f: "Frei" };
const shOk = (x) => typeof x === "string" && /^[nlf]{7}$/.test(x);
const shIdx = (iso) => (new Date(iso + "T12:00:00").getDay() + 6) % 7;
if (!GOALS.sched || typeof GOALS.sched !== "object" || Array.isArray(GOALS.sched)) GOALS.sched = {};
Object.keys(GOALS.sched).forEach((k) => { if (!/^\d{4}-\d{2}-\d{2}$/.test(k) || !shOk(GOALS.sched[k])) delete GOALS.sched[k]; });
if (GOALS.shift === "late") { const w0 = weekStartISO(todayISO()); if (!GOALS.sched[w0]) GOALS.sched[w0] = "llllllf"; }
delete GOALS.shift;
GOALS.buys = (Array.isArray(GOALS.buys) ? GOALS.buys : []).filter((x) => x && typeof x === "object" && /^\d{4}-\d{2}-\d{2}$/.test(x.d) && typeof x.a === "number" && isFinite(x.a) && x.a > 0 && x.a <= 2000).map((x) => ({ d: x.d, a: Math.round(x.a * 100) / 100 })).sort((a, b) => (a.d < b.d ? -1 : a.d > b.d ? 1 : 0)).slice(-400);
GOALS.hh = Number.isInteger(GOALS.hh) && GOALS.hh >= 1 && GOALS.hh <= 4 ? GOALS.hh : 2;
["lastBackup", "bkSnooze"].forEach((k) => { if (typeof GOALS[k] !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(GOALS[k])) delete GOALS[k]; });
function shGet(ws) {
  const S = GOALS.sched;
  if (shOk(S[ws])) return S[ws];
  const ks = Object.keys(S).filter((k) => k < ws && shOk(S[k])).sort();
  return ks.length ? S[ks[ks.length - 1]] : SH_DEF;
}
const shiftOf = (iso) => shGet(weekStartISO(iso))[shIdx(iso)];
function shPut(ws, str) {
  GOALS.sched[ws] = str;
  const ks = Object.keys(GOALS.sched).sort(); while (ks.length > 12) delete GOALS.sched[ks.shift()];
}
function shSet(iso, v) {
  if (!SH_NAME[v]) return;
  const ws = weekStartISO(iso), cur = shGet(ws).split(""); cur[shIdx(iso)] = v; shPut(ws, cur.join(""));
}
const weekCountISO = (ws) => sessions.filter((s) => weekStartISO(s) === ws).length;
function weekStreak() {
  let ws = weekStartISO(todayISO()), n = 0;
  if (weekCountISO(ws) < 2) ws = shiftDay(ws, -7);
  while (weekCountISO(ws) >= 2 && n < 520) { n++; ws = shiftDay(ws, -7); }
  return n;
}
const dateDE = (iso) => iso.slice(8) + "." + iso.slice(5, 7) + ".";

/* Ringe */
/* Die Ringe füllen sich beim Öffnen von Heute einmal sanft, bei jedem weiteren Neuzeichnen (Eintrag, Wasser) bleiben sie ruhig. */
let RINGANIM = true;
function animRings() {
  if (!RINGANIM) return;
  RINGANIM = false;
  if (reduceMotion()) return;
  document.querySelectorAll("#panel-heute .rgb").forEach((c, i) => {
    const to = parseFloat(c.style.strokeDashoffset), from = parseFloat(c.style.strokeDasharray);
    if (c.animate && from > to) c.animate([{ strokeDashoffset: from }, { strokeDashoffset: to }], { duration: 800, delay: i * 120, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)", fill: "backwards" });
  });
  document.querySelectorAll("#panel-heute .td.on").forEach((d, i) => { if (d.animate) d.animate([{ transform: "scale(0.3)", opacity: 0 }, { transform: "scale(1)", opacity: 1 }], { duration: 340, delay: 450 + i * 90, easing: "cubic-bezier(0.2, 0.8, 0.2, 1)", fill: "backwards" }); });
}
/* Heute: ein Kreis. Außen Eiweiß, innen dünner Kalorien, in der Mitte die Punkte fürs Training der Woche. Die Zahlen stehen daneben. */
function trioHTML(pv, pg, kv, kg, wc, n) {
  const arc = (r, f, color, cls) => {
    const C = 2 * Math.PI * r, g = Math.max(0, Math.min(1, f || 0));
    return '<circle cx="50" cy="50" r="' + r + '" class="rgt ' + cls + '"/><circle cx="50" cy="50" r="' + r + '" class="rgb ' + cls + '" style="stroke:' + color + ";stroke-dasharray:" + C.toFixed(1) + ";stroke-dashoffset:" + (C * (1 - g)).toFixed(1) + '"/>';
  };
  const over = kv > kg + 150, nd = Math.max(1, n);
  const dots = Array.from({ length: nd }, (_, i) => '<i class="td' + (i < wc ? " on" : "") + '"></i>').join("");
  const leg = (sw, name, val, extra) => '<li><i class="sw ' + sw + '"></i><div><b>' + name + "</b><span>" + val + "</span>" + (extra || "") + "</div></li>";
  return '<div class="rings"><div class="rgbox" aria-hidden="true"><svg viewBox="0 0 100 100" class="rg">' + arc(45, pv / pg, "var(--good)", "o") + arc(34, kv / kg, over ? "var(--warn)" : "var(--accent)", "i") +
    '</svg><div class="rgc"><div class="tdots">' + dots + "</div><span>" + wc + " von " + n + "</span></div></div>" +
    '<ul class="rleg">' + leg("sw-o", "Eiweiß", pv + " von " + pg + " g") +
    leg("sw-i" + (over ? " warn" : ""), "Kalorien", kv.toLocaleString("de-DE") + " von " + kg.toLocaleString("de-DE") + " kcal", over ? '<span class="warnt">über dem Ziel</span>' : "") +
    leg("sw-t", "Training", wc + " von " + n + " diese Woche") + "</ul></div>";
}

/* Vorschläge: was passt noch zum Tag */
function suggestList(n) {
  const e = dsum(), remP = Math.max(0, protGoal() - e.p), remK = GOALS.kcal - e.k;
  const score = (r) => Math.min(r.protein, remP || r.protein) / (r.cost + 0.4) - (r.kcal > Math.max(250, remK + 150) ? 25 : 0);
  return RECIPES.filter((r) => !isExc(r) && !(RAD.noSpinat && hasSpin(r)) && r.cost <= 3).sort((a, b) => score(b) - score(a)).slice(0, n);
}
/* Tagesvorschlag: Essen vor der Arbeit, in der Pause und abends */
const PLAN_LABELS = { late: ["Vor der Arbeit, in Ruhe essen", "Pause auf der Arbeit, ohne Aufwand", "Nach der Arbeit, schnell"], work: ["Vor der Arbeit", "Pause auf der Arbeit", "Abends nach der Arbeit", "Später am Abend, optional"], free: ["Frühstück", "Mittagessen", "Abendessen", "Später am Abend, optional"] };
const PLAN_HARD = ["bohne", "kiche", "linse", "kokos", "stueck"];
const isLate = (free) => !free && shiftOf(todayISO()) === "l";
function planPool(i, free, late) {
  const small = GOALS.pause !== "meal", lt = late === undefined ? isLate(free) : !!late;
  const base = RECIPES.filter((r) => !isExc(r) && !(RAD.noSpinat && hasSpin(r)));
  const kind = (m, tag) => { const a = base.filter((r) => r.meal === m && (!tag || r.tags.includes(tag))); return a.length ? a : base.filter((r) => r.meal === m); };
  /* Pause: nur Einfaches ohne Dosenzutaten, die man oft nicht zuhause hat */
  const easy = (a) => { const l = a.filter((r) => !r.ing.some((x) => PLAN_HARD.includes(x[4]))); return l.length ? l : a; };
  if (lt) {
    if (i === 0) { const m = base.filter((r) => r.meal === "Mittag/Abend" && r.time <= 35 && r.protein >= 35); return m.length >= 6 ? m : kind("Mittag/Abend"); }
    if (i === 1) return easy(small ? kind("Snack", "Für die Arbeit") : kind("Mittag/Abend", "Für die Arbeit"));
    if (i === 2) { const m = base.filter((r) => r.meal === "Mittag/Abend" && r.time <= 20); return m.length >= 6 ? m : kind("Mittag/Abend"); }
    return [];
  }
  if (i === 0) { const l = base.filter((r) => r.meal === "Frühstück" && r.time <= 15); return l.length ? l : kind("Frühstück"); }
  if (i === 1) return free ? kind("Mittag/Abend") : easy(small ? kind("Snack", "Für die Arbeit") : kind("Mittag/Abend", "Für die Arbeit"));
  if (i === 2) return kind("Mittag/Abend");
  return base.filter((r) => r.meal === "Snack");
}
const mkPlan = (ids, free, old) => ({ ids, done: ids.map((x, k) => !!(old && old.done && old.done[k] && old.ids[k] === x)), free: !!free, late: isLate(free) });
function planScore(recs, remP, remK) {
  const p = recs.reduce((a, r) => a + r.protein, 0), k = recs.reduce((a, r) => a + r.kcal, 0), c = recs.reduce((a, r) => a + r.cost, 0);
  let sc = -recs.filter((r) => FAV.includes(r.id)).length * 3 + Math.max(0, remP * 0.95 - p) * 4 + Math.max(0, k - (remK + 200)) / 8 + Math.max(0, (remK - 500) - k) / 8 + c * 3 + (RAD.maxDay ? Math.max(0, c - RAD.maxDay) * 40 : 0);
  if (mainKind(recs[1]) === mainKind(recs[2]) && recs[1].meal === "Mittag/Abend") sc += 25;
  if (recs[0].meal === "Mittag/Abend" && mainKind(recs[0]) === mainKind(recs[2])) sc += 25;
  return sc;
}
function makeDayPlan(free, keep) {
  const late = isLate(free);
  const e = dsum(), remP = Math.max(0, protGoal() - e.p), remK = Math.max(0, GOALS.kcal - e.k);
  const pools = [0, 1, 2].map((i) => planPool(i, free, late));
  if (pools.some((p) => !p.length)) return null;
  let best = null, bs = Infinity;
  for (let n = 0; n < 500; n++) {
    const pick = [], taken = new Set();
    for (let i = 0; i < 3; i++) {
      let r = keep && keep[i] ? byId(keep[i]) : null;
      if (!r) { const c = pools[i].filter((x) => !taken.has(x.id)); r = pickRnd(c.length ? c : pools[i]); }
      pick.push(r); taken.add(r.id);
    }
    const sc = planScore(pick, remP, remK);
    if (sc < bs) { bs = sc; best = pick; }
  }
  const ids = best.map((r) => r.id), sum = best.reduce((a, r) => a + r.protein, 0);
  if (sum < remP - 12 && !late) {
    const k = best.reduce((a, r) => a + r.kcal, 0), pool = planPool(3, free, late).filter((r) => !ids.includes(r.id) && k + r.kcal <= remK + 250);
    if (pool.length) ids.push(pool.sort((a, b) => b.protein / (b.cost + 0.3) - a.protein / (a.cost + 0.3))[0].id);
  }
  return ids;
}
function planEnsure() {
  const day = dayEns();
  if (!day.plan || !Array.isArray(day.plan.ids) || day.plan.ids.some((id) => !byId(id))) {
    const free = day.plan && typeof day.plan.free === "boolean" ? day.plan.free : shiftOf(todayISO()) === "f", ids = makeDayPlan(free);
    if (!ids) { delete day.plan; return null; }
    day.plan = mkPlan(ids, free);
    saveToday();
  }
  return day.plan;
}
function planRe(i) {
  const day = dayEns(), pl = day.plan; if (!pl) return;
  const cur = pl.ids[i], pool = planPool(i, pl.free, !!pl.late).filter((r) => !pl.ids.includes(r.id) || r.id === cur);
  const others = pool.filter((r) => r.id !== cur);
  if (!others.length) return;
  const e = dsum(), remP = Math.max(0, protGoal() - e.p), remK = Math.max(0, GOALS.kcal - e.k), base = pl.ids.slice(0, 3).map((id) => byId(id));
  const scored = others.map((r) => { const t = base.slice(); if (i < 3) t[i] = r; return { r, sc: i < 3 ? planScore(t, remP, remK) : -r.protein }; }).sort((a, b) => a.sc - b.sc);
  pl.ids[i] = pickRnd(scored.slice(0, Math.min(5, scored.length))).r.id; pl.done[i] = false;
  saveToday(); renderToday();
}
function planEat(i) {
  const day = dayEns(), pl = day.plan; if (!pl || pl.done[i]) return;
  const r = byId(pl.ids[i]); if (!r) return;
  pl.done[i] = true; logEat(r, 1);
}
function planAll() {
  const day = dayEns(), pl = day.plan; if (!pl) return;
  pl.ids.forEach((id, i) => { if (!pl.done[i]) { const r = byId(id); if (r) { pl.done[i] = true; day.items.push({ id: r.id, t: r.title, k: r.kcal, p: r.protein, c: Math.round(r.cost * 100) / 100 }); } } });
  saveToday(); renderToday();
}
function shiftHintHTML() {
  const t = todayISO(), a = shiftOf(t), b = shiftOf(shiftDay(t, 1)), N = { n: "Frühschicht", l: "Spätschicht", f: "frei" };
  const H = { n: "Training eher abends.", l: "Training vormittags, dann in Ruhe essen.", f: "Zeit fürs Kochen und Training." };
  return '<p class="shifthint"><button type="button" class="tag g shpill" data-shiftedit="1" aria-label="Schichten eintragen. Heute ' + N[a] + '">Heute ' + N[a] + '</button><button type="button" class="tag shpill" data-shiftedit="1" aria-label="Schichten eintragen. Morgen ' + N[b] + '">Morgen ' + N[b] + '</button><span class="shtxt">' + H[a] + "</span></p>";
}
function shAfter() {
  const d = dayEns(), free = shiftOf(todayISO()) === "f", ids = makeDayPlan(free);
  if (ids) d.plan = mkPlan(ids, free);
  saveToday(); renderToday(); if ($("#dlg-shift").open) renderShiftDlg();
}
function shChange(iso, v) { shSet(iso, v); if (iso === todayISO()) return shAfter(); saveToday(); if ($("#dlg-shift").open) renderShiftDlg(); }
function renderShiftDlg() {
  const t0 = weekStartISO(todayISO()), WDN = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
  const week = (ws, title) => {
    const cur = shGet(ws);
    const rows = [0, 1, 2, 3, 4, 5, 6].map((i) => { const iso = shiftDay(ws, i); return '<div class="shrow' + (iso === todayISO() ? " today" : "") + '"><span class="shday">' + WDN[i] + " " + dateDE(iso) + '</span><div class="seg">' + ["n", "l", "f"].map((v) => '<button class="segb" type="button" data-shd="' + iso + ":" + v + '" aria-pressed="' + (cur[i] === v) + '">' + SH_NAME[v] + "</button>").join("") + "</div></div>"; }).join("");
    return '<div class="shweek"><div class="rday-h"><h4>' + title + " (" + dateDE(ws) + " bis " + dateDE(shiftDay(ws, 6)) + ')</h4></div><div class="row"><button class="btn sm" type="button" data-shwk="' + ws + ':n">Mo bis Sa früh</button><button class="btn sm" type="button" data-shwk="' + ws + ':l">Mo bis Sa spät</button></div>' + rows + "</div>";
  };
  $("#dlg-shift").innerHTML = '<div class="dlg"><div class="dlg-head"><div><h3>Schichten eintragen</h3><p class="muted small">Der Tagesvorschlag richtet sich danach. Sonntag ist standardmäßig frei.</p></div><button class="btn icon" data-close aria-label="Schließen">' + ic("close") + "</button></div>" +
    week(t0, "Diese Woche") + week(shiftDay(t0, 7), "Nächste Woche") +
    '<p class="small muted">Wochen ohne Eintrag übernehmen die Schichten der letzten eingetragenen Woche.</p><div class="row"><button class="btn lg" type="button" data-close>Fertig</button></div></div>';
}
function planNew() { const day = dayEns(), free = day.plan ? !!day.plan.free : shiftOf(todayISO()) === "f", ids = makeDayPlan(free); if (ids) { day.plan = mkPlan(ids, free); saveToday(); renderToday(); } }
let PLANOPEN = null;
function planHTML(rest, day) {
  const open = day.plan && day.plan.done.some((d) => !d);
  if (rest <= 8 && !open) return day.items.length ? '<p class="warnt" style="color:var(--good)">Eiweißziel für heute erreicht.</p>' : "";
  const pl = planEnsure(); if (!pl) return "";
  const lab = pl.free ? PLAN_LABELS.free : pl.late ? PLAN_LABELS.late : PLAN_LABELS.work, recs = pl.ids.map((id) => byId(id));
  const tp = recs.reduce((a, r) => a + r.protein, 0), tk = recs.reduce((a, r) => a + r.kcal, 0), tc = recs.reduce((a, r) => a + r.cost, 0);
  const rows = recs.map((r, i) => '<li class="pslot' + (pl.done[i] ? " done" : "") + '"><div class="pl-l"><span class="pl-when">' + lab[i] + '</span><button class="pl-title" type="button" data-recipe="' + r.id + '">' + r.title + '</button><span class="muted small">' + r.protein + " g Eiweiß, " + r.kcal + " kcal, " + r.time + " Min, ca. " + eur(r.cost) + '</span></div><div class="pl-b">' +
    (pl.done[i] ? '<span class="pl-ok">Eingetragen</span>' : '<button class="btn sm" type="button" data-plan="' + i + '">Eintragen</button><button class="btn icon sm" type="button" data-planre="' + i + '" aria-label="Anderes Gericht für ' + lab[i] + '" title="Anderes Gericht">' + ic("repeat") + "</button>") + "</div></li>").join("");
  const po = PLANOPEN == null ? !isSheet() : PLANOPEN;
  return '<details class="plancol" id="plancol"' + (po ? " open" : "") + '><summary><span>Vorschlag für heute</span><span class="muted small">ca. ' + tp + " g Eiweiß, " + tk.toLocaleString("de-DE") + " kcal</span></summary><div class=\"plan\"><ul class=\"planlist\">" + rows + "</ul>" +
    '<div class="row plan-act">' + (open ? '<button class="btn primary" type="button" data-planall="all">Alles eintragen</button>' : "") + '<button class="btn" type="button" data-planall="new">Neu vorschlagen</button></div>' +
    '<label class="check"><input type="checkbox" id="plan-small"' + (GOALS.pause !== "meal" ? " checked" : "") + (pl.free ? " disabled" : "") + '> Pause: nur eine Kleinigkeit zum Mitnehmen</label>' +
    '<div class="row shiftrow"><span class="small muted">Schicht heute</span><div class="seg">' + ["n", "l", "f"].map((v) => '<button class="segb" type="button" data-shift="' + v + '" aria-pressed="' + (shiftOf(todayISO()) === v) + '">' + SH_NAME[v] + "</button>").join("") + '</div><button class="btn sm" type="button" data-shiftedit="1">Woche eintragen</button></div></div></details>';
}
function logEat(r, portions) {
  const n = portions || 1;
  dayEns().items.push({ id: r.id, n: n, t: r.title + (n > 1 ? " ×" + n : ""), k: Math.round(r.kcal * n), p: Math.round(r.protein * n), c: Math.round(r.cost * n * 100) / 100 });
  saveToday(); renderToday();
}

/* ======================= Wochen-Vorkochplan ======================= */
const PREPDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa"];
const prepSave = () => store.set("fc_prep", PREP);
const prepWeekISO = () => { const wd = (new Date().getDay() + 6) % 7, ws = weekStartISO(todayISO()); return wd >= 5 ? shiftDay(ws, 7) : ws; };
function prepKeep(r) {
  const t = r.title.toLowerCase(), rice = r.ing.some((i) => i[4] === "reis");
  if (/salat/.test(t)) return { fridge: 3, freeze: false, note: "Soße getrennt halten und erst vor dem Essen mischen." };
  if (/hartgekocht/.test(t)) return { fridge: 5, freeze: false, note: "Mit Schale in einer Box im Kühlschrank, pellen erst beim Essen." };
  if (/overnight/.test(t)) return { fridge: 3, freeze: false, note: "Im Glas oder in der Box mit Deckel. Für die späteren Tage setzt du frisch an, das dauert 5 Minuten." };
  if (/knusprige ofen-kichererbsen/.test(t)) return { fridge: 3, freeze: false, note: "Lose abgedeckt lagern, sonst werden sie weich." };
  if (/muffin|riegel|kekse/.test(t)) return { fridge: 3, freeze: true, note: "Erst ganz auskühlen lassen, dann in eine Dose. Zum Einfrieren einzeln einpacken." };
  return { fridge: 3, freeze: true, note: rice ? "Reis schnell abkühlen lassen (innerhalb etwa einer Stunde in den Kühlschrank) und später nur einmal richtig heiß machen." : "Flach in Boxen füllen, dann kühlt es schneller aus." };
}
function prepPool(kind) {
  const ok = (r) => !isExc(r) && !(RAD.noSpinat && hasSpin(r));
  if (kind === "main") return RECIPES.filter((r) => ok(r) && r.meal === "Mittag/Abend" && r.tags.includes("Meal-Prep") && !/salat/i.test(r.title) && r.time <= 45);
  if (kind === "b") return RECIPES.filter((r) => ok(r) && r.meal === "Frühstück" && r.tags.includes("Meal-Prep"));
  return RECIPES.filter((r) => ok(r) && r.meal === "Snack" && r.tags.includes("Meal-Prep"));
}
/* Reste sparsam einplanen: Gewicht und Haltbarkeit offener Packungen */
const RESTW = { quark: 1, skyr: 1, jog35: 1, moz: 1, schink: 1, paufs: 1, ruc: 1, eisb: 1, haehn: 0.5, pute: 0.5, schnitzel: 0.5, ghack: 0.5, rhack: 0.5, phack: 0.5, milch: 0.5, stueck: 0.7, kiche: 0.7, bohne: 0.7, burrata: 1, sahne: 0.5, brok: 1, kart: 1 };
const RESTD = { quark: [4, 1], skyr: [4, 1], jog35: [4, 0], moz: [4, 0], schink: [3, 0], paufs: [3, 0], ruc: [3, 0], eisb: [4, 0], haehn: [2, 1], pute: [2, 1], schnitzel: [2, 1], ghack: [1, 1], rhack: [1, 1], phack: [1, 1], milch: [5, 0], stueck: [3, 0], kiche: [3, 0], bohne: [3, 0], burrata: [2, 0], sahne: [3, 0], brok: [4, 0], kart: [3, 0] };
function restLines(calc) {
  return calc.lines.filter((l) => RESTW[l.k] && !l.staple && l.left != null && !PRICE[l.k].loose && l.left >= 0.2 * PRICE[l.k].pack)
    .map((l) => Object.assign({}, l, { val: l.left / PRICE[l.k].pack * PRICE[l.k].price }));
}
const restWaste = (calc) => restLines(calc).reduce((a, l) => a + l.val * RESTW[l.k], 0);
/* Reste über mehrere Tage im Wochenplan: Eine angebrochene Packung hält nur kurz (RESTD). Der Plan sucht für den Rest ein späteres Gericht innerhalb der Haltbarkeit. */
const slotAmt = (r, k) => r.ing.reduce((a, i) => a + (i[4] === k && i[0] != null ? i[0] * PRICE[k].per : 0), 0) * RAD.people;
function restChains(plan) {
  const chains = [], open = {};
  plan.days.forEach((d, di) => d.slots.forEach((s, si) => {
    const r = byId(s.id); if (!r) return;
    const seen = {};
    r.ing.forEach((i) => {
      const k = i[4];
      if (!k || seen[k] || i[0] == null || !RESTD[k] || !PRICE[k] || PRICE[k].loose || PRICE[k].staple) return;
      seen[k] = 1;
      const a = slotAmt(r, k), p = PRICE[k], c = open[k];
      let more = a;
      if (c && di - c.day <= RESTD[k][0] && c.left > 1e-6) { const take = Math.min(a, c.left); c.left -= take; c.uses.push({ d: di, s: si, amt: take, from: true }); more = a - take; }
      if (more > 1e-6) {
        const np = Math.ceil(more / p.pack - 1e-9), nc = { k, day: di, slot: si, pack: p.pack, total: np * p.pack, left: np * p.pack - more, uses: [{ d: di, s: si, amt: more, from: false }] };
        chains.push(nc); open[k] = nc;
      }
    });
  }));
  return chains;
}
const chainVal = (c) => (c.left >= 0.2 * c.pack ? c.left / c.pack * PRICE[c.k].price * (RESTW[c.k] || 0) : 0);
const planWaste = (plan) => restChains(plan).reduce((a, c) => a + chainVal(c), 0);
function radReste(plan) {
  if (RAD.mode !== "week" || RAD.reste === false) return;
  const pools = {}, poolOf = (sl) => { const key = sl.k + "|" + (sl.work ? 1 : 0); return pools[key] || (pools[key] = new Set(radPool(sl.k, sl.work).map((r) => r.id))); };
  const dsc = (day) => dayScore(day.slots.map((y) => byId(y.id)));
  let waste = planWaste(plan);
  for (let round = 0; round < 8 && waste > 0.05; round++) {
    const inPlan = new Set(); plan.days.forEach((d) => d.slots.forEach((y) => inPlan.add(y.id)));
    const cs = restChains(plan).filter((c) => chainVal(c) > 0.05).sort((a, b) => chainVal(b) - chainVal(a)).slice(0, 4);
    let step = null;
    for (const c of cs) {
      const found = [];
      plan.days.forEach((d, di) => {
        if (di < c.day || di - c.day > RESTD[c.k][0]) return;
        const old = dsc(d);
        d.slots.forEach((sl, si) => {
          if (sl.locked || (di === c.day && si <= c.slot)) return;
          const keep = sl.id, pool = poolOf(sl);
          recipesWith(c.k).forEach((r) => {
            if (!pool.has(r.id) || inPlan.has(r.id)) return;
            const amt = slotAmt(r, c.k);
            if (amt > c.left + 1e-6 || amt < 0.25 * c.left) return;
            sl.id = r.id;
            const w = planWaste(plan), ds = dsc(d);
            sl.id = keep;
            if (ds <= old + 1e-9 && w < waste - 0.05) found.push({ d: di, s: si, id: r.id, w, ds });
          });
        });
      });
      if (found.length) {
        found.sort((a, b) => a.w - b.w || a.ds - b.ds);
        const top = found.filter((f) => f.w <= found[0].w + 0.05);
        step = pickRnd(top); break;
      }
    }
    if (!step) break;
    plan.days[step.d].slots[step.s].id = step.id; waste = step.w;
  }
}
function restNotes(plan) {
  const out = {};
  if (!plan || RAD.mode !== "week" || RAD.reste === false) return out;
  const add = (d, s, t) => { (out[d + ":" + s] = out[d + ":" + s] || []).push(t); };
  const g = (k, x) => Math.max(10, Math.round(x / 10) * 10) + " " + PRICE[k].u;
  restChains(plan).forEach((c) => {
    const n = PRICE[c.k].n, f = c.uses[0], later = c.uses.slice(1);
    if ((c.total - f.amt) / c.pack * PRICE[c.k].price < 0.5) return;   /* Kleinkram ohne Hinweis */
    if (later.length) {
      const same = later.every((u) => u.d === f.d), days = later.map((u) => DAYN[u.d]).filter((x, i, a) => a.indexOf(x) === i);
      const when = same ? "noch am selben Tag" : "am " + (days.length > 1 ? days.slice(0, -1).join(", ") + " und " + days[days.length - 1] : days[0]);
      add(f.d, f.s, "Rest: " + n + " " + g(c.k, f.amt) + " von " + g(c.k, c.total) + ". Den Rest brauchst du " + when + ".");
      later.forEach((u) => add(u.d, u.s, "Rest: " + n + " " + g(c.k, u.amt) + " " + (u.d === f.d ? "vom " + plan.days[f.d].slots[f.s].label : "von " + DAYN[f.d]) + " wird verbraucht."));
    } else if (c.left >= 0.2 * c.pack) {
      const sh = RESTD[c.k] || [3, 0];
      add(f.d, f.s, "Rest: " + n + " " + g(c.k, f.amt) + " von " + g(c.k, c.total) + ". Übrig ca. " + g(c.k, c.left) + ", hält bis " + DAYN[(c.day + sh[0]) % 7] + (sh[1] ? ", sonst einfrieren" : "") + ".");
    }
  });
  return out;
}
function prepCalcWith(mains, b, s) {
  const keep = { main: PREP.main, b: PREP.b, s: PREP.s };
  PREP.main = mains; PREP.b = b || ""; PREP.s = s || "";
  try { return prepCalc().calc; } finally { PREP.main = keep.main; PREP.b = keep.b; PREP.s = keep.s; }
}
const wdShort = (iso) => WD[new Date(iso + "T12:00:00").getDay()].slice(0, 2);
function prepRestHTML(c) {
  const rl = restLines(c.calc).sort((a, b) => b.val - a.val), tot = rl.reduce((a, l) => a + l.val, 0), cook = shiftDay(PREP.week, -1);
  if (!rl.length) return '<div class="card" data-nofold><h3>Reste</h3><p>Der Plan passt gut zu den Packungsgrößen. Es bleibt kaum etwas übrig, das du verbrauchen musst.</p></div>';
  const li = rl.map((l) => {
    const p = PRICE[l.k], d = RESTD[l.k] || [3, 0];
    let amt = "";
    if (p.u === "g" || p.u === "ml") amt = "ca. " + Math.max(10, Math.round(l.left / 10) * 10) + " " + p.u;
    else { const n = Math.floor(l.left / p.per); amt = n >= 1 ? n + " " + (n > 1 && p.pl ? p.pl : p.n) : "ein Rest"; }
    const ideas = restIdeas(l.k, l.left, c.calc.used);
    return "<li><b>" + l.name + ":</b> Rest " + amt + " (ca. " + eur(l.val) + "). Offen hält es etwa bis " + wdShort(shiftDay(cook, d[0])) + (d[1] ? ", sonst einfrieren" : "") + "." +
      (ideas.length ? '<div class="row restideas"><span class="small muted">Dazu passt:</span>' + ideas.map((r) => '<button class="btn sm" type="button" data-recipe="' + r.id + '">' + r.title + "</button>").join("") + "</div>" : "") + "</li>";
  }).join("");
  const worth = restWaste(c.calc) >= 0.8;
  return '<div class="card" data-nofold><h3>Reste</h3><p class="kicker">Was nach dem Kochen aus den Packungen übrig bleibt. Warenwert zusammen etwa ' + eur(tot) + ". Vieles davon lässt sich einfrieren.</p><ul class=\"restlist\">" + li + "</ul>" +
    (worth ? '<div class="row"><button class="btn" type="button" data-prepgen="all">' + ic("repeat") + "<span>Plan mit weniger Resten würfeln</span></button></div>" : "") +
    '<p class="small muted">' + (PREP.eco !== false ? "Beim Würfeln achtet der Plan auf passende Packungsgrößen. Das ist nur ein Anstoß, Geschmack und Eiweiß gehen vor." : "Reste sparsam einplanen ist aus.") + "</p></div>";
}
function prepPick(kind, avoid, ctx) {
  let pool = prepPool(kind).filter((r) => !avoid.includes(r.id));
  if (kind === "main") { const kinds = avoid.map(byId).filter(Boolean).map(mainKind), alt = pool.filter((r) => !kinds.includes(mainKind(r))); if (alt.length) pool = alt; }
  if (!pool.length) pool = prepPool(kind);
  if (!pool.length) return "";
  const eco = PREP.eco !== false && ctx && (kind !== "main" || ctx.mains.length + 1 >= PREP.n) && (kind !== "b" || PREP.brk) && (kind !== "s" || PREP.snk);
  /* Erst grob bewerten (Eiweiß, Preis, Zeit, Lieblinge, Zufall), die aufwendige Reste-Rechnung nur für die besten 40. So bleibt das Würfeln auch bei vielen Rezepten schnell. */
  const base = pool.map((r) => ({ r, s: -(FAV.includes(r.id) ? 3 : 0) - r.protein / 12 + r.cost * 0.8 + r.time / 45 + Math.random() * 1.6 })).sort((a, b) => a.s - b.s);
  if (!eco) return base[0].r.id;
  return base.slice(0, 40).map((o) => {
    const w = restWaste(prepCalcWith(kind === "main" ? ctx.mains.concat(o.r.id) : ctx.mains, kind === "b" ? o.r.id : ctx.b, kind === "s" ? o.r.id : ctx.s));
    return { r: o.r, s: o.s + w * 1.5 };
  }).sort((a, b) => a.s - b.s)[0].r.id;
}
function prepGen(which) {
  if (which === "all" || !PREP.main.length) { PREP.main = []; PREP.b = ""; PREP.s = ""; PREP.done = {}; }
  if (/^m\d$/.test(which)) { const i = parseInt(which[1], 10), others = PREP.main.filter((_, k) => k !== i); PREP.main[i] = prepPick("main", others.concat(PREP.main[i] || []), { mains: others, b: PREP.b, s: PREP.s }); PREP.done = {}; }
  PREP.main = PREP.main.slice(0, PREP.n);
  while (PREP.main.length < PREP.n) PREP.main.push(prepPick("main", PREP.main, { mains: PREP.main.slice(), b: PREP.b, s: PREP.s }));
  PREP.main = PREP.main.filter(Boolean);
  if (which === "b") { PREP.b = prepPick("b", [PREP.b], { mains: PREP.main.slice(), b: "", s: PREP.s }); PREP.done = {}; }
  if (which === "s") { PREP.s = prepPick("s", [PREP.s], { mains: PREP.main.slice(), b: PREP.b, s: "" }); PREP.done = {}; }
  if (!PREP.b) PREP.b = prepPick("b", [], { mains: PREP.main.slice(), b: "", s: PREP.s });
  if (!PREP.s) PREP.s = prepPick("s", [], { mains: PREP.main.slice(), b: PREP.b, s: "" });
  PREP.week = PREP.week || prepWeekISO(); prepSave();
}
function prepSelect(iso) {
  if (PREP.week) PREP.plans[PREP.week] = { main: PREP.main.slice(), b: PREP.b, s: PREP.s, done: Object.assign({}, PREP.done) };
  const pl = PREP.plans[iso];
  PREP.week = iso;
  if (pl && pl.main && pl.main.length) { PREP.main = pl.main.slice(); PREP.b = pl.b || ""; PREP.s = pl.s || ""; PREP.done = Object.assign({}, pl.done); prepSave(); }
  else { PREP.main = []; PREP.b = ""; PREP.s = ""; PREP.done = {}; prepGen("all"); }
}
function prepWith(iso, fn) {
  if (PREP.week === iso) return fn();
  const pl = PREP.plans[iso]; if (!pl || !pl.main || !pl.main.length) return null;
  const keep = { main: PREP.main, b: PREP.b, s: PREP.s, done: PREP.done, week: PREP.week };
  PREP.main = pl.main; PREP.b = pl.b || ""; PREP.s = pl.s || ""; PREP.done = pl.done || {}; PREP.week = iso;
  try { return fn(); } finally { Object.assign(PREP, keep); }
}
function prepEnsure() {
  if (!PREP.week || PREP.week < weekStartISO(todayISO()) || PREP.autoDay !== todayISO()) { prepSelect(prepWeekISO()); PREP.autoDay = todayISO(); prepSave(); }
  else if (!PREP.main.length || PREP.main.some((id) => !byId(id) || isExc(byId(id)))) prepGen("all");
  else if (PREP.main.length !== PREP.n) prepGen();
}
function prepCalc() {
  const P = PREP.people, N = PREP.days, mains = PREP.main.map(byId).filter(Boolean), items = [];
  const dayMain = PREPDAYS.slice(0, N).map((d, i) => (mains.length ? mains[i % mains.length] : null));
  mains.forEach((r) => {
    const days = dayMain.map((m, i) => (m === r ? i : -1)).filter((i) => i >= 0), kp = prepKeep(r);
    items.push({ r, kind: "Hauptgericht", keep: kp, days, fridge: days.filter((i) => i < kp.fridge), later: days.filter((i) => i >= kp.fridge), n: (kp.freeze ? days.length : days.filter((i) => i < kp.fridge).length) * P });
  });
  [["b", "Frühstück", PREP.brk], ["s", "Snack", PREP.snk]].forEach(([k, label, on]) => {
    const r = on && byId(PREP[k]); if (!r) return;
    const all = Array.from({ length: Math.min(N, 5) }, (_, i) => i), kp = prepKeep(r), fridge = all.filter((i) => i < kp.fridge), later = all.filter((i) => i >= kp.fridge);
    items.push({ r, kind: label, keep: kp, days: all, fridge, later, n: (kp.freeze ? all.length : fridge.length) * P, key: k });
  });
  const entries = items.map((it) => ({ id: it.r.id, n: it.n })), calc = shopCalc(entries);
  const longest = Math.max(0, ...items.map((it) => it.r.time)), sum = items.reduce((a, it) => a + it.r.time, 0);
  return { items, dayMain, entries, calc, mins: Math.round((longest + (sum - longest) * 0.45 + 20) / 5) * 5 };
}
function prepSteps(c) {
  const mains = c.items.filter((it) => it.kind === "Hauptgericht").sort((a, b) => b.r.time - a.r.time);
  const ovenOf = (it) => it.r.steps.some((s) => /ofen/i.test(s)), nm = (arr) => arr.map((it) => "„" + it.r.title + "“").join(" und ");
  const oven = c.items.filter(ovenOf), stove = mains.filter((it) => !ovenOf(it)), cold = c.items.filter((it) => it.kind !== "Hauptgericht" && !ovenOf(it));
  const out = [];
  out.push(["setup", "Vorbereiten", "Einkauf auspacken, Boxen und Marker bereitlegen."]);
  if (oven.length) out.push(["oven", "Zuerst in den Ofen: " + nm(oven), "Ofen vorheizen, nebenher Zutaten vorbereiten."]);
  if (stove.length) out.push(["stove", "Auf dem Herd: " + nm(stove), "Mit dem Längsten anfangen, nebenher fürs nächste schneiden."]);
  if (cold.length) out.push(["cold", "Nebenbei ansetzen: " + nm(cold), "Braucht kaum Aufmerksamkeit, mach es nebenher."]);
  const fr = c.items.filter((it) => it.keep.freeze && it.later.length), n = (it) => it.later.length * PREP.people;
  out.push(["pack", "Abkühlen und einpacken", "Flach in Boxen füllen, höchstens 1 Stunde auskühlen, beschriften." + (fr.length ? " Einfrieren: " + fr.map((it) => n(it) + " × " + it.r.title).join(", ") + "." : "")]);
  if (fr.length) out.push(["thaw", "Unter der Woche", "Tiefgekühltes am Vorabend in den Kühlschrank stellen."]);
  return out;
}
function prepHTML() {
  prepEnsure();
  const c = prepCalc(), P = PREP.people, wk = PREP.week;
  const seg = (field, vals) => vals.map((v) => '<button class="btn" type="button" data-prepopt="' + field + '" data-v="' + v + '" aria-pressed="' + (PREP[field] === v) + '">' + v + "</button>").join("");
  const tog = (field, lab) => '<button class="btn" type="button" data-prepopt="' + field + '" aria-pressed="' + !!PREP[field] + '">' + lab + "</button>";
  const cur = weekStartISO(todayISO()), off = Math.round((new Date(wk + "T12:00:00") - new Date(cur + "T12:00:00")) / 604800000), wkName = off === 0 ? "Diese Woche" : off === 1 ? "Nächste Woche" : "In " + off + " Wochen";
  const picker = '<div class="weekpick" role="group" aria-label="Woche wählen"><button class="btn icon" type="button" data-prepweek="-1" aria-label="Vorherige Woche"' + (off <= 0 ? " disabled" : "") + ">‹</button><div><b>" + wkName + '</b><span class="small muted">' + dateDE(wk) + " bis " + dateDE(shiftDay(wk, 6)) + '</span></div><button class="btn icon" type="button" data-prepweek="1" aria-label="Nächste Woche"' + (off >= 4 ? " disabled" : "") + ">›</button></div>";
  const tagOf = (it, d) => (d >= it.keep.fridge ? (it.keep.freeze ? "Tiefkühler" : "frisch machen") : "");
  const once = (it, lab) => { if (!it) return ""; const t = it.later.length ? " ab " + PREPDAYS[it.keep.fridge] + ": " + (it.keep.freeze ? "Tiefkühler" : "frisch machen") : ""; return '<li class="wk-all"><b>' + lab + "</b><span>" + it.r.title + (t ? ' <em class="tag">' + t.trim() + "</em>" : "") + "</span></li>"; };
  const week = once(c.items.find((it) => it.key === "b"), "Früh") + once(c.items.find((it) => it.key === "s"), "Snack") + c.dayMain.map((m, d) => { const mi = c.items.find((it) => it.r === m), t = m ? tagOf(mi, d) : ""; return "<li><b>" + PREPDAYS[d] + "</b><span>" + (m ? m.title : "") + (t ? ' <em class="tag">' + t + "</em>" : "") + "</span></li>"; }).join("");
  const items = c.items.map((it) => {
    const who = it.kind === "Hauptgericht" ? "m" + c.items.filter((x) => x.kind === "Hauptgericht").indexOf(it) : it.key, per = it.n / P;
    const freezeN = it.keep.freeze ? it.later.length * P : 0, fresh = !it.keep.freeze && it.later.length ? it.later.map((i) => PREPDAYS[i]).join(", ") : "";
    return '<article class="card prepitem" data-nofold><div class="rday-h"><div><p class="kicker">' + it.kind + "</p><h3>" + it.r.title + '</h3></div><span class="rtot">' + eur(it.r.cost * it.n) + "</span></div>" +
      '<p class="small muted">' + it.n + " Portionen · " + it.r.protein + " g Eiweiß · " + it.r.kcal + " kcal · " + it.r.time + " Min</p>" +
      '<details class="exmore"><summary>Haltbarkeit</summary><p class="small">' + it.keep.fridge + " Tage im Kühlschrank" + (it.keep.freeze ? ", bis 3 Monate im Tiefkühler" + (freezeN ? " (" + freezeN + " Portionen einfrieren)" : "") : ", nicht zum Einfrieren") + ". " + it.keep.note + (fresh ? " Für " + fresh + " frisch machen." : "") + "</p></details>" +
      '<div class="row"><button class="btn" type="button" data-recipe="' + it.r.id + '">Rezept</button><button class="btn" type="button" data-cook="' + it.r.id + '">Kochmodus</button><button class="btn" type="button" data-prepgen="' + who + '" aria-label="Anderes Gericht">' + ic("repeat") + "<span>Anderes</span></button></div></article>";
  }).join("");
  const steps = prepSteps(c).map((st) => '<li class="' + (PREP.done[st[0]] ? "done" : "") + '"><label class="sline"><input type="checkbox" data-prepchk="' + st[0] + '"' + (PREP.done[st[0]] ? " checked" : "") + '><span class="sname"><b>' + st[1] + '</b><br><span class="muted small">' + st[2] + "</span></span></label></li>").join("");
  return '<div class="card" data-nofold><h3>Vorkochplan</h3>' + picker +
    '<div class="prepopts"><div class="row"><span class="small muted">Personen</span><span class="stepper"><button class="btn icon" type="button" data-prepopt="people" data-d="-1" aria-label="Weniger Personen">−</button><b>' + P + '</b><button class="btn icon" type="button" data-prepopt="people" data-d="1" aria-label="Mehr Personen">+</button></span></div>' +
    '<div class="row pseg"><span class="small muted">Tage</span>' + seg("days", [3, 4, 5, 6]) + '</div><div class="row pseg"><span class="small muted">Gerichte</span>' + seg("n", [1, 2, 3]) + '</div><div class="row pseg">' + tog("brk", "Frühstück") + tog("snk", "Snack") + tog("eco", "Reste sparsam einplanen") + "</div></div>" +
    '<p class="prepsum"><b>ca. ' + eur(c.calc.total) + "</b> · " + eur(c.calc.total / P) + " pro Person · " + c.mins + ' Min am Sonntag</p><div class="row"><button class="btn primary" type="button" data-prepcart="1">In die Einkaufsliste</button><button class="btn" type="button" data-prepgen="all" aria-label="Neu würfeln">' + ic("repeat") + "<span>Neu würfeln</span></button></div></div>" +
    '<div class="card" data-nofold><h3>Deine Woche</h3><ul class="prepweek">' + week + "</ul></div>" + prepRestHTML(c) +
    '<div class="grid2">' + items + "</div>" +
    '<details class="card acc" id="prepsteps" data-nofold' + (new Date().getDay() === 0 ? " open" : "") + '><summary><span class="acct">Sonntag: Reihenfolge zum Kochen</span></summary><div class="accbody"><ol class="prepsteps">' + steps + "</ol></div></details>" +
    '<details class="card acc radshop" data-nofold><summary><span class="acct">Einkauf ca. ' + eur(c.calc.total) + '</span></summary><div class="accbody">' + shopListHTML(c.calc) + "</div></details>";
}
function renderPrep() { $("#panel-vorkochen").innerHTML = prepHTML(); }
function prepTodayHTML() {
  if (!PREP.main.length) { if (((new Date().getDay() + 6) % 7) !== 6) return ""; prepEnsure(); }
  const wd = (new Date().getDay() + 6) % 7;
  if (wd === 6) { prepEnsure(); const c = prepCalc(); return '<div class="card"><div class="tdhead"><div><h3>Heute ist Vorkochtag</h3><p class="muted">' + c.items.length + " Gerichte für die Woche, etwa " + c.mins + " Minuten, ca. " + eur(c.calc.total) + ' bei Lidl.</p></div><div class="row"><button class="btn primary" type="button" data-tab="vorkochen">Plan öffnen</button></div></div></div>'; }
  if (wd >= PREP.days) return "";
  return prepWith(weekStartISO(todayISO()), () => prepBoxHTML(wd)) || "";
}
function prepBoxHTML(wd) {
  const c = prepCalc(), m = c.dayMain[wd]; if (!m) return "";
  const mi = c.items.find((it) => it.r === m), b = PREP.brk ? c.items.find((it) => it.key === "b") : null, how = wd >= mi.keep.fridge && mi.keep.freeze ? "aus dem Tiefkühler, am Vorabend in den Kühlschrank stellen" : "aus dem Kühlschrank";
  return '<div class="card"><div class="tdhead"><div><h3>Heute aus der Box</h3><p>' + (b && wd < 5 ? "Frühstück: " + b.r.title + ". " : "") + "Essen: " + m.title + ' <span class="muted small">(' + how + ')</span></p></div><div class="row"><button class="btn" type="button" data-tab="vorkochen">Vorkochplan</button></div></div></div>';
}

function renderToday() {
  const now = new Date(), plan = weekPlan()[(now.getDay() + 6) % 7], pg = protGoal(), e = dsum(), day = dayGet();
  const wc = weekCountISO(weekStartISO(todayISO())), streak = weekStreak(), doneToday = sessions.includes(todayISO());
  const title = plan[2] ? (doneToday ? "Training für heute geschafft" : "Heute ist Trainingstag") : "Heute: " + plan[1];
  const rest = Math.max(0, pg - e.p);
  const sug = suggestList(3);
  const glasses = Array.from({ length: GOALS.water }, (_, i) => '<button class="gl' + (i < day.water ? " on" : "") + '" data-water="' + i + '" aria-pressed="' + (i < day.water) + '" aria-label="Glas ' + (i + 1) + '"></button>').join("");
  $("#panel-heute").innerHTML =
    backupHTML() + '<div class="card hero"><div class="tdhead"><div><h3>' + title + '</h3><p class="muted">' + (plan[2] ? "Ganzkörper, etwa " + estMinutes() + " Minuten" : "Ruhetag: Erholung gehört zum Training") + "</p></div>" +
    '<div class="row">' + (plan[2] && !doneToday && !isActive() ? '<button class="btn primary" data-act="start">Training starten</button>' : "") + '<button class="btn" data-eatopen="1">Essen eintragen</button><button class="btn" data-tab="rad">Essen wählen</button></div></div>' +
    shiftHintHTML() + trioHTML(e.p, pg, e.k, GOALS.kcal, wc, trainDays()) +
    '</div>' +
    prepTodayHTML() + reviewToday() +
    '<div class="card"><div class="rday-h"><h3>Heute gegessen</h3>' + (day.items.length ? '<span class="rtot">ca. ' + eur(e.c) + " bei Lidl</span>" : "") + "</div>" +
    (day.items.length
      ? '<ul class="eatlist">' + day.items.map((x, i) => "<li><div><b>" + esc(x.t) + '</b><span class="muted small">' + x.p + " g Eiweiß, " + x.k + ' kcal</span></div><button class="btn icon sm" data-eatdel="' + i + '" aria-label="Eintrag löschen">' + ic("close") + "</button></li>").join("") + "</ul>"
      : '<p class="muted">Noch nichts eingetragen.</p>') +
    planHTML(rest, day) + '<div class="row"><button class="btn sm" type="button" data-tab="fortschritt" data-histgo="1">Alle Tage ansehen</button></div></div>' +
    '<div class="grid2"><div class="card"><div class="rday-h"><h3>Wasser</h3><span class="rtot">' + nf(Math.round(day.water * 25) / 100) + " von " + nf(Math.round(GOALS.water * 25) / 100) + ' Litern</span></div><div class="glasses">' + glasses + '</div></div>' +
    '<div class="card"><h3>Serie</h3><div class="stats"><div class="stat"><span class="big">' + streak + '</span><span>Wochen in Folge mit mindestens 2 Einheiten</span></div><div class="stat"><span class="big">' + sessions.length + '</span><span>Einheiten insgesamt</span></div></div></div></div>';
  animRings();
}

/* ======================= Selbst berechnen (Zutaten oder Gericht) ======================= */
const CNORM = (x) => x.toLowerCase().replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss").replace(/[^a-z0-9. ]/g, " ").replace(/\s+/g, " ").trim();
const CSYN = {
  haehn: "haehnchenbrust haehnchen haenchen hahnchen huhn huehnchen chicken haehnchenfilet", pute: "putenbrust pute putenfleisch putenschnitzel putenfilet", phack: "putenhack putenhackfleisch", rhack: "rinderhack rinderhackfleisch rindergehacktes",
  ghack: "hackfleisch hack gehacktes", schink: "schinken kochschinken", paufs: "aufschnitt putenaufschnitt", ei: "ei eier eiern spiegelei ruehrei", skyr: "skyr", quark: "quark magerquark", jog35: "joghurt naturjoghurt", milch: "milch",
  moz: "mozzarella", gouda: "gouda kaese schnittkaese", parm: "parmesan|parmigiano|parmigiano reggiano|reggiano", hafer: "haferflocken hafer porridge", chia: "chia|chiasamen|chia samen|chiasaat", mandel: "mandeln mandel", brot: "brot vollkornbrot brotscheibe graubrot mischbrot", wrap: "wrap wraps tortilla",
  broetchen: "broetchen semmel vollkornbroetchen", nudel: "nudeln pasta spaghetti penne fusilli makkaroni tagliatelle vollkornnudeln", reis: "reis", honig: "honig", oel: "oel olivenoel rapsoel sonnenblumenoel",
  tmark: "tomatenmark", stueck: "stueckige tomaten|passierte tomaten|dosentomaten", tom: "tomate tomaten", gurke: "gurke gurken salatgurke", pap: "paprika", zwie: "zwiebel zwiebeln", karo: "karotte karotten moehre moehren",
  eisb: "eisbergsalat salat eisberg", spin: "spinat", ruc: "rucola", sgurke: "saure gurke|saure gurken|gewuerzgurke|gewuerzgurken", knob: "knoblauch", banane: "banane bananen", erdb: "erdbeeren erdbeere", kiche: "kichererbsen",
  bohne: "kidneybohnen bohnen", linse: "linsen", kokos: "kokosmilch", bruehe: "gemuesebruehe bruehe", zitrone: "zitronensaft zitrone", senf: "senf", kakao: "kakao", schnitzel: "schweineschnitzel schnitzel schweinefleisch", curry: "currypulver curry",
  speisequark: "speisequark", jogGr: "griechischer joghurt|griechisches joghurt|joghurt griechisch|sahnejoghurt", butter: "butter markenbutter suessrahmbutter streichbutter", haehnst: "mini steaks|ministeaks|minutensteaks|minisnitzel", lyoner: "lyoner delikatess lyoner", burrata: "burrata", sahne: "sahne schlagsahne", brok: "brokkoli broccoli", kart: "kartoffeln kartoffel"
};
const CDEF = { speisequark: 150, jogGr: 150, butter: 10, haehnst: 150, lyoner: 30, gouda: 30, moz: 60, parm: 15, schink: 40, paufs: 40, quark: 150, skyr: 150, jog35: 150, hafer: 50, mandel: 20, chia: 15, reis: 80, nudel: 100, milch: 200, eisb: 80, gurke: 100, spin: 80, ruc: 30, erdb: 150, kiche: 120, bohne: 120, linse: 60, kokos: 100, bruehe: 200, stueck: 200, burrata: 60, sahne: 50, brok: 150, kart: 200 };
/* weitere Lebensmittel: [Schlüssel (| getrennt), Name, kcal/100 g, Eiweiß/100 g, Gramm je Stück, Standardmenge in g, ca. € pro 100 g] */
const CEXTRA = [
  ["eigelb|eidotter", "Eigelb", 322, 15.9, 17, 17, 0.3], ["eiweiss|eiklar", "Eiweiß (vom Ei)", 52, 10.9, 33, 33, 0.1],
  ["kartoffel|kartoffeln", "Kartoffeln", 77, 2, 120, 200, 0.15], ["pommes|pommes frites", "Pommes (Ofen oder Fritteuse)", 200, 3, 0, 150, 0.35], ["toast|toastbrot", "Toastbrot", 265, 8, 25, 50, 0.18], ["broetchen hell|weissbrot|baguette", "Weißbrot", 265, 8.5, 0, 60, 0.2],
  ["butter", "Butter", 740, 0.7, 0, 10, 0.9], ["frischkaese", "Frischkäse", 200, 6, 0, 30, 0.45], ["sahne", "Sahne", 300, 2.4, 0, 50, 0.3], ["schmand|creme fraiche", "Schmand", 200, 3, 0, 40, 0.3], ["salami", "Salami", 430, 22, 0, 30, 1.2],
  ["leberwurst|teewurst", "Streichwurst", 300, 12, 0, 30, 0.7], ["mehl", "Mehl", 350, 10, 0, 50, 0.1], ["muesli", "Müsli", 370, 10, 0, 60, 0.4], ["cornflakes", "Cornflakes", 380, 7, 0, 40, 0.35], ["zucker", "Zucker", 400, 0, 5, 10, 0.12],
  ["apfel|aepfel", "Apfel", 52, 0.3, 180, 180, 0.3], ["orange|orangen", "Orange", 47, 0.9, 200, 200, 0.3], ["birne|birnen", "Birne", 57, 0.4, 170, 170, 0.35], ["weintrauben|trauben", "Weintrauben", 70, 0.7, 0, 100, 0.5],
  ["zucchini", "Zucchini", 17, 1.2, 0, 150, 0.2], ["champignons|pilze", "Champignons", 22, 3, 0, 100, 0.4], ["brokkoli", "Brokkoli", 34, 2.8, 0, 150, 0.35], ["mais", "Mais (Dose)", 80, 3, 0, 100, 0.25],
  ["ketchup", "Ketchup", 110, 1.2, 0, 20, 0.25], ["mayo|mayonnaise", "Mayonnaise", 700, 1, 0, 15, 0.3], ["tomatensauce|tomatensosse", "Tomatensoße (Glas)", 50, 1.6, 0, 150, 0.2],
  ["schokolade", "Schokolade", 540, 6.5, 0, 25, 0.6], ["nutella|nussnougatcreme", "Nuss-Nougat-Creme", 540, 6, 0, 20, 0.5], ["chips", "Chips", 530, 6, 0, 50, 0.9], ["gummibaerchen|gummibaeren", "Gummibärchen", 340, 7, 0, 30, 0.6],
  ["cola|limo|limonade", "Cola oder Limonade", 42, 0, 0, 330, 0.1], ["saft|apfelsaft|orangensaft", "Saft", 45, 0.5, 0, 200, 0.12], ["energy|energydrink", "Energy-Drink", 45, 0, 0, 250, 0.2], ["bier", "Bier", 43, 0.5, 0, 500, 0.2],
  ["weizennudeln|helle nudeln|weisse nudeln", "Weizennudeln (Rohgewicht)", 355, 12.5, 0, 100, 0.2], ["proteinpulver|whey|eiweisspulver", "Proteinpulver", 380, 75, 30, 30, 2.5], ["tiefkuehlpizza|pizza tk", "Tiefkühlpizza", 250, 10, 350, 350, 0.55],
  ["blumenkohl", "Blumenkohl", 25, 2, 0, 150, 0.3], ["kohlrabi", "Kohlrabi", 27, 1.7, 0, 150, 0.3], ["aubergine", "Aubergine", 25, 1, 0, 150, 0.35], ["lauch|porree", "Lauch", 30, 2.1, 0, 100, 0.3], ["sellerie", "Sellerie", 20, 1.5, 0, 50, 0.25],
  ["rotkohl|weisskohl|kohl", "Kohl", 28, 1.5, 0, 150, 0.15], ["erbsen", "Erbsen", 80, 6, 0, 100, 0.3], ["radieschen", "Radieschen", 15, 1, 0, 50, 0.4], ["avocado", "Avocado", 160, 2, 150, 100, 0.8], ["oliven", "Oliven", 150, 1, 0, 30, 0.7],
  ["kiwi", "Kiwi", 50, 1, 80, 80, 0.4], ["mango", "Mango", 60, 0.7, 300, 150, 0.5], ["ananas", "Ananas", 55, 0.5, 0, 150, 0.3], ["melone|wassermelone", "Melone", 30, 0.6, 0, 200, 0.2], ["heidelbeeren|blaubeeren", "Heidelbeeren", 45, 0.7, 0, 100, 0.9],
  ["himbeeren", "Himbeeren", 40, 1.2, 0, 100, 0.9], ["mandarine|mandarinen|clementine|clementinen", "Mandarine", 45, 0.7, 70, 70, 0.3], ["pfirsich|nektarine", "Pfirsich", 40, 0.9, 150, 150, 0.4], ["rosinen|trockenfruechte|datteln", "Trockenfrüchte", 290, 2.5, 0, 30, 0.6],
  ["bratwurst|wurst|wuerstchen|wiener|bockwurst", "Wurst", 300, 12, 0, 100, 0.8], ["frikadelle|frikadellen|bulette|buletten|fleischpflanzerl", "Frikadelle", 230, 15, 90, 90, 0.5], ["haehnchenkeule|haehnchenschenkel|keule", "Hähnchenkeule (mit Haut, ohne Knochen)", 200, 18, 0, 150, 0.6],
  ["steak|rindersteak|rindfleisch", "Rindfleisch", 140, 21, 0, 150, 1.3], ["schweinefilet", "Schweinefilet", 110, 22, 0, 150, 0.9], ["bacon|speck", "Bacon", 400, 14, 0, 30, 1.4], ["milchreis", "Milchreis (fertig)", 120, 3.5, 0, 200, 0.3],
  ["pudding", "Pudding", 110, 3, 0, 125, 0.3], ["fruchtjoghurt", "Fruchtjoghurt", 100, 3.5, 0, 150, 0.2], ["buttermilch|kefir", "Buttermilch", 38, 3.5, 0, 250, 0.15], ["feta|schafskaese", "Feta", 260, 15, 0, 40, 0.8],
  ["camembert|brie", "Camembert", 290, 20, 0, 40, 0.8], ["emmentaler|bergkaese", "Emmentaler", 380, 28, 0, 30, 1.0], ["hafermilch|haferdrink|sojadrink|sojamilch|mandelmilch", "Pflanzendrink", 45, 1, 0, 250, 0.15],
  ["gnocchi", "Gnocchi", 150, 4, 0, 200, 0.35], ["knoedel|kloesse", "Knödel", 130, 3, 0, 200, 0.3], ["tortellini|ravioli", "Tortellini (gefüllt)", 280, 11, 0, 125, 0.7], ["bulgur", "Bulgur (Rohgewicht)", 350, 12, 0, 70, 0.3],
  ["quinoa", "Quinoa (Rohgewicht)", 370, 14, 0, 70, 0.6], ["kartoffelpueree|kartoffelbrei", "Kartoffelpüree", 90, 2, 0, 200, 0.2], ["bratkartoffeln", "Bratkartoffeln", 150, 3, 0, 200, 0.3], ["reiswaffel|reiswaffeln", "Reiswaffel", 380, 8, 8, 16, 0.5],
  ["knaeckebrot", "Knäckebrot", 340, 10, 10, 20, 0.5], ["brezel|laugenbrezel", "Laugenbrezel", 270, 8, 90, 90, 0.5], ["pfannkuchen|eierkuchen|crepes", "Pfannkuchen", 200, 6, 80, 160, 0.3], ["nuesse|nuss", "Nüsse", 620, 20, 0, 30, 1.2],
  ["sonnenblumenkerne|kuerbiskerne|leinsamen", "Kerne und Samen", 570, 22, 0, 15, 0.7], ["marmelade|konfituere|gelee", "Marmelade", 250, 0.4, 0, 20, 0.3], ["kekse|plaetzchen|keks", "Kekse", 470, 6, 10, 30, 0.6], ["kuchen", "Kuchen", 350, 5, 0, 100, 0.5],
  ["popcorn", "Popcorn", 400, 10, 0, 30, 0.5], ["tomatensuppe|gemuesesuppe|suppe", "Suppe (Dose oder Fertig)", 45, 1.5, 0, 400, 0.15], ["linsensuppe|eintopf", "Eintopf (Dose)", 75, 4, 0, 400, 0.25], ["pesto", "Pesto", 450, 5, 0, 20, 1.3],
  ["hummus", "Hummus", 230, 7, 0, 40, 0.7], ["currysauce|bratensauce|sosse", "Soße", 80, 1.5, 0, 100, 0.2], ["essig", "Essig", 5, 0, 0, 10, 0.1], ["kaffee", "Kaffee schwarz", 2, 0.2, 0, 250, 0.05], ["tee", "Tee ungesüßt", 1, 0, 0, 250, 0.03],
  ["ingwer", "Ingwer (frisch)", 80, 1.8, 0, 10, 0.8], ["koriander", "Koriander (frisch)", 23, 2.1, 0, 10, 2], ["petersilie", "Petersilie (frisch)", 36, 3, 0, 10, 1.5], ["schnittlauch", "Schnittlauch", 30, 3.3, 0, 10, 2], ["dill", "Dill (frisch)", 43, 3.5, 0, 10, 2],
  ["minze|pfefferminze", "Minze (frisch)", 44, 3.3, 0, 10, 2], ["basilikum", "Basilikum (frisch)", 23, 3.2, 0, 10, 2], ["chilischote|peperoni|jalapeno|peperoncini", "Chilischote", 40, 1.9, 15, 15, 1.5], ["fruehlingszwiebel|fruehlingszwiebeln|lauchzwiebel|lauchzwiebeln", "Frühlingszwiebel", 30, 1.8, 20, 40, 0.5],
  ["spargel", "Spargel", 20, 2, 0, 200, 0.9], ["mangold|pak choi|pakchoi|chinakohl", "Blattgemüse", 20, 1.8, 0, 150, 0.4], ["rote bete|rotebete", "Rote Bete", 43, 1.6, 0, 100, 0.3], ["kuerbis|hokkaido", "Kürbis", 26, 1, 0, 200, 0.3],
  ["suesskartoffel|suesskartoffeln|batate", "Süßkartoffel", 86, 1.6, 200, 200, 0.3], ["gruene bohnen|prinzessbohnen|buschbohnen", "Grüne Bohnen", 31, 1.8, 0, 150, 0.4], ["rosenkohl", "Rosenkohl", 43, 3.4, 0, 150, 0.45], ["fenchel", "Fenchel", 31, 1.2, 0, 150, 0.35],
  ["maiskolben", "Maiskolben", 90, 3.3, 200, 200, 0.4], ["weisse bohnen|cannellinibohnen|schwarze bohnen", "Weiße oder schwarze Bohnen (Dose)", 100, 7, 0, 120, 0.3], ["edamame", "Edamame", 120, 12, 0, 80, 0.8],
  ["pflaume|pflaumen|zwetschge|zwetschgen", "Pflaume", 46, 0.7, 60, 60, 0.4], ["kirschen", "Kirschen", 63, 1.1, 0, 100, 0.8], ["aprikose|aprikosen", "Aprikose", 48, 1.4, 45, 90, 0.5], ["grapefruit", "Grapefruit", 42, 0.8, 250, 125, 0.3],
  ["zitrone|limette|limettensaft", "Zitrone oder Limette", 29, 1.1, 80, 20, 0.3], ["feige|feigen", "Feige", 74, 0.8, 50, 50, 0.9], ["granatapfel", "Granatapfel", 83, 1.7, 0, 100, 0.8], ["trauben", "Weintrauben", 70, 0.7, 0, 100, 0.5],
  ["haehnchenschenkel|haehnchenunterschenkel", "Hähnchenschenkel (mit Haut, ohne Knochen)", 200, 18, 0, 150, 0.6], ["schweinenacken|nackensteak|kotelett|schweinekotelett", "Schweinenacken oder Kotelett", 220, 19, 0, 150, 0.9], ["schweinebauch", "Schweinebauch", 330, 15, 0, 100, 0.8],
  ["kassler", "Kassler", 170, 20, 0, 120, 1.0], ["bierschinken|lyoner|mortadella|fleischwurst|jagdwurst", "Aufschnitt (Wurst)", 260, 12, 0, 30, 1.0], ["nuggets|chicken nuggets", "Chicken Nuggets", 250, 14, 20, 120, 0.8],
  ["kroketten", "Kroketten", 160, 3, 25, 150, 0.35], ["maultaschen", "Maultaschen", 190, 8, 60, 200, 0.5], ["instantnudeln|ramen|nudelsuppe", "Instantnudeln (trocken)", 450, 9, 0, 85, 0.5],
  ["griechischer joghurt|joghurt griechisch|sahnejoghurt", "Griechischer Joghurt (10 %)", 123, 4.2, 0, 150, 0.35], ["reibekaese|pizzakaese|streukaese|geriebener kaese", "Reibekäse", 300, 22, 0, 30, 0.9], ["halloumi|grillkaese", "Halloumi", 320, 21, 0, 60, 1.3],
  ["ricotta", "Ricotta", 170, 9, 0, 50, 0.7], ["mascarpone", "Mascarpone", 400, 4.5, 0, 30, 0.8], ["gorgonzola|blauschimmelkaese", "Gorgonzola", 350, 19, 0, 30, 1.2], ["cheddar", "Cheddar", 400, 25, 0, 30, 1.0], ["schmelzkaese|scheibenkaese|schmelzkaeseecken", "Schmelzkäse", 250, 12, 20, 40, 0.6],
  ["vollmilch|trinkmilch", "Vollmilch (3,5 %)", 65, 3.4, 0, 200, 0.12], ["kaffeesahne|kondensmilch|kaffeemilch", "Kondensmilch (10 %)", 130, 6, 0, 10, 0.4], ["saure sahne", "Saure Sahne", 170, 3, 0, 30, 0.3], ["paneer", "Paneer", 300, 18, 0, 100, 1.2],
  ["pita|pitabrot|fladenbrot", "Pita oder Fladenbrot", 275, 9, 60, 60, 0.35], ["naan|naanbrot", "Naan", 290, 9, 90, 90, 0.5], ["bagel", "Bagel", 250, 10, 100, 100, 0.5], ["burgerbroetchen|burger bun", "Burgerbrötchen", 270, 9, 70, 70, 0.3],
  ["dinkelbrot|roggenbrot|toastbrot vollkorn", "Brot (Dinkel oder Roggen)", 230, 8, 50, 50, 0.25], ["paniermehl|semmelbroesel", "Paniermehl", 350, 11, 0, 20, 0.2], ["gries|griess|maisgries|polenta", "Grieß oder Polenta (Rohgewicht)", 350, 9, 0, 70, 0.2], ["hirse", "Hirse (Rohgewicht)", 360, 11, 0, 70, 0.4],
  ["speisestaerke|staerke|mondamin", "Speisestärke", 340, 0.3, 0, 10, 0.3], ["basmati|basmatireis|jasminreis|vollkornreis|naturreis|langkornreis|parboiled", "Reis (Rohgewicht)", 350, 7, 0, 80, 0.25], ["bandnudeln|lasagneplatten|spiralnudeln|hoernchen|hornnudeln", "Nudeln (Weizen, Rohgewicht)", 355, 12.5, 0, 100, 0.2],
  ["worcester|worcestersauce", "Worcestersauce", 78, 0, 0, 10, 0.3], ["sriracha|chilisauce|sambal|sambal oelek", "Chilisauce", 90, 2, 0, 15, 0.5], ["tabasco", "Tabasco", 12, 1, 0, 3, 1], ["harissa", "Harissa", 100, 3, 0, 15, 0.8],
  ["tahini|sesammus", "Tahini", 595, 17, 0, 15, 1.2], ["bbq|barbecue|bbqsauce|grillsauce", "Barbecuesoße", 150, 1, 0, 20, 0.3], ["balsamico|balsamicoessig", "Balsamico", 88, 0.5, 0, 10, 0.5], ["kokosoel|kokosfett", "Kokosöl", 862, 0, 0, 10, 1.0],
  ["sesamoel", "Sesamöl", 884, 0, 0, 10, 1.5], ["butterschmalz|ghee|schmalz", "Butterschmalz", 900, 0, 0, 10, 1.5], ["margarine", "Margarine", 720, 0.2, 0, 10, 0.5], ["hefeflocken", "Hefeflocken", 350, 45, 0, 10, 2.5],
  ["agavendicksaft|agavensirup|ahornsirup|reissirup|sirup", "Sirup", 300, 0, 0, 20, 0.5], ["kokosraspel|kokosflocken", "Kokosraspeln", 650, 6, 0, 15, 1.0], ["sesam", "Sesam", 573, 18, 0, 10, 1.0], ["mohn", "Mohn", 525, 18, 0, 10, 1.0],
  ["wein|rotwein|weisswein", "Wein", 85, 0.1, 0, 150, 0.4], ["sekt|prosecco", "Sekt", 80, 0.2, 0, 125, 0.5], ["eistee", "Eistee", 20, 0, 0, 330, 0.1], ["cola zero|zero|light getraenk", "Zuckerfreies Getränk", 1, 0, 0, 330, 0.1], ["mineralwasser|wasser", "Wasser", 0, 0, 0, 250, 0.02],
  ["smoothie", "Smoothie", 55, 0.7, 0, 250, 0.4], ["schokoriegel|snickers|twix|mars|kitkat|bounty", "Schokoriegel", 490, 7, 50, 50, 0.7], ["donut|berliner|krapfen", "Donut oder Berliner", 400, 5, 70, 70, 0.6], ["lebkuchen", "Lebkuchen", 380, 5, 40, 40, 0.8],
  ["waffel|waffeln", "Waffel", 330, 6, 60, 60, 0.4], ["marshmallows|mashmallows", "Marshmallows", 330, 3, 0, 30, 0.6], ["tzatziki", "Tzatziki", 120, 4, 0, 40, 0.5], ["guacamole", "Guacamole", 150, 2, 0, 40, 0.8], ["falafel", "Falafel", 330, 13, 25, 100, 0.8],
  ["rosinen", "Rosinen", 300, 3, 0, 30, 0.5], ["pinienkerne", "Pinienkerne", 670, 14, 0, 20, 5.0], ["kuerbiskerne", "Kürbiskerne", 560, 30, 0, 20, 1.2],
  ["garam masala|garam|masala", "Garam Masala", 325, 11, 2, 2, 6, "TL"],
  ["paprikapulver|paprika edelsuess|paprika rosenscharf|geraeuchertes paprikapulver|paprika geraeuchert", "Paprikapulver", 282, 14, 2.5, 2.5, 6, "TL"],
  ["kurkuma|gelbwurz", "Kurkuma", 312, 10, 3, 3, 6, "TL"],
  ["kreuzkuemmel|cumin|kumin|kreuzkuemmelpulver", "Kreuzkümmel", 375, 18, 2, 2, 6, "TL"],
  ["zimt|zimtpulver", "Zimt", 247, 4, 2.6, 2.6, 6, "TL"],
  ["chilipulver|chiliflocken|cayenne|cayennepfeffer|chili", "Chili und Cayenne (Pulver)", 290, 12, 2, 2, 6, "TL"],
  ["pfeffer|schwarzer pfeffer|weisser pfeffer", "Pfeffer", 251, 10, 2.3, 2.3, 6, "TL"],
  ["salz|meersalz|jodsalz|kraeutersalz", "Salz", 0, 0, 6, 6, 6, "TL"],
  ["oregano", "Oregano (getrocknet)", 265, 9, 1, 1, 6, "TL"],
  ["basilikum getrocknet", "Basilikum (getrocknet)", 233, 23, 0.7, 0.7, 6, "TL"],
  ["thymian", "Thymian", 276, 9, 1, 1, 6, "TL"],
  ["rosmarin", "Rosmarin", 331, 5, 1, 1, 6, "TL"],
  ["majoran", "Majoran", 271, 13, 0.6, 0.6, 6, "TL"],
  ["salbei", "Salbei", 315, 11, 0.7, 0.7, 6, "TL"],
  ["petersilie getrocknet", "Petersilie (getrocknet)", 292, 27, 0.5, 0.5, 6, "TL"],
  ["korianderpulver|koriandersamen|gemahlener koriander", "Koriander (Pulver)", 298, 12, 2, 2, 6, "TL"],
  ["ingwerpulver", "Ingwerpulver", 335, 9, 2, 2, 6, "TL"],
  ["knoblauchpulver|knoblauchgranulat", "Knoblauchpulver", 331, 17, 3, 3, 6, "TL"],
  ["zwiebelpulver|zwiebelgranulat", "Zwiebelpulver", 341, 10, 2.4, 2.4, 6, "TL"],
  ["muskat|muskatnuss", "Muskat", 525, 6, 2.2, 2.2, 6, "TL"],
  ["kardamom", "Kardamom", 311, 11, 2, 2, 6, "TL"],
  ["nelken|gewuerznelken", "Nelken", 274, 6, 2, 2, 6, "TL"],
  ["bockshornklee|kasuri methi", "Bockshornklee", 323, 23, 3, 3, 6, "TL"],
  ["senfkoerner|senfsaat|senfpulver", "Senfkörner", 508, 26, 3, 3, 6, "TL"],
  ["fenchelsamen|anis|sternanis", "Fenchel und Anis", 345, 16, 2, 2, 6, "TL"],
  ["suessstoff", "Süßstoff", 0, 0, 0.1, 0.1, 6, "TL"],
  ["bruehpulver|gemuesebruehpulver|bruehwuerfel|huehnerbruehe pulver", "Brühpulver", 180, 6, 4, 4, 6, "TL"],
  ["backpulver", "Backpulver", 53, 0.1, 4, 4, 6, "TL"],
  ["natron", "Natron", 0, 0, 4, 4, 6, "TL"],
  ["trockenhefe|backhefe", "Trockenhefe", 325, 40, 3, 3, 6, "TL"],
  ["vanille|vanilleextrakt|vanillearoma", "Vanilleextrakt", 288, 0.1, 4, 4, 6, "TL"],
  ["vanillezucker", "Vanillezucker", 390, 0, 8, 8, 6, "TL"],
/* ---- weitere Lebensmittel, Backen und Besonderes ---- */
  ["kaesekuchen|quarkkuchen", "Käsekuchen", 265, 8.5, 130, 130, 0.9],
  ["cheesecake|new york cheesecake", "Cheesecake", 320, 6, 120, 120, 1.2],
  ["apfelkuchen|apfeltorte|gedeckter apfelkuchen|apfeltarte|tarte tatin", "Apfelkuchen", 225, 2.8, 120, 120, 0.7],
  ["apfelstrudel|strudel|milchrahmstrudel|topfenstrudel", "Strudel", 225, 3.5, 150, 150, 0.8],
  ["streuselkuchen|butterkuchen|zuckerkuchen|hefekuchen|plattenkuchen|blechkuchen", "Streusel- oder Butterkuchen", 385, 5.5, 80, 80, 0.6],
  ["marmorkuchen|sandkuchen|ruehrkuchen|kastenkuchen|zitronenkuchen|eierlikoerkuchen|becherkuchen|rotweinkuchen|joghurtkuchen|kuchen vom blech|saftiger kuchen", "Rührkuchen", 395, 5, 70, 70, 0.6],
  ["gugelhupf|napfkuchen|rosinenkuchen|gugl", "Gugelhupf", 385, 5.5, 70, 70, 0.6],
  ["schokoladenkuchen|schokokuchen|saftiger schokokuchen|lavakuchen|schokotorte|sachertorte", "Schokoladenkuchen", 405, 5.5, 90, 90, 0.8],
  ["brownie|brownies", "Brownie", 430, 5, 60, 60, 0.9],
  ["muffin|muffins", "Muffin", 400, 5.5, 90, 90, 0.7],
  ["cupcake|cupcakes", "Cupcake", 400, 3.5, 80, 80, 1.0],
  ["donauwelle", "Donauwelle", 350, 4.5, 100, 100, 0.7],
  ["bienenstich", "Bienenstich", 380, 6, 100, 100, 0.8],
  ["zupfkuchen|russischer zupfkuchen|kirschzupfkuchen", "Zupfkuchen", 350, 7, 110, 110, 0.7],
  ["obstkuchen|obsttorte|erdbeerkuchen|erdbeertorte|fruchtkuchen|obsttortelett|tortelett|tarte", "Obstkuchen oder Obsttorte", 185, 3, 120, 120, 0.8],
  ["pflaumenkuchen|zwetschgenkuchen|zwetschgendatschi|kirschkuchen|rhabarberkuchen|beerenkuchen|heidelbeerkuchen|streuselobstkuchen", "Obstkuchen mit Streusel", 205, 3, 120, 120, 0.7],
  ["sahnetorte|buttercremetorte|kirschtorte|himbeertorte|schwarzwaelder|schwarzwaelder kirschtorte|kaesesahnetorte|frankfurter kranz|nusstorte|erdbeersahnetorte|sahneschnitte|kremschnitte", "Sahnetorte", 290, 4, 120, 120, 0.9],
  ["geburtstagstorte|hochzeitstorte|motivtorte|fondanttorte|buttercreme", "Motivtorte", 390, 4, 110, 110, 1.0],
  ["karottenkuchen|moehrenkuchen|rueblikuchen|carrot cake", "Karottenkuchen", 365, 5, 90, 90, 0.7],
  ["bananenbrot|bananenkuchen|banana bread", "Bananenbrot", 290, 4, 70, 70, 0.5],
  ["mohnkuchen|mohnstriezel|mohnschnecke", "Mohnkuchen", 330, 6.5, 90, 90, 0.7],
  ["nusskuchen|nussecke|nussecken|nusszopf|nussschnecke|haselnusskuchen", "Nusskuchen", 420, 6, 70, 70, 0.9],
  ["stollen|christstollen|butterstollen|marzipanstollen|dresdner stollen", "Stollen", 400, 6, 60, 60, 0.9],
  ["spekulatius|printen|lebkuchenherz|honigkuchen", "Spekulatius", 470, 5, 8, 24, 0.8],
  ["zimtsterne", "Zimtsterne", 440, 7, 8, 24, 1.5],
  ["vanillekipferl|butterplaetzchen|spritzgebaeck|mandelplaetzchen|ausstecherle|kipferl", "Plätzchen (Butter)", 495, 5.5, 8, 24, 1.2],
  ["dominosteine|dominostein|lebkuchen schoko", "Dominosteine", 400, 4, 10, 30, 1.0],
  ["butterkeks|leibniz|butterkekse|teegebaeck", "Butterkeks", 450, 7, 4.5, 20, 0.5],
  ["oreo|doppelkeks|prinzenrolle|schokokeks|schokokekse|doppelkekse|schoko keks", "Doppelkeks mit Creme", 480, 5, 11, 33, 0.7],
  ["cookie|cookies|american cookies|chocolate chip|schokocookie", "Cookie", 480, 5, 40, 40, 0.9],
  ["loeffelbiskuit|biskuit|biskotten|savoiardi", "Löffelbiskuit", 390, 8, 11, 33, 0.7],
  ["zwieback", "Zwieback", 400, 10, 8, 24, 0.6],
  ["windbeutel|eclair|eclairs|profiterole|profiteroles|sahnewindbeutel|brandteig", "Windbeutel oder Eclair", 300, 5, 90, 90, 1.0],
  ["tiramisu", "Tiramisu", 290, 5, 120, 120, 1.0],
  ["panna cotta|pannacotta", "Panna Cotta", 190, 3, 120, 120, 0.8],
  ["creme brulee|gebrannte creme", "Crème brûlée", 300, 4, 120, 120, 1.0],
  ["mousse|mousse au chocolat|schokomousse|schokoladenmousse", "Mousse au Chocolat", 230, 4.5, 80, 80, 0.8],
  ["rote gruetze|gruetze|beerengruetze|fruchtgruetze", "Rote Grütze", 100, 0.5, 0, 150, 0.4],
  ["vanillesauce|vanillesosse|vanillecreme", "Vanillesoße", 110, 2.5, 0, 100, 0.3],
  ["fruchtzwerge|fruchtzwerg|zwergenfruechte", "Fruchtzwerge", 125, 5.5, 50, 50, 0.6],
  ["quarkspeise|quarkcreme|dessertquark|quark dessert", "Quarkspeise", 130, 8, 0, 150, 0.4],
  ["quarkbaellchen|quarkkeulchen", "Quarkbällchen", 290, 9, 30, 90, 0.6],
  ["berliner pfannkuchen|pfannkuchen berliner|fastnachtskrapfen", "Berliner", 400, 5.5, 70, 70, 0.7],
  ["laugenbroetchen|laugenstange|laugenstangen|laugengebaeck|laugenzopf|laugenweckle", "Laugengebäck", 270, 8.5, 80, 80, 0.5],
  ["koernerbroetchen|mehrkornbroetchen|dinkelbroetchen|sesambroetchen|mohnbroetchen|kaiserbroetchen|weizenbroetchen|schrippe|schrippen|sonnenblumenbroetchen|roggenbroetchen", "Brötchen (Körner oder Sesam)", 270, 9, 60, 60, 0.5],
  ["ciabatta", "Ciabatta", 260, 8.5, 80, 80, 0.5],
  ["focaccia", "Focaccia", 270, 7, 100, 100, 0.7],
  ["brioche|briochebroetchen|milchbroetchen|milchbrot", "Brioche", 380, 8.5, 50, 50, 0.6],
  ["hefezopf|butterzopf|hefekranz|osterzopf|hefeteilchen|hefegebaeck", "Hefezopf", 330, 8, 60, 60, 0.6],
  ["franzbroetchen", "Franzbrötchen", 400, 6, 90, 90, 0.8],
  ["zimtschnecke|zimtschnecken|rosinenschnecke|plunderschnecke|hefeschnecke|cinnamon roll|cinnamon rolls", "Zimtschnecke", 380, 6, 100, 100, 0.9],
  ["plunder|plundergebaeck|apfeltasche|nusstasche|puddingteilchen|quarktasche|mandelhoernchen|blaetterteigteilchen|vanilleteilchen|kaesetasche", "Plundergebäck", 385, 5.5, 90, 90, 0.9],
  ["buttercroissant|schokocroissant|mandelcroissant|nussnougatcroissant|pain au chocolat|schokobroetchen|pain au raisin", "Croissant (süß)", 400, 7, 70, 70, 0.8],
  ["pumpernickel|vollkornschnitten", "Pumpernickel", 200, 6, 40, 40, 0.4],
  ["bauernbrot|landbrot|sauerteigbrot|koernerbrot|mehrkornbrot|sonnenblumenbrot|weltmeisterbrot|steinofenbrot|krustenbrot|haferbrot", "Bauern- oder Körnerbrot", 240, 8.5, 50, 50, 0.3],
  ["eiweissbrot|proteinbrot|lowcarbbrot|low carb brot|eiweiss brot", "Eiweißbrot", 240, 22, 40, 40, 0.8],
  ["salzstangen|salzbrezel|salzgebaeck|salzbrezeln|salzstangerl", "Salzstangen", 380, 10, 3, 30, 0.7],
  ["cracker|crackers|ritz|salzcracker|kaesecracker|cheese cracker|brotchips", "Cracker", 470, 9, 4, 30, 0.7],
  ["reiscracker|reischips|reiskuchen|reiswaffelchips", "Reiscracker", 390, 7, 3, 20, 0.7],
  ["tortillachips|tortilla chips|nachos|doritos|maischips", "Tortillachips", 490, 7, 0, 40, 0.8],
  ["erdnussflips|flips|erdnussflip|erdnuss flips", "Erdnussflips", 480, 11, 0, 40, 0.8],
  ["pringles|stapelchips|paprikachips|kartoffelsticks|chipsletten|kessel chips|kesselchips", "Kartoffelsnacks", 530, 5, 0, 40, 0.9],
  ["studentenfutter|nussmischung|trailmix|trail mix|nussmix|nuss frucht mix|nuss kern mix", "Studentenfutter", 500, 14, 0, 30, 1.2],
  ["gebrannte mandeln|gebrannte nuesse|kandierte nuesse|honigmandeln", "Gebrannte Mandeln", 480, 10, 0, 40, 1.5],
  ["walnuss|walnuesse|walnusskerne", "Walnüsse", 690, 15, 0, 30, 1.5],
  ["haselnuss|haselnuesse|haselnusskerne|gemahlene haselnuesse", "Haselnüsse", 640, 14, 0, 30, 1.3],
  ["cashew|cashews|cashewkerne|cashewnuesse", "Cashews", 570, 18, 0, 30, 1.6],
  ["erdnuss|erdnuesse|erdnusskerne|gesalzene erdnuesse|geroestete erdnuesse|erdnuesse gesalzen|erdnuesse geroestet", "Erdnüsse", 590, 26, 0, 30, 0.8],
  ["pistazien|pistazie|pistazienkerne", "Pistazien", 600, 20, 0, 30, 2.5],
  ["paranuss|paranuesse|paranusskerne", "Paranüsse", 680, 14, 0, 20, 2.2],
  ["pekannuss|pekannuesse|pecannuss|pecannuesse", "Pekannüsse", 700, 9, 0, 30, 2.5],
  ["macadamia|macadamianuss|macadamianuesse", "Macadamia", 750, 8, 0, 30, 3.0],
  ["erdnussbutter|erdnussmus|peanutbutter|peanut butter|erdnusscreme", "Erdnussbutter", 600, 25, 0, 15, 0.9],
  ["mandelmus|mandelbutter|nussmus|cashewmus|haselnussmus", "Nussmus", 620, 21, 0, 15, 2.0],
  ["schokoaufstrich|nusspli|nugatti|schoko nuss aufstrich|schokocreme", "Schoko-Nuss-Aufstrich", 540, 6, 0, 20, 0.5],
  ["karamellsauce|karamellsosse|karamell|dulce de leche|toffee|karamellcreme", "Karamell", 330, 2.5, 0, 20, 0.6],
  ["schokosauce|schokoladensauce|schokososse|kuchenglasur|schokoglasur", "Schokosoße", 330, 3, 0, 20, 0.5],
  ["zuckerruebensirup|ruebenkraut|ruebensirup|apfelkraut|dattelsirup|melasse", "Rübensirup", 290, 1, 0, 20, 0.5],
  ["backschokolade|kochschokolade|kuvertuere|schokotropfen|schokodrops|schokoraspeln|schokostreusel|hagelslag|schoko chips", "Backschokolade", 520, 5.5, 0, 25, 0.9],
  ["marzipan|marzipanrohmasse|persipan", "Marzipan", 480, 9, 0, 20, 1.2],
  ["nougat|nugat|nuss nougat masse", "Nougat", 520, 5.5, 0, 20, 1.0],
  ["zuckerguss|zuckerglasur|fondant|royal icing|zuckerstreusel|streuzucker|zuckerperlen", "Zuckerguss", 380, 0.2, 0, 20, 0.4],
  ["tortenguss|tortenglasur", "Tortenguss (Pulver)", 330, 0, 0, 12, 1.2],
  ["dinkelmehl|dinkelvollkornmehl|mehl typ 630|mehl 630", "Dinkelmehl", 340, 12, 0, 50, 0.15],
  ["vollkornmehl|weizenvollkornmehl|weizenmehl vollkorn", "Vollkornmehl", 335, 11.5, 0, 50, 0.15],
  ["roggenmehl|roggenvollkornmehl", "Roggenmehl", 320, 8, 0, 50, 0.15],
  ["mandelmehl|gemahlene mandeln|mandeln gemahlen|mandelgriess", "Mandelmehl", 600, 21, 0, 30, 1.2],
  ["kokosmehl", "Kokosmehl", 400, 18, 0, 30, 1.0],
  ["kichererbsenmehl|kichererbsmehl|linsenmehl|lupinenmehl", "Hülsenfruchtmehl", 355, 22, 0, 40, 0.5],
  ["haferkleie|weizenkleie|haferfasern", "Kleie", 250, 16, 0, 20, 0.3],
  ["puderzucker|staubzucker|zuckerpulver|feinzucker", "Puderzucker", 390, 0, 0, 20, 0.15],
  ["brauner zucker|rohrzucker|kandis|kandiszucker|demerara|muscovado|vollrohrzucker|zucker braun", "Brauner Zucker", 385, 0.1, 0, 10, 0.2],
  ["kokosbluetenzucker|kokoszucker", "Kokosblütenzucker", 380, 1.5, 0, 10, 1.2],
  ["xylit|birkenzucker", "Xylit", 240, 0, 0, 10, 1.2],
  ["erythrit|erythritol|stevia|sukrin|suessstoffstreu", "Erythrit oder Stevia", 0, 0, 0, 10, 1.0],
  ["frischhefe|hefewuerfel|hefe frisch|backhefe frisch", "Frischhefe (Würfel)", 105, 9, 42, 21, 1.2],
  ["sauerteig|anstellgut|sauerteigansatz", "Sauerteig", 180, 6, 0, 50, 0.3],
  ["gelatine|gelatineblatt|gelatineblaetter|speisegelatine", "Gelatine", 340, 85, 1.7, 6, 5],
  ["agar|agar agar|johannisbrotkernmehl|guarkernmehl|xanthan|pektin|gelierzucker|gelfix", "Gelier- und Bindemittel", 300, 2, 0, 5, 3],
  ["puddingpulver|vanillepuddingpulver|schokopuddingpulver|saucenpulver|sossenbinder|saucenbinder", "Puddingpulver", 350, 0.5, 0, 20, 0.8],
  ["blaetterteig|blaetterteigplatte|croissantteig|plundrteig", "Blätterteig", 390, 6, 0, 100, 0.8],
  ["muerbeteig|muerbeteigboden|kuchenteig|hefeteig|pizzateig|flammkuchenteig|strudelteig|filoteig|yufka|teigplatte|pizzateig frisch", "Fertigteig", 330, 7, 0, 100, 0.5],
  ["backmischung|kuchenbackmischung|brownie backmischung|backmix|muffinmischung", "Backmischung", 400, 5, 0, 100, 0.5],
  ["kakaonibs|kakao nibs|kakaosplitter|rohkakao", "Kakaonibs", 520, 13, 0, 10, 4],
  ["kondensmilch gezuckert|gezuckerte kondensmilch|milchmaedchen|sweetened condensed milk", "Gezuckerte Kondensmilch", 330, 8, 0, 30, 0.5],
  ["milchpulver|trockenmilch|magermilchpulver|kaffeeweisser|kaffeeweisserpulver", "Milchpulver", 500, 26, 0, 10, 0.8],
  ["kokoscreme|cream of coconut|kokosfett creme", "Kokoscreme", 330, 3, 0, 40, 0.5],
  ["kokosmilch light|leichte kokosmilch", "Kokosmilch (light)", 130, 0.7, 0, 100, 0.3],
  ["zitronenschale|orangenschale|zitronenabrieb|orangenabrieb|zitronenzeste|schale abgerieben", "Zitronen- oder Orangenschale", 47, 1.5, 2, 2, 8, "TL"],
  ["lebkuchengewuerz|spekulatiusgewuerz|pfefferkuchengewuerz|kuchengewuerz|apfelkuchengewuerz|backgewuerz|gewuerzmischung suess", "Lebkuchengewürz", 300, 5, 3, 3, 6, "TL"],
  ["vanilleschote|vanilleschoten|vanille schote|vanillemark|bourbon vanille", "Vanilleschote", 288, 0.1, 2, 2, 20, "Stk"],
  ["backaroma|bittermandelaroma|rumaroma|zitronenaroma|butter vanille aroma|orangenaroma", "Backaroma", 0, 0, 1, 1, 6, "TL"],
  ["lebensmittelfarbe|speisefarbe|farbpulver", "Lebensmittelfarbe", 0, 0, 1, 1, 6, "TL"],
  ["weinstein|weinsteinbackpulver|hirschhornsalz|pottasche|backoblaten|oblaten", "Backzusatz", 0, 0, 1, 1, 6, "TL"],
  ["granola|knuspermuesli|crunchy muesli|crunchy|haferkruspermuesli|nuss muesli", "Granola", 450, 9, 0, 50, 0.7],
  ["schokomuesli|schoko muesli|schoko cerealien|schokocerealien|choco crossies|choco krispies|frosties|honey pops|smacks|fruit loops|lion cerealien|nesquik cerealien|cini minis|trix|cheerios|chocapic", "Frühstücksflocken (gesüßt)", 385, 6.5, 0, 40, 0.5],
  ["weetabix|vollkornflakes|haferringe|kornflakes|bran flakes|specialk|special k|reisflakes|dinkelflakes", "Vollkorn-Frühstücksflocken", 360, 10, 0, 40, 0.5],
  ["haferbrei|porridge fertig|porridge gekocht|haferflockenbrei|haferschleim", "Haferbrei (gekocht)", 75, 3, 0, 250, 0.2],
  ["proteinriegel|eiweissriegel|proteinbar|protein bar|barebells|barrebells|barrel|quest bar|powerbar protein|rocka riegel", "Proteinriegel", 370, 33, 55, 55, 2.2],
  ["energieriegel|datteriegel|fruchtriegel|nussriegel|bifi riegel|lara bar|larabar|corny|corny riegel|getreideriegel|haferriegel|flapjack|flapjacks", "Müsli- oder Energieriegel", 400, 6, 30, 30, 1.0],
  ["huettenkaese|koerniger frischkaese|cottage cheese", "Hüttenkäse", 100, 12.5, 0, 150, 0.5],
  ["ziegenkaese|ziegenfrischkaese|chevre|ziegenweichkaese|ziegenrolle", "Ziegenkäse", 280, 18, 0, 40, 1.5],
  ["butterkaese|edamer|maasdamer|leerdammer|tilsiter|gouda jung|gouda mittelalt|gouda alt|schnittkaese scheiben|havarti|esrom|tilsit|appenzeller|raclette|raclettekaese|fondue kaese|kaesefondue", "Schnittkäse (Edamer, Tilsiter und ähnliche)", 345, 25, 0, 30, 1.0],
  ["burrata", "Burrata", 259, 10.3, 0, 60, 1.5],
  ["grana padano|pecorino|hartkaese|asiago|manchego", "Hartkäse", 390, 33, 0, 15, 2.0],
  ["harzer kaese|handkaese|sauermilchkaese|mainzer kaese|harzer roller", "Harzer Käse", 130, 30, 0, 100, 1.0],
  ["roquefort|bavaria blu|blauschimmel|edelpilzkaese|danablu", "Blauschimmelkäse", 370, 19, 0, 30, 1.5],
  ["kaesescheiben light|kaese light|leichter kaese|magerkaese|kaese 30", "Käse (leicht)", 220, 28, 0, 30, 1.0],
  ["dickmilch|sauermilch|saure milch|trinkjoghurt natur", "Dickmilch", 60, 3.4, 0, 150, 0.2],
  ["trinkjoghurt|trinkjogurt|actimel|joghurtdrink|joghurt drink|yakult|fruchtbuttermilch", "Trinkjoghurt", 70, 3, 0, 100, 0.3],
  ["milchschnitte|pinguin|kinder pingui|pingui", "Milchschnitte", 410, 8, 28, 28, 0.9],
  ["muellermilch|milchmischgetraenk|schokomilch|kakaomilch|trinkschokolade fertig|erdbeermilch|bananenmilch", "Milchmischgetränk", 85, 3.4, 0, 400, 0.2],
  ["proteinpudding|high protein pudding|ehrmann pudding|proteinjoghurt|high protein joghurt|proteinquark|protein skyr|proteindessert|alpro protein|protein dessert", "Protein-Pudding oder -Joghurt", 70, 10, 0, 200, 0.5],
  ["griessbrei|griesspudding|reispudding|milchreis fertig|puddingreis", "Grießbrei", 115, 3.5, 0, 200, 0.3],
  ["sojajoghurt|pflanzenjoghurt|alpro joghurt|kokosjoghurt|mandeljoghurt|haferjoghurt|veganer joghurt", "Pflanzenjoghurt", 60, 3.5, 0, 150, 0.4],
  ["veganer kaese|kaesealternative|pflanzenkaese|veganer schmelzkaese|veganer frischkaese", "Veganer Käseersatz", 270, 0.5, 0, 30, 1.5],
  ["creme fraiche kraeuter|kraeuterquark|kraeutercreme|kraeuterfrischkaese|dip kraeuter|kraeuterdip|sour cream|sourcream|saure sahne dip|joghurtdip", "Kräuterdip", 150, 2.5, 0, 30, 0.6],
  ["kochsahne|cremefine|cuisine|rama cremefine|sahne zum kochen|cremefine kochen|hafercreme|haferkochcreme", "Kochsahne (15 %)", 150, 2.7, 0, 50, 0.4],
  ["sahne 10|saure sahne light|schlagobers|schlagsahne 30|schlagsahne|spruehsahne|sahne aus der dose", "Schlagsahne", 300, 2.4, 0, 30, 0.4],
  ["sahnequark|quark 40|quark 20|speisequark 40|rahmquark|topfen|fruchtquark|mageres quark", "Sahnequark", 160, 11, 0, 100, 0.4],
  ["halbfettmargarine|rama|laetta|margarine light|streichfett|butterersatz|buttergold|kerrygold|butter light", "Streichfett (halbfett)", 400, 0.3, 0, 10, 0.5],
  ["lachs|lachsfilet|zuchtlachs|wildlachs|lachssteak|lachsforelle", "Lachs", 200, 20, 0, 150, 2.0],
  ["raeucherlachs|graved lachs|gravlax|lachsscheiben|raeucherfisch|geraeucherter lachs", "Räucherlachs", 190, 22, 0, 50, 3.5],
  ["thunfisch|thunfisch dose|thunfisch im eigenen saft|thunfisch in wasser|thunfischsteak|thunfisch natur", "Thunfisch (Dose, natur)", 115, 25, 0, 100, 1.2],
  ["thunfisch in oel|thunfisch oel|thunfisch in olivenoel", "Thunfisch (in Öl)", 200, 25, 0, 100, 1.5],
  ["forelle|saibling|zander|barsch|dorade|wolfsbarsch|loup de mer|seebarsch|karpfen|steinbeisser", "Süßwasser- oder Speisefisch", 120, 20, 0, 150, 1.8],
  ["kabeljau|seelachs|pangasius|pollock|rotbarsch|scholle|seehecht|fischfilet|fischfilets|tilapia|schellfisch|heilbutt|merlan|seezunge|dorsch", "Weißfisch (Filet)", 85, 18, 0, 150, 1.2],
  ["fischstaebchen|backfischstaebchen", "Fischstäbchen", 200, 13, 28, 112, 0.6],
  ["backfisch|schlemmerfilet|schlemmer filet|bordelaise|fischfilet paniert|knusperfilet|panierter fisch", "Backfisch (paniert)", 220, 13, 0, 125, 0.8],
  ["garnelen|shrimps|krabben|scampi|riesengarnelen|king prawns|prawn|prawns|nordseekrabben|krebs", "Garnelen", 90, 18, 0, 100, 2.5],
  ["tintenfisch|calamari|kalmar|oktopus|sepia|krake", "Tintenfisch", 90, 16, 0, 100, 1.8],
  ["muscheln|miesmuscheln|jakobsmuscheln|austern|venusmuscheln|muschelfleisch", "Muscheln", 80, 12, 0, 150, 1.8],
  ["hering|matjes|matjesfilet|rollmops|bismarckhering|brathering|salzhering|heringsfilet", "Hering", 210, 18, 0, 100, 1.3],
  ["sardinen|sardine|sprotten|sardellen|anchovis|anchovies|oelsardinen", "Sardinen (Dose)", 205, 24, 0, 80, 1.8],
  ["makrele|geraeucherte makrele|makrelenfilet|raeuchermakrele|stremellachs", "Makrele", 230, 19, 0, 100, 1.8],
  ["surimi|krabbenstaebchen|krebsfleisch|fischklops|fischfrikadelle", "Surimi", 95, 8, 0, 80, 1.2],
  ["entenbrust|ente|barbarieente|gaensebrust|gans|entenkeule|gaensekeule", "Ente oder Gans", 230, 19, 0, 150, 1.5],
  ["lamm|lammfleisch|lammkeule|lammkotelett|lammfilet|lammhack|lammruecken", "Lammfleisch", 230, 18, 0, 150, 2.5],
  ["kalb|kalbfleisch|kalbsschnitzel|kalbsfilet|kalbsleber|kalbsbraten|kalbshaxe|kalbsgeschnetzeltes", "Kalbfleisch", 115, 21, 0, 150, 2.2],
  ["rehfleisch|hirsch|wildschwein|wildfleisch|hirschfleisch|rehruecken|rehkeule|wildgulasch", "Wildfleisch", 115, 21, 0, 150, 2.3],
  ["kaninchen|kaninchenfleisch|haehnchenleber|gefluegelleber|rinderleber|leber|schweineleber|innereien", "Leber oder Kaninchen", 135, 20, 0, 100, 1.2],
  ["brathaehnchen|grillhaehnchen|backhendl|haehnchen gegrillt|ganzes haehnchen|haehnchen vom grill|haehnchenkeule gegrillt|poularde|suppenhuhn", "Brathähnchen (mit Haut)", 205, 21, 0, 200, 0.9],
  ["haehnchenfluegel|chicken wings|wings|hot wings|bbq wings|haehnchen wings", "Hähnchenflügel (mit Haut)", 220, 18, 0, 150, 0.9],
  ["hackbraten|hacksteak|hacksteaks|burgerpatty|pattie|patties|burger patty|hamburgerpatty|fleischkuchen|haschee", "Hacksteak oder Patty", 250, 17, 110, 110, 0.8],
  ["hackbaellchen|fleischbaellchen|hackfleischbaellchen|klopse|fleischkloesschen|koettbullar|mini frikadellen", "Fleischbällchen", 230, 16, 25, 125, 0.7],
  ["cevapcici|cevapi|cevapcici grill|pljeskavica|kebabspiess|kebab spiess|hackspiess|adana kebab|koefte|kofte", "Cevapcici oder Köfte", 260, 17, 25, 125, 1.0],
  ["schaschlik|fleischspiess|spiess|spiesse|grillspiess|haehnchenspiess|haehnchen spiess|shish|satay", "Fleischspieß", 150, 20, 0, 150, 1.5],
  ["gyros|gyrosfleisch|gyrospfanne|doenerfleisch|kebabfleisch|doner fleisch|hirtenfleisch", "Gyrosfleisch", 230, 17, 0, 150, 1.0],
  ["rohschinken|parmaschinken|serrano|serranoschinken|prosciutto|schwarzwaelder schinken|bauernschinken|knochenschinken|lachsschinken|nussschinken|katenschinken|bayerischer schinken|coppa|speck roh", "Rohschinken", 255, 25, 0, 40, 2.2],
  ["nuernberger|nuernberger rostbratwurst|rostbratwurst|thueringer|thueringer rostbratwurst|merguez|chorizo|salsiccia|grillwurst|bauernbratwurst|weisswurst|bregenwurst|knacker|knackwurst|debrecziner|currywurst roh|mini wuerstchen|cocktailwuerstchen", "Bratwurst (frisch oder Brühwurst)", 280, 13, 70, 100, 0.9],
  ["krakauer|wienerle|fleischwurst ring|schinkenwurst|cabanossi|kabanos|landjaeger|kabanossi|mettwuerstchen|mettwurst|salami stick|snack salami|gelbwurst|leberkaes|pfefferbeisser", "Dauerwurst oder Snackwurst", 330, 17, 30, 30, 1.4],
  ["mett|hackepeter|zwiebelmett|thueringer mett|tartar|schabefleisch|beefsteak tatar", "Mett", 250, 14, 0, 100, 1.0],
  ["gefluegelwurst|putenwurst|putensalami|haehnchenwurst|gefluegelaufschnitt|gefluegelmortadella|hahnchenbrust aufschnitt|putenroellchen|putenbrust geraeuchert|haehnchenbrustfilet aufschnitt|haehnchenbrustaufschnitt", "Geflügelwurst", 150, 17, 0, 40, 1.8],
  ["tofu|raeuchertofu|seidentofu|tofu natur", "Tofu", 120, 13, 0, 100, 0.8],
  ["tempeh", "Tempeh", 190, 19, 0, 100, 1.5],
  ["seitan", "Seitan", 120, 25, 0, 100, 1.5],
  ["sojagranulat|sojaschnetzel|sojahack|texturiertes sojaprotein|soja schnetzel|pflanzliches hack|veganes hack|erbsenprotein hack", "Sojagranulat (trocken)", 330, 50, 0, 30, 0.8],
  ["veggie wurst|vegane wurst|vegetarische wurst|veggie wuerstchen|vegane wuerstchen|veggie bratwurst|veganer aufschnitt|vegetarischer aufschnitt", "Vegane Wurst", 200, 15, 0, 80, 1.5],
  ["veggie burger|veganer burger|beyond meat|beyond burger|planted|vegane nuggets|veggie nuggets|veggie patty|pflanzliches patty|veggie schnitzel|vegetarisches schnitzel|veganes schnitzel|vegane bratwurst|ruegenwalder", "Veggie-Patty oder -Nuggets", 230, 17, 100, 100, 1.5],
  ["erbsenprotein|reisprotein|veganes proteinpulver|vegan protein|proteinpulver vegan|pflanzenprotein|hanfprotein", "Veganes Proteinpulver", 375, 78, 30, 30, 2.5],
  ["casein|kasein|caseinpulver|milchprotein|mehrkomponentenprotein|nachtprotein", "Casein-Pulver", 375, 78, 30, 30, 2.5],
  ["kollagen|kollagenpulver|kollagenpeptide|collagen", "Kollagenpulver", 360, 90, 10, 10, 4.0],
  ["massegainer|mass gainer|weight gainer|gainer", "Weight Gainer", 380, 20, 0, 100, 1.5],
  ["kreatin|creatin|creapure|bcaa|aminosaeuren|glutamin|beta alanin|pre workout", "Kreatin oder BCAA", 0, 0, 5, 5, 8, "TL"],
  ["misopaste|miso|misosuppe paste|dashi|dashipulver|hondashi", "Misopaste", 200, 12, 0, 15, 1.2],
  ["kimchi", "Kimchi", 25, 2, 0, 50, 1.0],
  ["sauerkraut|weinkraut|rotkohl glas|apfelrotkohl|rotkraut", "Sauerkraut", 20, 1, 0, 150, 0.3],
  ["mixed pickles|silberzwiebeln|cornichons|essiggurken|perlzwiebeln|pickles|eingelegte zwiebeln|eingelegtes gemuese", "Eingelegtes Gemüse", 20, 0.8, 0, 40, 0.5],
  ["kapern|kapernaepfel", "Kapern", 25, 2.4, 0, 10, 2.0],
  ["getrocknete tomaten|sonnengetrocknete tomaten|tomaten getrocknet|tomaten in oel|doerrtomaten", "Getrocknete Tomaten (in Öl)", 250, 5, 0, 30, 1.8],
  ["artischocken|artischockenherzen|antipasti|antipasti gemuese|gegrilltes gemuese|eingelegte paprika|gefuellte peperoni|peperonata|gegrillte paprika|gegrillte zucchini|oliven antipasti|schafskaese antipasti", "Antipasti", 130, 2, 0, 60, 1.0],
  ["ajvar|paprikamus|lecso|letscho|lecs", "Ajvar", 90, 1.5, 0, 30, 0.6],
  ["tabouleh|taboule|couscoussalat|bulgursalat|quinoasalat|linsensalat|kichererbsensalat|bohnensalat|bunter salat", "Getreide- oder Hülsenfrüchtesalat", 140, 4, 0, 150, 0.5],
  ["kartoffelsalat|kartoffelsalat mayo|kartoffelsalat essig|schwaebischer kartoffelsalat|bayerischer kartoffelsalat", "Kartoffelsalat", 150, 2, 0, 150, 0.4],
  ["nudelsalat|nudelsalat mayo|maccaronisalat|pastasalat|italienischer nudelsalat", "Nudelsalat", 170, 3.5, 0, 150, 0.5],
  ["krautsalat|coleslaw|weisskohlsalat|karottensalat|moehrensalat|rohkostsalat", "Krautsalat", 130, 1.2, 0, 100, 0.4],
  ["gurkensalat|tomatensalat|gemischter salat|beilagensalat|blattsalat|gruener salat|salatteller|salatmix|salatbeilage|rucolasalat|rohkost", "Salat (mit Dressing)", 55, 1.5, 0, 150, 0.5],
  ["wurstsalat|eiersalat|fleischsalat|schinkensalat|gefluegelsalat|thunfischsalat|heringssalat|salat mit ei|streichsalat|krabbensalat", "Wurst- oder Eiersalat", 250, 7, 0, 60, 0.9],
  ["obstsalat|fruchtsalat|obstteller|fruchtteller|obstmix|fruchtmix|beerenmix|obstbecher", "Obstsalat", 55, 0.7, 0, 200, 0.5],
  ["kompott|obstkonserve|pfirsiche dose|ananas dose|fruchtcocktail|mandarinen dose|birnen dose|kirschen glas|apfelkompott|pflaumenkompott|obst aus der dose", "Obst aus der Dose", 70, 0.4, 0, 150, 0.3],
  ["apfelmus|fruchtmus|obstmus|quetschie|quetschies|fruchtpueree|obstpueree|apfelpueree", "Apfelmus", 60, 0.3, 0, 100, 0.25],
  ["beerenmischung|waldfruchtmischung|tk beeren|tiefkuehlbeeren|tk obst|tk fruechte|tk himbeeren|tk heidelbeeren|tk mango|smoothie beeren", "Tiefkühl-Beeren", 45, 1, 0, 100, 0.6],
  ["papaya", "Papaya", 40, 0.5, 0, 150, 0.5],
  ["honigmelone|cantaloupe|galiamelone|zuckermelone|charentais", "Honigmelone", 35, 0.8, 0, 200, 0.3],
  ["passionsfrucht|maracuja|granadilla", "Passionsfrucht", 95, 2.2, 0, 50, 1.5],
  ["litschi|lychee|rambutan|physalis|kaki|sharon|sharonfrucht|drachenfrucht|pitaya|guave|sternfrucht|carambola", "Exotische Früchte", 65, 0.9, 0, 100, 0.9],
  ["johannisbeeren|stachelbeeren|brombeeren|rote johannisbeeren|schwarze johannisbeeren|jostabeeren|holunderbeeren|preiselbeeren frisch|cranberries frisch", "Beeren (Johannis-, Brombeeren)", 45, 1.2, 0, 100, 1.0],
  ["preiselbeeren|preiselbeerkompott|cranberrysauce|cranberry sauce|lingonbeeren|preiselbeermarmelade", "Preiselbeerkompott", 160, 0.3, 0, 20, 0.6],
  ["getrocknete cranberries|cranberries getrocknet|goji|gojibeeren|maulbeeren|getrocknete heidelbeeren|beerenmix getrocknet|getrocknete kirschen", "Getrocknete Beeren", 330, 1, 0, 25, 2.0],
  ["doerrobst|trockenobst|apfelringe|getrocknete aprikosen|getrocknete mangos|getrocknete feigen|getrocknete pflaumen|backpflaumen|trockenpflaumen|doerrpflaumen|getrocknete ananas|mangostreifen|apfelchips", "Trockenobst", 290, 2.5, 0, 30, 0.9],
  ["bananenchips|chips banane|kokoschips|fruchtchips|gemuesechips|chips gemuese|rote bete chips", "Bananenchips", 520, 2, 0, 30, 1.2],
  ["staudensellerie|stangensellerie|bleichsellerie|selleriestangen|sellerieknolle|knollensellerie", "Staudensellerie", 15, 0.8, 0, 60, 0.3],
  ["wirsing|spitzkohl|spitzkraut|kohlsprossen|weisskraut|blaukraut|kohlgemuese", "Wirsing oder Spitzkohl", 30, 3, 0, 150, 0.2],
  ["gruenkohl|palmkohl|schwarzkohl|lacinato|kale|cavolo nero|federkohl", "Grünkohl", 50, 4.5, 0, 100, 0.4],
  ["feldsalat|ackersalat|nuesslisalat|ruccola|romanasalat|romana|lollo rosso|lollo bianco|kopfsalat|batavia|endivie|chicoree|radicchio|babyleaf|baby leaf|salatherzen|kresse|gartenkresse|brunnenkresse", "Blattsalat", 18, 1.5, 0, 60, 0.7],
  ["pastinake|pastinaken|petersilienwurzel|steckrueben|steckruebe|kohlruebe|wurzelgemuese|suppengruen|suppengemuese", "Wurzelgemüse (Pastinake und ähnliche)", 60, 1.5, 0, 100, 0.3],
  ["rettich|rettiche|weisser rettich|schwarzer rettich|mairuebe|rueben|daikon|meerrettich frisch", "Rettich", 15, 1, 0, 80, 0.3],
  ["zuckerschoten|zuckerschote|zuckererbsen|kaiserschoten|kaiserschote|zuckerschotenerbsen|snack erbsen|sugar snaps", "Zuckerschoten", 40, 3, 0, 100, 0.8],
  ["sojasprossen|sprossen|keimlinge|mungobohnensprossen|bambussprossen|bambus|alfalfa|alfalfasprossen|brokkolisprossen|kressesprossen", "Sprossen", 30, 3, 0, 50, 0.9],
  ["kraeuterseitlinge|austernpilze|shiitake|pfifferlinge|steinpilze|champignons braun|braune champignons|portobello|pilzmischung|eierschwammerl|maronen|maronenroehrlinge|champignon", "Pilze (Wald und Zucht)", 25, 3, 0, 100, 1.0],
  ["rhabarber|rhabarberkompott|rhabarberstangen", "Rhabarber", 13, 0.6, 0, 150, 0.4],
  ["schalotte|schalotten|knoblauchzehe|knoblauch frisch|baerlauch|bunte zwiebeln|rote zwiebel|rote zwiebeln|weisse zwiebel", "Schalotten", 30, 1.5, 20, 20, 0.5],
  ["meerrettich|kren|sahnemeerrettich|tafelmeerrettich|wasabi|wasabipaste", "Meerrettich", 60, 2, 0, 10, 1.5],
  ["ofengemuese|ratatouille|gemuesepfanne|tk gemuese|buntes gemuese|gemuesemix|wokgemuese|pfannengemuese|asiagemuese|gemuese mix|gemuesereis|gemuese aus dem ofen|geduenstetes gemuese|gedunstetes gemuese|gemuese geduenstet", "Gemüsemix", 45, 2, 0, 200, 0.4],
  ["kartoffelgratin|gratin|dauphinoise|kartoffelauflauf|kartoffeltorte|gemuesegratin|nudelauflauf|auflauf|ueberbackenes|ueberbacken|lasagne tk|tk auflauf|fertiglasagne|tk lasagne|tiefkuehllasagne", "Auflauf oder Gratin", 150, 6, 0, 300, 0.5],
  ["kartoffelpuffer|reibekuchen|roesti|kartoffelroesti|reiberdatschi|kartoffelplaetzchen|hash browns|haschbrowns|kartoffelrosti", "Kartoffelpuffer oder Rösti", 200, 3.5, 60, 120, 0.4],
  ["ofenkartoffeln|backkartoffeln|wedges|kartoffelspalten|kartoffelecken|ofenkartoffel|haelftenkartoffeln|rosmarinkartoffeln|salzkartoffeln|pellkartoffeln|kartoffeln gekocht|kartoffelhaelften|knoblauchkartoffeln|country potatoes", "Ofenkartoffeln oder Wedges", 140, 3, 0, 200, 0.3],
  ["spaetzle|knoepfle|schupfnudeln|fingernudeln|kartoffelnudeln|pasta fresca|frische nudeln|eiernudeln|nudeln frisch|gnocchi frisch", "Spätzle und Schupfnudeln", 165, 6, 0, 200, 0.4],
  ["semmelknoedel|brotknoedel|knoedel semmel|serviettenknoedel|kartoffelkloesse|kartoffelknoedel|klosse|thueringer kloesse|kloesse halb und halb|knoedelbrot", "Semmelknödel", 150, 5, 100, 200, 0.3],
  ["reisnudeln|vermicelli|pad thai nudeln|reisbandnudeln|reisbandnudeln trocken", "Reisnudeln (Rohgewicht)", 360, 6, 0, 70, 0.4],
  ["glasnudeln|glasnudel|sojanudeln|mungbohnennudeln|konjaknudeln|shirataki|konjak", "Glasnudeln (Rohgewicht)", 340, 0.3, 0, 60, 0.5],
  ["udon|udonnudeln|udon nudeln|ramennudeln|ramen nudeln|eiernudeln asia|asianudeln|wok nudeln|mie nudeln", "Asia-Nudeln (gekocht)", 135, 4.5, 0, 200, 0.5],
  ["sobanudeln|soba|buchweizennudeln|buchweizen|amaranth|teff|hanfsamen|hanfsamen geschaelt|hanf", "Buchweizen oder Hanfsamen", 350, 14, 0, 50, 0.8],
  ["linsen rot|rote linsen|belugalinsen|tellerlinsen|gelbe linsen|puy linsen|berglinsen|linsen trocken|erbsen trocken|gelbe erbsen|trockenerbsen|kichererbsen trocken|sojabohnen trocken|bohnen trocken|trockenbohnen|dal|dhal", "Hülsenfrüchte (trocken)", 340, 24, 0, 60, 0.4],
  ["sojabohnen|sojabohne", "Sojabohnen", 150, 14, 0, 100, 0.5],
  ["salatdressing|dressing|vinaigrette|joghurtdressing|caesar dressing|french dressing|italian dressing|honig senf dressing|balsamico dressing|essig oel dressing|salatsosse|salatsauce", "Salatdressing", 200, 1, 0, 20, 0.4],
  ["salatcreme|miracel whip|miracle whip|salatmayonnaise|mayonnaise light|mayo light|remoulade|remouladensauce|remouladensosse|tartarsauce|tatarensauce", "Remoulade", 380, 1, 0, 20, 0.4],
  ["knoblauchsauce|knoblauchsosse|knobisauce|aioli|knoblauchdip|knoblauch dip|zaziki", "Knoblauchsoße", 450, 1.5, 0, 20, 0.5],
  ["bechamel|bechamelsauce|bechamelsosse|mehlschwitze|helle sauce|sauce hollandaise|hollandaise|sosse hollandaise|bearnaise|sauce bearnaise", "Bechamel oder Hollandaise", 110, 3, 0, 80, 0.4],
  ["pilzsauce|pilzsosse|rahmsauce|rahmsosse|sahnesauce|sahnesosse|jaegersauce|jaegersosse|rahmgeschnetzeltes sauce|zwiebelsauce|zwiebelsosse|champignonsauce|champignonsosse|gorgonzolasauce|kaesesauce|kaesesosse|carbonara sauce|carbonarasosse", "Sahnesoße", 110, 2, 0, 100, 0.4],
  ["bolognese|bolognesesauce|bologneser sauce|hackfleischsauce|fleischsauce|ragu|ragout|hacksosse", "Bolognesesoße", 120, 7, 0, 200, 0.6],
  ["hoisin|hoisinsauce|hoisinsosse|teriyaki|teriyakisauce|teriyakisosse|austernsauce|austernsosse|sojasauce suess|ketjap manis|kecap manis|pflaumensauce|suess sauer sosse|suess sauer sauce|suesssauer sauce", "Asia-Soße (süß)", 150, 2, 0, 20, 0.5],
  ["sweet chili|sweet chilli|suesse chilisauce|chilisauce suess|thai chili sauce|sweet chili sauce|sweet chilisauce", "Sweet-Chili-Soße", 220, 0.3, 0, 20, 0.4],
  ["fischsauce|fischsosse|nam pla|nampla", "Fischsoße", 35, 5, 0, 10, 0.5],
  ["currypaste|rote currypaste|gruene currypaste|gelbe currypaste|thai curry paste|massaman paste|tikka masala paste|curry paste|madras paste|currymischung|korma paste", "Currypaste", 130, 3, 0, 15, 2.0],
  ["passata|tomatenpassata|tomatenpueree|tomatensugo|sugo|tomaten sauce glas|pastasauce|pastasosse|arrabbiata sauce|napoli sauce|pizzasauce|pizzasosse|tomatensosse fertig|tomatensauce fertig", "Passata oder Pastasoße", 40, 1.5, 0, 150, 0.2],
  ["gewuerzketchup|curryketchup|currysauce ketchup|tomatenketchup|ketchup scharf|bbq ketchup", "Curryketchup", 120, 1.2, 0, 20, 0.3],
  ["pesto rosso|pesto verde|pesto genovese|basilikumpesto|rucolapesto|rotes pesto|gruenes pesto|baerlauchpesto|kuerbiskernpesto", "Pesto (Glas)", 450, 5, 0, 20, 1.3],
  ["leinoel|walnussoel|kuerbiskernoel|arganoel|haselnussoel|erdnussoel|traubenkernoel|disteloel|distelhoel|distelhl|distelol|distelhaoel|rapsoel kaltgepresst|hanfoel", "Spezialöl", 900, 0, 0, 10, 1.0],
  ["sprueoel|spruehoel|bratspray|oelspray|olivenoel spray|oel spray|backtrennspray|trennspray", "Bratspray (1 Sprühstoß)", 700, 0, 0, 1, 1.0],
  ["fanta|sprite|spezi|fritz kola|club mate|ginger ale|tonic|tonic water|bitter lemon|mezzo mix|mezzomix|schwip schwap|7 up|mountain dew|dr pepper|bionade|ice tea|fritz limo|limonade zitrone", "Softdrink (Limo)", 40, 0, 0, 330, 0.12],
  ["apfelschorle|saftschorle|schorle|traubenschorle|rhabarberschorle|johannisbeerschorle|kirschschorle|orangenschorle|fruchtschorle|wasser mit saft", "Saftschorle", 25, 0.2, 0, 300, 0.1],
  ["traubensaft|kirschsaft|multivitaminsaft|multivitamin|bananensaft|ananassaft|karottensaft|sauerkirschsaft|holundersaft|johannisbeersaft|nektar|fruchtsaft|direktsaft|mangosaft|pfirsichsaft|maracujasaft|grapefruitsaft|vitaminsaft", "Fruchtsaft", 48, 0.5, 0, 200, 0.12],
  ["tomatensaft|gemuesesaft|rote bete saft|sauerkrautsaft|selleriesaft|tomatensaft salz|gazpacho trinkbar", "Gemüsesaft", 20, 0.9, 0, 200, 0.15],
  ["milchshake|milkshake|shake schoko|shake vanille|shake erdbeer|shake mcdonalds|eiskaffee|eiscafe|frappe|frapp|frappee|iced coffee|ice coffee|kaltes kaffeegetraenk", "Milchshake", 100, 3.5, 0, 300, 0.4],
  ["proteinshake|proteindrink|protein shake|eiweissshake|eiweissdrink|ready to drink protein|proteinmilch|high protein drink|protein milch|fertigshake|myprotein shake|ehrmann protein drink|weider shake|barebells shake", "Proteinshake (fertig)", 70, 12, 0, 330, 0.8],
  ["kokoswasser|kokosnusswasser|birkenwasser|ahornwasser|vitaminwasser|sportgetraenk|isostar|isotonisch|isotonisches getraenk|iso getraenk|elektrolytgetraenk|powerade|gatorade|aquarius|elektrolyte", "Sportgetränk", 25, 0, 0, 500, 0.15],
  ["kombucha|wasserkefir|kefirwasser|ayran|lassi|mangolassi|salzlassi|joghurtgetraenk", "Kombucha, Ayran oder Lassi", 40, 1.5, 0, 250, 0.4],
  ["malzbier|malzgetraenk|vitamalz|nonnenbier|bionade malz|alkoholfreies bier|alkoholfreies weizen|bier alkoholfrei|0 0 bier|alkoholfreies pils", "Alkoholfreies Bier", 28, 0.4, 0, 500, 0.15],
  ["radler|alsterwasser|shandy|biermischgetraenk|bier mit limo|russn|schorle bier|colabier", "Radler", 33, 0.3, 0, 500, 0.15],
  ["weizenbier|weissbier|hefeweizen|pils|pilsner|helles|export|lager|kristallweizen|dunkles bier|dunkelbier|schwarzbier|bockbier|kellerbier|craft beer|stout|guinness|koelsch|alt bier|altbier|maibock", "Bier (Pils, Weizen, Helles)", 44, 0.5, 0, 500, 0.15],
  ["wodka|vodka|gin|rum|whisky|whiskey|korn|schnaps|likoer|jaegermeister|tequila|obstler|doppelkorn|grappa|cognac|weinbrand|ouzo|raki|averna|amaro|baileys|kraeuterlikoer|eierlikoer", "Spirituosen", 235, 0, 0, 40, 0.6],
  ["gluehwein|punsch|feuerzangenbowle|heisser apfelwein|heisse weinschorle|jagertee|hot toddy|bowle|sangria|weinschorle|weissweinschorle|rotweinschorle|wein schorle", "Glühwein oder Wein-Mischgetränk", 90, 0.1, 0, 200, 0.3],
  ["advocaat|eierpunsch", "Eierlikör", 280, 3, 0, 40, 0.8],
  ["hafermilch barista|barista haferdrink|mandeldrink|reisdrink|kokosdrink|cashewdrink|erbsendrink|dinkeldrink|nussdrink|sojadrink vanille|sojadrink schoko|haferdrink schoko|pflanzenmilch|alpro|oatly", "Barista- oder Pflanzendrink", 55, 1.5, 0, 250, 0.2],
  ["espresso|doppio|ristretto|kaffee espresso|espresso doppio|lungo|cafe crema|filterkaffee|schwarzer kaffee|americano|caffe americano|moccaccino", "Espresso", 2, 0.2, 0, 30, 0.2],
  ["kakao getrunken|trinkschokolade|schokomilch heiss|kakao mit milch|kakao trinken|kakaogetraenk|kakaopulver getraenk|nesquik|caotina|suchard|ovomaltine|kaba kakao", "Kakao (mit Milch)", 80, 3.3, 0, 250, 0.3],
  ["chai|chai tee|masala chai|golden milk|goldene milch|matcha|ingwertee|fencheltee|pfefferminztee|kamillentee|hagebuttentee|fruechtetee|gruentee|schwarztee|rooibos|rooibostee|kraeutertee|tee suess", "Tee", 1, 0, 0, 250, 0.03],
  ["kaffee mit zucker|zuckerkaffee|kaffee suess|kaffee zucker", "Kaffee mit Zucker", 25, 0.2, 0, 250, 0.05],
  ["wasser mit geschmack|aromawasser|fruchtwasser|infused water|zero limo|zero drink|cola light|diet cola|pepsi max|fanta zero|sprite zero|zuckerfrei|getraenk light|eistee zero|energy zero|monster zero|redbull sugarfree|red bull sugarfree|red bull zero|pepsi light|schweppes zero|powerade zero|bonaqua", "Zuckerfreies Getränk", 2, 0, 0, 330, 0.1],
  ["vollmilchschokolade|milchschokolade|alpenmilchschokolade|milka|ritter sport|schokoladentafel|tafel schokolade|lindt|toblerone", "Vollmilchschokolade", 535, 7, 5, 25, 0.8],
  ["zartbitterschokolade|bitterschokolade|dunkle schokolade|edelbitter|zartbitter|bitter schokolade|70 prozent schokolade", "Zartbitterschokolade", 560, 8, 5, 20, 1.0],
  ["weisse schokolade|weisse tafel|white chocolate", "Weiße Schokolade", 560, 6.5, 5, 25, 0.8],
  ["nussschokolade|haselnussschokolade|erdbeerschokolade|joghurtschokolade|knusperschokolade|nuss schokolade", "Nuss- oder Joghurtschokolade", 550, 8, 5, 25, 0.9],
  ["kinderschokolade|kinder schokolade", "Kinderschokolade", 560, 8, 12.5, 25, 1.2],
  ["kinder bueno|bueno", "Kinder Bueno", 570, 9, 43, 43, 1.5],
  ["kinder riegel|kinderriegel|kinder country|kinder maxi|kinder happy hippo|happy hippo|duplo|hanuta|knoppers|milchriegel|yogurette|milky way|milkyway|balisto|toffifee|raffaello", "Schoko-Riegel (Kinder, Hanuta, Duplo)", 550, 8, 25, 25, 1.2],
  ["pralinen|praline|lindor|ferrero rocher|mon cheri|konfekt|trueffel|schokotruefel|trueffelpralinen", "Pralinen", 570, 6, 12, 24, 2.0],
  ["weingummi|fruchtgummi|haribo|goldbaeren|saure zungen|schlumpf|schlumpfe|colorado|lakritzschnecken|veggie gummibaerchen|vegane gummibaerchen|schnuller", "Weingummi", 340, 6.5, 0, 30, 0.7],
  ["lakritz|lakritze|salmiak|salzlakritz|katjes", "Lakritz", 330, 3, 0, 20, 0.8],
  ["bonbons|bonbon|lutscher|hustenbonbon|karamellbonbon|zuckerl|kaubonbon|werthers|werther s|werthers original", "Bonbons", 390, 0.1, 4, 16, 0.6],
  ["zuckerwatte|zuckerstange|kandierte aepfel|liebesapfel|zuckerwolke", "Zuckerwatte", 390, 0, 0, 30, 0.5],
  ["speiseeis|vanilleeis|eiscreme|sahneeis|milcheis|erdbeereis|schokoladeneis|schokoeis|eiskonfekt|joghurteis|stracciatella|pistazieneis|nusseis|cookie eis|eis becher", "Eiscreme (Vanille, Schoko)", 210, 3.5, 50, 100, 0.7],
  ["fruchteis|sorbet|wassereis|zitroneneis|eis am stiel frucht|erdbeersorbet|zitronensorbet|granita|slush|slush eis|frozen joghurt|froyo|frozen yogurt", "Fruchteis oder Sorbet", 120, 0.5, 50, 100, 0.6],
  ["dosenravioli|ravioli dose|ravioli aus der dose|ravioli in tomatensauce|ravioli in tomatensosse|ravioli konserve|nudeln dose|nudeln aus der dose|bolognese dose|spaghetti dose|maccaroni dose|erbsen und moehren dose|kartoffelsuppe dose|gulaschsuppe dose|linsensuppe dose|eintopf aus der dose", "Dosengericht (Ravioli, Eintopf)", 90, 3.5, 0, 400, 0.3],
  ["rahmspinat|rahm spinat|spinat mit sahne|rahmspinat tk", "Rahmspinat", 70, 3.5, 0, 150, 0.3],
  ["fladenbroetchen|roti|chapati|paratha|piadina|lavash|pide|pita tasche|pitataschen|pita belegt", "Fladenbrot (Roti, Pide, Chapati)", 280, 9, 80, 80, 0.4],
  ["pizzaboden|pizzaboeden|pizzabodenmix|pizzateig fertig", "Fertiger Pizzaboden", 270, 8, 0, 150, 0.4],
  ["nutella brot|nutellabrot|nutella toast|schokobrot|honigbrot|marmeladenbrot|marmeladenbroetchen|butterbrot|butterbroetchen|butter honig brot|brot mit butter und honig|brot mit marmelade|brot mit nutella|brot mit honig|brot mit butter|stulle mit butter|stulle mit honig|stulle mit marmelade", "Brot mit Aufstrich (1 Scheibe)", 330, 7, 60, 60, 0.4],
];
/* Gerichte außer Haus oder Fertiggerichte, Richtwerte je Portion: [Schlüssel, Name, kcal, Eiweiß] */
const CDISH = [
  ["doenerteller", "Dönerteller", 950, 45], ["duerum|doener duerum", "Dürüm", 800, 38], ["doener", "Döner", 750, 38], ["big mac", "Big Mac", 510, 26], ["cheeseburger", "Cheeseburger", 310, 16], ["hamburger|burger", "Burger", 450, 22],
  ["currywurst", "Currywurst mit Pommes", 850, 26], ["bratwurst broetchen|bratwurst im broetchen", "Bratwurst im Brötchen", 450, 17], ["stueck pizza", "Stück Pizza", 280, 11], ["pizza margherita|pizza", "Pizza (ganz, Restaurant)", 850, 32],
  ["spaghetti bolognese|nudeln bolognese", "Spaghetti Bolognese (Restaurant)", 780, 32], ["lasagne", "Lasagne", 650, 30], ["schnitzel mit pommes|schnitzel pommes", "Schnitzel mit Pommes", 950, 42], ["hirtensalat|salat mit haehnchen", "Salat mit Hähnchen", 450, 32],
  ["leberkaesbroetchen|leberkaes broetchen|leberkaese", "Leberkäsbrötchen", 520, 20], ["kaesebroetchen|broetchen mit kaese|belegtes broetchen", "Brötchen mit Käse", 380, 17], ["schinkenbroetchen|broetchen mit schinken", "Brötchen mit Schinken", 350, 18],
  ["croissant", "Croissant", 280, 5], ["latte macchiato", "Latte macchiato", 150, 8], ["cappuccino", "Cappuccino", 90, 5], ["kaffee mit milch", "Kaffee mit Milch", 40, 2], ["eis|eiskugel", "Eiskugel", 90, 1.5], ["muesliriegel", "Müsliriegel", 100, 2], ["butter chicken|murgh makhani", "Butter Chicken (ohne Reis)", 520, 36], ["chicken tikka masala|tikka masala", "Chicken Tikka Masala (ohne Reis)", 480, 36], ["chili con carne", "Chili con Carne (Portion)", 450, 30], ["omelett|omelette", "Omelett (3 Eier)", 330, 21], ["samosa|samosas", "Samosa", 250, 5], ["pad thai", "Pad Thai", 700, 25], ["ramen", "Ramen (Restaurant)", 600, 25], ["kaesespaetzle", "Käsespätzle", 700, 28], ["rouladen", "Rouladen mit Beilage", 700, 45], ["gulasch", "Gulasch mit Nudeln", 650, 38],
/* ---- weitere Gerichte ---- */
  ["wiener schnitzel|paniertes schnitzel|schnitzel paniert|schnitzel wiener art", "Paniertes Schnitzel (ohne Beilage)", 550, 38],
  ["jaegerschnitzel|zigeunerschnitzel|rahmschnitzel", "Schnitzel mit Soße und Nudeln", 800, 40],
  ["cordon bleu", "Cordon bleu", 600, 40],
  ["schweinebraten|krustenbraten", "Schweinebraten mit Knödeln und Soße", 800, 42],
  ["sauerbraten|rinderbraten", "Sauerbraten mit Klößen", 750, 42],
  ["kassler mit sauerkraut|kasseler mit sauerkraut", "Kassler mit Sauerkraut und Kartoffeln", 650, 40],
  ["eisbein|schweinshaxe|schweinehaxe", "Haxe mit Beilage", 950, 65],
  ["huehnerfrikassee|haehnchenfrikassee|frikassee|zuercher geschnetzeltes|rahmgeschnetzeltes", "Geschnetzeltes oder Frikassee mit Reis", 650, 38],
  ["koenigsberger klopse", "Königsberger Klopse", 650, 32],
  ["bratwurst mit sauerkraut|wurst mit sauerkraut", "Bratwurst mit Sauerkraut und Püree", 800, 30],
  ["kartoffelsuppe", "Kartoffelsuppe", 350, 10],
  ["gulaschsuppe", "Gulaschsuppe", 400, 28],
  ["erbsensuppe|linsensuppe mit wurst|linseneintopf|bohneneintopf|erbseneintopf", "Eintopf mit Wurst", 450, 24],
  ["bauernfruehstueck|strammer max|bratkartoffeln mit ei|bratkartoffeln mit spiegelei|spiegelei mit bratkartoffeln", "Bauernfrühstück", 700, 28],
  ["pfannkuchen mit apfelmus|eierkuchen mit apfelmus|pancakes mit sirup|pancakes mit ahornsirup", "Pfannkuchen mit Beilage (2 Stück)", 520, 13],
  ["kaiserschmarrn|kaiserschmarren|schmarrn", "Kaiserschmarrn", 700, 18],
  ["germknoedel|dampfnudel|dampfnudeln|buchteln", "Germknödel oder Dampfnudel", 650, 12],
  ["zwetschgenknoedel|obstknoedel|marillenknoedel", "Obstknödel (2 Stück)", 520, 11],
  ["milchreis mit zimt|milchreis mit zimt und zucker|milchreis mit apfelmus", "Milchreis mit Zimt und Zucker", 450, 12],
  ["maultaschen in bruehe|geschmelzte maultaschen", "Maultaschen (3 Stück, in Brühe)", 450, 20],
  ["flammkuchen|tarte flambee", "Flammkuchen (ganz)", 750, 24],
  ["steak mit pommes|rumpsteak mit pommes|entrecote mit pommes|nackensteak mit pommes|grillteller", "Steak mit Pommes", 950, 50],
  ["fish and chips|backfisch mit pommes|backfisch mit kartoffelsalat", "Backfisch mit Pommes", 850, 32],
  ["lachs mit reis|lachs mit nudeln|lachs mit kartoffeln|lachsfilet mit gemuese", "Lachs mit Beilage", 650, 40],
  ["pizza salami|salamipizza|pizza diavola|pizza peperoni", "Pizza Salami (ganz)", 920, 38],
  ["pizza schinken|pizza hawaii|pizza funghi|pizza prosciutto|schinkenpizza|hawaiipizza|pizza gemuese|pizza vegetaria", "Pizza Schinken, Hawaii oder Funghi (ganz)", 850, 34],
  ["pizza tonno|pizza quattro stagioni|pizza capricciosa", "Pizza Tonno oder Stagioni (ganz)", 880, 42],
  ["pizza quattro formaggi|pizza vier kaese|pizza 4 kaese", "Pizza Quattro Formaggi (ganz)", 1000, 46],
  ["calzone", "Calzone", 900, 38],
  ["pizzabroetchen|pizzaschnecke|pizzaschnecken|pizzastange", "Pizzabrötchen", 330, 11],
  ["spaghetti carbonara|nudeln carbonara|pasta carbonara", "Spaghetti Carbonara", 850, 32],
  ["spaghetti napoli|nudeln mit tomatensauce|nudeln mit tomatensosse|pasta pomodoro|penne pomodoro|spaghetti tomatensauce", "Nudeln mit Tomatensoße", 600, 18],
  ["penne arrabbiata|spaghetti arrabbiata|nudeln arrabbiata", "Penne Arrabbiata", 650, 20],
  ["tortellini sahne schinken|tortellini mit sahnesauce|tortellini mit sahnesosse|ravioli mit sahne", "Tortellini mit Sahnesoße", 800, 28],
  ["spaghetti pesto|nudeln mit pesto|pasta pesto|penne pesto", "Nudeln mit Pesto", 750, 22],
  ["aglio e olio|spaghetti aglio e olio", "Spaghetti Aglio e Olio", 700, 17],
  ["gnocchi gorgonzola|gnocchi mit gorgonzola|gnocchi mit sahnesosse", "Gnocchi mit Soße", 800, 22],
  ["cannelloni|manicotti", "Cannelloni", 700, 30],
  ["risotto", "Risotto", 600, 15],
  ["nudeln mit garnelen|spaghetti frutti di mare|spaghetti vongole|lachsnudeln|nudeln mit lachs", "Nudeln mit Meeresfrüchten oder Lachs", 700, 30],
  ["insalata caprese|tomate mozzarella|bruschetta", "Caprese oder Bruschetta", 350, 18],
  ["gebratene nudeln|bami goreng|chow mein|mie goreng|yakisoba", "Gebratene Nudeln (Asia)", 800, 25],
  ["gebratener reis|nasi goreng|egg fried rice|fried rice", "Gebratener Reis", 750, 22],
  ["chinapfanne|china pfanne|chop suey|kung pao", "Chinapfanne mit Reis", 700, 32],
  ["suess sauer haehnchen|haehnchen suess sauer|suess saure ente|knusprige ente|peking ente", "Süß-sauer Hähnchen oder Ente mit Reis", 850, 35],
  ["fruehlingsrollen|fruehlingsrolle|sommerrollen|dim sum|dumplings|gyoza|wan tan|wonton|baozi", "Frühlingsrollen oder Dim Sum (4 Stück)", 400, 10],
  ["sushi|maki|nigiri|sashimi", "Sushi (8 Stück)", 380, 15],
  ["misosuppe|ramensuppe|pho bo|tom yum|tom kha|laksa", "Asia-Suppe (Portion)", 450, 25],
  ["bibimbap|bulgogi|poke bowl|pokebowl|buddha bowl|burrito bowl", "Bowl (Reis, Gemüse, Protein)", 650, 28],
  ["thai curry|rotes curry|gruenes curry|gelbes curry|massaman curry|kokoscurry|gemuesecurry", "Thai-Curry mit Reis", 750, 30],
  ["linsencurry|chana masala|kichererbsencurry|palak paneer|paneer tikka masala|aloo gobi|dal tadka|dal makhani", "Indisches Gemüse- oder Linsencurry (mit Reis)", 600, 20],
  ["chicken curry|haehnchen curry|huehnercurry|chicken korma|vindaloo|jalfrezi|lammcurry", "Hähnchen-Curry mit Reis", 750, 38],
  ["biryani|pilaw|pulao", "Biryani", 750, 30],
  ["falafel teller|falafelteller|mezzeteller|vorspeisenteller|hummusteller", "Falafel- oder Mezze-Teller", 850, 28],
  ["falafel im fladenbrot|falafel wrap|falafel tasche|falafeltasche|halloumi wrap|vegetarischer doener|veggie doener", "Falafel im Fladenbrot oder Wrap", 650, 22],
  ["gyros teller|gyrosteller|gyros mit pommes|gyros pita|gyrospita|souvlaki|souvlaki teller|bifteki", "Gyros- oder Souvlaki-Teller", 900, 42],
  ["moussaka|pastitsio|kohlroulade|kohlrouladen|dolmades|krautwickel", "Moussaka oder Kohlroulade", 650, 28],
  ["griechischer salat|bauernsalat|caesar salad|caesarsalat|nizza salat|salat nicoise", "Großer Salat mit Topping", 450, 22],
  ["tacos|taco", "Tacos (2 Stück)", 450, 20],
  ["burrito|burritos|chimichanga", "Burrito", 700, 30],
  ["enchiladas|fajitas|fajita", "Enchiladas oder Fajitas", 700, 32],
  ["quesadilla|quesadillas", "Quesadilla", 650, 28],
  ["nachos mit kaese|nachos mit hack|nachosteller", "Nachos mit Käse (Teller)", 700, 18],
  ["mcchicken|chicken burger|crispy chicken burger|filet o fish|fischburger", "Chicken- oder Fischburger", 420, 17],
  ["royal tx|whopper|big king|quarter pounder|premium burger|gourmet burger|bacon burger|bbq burger", "Großer Burger (Premium)", 600, 30],
  ["double cheeseburger|doppel cheeseburger|doppelcheeseburger", "Doppel-Cheeseburger", 450, 26],
  ["chicken mcnuggets|mcnuggets|nuggets mit pommes|chicken tenders", "Chicken Nuggets (6 Stück)", 270, 15],
  ["pommes klein|pommes mittel|pommes gross|pommes mit mayo|pommes mit ketchup|pommes rot weiss|portion pommes", "Pommes (mittlere Portion)", 450, 5],
  ["hotdog|hot dog|bockwurst im broetchen|wurst im broetchen|wuerstchen im broetchen", "Hotdog", 450, 16],
  ["frikadellenbroetchen|buletten broetchen|bulette im broetchen|frikadelle im broetchen", "Frikadellenbrötchen", 500, 20],
  ["fischbroetchen|matjesbroetchen|lachsbroetchen|backfischbroetchen|krabbenbroetchen|bismarckbroetchen", "Fischbrötchen", 400, 18],
  ["schnitzelbroetchen|schnitzelsemmel|schnitzel im broetchen|haehnchenwrap|chicken wrap|crispy chicken wrap", "Schnitzelbrötchen oder Hähnchenwrap", 550, 28],
  ["belegtes baguette|baguette mit kaese|baguette mit schinken|baguette mit salami|baguette mit pute|baguette caprese", "Belegtes Baguette", 500, 21],
  ["sandwich|club sandwich|panini|subway|footlong", "Sandwich oder Panini", 520, 24],
  ["toast hawaii|kaesetoast|schinkentoast|toast mit kaese|toast mit schinken|ueberbackener toast", "Toast Hawaii oder Käsetoast", 380, 18],
  ["avocadotoast|avocado toast|avocadobrot", "Avocadotoast", 350, 9],
  ["bagel mit frischkaese|bagel mit lachs|bagel belegt|bagel mit ei|bagel mit schinken", "Bagel belegt", 420, 15],
  ["butterbrezel|brezel mit butter|laugenbroetchen mit butter|laugenstange mit butter|brezel mit kaese|laugenbroetchen mit kaese|laugenbroetchen belegt", "Butterbrezel oder Laugenbrötchen belegt", 380, 11],
  ["kaesestange|kaesestangen|schinkencroissant|kaesecroissant|croissant mit schinken|croissant mit kaese", "Käsestange oder Schinkencroissant", 380, 13],
  ["milchkaffee|cafe latte|caffe latte|flat white|iced latte|eislatte|cold brew latte|cortado", "Milchkaffee oder Latte (groß)", 150, 8],
  ["chai latte|iced chai|matcha latte|golden latte|haferlatte|sojalatte", "Chai oder Matcha Latte", 200, 6],
  ["heisse schokolade|heisser kakao|kakao mit sahne|hot chocolate", "Heiße Schokolade mit Sahne", 350, 9],
  ["frappuccino|eiskaffee mit sahne|eisschokolade|affogato|caramel macchiato|mochaccino", "Frappuccino oder Eiskaffee mit Sahne", 400, 6],
  ["bubble tea|bubbletea|boba", "Bubble Tea", 400, 3],
  ["softeis|eis in der waffel|eistuete|eiswaffel", "Softeis oder Eis in der Waffel", 220, 4],
  ["eisbecher|spaghettieis|schwarzwaldbecher|banana split|bananasplit|dame blanche|coupe danmark|heisse liebe|erdbeerbecher", "Eisbecher mit Sahne", 480, 7],
  ["magnum|cornetto|solero|nogger|stieleis|eis am stiel|ben and jerrys|haagen dazs|premium eis", "Eis am Stiel oder Premium-Eis (Portion)", 280, 3.5],
  ["aperol spritz|aperol|hugo|lillet|campari spritz|veneziano", "Spritz (Aperol, Hugo und ähnliche)", 190, 0.2],
  ["gin tonic|cuba libre|rum cola|whisky cola|wodka cola|vodka cola|jaeger cola|moscow mule|caipirinha|mojito|margarita|pina colada|sex on the beach|long island|negroni|bloody mary|mai tai|tequila sunrise|white russian|wodka lemon|vodka lemon|wodka energy|vodka energy|wodka bull|vodka bull|amaretto sour|espresso martini|old fashioned|daiquiri|longdrink|long drink", "Cocktail oder Longdrink", 220, 0.3],
];
const CFOODS = (() => {
  const L = [], nm = (s) => s.split("|").map((x) => CNORM(x));
  Object.keys(PRICE).forEach((k) => { const p = PRICE[k]; L.push({ id: k, name: p.n.replace(/ \(.*\)/, "").replace(/^Scheibe /, ""), kcal: p.kcal, p: p.p, per: p.u === "g" || p.u === "ml" ? 0 : p.per, pu: p.u, def: CDEF[k] || (p.u === "g" || p.u === "ml" ? 100 : p.per), eur: p.price / p.pack * 100, keys: ((CSYN[k] || "").includes("|") ? CSYN[k].split("|") : (CSYN[k] || "").split(" ")).filter(Boolean), raw: ["reis", "nudel", "couscous", "linse"].includes(k) }); });
  CEXTRA.forEach((x, i) => L.push({ id: "x" + i,  name: x[1], kcal: x[2], p: x[3], per: x[4], pu: x[7] || (x[4] ? "Stk" : "g"), def: x[5], eur: x[6], keys: nm(x[0]), raw: /Rohgewicht/.test(x[1]) }));
  return L;
})();
const cLev = (a, b) => { const d = Array.from({ length: a.length + 1 }, (_, i) => [i]); for (let j = 1; j <= b.length; j++) d[0][j] = j; for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); return d[a.length][b.length]; };
function cFuzzy(list, text) {
  let best = null, bd = 9;
  text.split(" ").filter((w) => w.length >= 5).forEach((w) => list.forEach((it) => it.keys.forEach((k) => { if (k.includes(" ") || k.length < 5) return; const d = cLev(w, k), lim = k.length >= 8 ? 2 : 1; if (d <= lim && d < bd) { best = it; bd = d; } })));
  return best;
}
function cMatch(list, text) {
  let best = null, bl = 0;
  list.forEach((it) => it.keys.forEach((k) => {
    const words = text.split(" ");
    const hit = k.includes(" ") ? (" " + text + " ").includes(" " + k + " ") : words.some((w) => w === k || (k.length >= 5 && k !== "eiweiss" && w.includes(k)) || (k.length >= 4 && w.length > k.length && (w === k + "n" || w === k + "s" || w === k + "en" || w === k + "e")));
    if (hit && k.length > bl) { best = it; bl = k.length; }
  }));
  return best;
}
const CDISHL = CDISH.map((d) => ({ name: d[1], kcal: d[2], p: d[3], keys: d[0].split("|").map(CNORM) }));
const CUNIT = { g: "g", gr: "g", gramm: "g", kg: "kg", ml: "ml", l: "l", liter: "l", el: "el", essloeffel: "el", tl: "tl", teeloeffel: "tl", stk: "stk", stueck: "stk", x: "stk", scheibe: "scheibe", scheiben: "scheibe", dose: "dose", dosen: "dose", becher: "becher", packung: "packung", portion: "portion", portionen: "portion", messerspitzen: "prise", messerspitze: "prise", msp: "prise", prisen: "prise", prise: "prise", zehen: "stk", zehe: "stk", handvoll: "handvoll", tassen: "tasse", tasse: "tasse", glaeser: "glas", glas: "glas", bund: "bund", zweige: "zweig", zweig: "zweig" };
function cGrams(f, n, unit) {
  const per = f && f.per > 1 ? f.per : 0;
  switch (unit) {
    case "g": case "ml": return n; case "kg": case "l": return n * 1000;
    case "el": return n * (f && f.pu === "EL" ? f.per : f && f.pu === "TL" ? f.per * 3 : 15); case "tl": return n * (f && f.pu === "TL" ? f.per : 5);
    case "stk": return n * (per || (f && f.def) || 100); case "scheibe": return n * (f && f.pu === "Stk" ? f.per : 30);
    case "dose": return n * (f && ["kiche", "bohne"].includes(f.id) ? 240 : 400); case "becher": return n * 150; case "packung": return n * 250; case "portion": return n * ((f && f.def) || 150);
    case "prise": return n * 0.5; case "handvoll": return n * 30; case "tasse": return n * 250; case "glas": return n * 200; case "bund": return n * 30; case "zweig": return n * 3;
    default: return per && n < 20 ? n * per : n >= 10 ? n : n * ((f && f.def) || 100);
  }
}
/* Eier: Gewicht des essbaren Teils je Größe (ohne Schale) */
const EGGW = { s: 43, m: 51, l: 60, xl: 69 };
function eggSize(t) {
  const w = " " + t + " ";
  if (/ (?:xl|xxl) /.test(w)) return "xl";
  let m = w.match(/ (?:groesse|gr|size) (xl|s|m|l) /); if (m) return m[1];
  if (/ (?:klein|kleine|kleines|kleiner) /.test(w)) return "s";
  if (/ (?:mittel|mittlere|mittleres|mittelgrosse|mittelgrosses) /.test(w)) return "m";
  if (/ (?:gross|grosse|grosses|grosser) /.test(w)) return "l";
  m = w.match(/ (s|m|l) /); return m ? m[1] : null;
}
function cParse(text) {
  const pre = text.replace(/½/g, " 0.5 ").replace(/¼/g, " 0.25 ").replace(/(\d),(\d)/g, "$1.$2").replace(/(\d)\/(\d)/g, (m, a, b) => " " + (a / b) + " ");
  const segs = pre.split(/\n|;|\+|,|\s+und\s+|\s+plus\s+/i).map((x) => x.trim()).filter(Boolean).flatMap((x) => (cMatch(CDISHL, CNORM(x)) ? [x] : x.split(/\s+mit\s+/i).map((y) => y.trim()).filter(Boolean))).slice(0, 25);
  return segs.map((raw) => {
    let t = CNORM(raw), cooked = /gekocht/.test(t), fried = /gebraten|gegart|gegrillt|gebacken|angebraten/.test(t); t = t.replace(/gekochte[rnms]?|gekocht|gebratene[rnms]?|gebraten|gegarte[rnms]?|gegart|gegrillte[rnms]?|gegrillt|gebackene[rnms]?|angebratene[rnms]?/g, " ").replace(/\s+/g, " ").trim();
    let n = null, unit = "";
    const m = t.match(/(\d+(?:\.\d+)?|halbe[rsn]?|halb)\s*(kg|gramm|gr|g|ml|liter|l|el|essloeffel|tl|teeloeffel|stk|stueck|x|scheiben|scheibe|dosen|dose|becher|packung|portionen|portion|messerspitzen|messerspitze|msp|prisen|prise|zehen|zehe|handvoll|tassen|tasse|glaeser|glas|bund|zweige|zweig)?(?![a-z])/);
    if (m) { n = /^halb/.test(m[1]) ? 0.5 : parseFloat(m[1]); unit = CUNIT[m[2]] || ""; t = (t.slice(0, m.index) + " " + t.slice(m.index + m[0].length)).replace(/\s+/g, " ").trim(); }
    const mult = n != null && !unit ? n : 1, name = t || raw;
    const my = MYD.find((d) => t.includes(CNORM(d.name)));
    if (my) { const g = Math.min(20000, n == null ? my.lg : unit === "kg" ? n * 1000 : unit === "portion" || unit === "stk" || (!unit && n < 10) ? n * my.lg : n), f = g / my.w; return { raw, kind: "dish", name: my.name, qty: Math.round(g) + " g", k: my.k * f, p: my.p * f, c: my.c * f }; }
    const dish = cMatch(CDISHL, t);
    if (dish && (!n || !unit || unit === "stk" || unit === "portion")) return { raw, kind: "dish", name: dish.name, qty: Math.min(50, n != null ? n : 1) + " Portion" + (Math.min(50, n != null ? n : 1) === 1 ? "" : "en"), k: dish.kcal * Math.min(50, n != null ? n : 1), p: dish.p * Math.min(50, n != null ? n : 1), c: null };
    let f = cMatch(CFOODS, t) || cFuzzy(CFOODS, t);
    if (f && f.id === "nudel" && /weizen|\bhell|weiss|ohne vollkorn/.test(t)) f = CFOODS.find((x) => x.name.startsWith("Weizennudeln")) || f;
    if (!f) return { raw, kind: "unknown", name: raw, g: n != null ? Math.min(20000, Math.max(1, Math.round(cGrams(null, n, unit)))) : 100, k: null, p: null, c: null };
    let g = n == null ? f.def : cGrams(f, n, unit), note = "";
    if (f.id === "ei" && (!unit || unit === "stk")) { const sz = eggSize(t); if (sz) { g = (n == null ? 1 : n) * EGGW[sz]; note = "Größe " + sz.toUpperCase(); } else note = "als Größe M gerechnet"; }
    if (cooked && f.raw) { g *= 0.37; note = "gekocht gerechnet"; }
    else if ((cooked || fried) && ["haehn", "pute", "phack", "rhack", "ghack", "schnitzel"].includes(f.id)) { g *= 1.3; note = "gegart gerechnet, Fleisch verliert beim Garen Wasser"; }
    else if (["haehn", "pute", "phack", "rhack", "ghack", "schnitzel", "haehnst"].includes(f.id)) note = "als rohes Fleisch gerechnet";
    g = Math.min(20000, Math.round(g));
    return { raw, kind: "food", name: f.name, g, qty: g + " g", k: g * f.kcal / 100, p: g * f.p / 100, c: g * f.eur / 100, note, def: n == null };
  });
}
const CCATS = [["Gemüse", 30, 2], ["Obst", 55, 0.8], ["Fleisch oder Wurst", 230, 18], ["Brot, Reis oder Nudeln (gekocht)", 160, 5], ["Milchprodukt", 100, 6], ["Süßes oder Snack", 480, 6], ["Fertiggericht oder Suppe", 120, 5], ["Soße oder Fett", 350, 2]];
let CALC = { text: "", rows: null, man: {}, srv: 1, name: "", ai: false, busy: false, err: "" };
function cRowVals(r, i) {
  if (r.kind !== "unknown") return r;
  const m = CALC.man[i]; if (!m || !(m.k >= 0) || !(m.p >= 0) || m.k === "" || m.p === "") return r;
  return Object.assign({}, r, { kind: "manual", name: r.raw, qty: r.g + " g", note: m.cat ? "grob geschätzt als " + m.cat : "mit deinen Werten", k: r.g * m.k / 100, p: r.g * m.p / 100 });
}
function cTotals() {
  const rows = (CALC.rows || []).map(cRowVals), ok = rows.filter((r) => r.k != null);
  return { k: ok.reduce((a, r) => a + r.k, 0), p: ok.reduce((a, r) => a + r.p, 0), c: ok.every((r) => r.c != null) && ok.length ? ok.reduce((a, r) => a + r.c, 0) : null, open: rows.filter((r) => r.k == null).length, rows };
}
function calcHTML() {
  let out = "";
  if (CALC.err) out += '<p class="small warnt" role="status">' + CALC.err + "</p>";
  if (CALC.rows) {
    const T = cTotals(), per = Math.max(1, CALC.srv);
    out += '<ul class="calcrows">' + T.rows.map((r, i) => {
      if (r.kind === "unknown") return '<li class="cunk"><div><b>' + esc(r.raw) + '</b><span class="muted small"> kenne ich nicht. Wähle, was es am ehesten ist, dann schätze ich für ' + r.g + ' g. Die Menge änderst du, indem du sie vor den Namen schreibst, zum Beispiel „300 g Auflauf“.</span></div><div class="row cats">' + CCATS.map((c) => '<button class="btn sm" type="button" data-calccat="' + i + '" data-c="' + c[0] + '">' + c[0] + "</button>").join("") + '</div><details><summary class="small muted">Oder Werte selbst eintragen</summary><div class="row"><label class="field sm">kcal<input type="number" class="calcman" data-i="' + i + '" data-f="k" min="0" max="900" inputmode="decimal"></label><label class="field sm">Eiweiß g<input type="number" class="calcman" data-i="' + i + '" data-f="p" min="0" max="100" inputmode="decimal"></label></div></details></li>';
      return "<li><div><b>" + esc(r.name) + '</b><span class="muted small"> ' + esc(r.qty || "") + (r.note ? ", " + esc(r.note) : "") + (r.def ? " (Standardmenge, ändere sie oben)" : "") + '</span></div><span class="small">' + Math.round(r.k) + " kcal, " + (Math.round(r.p * 10) / 10).toLocaleString("de-DE") + " g Eiweiß" + (r.c != null ? ", ca. " + eur(r.c) : "") + "</span></li>";
    }).join("") + "</ul>";
    if (CALC.rows.some((r) => r.kind === "unknown")) out += '<div class="row"><button class="btn" type="button" data-calcre="1">Eigene Werte übernehmen</button></div>';
    out += '<div class="calctot"><b>Zusammen: ' + Math.round(T.k) + " kcal, " + (Math.round(T.p * 10) / 10).toLocaleString("de-DE") + " g Eiweiß" + (T.c != null ? ", ca. " + eur(T.c) + " bei Lidl" : "") + "</b>" + (T.open ? '<span class="small muted"> ohne ' + T.open + " nicht erkannte Zutat" + (T.open > 1 ? "en" : "") + "</span>" : "") + "</div>" +
      '<div class="row"><label class="field sm">Aufgeteilt auf Personen<input type="number" id="calc-srv" min="1" max="8" value="' + CALC.srv + '" inputmode="numeric"></label><label class="field">Name im Tagebuch<input type="text" id="calc-name" maxlength="60" value="' + esc(CALC.name) + '"></label></div>' +
      (per > 1 ? '<p class="small">Für dich: ' + Math.round(T.k / per) + " kcal, " + (Math.round(T.p / per * 10) / 10).toLocaleString("de-DE") + " g Eiweiß</p>" : "") +
      '<div class="row"><button class="btn primary" type="button" data-calcadd="1">Heute eintragen</button></div>' +
      '<details class="mydsave"><summary>Als Gericht speichern, um später nur Gramm einzugeben</summary><div class="row"><label class="field">Name<input type="text" id="myd-name" maxlength="60" value="' + esc(CALC.name) + '"></label><label class="field sm">Fertig gewogen (g)<input type="number" id="myd-w" min="50" max="20000" inputmode="numeric" placeholder="leer = Schätzung"></label></div><p class="small muted">Wiege das fertige Gericht, wenn du kannst. Ohne Angabe schätze ich das Gewicht nach dem Kochen, das ist ungenauer.</p><div class="row"><button class="btn" type="button" data-mydsave="1">Gericht speichern</button></div></details><p class="small muted">Richtwerte. Reis, Nudeln und Linsen gelten als Rohgewicht, außer du schreibst „gekocht“.</p>';
  }
  return '<h4 id="calc-sec">Selbst berechnen</h4><p class="small muted">Schreib Zutaten mit Menge oder ein Gericht, zum Beispiel „200 g Hähnchen, 150 g Reis, 1 Paprika“ oder „Döner“.</p>' +
    '<label class="field">Name des Gerichts (optional)<input type="text" id="calc-name0" maxlength="60" value="' + esc(CALC.name) + '" placeholder="z. B. Spaghetti Bolognese"></label><label class="field">Zutaten mit Mengen<textarea id="calc-in" rows="3" maxlength="400" placeholder="200 g Hähnchen, 150 g Reis, 1 Paprika">' + esc(CALC.text) + "</textarea></label>" +
    '<div class="row"><button class="btn primary" type="button" data-calcgo="1">Berechnen</button></div>' + out;
}
function calcGo() { CALC.text = ($("#calc-in") || {}).value || CALC.text; const nm = (($("#calc-name0") || {}).value || "").trim(); CALC.rows = cParse(CALC.text); CALC.man = {}; CALC.err = ""; CALC.ai = false; CALC.srv = 1; CALC.name = nm || CALC.text.split(/[\n,;]/)[0].slice(0, 40).trim(); drawEat(); }
function calcRead() { $$(".calcman").forEach((el) => { const i = el.dataset.i; CALC.man[i] = CALC.man[i] || {}; CALC.man[i][el.dataset.f] = el.value === "" ? "" : parseFloat(el.value); }); }
function calcAdd() {
  const T = cTotals(), srv = Math.max(1, Math.min(8, parseInt(($("#calc-srv") || {}).value, 10) || 1)), name = ((($("#calc-name") || {}).value) || CALC.name || "Eigenes Gericht").trim() || "Eigenes Gericht";
  CALC.srv = srv; if (!T.rows.some((r) => r.k != null)) return;
  dayEns().items.push({ t: name + (srv > 1 ? " (1 von " + srv + ")" : ""), k: Math.round(T.k / srv), p: Math.round(T.p / srv), c: T.c != null ? Math.round(T.c / srv * 100) / 100 : 0, det: T.rows.filter((r) => r.k != null).map((r) => (r.qty ? r.qty + " " : "") + (r.name || r.raw) + ": " + Math.round(r.k) + " kcal, " + (Math.round(r.p * 10) / 10).toLocaleString("de-DE") + " g Eiweiß").slice(0, 25).concat(srv > 1 ? ["Aufgeteilt auf " + srv + " Personen, gesamt " + Math.round(T.k) + " kcal"] : []) });
  saveToday(); renderToday(); const ok = name; CALC = { text: "", rows: null, man: {}, srv: 1, name: "", ai: false, busy: false, err: "" }; drawEat("Eingetragen: " + ok);
}


/* Eigene Gerichte: einmal Zutaten eingeben, danach nur noch die gegessenen Gramm */
const mydSave = () => store.set("fc_dishes", MYD);
function mydWeight(rows) {
  return rows.reduce((a, r) => { if (r.g == null) return a; const raw = /Rohgewicht/.test(r.name || "") || r.note === "gekocht gerechnet"; const meat = /Hähnchen|Pute|hack|Hack|Schnitzel|Rind|Schwein|Bacon|Kassler/.test(r.name || ""); return a + r.g * (raw && r.note !== "gekocht gerechnet" ? 2.4 : meat ? 0.75 : 0.88); }, 0);
}
function mydHTML() {
  const list = MYD.length ? '<ul class="calcrows">' + MYD.map((d, i) => { const f = (d.lg || 250) / d.w; return '<li class="mydli"><div><b>' + esc(d.name) + '</b><span class="muted small"> pro 100 g: ' + Math.round(d.k / d.w * 100) + " kcal, " + (Math.round(d.p / d.w * 1000) / 10).toLocaleString("de-DE") + " g Eiweiß. Gericht wiegt fertig " + Math.round(d.w) + " g" + (d.est ? " (geschätzt)" : "") + '</span></div><div class="row mydrow"><label class="field sm">Gegessen (g)<input type="number" class="myd-g" data-i="' + i + '" min="1" max="3000" value="' + (d.lg || 250) + '" inputmode="numeric"></label><span class="small" id="mydv' + i + '">= ' + Math.round(d.k * f) + " kcal, " + (Math.round(d.p * f * 10) / 10).toLocaleString("de-DE") + ' g Eiweiß</span></div><div class="row"><button class="btn primary" type="button" data-mydeat="' + i + '">Eintragen</button><button class="btn sm" type="button" data-mydel="' + i + '" aria-label="' + esc(d.name) + ' löschen">Löschen</button></div></li>'; }).join("") + "</ul>" : '<p class="small muted">Noch nichts gespeichert. Gib unten Zutaten ein, rechne sie aus und speichere sie als Gericht.</p>';
  return '<h4 id="myd-sec">Meine Gerichte</h4><p class="small muted">Gespeicherte Gerichte trägst du mit einer Mengenangabe ein, zum Beispiel 250 g vom Teller.</p>' + list;
}
function mydFromInput(i) { const d = MYD[i]; if (!d) return; const el = document.querySelector('.myd-g[data-i="' + i + '"]'), g = Math.max(1, Math.min(3000, parseFloat(el.value) || 0)), f = g / d.w; d.lg = g; const o = document.getElementById("mydv" + i); if (o) o.textContent = "= " + Math.round(d.k * f) + " kcal, " + (Math.round(d.p * f * 10) / 10).toLocaleString("de-DE") + " g Eiweiß"; }
function mydEat(i) {
  const d = MYD[i]; if (!d) return; mydFromInput(i); const g = d.lg, f = g / d.w;
  dayEns().items.push({ t: d.name + " (" + Math.round(g) + " g)", k: Math.round(d.k * f), p: Math.round(d.p * f), c: Math.round(d.c * f * 100) / 100, det: ["Gespeichertes Gericht: " + Math.round(g) + " g von " + Math.round(d.w) + " g" + (d.est ? " (Gewicht geschätzt)" : "")].concat(d.text ? ["Zutaten: " + d.text.replace(/\s+/g, " ")] : []) });
  mydSave(); saveToday(); renderToday(); drawEat("Eingetragen: " + d.name + ", " + Math.round(g) + " g");
}
function mydNew() {
  const T = cTotals(), name = (($("#myd-name") || {}).value || CALC.name || "").trim();
  if (!CALC.rows || T.open) { CALC.err = "Zum Speichern müssen alle Zutaten erkannt sein. Wähle bei den unbekannten eine Kategorie."; return drawEat(); }
  if (!name) { CALC.err = "Gib dem Gericht einen Namen."; return drawEat(); }
  const wIn = parseFloat(($("#myd-w") || {}).value), est = !(wIn > 0), w = est ? Math.max(50, Math.round(mydWeight(T.rows))) : wIn;
  const d = { id: String(Date.now()), name: name.slice(0, 60), k: T.k, p: T.p, c: T.c || 0, w, est, lg: 250, text: CALC.text.slice(0, 400) };
  const ix = MYD.findIndex((x) => CNORM(x.name) === CNORM(d.name)); if (ix >= 0) MYD[ix] = d; else MYD.unshift(d);
  MYD = MYD.slice(0, 60); mydSave(); CALC = { text: "", rows: null, man: {}, srv: 1, name: "", ai: false, busy: false, err: "" }; drawEat("Gespeichert: " + d.name + (est ? ". Das fertige Gewicht ist geschätzt, wiege das Gericht einmal für genauere Werte." : "."));
}

/* Essen eintragen */
let EATQ = "", RECENT = [];
function recentEaten() {
  const out = [], seen = new Set();
  Object.keys(DIARY).sort().reverse().slice(0, 21).forEach((d) => DIARY[d].items.slice().reverse().forEach((x) => { if (out.length < 6 && !seen.has(x.t)) { seen.add(x.t); out.push(x); } }));
  return out;
}
function drawEat(msg) {
  RECENT = recentEaten();
  const q = EATQ.trim().toLowerCase();
  const l = q ? RECIPES.filter((r) => (r.title + " " + r.ing.map((i) => i[2]).join(" ")).toLowerCase().includes(q)).slice(0, 8) : suggestList(8);
  $("#dlg-eat").innerHTML = '<div class="dlg"><div class="dlg-head"><h3>Essen eintragen</h3><button class="btn icon" data-close aria-label="Schließen">' + ic("close") + "</button></div>" +
    '<div class="search">' + ic("search") + '<input type="search" id="eatq" placeholder="Rezept suchen, z. B. Quark" value="' + EATQ.replace(/"/g, "&quot;") + '" aria-label="Rezept suchen"></div>' +
    (RECENT.length ? '<div class="recent"><span class="small muted">Zuletzt gegessen, ein Tipp trägt es nochmal ein:</span><div class="row recentrow">' + RECENT.map((x, i) => '<button class="fchip" type="button" data-eatagain="' + i + '">' + esc(x.t.length > 28 ? x.t.slice(0, 26) + "…" : x.t) + " · " + x.k + " kcal</button>").join("") + "</div></div>" : "") +
    '<div class="row eatjump"><button class="btn sm" type="button" data-eatjump="calc-sec">Selbst berechnen</button><button class="btn sm" type="button" data-eatjump="myd-sec">Meine Gerichte' + (MYD.length ? " (" + MYD.length + ")" : "") + '</button></div><p class="small muted" role="status">' + esc(msg || (q ? l.length + " Treffer" : "Vorschläge für heute")) + "</p>" +
    '<ul class="eatlist">' + (l.length ? l.map((r) => "<li><div><b>" + r.title + '</b><span class="muted small">' + r.protein + " g Eiweiß, " + r.kcal + " kcal, ca. " + eur(r.cost) + '</span></div><button class="btn sm" data-eat="' + r.id + '">Eintragen</button></li>').join("") : '<li class="muted">Kein Rezept gefunden. Trag es unten selbst ein.</li>') + "</ul>" +
    mydHTML() + calcHTML() + '<h4>Etwas anderes gegessen?</h4><form id="eatform" class="form"><label class="field">Name<input type="text" id="e-name" maxlength="60" required></label><label class="field">kcal<input type="number" id="e-k" min="0" max="3000" inputmode="numeric" required></label><label class="field">Eiweiß in g<input type="number" id="e-p" min="0" max="300" inputmode="numeric" required></label><button class="btn primary" type="submit">Eintragen</button></form></div>';
}
function openEat() { EATQ = ""; drawEat(); showDialog($("#dlg-eat"), $('[data-eatopen]')); }

/* Protokoll und Vorschlag für die nächste Stufe (Doppelte Progression wie in der r/bodyweightfitness Recommended Routine) */
const repRange = (e) => { const m = (e.reps || "").match(/(\d+)\D+(\d+)/); return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null; };
function repChips(e) {
  const r = repRange(e); if (!r) return "";
  let h = "";
  for (let n = Math.max(1, r[0] - 3); n <= r[1] + 2; n++) h += '<button class="fchip" data-reps="' + n + '">' + n + "</button>";
  return '<div class="repchips" role="group" aria-label="Wiederholungen eintragen"><span class="small muted">Wie viele hast du geschafft?</span><div class="row">' + h + "</div></div>";
}
const exOf = (w) => EXALL.filter((e) => w.sets.some((x) => x.ex === e.id));
function evalEx(e, sets) {
  const mine = sets.filter((s) => s.ex === e.id);
  if (!mine.length) return null;
  if (e.type === "hold") { const v = mine.map((s) => s.secs || 0); return { vals: v.map((x) => x + " s"), best: Math.max(...v), status: v.every((x) => x >= 30) ? "up" : "ok", unit: "s" }; }
  const r = repRange(e), reps = mine.map((s) => s.reps);
  if (reps.some((x) => x == null)) return { vals: reps.map((x) => (x == null ? "?" : x)), best: Math.max(0, ...reps.filter((x) => x != null)), status: "none", unit: "" };
  return { vals: reps, best: Math.max(...reps), status: reps.every((x) => x >= r[1]) ? "up" : reps.some((x) => x < r[0]) ? "low" : "ok", unit: "" };
}
function prevBest(e, lv, before) {
  let b = 0;
  WK.slice(0, before).forEach((w) => w.sets.forEach((s) => { if (s.ex === e.id && s.lvl === lv) b = Math.max(b, e.type === "hold" ? (s.secs || 0) : (s.reps || 0)); }));
  return b;
}
function drawSummary(idx) {
  const w = WK[idx]; if (!w) return;
  const rows = exOf(w).map((e) => {
    const ev = evalEx(e, w.sets); if (!ev) return "";
    if (w.q && ev.status === "up") ev.status = "ok";
    const lv = (w.sets.find((s) => s.ex === e.id) || {}).lvl, r = repRange(e), pb = prevBest(e, lv, idx);
    const nxt = e.ladder[lv + 1], now = lvl(e);
    let msg = "", btn = "";
    if (ev.status === "up") {
      if (nxt) { msg = "Du bist in allen Sätzen oben im Bereich. Bereit für die nächste Stufe: <b>" + nxt + "</b>."; btn = now === lv ? '<button class="btn sm primary" data-lvlup="' + e.id + '">Stufe hoch</button>' : '<span class="tag g">Stufe geändert</span>'; }
      else msg = "Du bist auf der höchsten Stufe. Steigere Wiederholungen und Kontrolle.";
    } else if (ev.status === "low") {
      msg = "Ein Satz lag unter " + r[0] + " Wiederholungen. Bleib auf dieser Stufe oder geh eine Stufe zurück, wenn es sich nicht sauber anfühlt.";
      btn = lv > 0 && now === lv ? '<button class="btn sm" data-lvldown="' + e.id + '">Leichter</button>' : "";
    } else if (ev.status === "ok") msg = e.type === "hold" ? "Ziel: in allen Sätzen 30 Sekunden halten, dann geht es eine Stufe hoch." : "Ziel: " + r[1] + " Wiederholungen in allen Sätzen, dann geht es eine Stufe hoch.";
    else msg = "Trag nächstes Mal deine Wiederholungen ein, dann schlage ich dir die nächste Stufe vor.";
    const pr = ev.best > 0 && pb > 0 && ev.best > pb ? '<span class="tag g">Neuer Rekord: ' + ev.best + ev.unit + " statt " + pb + ev.unit + "</span>" : (pb === 0 && ev.best > 0 ? '<span class="tag">Erster Eintrag</span>' : "");
    return '<div class="sumrow"><div class="sumh"><div><b>' + e.name + '</b><span class="muted small">' + e.ladder[lv] + "</span></div><div class=\"sumvals\">" + ev.vals.join(", ") + "</div></div><p class=\"small\">" + msg + "</p><div class=\"row\">" + pr + btn + "</div></div>";
  }).join("");
  const eff = [["leicht", "Eher leicht"], ["genau", "Genau richtig"], ["schwer", "Eher schwer"]].map((x) => '<button class="fchip" data-effort="' + x[0] + '" aria-pressed="' + (w.effort === x[0]) + '">' + x[1] + "</button>").join("");
  const hint = w.effort === "leicht" ? "Wenn es sich leicht anfühlte, gehst du eine Stufe hoch, sobald du oben im Bereich bist." : w.effort === "schwer" ? "Wenn es zu schwer war, geh bei der härtesten Übung eine Stufe zurück und gönn dir einen Tag mehr Pause." : "";
  $("#dlg-sum").innerHTML = '<div class="dlg"><div class="dlg-head"><div><h3>Training geschafft</h3><p class="muted">' + w.sets.length + " Sätze in etwa " + esc(w.min) + ' Minuten. Dehne jetzt noch kurz Brust, Oberschenkel und Rücken.</p></div><button class="btn icon" data-close aria-label="Schließen">' + ic("close") + "</button></div>" + rows +
    '<div><p><b>Wie fühlte sich das Training an?</b></p><div class="row">' + eff + "</div>" + (hint ? '<p class="small muted">' + hint + "</p>" : "") + "</div>" +
    '<div class="row"><button class="btn primary" data-close>Fertig</button></div></div>';
}
function openSummary(idx) { SUMIDX = idx; drawSummary(idx); showDialog($("#dlg-sum"), null); }

/* Diagramme */
function ema(pts) {
  let t = null, prev = 0;
  return pts.map((p) => { if (t == null) t = p.y; else t = t + (1 - Math.exp(-((p.ms - prev) / 86400000) / 7)) * (p.y - t); prev = p.ms; return { ms: p.ms, y: p.y, t }; });
}
function chartSVG(pts, label, trend) {
  if (pts.length < 2) return '<p class="muted">Trag an mindestens zwei Tagen ' + label + " ein, dann erscheint hier der Verlauf.</p>";
  const W2 = 640, H2 = 230, L = 46, R = 14, T = 12, B = 28;
  const vals = pts.flatMap((p) => (trend ? [p.y, p.t] : [p.y]));
  let lo = Math.min(...vals), hi = Math.max(...vals); const pad = Math.max(0.6, (hi - lo) * 0.25); lo -= pad; hi += pad;
  const x0 = pts[0].ms, x1 = pts[pts.length - 1].ms;
  const X = (ms) => L + (x1 === x0 ? 0.5 : (ms - x0) / (x1 - x0)) * (W2 - L - R), Y = (v) => T + (1 - (v - lo) / (hi - lo)) * (H2 - T - B);
  let g = "";
  for (let i = 0; i <= 3; i++) { const v = lo + (hi - lo) * i / 3, y = Y(v); g += '<line class="gl2" x1="' + L + '" x2="' + (W2 - R) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '"/><text x="' + (L - 8) + '" y="' + (y + 4).toFixed(1) + '" text-anchor="end">' + nf(Math.round(v * 10) / 10) + "</text>"; }
  const d1 = isoOf(new Date(x0)), d2 = isoOf(new Date(x1));
  g += '<text x="' + L + '" y="' + (H2 - 8) + '">' + dateDE(d1) + '</text><text x="' + (W2 - R) + '" y="' + (H2 - 8) + '" text-anchor="end">' + dateDE(d2) + "</text>";
  const line = (key, cls) => '<polyline class="' + cls + '" points="' + pts.map((p) => X(p.ms).toFixed(1) + "," + Y(p[key]).toFixed(1)).join(" ") + '"/>';
  const dots = pts.map((p) => '<circle class="dt" cx="' + X(p.ms).toFixed(1) + '" cy="' + Y(p.y).toFixed(1) + '" r="3.5"/>').join("");
  return '<svg viewBox="0 0 ' + W2 + " " + H2 + '" class="chart" role="img" aria-label="Verlauf ' + label + '">' + g + (trend ? dots + line("t", "tr") : line("y", "ln") + dots) + "</svg>";
}
function trendInfo() {
  const pts = ema(log.filter((x) => x.weight != null).map((x) => ({ ms: new Date(x.date + "T12:00:00").getTime(), y: x.weight })));
  if (!pts.length) return null;
  const last = pts[pts.length - 1];
  const old = pts.filter((p) => p.ms <= last.ms - 7 * 86400000).pop();
  return { pts, now: last.t, week: old ? last.t - old.t : null };
}
/* Auswertung: Gewichtstrend gegen Essen der letzten 28 Tage */
function coachEval() {
  const t = todayISO(), from = shiftDay(t, -27);
  const wp = log.filter((x) => typeof x.weight === "number" && x.date >= from && x.date <= t).map((x) => ({ d: new Date(x.date + "T12:00:00").getTime() / 86400000, y: x.weight, date: x.date })).sort((a, b) => a.d - b.d);
  const eaten = []; for (let i = 0; i < 28; i++) { const d = shiftDay(from, i), e = dsum(d); if (e.k >= 1000) eaten.push(e); }
  const out = { weights: wp.length, span: wp.length > 1 ? Math.round(wp[wp.length - 1].d - wp[0].d) : 0, eatenDays: eaten.length };
  if (wp.length < 4 || out.span < 14 || eaten.length < 10) return out;
  const n = wp.length, mx = wp.reduce((a, p) => a + p.d, 0) / n, my = wp.reduce((a, p) => a + p.y, 0) / n;
  const sxx = wp.reduce((a, p) => a + (p.d - mx) * (p.d - mx), 0), sxy = wp.reduce((a, p) => a + (p.d - mx) * (p.y - my), 0);
  const perDay = sxx > 0 ? sxy / sxx : 0;
  out.rate = perDay * 7; out.intake = eaten.reduce((a, e) => a + e.k, 0) / eaten.length; out.prot = eaten.reduce((a, e) => a + e.p, 0) / eaten.length;
  out.tdee = out.intake - perDay * 7700;
  return out;
}
function coachEvalHTML() {
  const ev = coachEval(), b = bodyCalc(), head = '<div class="card coacheval"><div class="rday-h"><h3>Auswertung der letzten 4 Wochen</h3></div>';
  if (ev.rate == null) return head + '<p class="muted">Noch zu wenig Daten für eine Einschätzung. Ich brauche mindestens 4 Gewichtswerte über 2 Wochen und 10 Tage mit eingetragenem Essen. Bisher: ' + ev.weights + " Gewichtswerte, " + ev.eatenDays + " Tage mit Essen.</p></div>";
  const lo = b.lossLo, hi = b.lossHi, rate = ev.rate, kcal = GOALS.kcal, floor = Math.max(1600, Math.round(prof.weight * 22));
  const sign = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + nf(Math.abs(Math.round(v * 100) / 100));
  let verdict, sugg = null, lowering = false;
  const target = Math.max(0.3, lo);
  const raw = ev.tdee - target * 1100;
  const clampK = (v) => Math.max(floor, Math.min(kcal + 200, Math.max(kcal - 200, Math.round(v / 50) * 50)));
  if (rate <= -hi * 1.15) { verdict = "Du verlierst schneller als empfohlen (bis " + nf(hi) + " kg pro Woche). Das kostet auf Dauer Muskeln. Iss etwas mehr."; sugg = clampK(Math.max(raw, kcal + 150)); }
  else if (rate < -lo * 0.6) verdict = "Das Tempo passt gut. Bleib bei deinem Kalorienziel.";
  else if (rate < 0.1) { verdict = "Dein Gewicht bleibt etwa gleich. Beim Muskelaufbau kann das trotzdem Fortschritt sein, schau auch auf Taille und Wiederholungen. Willst du abnehmen, hilft ein kleiner Schritt nach unten."; sugg = clampK(raw); lowering = true; }
  else { verdict = "Dein Gewicht steigt. Zum Abnehmen liegt dein Essen über deinem Verbrauch."; sugg = clampK(raw); lowering = true; }
  if (lowering && sugg != null && (sugg >= kcal || kcal <= floor + 50)) { sugg = null; verdict += " Dein Ziel liegt schon nah an der Untergrenze, senke es nicht weiter. Mehr Bewegung ist dann der bessere Hebel."; }
  if (sugg != null && Math.abs(sugg - kcal) < 50) sugg = null;
  const pg = protGoal(), pnote = ev.prot < pg * 0.9 ? " Dein Eiweiß liegt im Schnitt bei " + Math.round(ev.prot) + " g, dein Ziel ist " + pg + " g." : "";
  return head + '<ul class="ptable cev"><li><span>Gewichtstrend</span><b>' + sign(rate) + " kg pro Woche</b></li><li><span>Ø gegessen</span><b>" + Math.round(ev.intake).toLocaleString("de-DE") + " kcal, " + Math.round(ev.prot) + " g Eiweiß</b></li><li><span>Geschätzter Verbrauch</span><b>ca. " + (Math.round(ev.tdee / 50) * 50).toLocaleString("de-DE") + " kcal</b></li><li><span>Dein Kalorienziel</span><b>" + kcal.toLocaleString("de-DE") + " kcal</b></li></ul>" +
    "<p>" + verdict + pnote + "</p>" +
    (sugg != null ? '<div class="row"><button class="btn primary" type="button" data-setkcal="' + sugg + '">Ziel auf ' + sugg.toLocaleString("de-DE") + " kcal setzen</button></div>" : "") +
    '<p class="small muted">Das ist eine Schätzung aus ' + ev.weights + " Gewichtswerten und " + ev.eatenDays + " von 28 Tagen mit Essen. Fehlende Tage machen sie ungenauer. Wasser und Salz verschieben das Gewicht um 1 bis 2 kg, entscheidend ist der Verlauf über Wochen. Das ersetzt keine ärztliche Beratung.</p></div>";
}
let PERF = "";
function perfHTML() {
  const have = EX.filter((e) => WK.some((w) => w.sets.some((x) => x.ex === e.id)));
  if (!have.length) return "";
  if (!have.some((e) => e.id === PERF)) PERF = have[0].id;
  const e = have.find((x) => x.id === PERF);
  const rows = []; for (let i = WK.length - 1; i >= 0 && rows.length < 8; i--) {
    const w = WK[i], ev = evalEx(e, w.sets); if (!ev) continue;
    const lv = (w.sets.find((x) => x.ex === e.id) || {}).lvl, pb = prevBest(e, lv, i);
    rows.push('<li><b>' + esc(dateDE(w.date)) + '</b><span class="muted small">' + esc(e.ladder[lv] || "") + "</span><span>" + ev.vals.join(" / ") + (ev.best > 0 && pb > 0 && ev.best > pb ? ' <span class="tag g">Rekord</span>' : "") + "</span></li>");
  }
  const chips = have.map((x) => '<button class="fchip" type="button" data-perf="' + x.id + '" aria-pressed="' + (x.id === PERF) + '">' + esc(x.name) + "</button>").join("");
  return '<div class="card"><div class="rday-h"><h3>Leistung pro Übung</h3></div><div class="row">' + chips + '</div><ul class="eatlist perf">' + rows.join("") + '</ul><p class="small muted">Die letzten Einheiten mit Stufe und Wiederholungen je Satz.</p></div>';
}
/* Eigene Preise: überschreiben die Lidl-Richtwerte, Rezeptkosten werden neu berechnet */
const CHEAPMAX = { "Frühstück": 1.0, "Mittag/Abend": 2.0, "Snack": 0.8 };
const PRICE0 = {}; Object.keys(PRICE).forEach((k) => { PRICE0[k] = PRICE[k].price; });
function applyPrices() {
  if (!settings.prices || typeof settings.prices !== "object" || Array.isArray(settings.prices)) settings.prices = {};
  Object.keys(settings.prices).forEach((k) => { const v = settings.prices[k]; if (!PRICE[k] || typeof v !== "number" || !isFinite(v) || v < 0.05 || v > 99.99) delete settings.prices[k]; });
  Object.keys(PRICE).forEach((k) => { PRICE[k].price = settings.prices[k] != null ? settings.prices[k] : PRICE0[k]; });
  RECIPES.forEach((r) => {
    let c = 0; r.ing.forEach((i) => { const k = i[4]; if (k && PRICE[k]) c += i[0] * PRICE[k].per * PRICE[k].price / PRICE[k].pack; });
    r.cost = Math.round(c * 100) / 100;
    r.tags = r.tags.filter((t) => t !== "Günstig"); if (r.cost <= CHEAPMAX[r.meal]) r.tags.push("Günstig");
  });
}
let PRICEOPEN = false;
function pricesHTML() {
  const secs = {}; Object.keys(PRICE).forEach((k) => { (secs[PRICE[k].sec] = secs[PRICE[k].sec] || []).push(k); });
  const changed = Object.keys(settings.prices).length;
  const body = SECS.filter((sc) => secs[sc]).map((sc) => "<h4>" + sc + "</h4>" + secs[sc].sort((a, b) => PRICE[a].n.localeCompare(PRICE[b].n, "de")).map((k) => {
    const pr = PRICE[k], mod = settings.prices[k] != null;
    return '<label class="prow' + (mod ? " mod" : "") + '"><span>' + esc(pr.n) + '<small class="muted"> ' + esc(pr.label) + (mod ? ", Richtwert " + eur(PRICE0[k]) : "") + '</small></span><input type="text" inputmode="decimal" autocomplete="off" data-price="' + k + '" value="' + (Math.round(pr.price * 100) / 100).toFixed(2).replace(".", ",") + '" aria-label="Preis ' + esc(pr.n) + ' in Euro"></label>';
  }).join("")).join("");
  return '<details class="card pricebox" id="pricebox" data-nofold' + (PRICEOPEN ? " open" : "") + '><summary>Meine Preise' + (changed ? " (" + changed + " angepasst)" : "") + '</summary><p class="small muted">Trag den Preis pro Packung ein, den du wirklich zahlst. Kosten der Rezepte und die Einkaufsliste rechnen damit. Leeres Feld oder der Richtwert setzt zurück.</p>' + body + '<div class="row"><button class="btn sm" type="button" data-pricereset="1">Alle auf Richtwerte zurück</button></div></details>';
}
/* Ausgaben fürs Essen: echte Einkäufe und das, was nach Preisliste gegessen wurde */
let SPM = "";
const MONN = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
const monthShift = (ym, k) => { const y = parseInt(ym.slice(0, 4), 10), m = parseInt(ym.slice(5, 7), 10) - 1 + k, d = new Date(y, m, 1); return d.getFullYear() + "-" + _p2(d.getMonth() + 1); };
function spendMonth(ym) {
  const buys = GOALS.buys.filter((b) => b.d.slice(0, 7) === ym);
  let eaten = 0, days = 0;
  Object.keys(DIARY).forEach((d) => { if (d.slice(0, 7) !== ym) return; const e = dsum(d); if (DIARY[d].items.length) { eaten += e.c; days++; } });
  return { buys, bought: buys.reduce((a, b) => a + b.a, 0), eaten, days };
}
let ESTOPEN = false;
document.addEventListener("toggle", (ev) => { if (ev.target && ev.target.id === "estbox") ESTOPEN = ev.target.open; }, true);
/* Ausgaben schätzen: Packungen statt Gramm. Offene Packungen werden erst aufgebraucht, solange sie haltbar sind. */
const BUYWIN = { quark: 4, skyr: 4, speisequark: 4, jog35: 4, jogGr: 5, moz: 4, schink: 3, paufs: 3, lyoner: 4, ruc: 3, eisb: 5, milch: 6, haehn: 14, pute: 14, schnitzel: 14, ghack: 14, rhack: 14, phack: 14, haehnst: 14, stueck: 4, kiche: 4, bohne: 4, kokos: 4, ei: 21, gouda: 21, parm: 60, butter: 30, tom: 7, gurke: 7, pap: 8, zwie: 14, karo: 14, banane: 5, brot: 14, wrap: 10, broetchen: 2, sgurke: 30, knob: 14, spin: 60, erdb: 60 };
const buyWin = (k) => (BUYWIN[k] != null ? BUYWIN[k] : PRICE[k].sec === "Nudeln, Reis & Trockenes" ? 120 : 14);
const hhOf = (r) => (r.meal === "Mittag/Abend" ? GOALS.hh : 1);
function buyEstimate() {
  const days = Object.keys(DIARY).filter((d) => DIARY[d] && Array.isArray(DIARY[d].items) && DIARY[d].items.length).sort();
  const open = {}, packs = [], other = [];
  days.forEach((d) => {
    const need = {};
    DIARY[d].items.forEach((it) => {
      const r = it.id ? byId(it.id) : null;
      if (!r) { if (it.c > 0) other.push({ d, c: it.c, t: it.t }); return; }
      const m = /×(\d+)$/.exec(it.t || ""), n = typeof it.n === "number" && it.n > 0 ? it.n : m ? parseInt(m[1], 10) : 1;
      r.ing.forEach((i) => { const k = i[4]; if (!k || !PRICE[k] || i[0] == null || PRICE[k].staple) return; need[k] = (need[k] || 0) + i[0] * PRICE[k].per * n * hhOf(r); });
    });
    Object.keys(need).forEach((k) => {
      const p = PRICE[k]; let g = need[k];
      if (p.loose) { packs.push({ d, k, loose: true, n: 0, cost: g / 1000 * p.price, uses: [{ d, g }], left: 0 }); return; }
      const o = open[k];
      if (o && o.left > 1e-6 && d <= shiftDay(o.d, buyWin(k))) { const t = Math.min(o.left, g); o.left -= t; g -= t; o.uses.push({ d, g: t }); }
      if (g > 1e-6) { const n = Math.ceil(g / p.pack - 1e-9), pk = { d, k, n, cost: n * p.price, uses: [{ d, g }], left: n * p.pack - g }; packs.push(pk); open[k] = pk; }
    });
  });
  return { packs, other };
}
function estRange(a, b) {
  const E = buyEstimate();
  return E.packs.filter((x) => x.d >= a && x.d <= b).reduce((s, x) => s + x.cost, 0) + E.other.filter((x) => x.d >= a && x.d <= b).reduce((s, x) => s + x.c, 0);
}
function fmtAmt(k, g) {
  const p = PRICE[k];
  if (p.u === "g" || p.u === "ml") return g >= 1000 ? nf(Math.round(g / 100) / 10) + (p.u === "g" ? " kg" : " l") : Math.max(5, Math.round(g / 5) * 5) + " " + p.u;
  const q = Math.round(g / p.per * 10) / 10;
  return nf(q) + " " + (q > 1 && p.pl ? p.pl : p.n);
}
function spendEstHTML(ym) {
  const E = buyEstimate(), t = todayISO(), mp = E.packs.filter((x) => x.d.slice(0, 7) === ym), mo = E.other.filter((x) => x.d.slice(0, 7) === ym);
  const real = mp.filter((x) => !x.loose), loose = mp.filter((x) => x.loose);
  const total = mp.reduce((s, x) => s + x.cost, 0) + mo.reduce((s, x) => s + x.c, 0), nPacks = real.reduce((s, x) => s + x.n, 0);
  const waste = real.filter((x) => x.left > 0.2 * PRICE[x.k].pack && shiftDay(x.d, buyWin(x.k)) < t).map((x) => ({ k: x.k, left: x.left, val: x.left / PRICE[x.k].pack * PRICE[x.k].price }));
  const wasteSum = waste.reduce((s, x) => s + x.val, 0);
  const row = (x) => {
    const p = PRICE[x.k], multi = x.uses.length > 1;
    return "<li><span><b>" + esc(p.n) + "</b> · " + (x.n > 1 ? x.n + " × " : "1 × ") + esc(p.label) + '<br><span class="small muted">' + x.uses.map((u) => wdShort(u.d) + " " + dateDE(u.d) + " " + fmtAmt(x.k, u.g)).join(" + ") + (multi ? ", zusammen " + (x.n > 1 ? x.n + " Packungen" : "1 Packung") : "") + "</span></span><b>" + eur(x.cost) + "</b></li>";
  };
  const list = real.slice().reverse().slice(0, 40).map(row).join("");
  const looseSum = loose.reduce((s, x) => s + x.cost, 0), looseNames = [...new Set(loose.map((x) => PRICE[x.k].n))].join(", ");
  const otherSum = mo.reduce((s, x) => s + x.c, 0);
  const hh = GOALS.hh;
  const seg = '<div class="hhseg"><span class="small muted">Hauptgerichte koche ich für</span><div class="row">' + [1, 2, 3, 4].map((n) => '<button class="btn sm" type="button" data-hh="' + n + '" aria-pressed="' + (hh === n) + '">' + n + "</button>").join("") + '<span class="small muted">' + (hh === 1 ? "Person" : "Personen") + "</span></div></div>";
  const body = mp.length || mo.length
    ? '<ul class="estlist">' + list + (looseSum ? "<li><span><b>Lose Ware</b><br><span class=\"small muted\">" + esc(looseNames) + "</span></span><b>" + eur(looseSum) + "</b></li>" : "") + (otherSum ? "<li><span><b>Weitere Einträge</b><br><span class=\"small muted\">Rechner und eigene Gerichte, nach Preisliste</span></span><b>" + eur(otherSum) + "</b></li>" : "") + "</ul>" +
      (waste.length ? '<p class="small"><b>Nicht mehr haltbar übrig geblieben:</b> ' + waste.slice(0, 6).map((x) => esc(PRICE[x.k].n) + " ca. " + fmtAmt(x.k, x.left)).join(", ") + " (zusammen ca. " + eur(wasteSum) + ").</p>" : '<p class="small muted">Es ist nichts Haltbares verfallen.</p>')
    : '<p class="small muted">Für diesen Monat sind noch keine Rezepte im Tagebuch.</p>';
  return { total, nPacks, wasteSum, has: mp.length + mo.length > 0, html:
    '<details class="exmore" id="estbox"' + (ESTOPEN ? " open" : "") + '><summary>So kommt die Schätzung zustande</summary><p class="small muted">Ich gehe dein Essens-Tagebuch durch und kaufe in Gedanken ganze Packungen. Was in einer geöffneten Packung noch haltbar ist, wird zuerst verbraucht. Ist es abgelaufen, zählt eine neue Packung. Bei Fleisch rechne ich mit Einfrieren (14 Tage). Öl, Gewürze und Co. sind nicht dabei. Es zählt nur, was du als Rezept eingetragen hast.</p>' + seg + body + "</details>" };
}
function spendHTML() {
  if (!/^\d{4}-\d{2}$/.test(SPM)) SPM = todayISO().slice(0, 7);
  const sp = spendMonth(SPM), cur = SPM === todayISO().slice(0, 7), es = spendEstHTML(SPM);
  const list = sp.buys.slice().reverse().map((b) => { const i = GOALS.buys.indexOf(b); return "<li><span>" + dateDE(b.d) + '</span><b>' + eur(b.a) + '</b><button class="btn icon sm" type="button" data-buydel="' + i + '" aria-label="Einkauf löschen">' + ic("close") + "</button></li>"; }).join("");
  const big = (v) => eur(v).replace(" €", "").replace(" €", "") + "<small>€</small>";
  return '<div class="card" data-nofold id="spendcard"><div class="rday-h"><h3>Ausgaben fürs Essen</h3><span class="row" style="gap:4px"><button class="btn icon sm" type="button" data-spm="-1" aria-label="Voriger Monat">‹</button><b>' + MONN[parseInt(SPM.slice(5, 7), 10) - 1] + " " + SPM.slice(0, 4) + '</b><button class="btn icon sm" type="button" data-spm="1" aria-label="Nächster Monat"' + (cur ? " disabled" : "") + ">›</button></span></div>" +
    '<div class="stats"><div class="stat"><span class="big">' + (es.has ? big(es.total) : "–") + "</span><span>" + (es.has ? "Einkauf geschätzt, " + es.nPacks + (es.nPacks === 1 ? " Packung" : " Packungen") : "Einkauf geschätzt, sobald Rezepte im Tagebuch stehen") + '</span></div><div class="stat"><span class="big">' + big(sp.eaten) + "</span><span>gegessen nach Preisliste" + (sp.days ? ", Ø " + eur(sp.eaten / sp.days) + " pro Tag" : "") + "</span></div></div>" +
    es.html +
    (list ? '<h4>Tatsächliche Einkäufe</h4><div class="stat inl"><span class="big">' + big(sp.bought) + "</span><span>eingetragen (" + sp.buys.length + (sp.buys.length === 1 ? " Einkauf" : " Einkäufe") + ')</span></div><ul class="eatlist buylist">' + list + "</ul>" : '<p class="muted small">Du kannst zusätzlich echte Einkäufe eintragen, zum Beispiel den Betrag vom Kassenbon. Nötig ist das nicht.</p>') +
    '<div class="row buyform"><label class="field">Betrag in €<input type="text" inputmode="decimal" id="buy-a" autocomplete="off" placeholder="z. B. 38,40"></label><label class="field">Datum<input type="date" id="buy-d" value="' + todayISO() + '" max="' + todayISO() + '"></label><button class="btn primary" type="button" data-buyadd="1">Eintragen</button></div><p class="small muted" id="buymsg" role="status" aria-live="polite"></p></div>';
}
/* Wochenrückblick: Montag bis Sonntag */
let REVW = "";
function weekReview(ws) {
  const days = [0, 1, 2, 3, 4, 5, 6].map((i) => shiftDay(ws, i)), we = days[6], t = todayISO();
  const past = days.filter((d) => d <= t);
  const trained = sessions.filter((d) => d >= ws && d <= we).length;
  const eaten = past.map((d) => ({ d, e: dsum(d) })).filter((x) => x.e.k >= 1000);
  const water = past.filter((d) => dayGet(d).water >= GOALS.water).length;
  const wl = log.filter((x) => typeof x.weight === "number").sort((a, b) => (a.date < b.date ? -1 : 1));
  const last = wl.filter((x) => x.date <= we).pop(), prev = wl.filter((x) => x.date < ws).pop();
  const inWeek = last && last.date >= ws;
  const sp = { bought: GOALS.buys.filter((b) => b.d >= ws && b.d <= we).reduce((a, b) => a + b.a, 0), eaten: past.reduce((a, d) => a + dsum(d).c, 0), est: estRange(ws, we) };
  return { ws, we, trained, goal: trainDays(), nEaten: eaten.length, nPast: past.length, kcal: eaten.length ? eaten.reduce((a, x) => a + x.e.k, 0) / eaten.length : null, prot: eaten.length ? eaten.reduce((a, x) => a + x.e.p, 0) / eaten.length : null, water, dWeight: inWeek && prev ? last.weight - prev.weight : null, weight: inWeek ? last.weight : null, sp };
}
/* Ein Satz fürs nächste Mal: die größte Lücke der Woche, mit einem konkreten Schritt */
function reviewTip(r) {
  if (!r || r.nPast < 2) return "";
  const pg = protGoal(), tgt = Math.round(pg * 0.95);
  if (r.trained < r.goal) return "Plane die nächsten Trainings gleich zu Wochenbeginn ein, am besten nach einer Frühschicht oder an freien Tagen. Wenn die Kraft fehlt, zählt auch die Kurz-Einheit mit etwa 15 Minuten.";
  if (r.prot != null && r.prot < tgt) { const gap = Math.round(pg - r.prot), g = Math.max(50, Math.round(gap / PRICE.quark.p * 100 / 10) * 10); return "Dir fehlen im Schnitt etwa " + gap + " g Eiweiß am Tag. Das schließen zum Beispiel " + g + " g Magerquark als Snack."; }
  if (r.nPast >= 4 && r.nEaten < r.nPast - 1) return "Trag nächste Woche jeden Tag wenigstens das Abendessen ein. Dann stimmen die Durchschnitte hier.";
  if (r.kcal != null && r.kcal > GOALS.kcal + 250) return "Du liegst im Schnitt etwa " + Math.round(r.kcal - GOALS.kcal) + " kcal über deinem Ziel. Ein Snack weniger oder etwas weniger Reis oder Nudeln reicht schon.";
  if (r.nPast >= 4 && r.water < Math.ceil(r.nPast / 2)) return "Wasser war nur an " + r.water + " Tagen im Ziel. Stell dir morgens eine volle Flasche hin.";
  if (r.sp.bought > 0 && r.sp.est > 0 && r.sp.bought > r.sp.est * 1.25) return "Du hast mehr eingekauft als geschätzt (" + eur(r.sp.bought) + " gegen " + eur(r.sp.est) + "). Im Glücksrad plant „Reste verwerten“ angebrochene Packungen in die Woche ein.";
  return "Alles im Plan. Bleib bei deiner Routine, oder gehe bei einer Übung eine Stufe hoch, wenn sie leicht war.";
}
function reviewTipHTML(r) { const t = reviewTip(r); return t ? '<p class="small review-tip"><b>Fürs nächste Mal:</b> ' + esc(t) + "</p>" : ""; }
function reviewHTML(ws, nav) {
  const r = weekReview(ws), pg = protGoal(), ok = (c) => (c ? ' <span class="tag g">geschafft</span>' : "");
  const sg = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + nf(Math.abs(Math.round(v * 10) / 10));
  const rows = [
    ["Training", r.trained + " von " + r.goal + ok(r.trained >= r.goal)],
    ["Eiweiß", r.prot == null ? "keine Einträge" : "Ø " + Math.round(r.prot) + " g (Ziel " + pg + " g)" + ok(r.prot >= pg * 0.95)],
    ["Kalorien", r.kcal == null ? "keine Einträge" : "Ø " + Math.round(r.kcal).toLocaleString("de-DE") + " kcal (Ziel " + GOALS.kcal.toLocaleString("de-DE") + " kcal)"],
    ["Essen eingetragen", r.nEaten + " von " + r.nPast + " Tagen"],
    ["Wasser", r.water + " von " + r.nPast + " Tagen im Ziel"],
    ["Gewicht", r.weight == null ? "kein Wert in dieser Woche" : nf(r.weight) + " kg" + (r.dWeight != null ? " (" + sg(r.dWeight) + " kg zur Vorwoche)" : "")],
    ["Ausgaben", (r.sp.bought > 0 ? eur(r.sp.bought) + " eingekauft, " : r.sp.est > 0 ? "ca. " + eur(r.sp.est) + " Einkauf geschätzt, " : "") + eur(r.sp.eaten) + " gegessen (Preisliste)"]
  ];
  const range = dateDE(r.ws) + " bis " + dateDE(r.we);
  return '<div class="card review" data-nofold><div class="rday-h"><div><h3>Wochenrückblick</h3><p class="muted small">' + range + "</p></div>" + (nav ? '<span class="row" style="gap:4px"><button class="btn icon sm" type="button" data-rvw="-1" aria-label="Vorige Woche">‹</button><button class="btn icon sm" type="button" data-rvw="1" aria-label="Nächste Woche"' + (r.we >= todayISO() && r.ws >= weekStartISO(todayISO()) ? " disabled" : "") + ">›</button></span>" : "") + '</div><ul class="ptable rvl">' +
    rows.map((x) => "<li><span>" + x[0] + "</span><b>" + x[1] + "</b></li>").join("") + "</ul>" + reviewTipHTML(r) + "</div>";
}
function reviewToday() {
  const wd = (new Date().getDay() + 6) % 7, ws = weekStartISO(todayISO());
  if (wd === 6) return reviewHTML(ws, false);
  if (wd === 0) return reviewHTML(shiftDay(ws, -7), false);
  return "";
}
function heatHTML() {
  const start = shiftDay(weekStartISO(todayISO()), -77), set = new Set(sessions), today = todayISO();
  let cells = "";
  for (let w = 0; w < 12; w++) for (let d = 0; d < 7; d++) { const iso = shiftDay(start, w * 7 + d); cells += '<span class="hm' + (set.has(iso) ? " on" : "") + (iso === today ? " today" : "") + (iso > today ? " fut" : "") + '" title="' + dateDE(iso) + '"></span>'; }
  return '<div class="hmwrap"><div class="hmdays"><span>Mo</span><span></span><span>Mi</span><span></span><span>Fr</span><span></span><span></span></div><div class="hm12" role="img" aria-label="Trainingstage der letzten 12 Wochen">' + cells + "</div></div>";
}
function renderCharts() {
  const el = $("#charts"); if (!el) return;
  const ti = trendInfo();
  const wtxt = ti ? "Trend " + nf(Math.round(ti.now * 10) / 10) + " kg" + (ti.week != null ? ", 7 Tage " + (ti.week > 0 ? "+" : ti.week < 0 ? "−" : "") + nf(Math.abs(Math.round(ti.week * 10) / 10)) + " kg" : "") : "";
  const wpts = ti ? ti.pts : [];
  const cpts = log.filter((x) => x.waist != null).map((x) => ({ ms: new Date(x.date + "T12:00:00").getTime(), y: x.waist }));
  const recent = WK.slice(-5).reverse().map((w) => '<li><b>' + esc(dateDE(w.date)) + '</b><span class="muted small">' + esc(w.min) + " Min, " + exOf(w).map((e) => { const ev = evalEx(e, w.sets); return ev ? e.name + " " + ev.vals.join("/") : ""; }).filter(Boolean).join(", ") + "</span></li>").join("");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(REVW)) REVW = weekStartISO(todayISO());
  el.innerHTML =
    '<div class="card"><div class="rday-h"><h3>Gewicht</h3><span class="rtot">' + wtxt + "</span></div>" + chartSVG(wpts, "dein Gewicht", true) +
    '<p class="small muted">Die Linie zeigt deinen Trend und glättet Schwankungen durch Wasser und Essen. Wiege dich morgens nach dem Toilettengang und achte auf den Trend, nicht auf einzelne Tage. Ein gutes Tempo sind etwa 0,5 bis 1 % deines Gewichts pro Woche.</p></div>' +
    '<div class="card"><h3>Taille</h3>' + chartSVG(cpts, "deine Taille", false) + "</div>" +
    reviewHTML(REVW, true) + coachEvalHTML() +
    '<div class="card"><h3>Training der letzten 12 Wochen</h3>' + heatHTML() + '<p class="small muted">Jedes Feld ist ein Tag. Ziel sind drei Einheiten pro Woche.</p></div>' +
    perfHTML() + (recent ? '<div class="card"><h3>Letzte Einheiten</h3><ul class="eatlist">' + recent + "</ul></div>" : "");
}

function bindGoals() {
  $("#s-kcal").value = GOALS.kcal; $("#s-protein").value = GOALS.protein > 0 ? GOALS.protein : ""; $("#s-protein").placeholder = "auto: " + Math.round(prof.weight * 1.6); $("#s-water").value = String(GOALS.water);
  const save = () => {
    const k = parseInt($("#s-kcal").value, 10), p = parseInt($("#s-protein").value, 10), w = parseInt($("#s-water").value, 10);
    if (k >= 1000 && k <= 5000) GOALS.kcal = k;
    GOALS.protein = p >= 40 && p <= 400 ? p : 0;
    if (w >= 1 && w <= 20) GOALS.water = w;
    saveToday(); renderToday(); radRender();
  };
  ["#s-kcal", "#s-protein", "#s-water"].forEach((x) => $(x).addEventListener("change", save));
}


/* ======================= Ereignisse ======================= */
function openSettings() { showDialog($("#dlg-settings"), $("#b-settings")); }
document.addEventListener("click", (ev) => { const sm = ev.target.closest && ev.target.closest("summary"); if (sm && sm.parentElement && sm.parentElement.id === "plancol") { const d = sm.parentElement; setTimeout(() => { PLANOPEN = d.open; }, 0); } });
document.addEventListener("input", (ev) => { const t = ev.target; if (t && t.id === "calc-in") CALC.text = t.value; if (t && (t.id === "calc-name" || t.id === "calc-name0")) CALC.name = t.value; if (t && t.classList && t.classList.contains("myd-g")) mydFromInput(parseInt(t.dataset.i, 10)); });
document.addEventListener("click", (ev) => {
  const t = ev.target.closest("button"); if (!t) return;
  if (t.dataset.v3 != null && t.dataset.v3 !== "") return openV3(t.dataset.v3, t.dataset.i != null && t.dataset.i !== "" ? parseInt(t.dataset.i, 10) : null, t);
  if (t.dataset.prepopt) {
    const f = t.dataset.prepopt;
    if (f === "people") PREP.people = Math.max(1, Math.min(4, PREP.people + parseInt(t.dataset.d, 10)));
    else if (f === "days" || f === "n") { PREP[f] = parseInt(t.dataset.v, 10); if (f === "n") { prepSave(); prepGen(); } }
    else PREP[f] = !PREP[f];
    prepSave(); return renderPrep();
  }
  if (t.dataset.prepweek) { prepEnsure(); const nx = shiftDay(PREP.week, 7 * parseInt(t.dataset.prepweek, 10)), cur = weekStartISO(todayISO()); if (nx >= cur && nx <= shiftDay(cur, 28)) prepSelect(nx); return renderPrep(); }
  if (t.dataset.prepgen) { prepGen(t.dataset.prepgen); return renderPrep(); }
  if (t.dataset.prepcart) { const c = prepCalc(); c.entries.forEach((e) => cartAdd(e.id, e.n)); t.textContent = "Übernommen"; return; }
  if (t.dataset.eatagain != null) { const x = RECENT[parseInt(t.dataset.eatagain, 10)]; if (x) { const o = Object.assign({}, x, { again: true }); dayEns().items.push(o); saveToday(); renderToday(); drawEat("Nochmal eingetragen: " + x.t); } return; }
  if (t.dataset.calcgo) return calcGo();
  if (t.dataset.rvw) { const nx = shiftDay(/^\d{4}-\d{2}-\d{2}$/.test(REVW) ? REVW : weekStartISO(todayISO()), 7 * parseInt(t.dataset.rvw, 10)); if (nx <= weekStartISO(todayISO())) REVW = nx; return renderCharts(); }
  if (t.dataset.hh) { GOALS.hh = Math.max(1, Math.min(4, parseInt(t.dataset.hh, 10) || 2)); saveToday(); return renderShop(); }
  if (t.dataset.spm) { SPM = monthShift(/^\d{4}-\d{2}$/.test(SPM) ? SPM : todayISO().slice(0, 7), parseInt(t.dataset.spm, 10)); if (SPM > todayISO().slice(0, 7)) SPM = todayISO().slice(0, 7); return renderShop(); }
  if (t.dataset.buydel != null && t.dataset.buydel !== "") { GOALS.buys.splice(parseInt(t.dataset.buydel, 10), 1); saveToday(); return renderShop(); }
  if (t.dataset.buyadd) {
    const a = parseFloat(String($("#buy-a").value).replace(",", ".")), d = $("#buy-d").value, m = $("#buymsg");
    if (!(a > 0 && a <= 2000)) { m.textContent = "Trag einen Betrag zwischen 0,01 und 2000 € ein."; return; }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(d) || d > todayISO()) { m.textContent = "Das Datum passt nicht. Es darf nicht in der Zukunft liegen."; return; }
    GOALS.buys.push({ d: d, a: Math.round(a * 100) / 100 }); GOALS.buys.sort((x, y) => (x.d < y.d ? -1 : x.d > y.d ? 1 : 0)); GOALS.buys = GOALS.buys.slice(-400); SPM = d.slice(0, 7); saveToday(); return renderShop();
  }
  if (t.dataset.pricereset) { settings.prices = {}; store.set("fc_settings", settings); applyPrices(); renderRecipes(); renderShop(); renderToday(); return; }
  if (t.dataset.upd) { reloadFresh(); return; }
  if (t.dataset.setkcal) { const k = parseInt(t.dataset.setkcal, 10); if (k >= 1000 && k <= 6000) { GOALS.kcal = k; saveToday(); renderProgress(); renderToday(); } return; }
  if (t.dataset.perf) { PERF = t.dataset.perf; renderCharts(); return; }
  if (t.dataset.bkdo) { return doBackup().then((r) => { const m = $("#bkmsg"); if (r.ok) { renderToday(); } else if (m) { m.innerHTML = ""; const ta = document.createElement("textarea"); ta.rows = 3; ta.value = r.txt; ta.readOnly = true; m.appendChild(ta); ta.focus(); ta.select(); } }); }
  if (t.dataset.bklater) { GOALS.bkSnooze = shiftDay(todayISO(), 3); saveToday(); return renderToday(); }
  if (t.dataset.shift) return shChange(todayISO(), t.dataset.shift);
  if (t.dataset.shiftedit != null) { renderShiftDlg(); showDialog($("#dlg-shift"), t); return; }
  if (t.dataset.shd) { const [iso, v] = t.dataset.shd.split(":"); shChange(iso, v); return; }
  if (t.dataset.shwk) { const [ws, v] = t.dataset.shwk.split(":"); shPut(ws, v.repeat(6) + shGet(ws)[6]); shAfter(); return; }
  if (t.dataset.eatjump) { const el = document.getElementById(t.dataset.eatjump); if (el) el.scrollIntoView({ behavior: reduceMotion() ? "auto" : "smooth", block: "start" }); return; }
  if (t.dataset.histmore) { HISTN += 30; return renderEatHist(); }
  if (t.dataset.hdel) { const [dd, ii] = t.dataset.hdel.split(":"), day = DIARY[dd]; if (day && day.items[+ii]) { day.items.splice(+ii, 1); if (!day.items.length && !day.water && !day.plan) delete DIARY[dd]; saveToday(); renderEatHist(); renderToday(); } return; }
  if (t.dataset.mydsave) return mydNew();
  if (t.dataset.mydeat) return mydEat(parseInt(t.dataset.mydeat, 10));
  if (t.dataset.mydel) { const d = MYD[parseInt(t.dataset.mydel, 10)]; if (d) { MYD.splice(parseInt(t.dataset.mydel, 10), 1); mydSave(); drawEat("Gelöscht: " + d.name); } return; }
  if (t.dataset.calcre) { calcRead(); return drawEat(); }
  if (t.dataset.calccat) { const c = CCATS.find((x) => x[0] === t.dataset.c); calcRead(); CALC.man[t.dataset.calccat] = { k: c[1], p: c[2], cat: c[0] }; return drawEat(); }
  if (t.dataset.calcadd) { calcRead(); return calcAdd(); }
  if (t.dataset.swapopen) return openSwap(t.dataset.swapopen, t);
  if (t.dataset.gear) return toggleGear(t.dataset.gear);
  if (t.dataset.ms) return toggleMs(t.dataset.ms);
  if (t.dataset.goto) { const gd = t.closest("dialog"); if (gd && gd.open) gd.close(); return showTab(t.dataset.goto); }
  if (t.dataset.swap) return doSwap(t.dataset.swap, t.dataset.mode);
  if (t.dataset.reps) { if (W.phase === "work") setDone(parseInt(t.dataset.reps, 10)); return; }
  if (t.dataset.water != null && t.dataset.water !== "") { const i = parseInt(t.dataset.water, 10), day = dayEns(); day.water = day.water === i + 1 ? i : i + 1; saveToday(); return renderToday(); }
  if (t.dataset.plan != null && t.dataset.plan !== "") return planEat(parseInt(t.dataset.plan, 10));
  if (t.dataset.planre != null && t.dataset.planre !== "") return planRe(parseInt(t.dataset.planre, 10));
  if (t.dataset.planall) return t.dataset.planall === "new" ? planNew() : planAll();
  if (t.dataset.setsrec) { settings.sets = parseInt(t.dataset.setsrec, 10); store.set("fc_settings", settings); $("#s-sets").value = String(settings.sets); render(); renderEx(); renderToday(); return; }
  if (t.dataset.excz) { toggleExc("z:" + t.dataset.excz); return renderRecipes(); }
  if (t.dataset.excr) { toggleExc("r:" + t.dataset.excr); return renderRecipes(); }
  if (t.dataset.fav) { const id = t.dataset.fav; FAV = FAV.includes(id) ? FAV.filter((x) => x !== id) : FAV.concat(id); store.set("fc_fav", FAV); drawRecipe(); return renderRecipes(); }
  if (t.dataset.hide) { toggleExc("r:" + t.dataset.hide); closeDialog($("#dlg-recipe")); toast("Das Rezept ist ausgeblendet. Unter „Weitere Filter“ holst du es zurück."); return renderRecipes(); }
  if (t.dataset.cook) return openCook(t.dataset.cook, t);
  if (t.dataset.ckgo) return ckGo(parseInt(t.dataset.ckgo, 10));
  if (t.dataset.cktimer) return ckTimer(parseInt(t.dataset.cktimer, 10));
  if (t.dataset.ckclose) { ckStop(); unwake(); return closeDialog($("#dlg-cook")); }
  if (t.dataset.eatopen) return openEat();
  if (t.dataset.eat) { const r = byId(t.dataset.eat); if (r) { logEat(r, 1); t.textContent = "Eingetragen"; t.disabled = true; } return; }
  if (t.dataset.eatrec) { const r = byId(t.dataset.eatrec); if (r) { logEat(r, portions); t.textContent = "Eingetragen"; } return; }
  if (t.dataset.eatdel != null && t.dataset.eatdel !== "") { const dd = dayEns(), gone = dd.items.splice(parseInt(t.dataset.eatdel, 10), 1)[0]; if (gone && dd.plan && !gone.again) { const ix = dd.plan.ids.indexOf(gone.id); if (ix >= 0) dd.plan.done[ix] = false; } saveToday(); return renderToday(); }
  if (t.dataset.effort) { if (WK[SUMIDX]) { WK[SUMIDX].effort = t.dataset.effort; saveToday(); drawSummary(SUMIDX); } return; }
  if (t.dataset.lvlup || t.dataset.lvldown) { const id = t.dataset.lvlup || t.dataset.lvldown, e = EX.find((x) => x.id === id); levels[id] = Math.max(0, Math.min(e.ladder.length - 1, lvl(e) + (t.dataset.lvlup ? 1 : -1))); store.set("fc_levels", levels); renderEx(); render(); drawSummary(SUMIDX); return; }
  if (t.dataset.focusf) { const f = $("#" + t.dataset.focusf); if (f) { try { f.scrollIntoView({ block: "center", behavior: reduceMotion() ? "auto" : "smooth" }); } catch (e) {} f.focus({ preventScroll: true }); } return; }
  if (t.id === "b-settings") return openSettings();
  if (t.hasAttribute("data-close")) { closeDialog(t.closest("dialog")); return; }
  if (t.dataset.act) {
    if (t.dataset.act === "start" && window.matchMedia && matchMedia("(max-width: 979px)").matches) window.scrollTo({ top: 0, behavior: reduceMotion() ? "auto" : "smooth" });
    return act(t.dataset.act === "pause" && tm.id && !tm.running ? "resume" : t.dataset.act);
  }
  if (t.dataset.group) { const gg = GROUPS.find((x) => x.id === t.dataset.group); return showTab(LAST[gg.id] || gg.tabs[0]); }
  if (t.dataset.histgo) { showTab("fortschritt"); const h = document.getElementById("eathist"); if (h) h.scrollIntoView({ block: "start" }); return; }
  if (t.dataset.tab) return showTab(t.dataset.tab);
  if (t.dataset.lvl) {
    const e = EX.find((x) => x.id === t.dataset.lvl);
    levels[e.id] = Math.max(0, Math.min(e.ladder.length - 1, lvl(e) + parseInt(t.dataset.d, 10)));
    store.set("fc_levels", levels); renderEx(); render(); return;
  }
  if (t.dataset.cartadd) { cartAdd(t.dataset.cartadd, portions); t.textContent = "Hinzugefügt (" + portions + (portions === 1 ? " Portion)" : " Portionen)"); return; }
  if (t.dataset.cart) { const ci = parseInt(t.dataset.ci, 10), c = CART[ci]; c.n += parseInt(t.dataset.cart, 10); if (c.n < 1) CART.splice(ci, 1); saveCart(); return renderShop(); }
  if (t.dataset.cartclear) { CART = []; CHK = {}; saveCart(); return renderShop(); }
  if (t.dataset.cartplan) { const Pl = RPL[RAD.mode]; if (Pl) { planEntries(Pl, true).forEach((e) => cartAdd(e.id, e.n)); t.textContent = "Übernommen"; } return; }
  if (t.id === "spin") return radRoll();
  if (t.id === "skipspin") { rad.skip = true; return; }
  if (t.dataset.rmode) { RAD.mode = t.dataset.rmode; saveRad(); radShowAll(); renderRadOpts(); radIdle(); radRender(); drawWheel(); return; }
  if (t.dataset.rmeal) { RAD.meal = t.dataset.rmeal; saveRad(); renderRadOpts(); radIdle(); drawWheel(); return; }
  if (t.dataset.ropt) { RAD[t.dataset.ropt] = !RAD[t.dataset.ropt]; saveRad(); renderRadOpts(); radIdle(); radRender(); drawWheel(); return; }
  if (t.dataset.rmax) { RAD.maxDay = parseInt(t.dataset.rmax, 10); saveRad(); return renderRadOpts(); }
  if (t.dataset.rpeople) { RAD.people = parseInt(t.dataset.rpeople, 10); saveRad(); renderRadOpts(); return radRender(); }
  if (t.dataset.rlock) { const [d, i] = t.dataset.rlock.split(":").map(Number), sl = RPL[RAD.mode].days[d].slots[i]; sl.locked = !sl.locked; saveRad(); return radRender(); }
  if (t.dataset.rspin) return radRoll(t.dataset.rspin);
  if (t.dataset.recipe) return openRecipe(t.dataset.recipe, false, t);
  if (t.dataset.por) { portions = Math.max(1, Math.min(4, portions + parseInt(t.dataset.por, 10))); return drawRecipe(); }
  if (t.dataset.rmore) return renderRecipes(true);
  if (t.dataset.f) { const g = t.dataset.f, v = g === "time" ? parseInt(t.dataset.v, 10) : t.dataset.v; F[g] = F[g] === v ? (g === "time" ? 0 : "") : v; return renderRecipes(); }
  if (t.dataset.ft) { F[t.dataset.ft] = !F[t.dataset.ft]; return renderRecipes(); }
  if (t.dataset.exc) { EXC = EXC.includes(t.dataset.exc) ? EXC.filter((x) => x !== t.dataset.exc) : EXC.concat(t.dataset.exc); store.set("fc_exc", EXC); return renderRecipes(); }
  if (t.dataset.freset) return resetFilters();
  if (t.dataset.del) { log = log.filter((x) => x.date !== t.dataset.del); store.set("fc_log", log); renderProgress(); }
});
document.addEventListener("input", (ev) => {
  const t = ev.target;
  if (t.id === "rsearch") {
    F.q = t.value; const pos = t.selectionStart; renderRecipes();
    const n = $("#rsearch"); if (n) { n.focus(); try { n.setSelectionRange(pos, pos); } catch (e) {} }
  }
  if (t.id === "eatq") { EATQ = t.value; const pos = t.selectionStart; drawEat(); const n = $("#eatq"); if (n) { n.focus(); try { n.setSelectionRange(pos, pos); } catch (e) {} } }
  if (t.id === "b-weight" || t.id === "b-height") {
    const v = parseFloat(t.value);
    if (v > 0) { prof[t.id === "b-weight" ? "weight" : "height"] = v; store.set("fc_body", prof); $("#calc").innerHTML = calcStats(bodyCalc()); $("#waistnote").textContent = waistNote(); }
  }
  if (t.dataset && t.dataset.price) {
    const k = t.dataset.price; if (!PRICE[k]) return;
    const v = parseFloat(String(t.value).replace(",", "."));
    if (!isFinite(v) || v <= 0 || Math.abs(v - PRICE0[k]) < 0.005) delete settings.prices[k];
    else if (v >= 0.05 && v <= 99.99) settings.prices[k] = Math.round(v * 100) / 100;
    store.set("fc_settings", settings); applyPrices(); renderRecipes(); renderShop(); renderToday(); return;
  }
  if (t.id === "plan-small") {
    GOALS.pause = t.checked ? "small" : "meal"; const d = dayEns();
    if (d.plan && !d.plan.free) {
      const old = d.plan, ids = makeDayPlan(false, [old.ids[0], old.done[1] ? old.ids[1] : null, old.ids[2]]);
      if (ids) d.plan = mkPlan(ids, false, old);
    }
    saveToday(); return renderToday();
  }
  if (t.dataset && t.dataset.shop) { shop[t.dataset.shop] = t.checked; store.set("fc_shop", shop); }
  if (t.dataset && t.dataset.chk) { CHK[t.dataset.chk] = t.checked; saveCart(); shopRefresh(t.dataset.chk); }
  if (t.dataset && t.dataset.prepchk) { PREP.done[t.dataset.prepchk] = t.checked; prepSave(); const li = t.closest("li"); if (li) li.classList.toggle("done", t.checked); }
});
document.addEventListener("change", (ev) => { if (ev.target && ev.target.id === "rsort") { F.sort = ev.target.value; renderRecipes(); const n = $("#rsort"); if (n) n.focus(); return; } if (ev.target && ev.target.id === "budget") { BUDGET = Math.max(0, parseFloat(String(ev.target.value).replace(",", ".")) || 0); saveCart(); renderShop(); } });
["#dlg-recipe", "#dlg-settings", "#dlg-eat", "#dlg-sum", "#dlg-swap", "#dlg-shift"].forEach((s) => {
  $(s).addEventListener("click", (ev) => { if (ev.target === ev.currentTarget) closeDialog(ev.currentTarget); });
  $(s).addEventListener("cancel", (ev) => { ev.preventDefault(); closeDialog(ev.currentTarget); });
});
$("#logform").addEventListener("submit", (ev) => {
  ev.preventDefault();
  const num = (id) => { const v = parseFloat($(id).value.replace(",", ".")); return isNaN(v) ? null : v; };
  const part = {};
  const w = num("#f-weight"), c = num("#f-waist"), p = num("#f-push"), k = num("#f-plank");
  if (w != null) part.weight = w; if (c != null) part.waist = c; if (p != null) part.pushups = p; if (k != null) part.plank = k;
  if (!Object.keys(part).length) return;
  saveEntry(part); ev.target.reset();
});
document.addEventListener("submit", (ev) => {
  if (ev.target.id !== "eatform") return;
  ev.preventDefault();
  const name = $("#e-name").value.trim(), k = parseInt($("#e-k").value, 10), p = parseInt($("#e-p").value, 10);
  if (!name || isNaN(k) || isNaN(p)) return;
  dayEns().items.push({ t: name, k, p, c: 0 }); saveToday(); renderToday(); EATQ = ""; drawEat("Eingetragen: " + name);
});
function bindSettings() {
  $("#s-sets").value = String(settings.sets); $("#s-rest").value = String(settings.rest);
  $("#s-hold").value = String(settings.hold); $("#s-speak").checked = settings.speak; $("#s-text").value = String(settings.text);
  $("#s-text").addEventListener("change", () => { settings.text = parseInt($("#s-text").value, 10) || 100; store.set("fc_settings", settings); applyTextSize(); });
  const save = () => {
    settings.sets = parseInt($("#s-sets").value, 10); settings.rest = parseInt($("#s-rest").value, 10);
    settings.hold = parseInt($("#s-hold").value, 10); settings.speak = $("#s-speak").checked;
    store.set("fc_settings", settings); render();
  };
  ["#s-sets", "#s-rest", "#s-hold", "#s-speak"].forEach((s) => $(s).addEventListener("change", save));
  bindSync(); bindDays();
}
function bindDays() {
  const box = $("#s-tdays"), names = WEEK.map((d) => d[0]);
  const draw = () => {
    box.innerHTML = names.map((n, i) => '<button type="button" class="dbtn" data-day="' + i + '" aria-pressed="' + !!settings.tdays[i] + '">' + n + "</button>").join("");
    const t = settings.tdays, adj = t.some((v, i) => v && t[(i + 1) % 7]), cnt = trainDays();
    $("#tdays-note").textContent = adj ? "Tipp: Plane zwischen zwei Einheiten einen Ruhetag ein." : cnt > 4 ? "Für den Anfang reichen 3 Tage." : cnt < 2 ? "Mindestens 2 Tage pro Woche wären gut." : "";
  };
  box.addEventListener("click", (e) => { const b = e.target.closest("[data-day]"); if (!b) return; const i = parseInt(b.dataset.day, 10); settings.tdays[i] = settings.tdays[i] ? 0 : 1; store.set("fc_settings", settings); draw(); renderToday(); renderEx(); });
  draw();
}
const standalone = () => !!(window.navigator.standalone || (window.matchMedia && matchMedia("(display-mode: standalone)").matches));
const isoDays = (a, b) => Math.round((new Date(b + "T12:00:00") - new Date(a + "T12:00:00")) / 86400000);
async function doBackup() {
  const txt = FC.exportAll();
  try { await navigator.clipboard.writeText(txt); GOALS.lastBackup = todayISO(); saveToday(); return { ok: true, txt }; }
  catch (e) { return { ok: false, txt }; }
}
function backupHTML() {
  if (FC.sbInfo()) return "";
  const t = todayISO(), used = sessions.length + Object.keys(DIARY).length + log.length;
  if (used < 3 || (GOALS.bkSnooze && GOALS.bkSnooze > t)) return "";
  const last = GOALS.lastBackup, ago = last ? isoDays(last, t) : null;
  if (ago != null && ago < 7) return "";
  return '<div class="card bkcard"><div class="rday-h"><h3>Sicherung fällig</h3></div><p class="muted">' + (ago == null ? "Du hast noch keine Sicherung gemacht." : "Die letzte Sicherung ist " + ago + " Tage alt.") + " Deine Daten liegen nur auf diesem Gerät. Tippe auf „Jetzt sichern“ und füge den Text in eine Notiz ein.</p>" +
    '<div class="row"><button class="btn primary" type="button" data-bkdo="1">Jetzt sichern</button><button class="btn" type="button" data-bklater="1">Später</button></div><p class="small muted" id="bkmsg" role="status" aria-live="polite"></p></div>';
}
/* Kalender-Datei (.ics): Training und Vorkochen der nächsten 8 Wochen, Uhrzeit nach Schicht */
function buildICS() {
  const t = todayISO(), stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z"), L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Fitness Coach//DE", "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Fitness Coach"];
  const dt = (iso, hm) => iso.replace(/-/g, "") + "T" + hm.replace(":", "") + "00";
  const plus = (hm, min) => { const m = parseInt(hm.slice(0, 2), 10) * 60 + parseInt(hm.slice(3), 10) + min; return _p2(Math.floor(m / 60) % 24) + ":" + _p2(m % 60); };
  const ie = (x) => String(x).replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
  const ev = (uid, iso, hm, min, sum, desc, alarm) => { sum = ie(sum); desc = ie(desc); L.push("BEGIN:VEVENT", "UID:" + uid + "@fitness-coach", "DTSTAMP:" + stamp, "DTSTART:" + dt(iso, hm), "DTEND:" + dt(iso, plus(hm, min)), "SUMMARY:" + sum, "DESCRIPTION:" + desc, "BEGIN:VALARM", "TRIGGER:-PT" + alarm + "M", "ACTION:DISPLAY", "DESCRIPTION:" + sum, "END:VALARM", "END:VEVENT"); };
  let n = 0;
  for (let i = 0; i < 56; i++) {
    const iso = shiftDay(t, i), wd = shIdx(iso), sh = shiftOf(iso);
    if (settings.tdays[wd]) { ev("fc-training-" + iso.replace(/-/g, ""), iso, sh === "n" ? "18:00" : "10:00", 60, "Training", "Ganzkörper, ca. " + estMinutes() + " Minuten. Aufwärmen nicht vergessen.", 30); n++; }
    if (wd === 6) { ev("fc-vorkochen-" + iso.replace(/-/g, ""), iso, "14:00", 120, "Vorkochen", "Die Woche vorkochen. Einkaufsliste in der App.", 60); n++; }
  }
  L.push("END:VCALENDAR");
  return { text: L.join("\r\n") + "\r\n", count: n };
}
async function shareICS() {
  const r = buildICS(), msg = $("#icsmsg");
  const blob = new Blob([r.text], { type: "text/calendar" });
  try {
    const f = new File([blob], "fitness-coach.ics", { type: "text/calendar" });
    if (navigator.canShare && navigator.canShare({ files: [f] })) { await navigator.share({ files: [f], title: "Fitness Coach" }); msg.textContent = r.count + " Termine bereit. Wähle in der Liste „Kalender“."; return; }
  } catch (e) { if (e && e.name === "AbortError") { msg.textContent = "Abgebrochen."; return; } }
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "fitness-coach.ics"; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1500);
  msg.textContent = r.count + " Termine als Datei geladen. Öffne sie, dann fragt der Kalender nach dem Hinzufügen.";
}
/* Kurze Hinweiszeile unten */
let toastT = 0;
function toast(t) {
  let el = document.getElementById("toast");
  if (!el) { el = document.createElement("div"); el.id = "toast"; el.className = "toast"; el.setAttribute("role", "status"); document.body.appendChild(el); }
  el.textContent = t; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(() => { el.hidden = true; }, 5000);
}
/* Speicher voll oder gesperrt: Bescheid geben statt still Daten zu verlieren (lokal alle 5 Minuten, mit Datenbank einmal) */
let SAVEWARN = 0;
FC.onSaveFail(() => {
  const local = FC.mode === "local";
  if (SAVEWARN && (!local || Date.now() - SAVEWARN < 300000)) return;
  SAVEWARN = Date.now();
  toast(local ? "Speichern klappt gerade nicht, der Speicher im Browser ist voll oder gesperrt. Kopiere unter Einstellungen eine Sicherung, sonst gehen Änderungen beim Schließen verloren." : "Der Speicher im Browser ist voll oder gesperrt. Deine Änderungen liegen gerade nur in der Datenbank.");
});
/* Update-Prüfung: fragt den Server nach der aktuellen Versionsnummer */
const verNum = (v) => { const m = /v(\d+)\.(\d+)/.exec(v || ""); return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : null; };
const verNewer = (a, b) => { const x = verNum(a), y = verNum(b); return !!(x && y && (x[0] > y[0] || (x[0] === y[0] && x[1] > y[1]))); };
const canCheckUpdate = () => /^https?:$/.test(location.protocol);
async function remoteVersion() {
  const r = await fetch(location.pathname + "?fcv=" + Date.now(), { cache: "no-store" });
  if (!r.ok) throw new Error("http " + r.status);
  const m = /id="appver"[^>]*>([^<]*)</.exec(await r.text());
  return m ? m[1].trim() : null;
}
async function reloadFresh() {
  try { const rg = navigator.serviceWorker && (await navigator.serviceWorker.getRegistration()); if (rg) await rg.update(); } catch (e) {}
  try { const ks = await caches.keys(); await Promise.all(ks.map((k) => caches.delete(k))); } catch (e) {}
  location.reload();
}
function showUpdateBar(v) {
  let el = document.getElementById("updbar");
  if (!el) { el = document.createElement("div"); el.id = "updbar"; el.className = "updbar"; el.setAttribute("role", "status"); document.body.appendChild(el); }
  el.innerHTML = "<span>Neue Version " + esc(v) + '</span><button class="btn sm primary" type="button" data-upd="1">Jetzt laden</button>';
}
let UPDLAST = 0;
async function checkUpdate(force) {
  if (!canCheckUpdate() || (!force && Date.now() - UPDLAST < 45000)) return null;
  UPDLAST = Date.now();
  const cur = $("#appver").textContent.trim(), rv = await remoteVersion();
  if (rv && verNewer(rv, cur)) showUpdateBar(rv);
  return { cur, rv };
}
function bindSync() {
  const msg = (t) => { $("#restoremsg").textContent = t; };
  $("#instinfo").textContent = standalone() ? "Du nutzt gerade die installierte App." : "Noch nicht installiert. Mit diesen Schritten bekommst du ein Symbol auf dem Home-Bildschirm, Vollbild und Betrieb ohne Netz.";
  $("#b-ics").addEventListener("click", shareICS);
  $("#b-upd").addEventListener("click", async () => {
    const m = $("#updmsg"); m.textContent = "Prüfe …";
    try {
      const r = await checkUpdate(true);
      if (!r || !r.rv) m.textContent = "Die Version auf dem Server konnte nicht gelesen werden.";
      else if (verNewer(r.rv, r.cur)) m.textContent = "Neu: " + r.rv + ". Du hast " + r.cur + ". Tippe oben auf „Jetzt laden“.";
      else if (verNewer(r.cur, r.rv)) m.textContent = "Du hast " + r.cur + ", auf dem Server liegt noch " + r.rv + ". GitHub braucht manchmal ein paar Minuten.";
      else m.textContent = "Du hast die neueste Version: " + r.cur + ".";
    } catch (e) { m.textContent = "Keine Verbindung zum Server."; }
  });
  $("#sb-copy").addEventListener("click", async () => { const i = FC.sbInfo(); if (!i) return; const t = "FCSB:" + JSON.stringify({ url: i.url, key: i.key, mail: i.email }); try { await navigator.clipboard.writeText(t); $("#sbmsg").textContent = "Verbindung kopiert. Füge sie in der App unter „Eigene Datenbank verbinden“ ein."; } catch (e) { $("#sbmsg").textContent = "Kopieren hat nicht geklappt."; } });
  $("#sb-paste").addEventListener("input", (ev) => {
    const v = ev.target.value.trim(); if (v.indexOf("FCSB:") !== 0) return;
    try { const o = JSON.parse(v.slice(5)); if (typeof o.url === "string" && typeof o.key === "string") { $("#sb-url").value = o.url; $("#sb-key").value = o.key; $("#sb-mail").value = typeof o.mail === "string" ? o.mail : ""; ev.target.value = ""; $("#sbmsg").textContent = "Verbindung eingefügt. Jetzt nur noch dein Passwort eingeben und auf Anmelden tippen."; $("#sb-pw").focus(); } } catch (e) { $("#sbmsg").textContent = "Das sieht nicht nach einer kopierten Verbindung aus."; }
  });
  $("#b-backup").addEventListener("click", async () => {
    const r = await doBackup(), ta = $("#t-restore");
    if (r.ok) msg("Sicherung kopiert. Auf dem anderen Gerät unten einfügen und „Einspielen“ drücken.");
    else { ta.value = r.txt; ta.focus(); ta.select(); msg("Markiere den Text und kopiere ihn von Hand."); }
  });
  $("#b-restore").addEventListener("click", async () => {
    const t = $("#t-restore").value.trim();
    if (!t) return msg("Füge zuerst die Sicherung in das Feld ein.");
    try { const n = await FC.importAll(t); msg("Eingespielt (" + n + " Bereiche). Die App lädt neu …"); setTimeout(() => location.reload(), 700); }
    catch (e) { msg(e.message || "Das hat nicht geklappt."); }
  });
  const showSb = () => { const i = FC.sbInfo(); $("#sbform").hidden = !!i; $("#sbon").hidden = !i; if (i) $("#sb-who").textContent = i.email; };
  showSb();
  const sbDo = async (signup) => {
    const m = $("#sbmsg"); m.textContent = "Einen Moment …";
    try { await FC.sbLogin($("#sb-url").value, $("#sb-key").value, $("#sb-mail").value, $("#sb-pw").value, signup); m.textContent = "Verbunden. Die App lädt neu …"; setTimeout(() => location.reload(), 600); }
    catch (e) { m.textContent = e instanceof TypeError ? "Keine Verbindung zur Datenbank. Prüfe die Projekt-URL und deine Internetverbindung." : (e.message || "Das hat nicht geklappt."); }
  };
  $("#sb-login").addEventListener("click", () => sbDo(false));
  $("#sb-signup").addEventListener("click", () => sbDo(true));
  $("#sb-logout").addEventListener("click", async () => { $("#sbmsg").textContent = "Melde ab …"; await FC.sbLogout(); location.reload(); });
  FC.paint();
}
