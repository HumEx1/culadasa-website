/* Topics: a word cloud and a search ranked purely by number of mentions.
   Rule (Darin, 24 Nov 2026): rank by how often a document mentions the word,
   no other rules.  Matching: the word, case-insensitive, at the start of a
   word, so "compassion" also counts "compassionate" and "compassionately". */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var form = $('topic-form'), input = $('q'), cloudEl = $('cloud'), statusEl = $('status'), resultsEl = $('results'), filtersEl = $('filters');
  var DATA = null, KIND = 'All';
  var KINDS = ['All', 'Handout', 'Essay', 'Q&A', 'Interview', 'About', 'Video'];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pattern(q) {
    var words = q.trim().split(/\s+/).map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); });
    // a phrase: the words in order, the last one may continue (prefix)
    return new RegExp('(?<![\\p{L}\\p{M}])' + words.join('[\\s\\-–—]+') + '[\\p{L}\\p{M}’\'-]*', 'giu');
  }
  function count(text, re) { re.lastIndex = 0; var n = 0; while (re.exec(text)) n++; return n; }
  function snippets(text, re, max) {
    re.lastIndex = 0; var out = [], m, last = -400;
    while ((m = re.exec(text)) && out.length < max) {
      if (m.index - last < 260) continue;
      last = m.index;
      var a = Math.max(0, m.index - 110), b = Math.min(text.length, m.index + m[0].length + 140);
      var s = (a > 0 ? '…' : '') + text.slice(a, b).replace(/\s+/g, ' ') + (b < text.length ? '…' : '');
      out.push(s);
    }
    return out;
  }
  function mark(s, re) { re.lastIndex = 0; return esc(s).replace(new RegExp(re.source, 'giu'), function (w) { return '<mark>' + w + '</mark>'; }); }
  function rel(url) { return /^https?:/.test(url) ? url : url; }

  function search(q) {
    resultsEl.innerHTML = '';
    if (!q || q.trim().length < 2) { statusEl.textContent = 'Type a word, or choose one from the cloud.'; return; }
    var re = pattern(q), items = [];
    DATA.docs.forEach(function (d) {
      var n = count(d.text, re);
      if (n) items.push({ kind: d.type, title: d.title, url: d.url, n: n, credit: d.credit, snips: snippets(d.text, re, 3) });
    });
    DATA.qna.forEach(function (s) {
      var hits = [], n = 0;
      s.items.forEach(function (it) { var c = count(it.text, re); if (c) { n += c; hits.push(it); } });
      if (n) items.push({ kind: 'Q&A', title: s.title, url: s.url, n: n, qa: hits });
    });
    items.sort(function (a, b) { return b.n - a.n || a.title.localeCompare(b.title); });
    var counts = { All: items.length }; items.forEach(function (i) { counts[i.kind] = (counts[i.kind] || 0) + 1; });
    drawFilters(counts);
    var shown = KIND === 'All' ? items : items.filter(function (i) { return i.kind === KIND; });
    var total = items.reduce(function (s, i) { return s + i.n; }, 0);
    statusEl.textContent = items.length ? total + ' mentions of “' + q.trim() + '” in ' + items.length + ' sources, most mentions first.' : 'No mentions of “' + q.trim() + '”. Try a shorter or different word.';
    resultsEl.innerHTML = shown.slice(0, 60).map(function (i) {
      var body = i.qa
        ? '<ol class="qlist">' + i.qa.slice(0, 6).map(function (it) { return '<li><a class="t" href="' + esc(it.url) + '" rel="noopener">' + it.t + '</a> ' + mark(it.text.length > 320 ? it.text.slice(0, 320) + '…' : it.text, re) + '</li>'; }).join('') + '</ol>' + (i.qa.length > 6 ? '<p class="small muted">and ' + (i.qa.length - 6) + ' more questions in this session</p>' : '')
        : i.snips.map(function (s) { return '<p>' + mark(s, re) + '</p>'; }).join('');
      return '<article class="result"><div class="meta"><span>' + esc(i.kind) + '</span><span class="hits">' + i.n + (i.n === 1 ? ' mention' : ' mentions') + '</span>' + (i.credit ? '<span>' + esc(i.credit) + '</span>' : '') + '</div>' +
        '<h3><a href="' + esc(rel(i.url)) + '"' + (/^https?:/.test(i.url) ? ' rel="noopener"' : '') + '>' + esc(i.title) + '</a></h3>' + body + '</article>';
    }).join('');
  }

  function drawFilters(counts) {
    filtersEl.innerHTML = KINDS.filter(function (k) { return k === 'All' || counts[k]; }).map(function (k) {
      return '<button type="button" data-k="' + k + '" aria-pressed="' + (k === KIND) + '">' + (k === 'Q&A' ? 'Q&amp;A' : k === 'All' ? 'All' : k + 's') + ' <span class="muted">' + (counts[k] || 0) + '</span></button>';
    }).join('');
  }
  filtersEl.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    KIND = b.getAttribute('data-k'); search(input.value);
  });

  function drawCloud() {
    var max = DATA.cloud[0][1], min = DATA.cloud[DATA.cloud.length - 1][1];
    var words = DATA.cloud.slice().sort(function (a, b) { return a[0].localeCompare(b[0]); });
    cloudEl.innerHTML = words.map(function (w) {
      var t = (Math.sqrt(w[1]) - Math.sqrt(min)) / (Math.sqrt(max) - Math.sqrt(min));
      var size = Math.round(15 + t * 31), tone = t > .55 ? 't3' : t > .25 ? 't2' : '';
      return '<button type="button" class="' + tone + '" style="font-size:' + size + 'px" title="' + w[1] + ' mentions">' + esc(w[0]) + '</button>';
    }).join(' ');
  }
  cloudEl.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    input.value = b.textContent; go();
  });

  function go() {
    var q = input.value.trim();
    try { history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) + (KIND !== 'All' ? '&type=' + encodeURIComponent(KIND) : '') : location.pathname); } catch (e) {}
    search(q);
    if (q) resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); go(); });

  fetch('../data/topics.json').then(function (r) { return r.json(); }).then(function (d) {
    DATA = d; drawCloud();
    var p = new URLSearchParams(location.search);
    if (p.get('type') && KINDS.indexOf(p.get('type')) >= 0) KIND = p.get('type');
    if (p.get('q')) { input.value = p.get('q'); search(p.get('q')); } else { statusEl.textContent = 'Type a word, or choose one from the cloud.'; drawFilters({ All: 0 }); }
  }).catch(function () { statusEl.textContent = 'The teachings could not be loaded. Please reload the page.'; });
})();
