"""Render intro + outro cards to short silent WebM clips (for concat)."""
import os, tempfile
from playwright.sync_api import sync_playwright
OUT = os.path.abspath("recording/raw")
ROOT = "file://" + os.path.abspath("recording")
W, H = 1280, 720

def rec(card, seconds):
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            tempfile.mkdtemp(), headless=True,
            args=["--no-sandbox", "--disable-gpu", "--force-device-scale-factor=1"],
            viewport={"width": W, "height": H},
            record_video_dir=OUT, record_video_size={"width": W, "height": H})
        pg = ctx.pages[0]
        pg.goto(f"{ROOT}/{card}.html", wait_until="networkidle")
        pg.wait_for_timeout(int(seconds*1000))
        ctx.close()
        vids = [os.path.join(OUT, f) for f in os.listdir(OUT) if f.endswith(".webm")]
        vids.sort(key=os.path.getmtime)
        os.rename(vids[-1], os.path.join(OUT, f"{card}.webm"))
        print(card, "->", os.path.join(OUT, f"{card}.webm"))

rec("card-intro", 2.6)
rec("card-outro", 5.0)
