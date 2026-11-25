"""An index of The Mind Illuminated for the site search, with short phrases kept within the limits of Google Books' snippet view.

Usage:  python3 tools/build_book_index.py <book.txt> <book-layout.txt> > redesign/data/book.json
        where book.txt is `pdftotext` (reading order) and book-layout.txt is `pdftotext -layout` of the 2015
        first-edition final draft (478 pages). The text comes from the first, the page footers from the second.

The book itself is never in this repository or on the site; it stays in the maintainers' private storage. What is
published is (D, 25 Nov 2026):
  * For a set list of teaching terms (TERMS below): where each mention is (page, part and chapter, heading,
    paragraph on the page, line on the page), and a short phrase around at most three mentions, one per page.
  * For any other word: only the pages it is on (with their chapter and headings), no text.
The phrase limits follow the snippet view the US Court of Appeals found to be fair use in Authors Guild v. Google
(2d Cir. 2015): a short phrase, no more than three per search term, no more than one per page, and one page in ten
never shown (here: every page whose number ends in 0). The Glossary, Notes, Contents and Index pages never show
phrases (like Google, which shows none for dictionaries). Common English words are not indexed at all.
"""
import re, sys, json, unicodedata, collections

SRC, LAYOUT = sys.argv[1], sys.argv[2]
pages_raw = open(SRC, encoding='utf-8', errors='ignore').read().split('\f')          # reading order: the text
pages_lay = open(LAYOUT, encoding='utf-8', errors='ignore').read().split('\f')       # page layout: the footers


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if unicodedata.category(c) != 'Mn').replace('’', "'")


# The teaching terms that get detailed locations and phrases (D, 25 Nov 2026: the cloud terms, the stages, the
# challenges, the Pāli and Sanskrit words, names and titles). Each: shown form, then other spellings (folded).
TERMS = [
    ('jhāna', ['jhana', 'jhanas', 'dhyana']), ('pīti', ['piti']), ('sukha', []), ('samādhi', ['samadhi']), ('samatha', ['shamatha']),
    ('vipassanā', ['vipassana']), ('sati', []), ('mettā', ['metta', 'loving-kindness', 'loving kindness']), ('karuṇā', ['karuna']),
    ('muditā', ['mudita']), ('upekkhā', ['upekkha']), ('dukkha', []), ('anicca', ['impermanence']), ('anattā', ['anatta', 'no-self']),
    ('nibbāna', ['nibbana', 'nirvana']), ('taṇhā', ['tanha']), ('vedanā', ['vedana']), ('saññā', ['sanna']), ('saṅkhāra', ['sankhara']),
    ('viññāṇa', ['vinnana']), ('citta', []), ('nimitta', []), ('kasiṇa', ['kasina']), ('ekaggatā', ['ekaggata']), ('vitakka', []),
    ('vicāra', ['vicara']), ('upacāra', ['upacara', 'access concentration']), ('sampajañña', ['sampajanna']), ('sīla', ['sila']),
    ('paññā', ['panna']), ('ñāṇa', ['nana', 'nanas']), ('sotāpanna', ['sotapanna', 'stream entry', 'stream-entry']),
    ('arahant', ['arhat', 'arahant']), ('dharma', ['dhamma']), ('karma', ['kamma']), ('saṅgha', ['sangha']), ('sutta', ['sutra']),
    ('satipaṭṭhāna', ['satipatthana']), ('ānāpānasati', ['anapanasati']), ('abhidhamma', ['abhidharma']), ('Theravāda', ['theravada']),
    ('Mahāyāna', ['mahayana']), ('Vajrayāna', ['vajrayana']), ('mahāmudrā', ['mahamudra']), ('dzogchen', []), ('rigpa', []),
    ('bodhicitta', []), ('bodhisattva', []), ('saṃsāra', ['samsara']), ('suññatā', ['sunnata', 'sunyata', 'emptiness']),
    ('paṭicca samuppāda', ['paticca samuppada', 'dependent arising', 'dependent origination']), ('nirodha', []), ('kilesa', []),
    ('Buddha', []), ('Ānanda', ['ananda']), ('Māra', ['mara']), ('Nāgārjuna', ['nagarjuna']), ('Śāntideva', ['santideva', 'shantideva']),
    ('rinpoche', []), ('lama', []), ('guru', []), ('Mahasi', []),
    # the method
    ('attention', []), ('peripheral awareness', []), ('introspective awareness', []), ('metacognitive', []), ('mindfulness', []),
    ('awareness', []), ('the breath', []), ('meditation object', []), ('mind-wandering', ['mind wandering']), ('forgetting', []),
    ('gross distraction', []), ('subtle distraction', []), ('strong dullness', []), ('subtle dullness', []), ('dullness', []),
    ('distraction', []), ('exclusive attention', []), ('effortless', []), ('pliancy', []), ('unification', []), ('tranquility', []),
    ('equanimity', []), ('joy', []), ('purification', []), ('the hindrances', ['hindrance', 'hindrances']), ('doubt', []),
    ('sleepiness', []), ('restlessness', []), ('aversion', []), ('craving', []), ('pain', []), ('fear', []),
    ('energy currents', []), ('insight', []), ('awakening', []), ('enlightenment', []), ('the ten stages', ['ten stages']),
    ('milestone', ['milestones']), ('sub-minds', ['sub-mind']), ('mind-system', ['mind system']), ('consciousness', []),
    ('moments of consciousness', []), ('unconscious', []), ('intention', []), ('compassion', []), ('daily life', []),
    ('walking meditation', []), ('body scan', ['body scanning']), ('noting', []), ('labeling', []), ('the four paths', ['four paths']),
    ('fetters', ['fetter']), ('cessation', []), ('dark night', []), ('Dukkha Ñāṇas', ['dukkha nanas']),
]

STOP = set('''a about above after again against all also am an and any are aren't as at be because been before being below between both but by
can can't cannot could couldn't did didn't do does doesn't doing don't down during each even ever every few for from further had hadn't has
hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's however i i'd i'll i'm i've if in into is
isn't it it's its itself just let's like made make makes many may me might more most much must mustn't my myself no nor not now of off on once
one only or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some such than that that's the
their theirs them themselves then there there's these they they'd they'll they're they've this those though through to too two under until up
upon us very was wasn't way we we'd we'll we're we've well were weren't what what's when when's where where's whether which while who who's
whom why why's will with within without won't would wouldn't yet you you'd you'll you're you've your yours yourself yourselves also another
become becomes come comes get gets go goes going instead itself less often rather really still something sometimes thing things three time
times use used uses using want way ways whatever whenever'''.split())

ROMAN = re.compile(r'^[ivxlc]+$')


def footer(line):
    parts = [x for x in re.split(r'\s{2,}', line.strip()) if x]
    num = next((x for x in parts if re.fullmatch(r'[0-9]+|[ivxlc]+', x)), None)
    rest = [x for x in parts if x != num]
    part = next((x for x in rest if x.isupper()), None)
    title = next((x for x in rest if not x.isupper()), None)
    return num, part, title


SMALL = {'a', 'an', 'the', 'and', 'or', 'of', 'in', 'on', 'to', 'for', 'with', 'as', 'at', 'by', 'vs', 'from', 'into', 'is'}


def is_heading(s, prev_blank):
    s = s.strip()
    if not prev_blank or not s or len(s) > 80 or s[-1] in '.,;:?' or '. .' in s or s.isupper():
        return False
    if re.match(r'^(TABLE|FIGURE|Figure|Table|NOTES|\d)', s):
        return False
    w = re.findall(r"[A-Za-zÀ-ɏḀ-ỿ’'-]+", s)
    if not 1 <= len(w) <= 12:
        return False
    return all(x[0].isupper() or x.lower() in SMALL or not x[0].isalpha() for x in w)


# ---------------------------------------------------------------- read every page into lines with their place
# The text is `pdftotext` in reading order (not -layout), so side boxes and captions don't get mixed into the main text.
# Each page ends with its footer: the page number, the part (in capitals) and the chapter title, in some order.
pages, headings = [], []
lines_out = []          # (page_index, heading_index, paragraph, line_on_page, text)
cur_head = None
for pi, raw in enumerate(pages_raw):
    L = [l.rstrip() for l in raw.splitlines()]
    nb = [i for i, l in enumerate(L) if l.strip()]
    if not nb:
        continue
    LL = [l for l in pages_lay[pi].splitlines() if l.strip()] if pi < len(pages_lay) else []
    if not LL:
        continue
    num, part, title = footer(LL[-1])
    # drop the footer's own lines (page number, part, title) from the end of the reading-order text
    foot = set()
    for i in reversed(nb[-4:]):
        t = L[i].strip()
        if t in (num, part, title) or (title and t == title.strip()):
            foot.add(i)
    if not num:
        continue
    if part and title is None:
        # the title may sit just above the part, or the part may stand alone (Introduction, Notes, Glossary)
        pass
    pidx = len(pages)
    section = (part or '').strip()
    no_phrases = (ROMAN.match(num) is not None) or section in ('NOTES', 'GLOSSARY', 'INDEX', 'CONTENTS') or num.endswith('0')
    pages.append({'n': num, 'part': section, 'title': title or '', 'np': no_phrases})
    body = [L[i] for i in range(len(L)) if i not in foot]
    widths = sorted(len(l) for l in body if len(l.strip()) > 20)
    full = widths[len(widths) * 3 // 4] if widths else 60
    para, prev_blank, prev_short, line_no = 0, True, True, 0
    for l in body:
        if not l.strip():
            prev_blank = True
            continue
        line_no += 1
        if not ROMAN.match(num) and is_heading(l, prev_blank):
            cur_head = re.sub(r'\s+', ' ', l.strip())
            headings.append(cur_head)
            prev_blank, prev_short = False, True
            continue
        if prev_blank or prev_short:
            para += 1
        prev_blank = False
        prev_short = len(l) < full * 0.8 and l.rstrip()[-1:] in '.?!”"’:)'
        lines_out.append([pidx, len(headings) - 1 if cur_head else -1, max(para, 1), line_no, l.strip()])

# fill in the chapter title for pages whose footer shows only the part (left-hand pages show part and title on alternate sides)
last = {}
for p in pages:
    if p['part'] and p['title']:
        last[p['part']] = p['title']
for p in pages:
    if p['part'] and not p['title']:
        p['title'] = last.get(p['part'], '')

# the running text of each page, with words broken across lines joined again, and where each line starts in it
page_text = collections.defaultdict(str)
line_start = []
for i, (pidx, h, para, ln, t) in enumerate(lines_out):
    pt = page_text[pidx]
    if pt.endswith('-') and t[:1].islower():
        page_text[pidx] = pt[:-1]
    elif pt:
        page_text[pidx] += ' '
    line_start.append((pidx, len(page_text[pidx]), i))
    page_text[pidx] += t


def line_at(pidx, pos):
    best = None
    for p, start, i in line_start:
        if p == pidx and start <= pos:
            best = i
        elif p == pidx and start > pos:
            break
    return lines_out[best]


# ---------------------------------------------------------------- the detailed terms
folded = {p: fold(t) for p, t in page_text.items()}
terms_out = []
for shown, alts in TERMS:
    forms = sorted({fold(shown)} | set(alts), key=len, reverse=True)
    rx = re.compile(r"(?<![a-z0-9])(?:" + '|'.join(re.escape(f) for f in forms) + r")(?:s|'s|es)?(?![a-z0-9])")
    locs, phrases, used_pages = [], [], set()
    for pidx in sorted(folded):
        for m in rx.finditer(folded[pidx]):
            _, h, para, ln, _ = line_at(pidx, m.start())
            locs.append([pidx, h, para, ln])
            if len(phrases) < 3 and pidx not in used_pages and not pages[pidx]['np']:
                text = page_text[pidx]
                # about nine words either side, cut at word boundaries straight from the text (folding keeps positions)
                b = [x.start() for x in re.finditer(r'\S+', text[:m.start()])]
                e = [x.end() for x in re.finditer(r'\S+', text[m.end():])]
                start = b[-9] if len(b) >= 9 else 0
                end = m.end() + (e[8] if len(e) >= 9 else len(text) - m.end())
                phrase = re.sub(r'\s+', ' ', text[start:end]).strip()
                phrase = re.sub(r'([(“‘"])\s+', r'\1', phrase)
                phrase = re.sub(r'\s+([)”’",.;:?!])', r'\1', phrase)
                phrases.append([len(locs) - 1, ('…' if start > 0 else '') + phrase + ('…' if end < len(text) else '')])
                used_pages.add(pidx)
    if locs:
        terms_out.append({'t': shown, 'f': forms, 'n': len(locs), 'loc': locs, 'ph': phrases})

# ---------------------------------------------------------------- every other word: the pages it is on, nothing more
word_pages = collections.defaultdict(set)
for pidx, t in folded.items():
    for w in re.findall(r"[a-z][a-z'-]{2,}", t):
        w = w.strip("'-")
        if w and w not in STOP and len(w) > 2:
            word_pages[w].add(pidx)
words_out = {w: sorted(ps) for w, ps in sorted(word_pages.items())}
page_heads = collections.defaultdict(list)
for pidx, h, *_ in lines_out:
    if h >= 0 and (not page_heads[pidx] or page_heads[pidx][-1] != h):
        page_heads[pidx].append(h)

def nice(part):
    small = {'of', 'the', 'and', 'a', 'an', 'to', 'in', 'on'}
    w = part.lower().split()
    return ' '.join(x if (i and x in small) else x.capitalize() for i, x in enumerate(w))


out = {'book': 'The Mind Illuminated', 'edition': 'First edition (Dharma Treasure Press, 2015), final draft before printing; page, paragraph and line numbers follow that layout',
       'limits': 'Phrases: at most three per term, one per page; pages ending in 0, the contents, notes and glossary never show phrases (Authors Guild v. Google, 2d Cir. 2015).',
       'pages': [[p['n'], nice(p['part']), p['title'], page_heads.get(i, [])] for i, p in enumerate(pages)],
       'headings': headings, 'terms': terms_out, 'words': words_out, 'stop': sorted(STOP)}
print(json.dumps(out, ensure_ascii=False, separators=(',', ':')))
print(f"{len(pages)} pages, {len(headings)} headings, {len(terms_out)} terms ({sum(t['n'] for t in terms_out)} mentions, "
      f"{sum(len(t['ph']) for t in terms_out)} phrases), {len(words_out)} other words", file=sys.stderr)
