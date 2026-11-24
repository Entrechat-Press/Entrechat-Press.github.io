# entrechatpress.com

The Entrechat Press website. Plain HTML and CSS, hosted on GitHub Pages.

## Editing

Page content lives in `_src/pages/`. The header, footer and page shell are in `_src/layout.html`, and the shared "Ready to bring your book to life?" form section is in `_src/partials/cta_form.html`.

After changing anything in `_src/`, rebuild:

    python3 _src/build.py

That regenerates every page's `index.html` and `sitemap.xml`. Commit both the source and the built files, including `_src/lastmod.json`, which tracks the date each page's content last changed for the sitemap.

Styles: `css/site.css`. Scripts (menu, testimonial arrows, Zoho forms, video): `js/site.js`. Images: `images/`.

## Forms

All forms are Zoho Forms embeds. Their URLs are listed at the top of `_src/build.py`.

## Domain and forwarding pages

`CNAME` tells GitHub Pages the site lives at www.entrechatpress.com. The folders `home/`, `blog/`, `test/`, `publishing-template/` and `onboarding-1/` are hand-written forwarding pages for old addresses (`onboarding-1/` goes to `/onboarding/`); the build doesn't touch them.

## Announcement bar

A red bar at the top of the header promotes the free Book Blueprint guide. It shows on pages whose header comment has `announce: yes` (currently the homepage, Write, Publish and Market). The message lives in `ANNOUNCE` in `_src/build.py`; when you change it, also change `ANNOUNCE_ID` so visitors who closed the old message see the new one.
