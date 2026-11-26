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
  var KINDS = [['video', 'Videos'], ['audio', 'Audio'], ['ama', 'AMA sessions'], ['writings', 'Writings'], ['book', 'The Book']];   // the Library order (D, 25 Nov 2026)
  var SCOPE_NAME = { writings: 'the Writings', ama: 'the AMA sessions', video: 'the videos', audio: 'the audio recordings', book: 'The Mind Illuminated' };
  function selected() { return KINDS.map(function (k) { return k[0]; }).filter(function (k) { return SEL[k]; }); }
  function scopeText() {
    var s = selected().map(function (k) { return SCOPE_NAME[k]; });
    if (!s.length) return 'across the site';
    return 'in ' + (s.length === 1 ? s[0] : s.slice(0, -1).join(', ') + ' and ' + s[s.length - 1]);
  }
  // Pāli and Sanskrit forms of the same word find each other (D, 25 Nov 2026): Culadasa mostly said the Pāli,
  // sometimes the Sanskrit (nirvana, karma, dharma, arhat), and the transcripts keep what he said.
  var SYN = [['jhana', 'dhyana', 'jana', 'jhanna', 'janna'], ['metta', 'maitri', 'meta'], ['piti', 'priti', 'peeti'], ['sukha', 'suka', 'sukka'], ['dukkha', 'dukha', 'dukka'], ['samadhi', 'samadi'], ['nimitta', 'nimita'], ['upekkha', 'upeka', 'upekha'], ['sampajanna', 'sampajana'], ['nibbana', 'nirvana', 'nibana'], ['kamma', 'karma'], ['dhamma', 'dharma'],
    ['arahant', 'arhat'], ['anatta', 'anatman', 'anata'], ['dukkha', 'duhkha'], ['vipassana', 'vipashyana', 'vipasyana', 'vipasana'], ['samatha', 'shamatha', 'samata'],
    ['sotapanna', 'srotapanna'], ['sunnata', 'sunyata', 'shunyata'], ['khandha', 'skandha'], ['sutta', 'sutra'], ['bodhisatta', 'bodhisattva'],
    ['tanha', 'trishna'], ['sankhara', 'samskara'], ['kilesa', 'klesha', 'klesa'], ['sila', 'shila'], ['panna', 'prajna'], ['avijja', 'avidya']];
  // After "stage" or "stages", a number and its word are the same ("stage 4" also finds "stage four", which is how the
  // video captions write it), but only there, so "one" elsewhere does not find every "1" (D, 26 Nov 2026)
  var NUMW = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
  function wordRe(arr, i) {
    var w = arr[i], prev = i > 0 ? arr[i - 1] : '';
    if (/^stages?$/.test(prev)) {
      var n = /^(10|[1-9])$/.test(w) ? +w : NUMW.indexOf(w) + 1;
      if (n >= 1 && n <= 10) return '(?:' + n + '|' + NUMW[n - 1] + ')';
    }
    return alts(w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  }
  function alts(w) { for (var i = 0; i < SYN.length; i++) if (SYN[i].indexOf(w) >= 0) return '(?:' + SYN[i].join('|') + ')'; return w; }
  // The Mind Illuminated (D, 25 Nov 2026): the book is not on this site. Its index gives, for any word, the pages it is on;
  // for a set list of teaching terms also the chapter, heading, paragraph and line, and at most three short phrases,
  // one per page (the limits of Google Books' snippet view). Loaded only when a search covers the book.
  var BOOK = null, bookLoading = false;
  var OPEN = {}, OPENROW = {}, lastQ = '';   // sections the reader opened; kept when late data (book, transcripts) redraws the same search
  var GROUP = { video: [0, 'Videos'], ama: [1, 'AMA sessions'], writings: [2, 'Writings'], about: [2, 'Writings'], all: [2, 'Writings'], audio: [3, 'Audio'], book: [4, 'The Book'] };   // the same kinds as the lozenges
  var TR = null, trLoading = false;   // the video transcripts: loaded only when a search needs them
  var TYPE_OF = { 'Handout': 'writings', 'Essay': 'writings', 'Q&A': 'ama', 'Interview': 'all', 'Lineage': 'about', 'Video': 'video', 'Audio': 'audio' };
  var ALIAS = { 'tmi': 'book', 'the-book': 'book', 'mind-illuminated': 'book', 'qa': 'ama', 'q&a': 'ama', 'handout': 'writings', 'handouts': 'writings', 'essay': 'writings', 'essays': 'writings', 'videos': 'video', 'audios': 'audio', 'recordings': 'audio' };

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
  // AMA results say "Open the video" and open it on YouTube, at the first mention when the transcript has one (D, 25 Nov 2026);
  // a second link opens the session's questions on the AMA sessions page.
  // Links that leave the site, and PDFs, open in a new tab (D, 24 Nov 2026).
  function nt(u) { return /^https?:/.test(u) || /\.pdf$/i.test(u) ? ' target="_blank" rel="noopener"' : ''; }
  function isLetter(ch) { return /[a-z0-9À-ɏḀ-ỿ]/i.test(ch || ''); }
  // Find matches in folded text: word-start boundary checked by hand (no lookbehind, so older Safari works).
  function matcher(q) {
    var words = fold(q.trim()).split(/\s+/).map(function (w, i, arr) { return wordRe(arr, i); });
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
    var res = words.map(function (w, i, arr) { return new RegExp(wordRe(arr, i) + "[a-z0-9À-ɏḀ-ỿ]*", 'g'); });
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
    var wantVideo = !selected().length || SEL.video || SEL.ama;
    if (wantVideo && !TR) loadTranscripts();
    if (TR) {
      var byVid = {};
      items.forEach(function (i) { var m = /[?&]v=([\w-]{11})/.exec(i.url || ''); if (m && i.kind === 'video') byVid[m[1]] = i; });
      // AMA session recordings count as AMA sessions: the title opens the session on the AMA page, the times open the video (D, 25 Nov 2026)
      var amaTitle = {}, amaItem = {};
      DATA.qna.forEach(function (q) { if (q.video) amaTitle[q.video] = q.title; });
      items.forEach(function (i) { var m = /#s-([\w-]{11})$/.exec(i.url || ''); if (m && i.kind === 'ama') amaItem[m[1]] = i; });
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
        if (amaTitle[v.id]) {
          var a = amaItem[v.id];
          if (a) { a.n += cnt(hits); a.snips = snips; a.first = first; }
          else items.push({ kind: 'ama', label: 'AMA', title: amaTitle[v.id], url: '../online-meetings/#s-' + v.id, n: cnt(hits), credit: 'Transcript', snips: snips, first: first });
          return;
        }
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
    if (!clean) { statusEl.textContent = 'Type a word or a question, or choose one from the cloud.'; drawFilters({}); return; }
    if (!/[A-Za-zÀ-ɏḀ-ỿ]/.test(clean) || fold(clean).replace(/[^a-z0-9]/g, '').length < 2) { statusEl.textContent = 'Type at least two letters.'; drawFilters({}); return; }
    // Several words: first the exact phrase; if that finds nothing anywhere, passages where all the words
    // (common ones like "what" and "the" left out) appear close together (D, 25 Nov 2026). Punctuation is ignored.
    var qm = clean.replace(/[^\p{L}\p{N}\s'’\-]/gu, ' ').replace(/\s+/g, ' ').trim() || clean;
    var items = collect(matcher(qm)), near = null;
    if (!items.length && qm.split(' ').length > 1) { near = nearMatcher(qm); if (near) items = collect(near); }
    var wantBook = !selected().length || SEL.book;
    if (wantBook && !BOOK) loadBook();
    if (BOOK) { var bi = bookItem(qm); if (bi) items.push(bi); }
    var wantVideo = !selected().length || SEL.video || SEL.ama;
    // grouped by kind (D, 25 Nov 2026): videos, AMA sessions, writings, audio, then the book; most mentions first within each
    items.sort(function (a, b) { return (GROUP[a.kind] || [9])[0] - (GROUP[b.kind] || [9])[0] || b.n - a.n || a.title.localeCompare(b.title); });
    var counts = { all: items.length }; items.forEach(function (i) { counts[i.kind] = (counts[i.kind] || 0) + 1; });
    drawFilters(counts);
    var on = selected(), shown = on.length ? items.filter(function (i) { return SEL[i.kind]; }) : items;
    var total = shown.reduce(function (s, i) { return s + i.n; }, 0);
    statusEl.textContent = (near && shown.length ? 'The exact words “' + clean + '” are not in the teachings, so these are passages where ' + near.words.map(function (w) { return '“' + w + '”'; }).join(', ') + ' all appear close together. ' : '') + (shown.length ? ((wantVideo && !TR) || (wantBook && !BOOK) ? 'Still searching… ' : '') + total + (near ? ' place' + (total === 1 ? '' : 's') : ' mention' + (total === 1 ? '' : 's') + ' of “' + clean + '”') + ' in ' + shown.length + ' source' + (shown.length === 1 ? '' : 's') + ' ' + scopeText() + (near ? ', most first.' : ', most mentions first.')
      : ((wantVideo && !TR) || (wantBook && !BOOK) ? 'Searching the video transcripts and the book… ' : '') + 'No mentions of “' + clean + '” ' + scopeText() + '.' + (on.length && items.length ? ' Press Clear to see ' + items.length + ' source' + (items.length === 1 ? '' : 's') + ' across the site.' : ' Try a shorter or different word.'));
    // Nested results (D, 25 Nov 2026): one section per kind, the same kinds as the lozenges, in the order videos, AMA sessions,
    // writings, audio, the book. Each shows its three strongest results; its title or "See all" opens the rest, and
    // "Show fewer" at the bottom closes it again. With one kind chosen, its section opens in full.
    // Each source is one title row (D, 25 Nov 2026): click it to see where the word appears in it, click again to close.
    // The link to the source itself sits inside, as the title now opens and closes the row.
    var OPEN_LABEL = { video: 'Open the video', ama: 'Open the video', writings: 'Open', about: 'Open the page', all: 'Open', audio: 'Open the recording', book: 'About the book' };
    function openLinks(i) {
      var m = i.kind === 'ama' && /#s-([\w-]{11})$/.exec(i.url || '');
      if (m) {
        var v = i.first || 'https://www.youtube.com/watch?v=' + m[1];
        return '<a href="' + esc(v) + '" target="_blank" rel="noopener">Open the video →</a><a href="' + esc(i.url) + '">All questions in this session →</a>';
      }
      return '<a href="' + esc(i.url) + '"' + nt(i.url) + '>' + esc(OPEN_LABEL[i.kind] || 'Open') + ' →</a>';
    }
    function card(i) {
      var said = (i.snips || []).map(function (s) { return '<p>' + s + '</p>'; }).join('');
      var body = i.qa
        ? '<ol class="qlist">' + i.qa.slice(0, 6).map(function (x) { return '<li><a class="t" href="' + esc(x.it.url) + '"' + nt(x.it.url) + '>' + esc(x.it.t) + '</a> <span class="qsnip">' + snippet(x.it.text, x.hits, 0) + '</span></li>'; }).join('') + '</ol>' + (i.qa.length > 6 ? '<p class="small muted">and ' + (i.qa.length - 6) + ' more questions in this session</p>' : '') + (said ? '<p class="small muted said">In the recording:</p>' + said : '')
        : (i.html || said);
      var key = i.kind + '|' + i.title, open = !!OPENROW[key];
      var meta = i.n + (near ? (i.n === 1 ? ' place' : ' places') : (i.n === 1 ? ' mention' : ' mentions')) + (i.credit ? ' · ' + i.credit : '');
      return '<article class="result rrow' + (i.kind === 'book' ? ' result-book' : '') + (open ? ' open' : '') + '" data-key="' + esc(key) + '">' +
        '<h3><button type="button" class="rr-title" aria-expanded="' + open + '"><span class="rr-name">' + esc(i.title) + '</span><span class="rr-meta">' + esc(meta) + '</span></button></h3>' +
        '<div class="rr-body">' + body + '<p class="rr-open">' + openLinks(i) + '</p></div></article>';
    }
    var groups = [];
    shown.forEach(function (i) {
      var g = GROUP[i.kind] || [9, 'More'];
      var last = groups[groups.length - 1];
      if (!last || last.name !== g[1]) groups.push(last = { name: g[1], items: [] });
      last.items.push(i);
    });
    var single = selected().length === 1;
    if (clean !== lastQ) { OPEN = {}; OPENROW = {}; lastQ = clean; }
    resultsEl.innerHTML = stageLink(clean) + (groups.length ? '<p class="rr-hint">Click a title to see where it’s mentioned.</p>' : '') + groups.map(function (g, gi) {
      var m = g.items.reduce(function (s, i) { return s + i.n; }, 0), extra = g.items.length - 4, open = single || extra <= 0 || !!OPEN[g.name];
      return '<section class="rgroup' + (open ? ' open' : '') + '" data-g="' + gi + '" data-name="' + esc(g.name) + '">' +
        '<h2 class="result-group"><button type="button" class="rg-toggle" aria-expanded="' + open + '">' + esc(g.name) + ' <span class="rg-count">' + g.items.length + ' source' + (g.items.length === 1 ? '' : 's') + ' · ' + m + (near ? ' places' : ' mentions') + '</span></button></h2>' +
        g.items.map(function (i, k) { return k < 4 ? card(i) : '<div class="rg-more">' + card(i) + '</div>'; }).join('') +
        (extra > 0 ? '<p class="rg-foot"><button type="button" class="linklike rg-all">Show all ' + g.items.length + ' in ' + esc(g.name) + '</button><button type="button" class="linklike rg-less">Show fewer</button></p>' : '') +
        '</section>';
    }).join('');
  }

  // A search for a stage ("stage 4", "stage four", "fourth stage") or for "ten stages" first offers that stage's page,
  // with a video to start with and everything he said about it (D, 25 Nov 2026)
  var STAGE_NAMES = ['Establishing a practice', 'Interrupted attention and overcoming mind-wandering', 'Extended attention and overcoming forgetting',
    'Continuous attention and overcoming gross distraction and strong dullness', 'Overcoming subtle dullness and increasing mindfulness',
    'Subduing subtle distraction', 'Exclusive attention and unifying the mind', 'Mental pliancy and pacifying the senses',
    'Mental and physical pliancy and calming the intensity of meditative joy', 'Tranquility and equanimity'];
  var SW = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'];
  var SO = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth'];
  function stageLink(q) {
    var f = fold(q).replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim(), n = 0, m;
    if ((m = /^stage (10|[1-9]|[a-z]+)$/.exec(f))) n = /\d/.test(m[1]) ? +m[1] : SW.indexOf(m[1]) + 1;
    else if ((m = /^(?:the )?([a-z]+) stage$/.exec(f))) n = SO.indexOf(m[1]) + 1;
    var base = location.pathname.indexOf('/topics/') >= 0 || location.pathname.indexOf('/the-book/') >= 0 ? '../' : '';
    if (n >= 1 && n <= 10) {
      var W = SW[n - 1].charAt(0).toUpperCase() + SW[n - 1].slice(1);
      return '<p class="stage-callout"><a href="' + base + 'ten-stages/stage-' + n + '/"><strong>Stage ' + W + ': ' + esc(STAGE_NAMES[n - 1]) + '</strong> — a video to start with and everything he said about this stage →</a></p>';
    }
    if (/^(the )?(10|ten) stages?$/.test(f)) return '<p class="stage-callout"><a href="' + base + 'ten-stages/"><strong>The ten stages</strong> — each stage with a video to start with and everything he said about it →</a></p>';
    return '';
  }

  function hms(s) { var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), x = s % 60; return (h ? h + ':' + (m < 10 ? '0' : '') : '') + m + ':' + (x < 10 ? '0' : '') + x; }
  // the time stamp in force at a place in a transcript (marks: [position in text, seconds], in order)
  function timeAt(v, pos) {
    var lo = 0, hi = v.marks.length - 1;
    while (lo < hi) { var mid = (lo + hi + 1) >> 1; if (v.marks[mid][0] <= pos) lo = mid; else hi = mid - 1; }
    return v.marks.length ? v.marks[lo][1] : 0;
  }
  function loadBook() {
    if (bookLoading) return; bookLoading = true;
    fetch('../data/book.json').then(function (r) { return r.json(); }).then(function (d) {
      d.keys = Object.keys(d.words).sort(); d.stopSet = {}; (d.stop || []).forEach(function (w) { d.stopSet[w] = 1; }); BOOK = d;
      if (input.value.trim()) search(input.value.trim());
    }).catch(function () { bookLoading = false; });
  }
  function bookPlace(l, full) {
    var p = BOOK.pages[l[0]], h = l[1] >= 0 ? BOOK.headings[l[1]] : '';
    var where = [p[1], p[2]].filter(Boolean).join(': ');
    return 'p. ' + esc(p[0]) + (where ? ' · ' + esc(where) : '') + (h && h !== p[2] ? ' · ' + esc(h) : '') + (full ? ' · paragraph ' + l[2] + ', line ' + l[3] : '');
  }
  function markIn(text, q) {
    var h = matcher(q)(text, fold(text)), out = '', pos = 0;
    h.forEach(function (x) { out += esc(text.slice(pos, x[0])) + '<mark>' + esc(text.slice(x[0], x[1])) + '</mark>'; pos = x[1]; });
    return out + esc(text.slice(pos));
  }
  var BOOK_STOP = { the: 1, and: 1, for: 1, are: 1, but: 1, not: 1, you: 1, all: 1, can: 1, was: 1, his: 1, her: 1, what: 1, how: 1, why: 1, when: 1, does: 1, with: 1, this: 1, that: 1, from: 1, into: 1, about: 1, there: 1, their: 1, which: 1, who: 1, will: 1, would: 1, should: 1, could: 1 };
  function bookItem(q) {
    var fq = fold(q).replace(/[^a-z0-9'\- ]/g, ' ').replace(/\s+/g, ' ').trim();
    if (!fq) return null;
    var item = { kind: 'book', label: 'The Mind Illuminated', title: 'The Mind Illuminated — in the book', url: '../the-book/', credit: 'Not on this site: find it in your copy · ' + 'first edition, 2015' };
    var term = null, tries = [fq];
    SYN.forEach(function (g) { if (g.indexOf(fq) >= 0) tries = tries.concat(g); });   // "jana" also tries jhana and dhyana
    BOOK.terms.forEach(function (t) { if (!term && t.f.some(function (f) { return tries.some(function (x) { return f === x || f + 's' === x || x + 's' === f; }); })) term = t; });
    if (term) {
      var ph = term.ph.map(function (x) { return '<p class="bookph">“' + markIn(x[1], q) + '”<br><span class="small muted">' + bookPlace(term.loc[x[0]], true) + '</span></p>'; }).join('');
      var all = term.loc.slice(0, 40).map(function (l) { return '<span title="' + bookPlace(l, true).replace(/"/g, '&quot;') + '">' + esc(BOOK.pages[l[0]][0]) + '</span>'; }).join(', ');
      item.n = term.n;
      item.html = ph + '<p class="small bookall"><strong>All ' + term.n + ' places, by page:</strong> ' + all + (term.n > 40 ? ' and ' + (term.n - 40) + ' more' : '') + '.</p>';
      return item;
    }
    // common words ("what", "between") are not in the book's index, so they are left out of the search, as they are elsewhere
    var words = fq.split(' ').filter(function (w) { return w.length > 2 && !BOOK_STOP[w] && !BOOK.stopSet[w]; });
    if (!words.length) return null;
    var pages = null;
    for (var i = 0; i < words.length; i++) {
      var w = words[i], set = {};
      // word start, like the rest of the search: "awaken" also finds "awakening"
      var lo = 0, hi = BOOK.keys.length;
      while (lo < hi) { var mid = (lo + hi) >> 1; if (BOOK.keys[mid] < w) lo = mid + 1; else hi = mid; }
      for (var k = lo; k < BOOK.keys.length && BOOK.keys[k].indexOf(w) === 0; k++) BOOK.words[BOOK.keys[k]].forEach(function (p) { set[p] = 1; });
      var list = Object.keys(set).map(Number);
      pages = pages === null ? list : pages.filter(function (p) { return set[p]; });
      if (!pages.length) return null;
    }
    pages.sort(function (a, b) { return a - b; });
    item.n = pages.length;
    item.html = '<p class="small bookall"><strong>On ' + pages.length + ' page' + (pages.length === 1 ? '' : 's') + ':</strong> ' +
      pages.slice(0, 40).map(function (p) { var P = BOOK.pages[p]; return esc(P[0]) + (P[2] || P[1] ? ' <span class="muted">(' + esc(P[2] || P[1]) + ')</span>' : ''); }).join(', ') +
      (pages.length > 40 ? ' and ' + (pages.length - 40) + ' more' : '') + '.</p>';
    return item;
  }

  function loadTranscripts() {
    if (trLoading) return; trLoading = true;
    fetch('../data/transcripts.json').then(function (r) { return r.json(); }).then(function (d) {
      d.videos.forEach(function (v) { v.f = fold(v.text); });
      TR = d.videos;
      if (input.value.trim()) search(input.value.trim());
    }).catch(function () { trLoading = false; });
  }

  resultsEl.addEventListener('click', function (e) {
    var t = e.target.closest('.rr-title');
    if (t) { var row = t.closest('.rrow'), o = !row.classList.contains('open'); row.classList.toggle('open', o); t.setAttribute('aria-expanded', o); OPENROW[row.getAttribute('data-key')] = o; return; }
    var b = e.target.closest('.rg-toggle, .rg-all, .rg-less'); if (!b) return;
    var sec = b.closest('.rgroup'), open = b.classList.contains('rg-less') ? false : b.classList.contains('rg-all') ? true : !sec.classList.contains('open');
    sec.classList.toggle('open', open);
    OPEN[sec.getAttribute('data-name')] = open;
    sec.querySelector('.rg-toggle').setAttribute('aria-expanded', open);
    if (!open) sec.scrollIntoView({ block: 'start', behavior: 'smooth' });
  });

  function drawFilters(counts) {
    var searched = counts.all !== undefined;   // before a search the pills show without numbers
    filtersEl.innerHTML = '<button type="button" class="scope-all" data-k="all" aria-pressed="' + !selected().length + '">All' + (searched ? ' <span class="muted">' + counts.all + '</span>' : '') + '</button>' + KINDS.map(function (k) {
      return '<button type="button" data-k="' + k[0] + '" aria-pressed="' + !!SEL[k[0]] + '">' + esc(k[1]) + (searched ? ' <span class="muted">' + (counts[k[0]] || 0) + '</span>' : '') + '</button>';
    }).join('') + '<button type="button" class="scope-clear" data-k="clear">Clear</button>';
  }
  filtersEl.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var k = b.getAttribute('data-k');
    if (k === 'all') SEL = {}; else if (k === 'clear') { SEL = {}; input.value = ''; } else SEL[k] = !SEL[k];   // All: the whole site; Clear: start again
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
