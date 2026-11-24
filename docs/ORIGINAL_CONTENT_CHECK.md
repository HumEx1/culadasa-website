# Original site content check: what is missing or hard to find in Redesign 2

Every page, piece of text, link, file, image and playlist of the original culadasa.com (the mirror in `site/`), checked against `redesign-2/`. Tick each item once it has been looked at and a decision made: keep as is, restore, or move somewhere easier to find.

Made by `tools/original_content_audit.py`. Text counts as present when the same words appear anywhere in the redesign (ignoring case, quote marks, dashes and spacing). Line numbers refer to the files in `site/`.


## 1. Where each original page went

| Original page (old menu) | In the redesign | Missing | Edited slightly | Hidden or search-only |
|---|---|---|---|---|
| `/` About (the old home page) | Home page | 0 | 0 | 0 |
| `/online-meetings/` Online Meetings | Main menu › Library › Q&A archive | 0 | 0 | 7 |
| `/writings/` Teachings › Writings | Main menu › Library › Writings | 2 | 0 | 1 |
| `/audio/` Teachings › Audio | Main menu › Library › Audio | 0 | 0 | 0 |
| `/videos/` Teachings › Videos | Main menu › Library › Videos | 0 | 0 | 0 |
| `/teachers/` Teachings › Teachers | Main menu › Teachers | 6 | 0 | 0 |
| `/testimonials/` Teachings › Testimonials | Footer link only (bottom of every page); not in the menu | 0 | 3 | 0 |
| `/student-testimonials/` Teachings › Student testimonials | Address kept; it forwards to `/testimonials/` (Footer link only (bottom of every page); not in the menu) | 0 | 3 | 0 |
| `/book-reviews/` Teachings › Book reviews | Address kept; it forwards to `/the-book/` (Main menu › The Book) | 1 | 0 | 0 |
| `/meditation-manual-introduction/` Essay: Introduction to the Meditation Manual | Not in the menu; reached only through links inside pages (Home › /start-here/ › /meditation-manual-introduction/) | 0 | 0 | 1 |
| `/mindful-awareness-vs-dullness/` Essay: Mindful Awareness vs Dullness | Not in the menu; reached only through links inside pages (Home › /start-here/ › /mindful-awareness-vs-dullness/) | 0 | 0 | 0 |
| `/amount-of-concentration-needed-for-awakening/` Essay: Amount of Concentration Needed for Awakening | Not in the menu; reached only through links inside pages (Home › /writings/ › /amount-of-concentration-needed-for-awakening/) | 0 | 0 | 1 |
| `/daily-life-practice/` Essay: How to Maintain Practice in Daily Life | Not in the menu; reached only through links inside pages (Home › /start-here/ › /daily-life-practice/) | 0 | 0 | 0 |
| `/cultivating-mindfulness-in-daily-life/` Essay: Cultivating Mindfulness in Daily Life | Not in the menu; reached only through links inside pages (Home › /learn/ › /cultivating-mindfulness-in-daily-life/) | 0 | 0 | 0 |

"Missing" leaves out things removed on purpose (spam leftovers, a typo, a stray slug); those are still listed below with the reason.

## 2. Item by item


### `/` About (the old home page)

- [ ] **How to find it now:** Home page
- [ ] All of its text, links and media are in the redesign.

### `/online-meetings/` Online Meetings

- [ ] **How to find it now:** Main menu › Library › Q&A archive
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa August 2020 Patreon Q&A N°1 Recording"
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa January 2020 Patreon Q&A Nº 1 – Sunday"
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa August 2020 Patreon Q&A N°2 Recording"
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa July 2020 Patreon Q&A N°2 Recording"
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa July 2020 Patreon Q&A N°1 Recording"
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa September 2020 Patreon Q&A N°2 Recording"
- [ ] **Present but inside a collapsed section** (shown only when opened) (line 297): "Culadasa April 2020 Patreon Q&A Recording"

### `/writings/` Teachings › Writings

- [ ] **How to find it now:** Main menu › Library › Writings
- [ ] **Text not in the redesign** (`site/writings/index.html` line 312): "Teaching Retreats Handouts"
- [ ] **Text not in the redesign** (`site/writings/index.html` line 341): "Selected Writings from the Jhana_Insight Yahoo discussion board"
- [ ] **Only findable through Topics search**, not shown on any page (line 338): "When Buddhadharma Comes to the West – Part II & III: What the Buddha Taught & Wisdom and Virtue"

### `/audio/` Teachings › Audio

- [ ] **How to find it now:** Main menu › Library › Audio
- [ ] All of its text, links and media are in the redesign.

### `/videos/` Teachings › Videos

- [ ] **How to find it now:** Main menu › Library › Videos
- [ ] All of its text, links and media are in the redesign.

### `/teachers/` Teachings › Teachers

- [ ] **How to find it now:** Main menu › Teachers
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 294): "Recommended Teachers of The Mind Illuminated Meditation System"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 302): "2022 Graduates*:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 304): "2021 Graduates:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 318): "2020 Graduates:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 338): "2019 Graduates:"
- [ ] **Text not in the redesign** (`site/teachers/index.html` line 349): "2018 Graduates:"

### `/testimonials/` Teachings › Testimonials

- [ ] **How to find it now:** Footer link only (bottom of every page); not in the menu
- [ ] **In the redesign with small edits** (punctuation or a word or two; 99% the same) (line 300): "“I have had the privilege of attending two group meditation retreats given by Master Culadasa. His teachings are clear, comprehensive and easily adopted. I accomplished more in three days with him, than in three months o…"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 300): "“I had meditated for a number of years before I began to study with Culadasa; and, I had had the great fortune to have studied with illustrious teachers. It was Culadasa’s simple and eminently pragmatic understanding of …"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 300): "“Recalling numerous pieces of very clever advice from Upasaka Culadasa’s teachings transformed my month-long shamatha retreat from a frustrating struggle to a fascinating, rewarding challenge. Instead of battling to focu…"

### `/student-testimonials/` Teachings › Student testimonials

- [ ] **How to find it now:** Address kept; it forwards to `/testimonials/` (Footer link only (bottom of every page); not in the menu)
- [ ] **In the redesign with small edits** (punctuation or a word or two; 99% the same) (line 297): "“I have had the privilege of attending two group meditation retreats given by Master Culadasa. His teachings are clear, comprehensive and easily adopted. I accomplished more in three days with him, than in three months o…"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 299): "“I had meditated for a number of years before I began to study with Culadasa; and, I had had the great fortune to have studied with illustrious teachers. It was Culadasa’s simple and eminently pragmatic understanding of …"
- [ ] **In the redesign with small edits** (punctuation or a word or two; 100% the same) (line 300): "“Recalling numerous pieces of very clever advice from Upasaka Culadasa’s teachings transformed my month-long shamatha retreat from a frustrating struggle to a fascinating, rewarding challenge. Instead of battling to focu…"

### `/book-reviews/` Teachings › Book reviews

- [ ] **How to find it now:** Address kept; it forwards to `/the-book/` (Main menu › The Book)
- [ ] **Text not in the redesign** (`site/book-reviews/index.html` line 281): "HERE’S WHAT PEOPLE ARE SAYING ABOUT THE MIND ILLUMINATED :"

### `/meditation-manual-introduction/` Essay: Introduction to the Meditation Manual

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /start-here/ › /meditation-manual-introduction/)
- [ ] **Removed on purpose** (`site/meditation-manual-introduction/index.html` line 303): "develping skill in quickly entering effortless one-pointed concentration". Corrected on purpose: the original typo "develping" is spelled "developing" in the redesign.
- [ ] **Only findable through Topics search**, not shown on any page (line 287): "Meditation Manual — Introduction"

### `/mindful-awareness-vs-dullness/` Essay: Mindful Awareness vs Dullness

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /start-here/ › /mindful-awareness-vs-dullness/)
- [ ] **Removed on purpose** (`site/mindful-awareness-vs-dullness/index.html` line 321): "Powered by WooCommerce error". Removed on purpose: left over from hidden spam adverts on the old WordPress pages.

### `/amount-of-concentration-needed-for-awakening/` Essay: Amount of Concentration Needed for Awakening

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /writings/ › /amount-of-concentration-needed-for-awakening/)
- [ ] **Only findable through Topics search**, not shown on any page (line 287): "Exactly how much concentration is needed to attain Awakening?"

### `/daily-life-practice/` Essay: How to Maintain Practice in Daily Life

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /start-here/ › /daily-life-practice/)
- [ ] All of its text, links and media are in the redesign.

### `/cultivating-mindfulness-in-daily-life/` Essay: Cultivating Mindfulness in Daily Life

- [ ] **How to find it now:** Not in the menu; reached only through links inside pages (Home › /learn/ › /cultivating-mindfulness-in-daily-life/)
- [ ] **Removed on purpose** (`site/cultivating-mindfulness-in-daily-life/index.html` line 287): "cultivating-mindfulness-in-daily-life". Removed on purpose: a stray web-address slug shown as a heading on the original page.
- [ ] **Removed on purpose** (`site/cultivating-mindfulness-in-daily-life/index.html` line 303): "Powered by hemp healing products". Removed on purpose: left over from hidden spam adverts on the old WordPress pages.

## 3. Files from the original site that no redesign page links to

They are still kept at their old addresses, so old links and bookmarks work.

- [ ] `wp-content/uploads/2021/09/20130322-what-the-buddha-thought-slides-1.pdf` (no page on the original site linked to it either)
- [ ] `wp-content/uploads/2021/09/become_a_patron_button.png` (no page on the original site linked to it either)
- [ ] `wp-content/uploads/2021/09/retrr.jpg` (on the original it was only the logo in hidden search-engine data, captioned "Inspiration Station")

## 4. The original menu, header and footer

- [ ] Old menu item **Culadasa**: now the CULADASA name at the top of every page, which links to Home
- [ ] Old menu item **About**: now split in two: Home (portrait, his wishes, the way in) and the Lineage tab (lineage, wishes, obituary)
- [ ] Old menu item **Online Meetings**: now Library › Q&A archive (same address, /online-meetings/)
- [ ] Old menu item **Teachings**: now renamed Library; it holds Writings, Audio, Videos and the Q&A archive
- [ ] Old menu item **Writings**: in the new menu
- [ ] Old menu item **Audio**: in the new menu
- [ ] Old menu item **Videos**: in the new menu
- [ ] Old menu item **Teachers**: in the new menu
- [ ] Old menu item **Testimonials**: footer link only; in the old menu it sat under Teachings next to Book reviews
- [ ] Old menu item **Student testimonials**: now merged into Testimonials (old address forwards there)
- [ ] Old menu item **Book reviews**: now merged into The Book page, section "What teachers and authors say" (old address forwards there)
- [ ] Old footer text "Copyright © 2021. Manage By 24×7 WP Support": replaced by the licence line and social links
