"""
Professional silent screen recording for Subscription Ghost.
Scenes, in order (timed to match recording/voiceover/soundtrack.mp3, 88s):
  website hero -> ghost list -> tap Amazon Prime verdict -> tap iCloud verdict
  -> add a NEW subscription (Netflix, rarely) -> overlap 'music twice'
  -> kill a leak (total drops) -> scorecard -> GitHub repo README scroll.
Records WebM via Playwright recordVideo, adds a soft cursor dot + click ripple.
"""
import os, tempfile, time
from playwright.sync_api import sync_playwright

LIVE = "https://simplynadaf.github.io/subscription-ghost/"
REPO = "https://github.com/simplynadaf/subscription-ghost"
OUT = os.path.abspath("recording/raw")
os.makedirs(OUT, exist_ok=True)
W, H = 1280, 720

CURSOR = """
(() => {
  if (window.__cur) return;
  const d=document.createElement('div');
  d.id='__cursor';
  d.style.cssText='position:fixed;z-index:999999;width:18px;height:18px;border-radius:50%;background:rgba(124,108,255,.9);box-shadow:0 0 14px rgba(124,108,255,.7);pointer-events:none;transform:translate(-50%,-50%);transition:left .5s cubic-bezier(.32,.72,0,1),top .5s cubic-bezier(.32,.72,0,1);left:640px;top:360px';
  document.body.appendChild(d);
  window.__cur=d;
  window.__moveCur=(x,y)=>{d.style.left=x+'px';d.style.top=y+'px';};
  window.__ripple=(x,y)=>{const r=document.createElement('div');r.style.cssText='position:fixed;z-index:999998;left:'+x+'px;top:'+y+'px;width:10px;height:10px;border-radius:50%;border:2px solid rgba(124,108,255,.9);pointer-events:none;transform:translate(-50%,-50%);transition:all .6s ease-out';document.body.appendChild(r);requestAnimationFrame(()=>{r.style.width='54px';r.style.height='54px';r.style.opacity='0';});setTimeout(()=>r.remove(),650);};
})();
"""

def move(pg, sel):
    try:
        box = pg.evaluate("""(s)=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};}""", sel)
        if box:
            pg.evaluate("([x,y])=>window.__moveCur(x,y)", [box["x"], box["y"]])
            pg.wait_for_timeout(600)
            pg.evaluate("([x,y])=>window.__ripple(x,y)", [box["x"], box["y"]])
            pg.wait_for_timeout(200)
        return box
    except Exception:
        return None

def smooth_scroll(pg, to_y, steps=24, dt=42):
    pg.evaluate("""([ty,steps,dt])=>{return new Promise(res=>{const sy=window.scrollY;const d=(ty-sy)/steps;let i=0;const t=setInterval(()=>{i++;window.scrollTo(0,sy+d*i);if(i>=steps){clearInterval(t);res();}},dt);});}""", [to_y, steps, dt])
    pg.wait_for_timeout(steps*dt+200)

def run():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            tempfile.mkdtemp(), headless=True,
            args=["--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1"],
            viewport={"width": W, "height": H},
            record_video_dir=OUT, record_video_size={"width": W, "height": H},
        )
        pg = ctx.pages[0]

        # ---- SCENE A: website (0 - ~57s) ----
        pg.goto(LIVE + "?rec=1", wait_until="networkidle")
        pg.wait_for_timeout(3500)
        pg.evaluate(CURSOR)
        pg.wait_for_timeout(2500)                       # 0-6  hero holds

        move(pg, "#bigWaste"); pg.wait_for_timeout(1200)  # the leaking number

        # scroll to ghosts
        gy = pg.evaluate("document.getElementById('ghostsSection').offsetTop-40")
        smooth_scroll(pg, gy); pg.wait_for_timeout(1000)   # 6-16 ghost list

        # tap Amazon Prime verdict (find the row by text)
        pg.evaluate("""()=>{const rows=[...document.querySelectorAll('#ghostList .row')];const r=rows.find(x=>/Amazon Prime/i.test(x.textContent));if(r){const b=r.getBoundingClientRect();window.__moveCur(b.left+b.width/2,b.top+b.height/2);window.__ripple(b.left+b.width/2,b.top+b.height/2);r.click();}}""")
        pg.wait_for_timeout(3200)                        # 16-25 Prime verdict
        pg.evaluate("document.getElementById('sheetClose')?.click();document.querySelectorAll('.sheet,#verdictCard').forEach(s=>s.classList.remove('show'))")
        pg.wait_for_timeout(800)

        # tap iCloud verdict (the biggest ghost)
        pg.evaluate("""()=>{const rows=[...document.querySelectorAll('#ghostList .row')];const r=rows.find(x=>/iCloud/i.test(x.textContent));if(r){const b=r.getBoundingClientRect();window.__moveCur(b.left+b.width/2,b.top+b.height/2);window.__ripple(b.left+b.width/2,b.top+b.height/2);r.click();}}""")
        pg.wait_for_timeout(3000)
        pg.evaluate("document.getElementById('sheetClose')?.click();document.querySelectorAll('.sheet,#verdictCard').forEach(s=>s.classList.remove('show'))")
        pg.wait_for_timeout(700)

        # ADD a new subscription (Netflix, rarely)
        smooth_scroll(pg, 0, steps=16); pg.wait_for_timeout(400)
        move(pg, "#addBtn")
        pg.evaluate("document.getElementById('addBtn').click()")
        pg.wait_for_timeout(1200)                        # 25-45 add flow
        pg.evaluate("""()=>{const t=[...document.querySelectorAll('#catalogTiles .tile,#catalogTiles button')].find(x=>/Netflix/i.test(x.textContent));if(t){const b=t.getBoundingClientRect();window.__moveCur(b.left+b.width/2,b.top+b.height/2);window.__ripple(b.left+b.width/2,b.top+b.height/2);t.click();}}""")
        pg.wait_for_timeout(1400)
        pg.evaluate("""()=>{const u=[...document.querySelectorAll('#usagePick button,#usagePick .chip')].find(x=>/rarely/i.test(x.textContent));if(u){const b=u.getBoundingClientRect();window.__moveCur(b.left+b.width/2,b.top+b.height/2);window.__ripple(b.left+b.width/2,b.top+b.height/2);u.click();}}""")
        pg.wait_for_timeout(1200)
        move(pg, "#addConfirm")
        pg.evaluate("document.getElementById('addConfirm')?.click()")
        pg.wait_for_timeout(2500)

        # overlap 'paying for music twice'
        oy = pg.evaluate("(document.getElementById('overlapWrap')||document.getElementById('ghostsSection')).offsetTop-40")
        smooth_scroll(pg, oy); pg.wait_for_timeout(2000)

        # KILL a leak - total drops
        pg.evaluate("""()=>{const k=document.querySelector('.killbtn');if(k){const b=k.getBoundingClientRect();window.__moveCur(b.left+b.width/2,b.top+b.height/2);window.__ripple(b.left+b.width/2,b.top+b.height/2);k.click();}}""")
        pg.wait_for_timeout(3000)                        # 57-66 kill

        # scorecard
        sy = pg.evaluate("(document.getElementById('scoreGrid')||document.getElementById('statGrid')).offsetTop-60")
        smooth_scroll(pg, sy); pg.wait_for_timeout(3000) # 66-75 honest scorecard

        # ---- SCENE B: GitHub repo (~75 - 88s) ----
        pg.goto(REPO, wait_until="domcontentloaded")
        pg.wait_for_timeout(2500)
        smooth_scroll(pg, 700, steps=30, dt=55)
        pg.wait_for_timeout(1200)
        smooth_scroll(pg, 1500, steps=30, dt=55)
        pg.wait_for_timeout(1500)

        ctx.close()
        # the recorded file:
        vids = [os.path.join(OUT, f) for f in os.listdir(OUT) if f.endswith(".webm")]
        vids.sort(key=os.path.getmtime)
        print("RAW:", vids[-1] if vids else "NONE")

run()
