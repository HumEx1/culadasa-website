/* Culadasa redesign: shared behaviour.  No libraries. */
(function () {
  // Videos: show the thumbnail first and load YouTube only when pressed (faster pages, no tracking until play).
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.video button');
    if (!btn) return;
    var box = btn.parentNode, id = box.getAttribute('data-id');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0&enablejsapi=1' + (box.getAttribute('data-start') ? '&start=' + box.getAttribute('data-start') : '');   // enablejsapi: the times on a video page can move the player
    f.title = btn.getAttribute('aria-label') || 'YouTube video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    box.replaceChildren(f);
    f.focus();   // keep keyboard focus on the player that replaced the button (accessibility review, 27 Nov 2026)
  });

  // Newsletter: not connected to a mailing service yet, so say so plainly and send nothing.
  document.querySelectorAll('.signup-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.querySelector('.note');
      if (note) note.textContent = 'Thank you. This preview is not connected to a mailing service yet, so your address was not sent or stored anywhere.';
    });
  });

  // Phone menu: a real button, with Escape to close.
  var nav = document.querySelector('.nav'), btn = document.querySelector('.nav-button');
  function setMenu(open) { nav.classList.toggle('open', open); btn.setAttribute('aria-expanded', open); }
  if (btn) btn.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
  // "Library" dropdown: opens on click or keyboard as well as hover.
  document.querySelectorAll('.menu button.group').forEach(function (g) {
    g.addEventListener('click', function () {
      var li = g.parentNode, open = !li.classList.contains('open');
      li.classList.toggle('open', open); g.setAttribute('aria-expanded', open);
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (nav && nav.classList.contains('open')) { setMenu(false); btn.focus(); }
    document.querySelectorAll('.has-sub.open').forEach(function (li) { li.classList.remove('open'); li.querySelector('button').setAttribute('aria-expanded', false); });
  });
  document.querySelectorAll('.menu a').forEach(function (a) { a.addEventListener('click', function () { if (nav) setMenu(false); }); });
})();

/* "Show all" / "Show fewer" on the title lists of the Audio and Videos pages (the search page has its own) (D, 25 Nov 2026) */
document.addEventListener('click', function (e) {
  var b = e.target.closest && e.target.closest('.rg-all, .rg-less');
  if (!b || b.closest('#results')) return;
  var sec = b.closest('.rgroup'); if (!sec) return;
  var open = b.classList.contains('rg-all');
  sec.classList.toggle('open', open);
  // keyboard focus: on opening, the first row that appeared (the page does not move); on closing, back to "Show all" (round 2, 27 Nov 2026)
  var target = open ? sec.querySelector('.rg-more summary, .rg-more .rr-title, .rg-more a') : sec.querySelector('.rg-all');
  if (target) target.focus({ preventScroll: true });
  if (!open) sec.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
});

/* the filter rows and Library tabs on phones scroll sideways (27 Nov 2026): the chosen pill or current room is brought
   into view, and a row fades at its right edge only while there is more to scroll to */
(function () {
  var ROWS = '.scope, .search-panel .filters, .lib-side ul';
  function fade(el) { el.classList.toggle('scrolls', el.scrollWidth > el.clientWidth + 2 && el.scrollLeft < el.scrollWidth - el.clientWidth - 2); }
  function mark() {
    document.querySelectorAll(ROWS).forEach(function (el) {
      if (el.scrollWidth > el.clientWidth + 2) {
        var sel = el.querySelector('input:checked + span, [aria-pressed="true"]:not(.scope-all), [aria-current]');
        if (sel) { var r = sel.getBoundingClientRect(), b = el.getBoundingClientRect(); if (r.left < b.left || r.right > b.right - 24) el.scrollLeft += r.left - b.left - 16; }
      }
      fade(el);
      if (!el.dataset.fadeWatch) { el.dataset.fadeWatch = '1'; el.addEventListener('scroll', function () { fade(el); }, { passive: true }); }
    });
  }
  window.culadasaMarkScroll = mark;
  window.addEventListener('load', mark); window.addEventListener('resize', mark); mark();
})();

/* A video's own page (D, 28 Nov 2026): every time plays the video here from that moment; ?t=<seconds> opens the
   page at that moment; the find box picks out the paragraphs of the transcript that contain the words. */
(function () {
  var grid = document.querySelector('.vgrid'); if (!grid) return;
  var box = grid.querySelector('.video'), id = grid.getAttribute('data-video');
  var paras = [].slice.call(grid.querySelectorAll('.tp'));
  function mark(sec) {
    var cur = null; paras.forEach(function (p) { if (+p.id.slice(1) <= sec) cur = p; p.classList.remove('now'); });
    if (cur) cur.classList.add('now'); return cur;
  }
  var player = grid.querySelector('.vplayer');
  function seek(sec, from) {
    var f = box.querySelector('iframe');
    if (f) {
      f.contentWindow.postMessage(JSON.stringify({ event: 'command', func: 'seekTo', args: [sec, true] }), '*');
      f.contentWindow.postMessage(JSON.stringify({ event: 'command', func: 'playVideo', args: [] }), '*');
    } else {
      box.setAttribute('data-start', String(sec));
      var b = box.querySelector('button'); if (b) b.click();
    }
    mark(sec);
    pin();
    if (from) {
      from.focus({ preventScroll: true });   // keyboard focus stays on the time that was chosen
      requestAnimationFrame(function () {   // and the time is not left under the pinned player
        if (!player.classList.contains('pinned')) return;
        var r = from.getBoundingClientRect(), pb = player.getBoundingClientRect().bottom;
        if (r.top < pb + 8) window.scrollBy(0, r.top - pb - 8);
      });
    }
  }
  // On phones and tablets in portrait the video, once started, stays pinned under the menu so the reader keeps their
  // place; never on short screens (a phone on its side), where it would cover the page (28 Nov 2026)
  function canPin() { return window.innerWidth <= 900 && window.innerHeight >= 560; }
  function pad() {
    var on = player.classList.contains('pinned') && canPin();
    document.documentElement.style.scrollPaddingTop = on ? (player.getBoundingClientRect().height + 56) + 'px' : '';
  }
  function pin() { if (player && canPin()) { player.classList.add('pinned'); requestAnimationFrame(pad); } }
  window.addEventListener('resize', function () { if (!canPin()) player.classList.remove('pinned'); pad(); });
  box.addEventListener('click', pin);
  grid.addEventListener('click', function (e) {
    var a = e.target.closest('[data-seek]'); if (!a || e.ctrlKey || e.metaKey || e.shiftKey) return;
    e.preventDefault(); seek(+a.getAttribute('data-seek'), a);
  });
  var t = parseInt(new URLSearchParams(location.search).get('t') || '', 10);
  if (t > 0) { box.setAttribute('data-start', String(t)); pin(); var p = mark(t); if (p) p.scrollIntoView({ block: 'center' }); }   // the Play button stays in view, ready at that moment
  var input = document.getElementById('tf'), status = grid.querySelector('.tf-status');
  if (!input) return;
  function fold(x) { return x.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[’‘]/g, "'").replace(/[“”]/g, '"').toLowerCase(); }
  function esc(x) { return x.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  paras.forEach(function (p) { var t = p.querySelector('.tt'); p._t = t; p._raw = t ? t.textContent : ''; p.dataset.f = fold(p._raw); });
  input.addEventListener('input', function () {
    var q = fold(input.value.trim().replace(/\s+/g, ' ')), n = 0;
    paras.forEach(function (p) {
      var at = q ? p.dataset.f.indexOf(q) : 0, hit = !q || at >= 0; p.hidden = !hit; if (hit && q) n++;
      if (!p._t) return;
      if (!q || at < 0) { p._t.textContent = p._raw; return; }
      var out = '', from = 0, f = p.dataset.f;   // folding keeps the same length for these scripts, so positions line up
      while (at >= 0) { out += esc(p._raw.slice(from, at)) + '<mark>' + esc(p._raw.slice(at, at + q.length)) + '</mark>'; from = at + q.length; at = f.indexOf(q, from); }
      p._t.innerHTML = out + esc(p._raw.slice(from));
    });
    status.textContent = q ? (n ? n + ' paragraph' + (n === 1 ? '' : 's') + ' with “' + input.value.trim() + '”' : 'Not in this transcript') : '';
  });
})();

