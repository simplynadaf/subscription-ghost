import tempfile
from playwright.sync_api import sync_playwright
out = []
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(tempfile.mkdtemp(), args=["--no-sandbox"], viewport={"width": 1280, "height": 900})
    pg = ctx.pages[0]
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("https://simplynadaf.github.io/subscription-ghost/?fr=1", wait_until="networkidle")
    pg.wait_for_timeout(4500)
    out.append("rows: " + str(pg.evaluate("document.querySelectorAll('#ghostList .row').length")))
    out.append("bigWaste: " + pg.evaluate("document.getElementById('bigWaste').textContent"))
    out.append("fiveYear: " + pg.evaluate("document.getElementById('fiveYear').textContent"))
    before = pg.evaluate("document.getElementById('bigWaste').textContent")
    pg.evaluate("document.getElementById('ghostsSection').scrollIntoView()")
    pg.wait_for_timeout(900)
    pg.evaluate("document.querySelector('.killbtn').click()")
    pg.wait_for_timeout(2000)
    after = pg.evaluate("document.getElementById('bigWaste').textContent")
    out.append(f"kill: {before} -> {after} works={before != after}")
    out.append("pageerrors: " + (str(errs) if errs else "none"))
    ctx.close()
print("\n".join(out))
