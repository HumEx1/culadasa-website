"""Every place Culadasa talks about each of the ten stages, for the stage pages (D, 25 Nov 2026).

Usage:  python3 tools/build_stages.py          (reads redesign/data/, writes redesign/data/stages.json)

Sources: the video transcripts (transcripts.json), Alex's AMA questions, the writings and the audio descriptions
(topics.json), and the book's chapter pages (book.json). The matching rules are written out in docs/STAGES.md;
keep the two in step.
"""
import re, json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'redesign' / 'data'
tr = json.loads((D / 'transcripts.json').read_text())['videos']
tp = json.loads((D / 'topics.json').read_text())
book = json.loads((D / 'book.json').read_text())

WORDS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']
ORD = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']
NUM = r'(?:10|[1-9]|' + '|'.join(WORDS) + r')'
SEP = r'(?:\s*(?:,|&amp;|&|and|or|to|through|thru|-|–)\s*|\s+)'
# "stage four", "stage 4", "stages five and six", "stages two to four", "stage one two three"
NUMBERED = re.compile(r'\bstages?\s+(' + NUM + r'(?:' + SEP + NUM + r')*)\b', re.I)
# "the fourth stage" (only when nothing nearby says it is a stage of awakening or insight)
ORDINAL = re.compile(r'\b(' + '|'.join(ORD) + r')\s+stage\b', re.I)
NOT_AFTER = re.compile(r'\s+(?:of\s+(?:awakening|insight|the\s+path|enlightenment|samatha\s+vipassana|the\s+journey)|path|nana|ñāṇa)\b', re.I)
NOT_NEAR = re.compile(r'awakening|\bpath\b|insight|stream|jh[aā]na|fetter|feather', re.I)


def value(tok):
    tok = tok.lower()
    return int(tok) if tok.isdigit() else WORDS.index(tok) + 1


def stages_in(m):
    """The stages a NUMBERED match names. Ranges of more than four stages ("stages one to six") are about the
    stages in general, so they count for none of them."""
    toks = re.findall(NUM, m.group(1), re.I)
    seps = re.findall(SEP, m.group(1), re.I)
    out = {value(toks[0])}
    for i in range(1, len(toks)):
        a, b = value(toks[i - 1]), value(toks[i])
        if re.search(r'to|through|thru|-|–', seps[i - 1] if i - 1 < len(seps) else '', re.I) and a < b:
            if b - a + 1 > 4:
                return set()
            out.update(range(a, b + 1))
        else:
            out.add(b)
    return {s for s in out if 1 <= s <= 10}


def hits(text):
    """[(start, end, set of stages)] for every mention of a numbered stage in the text."""
    found = []
    for m in NUMBERED.finditer(text):
        if NOT_AFTER.match(text, m.end()) or re.search(r'insight\s+$', text[max(0, m.start() - 9):m.start()], re.I):
            continue
        s = stages_in(m)
        if s:
            found.append((m.start(), m.end(), s))
    for m in ORDINAL.finditer(text):
        if NOT_AFTER.match(text, m.end()) or NOT_NEAR.search(text[max(0, m.start() - 100):m.end() + 100]):
            continue
        found.append((m.start(), m.end(), {ORD.index(m.group(1).lower()) + 1}))
    return sorted(found)


def snippet(text, a, b, before=120, after=160):
    """The words around a mention, cut at word boundaries, the mention marked."""
    s, e = max(0, a - before), min(len(text), b + after)
    if s > 0:
        s = text.find(' ', s, a) + 1 or s
    if e < len(text):
        e = text.rfind(' ', b, e) if text.rfind(' ', b, e) > b else e
    clean = lambda x: html.escape(re.sub(r'\s+', ' ', html.unescape(x)))
    return ('…' if s > 0 else '') + clean(text[s:a]) + '<mark>' + clean(text[a:b]) + '</mark>' + clean(text[b:e]) + ('…' if e < len(text) else '')


def time_at(v, pos):
    t = 0
    for p, s in v['marks']:
        if p > pos:
            break
        t = s
    return t


ama_title = {q['video']: q['title'] for q in tp['qna'] if q.get('video')}
for v in tr:   # one title was cut short on download ("... - RE-UPLOAD WI"): show it without the cut-off end
    v['title'] = re.sub(r'\s*-\s*RE-UPLOAD.*$', '', v['title'])
out = [{'n': n, 'videos': [], 'ama': {}, 'writings': [], 'audio': [], 'book': None} for n in range(1, 11)]

# videos and AMA recordings: one moment per time stamp (mentions a few seconds apart are one moment)
for v in tr:
    per = {}
    for a, b, ss in hits(v['text']):
        t = time_at(v, a)
        for s in ss:
            moments = per.setdefault(s, [])
            if moments and t - moments[-1][0] < 25:
                moments[-1][2] += 1
                continue
            moments.append([t, snippet(v['text'], a, b), 1])
    for s, moments in per.items():
        n = sum(m[2] for m in moments)
        rec = {'id': v['id'], 'title': v['title'], 'date': v['date'], 'n': n, 'moments': [[t, sn] for t, sn, _ in moments]}
        if v['id'] in ama_title:
            out[s - 1]['ama'].setdefault(v['id'], {'id': v['id'], 'title': ama_title[v['id']], 'n': 0, 'questions': [], 'moments': []})
            a_ = out[s - 1]['ama'][v['id']]
            a_['n'] += n
            a_['moments'] = rec['moments']
        else:
            out[s - 1]['videos'].append(rec)

# Alex's AMA questions
for q in tp['qna']:
    if not q.get('video'):
        continue
    for it in q['items']:
        for a, b, ss in hits(it['text']):
            for s in ss:
                out[s - 1]['ama'].setdefault(q['video'], {'id': q['video'], 'title': q['title'], 'n': 0, 'questions': [], 'moments': []})
                a_ = out[s - 1]['ama'][q['video']]
                a_['n'] += 1
                if not a_['questions'] or a_['questions'][-1][1] != it['url']:
                    a_['questions'].append([it['t'], it['url'], snippet(it['text'], a, b, 160, 200)])

# writings and audio descriptions
for d in tp['docs']:
    kind = 'audio' if d['type'] == 'Audio' else None if d['type'] == 'Video' else 'writings'
    if not kind:
        continue
    per = {}
    for a, b, ss in hits(d['text']):
        for s in ss:
            per.setdefault(s, []).append(snippet(d['text'], a, b))
    for s, snips in per.items():
        out[s - 1][kind].append({'title': d['title'], 'url': d['url'], 'n': len(snips), 'snips': snips})

# the book: the pages of each stage's chapter (2015 final draft). A chapter runs from its first page to the page
# before the next part starts (its last pages carry no running footer, so they are counted with it)
parts = []
for p in book['pages']:
    if p[1] and (not parts or parts[-1][0] != p[1]):
        parts.append([p[1], []])
    if parts:
        parts[-1][1].append(p[0])
for s in range(1, 11):
    for name, pages in parts:
        if name == f'Stage {WORDS[s - 1].title()}':
            out[s - 1]['book'] = {'first': pages[0], 'last': pages[-1], 'pages': len(pages)}


# The videos the teachers choose, stage number -> (video id, start in seconds). Record each choice in docs/STAGES.md too.
CHOSEN = {}

# the video to start with, until the teachers choose one: the video or AMA recording where he talks about the stage
# longest, measured as the most moments within ten minutes; a talk wins a tie. It starts five seconds before that stretch.
for st in out:
    st['ama'] = sorted(st['ama'].values(), key=lambda x: -x['n'])
    for k in ('videos', 'writings', 'audio'):
        st[k].sort(key=lambda x: -x['n'])
    best = None
    for c in st['videos'] + st['ama']:
        ts = [m[0] for m in c['moments']]
        for t in ts:
            score = sum(1 for x in ts if t <= x < t + 600)
            key = (score, c in st['videos'])
            if not best or key > best[0]:
                best = (key, c, t)
    if st['n'] in CHOSEN:
        vid, start = CHOSEN[st['n']]
        title = next((v['title'] for v in tr if v['id'] == vid), ama_title.get(vid, ''))
        st['pin'] = {'id': vid, 'title': title, 'start': start, 'chosen': True, 'ama': vid in ama_title}
        continue
    if best:
        (score, _), c, t = best
        st['pin'] = {'id': c['id'], 'title': c['title'], 'start': max(0, t - 5), 'moments': score, 'ama': c in st['ama']}

(D / 'stages.json').write_text(json.dumps({'stages': out}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
for st in out:
    print(f"Stage {st['n']}: videos {len(st['videos'])} ({sum(v['n'] for v in st['videos'])}), AMA {len(st['ama'])} ({sum(a['n'] for a in st['ama'])}), "
          f"writings {len(st['writings'])}, audio {len(st['audio'])}, book {st['book']}, pin {st.get('pin', {}).get('title')}")
