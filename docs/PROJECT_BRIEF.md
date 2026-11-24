# Culadasa website — project brief

**Sources:**
1. The email thread "Culadasa website", 20–23 November 2026, started by Elizabeth Pugh on the Mind Illuminated Teachers Community Google Group. 18 messages, read in full on 24 November 2026.
2. A Claude chat of about 21 November 2026 in which Darin had the live site culadasa.com analysed page by page and the reply to the thread drafted. Merged here on 24 November 2026.
3. The WordPress export attached to the thread's last message, in this repository at `source/wordpress-export/`.

**Written:** 24 November 2026 by Claude for Darin McFadyen (D). Facts only. **This repository will become public** (GitHub Pages on a free account requires it), so it holds no email addresses, phone numbers, passwords or login details. Contact details and the access inventory are kept privately by D.

---

## 1. The situation

- culadasa.com is the legacy website of Culadasa (John Yates, author of *The Mind Illuminated*), who died in 2021. The site's WordPress title is "Inspiration Station".
- Elizabeth Pugh has kept it up since his death by paying the support company the site ended up with when it went down in his last days: **24x7 WP Support** (24x7wpsupport.com), which hosts the site and holds a support contract with "large payments needed for something every year". It has been expensive and Elizabeth does not have time to maintain it.
- The site is paid up and will stay live for about another year from 20 November 2026. A plan is needed before then.
- No recent content edits. Elizabeth has admin access to the WordPress site and the hosting account and can make exports. Metadata on the live pages shows a last-modified date of 30 June 2023; the footer says copyright 2021.
- Traffic (Elizabeth's analytics screenshot, read by Jesse Fallon): roughly 60–100 visits a month, direct.

## 2. What was decided

| Decision | Who | Status |
|---|---|---|
| Migrate culadasa.com off WordPress to a static site hosted free on GitHub Pages; every existing URL keeps working; look can stay the same or get a light refresh | Proposed by D (21 Nov); backed by Chris Gagne, Li-Anne Tang, Junot Castelyn, Jesse Fallon, Elizabeth Pugh, Mark Pirtle | Agreed |
| D does the migration | D offered; group accepted | Agreed |
| 2–3 people hold independent access to source, registrar, hosting, administration and backups | Li-Anne Tang; D agreed | Agreed in principle, see §4 |
| Ongoing maintenance group with shared accounts (§4) | D proposed 22 Nov; no objections | Proposed, not yet built |
| The site code lives in its own repository (this one), to be transferred to a "Culadasa" GitHub organisation | D, 24 Nov | Done: repository created under HumEx1 pending the organisation |
| After the move, the only recurring cost is the culadasa.com renewal (typically about $15 a year, less for multi-year; not yet checked at GoDaddy) | D | Stated in thread |
| Patreon is left alone for now; its Q&As may be added to the website later to make them searchable | D | Agreed |
| When the site is about to move, Elizabeth will ask 24x7 WP Support about a partial refund of the remaining support contract | Elizabeth | Open |
| Chris Gagne can host the existing WordPress site on his KnownHost reseller account as a fallback | Chris | Offered, not needed if the static move happens |

## 3. Access — summary (details held privately by D)

| Asset | Where | Who has access |
|---|---|---|
| Domain culadasa.com | GoDaddy | Elizabeth Pugh; login to be passed to D. Elizabeth also registered **culadasa.resources** "just in case"; nothing on it; to be transferred or dropped |
| Email on culadasa.com | — | None exists, as far as Elizabeth knows |
| WordPress site and hosting | 24x7 WP Support | Elizabeth (site admin and hosting account) |
| SoundCloud | soundcloud.com, user 111086538 | Elizabeth; login to be passed to D |
| SoundCloud audio files, offline | Physical backup drive mailed by Paulin Elley to Elizabeth | Elizabeth; untested, very large |
| YouTube channel | Culadasa's personal Google account | **Nobody in the group.** Recovery would go through his family |
| Patreon (patreon.com/culadasa) | Culadasa's personal Google account | **Nobody in the group.** Set to collect no money; may need to stay with his estate |

The site only embeds public YouTube playlists and SoundCloud players, so the migration does not need those logins.

## 4. Ongoing maintenance group — D's proposal (22 November 2026)

Not yet built. No objections raised.

- **A new shared Google account** as the contact and login email for everything below; password shared with the group. All passwords in a Google Sheet on that account, shared only with group members; two-factor backup codes in a "Culadasa Website Info" sheet.
- **Domain:** every group member added as a user on the registrar account, auto-renew on (needs a credit card). If GoDaddy's access levels don't allow it, move the name to Namecheap under the new Gmail.
- **Website source:** a free GitHub organisation "Culadasa". GitHub does not allow shared logins, so each member creates a free GitHub account and is added as an owner.
- **YouTube:** every member given owner-level access (blocked until the Google account is recovered).
- **SoundCloud:** login moved to the new Gmail.
- **Patreon:** login moved to the new Gmail, or left with whoever runs it.
- **Backups:** site files on GitHub; anyone in the group can download a copy. D asked Elizabeth to upload the SoundCloud backup drive to the new account's Google Drive as a second copy.
- **Handover note:** a one-page guide to what's where and who has access, with no passwords in it.

## 5. People

| Name | Role |
|---|---|
| Elizabeth Pugh | Has paid for and administered the site since 2021; holds domain, hosting, WordPress and SoundCloud access |
| Darin McFadyen (D) | Doing the migration and setting up the maintenance group |
| Chris Gagne | Technical; backs the plan; KnownHost fallback |
| Li-Anne Tang | Proposed independent access for 2–3 people |
| Mark Pirtle | Suggested using AI tools; supportive |
| Jesse Fallon | Read the traffic figure; supportive |
| Junot Castelyn | Wants to be kept in the loop |
| Ollie Bray | On the thread (changed email address) |
| Alexandra (Ali) Tataryn | Asked to be included |
| Paulin Elley | Made the SoundCloud backup drive; added 23 Nov |
| A family member | Contact for his Google account and Patreon, through Elizabeth |

The recipient list varied from message to message and needs sorting into a defined group. D moved non-commenters to bcc on 21 Nov.

## 6. The existing site

### 6a. From the live pages (Claude chat, c. 21 Nov 2026)

- 14 URLs in the sitemap. No forms, search, shop, logins or comments anywhere.
- Built with **Elementor 4.4.1** (generator meta tag), Google Fonts, YouTube Embed Plus plugin for video. Footer: "Manage By 24×7 WP Support".
- Most pages carry the same SoundCloud profile player at the bottom.

| Menu item | Contents | Media host |
|---|---|---|
| About (home) | Portrait, the family's legacy statement (CC BY), memorial note, obituary, biography, lineage text with a chart image | 2 images on the site |
| Online Meetings | Intro text and a Patreon link; one YouTube player (video ID kwyGPfavfFY); a 9-title Q&A video slider; a SoundCloud playlist and the SoundCloud profile player | YouTube, SoundCloud |
| Teachings › | Parent menu item; links nowhere (`#`) | — |
| › Writings | 26 writings: 21 PDFs and 5 WordPress pages | PDFs on the site under `/wp-content/uploads/2021/09/` |
| › Audio | 4 SoundCloud playlists (Q&A, Teaching Retreats, Guided Meditations, Intensive Retreats) plus the profile player | SoundCloud |
| › Videos | 9 video titles with play-button overlays from the embed plugin, plus a second page | YouTube |
| Teachers | 48 teachers by name only, grouped by graduating year 2018–2022; no photos, bios or links | Text |
| Testimonials | 5 student testimonials; "Student testimonials" is a separate page with the same 5 | Text |
| › Book reviews | 11 reviews, each attributed to a named author or teacher | Text |

### 6b. From the WordPress export of 20 November 2026

`source/wordpress-export/inspirationstation.WordPress.2026-11-20.xml`, 452,806 bytes, WXR 1.2, one author (`[login removed]`). 18 items carry Elementor data (templates: Default Kit, myHeader, myHeaderNew, rightSidebar, myFooter) and there is one custom CSS entry. Page bodies are also present as plain HTML, so the content can be read without Elementor.

**14 published pages, no blog posts.** These URLs are the acceptance list: every one must resolve on the new site.

| URL | Title | Notes |
|---|---|---|
| / | About | Home. "Culadasa's wishes and his legacy": his work to be freely and equally available to all; Creative Commons BY 4.0 linked |
| /online-meetings/ | Online Meetings | |
| /writings/ | Writings | Links to the five essays and the PDF handouts |
| /audio/ | Audio | SoundCloud embeds: playlists 282960661, 283520935, 283729524, 296077102, 967729615 and user 111086538 |
| /videos/ | Videos | YouTube playlists PL5vT0La_cRtIN4640VK9tO6pmgRy4cahy and PL5vT0La_cRtIqGrpKhqUNWq6NPYcMrV00; single videos 2LYa1YCdZH8 and vtWoFpEHTBs (embedyt shortcode) |
| /teachers/ | Teachers | |
| /testimonials/ | Testimonials | |
| /student-testimonials/ | Student testimonials | |
| /book-reviews/ | Book reviews | |
| /meditation-manual-introduction/ | Meditation Manual — Introduction | Essay |
| /mindful-awareness-vs-dullness/ | Mindful Awareness vs Dullness | Essay, ~12k chars |
| /amount-of-concentration-needed-for-awakening/ | (slug as title) | Essay |
| /daily-life-practice/ | (slug as title) | Essay, ~13k chars |
| /cultivating-mindfulness-in-daily-life/ | (slug as title) | Essay |

**28 media attachments**, all under `/wp-content/uploads/2021/09/`: 22 PDF files (reading list; beginning meditation; Light on Meditation; preparation for practice; Offering the Mandala; Satipatthana retreat; jhanas and mindfulness; Leigh Brasington's jhana instructions; Cape Ann retreat; Magic of Mindfulness; Awakening in Daily Life; What Is Enlightenment; Meditation and Insight I, II, III; Insight slides Oct 2012; What the Buddha Thought handout and two copies of its slides; Buddhadharma West parts I and II–III; Meditation and Joy) and 6 images (book-cover portrait in two sizes, a "become a patron" button, two screenshots, `retrr.jpg`). The 21 PDFs counted on the live Writings page plus the duplicate slides upload account for the 22. **The export holds only URLs; the files must be downloaded from the live site.**

External links in page content: Creative Commons, patreon.com/culadasa, 24x7wpsupport.com (footer credit), and two stray commercial links (a CBD salve shop and a WooCommerce support service) that look like host or plugin spam and should not be carried over.

### 6c. Problems to fix during the move (from the live-site analysis)

- **Wrong site name.** Pages declare themselves "Inspiration Station" (e.g. og:title "About - Inspiration Station"); that is what Google and link previews show. Should be "Culadasa".
- **Video IDs hidden.** The Videos page and the Online Meetings slider load videos through plugin JavaScript, so the IDs are not in the page source, and the two slider counters don't match their lists. Replace with standard YouTube playlist embeds (the two playlist IDs above are in the export; confirm them against the live page in a browser).
- **Duplicate link.** On Writings, "Introduction to What the Buddha Thought – Slides" links to the same PDF as item 18.
- **Small leftovers.** The Teachings menu item links nowhere; the Teachers page formats the 2020 names differently from other years; the meditation manual page has a typo ("develping"); the Patreon link may be dead; the 24x7 WP Support footer credit goes.

## 7. How it will be rebuilt

- **Superseded on 24 Nov 2026 by the mirror rule (see 7b).** The original plan here was a plain-HTML rebuild; the site is now an exact static copy of the WordPress pages, with no PHP and no database. Nothing on the site takes input, so finished pages are served as they are.
- **Hosting: GitHub Pages**, the same as Darin's Between The Silence site (GitHub Pages from a public repository with the custom domain pointed at it). Limits checked in the chat: 1 GB site size, 100 GB/month soft bandwidth, no commercial use; all comfortably met. A free account must publish from a **public** repository, which matches the family's CC BY wishes.
- **Alternative considered:** Cloudflare Pages (uncapped bandwidth, 25 MiB per-file limit). Rejected as the first choice because GitHub Pages keeps the site in the same repository as its source.
- **Same addresses.** Pages keep their paths (e.g. `/writings/`), and the PDFs are placed in folders named `wp-content/uploads/2021/09/` so every old link, bookmark and search result still works. Only WordPress's admin and login pages disappear.
- **Licence.** Carry the Creative Commons BY 4.0 notice over.
- **Steps:** (1) archive the current site: all 14 pages, 22 PDFs, 6 images; (2) collect the YouTube and SoundCloud IDs; (3) rebuild as static HTML; (4) check side by side against the live site, URL by URL; (5) point culadasa.com at GitHub Pages (a few DNS records for the bare name and www; check MX records first even though no mailboxes are known); (6) cancel 24x7 WP Support only after the new site has been live and checked.
- **Time.** Build and check about 3–4 hours; DNS change takes effect within hours, up to 48; the HTTPS certificate usually within an hour, up to 24. Realistic end to end: a day or two, governed by handoffs rather than the build.
- **Where the servers are.** GitHub's own servers behind the Fastly content delivery network, so visitors are served from a cache near them.
- **Infrastructure note.** From Claude's cloud container, culadasa.com is blocked by the network allowlist; the media download needs an allowlist change or D's machine.

## 7b. Status, 24 November 2026 (night)

- **Darin's rule: the initial migration is a mirror of the live site.** The first rebuild (plain HTML with fixes and a new stylesheet) was replaced the same day by an exact copy of the live pages and their files, because the group needs to see a faithful job first. Fixes and redesigns come later as separate changes.
- `site/` is that mirror, built by `tools/mirror_build.py` from a full copy of culadasa.com. Every page matches the live site pixel for pixel at desktop, tablet and phone width, except one phone-only readability fix on the About page. Everything that differs under the hood is listed in `docs/MIRROR_NOTES.md`.
- Both video galleries page through all their videos (Online Meetings: 61 videos on 7 pages; Videos: 10 on 2) from saved files instead of WordPress.
- `.github/workflows/pages.yml` publishes `site/` to https://humex1.github.io/culadasa-website/ on every push to main.
- The design directions for a later refresh (A to E) are in `docs/DESIGN_OPTIONS.md`.

## 8. Open items

| Item | Owner |
|---|---|
| Pass GoDaddy and SoundCloud logins to D, coordinating a time for two-factor confirmations | Elizabeth |
| Find the SoundCloud backup drive; get its contents to D and/or cloud storage | Elizabeth |
| Create the shared Google account and the password and backup-codes sheets | D |
| Create the "Culadasa" GitHub organisation; transfer this repository into it; add group members as owners | D |
| Download all 28 media files from the live site | D / Claude |
| Confirm the YouTube playlist and video IDs against the live Videos and Online Meetings pages in a browser | D / Claude |
| Build the static site and verify every URL in §6b | D / Claude |
| Point culadasa.com at the new host; then Elizabeth asks 24x7 WP Support about a refund | D, then Elizabeth |
| Decide what to do with culadasa.resources | Elizabeth |
| Approach his family about recovering Culadasa's Google account (YouTube, Patreon) once the group knows what it needs | Elizabeth with D |
| Tidy the recipient list into a defined maintenance group | D / Elizabeth |
| Later: add the Patreon Q&As to the website | D |
