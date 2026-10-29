"""Viraloop site — shared layout, components and helpers."""
import os
import html as _html

SITE = "https://itsrawdevvvvvv-arch.github.io/autodm"
BASE_PATH = "/" + SITE.split("//", 1)[1].split("/", 1)[1].strip("/") if "/" in SITE.split("//", 1)[1] else ""
BRAND = "Viraloop"
EMAIL = "hello@viraloop.co"
INSTAGRAM = "https://instagram.com/viraloop"
UPDATED = "29 October 2026"

# Where the dashboard lives once deployed. Leave empty until you have a URL:
# the site then shows the one-click deploy button instead of a dead link.
APP_URL = ""
REPO_URL = "https://github.com/itsrawdevvvvvv-arch/autodm"
DEPLOY_URL = "https://deploy.workers.cloudflare.com/?url=" + REPO_URL
FREE_LINE = "Free forever, one account, no card"


def connect_href(depth=0):
    """Where the Connect button goes: the running app if we know its URL."""
    if APP_URL:
        return APP_URL.rstrip("/") + "/auth/instagram"
    return rel(depth, "connect.html")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NAV = [
    ("features", "Features", "features.html"),
    ("pricing", "Pricing", "pricing.html"),
    ("blog", "Blog", "blog/index.html"),
    ("help", "Help", "help/index.html"),
    ("connect", "Connect", "connect.html"),
    ("about", "About", "about.html"),
]


def rel(depth, path):
    return ("../" * depth) + path


def url_for(path):
    """Absolute URL for a site-relative path."""
    if path in ("index.html", ""):
        return SITE + "/"
    if path.endswith("index.html"):
        return SITE + "/" + path[: -len("index.html")]
    return SITE + "/" + path


ICONS = {
    "bolt": '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z"/>',
    "chat": '<path d="M21 12a8 8 0 0 1-8 8H8l-4 3v-6a8 8 0 0 1 8-8h1a8 8 0 0 1 8 3Z"/><path d="M8 11h8M8 15h5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "link": '<path d="M9.5 14.5 14.5 9.5"/><path d="M7 17a4 4 0 0 1 0-6l2-2"/><path d="M17 7a4 4 0 0 1 0 6l-2 2"/>',
    "store": '<path d="M4 9h16l-1.2 10H5.2L4 9Z"/><path d="M8 9V7a4 4 0 0 1 8 0v2"/>',
    "inbox": '<path d="M4 13h4l2 3h4l2-3h4"/><path d="M4 13 6 4h12l2 9v7H4v-7Z"/>',
    "check": '<path d="m4 12 5 5L20 6"/>',
    "shield": '<path d="M12 3 5 6v6c0 4 3 7 7 9 4-2 7-5 7-9V6l-7-3Z"/><path d="m9 12 2 2 4-4"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20a6 6 0 0 1 12 0"/><path d="M17 5.2A3.2 3.2 0 0 1 17 11"/><path d="M15.5 14.4A6 6 0 0 1 21 20"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
}


def icon(name, cls=""):
    return (f'<svg viewBox="0 0 24 24" class="{cls}" aria-hidden="true" focusable="false">'
            f'{ICONS[name]}</svg>')


def brand_mark():
    return ('<span class="brand__mark" aria-hidden="true">'
            '<svg viewBox="0 0 24 24"><path d="M5 18c4 0 4-12 8-12 2.2 0 3 2 3 4"/>'
            '<path d="M16 14c0 2-.8 4-3 4-4 0-4-12-8-12"/></svg></span>')


def head(title, desc, path, depth=0, jsonld=None, extra_css=None, noindex=False):
    r = lambda p: rel(depth, p)
    ld = ""
    if jsonld:
        ld = "\n".join(f'<script type="application/ld+json">{_json(b)}</script>' for b in jsonld)
    robots = ('<meta name="robots" content="noindex,follow">' if noindex
              else '<meta name="robots" content="index,follow,max-image-preview:large">')
    canon = url_for(path)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#f4ead9">
<meta name="color-scheme" content="light">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Viraloop — Instagram DM automation for creators">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/assets/img/og.png">
<link rel="preload" href="{r('assets/fonts/archivo-black-400.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r('assets/fonts/space-grotesk-var.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r('assets/css/styles.css')}" as="style">
<link rel="stylesheet" href="{r('assets/css/styles.css')}">
<link rel="icon" href="{r('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{r('assets/img/apple-touch-icon.png')}">
<link rel="sitemap" type="application/xml" href="{r('sitemap.xml')}">{extra_css or ''}
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def _json(obj):
    import json
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def header(active, depth=0):
    r = lambda p: rel(depth, p)
    links = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{r(href)}"{cur}>{label}</a>')
    return f"""<header class="header" data-open="false">
  <div class="wrap header__inner">
    <a class="brand" href="{r('index.html')}">{brand_mark()}<span>{BRAND}</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu"><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Primary">
      {''.join(links)}
    </nav>
    <div class="header__cta">
      <a class="btn btn--ghost btn--sm" href="{r('pricing.html')}#start">Get it free</a>
    </div>
  </div>
</header>"""


def ticker(items):
    row = "".join(f"<span>{i}</span>" for i in items)
    return f'<div class="ticker" aria-hidden="true"><div class="ticker__track">{row}{row}</div></div>'


def footer(depth=0):
    r = lambda p: rel(depth, p)
    return f"""<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="brand" href="{r('index.html')}">{brand_mark()}<span>{BRAND}</span></a>
        <p>Free Instagram DM automation for one account. Built on Meta's official API, policy-safe by design.</p>
      </div>
      <div>
        <h4>Product</h4>
        <ul>
          <li><a href="{r('features.html')}">Features</a></li>
          <li><a href="{r('pricing.html')}">Pricing</a></li>
          <li><a href="{r('help/index.html')}">Help centre</a></li>
          <li><a href="{r('connect.html')}">Connect Instagram</a></li>
          <li><a href="{r('pricing.html')}#start">Get it free</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="{r('about.html')}">About</a></li>
          <li><a href="{r('blog/index.html')}">Blog</a></li>
          <li><a href="{r('contact.html')}">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Legal</h4>
        <ul>
          <li><a href="{r('terms.html')}">Terms of service</a></li>
          <li><a href="{r('privacy.html')}">Privacy policy</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© 2026 {BRAND}. Operated by [Your Legal Entity], [City], India.</span>
      <span>Last updated {UPDATED}</span>
    </div>
  </div>
</footer>
<script src="{r('assets/js/app.js')}" defer></script>
</body>
</html>"""


def page(path, title, desc, body, active="", depth=0, jsonld=None, noindex=False, tick=None):
    """Write a page to disk. path is site-relative, e.g. 'blog/index.html'."""
    html = head(title, desc, path, depth, jsonld, noindex=noindex)
    html += "\n" + header(active, depth)
    if tick:
        html += "\n" + ticker(tick)
    html += f'\n<main id="main">\n{body}\n</main>\n'
    html += footer(depth)
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out


# ---------- reusable blocks ----------

def cta_band(depth=0, heading="Turn your comments into conversations.",
             sub="Free forever, one account, no card. Deploy it once and it is yours.",
             label="Get it free", href="pricing.html#start"):
    r = lambda p: rel(depth, p)
    return f"""<section class="section cta-band">
  <div class="wrap center stack">
    <h2>{heading}</h2>
    <p class="lede" style="margin-inline:auto">{sub}</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="{r(href)}">{label}</a>
      <a class="btn btn--ink" href="{r('features.html')}">See the features</a>
    </div>
  </div>
</section>"""


def faq_block(items, heading="Questions, answered.", id_="faq"):
    rows = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{q}</summary>'
        f'<div class="faq__a">{a}</div></details>'
        for i, (q, a) in enumerate(items))
    return f"""<section class="section" id="{id_}">
  <div class="wrap">
    <div class="grid grid-2" style="align-items:start;gap:clamp(1.5rem,4vw,3rem)">
      <div class="stack">
        <span class="eyebrow">FAQ</span>
        <h2>{heading}</h2>
        <p class="muted">Still unsure? Email <a href="mailto:{EMAIL}">{EMAIL}</a> — a human answers, usually within a day.</p>
      </div>
      <div class="faq">{rows}</div>
    </div>
  </div>
</section>"""


def breadcrumbs(items, depth=0):
    """items: list of (label, href or None) — last item is current page."""
    r = lambda p: rel(depth, p)
    lis = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            lis.append(f'<li><a href="{r(href)}">{label}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{label}</li>')
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def breadcrumb_ld(items, path, depth=0):
    elems = []
    for i, (label, href) in enumerate(items):
        item = {"@type": "ListItem", "position": i + 1, "name": label}
        if href and i < len(items) - 1:
            item["item"] = url_for(href)
        elems.append(item)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elems}


ORG_LD = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": BRAND,
    "url": SITE + "/",
    "logo": SITE + "/assets/img/og.png",
    "sameAs": [INSTAGRAM],
    "contactPoint": {"@type": "ContactPoint", "email": EMAIL, "contactType": "customer support"},
}

APP_LD = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": BRAND,
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web",
    "description": "Instagram DM automation for creators: comment-to-DM triggers, story reply capture, timed follow-ups and link delivery.",
    "url": SITE + "/",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR",
               "description": "Free. One account, self-hosted."},
}
