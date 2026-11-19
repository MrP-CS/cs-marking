/* offline: everything is kept on the device; new versions arrive when the device can reach this site */
const V = 'cs-marking-2026-11-19_1014-e92bd8aca8', FILES = ["./", "index.html", "app.bin", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "icon-maskable.png"];
self.addEventListener('install', e => e.waitUntil((async () => { const c = await caches.open(V);
  for (const f of FILES) { const r = await fetch(f, {cache: 'reload'}); if (!r.ok) throw Error('missing ' + f);
    if (f === 'app.bin') { const b = new Uint8Array(await r.clone().arrayBuffer()); if (b.length < 1000 || String.fromCharCode(...b.slice(0, 5)) !== 'OPTM1') throw Error('bad app.bin'); }
    if (f === 'index.html' || f === './') { const t = await r.clone().text(); if (!t.includes('id="optlock"')) throw Error('bad page'); }
    await c.put(f, r); }
  self.skipWaiting(); })()));
self.addEventListener('activate', e => e.waitUntil((async () => { for (const k of await caches.keys()) if (k !== V) await caches.delete(k); await self.clients.claim(); })()));
self.addEventListener('fetch', e => { const u = new URL(e.request.url); if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  e.respondWith((async () => { const c = await caches.open(V); const hit = await c.match(e.request, {ignoreSearch: true}) || (e.request.mode === 'navigate' ? await c.match('index.html') : null);
    return hit || fetch(e.request); })()); });
