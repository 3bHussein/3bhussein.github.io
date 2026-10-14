"""End-to-end visual and interaction smoke checks in headless Chromium."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "browser-screenshots"
OUT.mkdir(exist_ok=True)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/"

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, width, height in [("desktop", 1440, 900), ("tablet", 820, 1180), ("mobile", 390, 844)]:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            errors = []
            page.on("pageerror", lambda err: errors.append(str(err)))
            page.goto(url, wait_until="domcontentloaded")
            page.locator(".v3-header").wait_for()
            assert page.locator("#about h1").is_visible(), f"{name}: hero missing"
            assert page.locator("#projects .pro-project").count() == 3, f"{name}: project cards missing"
            assert page.locator("#experience").count() == 1
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 2"), f"{name}: horizontal overflow"
            if width <= 900:
                button = page.locator(".v3-menu-toggle")
                assert button.is_visible(), f"{name}: menu toggle hidden"
                button.click()
                assert button.get_attribute("aria-expanded") == "true"
                assert page.locator("#v3MobileNav").is_visible()
                page.keyboard.press("Escape")
                assert button.get_attribute("aria-expanded") == "false"
                button.click()
                page.locator("#v3MobileNav a[href='#projects']").click()
                assert page.locator("#v3MobileNav").is_hidden()
            else:
                assert page.locator(".v3-nav").is_visible()
            page.screenshot(path=str(OUT / f"{name}.png"), full_page=True, animations="disabled")
            assert not errors, f"{name}: JavaScript errors: {errors}"
            page.close()
        browser.close()
finally:
    server.shutdown()
