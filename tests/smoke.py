"""Checks the published site before it goes live: passcode lock, the app opening, offline use,
and the iPad route (open trackers from Files, mark a notebook check, Save to Files).
Run: python tests/smoke.py [browsers...]   (needs MARKING_PASSCODE; serves ./site on localhost)"""
import asyncio, os, sys, threading, functools, http.server, socketserver, pathlib
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
PW = os.environ.get('MARKING_PASSCODE', '')
FIX = str(ROOT / 'tests' / 'fixtures' / 'BDB 10X CS tracker.xlsx')   # fabricated students only
PORT = 8765
IPAD = """delete window.showDirectoryPicker; Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 5});
Object.defineProperty(navigator, 'platform', {get: () => 'MacIntel'}); navigator.canShare = () => true; navigator.share = async d => { window.__shared = d.files.map(f => f.name); };"""

def serve():
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=str(ROOT / 'site'))
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), h); threading.Thread(target=s.serve_forever, daemon=True).start(); return s

async def run(p, kind, ipad):
    errs = []; b = await getattr(p, kind).launch(executable_path=(os.environ.get('CHROME') or None) if kind == 'chromium' else None)   # CHROME: optional local browser
    opts = dict(p.devices['iPad Pro 11 landscape']) if ipad else {'viewport': {'width': 1366, 'height': 900}}
    if kind != 'webkit': opts.pop('is_mobile', None); opts.pop('default_browser_type', None)
    opts.pop('default_browser_type', None)
    ctx = await b.new_context(**opts, accept_downloads=True)
    if ipad: await ctx.add_init_script(IPAD)
    await ctx.add_init_script("localStorage.setItem('opt-tmark-marker','Mr Test')")
    pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('dialog', lambda d: asyncio.ensure_future(d.accept()))
    url = f'http://127.0.0.1:{PORT}/'
    await pg.goto(url); await pg.wait_for_selector('#optlock:not([hidden])')
    await pg.fill('#pc', 'wrong-passcode'); await pg.click('#go'); await pg.wait_for_function("document.getElementById('err').textContent.length > 0", timeout=60000)
    assert 'not right' in await pg.inner_text('#err'), 'wrong passcode not rejected'
    if not PW: print(kind, 'ipad' if ipad else 'pc', ': no MARKING_PASSCODE – lock checked only'); await b.close(); return errs
    await pg.fill('#pc', PW); await pg.click('#go'); await pg.wait_for_selector('.homehero', timeout=60000)
    await pg.reload(); await pg.wait_for_selector('.homehero', timeout=60000)          # remembered, now controlled by the service worker
    await pg.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller", timeout=30000)
    await ctx.set_offline(True); await pg.reload(); await pg.wait_for_selector('.homehero', timeout=60000); print(kind, 'ipad' if ipad else 'pc', ': opens offline ✓')
    if not ipad:   # Force update: checks the site's version.json, clears the offline copy, reloads the newest
        await ctx.set_offline(False); await pg.click('button:has-text("Force update")'); await pg.wait_for_selector('.uidlg', timeout=20000)
        assert 'newest version' in await pg.inner_text('.uidlg'), 'Force update did not read version.json'
        await pg.click('.uidlg .btn.go'); await pg.wait_for_url('**/?u=*', timeout=60000); await pg.wait_for_selector('.homehero', timeout=60000)
        await pg.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller", timeout=30000)
        await ctx.set_offline(True); await pg.reload(); await pg.wait_for_selector('.homehero', timeout=60000); print(kind, 'pc : Force update reloads and still works offline ✓')
    if ipad:
        async with pg.expect_file_chooser() as fc: await pg.click('.connect .tfopen')
        await (await fc.value).set_files(FIX); await pg.wait_for_timeout(1500)
        await pg.click('.tile >> text=Notebook check'); await pg.wait_for_timeout(800)
        await pg.select_option('.clpick select', 'BDB 10X'); await pg.wait_for_timeout(800)
        await pg.click('.wnav .btn.go'); await pg.wait_for_timeout(800)
        await pg.click('button:has-text("Open “BDB 10X CS tracker.xlsx”")'); await pg.wait_for_timeout(800)
        await pg.click('.wnav .btn.go'); await pg.wait_for_selector('.nbcard')
        await pg.click('.nbseg button >> nth=0'); await pg.click('.nbtick input >> nth=0'); await pg.click('button:has-text("Copy & next")'); await pg.wait_for_timeout(900)
        await pg.click('text=📊 Class summary'); await pg.wait_for_selector('.sumwrap')
        await pg.click('text=Next: save'); await pg.click('.step3 .btn.go'); await pg.wait_for_timeout(1500)
        shared = await pg.evaluate('window.__shared || null'); assert shared and shared[0].endswith('CS tracker.xlsx'), 'Save to Files not offered: %r' % shared
        print(kind, 'ipad : notebook check marked and saved through Save to Files offline ✓')
    await b.close(); return errs

async def main():
    kinds = sys.argv[1:] or ['chromium', 'webkit']; s = serve(); bad = []
    async with async_playwright() as p:
        for k in kinds:
            for ipad in ([False, True] if k == 'chromium' else [True]):
                e = await run(p, k, ipad)
                if e: bad.append((k, ipad, e))
    s.shutdown()
    if bad: print('PAGE ERRORS', bad); sys.exit(1)
    print('all checks passed')
asyncio.run(main())
