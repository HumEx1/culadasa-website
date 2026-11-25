"""Turn Alex's Culadasa Q&A Index into data for the Q&A archive page.

Usage:  python3 tools/build_qna_index.py source/qna-index-2026-11-25/culadasa_qna_index.html > redesign/data/qna_index.json

The source is a saved, unedited copy of https://transcendentmind.github.io/html/culadasa_qna_index.html
(D, 25 Nov 2026: "make this match the website"). Nothing is rewritten: questions, keywords and quotes are
Alex's words; only the markup is read. Italics (<i>, <em>) are kept; every other tag is dropped.
"""
import re, sys, json, html as htmlmod
from bs4 import BeautifulSoup, NavigableString

src = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
soup = BeautifulSoup(src, 'html.parser')

def inline(el, links=False):
    """Text of an element with only italics (and, for the introduction, links) kept, as safe HTML."""
    out = []
    for c in el.children:
        if isinstance(c, NavigableString):
            out.append(htmlmod.escape(str(c), quote=False))
        elif c.name in ('i', 'em'):
            out.append('<i>' + inline(c, links) + '</i>')
        elif c.name == 'br':
            out.append(' ')
        elif links and c.name == 'a' and c.get('href', '').startswith(('http://', 'https://')):
            out.append(f'<a href="{htmlmod.escape(c["href"])}">' + inline(c, links) + '</a>')
        else:
            out.append(inline(c, links))
    return re.sub(r'\s+', ' ', ''.join(out)).strip()

def yt(url):
    m = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', url or '')
    return m.group(1) if m else None

body = soup.body
h2s = body.find_all('h2')
first = h2s[0]
# Alex's introduction: everything before the first session
intro = []
for el in first.find_all_previous(['p', 'h1', 'h3', 'h4']):
    if el.name == 'h1':
        break
    intro.append(el)
intro.reverse()
intro_out = []
for el in intro:
    links = [(a.get_text(' ', strip=True), a['href']) for a in el.find_all('a', href=True)]
    intro_out.append({'kind': 'heading' if el.name != 'p' else 'p', 'html': inline(el, links=True), 'links': links})

sessions = []
for h2 in h2s:
    a = h2.find('a', href=True)
    s = {'title': re.sub(r'\s+', ' ', h2.get_text(' ', strip=True)), 'anchor': h2.get('id', ''), 'url': a['href'] if a else '',
         'video': yt(a['href']) if a else None, 'questions': []}
    q = None
    for el in h2.find_next_siblings():
        if el.name == 'h2':
            break
        if el.name == 'h3':
            qa = el.find('a', href=True)
            q = {'time': el.get_text(' ', strip=True), 'url': qa['href'] if qa else '', 'question': [], 'keywords': [], 'quotes': []}
            s['questions'].append(q)
            continue
        if q is None:
            continue
        if el.name == 'blockquote':
            ps = el.find_all('p')
            stamp = None
            text = []
            for p in ps:
                la = p.find('a', href=True)
                if la and p.get_text(' ', strip=True) == la.get_text(' ', strip=True) and re.match(r'^\d', la.get_text(strip=True)):
                    stamp = (la.get_text(' ', strip=True), la['href'])
                else:
                    text.append(inline(p))
            q['quotes'].append({'text': text, 'time': stamp[0] if stamp else '', 'url': stamp[1] if stamp else ''})
            continue
        if el.name == 'p':
            t = el.get_text(' ', strip=True)
            if t.startswith('Keywords:'):
                for k in el.find_all('span', class_='keyword'):
                    parent_a = k.find_parent('a', href=True)
                    inner_a = k.find('a', href=True)
                    link = (parent_a or inner_a)
                    q['keywords'].append({'text': re.sub(r'\s+', ' ', k.get_text(' ', strip=True)), 'url': link['href'] if link else ''})
            else:
                q['question'].append(inline(el))
        elif el.name in ('ul', 'ol'):
            q['question'].append(' '.join('• ' + inline(li) for li in el.find_all('li')))
    sessions.append(s)

# Corrections (D, 25 Nov 2026): plain misspellings in the questions, keywords and quotes (tools/spelling.py), and one
# link in Alex's introduction that misses GitHub's /blob/master/ path (the file itself is named "contibuting" in his repository).
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from spelling import fix_spelling
BROKEN = 'https://github.com/transcendentmind/transcendentmind.github.io/culadasa_qna_index_contibuting.md'
FIXED = 'https://github.com/transcendentmind/transcendentmind.github.io/blob/master/culadasa_qna_index_contibuting.md'
for p in intro_out:
    p['html'] = p['html'].replace(BROKEN, FIXED)
    p['links'] = [(t, FIXED if u == BROKEN else u) for t, u in p['links']]
for s in sessions:
    for q in s['questions']:
        q['question'] = [fix_spelling(x) for x in q['question']]
        for k in q['keywords']:
            k['text'] = fix_spelling(k['text'])
        for qt in q['quotes']:
            qt['text'] = [fix_spelling(x) for x in qt['text']]

out = {'source': 'https://transcendentmind.github.io/html/culadasa_qna_index.html', 'author': 'Alex',
       'intro': intro_out, 'sessions': sessions}
print(json.dumps(out, ensure_ascii=False, indent=1))
nq = sum(len(s['questions']) for s in sessions)
print(f'{len(sessions)} sessions, {nq} questions, {sum(len(q["keywords"]) for s in sessions for q in s["questions"])} keywords, '
      f'{sum(len(q["quotes"]) for s in sessions for q in s["questions"])} quotes', file=sys.stderr)
