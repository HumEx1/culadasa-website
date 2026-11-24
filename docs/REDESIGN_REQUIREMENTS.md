# Redesign requirements (Darin's list)

Every need Darin listed for the redesign on 24 November 2026, in his order, with how it is met. Status is updated as the work lands; the adversarial review checks each line.

| # | Need (Darin's words, lightly condensed) | How it is met | Status |
|---|---|---|---|
| 0 | Keep the old mirror site and design the new one so both can be viewed and compared | Mirror stays at the root address; redesign at `/redesign/`; a side-by-side compare page at `/redesign/compare/` | in progress |
| 1 | A sans-serif version of designs A and D | Options A2 and D2 on the design canvas | done |
| 2a | A more logical, modern layout that feels like a living Buddhist teaching / coaching site. Tasteful, minimal, modern. *Base design updated by #11: a combination of A2 and D2, not D2 alone* | `/redesign/` | in progress |
| 2b | Email capture | Sign-up form on every page (not connected to a mailing service yet; see decisions) | in progress |
| 2c | Social media icons: Facebook, YouTube (and SoundCloud, Patreon) | Footer icons | in progress |
| 2d | "Whatever else" a site like this needs | Start here path, The Book page, Q&A archive | in progress |
| 2e | Search the web for interesting content (podcasts, interviews with other people, like mindful.org) and add to a blog page | Conversations page, verified items only | in progress |
| 2f | A nicely laid-out TOPICS page: search every teaching as deeply as possible, a word cloud, and a search box that ranks content by how often it mentions the word (no further rules on surfacing) | Topics page over 191,000 words: 21 handouts, 5 essays, About, 61 Q&A sessions (439 questions), 2 interview transcripts, all video titles | in progress |
| 2g | Try a few other pages sites like this use, populated with real Culadasa content from across the web | Start here, The Book, Q&A archive, Learn hub | in progress |
| 3 | Check all the work three different ways, adversarially, trying to prove there are better ways; make sure all old content is there (YouTube and SoundCloud playlists and individual videos) | Three independent reviews: content completeness, design and user journey, technical; findings fixed or listed | to do |
| 4 | Present the links here | Final message | to do |
| — | Make decisions without asking; keep a list for review | `DECISIONS_FOR_REVIEW.md` in HumEx1/Claude `Culadasa_Website/` | in progress |
| — | Remove the old links to the site from this conversation and the artifact menus; only the new one should appear | Old private preview artifact deleted; only the GitHub Pages links given from now on | to do |
| 5 | A teachers page where each teacher gets a bio page with photos; mock some up | Teachers directory plus individual profile pages | to do |
| 6 | Find the old version of dharmatreasure.org in a web archive; take all teacher profiles and images; store on GitHub (photos on Dropbox if needed) | Wayback Machine; public details only (name, bio, photo, city or region) | to do |
| 7 | Remove information the teacher pages make redundant | The plain year-by-year name list becomes the directory | to do |
| 8 | On the same page, a map of all teachers' locations and "find a teacher near you" | OpenStreetMap map (no API key) with "use my location" and a place filter | to do |
| 9 | Look at mindful.org/category/learn for ideas; cherry-pick, don't over-engineer; focus on the user: a user journey, the basics, well-organised content, easy-to-find topics, teachers easy to explore and find; the teacher-who-is-a-neuroscientist angle | Learn hub and journey; see decisions | to do |
| 10 | Use tonally related banner headers to add impact and clarity where needed; pages need not all be white like D2 | Coloured page banners drawn from the cover palette (teal, gold, deep ink) on section and page heads | in progress |
| 11 | Make the working redesign a combination of A2 and D2: lead with his big picture as in A2, use some of D2's textures and graphics, combined in a tasteful, minimalist way with some pops of tonally complementary colour so it doesn't look too hippy. Keep it restrained | Home opens with A2's large framed portrait beside the legacy quote; D2's gold clouds (header, footer) and cube bands as dividers; the eyes used once; Jost headings with Source Sans 3 body; teal as the main colour, one muted terracotta for small accents | in progress |
| 12 | Add a page for *The Mind Illuminated* book, with the reviews on it | `/redesign/the-book/` in the main menu, with all 11 reviews; the old reviews address forwards there | in progress |
| 13 | Show a mock-up of one of the pages once clicked through | Screenshot of an inner page sent in the conversation | in progress |
| — | Make sure it is good for mobile viewing | Checked at 390px and 768px on every page | applies to all |
| — | Mirror rule: the initial migration is an exact copy of the live site | Done and checked (27 of 28 views pixel-identical; the 28th is a phone-only readability fix) | done |
