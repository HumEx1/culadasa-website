/* Topics: a word cloud and a search ranked purely by number of mentions.
   Rule (Darin, 24 Nov 2026): rank by how often a source mentions the word,
   no other rules.  Matching: case-insensitive, accents and apostrophe styles
   ignored ("jhana" finds "jhāna"), at the start of a word, so "compassion"
   also counts "compassionate".  Several words match as a phrase. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var form = $('topic-form'), input = $('q'), cloudEl = $('cloud'), statusEl = $('status'), resultsEl = $('results'), filtersEl = $('filters');
  var DATA = null, SEL = {}, LIMIT = 60;   // SEL: the parts of the site switched on; none switched on = the whole site
  // Scoped search (D, 25 Nov 2026): one box, and pills that each switch a part of the site on or off, independently,
  // so Writings and AMA sessions can be searched together. Clear switches them all off, which searches everything.
  // The count and the status line follow the choice. Writings = handouts and essays. The Lineage page is searched when nothing is switched on.
  var KINDS = [['writings', 'Writings'], ['ama', 'AMA sessions'], ['video', 'Videos'], ['audio', 'Audio']];
  var SCOPE_NAME = { writings: 'the Writings', ama: 'the AMA sessions', video: 'the videos', audio: 'the audio recordings' };
  function selected() { return KINDS.map(function (k) { return k[0]; }).filter(function (k) { return SEL[k]; }); }
  function scopeText() {
    var s = selected().map(function (k) { return SCOPE_NAME[k]; });
    if (!s.length) return 'across the site';
    return 'in ' + (s.length === 1 ? s[0] : s.slice(0, -1).join(', ') + ' and ' + s[s.length - 1]);
  }
  // Pāli and Sanskrit forms of the same word find each other (D, 25 Nov 2026): Culadasa mostly said the Pāli,
  // sometimes the Sanskrit (nirvana, karma, dharma, arhat), and the transcripts keep what he said.
  var SYN = [['jhana', 'dhyana'], ['metta', 'maitri'], ['piti', 'priti'], ['nibbana', 'nirvana'], ['kamma', 'karma'], ['dhamma', 'dharma'],
    ['arahant', 'arhat'], ['anatta', 'anatman'], ['dukkha', 'duhkha'], ['vipassana', 'vipashyana', 'vipasyana'], ['samatha', 'shamatha'],
    ['sotapanna', 'srotapanna'], ['sunnata', 'sunyata', 'shunyata'], ['khandha', 'skandha'], ['sutta', 'sutra'], ['bodhisatta', 'bodhisattva'],
    ['tanha', 'trishna'], ['sankhara', 'samskara'], ['kilesa', 'klesha', 'klesa'], ['sila', 'shila'], ['panna', 'prajna'], ['avijja', 'avidya']];
  function alts(w) { for (var i = 0; i < SYN.length; i++) if (SYN[i].indexOf(w) >= 0) return '(?:' + SYN[i].join('|') + ')'; return w; }
  var TR = null, trLoading = false;   // the video transcripts: loaded only when a search needs them
  var TYPE_OF = { 'Handout': 'writings', 'Essay': 'writings', 'Q&A': 'ama', 'Interview': 'all', 'Lineage': 'about', 'Video': 'video', 'Audio': 'audio' };
  var ALIAS = { 'qa': 'ama', 'q&a': 'ama', 'handout': 'writings', 'handouts': 'writings', 'essay': 'writings', 'essays': 'writings', 'videos': 'video', 'audios': 'audio', 'recordings': 'audio' };

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
  // AMA results open the session on the Culadasa AMA sessions page (opened, outlined, marked in its list); their times still go to the video (D, 25 Nov 2026).
  // Links that leave the site, and PDFs, open in a new tab (D, 24 Nov 2026).
  function nt(u) { return /^https?:/.test(u) || /\.pdf$/i.test(u) ? ' target="_blank" rel="noopener"' : ''; }
  function isLetter(ch) { return /[a-z0-9À-ɏḀ-ỿ]/i.test(ch || ''); }
  // Find matches in folded text: word-start boundary checked by hand (no lookbehind, so older Safari works).
  function matcher(q) {
    var words = fold(q.trim()).split(/\s+/).map(function (w) { return alts(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')); });
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
  // All the words close together (within about 200 characters), in any order. Each place counts once.
  var STOP = {};
  ('a an the and or but of to in on at for with from by as is are was were be been am it its this that these those what which ' +
   'how why when where who whom do does did doing i you he she we they me my your his her our their can could would should ' +
   'will about if not no so there here than then just very into out up any some all more most such have has had').split(' ').forEach(function (w) { STOP[w] = 1; });
  function nearMatcher(q) {
    var all = fold(q).split(/\s+/).filter(Boolean), words = all.filter(function (w) { return !STOP[w.replace(/['’]/g, '')]; });
    if (!words.length) words = all;
    if (words.length < 2) { var one = matcher(words.join(' ')); one.words = words; return words.length ? one : null; }
    var res = words.map(function (w) { return new RegExp(alts(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')) + "[a-z0-9À-ɏḀ-ỿ]*", 'g'); });
    var W = 200;
    var f = function (text, folded) {
      var lists = [];
      for (var i = 0; i < res.length; i++) {
        var l = [], m; res[i].lastIndex = 0;
        while ((m = res[i].exec(folded))) { if (m[0] === '') { res[i].lastIndex++; continue; } if (!isLetter(folded[m.index - 1])) l.push([m.index, m.index + m[0].length]); }
        if (!l.length) return [];
        lists.push(l);
      }
      lists.sort(function (a, b) { return a.length - b.length; });   // walk the rarest word
      var flat = [], count = 0, lastEnd = -1;
      lists[0].forEach(function (a) {
        if (a[0] < lastEnd) return;
        var win = [a];
        for (var j = 1; j < lists.length; j++) {
          var L = lists[j], lo = 0, hi = L.length - 1;   // nearest by binary search: the lists are in text order
          while (lo < hi) { var mid = (lo + hi) >> 1; if (L[mid][0] < a[0]) lo = mid + 1; else hi = mid; }
          var best = null;
          [L[lo - 1], L[lo]].forEach(function (h) { if (h && Math.abs(h[0] - a[0]) <= W && (!best || Math.abs(h[0] - a[0]) < Math.abs(best[0] - a[0]))) best = h; });
          if (!best) return;
          win.push(best);
        }
        count++;
        lastEnd = Math.max.apply(null, win.map(function (h) { return h[1]; }));
        flat = flat.concat(win);
      });
      flat.sort(function (a, b) { return a[0] - b[0]; });
      flat = flat.filter(function (h, i) { return !i || h[0] !== flat[i - 1][0]; });
      flat.count = count;
      return count ? flat : [];
    };
    f.words = words;
    return f;
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

  function cnt(h) { return h.count != null ? h.count : h.length; }
  function collect(find) {
    var items = [];
    DATA.docs.forEach(function (d) {
      var hits = find(d.text, d.f);
      if (hits.length) items.push({ kind: TYPE_OF[d.type], label: d.type === 'Q&A' ? 'AMA' : d.type, title: d.title, url: d.url, n: cnt(hits), credit: d.credit, snips: snippets(d.text, hits, 3) });
    });
    DATA.qna.forEach(function (s) {
      var list = [], n = 0;
      s.items.forEach(function (it) { var h = find(it.text, it.f); if (h.length) { n += cnt(h); list.push({ it: it, hits: h }); } });
      if (n) items.push({ kind: 'ama', label: 'AMA', title: s.title, url: s.video ? '../online-meetings/#s-' + s.video : s.url, n: n, qa: list });
    });
    // Video transcripts (YouTube's automatic captions, Pāli terms corrected): each result links into the video at the moment it is said.
    var wantVideo = !selected().length || SEL.video;
    if (wantVideo && !TR) loadTranscripts();
    if (TR) {
      var byVid = {};
      items.forEach(function (i) { var m = /[?&]v=([\w-]{11})/.exec(i.url || ''); if (m && i.kind === 'video') byVid[m[1]] = i; });
      TR.forEach(function (v) {
        var hits = find(v.text, v.f);
        if (!hits.length) return;
        var snips = [], last = -999;
        for (var k = 0; k < hits.length && snips.length < 3; k++) {
          if (hits[k][0] - last < 260) continue;
          last = hits[k][0];
          var t = timeAt(v, hits[k][0]), u = 'https://www.youtube.com/watch?v=' + v.id + '&t=' + t + 's';
          snips.push('<a class="tstamp" href="' + u + '" target="_blank" rel="noopener">' + hms(t) + '</a> ' + snippet(v.text, hits, k));
        }
        var first = 'https://www.youtube.com/watch?v=' + v.id + '&t=' + timeAt(v, hits[0][0]) + 's';
        var it = byVid[v.id];
        if (it) { it.n += cnt(hits); it.snips = snips; it.label = 'Video'; it.url = first; }
        else items.push({ kind: 'video', label: 'Video', title: v.title, url: first, n: cnt(hits), credit: 'Transcript', snips: snips });
      });
    }
    return items;
  }

  function search(q) {
    resultsEl.innerHTML = '';
    var clean = (q || '').trim();
    if (!clean) { statusEl.textContent = 'Type a word, or choose one from the cloud.'; drawFilters({}); return; }
    if (!/[A-Za-zÀ-ɏḀ-ỿ]/.test(clean) || fold(clean).replace(/[^a-z0-9]/g, '').length < 2) { statusEl.textContent = 'Type at least two letters.'; drawFilters({}); return; }
    // Several words: first the exact phrase; if that finds nothing anywhere, passages where all the words
    // (common ones like "what" and "the" left out) appear close together (D, 25 Nov 2026). Punctuation is ignored.
    var qm = clean.replace(/[^\p{L}\p{N}\s'’\-]/gu, ' ').replace(/\s+/g, ' ').trim() || clean;
    var items = collect(matcher(qm)), near = null;
    if (!items.length && qm.split(' ').length > 1) { near = nearMatcher(qm); if (near) items = collect(near); }
    var wantVideo = !selected().length || SEL.video;
    items.sort(function (a, b) { return b.n - a.n || a.title.localeCompare(b.title); });
    var counts = { all: items.length }; items.forEach(function (i) { counts[i.kind] = (counts[i.kind] || 0) + 1; });
    drawFilters(counts);
    var on = selected(), shown = on.length ? items.filter(function (i) { return SEL[i.kind]; }) : items;
    var total = shown.reduce(function (s, i) { return s + i.n; }, 0);
    statusEl.textContent = (near && shown.length ? 'The exact words “' + clean + '” are not in the teachings, so these are passages where ' + near.words.map(function (w) { return '“' + w + '”'; }).join(', ') + ' all appear close together. ' : '') + (shown.length ? (wantVideo && !TR ? 'Searching the video transcripts too… ' : '') + total + (near ? ' place' + (total === 1 ? '' : 's') : ' mention' + (total === 1 ? '' : 's') + ' of “' + clean + '”') + ' in ' + shown.length + ' source' + (shown.length === 1 ? '' : 's') + ' ' + scopeText() + (near ? ', most first.' : ', most mentions first.')
      : (wantVideo && !TR ? 'Searching the video transcripts… ' : '') + 'No mentions of “' + clean + '” ' + scopeText() + '.' + (on.length && items.length ? ' Press Clear to see ' + items.length + ' source' + (items.length === 1 ? '' : 's') + ' across the site.' : ' Try a shorter or different word.'));
    resultsEl.innerHTML = shown.slice(0, LIMIT).map(function (i) {
      var body = i.qa
        ? '<ol class="qlist">' + i.qa.slice(0, 6).map(function (x) { return '<li><a class="t" href="' + esc(x.it.url) + '"' + nt(x.it.url) + '>' + esc(x.it.t) + '</a> ' + snippet(x.it.text, x.hits, 0) + '</li>'; }).join('') + '</ol>' + (i.qa.length > 6 ? '<p class="small muted">and ' + (i.qa.length - 6) + ' more questions in this session</p>' : '')
        : i.snips.map(function (s) { return '<p>' + s + '</p>'; }).join('');
      return '<article class="result"><div class="meta"><span>' + esc(i.label) + '</span><span class="hits">' + i.n + (near ? (i.n === 1 ? ' place' : ' places') : (i.n === 1 ? ' mention' : ' mentions')) + '</span>' + (i.credit ? '<span>' + esc(i.credit) + '</span>' : '') + '</div>' +
        '<h3><a href="' + esc(i.url) + '"' + nt(i.url) + '>' + esc(i.title) + '</a></h3>' + body + '</article>';
    }).join('') + (shown.length > LIMIT ? '<p><button type="button" class="btn ghost" id="more">Show all ' + shown.length + ' sources</button></p>' : '');
    var more = $('more'); if (more) more.addEventListener('click', function () { LIMIT = 100000; search(clean); });
  }

  function hms(s) { var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60; return (h ? h + ':' + (m < 10 ? '0' : '') : '') + m + ':' + (x < 10 ? '0' : '') + x; }
  // the time stamp in force at a place in a transcript (marks: [position in text, seconds], in order)
  function timeAt(v, pos) {
    var lo = 0, hi = v.marks.length - 1;
    while (lo < hi) { var mid = (lo + hi + 1) >> 1; if (v.marks[mid][0] <= pos) lo = mid; else hi = mid - 1; }
    return v.marks.length ? v.marks[lo][1] : 0;
  }
  function loadTranscripts() {
    if (trLoading) return; trLoading = true;
    fetch('../data/transcripts.json').then(function (r) { return r.json(); }).then(function (d) {
      d.videos.forEach(function (v) { v.f = fold(v.text); });
      TR = d.videos;
      if (input.value.trim()) search(input.value.trim());
    }).catch(function () { trLoading = false; });
  }

  function drawFilters(counts) {
    var searched = counts.all !== undefined;   // before a search the pills show without numbers
    filtersEl.innerHTML = KINDS.map(function (k) {
      return '<button type="button" data-k="' + k[0] + '" aria-pressed="' + !!SEL[k[0]] + '">' + esc(k[1]) + (searched ? ' <span class="muted">' + (counts[k[0]] || 0) + '</span>' : '') + '</button>';
    }).join('') + '<button type="button" class="scope-clear" data-k="clear"' + (selected().length ? '' : ' disabled') + '>Clear</button>';
  }
  filtersEl.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var k = b.getAttribute('data-k');
    if (k === 'clear') SEL = {}; else SEL[k] = !SEL[k];
    go(false);
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
    input.value = b.textContent; go(true);
  });

  function go(scroll) {
    var q = input.value.trim(); LIMIT = 60;
    try { history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) + selected().map(function (k) { return '&type=' + k; }).join('') : location.pathname); } catch (e) {}
    search(q);
    if (q && scroll) resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); go(true); });   // the chosen scope stays

  fetch('../data/topics.json').then(function (r) { return r.json(); }).then(function (d) {
    d.docs.forEach(function (x) { x.f = fold(x.text); });
    d.qna.forEach(function (s) { s.items.forEach(function (i) { i.f = fold(i.text); }); });
    DATA = d; drawCloud();
    var p = new URLSearchParams(location.search);
    p.getAll('type').join(',').toLowerCase().split(',').forEach(function (t) {
      t = ALIAS[t.trim()] || t.trim();
      if (KINDS.some(function (k) { return k[0] === t; })) SEL[t] = true;   // 'all' or unknown values leave the search site-wide
    });
    if (p.get('q')) { input.value = p.get('q'); search(p.get('q')); } else search('');
  }).catch(function () { statusEl.textContent = 'The teachings could not be loaded. Please reload the page.'; });
})();
