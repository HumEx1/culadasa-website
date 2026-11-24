# Design refresh options

Three light-refresh directions for culadasa.com, drawn on 24 November 2026 as home-page mock-ups on a design canvas (private to the maintainers until shared). All three keep the same page structure, menu and content as the faithful rebuild in `site/`; only the look changes. Each is a complete token set so whichever is chosen can be applied to `site/assets/style.css` without further decisions.

The brief from Darin: tasteful, minimalist, zen and spiritual but modern; science meets Buddhism, not "tech bro"; one option built from the cover of *The Mind Illuminated* (gold ground, teal geometric cubes, serif small-caps title).

## Option A · Illuminated (from the book)

| Token | Value |
|---|---|
| Ground | `#F5EFE2` parchment; panels `#FBF8F1` |
| Ink | `#1E2A33`; body text `#3A464F`; muted `#5B6670` |
| Accent 1, gold | `#C4972F` rules and frames; `#A07A1F` for small-caps labels (4.6:1 on the ground) |
| Accent 2, teal | `#1F8A84` links and card rules (4.7:1); hover `#15605C` |
| Footer | `#1E2A33` with `#C9C2B2` text, gold wordmark `#E3B84A` |
| Wordmark | Cinzel 600, 34px, letter-spacing .32em, "CULADASA" |
| Headings | Cormorant Garamond 500: h1 46px, h2 34px, line-height 1.15 |
| Body | Source Serif 4, 17px / 1.7 |
| UI, labels, nav | Source Sans 3 600, 12.5–14px, uppercase, letter-spacing .14–.22em |
| Motif | Isometric cube lattice (one SVG pattern) behind the header at 16% gold, fading into the ground |
| Spacing | 1120px container; section padding 56–72px; 1px `#D9CDB3` section rules |

Motivation: carries the visual memory of the book that most visitors arrive from. Tradeoff: the warmest and most decorated of the three, so it needs the most discipline to stay minimal; Cinzel can read as "epic" if used anywhere other than the wordmark.

## Option B · Clear Light (zen modern, science meets Buddhism)

| Token | Value |
|---|---|
| Ground | `#FAFAF9` |
| Ink | `#1A1C1E`; body `#3B4046`; muted `#6B7075` (5.1:1); hairlines `#E3E4E2` |
| Accent | `#3D5A73` slate-indigo for links (6.8:1); hover `#2D4457`; primary button is ink on ground |
| Display | IBM Plex Serif 300: h1 58px / 1.12, h2 34px / 1.2, pull quote 26px / 1.4 |
| Body and UI | IBM Plex Sans 400/500: body 17px / 1.75, nav 15px, labels 13px uppercase .08em |
| Imagery | Portraits in greyscale |
| Layout | Left-aligned; 1120px container; a 3/8 grid with section labels in the left rail on a short black rule; prose measure 640px; 88–96px between sections |

Motivation: the quietest and most "research institute" of the three; Plex comes from scientific and engineering typography without reading as a start-up. Tradeoff: the greyscale portraits and the cool palette may feel austere for a memorial site; a single warm accent could be swapped in.

## Option C · Still Water (low-key colours, one pop)

| Token | Value |
|---|---|
| Ground | `#EFEDE8` stone; panel `#F7F5F0` |
| Ink | `#2B2B2B`; body `#55524B`; muted `#7A766D` (4.6:1); hairlines `#D6D2C8` |
| Pop | `#D9532B` persimmon, used only as a dot in the wordmark, a dot before "Remembering Culadasa", and hover states. Alternatives offered as a tweak: `#B8860B` gold, `#2F7F6F` jade, `#4F5FAE` indigo |
| Display | Instrument Serif 400: h1 68px / 1.06, h2 34–40px / 1.1, italic for attributions |
| Body and UI | Albert Sans 400/500: body 17px / 1.75, nav 14.5px, labels 13px uppercase .12em |
| Layout | Centred hero; 1080px container; entry list with 44px circular arrows; legacy on a lighter panel; two-column obituary and biography; 96–120px between sections |

Motivation: the most restful; colour is almost absent so the one point of persimmon lands. Tradeoff: large Instrument Serif at 68px needs the balanced line-wrapping to hold on phones (set in the mock-up); a stone ground shows photographs slightly warmer.

## Self-critique against the brief (design-critique framework)

- **First impression.** A reads "the book"; B reads "a quiet institute"; C reads "a place to sit down". All three put the legacy statement, not navigation chrome, first.
- **Usability.** Each adds a three-entry "teachings" row (Writings, Audio, Videos) on the home page, which the 2021 site lacked; visitors otherwise had to find the Teachings dropdown. Nav stays seven items at phone width by wrapping. Touch targets are 44px or more.
- **Hierarchy.** One large serif statement per page, then labels in small caps, then prose at a 600–640px measure. The old site had no hierarchy at all below the wordmark.
- **Consistency.** Each option is one type pairing and at most two accents, so it can be written as a token block at the top of `style.css`.
- **Accessibility.** All text colours listed pass 4.5:1 on their grounds; muted labels were darkened to pass. Persimmon in C is never the only carrier of meaning.
- **Risks to decide.** A: keep Cinzel to the wordmark only. B: greyscale photos or colour. C: which pop colour.

## How a chosen option gets applied

Only after the group agrees to a redesign. The live look is kept as an exact mirror until then (Darin's rule, 24 Nov 2026). A redesign would be a new set of pages built from the mirror's content, reviewed side by side with it. The home-page "teachings" row is an addition to the content and needs the group's agreement before it goes live.

---

## Options built from the cover of *The Mind Illuminated* (added 24 November 2026)

Darin asked for two more directions that use the actual cover image, one heavily and one lightly. Source: a high-resolution cover scan (2244 × 2775 px) from the maintainers' Dropbox. Six pieces were cut from it, avoiding all printed text:

| Piece | Cut from the cover | Size used |
|---|---|---|
| Gold cloud band | top edge, full width | 2244 × 195 |
| Teal cube band | the cube row between "The" and "MIND", clouds at both ends | 2244 × 177 |
| Glowing cube band | the cube row under "ILLUMINATED", with the peach glow | 2244 × 165 |
| The eyes | the Buddha's closed eyes, full width | 2000 × 518 |
| Cloud corners | two cloud patches from the left and right margins | 344 × 480, 330 × 820 |

Colours sampled from the cover: gold ground `#E7D7AE`, cloud-line brown `#9E7B52`, cube teal `#61A0B4` (darker `#4D94AE`), eyes ground `#F7F7F5`.

**Rights.** The cover artwork belongs to the book's publisher. These crops are used only in the private mock-ups and are **not committed to this public repository**. Using them on the live site needs the publisher's permission, or the family's confirmation that it is covered. Option E leans on the art least, so it is the easiest to swap to an original texture if permission is not given.

### Option D · The Cover (heavy)

| Token | Value |
|---|---|
| Header | Gold cloud band as the full header background; teal cube band directly below as its lower edge |
| Hero | The cover's own composition: legacy quote in large serif, then the eyes full width, faded top and bottom into `#F7F7F5` |
| Dividers | Glowing cube band between hero and the teachings row |
| Footer | Gold cloud band again |
| Ink | `#2A241C`; body `#4A4033`; labels `#6B5332` (5.1:1 on gold, 6.6:1 on cream) |
| Links | `#226A7E` (5.6:1); card rule `#4D94AE` |
| Wordmark and labels | Cormorant SC 700 / 600, echoing the cover's small-caps author line |
| Headings | Cormorant Garamond 500: h1 54px, h2 36px |
| Body | Crimson Pro 19px / 1.65 |
| Nav | Jost 600, 13px uppercase, .16em, a nod to the cover's geometric title face |
| Portraits | Framed with an 8px cream mat and a 1px rule |

Motivation: unmistakably the book; anyone who has read it recognises the site at once. Tradeoff: the most image-heavy (about 0.6 MB of cover art on the home page) and the most dependent on the publisher's permission.

### Option E · Dawn (light)

| Token | Value |
|---|---|
| Colour | A single 18px strip of the glowing cube band under the header is the only colour on the page |
| Hero | One light serif line, then the eyes at 720px wide, faded at every edge with a radial mask so they float on the page |
| Footer | Gold cloud band at 22% opacity behind the footer text |
| Ground | `#FAF8F4`; ink `#24211D`; body `#45413B`; muted `#6F6A61` (5.0:1) |
| Links | `#226A7E` teal with a pale `#A9CDD8` underline |
| Type | Newsreader (300 display, 400 body, 19px / 1.7) with Jost 500 for nav and labels |
| Layout | Left-rail section labels as in Option B; a three-line entry list (Read, Listen, Watch) |

Motivation: the calmest option that still carries the book's identity, in two quiet places. Tradeoff: someone who does not know the book may read the eyes as generic; the cube strip is thin enough to look like a coloured rule at a glance.
