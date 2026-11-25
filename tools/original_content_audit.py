"""Where did everything on the original site go in a redesign?

Usage:  python3 tools/original_content_audit.py [redesign-2] > docs/ORIGINAL_CONTENT_CHECK.md

For each of the original pages (the mirror in site/):
- How a visitor reaches it in the redesign: main menu, Library menu, footer only,
  only from inside other pages, redirect, or not at all (shortest click path from Home).
- Every piece of its main text (headings, paragraphs, list items, captions, image
  descriptions) that does NOT appear word for word anywhere in the redesign.
- Every link, PDF, image, video playlist and audio playlist it had that the redesign
  does not link to or show.
- Original text that the redesign does have but only inside collapsed sections
  (open/close boxes) or only through the search box.
Matching ignores case, quote styles, dashes and spacing, as in tools/new_text_inventory.py.
"""
import re, sys, pathlib, difflib, html as htmlmod, urllib.parse
from collections import deque
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
RED = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'redesign-2')

def norm(s):
    s = htmlmod.unescape(s or '')
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = re.sub('[–—‒]', '-', s).replace(' ', ' ').replace('…', '...').replace('×', 'x')
    s = re.sub(r'\s+', ' ', s).strip().lower()
    s = re.sub(r'^[\s"\'\-←→]+|[\s"\'\-←→]+$', '', s)
    return s.strip(' .,:;')

ORIG_PAGES = ['', 'online-meetings/', 'writings/', 'audio/', 'videos/', 'teachers/', 'testimonials/',
              'student-testimonials/', 'book-reviews/', 'meditation-manual-introduction/', 'mindful-awareness-vs-dullness/',
              'amount-of-concentration-needed-for-awakening/', 'daily-life-practice/', 'cultivating-mindfulness-in-daily-life/']
ORIG_NAME = {'': 'About (the old home page)', 'online-meetings/': 'Online Meetings', 'writings/': 'Teachings › Writings',
             'audio/': 'Teachings › Audio', 'videos/': 'Teachings › Videos', 'teachers/': 'Teachings › Teachers',
             'testimonials/': 'Teachings › Testimonials', 'student-testimonials/': 'Teachings › Student testimonials',
             'book-reviews/': 'Teachings › Book reviews', 'meditation-manual-introduction/': 'Essay: Introduction to the Meditation Manual',
             'mindful-awareness-vs-dullness/': 'Essay: Mindful Awareness vs Dullness',
             'amount-of-concentration-needed-for-awakening/': 'Essay: Amount of Concentration Needed for Awakening',
             'daily-life-practice/': 'Essay: How to Maintain Practice in Daily Life',
             'cultivating-mindfulness-in-daily-life/': 'Essay: Cultivating Mindfulness in Daily Life'}

# ---------------------------------------------------------------- the redesign: text, links, structure
red_pages = {}
for f in sorted(RED.rglob('index.html')):
    rel = str(f.parent.relative_to(RED)).replace('.', '')
    rel = '' if rel == '' else rel + '/'
    red_pages[rel] = BeautifulSoup(f.read_text(), 'html.parser')

RED_TEXT, RED_VISIBLE, RED_HREFS, RED_IMGS = [], [], set(), []
for rel, soup in red_pages.items():
    for t in soup(['script', 'style', 'noscript']):
        t.decompose()
    RED_TEXT.append(soup.get_text(' '))
    vis = BeautifulSoup(str(soup), 'html.parser')
    for d in vis.find_all('details'):
        summ = d.find('summary')
        keep = summ.get_text(' ') if summ else ''
        d.replace_with(keep)
    RED_VISIBLE.append(vis.get_text(' '))
    for img in soup.find_all('img'):
        RED_TEXT.append(img.get('alt', ''))
        RED_IMGS.append(img.get('src', ''))
    for a in soup.find_all(['a', 'iframe', 'div']):
        for attr in ('href', 'src', 'data-id'):
            if a.get(attr):
                RED_HREFS.add(a.get(attr))
# data files the pages read (search index, teacher data) count as present but "search only"
DATA_TEXT = ''
for j in (RED / 'data').glob('*.json'):
    DATA_TEXT += ' ' + j.read_text(errors='ignore')
RED_ALL = ' ' + norm(' \n '.join(RED_TEXT)) + ' '
RED_VIS = ' ' + norm(' \n '.join(RED_VISIBLE)) + ' '
RED_DATA = ' ' + norm(DATA_TEXT.encode().decode('unicode_escape', errors='ignore') if '\\u' in DATA_TEXT else DATA_TEXT) + ' '
HREFS_JOINED = ' '.join(RED_HREFS) + ' ' + DATA_TEXT

# Things removed or changed on purpose, so the reader knows why (decisions in Culadasa_Website/DECISIONS_FOR_REVIEW.md)
KNOWN = [
    (r'^powered by', 'Removed on purpose: left over from hidden spam adverts on the old WordPress pages.'),
    (r'develping', 'Corrected on purpose: the original typo "develping" is spelled "developing" in the redesign.'),
    (r'^cultivating-mindfulness-in-daily-life$', 'Removed on purpose: a stray web-address slug shown as a heading on the original page.'),
]
RENAMED_IMAGES = {'culadasa-photo-from-book-cover': 'culadasa-portrait.jpg', 'screen-shot-2014-10-06': 'culadasa-robes.jpg'}
GALLERY_UI = ('playhover', 'gallery-page-loader')
OLD_MENU_NOW = {
    'culadasa': 'the CULADASA name at the top of every page, which links to Home',
    'about': 'split in two: Home (portrait, his wishes, the way in) and the Lineage tab (lineage, wishes, obituary)',
    'online meetings': 'Library › Culadasa AMA sessions (same address, /online-meetings/)',
    'teachings': 'renamed Library; it holds Writings, Audio, Videos and the Q&A archive',
    'student testimonials': 'merged into Testimonials (old address forwards there)',
    'book reviews': 'merged into The Book page, section "What teachers and authors say" (old address forwards there)',
}

def known_reason(n):
    for pat, why in KNOWN:
        if re.search(pat, n):
            return why
    return ''

def near_match(n, corpus):
    """Same text with small edits (punctuation, a word or two)?  Returns the similarity, 0-1."""
    words = n.split()
    if len(words) < 8:
        return 0
    for k in range(0, min(len(words) - 6, 40), 3):
        probe = ' '.join(words[k:k + 6])
        i = corpus.find(probe)
        if i >= 0:
            start = max(0, i - len(' '.join(words[:k])) - 20)
            window = corpus[start:start + len(n) + 60]
            return difflib.SequenceMatcher(None, n, window).find_longest_match(0, len(n), 0, len(window)).size / len(n) if False else \
                   difflib.SequenceMatcher(None, n, window).ratio() * (len(window) + len(n)) / (2 * len(n))
    return 0

def found_in(n, corpus):
    if len(n.split()) <= 2:
        return re.search(r'(?<![a-z0-9])' + re.escape(n) + r'(?![a-z0-9])', corpus) is not None
    return n in corpus

# ---------------------------------------------------------------- how each redesign page is reached
def links_of(soup, region):
    out = []
    for a in soup.find_all('a', href=True):
        reg = 'page'
        for p in a.parents:
            if p.name == 'nav' and 'nav' in (p.get('class') or []):
                reg = 'menu'; break
            if p.name == 'footer' and p.get('class') and 'footer' in p.get('class'):
                reg = 'footer'; break
        if region and reg != region:
            continue
        out.append(a['href'])
    return out

def resolve(rel, href):
    if re.match(r'(https?:|mailto:|#|javascript:)', href):
        return None
    u = urllib.parse.urljoin('https://x/' + rel, href.split('#')[0].split('?')[0])
    path = urllib.parse.urlparse(u).path.lstrip('/')
    if path.endswith('index.html'):
        path = path[:-10]
    return path

home = red_pages['']
menu_targets = {resolve('', h) for h in links_of(home, 'menu')}
footer_targets = {resolve('', h) for h in links_of(home, 'footer')}
# shortest path from Home through any links
dist, prev = {'': 0}, {}
q = deque([''])
while q:
    cur = q.popleft()
    for h in links_of(red_pages[cur], None):
        t = resolve(cur, h)
        if t is not None and t in red_pages and t not in dist:
            dist[t] = dist[cur] + 1; prev[t] = cur; q.append(t)

def redirect_of(rel):
    soup = red_pages.get(rel)
    if soup is None:
        return None
    m = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if m:
        return resolve(rel, m['content'].split('url=')[-1])
    return None

def how_reached(rel):
    if rel not in red_pages:
        return 'NOT IN THE REDESIGN (address gives "page not found")'
    r = redirect_of(rel)
    if r is not None:
        return f'Address kept; it forwards to `/{r}` ({how_reached(r)})'
    label = None
    for a in home.select('nav.nav a'):
        if resolve('', a['href']) == rel:
            label = a.get_text(' ', strip=True)
            in_sub = a.find_parent(class_='sub') is not None
            return f'Main menu{" › Library" if in_sub else ""} › {label}'
    if rel == '':
        return 'Home page'
    if rel in footer_targets:
        return 'Footer link only (bottom of every page); not in the menu'
    if rel in dist:
        path = [rel]
        while path[-1] in prev:
            path.append(prev[path[-1]])
        names = ' › '.join('/' + p if p else 'Home' for p in reversed(path))
        return f'Not in the menu; reached only through links inside pages ({names})'
    return 'Exists but nothing links to it'

# ---------------------------------------------------------------- go through the original pages
out = []
out.append('# Original site content check: what is missing or hard to find in Redesign 2\n')
out.append(f'Every page, piece of text, link, file, image and playlist of the original culadasa.com (the mirror in `site/`), checked against `{RED.name}/`. '
           'Tick each item once it has been looked at and a decision made: keep as is, restore, or move somewhere easier to find.\n')
out.append('Made by `tools/original_content_audit.py`. Text counts as present when the same words appear anywhere in the redesign '
           '(ignoring case, quote marks, dashes and spacing). Line numbers refer to the files in `site/`.\n')

summary_rows, sections = [], []
for rel in ORIG_PAGES:
    f = SITE / rel / 'index.html'
    soup = BeautifulSoup(f.read_text(errors='ignore'), 'html.parser')
    main = soup.select_one('main') or soup
    for t in main(['script', 'style', 'noscript']):
        t.decompose()
    missing, hidden, searchonly, links_missing, media, edited = [], [], [], [], [], []
    seen = set()
    for el in main.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'figcaption', 'blockquote', 'td', 'a', 'span', 'div']):
        if el.name in ('a', 'span', 'div') and el.find(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'div', 'span', 'a']):
            continue
        if el.name in ('a', 'span', 'div') and el.find_parent(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'figcaption', 'blockquote']):
            continue
        txt = re.sub(r'\s+', ' ', el.get_text(' ')).strip()
        n = norm(txt)
        if not n or not re.search(r'[a-z]', n) or n in seen or n in ('prev', 'next'):
            continue
        seen.add(n)
        if found_in(n, RED_ALL):
            if not found_in(n, RED_VIS) and len(n) > 30:
                hidden.append((el.sourceline, txt))
            continue
        # a paragraph may have been split into smaller pieces: check its sentences
        sents = [s for s in re.split(r'(?<=[.!?])\s+', n) if len(s) > 25]
        if sents and all(found_in(s.strip(' .,:;'), RED_ALL) for s in sents):
            continue
        why = known_reason(n)
        sim = near_match(n, RED_ALL)
        if not why and sim >= 0.9:
            edited.append((el.sourceline, txt, sim))
            continue
        if found_in(n, RED_DATA) and not why:
            searchonly.append((el.sourceline, txt))
            continue
        missing.append((el.sourceline, el.name, txt, why))
    for a in main.find_all(['a', 'iframe'], href=True) + main.find_all('iframe', src=True):
        h = a.get('href') or a.get('src')
        if not h or h.startswith('#') or h.startswith('mailto:'):
            continue
        key = h
        m = re.search(r'(wp-content/uploads/[^"?#]+)', h)
        if m:
            key = m.group(1).split('/')[-1]
        m2 = re.search(r'playlists(?:%2F|/)(\d+)', h) or re.search(r'list=([\w-]+)', h) or re.search(r'embed/([\w-]{11})', h)
        if m2:
            key = m2.group(1)
        if key in HREFS_JOINED or urllib.parse.unquote(key) in HREFS_JOINED:
            continue
        if re.match(r'(\.\./)*(\w[\w-]*/)?$', h) or 'culadasa.com/' in h and not 'uploads' in h:
            continue   # links between the old pages themselves; their pages are covered above
        links_missing.append((a.sourceline, a.get_text(' ', strip=True) or a.get('title', '') or 'embedded player', h))
    for img in main.find_all('img'):
        src = img.get('src', '')
        name = src.split('/')[-1]
        if any(g in name for g in GALLERY_UI):
            continue
        ren = next((v for k, v in RENAMED_IMAGES.items() if name.lower().startswith(k)), None)
        if ren and any(ren in r for r in RED_IMGS):
            continue
        base = re.sub(r'-\d+x\d+(?=\.\w+$)', '', name).split('.')[0][:20].lower()
        if any(base and base in r.lower() for r in RED_IMGS):
            continue
        media.append((img.sourceline, img.get('alt', ''), name))
    sections.append((rel, missing, hidden, searchonly, links_missing, media, edited))
    summary_rows.append((rel, how_reached(rel), sum(1 for x in missing if not x[3]) + len(links_missing) + len(media), len(hidden) + len(searchonly), len(edited)))

out.append('\n## 1. Where each original page went\n')
out.append('| Original page (old menu) | In the redesign | Missing | Edited slightly | Hidden or search-only |\n|---|---|---|---|---|')
for rel, how, nmiss, nhid, ned in summary_rows:
    out.append(f'| `/{rel}` {ORIG_NAME[rel]} | {how} | {nmiss} | {ned} | {nhid} |')
out.append('\n"Missing" leaves out things removed on purpose (spam leftovers, a typo, a stray slug); those are still listed below with the reason.')

out.append('\n## 2. Item by item\n')
for rel, missing, hidden, searchonly, links_missing, media, edited in sections:
    out.append(f'\n### `/{rel}` {ORIG_NAME[rel]}\n')
    out.append(f'- [ ] **How to find it now:** {how_reached(rel)}')
    if not (missing or hidden or searchonly or links_missing or media or edited):
        out.append('- [ ] All of its text, links and media are in the redesign.')
    for line, tag, txt, why in missing:
        if why:
            out.append(f'- [ ] **Removed on purpose** (`site/{rel}index.html` line {line}): "{txt[:200]}". {why}')
        else:
            out.append(f'- [ ] **Text not in the redesign** (`site/{rel}index.html` line {line}): "{txt[:400]}{"…" if len(txt) > 400 else ""}"')
    for line, txt, sim in edited:
        out.append(f'- [ ] **In the redesign with small edits** (punctuation or a word or two; {sim:.0%} the same) (line {line}): "{txt[:220]}{"…" if len(txt) > 220 else ""}"')
    for line, txt in searchonly:
        out.append(f'- [ ] **Only findable through Topics search**, not shown on any page (line {line}): "{txt[:300]}{"…" if len(txt) > 300 else ""}"')
    for line, txt in hidden:
        out.append(f'- [ ] **Present but inside a collapsed section** (shown only when opened) (line {line}): "{txt[:200]}{"…" if len(txt) > 200 else ""}"')
    for line, label, h in links_missing:
        out.append(f'- [ ] **Link or embed not in the redesign** (line {line}): "{label[:120]}" → `{h[:160]}`')
    for line, alt, name in media:
        out.append(f'- [ ] **Image not shown in the redesign** (line {line}): `{name}`' + (f' ("{alt}")' if alt else ''))

# files under wp-content/uploads that no redesign page links to
out.append('\n## 3. Files from the original site that no redesign page links to\n')
out.append('They are still kept at their old addresses, so old links and bookmarks work.\n')
ORIG_VISIBLE_LINKS = ''
for g in SITE.rglob('*.html'):
    sp = BeautifulSoup(g.read_text(errors='ignore'), 'html.parser')
    for t in sp(['script']):
        t.decompose()
    ORIG_VISIBLE_LINKS += ' '.join((a.get('href') or '') + ' ' + (a.get('src') or '') for a in sp.find_all(['a', 'img', 'iframe']))
for f in sorted((SITE / 'wp-content/uploads/2021/09').iterdir()):
    ren = next((v for k, v in RENAMED_IMAGES.items() if f.name.lower().startswith(k)), None)
    if ren and any(ren in r for r in RED_IMGS):
        continue
    if f.name not in HREFS_JOINED and not any(f.stem[:20].lower() in r.lower() for r in RED_IMGS):
        note = '' if f.name in ORIG_VISIBLE_LINKS else ' (no page on the original site linked to it either)'
        if f.name == 'retrr.jpg':
            note = ' (on the original it was only the logo in hidden search-engine data, captioned "Inspiration Station")'
        out.append(f'- [ ] `wp-content/uploads/2021/09/{f.name}`{note}')

# the old menu, header and footer
out.append('\n## 4. The original menu, header and footer\n')
oh = BeautifulSoup((SITE / 'index.html').read_text(errors='ignore'), 'html.parser')
menu = []
for a in oh.select('header a'):
    t = a.get_text(' ', strip=True)
    if t and t not in menu:
        menu.append(t)
for t in menu:
    n = norm(t)
    inred = any(norm(a.get_text(' ', strip=True)) == n for a in home.select('nav.nav a, nav.nav button'))
    infoot = any(norm(a.get_text(' ', strip=True)) == n for a in home.select('footer a'))
    state = 'in the new menu' if inred else ('footer link only' if infoot else 'not in the new menu or footer')
    if n in OLD_MENU_NOW:
        state = 'now ' + OLD_MENU_NOW[n]
    elif n == 'testimonials':
        state = 'footer link only; in the old menu it sat under Teachings next to Book reviews'
    out.append(f'- [ ] Old menu item **{t}**: {state}')
foot = oh.select_one('footer')
if foot:
    out.append(f'- [ ] Old footer text "{re.sub(chr(10), " ", foot.get_text(" ", strip=True))}": replaced by the licence line and social links')
print('\n'.join(out))
