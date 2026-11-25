/* offline: everything is kept on the device; new versions arrive when the device can reach this site */
const V = 'cs-marking-2026-11-25_1230-ea1be85eb5', FILES = ["./", "index.html", "app.bin", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "icon-maskable.png"];
async function fill(){ const c = await caches.open(V + '-new');
  for (const f of FILES) { const r = await fetch(f, {cache: 'reload'}); if (!r.ok) throw Error('missing ' + f);
    if (f === 'app.bin') { const b = new Uint8Array(await r.clone().arrayBuffer()); if (b.length < 1000 || String.fromCharCode(...b.slice(0, 5)) !== 'OPTM1') throw Error('bad app.bin'); }
    if (f === 'index.html' || f === './') { const t = await r.clone().text(); if (!t.includes('id="optlock"')) throw Error('bad page'); }
    await c.put(f, r); }
  await caches.delete(V); const d = await caches.open(V), t = await caches.open(V + '-new'); for (const q of await t.keys()) await d.put(q, await t.match(q)); await caches.delete(V + '-new'); }
self.addEventListener('install', e => e.waitUntil(fill().then(() => self.skipWaiting())));
/* Force update: download every file again (all or nothing – a failed download keeps the copy that works) */
self.addEventListener('message', e => { if (e.data === 'refresh') e.waitUntil(fill().catch(() => {}).then(() => { if (e.ports[0]) e.ports[0].postMessage('done'); })); });
self.addEventListener('activate', e => e.waitUntil((async () => { for (const k of await caches.keys()) if (k !== V) await caches.delete(k); await self.clients.claim(); })()));
self.addEventListener('fetch', e => { const u = new URL(e.request.url); if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  e.respondWith((async () => { const c = await caches.open(V); const hit = await c.match(e.request, {ignoreSearch: true}) || (e.request.mode === 'navigate' ? await c.match('index.html') : null);
    return hit || fetch(e.request); })()); });
