#!/usr/bin/env python3
"""Builds the Entrechat Press site.

Each page lives in _src/pages/<name>.html: a metadata comment at the top, then the page body.
Run `python3 _src/build.py` from the repo root. Output goes next to it: index.html, write/index.html, etc.

Shortcuts you can use inside page files:
  src="@a471043c"      -> image whose file name starts with a471043c (width/height added automatically)
  {{> cta_form }}      -> drop in a partial from _src/partials/cta_form.html
  {{ZOHO_CONTACT}}     -> a form URL from FORMS below
"""
import os, re, glob, html, json
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
       ('about', '/about/', 'About.'), ('titles', '/our-books/', 'Our Titles.'), ('resources', '/resources/', 'Resources.')]

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


ORG = {
    "@type": ["Organization", "ProfessionalService"], "@id": SITE_URL + "/#org",
    "name": "Entrechat Press", "url": SITE_URL + "/",
    "logo": SITE_URL + "/images/logo.webp", "image": SITE_URL + "/images/logo-share.png",
    "description": "Toronto hybrid publisher offering ghostwriting, book coaching, editing, publishing and marketing for first-time nonfiction authors.",
    "address": {"@type": "PostalAddress", "addressLocality": "Toronto", "addressRegion": "ON", "addressCountry": "CA"},
    "areaServed": ["CA", "US"],
    "knowsAbout": ["Ghostwriting", "Book coaching", "Manuscript editing", "Hybrid publishing", "Book marketing", "Nonfiction"],
    "founder": {"@id": SITE_URL + "/#adina"},
    "sameAs": ["https://www.instagram.com/entrechat.press/"],
}
PERSON = {
    "@type": "Person", "@id": SITE_URL + "/#adina", "name": "Adina Samuels",
    "jobTitle": "Founder and Publisher", "worksFor": {"@id": SITE_URL + "/#org"},
    "url": SITE_URL + "/about/",
    "description": "Publishing strategist, author coach and founder of Entrechat Press, with 20+ years of experience helping first-time nonfiction authors turn their expertise into finished books.",
    "memberOf": [{"@type": "Organization", "name": "Independent Book Publishers Association"},
                 {"@type": "Organization", "name": "Association of Ghostwriters"}],
    "sameAs": ["https://www.linkedin.com/in/adinasamuels/", "https://www.instagram.com/adinasamuels/",
               "https://www.youtube.com/@adinasamuels"],
}


def strip_tags(x):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x))).strip()


def abs_img(v):
    if v.startswith('@'):
        v = image_path(v[1:])
    return SITE_URL + v


def schema_for(meta, body, canonical):
    graph = [ORG, PERSON, {"@type": "WebPage", "@id": canonical, "url": canonical, "name": meta['title'],
                           "description": meta.get('description', ''), "isPartOf": {"@id": SITE_URL + "/#site"},
                           "about": {"@id": SITE_URL + "/#org"}}]
    if meta['path'] == '/':
        graph.append({"@type": "WebSite", "@id": SITE_URL + "/#site", "url": SITE_URL + "/", "name": "Entrechat Press",
                      "publisher": {"@id": SITE_URL + "/#org"}})
    qa = re.findall(r'<details><summary>(.*?)</summary><div class="ans">(.*?)</div></details>', body, re.S)
    if qa:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in qa]})
    if meta.get('book'):
        b = {"@type": "Book", "name": meta['book'], "url": canonical,
             "author": [{"@type": "Person", "name": n.strip()} for n in meta['book_author'].split(';')],
             "publisher": {"@id": SITE_URL + "/#org"}, "inLanguage": "en"}
        if meta.get('isbn'):
            b["isbn"] = meta['isbn']
        if meta.get('image'):
            b["image"] = abs_img(meta['image'])
        graph.append(b)
    if meta.get('kind') in ('guide', 'blog'):
        a = {"@type": "Article", "headline": meta['heading'], "description": meta.get('description', ''),
             "author": {"@id": SITE_URL + "/#adina"}, "publisher": {"@id": SITE_URL + "/#org"},
             "mainEntityOfPage": canonical}
        if meta.get('date'):
            a["datePublished"] = meta['date']
        graph.append(a)
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + '</script>'


def parse(path):
    raw = read(path)
    meta_m = re.match(r'\s*<!--(.*?)-->', raw, re.S)
    meta = dict(re.findall(r'^\s*(\w+):\s*(.*?)\s*$', meta_m.group(1), re.M))
    return meta, raw[meta_m.end():]


def resources_list(articles):
    out = []
    for kind, label in (('guide', 'Guides'), ('blog', 'From the blog')):
        items = [m for m in articles if m.get('kind') == kind]
        if not items:
            continue
        cards = ''.join(
            f'<a class="res-card" href="{m["path"]}"><p class="res-kind">{label[:-1] if kind == "guide" else "Blog"}'
            f'{" &middot; Draft" if m.get("draft") == "yes" else ""}</p><h3>{html.escape(m["heading"])}</h3>'
            f'<p>{html.escape(m.get("description", ""))}</p><span>Read it &rarr;</span></a>'
            for m in sorted(items, key=lambda m: m.get('date', ''), reverse=True))
        out.append(f'<h2 class="res-h">{label}</h2><div class="res-grid">{cards}</div>')
    return ''.join(out)


def build_page(path, articles):
    meta, body = parse(path)
    url = meta['path']
    nav = ''.join(
        f'<a href="{href}"{" aria-current=\"page\"" if meta.get("nav") == key else ""}>{label}</a>'
        for key, href, label in NAV)
    body = body.replace('{{resources_list}}', resources_list(articles))
    layout = read(os.path.join(SRC, 'layout.html'))
    canonical = SITE_URL + url
    head_extra = schema_for(meta, body, canonical) if url != '/404/' else ''
    if meta.get('draft') == 'yes' or url == '/404/':
        head_extra += '\n<meta name="robots" content="noindex">'
    out = (layout.replace('{{title}}', html.escape(meta['title']))
                 .replace('{{description}}', html.escape(meta.get('description', '')))
                 .replace('{{canonical}}', canonical)
                 .replace('{{og_image}}', abs_img(meta['image']) if meta.get('image') else SITE_URL + '/images/logo-share.png')
                 .replace('{{head_extra}}', head_extra)
                 .replace('{{nav}}', nav)
                 .replace('{{body}}', body))
    out = render(out)
    dest = os.path.join(ROOT, url.strip('/'), 'index.html') if url != '/' else os.path.join(ROOT, 'index.html')
    if url == '/404/':
        dest = os.path.join(ROOT, '404.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(out)
    return url, canonical, meta


def main():
    pages = sorted(glob.glob(os.path.join(SRC, 'pages', '*.html')))
    articles = [m for m in (parse(p)[0] for p in pages) if m.get('kind') in ('guide', 'blog')]
    built = [build_page(p, articles) for p in pages]
    today = date.today().isoformat()
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'  <url><loc>{c}</loc><lastmod>{today}</lastmod></url>' for u, c, m in built
           if u != '/404/' and m.get('draft') != 'yes']
    sm.append('</urlset>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
        f.write('\n'.join(sm) + '\n')
    print('built', len(built), 'pages')


if __name__ == '__main__':
    main()
