"""Culadasa's SoundCloud recordings as data, for Topics search and the Audio page.

Usage:  python3 tools/build_audio.py source/soundcloud-feed-2026-11-25/sounds.rss > redesign/data/audio.json

The source is his public SoundCloud podcast feed (401 recordings), saved with email addresses removed.
Each recording keeps its title, link, date and length, and the useful part of its description
(timestamps, questions, summaries). Repeated promotional lines (follow on Twitter/Facebook, buy the books,
"much more at…", requests for comments) and bare links are dropped. Nothing is reworded.
"""
import re, sys, json, html
from email.utils import parsedate_to_datetime

src = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
PROMO = re.compile(r'^(follow culadasa|much more at|more at|buy culadasa|we need your help|support culadasa|become a patron|'
                   r'join (us|culadasa) on patreon|subscribe|\[email\]|https?://\S+$|www\.\S+$)', re.I)

def tag(t, x):
    m = re.search(r'<' + t + r'[^>]*>(.*?)</' + t + '>', x, re.S)
    return html.unescape(re.sub(r'<!\[CDATA\[|\]\]>', '', m.group(1))).strip() if m else ''

out = []
for it in re.findall(r'<item>(.*?)</item>', src, re.S):
    lines = [l.strip() for l in tag('description', it).splitlines()]
    keep = [l for l in lines if l and not PROMO.match(l)]
    try:
        date = parsedate_to_datetime(tag('pubDate', it)).date().isoformat()
    except Exception:
        date = ''
    # every link in the description is kept (D, 25 Nov 2026), so handouts and other files can later be attached to the listing
    raw = tag('description', it)
    links = list(dict.fromkeys(re.sub(r'[).,;]+$', '', u) for u in re.findall(r'(?:https?://|www\.)[^\s<>"]+', raw)))
    out.append({'title': tag('title', it), 'url': tag('link', it), 'date': date,
                'duration': tag('itunes:duration', it), 'text': '\n'.join(keep), 'links': links})
print(json.dumps({'source': 'https://feeds.soundcloud.com/users/soundcloud:users:111086538/sounds.rss',
                  'count': len(out), 'recordings': out}, ensure_ascii=False, indent=1))
print(f'{len(out)} recordings, {sum(1 for r in out if r["text"])} with descriptions kept', file=sys.stderr)
