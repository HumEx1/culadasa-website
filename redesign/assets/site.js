/* Culadasa redesign: shared behaviour.  No libraries. */
(function () {
  // Videos: show the thumbnail first and load YouTube only when pressed (faster pages, no tracking until play).
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.video button');
    if (!btn) return;
    var box = btn.parentNode, id = box.getAttribute('data-id');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0' + (box.getAttribute('data-start') ? '&start=' + box.getAttribute('data-start') : '');
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
