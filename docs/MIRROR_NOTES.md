# Mirror notes

`site/` is an exact static mirror of culadasa.com as it was on 24 November 2026. This file lists every way the mirror differs from the WordPress site, all of them under the hood, plus the one visible exception, and how the result was checked.

## What was copied

- All 14 pages, with their HTML exactly as WordPress served it: text, menus, titles (including "Inspiration Station" in the page titles), the footer ("Copyright © 2021. Manage By 24×7 WP Support"), every embed, and every quirk of the live site.
- Every stylesheet, script, font and image the pages load: the Astra theme, Elementor and Elementor Pro, jQuery, Font Awesome, Elementor icons, and the YouTube Embed Plus plugin.
- All 28 files under `wp-content/uploads/2021/09/` (22 PDFs, 6 images), including the ones no page links to, because old links and bookmarks may point at them.
- `robots.txt`, `sitemap_index.xml`, `page-sitemap.xml` and the site icon WordPress served at `/favicon.ico`.
- The live "page not found" page, as `404.html`.

## Differences under the hood (nothing visible)

| What | Why | Where |
|---|---|---|
| Asset addresses are relative (`wp-content/...`, `../wp-content/...`) instead of `https://culadasa.com/wp-content/...` | So the same files work at the preview address and at culadasa.com, and never call the old WordPress server | every page |
| Page links end in `/` (for example `writings/`), as WordPress served them | The copying tool had rewritten them to `writings/index.html` | every page |
| `<head>` links to WordPress-only services removed: RSS feeds, comments feed, REST API, oEmbed, XML-RPC, shortlink | Those services stop existing when WordPress goes. No visitor ever sees these links | every page |
| The video galleries' Next / Prev buttons read saved pages instead of asking WordPress | WordPress answered those requests; a static site cannot. All pages of both galleries were saved on 24 Nov 2026 (`epyt-pages/`) and `assets/epyt-static.js` serves them. The galleries look and behave the same | Online Meetings, Videos |
| Ten Elementor files that load while a page runs (lightbox, dialog, slider styles, small script chunks) were fetched separately | The copying tool only follows tags; these are requested by scripts. Found by recording a browser on every live page | `wp-content/plugins/elementor/` |
| Font files lost a `@version` suffix in their names | GitHub Pages decides file types from names | Elementor and Font Awesome fonts |
| Every page carries `<meta name="robots" content="noindex">` | So search engines do not list the github.io preview as a duplicate of culadasa.com. **Remove at cutover** (one line per page, marked with a comment). Not visible | every page |
| The 404 page loads its styles from `https://culadasa.com/` | It is served for any missing address at any folder depth, so relative addresses would break. Once culadasa.com points here, those addresses are this site | `404.html` |

## The one visible difference

**Phone only, About page.** On the live site, the two photos on the About page float at 250px wide even on a phone, which squeezes the text beside them into a column one or two words wide. Below 545px (the theme's own phone breakpoint) the mirror lets the text run underneath the photo instead. The photo keeps its size and position. Desktop and tablet are unchanged. This is `assets/mobile.css`, one rule; delete the file and its `<link>` to undo it.

## Kept as on the live site, for the group to decide later

These are left exactly as they are, because the mirror changes nothing visible:

- Page titles and link previews say "Inspiration Station" rather than "Culadasa".
- The footer credits "24×7 WP Support".
- On Writings, "Introduction to What the Buddha Thought – Slides" opens the handout PDF, not the slides PDF.
- The "Teachings" menu item links nowhere (`#`); it only opens its sub-menu.
- The Teachers page formats the 2020 names differently from the other years.
- The meditation manual introduction has the typo "develping".
- A Google AdSense loader script is on every page but shows no ads.
- A large empty space sits above the footer on some pages.
- The gallery thumbnails and titles are fixed at what the playlists held on 24 Nov 2026. If videos are added to those YouTube playlists, the galleries need re-saving.

## How it was checked

- **Pixel comparison.** Each of the 14 pages was screenshotted on the live site and the mirror at 1280px (desktop) and 390px (phone), with YouTube, SoundCloud and ads blocked on both so only the pages themselves were compared. 27 of 28 views were identical to the pixel. The 28th is the phone About page, which differs only by the readability fix above.
- **Behaviour.** The Online Meetings gallery was clicked through all 7 pages and the Videos gallery through both pages, with Prev tested and Next hiding on the last page, as on the live site. The desktop menus and the phone menu were opened on both sites. A PDF link was opened.
- **Independence.** Every page was loaded at desktop and phone width, scrolled, and the galleries clicked, while recording every request: no requests to culadasa.com, no files missing, no script errors. The 404 page is the exception by design (see the table above).
- **Phone and tablet.** Every page was checked at 390px and 768px for sideways scrolling and unreadably small text. None found, apart from the About-page squeeze, now fixed.
- **Published copy.** After publishing, every page and file was fetched from https://humex1.github.io/culadasa-website/.

## Rebuilding

Re-copy the live site and re-save the gallery pages, then run:

```
python3 tools/mirror_build.py <wget-copy-folder> <gallery-pages-folder>
```

The exact `wget` command is in the script's header. This only works while the WordPress site is still up.
