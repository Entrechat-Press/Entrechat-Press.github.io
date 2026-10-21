#!/usr/bin/env python3
"""Builds the Entrechat Press site.

Each page lives in _src/pages/<name>.html: a metadata comment at the top, then the page body.
Run `python3 _src/build.py` from the repo root. Output goes next to it: index.html, write/index.html, etc.

Shortcuts you can use inside page files:
  src="@a471043c"      -> image whose file name starts with a471043c (width/height added automatically)
  {{> cta_form }}      -> drop in a partial from _src/partials/cta_form.html
  {{ZOHO_CONTACT}}     -> a form URL from FORMS below
"""
import os, re, glob, html
from datetime import date
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '_src')
SITE_URL = 'https://www.entrechatpress.com'

FORMS = {
    'ZOHO_WHITE': 'https://forms.zohopublic.ca/entrechatpress/form/EPContactFormWhite/formperma/BBlkCVX6aRiFesGuW_x5_0ETBSjp1-OELmJvkeKrQK0?zf_rszfm=1',
    'ZOHO_CONTACT': 'https://forms.zohopublic.ca/entrechatpress/form/ContactForm/formperma/0L37fYyvEovIcRBupDbE4N1VhOjsljSEEPGMlkDl-qM?zf_rszfm=1',
    'ZOHO_DAMINDRA': 'https://forms.zohopublic.ca/entrechatpress/form/IfICanYouCanBookPreLaunchForm/formperma/5WjqIlVqPotEoVpqASzZkbMKfSJ71rsSXm358_Lzq-o?zf_rszfm=1',
    'ZOHO_CHRIS': 'https://forms.zohopublic.ca/entrechatpress/form/ChrisGrahamBookPreLaunchForm/formperma/J0n4PRxMWOysOqjBnkvy9XtVcVpK8DITi757I5t_XfY?zf_rszfm=1',
    'ZOHO_REBECCA': 'https://forms.zohopublic.ca/entrechatpress/form/RebeccaAzuelosBookPreLaunchForm/formperma/mntLsI-E_ZVJpjA3JBVNRsRyd1OSCWmKFXDnQopXraM?zf_rszfm=1',
}

NAV = [('write', '/write/', 'Write.'), ('publish', '/publish/', 'Publish.'), ('market', '/market/', 'Market.'),
       ('about', '/about/', 'About.'), ('titles', '/our-books/', 'Our Titles.')]

IMAGES = {os.path.basename(p): p for p in glob.glob(os.path.join(ROOT, 'images', '*'))}
_size_cache = {}


def image_path(key):
    hits = [n for n in IMAGES if n.startswith(key)]
    if len(hits) != 1:
        raise SystemExit(f'Image "{key}" matched {len(hits)} files: {hits}')
    return '/images/' + hits[0]


def image_size(path):
    if path not in _size_cache:
        with Image.open(os.path.join(ROOT, path.lstrip('/'))) as im:
            _size_cache[path] = im.size
    return _size_cache[path]


def fix_img(m):
    tag = m.group(0)
    tag = re.sub(r'src="@([\w-]+)"', lambda s: f'src="{image_path(s.group(1))}"', tag)
    src = re.search(r'src="(/images/[^"]+)"', tag)
    if src and 'width=' not in tag:
        w, h = image_size(src.group(1))
        tag = tag.replace('<img ', f'<img width="{w}" height="{h}" ', 1)
    if 'loading=' not in tag and 'data-eager' not in tag:
        tag = tag.replace('<img ', '<img loading="lazy" ', 1)
    return tag.replace(' data-eager', '')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def render(body):
    for _ in range(3):
        body = re.sub(r'\{\{>\s*(\w+)\s*\}\}', lambda m: read(os.path.join(SRC, 'partials', m.group(1) + '.html')), body)
    for k, v in FORMS.items():
        body = body.replace('{{' + k + '}}', v)
    body = re.sub(r'url\(@([\w-]+)\)', lambda m: f'url({image_path(m.group(1))})', body)
    body = re.sub(r'<img\b[^>]*>', fix_img, body)
    return body


def build_page(path):
    raw = read(path)
    meta_m = re.match(r'\s*<!--(.*?)-->', raw, re.S)
    meta = dict(re.findall(r'^\s*(\w+):\s*(.*?)\s*$', meta_m.group(1), re.M))
    body = raw[meta_m.end():]
    url = meta['path']
    nav = ''.join(
        f'<a href="{href}"{" aria-current=\"page\"" if meta.get("nav") == key else ""}>{label}</a>'
        for key, href, label in NAV)
    layout = read(os.path.join(SRC, 'layout.html'))
    canonical = SITE_URL + ('/' if url == '/' else url.rstrip('/'))
    out = (layout.replace('{{title}}', html.escape(meta['title']))
                 .replace('{{description}}', html.escape(meta.get('description', '')))
                 .replace('{{canonical}}', canonical)
                 .replace('{{og_image}}', SITE_URL + meta.get('image', '/images/logo-share.png'))
                 .replace('{{nav}}', nav)
                 .replace('{{body}}', body))
    out = render(out)
    dest = os.path.join(ROOT, url.strip('/'), 'index.html') if url != '/' else os.path.join(ROOT, 'index.html')
    if url == '/404/':
        dest = os.path.join(ROOT, '404.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(out)
    return url, canonical


def main():
    urls = [build_page(p) for p in sorted(glob.glob(os.path.join(SRC, 'pages', '*.html')))]
    today = date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'  <url><loc>{c}</loc><lastmod>{today}</lastmod></url>' for u, c in urls if u != '/404/']
    sm.append('</urlset>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
        f.write('\n'.join(sm) + '\n')
    print('built', len(urls), 'pages')


if __name__ == '__main__':
    main()
