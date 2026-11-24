/* Culadasa redesign: shared behaviour.  No libraries. */
(function () {
  // Videos: show the thumbnail first and load YouTube only when pressed (faster pages, no tracking until play).
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.video button');
    if (!btn) return;
    var box = btn.parentNode, id = box.getAttribute('data-id');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
    f.title = btn.getAttribute('aria-label') || 'YouTube video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    box.replaceChildren(f);
  });

  // Newsletter: not connected to a mailing service yet, so say so plainly and send nothing.
  document.querySelectorAll('.signup-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.querySelector('.note');
      if (note) note.textContent = 'Thank you. This preview is not connected to a mailing service yet, so your address was not sent or stored anywhere.';
    });
  });

  // Phone menu: close it after choosing a page.
  var toggle = document.getElementById('nav-toggle');
  if (toggle) document.querySelectorAll('.menu a').forEach(function (a) {
    a.addEventListener('click', function () { toggle.checked = false; });
  });
})();
