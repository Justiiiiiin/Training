"""Körpergeometrie der Animationen: Pike-Liegestütze und Rucksack-Rudern (Gelenke aus V3.solve)."""
import sys
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
errs = []; fails = []


def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)


JS = """
() => {
  const out = { pike: [], rowbp: [] };
  const uniq = (an) => { const seen = new Set(), r = []; an.kf.forEach((k) => { const key = JSON.stringify(k.p); if (!seen.has(key)) { seen.add(key); r.push(k.p); } }); return r; };
  V3A.pike.forEach((an, li) => {
    const [top, bot] = uniq(an).map((p) => ({ p, J: V3.solve(p) }));
    const d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
    out.pike.push({ li,
      wristErr: Math.max(d(top.J.wL, top.p.lw), d(bot.J.wL, bot.p.lw), d(top.J.wR, top.p.rw), d(bot.J.wR, bot.p.rw)),
      ankleErr: Math.max(d(top.J.aL, top.p.la), d(bot.J.aL, bot.p.la)),
      shTopX: top.J.neck[0], shBotX: bot.J.neck[0], wristX: top.J.wL[0], wristY: top.J.wL[1],
      hipTop: top.J.P[1], hipBot: bot.J.P[1], neckTop: top.J.neck[1], neckBot: bot.J.neck[1],
      elbowBotY: bot.J.elL[1], headBotY: bot.J.head[1], armTop: d(top.J.sL, top.J.elL) + d(top.J.elL, top.J.wL), reachTop: d(top.J.sL, top.J.wL),
      legStretch: d(top.J.hL, top.J.aL) });
  });
  V3A.rowbp.forEach((an, li) => {
    const ps = uniq(an), a = V3.solve(ps[0]), b = V3.solve(ps[ps.length - 1]);
    const ex = V3A.rowbp[li].kf.map((k) => V3.solve(k.p));
    let hang = ex[0], top = ex[0];
    ex.forEach((j) => { if (j.wR[1] < hang.wR[1]) hang = j; if (j.wR[1] > top.wR[1]) top = j; });
    out.rowbp.push({ li, rise: top.wR[1] - hang.wR[1], back: hang.wR[0] - top.wR[0], hangUnderShoulder: hang.wR[0] - hang.sR[0], elbowAboveBackTop: top.elR[1] - (top.P[1] + (top.sR[1] - top.P[1]) * ((top.elR[0] - top.P[0]) / (top.sR[0] - top.P[0] || 1))), hipY: top.P[1], torso: Math.atan2(top.neck[1] - top.P[1], top.neck[0] - top.P[0]) * 180 / Math.PI });
  });
  return out;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_function("window.__fcReady === true", timeout=15000)
    r = pg.evaluate(JS)
    for q in r["pike"]:
        n = "Pike %d" % q["li"]
        ck(n + ": Hände bleiben auf dem Griffpunkt (Arme nicht zu kurz)", q["wristErr"] < 0.02, "%.3f" % q["wristErr"])
        ck(n + ": Füße bleiben stehen", q["ankleErr"] < 0.02, "%.3f" % q["ankleErr"])
        ck(n + ": Arme oben fast gestreckt", q["reachTop"] > 0.48, "%.2f" % q["reachTop"])
        ck(n + ": Beine gestreckt (Hüfte oben)", q["legStretch"] > 0.8, "%.2f" % q["legStretch"])
        ck(n + ": Schultern sinken", q["neckBot"] < q["neckTop"] - 0.08, "%.2f -> %.2f" % (q["neckTop"], q["neckBot"]))
        ck(n + ": Hüfte sinkt höchstens 0,25 m", q["hipTop"] - q["hipBot"] < 0.25, "%.2f -> %.2f" % (q["hipTop"], q["hipBot"]))
        if q["li"] > 0:
            ck(n + ": Schultern wandern nach vorn (Kopf zwischen die Hände)", q["shBotX"] > q["shTopX"] + 0.05, "%.2f -> %.2f" % (q["shTopX"], q["shBotX"]))
            ck(n + ": Ellbogen unten nicht am Boden", q["elbowBotY"] > 0.15, "%.2f" % q["elbowBotY"])
            ck(n + ": Kopf berührt den Boden nicht", q["headBotY"] > 0.15, "%.2f" % q["headBotY"])
        else:
            ck(n + ": Hüfte höher als Schulter (umgedrehtes V)", q["hipTop"] > q["neckTop"] - 0.02, "%.2f / %.2f" % (q["hipTop"], q["neckTop"]))
    for q in r["rowbp"]:
        n = "Rucksack-Rudern %d" % q["li"]
        ck(n + ": Rucksack wandert mindestens 20 cm hoch", q["rise"] > 0.2, "%.2f" % q["rise"])
        ck(n + ": und mindestens 15 cm nach hinten zur Hüfte", q["back"] > 0.15, "%.2f" % q["back"])
        ck(n + ": Oberkörper vorgebeugt (20 bis 50 Grad)", 20 <= q["torso"] <= 50, "%.0f" % q["torso"])
    ck("Keine Seitenfehler", not errs, "; ".join(errs[:3]))
    b.close()
print("FAILS:", fails)
sys.exit(1 if fails else 0)
