"""Validate the static site's crawlable content, local links and metadata."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = 'safetw.app'
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids, self.links, self.assets, self.canonicals, self.schemas = [], [], [], [], []
        self.title, self.h1, self.description, self.lang = '', 0, '', ''
        self.capture_title, self.capture_json, self.raw_json = False, False, ''
        self.controls = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html': self.lang = attrs.get('lang', '')
        if attrs.get('id'): self.ids.append(attrs['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.capture_title = True
        if attrs.get('aria-controls'): self.controls.extend(attrs['aria-controls'].split())
        if tag == 'a' and attrs.get('href'): self.links.append(attrs['href'])
        if tag in ('img','script') and attrs.get('src'): self.assets.append(attrs['src'])
        if tag == 'link':
            if attrs.get('rel') == 'canonical': self.canonicals.append(attrs.get('href'))
            elif attrs.get('rel') in ('stylesheet','icon','apple-touch-icon'): self.assets.append(attrs.get('href',''))
        if tag == 'meta':
            if attrs.get('name') == 'description': self.description = attrs.get('content','')
            if attrs.get('name') == 'robots' and 'noindex' in attrs.get('content','').lower(): errors.append(f'{self.path.name}: unexpected noindex')
        if tag == 'script' and attrs.get('type') == 'application/ld+json': self.capture_json, self.raw_json = True, ''
    def handle_data(self, data):
        if self.capture_title: self.title += data
        if self.capture_json: self.raw_json += data
    def handle_endtag(self, tag):
        if tag == 'title': self.capture_title = False
        if tag == 'script' and self.capture_json:
            try: self.schemas.append(json.loads(self.raw_json))
            except ValueError as exc: errors.append(f'{self.path.name}: invalid JSON-LD: {exc}')
            self.capture_json = False

pages = {}
for path in sorted(ROOT.glob('*.html')):
    page = Page(path)
    page.feed(path.read_text())
    pages[path.name] = page

titles, descriptions = {}, {}
for name, page in pages.items():
    expected = 'https://safetw.app/' + ('' if name == 'index.html' else name)
    for ok, message in [
        (page.lang in ('zh-TW','zh-Hant'), 'missing Traditional Chinese lang'),
        (page.h1 == 1, f'expected one H1, found {page.h1}'),
        (bool(page.title.strip()), 'missing title'),
        (bool(page.description.strip()), 'missing description'),
        (page.canonicals == [expected], f'canonical should be {expected}'),
        (len(page.ids) == len(set(page.ids)), 'duplicate element IDs')
    ]:
        if not ok: errors.append(f'{name}: {message}')
    if page.title in titles: errors.append(f'{name}: duplicate title with {titles[page.title]}')
    if page.description in descriptions: errors.append(f'{name}: duplicate description with {descriptions[page.description]}')
    titles[page.title], descriptions[page.description] = name, name
    for control in page.controls:
        if control not in page.ids: errors.append(f'{name}: aria-controls target missing: {control}')
    for href in page.links + page.assets:
        part = urlsplit(href)
        if part.scheme and part.scheme not in ('http','https'): continue
        if part.netloc and part.netloc != HOST: continue
        path = unquote(part.path)
        target = ROOT / (path.lstrip('/') or (name if href.startswith('#') else 'index.html'))
        if not target.exists(): errors.append(f'{name}: broken local URL {href}'); continue
        if part.fragment and target.suffix == '.html':
            dest = pages.get(target.name)
            if dest and unquote(part.fragment) not in dest.ids: errors.append(f'{name}: missing anchor {href}')

tree = ET.parse(ROOT/'sitemap.xml')
urls = [node.text for node in tree.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
expected_urls = {'https://safetw.app/' + ('' if name == 'index.html' else name) for name in pages}
if set(urls) != expected_urls: errors.append(f'sitemap mismatch: missing {expected_urls-set(urls)}, extra {set(urls)-expected_urls}')
if len(urls) != len(set(urls)): errors.append('sitemap contains duplicate URLs')
robots = (ROOT/'robots.txt').read_text()
if 'Sitemap: https://safetw.app/sitemap.xml' not in robots: errors.append('robots sitemap declaration missing')

# Every HTML page must be discoverable through real anchor links from the homepage.
seen, queue = set(), ['index.html']
while queue:
    name = queue.pop()
    if name in seen: continue
    seen.add(name)
    for href in pages[name].links:
        part = urlsplit(href)
        if part.netloc and part.netloc != HOST: continue
        if part.scheme and part.scheme not in ('http','https'): continue
        path = part.path.lstrip('/') or ('index.html' if not href.startswith('#') else name)
        if path in pages and path not in seen: queue.append(path)
if set(pages)-seen: errors.append(f'orphan pages: {sorted(set(pages)-seen)}')

for name in ('index.html','taiwan-strait-war-warning-signs.html'):
    html = (ROOT/name).read_text()
    if 'cdn.tailwindcss.com' in html or 'lucide@latest' in html: errors.append(f'{name}: runtime or unpinned CDN remains')

if errors:
    print('\n'.join(errors))
    raise SystemExit(1)
print(f'PASS: {len(pages)} HTML pages, unique titles/descriptions, canonicals, JSON-LD, local assets/anchors, ARIA targets, sitemap and crawlable navigation.')
