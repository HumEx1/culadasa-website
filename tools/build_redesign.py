#!/usr/bin/env python3
"""Generate the redesign draft into redesign/ (static HTML, no build step on the host).

Design: A2 and D2 combined (Darin, 24 Nov 2026): his portrait leads as in A2; D2's cover textures support.
Content: real Culadasa material only (redesign/data/*.json, built from the
WordPress export, the saved galleries, the Q&A index and verified web sources).
Every page sits at the same path as on the old site where one existed, so the
redesign can later replace the mirror without breaking links.

Usage:  python3 tools/build_redesign.py
"""
import json, re, html, pathlib, datetime, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'redesign'
D = OUT / 'data'
content = json.loads((D / 'content.json').read_text())
videos = json.loads((D / 'videos.json').read_text())
topics = json.loads((D / 'topics.json').read_text())
teachers = json.loads((D / 'teachers.json').read_text())
convos = json.loads((D / 'conversations.json').read_text())
esc = html.escape
YEAR = datetime.date.today().year

NAV = [
    ('Start here', 'start-here/', None),
    ('Learn', 'learn/', None),
    ('Teachings', None, [('Writings', 'writings/'), ('Audio', 'audio/'), ('Videos', 'videos/'), ('Q&A archive', 'online-meetings/')]),
    ('Topics', 'topics/', None),
    ('The Book', 'the-book/', None),
    ('Teachers', 'teachers/', None),
    ('Conversations', 'conversations/', None),
    ('About', 'about/', None),
]
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


def nav_html(current, r):
    out = []
    for label, href, sub in NAV:
        if sub:
            cur = any(h == current for _, h in sub)
            subs = ''.join(f'<li><a href="{r}{h}"{" aria-current=\"page\"" if h == current else ""}>{esc(l)}</a></li>' for l, h in sub)
            out.append(f'<li class="has-sub"><span class="group" tabindex="0"{" aria-current=\"page\"" if cur else ""}>{label}</span><ul class="sub">{subs}</ul></li>')
        else:
            out.append(f'<li><a href="{r}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>')
    return ''.join(out)


def social_html(r=''):
    return ''.join(f'<a href="{u}" rel="noopener" aria-label="Culadasa on {n}"><svg viewBox="0 0 24 24" aria-hidden="true">{p}</svg></a>' for n, u, p in SOCIAL)


def page(path, title, body, *, description='', compact=True, extra_head='', extra_js=''):
    depth = 0 if path == '' else path.strip('/').count('/') + 1
    r = rel(depth)
    full = 'Culadasa — the teachings of John Yates' if path == '' else f'{title} — Culadasa'
    OLD = {'', 'writings/', 'audio/', 'videos/', 'online-meetings/', 'teachers/', 'testimonials/', 'student-testimonials/', 'book-reviews/',
           'meditation-manual-introduction/', 'mindful-awareness-vs-dullness/', 'amount-of-concentration-needed-for-awakening/',
           'daily-life-practice/', 'cultivating-mindfulness-in-daily-life/'}
    counterpart = path if path in OLD else ('teachers/' if path.startswith('teachers/') else ('book-reviews/' if path == 'the-book/' else ('online-meetings/' if path == 'topics/' else '')))
    mirror = r + '../' + counterpart
    mirror_label = 'See this page on the current site' if path in OLD else 'See the nearest page on the current site'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,300;0,400;0,500;1,300&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&display=swap">
<link rel="stylesheet" href="{r}assets/site.css">
{extra_head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="preview-bar">Draft redesign for review · <a href="{mirror}">{mirror_label}</a> · <a href="{r}compare/">Compare side by side</a></div>
<header class="masthead{' compact' if compact else ''}">
  <a class="wordmark" href="{r or './'}">Culadasa</a>
  <p class="tagline">Upasaka Culadasa · John Yates, Ph.D. · 1945–2021</p>
</header>
<img class="cubes" src="{r}assets/img/tmi-cubes-band.jpg" alt="">
<nav class="nav" aria-label="Main">
  <div class="wrap">
    <input type="checkbox" id="nav-toggle" class="nav-toggle">
    <label for="nav-toggle" class="nav-button">Menu</label>
    <ul class="menu">{nav_html(path, r)}</ul>
    <a class="subscribe" href="#signup">Newsletter</a>
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
      <p class="muted">A teaching, a Q&amp;A moment or a newly added recording, a few times a year. No more than that.</p>
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
        <li><a href="{r}start-here/">Start here</a></li><li><a href="{r}learn/">Learn</a></li><li><a href="{r}writings/">Writings</a></li><li><a href="{r}audio/">Audio</a></li>
        <li><a href="{r}videos/">Videos</a></li><li><a href="{r}online-meetings/">Q&amp;A archive</a></li><li><a href="{r}topics/">Topics</a></li>
        <li><a href="{r}the-book/">The Mind Illuminated</a></li><li><a href="{r}teachers/">Teachers</a></li><li><a href="{r}conversations/">Conversations</a></li>
        <li><a href="{r}testimonials/">Testimonials</a></li><li><a href="{r}about/">About</a></li>
      </ul></nav>
    </div>
    <div class="social">{social_html(r)}</div>
    <p class="licence">The teachings of Culadasa are offered freely under a <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">Creative Commons Attribution 4.0</a> licence, as he wished. © 2021–{YEAR}.</p>
  </div>
</footer>
<script src="{r}assets/site.js" defer></script>
{extra_js}</body>
</html>
'''
    out = OUT / (path + 'index.html' if path else 'index.html')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return out


def banner(label, h1, lead='', tone='teal', extra=''):
    return f'''<header class="banner {tone}"><div class="wrap">
  <p class="label">{label}</p><h1>{h1}</h1>{f'<p class="lead">{lead}</p>' if lead else ''}{extra}
</div></header>'''


def video_tile(v, r, sub=''):
    return f'''<article class="video-card">
  <div class="video" data-id="{v['id']}"><button type="button" aria-label="Play: {esc(v['title'])}"><img src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="" loading="lazy"><span class="play"></span></button></div>
  <h3>{esc(v['title'])}</h3>{f'<p>{sub}</p>' if sub else ''}
</article>'''


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
    ('Teaching retreat handouts', [
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
        ('When Buddhadharma Comes to the West – Parts II & III: What the Buddha Taught & Wisdom and Virtue', 'pdf', 'BuddhadharmaWestPartsIIandIII.pdf'),
        ('Joy & Meditation – More Than Just a Happy Feeling', 'pdf', 'Meditation-and-Joy-Handout.pdf'),
    ]),
    ('From the Jhana_Insight discussion board', [
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


STAGES = [
    ('Establishing a practice', 'Novice'), ('Interrupted attention and overcoming mind-wandering', 'Novice'),
    ('Extended attention and overcoming forgetting', 'Novice'),
    ('Continuous attention and overcoming gross distraction and strong dullness', 'Skilled'),
    ('Overcoming subtle dullness and increasing mindfulness', 'Skilled'), ('Subduing subtle distraction', 'Skilled'),
    ('Exclusive attention and unifying the mind', 'Transition'), ('Mental pliancy and pacifying the senses', 'Adept'),
    ('Mental and physical pliancy and calming the intensity of meditative joy', 'Adept'), ('Tranquility and equanimity', 'Adept'),
]


def clean_essay(raw):
    s = re.sub(r'\s(style|class|id)="[^"]*"', '', raw)
    s = re.sub(r'<h2[^>]*>.*?</h2>', '', s, count=1, flags=re.S)
    s = s.replace('develping', 'developing')
    s = re.sub(r'<br\s*/?>\s*</', '</', s)
    s = s.replace('https://culadasa.com/', '../')
    paras = [p.strip() for p in re.split(r'\n\s*\n', s) if p.strip()]
    out = []
    for p in paras:
        out.append(p if re.match(r'<(p|ul|ol|h\d|blockquote)', p) else f'<p>{p}</p>')
    return '\n'.join(out)


def build():
    vid_by_id = {v['id']: v for v in videos}
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
      <p class="label">His wishes and his legacy</p>
      <h1>That his work be freely and equally available to all students.</h1>
      <p class="by">— Culadasa, in his final days</p>
      <p class="lead">Culadasa, John Yates Ph.D., spent four decades in the Tibetan and Theravādin traditions and taught physiology and neuroscience. His book <em>The Mind Illuminated</em> joins the two. Everything he taught is here, free.</p>
      <div class="actions"><a class="btn" href="start-here/">Start here</a><a class="btn ghost" href="topics/">Search the teachings</a></div>
    </div>
  </div>
</section>
<img class="glow" src="assets/img/tmi-cubes-glow.jpg" alt="">
<section class="section">
  <div class="wrap">
    <p class="label">Find your way in</p>
    <div class="grid cols-4">
      <a class="card" href="start-here/"><span class="meta">New to meditation</span><h3>Start here</h3><p>Seven steps from your first sit to a daily practice, using his own handouts and guided meditations.</p><span class="more">Begin →</span></a>
      <a class="card" href="learn/"><span class="meta">The basics</span><h3>Learn the method</h3><p>Attention and awareness, the ten stages, insight, and practice in daily life, in his words.</p><span class="more">Learn →</span></a>
      <a class="card" href="topics/"><span class="meta">Every teaching, searchable</span><h3>Topics</h3><p>Search 190,000 words of handouts, essays, interviews and 439 recorded questions and answers.</p><span class="more">Search →</span></a>
      <a class="card" href="teachers/"><span class="meta">Practise with someone</span><h3>Find a teacher</h3><p>The 48 teachers he certified in The Mind Illuminated method, on a map.</p><span class="more">Find →</span></a>
    </div>
  </div>
</section>
<section class="section tight band-panel">
  <div class="wrap">
    <form class="search" action="topics/" method="get" role="search">
      <label class="sr" for="home-q">Search the teachings</label>
      <input id="home-q" name="q" type="search" placeholder="Search the teachings, for example: compassion">
      <button class="btn" type="submit">Search</button>
    </form>
    <p class="small muted" style="margin:14px 0 0">Most discussed: {" · ".join(f'<a href="topics/?q={urllib.parse.quote(w)}">{esc(w)}</a>' for w in cloud_top)}</p>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <p class="label">Watch</p><h2>From the archive</h2><p class="muted">Talks from his YouTube channel, and his last recorded question-and-answer session. <a href="videos/">All videos</a> · <a href="online-meetings/">Q&amp;A archive</a></p>
    <div class="grid">{''.join(video_tile(v, '') for v in feat)}</div>
  </div>
</section>
<section class="section banner-section ink">
  <div class="wrap two">
    <div><img class="framed" src="assets/img/the-mind-illuminated-cover.jpg" alt="Cover of The Mind Illuminated" width="320" loading="lazy"></div>
    <div>
      <p class="label">The book</p>
      <h2>The Mind Illuminated</h2>
      <p>A complete meditation guide integrating Buddhist wisdom and brain science, written with Matthew Immergut and Jeremy Graves. Its ten stages map the path from a first, distracted sit to tranquility and equanimity.</p>
      <ol class="stages compact">{''.join(f'<li><span>{esc(n)}</span></li>' for n, _ in STAGES[:5])}</ol>
      <p><a class="btn ghost light" href="the-book/">The ten stages →</a></p>
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
<section class="eyes-band" aria-label="Closing">
  <img src="assets/img/tmi-eyes.jpg" alt="The closed eyes of the Buddha, from the cover of The Mind Illuminated" loading="lazy">
  <p>All of Culadasa’s students are his successors.</p>
  <p class="small muted" style="font-family:var(--text);font-size:15px;margin-top:6px">— The Yates family</p>
</section>'''
    page('', 'Home', body, compact=False,
         description='The teachings of Culadasa (John Yates, Ph.D.), author of The Mind Illuminated: writings, talks, Q&A recordings, topics and teachers.')

    # ---------------------------------------------------------------- start here
    r = '../'
    steps = [
        ('Read the beginning meditation handout', 'Two pages on posture, the breath at the nose, and what to do when the mind wanders.', f'<a class="btn ghost" href="{r}{UP}beginning-meditation-handout.pdf">Open the handout (PDF)</a>'),
        ('Prepare for each sit', 'His six preparations: motivation, goals, expectations, diligence, distractions and posture.', f'<a class="btn ghost" href="{r}{UP}preparation-for-practice.pdf">Preparation for Practice (PDF)</a>'),
        ('Sit with a guided meditation', 'Follow his voice. Start with one of the shorter recordings and sit daily, even briefly.', sc_player('playlists', '282960661', 300, False)),
        ('Learn the map', 'The ten stages show where you are and what to work on next. Read the introduction to the meditation manual, then the stages.', f'<div class="actions"><a class="btn ghost" href="{r}meditation-manual-introduction/">Introduction to the manual</a><a class="btn ghost" href="{r}the-book/">The ten stages</a></div>'),
        ('Understand attention and awareness', 'The two kinds of knowing the whole method trains. His essay on dullness explains why vividness matters.', f'<a class="btn ghost" href="{r}mindful-awareness-vs-dullness/">Mindful Awareness vs Dullness</a>'),
        ('Take it into daily life', 'Practice does not end when you stand up. His handout and essays on daily life.', f'<div class="actions"><a class="btn ghost" href="{r}{UP}Awakening-in-Daily-Life-Handout.pdf">The Path to Awakening in Daily Life (PDF)</a><a class="btn ghost" href="{r}daily-life-practice/">Maintaining practice in daily life</a></div>'),
        ('Ask your question', 'Someone has probably asked it already. Search 439 recorded questions and jump to his answer.', f'<a class="btn" href="{r}topics/">Search the teachings</a>'),
    ]
    body = banner('New to meditation', 'Start here', 'Seven steps through his own handouts, essays and recordings, from your first sit to a daily practice.', 'teal') + f'''
<section class="section"><div class="wrap measure"><ol class="steps">{''.join(f'<li><div><h3>{t}</h3><p>{d}</p>{a}</div></li>' for t, d, a in steps)}</ol></div></section>
<section class="section band-panel" id="asked"><div class="wrap measure"><p class="label">Frequently asked</p><h2>What people asked him most</h2>
<p class="muted">From the 439 questions put to him in his Q&amp;A sessions, 2017–2021. Each link opens his answers, most-discussed first.</p>
<ul class="doclist">{''.join(f'<li><a href="{r}topics/?q={urllib.parse.quote(f["q"])}&amp;type=Q%26A"><span>{esc(f["label"])}</span><span class="kind">{f["n"]} questions</span></a></li>' for f in content['faq'])}</ul></div></section>'''
    page('start-here/', 'Start here', body, description='A seven-step beginning path through Culadasa’s own handouts, guided meditations and essays.')

    # ---------------------------------------------------------------- learn hub (journey by level)
    def qlink(q): return f'{r}topics/?q={urllib.parse.quote(q)}'
    tracks = [
        ('The basics', 'teal', [
            ('What meditation trains', 'Attention and peripheral awareness, and how they work together.', qlink('peripheral awareness')),
            ('Posture and preparation', 'Sitting comfortably and the six preparations.', f'{r}{UP}preparation-for-practice.pdf'),
            ('Mind-wandering', 'Why the mind wanders, and why noticing it is a success, not a failure.', qlink('mind-wandering')),
            ('Dullness', 'Mindful awareness versus dullness: his essay.', f'{r}mindful-awareness-vs-dullness/'),
        ]),
        ('The method', 'gold', [
            ('The ten stages', 'Novice, skilled, transition and adept: the map in his book.', f'{r}the-book/'),
            ('Introduction to the manual', 'Concentration and mindful awareness to a minimum level, the first step towards awakening.', f'{r}meditation-manual-introduction/'),
            ('An introduction to the ten stages of samatha', 'His retreat handout on the stages.', f'{r}{UP}Cape-Ann-Retreat-for-Peace-Handout-.pdf'),
            ('Jhāna', 'The original practice of mindfulness and insight.', f'{r}{UP}jhanas-and-mindfulness-handout.pdf'),
        ]),
        ('The science of mind', 'ink', [
            ('The mind-system model', 'His model of the mind as many sub-minds, from the book and the Q&As.', qlink('mind-system')),
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
            ('Craving', 'Recognising craving and what to do next.', qlink('craving')),
            ('Compassion', 'Compassion in his teaching and answers.', qlink('compassion')),
        ]),
    ]
    sec = ''
    for name, tone, items in tracks:
        sec += f'''<section class="section"><div class="wrap"><div class="track-head {tone}"><h2>{name}</h2></div>
<div class="grid cols-4">{''.join(f'<a class="card" href="{u}"><h3>{esc(t)}</h3><p>{esc(d)}</p><span class="more">{"Search" if "topics/?q=" in u else "Open"} →</span></a>' for t, d, u in items)}</div></div></section>'''
    body = banner('The basics, then deeper', 'Learn', 'His teaching arranged as a journey: the basics, the method, the science of mind, going deeper, and daily life.', 'ink') + sec
    page('learn/', 'Learn', body, description='Culadasa’s teaching arranged as a journey: basics, method, science of mind, going deeper, daily life.')

    # ---------------------------------------------------------------- the book
    body = banner('The book', '<em>The Mind Illuminated</em>', 'A complete meditation guide integrating Buddhist wisdom and brain science.', 'gold') + f'''
<section class="section"><div class="wrap two">
  <div><img class="framed" src="{r}assets/img/the-mind-illuminated-cover.jpg" alt="Cover of The Mind Illuminated" loading="lazy"></div>
  <div class="measure">
    <p class="lead">Written by Culadasa (John Yates, Ph.D.) with Matthew Immergut, Ph.D. and Jeremy Graves, and first published by Dharma Treasure Press on 6 October 2015.</p>
    <p>The book sets out ten stages of meditative development, from establishing a daily practice to tranquility and equanimity, with clear instructions for each stage and an account of how the mind works drawn from both the Buddhist tradition and cognitive science.</p>
    <p><a class="btn" href="https://www.simonandschuster.com/books/The-Mind-Illuminated/John-Yates/9781501156984" rel="noopener">From the publisher</a></p>
  </div>
</div></section>
<section class="section"><div class="wrap"><p class="label">The ten stages</p><h2>From the first sit to equanimity</h2>
<ol class="stages">{''.join(f'<li><span><small>{lvl}</small>{esc(n)}</span></li>' for n, lvl in STAGES)}</ol>
<p class="muted small" style="margin-top:18px">Milestones: continuous attention to the meditation object (after stage 3); sustained exclusive focus of attention (after stage 6); effortless stability of attention (after stage 7); persistence of the mental qualities of an adept (after stage 10).</p></div></section>
<section class="section" id="reviews"><div class="wrap"><p class="label">Reviews</p><h2>What teachers and authors say</h2><div class="quotes">{''.join(f'<figure class="quote"><p>“{esc(q["text"])}”</p><footer>— {esc(q["by"])}</footer></figure>' for q in content['reviews'])}</div></div></section>'''
    page('the-book/', 'The Mind Illuminated', body, description='The Mind Illuminated by Culadasa (John Yates, Ph.D.): the ten stages of meditative development.')

    # ---------------------------------------------------------------- writings (old path)
    body = banner('Read', 'Writings', 'Twenty-six handouts and essays, free to read and download.', 'teal') + '<section class="section"><div class="wrap measure">' + ''.join(
        f'<h2>{esc(g)}</h2><ul class="doclist">{"".join(doc_link(t, k, x, r) for t, k, x in items)}</ul>' for g, items in WRITINGS) + '</div></section>'
    page('writings/', 'Writings', body, description='Culadasa’s handouts and essays, free to download.')

    # ---------------------------------------------------------------- essays (old paths)
    for slug, raw in content['essays'].items():
        title = next(t for g, items in WRITINGS for t, k, x in items if x == slug + '/')
        words = len(re.sub(r'<[^>]+>', ' ', raw).split())
        body = f'''<header class="banner panel"><div class="wrap measure"><p class="label">Essay · {max(1, round(words / 230))} min read</p><h1>{esc(title)}</h1></div></header>
<article class="section"><div class="wrap measure prose">{clean_essay(raw)}</div></article>
<section class="section tight"><div class="wrap measure"><p><a href="{r}writings/">← All writings</a> · <a href="{r}topics/">Search the teachings</a></p></div></section>'''
        page(slug + '/', title, body, description=f'{title}: an essay by Culadasa.')

    # ---------------------------------------------------------------- audio (old path)
    PL = [('Guided Meditations', '282960661'), ('Questions and Answers', '283520935'), ('Teaching Retreats', '296077102'),
          ('Intensive Meditation Retreats', '283729524'), ('Patreon Q&As', '967729615')]
    body = banner('Listen', 'Audio', 'Guided meditations, teaching retreats and questions and answers: 401 recordings in 26 collections on his SoundCloud.', 'ink',
                  '<p><a class="btn ghost light" href="https://soundcloud.com/culadasa" rel="noopener">Open SoundCloud</a></p>') + '<section class="section"><div class="wrap"><div class="grid">' + ''.join(
        f'<section><h2 style="font-size:24px">{t}</h2>{sc_player("playlists", i, 420)}</section>' for t, i in PL) + f'</div></div></section><section class="section"><div class="wrap"><h2>Every recording</h2><p class="muted">All 401 recordings, newest first.</p>{sc_player("users", "111086538", 600)}</div></section>'
    page('audio/', 'Audio', body, description='Culadasa’s guided meditations, retreats and Q&A recordings on SoundCloud.')

    # ---------------------------------------------------------------- videos (old path)
    body = banner('Watch', 'Videos', f'{len(talks)} talks and discussions, and {len(qna)} recorded question-and-answer sessions.', 'teal',
                  '<p><a class="btn ghost light" href="https://www.youtube.com/@Culadasa" rel="noopener">Open YouTube</a></p>') + f'''
<section class="section"><div class="wrap"><h2>Talks and discussions</h2><div class="grid">{''.join(video_tile(v, r) for v in talks)}</div></div></section>
<section class="section"><div class="wrap"><h2>Question-and-answer sessions</h2><p class="muted">Each session’s questions are listed, with links to the moment he answers, in the <a href="{r}online-meetings/">Q&amp;A archive</a>.</p>
<div class="grid">{''.join(video_tile(vid_by_id[s['video']], r, f"{len(s['items'])} questions") for s in reversed(qna))}</div></div></section>'''
    page('videos/', 'Videos', body, description='Talks, discussions and Q&A sessions by Culadasa on YouTube.')

    # ---------------------------------------------------------------- Q&A archive (old path: online-meetings)
    sess = ''
    for s in reversed(qna):
        v = vid_by_id[s['video']]
        items = ''.join(f'<li><a class="t" href="{esc(i["url"])}" rel="noopener">{i["t"]}</a> {esc(i["text"][:400])}{"…" if len(i["text"]) > 400 else ""}</li>' for i in s['items'])
        sess += f'''<details class="session"><summary><h3>{esc(s['month'])}</h3><span class="count">{len(s['items'])} questions</span></summary>
<div class="body"><div>{video_tile(v, r)}</div><ol class="qlist">{items}</ol></div></details>'''
    body = banner('Online meetings', 'Q&amp;A archive', esc(content['online_meetings_intro']), 'teal',
                  f'<p class="small">Questions transcribed by Alex in the <a href="{topics["credit"]["qna"]["url"]}" rel="noopener">Culadasa Q&amp;A Index</a>. Each time links to the moment the question is asked.</p>') + f'''
<section class="section"><div class="wrap"><form class="search" action="{r}topics/" method="get" role="search"><label class="sr" for="qa-q">Search the questions</label><input id="qa-q" name="q" type="search" placeholder="Search {sum(len(s['items']) for s in qna)} questions and answers"><input type="hidden" name="type" value="Q&amp;A"><button class="btn">Search</button></form>
{sess}</div></section>
<section class="section"><div class="wrap"><h2>Audio of the meetings</h2>{sc_player('playlists', '967729615', 450, False)}</div></section>'''
    page('online-meetings/', 'Q&A archive', body, description='Every question from Culadasa’s 61 recorded Q&A sessions, 2017–2021, with links to his answers.')

    # ---------------------------------------------------------------- topics
    body = banner('Every teaching, searchable', 'Topics', f'Search {round(sum(len(d["text"].split()) for d in topics["docs"]) / 1000) + round(sum(len(i["text"].split()) for s in qna for i in s["items"]) / 1000)},000 words: handouts, essays, two long interviews, and {sum(len(s["items"]) for s in qna)} recorded questions. Results are ranked by how often they mention what you search for.', 'ink') + f'''
<section class="section"><div class="wrap">
  <form class="search" id="topic-form" role="search"><label class="sr" for="q">Search the teachings</label><input id="q" name="q" type="search" placeholder="Try: compassion, dullness, jhāna, craving" autocomplete="off"><button class="btn" type="submit">Search</button></form>
  <div class="filters" id="filters" aria-label="Filter by kind"></div>
  <div class="cloud" id="cloud" aria-label="Most frequent words across the teachings"></div>
  <p class="status" id="status" role="status">Loading the teachings…</p>
  <div class="results" id="results"></div>
  <p class="small muted">Sources: his handouts and essays; the Culadasa Q&amp;A Index by Alex; interview transcripts from Buddha at the Gas Pump and Deconstructing Yourself (his words only). Common English words are left out of the word cloud.</p>
</div></section>'''
    page('topics/', 'Topics', body, description='Search every Culadasa teaching by topic, ranked by mentions, with a word cloud.',
         extra_js=f'<script src="{r}assets/topics.js" defer></script>\n')

    # ---------------------------------------------------------------- conversations (blog)
    items = ''.join(f'''<article class="convo"><div class="when">{esc(c['date_label'])}</div><div>
<h3><a href="{esc(c['url'])}" rel="noopener">{esc(c['title'])}</a></h3><p class="show">{esc(c['show'])}{f" · with {esc(c['host'])}" if c.get('host') else ''}</p>
<p>{esc(c['description'])}</p><p class="small">{' · '.join(f'<a href="{esc(u)}" rel="noopener">{esc(l)}</a>' for l, u in c.get('links', []))}</p></div></article>''' for c in convos['items'])
    body = banner('In conversation', 'Conversations', 'Interviews, podcasts and talks with Culadasa, from across the web.', 'gold') + f'<section class="section"><div class="wrap measure">{items}<p class="small muted" style="margin-top:24px">{esc(convos["note"])}</p></div></section>'
    page('conversations/', 'Conversations', body, description='Interviews, podcasts and talks with Culadasa from across the web.')

    # ---------------------------------------------------------------- about
    about = content['about_html']
    about = re.sub(r'<a href="https://culadasa\.com/wp-content[^"]*"><img[^>]*Culadasa-photo[^>]*/></a>', '', about)
    about = re.sub(r'<a href="https://culadasa\.com/wp-content[^"]*"><img[^>]*Screen-Shot[^>]*/></a>', '', about)
    about = re.sub(r'\s(style|class|id|title)="[^"]*"', '', about)
    about = re.sub(r'<b>\s*</b>', '', about)
    about = re.sub(r'<p><strong>([^<]{3,60})</strong></p>', r'<h2>\1</h2>', about)
    body = banner('About', 'Culadasa', 'Upasaka Culadasa, John Yates Ph.D., 1945–2021. Meditation master, neuroscientist, author.', 'gold') + f'''
<section class="section"><div class="wrap two"><div><img class="framed" src="{r}assets/img/culadasa-portrait.jpg" alt="Culadasa, John Yates" loading="lazy"><img class="framed" style="margin-top:28px;max-width:260px" src="{r}assets/img/culadasa-robes.jpg" alt="Culadasa laughing, seated in robes" loading="lazy"></div>
<div class="prose measure">{about}</div></div></section>'''
    page('about/', 'About Culadasa', body, description='Culadasa (John Yates, Ph.D.): his wishes and legacy, obituary, biography and Buddhist lineage.')

    # ---------------------------------------------------------------- testimonials (old path) + book reviews (old path)
    body = banner('Testimonials', 'Praise for Culadasa as a teacher', '', 'teal') + f'<section class="section"><div class="wrap"><div class="quotes">{"".join(f"<figure class=quote><p>“{esc(q["text"])}”</p><footer>— {esc(q["by"])}</footer></figure>" for q in content["testimonials"])}</div><p><a href="{r}the-book/#reviews">Reviews of The Mind Illuminated →</a></p></div></section>'
    page('testimonials/', 'Testimonials', body, description='What students say about Culadasa as a teacher.')
    redirect = '<meta http-equiv="refresh" content="0; url=../testimonials/">\n<link rel="canonical" href="../testimonials/">\n'
    page('student-testimonials/', 'Student testimonials', '<section class="section"><div class="wrap"><p>This page has moved to <a href="../testimonials/">Testimonials</a>.</p></div></section>', extra_head=redirect)
    redirect = '<meta http-equiv="refresh" content="0; url=../the-book/#reviews">\n<link rel="canonical" href="../the-book/">\n'
    page('book-reviews/', 'Book reviews', '<section class="section"><div class="wrap"><p>The reviews are now on <a href="../the-book/#reviews">The Mind Illuminated</a> page.</p></div></section>', extra_head=redirect)

    # ---------------------------------------------------------------- teachers directory + map
    cards = ''
    for t in teachers['teachers']:
        initials = ''.join(w[0] for w in re.sub(r'\(.*?\)|".*?"', '', t['name']).split()[:2])
        has = t.get('profile') == 'sample'
        photo = (f'<img src="{r}{t["photo"]}" alt="" loading="lazy">' if t.get('photo') else f'<span class="initials" aria-hidden="true">{esc(initials)}</span>')
        loc = esc(t.get('place') or 'Location to come')
        cards += f'''<li class="tcard" data-name="{esc(t['name'].lower())}" data-place="{esc((t.get('place') or '').lower())}" data-year="{t['year']}" data-online="{1 if t.get('online') else 0}" {f'data-lat="{t["lat"]}" data-lng="{t["lng"]}"' if t.get('lat') else ''}>
<a href="{r}teachers/{t['slug']}/">{photo}<span class="tname">{esc(t['name'])}</span><span class="tmeta">Certified {t['year']} · {loc}{' · Online' if t.get('online') else ''}</span>{'<span class="badge">Sample profile</span>' if has else ''}</a></li>'''
    body = banner('Practise with a teacher', 'Teachers', esc(content['teachers_intro'][0]), 'gold') + f'''
<section class="section"><div class="wrap">
  <div class="finder">
    <form class="search" id="teacher-form" role="search"><label class="sr" for="tq">Find a teacher by name or place</label><input id="tq" type="search" placeholder="Name, town or country"><button class="btn ghost" type="button" id="near">Near me</button></form>
    <div class="filters" id="tfilters"><button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="online" aria-pressed="false">Teaches online</button>{''.join(f'<button type="button" data-f="{y["year"]}" aria-pressed="false">{y["year"]}</button>' for y in content['teacher_years'])}</div>
    <div id="map" class="map" role="region" aria-label="Map of teachers"></div>
    <p class="status small" id="tstatus" role="status"></p>
  </div>
  <ul class="tgrid" id="tlist">{cards}</ul>
  <p class="small muted">{esc(teachers['note'])}</p>
  <hr><div class="measure small muted"><p>{esc(content['teachers_intro'][1])}</p><p>{esc(content['teachers_intro'][2])}</p></div>
</div></section>'''
    page('teachers/', 'Teachers', body, description='Find a teacher certified by Culadasa in The Mind Illuminated method, by name, place or map.',
         extra_head=f'<link rel="stylesheet" href="{r}assets/vendor/leaflet/leaflet.css">\n',
         extra_js=f'<script src="{r}assets/vendor/leaflet/leaflet.js" defer></script>\n<script src="{r}assets/teachers.js" defer></script>\n')
    for t in teachers['teachers']:
        rr = '../../'
        sample = t.get('profile') == 'sample'
        photo = f'<img class="framed" src="{rr}{t["photo"]}" alt="{esc(t["name"])}">' if t.get('photo') else f'<div class="initials big" aria-hidden="true">{esc("".join(w[0] for w in re.sub(r"\(.*?\)|\".*?\"", "", t["name"]).split()[:2]))}</div>'
        bio = ''.join(f'<p>{esc(p)}</p>' for p in t.get('bio', [])) or '<p class="muted">[Biography to come, in the teacher’s own words: their path in practice, how they teach, and what students can expect.]</p>'
        details = [('Certified', f'{t["year"]}, The Mind Illuminated Teacher Training Program')]
        details.append(('Based in', t.get('place') or '[Town, region, country — to come]'))
        details.append(('Teaches', t.get('teaches') or '[In person, online, retreats — to come]'))
        details.append(('Website', f'<a href="{esc(t["website"])}" rel="noopener">{esc(t["website"])}</a>' if t.get('website') else '[Website — to come]'))
        body = f'''<header class="banner gold"><div class="wrap"><p class="label"><a href="{rr}teachers/">Teachers</a>{' · Sample profile (mock-up)' if sample else ''}</p><h1>{esc(t['name'])}</h1></div></header>
<section class="section"><div class="wrap two"><div>{photo}</div><div class="measure">{bio}
<dl class="facts">{''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in details)}</dl>
<p class="actions"><a class="btn" href="{rr}teachers/">All teachers</a></p></div></div></section>'''
        out = page(f'teachers/{t["slug"]}/', t['name'], body, description=f'{t["name"]}, a teacher of The Mind Illuminated method certified by Culadasa.')
        # these pages sit two levels down: page() computed depth from the path, so links are already right

    # ---------------------------------------------------------------- compare (mirror vs redesign)
    pairs = [('Home / About', '', ''), ('Writings', 'writings/', 'writings/'), ('Audio', 'audio/', 'audio/'), ('Videos', 'videos/', 'videos/'),
             ('Online meetings', 'online-meetings/', 'online-meetings/'), ('Teachers', 'teachers/', 'teachers/'), ('Testimonials', 'testimonials/', 'testimonials/'),
             ('Book reviews', 'book-reviews/', 'book-reviews/'), ('Mindful Awareness vs Dullness', 'mindful-awareness-vs-dullness/', 'mindful-awareness-vs-dullness/')]
    opts = ''.join(f'<option value="{m}|{n}">{esc(l)}</option>' for l, m, n in pairs)
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compare: current site and redesign — Culadasa</title><meta name="robots" content="noindex"><link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500&display=swap"><link rel="stylesheet" href="../assets/site.css"></head>
<body><div class="compare-bar"><label for="pick">Page</label><select id="pick">{opts}</select><span>Left: the current site (exact mirror). Right: the redesign draft.</span><a href="../">Open the redesign</a><a href="../../">Open the current site</a></div>
<div class="panes"><section><h2>Current site</h2><iframe id="left" title="Current site" src="../../"></iframe></section><section><h2>Redesign draft</h2><iframe id="right" title="Redesign draft" src="../"></iframe></section></div>
<script>
const pick=document.getElementById('pick'),L=document.getElementById('left'),R=document.getElementById('right');
function go(){{const [m,n]=pick.value.split('|');L.src='../../'+m;R.src='../'+n;try{{history.replaceState(null,'','#'+encodeURIComponent(pick.value))}}catch(e){{}}}}
const h=decodeURIComponent(location.hash.slice(1));if(h&&[...pick.options].some(o=>o.value===h)){{pick.value=h;go()}}
pick.addEventListener('change',go);
</script></body></html>'''
    (OUT / 'compare').mkdir(parents=True, exist_ok=True)
    (OUT / 'compare' / 'index.html').write_text(doc)
    n = sum(1 for _ in OUT.rglob('index.html'))
    print(f'{n} pages written in redesign/')


if __name__ == '__main__':
    build()
