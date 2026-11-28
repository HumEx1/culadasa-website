#!/usr/bin/env python3
"""Generate the redesign draft into redesign/ (static HTML, no build step on the host).

Design: A2 and D2 combined (Darin, 24 Nov 2026): his portrait leads as in A2; D2's cover textures support.
Content: real Culadasa material only (redesign/data/*.json, built from the
WordPress export, the saved galleries, the Q&A index and verified web sources).
Every page sits at the same path as on the old site where one existed, so the
redesign can later replace the mirror without breaking links.

Usage:  python3 tools/build_redesign.py        -> redesign/    (A2 + D2: portrait leads, cover textures)
        python3 tools/build_redesign.py 2      -> redesign-2/  (A2 sans base: more open and minimal; lattice
                                                   texture in the masthead; cover graphics only on The Book)
"""
from urllib.parse import quote_plus
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from spelling import fix_spelling

import json, re, html, pathlib, datetime, urllib.parse, shutil, sys, unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
V2 = len(sys.argv) > 1 and sys.argv[1] == '2'
OUT = ROOT / ('redesign-2' if V2 else 'redesign')
D = ROOT / 'redesign' / 'data'   # one set of data for both variants
content = json.loads((D / 'content.json').read_text())
videos = json.loads((D / 'videos.json').read_text())
topics = json.loads((D / 'topics.json').read_text())
teachers = json.loads((D / 'teachers.json').read_text())
convos = json.loads((D / 'conversations.json').read_text())
qindex = json.loads((D / 'qna_index.json').read_text())   # Alex's Q&A index, parsed by tools/build_qna_index.py
esc = html.escape
YEAR = datetime.date.today().year

NAV = [  # order and names (D, 27 Nov 2026): Start here · Learn · Library · The Book · Teachers · About, then the Search button
    ('Start here', 'start-here/', None),
    ('Learn', 'learn/', None),
    ('Library', None, [('Writings', 'writings/'), ('Audio', 'audio/'), ('Videos', 'videos/'), ('AMA videos', 'online-meetings/')]),   # see LIBRARY_STYLE
    ('The Book', 'the-book/', None),
    ('Teachers', 'teachers/', None),
    ('About', 'lineage/', None),   # Lineage renamed About (D, 27 Nov 2026); the page stays at lineage/
]
# Conversations is a Library room and Search is the button at the right of the menu row (design review, D, 27 Nov 2026)
# Library layout (D, 25 Nov 2026): 'side' = one Library section with its four pages listed down the left (a row of tabs on
# phones), opening on Videos; the pages themselves are unchanged. 'dropdown' = the earlier Library dropdown menu.
# To go back, set LIBRARY_STYLE = 'dropdown' and rebuild both variants.
LIBRARY_STYLE = 'side'
LIB_PAGES = [('Videos', 'videos/'), ('Audio', 'audio/'), ('Writings', 'writings/'), ('Conversations', 'conversations/')]   # AMA videos are in Videos (D, 28 Nov 2026)
if LIBRARY_STYLE == 'side':
    NAV = [('Library', 'library/', None) if n == 'Library' else (n, h, sub) for n, h, sub in NAV]   # the Library front page (D, 27 Nov 2026)


def stamp_assets(doc):
    """Add a version stamp (part of a hash of the file) to every stylesheet and script link, so browsers load the new
    file as soon as it changes instead of a saved copy for up to 10 minutes (D, 25 Nov 2026)."""
    import hashlib
    def stamp(m):
        f = m.group(1)
        src = ROOT / 'tools' / 'site2.css' if f == 'site2.css' else ROOT / 'redesign' / 'assets' / f
        if not src.exists():
            return m.group(0)
        return f'assets/{f}?v={hashlib.md5(src.read_bytes()).hexdigest()[:8]}"'
    return re.sub(r'assets/([\w./-]+\.(?:css|js))"', stamp, doc)


def library_layout(path, body, r):
    """Put a Library page in the side-menu layout: the gold Library banner on top, the four pages down the left."""
    m = re.match(r'\s*(<header class="banner) [a-z]+(">.*?</header>)(.*)', body, re.S)
    if not m:
        return body
    head = m.group(1) + ' teal lib-banner' + m.group(2)   # each page keeps its own label (Watch, Listen, Read…) and rule
    items = ''.join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == path else ""}>{esc(l)}</a></li>' for l, h in LIB_PAGES)
    side = f'<nav class="lib-side" aria-label="Library"><p class="label">Library</p><ul>{items}</ul></nav>'
    return f'{head}<div class="lib-layout wrap">{side}<div class="lib-main">{m.group(3)}</div></div>'

SOCIAL = [
    ('YouTube', 'https://www.youtube.com/@Culadasa',
     '<path d="M21.6 7.2a2.7 2.7 0 0 0-1.9-1.9C18 4.8 12 4.8 12 4.8s-6 0-7.7.5A2.7 2.7 0 0 0 2.4 7.2 28 28 0 0 0 2 12a28 28 0 0 0 .4 4.8 2.7 2.7 0 0 0 1.9 1.9c1.7.5 7.7.5 7.7.5s6 0 7.7-.5a2.7 2.7 0 0 0 1.9-1.9A28 28 0 0 0 22 12a28 28 0 0 0-.4-4.8ZM10 15.1V8.9l5.2 3.1Z" fill="currentColor"/>'),
    ('SoundCloud', 'https://soundcloud.com/culadasa',
     '<path d="M18.5 10.3a4.6 4.6 0 0 0-8.4-2.4v9.6h8.4a3.6 3.6 0 0 0 0-7.2ZM8.8 8.6v8.9h-.9V9.1Zm-1.8 1v7.9h-.9V9.9Zm-1.8.8v6.8h-.9v-6.6Zm-1.8 1.2v5.6h-.9v-5.4Zm-1.8 1.3v3.2H.7v-3.1Z" fill="currentColor"/>'),
    ('Facebook', 'https://www.facebook.com/Culadasa.John.Yates/',
     '<path d="M13.5 21v-7.5H16l.4-3h-2.9V8.7c0-.9.3-1.5 1.5-1.5h1.5V4.6A20 20 0 0 0 14.3 4.5c-2.2 0-3.8 1.4-3.8 3.9v2.1H8v3h2.5V21Z" fill="currentColor"/>'),
    ('Patreon', 'https://www.patreon.com/culadasa',
     '<circle cx="14.5" cy="9.5" r="5.5" fill="currentColor"/><rect x="3" y="4" width="3" height="16" fill="currentColor"/>'),
]


def rel(depth):
    return '../' * depth


SECTION_MENU = {'start-here': 'Start here', 'learn': 'Learn', 'library': 'Library', 'book': 'The Book', 'teachers': 'Teachers', 'lineage': 'About'}


def nav_html(current, r, section=''):
    out = []
    for label, href, sub in NAV:
        if sub:
            cur = any(h == current for _, h in sub)
            subs = ''.join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == current else ""}>{esc(l)}</a></li>' for l, h in sub)
            out.append(f'<li class="has-sub"><button type="button" class="group" aria-expanded="false" aria-controls="sub-{label.lower()}"{" aria-current=\"page\"" if cur else ""}>{label}</button><ul class="sub" id="sub-{label.lower()}">{subs}</ul></li>')
        else:
            cur = ' aria-current="page"' if href == current else ' aria-current="true"' if SECTION_MENU.get(section) == label else ''
            out.append(f'<li><a href="{r}{href}"{cur}>{label}</a></li>')
    return ''.join(out)


def social_html(r=''):
    return ''.join(f'<a href="{u}" rel="noopener" aria-label="Culadasa on {n}"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg></a>' for n, u, p in SOCIAL)


def new_tab(html):
    """Links that leave the site, PDFs and the 'current site' comparison link open in a new tab (D, 24 Nov 2026).
    Moving between pages of this site stays in the same tab."""
    def fix(m):
        tag, href = m.group(0), m.group(1)
        leaves = re.match(r'https?://', href) or href.lower().endswith('.pdf') or 'class="mirror-link"' in tag
        if not leaves or 'target=' in tag:
            return tag
        tag = re.sub(r'\s+rel="[^"]*"', '', tag)
        return tag[:-1] + ' target="_blank" rel="noopener">'
    return re.sub(r'<a\s[^>]*?href="([^"]+)"[^>]*>', fix, html)


# A missing address can be any depth below the site, so the 404 page sets its own base: the site root, or the
# redesign-2 folder while the redesign is previewed there (design review, 27 Nov 2026)
NOTFOUND_BASE = ('\n<script>(function(){var p=location.pathname,i=p.indexOf("/redesign-2/");'
                 'document.write(\'<base href="\'+(i>=0?p.slice(0,i)+"/redesign-2/":"/")+\'">\')})();</script>')


def page(path, title, body, *, description='', compact=False, extra_head='', extra_js='', cover_band=False):
    depth = 0 if path in ('', '404.html') else path.strip('/').count('/') + 1
    r = rel(depth)
    first = path.split('/')[0]
    LIBRARY = {'library', 'conversations', 'writings', 'audio', 'videos', 'online-meetings', 'meditation-manual-introduction', 'mindful-awareness-vs-dullness',
               'amount-of-concentration-needed-for-awakening', 'daily-life-practice', 'cultivating-mindfulness-in-daily-life'}
    section = ('home' if not first else 'library' if first in LIBRARY else 'lineage' if first in ('lineage', 'about', 'testimonials', 'student-testimonials')
               else 'book' if first in ('the-book', 'book-reviews') else 'learn' if first == 'ten-stages' else first)   # the ten stages sit under Learn (D, 27 Nov 2026)
    group = {'start-here': 'guide', 'learn': 'guide', 'topics': 'guide', 'library': 'library', 'book': 'book',
             'teachers': 'people', 'conversations': 'people', 'lineage': 'people'}.get(section, 'home')
    if LIBRARY_STYLE == 'side' and path in {h for _, h in LIB_PAGES}:
        body = library_layout(path, body, r)
    full = 'Culadasa - The Mind Illuminated Path' if path == '' else f'{title} - Culadasa'
    OLD = {'', 'writings/', 'audio/', 'videos/', 'online-meetings/', 'teachers/', 'testimonials/', 'student-testimonials/', 'book-reviews/',
           'meditation-manual-introduction/', 'mindful-awareness-vs-dullness/', 'amount-of-concentration-needed-for-awakening/',
           'daily-life-practice/', 'cultivating-mindfulness-in-daily-life/'}
    counterpart = path if path in OLD else ('teachers/' if path.startswith('teachers/') else ('book-reviews/' if path == 'the-book/' or path.startswith('ten-stages/') else ('online-meetings/' if path == 'topics/' else ('videos/' if path == 'library/' or path.startswith('videos/') else ''))))
    mirror = r + '../' + counterpart
    mirror_label = 'See this page on the current site' if path in OLD else 'See the nearest page on the current site'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">{NOTFOUND_BASE if path == '404.html' else ''}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full)}</title>
<meta name="description" content="{esc(description or title)}">
<meta name="robots" content="noindex">
<meta property="og:title" content="{esc(full)}">
<meta property="og:description" content="{esc(description or title)}">
<meta property="og:image" content="{r}assets/img/tmi-eyes.jpg">
<link rel="icon" href="{r}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@600&family=Jost:ital,wght@0,300;0,400;0,500;1,300&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap">
<link rel="stylesheet" href="{r}assets/site.css">
{f'<link rel="stylesheet" href="{r}assets/site2.css">' if V2 else ''}
{extra_head}</head>
<body data-section="{section}" data-group="{group}">
<a class="skip" href="#main">Skip to content</a>
<div class="preview-bar">{'Draft redesign (2) for review' if V2 else 'Draft redesign for review'}</div>
<header class="masthead{' compact' if compact else ''}{' lattice' if V2 else ''}">
  <a class="wordmark" href="{r or './'}">Culadasa</a>
  <p class="tagline">Upasaka Culadasa · John Yates, Ph.D. · 1945–2021</p>
</header>
{'' if V2 else f'<img class="cubes" src="{r}assets/img/tmi-cubes-band.jpg" alt="">'}
<nav class="nav" aria-label="Main">
  <div class="wrap">
    <button type="button" class="nav-button" aria-expanded="false" aria-controls="menu">Menu</button>
    <ul class="menu" id="menu">{nav_html(path, r, section)}</ul>
    <a class="nav-search" href="{r}topics/" aria-label="Search"{' aria-current="page"' if section == 'topics' else ''}><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="m15.5 15.5 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span>Search</span></a>
  </div>
</nav>
<main id="main">
{body}
</main>
<section class="signup" id="signup" aria-labelledby="signup-h">
  <div class="wrap">
    <div>
      <p class="label">Newsletter</p>
      <h2 id="signup-h">Occasional letters from the archive</h2>
      <p class="muted">A teaching, an AMA moment or a newly added recording, a few times a year. No more than that.</p>
    </div>
    <form class="signup-form" action="#" method="post">
      <label class="sr" for="signup-email">Email address</label>
      <input id="signup-email" type="email" name="email" placeholder="Your email address" autocomplete="email" required>
      <button class="btn" type="submit">Subscribe</button>
      <p class="note" role="status">Preview only: this form is not yet connected to a mailing service, so nothing is sent or stored.</p>
    </form>
  </div>
</section>
<footer class="footer">
  <div class="wrap">
    <div>
      <a class="wordmark" href="{r or './'}">Culadasa</a>
      <nav aria-label="Footer"><ul>
        <li><a href="{r}start-here/">Start here</a></li><li><a href="{r}learn/">Learn</a></li><li><a href="{r}ten-stages/">The ten stages</a></li><li><a href="{r}library/">Library</a></li>
        <li><a href="{r}videos/">Videos</a></li><li><a href="{r}audio/">Audio</a></li><li><a href="{r}videos/?show=ama">AMA videos</a></li><li><a href="{r}writings/">Writings</a></li><li><a href="{r}conversations/">Conversations</a></li>
        <li><a href="{r}the-book/">The Book</a></li><li><a href="{r}teachers/">Teachers</a></li><li><a href="{r}lineage/">About</a></li><li><a href="{r}testimonials/">Testimonials</a></li>
        <li><a href="{r}topics/">Search</a></li><li><a href="#signup">Newsletter</a></li>
      </ul></nav>
    </div>
    <div class="social">{social_html(r)}</div>
    <p class="licence">The teachings of Culadasa are offered freely under a <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">Creative Commons Attribution 4.0</a> license, as he wished. © 2021–{YEAR}.</p>
  </div>
</footer>
<script src="{r}assets/site.js" defer></script>
{extra_js}</body>
</html>
'''
    doc = stamp_assets(doc)
    doc = doc.replace('His principle teachers', 'His principal teachers')   # spelling (D, 25 Nov 2026); the mirror keeps the original
    out = OUT / ('404.html' if path == '404.html' else path + 'index.html' if path else 'index.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(new_tab(doc))
    return out


def banner(label, h1, lead='', tone='teal', extra=''):
    if V2:
        tone = {'ink': 'slate'}.get(tone, tone)
    long_ = ' class="long"' if len(re.sub(r'<[^>]+>', '', h1)) > 40 else ''   # long titles step down one size (design review, 27 Nov 2026)
    m_ = re.search(r'href="([^"]+)"[^>]*>(Open [^<]+)</a>', extra or '')
    if m_ and lead:   # on phones the banner's button becomes a link at the end of the lead (D, 27 Nov 2026)
        lead += f' <a class="phone-only" href="{m_.group(1)}" rel="noopener">{esc(m_.group(2))} ↗</a>'
    return f'''<header class="banner {tone}"><div class="wrap">
  <p class="label">{label}</p><h1{long_}>{h1}</h1>{f'<p class="lead">{lead}</p>' if lead else ''}{extra}
</div></header>'''


def video_tile(v, r, sub=''):
    return f'''<article class="video-card">
  <div class="video" data-id="{v['id']}"><button type="button" aria-label="Play: {esc(v['title'])}"><img src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="" loading="lazy"><span class="play"></span></button></div>
  <h3>{esc(v['title'])}</h3>{f'<p>{sub}</p>' if sub else ''}
</article>'''


SCOPES = [('video', 'Videos'), ('audio', 'Audio'), ('ama', 'AMA'), ('writings', 'Writings'), ('book', 'The Book')]   # "AMA" saves room (D, 27 Nov 2026)   # the Library order (D, 25 Nov 2026)


def scoped_search(r, scope, placeholder, ident):
    """One search box used on several pages (D, 25 Nov 2026): it starts with the page's own scope selected and opens
    Topics with that scope; the reader can widen it to All or switch to another part of the site."""
    # each pill switches on or off by itself, so several parts can be searched together; none on = the whole site (D, 25 Nov 2026)
    # one row of lozenges (D, 25 Nov 2026): All, the kinds, Clear. All = the whole site; Clear = the whole site and an empty box
    pills = ('<button type="button" class="scope-all" onclick="this.form.querySelectorAll(\'input[name=type]\').forEach(function(c){c.checked=false})">All</button>'
             + ''.join(f'<label class="scope-pill"><input type="checkbox" name="type" value="{k}"{" checked" if k == scope or (isinstance(scope, (list, tuple)) and k in scope) else ""}><span>{esc(t)}</span></label>' for k, t in SCOPES)
             + '<button type="button" class="scope-clear" onclick="this.form.querySelectorAll(\'input[name=type]\').forEach(function(c){c.checked=false});this.form.q.value=\'\'">Clear</button>')
    return (f'<form class="search scoped" action="{r}topics/" method="get" role="search" aria-label="Search the teachings">'
            f'<div class="scoped-row"><label class="sr" for="{ident}">Search</label><input id="{ident}" name="q" type="search" placeholder="{esc(placeholder)}">'
            f'<button class="btn">Search</button></div>'
            f'<fieldset class="scope"><legend class="sr">Where to search</legend>{pills}</fieldset></form>')


def sc_player(kind, ident, height=450, comments=True):
    url = f'https%3A//api.soundcloud.com/{kind}/{ident}'
    return (f'<div class="audio"><iframe title="SoundCloud player" loading="lazy" height="{height}" allow="autoplay" '
            f'src="https://w.soundcloud.com/player/?url={url}&amp;color=%23226a7e&amp;auto_play=false&amp;hide_related=true&amp;show_comments={"true" if comments else "false"}&amp;show_user=true&amp;show_reposts=false&amp;visual=false"></iframe></div>')


# ------------------------------------------------------------------ writings data
UP = '../wp-content/uploads/2021/09/'   # the mirror's files, one level above /redesign/
WRITINGS = [
    ('Begin here', [
        ('Recommended Book List', 'pdf', 'reading-list-20130813-1.pdf'),
        ('Beginning Meditation Handout', 'pdf', 'beginning-meditation-handout.pdf'),
        ('Introduction to the Meditation Manual', 'essay', 'meditation-manual-introduction/'),
        ('Meditation Manual for Tranquility and Insight', 'pdf', 'LightOnMeditationHandout.pdf'),
        ('Preparation for Practice', 'pdf', 'preparation-for-practice.pdf'),
        ('Offering the Mandala', 'pdf', 'OFFERING_THE_MANDALA.pdf'),
        ('Commentary on the Satipaṭṭhāna Sutta', 'pdf', 'Satipatthana-Retreat-Handout-Culadasa.pdf'),
    ]),
    ('Teaching Retreats Handouts', [
        ('The Jhānas – The Original Practice of Mindfulness and Insight', 'pdf', 'jhanas-and-mindfulness-handout.pdf'),
        ('Instructions for Entering Jhāna by Leigh Brasington', 'pdf', 'instructions-for-entering-jhana-leigh-brasington.pdf'),
        ('An Introduction to the Practice of the Ten Stages of Samatha', 'pdf', 'Cape-Ann-Retreat-for-Peace-Handout-.pdf'),
        ('The Magic of Mindfulness – Seeing Things as They Really Are', 'pdf', 'Magic-of-Mindfulness-Handout.pdf'),
        ('The Path to Awakening in Daily Life', 'pdf', 'Awakening-in-Daily-Life-Handout.pdf'),
        ('What Is Enlightenment and Why Should I Care?', 'pdf', 'What-Is-Enlightenment-Handout.pdf'),
        ('Meditation and Insight I', 'pdf', 'Meditation-and-Insight-I.pdf'),
        ('Meditation and Insight II', 'pdf', 'Meditation-and-Insight-II.pdf'),
        ('Meditation and Insight III', 'pdf', 'Meditation-and-Insight-III.pdf'),
        ('Meditation and Insight – Slides', 'pdf', 'Insight_Slides-October2012.pdf'),
        ('Introduction to What the Buddha Thought', 'pdf', '20130322-what-the-buddha-thought-handout.pdf'),
        ('Introduction to What the Buddha Thought – Slides', 'pdf', '20130322-what-the-buddha-thought-slides.pdf'),
        ('When Buddhadharma Comes to the West – Part I: Future History in the Making', 'pdf', 'BuddhadharmaWestPartI.pdf'),
        ('When Buddhadharma Comes to the West – Part II & III: What the Buddha Taught & Wisdom and Virtue', 'pdf', 'BuddhadharmaWestPartsIIandIII.pdf'),
        ('Joy & Meditation – More Than Just a Happy Feeling', 'pdf', 'Meditation-and-Joy-Handout.pdf'),
    ]),
    ('Selected Writings from the Jhana_Insight Yahoo discussion board', [
        ('Mindful Awareness vs Dullness', 'essay', 'mindful-awareness-vs-dullness/'),
        ('Amount of Concentration Needed for Awakening', 'essay', 'amount-of-concentration-needed-for-awakening/'),
        ('How to Maintain Practice in One’s Daily Life', 'essay', 'daily-life-practice/'),
        ('Cultivating Mindfulness in Daily Life', 'essay', 'cultivating-mindfulness-in-daily-life/'),
    ]),
]
PDF_PAGES = {}
for d in topics['docs']:
    if d['type'] == 'Handout':
        PDF_PAGES[d['url'].split('/')[-1]] = d


def doc_link(title, kind, target, r):
    if kind == 'pdf':
        words = len(PDF_PAGES.get(target, {}).get('text', '').split())
        mins = max(1, round(words / 230)) if words else None
        meta = f'PDF{f" · {mins} min read" if mins else ""}'
        return f'<li><a href="{r}{UP}{target}"><span>{esc(title)}</span><span class="kind">{meta}</span></a></li>'
    return f'<li><a href="{r}{target}"><span>{esc(title)}</span><span class="kind">Essay</span></a></li>'


# Each stage named by what is achieved in it (D, 26 Nov 2026): the second half of the book's chapter title, checked
# against the 2015 final draft's contents and chapter headings. BOOK_STAGE_TITLES are the book's full titles.
STAGES = [
    ('Establishing a practice', 'Novice'), ('Overcoming mind-wandering', 'Novice'), ('Overcoming forgetting', 'Novice'),
    ('Overcoming gross distraction and strong dullness', 'Skilled'), ('Overcoming subtle dullness and increasing mindfulness', 'Skilled'),
    ('Subduing subtle distractions', 'Skilled'), ('Unifying the mind', 'Transition'), ('Pacifying the senses', 'Adept'),
    ('Calming the intensity of meditative joy', 'Adept'), ('Tranquility and equanimity', 'Adept'),
]
BOOK_STAGE_TITLES = [
    'Establishing a Practice', 'Interrupted Attention and Overcoming Mind-Wandering', 'Extended Attention and Overcoming Forgetting',
    'Continuous Attention and Overcoming Gross Distraction and Strong Dullness', 'Overcoming Subtle Dullness and Increasing Mindfulness',
    'Subduing Subtle Distractions', 'Exclusive Attention and Unifying the Mind', 'Mental Pliancy and Pacifying the Senses',
    'Mental and Physical Pliancy and Calming the Intensity of Meditative Joy', 'Tranquility and Equanimity',
]


def ESSAY_NEXT(slug, r):
    """Where each essay sits in the journey (D, 25 Nov 2026: a next step after reading, back into the journey)."""
    steps = {'meditation-manual-introduction': [('Start here', 'start-here/'), ('Learn: the method', 'learn/#the-method')],
             'mindful-awareness-vs-dullness': [('Start here', 'start-here/'), ('Learn: the basics', 'learn/#the-basics')],
             'amount-of-concentration-needed-for-awakening': [('Learn: going deeper', 'learn/#going-deeper')],
             'daily-life-practice': [('Start here', 'start-here/'), ('Learn: daily life', 'learn/#daily-life')],
             'cultivating-mindfulness-in-daily-life': [('Learn: daily life', 'learn/#daily-life')]}
    return ' · '.join(f'<a href="{r}{h}">{esc(t)} →</a>' for t, h in steps.get(slug, [('Learn', 'learn/')]))


def clean_essay(raw):
    s = re.sub(r'\s(style|class|id)="[^"]*"', '', raw)
    s = re.sub(r'<h2[^>]*>.*?</h2>', '', s, count=1, flags=re.S)
    s = s.replace('develping', 'developing')
    s = fix_spelling(s)   # plain misspellings in the essays (tools/spelling.py; D, 25 Nov 2026)
    s = re.sub(r'<br\s*/?>\s*</', '</', s)
    s = s.replace('https://culadasa.com/', '../')
    s = re.sub(r'<a[^>]*(justanotherwp|dacremabotanicals)[^>]*>.*?</a>', '', s, flags=re.S)  # host spam on the old pages
    s = re.sub(r'<p>\s*(Powered by WooCommerce error|Powered by)?\s*</p>', '', s)  # the words left over from the hidden spam advert
    paras = [p.strip() for p in re.split(r'\n\s*\n', s) if p.strip()]
    out = []
    for p in paras:
        out.append(p if re.match(r'<(p|ul|ol|h\d|blockquote)', p) else f'<p>{p}</p>')
    return '\n'.join(out)


EYES = '''<section class="eyes-band" aria-label="Closing">
  <img src="assets/img/tmi-eyes.jpg" alt="The closed eyes of the Buddha, from the cover of The Mind Illuminated" loading="lazy">
  <p>All of Culadasa’s students are his successors.</p>
  <p class="small muted" style="font-family:var(--text);font-size:15px;margin-top:6px">- The Yates family</p>
</section>'''


def book_finder(r):
    """Search the book, across the page below the cover (D, 25 Nov 2026; no word cloud). The book is not on this site:
    results give the place in the book (page, chapter, heading, paragraph, line) and, for teaching terms, a few short phrases."""
    if not (D / 'book.json').exists():
        return ''
    return (f'<section class="section tight book-finder"><div class="wrap"><p class="label">Search the book</p>'
            f'{scoped_search(r, "book", "Search the book", "b-q")}'
            f'<p class="small muted">The book itself is not on this site. A search shows where a word appears (page, chapter, heading, paragraph and line, in the 2015 first edition) and, for teaching terms, a few short phrases, so you can find the passage in your own copy.</p></div></section>')


def row(title, meta, body, key=''):
    """One title row that opens to show its detail (D, 25 Nov 2026): the same convention as the search results."""
    return (f'<details class="lrow"{f" id={chr(34)}{esc(key)}{chr(34)}" if key else ""}><summary><span class="rr-name">{esc(title)}</span>'
            f'<span class="rr-meta">{esc(meta)}</span></summary><div class="rr-body">{body}</div></details>')


def row_groups(groups, show=4):
    """Sections of title rows; each shows `show` rows, "Show all N" opens the rest, "Show fewer" closes them."""
    out = ''
    for name, rows_ in groups:
        extra = len(rows_) - show
        out += (f'<section class="rgroup{" open" if extra <= 0 else ""}"><h3 class="result-group"><span class="rg-name">{esc(name)}</span>'
                f'<span class="rg-count">{len(rows_)}</span></h3>'
                + ''.join(r_ if k < show else f'<div class="rg-more">{r_}</div>' for k, r_ in enumerate(rows_))
                + (f'<p class="rg-foot"><button type="button" class="linklike rg-all">Show all {len(rows_)} in {esc(name)}</button>'
                   f'<button type="button" class="linklike rg-less">Show fewer</button></p>' if extra > 0 else '') + '</section>')
    return out


def play(url, label):
    """A time as a play button (D, 25 Nov 2026): ▶ 12:34, opening the recording or video at that moment."""
    ext = url.startswith('http')
    return f'<a class="play" href="{esc(url)}" aria-label="Play from {esc(label)}{" on YouTube" if "youtube" in url else ""}{" (opens a new tab)" if ext else ""}"{" rel=\"noopener\"" if ext else ""}>{esc(label)}</a>'


def handout_map():
    """Handouts linked from the recordings → our own copies (docs/AUDIO_LINKS.md)."""
    m, cur = {}, []
    p_ = ROOT / 'docs' / 'AUDIO_LINKS.md'
    if not p_.exists():
        return m
    for line in p_.read_text().splitlines():
        if line.startswith('- Linked as: '):
            cur.append(line[13:].strip())
        elif line.startswith('- Our copy: `'):
            for u in cur:
                m[u] = line.split('`')[1]
            cur = []
        elif line.startswith('### '):
            cur = []
    return m


NUMW = ['One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']


def hms_(t):
    t = int(t)
    return f'{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}' if t >= 3600 else f'{t // 60}:{t % 60:02d}'


def yt_secs(t):
    """Seconds from a YouTube time parameter: "7m27s", "47s", "1h2m3s", "47"."""
    t = str(t or '0')
    if t.isdigit():
        return int(t)
    return sum(int(n) * {'h': 3600, 'm': 60, 's': 1}[u] for n, u in re.findall(r'(\d+)([hms])', t))


def yt_page(url, prefix):
    """A YouTube link (watch?v=ID&t=…) as a link to that video's page on this site, at the same moment (D, 28 Nov 2026)."""
    m = re.search(r'[?&]v=([\w-]{11})(?:.*?[?&]t=([0-9hms]+))?', url or '')
    if not m:
        return url
    t = yt_secs(m.group(2)) if m.group(2) else 0
    return f'{prefix}videos/{m.group(1)}/' + (f'?t={t}' if t else '')


def related_topics(n, rr):
    """Topic pages that belong with stage n (D, 28 Nov 2026)."""
    f_ = D / 'topic_pages.json'
    if not f_.exists():
        return ''
    ts = [t for t in json.loads(f_.read_text())['topics'] if n in t['stages']]
    return ('<p class="small related">Related topics: ' + ' · '.join(f'<a href="{rr}learn/topics/{t["slug"]}/">{esc(t["title"])}</a>' for t in ts) + '</p>') if ts else ''


def stage_pages(r):
    """The ten stages in his words (D, 25 Nov 2026): an overview, and a page per stage with a video to start with and
    every place he talks about that stage. The mentions come from tools/build_stages.py (rules in docs/STAGES.md)."""
    f_ = D / 'stages.json'
    if not f_.exists():
        return
    data = json.loads(f_.read_text())['stages']
    yt = lambda i, t=0: f'{rr}videos/{i}/' + (f'?t={int(t)}' if t else '')   # the video's own page, at the moment (D, 28 Nov 2026)
    total = lambda st: sum(x['n'] for k in ('videos', 'ama', 'writings', 'audio') for x in st[k])
    rr = '../../'
    PROVISIONAL = 'Chosen for now as the stretch where he talks about this stage longest. The teachers will choose the video to start with.'
    for st in data:
        n, (name, lvl) = st['n'], STAGES[st['n'] - 1]
        W = NUMW[n - 1]
        moments = lambda ms, vid: ''.join(f'<p class="tline">{play(yt(vid, t), hms_(t))} {sn}</p>' for t, sn in ms)
        vrows = [row(v['title'], f"{v['n']} mention{'s' if v['n'] != 1 else ''} · {v['date']}",
                     moments(v['moments'], v['id']) + f'<p class="rr-open"><a href="{yt(v["id"])}">Open the video page →</a></p>')
                 for v in st['videos']]
        arows = []
        for a in st['ama']:
            body = ''
            if a['questions']:
                body += '<ol class="qlist">' + ''.join(f'<li><a class="t" href="{esc(yt_page(u, rr))}" aria-label="Play from {esc(t)}">{esc(t)}</a> <span class="qsnip">{sn}</span></li>' for t, u, sn in a['questions']) + '</ol>'
            if a['moments']:
                body += ('<p class="small muted said">In the recording:</p>' if a['questions'] else '') + moments(a['moments'], a['id'])
            body += f'<p class="rr-open"><a href="{yt(a["id"])}">Open the video page: its questions and transcript →</a></p>'
            arows.append(row(a['title'], f"{a['n']} mention{'s' if a['n'] != 1 else ''}", body))
        def drows(items, label):
            out = []
            for d in items:
                u = d['url'] if d['url'].startswith('http') else '../' + d['url']
                nt_ = ' target="_blank" rel="noopener"' if u.startswith('http') or u.endswith('.pdf') else ''
                out.append(row(d['title'], f"{d['n']} mention{'s' if d['n'] != 1 else ''}",
                               ''.join(f'<p>{sn}</p>' for sn in d['snips'][:8]) + (f'<p class="small muted">and {len(d["snips"]) - 8} more</p>' if len(d['snips']) > 8 else '')
                               + f'<p class="rr-open"><a href="{esc(u)}"{nt_}>{label} →</a></p>'))
            return out
        groups = [(g, rows_) for g, rows_ in (('Videos', vrows), ('AMA videos', arows), ('Writings', drows(st['writings'], 'Open')),
                                               ('Audio', drows(st['audio'], 'Open the recording'))) if rows_]
        b = st.get('book')
        if b:
            groups.append(('The Book', [row(f'The Mind Illuminated: Stage {W}', f"pages {b['first']}–{b['last']} · first edition, 2015",
                                            f'<p>The book’s chapter on Stage {W}, {esc(BOOK_STAGE_TITLES[n - 1])}, runs from page {b["first"]} to page {b["last"]} of the 2015 first edition. Page numbers in later editions may differ.</p>'
                                            f'<p class="rr-open"><a href="{rr}the-book/">About the book →</a></p>')]))
        pin = st.get('pin')
        pin_html = ''
        if pin:
            pin_html = f'''<section class="section tight"><div class="wrap"><div class="stage-pin">
  <h2 class="label">Start with this video</h2>
  {video_tile({'id': pin['id'], 'title': pin['title']}, rr).replace('<div class="video" data-id=', f'<div class="video" data-start="{pin["start"]}" data-id=', 1)}
  <p class="small">{play(yt(pin['id'], pin['start']), hms_(pin['start']))} It starts where he talks about Stage {W}. <a href="{yt(pin['id'], pin['start'])}">Open the video page →</a></p>
  <p class="small muted">{'Chosen by the teachers.' if pin.get('chosen') else PROVISIONAL}</p>
</div></div></section>'''
        prev_ = f'<a href="{rr}ten-stages/stage-{n - 1}/">← Stage {NUMW[n - 2]}</a>' if n > 1 else '<span></span>'
        next_ = f'<a href="{rr}ten-stages/stage-{n + 1}/">Stage {NUMW[n]} →</a>' if n < 10 else '<span></span>'
        body = banner(f'<a href="{rr}ten-stages/">The ten stages</a> · {lvl}', f'Stage {W}: {esc(name)}', f'In the book: {esc(BOOK_STAGE_TITLES[n - 1])}', 'gold') + f'''
{pin_html}
<section class="section tight"><div class="wrap measure"><p class="lead">Everything Culadasa said about Stage {W} in his talks, AMA videos, writings and recordings: {total(st)} mentions. Much of it came after the book was published, so it adds to what the book says.</p>
{related_topics(n, rr)}
<p class="book-link"><a href="{rr}the-book/">About <em>The Mind Illuminated</em> and its method →</a></p></div></section>
<section class="section"><div class="wrap"><h2>Where he talks about Stage {W}</h2><p class="rr-hint">Select a title to see where it’s mentioned.</p>{row_groups(groups)}
<nav class="stage-nav" aria-label="Stages">{prev_}<a href="{rr}ten-stages/">All ten stages</a>{next_}</nav></div></section>'''
        body = body.replace('<h1 class="long">', '<h1>', 1).replace('<h1>', '<h1 class="stage">', 1)   # one title size for all ten stages (round 3, 27 Nov 2026)
        page(f'ten-stages/stage-{n}/', f'Stage {W}: {name}', body, description=f'Stage {W} of The Mind Illuminated, {name}: a video to start with and everything Culadasa said about it.')
    # the overview
    r1 = '../'
    items = ''.join(f'''<li><a href="stage-{st['n']}/"><span><small>{STAGES[st['n'] - 1][1]}</small>{esc(STAGES[st['n'] - 1][0])}<em class="stage-count">{total(st)} mentions</em></span></a></li>''' for st in data)
    body = banner('<a href="../learn/">Learn</a>', 'The ten stages', 'Each stage of <em>The Mind Illuminated</em>, in Culadasa’s own words.', 'gold') + f'''
<section class="section"><div class="wrap">
<p class="measure">Open a stage for a video to start with and every place he talks about it. Many of these talks came after the book, so they add to it: questions students asked as they practised, and his answers. The book’s own overview of the ten stages is on pages 2–19 of the 2015 first edition.</p>
<ol class="stages linked">{items}</ol>
<p class="muted small" style="margin-top:18px">Milestones: continuous attention to the meditation object (after stage 3); sustained exclusive focus of attention (after stage 6); effortless stability of attention (after stage 7); persistence of the mental qualities of an adept (after stage 10).</p>
<p class="muted small">The videos to start with are chosen for now by where he talks about each stage longest. The teachers will choose them.</p>
<p class="book-link"><a href="../the-book/">About <em>The Mind Illuminated</em> and its method →</a></p>
</div></section>'''
    page('ten-stages/', 'The ten stages', body, description='The ten stages of The Mind Illuminated, each with a video to start with and everything Culadasa said about it.')


# The glossary (D, 28 Nov 2026): Pāli and method terms, each with a one-line meaning. The meanings are a first draft
# by Claude for the teachers to check against his own glossary and teaching (volunteer task); the page says so.
GLOSSARY = [
    ('ānāpānasati', 'anapanasati', 'Mindfulness of breathing: the meditation the ten stages are built on.', 'mindfulness'),
    ('anattā', 'anatta, no-self', 'Not-self: no lasting, separate self is found in experience.', 'insight'),
    ('anicca', 'impermanence', 'Impermanence: everything that arises passes away.', 'insight'),
    ('attention', '', 'Focusing on one part of experience, picking it out from everything else.', 'attention-and-awareness'),
    ('bhāvanā', 'bhavana', 'Cultivation: meditation as the steady development of the mind.', ''),
    ('brahmavihāras', 'brahmaviharas', 'The four "divine abodes": loving-kindness, compassion, sympathetic joy and equanimity.', 'metta'),
    ('Dark Night', '', 'A period of distress that can follow an insight breakthrough; he distinguished it from the dukkha ñāṇas.', 'dark-night'),
    ('dukkha ñāṇas', 'dukkha nanas', 'The insight knowledges of suffering: the stages of insight in the Theravāda map that follow the arising and passing away.', 'insight'),
    ('dukkha', 'dukkha', 'Suffering, unsatisfactoriness: the first of the Four Noble Truths.', 'craving'),
    ('dullness', 'strong dullness, subtle dullness', 'A drop in the mind’s energy and clarity, from drowsiness to a pleasant haze.', 'dullness'),
    ('ekaggatā', 'ekaggata', 'Unification of mind: he notes it is often mistranslated as "one-pointedness".', 'unification'),
    ('equanimity', 'upekkhā', 'Balance that is not pushed or pulled by pleasant or unpleasant experience.', 'equanimity'),
    ('forgetting', '', 'Losing track of the meditation object altogether, without noticing.', 'forgetting'),
    ('gross distraction', '', 'A distraction that takes over attention while the meditation object fades to the background.', 'distraction'),
    ('introspective awareness', '', 'Awareness of what the mind itself is doing, from moment to moment.', 'attention-and-awareness'),
    ('jhāna', 'jhana, dhyāna', 'A meditative absorption: a deeply unified, stable and joyful state.', 'jhana'),
    ('karuṇā', 'karuna', 'Compassion: the wish that others be free of suffering.', 'metta'),
    ('mettā', 'metta, loving-kindness', 'Loving-kindness: warm goodwill toward oneself and all beings.', 'metta'),
    ('metacognitive introspective awareness', '', 'Clear, continuous awareness of the state and activity of the mind.', 'metacognition'),
    ('mind-system', 'sub-minds', 'His model of the mind as many sub-minds that share a common space of consciousness.', 'mind-system'),
    ('mind-wandering', '', 'Forgetting the meditation object and following other thoughts, sometimes for a long time.', 'mind-wandering'),
    ('muditā', 'mudita', 'Sympathetic joy: gladness at the happiness of others.', 'metta'),
    ('nibbāna', 'nirvana', 'The end of craving and suffering: the goal of the path.', 'awakening'),
    ('nimitta', 'nimitta', 'A sign: a mental image or light that can appear in deep concentration.', 'jhana'),
    ('passaddhi', 'passaddhi', 'Tranquility: the calm that follows the settling of joy.', 'piti'),
    ('peripheral awareness', '', 'The broad, open awareness of everything in the background of attention.', 'attention-and-awareness'),
    ('pīti', 'piti, meditative joy', 'Meditative joy: an energising delight of body and mind.', 'piti'),
    ('pliancy', 'mental pliancy, physical pliancy', 'A mind and body that work together without resistance, as attention becomes effortless.', 'unification'),
    ('purification', '', 'Old mental material surfacing and being released as the mind unifies.', 'purification'),
    ('samādhi', 'samadhi', 'Concentration, which he described as unification of mind; the ten stages build it with stable attention and mindfulness.', 'unification'),
    ('samatha', 'shamatha, śamatha', 'Tranquility: a calm, stable and joyful mind, the goal of the ten stages.', ''),
    ('sampajañña', 'sampajanna', 'Clear comprehension: knowing what one is doing while doing it.', 'mindfulness'),
    ('sati', 'mindfulness', 'Mindfulness: the optimal working together of attention and awareness.', 'mindfulness'),
    ('stream entry', 'sotāpatti', 'The first stage of awakening; one who has reached it is a sotāpanna, a stream-enterer.', 'awakening'),
    ('subtle distraction', '', 'Other thoughts and sensations at the edge of attention while the object stays in focus.', 'distraction'),
    ('sukha', 'sukha', 'Happiness: the deep contentment that comes with meditative joy.', 'piti'),
    ('taṇhā', 'tanha, craving', 'Craving: wanting and not-wanting, the cause of suffering.', 'craving'),
    ('unification of mind', '', 'Sub-minds coming to share the same intention, so the mind works as one.', 'unification'),
    ('upekkhā', 'upekkha, equanimity', 'Equanimity: balance and evenness in the face of every kind of experience.', 'equanimity'),
    ('vipassanā', 'vipassana, insight', 'Insight: seeing clearly how things really are.', 'insight'),
]


def nice_date_(d_):
    try:
        y_, m_, dd_ = map(int, d_.split('-'))
        return f'{dd_} {datetime.date(y_, m_, 1).strftime("%B")} {y_}'
    except Exception:
        return d_


def azkey(t):
    """A–Z order that ignores accents and a leading "The"."""
    t = unicodedata.normalize('NFD', t.lower()).encode('ascii', 'ignore').decode()
    return t[4:] if t.startswith('the ') else t


def topic_pages(r):
    """Topic pages and the glossary (D, 28 Nov 2026), under Learn, built like the stage pages. Data from
    tools/build_topic_pages.py (rules in docs/TOPICS.md)."""
    f_ = D / 'topic_pages.json'
    if not f_.exists():
        return
    data = json.loads(f_.read_text())['topics']
    book = json.loads((D / 'book.json').read_text()) if (D / 'book.json').exists() else None
    rr = '../../../'
    yt = lambda i, t=0: f'{rr}videos/{i}/' + (f'?t={int(t)}' if t else '')
    mentions = lambda n: f"{n} mention{'s' if n != 1 else ''}"
    titles = {t['slug']: t['title'] for t in data}
    for st in data:
        moments = lambda ms, vid: ''.join(f'<p class="tline">{play(yt(vid, t), hms_(t))} {sn}</p>' for t, sn in ms)
        vrows = [row(v['title'], f"{mentions(v['n'])} · {nice_date_(v['date'])}", moments(v['moments'], v['id']) + f'<p class="rr-open"><a href="{yt(v["id"])}">Open the video page →</a></p>') for v in st['videos']]
        arows = []
        for a in st['ama']:
            body = ''
            if a['questions']:
                body += '<ol class="qlist">' + ''.join(f'<li><a class="t" href="{esc(yt_page(u, rr))}" aria-label="Play from {esc(t)}">{esc(t)}</a> <span class="qsnip">{sn}</span></li>' for t, u, sn in a['questions']) + '</ol>'
            if a['moments']:
                body += ('<p class="small muted said">In the recording:</p>' if a['questions'] else '') + moments(a['moments'], a['id'])
            body += f'<p class="rr-open"><a href="{yt(a["id"])}">Open the video page: its questions and transcript →</a></p>'
            arows.append(row(a['title'], mentions(a['n']), body))
        def drows(items, label):
            out = []
            for d in items:
                u = d['url'] if d['url'].startswith('http') else '../../' + d['url']
                nt_ = ' target="_blank" rel="noopener"' if u.startswith('http') or u.endswith('.pdf') else ''
                more = f'<p class="small muted">and {d["n"] - len(d["snips"][:8])} more in it</p>' if d['n'] > len(d['snips'][:8]) else ''
                out.append(row(d['title'], mentions(d['n']), ''.join(f'<p>{sn}</p>' for sn in d['snips'][:8]) + more + f'<p class="rr-open"><a href="{esc(u)}"{nt_}>{label} →</a></p>'))
            return out
        groups = [(g, rows_) for g, rows_ in (('Videos', vrows), ('AMA videos', arows), ('Writings', drows(st['writings'], 'Open')), ('Audio', drows(st['audio'], 'Open the recording'))) if rows_]
        b = st.get('book')
        if b:
            pg = ', '.join(b['pages'][:40]) + (f' and {len(b["pages"]) - 40} more' if len(b['pages']) > 40 else '')
            groups.append(('The Book', [row('The Mind Illuminated', f"{b['n']} places · first edition, 2015",
                                            f'<p>In the book, on pages {esc(pg)}. Page numbers are from the 2015 first edition; later editions may differ.</p><p class="rr-open"><a href="{rr}the-book/">About the book →</a></p>')]))
        pin = st.get('pin')
        pin_html = ''
        if pin:
            pin_html = f'''<section class="section tight"><div class="wrap"><div class="stage-pin">
  <h2 class="label">Start with this video</h2>
  {video_tile({'id': pin['id'], 'title': pin['title']}, rr).replace('<div class="video" data-id=', f'<div class="video" data-start="{pin["start"]}" data-id=', 1)}
  <p class="small">{play(yt(pin['id'], pin['start']), hms_(pin['start']))} It starts where he turns to this topic. <a href="{yt(pin['id'], pin['start'])}">Open the video page →</a></p>
  <p class="small muted">{'Chosen for now as the talk named for this topic that mentions it most.' if pin.get('titled') else 'Chosen for now as the ten minutes where he mentions it most.'} The teachers will choose the video to start with.</p>
</div></div></section>'''
        stage_links = ' · '.join(f'<a href="{rr}ten-stages/stage-{n}/">Stage {NUMW[n - 1]}</a>' for n in st['stages'])
        intro = (f'<p class="small muted">{st["total"]} mentions in all. This topic and its introduction are a first draft, for the teachers to confirm.</p>'
                 + (f'<p class="small">Belongs with: {stage_links}</p>' if stage_links else '')
                 + f'<p class="book-link"><a href="{rr}learn/glossary/">Glossary →</a> · <a href="{rr}learn/topics/">All topics →</a></p>')
        body = banner(f'<a href="{rr}learn/topics/">Topics</a>', esc(st['title']), esc(st['lead']), 'gold') + f'''
{pin_html}
<section class="section tight"><div class="wrap measure">{intro}</div></section>
<section class="section"><div class="wrap"><h2>Where he talks about it</h2><p class="rr-hint">Select a title to see where it’s mentioned.</p>{row_groups(groups)}</div></section>'''
        page(f'learn/topics/{st["slug"]}/', st['title'], body, description=f'{st["title"]}: everything Culadasa said about it, in his talks, AMA videos, writings and recordings.')
    # the list of topics
    items = ''.join(f'<li><a href="{t["slug"]}/"><span class="tl-name">{esc(t["title"])}</span><span class="tl-lead">{esc(t["lead"])}</span><span class="tl-n">{t["total"]} mentions</span></a></li>' for t in sorted(data, key=lambda x: azkey(x['title'])))
    body = banner('<a href="../">Learn</a>', 'Topics', 'The questions students bring, each with what he said about it.', 'gold') + f'''
<section class="section"><div class="wrap">
<p class="measure">Each topic gathers what he said about it in his talks, AMA videos, writings and recordings, with a video to start with. The list is a first draft for the teachers to confirm. The <a href="../glossary/">glossary</a> gives a short meaning for each Pāli and method term.</p>
<ul class="topic-list">{items}</ul>
</div></section>'''
    page('learn/topics/', 'Topics', body, description='The teaching topics of The Mind Illuminated Path, each with everything Culadasa said about it.')
    # the glossary
    rows_ = ''
    for term, also, meaning, slug in sorted(GLOSSARY, key=lambda g: azkey(g[0])):
        links = ([f'<a href="../topics/{slug}/">{esc(titles.get(slug, slug))} →</a>'] if slug else []) + [f'<a href="../../topics/?q={quote_plus(term)}">Search →</a>']
        rows_ += (f'<div class="gl-row" id="{esc(re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFD", term.lower()).encode("ascii", "ignore").decode()).strip("-"))}">'
                  f'<dt>{esc(term)}' + (f' <span class="gl-also">{esc(also)}</span>' if also and also.lower() != term.lower() else '') + '</dt>'
                  f'<dd>{esc(meaning)}<span class="gl-links">{" · ".join(links)}</span></dd></div>')   # no book page: the word index cannot tell an entry from a mention
    body = banner('<a href="../">Learn</a>', 'Glossary', 'Pāli and method terms, each with a short meaning and where to find more.', 'gold') + f'''
<section class="section"><div class="wrap measure">
<p class="small muted">The meanings are a first draft, to be checked by the teachers against his own glossary in <em>The Mind Illuminated</em> and his teaching. Each term links to its topic page where there is one, and to a search of everything he said.</p>
<dl class="glossary">{rows_}</dl>
</div></section>'''
    page('learn/glossary/', 'Glossary', body, description='Pāli and method terms of The Mind Illuminated Path, each with a short meaning.')


def build():
    vid_by_id = {v['id']: v for v in videos}
    global WORDS
    WORDS = sum(len(d['text'].split()) for d in topics['docs']) + sum(len(i['text'].split()) for s in topics['qna'] for i in s['items'])
    # the video transcripts are searched too (D, 25 Nov 2026); they are a separate file, loaded only when needed
    _tr = json.loads((D / 'transcripts.json').read_text())['videos'] if (D / 'transcripts.json').exists() else []
    N_VIDEOS, N_AUDIO = len(_tr), sum(1 for d in topics['docs'] if d['type'] == 'Audio')
    N_WRIT = sum(1 for d in topics['docs'] if d['type'] in ('Handout', 'Essay'))
    N_AUDIO_TXT = f'{N_AUDIO // 100 * 100}+'   # D, 25 Nov 2026: "400+ audio recordings"
    WORDS += sum(len(v['text'].split()) for v in _tr)
    qna = topics['qna']
    talks = [v for v in videos if v['group'] == 'talks']

    # ---------------------------------------------------------------- home
    cloud_top = [w for w, _ in topics['cloud'][:10]]
    feat = [vid_by_id[i] for i in ('2LYa1YCdZH8', 'vtWoFpEHTBs') if i in vid_by_id] + [vid_by_id[qna[-1]['video']]]
    body = f'''
<section class="lead-hero">
  <div class="wrap">
    <div class="portrait-frame"><img src="assets/img/culadasa-portrait.jpg" alt="Culadasa, John Yates" width="440" height="587"></div>
    <div>
      <p class="label">The Mind Illuminated Path, free for everyone</p>
      <h1>“Culadasa gives us the full conceptual framework together with complete instructions for putting it into play.”</h1>
      <p class="by">- Sharon Salzberg, meditation teacher and author of <em>Real Happiness</em></p>
      <div class="actions"><a class="btn" href="start-here/">Start here</a><a class="btn ghost" href="topics/">Search the teachings</a></div>
      <p class="lead">Culadasa, John Yates Ph.D., spent four decades in the Tibetan and Theravādin traditions and taught physiology and neuroscience. His book <em>The Mind Illuminated</em> joins the two. Everything he taught is here, free.</p>
      <p class="lineage-link"><a href="lineage/">Culadasa’s Buddhist Lineage →</a></p>
    </div>
  </div>
</section>
{'' if V2 else '<img class="glow" src="assets/img/tmi-cubes-glow.jpg" alt="">'}
<section class="section">
  <div class="wrap">
    <h2 class="label">Find your way in</h2>
    <div class="grid cols-4">
      <a class="card" href="start-here/"><span class="meta">New to meditation</span><h3>Start here</h3><p>Seven steps from your first sit to a daily practice, using his own handouts and guided meditations.</p><span class="more">Begin →</span></a>
      <a class="card" href="learn/"><span class="meta">From the basics to going deeper</span><h3>Learn the method</h3><p>The Mind Illuminated Path: the ten stages, insight and daily life, with Culadasa as guide.</p><span class="more">Learn →</span></a>
      <a class="card" href="topics/"><span class="meta">Every teaching, searchable</span><h3>Search</h3><p>Search over a million words: every word of about {round(N_VIDEOS, -1)} videos, {N_WRIT} retreat handouts and essays, {sum(len(s_["items"]) for s_ in topics["qna"])} AMA questions, and the titles and descriptions of {N_AUDIO_TXT} audio recordings.</p><span class="more">Search →</span></a>
      <a class="card" href="teachers/"><span class="meta">Practice with someone</span><h3>Find a teacher</h3><p>The 48 teachers certified in The Mind Illuminated Teacher Training Program.</p><span class="more">Find →</span></a>
    </div>
  </div>
</section>
<section class="section tight band-panel">
  <div class="wrap">
    <form class="search" action="topics/" method="get" role="search">
      <label class="sr" for="home-q">Search the teachings</label>
      <input id="home-q" name="q" type="search" placeholder="Search the teachings">
      <button class="btn" type="submit">Search</button>
    </form>
    <p class="small muted" style="margin:14px 0 0">Most discussed: {" · ".join(f'<a href="topics/?q={urllib.parse.quote(w)}">{esc(w)}</a>' for w in cloud_top)}</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <p class="label">Watch</p><h2>From the archive</h2><p class="muted">Talks from his YouTube channel, and the May 2021 AMA video. <a href="videos/">All videos</a> · <a href="videos/?show=ama">AMA videos</a></p>
    <div class="grid">{''.join(video_tile(v, '') for v in feat)}</div>
  </div>
</section>
<section class="section banner-section {"slate" if V2 else "ink"}">
  <div class="wrap two">
    <div><img class="framed" src="assets/img/the-mind-illuminated-cover.jpg" alt="Cover of The Mind Illuminated" width="320" loading="lazy"></div>
    <div>
      <p class="label">The book</p>
      <h2>The Mind Illuminated</h2>
      <p>A complete meditation guide integrating Buddhist wisdom and brain science, written with Matthew Immergut and Jeremy Graves. Its ten stages map the path from a first, distracted sit to tranquility and equanimity.</p>
      <ol class="stages compact">{''.join(f'<li><span>{esc(n)}</span></li>' for n, _ in STAGES[:5])}</ol>
      <p><a class="btn ghost light" href="ten-stages/">The ten stages →</a></p>
    </div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <p class="label">Conversations</p>
    <h2>Culadasa in conversation</h2>
    <div class="grid">{''.join(f'<a class="card" href="{esc(c["url"])}" rel="noopener"><span class="meta">{esc(c["show"])} · {esc(c["date_label"])}</span><h3>{esc(c["title"])}</h3><p>{esc(c["description"])}</p><span class="more">{esc(c["cta"])} →</span></a>' for c in convos["items"][:3])}</div>
    <p style="margin-top:20px"><a href="conversations/">All conversations →</a></p>
  </div>
</section>
{'' if V2 else EYES}'''
    page('', 'Home', body,
         description='The Mind Illuminated meditation path, taught by Upasaka Culadasa (John Yates, Ph.D.): talks, AMA videos, writings, recordings and teachers.')

    # ---------------------------------------------------------------- start here
    r = '../'
    steps = [
        ('Read the beginning meditation handout', 'Two pages on posture, the breath at the nose, and what to do when the mind wanders.', f'<a class="btn ghost" href="{r}{UP}beginning-meditation-handout.pdf">Open the handout (PDF)</a>'),
        ('Prepare for each sit', 'His six preparations: motivation, goals, expectations, diligence, distractions and posture.', f'<a class="btn ghost" href="{r}{UP}preparation-for-practice.pdf">Preparation for Practice (PDF)</a>'),
        ('Sit with a guided meditation', 'Follow his voice. Start with one of the shorter recordings and sit daily, even briefly.', sc_player('playlists', '282960661', 300, False)),
        ('Learn the map', 'The ten stages show where you are and what to work on next. Read the introduction to the meditation manual, then the stages.', f'<div class="actions"><a class="btn ghost" href="{r}meditation-manual-introduction/">Introduction to the manual</a><a class="btn ghost" href="{r}ten-stages/">The ten stages</a></div>'),
        ('Understand attention and awareness', 'The two kinds of knowing the whole method trains. His essay on dullness explains why vividness matters.', f'<a class="btn ghost" href="{r}mindful-awareness-vs-dullness/">Mindful Awareness vs Dullness</a>'),
        ('Take it into daily life', 'Practice does not end when you stand up. His handout and essays on daily life.', f'<div class="actions"><a class="btn ghost" href="{r}{UP}Awakening-in-Daily-Life-Handout.pdf">The Path to Awakening in Daily Life (PDF)</a><a class="btn ghost" href="{r}daily-life-practice/">Maintaining practice in daily life</a></div>'),
        ('Ask your question', 'Someone has probably asked it already. Search his ' + str(sum(len(s_['items']) for s_ in topics['qna'])) + ' recorded questions and everything he says in about 100 videos, and jump to his answer.', f'<a class="btn" href="{r}topics/">Search the teachings</a>'),
    ]
    body = banner('New to meditation', 'Start here', 'Seven steps from your first sit to the focus, resilience and calm of a daily practice.', 'teal') + f'''
<section class="section"><div class="wrap measure"><h2 class="sr">Seven steps</h2><ol class="steps">{''.join(f'<li><div><h3>{t}</h3><p>{d}</p>{a}</div></li>' for t, d, a in steps)}</ol></div></section>
<section class="section band-panel" id="asked"><div class="wrap measure"><p class="label">Frequently asked</p><h2>What people asked him most</h2>
<p class="muted">From the 441 questions put to him in his AMA videos, 2017–2021. Each link opens his answers, most-discussed first.</p>
<ul class="doclist">{''.join(f'<li><a href="{r}topics/?q={urllib.parse.quote(f["q"])}&amp;type=Q%26A"><span>{esc(f["label"])}</span><span class="kind">{f["n"]} questions</span></a></li>' for f in content['faq'])}</ul></div></section>'''
    page('start-here/', 'Start here', body, description='A seven-step beginning path through Culadasa’s own handouts, guided meditations and essays.')

    # ---------------------------------------------------------------- learn hub (journey by level)
    def qlink(q): return f'{r}topics/?q={urllib.parse.quote(q)}'
    tracks = [
        ('The basics', 'teal', [
            ('What meditation trains', 'Attention and peripheral awareness, and how they work together.', qlink('peripheral awareness')),
            ('Posture and preparation', 'Sitting comfortably and the six preparations.', f'{r}{UP}preparation-for-practice.pdf'),
            ('Mind-wandering', 'Why the mind wanders, and why noticing it is a success, not a failure.', f'{r}learn/topics/mind-wandering/'),
            ('Dullness', 'Mindful awareness versus dullness: his essay.', f'{r}mindful-awareness-vs-dullness/'),
        ]),
        ('The method', 'gold', [
            ('The ten stages', 'Novice, skilled, transition and adept: the map in his book, with his talks on each stage.', f'{r}ten-stages/'),
            ('Introduction to the manual', 'Concentration and mindful awareness to a minimum level, the first step towards awakening.', f'{r}meditation-manual-introduction/'),
            ('An introduction to the ten stages of samatha', 'His retreat handout on the stages.', f'{r}{UP}Cape-Ann-Retreat-for-Peace-Handout-.pdf'),
            ('Jhāna', 'The original practice of mindfulness and insight.', f'{r}{UP}jhanas-and-mindfulness-handout.pdf'),
        ]),
        ('The science of mind', 'ink', [
            ('The mind-system model', 'His model of the mind as many sub-minds, from the book and the AMA videos.', f'{r}learn/topics/mind-system/'),
            ('Consciousness', 'What consciousness is, discussed across his talks and handouts.', qlink('consciousness')),
            ('Meditation and insight', 'Three handouts and slides on how insight arises.', f'{r}{UP}Meditation-and-Insight-I.pdf'),
            ('What the Buddha thought', 'An introduction to the Buddha’s teaching, with slides.', f'{r}{UP}20130322-what-the-buddha-thought-handout.pdf'),
        ]),
        ('Going deeper', 'teal', [
            ('Insight and awakening', 'What enlightenment is and why it matters.', f'{r}{UP}What-Is-Enlightenment-Handout.pdf'),
            ('Stream entry', 'His conversation with Michael Taft on stream entry.', 'https://deconstructingyourself.com/culadasa-stream-entry.html'),
            ('The Satipaṭṭhāna Sutta', 'His commentary on the foundations of mindfulness.', f'{r}{UP}Satipatthana-Retreat-Handout-Culadasa.pdf'),
            ('Joy', 'Joy and meditation: more than just a happy feeling.', f'{r}{UP}Meditation-and-Joy-Handout.pdf'),
        ]),
        ('Daily life', 'gold', [
            ('The path to awakening in daily life', 'His handout on practice off the cushion.', f'{r}{UP}Awakening-in-Daily-Life-Handout.pdf'),
            ('Cultivating mindfulness in daily life', 'An essay from the discussion board.', f'{r}cultivating-mindfulness-in-daily-life/'),
            ('Craving', 'Recognising craving and what to do next.', f'{r}learn/topics/craving/'),
            ('Compassion', 'Compassion in his talks and answers.', qlink('compassion')),
        ]),
    ]
    sec = ''
    slug_of = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')
    for name, tone, items in tracks:
        sec += f'''<section class="section learn-sec" id="{slug_of(name)}"><div class="wrap"><div class="track-head {tone}"><h2>{name}</h2><a class="scard-back" href="#learn-sections">All sections ↑</a></div>
<div class="grid cols-4">{''.join(f'<a class="card tone-{tone}" href="{u}"><h3>{esc(t)}</h3><p>{esc(d)}</p><span class="more">{"Search" if "topics/?q=" in u else "Open"} →</span></a>' for t, d, u in items)}</div></div></section>'''
    # quick links to the five sections; the one chosen keeps a thin gold outline, as on the AMA sessions page (D, 25 Nov 2026)
    # Topics and the glossary follow the ten stages (D, 28 Nov 2026)
    _tp = json.loads((D / 'topic_pages.json').read_text())['topics'] if (D / 'topic_pages.json').exists() else []
    learn_topics = (f'<section class="section tight learn-topics"><div class="wrap"><p class="label">Topics</p><h2>The questions students bring</h2>'
                    f'<p class="measure">Each topic gathers what he said about it, with a video to start with. The list is a first draft for the teachers to confirm.</p><p class="topic-chips">'
                    + ''.join(f'<a href="{r}learn/topics/{t["slug"]}/">{esc(t["title"])}</a>' for t in sorted(_tp, key=lambda x: azkey(x['title'])))
                    + f'</p><p class="actions"><a class="btn ghost" href="{r}learn/topics/">All topics →</a><a class="btn ghost" href="{r}learn/glossary/">Glossary →</a></p></div></section>') if _tp else ''
    # The ten stages first (D, 25 Nov 2026): the foundation of the method, so they open Learn
    learn_stages = (f'<section class="section tight learn-stages"><div class="wrap"><p class="label">The foundation of the method</p>'
                    f'<h2>The ten stages</h2><p class="measure">The map of the whole path in <em>The Mind Illuminated</em>. Open a stage for a video to start with and everything he said about it.</p>'
                    f'<ol class="stages linked compact-grid">' + ''.join(f'<li><a href="{r}ten-stages/stage-{k + 1}/"><span><small>{lvl}</small>{esc(n)}</span></a></li>' for k, (n, lvl) in enumerate(STAGES))
                    + f'</ol><p class="actions"><a class="btn" href="{r}ten-stages/">The ten stages in his words →</a></p></div></section>')
    jump = ('<section class="section tight"><div class="wrap"><nav class="jump jump-main learn-jump" id="learn-sections" aria-label="Sections of the path">'
            '<p>' + ' · '.join(f'<a href="#{slug_of(n)}">{esc(n)}</a>' for n, _, _ in tracks) + '</p></nav></div></section>')
    learn_js = '''<script>
(function () {
  function mark(id) { document.querySelectorAll('.learn-jump a').forEach(function (a) { var on = a.getAttribute('href') === '#' + id; a.classList.toggle('current', on); if (on) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); }); }
  document.querySelectorAll('.learn-sec').forEach(function (s) { s.addEventListener('pointerdown', function () { mark(s.id); }); s.addEventListener('focusin', function () { mark(s.id); }); });
  function fromHash() { var id = location.hash.slice(1); if (document.getElementById(id) && document.getElementById(id).classList.contains('learn-sec')) mark(id); }
  window.addEventListener('hashchange', fromHash); fromHash();
})();
</script>'''
    body = banner('The basics, then deeper', 'Learn', 'The Mind Illuminated method: ten stages, how to progress, and the benefits in daily life.', 'ink') + learn_stages + learn_topics + jump + sec + learn_js
    page('learn/', 'Learn', body, description='Culadasa’s teaching arranged as a journey: basics, method, science of mind, going deeper, daily life.')

    # ---------------------------------------------------------------- the book
    body = banner('The book', '<em>The Mind Illuminated</em>', 'A complete meditation guide integrating Buddhist wisdom and brain science.', 'gold') + f'''
<section class="section"><div class="wrap two">
  <div class="book-cover"><img class="framed" src="{r}assets/img/the-mind-illuminated-cover.jpg" alt="Cover of The Mind Illuminated" loading="lazy">
    <p class="book-buy"><a class="btn" href="https://www.simonandschuster.com/books/The-Mind-Illuminated/John-Yates/9781501156984" rel="noopener">Buy from Publisher</a></p></div>
  <div class="measure">
    <p class="lead">Written by Culadasa (John Yates, Ph.D.) with Matthew Immergut, Ph.D. and Jeremy Graves, and first published by Dharma Treasure Press on 6 October 2015.</p>
    <p>The book sets out ten stages of meditative development, from establishing a daily practice to tranquility and equanimity, with clear instructions for each stage and an account of how the mind works drawn from both the Buddhist tradition and cognitive science.</p>
    {''.join(f'<figure class="quote book-lead-quote"><p>“{esc(q["text"])}”</p><footer>- {esc(q["by"])}</footer></figure>' for q in content['reviews'] if 'Salzberg' in q['by'])}
  </div>
</div></section>
{book_finder(r)}
<section class="section"><div class="wrap"><p class="label">The ten stages</p><h2>From the first sit to equanimity</h2>
<p class="muted">Open a stage for a video to start with and everything Culadasa said about it in his talks, AMA videos, writings and recordings, much of it after the book.</p>
<ol class="stages linked">{''.join(f'<li><a href="{r}ten-stages/stage-{k + 1}/"><span><small>{lvl}</small>{esc(n)}</span></a></li>' for k, (n, lvl) in enumerate(STAGES))}</ol>
<p class="actions" style="margin-top:22px"><a class="btn ghost" href="{r}ten-stages/">The ten stages in his words →</a></p>
<p class="muted small" style="margin-top:18px">Milestones: continuous attention to the meditation object (after stage 3); sustained exclusive focus of attention (after stage 6); effortless stability of attention (after stage 7); persistence of the mental qualities of an adept (after stage 10).</p></div></section>
<section class="section" id="reviews"><div class="wrap"><p class="label">Reviews</p><h2>What teachers and authors say</h2><div class="quotes">{''.join(f'<figure class="quote"><p>“{esc(q["text"])}”</p><footer>- {esc(q["by"])}</footer></figure>' for q in content['reviews'] if 'Salzberg' not in q['by'])}</div></div></section>
<section class="section band-panel" id="students"><div class="wrap"><p class="label">Testimonials</p><h2>What his students say about the Mind Illuminated method</h2><div class="quotes">{''.join(f'<figure class="quote"><p>“{esc(q["text"])}”</p><footer>- {esc(q["by"])}</footer></figure>' for q in content['testimonials'])}</div></div></section>'''
    if V2:
        body = body.replace('<header class="banner gold">', '<header class="banner cover">', 1)
    page('the-book/', 'The Mind Illuminated', body, description='The Mind Illuminated by Culadasa (John Yates, Ph.D.): the ten stages of meditative development.', cover_band=True)

    stage_pages(r)
    topic_pages(r)

    # ---------------------------------------------------------------- writings (old path)
    essays_all = [(t, k, x) for g, items in WRITINGS for t, k, x in items if k == 'essay']
    essay_index = ('<h2>Essays</h2><p class="muted">All five of his essays on this site, in one place. Each also appears in its group below.</p>'
                   f'<ul class="doclist">{"".join(doc_link(t, k, x, r) for t, k, x in essays_all)}</ul>')
    body = banner('Read', 'Writings', 'Twenty-six handouts and essays, free to read and download.', 'teal') + '<section class="section"><div class="wrap measure">' + scoped_search(r, 'writings', 'Search writings', 'w-q') + essay_index + ''.join(
        f'<h2>{esc(g)}</h2><ul class="doclist">{"".join(doc_link(t, k, x, r) for t, k, x in items)}</ul>' for g, items in WRITINGS) + '</div></section>'
    page('writings/', 'Writings', body, description='Culadasa’s handouts and essays, free to download.')

    # ---------------------------------------------------------------- essays (old paths)
    for slug, raw in content['essays'].items():
        title = next(t for g, items in WRITINGS for t, k, x in items if x == slug + '/')
        words = len(re.sub(r'<[^>]+>', ' ', raw).split())
        m_sub = re.search(r'<h2[^>]*>(.*?)</h2>', raw, re.S)
        sub = re.sub(r'<[^>]+>|\s+', ' ', m_sub.group(1)).strip() if m_sub else ''
        norm_t = lambda x: re.sub(r'[^a-z0-9]+', ' ', x.lower().replace('’', "'")).strip()
        if sub and (norm_t(sub) == norm_t(title) or sub == slug):
            sub = ''   # the original heading only repeated the title (or was a stray web-address slug)
        body = f'''<header class="banner panel"><div class="wrap measure"><p class="label">Essay · {max(1, round(words / 230))} min read</p><h1>{esc(title)}</h1>{f'<p class="lead essay-sub">{esc(sub)}</p>' if sub else ''}</div></header>
<article class="section"><div class="wrap measure prose">{clean_essay(raw)}</div></article>
<section class="section tight"><div class="wrap measure"><p class="label">Where next</p><p>{ESSAY_NEXT(slug, r)} · <a href="{r}writings/">All writings</a> · <a href="{r}topics/">Search the teachings</a></p></div></section>'''
        page(slug + '/', title, body, description=f'{title}: an essay by Culadasa.')

    # ---------------------------------------------------------------- audio (old path)
    # Every recording as a list of titles by year (D, 25 Nov 2026), from the public SoundCloud feed (tools/build_audio.py).
    audio_all = json.loads((D / 'audio.json').read_text())['recordings']
    hmap = handout_map()
    def audio_body(a_):
        parts = []
        for line in a_['text'].splitlines():
            line = re.sub(r'[\u200b\u200c\u200d\ufeff\u00a0]', ' ', line)   # invisible characters some descriptions carry
            m_ = re.match(r'^\s*\(?((?:\d{1,2}:)?\d{1,2}:\d{2})\)?\s*[-–—:]?\s*(.*)$', line)
            if m_ and a_['url']:
                parts.append(f'<p class="tline">{play(a_["url"] + "#t=" + m_.group(1), m_.group(1))} {esc(m_.group(2))}</p>')
            elif line.strip() and not line.strip().lower().startswith('timestamps'):
                parts.append(f'<p>{esc(line.strip())}</p>')
        hs = [(u, hmap[u]) for u in a_.get('links', []) if u in hmap]
        if hs:
            parts.append('<p class="small"><strong>Handouts:</strong> ' + ' · '.join(
                f'<a href="{r}../{esc(p_)}">{esc(p_.rsplit("/", 1)[-1].replace("-", " ").replace(".pdf", ""))}</a>' for u, p_ in hs) + '</p>')
        parts.append(f'<p class="rr-open"><a href="{esc(a_["url"])}" rel="noopener">Listen on SoundCloud →</a></p>')
        return ''.join(parts)
    def dur(d):
        d = re.sub(r'^00:', '', d or '')
        return re.sub(r'^0(?=\d)', '', d)
    # grouped by series, read from the titles (the feed's dates are upload dates, so years would mislead)
    def a_series(t):
        t = t.replace(' - Culadasa', '').strip()
        if re.search(r'patreon|q ?& ?a\b|q and a', t, re.I):
            return 'AMA and Q&A recordings'
        if re.match(r'TCMC Thursday', t):
            return 'TCMC Thursday evenings'
        t = re.sub(r'[,:\-–]?\s*(Part|Pt\.?|Session|Day|Talk)\s*,?\s*\d+.*$', '', t, flags=re.I).strip(' ,-–:')
        t = re.sub(r'^(Dharma Talk|Guided Metta|Guided Meditation|Meditation|Q&A),\s*', '', t)
        return t
    by_s = {}
    for a_ in sorted(audio_all, key=lambda x: (x['date'], x['title']), reverse=True):
        by_s.setdefault(a_series(a_['title']), []).append(a_)
    singles = [a_ for k, v in by_s.items() if len(v) == 1 for a_ in v]
    series_ = sorted(((k, v) for k, v in by_s.items() if len(v) > 1), key=lambda kv: (kv[0] != 'AMA and Q&A recordings', -len(kv[1]), kv[0]))
    def a_row(a_):
        return row(a_['title'].replace(' - Culadasa', ''), ' · '.join(x for x in (a_['date'], dur(a_['duration'])) if x), audio_body(a_))
    def natural(t):   # Part 2 before Part 10
        return [int(x) if x.isdigit() else x.lower() for x in re.split(r'(\d+)', t)]
    audio_groups = [(k, [a_row(a_) for a_ in sorted(v, key=lambda x: natural(x['title']))] if k != 'AMA and Q&A recordings' else [a_row(a_) for a_ in v]) for k, v in series_]
    if singles:
        audio_groups.append(('Single talks and meditations', [a_row(a_) for a_ in sorted(singles, key=lambda x: natural(x['title']))]))
    PL = [('Guided Meditations', '282960661'), ('Questions and Answers', '283520935'), ('Teaching Retreats', '296077102'),
          ('Intensive Meditation Retreats', '283729524'), ('Patreon Q&As', '967729615')]
    body = banner('Listen', 'Audio', 'Over 400 recordings: guided meditations, retreats, and questions and answers.', 'ink',
                  '<p><a class="btn ghost light" href="https://soundcloud.com/culadasa" rel="noopener">Open SoundCloud</a></p>') + '<section class="section tight"><div class="wrap">' + scoped_search(r, 'audio', 'Search recordings', 'a-q') + '</div></section><section class="section"><div class="wrap"><div class="grid">' + ''.join(
        f'<section id="{re.sub(r"[^a-z]+", "-", t.lower()).strip("-")}"><h2 style="font-size:24px">{t}</h2>{sc_player("playlists", i, 420)}</section>' for t, i in PL) + f'</div></div></section><section class="section"><div class="wrap"><h2>Every recording</h2><p class="muted">All {len(audio_all)} recordings, grouped by retreat or series. Open one for its notes, the handouts that go with it, and the moments in it.</p><p class="rr-hint">Select a title to open it.</p>{row_groups(audio_groups)}</div></section>'
    page('audio/', 'Audio', body, description='Culadasa’s guided meditations, retreats and AMA recordings on SoundCloud.')

    # ---------------------------------------------------------------- videos (old path)
    # Every video as a list of titles (D, 25 Nov 2026): the talks, then the AMA sessions by year. The list covers all the
    # videos on his channel that have transcripts, not only the ones that were on the old Videos page.
    _trv = {v['id']: v for v in json.loads((D / 'transcripts.json').read_text())['videos']} if (D / 'transcripts.json').exists() else {}
    ama_ids = {s_['video']: s_ for s_ in qna if s_.get('video')}
    all_vids = list(dict.fromkeys([v['id'] for v in videos] + list(_trv)))
    def vtitle(i):
        t_ = vid_by_id[i]['title'] if i in vid_by_id else _trv[i]['title']
        t_ = t_.replace('┬á', ' ').replace('\u00a0', ' ')   # a non-breaking space garbled on download
        return re.sub(r'\s*-\s*RE-UPLOAD.*$', '', t_).strip()
    # One Videos room (D, 28 Nov 2026, after looking at how TED, Attia, Lex Fridman, Huberman and Dharma Seed do it):
    # every video in one list, AMA videos as a series in it, filters at the top; each video has its own page.
    def vlen(i):
        mk = (_trv.get(i) or {}).get('marks') or []
        s_ = mk[-1][1] if mk else 0
        if s_ >= 3600:
            return f'{s_ // 3600} h' + (f' {s_ % 3600 // 60} min' if s_ % 3600 // 60 else '')
        return f'{max(1, round(s_ / 60))} min' if s_ else ''
    def nice_date(d_):
        try:
            y_, m_, dd_ = map(int, d_.split('-')); return f'{dd_} {datetime.date(y_, m_, 1).strftime("%B")} {y_}'
        except Exception:
            return d_
    held = {s_['video']: (k, s_['title']) for k, s_ in enumerate(qindex['sessions']) if s_.get('video')}   # Alex's index runs oldest first
    def held_label(i):
        t_ = held.get(i, (0, ''))[1]
        m_ = re.fullmatch(r'(19|20)\d\d(\d\d)(\d\d)', t_.strip())   # e.g. Alex's "20190517"
        return datetime.date(2000, int(m_.group(2)), int(m_.group(3))).strftime('%B ') + str(int(m_.group(3))) + ', ' + t_[:4] if m_ else t_
    def vcard(i):
        when = held_label(i) if i in held else nice_date((_trv.get(i) or {}).get('date', ''))
        meta = ' · '.join(x for x in (when, vlen(i), f"{len(ama_ids[i]['items'])} questions" if i in ama_ids else '') if x)
        return (f'<li><a class="vcard" href="{r}videos/{i}/"><img src="https://i.ytimg.com/vi/{i}/mqdefault.jpg" alt="" loading="lazy" width="320" height="180">'
                f'<span class="vc-title">{esc(vtitle(i))}</span><span class="vc-meta">{esc(meta)}</span></a></li>')
    talk_ids = sorted([i for i in all_vids if i not in ama_ids], key=lambda i: (_trv.get(i) or {}).get('date', ''), reverse=True)
    def ama_year(i):   # the year the session was held (from its title), not the year it was uploaded
        m_ = re.search(r'(19|20)\d\d', ama_ids[i]['title'])
        return m_.group(0) if m_ else (_trv.get(i) or {}).get('date', '')[:4]
    ama_years = sorted({ama_year(i) for i in ama_ids}, reverse=True)
    vsec = f'<section class="vgroup" data-kind="talk" id="talks"><h2>Talks and discussions <span class="rg-count">{len(talk_ids)}</span></h2><ul class="vcards">{"".join(vcard(i) for i in talk_ids)}</ul></section>'
    ama_intro = (f'<p class="muted vgroup-intro" data-kind="ama">His monthly ask-me-anything sessions on Patreon, 2017–2021. Each video’s page lists the questions asked, '
                 f'from the <a href="{esc(qindex["source"])}" rel="noopener">Culadasa Q&amp;A Index</a> by {esc(qindex["author"])}, with the full transcript. '
                 'Years: ' + ' · '.join(f'<a href="#ama-{y}">{y}</a>' for y in ama_years) + '</p>'
                 + '<details class="vgroup-intro alex-intro" data-kind="ama"><summary>About the Culadasa Q&amp;A Index, by Alex</summary>'
                 + ''.join(f'<p>{it["html"]}</p>' for it in qindex['intro'] if it.get('kind') == 'p') + '</details>')
    for y in ama_years:
        ids = sorted([i for i in ama_ids if ama_year(i) == y], key=lambda i: held.get(i, (0, ''))[0], reverse=True)   # newest session first
        vsec += (ama_intro if y == ama_years[0] else '') + f'<section class="vgroup" data-kind="ama" id="ama-{y}"><h2>AMA videos {y} <span class="rg-count">{len(ids)}</span></h2><ul class="vcards">{"".join(vcard(i) for i in ids)}</ul></section>'
    chips = ''.join(f'<button type="button" class="vchip" data-show="{k}" aria-pressed="{str(k == "all").lower()}">{esc(t)}</button>'
                    for k, t in (('all', f'All {len(all_vids)}'), ('talk', f'Talks {len(talk_ids)}'), ('ama', f'AMA videos {len(ama_ids)}')))
    body = banner('Watch', 'Videos', 'His talks and AMA (ask me anything) videos, searchable word for word.', 'teal',
                  '<p><a class="btn ghost light" href="https://www.youtube.com/@Culadasa" rel="noopener">Open YouTube</a></p>') + f'''
<section class="section tight"><div class="wrap">{scoped_search(r, ('video', 'ama'), 'Search videos', 'v-q')}</div></section>
<section class="section"><div class="wrap">
<div class="vchips" role="group" aria-label="Show">{chips}</div>
<p class="muted small">Open a video for its page: the player, the questions asked (AMA videos) and the full transcript, where every time plays from that moment.</p>
{vsec}
</div></section>
<script>
/* the filter at the top of Videos: all, talks or AMA videos; ?show=ama opens on the AMA videos (D, 28 Nov 2026) */
(function () {{
  var chips = document.querySelectorAll('.vchip');
  function show(k) {{
    chips.forEach(function (c) {{ c.setAttribute('aria-pressed', c.getAttribute('data-show') === k ? 'true' : 'false'); }});
    try {{ history.replaceState(null, '', k === 'all' ? location.pathname : '?show=' + k + (k === 'ama' ? location.hash : '')); }} catch (e) {{}}
    document.querySelectorAll('.vgroup, .vgroup-intro').forEach(function (g) {{ g.hidden = k !== 'all' && g.getAttribute('data-kind') !== k; }});
  }}
  chips.forEach(function (c) {{ c.addEventListener('click', function () {{ show(c.getAttribute('data-show')); }}); }});
  function fromAddress() {{ var q = new URLSearchParams(location.search).get('show'); show(q === 'ama' || q === 'talk' ? q : (/^#ama-/.test(location.hash) ? 'ama' : 'all')); }}
  fromAddress(); window.addEventListener('popstate', fromAddress);
  if (/^#ama-/.test(location.hash)) show('ama');
  window.addEventListener('hashchange', function () {{ if (/^#ama-/.test(location.hash)) {{ show('ama'); var t = document.querySelector(location.hash); if (t) t.scrollIntoView(); }} }});
}})();
</script>'''
    page('videos/', 'Videos', body, description='Talks and AMA (ask me anything) videos by Culadasa, each with its questions and full transcript.')

    # ---------------------------------------------------------------- Q&A archive (old path: online-meetings)
    # The whole of Alex's Culadasa Q&A Index, in the site's design (D, 25 Nov 2026): his introduction, every question
    # in full, his quotes from the answers and his keywords, each linked to its moment in the video.
    def short_time(t):
        t = re.sub(r'^00:', '', t.strip())
        return re.sub(r'^0(?=\d)', '', t)
    def q_item(q):
        def quote_html(qq):
            stamp = f'<p class="qtime"><a href="{esc(qq["url"])}" rel="noopener" aria-label="Play from {esc(short_time(qq["time"]))} on YouTube (opens a new tab)">{esc(short_time(qq["time"]))}</a></p>' if qq['url'] else ''
            return '<blockquote class="qquote">' + ''.join(f'<p>{t}</p>' for t in qq['text']) + stamp + '</blockquote>'
        quotes = ''.join(quote_html(qq) for qq in q['quotes'])
        kws = ''
        if q['keywords']:
            kws = '<p class="kw"><span class="kw-label">Keywords</span> ' + ', '.join(
                (f'<a href="{esc(k["url"])}" rel="noopener">{esc(k["text"])}</a>' if k['url'] else esc(k['text'])) for k in q['keywords']) + '</p>'
        text = ''.join(f'<p>{t}</p>' for t in q['question'])
        return f'<li><a class="t" href="{esc(q["url"])}" rel="noopener" aria-label="Play from {esc(short_time(q["time"]))} on YouTube (opens a new tab)">{esc(short_time(q["time"]))}</a><div class="qbody">{text}{quotes}{kws}</div></li>'
    def session_label(t):
        m = re.fullmatch(r'(19|20)\d\d(\d\d)(\d\d)', t.strip())   # e.g. Alex's "20190517"
        if m:
            return datetime.date(2000, int(m.group(2)), int(m.group(3))).strftime('%B ') + str(int(m.group(3)))
        return re.sub(r",? ?(19|20)[0-9][0-9]", "", t).strip() or t
    isess = list(reversed(qindex['sessions']))
    by_year = {}
    for s_ in isess:
        y = re.search(r'(19|20)\d\d', s_['title'])
        by_year.setdefault(y.group(0) if y else 'Other', []).append(s_)
    n_patreon = sum(1 for s_ in isess if s_['video'] in vid_by_id and 'patreon' in vid_by_id[s_['video']]['title'].lower())
    n_q = sum(len(s_['questions']) for s_ in isess)
    sess = ''
    for s_ in isess:
        v = vid_by_id.get(s_['video'])
        tile = video_tile(v, r) if v else f'<p><a href="{esc(s_["url"])}" rel="noopener">Watch on YouTube</a></p>'
        first_q = re.sub(r'<[^>]+>', '', s_['questions'][0]['question'][0]) if s_['questions'] and s_['questions'][0]['question'] else ''
        n_ = len(s_['questions'])
        sess += f'''<article class="scard" id="s-{esc(s_['video'])}"><div class="scard-media">{tile}</div>
<div class="scard-main"><div class="scard-top"><h3><button type="button" class="scard-title" aria-expanded="false">{esc(s_['title'])}</button></h3><a class="scard-back" href="#sessions">Return to AMA list</a></div>
<p class="scard-first">{esc(first_q[:220])}{'…' if len(first_q) > 220 else ''}</p>
<details class="scard-q"><summary><span class="when-closed">Open all {n_} question{'s' if n_ != 1 else ''}</span><span class="when-open">Close all {n_} question{'s' if n_ != 1 else ''}</span></summary><ol class="qlist">{''.join(q_item(q) for q in s_['questions'])}</ol><p class="scard-close"><button type="button" class="close-q">Close all {n_} question{'s' if n_ != 1 else ''}</button></p></details></div></article>'''
    intro_html = ''.join((f'<h3>{x["html"]}</h3>' if x['html'] in ('Some basic notes on how to use this document', 'Contributing') else f'<p>{x["html"]}</p>') for x in qindex['intro'])
    om_intro = re.sub(r'\s*,\s*a crowdsourcing platform', '', content['online_meetings_intro']).replace('Patreon .', 'Patreon.')   # D, 25 Nov 2026
    body = banner('Ask me anything', 'AMA videos', 'His monthly ask-me-anything videos, 2017–2021: every question, linked to his answer.', 'teal') + f'''
<section class="section tight"><div class="wrap">{scoped_search(r, 'ama', 'Search questions', 'qa-q')}</div></section>   
<section class="section"><div class="wrap">
<nav class="jump jump-main" id="sessions" aria-label="AMA videos by year"><h2>All {len(isess)} Patreon AMA videos organized by year</h2><p class="muted">Choose one to go to it. This page remembers the last video you opened on this device.</p>{''.join(f'<p><strong>{y}</strong> {" · ".join(f'<a href="#s-{esc(x["video"])}">{esc(session_label(x["title"]))}</a>' for x in ss)}</p>' for y, ss in by_year.items())}</nav>
<p class="tinfo-open"><button type="button" class="linklike" id="tinfo-btn" aria-haspopup="dialog" aria-controls="tinfo">About this index</button></p>
<dialog id="tinfo" class="tinfo" aria-labelledby="tinfo-h">
  <div class="tinfo-head"><h2 id="tinfo-h">About this index</h2><button type="button" class="tinfo-close" id="tinfo-close" aria-label="Close">×</button></div>
  <div class="prose small-prose">
    <p class="small muted">The questions, keywords and quotes on this page come from the <a href="{esc(qindex["source"])}" rel="noopener">Culadasa Q&amp;A Index</a>, shown here in full, with spelling mistakes corrected. Each time links to the moment the question is asked. Corrections go to the original index. Its introduction follows.</p>
    {intro_html}
  </div>
</dialog>
<script>
(function () {{
  var d = document.getElementById('tinfo'), b = document.getElementById('tinfo-btn'), c = document.getElementById('tinfo-close');
  if (!d || !b) return;
  b.addEventListener('click', function () {{ if (d.showModal) d.showModal(); else d.setAttribute('open', ''); }});
  c.addEventListener('click', function () {{ d.close ? d.close() : d.removeAttribute('open'); b.focus(); }});
  d.addEventListener('click', function (e) {{ if (e.target === d) {{ d.close(); }} }});
}})();
</script>
</div></section>
<section class="section band-panel"><div class="wrap"><h2>Audio of the meetings</h2>{sc_player('playlists', '967729615', 450, False)}</div></section>
<section class="section" id="all-sessions"><div class="wrap"><h2>The videos</h2>
<div class="scards">{sess}</div>
<script>
/* a year link or the page address opens its session; an opened card widens to the full row */
(function () {{
  function sync(card) {{ var d = card.querySelector('details'); card.classList.toggle('open', !!(d && d.open)); }}
  document.querySelectorAll('.scard details').forEach(function (d) {{ d.addEventListener('toggle', function () {{ sync(d.closest('.scard')); }}); }});
  /* clicking the session name opens or closes its questions, like the prompt below it (D, 25 Nov 2026) */
  document.querySelectorAll('.scard .scard-title').forEach(function (t) {{ t.addEventListener('click', function () {{
    var c = t.closest('.scard'), d = c.querySelector('details'); d.open = !d.open; sync(c); activate(c); }}); }});
  document.querySelectorAll('.scard details').forEach(function (d) {{ d.addEventListener('toggle', function () {{
    var t = d.closest('.scard').querySelector('.scard-title'); if (t) t.setAttribute('aria-expanded', d.open ? 'true' : 'false'); }}); }});
  document.querySelectorAll('.scard .close-q').forEach(function (b) {{ b.addEventListener('click', function () {{
    var d = b.closest('details'), c = b.closest('.scard'); d.open = false; sync(c); c.scrollIntoView({{ block: 'start' }}); d.querySelector('summary').focus({{ preventScroll: true }}); }}); }});
  /* the session being looked at is marked active: thin gold line, slightly lighter ground (D, 25 Nov 2026) */
  function activate(c) {{
    document.querySelectorAll('.scard.active').forEach(function (x) {{ if (x !== c) x.classList.remove('active'); }}); if (c) c.classList.add('active');
    /* the same session's link in the list at the top keeps a thin gold outline, so "Return to AMA list" shows where you were */
    document.querySelectorAll('.jump-main a.current').forEach(function (a) {{ a.classList.remove('current'); a.removeAttribute('aria-current'); }});
    var l = c && document.querySelector('.jump-main a[href="#' + c.id + '"]'); if (l) {{ l.classList.add('current'); l.setAttribute('aria-current', 'true'); }}
  }}
  document.querySelectorAll('.scard').forEach(function (c) {{
    c.addEventListener('pointerdown', function () {{ activate(c); }});
    c.addEventListener('focusin', function () {{ activate(c); }});
    var d = c.querySelector('details'); if (d) d.addEventListener('toggle', function () {{ if (d.open) activate(c); }});
  }});
  function openFromHash() {{ var c = location.hash && document.getElementById(location.hash.slice(1)); if (c && c.classList.contains('scard')) {{ var d = c.querySelector('details'); d.open = true; sync(c); activate(c); c.scrollIntoView({{ block: 'start' }}); return true; }} return false; }}
  /* this device remembers the last session read, so it is still marked on a later visit (localStorage; nothing is sent anywhere) */
  var KEY = 'culadasa-last-ama';
  document.addEventListener('click', function () {{ var a = document.querySelector('.scard.active'); try {{ if (a) localStorage.setItem(KEY, a.id); }} catch (e) {{}} }});
  if (!(location.hash && document.getElementById(location.hash.slice(1)))) {{ var last = null; try {{ last = localStorage.getItem(KEY); }} catch (e) {{}} var lc = last && document.getElementById(last); if (lc && lc.classList.contains('scard')) activate(lc); }}
  window.addEventListener('hashchange', openFromHash); openFromHash();
}})();
</script>
</div></section>'''
    # The AMA page's old address keeps working (D, 28 Nov 2026): a session link (#s-<video id>, or Alex's own anchors)
    # goes to that video's page; anything else to the AMA videos in Videos.
    anchors = {s_['anchor']: s_['video'] for s_ in isess if s_.get('video') and s_.get('anchor')}
    redirect = ('<script>(function(){var h=location.hash.slice(1),a=' + json.dumps(anchors) + ',ids=Object.values(a),m=/^s-([\\w-]{11})$/.exec(h),v=m&&ids.indexOf(m[1])>=0?m[1]:a[h];'
                'location.replace(v?"../videos/"+v+"/":"../videos/?show=ama");})();</script>\n'
                '<meta http-equiv="refresh" content="1; url=../videos/?show=ama">\n<link rel="canonical" href="../videos/?show=ama">\n')
    page('online-meetings/', 'AMA videos', '<section class="section"><div class="wrap"><p>The AMA videos are now in <a href="../videos/?show=ama">Videos</a>, each on its own page with its questions and transcript.</p></div></section>', extra_head=redirect)

    # ---------------------------------------------------------------- a page for every video (D, 28 Nov 2026)
    # The player, then (for AMA videos) the questions asked, from Alex's index, then the full transcript with a find box;
    # every time on the page plays the video from that moment here. ?t=<seconds> opens the page at that moment.
    sess_by_vid = {s_['video']: s_ for s_ in isess if s_.get('video')}
    stage_data = json.loads((D / 'stages.json').read_text())['stages'] if (D / 'stages.json').exists() else []
    def add_seek(html_, vid):
        def f(m):
            return f'{m.group(0)} data-seek="{yt_secs(m.group(1))}"'
        return re.sub(r'href="https://www\.youtube\.com/watch\?v=' + re.escape(vid) + r'(?:&amp;|&)t=([0-9hms]+)"', f, html_)
    for i in all_vids:
        tv = _trv.get(i)
        rv = '../../'
        is_ama = i in ama_ids
        label = f'<a href="{rv}videos/{"?show=ama" if is_ama else ""}">{"AMA video" if is_ama else "Talk"}</a>' + (f' · {ama_year(i)}' if is_ama else '')
        facts = ' · '.join(x for x in ((f'AMA session: {held_label(i)}' if is_ama and i in held else nice_date((tv or {}).get('date', ''))), vlen(i)) if x)
        stages_here = []
        for st in stage_data:
            for k in ('videos', 'ama'):
                for x in st[k]:
                    if x['id'] == i:
                        stages_here.append((st['n'], x['n'], x['moments'][0][0] if x.get('moments') else 0))
        st_html = ('<p class="small">On the ten stages pages: ' + ' · '.join(f'<a href="{rv}ten-stages/stage-{n}/">Stage {NUMW[n - 1]}</a> ({c})' for n, c, _ in stages_here) + '</p>') if stages_here else ''
        qs = ''
        if is_ama and i in sess_by_vid:
            sq = sess_by_vid[i]
            qs = (f'<section class="vblock" id="questions"><h2>Questions in this video <span class="rg-count">{len(sq["questions"])}</span></h2>'
                  f'<p class="small muted">From the <a href="{esc(qindex["source"])}" rel="noopener">Culadasa Q&amp;A Index</a> by {esc(qindex["author"])}: each time plays his answer.</p>'
                  f'<ol class="qlist">{"".join(q_item(q) for q in sq["questions"])}</ol></section>').replace(' on YouTube (opens a new tab)"', '"')
        paras = ''
        if tv:
            text, marks = tv['text'], tv['marks']
            starts = []
            for pos, sec in marks:
                if not starts or sec - starts[-1][1] >= 60:
                    starts.append((pos, sec))
            for k, (pos, sec) in enumerate(starts):
                end = starts[k + 1][0] if k + 1 < len(starts) else len(text)
                paras += (f'<p class="tp" id="t{sec}"><a class="play" href="https://www.youtube.com/watch?v={i}&amp;t={sec}s" '
                          f'aria-label="Play from {hms_(sec)}">{hms_(sec)}</a> <span class="tt">{esc(html.unescape(text[pos:end]).strip())}</span></p>')
        tr = (f'<section class="vblock" id="transcript"><h2>Transcript</h2>'
              f'<p class="small muted">YouTube’s automatic captions, with the Pāli terms it mishears corrected, so expect mistakes. Each time plays the video from that moment.</p>'
              f'<form class="tfind" role="search" onsubmit="return false"><label class="sr" for="tf">Find in this transcript</label><input id="tf" type="search" placeholder="Find in this transcript" autocomplete="off"><span class="tf-status small muted" role="status"></span></form>'
              f'<div class="transcript">{paras}</div></section>') if paras else ''
        v = vid_by_id.get(i) or {'id': i, 'title': vtitle(i)}
        body = banner(label, esc(vtitle(i)), '', 'teal') + f'''
<section class="section vpage"><div class="wrap vgrid" data-video="{i}">
  <div class="vleft"><div class="vplayer">{re.sub(r'<h3>.*?</h3>', '', video_tile(v, rv), count=1, flags=re.S)}</div>
    <div class="vmeta"><p class="small vfacts">{esc(facts)} · <a href="https://www.youtube.com/watch?v={i}" rel="noopener">Open on YouTube ↗</a>{' · <a href="#transcript">Transcript ↓</a>' if tv else ''}</p>{st_html}
    <p class="small vback"><a href="{rv}videos/{"?show=ama" if is_ama else "?show=talk"}">← All {"AMA videos" if is_ama else "talks"}</a></p></div></div>
  <div class="vtext">{qs}{tr}</div>
</div></section>'''
        page(f'videos/{i}/', vtitle(i), add_seek(body, i), description=f'{vtitle(i)}: Culadasa on video, with {"the questions asked and " if is_ama else ""}the full transcript.')

    # ---------------------------------------------------------------- topics
    SEARCH_COUNTS = f'Search over a million words: every word of about {round(N_VIDEOS, -1)} videos, {N_WRIT} retreat handouts and essays, {sum(len(s["items"]) for s in qna)} AMA questions, and the titles and descriptions of {N_AUDIO_TXT} audio recordings. Results are ranked by how often they mention what you search for.'
    body = banner('Every teaching, searchable', 'Search', 'Every word of his talks, writings, AMA answers and recording notes, in one search.', 'ink') + f'''
<section class="section"><div class="wrap">
  <div class="search-panel">
  <form class="search" id="topic-form" role="search"><label class="sr" for="q">Search the teachings</label><input id="q" name="q" type="search" placeholder="Try: dullness, jhāna" autocomplete="off"><button class="btn" type="submit">Search</button></form>
  <div class="filters" id="filters" aria-label="Filter by kind"></div>
  </div>
  <p class="status" id="status" role="status">Loading the teachings…</p>
  <div class="results" id="results"></div>
  <div class="cloud" id="cloud" aria-label="Most frequent words across the teachings"></div>   <!-- below the results, so a search shows its results first (D, 25 Nov 2026) -->
  <p class="small muted">{SEARCH_COUNTS}</p>
  <p class="small muted">Sources: his handouts and essays, the About page, the Culadasa Q&amp;A Index (the questions from his AMA videos), the audio recordings&rsquo; titles and descriptions, and the transcripts of 99 videos. The transcripts are YouTube&rsquo;s automatic captions with the Pāli terms corrected, so expect some mistakes; each result opens the video at the moment he says it. You can also type a whole question. Spellings with and without accents match each other, and so do the Pāli and Sanskrit forms of a word (jhāna and dhyāna, mettā and maitrī). Common English words are left out of the word cloud.</p>
</div></section>'''
    # pages of the site a search can point to before the results (D, 28 Nov 2026)
    _site = [('Start here', 'start-here/', ['start', 'start here', 'beginner', 'beginners', 'begin', 'how do i start', 'how to start', 'new to meditation', 'first sit']),
             ('Guided meditations (Audio)', 'audio/#guided-meditations', ['guided meditation', 'guided meditations', 'guided', 'meditation recording']),
             ('Find a teacher', 'teachers/', ['teacher', 'teachers', 'find a teacher', 'certified teacher', 'instructor']),
             ('The ten stages', 'ten-stages/', ['stages', 'ten stages', 'the map', 'map']),
             ('The Book: The Mind Illuminated', 'the-book/', ['book', 'the mind illuminated', 'tmi', 'buy', 'buy the book']),
             ('Topics', 'learn/topics/', ['topic', 'topics']),
             ('Glossary', 'learn/glossary/', ['glossary', 'pali', 'pali terms', 'definition', 'meaning']),
             ('Videos', 'videos/', ['video', 'videos', 'youtube', 'ama', 'ask me anything']),
             ('Conversations', 'conversations/', ['podcast', 'podcasts', 'interview', 'interviews']),
             ('Writings', 'writings/', ['handout', 'handouts', 'essay', 'essays', 'pdf']),
             ('About Culadasa', 'lineage/', ['about', 'biography', 'lineage', 'obituary', 'john yates', 'culadasa', 'his life'])]
    for t in teachers['teachers']:
        if t.get('profile') != 'sample' and not t.get('hidden'):
            _site.append((f"{t['name']} (teacher)", f"teachers/{t['slug']}/", [t['name']] + [w for w in re.sub(r'\(.*?\)|".*?"', '', t['name']).split() if len(w) > 3]))
    _site_js = [{'t': t, 'u': u, 'w': sorted({unicodedata.normalize('NFD', w.lower()).encode('ascii', 'ignore').decode() for w in ws})} for t, u, ws in _site]
    _tlinks = {}
    for t in (json.loads((D / 'topic_pages.json').read_text())['topics'] if (D / 'topic_pages.json').exists() else []):
        for w in [t['title']] + t['words']:
            _tlinks[unicodedata.normalize('NFD', w.lower()).encode('ascii', 'ignore').decode().replace('-', ' ')] = [t['slug'], t['title']]
    _titles = {t['slug']: t['title'] for t in (json.loads((D / 'topic_pages.json').read_text())['topics'] if (D / 'topic_pages.json').exists() else [])}
    for term, also, _m, slug in GLOSSARY:   # the glossary's words lead to their topic too
        if slug in _titles:
            for w in [term] + [a.strip() for a in also.split(',') if a.strip()]:
                _tlinks.setdefault(unicodedata.normalize('NFD', w.lower()).encode('ascii', 'ignore').decode().replace('-', ' '), [slug, _titles[slug]])
    page('topics/', 'Search', body, description='Search every Culadasa teaching by topic, ranked by mentions, with a word cloud.',
         extra_js=f'<script>window.CULADASA_TOPICS={json.dumps(_tlinks, ensure_ascii=False)};window.CULADASA_SITE={json.dumps(_site_js, ensure_ascii=False)};</script>\n<script src="{r}assets/topics.js" defer></script>\n')

    # ---------------------------------------------------------------- conversations (blog)
    def convo_img(c):
        if not c.get('image'):
            return '<div class="cimg cimg-none" aria-hidden="true"></div>'
        src = c['image'] if c['image'].startswith('http') else r + c['image']
        credit = f'<figcaption>{esc(c["image_credit"])}</figcaption>' if c.get('image_credit') else ''
        return f'<figure class="cimg"><a href="{esc(c["url"])}" rel="noopener" tabindex="-1"><img src="{esc(src)}" alt="{esc(c.get("image_alt", ""))}" loading="lazy"></a>{credit}</figure>'
    items = ''.join(f'''<article class="convo">{convo_img(c)}<div><div class="when">{esc(c['date_label'])}</div>
<h3><a href="{esc(c['url'])}" rel="noopener">{esc(c['title'])}</a></h3><p class="show">{esc(c['show'])}{f" · with {esc(c['host'])}" if c.get('host') else ''}</p>
<p>{esc(c['description'])}</p><p class="small">{' · '.join(f'<a href="{esc(u)}" rel="noopener">{esc(l)}</a>' for l, u in c.get('links', []))}</p></div></article>''' for c in convos['items'])
    body = banner('In conversation', 'Conversations', 'Interviews and podcasts with Culadasa from across the web.', 'gold') + f'<section class="section"><div class="wrap measure"><h2 class="sr">Interviews and podcasts</h2>{items}{f'<p class="small muted" style="margin-top:24px">{esc(convos["note"])}</p>' if convos["note"] else ''}</div></section>'
    page('conversations/', 'Conversations', body, description='Interviews and podcasts with Culadasa from across the web.')

    # ---------------------------------------------------------------- lineage (was About; D, 24 Nov 2026)
    # Order: the lineage first, then his wishes, then the obituary.  Text is the live site's, unchanged;
    # the lineage chain repeats only what that text says.  Photos: Namgyal Rinpoche from wangapeka.org,
    # Kema Ananda from arrowriver.ca (top photo), the 16th Karmapa with Namgyal Rinpoche from wangapeka.org;
    # all chosen by D; permission still to confirm.
    about = content['about_html']
    def clean(h):
        h = re.sub(r'<a href="https://culadasa\.com/wp-content[^"]*"><img[^>]*/></a>', '', h)
        h = re.sub(r'\s(style|class|id|title)="[^"]*"', '', h)
        h = re.sub(r'<b>\s*</b>', '', h)
        h = re.sub(r'<p>\s*(&nbsp;|\xa0)?\s*</p>', '', h)
        return re.sub(r'<p><strong>([^<]{3,60})</strong></p>', r'<h2>\1</h2>', h)
    i_wish = about.index("<p><strong>Culadasa's wishes")
    i_obit = about.index('<p><strong>Obituary</strong></p>')
    i_line = about.index('<h2>The Buddhist Lineage')
    wishes, obit, lineage = clean(about[i_wish:i_obit]), clean(about[i_obit:i_line]), clean(about[i_line:])
    # D moved this paragraph from the biography to sit under the lineage (24 Nov 2026), so it appears once
    obit, n_moved = re.subn(r'<p>For many years, Culadasa taught physiology and neuroscience.*?</p>', '', obit, count=1, flags=re.S)
    assert n_moved == 1, 'paragraph to move not found in the obituary text'
    lineage = re.sub(r'<h2>The Buddhist Lineage of Upasaka Culadasa</h2>', '', lineage).strip()
    if not lineage.startswith('<p'):
        lineage = f'<p>{lineage}</p>'
    # second paragraph supplied by D, 24 Nov 2026 (text as given)
    lineage += ('<p>For many years, Culadasa taught physiology and neuroscience and worked at the forefront of the new fields of '
                'complementary healthcare education, physical medicine, and therapeutic massage. His unique lineage allows Culadasa '
                'to provide his students with a broad and in-depth perspective on the Buddha Dharma. He combines the original '
                'teachings of the Buddha with an emerging, scientific understanding of the mind to give students a rich and rare '
                'opportunity for rapid progress and profound insight.</p>')
    chain = [
        ('karmapa-namgyal-rinpoche.jpg', 'His Holiness the 16th Gyalwa Karmapa', 'with Namgyal Rinpoche', 'Whose lineage is traced to the Buddha', 'Photo: wangapeka.org', 319, 252),
        ('namgyal-rinpoche.jpg', 'Namgyal Rinpoche', 'Ananda Bodhi', 'Ordained by His Holiness the 16th Gyalwa Karmapa', 'Photo: wangapeka.org', 300, 400),
        ('kema-ananda.jpg', 'Upasaka Kema Ananda', '', 'Ordained by Namgyal Rinpoche', 'Photo: arrowriver.ca', 300, 400),
        ('culadasa-robes.jpg', 'Upasaka Culadasa', 'John Yates, Ph.D.', 'Ordained by Upasaka Kema Ananda', '', 300, 400),
    ]
    chain_html = ''.join(f'''<li><figure><img src="{r}assets/img/{img}" alt="{esc(name + (' ' + alt if alt.startswith('with ') else ''))}" width="{w}" height="{h}" loading="lazy">
<figcaption><strong>{esc(name)}</strong>{f'<em>{esc(alt)}</em>' if alt else ''}<span>{esc(note)}</span>{f'<small>{esc(credit)}</small>' if credit else ''}</figcaption></figure></li>''' for img, name, alt, note, credit, w, h in chain)
    body = banner('About', 'Upasaka Culadasa', 'Upasaka Culadasa’s Buddhist lineage, scientific career, wishes for his teachings and life.', 'gold') + f'''
<section class="section" id="lineage"><div class="wrap">
<div class="two"><div><img class="framed" src="{r}assets/img/culadasa-portrait.jpg" alt="Culadasa, John Yates" width="400" height="602"></div>
<div><h2>The Buddhist lineage of Upasaka Culadasa</h2>
<div class="prose measure">{lineage}</div></div></div>
</div></section>
<section class="section band-panel" id="teachers-of-culadasa"><div class="wrap">
<h2>From teacher to student</h2>
<p class="muted">Ordination passed from teacher to student, in a lineage traced to the Buddha.</p>
<ol class="lineage">{chain_html}</ol>
</div></section>
<section class="section" id="wishes"><div class="wrap measure prose">{wishes}</div></section>
<section class="section band-panel" id="obituary"><div class="wrap measure prose">{obit}</div></section>'''
    page('lineage/', 'About Upasaka Culadasa', body, description='The Buddhist lineage of Upasaka Culadasa (John Yates, Ph.D., 1945–2021), his wishes for his teachings, and his obituary.')
    redirect = '<meta http-equiv="refresh" content="0; url=../lineage/">\n<link rel="canonical" href="../lineage/">\n'
    page('about/', 'About Culadasa', '<section class="section"><div class="wrap"><p>This page is now <a href="../lineage/">About</a>.</p></div></section>', extra_head=redirect)

    # ---------------------------------------------------------------- testimonials (old path) + book reviews (old path)
    body = banner('Testimonials', 'Praise for Culadasa as a teacher', '', 'teal') + f'<section class="section"><div class="wrap"><div class="quotes">{"".join(f"<figure class=quote><p>“{esc(q["text"])}”</p><footer>- {esc(q["by"])}</footer></figure>" for q in content["testimonials"])}</div><p><a href="{r}the-book/#reviews">Reviews of The Mind Illuminated →</a></p></div></section>'
    page('testimonials/', 'Testimonials', body, description='What students say about Culadasa as a teacher.')
    redirect = '<meta http-equiv="refresh" content="0; url=../testimonials/">\n<link rel="canonical" href="../testimonials/">\n'
    page('student-testimonials/', 'Student testimonials', '<section class="section"><div class="wrap"><p>This page has moved to <a href="../testimonials/">Testimonials</a>.</p></div></section>', extra_head=redirect)
    redirect = '<meta http-equiv="refresh" content="0; url=../the-book/#reviews">\n<link rel="canonical" href="../the-book/">\n'
    page('book-reviews/', 'Book reviews', '<section class="section"><div class="wrap"><p>The reviews are now on <a href="../the-book/#reviews">The Mind Illuminated</a> page.</p></div></section>', extra_head=redirect)

    # ---------------------------------------------------------------- teachers directory + map
    PUBLIC_T = [t for t in teachers['teachers'] if not t.get('hidden') and t.get('profile') != 'sample']
    HAS_PLACES = any(t.get('lat') or t.get('online') for t in PUBLIC_T)   # until teachers send their details there is nothing to map
    cards = ''
    for t in teachers['teachers']:
        if t.get('hidden') or t.get('profile') == 'sample':   # sample profiles are kept out of the public site (D, 27 Nov 2026)
            continue
        initials = ''.join(w[0] for w in re.sub(r'\(.*?\)|".*?"', '', t['name']).split()[:2])
        has = t.get('profile') == 'sample'
        photo = (f'<img src="{r}{t["photo"]}" alt="" loading="lazy">' if t.get('photo') else f'<span class="initials" aria-hidden="true">{esc(initials)}</span>')
        loc = esc(t.get('place') or '')
        cards += f'''<li class="tcard" data-name="{esc(t['name'].lower())}" data-place="{esc((t.get('place') or '').lower())}" data-year="{t['year']}" data-online="{1 if t.get('online') else 0}" data-inperson="{1 if t.get('lat') else 0}" {f'data-lat="{t["lat"]}" data-lng="{t["lng"]}"' if t.get('lat') else ''}>
<a href="{r}teachers/{t['slug']}/">{photo}<span class="tname">{esc(t['name'])}</span><span class="tmeta">Certified {t['year']}{'*' if t['year'] == 2022 else ''}{' · ' + loc if loc else ''}{' · Online' if t.get('online') else ''}</span>{'<span class="badge">Sample profile</span>' if has else ''}</a></li>'''
    body = banner('Practice with a teacher', 'Teachers', 'Certified teachers of The Mind Illuminated, online and in person.', 'gold') + f'''
<section class="section"><div class="wrap">
  <h2>Certified Teachers</h2>
  <p class="measure teacher-statement">{esc(content['teachers_intro'][0])}</p>
  <div class="finder">
    <div class="search-panel">
    <form class="search" id="teacher-form" role="search"><label class="sr" for="tq">Find a teacher by name</label><input id="tq" type="search" placeholder="Find a teacher by name"><button class="btn ghost" type="button" id="near"{'' if HAS_PLACES else ' hidden'}>Near me</button></form>
    <div class="filters" id="tfilters"{'' if HAS_PLACES else ' hidden'}><button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="online" aria-pressed="false">Teaches online</button><button type="button" data-f="inperson" aria-pressed="false">In person</button></div>
    </div>
    <p class="status small" id="tstatus" role="status"></p>
  </div>
  <details class="map-wrap" id="mapbox" open{'' if HAS_PLACES else ' hidden'}><summary>Map</summary><div id="map" class="map" role="region" aria-label="Map of teachers"></div></details>
  <ul class="tgrid" id="tlist">{cards}</ul>
  <p class="small muted">{esc(teachers['note'].split(' The twelve')[0])}</p>
  <hr><div class="measure small muted"><p>{esc(content['teachers_intro'][1])}</p><p>{esc(content['teachers_intro'][2])}</p><p>* 2022 graduates were certified to have completed <em>The Mind Illuminated Teacher Training Program</em> under the direct and personal guidance of Upāsaka Culadasa/John Yates PhD and graduates of the program.</p></div>
</div></section>'''
    page('teachers/', 'Teachers', body, description='Find a teacher certified in The Mind Illuminated method.',
         extra_head=f'<link rel="stylesheet" href="{r}assets/vendor/leaflet/leaflet.css">\n' if HAS_PLACES else '',
         extra_js=(f'<script src="{r}assets/vendor/leaflet/leaflet.js" defer></script>\n' if HAS_PLACES else '') + f'<script src="{r}assets/teachers.js" defer></script>\n')
    for t in teachers['teachers']:
        if t.get('profile') == 'sample':   # kept out of the public site (D, 27 Nov 2026); their data stays in teachers.json for the mock-up
            continue
        rr = '../../'
        sample = t.get('profile') == 'sample'
        photo = f'<img class="framed" src="{rr}{t["photo"]}" alt="{esc(t["name"])}">' if t.get('photo') else f'<div class="initials big" aria-hidden="true">{esc("".join(w[0] for w in re.sub(r"\(.*?\)|\".*?\"", "", t["name"]).split()[:2]))}</div>'
        bio = ''.join(f'<p>{esc(p)}</p>' for p in t.get('bio', [])) or '<p class="muted">[Biography to come, in the teacher’s own words: their path in practice, how they teach, and what students can expect.]</p>'
        details = [('Certified', f'{t["year"]}, The Mind Illuminated Teacher Training Program')]
        details.append(('Based in', t.get('place') or '[Town, region, country - to come]'))
        details.append(('Teaches', t.get('teaches') or '[In person, online, retreats - to come]'))
        details.append(('Website', f'<a href="{esc(t["website"])}" rel="noopener">{esc(t["website"])}</a>' if t.get('website') else '[Website - to come]'))
        body = f'''<header class="banner gold"><div class="wrap"><p class="label"><a href="{rr}teachers/">Teachers</a>{' · Sample profile (mock-up)' if sample else ''}</p><h1>{esc(t['name'])}</h1></div></header>
<section class="section"><div class="wrap two"><div>{photo}</div><div class="measure">{bio}
<dl class="facts">{''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in details)}</dl>
<p class="actions"><a class="btn" href="{rr}teachers/">All teachers</a></p></div></div></section>'''
        out = page(f'teachers/{t["slug"]}/', t['name'], body, description=f'{t["name"]}, a teacher of The Mind Illuminated method certified by Culadasa.')
        # these pages sit two levels down: page() computed depth from the path, so links are already right

    if V2:  # shared assets and data come from redesign/; site2.css is variant 2's own layer
        for sub in ('img', 'vendor'):
            shutil.copytree(ROOT / 'redesign' / 'assets' / sub, OUT / 'assets' / sub, dirs_exist_ok=True)
        for f in ('site.css', 'site.js', 'topics.js', 'teachers.js'):
            shutil.copy2(ROOT / 'redesign' / 'assets' / f, OUT / 'assets' / f)
        shutil.copy2(ROOT / 'tools' / 'site2.css', OUT / 'assets' / 'site2.css')
        shutil.copytree(D, OUT / 'data', dirs_exist_ok=True)
        pub = dict(teachers, teachers=[t for t in teachers['teachers'] if t.get('profile') != 'sample'])   # samples stay private (D, 27 Nov 2026)
        pub['note'] = teachers['note'].split(' The twelve')[0]
        (OUT / 'data' / 'topic_pages.json').unlink(missing_ok=True)   # used only by the build
        (OUT / 'data' / 'teachers.json').write_text(json.dumps(pub, ensure_ascii=False, indent=1))
    # ---------------------------------------------------------------- Library front page (D, 27 Nov 2026: "let's try it")
    n_talks = sum(1 for i in {v['id'] for v in _tr} | {v['id'] for v in videos} if i not in {s_['video'] for s_ in qna if s_.get('video')})
    rooms = [('Watch', 'Videos', 'videos/', f'{n_talks} talks and {len(qna)} AMA videos, every word searchable; each AMA video with its questions.'),
             ('Listen', 'Audio', 'audio/', 'Over 400 recordings: guided meditations, retreats, and questions and answers.'),
             ('Read', 'Writings', 'writings/', f'{N_WRIT} handouts and essays, free to read and download.'),
             ('In conversation', 'Conversations', 'conversations/', 'Interviews and podcasts with Culadasa from across the web.')]
    body = banner('Read, watch, listen', 'Library', 'The complete body of work: talks, recordings, AMA videos and writings, free to all.', 'teal') + f'''
<section class="section tight"><div class="wrap">{scoped_search(r, '', 'Search the library', 'l-q')}</div></section>
<section class="section"><div class="wrap"><h2 class="sr">The rooms of the Library</h2><div class="grid cols-4 library-rooms">{''.join(f'<a class="card" href="{r}{h}"><span class="meta">{esc(m)}</span><h3>{esc(t)}</h3><p>{esc(d)}</p><span class="more">Open →</span></a>' for m, t, h, d in rooms)}</div></div></section>'''
    page('library/', 'Library', body, description='The complete body of work of Upasaka Culadasa: talks, recordings, AMA videos and writings, free to all.')

    # ---------------------------------------------------------------- page not found (design review, 27 Nov 2026)
    ways = [('New to meditation', 'Start here', 'start-here/'), ('The Mind Illuminated Path', 'Learn', 'learn/'),
            ('Talks, recordings and writings', 'Library', 'library/'), ('Practice with someone', 'Find a teacher', 'teachers/')]
    body = banner('Error 404', 'Page not found', 'That address isn’t on the site. Search, or choose a way in below.', 'teal') + f'''
<section class="section tight"><div class="wrap">{scoped_search('', '', 'Search the site', 'nf-q')}</div></section>
<section class="section"><div class="wrap"><h2 class="sr">Ways in</h2><div class="grid cols-4">{''.join(f'<a class="card" href="{h}"><span class="meta">{esc(m)}</span><h3>{esc(t)}</h3><span class="more">Go →</span></a>' for m, t, h in ways)}</div></div></section>'''
    page('404.html', 'Page not found', body, description='Page not found.',
         extra_js='<script>document.querySelectorAll(\'a[href^="#"]\').forEach(function(a){a.href=location.href.split("#")[0]+a.getAttribute("href")});</script>\n')

    n = sum(1 for _ in OUT.rglob('index.html'))
    print(f'{n} pages written in {OUT.name}/')


if __name__ == '__main__':
    build()
