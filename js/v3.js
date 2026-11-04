/* Fitness Coach: 3D-Ansicht der Übungen. Klassisches Skript, teilt sich den globalen Bereich mit den anderen Dateien in js/ (Reihenfolge siehe js/boot.js). */
/* ======================= 3D-Ansicht der Übungen ======================= */
/* Eigene kleine 3D-Engine: Gelenk-Figur mit Inverser Kinematik, Perspektive, Drehen per Ziehen. Braucht keine Bibliothek und keine Internetverbindung. */
const V3 = (() => {
  const RAD = Math.PI / 180;
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const len = (a) => Math.hypot(a[0], a[1], a[2]);
  const nrm = (a) => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const dir = (deg) => [Math.cos(deg * RAD), Math.sin(deg * RAD), 0];
  const SEG = { thigh: 0.43, shin: 0.43, up: 0.30, fore: 0.26, torso: 0.50, foot: 0.18, hand: 0.09 };
  const DEF = {
    pel: [0, 0.94, 0], tor: 90, hd: 90,
    la: [0, 0.08, -0.1], ra: [0, 0.08, 0.1], lfa: -26, rfa: -26,
    lw: [0.02, 0.86, -0.25], rw: [0.02, 0.86, 0.25], lha: null, rha: null,
    lkp: [1, 0, 0], rkp: [1, 0, 0], lep: [-1, 0, -0.4], rep: [-1, 0, 0.4],
    hipW: 0.09, shW: 0.19, roll: 0
  };
  const clone = (o) => { const r = {}; for (const k in o) r[k] = Array.isArray(o[k]) ? o[k].slice() : o[k]; return r; };
  const POSE = (o) => Object.assign(clone(DEF), o || {});
  const lerpv = (a, b, s) => Array.isArray(a) ? a.map((v, i) => v + (b[i] - v) * s) : typeof a === "number" && typeof b === "number" ? a + (b - a) * s : (s < 0.5 ? a : b);
  const mixPose = (a, b, s) => { const r = {}; for (const k in a) r[k] = lerpv(a[k], b[k], s); return r; };
  const ease = (t) => t * t * t * (t * (t * 6 - 15) + 10);

  function ik(A, T, l1, l2, pole) {
    let d = sub(T, A), dist = len(d); const max = l1 + l2 - 1e-4;
    if (dist > max) { d = mul(d, max / dist); dist = max; }
    if (dist < 1e-3) dist = 1e-3;
    const u = mul(d, 1 / dist), T2 = add(A, d);
    const a = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist), h = Math.sqrt(Math.max(0, l1 * l1 - a * a));
    let pp = sub(pole, mul(u, dot(pole, u))); if (len(pp) < 1e-5) pp = [0, 0, 1];
    pp = nrm(pp);
    return { j: add(A, add(mul(u, a), mul(pp, h))), t: T2 };
  }
  function solve(p) {
    const P = p.pel, d = dir(p.tor), neck = add(P, mul(d, SEG.torso));
    const S = sub(neck, mul(d, 0.04)), head = add(neck, mul(dir(p.hd), 0.17));
    const rr = (p.roll || 0) * RAD, lat = [Math.sin(rr) * d[1], -Math.sin(rr) * d[0], Math.cos(rr)];
    const J = { P, neck, head, sL: sub(S, mul(lat, p.shW)), sR: add(S, mul(lat, p.shW)), hL: sub(P, mul(lat, p.hipW)), hR: add(P, mul(lat, p.hipW)) };
    for (const s of ["L", "R"]) {
      const l = s === "L", leg = ik(J["h" + s], l ? p.la : p.ra, SEG.thigh, SEG.shin, l ? p.lkp : p.rkp);
      J["k" + s] = leg.j; J["a" + s] = leg.t;
      const fd = dir(l ? p.lfa : p.rfa);
      J["t" + s] = add(leg.t, mul(fd, SEG.foot)); J["e" + s] = sub(leg.t, mul(fd, 0.05));
      const arm = ik(J["s" + s], l ? p.lw : p.rw, SEG.up, SEG.fore, l ? p.lep : p.rep);
      J["el" + s] = arm.j; J["w" + s] = arm.t;
      const ha = l ? p.lha : p.rha, hd2 = ha == null ? nrm(sub(arm.t, arm.j)) : dir(ha);
      J["f" + s] = add(arm.t, mul(hd2, SEG.hand));
    }
    return J;
  }
  /* Bausteine für Posen */
  const shoulderOf = (p) => { const d = dir(p.tor), n = add(p.pel, mul(d, SEG.torso)); return sub(n, mul(d, 0.04)); };
  function reach(p, dx, dy, spread) {
    const S = shoulderOf(p), w = spread == null ? p.shW : spread;
    p.lw = [S[0] + dx, S[1] + dy, -w]; p.rw = [S[0] + dx, S[1] + dy, w]; return p;
  }
  const armsDown = (p) => reach(p, 0.03, -0.6, p.shW + 0.06);
  /* Körper als starre Linie, Drehpunkt am Fuß (Liegestütz, Plank) */
  const BODY = 0.855;
  function line(ax, ay, th, o) {
    const u = dir(th);
    return POSE(Object.assign({
      pel: [ax + BODY * u[0], ay + BODY * u[1], 0], tor: th, hd: th - 8,
      la: [ax, ay, -0.1], ra: [ax, ay, 0.1], lfa: -95, rfa: -95, lkp: [0, -1, 0], rkp: [0, -1, 0],
      lep: [-1, -0.3, -0.5], rep: [-1, -0.3, 0.5], lha: 0, rha: 0
    }, o));
  }
  const shoulderLine = 1.315;
  const thForShoulder = (ay, sy) => Math.asin(Math.max(-1, Math.min(1, (sy - ay) / shoulderLine))) / RAD;
  const kf = (p, d, l) => ({ p, d, l });

  /* Requisiten */
  const box = (x0, y0, z0, x1, y1, z1, col, alpha) => ({ x0, y0, z0, x1, y1, z1, col: col || "#9aa0a6", alpha: alpha == null ? 1 : alpha });
  const chair = (x, h) => [box(x - 0.24, h - 0.04, -0.24, x + 0.24, h, 0.24, "#b08a5b"), box(x - 0.24, 0, -0.24, x - 0.2, h - 0.04, -0.2, "#8a6a43"), box(x + 0.2, 0, -0.24, x + 0.24, h - 0.04, -0.2, "#8a6a43"),
    box(x - 0.24, 0, 0.2, x - 0.2, h - 0.04, 0.24, "#8a6a43"), box(x + 0.2, 0, 0.2, x + 0.24, h - 0.04, 0.24, "#8a6a43")];
  const chairBack = (x, h) => chair(x, h).concat([box(x - 0.26, h, -0.24, x - 0.22, h + 0.45, 0.24, "#b08a5b")]);
  const wall = (x) => [box(x, 0, -1.1, x + 0.05, 2.3, 1.1, "#7d8aa3", 0.45)];
  const block = (x0, x1, h, col) => [box(x0, 0, -0.4, x1, h, 0.4, col || "#b08a5b")];
  const table = (x0, x1, h) => [box(x0, h - 0.04, -0.55, x1, h, 0.55, "#b08a5b", 0.92), box(x0 + 0.03, 0, -0.52, x0 + 0.08, h - 0.04, -0.47, "#8a6a43"), box(x0 + 0.03, 0, 0.47, x0 + 0.08, h - 0.04, 0.52, "#8a6a43"),
    box(x1 - 0.08, 0, -0.52, x1 - 0.03, h - 0.04, -0.47, "#8a6a43"), box(x1 - 0.08, 0, 0.47, x1 - 0.03, h - 0.04, 0.52, "#8a6a43")];
  const bar = (x, h) => [box(x - 0.03, h - 0.02, -0.55, x + 0.03, h + 0.03, 0.55, "#6b7280"), box(x - 0.03, h - 0.02, -0.57, x + 0.03, 2.35, -0.52, "#6b7280"), box(x - 0.03, h - 0.02, 0.52, x + 0.03, 2.35, 0.57, "#6b7280")];
  const mat = (x0, x1) => [box(x0, 0, -0.45, x1, 0.02, 0.45, "#6f8f7a", 0.9)];

  return { RAD, add, sub, mul, dot, len, nrm, dir, SEG, DEF, POSE, mixPose, ease, solve, shoulderOf, reach, armsDown, line, thForShoulder, kf, box, chair, chairBack, wall, block, table, bar, mat, clone };
})();

/* Bewegungsabläufe: je Stufe ein Zyklus aus Schlüsselposen */
/* Bewegungsabläufe: je Stufe ein Zyklus aus Schlüsselposen */
const V3A = (() => {
  const { POSE, reach, armsDown, line, thForShoulder, kf, dir, RAD, chair, chairBack, wall, block, table, bar, mat, add, mul } = V3;
  const feet = (p, x, y) => { p.la = [x, y == null ? 0.08 : y, -0.13]; p.ra = [x, y == null ? 0.08 : y, 0.13]; return p; };
  const seq = (a, b, down, up, hold, labelDown, labelUp, labelA, labelB) => [kf(a, hold || 0.5, labelA || "Aufrecht stehen"), kf(a, down, labelDown), kf(b, hold || 0.5, labelB || "Unten kurz halten"), kf(b, up, labelUp)];

  /* ---------- Kniebeugen ---------- */
  const sq = (px, py, tor) => { const p = feet(POSE({ pel: [px, py, 0], tor, hd: tor + (90 - tor) * 0.6 }), 0); return reach(p, 0.52, -0.02); };
  const stand = sq(0, 0.94, 90);
  const squat0 = { kf: seq(stand, sq(-0.34, 0.58, 62), 1.6, 1.3, 0.5, "Langsam hinsetzen", "Aufstehen", "Aufrecht stehen", "Kurz absetzen"), props: chairBack(-0.4, 0.45), cam: { cx: -0.1, cy: 0.75, R: 1.35 } };
  const squat1 = { kf: seq(stand, sq(-0.3, 0.5, 60), 1.5, 1.2, 0.5, "Runter, Fersen bleiben am Boden", "Hoch", "Aufrecht stehen", "Unten kurz halten"), props: [], cam: { cx: -0.05, cy: 0.75, R: 1.35 } };
  const squat2 = { kf: seq(stand, sq(-0.3, 0.5, 60), 3.0, 1.2, 0.5, "Langsam runter, 3 Sekunden", "Hoch", "Aufrecht stehen", "Unten kurz halten"), props: [], cam: { cx: -0.05, cy: 0.75, R: 1.35 } };
  const split = (y) => { const p = POSE({ pel: [0, y, 0], tor: 90, hd: 90, la: [-0.5, 0.17, -0.1], lfa: -70, lkp: [0, -1, 0], ra: [0.5, 0.08, 0.1], rkp: [1, 0, 0] }); return reach(p, 0.03, -0.55, 0.24); };
  const squat3 = { kf: seq(split(0.77), split(0.47), 1.7, 1.3, 0.5, "Gerade runter, hinteres Knie Richtung Boden", "Hoch", "Aufrecht im Ausfallschritt", "Unten kurz halten"), props: [], cam: { cx: 0, cy: 0.7, R: 1.5 } };
  const bulg = (y) => { const p = POSE({ pel: [-0.05, y, 0], tor: 86, hd: 88, la: [-0.78, 0.53, -0.1], lfa: 200, lkp: [0, -1, 0], ra: [0.45, 0.08, 0.1], rkp: [1, 0, 0] }); return reach(p, 0.03, -0.55, 0.24); };
  const squat4 = { kf: seq(bulg(0.76), bulg(0.5), 1.8, 1.4, 0.5, "Gerade runter, vorderes Knie über dem Fuß", "Hoch", "Hinterer Fuß auf dem Stuhl", "Unten kurz halten"), props: chair(-0.8, 0.45), cam: { cx: -0.1, cy: 0.7, R: 1.55 } };

  /* ---------- Liegestütze ---------- */
  function push(c) {
    const thTop = c.thTop != null ? c.thTop : thForShoulder(c.ay, c.hy + 0.55), thBot = c.thBot != null ? c.thBot : thForShoulder(c.ay, c.hy + (c.low || 0.2));
    const hx = c.hx != null ? c.hx : c.ax + 1.315 * Math.cos(thTop * RAD) + (c.dx || 0);
    const mk = (th) => {
      const p = line(c.ax, c.ay, th, c.feet || {});
      p.lw = [hx, c.hy, -c.sp]; p.rw = [hx, c.hy, c.sp]; p.lha = p.rha = c.fing == null ? 0 : c.fing;
      if (c.el) { p.lep = c.el.map((v, i) => (i === 2 ? -v : v)); p.rep = c.el.slice(); }
      return p;
    };
    return { kf: seq(mk(thTop), mk(thBot), 1.5, 1.2, 0.4, "Runter, Körper bleibt eine Linie", "Hochdrücken", "Oben: Arme gestreckt", "Unten kurz halten"), props: c.props || [], cam: c.cam || { cx: 0.65, cy: 0.5, R: 1.5 } };
  }
  const flat = { lfa: -26, rfa: -26 };
  const push0 = push({ ax: 0, ay: 0.08, hy: 1.35, sp: 0.19, fing: 90, thTop: 72.5, thBot: 55, hx: 0.92, feet: flat, props: wall(0.96), cam: { cx: 0.5, cy: 0.9, R: 1.55 } });
  const push1 = push({ ax: 0, ay: 0.08, hy: 0.635, sp: 0.19, feet: flat, low: 0.2, props: block(0.5, 1.3, 0.6), cam: { cx: 0.6, cy: 0.65, R: 1.55 } });
  const push2 = push({ ax: 0, ay: 0.18, hy: 0.235, sp: 0.19, low: 0.2, props: block(1.0, 1.5, 0.2), dx: 0, cam: { cx: 0.7, cy: 0.5, R: 1.55 } });
  function kneePush() {
    const K = [0, 0.07], L = 0.89;
    const mk = (sy) => {
      const th = Math.asin((sy - 0.07) / L) / RAD, u = dir(th);
      const p = POSE({ pel: [K[0] + 0.43 * u[0], K[1] + 0.43 * u[1], 0], tor: th, hd: th - 8, la: [-0.4, 0.12, -0.1], ra: [-0.4, 0.12, 0.1], lfa: 190, rfa: 190, lkp: [0, -1, 0], rkp: [0, -1, 0], lep: [-1, -0.3, -0.5], rep: [-1, -0.3, 0.5], lha: 0, rha: 0 });
      return p;
    };
    const thTop = Math.asin((0.585 - 0.07) / L) / RAD, hx = L * Math.cos(thTop * RAD);
    const fin = (p) => { p.lw = [hx, 0.035, -0.19]; p.rw = [hx, 0.035, 0.19]; return p; };
    return { kf: seq(fin(mk(0.585)), fin(mk(0.23)), 1.5, 1.2, 0.4, "Runter, vom Knie bis zum Kopf eine Linie", "Hochdrücken", "Oben: Arme gestreckt", "Unten kurz halten"), props: mat(-0.7, 1.6), cam: { cx: 0.5, cy: 0.45, R: 1.3 } };
  }
  const push3 = kneePush();
  const push4 = push({ ax: 0, ay: 0.18, hy: 0.035, sp: 0.19, low: 0.2, props: mat(-0.5, 1.9), cam: { cx: 0.65, cy: 0.45, R: 1.5 } });
  const push5 = push({ ax: 0, ay: 0.58, hy: 0.035, sp: 0.19, low: 0.2, props: chair(0, 0.4), cam: { cx: 0.65, cy: 0.5, R: 1.5 } });
  const push6 = push({ ax: 0, ay: 0.18, hy: 0.035, sp: 0.05, low: 0.2, dx: -0.04, el: [-1, -0.3, 0.9], props: mat(-0.5, 1.9), cam: { cx: 0.65, cy: 0.45, R: 1.5 } });


  /* ---------- Pike-Liegestütze (Schultern) ---------- */
  function pike(c) {
    /* Füße (Fußgelenk) und Hände (Handgelenk) stehen fest. Aus der gewünschten Schulterlage folgt die Hüfte:
       Beine 0,855 m und Rumpf 0,5 m bilden ein umgedrehtes V, die Hüfte liegt am oberen Schnittpunkt der beiden Kreise. */
    const A = [c.ax, 0.08 + (c.fh || 0)], W = [c.hx, (c.hh || 0) + 0.035], L = 0.855, T = 0.5;
    const body = (off) => {
      const S0 = [W[0] + off[0], W[1] + off[1]];
      let N = S0.slice(), P = [0, 0], tor = -60;
      for (let k = 0; k < 5; k++) {
        const dx = N[0] - A[0], dy = N[1] - A[1], d0 = Math.hypot(dx, dy), d = Math.min(L + T - 0.01, Math.max(Math.abs(L - T) + 0.01, d0));
        const a = (L * L - T * T + d * d) / (2 * d), h = Math.sqrt(Math.max(0, L * L - a * a)), ux = dx / d0, uy = dy / d0;
        P = [A[0] + ux * a - uy * h, A[1] + uy * a + ux * h];
        tor = Math.atan2(N[1] - P[1], N[0] - P[0]) / RAD;
        N = [S0[0] + 0.04 * Math.cos(tor * RAD), S0[1] + 0.04 * Math.sin(tor * RAD)];
      }
      const p = POSE({ pel: [P[0], P[1], 0], tor, hd: Math.max(-90, tor - 6), la: [A[0], A[1], -0.1], ra: [A[0], A[1], 0.1], lfa: -26, rfa: -26, lkp: [1, 0, 0], rkp: [1, 0, 0], lha: 0, rha: 0, lep: [-1, -0.2, -0.5], rep: [-1, -0.2, 0.5] });
      p.lw = [W[0], W[1], -0.19]; p.rw = [W[0], W[1], 0.19];
      return p;
    };
    return { top: body(c.top || [-0.05, 0.54]), bot: body(c.bot || [0.08, 0.34]) };
  }
  const pk = (c, down, label) => { const q = pike(c); return { kf: seq(q.top, q.bot, down, 1.2, 0.4, label || "Kopf zwischen den Händen senken, Hüfte bleibt hoch", "Hochdrücken", "Oben: Hüfte hoch, Arme gestreckt", "Unten kurz halten"), props: c.props || [], cam: c.cam || { cx: 0.5, cy: 0.6, R: 1.3 } }; };
  const pike0 = pk({ ax: 0.1, fh: 0, hh: 0.45, hx: 1.2, top: [-0.38, 0.39], bot: [-0.1, 0.28], props: block(0.95, 1.45, 0.45).concat(mat(-0.3, 0.95)), cam: { cx: 0.65, cy: 0.62, R: 1.6 } }, 1.5);
  const pike1 = pk({ ax: 0.1, fh: 0, hh: 0, hx: 0.94, props: mat(-0.3, 1.3), cam: { cx: 0.55, cy: 0.6, R: 1.4 } }, 1.5);
  const pike2 = pk({ ax: 0.1, fh: 0.2, hh: 0, hx: 0.88, props: block(-0.1, 0.4, 0.2).concat(mat(-0.3, 1.3)), cam: { cx: 0.5, cy: 0.7, R: 1.4 } }, 1.5);
  const pike3 = pk({ ax: 0.1, fh: 0.42, hh: 0, hx: 0.8, props: chair(0.12, 0.42).concat(mat(-0.3, 1.3)), cam: { cx: 0.5, cy: 0.8, R: 1.5 } }, 1.6);
  const pike4 = pk({ ax: 0.1, fh: 0.42, hh: 0, hx: 0.8, props: chair(0.12, 0.42).concat(mat(-0.3, 1.3)), cam: { cx: 0.5, cy: 0.8, R: 1.5 } }, 3.0, "Langsam runter, 3 Sekunden");

  /* ---------- Rows unter dem Tisch ---------- */
  const TAB = table(-0.85, 1.05, 0.78);
  const grip = (p) => { p.lw = [1.02, 0.76, -0.22]; p.rw = [1.02, 0.76, 0.22]; p.lha = p.rha = null; p.lep = [0, -1, -0.6]; p.rep = [0, -1, 0.6]; return p; };
  const rowLine = (ax, ay, sy, fa) => { const th = thForShoulder(ay, sy); const p = line(ax, ay, th, { lfa: fa, rfa: fa, hd: th + 6, lkp: [0, 1, 0], rkp: [0, 1, 0] }); return grip(p); };
  const rowBent = (sy) => {
    const th = Math.asin((sy - 0.42) / 0.5) / RAD;
    const p = POSE({ pel: [0.55, 0.42, 0], tor: th, hd: th + 6, la: [0.12, 0.08, -0.12], ra: [0.12, 0.08, 0.12], lkp: [0, 1, 0], rkp: [0, 1, 0] });
    return grip(p);
  };
  const rowSeq = (a, b, down, up) => [kf(a, 0.5, "Arme gestreckt, Körper eine Linie"), kf(a, up, "Brust zur Tischkante ziehen"), kf(b, 0.5, "Oben kurz halten, Schulterblätter zusammen"), kf(b, down, "Kontrolliert absenken")];
  const rcam = { cx: 0.4, cy: 0.5, R: 1.7 };
  const row0 = { kf: rowSeq(rowBent(0.2), rowBent(0.62), 1.6, 1.2), props: TAB, cam: rcam };
  const row1 = { kf: rowSeq(rowLine(-0.3, 0.08, 0.19, 50), rowLine(-0.3, 0.08, 0.62, 50), 1.6, 1.2), props: TAB, cam: rcam };
  const row2 = { kf: rowSeq(rowLine(-0.3, 0.53, 0.19, 50), rowLine(-0.3, 0.53, 0.62, 50), 1.6, 1.2), props: TAB.concat(chair(-0.3, 0.45)), cam: rcam };
  const row3 = { kf: rowSeq(rowLine(-0.3, 0.53, 0.19, 50), rowLine(-0.3, 0.53, 0.62, 50), 3.0, 1.2), props: TAB.concat(chair(-0.3, 0.45)), cam: rcam };
  row3.kf[3].l = "Langsam absenken, 3 Sekunden";

  /* ---------- Glute Bridge ---------- */
  const NK = [1.0, 0.12];
  function bridge(phi, o) {
    const u = dir(-phi), P = [NK[0] - 0.5 * u[0], NK[1] - 0.5 * u[1], 0];
    const p = POSE(Object.assign({ pel: P, tor: -phi, hd: 0, la: [-0.12, 0.08, -0.13], ra: [-0.12, 0.08, 0.13], lkp: [0, 1, 0], rkp: [0, 1, 0], lw: [0.45, 0.035, -0.3], rw: [0.45, 0.035, 0.3], lha: 0, rha: 0 }, o || {}));
    return p;
  }
  const bcam = { cx: 0.5, cy: 0.35, R: 1.25 };
  const br0 = { kf: seq(bridge(0), bridge(35), 1.2, 1.2, 0.5, "Hüfte anheben, Po anspannen", "Absenken", "Auf dem Rücken, Füße hüftbreit", "Oben kurz halten"), props: mat(-0.5, 1.6), cam: bcam };
  const br1 = { kf: seq(bridge(0), bridge(35), 1.2, 1.2, 0.5, "Hüfte anheben, Po anspannen", "Absenken", "Auf dem Rücken, Füße hüftbreit", "Oben 2 Sekunden halten"), props: mat(-0.5, 1.6), cam: bcam };
  br1.kf[2] = kf(bridge(35), 2.0, "Oben 2 Sekunden halten");
  const legUp = (p, ang) => { p.la = add(p.pel, mul(dir(ang), 0.85)); p.la[2] = -0.12; p.lfa = 100; p.lkp = [0, 0, -1]; return p; };
  const br2 = { kf: seq(legUp(bridge(0), 125), legUp(bridge(35), 145), 1.3, 1.3, 0.5, "Hüfte anheben, ein Bein gestreckt", "Absenken", "Ein Bein hochgestreckt", "Oben kurz halten"), props: mat(-0.5, 1.6), cam: bcam };
  /* Hip Hinge */
  const hinge = (px, py, tor, hd) => { const p = feet(POSE({ pel: [px, py, 0], tor, hd, lkp: [1, 0, 0], rkp: [1, 0, 0] }), 0); return reach(p, 0.02, -0.6, 0.24); };
  const br3 = { kf: seq(hinge(0, 0.94, 90, 90), hinge(-0.27, 0.83, 24, 40), 1.8, 1.4, 0.5, "Hüfte nach hinten, Rücken gerade", "Hüfte nach vorn, aufrichten", "Aufrecht stehen", "Unten kurz halten"), props: [], cam: { cx: 0.05, cy: 0.7, R: 1.35 } };
  const one = (y, tor, la, lfa, hand) => {
    const p = POSE({ pel: [-0.02, y, 0], tor, hd: tor + 15, la, lfa, ra: [0, 0.08, 0.1], rfa: -26, lkp: [0, 1, 0], rkp: [1, 0, 0] });
    reach(p, 0.02, -0.6, 0.24);
    if (hand) { p.rw = hand; p.rha = 90; p.rep = [-1, 0, 0.4]; }
    return p;
  };
  const wallHand = [0.92, 0.9, 0.19];
  const brUp = one(0.94, 90, [-0.14, 0.18, -0.1], -80, [0.92, 0.9, 0.19]);
  const brDn = one(0.84, 5, [-0.87, 0.77, -0.1], -90, wallHand);
  brUp.rw = [0.4, 0.95, 0.19]; brUp.rha = null;
  const br4 = { kf: seq(brUp, brDn, 2.0, 1.6, 0.6, "Hüfte zurück, Bein nach hinten, Rücken gerade", "Aufrichten", "Auf einem Bein stehen", "Unten kurz halten"), props: wall(0.97), cam: { cx: 0.0, cy: 0.75, R: 1.5 } };

  /* ---------- Plank ---------- */
  function kneePlank(b) {
    const L = 0.89, sy = 0.33 + b, th = Math.asin((sy - 0.07) / L) / RAD, u = dir(th), sx = L * Math.cos(th * RAD);
    const p = POSE({ pel: [0.43 * u[0], 0.07 + 0.43 * u[1], 0], tor: th, hd: th - 4, la: [-0.4, 0.12, -0.1], ra: [-0.4, 0.12, 0.1], lfa: 190, rfa: 190, lkp: [0, -1, 0], rkp: [0, -1, 0], lha: 0, rha: 0, lep: [-1, -0.4, 0], rep: [-1, -0.4, 0] });
    p.lw = [sx + 0.26, 0.035, -0.17]; p.rw = [sx + 0.26, 0.035, 0.17]; return p;
  }
  function toePlank(b) {
    const sy = 0.33 + b, th = thForShoulder(0.18, sy), p = line(0, 0.18, th, { hd: th - 6, lep: [-1, -0.4, 0], rep: [-1, -0.4, 0] });
    const sx = 1.315 * Math.cos(th * RAD); p.lw = [sx + 0.26, 0.035, -0.17]; p.rw = [sx + 0.26, 0.035, 0.17]; return p;
  }
  const hold = (f, label) => ({ kf: [kf(f(0), 2.0, label), kf(f(0.008), 2.0, "Ruhig weiteratmen")] });
  const pl0 = Object.assign(hold(kneePlank, "Halten: Körper eine Linie vom Knie bis zum Kopf"), { props: mat(-0.7, 1.4), cam: { cx: 0.45, cy: 0.35, R: 1.25 } });
  const pl1 = Object.assign(hold(toePlank, "Halten: Körper eine Linie, Bauch und Po fest"), { props: mat(-0.5, 1.9), cam: { cx: 0.65, cy: 0.35, R: 1.5 } });
  function hollow(b, leg) {
    const p = POSE({ pel: [0, 0.12, 0], tor: 28 + b, hd: 28 + b, lkp: [0, 1, 0], rkp: [0, 1, 0], lha: 12, rha: 12, lfa: 80, rfa: 80 });
    const S = V3.shoulderOf(p), w = add(S, mul(dir(12), 0.56));
    p.lw = [w[0], w[1], -0.17]; p.rw = [w[0], w[1], 0.17];
    const bent = [-0.61, 0.56];
    p.ra = [bent[0], bent[1], 0.1]; p.la = leg ? [-0.8, 0.3, -0.1] : [bent[0], bent[1], -0.1];
    if (!leg) { p.lkp = [1, 1, 0]; } p.rkp = [1, 1, 0];
    return p;
  }
  const pl2 = { kf: [kf(hollow(0, false), 2.0, "Halten: Rücken am Boden, Arme über dem Kopf"), kf(hollow(1.5, false), 2.0, "Ruhig weiteratmen")], props: mat(-1.0, 1.4), cam: { cx: 0.2, cy: 0.35, R: 1.3 } };
  const pl3 = { kf: [kf(hollow(0, true), 2.0, "Halten: ein Bein gestreckt, Rücken am Boden"), kf(hollow(1.5, true), 2.0, "Ruhig weiteratmen")], props: mat(-1.0, 1.4), cam: { cx: 0.2, cy: 0.35, R: 1.3 } };

  /* ---------- Extras ---------- */
  function dead(armL, armR, legL, legR) {
    const p = POSE({ pel: [0, 0.12, 0], tor: 0, hd: 0, lfa: 90, rfa: 90, lkp: [1, 1, 0], rkp: [1, 1, 0], lha: 90, rha: 90 });
    const S = V3.shoulderOf(p), up = [S[0], S[1] + 0.58], over = [S[0] + 0.6, 0.17];
    p.lw = [(armL ? over : up)[0], (armL ? over : up)[1], -0.19]; p.rw = [(armR ? over : up)[0], (armR ? over : up)[1], 0.19];
    p.lha = armL ? 0 : 90; p.rha = armR ? 0 : 90;
    p.la = legL ? [-0.85, 0.2, -0.1] : [-0.43, 0.55, -0.1]; p.ra = legR ? [-0.85, 0.2, 0.1] : [-0.43, 0.55, 0.1];
    if (legL) p.lkp = [0, 1, 0]; if (legR) p.rkp = [0, 1, 0];
    return p;
  }
  const d0 = dead(false, false, false, false);
  const deadbug = { kf: [kf(d0, 0.6, "Start: Arme senkrecht, Knie im rechten Winkel"), kf(dead(true, false, false, true), 1.6, "Linker Arm und rechtes Bein langsam strecken"), kf(dead(true, false, false, true), 0.4, "Unterer Rücken bleibt am Boden"), kf(d0, 1.4, "Zurück zur Mitte"), kf(dead(false, true, true, false), 1.6, "Rechter Arm und linkes Bein strecken"), kf(dead(false, true, true, false), 0.4, "Unterer Rücken bleibt am Boden"), kf(d0, 1.4, "Zurück zur Mitte")], props: mat(-1.2, 1.5), cam: { cx: 0.2, cy: 0.35, R: 1.3 } };
  const wr = (px, tor) => { const p = feet(POSE({ pel: [px, 0.94, 0], tor, hd: tor + 10 }), 0); p.lw = [0.42, 0.81, -0.19]; p.rw = [0.42, 0.81, 0.19]; p.lha = p.rha = 0; p.lep = [-1, 0, -0.2]; p.rep = [-1, 0, 0.2]; return p; };
  const wrist = { kf: [kf(wr(0, 62), 1.8, "Gewicht vorsichtig nach vorn"), kf(wr(0.12, 54), 0.4, "Kurz halten"), kf(wr(0.12, 54), 1.8, "Gewicht zurück, nicht ruckartig"), kf(wr(0, 62), 0.4, "Kurz halten")], props: table(0.35, 1.2, 0.8), cam: { cx: 0.4, cy: 0.85, R: 1.35 } };
  const BARX = 0.2;
  const pull = (sy, ex) => {
    const p = POSE({ pel: [BARX, sy + 0.04 - 0.5, 0], tor: 90, hd: 94, lha: 90, rha: 90, lkp: [1, 0, 0], rkp: [1, 0, 0] });
    p.lw = [BARX, 2.09, -0.25]; p.rw = [BARX, 2.09, 0.25];
    p.la = [BARX - 0.22 + (ex || 0), p.pel[1] - 0.62, -0.1]; p.ra = [BARX - 0.22 + (ex || 0), p.pel[1] - 0.62, 0.1]; p.lfa = -60; p.rfa = -60;
    return p;
  };
  const pcam = { cx: 0.1, cy: 1.12, R: 1.75 };
  const pu0 = { kf: [kf(pull(1.5), 0.8, "Locker hängen, Schultern bei den Ohren"), kf(pull(1.5), 1.2, "Schulterblätter nach unten ziehen"), kf(pull(1.53), 1.0, "Arme bleiben gestreckt, Schultern weg von den Ohren"), kf(pull(1.53), 1.2, "Wieder locker lassen")], props: bar(BARX, 2.1), cam: pcam };
  const pu1 = { kf: [kf(pull(1.53), 2.5, "Hängen, 20 bis 30 Sekunden"), kf(pull(1.53, 0.04), 2.5, "Ruhig weiteratmen")], props: bar(BARX, 2.1), cam: pcam };
  const pu2 = { kf: [kf(pull(1.93), 0.6, "Start oben: Kinn über der Stange (Stuhl oder Sprung)"), kf(pull(1.93), 4.0, "Langsam absenken, 3 bis 5 Sekunden"), kf(pull(1.53), 0.6, "Unten kurz hängen"), kf(pull(1.53), 1.0, "Wieder nach oben helfen")], props: bar(BARX, 2.1), cam: pcam };
  const pu3 = { kf: [kf(pull(1.53), 0.6, "Hängen, Schulterblätter aktiv"), kf(pull(1.53), 1.8, "Hochziehen, Ellbogen nach unten"), kf(pull(1.93), 0.6, "Oben: Kinn über der Stange"), kf(pull(1.93), 2.2, "Kontrolliert absenken")], props: bar(BARX, 2.1), cam: pcam };

  /* ======== Neue Varianten: Rucksack, Tür, Boden, Sofa ======== */
  const PACK = "#2f6f5e", sh = (p) => V3.shoulderOf(p), mats = (a, b) => mat(a, b);
  const packHands = (off, s) => [{ at: "hands", off: off || [0, -0.14, 0], s: s || [0.07, 0.16, 0.17], col: PACK }];
  /* Rucksack-Rudern im Stand */
  const rbp = (tor, up, chairHand, pel) => {
    const p = POSE({ pel: pel || [-0.1, 0.8, 0], tor, hd: tor - 6, la: [0.08, 0.08, -0.13], ra: [0.08, 0.08, 0.13], lkp: [1, 0, 0], rkp: [1, 0, 0] });
    /* unten hängen die Arme leicht nach vorn, oben sind die Hände an der Hüfte und die Ellbogen hinter dem Rücken */
    const S = sh(p), t = up ? [S[0] - 0.24, S[1] - 0.3] : [S[0] + 0.07, S[1] - 0.55];
    p.lw = [t[0], t[1], -0.2]; p.rw = [t[0], t[1], 0.2]; p.lep = [-1, 0.6, -0.6]; p.rep = [-1, 0.6, 0.6]; p.lha = p.rha = null;
    if (chairHand) { p.lw = [chairHand[0], chairHand[1], -0.19]; p.lep = [0.3, -1, -0.3]; p.lha = 0; p.rw = [t[0], t[1], 0.1]; p.rep = [-1, 0.6, 0.4]; }
    return p;
  };
  const rowL = ["Rücken gerade, Rucksack hängt vor dir", "Ellbogen zur Hüfte ziehen", "Oben kurz halten, Schulterblätter zusammen", "Langsam absenken"];
  const rowSeqB = (a, b, down, up, hold) => [kf(a, 0.5, rowL[0]), kf(a, up, rowL[1]), kf(b, hold || 0.5, rowL[2]), kf(b, down, rowL[3])];
  const HINGE = [-0.2, 0.85, 0];
  const rowbp0 = { kf: rowSeqB(rbp(40, false, null, HINGE), rbp(40, true, null, HINGE), 1.6, 1.1), props: [], held: packHands(), cam: { cx: 0.12, cy: 0.62, R: 1.3 } };
  const rowbp1 = { kf: rowSeqB(rbp(40, false, null, HINGE), rbp(40, true, null, HINGE), 1.8, 1.1), props: [], held: packHands(), cam: { cx: 0.12, cy: 0.62, R: 1.3 } };
  const chH = [0.46, 0.47];
  const one1 = (single) => ({ kf: rowSeqB(rbp(26, false, chH), rbp(26, true, chH), 1.7, 1.1, single), props: chair(0.5, 0.45).map((b) => Object.assign({}, b, { z0: b.z0 - 0.26, z1: b.z1 - 0.26 })), held: [{ at: "wR", off: [0, -0.15, 0], s: [0.07, 0.16, 0.13], col: PACK }], cam: { cx: 0.2, cy: 0.6, R: 1.5 } });
  const rowbp2 = one1(0.5), rowbp3 = one1(2.0);
  rowbp3.kf[2].l = "Oben 2 Sekunden halten";
  /* Handtuch an der Tür */
  const DOORX = 1.18, ANCH = [DOORX, 1.1, 0];
  function doorRow(ax, thB, thT) {
    const mk = (th) => line(ax, 0.08, th, { lfa: -26, rfa: -26, hd: 90 + (th - 90) * 0.3, lkp: [0, 1, 0], rkp: [0, 1, 0] });
    const b = mk(thB), t = mk(thT), S = sh(b), d = V3.nrm(V3.sub(ANCH, S)), H = add(S, mul(d, 0.54));
    [b, t].forEach((p) => { p.lw = [H[0], H[1], -0.17]; p.rw = [H[0], H[1], 0.17]; p.lha = p.rha = null; p.lep = [-1, -0.2, -0.5]; p.rep = [-1, -0.2, 0.5]; });
    return { kf: [kf(b, 0.5, "Arme gestreckt, Körper eine gerade Linie"), kf(b, 1.4, "Brust zur Tür ziehen, Ellbogen nah am Körper"), kf(t, 0.5, "Oben kurz halten, Schulterblätter zusammen"), kf(t, 1.6, "Kontrolliert zurücklehnen")],
      props: [{ x0: DOORX, x1: DOORX + 0.06, y0: 0, y1: 2.1, z0: -0.55, z1: 0.55, col: "#b08a5b", alpha: 0.9 }, { x0: DOORX - 0.03, x1: DOORX, y0: 1.04, y1: 1.16, z0: -0.05, z1: 0.05, col: "#e8e4d8", alpha: 1 }], rope: ANCH, cam: { cx: 0.78, cy: 0.8, R: 1.7 } };
  }
  const rowtowel0 = doorRow(0.7, 108, 95), rowtowel1 = doorRow(0.8, 120, 98), rowtowel2 = doorRow(0.92, 132, 102);
  /* Superman-Rudern, bäuchlings */
  const sup = (lift, arms) => {
    const tor = lift ? 13 : 0, ang = lift ? 15 : 0, hip = [0.35, 0.1];
    const p = POSE({ pel: [hip[0], hip[1], 0], tor, hd: tor + 14, lkp: [0, 1, 0], rkp: [0, 1, 0], lfa: 195, rfa: 195, lha: null, rha: null });
    const leg = [hip[0] - 0.86 * Math.cos(ang * RAD), hip[1] + 0.86 * Math.sin(ang * RAD) + (lift ? 0.0 : 0)];
    p.la = [leg[0], Math.max(0.09, leg[1]), -0.1]; p.ra = [leg[0], Math.max(0.09, leg[1]), 0.1];
    const S = sh(p), wy = lift ? S[1] + 0.1 : 0.05;
    if (arms === "w") { p.lw = [S[0] + 0.18, S[1] + 0.12, -0.36]; p.rw = [S[0] + 0.18, S[1] + 0.12, 0.36]; p.lep = [-1, 0.3, -0.7]; p.rep = [-1, 0.3, 0.7]; }
    else { p.lw = [S[0] + 0.55, wy, -0.2]; p.rw = [S[0] + 0.55, wy, 0.2]; p.lep = [0, 0.4, -1]; p.rep = [0, 0.4, 1]; }
    return p;
  };
  const supCam = { cx: 0.4, cy: 0.35, R: 1.4 };
  const rowsup0 = { kf: seq(sup(false, "y"), sup(true, "y"), 1.2, 1.2, 0.5, "Brust, Arme und Beine leicht vom Boden heben", "Langsam ablegen", "Bauch am Boden, Arme nach vorn", "Oben kurz halten, Blick zum Boden"), props: mats(-0.8, 1.4), cam: supCam };
  const rowsup1 = { kf: seq(sup(true, "y"), sup(true, "w"), 1.3, 1.3, 0.4, "Ellbogen zu einem W zur Hüfte ziehen", "Arme wieder nach vorn strecken", "Arme nach vorn, Brust und Beine leicht oben", "Oben kurz halten, Schulterblätter zusammen"), props: mats(-0.8, 1.4), cam: supCam };
  rowsup1.kf[0].l = "Arme nach vorn, Brust und Beine leicht oben";
  const rowsup2 = { kf: [kf(sup(true, "y"), 0.5, "Arme nach vorn, Brust und Beine leicht oben"), kf(sup(true, "y"), 1.6, "Ellbogen zu einem W zur Hüfte ziehen"), kf(sup(true, "w"), 2.0, "Oben 2 Sekunden halten, Schulterblätter zusammen"), kf(sup(true, "w"), 1.6, "Langsam wieder nach vorn")], props: mats(-0.8, 1.4), cam: supCam };
  /* Floor Press (Rücken am Boden) */
  const sup0 = () => POSE({ pel: [0.5, 0.12, 0], tor: 0, hd: 0, la: [-0.05, 0.08, -0.14], ra: [-0.05, 0.08, 0.14], lkp: [0, 1, 0], rkp: [0, 1, 0], lha: null, rha: null });
  const fp = (top) => { const p = sup0(), S = sh(p); if (top) { p.lw = [S[0], S[1] + 0.54, -0.2]; p.rw = [S[0], S[1] + 0.54, 0.2]; p.lep = [0.3, 0, -1]; p.rep = [0.3, 0, 1]; } else { p.lw = [S[0], 0.33, -0.2]; p.rw = [S[0], 0.33, 0.2]; p.lep = [0, -0.4, -1]; p.rep = [0, -0.4, 1]; } return p; };
  const fpHeld = [{ at: "hands", off: [0, 0.0, 0], s: [0.07, 0.14, 0.15], col: PACK }];
  const fpAnim = (down) => ({ kf: seq(fp(true), fp(false), down, 1.1, 0.4, "Langsam absenken, bis die Ellbogen den Boden berühren", "Hochdrücken", "Oben: Arme gestreckt über der Brust", "Unten kurz absetzen, nicht ausruhen"), props: mats(-0.5, 1.5), held: fpHeld, cam: { cx: 0.7, cy: 0.45, R: 1.35 } });
  const pushfp0 = fpAnim(1.5), pushfp1 = fpAnim(1.6), pushfp2 = fpAnim(3.0);
  pushfp2.kf[1].l = "Langsam absenken, 3 Sekunden";
  /* Schulterdrücken im Stand */
  const ohp = (top) => { const p = feet(POSE({ pel: [0, 0.94, 0], tor: 90, hd: 90 }), 0), S = sh(p); p.lha = p.rha = null;
    if (top) { p.lw = [S[0] + 0.03, S[1] + 0.54, -0.2]; p.rw = [S[0] + 0.03, S[1] + 0.54, 0.2]; p.lep = [0.5, 0, -1]; p.rep = [0.5, 0, 1]; }
    else { p.lw = [S[0] + 0.1, S[1] + 0.02, -0.2]; p.rw = [S[0] + 0.1, S[1] + 0.02, 0.2]; p.lep = [0.1, -1, -0.5]; p.rep = [0.1, -1, 0.5]; }
    return p; };
  const ohpAnim = (down) => ({ kf: seq(ohp(false), ohp(true), 1.3, down, 0.4, "Rucksack gerade nach oben drücken", "Langsam zur Schulter absenken", "Rucksack auf Schulterhöhe, Rippen unten", "Oben: Arme gestreckt, nicht ins Hohlkreuz"), props: [], held: packHands([0, 0.0, 0], [0.07, 0.15, 0.17]), cam: { cx: 0.1, cy: 1.05, R: 1.75 } });
  const pikeohp0 = ohpAnim(1.4), pikeohp1 = ohpAnim(1.5), pikeohp2 = ohpAnim(3.0);
  pikeohp2.kf[3].l = "Langsam absenken, 3 Sekunden";
  /* Goblet-Kniebeuge (Rucksack vor der Brust) */
  const gob = (px, py, tor) => { const p = feet(POSE({ pel: [px, py, 0], tor, hd: tor + (90 - tor) * 0.6 }), 0), S = sh(p); p.lw = [S[0] + 0.2, S[1] - 0.2, -0.14]; p.rw = [S[0] + 0.2, S[1] - 0.2, 0.14]; p.lep = [0.2, -1, -0.3]; p.rep = [0.2, -1, 0.3]; p.lha = p.rha = null; return p; };
  const gobHeld = [{ at: "hands", off: [0.07, 0, 0], s: [0.07, 0.17, 0.17], col: PACK }];
  const gobA = (down) => ({ kf: seq(gob(0, 0.94, 90), gob(-0.3, 0.5, 60), down, 1.2, 0.5, "Runter, Rucksack bleibt an der Brust", "Hoch", "Aufrecht, Rucksack vor der Brust", "Unten kurz halten, Fersen am Boden"), props: [], held: gobHeld, cam: { cx: -0.05, cy: 0.75, R: 1.35 } });
  const squatgb0 = gobA(1.5), squatgb1 = gobA(1.7), squatgb2 = gobA(3.0);
  squatgb2.kf[1].l = "Langsam runter, 3 Sekunden";
  /* Step-up */
  function stepUp(h, pack) {
    const X = 0.4, top = h + 0.08;
    const arms = (p) => { if (pack) { const S = sh(p); p.lw = [S[0] + 0.2, S[1] - 0.2, -0.14]; p.rw = [S[0] + 0.2, S[1] - 0.2, 0.14]; p.lep = [0.2, -1, -0.3]; p.rep = [0.2, -1, 0.3]; p.lha = p.rha = null; return p; } return reach(p, 0.03, -0.55, 0.24); };
    const A = arms(feet(POSE({ pel: [-0.05, 0.94, 0], tor: 88, hd: 90, lkp: [1, 0, 0], rkp: [1, 0, 0] }), -0.1));
    const B = arms(POSE({ pel: [0.14, 0.64 + h * 0.6, 0], tor: 72, hd: 80, la: [X, top, -0.13], ra: [-0.1, 0.08, 0.13], lkp: [1, 0, 0], rkp: [1, 0, 0] }));
    const C = arms(POSE({ pel: [X, h + 0.94, 0], tor: 90, hd: 90, la: [X, top, -0.13], ra: [X + 0.35, h + 0.55, 0.13], rfa: -60, lkp: [1, 0, 0], rkp: [1, 0, 0] }));
    return { kf: [kf(A, 0.5, "Vor der Stufe stehen"), kf(A, 0.9, "Einen Fuß ganz auf die Stufe setzen"), kf(B, 1.2, "Mit dem vorderen Bein hochdrücken, Knie des anderen Beins hoch"), kf(C, 0.5, "Oben kurz stabil stehen"), kf(C, 1.6, "Langsam zurück, Fuß vorsichtig absetzen")],
      props: h < 0.3 ? block(0.14, 0.66, h) : chair(X, h), held: pack ? gobHeld : undefined, cam: { cx: 0.2, cy: 0.95 + h * 0.3, R: 1.95 } };
  }
  const squatsu0 = stepUp(0.17, false), squatsu1 = stepUp(0.45, false), squatsu2 = stepUp(0.45, true);
  /* Hip Thrust am Sofa */
  const hipT = (py, pack) => {
    const NKy = 0.57, tor = Math.asin(Math.max(-1, Math.min(1, (NKy - py) / 0.5))) / RAD, px = 1.0 - 0.5 * Math.cos(tor * RAD);
    const p = POSE({ pel: [px, py, 0], tor, hd: 0, la: [0.05, 0.08, -0.14], ra: [0.05, 0.08, 0.14], lkp: [0, 1, 0], rkp: [0, 1, 0], lha: null, rha: null });
    if (pack) { p.lw = [px + 0.05, py + 0.2, -0.18]; p.rw = [px + 0.05, py + 0.2, 0.18]; p.lep = [0, 0.5, -1]; p.rep = [0, 0.5, 1]; }
    else { p.lw = [1.1, 0.52, -0.5]; p.rw = [1.1, 0.52, 0.5]; p.lep = [0, 0, -1]; p.rep = [0, 0, 1]; }
    return p;
  };
  const sofa = block(0.95, 1.8, 0.45, "#8a7fa8").concat(mats(-0.5, 0.95));
  const hipA = (hold, pack, labelTop) => ({ kf: [kf(hipT(0.2, pack), 0.5, "Schultern auf dem Sofa, Hüfte unten"), kf(hipT(0.2, pack), 1.3, "Hüfte hochdrücken, Po anspannen"), kf(hipT(0.53, pack), hold, labelTop), kf(hipT(0.53, pack), 1.3, "Langsam absenken")], props: sofa, held: pack ? [{ at: "P", off: [0, 0.17, 0], s: [0.1, 0.1, 0.17], col: PACK }] : undefined, cam: { cx: 0.55, cy: 0.45, R: 1.45 } });
  const bridgehip0 = hipA(0.5, false, "Oben: von den Knien bis zu den Schultern eine Linie");
  const bridgehip1 = hipA(2.0, false, "Oben 2 Sekunden halten, Po fest");
  const bridgehip2 = hipA(1.0, true, "Oben kurz halten, Rucksack liegt auf der Hüfte");
  /* Seitstütz */
  function sidePlank(mode, b) {
    const piv = mode === 0 ? [0, 0.06] : [0, 0.1], L = mode === 0 ? 0.89 : 1.315, Sy = 0.53 + (b || 0), pOff = mode === 0 ? 0.43 : 0.855;
    const th = Math.asin((Sy - piv[1]) / L) / RAD, u = dir(th), c = Math.cos(th * RAD), s = Math.sin(th * RAD);
    const P = [piv[0] + pOff * u[0], piv[1] + pOff * u[1], 0];
    const p = POSE({ pel: P, tor: th, hd: th - 3, roll: 90, lha: null, rha: null, lfa: -10, rfa: -10, lkp: [0, -1, 0], rkp: [0, -1, 0] });
    const S = sh(p), sR = [S[0] + 0.19 * s, S[1] - 0.19 * c], sL = [S[0] - 0.19 * s, S[1] + 0.19 * c], hL = [P[0] - 0.09 * s, P[1] + 0.09 * c, 0];
    p.rw = [sR[0], 0.04, 0.26]; p.rep = [0, -1, -1]; p.lw = [sL[0], sL[1] + 0.54, 0]; p.lep = [0, 0, -1];
    if (mode === 0) { p.ra = [piv[0] - 0.43, 0.07, 0]; p.la = [piv[0] - 0.43, 0.18, 0]; }
    else { p.ra = [piv[0], 0.08, 0]; p.la = mode === 1 ? [piv[0], 0.19, 0] : add(hL, mul(dir(180 + th - 35), 0.85)); }
    return p;
  }
  const spHold = (mode, label) => ({ kf: [kf(sidePlank(mode, 0), 2.0, label), kf(sidePlank(mode, 0.012), 2.0, "Ruhig weiteratmen")], props: mats(-0.7, 1.6), face: 0, cam: { cx: 0.05, cy: 0.5, R: 1.95 } });
  const plankside0 = spHold(0, "Halten: Knie und Unterarm am Boden, Hüfte oben");
  const plankside1 = spHold(1, "Halten: Körper eine Linie, Ellbogen unter der Schulter");
  const plankside2 = spHold(2, "Halten: oberes Bein angehoben, Hüfte bleibt oben");

  const out = { squat: [squat0, squat1, squat2, squat3, squat4], push: [push0, push1, push2, push3, push4, push5, push6], pike: [pike0, pike1, pike2, pike3, pike4], row: [row0, row1, row2, row3], bridge: [br0, br1, br2, br3, br4], plank: [pl0, pl1, pl2, pl3], deadbug: [deadbug], wrist: [wrist], pullup: [pu0, pu1, pu2, pu3],
    rowbp: [rowbp0, rowbp1, rowbp2, rowbp3], rowtowel: [rowtowel0, rowtowel1, rowtowel2], rowsup: [rowsup0, rowsup1, rowsup2], pushfp: [pushfp0, pushfp1, pushfp2], pikeohp: [pikeohp0, pikeohp1, pikeohp2],
    squatgb: [squatgb0, squatgb1, squatgb2], squatsu: [squatsu0, squatsu1, squatsu2], bridgehip: [bridgehip0, bridgehip1, bridgehip2], plankside: [plankside0, plankside1, plankside2] };
  const TRK = { squat: "P", squatgb: "P", squatsu: "P", push: "neck", pushfp: "wR", pike: "head", pikeohp: "wR", row: "neck", rowbp: "wR", rowtowel: "neck", rowsup: "wR", bridge: "P", bridgehip: "P" };
  for (const k in out) out[k].forEach((a) => { if (a.track === undefined && TRK[k]) a.track = TRK[k]; });
  out.row.forEach((a) => (a.face = 1)); out.bridge.slice(0, 3).forEach((a) => (a.face = 1)); out.plank.slice(2).forEach((a) => (a.face = 1)); out.deadbug.forEach((a) => (a.face = 1));
  out.pushfp.forEach((a) => (a.face = 1)); out.bridgehip.forEach((a) => (a.face = 1));
  return out;
})();
V3A.rowband = V3A.rowtowel; V3A.rowpull = V3A.pullup;

function makeView(opts) {
  opts = opts || {};
  const { add, sub, mul, solve, mixPose, ease, RAD } = V3;
  const G = { id: null, idx: 0, anim: null, t: 0, T: 1, playing: true, speed: 1, yaw: 0, pitch: 8 * RAD, auto: false, raf: 0, last: 0, cv: null, ctx: null, W: 0, H: 0, pal: null };

  function rgbOf(css) {
    const c = document.createElement("canvas"); c.width = c.height = 1; const x = c.getContext("2d");
    x.fillStyle = css; x.fillRect(0, 0, 1, 1); const d = x.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2]];
  }
  const rgb = (c, a) => "rgba(" + Math.round(c[0]) + "," + Math.round(c[1]) + "," + Math.round(c[2]) + "," + (a == null ? 1 : a) + ")";
  const mixc = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  function palette() {
    if (opts.dark) return { acc: [241, 203, 169], ink: [247, 241, 230], bg: [77, 101, 83], muted: [238, 242, 234], dark: true, near: [214, 236, 220], far: [150, 186, 162], hot: [255, 150, 85], nose: [236, 238, 242], torso: [247, 241, 230], head: [250, 245, 236], line: [40, 58, 46], floor: [255, 255, 255], grid: [255, 255, 255], floorA: 0.06, gridA: 0.1 };
    const cs = getComputedStyle(document.documentElement), g = (n, d) => (cs.getPropertyValue(n).trim() || d);
    const acc = rgbOf(g("--accent", "#3b4bd6")), ink = rgbOf(g("--ink", "#111")), bg = rgbOf(g("--surface", "#fff")), muted = rgbOf(g("--muted", "#666"));
    const dark = (bg[0] + bg[1] + bg[2]) / 3 < 128;
    return { acc, ink, bg, muted, dark, hot: dark ? [255, 150, 85] : [226, 98, 28], nose: mixc(ink, bg, 0.65), near: dark ? [170, 206, 184] : [86, 128, 106], far: dark ? [112, 148, 126] : [52, 88, 74], torso: mixc(ink, bg, dark ? 0.35 : 0.2), head: mixc(ink, bg, dark ? 0.2 : 0.1), line: dark ? [0, 0, 0] : [255, 255, 255], floor: mixc(bg, ink, 0.07), grid: mixc(bg, ink, 0.18), floorA: 1, gridA: 0.55 };
  }

  /* Kamera */
  let C = [0, 0.8, 0], D = 5, F = 600;
  function setCam(anim) {
    const cam = G.fit || anim.cam || { cx: 0.2, cy: 0.8, R: 1.4 };
    C = [cam.cx, cam.cy, 0]; const R = cam.R * (G.fit ? (opts.zoom || 1) : (opts.zoom || 0.7)); D = R * 4; F = (Math.min(G.W, G.H * 1.2) * 0.5 / 1.12) * D / R;
  }
  function proj(p) {
    const x = p[0] - C[0], y = p[1] - C[1], z = p[2] - C[2], cy = Math.cos(G.yaw), sy = Math.sin(G.yaw), cp = Math.cos(G.pitch), sp = Math.sin(G.pitch);
    const x1 = cy * x - sy * z, z1 = sy * x + cy * z, y2 = cp * y - sp * z1, z2 = sp * y + cp * z1, dep = D - z2, s = F / dep;
    return { x: G.W / 2 + x1 * s, y: G.H * 0.5 - y2 * s, d: dep, s };
  }

  /* Kamera passt sich der Bewegung an, damit die Figur groß und vollständig im Bild ist */
  function fitCam() {
    const a = G.anim; if (!a || !G.W || !G.H) return;
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    const grow = (p, r) => { x0 = Math.min(x0, p[0] - r); x1 = Math.max(x1, p[0] + r); y0 = Math.min(y0, p[1] - r); y1 = Math.max(y1, p[1] + r); };
    for (let i = 0; i < 28; i++) { const J = solve(frame(G.T * i / 28).pose); for (const k in J) grow(J[k], k === "head" ? 0.13 : 0.06); }
    (a.held || []).forEach(() => grow([x0, y1 + 0.05], 0));
    if (y0 < 0.45) y0 = Math.min(y0, 0);
    const m = Math.min(G.W, G.H * 1.2), w = x1 - x0 + 0.3, h = y1 - y0 + 0.3;
    G.fit = { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, R: Math.max(h * 0.446 * m / G.H, w * 0.446 * m / G.W) / 0.86 };
  }
  function frame(t) {
    const k = G.anim.kf; let acc = 0, i = 0;
    for (; i < k.length; i++) { if (t < acc + k[i].d) break; acc += k[i].d; }
    if (i >= k.length) { i = k.length - 1; acc = G.T - k[i].d; }
    const a = k[i], b = k[(i + 1) % k.length], s = a.d > 0 ? Math.min(1, (t - acc) / a.d) : 1;
    return { pose: mixPose(a.p, b.p, ease(s)), label: a.l, i, s };
  }

  function faces(b) {
    const x0 = b.x0, x1 = b.x1, y0 = b.y0, y1 = b.y1, z0 = b.z0, z1 = b.z1;
    const V = [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]];
    return [[[0, 1, 2, 3], [0, 0, -1]], [[4, 5, 6, 7], [0, 0, 1]], [[0, 1, 5, 4], [0, -1, 0]], [[3, 2, 6, 7], [0, 1, 0]], [[0, 3, 7, 4], [-1, 0, 0]], [[1, 2, 6, 5], [1, 0, 0]]].map((f) => ({ pts: f[0].map((n) => V[n]), n: f[1] }));
  }
  const hex2 = (h) => rgbOf(h);

  function draw() {
    const { ctx, W, H, pal } = G; if (!ctx) return;
    ctx.clearRect(0, 0, W, H); if (!opts.transparent) { ctx.fillStyle = rgb(pal.bg); ctx.fillRect(0, 0, W, H); }
    const fr = frame(G.t), J = solve(fr.pose), items = [];
    /* Boden */
    const gx = C[0], R = (G.anim.cam && G.anim.cam.R) || 1.4, ext = Math.ceil(R * 2.2 * 2) / 2 + 0.5;
    ctx.fillStyle = rgb(pal.floor, pal.floorA);
    const fl = [[gx - ext, 0, -ext], [gx + ext, 0, -ext], [gx + ext, 0, ext], [gx - ext, 0, ext]].map(proj);
    ctx.beginPath(); fl.forEach((q, n) => (n ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y))); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = rgb(pal.grid, pal.gridA); ctx.lineWidth = 1;
    const x0 = Math.ceil((gx - ext) * 2) / 2;
    for (let x = x0; x <= gx + ext; x += 0.5) { const a = proj([x, 0, -ext]), b = proj([x, 0, ext]); ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
    for (let z = -ext; z <= ext + 1e-6; z += 0.5) { const a = proj([gx - ext, 0, z]), b = proj([gx + ext, 0, z]); ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }
    /* Schatten */
    const sh = (a, b, r) => { const pa = proj([a[0], 0, a[2]]), pb = proj([b[0], 0, b[2]]); ctx.lineCap = "round"; ctx.lineWidth = Math.max(2, 2 * r * (pa.s + pb.s) / 2); ctx.strokeStyle = "rgba(0,0,0,0.09)"; ctx.beginPath(); ctx.moveTo(pa.x, pa.y); ctx.lineTo(pb.x, pb.y); ctx.stroke(); };
    [["hL", "kL"], ["kL", "aL"], ["hR", "kR"], ["kR", "aR"], ["P", "neck"], ["sL", "sR"], ["sL", "elL"], ["elL", "wL"], ["sR", "elR"], ["elR", "wR"]].forEach(([a, b]) => sh(J[a], J[b], 0.05));
    /* Teile sammeln */
    const cap = (a, b, r, col, bias) => { const pa = proj(a), pb = proj(b); items.push({ k: "cap", pa, pb, r, col, d: (pa.d + pb.d) / 2 - (bias || 0) }); };
    const ball = (c, r, col) => { const p = proj(c); items.push({ k: "ball", p, r, col, d: p.d }); };
    const { near, far, torso, head } = pal;
    const pushBox = (b, bias) => {
      const base = hex2(b.col);
      faces(b).forEach((f) => {
        const pts = f.pts.map(proj), d = pts.reduce((a, q) => a + q.d, 0) / 4;
        const lit = 0.72 + 0.28 * Math.max(0, f.n[1] * 0.7 + f.n[0] * 0.3 + f.n[2] * 0.4);
        items.push({ k: "face", pts, col: mixc([0, 0, 0], base, Math.min(1, lit)), a: b.alpha, d: d - 0.02 + (bias || 0) });
      });
    };
    const hot = G.hot || {}, hc = pal.hot, HT = (k, base) => (hot[k] ? hc : base), mid = mul(add(J.P, J.neck), 0.5);
    cap(J.hL, J.kL, 0.062, HT("quad", far)); cap(J.kL, J.aL, 0.046, HT("calf", far)); cap(J.eL, J.tL, 0.034, far);
    cap(J.sL, J.elL, 0.042, hot.tri || hot.bi ? hc : far); cap(J.elL, J.wL, 0.034, far); cap(J.wL, J.fL, 0.03, far);
    cap(J.hR, J.kR, 0.062, HT("quad", near)); cap(J.kR, J.aR, 0.046, HT("calf", near)); cap(J.eR, J.tR, 0.034, near);
    cap(J.sR, J.elR, 0.042, hot.tri || hot.bi ? hc : near); cap(J.elR, J.wR, 0.034, near); cap(J.wR, J.fR, 0.03, near);
    cap(J.P, J.neck, 0.115, torso); cap(J.hL, J.hR, 0.06, torso); cap(J.sL, J.sR, 0.05, torso);
    if (hot.chest || hot.back) cap(mid, J.neck, 0.122, hc, 0.004);
    if (hot.core) cap(J.P, mid, 0.122, hc, 0.004);
    if (hot.glute) { cap(J.hL, J.hR, 0.095, hc, 0.004); ball(J.P, 0.105, hc); }
    if (hot.shoulder) { cap(J.sL, J.sR, 0.065, hc, 0.004); ball(J.sL, 0.062, hc); ball(J.sR, 0.062, hc); }
    cap(J.neck, J.head, 0.04, head); ball(J.head, 0.105, head);
    if (G.anim.face !== 0 && !(fr.pose.roll)) { const fa = fr.pose.hd + (G.anim.face === 1 ? 90 : -90) * 1, fv = [Math.cos(fa * RAD), Math.sin(fa * RAD), 0]; cap(J.head, add(J.head, mul(fv, 0.11)), 0.026, pal.nose, 0.02); }
    ball(J.wL, 0.04, far); ball(J.wR, 0.04, near);
    /* Gehaltene Gegenstände (Rucksack) und Seil */
    (G.anim.held || []).forEach((h) => {
      const c0 = h.at === "hands" ? mul(add(J.wL, J.wR), 0.5) : J[h.at], o = h.off || [0, 0, 0], c = [c0[0] + o[0], c0[1] + o[1], c0[2] + o[2]];
      pushBox({ x0: c[0] - h.s[0], x1: c[0] + h.s[0], y0: c[1] - h.s[1], y1: c[1] + h.s[1], z0: c[2] - h.s[2], z1: c[2] + h.s[2], col: h.col || "#2f6f5e", alpha: 1 }, -0.04);
    });
    if (G.anim.rope) { const f = G.anim.rope; [J.wL, J.wR].forEach((w) => { const pa = proj(f), pb = proj(w); items.push({ k: "line", pa, pb, d: Math.min(pa.d, pb.d) - 0.05 }); }); }
    /* Requisiten */
    (G.anim.props || []).forEach((b) => pushBox(b, 0));
    items.sort((a, b) => b.d - a.d);
    for (const it of items) {
      if (it.k === "cap") {
        const w = Math.max(2, 2 * it.r * (it.pa.s + it.pb.s) / 2);
        ctx.lineCap = "round"; ctx.strokeStyle = rgb(pal.line, 0.9); ctx.lineWidth = w + 3; ctx.beginPath(); ctx.moveTo(it.pa.x, it.pa.y); ctx.lineTo(it.pb.x, it.pb.y); ctx.stroke();
        ctx.strokeStyle = rgb(it.col); ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(it.pa.x, it.pa.y); ctx.lineTo(it.pb.x, it.pb.y); ctx.stroke();
      } else if (it.k === "line") {
        ctx.lineCap = "round"; ctx.strokeStyle = rgb(pal.ink, 0.75); ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(it.pa.x, it.pa.y); ctx.lineTo(it.pb.x, it.pb.y); ctx.stroke();
      } else if (it.k === "ball") {
        const r = it.r * it.p.s; ctx.fillStyle = rgb(it.col); ctx.strokeStyle = rgb(pal.line, 0.9); ctx.lineWidth = 3;
        ctx.beginPath(); ctx.arc(it.p.x, it.p.y, r, 0, 7); ctx.stroke(); ctx.fill();
      } else {
        ctx.globalAlpha = it.a; ctx.fillStyle = rgb(it.col); ctx.strokeStyle = "rgba(0,0,0,0.25)"; ctx.lineWidth = 1;
        ctx.beginPath(); it.pts.forEach((q, n) => (n ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y))); ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.globalAlpha = 1;
      }
    }
    /* Pfeil: wohin sich der Körper als Nächstes bewegt */
    const trk = G.anim.track;
    if (trk && G.playing !== null) {
      const ah = frame((G.t + 0.4 * Math.max(0.5, G.speed)) % G.T), J2 = solve(ah.pose), a = J[trk], b = J2[trk];
      if (a && b && V3.len(sub(b, a)) > 0.07) {
        const pa = proj(a), pb = proj(b), dx = pb.x - pa.x, dy = pb.y - pa.y, L = Math.hypot(dx, dy);
        if (L > 10) {
          const ux = dx / L, uy = dy / L, hs = Math.max(8, Math.min(14, L * 0.35));
          ctx.save(); ctx.globalAlpha = 0.92; ctx.strokeStyle = rgb(pal.hot); ctx.fillStyle = rgb(pal.hot); ctx.lineWidth = 3.5; ctx.lineCap = "round";
          ctx.beginPath(); ctx.moveTo(pa.x, pa.y); ctx.lineTo(pb.x - ux * hs * 0.6, pb.y - uy * hs * 0.6); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(pb.x, pb.y); ctx.lineTo(pb.x - ux * hs - uy * hs * 0.55, pb.y - uy * hs + ux * hs * 0.55); ctx.lineTo(pb.x - ux * hs + uy * hs * 0.55, pb.y - uy * hs - ux * hs * 0.55); ctx.closePath(); ctx.fill(); ctx.restore();
        }
      }
    }
    return fr;
  }

  function size() {
    const cv = G.cv; if (!cv) return;
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    G.W = Math.max(200, cv.clientWidth); G.H = Math.max(150, cv.clientHeight);
    cv.width = G.W * dpr; cv.height = G.H * dpr; G.ctx = cv.getContext("2d"); G.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (G.anim) { fitCam(); setCam(G.anim); }
  }
  function uiPhase(fr) {
    if (opts.noUi) return;
    const el = document.getElementById("v3-phase"), sl = document.getElementById("v3-scrub");
    if (el && fr && el.dataset.i !== String(fr.i)) { el.dataset.i = String(fr.i); el.textContent = (G.anim.kf.length > 2 ? (fr.i + 1) + " von " + G.anim.kf.length + ": " : "") + (fr.label || ""); }
    if (sl && document.activeElement !== sl) sl.value = String(Math.round(G.t / G.T * 1000));
  }
  function tick(ts) {
    G.raf = requestAnimationFrame(tick);
    const dt = G.last ? Math.min(0.05, (ts - G.last) / 1000) : 0; G.last = ts;
    if (G.playing) G.t = (G.t + dt * G.speed) % G.T;
    if (G.auto) G.yaw += dt * 0.5;
    uiPhase(draw());
  }
  function setAnim(id, idx) {
    G.id = id; G.idx = idx; G.anim = V3A[id][idx]; G.hot = (typeof MAPX !== "undefined" && MAPX[id]) || {}; G.T = G.anim.kf.reduce((a, k) => a + k.d, 0); G.t = 0; G.pal = palette();
    if (!opts.noUi) { const el = document.getElementById("v3-phase"); if (el) el.dataset.i = ""; }
    G.fit = null; size(); if (G.anim) { fitCam(); setCam(G.anim); }
  }
  function start() { stop(); G.last = 0; G.raf = requestAnimationFrame(tick); }
  function stop() { cancelAnimationFrame(G.raf); G.raf = 0; }
  function bindCanvas(cv) {
    G.cv = cv; let drag = null;
    cv.addEventListener("pointerdown", (e) => { drag = { x: e.clientX, y: e.clientY }; try { cv.setPointerCapture(e.pointerId); } catch (x) {} G.auto = false; const b = document.getElementById("v3-auto"); if (b) b.setAttribute("aria-pressed", "false"); });
    cv.addEventListener("pointermove", (e) => { if (!drag) return; G.yaw -= (e.clientX - drag.x) * 0.012; G.pitch = Math.max(-0.1, Math.min(1.5, G.pitch + (e.clientY - drag.y) * 0.01)); drag = { x: e.clientX, y: e.clientY }; if (!G.playing) uiPhase(draw()); });
    const up = () => { drag = null; }; cv.addEventListener("pointerup", up); cv.addEventListener("pointercancel", up);
    cv.addEventListener("keydown", (e) => { const m = { ArrowLeft: [-0.15, 0], ArrowRight: [0.15, 0], ArrowUp: [0, -0.08], ArrowDown: [0, 0.08] }[e.key]; if (m) { e.preventDefault(); G.yaw += m[0]; G.pitch = Math.max(-0.1, Math.min(1.5, G.pitch + m[1])); if (!G.playing) uiPhase(draw()); } });
    window.addEventListener("resize", () => { if (G.raf) { size(); } });
  }
  const view = (name) => { const v = { side: [0, 8], front: [90, 8], angle: [40, 22], top: [0, 84], start: [26, 13], mini: [20, 9] }[name]; if (v) { G.yaw = v[0] * RAD; G.pitch = v[1] * RAD; if (!G.playing) uiPhase(draw()); } };
  return { G, setAnim, start, stop, bindCanvas, size, view, draw, uiPhase };
}
const V3View = makeView();
const V3Mini = makeView({ noUi: true, dark: true, transparent: true, zoom: 1 });

/* Bedienung der 3D-Ansicht */
const V3KEY = { "Dead Bug": "deadbug", "Klimmzug-Vorstufen": "pullup", "Handgelenke aufwärmen": "wrist" };
const V3X = { deadbug: ["Dead Bug", ["Dead Bug"]], wrist: ["Handgelenke aufwärmen", ["Handgelenke aufwärmen"]], pullup: ["Klimmzug-Vorstufen", ["Schulterblätter aktivieren", "Hängen, 20 bis 30 Sekunden", "Negative Klimmzüge", "Klimmzug"]] };
let v3cur = null;
function v3Works(id) {
  const m = MAPX[id]; if (!m) return "";
  return Object.keys(m).sort((a, b) => m[b] - m[a]).map((k) => { const n = (MUSC.find((x) => x[0] === k) || [0, k])[1]; return m[k] >= 1 ? "<b>" + n + "</b>" : n; }).join(", ");
}
function v3Info(id) {
  const e = exById(id);
  if (e) return { title: e.name, sub: e.reps, names: e.ladder, cue: e.cue, mistakes: e.mistakes, cur: lvl(e), need: e.need || "", works: v3Works(e.id), slot: e.slot };
  const x = V3X[id]; if (!x) return null;
  const ex = EXTRAS.find((q) => q.name === x[0]);
  return { title: x[0], sub: ex ? ex.sub : "", names: x[1], cue: ex ? ex.text : "", mistakes: "", cur: 0, need: "", works: "", slot: null };
}
function v3Vars() {
  const g = v3cur.g, box = $("#v3-vars");
  box.hidden = g.names.length < 2;
  box.innerHTML = g.names.map((n, i) => '<button class="btn" type="button" data-v3i="' + i + '" aria-pressed="false"><b>' + (i + 1) + "</b> " + n + (v3cur.id === "pullup" ? "" : (i === g.cur ? " (deine Stufe)" : "")) + "</button>").join("");
}
function v3Select(i) {
  v3cur.idx = i;
  $$("#v3-vars [data-v3i]").forEach((b) => b.setAttribute("aria-pressed", String(parseInt(b.dataset.v3i, 10) === i)));
  V3View.setAnim(v3cur.id, i);
  const G = V3View.G;
  G.playing = !reduceMotion(); if (!G.playing) G.t = G.T * 0.4;
  v3Play();
  V3View.start();
}
function v3Alts(id) {
  const box = $("#v3-alts"), e = exById(id), list = e ? slotVariants(e.slot).filter((x) => V3A[x.id]) : [];
  box.hidden = list.length < 2;
  box.innerHTML = list.length < 2 ? "" : '<span class="small muted">Andere Variante dieser Übung:</span>' + list.map((x) => '<button class="btn" type="button" data-v3alt="' + x.id + '" aria-pressed="' + (x.id === id) + '">' + x.name + "</button>").join("");
}
function v3Play() {
  const G = V3View.G, b = $("#v3-play");
  b.textContent = G.playing ? "Pause" : "Abspielen";
}
function openV3(id, idx, src) {
  const g = v3Info(id); if (!g || !V3A[id]) return;
  if (idx == null || isNaN(idx)) idx = g.cur;
  idx = Math.max(0, Math.min(V3A[id].length - 1, idx));
  v3cur = { id, g, idx };
  $("#v3-title").textContent = g.title; $("#v3-sub").textContent = g.sub;
  $("#v3-txt").innerHTML = (g.works ? '<p class="v3works"><span class="hotdot" aria-hidden="true"></span> Hier arbeitet: ' + g.works + ". Die orange markierten Teile sind die beanspruchten Muskeln, der Pfeil zeigt die Bewegung.</p>" : "") + (g.need ? '<p class="small muted">Du brauchst: ' + g.need + "</p>" : "") + "<p>" + g.cue + "</p>" + (g.mistakes ? '<p class="mistake"><b>Häufige Fehler:</b> ' + g.mistakes + "</p>" : "");
  v3Vars(); v3Alts(id);
  if (!$("#dlg-3d").open) showDialog($("#dlg-3d"), src);
  requestAnimationFrame(() => { V3View.view("start"); v3Select(idx); if (!src || !src.closest || !src.closest("#dlg-3d")) $("#v3-cv").focus({ preventScroll: true }); });
}
let coachKey = "";
function coachFig() {
  const box = $("#coachfig"); if (!box || typeof V3Mini === "undefined") return;
  const p = W.phase, show = ["prep", "work", "hold", "rest"].includes(p);
  box.hidden = !show;
  if (!show) { V3Mini.stop(); coachKey = ""; return; }
  const e = EX[Math.min(p === "rest" ? nextPos().ex : W.ex, EX.length - 1)], idx = lvl(e), key = e.id + ":" + idx;
  if (!V3A[e.id]) { box.hidden = true; V3Mini.stop(); coachKey = key; return; }
  if (key !== coachKey) { coachKey = key; V3Mini.size(); V3Mini.setAnim(e.id, idx); V3Mini.view("mini"); }
  if (reduceMotion()) { V3Mini.G.playing = false; V3Mini.G.t = V3Mini.G.T * 0.4; V3Mini.draw(); V3Mini.stop(); return; }
  if (!V3Mini.G.raf) V3Mini.start();
}
function bindV3() {
  V3Mini.bindCanvas($("#coach-cv"));
  V3View.bindCanvas($("#v3-cv"));
  $("#x-3d").innerHTML = ic("close");
  $("#dlg-3d").addEventListener("close", () => V3View.stop());
  $("#dlg-cook").addEventListener("close", () => { ckStop(); unwake(); });
  $("#v3-scrub").addEventListener("input", (e) => { const G = V3View.G; G.playing = false; G.t = (parseInt(e.target.value, 10) / 1000) * G.T; v3Play(); V3View.uiPhase(V3View.draw()); });
  $("#v3-play").addEventListener("click", () => { const G = V3View.G; G.playing = !G.playing; v3Play(); });
  $("#v3-speed").addEventListener("click", () => { const G = V3View.G; G.speed = G.speed === 1 ? 0.5 : G.speed === 0.5 ? 0.25 : 1; $("#v3-speed").textContent = "Tempo " + String(G.speed).replace(".", ",") + "×"; });
  $("#v3-auto").addEventListener("click", () => { const G = V3View.G; G.auto = !G.auto; $("#v3-auto").setAttribute("aria-pressed", String(G.auto)); });
  $$("[data-v3view]").forEach((b) => b.addEventListener("click", () => { V3View.G.auto = false; $("#v3-auto").setAttribute("aria-pressed", "false"); V3View.view(b.dataset.v3view); }));
  $("#v3-vars").addEventListener("click", (e) => { const b = e.target.closest("[data-v3i]"); if (b) v3Select(parseInt(b.dataset.v3i, 10)); });
  $("#v3-alts").addEventListener("click", (e) => { const b = e.target.closest("[data-v3alt]"); if (b) openV3(b.dataset.v3alt, null, b); });
}
