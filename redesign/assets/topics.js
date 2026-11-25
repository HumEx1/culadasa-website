/* Topics: a word cloud and a search ranked purely by number of mentions.
   Rule (Darin, 24 Nov 2026): rank by how often a source mentions the word,
   no other rules.  Matching: case-insensitive, accents and apostrophe styles
   ignored ("jhana" finds "jhāna"), at the start of a word, so "compassion"
   also counts "compassionate".  Several words match as a phrase. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var form = $('topic-form'), input = $('q'), cloudEl = $('cloud'), statusEl = $('status'), resultsEl = $('results'), filtersEl = $('filters');
  var DATA = null, KIND = 'all', LIMIT = 60;
  var KINDS = [['all', 'All'], ['handout', 'Handouts'], ['essay', 'Essays'], ['qa', 'AMA'], ['interview', 'Interviews'], ['about', 'Lineage'], ['video', 'Videos']];
  var TYPE_OF = { 'Handout': 'handout', 'Essay': 'essay', 'Q&A': 'qa', 'Interview': 'interview', 'Lineage': 'about', 'Video': 'video' };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  // Fold accents and apostrophes, one character in, one out, so positions stay aligned with the original text.
  function fold(s) {
    var out = '';
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (c === '’' || c === '‘') { out += "'"; continue; }
      var d = c.normalize('NFD').replace(/[̀-ͯ]/g, '');
      out += d.length === 1 ? d.toLowerCase() : c.toLowerCase().slice(0, 1);
    }
    return out;
  }
  // Links that leave the site, and PDFs, open in a new tab (D, 24 Nov 2026).
  function nt(u) { return /^https?:/.test(u) || /\.pdf$/i.test(u) ? ' target="_blank" rel="noopener"' : ''; }
  function isLetter(ch) { return /[a-z0-9À-ɏḀ-ỿ]/i.test(ch || ''); }
  // Find matches in folded text: word-start boundary checked by hand (no lookbehind, so older Safari works).
  function matcher(q) {
    var words = fold(q.trim()).split(/\s+/).map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
    var re = new RegExp(words.join("[\\s\\-–—]+") + "[a-z0-9À-ɏḀ-ỿ]*", 'g');
    return function (text, folded, max) {
      var hits = [], m;
      re.lastIndex = 0;
      while ((m = re.exec(folded))) {
        if (m[0] === '') { re.lastIndex++; continue; }
        if (!isLetter(folded[m.index - 1])) hits.push([m.index, m.index + m[0].length]);
        if (max && hits.length >= max) break;
      }
      return hits;
    };
  }
  function snippet(text, hits, at) {
    var a = Math.max(0, hits[at][0] - 110), b = Math.min(text.length, hits[at][1] + 140), out = a > 0 ? '…' : '', pos = a;
    hits.forEach(function (h) {
      if (h[0] < a || h[1] > b) return;
      out += esc(text.slice(pos, h[0]).replace(/\s+/g, ' ')) + '<mark>' + esc(text.slice(h[0], h[1])) + '</mark>';
      pos = h[1];
    });
    return out + esc(text.slice(pos, b).replace(/\s+/g, ' ')) + (b < text.length ? '…' : '');
  }
  function snippets(text, hits, max) {
    var out = [], last = -999;
    for (var i = 0; i < hits.length && out.length < max; i++) {
      if (hits[i][0] - last < 260) continue;
      last = hits[i][0]; out.push(snippet(text, hits, i));
    }
    return out;
  }

  function search(q) {
    resultsEl.innerHTML = '';
    var clean = (q || '').trim();
    if (!clean) { statusEl.textContent = 'Type a word, or choose one from the cloud.'; drawFilters({}); return; }
    if (!/[A-Za-zÀ-ɏḀ-ỿ]/.test(clean) || fold(clean).replace(/[^a-z0-9]/g, '').length < 2) { statusEl.textContent = 'Type at least two letters.'; drawFilters({}); return; }
    var find = matcher(clean), items = [];
    DATA.docs.forEach(function (d) {
      var hits = find(d.text, d.f);
      if (hits.length) items.push({ kind: TYPE_OF[d.type], label: d.type, title: d.title, url: d.url, n: hits.length, credit: d.credit, snips: snippets(d.text, hits, 3) });
    });
    DATA.qna.forEach(function (s) {
      var list = [], n = 0;
      s.items.forEach(function (it) { var h = find(it.text, it.f); if (h.length) { n += h.length; list.push({ it: it, hits: h }); } });
      if (n) items.push({ kind: 'qa', label: 'AMA', title: s.title, url: s.url, n: n, qa: list });
    });
    items.sort(function (a, b) { return b.n - a.n || a.title.localeCompare(b.title); });
    var counts = { all: items.length }; items.forEach(function (i) { counts[i.kind] = (counts[i.kind] || 0) + 1; });
    drawFilters(counts);
    var shown = KIND === 'all' ? items : items.filter(function (i) { return i.kind === KIND; });
    var total = items.reduce(function (s, i) { return s + i.n; }, 0);
    statusEl.textContent = items.length ? total + ' mentions of “' + clean + '” in ' + items.length + ' sources, most mentions first.' : 'No mentions of “' + clean + '”. Try a shorter or different word.';
    resultsEl.innerHTML = shown.slice(0, LIMIT).map(function (i) {
      var body = i.qa
        ? '<ol class="qlist">' + i.qa.slice(0, 6).map(function (x) { return '<li><a class="t" href="' + esc(x.it.url) + '"' + nt(x.it.url) + '>' + esc(x.it.t) + '</a> ' + snippet(x.it.text, x.hits, 0) + '</li>'; }).join('') + '</ol>' + (i.qa.length > 6 ? '<p class="small muted">and ' + (i.qa.length - 6) + ' more questions in this session</p>' : '')
        : i.snips.map(function (s) { return '<p>' + s + '</p>'; }).join('');
      return '<article class="result"><div class="meta"><span>' + esc(i.label) + '</span><span class="hits">' + i.n + (i.n === 1 ? ' mention' : ' mentions') + '</span>' + (i.credit ? '<span>' + esc(i.credit) + '</span>' : '') + '</div>' +
        '<h3><a href="' + esc(i.url) + '"' + nt(i.url) + '>' + esc(i.title) + '</a></h3>' + body + '</article>';
    }).join('') + (shown.length > LIMIT ? '<p><button type="button" class="btn ghost" id="more">Show all ' + shown.length + ' sources</button></p>' : '');
    var more = $('more'); if (more) more.addEventListener('click', function () { LIMIT = 100000; search(clean); });
  }

  function drawFilters(counts) {
    filtersEl.innerHTML = KINDS.filter(function (k) { return k[0] === 'all' || counts[k[0]]; }).map(function (k) {
      return '<button type="button" data-k="' + k[0] + '" aria-pressed="' + (k[0] === KIND) + '">' + esc(k[1]) + ' <span class="muted">' + (counts[k[0]] || 0) + '</span></button>';
    }).join('');
  }
  filtersEl.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    KIND = b.getAttribute('data-k'); go(false);
  });

  function drawCloud() {
    var nums = DATA.cloud.map(function (w) { return w[1]; }), max = Math.max.apply(null, nums), min = Math.min.apply(null, nums);
    var words = DATA.cloud.slice().sort(function (a, b) { return a[0].localeCompare(b[0]); });
    cloudEl.innerHTML = words.map(function (w) {
      var t = (Math.sqrt(w[1]) - Math.sqrt(min)) / (Math.sqrt(max) - Math.sqrt(min));
      var size = Math.round(15 + t * 31), tone = t > .55 ? 't3' : t > .25 ? 't2' : '';
      return '<button type="button" class="' + tone + '" style="font-size:' + size + 'px" title="' + w[1] + ' mentions">' + esc(w[0]) + '</button>';
    }).join(' ');
  }
  cloudEl.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    input.value = b.textContent; KIND = 'all'; go(true);
  });

  function go(scroll) {
    var q = input.value.trim(); LIMIT = 60;
    try { history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) + (KIND !== 'all' ? '&type=' + KIND : '') : location.pathname); } catch (e) {}
    search(q);
    if (q && scroll) resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); KIND = 'all'; go(true); });

  fetch('../data/topics.json').then(function (r) { return r.json(); }).then(function (d) {
    d.docs.forEach(function (x) { x.f = fold(x.text); });
    d.qna.forEach(function (s) { s.items.forEach(function (i) { i.f = fold(i.text); }); });
    DATA = d; drawCloud();
    var p = new URLSearchParams(location.search), t = (p.get('type') || '').toLowerCase().replace('q&a', 'qa');
    if (KINDS.some(function (k) { return k[0] === t; })) KIND = t;
    if (p.get('q')) { input.value = p.get('q'); search(p.get('q')); } else search('');
  }).catch(function () { statusEl.textContent = 'The teachings could not be loaded. Please reload the page.'; });
})();
