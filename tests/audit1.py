import json, random
from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
errs=[]
def newpage(b, init=None, w=1360):
    c=b.new_context(viewport={"width":w,"height":900})
    if init: c.add_init_script(init)
    pg=c.new_page()
    pg.on("pageerror",lambda e:errs.append("PAGEERR "+str(e)))
    pg.on("console",lambda m: errs.append("CONSOLE "+m.text) if m.type=="error" else None)
    pg.goto(URL); pg.wait_for_timeout(500)
    return pg
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1) workout fuzz
    pg=newpage(b)
    res=pg.evaluate("""()=>{
      const acts=['start','done','next','back','pause','resume','repeat','stop'];
      const bad=[]; let seed=12345; const rnd=()=>{seed=(seed*1103515245+12345)&0x7fffffff;return seed/0x7fffffff};
      for(let i=0;i<4000;i++){
        const a=acts[Math.floor(rnd()*acts.length)];
        try{
          if(rnd()<0.15) skipTimer();
          if(rnd()<0.2 && (W.phase==='work')) setDone(Math.floor(rnd()*20));
          else act(a);
        }catch(e){bad.push(a+': '+e.message+' phase='+W.phase);}
        if(!(W.ex>=0&&W.ex<EX.length)) bad.push('ex out of range '+W.ex+' after '+a);
        if(!(W.set>=1&&W.set<=settings.sets)) bad.push('set out of range '+W.set+' after '+a);
        if(!['idle','warmup','prep','work','hold','rest','done'].includes(W.phase)) bad.push('phase '+W.phase);
        if(W.phase==='idle' && SESS) bad.push('SESS left in idle');
        if(isActive() && !SESS) bad.push('active without SESS after '+a+' phase '+W.phase);
        if(bad.length>8) break;
      }
      return {bad, wk:WK.length};
    }""")
    print("workout fuzz:",res)
    pg.evaluate("stopWorkout(); rad.busy=false; rad.skip=true")
    # 2) wheel all exclusions
    r=pg.evaluate("""()=>{const bad=[];const all=[...new Set(RECIPES.flatMap(r=>r.contains))];
      const old=EXC.slice();
      EXC=all.slice(); 
      for(const mode of ['meal','day','week']){RAD.mode=mode; for(const cheap of [true,false]) for(const work of [true,false]){RAD.cheap=cheap;RAD.work=work;
        try{RPL[mode]=radBuild(null)}catch(e){bad.push('allexc '+mode+': '+e.message)}}}
      // alle bis auf Rindfleisch
      EXC=all.filter(x=>x!=='Rindfleisch');
      for(const mode of ['meal','day','week']){RAD.mode=mode;try{RPL[mode]=radBuild(null)}catch(e){bad.push('beef '+mode+': '+e.message)}}
      EXC=old; return {bad, contains:all}}""")
    print("wheel allexc:",r)
    # render with empty plan
    r=pg.evaluate("""()=>{const bad=[];try{EXC=[...new Set(RECIPES.flatMap(r=>r.contains))];RAD.mode='day';RPL.day=null;radRender&&radRender();}catch(e){bad.push('radRender: '+e.message)};try{drawWheel()}catch(e){bad.push('drawWheel '+e.message)};try{radRoll&&radRoll()}catch(e){bad.push('radRoll '+e.message)};return bad}""")
    print("wheel render allexc:",r)
    # 4) shopCalc
    r=pg.evaluate("""()=>{const bad=[];
      const chk=(o,l)=>{const s=JSON.stringify(o);if(/NaN|Infinity|undefined|null/.test(s)) bad.push(l+' '+s.slice(0,200))};
      for(const rc of RECIPES){try{const x=shopCalc([{id:rc.id,n:1}]);chk(x,rc.id)}catch(e){try{const x=shopCalc([rc.id]);chk(x,rc.id)}catch(e2){bad.push(rc.id+': '+e2.message)}}}
      return bad.slice(0,10)}""")
    print("shopCalc:",r)
    pg.close()
    print("ERRORS:",errs)
    b.close()
