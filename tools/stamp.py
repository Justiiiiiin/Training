import re,datetime,zoneinfo,sys
import os
p=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"index.html")
s=open(p,encoding="utf-8").read()
now=datetime.datetime.now(zoneinfo.ZoneInfo("Europe/Berlin")).strftime("%d.%m. %H:%M")
m=re.search(r'(<span class="ver" id="appver"[^>]*>)([^<]*)(</span>)',s)
old=m.group(2); mv=re.search(r'v(\d+)\.(\d+)',old)
major,minor=(int(mv.group(1)),int(mv.group(2))) if mv else (3,0)
if "--major" in sys.argv: major,minor=major+1,0
else: minor+=1
txt=f"v{major}.{minor} · {now}"
s=s[:m.start(2)]+txt+s[m.end(2):]
open(p,"w",encoding="utf-8").write(s); print(txt)
