#!/usr/bin/env python3
r"""Build redesign/data/topics.json: the searchable text behind the Topics page.

Sources (all real Culadasa material):
  * the 21 distinct PDF handouts in site/wp-content/uploads/2021/09/
    (the two identical "What the Buddha Thought" slide files count once);
  * the five essays and the About page text from the WordPress export;
  * the Culadasa Q&A Index by Alex (transcendentmind.github.io): every question
    asked in the 61 Patreon Q&A sessions, Oct 2017 to May 2021, with keywords,
    quotes and links to the exact moment in each YouTube video;
  (interview transcripts are not indexed: they belong to the sites that made them;
   the Conversations page links to them instead)
  * the titles of every video on his YouTube channel that the old site showed.

Search rule (Darin, 24 Nov 2026): rank purely by how many times the searched
word appears, no other rules.  The Topics page counts matches of the word and
of words that start with it (so "compassion" also counts "compassionate").
The word cloud is the most frequent words across everything, after removing
common English words (the list is below and in the decisions log).

Usage:
  python3 tools/build_topics.py <qna-index.md> <interviews-dir>
"""
import json, re, sys, subprocess, pathlib, html, collections, unicodedata
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
UP = ROOT / 'site' / 'wp-content' / 'uploads' / '2021' / '09'
OUT = ROOT / 'redesign' / 'data' / 'topics.json'

PDF_TITLES = {  # titles exactly as the old Writings page lists them
    'reading-list-20130813-1.pdf': 'Recommended Book List',
    'beginning-meditation-handout.pdf': 'Beginning Meditation Handout',
    'LightOnMeditationHandout.pdf': 'Meditation Manual for Tranquility and Insight',
    'preparation-for-practice.pdf': 'Preparation for Practice',
    'OFFERING_THE_MANDALA.pdf': 'Offering the Mandala',
    'Satipatthana-Retreat-Handout-Culadasa.pdf': 'Commentary on the Satipaṭṭhāna Sutta',
    'jhanas-and-mindfulness-handout.pdf': 'The Jhānas – The Original Practice of Mindfulness and Insight',
    'instructions-for-entering-jhana-leigh-brasington.pdf': 'Instructions for Entering Jhāna by Leigh Brasington',
    'Cape-Ann-Retreat-for-Peace-Handout-.pdf': 'An Introduction to the Practice of the Ten Stages of Samatha',
    'Magic-of-Mindfulness-Handout.pdf': 'The Magic of Mindfulness – Seeing Things as They Really Are',
    'Awakening-in-Daily-Life-Handout.pdf': 'The Path to Awakening in Daily Life',
    'What-Is-Enlightenment-Handout.pdf': 'What Is Enlightenment and Why Should I Care?',
    'Meditation-and-Insight-I.pdf': 'Meditation and Insight I',
    'Meditation-and-Insight-II.pdf': 'Meditation and Insight II',
    'Meditation-and-Insight-III.pdf': 'Meditation and Insight III',
    'Insight_Slides-October2012.pdf': 'Meditation and Insight – Slides',
    '20130322-what-the-buddha-thought-handout.pdf': 'Introduction to What the Buddha Thought',
    '20130322-what-the-buddha-thought-slides.pdf': 'Introduction to What the Buddha Thought – Slides',
    'BuddhadharmaWestPartI.pdf': 'When Buddhadharma Comes to the West – Part I: Future History in the Making',
    'BuddhadharmaWestPartsIIandIII.pdf': 'When Buddhadharma Comes to the West – Part II & III: What the Buddha Taught & Wisdom and Virtue',
    'Meditation-and-Joy-Handout.pdf': 'Joy & Meditation – More Than Just a Happy Feeling',
}
ESSAYS = {  # export slug -> title as listed on the Writings page
    'meditation-manual-introduction': 'Introduction to the Meditation Manual',
    'mindful-awareness-vs-dullness': 'Mindful Awareness vs Dullness',
    'amount-of-concentration-needed-for-awakening': 'Amount of Concentration Needed for Awakening',
    'daily-life-practice': 'How to Maintain Practice in One’s Daily Life',
    'cultivating-mindfulness-in-daily-life': 'Cultivating Mindfulness in Daily Life',
}
INTERVIEWS_OFF = [
    ('batgap-394.txt', 'Culadasa:', 'Buddha at the Gas Pump #394 — interview with Rick Archer (2017)',
     'https://batgap.com/culadasa-john-yates-interview-transcript/', 'Transcript: batgap.com'),
    ('deconstructing-yourself-dy022.txt', 'John Yates:', 'Deconstructing Yourself DY 022 — Culadasa on Stream Entry, with Michael Taft (2018)',
     'https://deconstructingyourself.com/culadasa-stream-entry.html', 'Transcript: deconstructingyourself.com'),
]
STOP = set("""a about above after again against all almost also although always am among an and any are aren't as at be
because been before being below between both but by can can't cannot could couldn't did didn't do does doesn't doing don't
down during each either else enough even ever every few for from further get gets getting go goes going gone got had hadn't
has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's however i i'd i'll
i'm i've if in into is isn't it it's its itself just let's like made make makes many may me might more most much must mustn't
my myself need never no nor not now of off often on once one only or other others otherwise ought our ours ourselves out over
own per perhaps put quite rather really said same say says see seem seems shall shan't she she'd she'll she's should shouldn't
since so some something sometimes still such than that that's the their theirs them themselves then there there's therefore
these they they'd they'll they're they've thing things this those though through thus to too toward towards under until up
upon us use used using very via want was wasn't way we we'd we'll we're we've well were weren't what what's when when's where
where's whether which while who who's whom whose why why's will with within without won't would wouldn't yes yet you you'd
you'll you're you've your yours yourself yourselves also actually kind sort lot lots going gonna yeah okay ok right know think
mean said says say get got two three first second third new us one's another back come comes came take takes taken give gives
well able around rather simply become becomes becoming within part parts point time times much many little long whole fact
example called call different good great every each next last page pp et al vol
keywords culadasa upasaka yates""".split())  # last line: the index's own label and the author's name, which every PDF header repeats

WORD = re.compile(r"[a-zāīūṛṝḷṃṅñṭḍṇśṣḥ][a-zāīūṛṝḷṃṅñṭḍṇśṣḥ'’-]*", re.I)


def clean(t):
    t = t.replace('­', '').replace('\x0c', '\n')
    t = re.sub(r'-\n(?=[a-z])', '', t)          # re-join words hyphenated across lines
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()


def pdf_text(p):
    return clean(subprocess.run(['pdftotext', '-enc', 'UTF-8', str(p), '-'], capture_output=True, text=True).stdout)


def html_text(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.S)
    s = re.sub(r'</p>|<br\s*/?>|</h\d>|</li>', '\n', s)
    s = re.sub(r'\[/?embedyt\][^\[]*', ' ', s)
    return clean(html.unescape(re.sub(r'<[^>]+>', ' ', s)))


def md_inline(s):
    s = re.sub(r'\[`?([^\]`]+)`?\]\([^)]*\)', r'\1', s)
    s = s.replace('`', '').replace('_', '').replace('*', '')
    return re.sub(r'\s+', ' ', s).strip()


def parse_qna(md):
    sessions, cur, item = [], None, None
    for line in md.splitlines():
        m = re.match(r'^## \[([^\]]+)\]\((https://www\.youtube\.com/watch\?v=([\w-]{11}))\)', line)
        if m:
            cur = {'title': f'Culadasa {m.group(1)} Patreon Q&A', 'month': m.group(1), 'video': m.group(3),
                   'url': m.group(2), 'items': []}
            sessions.append(cur); item = None; continue
        if cur is None:
            continue
        m = re.match(r'^### (\d\d):(\d\d):(\d\d)', line)
        if m:
            h, mi, se = map(int, m.groups())
            secs = h * 3600 + mi * 60 + se
            item = {'t': f'{h}:{mi:02d}:{se:02d}' if h else f'{mi}:{se:02d}',
                    'url': f'https://www.youtube.com/watch?v={cur["video"]}&t={secs}s', 'text': ''}
            cur['items'].append(item); continue
        if item is not None and line.strip() and not line.startswith('<!--'):
            item['text'] += ' ' + md_inline(line.lstrip('> ')).replace('Keywords:', 'Keywords —')
    for s in sessions:
        for it in s['items']:
            it['text'] = it['text'].strip()
        s['items'] = [i for i in s['items'] if i['text']]
    return sessions


def main(qna_md, interviews_dir):
    docs = []
    for fname, title in PDF_TITLES.items():
        docs.append({'id': 'pdf-' + fname[:-4], 'type': 'Handout', 'title': title,
                     'url': f'../wp-content/uploads/2021/09/{fname}', 'text': pdf_text(UP / fname)})
    ch = ET.parse(next((ROOT / 'source' / 'wordpress-export').glob('*.xml'))).getroot().find('channel')
    ns = {'wp': 'http://wordpress.org/export/1.2/', 'content': 'http://purl.org/rss/1.0/modules/content/'}
    for it in ch.findall('item'):
        slug = it.findtext('wp:post_name', namespaces=ns)
        body = it.findtext('content:encoded', namespaces=ns) or ''
        if slug in ESSAYS:
            docs.append({'id': 'essay-' + slug, 'type': 'Essay', 'title': ESSAYS[slug], 'url': f'../{slug}/', 'text': html_text(body)})
        if slug == 'about':
            docs.append({'id': 'about', 'type': 'About', 'title': 'About Culadasa: biography and lineage', 'url': '../about/', 'text': html_text(body)})
    for fname, marker, title, url, credit in []:
        t = (pathlib.Path(interviews_dir) / fname).read_text()
        turns = re.split(r'\n\s*\n|(?=\b(?:Rick|Michael Taft|Culadasa|John Yates):)', t)
        own = [x.split(':', 1)[1].strip() for x in turns if x.strip().startswith(marker)]
        docs.append({'id': 'interview-' + fname[:-4], 'type': 'Interview', 'title': title, 'url': url, 'credit': credit, 'text': '\n\n'.join(own)})
    vids = json.loads((ROOT / 'redesign' / 'data' / 'videos.json').read_text())
    qna = parse_qna(pathlib.Path(qna_md).read_text())
    qna_ids = {s['video'] for s in qna}
    for v in vids:
        if v['id'] not in qna_ids:
            docs.append({'id': 'video-' + v['id'], 'type': 'Video', 'title': v['title'],
                         'url': f'https://www.youtube.com/watch?v={v["id"]}', 'text': v['title']})
    # word cloud: most frequent words across everything
    counts = collections.Counter()
    for d in docs:
        counts.update(w.lower().replace('’', "'").strip("'-") for w in WORD.findall(d['text']))
    for s in qna:
        for i in s['items']:
            counts.update(w.lower().replace('’', "'").strip("'-") for w in WORD.findall(i['text']))
    top = [w for w, c in counts.most_common(2000) if len(w) > 3 and w not in STOP and not w.isdigit()][:90]
    # show each word with the count a search for it returns (same rule as the Topics page: word start, accents folded)
    def fold(t):
        return unicodedata.normalize('NFD', t.replace('’', "'")).encode('ascii', 'ignore').decode().lower() if False else ''.join(
            (unicodedata.normalize('NFD', ch)[0] if ch not in '’‘' else "'") for ch in t).lower()
    texts = [fold(d['text']) for d in docs] + [fold(i['text']) for s in qna for i in s['items']]
    cloud = []
    for w in top:
        pat = re.compile(r'(?<![a-z0-9\u00c0-\u024f\u1e00-\u1eff])' + re.escape(fold(w)) + r'[a-z0-9\u00c0-\u024f\u1e00-\u1eff]*')
        cloud.append((w, sum(len(pat.findall(t)) for t in texts)))
    cloud.sort(key=lambda x: -x[1])
    for d in docs:  # account emails printed in his handouts are not repeated in the search index
        d['text'] = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}', '[email]', d['text'])
    data = {'built': __import__('datetime').date.today().isoformat(),
            'credit': {'qna': {'name': 'Culadasa Q&A Index by Alex', 'url': 'https://transcendentmind.github.io/html/culadasa_qna_index.html'}},
            'docs': docs, 'qna': qna, 'cloud': cloud}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    words = sum(len(d['text'].split()) for d in docs) + sum(len(i['text'].split()) for s in qna for i in s['items'])
    print(f'{len(docs)} documents, {len(qna)} Q&A sessions, {sum(len(s["items"]) for s in qna)} questions, '
          f'{words} words, {OUT.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main(*sys.argv[1:3])
