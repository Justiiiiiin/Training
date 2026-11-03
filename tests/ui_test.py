"""Oberfläche: Kontrast (WCAG AA), Tap-Ziele (mindestens 24 px, WCAG 2.5.8) und kein seitlicher Überlauf.
Hell bei 320 px und dunkel bei 390 px, alle Tabs und die wichtigsten Dialoge."""
from playwright.sync_api import sync_playwright
URL = __import__("fcenv").APP_URL
fails = []
def ck(n, c, info=""):
    print(("OK   " if c else "FAIL ") + n, info)
    if not c: fails.append(n)
SCAN = r"""() => {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 }; };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const blend = (top, bot) => ({ r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1 });
  const bgOf = (el) => { const chain = []; for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) { chain.push(c); if (c.a >= 1) break; } if (getComputedStyle(e).backgroundImage !== 'none') return null; }
    let bg = parse(getComputedStyle(document.body).backgroundColor) || { r: 255, g: 255, b: 255, a: 1 }; for (let i = chain.length - 1; i >= 0; i--) bg = blend(chain[i], bg); return bg; };
  const vis = (e) => { const r = e.getBoundingClientRect(); if (!r.width || !r.height) return false; const s = getComputedStyle(e); return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const out = { contrast: {}, tap: {}, overflow: [] };
  const W = innerWidth;
  document.querySelectorAll('body *').forEach((e) => {
    if (!vis(e) || e.closest('svg') || e.closest('canvas')) return;
    const own = Array.from(e.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
    if (own && !e.closest('.tab[aria-selected="true"], .gbtn[aria-selected="true"]')) {
      const s = getComputedStyle(e), fg = parse(s.color), bg = bgOf(e);
      if (fg && bg) {
        const f = fg.a < 1 ? blend(fg, bg) : fg, L1 = lum(f), L2 = lum(bg), cr = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
        const size = parseFloat(s.fontSize), bold = +s.fontWeight >= 700, large = size >= 24 || (bold && size >= 18.66);
        const need = large ? 3 : 4.5;
        if (cr < need && !e.closest('[disabled]') && !e.matches(':disabled')) {
          const k = (e.tagName + '.' + (typeof e.className === 'string' ? e.className.split(' ')[0] : '')) + ' "' + e.textContent.trim().slice(0, 22) + '"';
          out.contrast[k] = Math.round(cr * 100) / 100 + ' < ' + need;
        }
      }
    }
    if (e.matches('button, a[href], [role=button], input:not([type=hidden]), select, summary, label.check, [tabindex="0"]')) {
      const r = e.getBoundingClientRect(); let hit = r;
      const lab = e.closest('label'); if (lab && e.matches('input')) hit = lab.getBoundingClientRect();
      if (hit.width < 44 || hit.height < 44) {
        const k = (e.tagName + '.' + (typeof e.className === 'string' ? e.className.split(' ')[0] : '') + (e.id ? '#' + e.id : '')) + ' ' + Math.round(hit.width) + 'x' + Math.round(hit.height);
        if (hit.width < 24 || hit.height < 24) out.tap['!' + k] = 1; else out.tap[k] = 1;
      }
    }
    const r = e.getBoundingClientRect();
    if ((r.right > W + 1 || r.left < -1) && getComputedStyle(e).position !== 'fixed' && !e.closest('.tabs, .rcard .tags, .seg, .rscroll, [data-scroll]')) {
      let p = e.parentElement, clipped = false; for (; p; p = p.parentElement) { const ov = getComputedStyle(p).overflowX; if (ov === 'auto' || ov === 'scroll' || ov === 'hidden') { clipped = true; break; } }
      if (!clipped) out.overflow.push(e.tagName + '.' + e.className);
    }
  });
  out.overflow = [...new Set(out.overflow)].slice(0, 5); out.sw = document.documentElement.scrollWidth;
  return out;
}"""
TABS = ["heute", "uebungen", "tipps", "ausblick", "rezepte", "rad", "vorkochen", "einkauf", "ernaehrung", "fortschritt"]
DLG = [("Essen", "openEat()"), ("Einstellungen", "openSettings()"), ("Rezept", "openRecipe(RECIPES[0].id)"), ("Kochen", "openCook(RECIPES[0].id)"), ("Training", "openSummary(WK.length-1)"), ("3D", "openV3(EX[0].id)")]
with sync_playwright() as p:
    b = p.chromium.launch()
    for scheme, w in [("light", 320), ("dark", 390)]:
        c = b.new_context(viewport={"width": w, "height": 760}, color_scheme=scheme, reduced_motion="reduce", has_touch=True, is_mobile=True)  # ohne Farbübergänge, sonst misst man Zwischenstände
        pg = c.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(800)
        pg.evaluate("() => { logEat(RECIPES[0],1); cartAdd(RECIPES[1].id,1); saveEntry({weight:80, waist:90}); sessions.push(todayISO()); store.set('fc_sessions', sessions); WK.push({date:todayISO(),min:30,sets:[{ex:EX[0].id,lvl:0,set:1,reps:10,secs:null}],effort:'',q:0}); saveToday(); RPL.day = radBuild(); saveRad(); radShowAll(); radRender(); }")
        res = []
        for t in TABS:
            pg.evaluate(f"showTab('{t}')"); pg.wait_for_timeout(120); pg.evaluate("document.querySelectorAll('.panel details').forEach(d => d.open = true)")
            res.append((t, pg.evaluate(SCAN)))
        for n, js in DLG:
            pg.evaluate(js); pg.wait_for_timeout(300)
            res.append(("Dialog " + n, pg.evaluate(SCAN)))
            pg.evaluate("document.querySelectorAll('dialog[open]').forEach(d => d.close())")
        tag = f"{scheme} {w} px"
        con = {k: v for _, r in res for k, v in r["contrast"].items()}
        tiny = sorted({k[1:] + " (" + where + ")" for where, r in res for k in r["tap"] if k.startswith("!")})
        over = [(where, r["sw"], r["overflow"]) for where, r in res if r["overflow"] or r["sw"] > w]
        ck(tag + ": Kontrast überall mindestens WCAG AA", not con, str(list(con.items())[:4]))
        ck(tag + ": keine Tap-Ziele unter 24 px", not tiny, str(tiny[:4]))
        ck(tag + ": kein seitlicher Überlauf", not over, str(over[:3]))
        ck(tag + ": keine Fehler", not errs, str(errs[:2]))
        c.close()
    b.close()
print("FAILS", fails)
