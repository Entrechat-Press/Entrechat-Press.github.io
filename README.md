# entrechatpress.com

The Entrechat Press website. Plain HTML and CSS, hosted on GitHub Pages.

## Editing

Page content lives in `_src/pages/`. The header, footer and page shell are in `_src/layout.html`, and the shared "Ready to bring your book to life?" form section is in `_src/partials/cta_form.html`.

After changing anything in `_src/`, rebuild:

    python3 _src/build.py

That regenerates every page's `index.html` and `sitemap.xml`. Commit both the source and the built files.

Styles: `css/site.css`. Scripts (menu, testimonial arrows, Zoho forms, video): `js/site.js`. Images: `images/`.

## Forms

All forms are Zoho Forms embeds. Their URLs are listed at the top of `_src/build.py`.

## Domain and forwarding pages

`CNAME` tells GitHub Pages the site lives at www.entrechatpress.com. The folders `home/`, `blog/`, `test/` and `publishing-template/` are hand-written forwarding pages for old Squarespace addresses; the build doesn't touch them.
