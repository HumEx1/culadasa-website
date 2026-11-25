# Redesign requirements (Darin's list)

Every need Darin listed for the redesign on 24 November 2026, in his order, with how it is met. Status is updated as the work lands; the adversarial review checks each line.

| # | Need (Darin's words, lightly condensed) | How it is met | Status |
|---|---|---|---|
| 0 | Keep the old mirror site and design the new one so both can be viewed and compared | Mirror stays at the root address; redesign at `/redesign/`; a side-by-side compare page at `/redesign/compare/` | done — two separate addresses; compare page removed at D's request |
| 1 | A sans-serif version of designs A and D | Options A2 and D2 on the design canvas | done |
| 2a | A more logical, modern layout that feels like a living Buddhist teaching / coaching site. Tasteful, minimal, modern. *Base design updated by #11: a combination of A2 and D2, not D2 alone* | `/redesign/` | done |
| 2b | Email capture | Sign-up form on every page (not connected to a mailing service yet; see decisions) | done, not yet connected to a mailing service |
| 2c | Social media icons: Facebook, YouTube (and SoundCloud, Patreon) | Footer icons | done |
| 2d | "Whatever else" a site like this needs | Start here path, The Book page, Q&A archive | done |
| 2e | Search the web for interesting content (podcasts, interviews with other people, like mindful.org) and add to a blog page | Conversations page, verified items only | done — 8 verified items |
| 2f | A nicely laid-out TOPICS page: search every teaching as deeply as possible, a word cloud, and a search box that ranks content by how often it mentions the word (no further rules on surfacing) | Topics page over 191,000 words: 21 handouts, 5 essays, About, 61 Q&A sessions (439 questions), 2 interview transcripts, all video titles | done — accent-insensitive; counts match the cloud |
| 2g | Try a few other pages sites like this use, populated with real Culadasa content from across the web | Start here, The Book, Q&A archive, Learn hub | done |
| 3 | Check all the work three different ways, adversarially, trying to prove there are better ways; make sure all old content is there (YouTube and SoundCloud playlists and individual videos) | Three independent reviews: content completeness, design and user journey, technical; findings fixed or listed | done — three reviews; fixes applied (see decisions) |
| 4 | Present the links here | Final message | in progress |
| — | Make decisions without asking; keep a list for review | `DECISIONS_FOR_REVIEW.md` in HumEx1/Claude `Culadasa_Website/` | done |
| — | Remove the old links to the site from this conversation and the artifact menus; only the new one should appear | Old private preview artifact deleted; only the GitHub Pages links given from now on | done — old preview deleted; both sites added to the artifacts menu as launchers |
| 5 | A teachers page where each teacher gets a bio page with photos; mock some up | Teachers directory plus individual profile pages | partly — directory and profile pages built; real bios and photos blocked (see 6); two samples show the layout |
| 6 | Find the old version of dharmatreasure.org in a web archive; take all teacher profiles and images; store on GitHub (photos on Dropbox if needed) | Wayback Machine; public details only (name, bio, photo, city or region) | blocked — web archive not reachable from this session; Dharma Treasure bot check |
| 7 | Remove information the teacher pages make redundant | The plain year-by-year name list becomes the directory | done |
| 8 | On the same page, a map of all teachers' locations and "find a teacher near you" | OpenStreetMap map (no API key) with "use my location" and a place filter | done — map and "near me" built; pins appear as locations are added |
| 9 | Look at mindful.org/category/learn for ideas; cherry-pick, don't over-engineer; focus on the user: a user journey, the basics, well-organised content, easy-to-find topics, teachers easy to explore and find; the teacher-who-is-a-neuroscientist angle | mindful.org itself was unreachable from the server; its structure (what, why, how, basic meditations, beyond the beginning, FAQ) was read from search results. Taken: the beginner path (Start here), a journey by level (Learn), and a FAQ built from the questions people actually asked him most (Start here, "What people asked him most"). Not taken: email courses, articles by others | done |
| 10 | Use tonally related banner headers to add impact and clarity where needed; pages need not all be white like D2 | Coloured page banners drawn from the cover palette (teal, gold, deep ink) on section and page heads | done |
| 11 | Make the working redesign a combination of A2 and D2: lead with his big picture as in A2, use some of D2's textures and graphics, combined in a tasteful, minimalist way with some pops of tonally complementary colour so it doesn't look too hippy. Keep it restrained | Home opens with A2's large framed portrait beside the legacy quote; D2's gold clouds (header, footer) and cube bands as dividers; the eyes used once; Jost headings with Source Sans 3 body; teal as the main colour, one muted terracotta for small accents | done |
| 12 | Add a page for *The Mind Illuminated* book, with the reviews on it | `/redesign/the-book/` in the main menu, with all 11 reviews; the old reviews address forwards there | done |
| 13 | Show a mock-up of one of the pages once clicked through | Screenshot of an inner page sent in the conversation | done |
| 14 | Keep the finished redesign, and make one more live version, redesign (2): home page based on A2 sans; more minimal, fewer graphics, more open, simple and classy, less hippy; coloured banners (Topics not black); some pop on every page; a little structured texture like the lattice behind the A2 title, subtle and only in parts; The Book page keeps the cover's graphics | `/redesign-2/`, built by the same generator with `tools/site2.css` | in progress |
| 15 | Make the page header consistent on every tab except The Book: one tone, or similar tones that vary a little; no mix of pale and coloured headers | One deep teal-to-slate banner family on every page but The Book, a step darker per section along the menu (Start here → About); same type, gold label and terracotta rule everywhere; in redesign (2) the same faint lattice on every banner | done |
| 16 | The Book: no extra graphics row above the menu; a sandy colour block that matches the other banners' texture | Cube row removed; sand block with the same lattice | done |
| 17 | Make the banner colours intentional and consistent (either hierarchy, or a left-to-right fade green → gold (book) → rust with another colour for the content tabs); question the idea and improve it | Colour by purpose, four groups: guidance (Start here, Learn, Topics) teal; library (Writings, Audio, Videos, Q&A, essays) slate; the book sand; people (Teachers, Conversations, About) rust. Menu regrouped so it reads teal → slate → sand → rust left to right; the active tab's underline takes its group colour. Why not a plain gradient: position in the menu means nothing to a visitor, and eight hues look like a rainbow | done |
| — | Make sure it is good for mobile viewing | Checked at 390px and 768px on every page | applies to all |
| — | Mirror rule: the initial migration is an exact copy of the live site | Done and checked (27 of 28 views pixel-identical; the 28th is a phone-only readability fix) | done |

18. **Banner colours as one spectrum (D, 24 Nov 2026).** "Make the colors blend into one color spectrum … like paint color sampler with gold in it's position." Each menu tab gets its own step, left to right: Start here #017890, Learn #007b76, Topics #307c58, Library #5c7637, The Book keeps its sand block (D: "what you have now works well - sandy color"), Teachers #976230, Conversations #a05d46, About #a25a5a. Equal lightness, evenly spaced hues, white text 5:1 or better. Both redesigns. Replaces the purpose groups of item 17.

19. **Mid-century palette for the banners (D, 24 Nov 2026).** "Your tones are too random - use this mid century modern tone swatches." Six tones sampled from D's swatch card: slate #546263, sage #859891, olive #888c65, mustard #ccb069, sand #dbc9ad, terracotta #b6835d. Two deeper shades of the same family cover the remaining tabs: burnt terracotta #8f5f3f and deep slate #3f4b4c. Menu order: Start here slate, Learn sage, Topics olive, Library mustard, The Book sand, Teachers terracotta, Conversations burnt terracotta, About deep slate. White text on the dark steps, deep ink #141c21 on the light ones (all 4.5:1 or better). Replaces the spectrum of item 18.

20. **The CULADASA masthead is the same size on every page (D, 24 Nov 2026).** "Its confusing seeing it change size from home page to tabs." The home page now uses the same compact masthead as the tabs, in both redesigns. The masthead tagline it used to show on home is dropped; the hero's own label says the same thing.

21. **Banners the same height on every tab (D, 24 Nov 2026).** "Make teachers writing box wider to the right so the color banner doesn't grow in height compared to others." The Teachers banner text now runs the full width. Every banner is also at least 305px tall on desktop, so tabs with one line of text match tabs with two. On phones the text has to wrap, so heights still differ there.

22. **About banner in the palette's sand (D, 24 Nov 2026).** "Make about banner sandy as in swatch and change text colors so the text is readable." About is now sand #dbc9ad with deep ink #141c21 text (about 9:1), a terracotta rule and, in Redesign 2, the dark lattice. It replaces the deep slate of item 19.

23. **Conversations redder, About dark green slate (D, 24 Nov 2026).** "Redder brown/rust for conversations and dark green slate for Culadasa (adjust text as needed)." Conversations is now rust #8f4a36 and About (whose banner reads "Culadasa") is dark green slate #3d5048, both with white text (6:1 or better and 8.6:1). This replaces About's sand from item 22.

24. **Learn in a deep mid-century green (D, 24 Nov 2026).** "Instead of grey for LEARN use a deeper mid century modern green … deeper." Learn is now a grey-green #4a5d48 with white text (7.1:1), in place of the sage of item 19. D then asked for "a little grey in it so the tabs flow from left to right … a little greyer": it sits between the slate of Start here and the olive of Topics.

25. **Teachers a lighter apricot (D, 24 Nov 2026).** "Teachers apricot a little lighter." Teachers is now #c4926c (was the palette terracotta #b6835d), with dark ink text at 6.3:1.

26. **Conversations a little redder, still dark (D, 24 Nov 2026).** "Brown/rust a little redder still with dark tones tho." Conversations is now #8c3e31 (was #8f4a36), with white text at 7.4:1.

27. **The large masthead on every page (D, 24 Nov 2026).** "Try the reverse - make all the page tops bigger like the original A2 CULADASA universal banner." Every page, home included, now uses the large masthead: CULADASA at 40px with the line "Upasaka Culadasa · John Yates, Ph.D. · 1945–2021" under it on desktop. On phones the wordmark is 26px and the line is hidden. This reverses the compact choice of item 20; all pages still match.

28. **Header styled as Option A2 on every page (D, 24 Nov 2026).** D sent a screenshot of the A2 header: "Like this." Every page in both redesigns now has one parchment header with CULADASA in Josefin Sans, large and widely spaced; "Upasaka Culadasa · John Yates, Ph.D. · 1945–2021" under it in gold capitals; and the menu between two thin gold rules in bold, letter-spaced capitals, with the current tab in teal. In Redesign 2 the cube lattice runs the full width and fades downwards, as in A2. Redesign 1 keeps its cover clouds and cube band. The name line also shows on phones.

29. **Page background as warm as A2 (D, 24 Nov 2026).** "The whole background was a slightly richer gold/beige too - match that … don't overdo it but match the warmth." The page background in both redesigns is now A2's own #f5efe2 (was #f8f5ee in Redesign 2, #f7f6f2 in Redesign 1); lighter bands use #f9f4e9. Redesign 2's gold labels and the header's name line are darkened a touch, to #7d5f1f, so they still read at 4.5:1 or better on the warmer ground.

30. **Name and dates line lighter, more gold-tan (D, 24 Nov 2026).** "Slightly lighter text and more gold/tan for name and birth/death dates too." The line under CULADASA is now A2's own gold #a07a1f in both redesigns. On the #f5efe2 background it reads at about 3.3:1, below the 4.5:1 guideline for text this size; D chose the look. Other gold labels stay at #7d5f1f.

31. **Start here in a more inviting mid-century modern blue (D, 24 Nov 2026).** "Start here needs a more inviting color. Blue mid century modern?" Start here is now #3d7088 (was slate #546263), with white text at 5.4:1.

32. **About in green heather sage (D, 24 Nov 2026).** "More green heather sage rather than slate in Culadasa at the end." About is now sage #8fa087 with dark ink text at 6.2:1 and, in Redesign 2, the dark lattice. It replaces the dark green slate of item 23. White text was not used because it reads at only 2.8:1 on this sage.

33. **Links open in a new tab (D, 24 Nov 2026).** "Can you dictate that all links are opened in a new tab? On The Book tab the 'publisher' link button should open in a new tab - everything should really." Every link that leaves the site, and every PDF, opens in a new tab: 899 links per redesign, plus the links in Topics search results. This includes "From the publisher", Amazon and the other shops, YouTube, SoundCloud, teacher websites and the handout PDFs. Links between pages of the site itself still open in the same tab (see decision 63). The build tool applies this to every page automatically, so new links follow the rule.

34. **Conversations a little redder and lighter, from a reference palette (D, 24 Nov 2026).** "Search for a modern mid century tonal palette reference that had a red that matches this and use that ratio - doesn't have to change radically." Reference: the "Mustard Vinyl" mid-century palette on media.io (#D6A21E mustard, #C45D4B red, #6C8A7A sage, #2E2B28, #F4E9D8). It holds the same mustard and sage as ours, and its red sits at the same hue as our rust, about 31° in OKLCH. Our palette runs at about 0.82 of that palette's colour strength (mustard compared with mustard). The new rust takes the reference red's hue, nudged 2° redder; that strength ratio (chroma 0.118); and lightness raised 0.05 from the old rust. Result: #a0493e (was #8c3e31), white text at 6:1. One source only: a palette-tool site, not a paint maker's swatch.

35. **Conversations a lighter red (D, 24 Nov 2026).** "Lighter red." The same hue and strength as item 34, lighter: #b15549 (was #a0493e), with white text at 4.9:1. Going any lighter would push white text under 4.5:1.

36. **About becomes Lineage (D, 24 Nov 2026).** "Change the About tab to Lineage page: start with the lineage, then to his wishes, then obit. Use photo like this one of Namgyal Rinpoche … Kema Ananda … top photo." The menu tab and page are now Lineage at `/lineage/`, and `/about/` redirects there. The page opens with the lineage: a teacher-to-student row of Namgyal Rinpoche (Ananda Bodhi), Upasaka Kema Ananda and Upasaka Culadasa, each captioned only with what the site's own lineage text says, followed by that text unchanged. Then comes his wishes and legacy (with "Remembering Culadasa"), then the obituary. Photos: Namgyal Rinpoche from wangapeka.org and Kema Ananda from arrowriver.ca (the top photo on that page), each credited under the image. Permission to use them is still to be confirmed. Topics search now labels this source "Lineage".

37. **Lineage page opens with his large portrait (D, 24 Nov 2026).** "Start with his large green photo at the top as previous and the three below as you have it." The large green-shirt portrait now sits at the top of the Lineage page beside the lineage text, with the three teacher-to-student photos below. The wishes section follows as text only.

38. **Second lineage paragraph, and text alignment (D, 24 Nov 2026).** D's paragraph "For many years, Culadasa taught physiology and neuroscience …" now sits under the lineage text as its second paragraph, word for word as given. The same paragraph was already in the obituary's biography text, so it was moved there rather than repeated. Alignment: every page on the site is left-aligned with a ragged right edge, and no page uses justified text. Long reading pages (the essays, Start here, Writings) centre a 680px reading column, so the Lineage page's wishes and obituary now use that same column. The opening lineage section keeps the photo-beside-text layout used on The Book and Conversations.

39. **Lineage sections separated the site's usual way (D, 24 Nov 2026).** "Delineate the top section and the 3 photos below - how do other sections delineate?" Across the site, sections are separated by alternating background bands: the page's beige, then a slightly lighter panel band with a thin line above and below, each with generous space and its own heading. There are no boxes or heavy rules. The Lineage page now alternates the same way: lineage text and portrait (beige), "From teacher to student" with the three photos (panel band), wishes (beige), obituary (panel band).

40. **Lineage banner text (D, 24 Nov 2026).** The sentence under the Lineage banner now reads, as D wrote it: "His Buddhist lineage, his career in physiology and neuroscience, his wishes for his teachings, and his life. John Yates, Ph.D., 1945–2021."

41. **16th Karmapa as the first lineage link (D, 24 Nov 2026).** "Add 16th Karmapa photo (with Namgyal Rinpoche) as first link in lineage." The "From teacher to student" row now begins with His Holiness the 16th Gyalwa Karmapa, captioned "with Namgyal Rinpoche" and "Whose lineage is traced to the Buddha" (the lineage text's own words). The photo of the two of them together comes from the Ven. Namgyal Rinpoche page on wangapeka.org and is credited under it. Permission is still to be confirmed. There are four links, left to right on desktop and tablet, and stacked with down-arrows on phones.

42. **Teacher profile details aligned (D, 24 Nov 2026).** "Align text." On every teacher page the small labels (Certified, Based in, Teaches, Website) now share a baseline with their values, so each label sits level with its line of text.

43. **Fixes for missing or hard-to-find content (D, 25 Nov 2026)**, from `docs/ORIGINAL_CONTENT_CHECK.md`:
    1. Student testimonials now also sit on The Book page, in their own panel band under the reviews, headed "What his students say about the Mind Illuminated method". The footer link and /testimonials/ page stay.
    2. The Teachers page has the heading "Certified Teachers" above the search and map.
    3. Teacher year groups: left as they are (each teacher shows "Certified <year>").
    4. Writings uses the original group headings again: "Teaching Retreats Handouts" and "Selected Writings from the Jhana_Insight Yahoo discussion board".
    5. The Book reviews heading stays "What teachers and authors say" (a deliberate change from "HERE'S WHAT PEOPLE ARE SAYING ABOUT THE MIND ILLUMINATED").
    6. Essays show their original sub-heading under the title where it differs from the title: "Meditation Manual — Introduction" and "Exactly how much concentration is needed to attain Awakening?".
    7. Writings uses the original link title "When Buddhadharma Comes to the West – Part II & III: What the Buddha Taught & Wisdom and Virtue".
    8. The Q&A archive lists all 61 sessions by year at the top. Each link opens its session. (60 of the 61 are Patreon Q&As, so a Patreon-only list would have repeated the whole archive.)
    9. Writings opens with an "Essays" list of all five essays.

44. **Episode images on Conversations (D, 25 Nov 2026).** Each conversation shows the show's own image for Culadasa's episode, linked to the episode and credited: Guru Viking episodes 35 and 13 (guruviking.com), Deconstructing Yourself DY 022 (deconstructingyourself.com), Buddha at the Gas Pump 394 (its YouTube video's thumbnail), Tricycle Dharma Talks (tricycle.org). The two YouTube talks use their video thumbnails. Alex's Q&A index has no image. Permission to use the show images is still to be confirmed.

45. **The Q&A archive carries Alex's whole index, in the site's design (D, 25 Nov 2026).** "Make this match the website", referring to Alex's Culadasa Q&A Index. Alex's own page is his, so it is unchanged. The Q&A archive (/online-meetings/) now shows the whole index as Alex wrote it, in the site's look:
    - his introduction and contributing note, with his links, in a band headed "By Alex, who transcribed it";
    - all 61 sessions (newest first, plus the index by year) and all 441 questions in full, no longer cut at 400 characters;
    - his 34 quotes from Culadasa's answers, each with its timestamp;
    - his keywords, the linked ones going to their moment in the video.

    The source is saved unedited in `source/qna-index-2026-11-25/` and parsed by `tools/build_qna_index.py` into `redesign/data/qna_index.json`; rerun both on a fresh copy to pick up Alex's later corrections. Permission from Alex is still to be confirmed.

46. **Photo for the Q&A Index on Conversations (D, 25 Nov 2026).** "Find a nice high definition photo." The Culadasa Q&A Index entry on Conversations uses a high-definition still of Culadasa from his April 2018 Q&A session video (YouTube, 1280×720, cropped square). It is credited "Still from his April 2018 Q&A session on YouTube".

47. **Q&A archive leads with the sessions (D, 25 Nov 2026).** "Take off ', a crowdsourcing platform'. All of the below should be the focus and the info currently at the top should be footnotes." The banner sentence now ends "…question and answer meetings on Patreon." The mirror keeps the original wording. The page opens with "All 61 sessions by year", then the search box and the sessions. The credit line and Alex's introduction moved to a "Notes · About this index" band at the foot of the page, after the audio.

48. **Q&A archive as one long page (D, 25 Nov 2026).** Alex's whole index, in the site's look, in this order:
    1. the banner about the Patreon meetings;
    2. a short note in small type that Alex transcribed the questions, with keywords and quotes;
    3. "All 61 sessions by year", whose links jump to each session;
    4. the search box;
    5. every session open, one after another, each with its video beside the questions and an "All sessions ↑" link back to the index;
    6. the audio;
    7. Alex's introduction as notes at the foot.

    Nothing is collapsed any more. It stays on this site (same GitHub repository, moving to the organisation with it) rather than a separate GitHub page.

49. **Transcription information in a pop-up; index heading (D, 25 Nov 2026).** The short note about the transcription at the top and the "About this index" notes at the foot are gone. Below the last session, just above the SoundCloud player, a small "Transcription information" link opens a pop-up with the same information: where the questions, keywords and quotes come from, and the index's own introduction. Nothing on the page itself names Alex. The index heading reads "All 61 Patreon Q&A sessions organized by year".

50. **Search and word cloud cover the whole Q&A index (D, 25 Nov 2026).** "Do all these words now show up in the word cloud and search?" Before this, no. Search was built from an older copy of the index: 439 questions, 21 of 34 quotes, 617 of 645 keywords. `tools/build_topics.py` now reads `redesign/data/qna_index.json`, the same data the Q&A archive shows, so search covers all 441 questions, all 34 quotes and all the keywords. The word cloud is counted from the same text. Its 90 words are unchanged; a few counts moved by one.

51. **Q&A archive made compact (D, 25 Nov 2026).** In order:
    1. the sessions by year;
    2. "Transcription information" just below the 2017 row (opens the pop-up);
    3. the SoundCloud player;
    4. "The sessions", with the search box;
    5. the sessions as compact cards, three to a row on desktop and each as wide as its video. A card shows the video, the session name and the start of the first question. "Show all N questions" opens it out to the full row, video on the left, questions on the right. Every card ends with "Return to main list". A year link opens its card and scrolls to it.

52. **Q&A sessions as horizontal banners (D, 25 Nov 2026).** Each session is one full-width row:
    - the video on the left;
    - on the right, the session name, with "Return to Q&A list" at the far right of the same line;
    - below the name, the start of the first question, then "Open all N questions", which changes to "Close all N questions" once opened.

    Opened, the questions run down the right while the video stays in view on the left. On phones the video sits above the text.

53. **"Close all N questions" at the end of each open session too (D, 25 Nov 2026).** When a session's questions are open, a second "Close all N questions" sits under the last question. Clicking it closes the list and brings the reader back to the top of that session. D: keep the sessions as banners for now.

54. **"Q&A archive" renamed "Culadasa AMA sessions" (D, 25 Nov 2026).** The new name is used for:
    - the Library menu item, the footer link, the page heading and the browser tab;
    - the year index heading, now "All 61 Patreon AMA sessions organized by year";
    - each session's "Return to AMA list";
    - the links and headings on Home, Videos, Learn and Conversations;
    - the Topics filter and result labels, now "AMA".

    The address stays /online-meetings/. Alex's own title, "Culadasa Q&A Index", and the YouTube video titles keep "Q&A", because they are other people's names for their work. The hard-coded "439 questions" on Home and Start here now count from the data (441).

55. **The session being looked at is highlighted (D, 25 Nov 2026).** "Put a gold line around the post you are looking at… expands to the shape of the text box if you open out." The active session gets a thin gold line round the whole banner and a slightly lighter background. The outline grows with the banner when its questions are open. A session becomes active when you click anything in it, open it, play its video, or arrive from a year link. Only one is active at a time.

56. **Clicking a session's name opens its questions (D, 25 Nov 2026).** Each session name is now also the open/close control, and a second click closes it. The "Open all N questions" prompt stays below it. The name turns teal on hover and works from the keyboard. Screen readers are told whether the session is open.

57. **The list at the top marks where you were (D, 25 Nov 2026).** In "All 61 Patreon AMA sessions organized by year", the link of the session last looked at keeps a thin gold outline. That covers the link you clicked, and any session you clicked into lower down. After "Return to AMA list" you can see which one you were on. It moves when another session becomes active and does not persist after leaving the page. Clicking a session's name a second time closes it (already in place).

58. **"AMA" in place of "Q&A" in the site's own words, everywhere (D, 25 Nov 2026).** The leftovers after item 54 were the newsletter blurb on every page, the Home and Audio search descriptions, Learn's mind-system line, and the Q&A Index entry on Conversations (its description, photo credit and image description). All now say AMA. Unchanged: people's own questions, Alex's "Culadasa Q&A Index", and the YouTube and SoundCloud titles.

59. **AMA search results open the session on our page (D, 25 Nov 2026).** In Topics search, an AMA result's title now opens that session on the Culadasa AMA sessions page. The session is scrolled to, opened, outlined in gold and marked in the list at the top. Each question's time link still opens the video at that moment, in a new tab.

60. **Teachers list marks the teacher last looked at (D, 25 Nov 2026).** After opening a teacher's profile and pressing Back, that teacher's card has a thin gold outline. Clicking a pin on the map outlines the matching card. Only one is marked at a time. The browser remembers it for the visit only (cleared when the tab closes) and nothing is sent anywhere.

61. **Videos page joined to the AMA sessions (D, 25 Nov 2026).** The session box's label switches between "Show all 61 sessions" and "Hide the 61 sessions", with a second "Hide the 61 sessions" under the list that closes it and returns to its top. Each session tile reads "N questions · Questions →". The link opens that session on the Culadasa AMA sessions page, opened and marked.

62. **Scoped search (D, 25 Nov 2026).** One search box design used on four pages:
    - **The box:** a field with pills under it for where to search: All · Writings · AMA sessions · Videos.
    - **Where it appears:** on the AMA sessions, Writings and Videos pages it starts with that page's scope selected, and searching opens Topics with that scope. On Topics the old filter buttons are now those same pills.
    - **Behaviour:** the chosen scope stays when you search again. The result count and the status line ("91 mentions of 'jhana' in 25 sources in the AMA sessions") count only that scope. If nothing matches in a scope, it says how many sources match elsewhere.
    - **What each scope covers:** Writings = handouts and essays; Videos = the talk titles (the AMA session videos are under AMA sessions). The Lineage page is searched under All.
    - **Old links:** old addresses such as ?type=qa still work.

63. **Audio in the search (D, 25 Nov 2026).** All 401 of Culadasa's SoundCloud recordings are now searchable by title and by the useful part of their descriptions (question timestamps, retreat summaries, handout notes). The data comes from his public SoundCloud podcast feed, saved in `source/soundcloud-feed-2026-11-25/` with email addresses replaced by `[email]`, and parsed by `tools/build_audio.py` into `redesign/data/audio.json`. Promotional lines are dropped. The scope pills now read All · Writings · AMA sessions · Videos · Audio, and the Audio page has the box with Audio preselected. Results link to each recording on SoundCloud. The searchable total is now about 195,000 words; the banners count it from the data. Still to get, via a SoundCloud login: which of the 26 collections each recording belongs to, and anything the public feed leaves out.

64. **Learn quick links, and the AMA page remembers your place (D, 25 Nov 2026: "do the things you suggested").**
    - **Learn:** a row of quick links under the banner (The basics · The method · The science of mind · Going deeper · Daily life). The section you jump to, or click into, keeps a thin gold outline in that row. Each section has "All sections ↑" back to the row.
    - **AMA sessions:** this device now remembers the last session read (stored in the browser, nothing sent anywhere). On a later visit it is still outlined and marked in the list at the top, without opening or scrolling.
    - **Writings:** no quick links, as recommended; the page has its search box instead.

65. **Search pills switch on and off independently, with Clear on the right (D, 25 Nov 2026).** Writings · AMA sessions · Videos · Audio each toggle on their own, so any mix can be searched together, for example Writings and AMA sessions. "All" is gone. With nothing switched on, the search covers the whole site, and **Clear**, at the right end of the row, switches everything off. The status line names the mix ("368 mentions of 'jhana' in 36 sources in the Writings and the AMA sessions"). The page boxes on AMA sessions, Writings, Videos and Audio start with their own part switched on, have the same Clear button, and carry any mix through to Topics (for example `?type=writings&type=ama`).

66. **Every video searchable by what he says (D, 25 Nov 2026).** The captions of 99 YouTube videos are kept as transcripts in `docs/transcripts/`, with his Pāli terms corrected (list agreed with D: `docs/TRANSCRIPTS.md`). The Videos search, and the whole-site search, now search what he says, not only the titles, and each result opens the video at that moment. Pāli and Sanskrit forms find each other (jhāna/dhyāna, mettā/maitrī, nibbāna/nirvana, and so on). The transcripts are marked as YouTube's automatic captions. Feature for the summary of the new site.
