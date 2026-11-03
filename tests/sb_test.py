import json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
ROWS={}   # (uid,k)->{k,t,v}
STATE={"valid":set(),"n":0,"users":{"a@b.de":"geheim123"},"offline":False}
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def _send(self,code,obj=None):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS")
        self.send_header("Content-Type","application/json"); self.end_headers()
        if obj is not None: self.wfile.write(json.dumps(obj).encode())
    def do_OPTIONS(self): self._send(204)
    def _body(self):
        n=int(self.headers.get("Content-Length") or 0); return json.loads(self.rfile.read(n) or b"{}")
    def _tok(self):
        a=self.headers.get("Authorization","").replace("Bearer ","")
        return a if a in STATE["valid"] else None
    def do_POST(self):
        u=urlparse(self.path); q=parse_qs(u.query)
        if STATE["offline"]: return self._send(503,{})
        if u.path=="/auth/v1/token":
            b=self._body()
            if q["grant_type"][0]=="password":
                if STATE["users"].get(b.get("email"))!=b.get("password"): return self._send(400,{"error_description":"Invalid login credentials"})
            else:
                if b.get("refresh_token")!="rt-ok": return self._send(400,{"error_description":"bad refresh"})
            STATE["n"]+=1; t="at-%d"%STATE["n"]; STATE["valid"].add(t)
            return self._send(200,{"access_token":t,"refresh_token":"rt-ok","expires_in":3600})
        if u.path=="/auth/v1/signup":
            b=self._body(); STATE["users"][b["email"]]=b["password"]; STATE["n"]+=1; t="at-%d"%STATE["n"]; STATE["valid"].add(t)
            return self._send(200,{"access_token":t,"refresh_token":"rt-ok","expires_in":3600})
        if u.path=="/rest/v1/kv":
            if not self._tok(): return self._send(401,{})
            for r in self._body(): ROWS[("u1",r["k"])]=dict(r)
            return self._send(201)
        self._send(404)
    def do_GET(self):
        u=urlparse(self.path)
        if STATE["offline"]: return self._send(503,{})
        if u.path=="/rest/v1/kv":
            if not self._tok(): return self._send(401,{})
            return self._send(200,[v for (uid,k),v in ROWS.items()])
        self._send(404)
srv=ThreadingHTTPServer(("127.0.0.1",8765),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
URL=__import__("fcenv").APP_URL; SB="http://127.0.0.1:8765"
errs=[]
def dev(b,w=1300):
    c=b.new_context(viewport={"width":w,"height":900}); pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: errs.append(m.text) if m.type=="error" and "503" not in m.text and "Failed to load" not in m.text else None)
    return c,pg
def login(pg,pw="geheim123",signup=False):
    pg.evaluate("document.getElementById('b-settings').click()")
    pg.evaluate("document.getElementById('sbbox').open=true")
    pg.fill("#sb-url",SB); pg.fill("#sb-key","anon-key"); pg.fill("#sb-mail","a@b.de"); pg.fill("#sb-pw",pw)
    pg.click("#sb-signup" if signup else "#sb-login"); pg.wait_for_timeout(1500)
with sync_playwright() as p:
    b=p.chromium.launch()
    cA,A=dev(b); A.goto(URL); A.wait_for_timeout(500)
    print("A mode",A.evaluate("FC.mode"))
    A.evaluate("document.getElementById('b-settings').click()"); A.evaluate("document.getElementById('sbbox').open=true")
    A.fill("#sb-url","http://127.0.0.1:8765"); A.fill("#sb-key","k"); A.fill("#sb-mail","a@b.de"); A.fill("#sb-pw","falsch"); A.click("#sb-login"); A.wait_for_timeout(800)
    print("falsches Passwort ->",A.inner_text("#sbmsg"))
    A.fill("#sb-pw","geheim123"); A.click("#sb-login"); A.wait_for_timeout(2000)
    print("A mode nach Login",A.evaluate("FC.mode"),"state",A.evaluate("FC.state()"))
    A.evaluate("GOALS.kcal=2345; saveToday()"); A.wait_for_timeout(2500)
    print("rows",sorted(k for (_,k) in ROWS),"A state",A.evaluate("FC.state()"))
    # Gerät B
    cB,B=dev(b); B.goto(URL); B.wait_for_timeout(300)
    login(B); B.wait_for_timeout(1500)
    print("B goals",B.evaluate("GOALS.kcal"),"mode",B.evaluate("FC.mode"))
    # 401 -> Refresh
    STATE["valid"].clear()
    B.evaluate("GOALS.kcal=2400; saveToday()"); B.wait_for_timeout(2500)
    print("nach Token-Ablauf remote kcal",json.loads(ROWS[("u1","fc_goals")]["v"])["kcal"],"state",B.evaluate("FC.state()"))
    # Offline-Edit -> später nachholen
    STATE["offline"]=True
    B.evaluate("GOALS.kcal=2600; saveToday()"); B.wait_for_timeout(2500)
    print("offline:",B.evaluate("FC.state()"),B.evaluate("FC.dirtyCount()"))
    STATE["offline"]=False
    B.evaluate("FC.syncNow()"); B.wait_for_timeout(2500)
    print("nachgeholt:",B.evaluate("FC.state()"),json.loads(ROWS[("u1","fc_goals")]["v"])["kcal"])
    # A zieht per Sichtbarkeit (Poll simuliert)
    A.evaluate("FC.syncNow()"); A.wait_for_timeout(2500)
    print("A kcal nach Sync",A.evaluate("GOALS.kcal"))
    # Logout
    B.evaluate("document.getElementById('b-settings').click()"); B.evaluate("document.getElementById('sbbox').open=true"); B.click("#sb-logout"); B.wait_for_timeout(1200)
    print("B nach Logout",B.evaluate("FC.mode"),B.evaluate("GOALS.kcal"))
    # Offline beim Start mit schon synchronisiertem Gerät
    STATE["offline"]=True
    A.reload(); A.wait_for_timeout(2500)
    print("A offline-Start: state",A.evaluate("FC.state()"),"kcal",A.evaluate("GOALS.kcal"))
    A.evaluate("GOALS.kcal=3000; saveToday()"); A.wait_for_timeout(500)
    STATE["offline"]=False; A.wait_for_timeout(17000)
    print("A nach Rückkehr: state",A.evaluate("FC.state()"),"remote",json.loads(ROWS[("u1","fc_goals")]["v"])["kcal"])
    b.close()
print("ERRORS",errs[:6])
