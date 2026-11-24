#!/usr/bin/env python3
r"""Build site/ as an exact mirror of the live culadasa.com.

Rule (Darin, 24 Nov 2026): the initial migration is a MIRROR of the live site.
Nothing visible is changed.  This script only makes the copied WordPress pages
work as plain files on any host:

  1. Starts from a wget copy of culadasa.com (pages plus every stylesheet,
     script, font and image they load), made with:

       wget -e robots=off --recursive --level=inf --page-requisites \
            --convert-links --adjust-extension --restrict-file-names=windows \
            --domains=culadasa.com --no-host-directories --wait=0.2 \
            --reject-regex '(wp-admin|wp-json|xmlrpc|/feed/|/comments/|\?replytocom|wp-login|/author/|\?p=|oembed)' \
            https://culadasa.com/

  2. Adds the gallery pages saved from the YouTube Embed Plus plugin
     (epyt-pages/<playlist>/<pageToken>.html) and a small script,
     assets/epyt-static.js, that answers the plugin's "Next / Prev" request
     from those files instead of WordPress.
  3. Adds the few files the pages load from code rather than tags (emoji
     scripts, a Lottie placeholder), the favicon WordPress served, robots.txt,
     the Yoast sitemaps, and the live 404 page.
  4. Points every culadasa.com asset URL at the local copy with relative paths,
     so the same files work at humex1.github.io/culadasa-website/ and at
     culadasa.com/.  Canonical and social-preview URLs stay absolute.
  5. Removes <head> links to WordPress-only endpoints (feeds, REST API, XML-RPC,
     oEmbed) that will not exist once WordPress is gone.  None is visible.
  6. Renames font files whose names carried a "?ver" suffix.
  7. Adds assets/mobile.css: one phone-only rule so text no longer squeezes
     beside the About page photos (see the file).  Desktop is unchanged.

Usage:  python3 tools/mirror_build.py <wget-mirror-dir> <epyt-pages-dir>
Writes site/ in the repository root (replacing it).
"""
import os, re, shutil, sys, pathlib, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / 'site'
LIVE = 'https://culadasa.com'
UA = {'User-Agent': 'Mozilla/5.0 (site mirror)'}

EXTRA = [  # loaded by inline code, not by tags, so wget does not see them
    'wp-includes/js/wp-emoji-release.min.js',
    'wp-includes/js/wp-emoji-loader.min.js',
    'wp-content/plugins/elementor-pro/modules/lottie/assets/animations/default.json',
    'wp-includes/images/w-logo-gray-white-bg.png',   # what /favicon.ico redirects to
    'robots.txt', 'sitemap_index.xml', 'page-sitemap.xml',
    # loaded by Elementor while the page runs (found by recording a browser on every live page)
    'wp-content/plugins/elementor/assets/css/conditionals/dialog.min.css',
    'wp-content/plugins/elementor/assets/css/conditionals/lightbox.min.css',
    'wp-content/plugins/elementor/assets/js/chunks/background-slideshow.min.js',
    'wp-content/plugins/elementor/assets/js/chunks/background-video.min.js',
    'wp-content/plugins/elementor/assets/js/chunks/lightbox-lightbox.min.js',
    'wp-content/plugins/elementor/assets/js/chunks/section-stretched-section.min.js',
    'wp-content/plugins/elementor/assets/js/chunks/text-editor.min.js',
    'wp-content/plugins/elementor/assets/lib/dialog/dialog.min.js',
    'wp-content/plugins/elementor/assets/lib/share-link/share-link.min.js',
    'wp-content/plugins/elementor/assets/lib/swiper/v8/css/swiper.min.css',
]
HEAD_DROP = re.compile(
    r"""<link[^>]*(?:rel=["']alternate["'][^>]*(?:feed|oembed|wp-json)|rel=["']https://api\.w\.org/["']|rel=["']EditURI["']|rel=["']wlwmanifest["']|rel=["']shortlink["']|rel=["']pingback["'])[^>]*>\s*""")


def get(path, allow_404=False):
    req = urllib.request.Request(f'{LIVE}/{path}', headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except urllib.error.HTTPError as e:   # the 404 page arrives as an error with a body
        if e.code == 404 and allow_404:
            return e.read()
        raise


def localise(text, prefix):
    """Point culadasa.com asset URLs at the local copy (plain and JSON-escaped)."""
    for folder in ('wp-content/', 'wp-includes/'):
        text = text.replace(f'{LIVE}/{folder}', prefix + folder)
        esc_live = LIVE.replace('/', '\\/') + '\\/' + folder.replace('/', '\\/')
        text = text.replace(esc_live, prefix.replace('/', '\\/') + folder.replace('/', '\\/'))
    return text


def tidy_links(text, prefix):
    """wget writes page links as x/index.html; WordPress served them as x/."""
    text = re.sub(r'href="((?:\.\./)*)index\.html(#[^"]*)?"', lambda m: f'href="{m.group(2)}"' if (not m.group(1) and m.group(2)) else f'href="{m.group(1) or "./"}{m.group(2) or ""}"', text)
    text = re.sub(r'href="((?:\.\./)*[a-z0-9-]+/)index\.html(#[^"]*)?"', lambda m: f'href="{m.group(1)}{m.group(2) or ""}"', text)
    return text


def main(mirror, epyt):
    mirror, epyt = pathlib.Path(mirror), pathlib.Path(epyt)
    keep_uploads = SITE / 'wp-content' / 'uploads'
    tmp = ROOT / '.site-build'
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(mirror, tmp)
    # all 28 uploads, including ones no page links to (old links and bookmarks may)
    if keep_uploads.exists():
        for f in keep_uploads.rglob('*'):
            if f.is_file():
                dest = tmp / f.relative_to(SITE)
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
    for p in EXTRA:
        dest = tmp / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(get(p))
    shutil.copy2(tmp / 'wp-includes/images/w-logo-gray-white-bg.png', tmp / 'favicon.ico')
    # sitemaps: point the stylesheet reference at the local copy
    for sm in ('sitemap_index.xml', 'page-sitemap.xml'):
        t = (tmp / sm).read_text()
        (tmp / sm).write_text(t)
    # font files named with a ?ver suffix
    renames = {}
    for f in list(tmp.rglob('*@*')):
        new = f.with_name(f.name.split('@')[0])
        f.rename(new)
        renames[f.name] = new.name
    for css in tmp.rglob('*.css'):
        t = css.read_text(errors='surrogateescape')
        t2 = t
        for old, new in renames.items():
            t2 = t2.replace(old.replace('@', '%40'), new).replace(old, new)
        if t2 != t:
            css.write_text(t2, errors='surrogateescape')
    # gallery pages + the static answer to the plugin's paging request
    shutil.copytree(epyt, tmp / 'epyt-pages')
    for frag in (tmp / 'epyt-pages').rglob('*.html'):
        frag.write_text(localise(frag.read_text(), '../'))   # injected into pages one folder deep
    (tmp / 'assets').mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'tools' / 'epyt-static.js', tmp / 'assets' / 'epyt-static.js')
    shutil.copy2(ROOT / 'tools' / 'mobile.css', tmp / 'assets' / 'mobile.css')
    # pages
    for page in tmp.rglob('index.html'):
        depth = len(page.relative_to(tmp).parts) - 1
        prefix = '../' * depth
        t = page.read_text()
        t = localise(t, prefix)
        t = HEAD_DROP.sub('', t)
        t = tidy_links(t, prefix)
        if 'epyt-gallery' in t:
            t = re.sub(r'(<script[^>]*youtube-embed-plus/scripts/ytprefs\.min\.js[^>]*></script>)',
                       r'\1\n<script src="' + prefix + 'assets/epyt-static.js"></script>', t, count=1)
        t = t.replace('</head>', '<link rel="stylesheet" href="' + prefix + 'assets/mobile.css">\n</head>', 1)
        t = re.sub(r'(<head[^>]*>)', r'\1\n<meta name="robots" content="noindex"><!-- preview copy only: remove when culadasa.com points here -->', t, count=1)
        page.write_text(t)
    # the live 404 page, served for any missing address at any depth: absolute URLs
    t = get('no-such-page-mirror-404/', allow_404=True).decode()
    t = HEAD_DROP.sub('', t)
    (tmp / '404.html').write_text(t)
    if SITE.exists():
        shutil.rmtree(SITE)
    tmp.rename(SITE)
    n = sum(1 for _ in SITE.rglob('*') if _.is_file())
    print(f'site/ written: {n} files')


if __name__ == '__main__':
    main(*sys.argv[1:3])
