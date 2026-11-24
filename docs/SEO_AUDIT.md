# SEO audit — culadasa.com rebuild

24 November 2026. Audited: the Redesign 2 preview (80 pages, https://humex1.github.io/culadasa-website/redesign-2/) and the mirror of the current site (https://humex1.github.io/culadasa-website/). Prepared by Claude for the Mind Illuminated teachers group.

**Scope rule.** The first launch is a mirror of the current site (CLAUDE.md rule 0). Nothing in this audit changes the mirror's look or text. Recommendations marked **[launch]** are invisible plumbing that a faithful migration still needs. Everything else is for the redesign, when the group chooses to go ahead.

---

## 1. The top 10, site-wide

1. **[launch] Remove `noindex` only when the domain points here, and keep it on every preview copy.** Every page of the mirror and both redesigns carries `<meta name="robots" content="noindex">` (80 of 80 pages in Redesign 2; every mirror page via `tools/mirror_build.py` line 148). That is right for previews and fatal if it ships. Make it the first item on the cut-over checklist. At cut-over, delete `/redesign/` and `/redesign-2/` from the published site, so three copies of the same teachings never compete. (Leaving them up with `noindex` plus a canonical would send mixed signals.) Make `noindex` a build switch tied to the launch, not a hand edit.
2. **[launch] Keep the sitemap, robots.txt, PDFs and a 404 page working at the same addresses.** The current site's `robots.txt` points to `https://culadasa.com/sitemap_index.xml`, which lists `page-sitemap.xml` (14 URLs). Both files are mirrored. The redesign has neither, so it needs a generated `sitemap.xml` (and `robots.txt` pointing to it) listing every indexable page, including the new ones: Start here, Learn, Topics, The Book, Conversations, About. The redesign also has no `wp-content/` folder: its PDF links work today only because the mirror is published alongside it. Copy the 28 media files into the redesign at the same paths, and give it its own `404.html` (the mirror's is a WordPress page titled "Page not found - Inspiration Station").
3. **[launch] Use absolute canonical URLs.** The live site's Yoast tags used `https://culadasa.com/…`. The mirror rewrote them to relative `./`, and the redesign has no canonical at all (the two redirect stubs have relative ones, `../the-book/`, and also carry `noindex`, which contradicts a canonical pointing elsewhere). Use `<link rel="canonical" href="https://culadasa.com/<path>/">` on every page, switched on by the same launch build switch. On the redirect stubs, the launch version should carry the refresh and the absolute canonical only, with no `noindex`. In the mirror, this is an invisible change and must be listed in `docs/MIRROR_NOTES.md` (rule 6).
4. **Don't publish placeholder teacher profiles.** 60 profile pages average 53 words, and the real ones read "[Biography to come …]". Google's January 2025 rater-guideline changes rate pages with little or no original content as low quality, and Lily Ray's reported view is that a high share of thin pages drags down the whole site. (These are thin pages, not "scaled content abuse", which targets content mass-produced to manipulate rankings.) Until a teacher's details arrive, either keep the profile `noindex` and out of the sitemap, or don't build it. Delete the 12 "Sample Teacher" entries (`teachers/sample-teacher-a` to `-l`) before launch: their pages, their cards on the Teachers index, their map pins and their rows in `data/teachers.json`, all in one change.
5. **Add structured data that matches what is visible.** The live site has Yoast JSON-LD (WebPage, WebSite, Organization, BreadcrumbList), but under the wrong name (see 6). The redesign has none. Use `Person` for Culadasa (with `sameAs` to Wikipedia), `Book` on The Book, `Article` with `author` on the essays, and `BreadcrumbList`. Add `VideoObject` only where a video is the main thing on the page (see item 8). Google's May 2025 guidance says markup must match the visible content and be validated. It does not make markup a requirement for AI features.
6. **Fix the site name.** Every live page title reads "… - Inspiration Station" (the old WordPress theme's site title), as do `og:site_name` and the Organization schema. This is what Google shows today. The mirror keeps it, per rule 0. The redesign already uses "— Culadasa". Fix it on the live site as the first agreed change after the mirror launches.
7. **Give every page a descriptive title and description.** Redesign titles are short labels ("Audio — Culadasa", 16 characters; "Topics — Culadasa", 17). Several descriptions are one or two words ("Book reviews", "Student testimonials"). Write titles around what people search for, such as "The Mind Illuminated: the ten stages of meditation — Culadasa", with 120–155-character descriptions.
8. **Make video and Q&A content visible to search.** The 68 videos use a click-to-load preview, so no YouTube player is in the page until someone clicks. The 439 Q&A questions sit inside 61 collapsed sessions on one 27,900-word page, and the generator cuts each question at 400 characters, so 285 of them end in "…" although the full text is in the data (`tools/build_redesign.py` line 467). Show the full questions. Video rich results need the video to be the main content of its page and need an upload date, which `data/videos.json` doesn't hold. So give the main talks their own pages, each with the embed, a summary and `VideoObject`. Don't mark up 68 videos on one listing page. Give the most-asked topics their own headed sections or pages, so a passage can answer a query on its own. Kevin Indig's 2026 data has 44% of ChatGPT citations coming from the first 30% of a page, and Aleyda Solis's checklist stresses chunk-level retrieval.
9. **Stop the pages jumping as they load (Cumulative Layout Shift).** Measured on a phone-sized browser: About 0.505, The Book 0.414, Topics 0.38. Google's "good" threshold is 0.1. Causes found: images without `width`/`height` (the robes photo, the book cover, 134 video thumbnails), the web fonts swapping in the header, and the Topics status line arriving after the data loads. The book cover is also `loading="lazy"` although it is on the first screen. Fix with image dimensions, font preloading or a matched fallback font, and reserved space for the status line. Self-hosting the three font families would also remove the requests to Google's font servers, which helps both speed and privacy.
10. **Show who wrote what and when.** The essays carry no author line or date, and the handout PDFs have titles like "Microsoft Word - beginning meditation 3.docx" in their metadata. Google's helpful-content questions start with "who created it". Add "By Culadasa (John Yates, Ph.D.)" plus the original year or source to each essay, and set proper Title and Author metadata on each PDF.

---

## 2. How the work was checked

| Check | Method | What it found that the others didn't |
|---|---|---|
| 1. Static parse | A Python HTML parser over all 80 built pages: titles, descriptions, headings, canonical, robots, Open Graph, JSON-LD, images, words in `<main>`, internal links (`docs/` script kept in the session scratchpad, results summarised here) | The missing canonicals and JSON-LD, the 53-word teacher pages, the relative `og:image`, duplicate checks (no duplicate titles or descriptions) |
| 2. Live browser crawl | Playwright on the deployed preview at phone size, measuring status, final URL, page weight, Largest Contentful Paint and layout shift; then curl on all 103 internal URLs | The layout-shift scores and their causes; that both meta-refresh stubs land on the right pages; that all 103 internal links and PDFs return 200 (check 1 flagged 33 PDF links as broken; that was a local-folder artefact, and check 2 confirmed they work live) |
| 3. Adversarial | (a) A separate agent audited the code blind, without seeing checks 1–2. (b) Every claim was challenged against the files and research notes. (c) A third agent tried to break the finished report. See §7. | See §7 |

**Limits.**
- Pages could not be fetched from SEO blogs or from Google's documentation: this environment's network blocks those hosts. All expert and Google guidance below comes from web-search summaries, not pages read in full. Each item carries its URL so it can be checked.
- No Search Console data was available, so traffic and query figures are unknown.

---

## 3. Three methodologies

### A. Aleyda Solis (Orainti): migration validation and AI-search readiness
- **Migration.** Her same-domain "URL changes & web migration minimum viable SEO validation" checklist, as summarised, runs in this order:
  1. List the old top URLs.
  2. Confirm each resolves or redirects.
  3. Confirm the destinations are optimised.
  4. Check redirect and canonical chains.
  5. Check that backlinked URLs are covered.

  For unreviewed changes, she compares raw and rendered content, then runs a full old-versus-new crawl. ([checklists](https://aleydasolis.com/en/search-engine-optimization/seo-for-web-migrations/), [2023 post](https://www.aleydasolis.com/en/search-engine-optimization/the-worst-seo-horror-stories-in-2023-and-how-to-wake-up-from-these-nightmares/))
- **AI search.** Her checklist ([page, updated Sep 2026](https://www.aleydasolis.com/en/ai-search/ai-search-optimization-checklist/)) grew from 8 points in June 2025 to 10 steps in July 2025 and 12 steps in September 2026. Steps include:
  - AI crawlability (key content in plain HTML, not behind JavaScript);
  - chunk-level retrieval (self-contained, clearly headed sections);
  - citation-worthiness;
  - topical depth;
  - authority signals;
  - monitoring.

  She frames measurement in three layers: presence, readiness and business impact ([deck, 2026](https://speakerdeck.com/aleyda/redefining-metrics-for-the-ai-search-era-a-3-layer-framework-to-measure-ai-presence-readiness-and-business-impact)).
- **Applied here:**
  - The 14 page paths and 28 PDF paths are the "top URLs".
  - Same-domain, same-path migration means few redirects; the two meta-refresh stubs are the only ones.
  - The Topics search and teacher map are JavaScript-only, which matters for AI crawlers.

### B. Lily Ray (Amsive): E-E-A-T, quality and reputation
- **Quality.** Authorship and expert review are not ranking factors in themselves. They help people and raters judge trust. She cites visible bylines, reviewer credits and last-updated dates as good practice ([SEJ](https://www.searchenginejournal.com/how-to-improve-your-websites-e-a-t/374212/)). She has also said a large share of thin or templated pages is judged at site level ([ppc.land](https://ppc.land/seo-expert-says-websites-lose-rankings-because-theyre-doing-too-much-seo/)).
- **Health content.** Her core-update analyses, Dec 2025 and May 2026, report long-established health sites losing visibility ([ppc.land, Jan 2026](https://ppc.land/health-sites-that-once-dominated-seo-just-got-crushed-by-google/), [Rank Math tracker](https://rankmath.com/google-update/december-2025-core-update/)). Meditation is health-adjacent, so trust signals are hygiene, not protection.
- **AI search.** Her 2025–2026 talks argue that "GEO/AEO/LLMO" extend SEO rather than replace it ([MozCon 2025 report](https://www.stanventures.com/news/seo-still-powers-the-age-of-ai-search-says-lily-ray-5714/)). Her April 2026 experiment showed AI systems repeating a fabricated article ([ppc.land](https://ppc.land/lily-ray-what-the-seo-industry-is-getting-dangerously-wrong-about-ai-search/)). So AI answers about Culadasa will repeat whatever the web says, accurate or not.
- **Reputation.** When a site's self-description and outside sources disagree, raters trust the outside sources ([2020 deck](https://www.slideshare.net/slideshow/actionable-tips-to-increase-your-website-authority-lily-ray/232928167)).
- **Applied here:**
  - Teacher profiles are the site's main thin-content risk.
  - Essays need bylines and dates.
  - About must be accurate and consistent with independent sources such as Wikipedia, and must not overclaim.
  - No step-by-step 2025–2026 audit procedure from her was found. Her method is assembled from her published positions, not a checklist of hers.

### C. Kevin Indig (Growth Memo): content shape for AI citation
- **Findings (2026, as summarised):**
  - 44.2% of ~18,000 ChatGPT citations come from the first 30% of a page ([Growth Memo](https://www.growth-memo.com/p/shorter-focused-content-wins-in-chatgpt), [Search Engine Land](https://searchengineland.com/chatgpt-citations-content-study-469483)).
  - Focused pages beat "ultimate guides".
  - Headings that match how the query is phrased get cited more consistently.
  - Named entities, dates and definite statements correlate with citation.
  - Being mentioned and being cited are different measures ([research summary](https://www.growth-memo.com/p/2026-growth-memo-research-summary)).
  - Within a topic, a small set of domains takes most citations ([Search Engine Land](https://searchengineland.com/chatgpt-citations-domains-study-472349)), so a primary-source archive can be one of them.
- **Topic clusters.** Hubs and spokes with contextual internal links ([BuzzStream podcast summary](https://www.buzzstream.com/blog/topical-authority-podcast/)).
- **Applied here:**
  - The site is the primary source for a named method, so put the definition first on each page.
  - Name the stages and terms in the headings.
  - Link the Learn path, the essays, the Q&A answers and the videos to each other by topic.
  - His views on PDFs, directories and non-commercial measurement were not found and are not attributed to him.

### Google guidance used (search-summary level)
- **Meta refresh.** An instant meta refresh is treated as a permanent redirect and is acceptable when server redirects are impossible ([redirects doc](https://developers.google.com/search/docs/crawling-indexing/301-redirects)). This covers `book-reviews/` and `student-testimonials/`. A 2015 Mueller quote prefers 301s where possible ([SER](https://www.seroundtable.com/google-meta-refresh-type-redirects-19824.html)); on GitHub Pages they are not possible.
- **noindex.** It must be crawlable to work, and robots.txt does not stop indexing ([block-indexing doc](https://developers.google.com/search/docs/crawling-indexing/block-indexing)).
- **Canonicals.** Canonical tags are strong signals and sitemaps weak ones; don't send mixed signals ([canonicalization](https://developers.google.com/search/docs/crawling-indexing/canonicalization)).
- **FAQ rich results.** Restricted in 2023 and reported gone from Search in 2026. The markup is still understood but brings no rich result ([SER](https://www.seroundtable.com/google-drops-faq-rich-results-41298.html), [doc](https://developers.google.com/search/docs/appearance/structured-data/faqpage)).
- **llms.txt.** Google says no AI system it runs uses it ([SER, Jun 2025](https://www.seroundtable.com/google-ai-llms-txt-39607.html)). Low priority.
- **Embedded YouTube.** It can be indexed on the embedding page ([video doc](https://developers.google.com/search/docs/appearance/video)).
- **Helpful content.** The self-assessment opens with "who created the content", bylines where expected, and disclosure of automation ([doc](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)).
- **AI features.** Unique content, page experience, crawl access, and structured data that matches the page ([Search Central blog, May 2025](https://developers.google.com/search/blog/2025/05/succeeding-in-ai-search)).

---

## 4. Measured facts (Redesign 2)

| Page | Title chars | Description chars | Words in main | Layout shift (phone) | Page weight | Notes |
|---|---|---|---|---|---|---|
| Home | 38 | 132 | 408 | 0.018 | 565 KB | 5 images; LCP 1.1 s |
| Start here | 21 | 91 | 266 | 0 | 220 KB | |
| Learn | 16 | 101 | 286 | 0.022 | 220 KB | |
| Topics | 17 | 79 | 70 static (166 after script) | **0.38** | 580 KB | results and cloud need JavaScript |
| Writings | 19 | 49 | 281 | 0.022 | 220 KB | links 21 of the 22 PDFs (`20130322-what-the-buddha-thought-slides-1.pdf` is linked from nowhere) |
| Audio | 16 | 73 | **40** | 0.035 | 219 KB | 6 SoundCloud embeds, almost no text |
| Videos | 17 | 59 | 735 | 0.022 | 383 KB | 68 videos as 73 click-to-load tiles (5 Q&A sessions appear twice) |
| Q&A archive | 22 | 94 | 27,912 | 0 | 284 KB | 61 collapsed sessions, 439 timestamped links |
| The Book | 31 | 95 | 1,116 | **0.414** | 337 KB | cover image has no dimensions |
| Teachers | 19 | 91 | 637 | 0.042 | 389 KB | map needs JavaScript |
| Teacher profiles (60) | ~20–30 | short | **53 median** | n/m | n/m | placeholders |
| Conversations | 24 | 65 | 334 | 0.032 | 220 KB | |
| About | 25 | 94 | 997 | **0.505** | 581 KB | robes photo has no dimensions |
| Testimonials | 23 | 46 | 473 | 0.022 | 220 KB | |
| Essays (5) | 40–55 | 52–67 | 339–2,290 | 0.02–0.04 | ~224 KB | no byline or date |
| book-reviews/, student-testimonials/ | — | 12 / 20 | stub | 0 | — | instant meta refresh is the right method; at launch drop their `noindex` and make the canonical absolute |

Word counts are words inside `<main>` in the static HTML (check 1); a browser count differs by a few percent. All pages: one `<h1>`, `lang="en"`, no duplicate titles or descriptions, all images have `alt`, no JSON-LD, no canonical, `og:image` relative (should be absolute), no Twitter card tags, `noindex` (preview).

---

## 5. Recommendations page by page (top 10 each)

Most important first. **[launch]** = needed for the mirror cut-over without changing how anything looks.

### Home (`/`)
1. [launch] Remove `noindex` at cut-over; absolute canonical `https://culadasa.com/`.
2. Title: "Culadasa (John Yates, Ph.D.) — The Mind Illuminated teachings, free" or similar, under 60 characters.
3. JSON-LD: `WebSite` (name "Culadasa"), `Person` for John Yates with `sameAs` (Wikipedia, publisher page), and `Organization` if the group takes a name.
4. Put a one-sentence definition in the first 30% of the page: who Culadasa was and what the site holds.
5. Use descriptive internal anchor text ("The ten stages", "Q&A archive: 439 answered questions") rather than "Start here" alone.
6. Absolute `og:image` with width and height, plus `twitter:card`.
7. Give the home images `width`/`height` and preload the portrait (the LCP element).
8. Keep the word-cloud links to `topics/?q=…` out of the sitemap, and give Topics a self-canonical so query variants consolidate.
9. Add the newsletter only once it is connected, since a dead form is a trust signal against.
10. Search Console: verify the domain by DNS TXT record (no verification file or tag committed to this public repo) before cut-over, and export the last 16 months of queries and pages as the baseline (Solis: "gather old top URLs"). Keep the exports out of the repo.

### Start here
1. [new URL] Add to the sitemap and link from the home page's first screen (already done).
2. Title around the intent: "How to start meditating with The Mind Illuminated — Culadasa".
3. Open with a 2–3 sentence answer to "where do I begin?" before the steps.
4. Number the seven steps with headings that name what each is ("Step 1: Preparing to practice").
5. Link each step to its handout, essay, recording and Q&A answers (a hub-and-spoke cluster, after Indig).
6. Each PDF linked here gets a proper PDF Title (not "Microsoft Word - …").
7. `BreadcrumbList` JSON-LD.
8. A short "who this is from" line: Culadasa's own handouts, with dates.
9. Description that promises the outcome (120–155 characters).
10. Measure clicks from search to this page as the main beginner metric.

### Learn
1. Title: "Learn The Mind Illuminated method: basics to awakening — Culadasa".
2. Each section heading names the concept (stages, attention and awareness, dullness, jhāna) as people search for it.
3. A one-paragraph definition under each heading, so each section can stand alone as a passage.
4. Link to essays and Q&A answers by topic, not just by format.
5. `BreadcrumbList`; consider `ItemList` for the ordered path.
6. Accented and plain spellings both present in the text ("jhāna (jhana)").
7. Avoid restating Start here: make Learn the deeper path, so the two don't compete for the same query.
8. Show the source and year of each item.
9. Description 120–155 characters.
10. Track which sections earn search entries in Search Console.

### Topics (site search)
1. Self-canonical to `https://culadasa.com/topics/` so every `?q=` variant consolidates; keep `?q=` URLs out of the sitemap.
2. Server-render a static, crawlable list of the top topics with links to their best sources, so the page has content without JavaScript. Today the filters, cloud and results are empty in the HTML and there is no `<noscript>` text.
3. Reserve space for the status line and cloud to remove the 0.38 layout shift.
4. Title: "Search Culadasa's teachings by topic".
5. Consider static topic pages for the 20 most-searched terms (for example `/topics/dullness/`), each opening with a definition in his words and linking to the sources. This is the strongest AI-citation play in Indig's terms. Do it only for terms with real depth, to avoid thin pages.
6. `noindex` any future topic page with fewer than about 3 strong sources.
7. Don't block `/topics/` in robots.txt; the page itself should be indexed.
8. `topics.json` is 1.1 MB. Split it (cloud data first, full texts on first search) to protect speed on phones.
9. Description naming the scale: "172,000 words, 439 recorded questions".
10. Watch Search Console for `?q=` URLs getting indexed. The self-canonical (item 1) is the fix; don't inject `noindex` by script, which is unreliable.

### Writings (handouts and essays index)
1. [launch] All 22 PDF URLs keep their exact paths, including the one Writings doesn't link to (verified: all return 200 on the preview). Copy the files into the redesign itself; today they are served from the mirror's folder.
2. Fix PDF metadata: Title and Author on every PDF (read with `pdfinfo`, which decodes compressed metadata: of all 22 PDFs, 15 say "Microsoft Word - …" or "PowerPoint Presentation" and 7 have none). Label links "(PDF, 240 KB)".
3. Give each handout an HTML landing paragraph (what it covers, when given) next to the link. A bare list of PDFs is thin.
4. Group by topic with headings that name the topics.
5. Title: "Culadasa's handouts and essays on meditation (free PDFs)".
6. `ItemList` or `CollectionPage` JSON-LD.
7. Show year and event for each handout.
8. Consider HTML versions of the most-used handouts, which are easier to cite and read on phones.
9. Link each essay to related Q&A answers.
10. Description 120–155 characters.

### Essays (5 pages: Meditation manual introduction, Mindful awareness vs dullness, Amount of concentration needed for awakening, Daily life practice, Cultivating mindfulness in daily life)
1. [launch] Keep exact URLs (done).
2. Byline "By Culadasa (John Yates, Ph.D.)" and original date or source.
3. `Article` JSON-LD with `author` → the `Person`, `datePublished`, and `isPartOf` the site.
4. A 2–3 sentence summary at the top (first 30% rule).
5. Subheadings inside the longer essays (each has one `h2` across up to 2,290 words) so passages stand alone. Descriptions are 52–67 characters; lengthen to 120–155.
6. Related links at the end: the matching stage, Q&A answers, videos.
7. Titles that keep the essay name and add the topic word where it helps ("Mindful Awareness vs Dullness in Meditation — Culadasa").
8. Canonical absolute.
9. Breadcrumb (Writings → essay).
10. Check none of the text duplicates a PDF word for word without saying so; if it does, say "also available as PDF".

### Audio
1. Only 40 words of text: add a short description of each recording (title, date, what is discussed).
2. Title: "Culadasa audio talks and guided meditations".
3. Add transcripts or summaries for the most important recordings.
4. Lazy-load the 6 SoundCloud players (click to load, like the videos) for speed.
5. `AudioObject` or `PodcastEpisode`-style markup only if each item has a page or clear on-page details.
6. Headings for each recording.
7. Link recordings to their topics.
8. Description naming what is there.
9. Canonical absolute.
10. Keep the legacy URL `/audio/` (done).

### Videos
1. The click-to-load preview hides the players from crawlers, and a 68-video listing isn't eligible for video results anyway. Give the most important talks their own pages (embed, summary, `VideoObject` with name, description, thumbnailUrl, uploadDate and embedUrl). The upload dates come from YouTube, so the group would need to supply them or allow the lookup.
2. Short description under each title, not just the title.
3. Consider a page per major talk with a transcript or summary (YouTube transcripts could not be fetched here; the group may have them).
4. Group with headings by series ("My Journey").
5. Title: "Culadasa videos: talks, My Journey series and Q&A recordings".
6. All 73 thumbnails are lazy (good) but have no `width`/`height`; add them. Their `alt=""` is acceptable because each sits in a labelled button with a visible title.
7. Link to the Q&A archive's timestamps for the Q&A recordings.
8. Description 120–155 characters.
9. Make sure the YouTube channel links back to culadasa.com (off-site, reputation).
10. Keep `/videos/` (done).

### Q&A archive (`/online-meetings/`)
1. [launch] Keep the URL (done).
2. Fix the heading order: the page goes from `h1` straight to `h3`, and each session has two `h3`s (session name and video title). Use `h2` per session, `h3` per question if split. Collapsed `<details>` content is indexed; whether Google weights it lower is debated, so don't rely on it either way.
3. Split into one page per session, or into topic pages, if the group agrees. 27,900 words on one URL can't rank for the 439 separate questions.
4. Show each question in full: 285 of 439 are cut at 400 characters by the generator (line 467). Each links to its YouTube timestamp (done); add a one-line answer summary where possible (high citation value).
5. Title: "Culadasa Q&A archive: 439 meditation questions answered (2019–2021)".
6. Credit Alex's index visibly (done) and get permission confirmed (open item).
7. Don't use `QAPage` or `FAQPage` markup. `QAPage` is for user-submitted answers, and FAQ results are gone. The visible, well-headed text is what counts.
8. Jump links by year and topic at the top.
9. Breadcrumb.
10. Description with the numbers.

### The Book
1. `Book` JSON-LD: name, author `Person` (Culadasa), co-authors, publisher, `datePublished` 2015-10-06, ISBN (9781501156984 for the edition linked), `sameAs` the publisher page.
2. Add `width`/`height` to the cover image and remove its `loading="lazy"` (it is on the first screen) to cure the 0.414 layout shift.
3. Title: "The Mind Illuminated by Culadasa: the ten stages of meditation".
4. A section per stage name, at least as headings, because people search for "stage 4", "stage 6 subduing subtle dullness" and so on. Check the publisher's permission before quoting at length.
5. Reviews: keep them as quoted text with sources. Don't add `Review`/`AggregateRating` markup for them: they are hand-picked quotes, not ratings, and Google's review-snippet rules exclude reviews a site chooses about its own work. (The blind check suggested this markup; see §7.)
6. Buy links open in a new tab (done) and are marked as plain links. Add `rel="sponsored"` only if any become affiliate links.
7. Link to the stages content in Learn.
8. Description 120–155 characters.
9. Breadcrumb.
10. [launch] Keep `/book-reviews/` redirecting to `/the-book/#reviews` by instant meta refresh. At launch drop its `noindex` and make its canonical absolute.

### Teachers (index)
1. The card list is already server-rendered HTML (checked); only the map needs JavaScript. Add a `<noscript>` line under the map pointing to the list.
2. Title: "Find a certified Mind Illuminated teacher near you".
3. Only link profiles that have real content; until then, list the name with the certification year and no profile link. Today the index links all 60.
4. `ItemList` of `Person` entries (name, `url`, `areaServed`) only for real data.
5. Add `width`/`height` to the map container so it doesn't shift.
6. State who certified them and how the list is maintained (trust signal).
7. Description 120–155 characters.
8. Remove "Sample Teacher" entries before launch.
9. Each teacher's own website linked from their profile (earns links back when they reciprocate).
10. [launch] Keep `/teachers/` (done).

### Teacher profiles (60 pages, `/teachers/<name>/`)
1. Don't index placeholders: `noindex` plus out of the sitemap until the teacher sends their details, or don't generate the page.
2. Delete the 12 sample profiles before launch.
3. When filled, each needs 150–300 words in the teacher's own voice, plus a photo, a town or region (never a home address) and how they teach. All of it is supplied and consented to by the teacher (PRIVACY.md).
4. `Person` JSON-LD with `name`, `jobTitle` ("Meditation teacher"), `areaServed` (town or region only), `url`, `sameAs` (their site).
5. Title: "<Name>, Mind Illuminated meditation teacher in <place>".
6. Link back to the teacher's own site and ask them to link to their profile.
7. Breadcrumb (Teachers → name).
8. Description from their bio.
9. Avoid templated sentences repeated across all 60 pages beyond the certification line.
10. Review yearly; remove or mark retired teachers.

### Conversations
1. Each item: date, host, what is discussed, plus a link. 334 words now.
2. Title: "Culadasa interviews and podcasts".
3. `VideoObject`/`PodcastEpisode`-style markup only where the item is embedded or described on the page.
4. Only verified items (as now); no made-up summaries.
5. Link these interviews' hosts back to culadasa.com: outreach for earned links.
6. Fix heading order (`h1` then `h3`, no `h2`).
7. Description 120–155 characters.
8. Breadcrumb.
9. Absolute canonical.
10. Add to the sitemap (new URL).

### About
1. `Person` JSON-LD for John Yates: `birthDate` 1945, `deathDate` 2021, `alumniOf`/`affiliation` only where sourced, `sameAs` Wikipedia.
2. Add `width`/`height` to the photos to remove the 0.505 layout shift.
3. Keep every factual claim consistent with independent sources (Ray's reputation point). Cite them inline where possible.
4. Address what the group wants said about his later years honestly and briefly, if at all. AI answers will draw on outside sources either way. This is a group decision, not an SEO one.
5. State who runs the site now (the teachers group) and give a role contact address supplied by the maintainers. No named individuals' details go in the repo (PRIVACY.md). Who is responsible is a trust signal.
6. Title: "About Culadasa (John Yates, Ph.D., 1945–2021)".
7. Link to the Book, the Teachers and the lineage.
8. Description 120–155 characters.
9. Breadcrumb.
10. Licence statement (Creative Commons) is present; keep it visible.

### Testimonials
1. Keep as quoted text with first names or initials as on the live site (privacy).
2. Don't mark them up as `Review` (self-serving reviews aren't eligible).
3. Title: "What students say about Culadasa's teaching".
4. Date or context for each testimonial.
5. Link to Teachers (the next step for a reader).
6. [launch] Keep `/student-testimonials/` redirecting to `/testimonials/` by instant meta refresh. At launch drop its `noindex` and make its canonical absolute.
7. Description 120–155 characters.
8. Breadcrumb.
9. Absolute canonical.
10. Keep `/testimonials/` (done).

### Mirror of the current site (cut-over only, no visible change)
1. Remove the preview `noindex` (added by `mirror_build.py`) only at cut-over.
2. Restore absolute canonicals (`https://culadasa.com/…`) as Yoast had them, and list the change in `docs/MIRROR_NOTES.md`. The Yoast JSON-LD is intact on all 14 pages. The 16 `epyt-pages/*.html` gallery fragments carry no `noindex`; give them one, since they are not pages.
3. Keep `robots.txt`, `sitemap_index.xml` and `page-sitemap.xml` at the same paths (done). At cut-over, check every listed URL returns 200 and update the `lastmod` dates (they say 2023).
4. Check all 14 page paths and 28 media paths return 200 on the custom domain (Solis's old-versus-new crawl).
5. Add a `CNAME` and enforce HTTPS in GitHub Pages settings.
6. Keep `http://` → `https://` and `www` → apex working (GitHub Pages does this when configured).
7. Submit the sitemap in Search Console the same day; watch Indexing → Pages for 404s for 4–6 weeks.
8. Suggest to the owner that the old WordPress host stay online, read-only, for a week as a fallback. Hosting decisions are theirs (CLAUDE.md rule 3).
9. Record the date of the cut-over so traffic changes can be read against it.
10. After launch, fix "Inspiration Station" in titles as the first agreed change.

---

## 6. Launch checklist (in order)

1. Search Console: verify `culadasa.com` as a domain property; export 16 months of pages and queries.
2. Freeze the URL list: 14 pages, 28 media, sitemap files.
3. Final mirror build; remove preview `noindex`; absolute canonicals.
4. Remove `/redesign/` and `/redesign-2/` from the published site, or keep them `noindex`. If the redesign is what launches: remove the "Draft redesign for review" bar, connect or remove the newsletter form (`action="#"` today), copy in the 28 media files, add `404.html`, `robots.txt` and `sitemap.xml`, and make the noindex a build switch so it can't ship by accident.
5. Point the domain (DNS) only with the owner's confirmation (CLAUDE.md rule 3).
6. Same day: crawl every URL on the live domain for 200s; submit the sitemap.
7. Weeks 1–6: watch Search Console coverage and the queries baseline.

---

## 7. Adversarial review (check 3)

**Part A: blind audit.** A separate agent audited the code and the preview without seeing checks 1 and 2. It agreed on:
- the site-wide `noindex`;
- the missing canonicals and structured data;
- the relative `og:image`;
- the thin and sample teacher pages;
- the missing sitemap and robots.txt;
- the JavaScript-only Topics page;
- the short titles and descriptions.

**It found, and this report now includes:**
- the generator cuts 285 of the 439 Q&A questions at 400 characters, though the full text is in the data;
- the redesign has no `wp-content/` folder and no `404.html` of its own;
- the redirect stubs combine `noindex` with a relative canonical;
- there is no `<noscript>` fallback;
- `topics.json` is 1.1 MB;
- the share image is 298 KB;
- heading order jumps `h1`→`h3` on the Q&A archive and Conversations;
- 134 thumbnails have no dimensions;
- the book cover lazy-loads on the first screen;
- the preview bar and the unconnected form have to go before a redesign launch.

**Where it was wrong (checked against the files):**
- "The mirror has no noindex": false. All 14 mirror pages carry it; the empty `Disallow:` in robots.txt is a different mechanism.
- "Audio has 3 SoundCloud iframes": false. There are 6 players, for 5 distinct playlists.
- It suggested `Review`/`AggregateRating` markup for the book's quoted reviews. That was rejected: they are hand-picked quotes, not user ratings.
- It flagged `&amp;` in the Q&A title as a possible double-escape. It isn't one: `&amp;` in HTML source displays as "&".

**Where check 1 was wrong:**
- It flagged 33 PDF links as broken. That was a local-folder artefact; check 2 found all 103 internal URLs return 200 live.

**Part B: claim challenge.** Every claim was re-tested against the files or the research notes:
- Measured numbers come from the two crawls and are reproducible with the scripts.
- Claims about experts are search-summary level and say so.
- These were cut or softened because they couldn't be backed:
  - a "manual action" risk for review markup;
  - a firm statement that collapsed content ranks lower;
  - any attribution to Kevin Indig of views on PDFs or directories.
- Lily Ray has no published 2025–2026 step-by-step audit. Her section is assembled from her stated positions and is labelled that way.

**Part C: red-team pass on the finished report.** A third agent tried to break this report against the files. Corrections made:
- **Contradictions resolved:**
  - The redirect stubs drop `noindex` at launch.
  - Preview folders are deleted at cut-over, not left up with `noindex`.
- **Advice withdrawn:**
  - `VideoObject` across one 68-video listing (not eligible, and upload dates missing).
  - `QAPage` markup.
  - Script-injected `noindex`.
- **"Scaled content" softened to "thin content".**
- **Privacy guards added:**
  - Search Console verified by DNS, with exports kept out of the repo.
  - A role contact address only.
  - Teacher data supplied and consented to, with no home addresses.
- **Mirror changes:** the canonical change goes in `MIRROR_NOTES.md`; the WordPress host stays the owner's decision.
- **Counts corrected:** 21 of 22 PDFs linked from Writings; 68 videos shown as 73 tiles.
- **Its own claims that were wrong:**
  - It doubted the PDF metadata figures from a raw text scan. `pdfinfo`, which decodes the compressed metadata, confirms 15 generic and 7 empty.
  - Its word counts differ by up to 5% because it counted differently (method now stated).

---

## Sources
Listed inline. All expert and Google sources were seen as web-search summaries; none could be opened in full from this environment.
