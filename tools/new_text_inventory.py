"""List every piece of text in a redesign that is not on the original site.

Usage:  python3 tools/new_text_inventory.py [redesign-2] > docs/NEW_TEXT_CHECKLIST.md

How it decides (D asked for every added word, 24 Nov 2026):
- "Original" text = all text on the mirrored live site in site/ (every HTML page, including
  the video-gallery fragments): visible text, <title>, meta descriptions, image alt text.
- Each piece of text in the redesign (a heading, paragraph, list item, caption, button,
  label, page title, meta description, alt text, placeholder) is normalised (lower case,
  straight quotes, dashes and spaces made uniform) and counts as original only if it appears
  word for word somewhere in the original text (whole words only). Short pieces of three
  words or fewer (menu labels, buttons, headings) count as original only if the original
  site used exactly that text as a whole heading, link, button or other element of its own,
  so a new label like "Learn" is listed even though the word appears in old prose.
  Anything else, including original text that was edited, is listed.
- The same text on several pages is listed once, with every page it appears on.
- Text written by the page scripts (search, map) is listed from the script files.
"""
import re, sys, json, pathlib, html as htmlmod
from collections import OrderedDict
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
RED = ROOT / (sys.argv[1] if len(sys.argv) > 1 else 'redesign-2')

def norm(s):
    s = htmlmod.unescape(s)
    s = s.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    s = re.sub('[\u2013\u2014\u2012]', '-', s).replace('\u00a0', ' ').replace('\u2026', '...')
    s = re.sub(r'\s+', ' ', s).strip().lower()
    s = re.sub(r'^[\s"\'\-\u2190\u2192]+|[\s"\'\-\u2190\u2192]+$', '', s)   # quote marks, dashes and arrows added around original words
    return s.strip(' .,:;')

# ---- the original corpus
orig = []
ORIG_ELEMENTS = set()
for f in sorted(SITE.rglob('*.html')):
    soup = BeautifulSoup(f.read_text(errors='ignore'), 'html.parser')
    for t in soup(['script', 'style', 'noscript']):
        t.decompose()
    orig.append(soup.get_text(' '))
    for el in soup.find_all(True):
        t = norm(el.get_text(' '))
        if t and len(t) < 200:
            ORIG_ELEMENTS.add(t)
    if soup.title:
        ORIG_ELEMENTS.add(norm(soup.title.get_text()))
    for img in soup.find_all('img'):
        orig.append(img.get('alt', ''))
    for m in soup.find_all('meta'):
        orig.append(m.get('content', '') or '')
ORIG = ' ' + norm(' \n '.join(orig)) + ' '

def is_original(t):
    n = norm(t)
    if not n:
        return True
    if len(n.split()) <= 3:
        return n in ORIG_ELEMENTS
    return re.search(r'(?<![a-z0-9])' + re.escape(n) + r'(?![a-z0-9])', ORIG) is not None

BLOCK = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'figcaption', 'summary', 'blockquote', 'dt', 'dd',
         'td', 'th', 'label', 'button', 'legend', 'caption', 'footer', 'small', 'em', 'strong', 'span', 'a', 'div', 'header'}
LEAFY = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'figcaption', 'summary', 'blockquote', 'dt', 'dd',
         'td', 'th', 'label', 'button', 'legend', 'caption'}

def page_name(rel):
    return '/' + rel if rel else '/ (Home)'

found = OrderedDict()   # norm text -> dict(text, kind, places[])

def add(text, kind, rel, line, heading, region):
    text = re.sub(r'\s+', ' ', text).strip()
    if not text or not re.search(r'[A-Za-z]', text) or is_original(text):
        return
    key = norm(text)
    item = found.setdefault(key, {'text': text, 'kind': kind, 'places': []})
    item['places'].append((rel, line, heading, region))

def region_of(el):
    for p in el.parents:
        if p.name == 'nav' or (p.get('class') and 'preview-bar' in p.get('class')):
            return 'menu'
        if p.name == 'footer' and p.get('class') and 'footer' in p.get('class'):
            return 'footer'
        if p.name == 'section' and p.get('class') and 'signup' in p.get('class'):
            return 'newsletter box'
        if p.name == 'header' and p.get('class') and 'masthead' in p.get('class'):
            return 'header'
    return 'page'

pages = sorted(RED.rglob('index.html'), key=lambda f: (f.parent != RED, str(f)))
for f in pages:
    rel = str(f.parent.relative_to(RED)).replace('.', '')
    rel = '' if rel == '' else rel + '/'
    soup = BeautifulSoup(f.read_text(), 'html.parser')
    if soup.title:
        add(soup.title.get_text(), 'Page title (browser tab)', rel, soup.title.sourceline, '', 'head')
    for m in soup.find_all('meta'):
        if m.get('name') == 'description':
            add(m.get('content', ''), 'Search description (hidden)', rel, m.sourceline, '', 'head')
    for t in soup(['script', 'style', 'noscript']):
        t.decompose()
    # on the stage pages, the quoted passages are his own words from transcripts, AMA questions, writings and recording
    # notes (sources already on the site), so only the page's own wording is listed (D, 25 Nov 2026)
    if 'videos' in f.parts and f.parent.name != 'videos':   # a video page: the transcript and Alex's questions are quoted, not new
        for t in soup.select('.transcript, #questions .qlist'):
            t.decompose()
    if 'ten-stages' in f.parts or ('learn' in f.parts and 'topics' in f.parts):
        for t in soup.select('.rr-body p.tline, .rr-body .qsnip, .rr-body > p:not(.rr-open):not(.small)'):
            t.decompose()
    heading = ''
    for el in soup.body.descendants:
        if not getattr(el, 'name', None):
            continue
        if el.name in ('h1', 'h2', 'h3') and region_of(el) == 'page':
            heading = re.sub(r'\s+', ' ', el.get_text(' ')).strip()
        if el.name == 'img' and el.get('alt'):
            add(el['alt'], 'Image description (alt text)', rel, el.sourceline, heading, region_of(el))
        if el.name == 'input' and el.get('placeholder'):
            add(el['placeholder'], 'Search box hint', rel, el.sourceline, heading, region_of(el))
        if el.get('aria-label') and el.name in ('a', 'button', 'nav', 'section', 'div'):
            add(el['aria-label'], 'Screen-reader label (hidden)', rel, el.sourceline, heading, region_of(el))
        if el.name in LEAFY or (el.name in BLOCK and not el.find(list(BLOCK))):
            if el.find(list(LEAFY)) and el.name in LEAFY:
                # a block that contains other blocks: take only its own direct text
                own = ' '.join(s for s in el.find_all(string=True, recursive=False))
                add(own, el.name, rel, el.sourceline, heading, region_of(el))
                continue
            if el.name not in LEAFY and el.find_parent(list(LEAFY)):
                continue
            add(el.get_text(' '), el.name, rel, el.sourceline, heading, region_of(el))

# ---- text written by the page scripts
SCRIPTS = []
for js in ['topics.js', 'teachers.js', 'site.js']:
    p = RED / 'assets' / js
    if not p.exists():
        continue
    for i, line in enumerate(p.read_text().splitlines(), 1):
        if line.strip().startswith('//') or line.strip().startswith('/*') or line.strip().startswith('*'):
            continue
        for lab in re.findall(r"\['[a-z]+', '([^']+)'\]", line):      # filter-button labels
            if not is_original(lab):
                SCRIPTS.append((js, i, lab))
        for s in re.findall(r"'((?:[^'\\]|\\.)*)'", line):
            s2 = re.sub(r'<[^>]+>', ' ', s.replace('\\u2026', '…')).strip()
            if s2.startswith(('.', '#', '[')) or re.search(r'[{}();=]', s2) or not re.search(r'[A-Za-z]{3,}', s2):
                continue
            if ' ' not in s2 and re.search(r'[-/_.]', s2):
                continue
            if re.search(r'[A-Za-z]{2,}\s+[A-Za-z]', s2) and not is_original(s2):
                SCRIPTS.append((js, i, s2))

KIND = {'h1': 'Page heading', 'h2': 'Section heading', 'h3': 'Sub-heading', 'h4': 'Sub-heading', 'p': 'Paragraph',
        'li': 'List item', 'figcaption': 'Photo caption', 'summary': 'Expandable heading', 'blockquote': 'Quote',
        'button': 'Button', 'label': 'Form label', 'a': 'Link text', 'span': 'Short label', 'small': 'Small print',
        'em': 'Italic text', 'strong': 'Bold text', 'div': 'Text block', 'footer': 'Footer text', 'dt': 'Term', 'dd': 'Definition',
        'header': 'Text block'}

TAB = [('', 'Home'), ('start-here/', 'Start here'), ('learn/', 'Learn'), ('topics/', 'Topics'),
       ('writings/', 'Library › Writings'), ('audio/', 'Library › Audio'), ('videos/', 'Library › Videos'),
       ('online-meetings/', 'Library › AMA videos (redirect)'), ('meditation-manual-introduction/', 'Library › Writings › essay'),
       ('mindful-awareness-vs-dullness/', 'Library › Writings › essay'), ('amount-of-concentration-needed-for-awakening/', 'Library › Writings › essay'),
       ('daily-life-practice/', 'Library › Writings › essay'), ('cultivating-mindfulness-in-daily-life/', 'Library › Writings › essay'),
       ('the-book/', 'The Book'), ('book-reviews/', 'The Book (old address, redirects)'), ('teachers/', 'Teachers'),
       ('conversations/', 'Conversations'), ('lineage/', 'Lineage'), ('about/', 'Lineage (old About address, redirects)'),
       ('testimonials/', 'Footer › Testimonials'), ('student-testimonials/', 'Footer › Testimonials (old address, redirects)')]
TABNAME = dict(TAB)

def tab_of(rel):
    if rel.startswith('teachers/') and rel != 'teachers/':
        return 'Teachers › profile'
    return TABNAME.get(rel, rel)

def where(places):
    rel, line, heading, region = places[0]
    loc = f"{tab_of(rel)} (`{RED.name}/{rel}index.html` line {line})"
    if region != 'page' and region != 'head':
        loc += f", in the {region}"
    elif heading:
        loc += f", under \"{heading}\""
    if len(places) > 1:
        pg = sorted({p[0] for p in places})
        loc += f"; also on {len(places) - 1} more place{'s' if len(places) > 2 else ''}" + (f" ({len(pg)} pages)" if len(pg) > 1 else '')
    return loc

def esc_md(s):
    return s.replace('|', '\\|').replace('\n', ' ')

# ---- group: site-wide chrome first, then each tab in menu order, teacher profiles, then scripts
groups = OrderedDict()
for key, it in found.items():
    rel, line, heading, region = it['places'][0]
    if region in ('menu', 'footer', 'newsletter box', 'header'):
        g = 'Every page: header, menu, newsletter box and footer'
    elif rel.startswith('teachers/') and rel != 'teachers/':
        g = 'Teachers › individual profile pages'
    else:
        g = tab_of(rel)
    groups.setdefault(g, []).append(it)

order = ['Every page: header, menu, newsletter box and footer'] + [t for _, t in TAB] + ['Teachers › individual profile pages']
out = []
total = sum(len(v) for v in groups.values()) + len(SCRIPTS)
out.append('# New text checklist: Redesign 2\n')
out.append(f'Every piece of text in `{RED.name}/` that does not appear word for word on the original site (the mirror in `site/`). '
           f'{total} items. Tick each one once it has been read and approved, changed, or removed.\n')
out.append('How the list was made: `tools/new_text_inventory.py` compares each heading, paragraph, list item, caption, button, page title, '
           'search description, image description and search-box hint with all the text of the original site. '
           'Original text that was edited also shows up here. Text that is the same on many pages is listed once, with a count. '
           'Line numbers are in the built page files and change when the site is rebuilt.\n')
out.append('Where the text came from, when it is not Claude\'s own writing: Q&A questions and session titles come from Alex\'s Q&A index; '
           'video titles from YouTube; "Sample Teacher" entries and their details are invented examples. '
           'The second lineage paragraph is not listed because it is the original site\'s own text, moved from the obituary.\n')
toc = [g for g in order + [k for k in groups if k not in order] if g in groups]
toc = list(dict.fromkeys(toc))
out.append('\n## Contents\n')
out.append('| Section | Items |\n|---|---|')
for g in toc:
    out.append(f'| {g} | {len(groups[g])} |')
if SCRIPTS:
    out.append(f'| Messages shown by the search and map scripts | {len(SCRIPTS)} |')
out.append(f'| **Total** | **{total}** |')
seen = set()
for g in order + [k for k in groups if k not in order]:
    if g in seen or g not in groups:
        continue
    seen.add(g)
    items = groups[g]
    out.append(f'\n## {g} ({len(items)})\n')
    for it in items:
        k = KIND.get(it['kind'], it['kind'])
        out.append(f"- [ ] **{k}:** \"{esc_md(it['text'])}\"  \n  {where(it['places'])}")
if SCRIPTS:
    out.append(f'\n## Messages shown by the search and map scripts ({len(SCRIPTS)})\n')
    out.append('These appear while using Topics search and the Teachers map; they are not in the page files.\n')
    for js, i, s in SCRIPTS:
        out.append(f"- [ ] \"{esc_md(s)}\"  \n  `{RED.name}/assets/{js}` line {i}")
print('\n'.join(out))
