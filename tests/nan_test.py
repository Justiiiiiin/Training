from playwright.sync_api import sync_playwright
URL=__import__("fcenv").APP_URL
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":900,"height":800}); errs=[]
    pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500)
    r=pg.evaluate("""()=>{ const bad=[]; const cv=document.createElement('canvas'); cv.style.cssText='width:480px;height:360px'; document.body.appendChild(cv);
      const v=makeView(); v.bindCanvas(cv);
      for(const id in V3A){ V3A[id].forEach((a,i)=>{ v.setAnim(id,i); const G=v.G; for(let k=0;k<12;k++){ G.t=G.T*k/12; try{ v.draw(); }catch(e){ bad.push(id+i+': '+e.message); break; } }
          if(!G.fit || !isFinite(G.fit.R) || !isFinite(G.fit.cx) || !isFinite(G.fit.cy)) bad.push(id+i+' fit'); 
          const J=V3.solve(G.anim.kf[0].p); for(const key in J){ if(J[key].some(x=>!isFinite(x))) bad.push(id+i+' nan '+key); } }); }
      return {n:Object.keys(V3A).length, anims:Object.values(V3A).reduce((a,x)=>a+x.length,0), bad}; }""")
    print(r, errs[:3]); b.close()
