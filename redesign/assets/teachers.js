/* Teachers: filter by name or place, by year or online, sort by distance, and a map.
   The map uses Leaflet (in assets/vendor) and OpenStreetMap tiles; no API key.
   Location is only read if the visitor presses "Near me". It is used in the browser to sort by distance;
   the site never sends it anywhere, though centring the map loads map tiles for that area from OpenStreetMap. */
(function () {
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var list = document.getElementById('tlist'), q = document.getElementById('tq'), near = document.getElementById('near');
  var filters = document.getElementById('tfilters'), statusEl = document.getElementById('tstatus');
  var cards = Array.prototype.slice.call(list.querySelectorAll('.tcard'));
  var F = 'all', here = null, map = null, markers = [];
  var box = document.getElementById('mapbox');
  if (box) box.open = true;  // sample locations exist, so show the map

  function km(a, b) {
    var R = 6371, r = Math.PI / 180, dLat = (b[0] - a[0]) * r, dLng = (b[1] - a[1]) * r;
    var h = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    return 2 * R * Math.asin(Math.sqrt(h));
  }
  function apply() {
    var term = (q.value || '').trim().toLowerCase(), shown = 0;
    cards.forEach(function (c) {
      var ok = (!term || c.dataset.name.indexOf(term) >= 0 || c.dataset.place.indexOf(term) >= 0) &&
               (F === 'all' || (F === 'online' ? c.dataset.online === '1' : F === 'inperson' ? c.dataset.inperson === '1' : c.dataset.year === F));
      c.hidden = !ok; if (ok) shown++;
    });
    if (here) {
      cards.sort(function (a, b) {
        var da = a.dataset.lat ? km(here, [+a.dataset.lat, +a.dataset.lng]) : 1e9, db = b.dataset.lat ? km(here, [+b.dataset.lat, +b.dataset.lng]) : 1e9;
        return da - db;
      }).forEach(function (c) { list.appendChild(c); });
    }
    var located = cards.filter(function (c) { return c.dataset.lat; }).length;
    statusEl.textContent = shown + ' of ' + cards.length + ' teachers shown. ' + located + (located === 1 ? ' has' : ' have') + ' a location on the map so far.' + (here ? ' Nearest first.' : '');
  }
  q.addEventListener('input', apply);
  document.getElementById('teacher-form').addEventListener('submit', function (e) { e.preventDefault(); apply(); });
  filters.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    F = b.dataset.f;
    filters.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
    apply();
  });
  near.addEventListener('click', function () {
    if (!navigator.geolocation) { statusEl.textContent = 'Your browser cannot share a location. Search by town or country instead.'; return; }
    statusEl.textContent = 'Finding teachers near you…';
    navigator.geolocation.getCurrentPosition(function (p) {
      here = [p.coords.latitude, p.coords.longitude];
      if (box && !box.open) { box.open = true; }
      if (map) { map.setView(here, 6); window.L.circleMarker(here, { radius: 7, color: '#2a241c', fillColor: '#f3e3a8', fillOpacity: 1 }).addTo(map).bindPopup('You are here'); }
      apply();
    }, function () { statusEl.textContent = 'Location was not shared. Search by town or country instead.'; }, { timeout: 10000 });
  });

  function initMap() {
    if (!window.L || map) return;
    map = window.L.map('map', { scrollWheelZoom: false, worldCopyJump: true }).setView([30, -40], 2);
    window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
    var icon = window.L.divIcon({ className: 'pin', html: '<span></span>', iconSize: [18, 18], iconAnchor: [9, 9] });
    cards.forEach(function (c) {
      if (!c.dataset.lat) return;
      var a = c.querySelector('a');
      var m = window.L.marker([+c.dataset.lat, +c.dataset.lng], { icon: icon, title: a.querySelector('.tname').textContent })
        .addTo(map).bindPopup('<a href="' + esc(a.getAttribute('href')) + '">' + esc(a.querySelector('.tname').textContent) + '</a><br>' + esc(a.querySelector('.tmeta').textContent));
      markers.push(m);
    });
  }
  if (box) box.addEventListener('toggle', function () { if (box.open && !map) initMap(); else if (map) map.invalidateSize(); });
  if (document.readyState === 'complete') initMap(); else window.addEventListener('load', initMap);
  apply();
})();
