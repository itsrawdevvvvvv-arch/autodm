"""QA: link graph, schema, metadata, contrast, weight."""
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"src", ".git", "assets", ".github"}
IGNORE = {"404.html", "autodm-setup-guide.html"}

errors, warns = [], []


def pages():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(base, f), ROOT).replace(os.sep, "/"))
    return sorted(out)


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.imgs, self.ids, self.h, self.title = [], [], set(), [], []
        self.in_title = False
        self.metas = {}
        self.lang = None
        self.forms = 0
        self.labels = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.h.append(int(tag[1]))
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.metas[k] = a.get("content", "")
        if tag == "title":
            self.in_title = True
        if tag == "form":
            self.forms += 1
        if tag == "label" and "for" in a:
            self.labels.add(a["for"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)


titles, descs = {}, {}
total_bytes = 0
for rel in pages():
    if rel in IGNORE:
        continue
    path = os.path.join(ROOT, rel)
    raw = open(path, encoding="utf-8").read()
    total_bytes += len(raw.encode())
    p = P()
    p.feed(raw)

    # --- template leaks
    for pat, label in [(r"\{[a-zA-Z_'\[\]]+\}", "unrendered f-string"),
                       (r"\[cite:", "citation marker"),
                       (r"mailto:EMAIL", "literal EMAIL placeholder"),
                       (r"None<", "python None")]:
        m = re.findall(pat, raw)
        if m:
            errors.append(f"{rel}: {label} → {m[:3]}")

    # --- titles / descriptions
    t = "".join(p.title).strip()
    d = p.metas.get("description", "")
    titles.setdefault(t, []).append(rel)
    descs.setdefault(d, []).append(rel)
    if not t:
        errors.append(f"{rel}: missing <title>")
    if not d:
        errors.append(f"{rel}: missing meta description")
    if len(t) > 65:
        warns.append(f"{rel}: title {len(t)} chars — may truncate in SERPs")
    if not (120 <= len(d) <= 165):
        warns.append(f"{rel}: description {len(d)} chars")
    if not p.metas.get("og:image"):
        errors.append(f"{rel}: missing og:image")
    if p.lang != "en":
        errors.append(f"{rel}: missing lang=en")

    # --- headings
    if rel != "404.html":
        if p.h.count(1) != 1:
            warns.append(f"{rel}: {p.h.count(1)} h1 elements")
        if p.h and p.h[0] != 1:
            warns.append(f"{rel}: first heading is h{p.h[0]}")

    # --- images
    for img in p.imgs:
        if "alt" not in img:
            errors.append(f"{rel}: img without alt")

    # --- forms: every input has a label
    for m in re.finditer(r"<(?:input|textarea|select)[^>]*id=\"([^\"]+)\"", raw):
        if m.group(1) not in p.labels:
            errors.append(f"{rel}: field {m.group(1)} has no <label for>")

    # --- json-ld
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            json.loads(block)
        except Exception as e:
            errors.append(f"{rel}: bad JSON-LD ({e})")

    # --- links
    depth = rel.count("/")
    base_dir = os.path.dirname(rel)
    for href in p.links:
        if href.startswith(("http://", "https://", "mailto:", "#", "tel:", "/")):
            continue  # "/" links are root-absolute, used by 404.html
        target, _, frag = href.partition("#")
        if not target:  # in-page anchor
            if frag and frag not in p.ids:
                errors.append(f"{rel}: dead anchor #{frag}")
            continue
        resolved = os.path.normpath(os.path.join(base_dir, target))
        if not os.path.exists(os.path.join(ROOT, resolved)):
            errors.append(f"{rel}: broken link → {href}")
        elif frag:
            tpath = os.path.join(ROOT, resolved)
            if tpath.endswith(".html"):
                tids = set(re.findall(r'id="([^"]+)"', open(tpath, encoding="utf-8").read()))
                if frag not in tids:
                    errors.append(f"{rel}: link to missing anchor {href}")

# --- duplicate metadata
for t, files in titles.items():
    if len(files) > 1:
        errors.append(f"duplicate title across {files}: {t[:60]}")
for d, files in descs.items():
    if len(files) > 1:
        errors.append(f"duplicate description across {files}")

# --- sitemap coverage
sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
html_pages = [p for p in pages() if p not in IGNORE]
if len(locs) != len(html_pages):
    errors.append(f"sitemap has {len(locs)} urls, site has {len(html_pages)} pages")
for p in html_pages:
    want = "/" + p.replace("index.html", "")
    if not any(l.endswith(want) for l in locs):
        errors.append(f"sitemap missing {p}")

# --- assets referenced exist
for rel in pages():
    raw = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    base_dir = os.path.dirname(rel)
    for m in re.findall(r'(?:href|src)="((?:\.\./)*assets/[^"]+)"', raw):
        target = os.path.normpath(os.path.join(base_dir, m))
        if not os.path.exists(os.path.join(ROOT, target)):
            errors.append(f"{rel}: missing asset {m}")

# --- contrast
def lum(hexc):
    hexc = hexc.lstrip("#")
    c = [int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


pairs = [("#1d120c", "#f4ead9", "ink on paper"),
         ("#1d120c", "#fbf6ec", "ink on card"),
         ("#46281a", "#f4ead9", "coffee on paper"),
         ("#f4ead9", "#a84e2a", "paper on clay button"),
         ("#1d120c", "#e9b95e", "ink on gold chip"),
         ("#f4ead9", "#1d120c", "paper on ink section"),
         ("#e9b95e", "#1d120c", "gold on ink section"),
         ("#1d120c", "#e3cba6", "ink on tan section"),
         ("#a84e2a", "#f4ead9", "clay text on paper")]

print(f"pages: {len([p for p in pages() if p not in IGNORE])}  ·  html bytes: {total_bytes/1024:.1f} KB")
print("\ncontrast:")
for fg, bg, label in pairs:
    r = ratio(fg, bg)
    flag = "AA" if r >= 4.5 else ("AA-large" if r >= 3 else "FAIL")
    print(f"  {label:24s} {r:5.2f}  {flag}")
    if r < 3:
        errors.append(f"contrast fail: {label} {r}")

print(f"\nerrors: {len(errors)}")
for e in errors:
    print("  ✗", e)
print(f"warnings: {len(warns)}")
for w in warns[:25]:
    print("  !", w)

sys.exit(1 if errors else 0)
