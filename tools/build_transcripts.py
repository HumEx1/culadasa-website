"""Readable, searchable transcripts of Culadasa's YouTube videos, made from YouTube's automatic captions.

Usage:  python3 tools/build_transcripts.py <folder of .vtt caption files>

The caption files were downloaded on 25 Nov 2026 from https://www.youtube.com/@Culadasa/videos with
  yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "en,en-orig,en-US,en-GB" --sub-format vtt
         --sleep-requests 1 --sleep-subtitles 2 --ignore-errors -o "%(upload_date)s %(id)s %(title).80B.%(ext)s"
179 files for 99 videos (43 MB). They are data, so they are kept by the maintainers outside this repository;
this script reads the one "en-orig" file per video (YouTube's own English captions, not a translation).

Writes:
  docs/transcripts/<date>-<video id>.md   one document per video, a time stamp linking into the video about once a minute
  docs/transcripts/README.md              the list of all of them
  redesign/data/transcripts.json          the same text for the search on the Topics page, with time stamps

Nothing is reworded. Rolling caption lines are joined once, and the Pāli terms YouTube mishears are corrected
by tools/caption_corrections.py (the list agreed with D, 25 Nov 2026; see docs/TRANSCRIPTS.md).
"""
import re, sys, json, glob, os, pathlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from caption_corrections import fix

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = sys.argv[1]
SITE_TITLES = {v['id']: v['title'] for v in json.loads((ROOT / 'redesign/data/videos.json').read_text())}


def secs(ts):
    h, m, s = ts.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def lines_of(path):
    """(seconds, text) for each new caption line, in order."""
    raw = open(path, encoding='utf-8').read()
    rolling = '<c>' in raw
    out, last = [], ''
    for blk in raw.split('\n\n'):
        m = re.search(r'(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)', blk)
        if not m:
            continue
        start, end = secs(m.group(1)), secs(m.group(2))
        text = [re.sub(r'<[^>]+>', '', l).strip() for l in blk.split('\n') if '-->' not in l and not l.startswith(('Kind:', 'Language:', 'WEBVTT'))]
        if rolling:
            # YouTube's rolling captions: a cue shows the previous line and then the new one; 10 ms cues only repeat
            if end - start < 0.05 or not text or not text[-1]:
                continue
            text = [text[-1]]
        for t in text:
            if t and t != last:
                out.append((int(start), t))
                last = t
    return out


def hms(s):
    return f'{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}' if s >= 3600 else f'{s // 60}:{s % 60:02d}'


files = sorted(glob.glob(os.path.join(SRC, '*.en-orig.vtt')))
outdir = ROOT / 'docs' / 'transcripts'
outdir.mkdir(parents=True, exist_ok=True)
for old in outdir.glob('*.md'):
    old.unlink()
videos, index, changes = [], [], 0
for f in files:
    name = os.path.basename(f)[:-len('.en-orig.vtt')]
    date, vid, title = name.split(' ', 2)
    date = f'{date[:4]}-{date[4:6]}-{date[6:]}'
    title = SITE_TITLES.get(vid, title)
    url = f'https://www.youtube.com/watch?v={vid}'
    log = []
    ls = [(t, fix(x, log)) for t, x in lines_of(f)]
    changes += len(log)
    # search data: the whole text, and where each time stamp starts in it (one about every 10 seconds)
    text, marks, last_mark = '', [], -99
    for t, x in ls:
        if t - last_mark >= 10:
            marks.append([len(text), t])
            last_mark = t
        text += x + ' '
    videos.append({'id': vid, 'title': title, 'date': date, 'text': text.strip(), 'marks': marks})
    # the document: a paragraph about every minute, each opening with a time stamp that plays the video from there
    paras, cur, cur_t = [], [], None
    for t, x in ls:
        if cur_t is None:
            cur_t = t
        cur.append(x)
        if t - cur_t >= 60 and re.search(r'[.?!]$', x) or t - cur_t >= 90:
            paras.append((cur_t, ' '.join(cur)))
            cur, cur_t = [], None
    if cur:
        paras.append((cur_t, ' '.join(cur)))
    fname = f'{date}-{vid}.md'
    words = len(text.split())
    body = [f'# {title}', '',
            f'Video: {url}  ',
            f'Published on YouTube: {date}  ',
            f'Length of transcript: {words:,} words', '',
            '> Transcribed automatically by YouTube, not by a person, so expect mistakes. Pāli terms YouTube mishears '
            '(jhāna, pīti, mettā and others) have been corrected; nothing else has been changed. '
            'Each time stamp opens the video at that moment. How this was made: [TRANSCRIPTS.md](../TRANSCRIPTS.md).', '']
    for t, p in paras:
        body += [f'**[{hms(t)}]({url}&t={t}s)** {p}', '']
    (outdir / fname).write_text('\n'.join(body), encoding='utf-8')
    index.append((date, title, fname, words, vid in SITE_TITLES))

index.sort(reverse=True)
readme = ['# Video transcripts', '',
          f'{len(index)} of Culadasa\'s videos on YouTube, transcribed automatically by YouTube, with the Pāli terms it mishears corrected. '
          'Newest first. ● marks the videos listed on the site\'s Videos page. How they were made: [TRANSCRIPTS.md](../TRANSCRIPTS.md).', '',
          '| Date | Video | Words |', '|---|---|---|']
readme += [f'| {d} | {"● " if on else ""}[{t.replace("|", "/")}]({fn}) | {w:,} |' for d, t, fn, w, on in index]
(outdir / 'README.md').write_text('\n'.join(readme) + '\n', encoding='utf-8')
videos.sort(key=lambda v: v['date'], reverse=True)
(ROOT / 'redesign/data/transcripts.json').write_text(json.dumps({'videos': videos}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'{len(videos)} transcripts, {sum(len(v["text"].split()) for v in videos):,} words, {changes} Pāli corrections', file=sys.stderr)
