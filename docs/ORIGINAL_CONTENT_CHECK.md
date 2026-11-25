# Original site content check: what is missing or hard to find in Redesign 2

Every page, piece of text, link, file, image and playlist of the original culadasa.com (the mirror in `site/`), checked against `redesign-2/`. Tick each item once it has been looked at and a decision made: keep as is, restore, or move somewhere easier to find.

Made by `tools/original_content_audit.py`. Text counts as present when the same words appear anywhere in the redesign (ignoring case, quote marks, dashes and spacing). Line numbers refer to the files in `site/`.


## 1. Where each original page went

| Original page (old menu) | In the redesign | Missing | Edited slightly | Hidden or search-only |
|---|---|---|---|---|
| `/` About (the old home page) | Home page | 0 | 1 | 0 |
| `/online-meetings/` Online Meetings | Footer link only (bottom of every page); not in the menu | 0 | 0 | 1 |
| `/writings/` Teachings › Writings | Footer link only (bottom of every page); not in the menu | 1 | 0 | 0 |
| `/audio/` Teachings › Audio | Footer link only (bottom of every page); not in the menu | 0 | 0 | 0 |
| `/videos/` Teachings › Videos | Main menu › Library | 0 | 0 | 0 |
| `/teachers/` Teachings › Teachers | Main menu › Teachers | 6 | 0 | 0 |
| `/testimonials/` Teachings › Testimonials | Footer link only (bottom of every page); not in the menu | 0 | 3 | 0 |
| `/student-testimonials/` Teachings › Student testimonials | Address kept; it forwards to `/testimonials/` (Footer link only (bottom of every page); not in the menu) | 0 | 3 | 0 |
| `/book-reviews/` Teachings › Book reviews | Address kept; it forwards to `/the-book/` (Main menu › The Book) | 1 | 0 | 0 |
| `/meditation-manual-introduction/` Essay: Introduction to the Meditation Manual | Not in the menu; reached only through links inside pages (Home › /start-here/ › /meditation-manual-introduction/) | 0 | 0 | 0 |
| `/mindful-awareness-vs-dullness/` Essay: Mindful Awareness vs Dullness | Not in the menu; reached only through links inside pages (Home › /start-here/ › /mindful-awareness-vs-dullness/) | 0 | 0 | 0 |
| `/amount-of-concentration-needed-for-awakening/` Essay: Amount of Concentration Needed for Awakening | Not in the menu; reached only through links inside pages (Home › /writings/ › /amount-of-concentration-needed-for-awakening/) | 0 | 0 | 0 |
| `/daily-life-practice/` Essay: How to Maintain Practice in Daily Life | Not in the menu; reached only through links inside pages (Home › /start-here/ › /daily-life-practice/) | 0 | 0 | 0 |
| `/cultivating-mindfulness-in-daily-life/` Essay: Cultivating Mindfulness in Daily Life | Not in the menu; reached only through links inside pages (Home › /learn/ › /cultivating-mindfulness-in-daily-life/) | 0 | 0 | 0 |

"Missing" leaves out things removed on purpose (spam leftovers, a typo, a stray slug); those are still listed below with the reason.

## 2. Item by item


### `/` About (the old home page)

- [ ] **How to find it now:** Home page
- [ ] **In the redesign with small edits** (punctuation or a word or two; 95% the same) (line 270): "His principle teachers were Upasaka Kema Ananda and the Venerable Jotidhamma Bhikkhu, both trained in the Theravadin and Tibetan Karma Kagyu traditions with lineage to the Venerable Ananda Bodhi (later recognized by the …"

### `/online-meetings/` Online Meetings

- [ ] **How to find it now:** Footer link only (bottom of every page); not in the menu
- [ ] **Only findable through Topics search**, not shown on any page (line 269): "Culadasa held monthly video AMA / question and answer meetings on Patreon , a crowdsourcing platform. The videos from these sessions are available on his YouTube site and can be viewed and listened to below."

### `/writings/` Teachings › Writings

- [ ] **How to find it now:** Footer link only (bottom of every page); not in the menu
- [ ] **Link or embed not in the redesign** (line 319): "Introduction to What the Buddha Thought – Slides" → `../wp-content/uploads/2021/09/20130322-what-the-buddha-thought-slides-1.pdf`

### `/audio/` Teachings › Audio

- [ ] **How to find it now:** Footer link only (bottom of every page); not in the menu
- [ ] All of its text, links and media are in the redesign.

### `/videos/` Teachings › Videos

- [ ] **How to find it now:** Main menu › Library
- [ ] All of its text, links and media are in the redesign.

### `/teachers/` Teachings › Teachers

- [ ] **How to find it now:** Main menu › Teachers
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 278): "Recommended Teachers of The Mind Illuminated Meditation System"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 286): "2022 Graduates*:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 288): "2021 Graduates:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 302): "2020 Graduates:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 322): "2019 Graduates:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 333): "2018 Graduates:"

### `/testimonials/` Teachings › Testimonials

- [ ] **How to find it now:** Footer link only (bottom of every page); not in the menu
- [ ] **In the redesign with small edits** (punctuation or a word or two; 99% the same) (line 284): "“I have had the privilege of attending two group meditation retreats given by Master Culadasa. His teachings are clear, comprehensive and easily adopted. I accomplished more in three days with him, than in three months o…"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 284): "“I had meditated for a number of years before I began to study with Culadasa; and, I had had the great fortune to have studied with illustrious teachers. It was Culadasa’s simple and eminently pragmatic understanding of …"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 284): "“Recalling numerous pieces of very clever advice from Upasaka Culadasa’s teachings transformed my month-long shamatha retreat from a frustrating struggle to a fascinating, rewarding challenge. Instead of battling to focu…"

### `/student-testimonials/` Teachings › Student testimonials

- [ ] **How to find it now:** Address kept; it forwards to `/testimonials/` (Footer link only (bottom of every page); not in the menu)
- [ ] **In the redesign with small edits** (punctuation or a word or two; 99% the same) (line 281): "“I have had the privilege of attending two group meditation retreats given by Master Culadasa. His teachings are clear, comprehensive and easily adopted. I accomplished more in three days with him, than in three months o…"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 283): "“I had meditated for a number of years before I began to study with Culadasa; and, I had had the great fortune to have studied with illustrious teachers. It was Culadasa’s simple and eminently pragmatic understanding of …"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 284): "“Recalling numerous pieces of very clever advice from Upasaka Culadasa’s teachings transformed my month-long shamatha retreat from a frustrating struggle to a fascinating, rewarding challenge. Instead of battling to focu…"

### `/book-reviews/` Teachings › Book reviews

- [ ] **How to find it now:** Address kept; it forwards to `/the-book/` (Main menu › The Book)
- [ ] **Text not in the redesign** (`site/book-reviews/index.html` line 265): "HERE’S WHAT PEOPLE ARE SAYING ABOUT THE MIND ILLUMINATED :"

### `/meditation-manual-introduction/` Essay: Introduction to the Meditation Manual

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /start-here/ › /meditation-manual-introduction/)
- [ ] All of its text, links and media are in the redesign.

### `/mindful-awareness-vs-dullness/` Essay: Mindful Awareness vs Dullness

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /start-here/ › /mindful-awareness-vs-dullness/)
- [ ] All of its text, links and media are in the redesign.

### `/amount-of-concentration-needed-for-awakening/` Essay: Amount of Concentration Needed for Awakening

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /writings/ › /amount-of-concentration-needed-for-awakening/)
- [ ] **Removed on purpose** (`site/amount-of-concentration-needed-for-awakening/index.html` line 282): "For those of you who are familiar with the physics of light, it has the characteristics of both a wave and a particle simultaneously. If you design an experiement to reveal its wave-like properties, t". Corrected on purpose: the original misspelling "experiement" is spelled "experiment" in the redesign.

### `/daily-life-practice/` Essay: How to Maintain Practice in Daily Life

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /start-here/ › /daily-life-practice/)
- [ ] All of its text, links and media are in the redesign.

### `/cultivating-mindfulness-in-daily-life/` Essay: Cultivating Mindfulness in Daily Life

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /learn/ › /cultivating-mindfulness-in-daily-life/)
- [ ] **Removed on purpose** (`site/cultivating-mindfulness-in-daily-life/index.html` line 271): "cultivating-mindfulness-in-daily-life". Removed on purpose: a stray web-address slug shown as a heading on the original page.

## 3. Files from the original site that no redesign page links to

They are still kept at their old addresses, so old links and bookmarks work.

- [ ] `wp-content/uploads/2021/09/20130322-what-the-buddha-thought-slides-1.pdf`
- [ ] `wp-content/uploads/2021/09/become_a_patron_button.png` (no page on the original site linked to it either)
- [ ] `wp-content/uploads/2021/09/retrr.jpg` (on the original it was only the logo in hidden search-engine data, captioned "Inspiration Station")

## 4. The original menu, header and footer

- [ ] Old menu item **Culadasa**: now the CULADASA name at the top of every page, which links to Home
- [ ] Old menu item **About**: now split in two: Home (portrait, his wishes, the way in) and the Lineage tab (lineage, wishes, obituary)
- [ ] Old menu item **Online Meetings**: now Library › Culadasa AMA sessions (same address, /online-meetings/)
- [ ] Old menu item **Teachings**: now renamed Library; it holds Writings, Audio, Videos and the Q&A archive
- [ ] Old menu item **Writings**: footer link only
- [ ] Old menu item **Audio**: footer link only
- [ ] Old menu item **Videos**: footer link only
- [ ] Old menu item **Teachers**: in the new menu
- [ ] Old menu item **Testimonials**: footer link only; in the old menu it sat under Teachings next to Book reviews
- [ ] Old menu item **Student testimonials**: now merged into Testimonials (old address forwards there)
- [ ] Old menu item **Book reviews**: now merged into The Book page, section "What teachers and authors say" (old address forwards there)
- [ ] Old footer text "": replaced by the licence line and social links
