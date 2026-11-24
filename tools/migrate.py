#!/usr/bin/env python3
"""One-time migration: WordPress export -> static pages in site/.

Run from the repository root:  python3 tools/migrate.py
It reads source/wordpress-export/*.xml, cleans each page's HTML and writes
site/<slug>/index.html (home -> site/index.html), plus sitemap.xml, robots.txt
and 404.html.  The pages in site/ are the source of truth after migration;
this script is kept so the conversion can be audited or re-run.
"""
import re, html, pathlib, datetime
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPORT = next((ROOT / 'source' / 'wordpress-export').glob('*.xml'))
SITE = ROOT / 'site'
DOMAIN = 'https://culadasa.com'
NS = {'wp': 'http://wordpress.org/export/1.2/', 'content': 'http://purl.org/rss/1.0/modules/content/'}

# ---- navigation (same structure as the 2021 site) --------------------------
NAV = [
    ('About', '/', None),
    ('Online Meetings', '/online-meetings/', None),
    ('Teachings', None, [('Writings', '/writings/'), ('Audio', '/audio/'), ('Videos', '/videos/')]),
    ('Teachers', '/teachers/', None),
    ('Testimonials', '/testimonials/', [('Student testimonials', '/student-testimonials/'), ('Book reviews', '/book-reviews/')]),
]

# ---- per-page settings ------------------------------------------------------
TITLES = {  # slug -> (browser title, h1 to add when the page has none)
    'about': ('About', None),
    'online-meetings': ('Online Meetings', 'Online Meetings'),
    'writings': ('Writings', 'Writings'),
    'audio': ('Audio', 'Audio'),
    'videos': ('Videos', 'Videos'),
    'teachers': ('Teachers', None),
    'testimonials': ('Testimonials', None),
    'student-testimonials': ('Student testimonials', None),
    'book-reviews': ('Book reviews', None),
    'meditation-manual-introduction': ('Meditation Manual — Introduction', None),
    'mindful-awareness-vs-dullness': ('Mindful Awareness vs Dullness', None),
    'amount-of-concentration-needed-for-awakening': ('Amount of Concentration Needed for Awakening', 'Amount of Concentration Needed for Awakening'),
    'daily-life-practice': ('How to Maintain Practice in One’s Daily Life', 'How to Maintain Practice in One’s Daily Life'),
    'cultivating-mindfulness-in-daily-life': ('Cultivating Mindfulness in Daily Life', 'Cultivating Mindfulness in Daily Life'),
}
DESCRIPTIONS = {
    'about': 'Culadasa (John Yates, PhD), author of The Mind Illuminated: his wishes and legacy, obituary, biography and Buddhist lineage.',
    'online-meetings': 'Recordings of Culadasa’s monthly question-and-answer meetings, on YouTube and SoundCloud.',
    'writings': 'Handouts, essays and the meditation manual by Culadasa, free to download.',
    'audio': 'Culadasa’s talks, guided meditations and retreat recordings on SoundCloud.',
    'videos': 'Videos of Culadasa’s talks and discussions on YouTube.',
    'teachers': 'Teachers certified by Culadasa to teach The Mind Illuminated meditation system.',
    'testimonials': 'What students say about Culadasa as a teacher.',
    'student-testimonials': 'What students say about Culadasa as a teacher.',
    'book-reviews': 'Reviews of The Mind Illuminated by Culadasa.',
}
# YouTube playlists behind the old plugin galleries (IDs read from the live pages, 24 Nov 2026)
PLAYLISTS = {
    'online-meetings': ('PL5vT0La_cRtIN4640VK9tO6pmgRy4cahy', 'Patreon question-and-answer meetings'),
    'videos': ('PL5vT0La_cRtIqGrpKhqUNWq6NPYcMrV00', 'Talks and discussions'),
}
SINGLE_VIDEOS = {'videos': ['2LYa1YCdZH8', 'vtWoFpEHTBs']}
SOUNDCLOUD_PROFILE = 'https://api.soundcloud.com/users/111086538'

def sc_player(url, comments='true', height=450):
    src = ('https://w.soundcloud.com/player/?url=' + url.replace(':', '%3A')
           + f'&color=%23ff5500&auto_play=false&hide_related=false&show_comments={comments}&show_user=false&show_reposts=false')
    return f'<div class="audio"><iframe loading="lazy" title="SoundCloud player" allow="autoplay" src="{src}"></iframe></div>'

def yt_iframe(src, title):
    return f'<div class="video"><iframe loading="lazy" src="{src}" title="{html.escape(title)}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>'

# ---- cleaning ---------------------------------------------------------------
def autop(soup, container):
    """Wrap bare text separated by blank lines in <p> (WordPress did this at render time)."""
    for node in list(container.contents):
        if isinstance(node, NavigableString) and not isinstance(node, Comment) and node.strip():
            txt = str(node)
            sep = r'\n\s*\n' if re.search(r'\n\s*\n', txt) else r'\n'
            parts = [p.strip() for p in re.split(sep, txt) if p.strip()]
            if sep == r'\n':  # single newlines: only break where a sentence ends
                merged = []
                for p in parts:
                    if merged and not re.search(r'[.!?:”"’)\]]$', merged[-1]):
                        merged[-1] += ' ' + p
                    else:
                        merged.append(p)
                parts = merged
            new = []
            for p in parts:
                tag = soup.new_tag('p'); tag.string = re.sub(r'\s*\n\s*', ' ', p); new.append(tag)
            for t in reversed(new): node.insert_after(t)
            node.extract()

def clean(body_html, slug):
    body_html = body_html.replace('develping', 'developing')  # typo on the live page
    soup = BeautifulSoup(body_html, 'lxml')
    root = soup.body or soup
    for t in root.find_all(['style', 'script']): t.decompose()
    for c in root.find_all(string=lambda s: isinstance(s, Comment)): c.extract()
    for t in root.find_all('font'): t.unwrap()
    for t in root.find_all(True):
        for a in ['style', 'class', 'id', 'width', 'height', 'title', 'face', 'color', 'target', 'rel']:
            if a in t.attrs and not (t.name == 'img' and a in ('width', 'height')):
                del t.attrs[a]
        if t.name == 'a' and t.get('href', '').startswith(DOMAIN):
            t['href'] = t['href'][len(DOMAIN):] or '/'
        if t.name == 'img' and t.get('src', '').startswith(DOMAIN):
            t['src'] = t['src'][len(DOMAIN):]
        if t.name == 'a' and t.get('href', '').startswith('http'):
            t['rel'] = 'noopener'
    for t in root.find_all(['b', 'strong', 'p', 'em']):
        if not t.get_text(strip=True) and not t.find('img'):
            t.decompose()
    for br in root.find_all('br'):
        prev = br.find_previous_sibling(); nxt = br.find_next_sibling()
        if br.parent and br.parent.name == 'ul':  # <br/> between <li>s
            br.decompose()
    autop(soup, root)
    # headings: the page's own heading becomes the h1
    first = root.find(['h1', 'h2', 'h3'])
    if first is not None and slug not in ('about',):
        first.name = 'h1'
        for br in first.find_all('br'): br.replace_with(' ')
        first.string = re.sub(r'\s+', ' ', first.get_text()).strip()
    return soup, root

def page_specific(soup, root, slug):
    if slug == 'about':
        first_p = root.find('p')
        img_link = first_p.find('a') if first_p else None
        if img_link:
            fig = soup.new_tag('figure', attrs={'class': 'portrait'})
            img_link['href'] = '/wp-content/uploads/2021/09/Culadasa-photo-from-book-cover-2-MB-scaled.jpg'
            img = img_link.find('img'); img['alt'] = 'Culadasa, John Yates'; img['width'] = '250'; img['height'] = '376'
            fig.append(img_link.extract()); first_p.replace_with(fig)
        strong_ps = [p for p in root.find_all('p') if p.find('strong') and len(p.get_text(strip=True)) < 60 and p.get_text(strip=True) == p.find('strong').get_text(strip=True)]
        for p in strong_ps:  # "Culadasa's wishes and his legacy", "Remembering Culadasa", "Obituary" -> h2
            p.name = 'h2'; p.find('strong').unwrap()
        h2s = root.find_all('h2')
        lineage = h2s[-1] if h2s else None
        if lineage is not None and 'Lineage' in lineage.get_text():
            sec = soup.new_tag('section', attrs={'class': 'lineage'})
            nodes = []
            n = lineage.next_sibling
            while n is not None:
                nxt = n.next_sibling; nodes.append(n.extract()); n = nxt
            lineage.insert_after(sec); sec.append(lineage.extract())
            for n in nodes: sec.append(n)
            for img in sec.find_all('img'):
                img['alt'] = 'Culadasa laughing, seated in robes'
                link = img.parent if img.parent.name == 'a' else img
                holder = link.parent
                fig = soup.new_tag('figure', attrs={'class': 'portrait'})
                (holder if holder.name == 'p' else link).insert_before(fig)
                fig.append(link.extract())
                if holder.name == 'p' and not holder.get_text(strip=True): holder.decompose()
    if slug == 'teachers':
        h1 = root.find('h1')
        for h in root.find_all('h3'):
            if 'Graduates' in h.get_text():
                h.name = 'h2'
        # names: h3 (2021, 2022) and p (2018-2020) -> one <ul> per year
        for h2 in root.find_all('h2'):
            ul = soup.new_tag('ul'); n = h2.next_sibling
            while n is not None and not (getattr(n, 'name', None) in ('h2',)):
                nxt = n.next_sibling
                if getattr(n, 'name', None) in ('h3', 'p'):
                    text = n.get_text(' ', strip=True)
                    if text.startswith('*'):
                        break
                    li = soup.new_tag('li'); li.string = text; ul.append(li); n.decompose()
                n = nxt
            h2.insert_after(ul)
        foot = root.find_all('p')[-1]
        if foot.get_text(strip=True).startswith('*'):
            foot['class'] = 'note'
            for i in foot.find_all('i'): i.name = 'em'
    if slug == 'writings':
        for a in root.find_all('a'):
            # the "Slides" entry pointed at the handout instead of the slides file
            if a.get_text(strip=True).startswith('Introduction to What the Buddha Thought') and 'Slides' in a.get_text() \
               and a['href'].endswith('what-the-buddha-thought-handout.pdf'):
                a['href'] = '/wp-content/uploads/2021/09/20130322-what-the-buddha-thought-slides.pdf'
        for p in root.find_all('p'):  # section labels -> h2
            p.name = 'h2'
            for s in p.find_all('strong'): s.unwrap()
        for s in root.find_all('strong'):  # whole list was bold; CSS does that now
            if s.parent and s.parent.name == 'li': s.unwrap()
            elif s.find('h2'): s.unwrap()
    if slug == 'audio':
        labels = ['Questions and Answers', 'Teaching Retreats', 'Guided Meditations', 'Intensive Meditation Retreats']
        for p in root.find_all('p'):
            if p.get_text(strip=True) in labels:
                p.name = 'h2'; p.string = p.get_text(strip=True)
        for f in root.find_all('iframe'):
            url = re.search(r'url=([^&]+)', f['src']).group(1).replace('%3A', ':')
            comments = 'true' if 'show_comments=true' in f['src'] else 'false'
            f.replace_with(BeautifulSoup(sc_player(url, comments), 'lxml').div)
        # wrap each heading + player in a .media block
        for h2 in root.find_all('h2'):
            sec = soup.new_tag('section', attrs={'class': 'media'}); player = h2.find_next_sibling('div')
            h2.insert_before(sec); sec.append(h2.extract());
            if player: sec.append(player.extract())
        allrec = BeautifulSoup('<section class="media"><h2>All recordings</h2>' + sc_player(SOUNDCLOUD_PROFILE) +
                               '<p class="media-link"><a href="https://soundcloud.com/user-111086538" rel="noopener">Open Culadasa’s SoundCloud</a></p></section>', 'lxml').section
        root.append(allrec)
    if slug in PLAYLISTS:
        pl, label = PLAYLISTS[slug]
        blocks = ''
        for vid in SINGLE_VIDEOS.get(slug, []):
            blocks += yt_iframe(f'https://www.youtube.com/embed/{vid}', 'YouTube video')
        blocks += f'<section class="media"><h2>{label}</h2>' + yt_iframe(f'https://www.youtube.com/embed/videoseries?list={pl}', label) + \
                  f'<p class="media-link"><a href="https://www.youtube.com/playlist?list={pl}" rel="noopener">Open this playlist on YouTube</a></p></section>'
        # replace the [embedyt] shortcodes
        text_nodes = [n for n in root.find_all(string=True) if '[embedyt]' in n]
        for n in text_nodes:
            n.replace_with(NavigableString(re.sub(r'\[embedyt\].*?\[/embedyt\]', '', n)))
        frag = BeautifulSoup(blocks, 'lxml').body
        anchor = root.find('p')
        items = list(frag.contents)
        if anchor is not None and slug == 'online-meetings':
            for it in reversed(items): anchor.insert_after(it)
            # SoundCloud playlist iframe on the page
            for f in root.find_all('iframe', src=re.compile('soundcloud')):
                url = re.search(r'url=([^&]+)', f['src']).group(1).replace('%3A', ':')
                sec = BeautifulSoup('<section class="media"><h2>Audio recordings of the meetings</h2>' + sc_player(url, 'false') + '</section>', 'lxml').section
                f.replace_with(sec)
        else:
            for it in items: root.append(it)
    for p in root.find_all('p'):  # empty paragraphs left by the conversion
        if not p.get_text(strip=True).replace('\xa0', '') and not p.find(['img', 'iframe']):
            p.decompose()
    return root

def inner_html(root):
    out = ''.join(str(c) for c in root.contents)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out.strip()

# ---- templates ----------------------------------------------------------------
def rel(prefix, href):
    return prefix + href.lstrip('/') if href.startswith('/') else href

def nav_html(current, prefix):
    items = []
    for label, href, sub in NAV:
        cur = ' aria-current="page"' if href == current else ''
        if sub:
            subs = ''.join(f'<li><a href="{rel(prefix, h)}"{" aria-current=\"page\"" if h == current else ""}>{l}</a></li>' for l, h in sub)
            if href:
                head = f'<a href="{rel(prefix, href)}"{cur}>{label}</a>'
            else:
                head = f'<span class="sub-label" tabindex="0">{label}</span>'
            items.append(f'<li class="has-sub"{cur}>{head}<ul class="sub">{subs}</ul></li>')
        else:
            items.append(f'<li{cur}><a href="{rel(prefix, href)}">{label}</a></li>')
    return ''.join(items)

def page(slug, title, body, description, path, extra_class='', prefix=None):
    if prefix is None:
        prefix = '' if path == '/' else '../' * (path.strip('/').count('/') + 1)
    body = re.sub(r'(href|src)="/(?!/)', lambda m: f'{m.group(1)}="{prefix}', body)
    full_title = 'Culadasa' if slug == 'about' else f'{title} – Culadasa'
    canonical = DOMAIN + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="Culadasa">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:image" content="{DOMAIN}/wp-content/uploads/2021/09/Culadasa-photo-from-book-cover-2-MB-scaled.jpg">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@500;600;800&family=Roboto:ital,wght@0,400;0,700;1,400&display=swap">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <p class="site-title"><a href="{prefix}">Culadasa</a></p>
    <nav class="site-nav" aria-label="Main">
      <input type="checkbox" id="menu-toggle" class="menu-toggle">
      <label for="menu-toggle" class="menu-button">Menu</label>
      <ul class="menu">{nav_html(path, prefix)}</ul>
    </nav>
  </div>
</header>
<main id="main" class="wrap">
  <article class="content {extra_class}">
{body}
  </article>
</main>
<footer class="site-footer">
  <p>Copyright © 2021–{datetime.date.today().year}. The teachings of Culadasa are offered under a <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">Creative Commons Attribution 4.0</a> licence.</p>
</footer>
</body>
</html>
'''

# ---- main -----------------------------------------------------------------------
def main():
    ch = ET.parse(EXPORT).getroot().find('channel')
    pages = {}
    for i in ch.findall('item'):
        if i.findtext('wp:post_type', namespaces=NS) == 'page' and i.findtext('wp:status', namespaces=NS) == 'publish':
            slug = i.findtext('wp:post_name', namespaces=NS)
            pages[slug] = (i.findtext('link').replace(DOMAIN, '') or '/', i.findtext('content:encoded', namespaces=NS) or '')
    urls = []
    for slug, (path, raw) in pages.items():
        title, add_h1 = TITLES[slug]
        soup, root = clean(raw, slug)
        root = page_specific(soup, root, slug)
        body = inner_html(root)
        if add_h1:
            body = f'<h1>{html.escape(add_h1)}</h1>\n' + body
        desc = DESCRIPTIONS.get(slug) or re.sub(r'\s+', ' ', BeautifulSoup(body, 'lxml').get_text(' ', strip=True))[:155].rsplit(' ', 1)[0] + '…'
        out = SITE / ('index.html' if path == '/' else path.strip('/') + '/index.html')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(slug, title, body, desc, path, extra_class=slug), encoding='utf-8')
        urls.append(path)
        print(f'{out.relative_to(ROOT)}  {len(body)} chars')
    # 404
    body = '<h1>Page not found</h1><p>That address does not exist on this site. Try the menu above, or start from the <a href="/">About page</a>.</p>'
    (SITE / '404.html').write_text(page('404', 'Page not found', body, 'Page not found', '/404.html', prefix='/'), encoding='utf-8')
    (SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    today = datetime.date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         ''.join(f'  <url><loc>{DOMAIN}{u}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n'
    (SITE / 'sitemap.xml').write_text(sm)
    print(f'{len(urls)} pages written')

if __name__ == '__main__':
    main()
