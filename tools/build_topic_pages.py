"""Topic pages and the glossary (D, 28 Nov 2026): for each teaching topic, every place Culadasa talks about it.

Usage:  python3 tools/build_topic_pages.py      (reads redesign/data/, writes redesign/data/topic_pages.json)

Sources, as for the stage pages: the video transcripts (transcripts.json), Alex's AMA questions, the writings and the
audio descriptions (topics.json), and the book index (book.json). The topic list and the words that count for each
are below and in docs/TOPICS.md; both are a first draft for the teachers to confirm. Keep the two in step.
"""
import re, json, html, pathlib, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'redesign' / 'data'
tr = json.loads((D / 'transcripts.json').read_text())['videos']
tp = json.loads((D / 'topics.json').read_text())
book = json.loads((D / 'book.json').read_text())

# slug, title, a one-line introduction (draft), the words that count (matched without accents, whole words at the
# start, so "dullness" also finds "dullnesses"), the stages it belongs with, and the book index terms that match.
TOPICS = [
    ('dullness', 'Dullness', 'Drowsiness and the loss of clarity, from strong dullness to subtle dullness.',
     ['dullness', 'subtle dullness', 'strong dullness', 'drowsiness', 'drowsy', 'sleepiness', 'dull'], [4, 5], ['dullness']),
    ('mind-wandering', 'Mind-wandering', 'When attention drifts off the meditation object, and how to come back.',
     ['mind-wandering', 'mind wandering', 'wandering mind', 'mind wanders', 'mind wandered', 'mind wander'], [2, 3], ['mind-wandering']),
    ('distraction', 'Distraction', 'Gross and subtle distraction, and how attention learns to stay.',
     ['distraction', 'distractions', 'distracted', 'gross distraction', 'subtle distraction'], [4, 6], ['distraction']),
    ('forgetting', 'Forgetting', 'Forgetting the meditation object, and the skills that overcome it.',
     ['forgetting', 'forget the breath', 'forgot the breath'], [3], ['forgetting']),
    ('attention-and-awareness', 'Attention and awareness', 'The two ways of knowing that the whole method trains.',
     ['peripheral awareness', 'introspective awareness', 'extrospective awareness', 'attention and awareness'], [1, 2, 3, 4], ['peripheral awareness', 'introspective awareness']),
    ('metacognition', 'Metacognitive awareness', 'Awareness of the state and activity of the mind itself.',
     ['metacognitive', 'metacognition', 'meta-cognitive', 'metacognitive introspective awareness'], [6, 7], ['metacognitive']),
    ('mindfulness', 'Mindfulness', 'Sati: what mindfulness is, in his terms, and how it grows.',
     ['mindfulness', 'mindful', 'sati', 'sampajañña'], [5], ['mindfulness', 'sati']),
    ('mind-system', 'The mind-system', 'His model of the mind as many sub-minds working together.',
     ['mind-system', 'mind system', 'sub-mind', 'submind'], [], ['mind-system', 'sub-minds']),
    ('unification', 'Unification of mind', 'Sub-minds coming together behind one intention.',
     ['unification', 'unified mind', 'unifying the mind', 'ekaggata'], [7, 8], ['unification']),
    ('purification', 'Purification', 'Old material surfacing and being released as practice deepens.',
     ['purification', 'purifying'], [4, 7, 8], ['purification']),
    ('piti', 'Pīti and meditative joy', 'Joy, energy currents and the calming of meditative joy.',
     ['piti', 'meditative joy', 'energy current'], [8, 9], ['piti']),
    ('jhana', 'Jhāna', 'The meditative absorptions, pleasure jhānas and luminous jhānas.',
     ['jhana', 'dhyana'], [], ['jhanas', 'jhana']),
    ('insight', 'Insight', 'Insight experiences and what they reveal about mind and self.',
     ['insight', 'vipassana'], [], ['vipassana', 'insight']),
    ('awakening', 'Awakening and stream entry', 'The stages of awakening, beginning with stream entry.',
     ['stream entry', 'stream-entry', 'stream enterer', 'sotapanna', 'awakening'], [], ['stream entry', 'awakening']),
    ('dark-night', 'The Dark Night', 'A period of distress that can follow an insight breakthrough, and how to meet it.',
     ['dark night'], [], ['dark night']),
    ('equanimity', 'Equanimity', 'Upekkhā: balance that is not disturbed by pleasure or pain.',
     ['equanimity', 'upekkha', 'upekkhā'], [10], ['upekkha', 'equanimity']),
    ('metta', 'Loving-kindness', 'Mettā: loving-kindness practice and the brahmavihāras.',
     ['metta', 'loving kindness', 'lovingkindness', 'brahmavihara'], [], ['loving kindness', 'metta']),
    ('craving', 'Craving', 'Taṇhā: wanting and not-wanting, and the end of suffering.',
     ['craving', 'tanha'], [], ['craving']),
    ('pain', 'Pain', 'Physical and emotional pain in practice, and how to meet it.',
     ['physical pain', 'pain', 'painful'], [4], ['pain']),
    ('daily-life', 'Daily life', 'Practice off the cushion: work, relationships, ordinary days.',
     ['daily life', 'everyday life'], [], ['daily life']),
]


def fold(s):
    """Lower case without accents, one character per character, so positions line up with the original."""
    out = []
    for c in s:
        d = unicodedata.normalize('NFD', c)
        d = ''.join(x for x in d if not unicodedata.combining(x)) or c
        out.append(d[0].lower() if len(d) >= 1 else c.lower())
    return ''.join(out)


# Names and titles that contain a topic word but are not about it (adversarial review, 28 Nov 2026)
EXCLUDE = [r'path of purification', r'insight meditation society', r'insight timer', r'sati the', r'sati,? the fisherman']


def matcher(words):
    """Whole words only, with a plural or possessive ending: "sati" no longer matches "satisfaction", nor "pain" "paint"."""
    alts = sorted({fold(w) for w in words}, key=len, reverse=True)
    pat = r'(?<![a-z0-9])(?:' + '|'.join(re.escape(a).replace(r'\-', '\x00').replace(r'\ ', r'[\s\-]+').replace('\x00', r'[\s\-]?') for a in alts) + r")(?:e?s|'s)?(?![a-z0-9])"
    return re.compile(pat)


EX = re.compile('|'.join(EXCLUDE))


def kept(text_f, m):
    """False when the match sits inside one of the excluded names or titles."""
    return not EX.search(text_f[max(0, m.start() - 30):m.end() + 30])


def snippet(text, a, b, before=120, after=160):
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


for v in tr:
    v['f'] = fold(html.unescape(v['text']))
    v['t'] = html.unescape(v['text'])
ama_title = {q['video']: q['title'] for q in tp['qna'] if q.get('video')}
out = []
for slug, title, lead, words, stages, bterms in TOPICS:
    rx = matcher(words)
    rec = {'slug': slug, 'title': title, 'lead': lead, 'words': words, 'stages': stages, 'videos': [], 'ama': {}, 'writings': [], 'audio': [], 'book': None}
    for v in tr:
        moments = []
        for m in (m for m in rx.finditer(v['f']) if kept(v['f'], m)):
            t = time_at(v, m.start())
            if moments and t - moments[-1][0] < 25:
                moments[-1][2] += 1
                continue
            moments.append([t, snippet(v['t'], m.start(), m.end()), 1])
        if not moments:
            continue
        n = sum(x[2] for x in moments)
        r_ = {'id': v['id'], 'title': v['title'], 'date': v['date'], 'n': n, 'moments': [[t, sn] for t, sn, _ in moments], 'w': [c for _, _, c in moments]}
        if v['id'] in ama_title:
            a = rec['ama'].setdefault(v['id'], {'id': v['id'], 'title': ama_title[v['id']], 'n': 0, 'questions': [], 'moments': []})
            a['n'] += n
            a['moments'] = r_['moments']
            a['w'] = r_['w']
        else:
            rec['videos'].append(r_)
    for q in tp['qna']:
        if not q.get('video'):
            continue
        for it in q['items']:
            ft = fold(it['text'])
            hits = [m for m in rx.finditer(ft) if kept(ft, m)]
            if not hits:
                continue
            a = rec['ama'].setdefault(q['video'], {'id': q['video'], 'title': q['title'], 'n': 0, 'questions': [], 'moments': []})
            a['n'] += len(hits)
            a['questions'].append([it['t'], it['url'], snippet(it['text'], hits[0].start(), hits[0].end(), 160, 200)])
    for d in tp['docs']:
        kind = 'audio' if d['type'] == 'Audio' else None if d['type'] == 'Video' else 'writings'
        if not kind:
            continue
        ft = fold(d['text'])
        hits = [m for m in rx.finditer(ft) if kept(ft, m)]
        if hits:
            rec[kind].append({'title': d['title'], 'url': d['url'], 'n': len(hits), 'snips': [snippet(d['text'], m.start(), m.end()) for m in hits[:8]]})
    # the book: the index term's pages (2015 first edition, final draft)
    pages, n_ = set(), 0
    for t in book['terms']:
        if any(fold(b) in [fold(x) for x in t['f']] for b in bterms):
            n_ += t['n']
            for l in t['loc']:
                p = book['pages'][l[0]][0]
                if p.isdigit():
                    pages.add(int(p))
    if pages:
        rec['book'] = {'n': n_, 'pages': [str(p) for p in sorted(pages)]}
    rec['ama'] = sorted(rec['ama'].values(), key=lambda x: -x['n'])
    for k in ('videos', 'writings', 'audio'):
        rec[k].sort(key=lambda x: -x['n'])
    # where to start (provisional, for the teachers to choose): a talk whose title names the topic and that mentions it
    # at least five times, the most mentions first; otherwise the video or AMA recording with the most mentions (every
    # one counted) within any ten minutes. It starts ten seconds before the first of them.
    titled = [c for c in rec['videos'] if c['n'] >= 5 and rx.search(fold(c['title']))]
    best = None
    for c in (titled or rec['videos'] + rec['ama']):
        ts = [m[0] for m in c['moments']]
        ws = c.get('w') or [1] * len(ts)
        for t in ts:
            score = sum(w for x, w in zip(ts, ws) if t <= x < t + 600)
            key = (c['n'] if titled else score, c in rec['videos'], score)
            if not best or key > best[0]:
                best = (key, c, t if not titled else ts[0])
    if best:
        _, c, t = best
        rec['pin'] = {'id': c['id'], 'title': c['title'], 'start': max(0, t - 10), 'titled': bool(titled)}
    rec['total'] = sum(x['n'] for k in ('videos', 'ama', 'writings', 'audio') for x in rec[k])
    out.append(rec)

(D / 'topic_pages.json').write_text(json.dumps({'topics': out}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
for r in out:
    print(f"{r['slug']:24} total {r['total']:5}  videos {len(r['videos']):3}  ama {len(r['ama']):3}  writings {len(r['writings']):3}  audio {len(r['audio']):3}  book {r['book']['n'] if r['book'] else '-'}")
