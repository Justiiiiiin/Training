import json, time
from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
DB={}   # path -> data
FAIL={"on":False}
FAKE = """
(() => {
  const call = (op, path, data) => window.__db(op, path, data === undefined ? null : JSON.stringify(data)).then(r => r === null ? null : JSON.parse(r));
  const mkDoc = (path, exists, data) => ({ id: path.split('/').pop(), exists, data: () => data, metadata: {} });
  const doc = (path) => ({ id: path.split('/').pop(), path,
    get: async () => { const d = await call('get', path); return mkDoc(path, d !== null, d || undefined); },
    set: async (data) => { await call('set', path, data); },
    delete: async () => { await call('del', path); } });
  const col = (path) => ({ path, doc: (id) => doc(path + '/' + id),
    get: async () => { const r = await call('list', path); return { docs: r.map(([id, d]) => mkDoc(path + '/' + id, true, d)) }; },
    onSnapshot: (next) => { let last = ''; const run = async () => { try { const r = await call('list', path); const sig = JSON.stringify(r); if (sig !== last) { last = sig; next({ docs: r.map(([id, d]) => mkDoc(path + '/' + id, true, d)) }); } } catch (e) {} }; const iv = setInterval(run, 400); run(); return () => clearInterval(iv); } });
  window.claude = { use: async (n) => n === 'db' ? { doc, collection: col } : n === 'user' ? { id: async () => 'u_test1' } : null };
})();
"""
def attach(ctx):
    def handler(source, op, path, data):
        if FAIL["on"] and op in ("set","del"): raise Exception("offline")
        d = json.loads(data) if data else None
        if op=="get": return json.dumps(DB[path]) if path in DB else None
        if op=="set": DB[path]=d; return None
        if op=="del": DB.pop(path,None); return None
        if op=="list":
            pre=path+"/"; return json.dumps([[k[len(pre):],v] for k,v in sorted(DB.items()) if k.startswith(pre) and "/" not in k[len(pre):]])
    ctx.expose_binding("__db", handler)
    ctx.add_init_script(FAKE)
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch()
    def dev():
        c=b.new_context(viewport={"width":1300,"height":900}); attach(c); pg=c.new_page()
        pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
        return c,pg
    # Gerät A: Daten anlegen
    cA,A=dev(); A.goto(URL); A.wait_for_timeout(1500)
    print("A embedded",A.evaluate("FC.embedded"),"state",A.evaluate("FC.state()"),"chip",A.inner_text("#syncst"))
    A.evaluate("GOALS.kcal=2222; GOALS.protein=140; saveToday(); logEat && 0")
    A.evaluate("addWater && addWater()")
    A.wait_for_timeout(3000)
    print("A state",A.evaluate("FC.state()"),"dirty",A.evaluate("FC.dirtyCount()"))
    print("DB keys",sorted(k.split('/')[-1] for k in DB))
    # Gerät B: frisch, soll Daten ziehen
    cB,B=dev(); B.goto(URL); B.wait_for_timeout(2500)
    print("B goals",B.evaluate("GOALS"),"water",B.evaluate("JSON.stringify(dayGet().water)"))
    # B ändert -> A bekommt es (Reload)
    B.evaluate("GOALS.kcal=2500; saveToday()"); B.wait_for_timeout(3500)
    A.wait_for_timeout(4500)
    print("A goals after B edit",A.evaluate("GOALS.kcal"))
    # Offline-Schreiben auf A und danach wieder online
    FAIL["on"]=True
    A.evaluate("GOALS.kcal=2700; saveToday()"); A.wait_for_timeout(2500)
    print("offline state",A.evaluate("FC.state()"),"dirty",A.evaluate("FC.dirtyCount()"),"chip",A.inner_text("#syncst"))
    FAIL["on"]=False
    A.evaluate("FC.syncNow()"); A.wait_for_timeout(2500)
    print("back online",A.evaluate("FC.state()"),"dirty",A.evaluate("FC.dirtyCount()"),"remote kcal",json.loads(DB["data/users/u_test1/fc_goals"]["v"])["kcal"])
    # Große Daten (Chunking)
    A.evaluate("for(let i=0;i<2500;i++){ DIARY['2020-01-'+String(i)]={items:[{n:'x'.repeat(80),kcal:1}],water:0}; } saveToday()"); A.wait_for_timeout(3500)
    print("chunk docs",[k.split('/')[-1] for k in DB if 'fc_diary' in k], "meta",{k:v for k,v in DB['data/users/u_test1/fc_diary'].items() if k!='v'})
    cC,C=dev(); C.goto(URL); C.wait_for_timeout(3000)
    print("C diary size",C.evaluate("Object.keys(DIARY).length"))
    # Backup / Restore
    exp=C.evaluate("FC.exportAll()"); print("export bytes",len(exp))
    cD,Dd=dev(); Dd.goto(URL); Dd.wait_for_timeout(2500)
    Dd.evaluate("document.getElementById('b-settings').click()"); Dd.fill("#t-restore",exp); Dd.click("#b-restore"); Dd.wait_for_timeout(2500)
    print("restore msg ok; D diary",Dd.evaluate("Object.keys(DIARY).length"))
    # Falsches Format
    Dd.evaluate("document.getElementById('b-settings').click()")
    Dd.fill("#t-restore","{kaputt"); Dd.click("#b-restore"); print("bad restore:",Dd.inner_text("#restoremsg"))
    # Fehler bei db == null
    c=b.new_context(); c.add_init_script("window.claude={use:async()=>null}"); pg=c.new_page(); pg.on("pageerror",lambda e:errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(1500)
    print("no db -> state",pg.evaluate("FC.state()"),)
    pg.evaluate("GOALS.kcal=2100; saveToday()"); pg.reload(); pg.wait_for_timeout(1500); print("persist without db",pg.evaluate("GOALS.kcal"))
    b.close()
print("ERRORS",errs[:8])
