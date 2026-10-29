"""Build the Viraloop static site: pages, assets, sitemap, robots."""
import os
import re
import datetime

import layout
from layout import ROOT, SITE

import pages_a
import pages_b
import pages_c

SRC = os.path.join(ROOT, "src")


# ---------------------------------------------------------------- assets

def write(path, content, mode="w"):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    with open(full, mode) as f:
        f.write(content)
    return full


APP_JS = """/* Viraloop — progressive enhancement only. Everything works without JS. */
(function () {
  'use strict';

  /* Mobile navigation */
  var header = document.querySelector('.header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    toggle.addEventListener('click', function () {
      var open = header.getAttribute('data-open') === 'true';
      header.setAttribute('data-open', String(!open));
      toggle.setAttribute('aria-expanded', String(!open));
      toggle.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.getAttribute('data-open') === 'true') {
        header.setAttribute('data-open', 'false');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* Forms: build a mailto: so the site stays backend-free.
     Swap the action for a real endpoint when you have one. */
  document.querySelectorAll('form[data-mailto]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var to = form.getAttribute('action').replace('mailto:', '').split('?')[0];
      var lines = [];
      new FormData(form).forEach(function (value, key) {
        if (key === 'consent') value = 'yes';
        lines.push(key.charAt(0).toUpperCase() + key.slice(1) + ': ' + value);
      });
      var subject = (form.querySelector('h3') || {}).textContent || document.title;
      var href = 'mailto:' + to +
        '?subject=' + encodeURIComponent('Website enquiry — ' + document.title) +
        '&body=' + encodeURIComponent(lines.join('\\n'));
      var status = form.querySelector('.form__status');
      if (status) status.textContent = 'Opening your email app…';
      window.location.href = href;
    });
  });

  /* Current year in footers written before the build year */
  var year = String(new Date().getFullYear());
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = year; });
})();
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect x="1.5" y="1.5" width="29" height="29" rx="4" fill="#a84e2a" stroke="#1d120c" stroke-width="3"/>
  <g fill="none" stroke="#f4ead9" stroke-width="2.8" stroke-linecap="round">
    <path d="M8 22c5 0 5-12 10-12 2.6 0 3.6 2.2 3.6 4.4"/>
    <path d="M21.6 17.4c0 2.2-1 4.6-3.6 4.6-5 0-5-12-10-12"/>
  </g>
</svg>
"""


def make_images():
    from PIL import Image, ImageDraw, ImageFont
    ttf = os.path.join(SRC, "ArchivoBlack-Regular.ttf")
    if not os.path.exists(ttf):
        raise SystemExit("missing display TTF for image generation")

    paper, ink, clay, gold = (244, 234, 217), (29, 18, 12), (168, 78, 42), (233, 185, 94)

    def border(d, box, w=8):
        d.rectangle(box, outline=ink, width=w)

    # --- Open Graph 1200x630 ---
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=paper)
    # offset shadow block
    d.rectangle([64 + 14, 64 + 14, W - 64 + 14, H - 64 + 14], fill=ink)
    d.rectangle([64, 64, W - 64, H - 64], fill=gold, outline=ink, width=8)

    big = ImageFont.truetype(ttf, 132)
    mid = ImageFont.truetype(ttf, 46)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28) \
        if os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") else big

    d.text((112, 128), "VIRALOOP", font=big, fill=ink)
    d.text((116, 288), "Turn every comment", font=mid, fill=ink)
    d.text((116, 348), "into a conversation.", font=mid, fill=ink)
    # pill
    d.rectangle([116, 452, 646, 512], fill=clay, outline=ink, width=6)
    d.text((142, 466), "INSTAGRAM DM AUTOMATION", font=small, fill=paper)
    d.text((116, 540), "viraloop  ·  built on Meta's official API", font=small, fill=ink)
    img.save(os.path.join(ROOT, "assets/img/og.png"), optimize=True)

    # --- apple touch icon 180x180 ---
    icon = Image.new("RGB", (180, 180), clay)
    di = ImageDraw.Draw(icon)
    di.rectangle([0, 0, 179, 179], outline=ink, width=10)
    f = ImageFont.truetype(ttf, 96)
    di.text((90, 92), "V", font=f, fill=paper, anchor="mm")
    icon.save(os.path.join(ROOT, "assets/img/apple-touch-icon.png"), optimize=True)


def make_sitemap():
    pages = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in ("src", ".git", "assets", ".github")]
        for fn in sorted(files):
            if not fn.endswith(".html") or fn in ("404.html", "autodm-setup-guide.html"):
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace(os.sep, "/")
            pages.append(rel)

    def priority(p):
        if p == "index.html":
            return "1.0", "weekly"
        if p in ("features.html", "pricing.html"):
            return "0.9", "monthly"
        if p in ("blog/index.html", "help/index.html"):
            return "0.8", "weekly"
        if p.startswith("blog/") or p.startswith("help/"):
            return "0.7", "monthly"
        if p in ("about.html", "contact.html"):
            return "0.5", "yearly"
        return "0.3", "yearly"

    today = datetime.date(2026, 10, 29).isoformat()
    rows = []
    for p in pages:
        loc = layout.url_for(p)
        pr, cf = priority(p)
        rows.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>"
                    f"\n    <changefreq>{cf}</changefreq>\n    <priority>{pr}</priority>\n  </url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(rows) + "\n</urlset>\n")
    write("sitemap.xml", xml)
    return pages


ROBOTS = f"""# Viraloop
User-agent: *
Allow: /
Disallow: /404.html

Sitemap: {SITE}/sitemap.xml
"""

README = f"""# Viraloop — website

Marketing site for **Viraloop**, an Instagram DM automation product for creators.
Static HTML/CSS/JS, no build step required to serve, no trackers, no cookie banner.

Live: {SITE}/

## What's here

```
index.html          Home
features.html       Feature detail
pricing.html        Pricing (free) + setup steps
about.html          Company
contact.html        Contact + form
blog/               Blog index + 3 articles
help/               Help centre + 6 guides
terms.html          Terms of service
privacy.html        Privacy policy
404.html            Not-found page
assets/css/         One stylesheet (design tokens at the top)
assets/js/          Progressive enhancement only (~1.5KB)
assets/fonts/       Self-hosted Archivo Black + Space Grotesk (41KB total)
assets/img/         OG image + apple touch icon
src/                Python generator that produces every page above
sitemap.xml         Generated
robots.txt
```

## Editing

Pages are generated so the nav, footer, head tags and JSON-LD stay consistent.
Edit content in `src/pages_a.py` (home, features, pricing), `src/pages_b.py`
(about, contact, blog) or `src/pages_c.py` (help, legal, 404), then rebuild:

```bash
cd src && python3 build.py
```

Editing the generated HTML directly also works — just know the next build
overwrites it.

## Before you launch — placeholders to replace

1. **Legal entity.** `[Your Legal Entity]`, `[Registered Address]`, `[City, State, PIN]`
   appear in the footer, About, Terms and Privacy. Indian consumer-protection
   rules expect a real seller identity on a commercial site.
2. **Domain.** `SITE` in `src/layout.py` drives canonical URLs, OG tags and the
   sitemap. Change it, rebuild, and update the `CNAME` file if you use a custom
   domain.
3. **Email.** `EMAIL` in `src/layout.py` (`hello@viraloop.co`) — must be a
   mailbox you actually read.
4. **Forms.** They open the visitor's mail client (`data-mailto`). Swap the
   `action` for a real endpoint (Formspree, Buttondown, your own API) and delete
   the `data-mailto` attribute when you have one.
5. **Instagram handle.** `INSTAGRAM` in `src/layout.py`.
6. **App URL.** `APP_URL` in `src/layout.py` is empty until you deploy the
   dashboard. Set it to your Render URL (e.g. `https://viraloop.onrender.com`)
   and the site links straight into the app. `DEPLOY_URL` is the one-click
   Render blueprint for the repo.

## Design system

Neobrutalist: 3px ink borders, hard offset shadows, zero-to-3px radii,
Archivo Black for display and Space Grotesk for text. All colours are CSS
custom properties at the top of `assets/css/styles.css`:

| Token | Value | Use |
|---|---|---|
| `--paper` | `#f4ead9` | Page background |
| `--paper-2` | `#fbf6ec` | Cards |
| `--ink` | `#1d120c` | Text, borders |
| `--coffee` | `#46281a` | Secondary text |
| `--clay` | `#c4633a` | Primary action |
| `--tan` | `#e3cba6` | Alternate sections |
| `--gold` | `#e9b95e` | Highlights, chips |

## Performance & privacy

- Two self-hosted variable/subset fonts (41KB), preloaded.
- One stylesheet, one 1.5KB script, no third-party requests at all.
- No analytics, no pixels, no cookies — so no consent banner is needed.
- Semantic landmarks, skip link, visible focus rings, `prefers-reduced-motion`
  support, print styles for the legal pages.

## Deploying

GitHub Pages serves the repository root directly (`.nojekyll` is included).
Push to `main` and the site updates at {SITE}/.

For a custom domain: add a `CNAME` file containing the bare domain, point a
CNAME DNS record at `<user>.github.io`, enable HTTPS in repo settings, then set
`SITE` in `src/layout.py` and rebuild.
"""


def main():
    pages_a.build()
    pages_b.build()
    pages_c.build()
    write("assets/js/app.js", APP_JS)
    write("favicon.svg", FAVICON)
    write("robots.txt", ROBOTS)
    write(".nojekyll", "")
    write("site-readme.md", README)
    make_images()
    pages = make_sitemap()
    print(f"built {len(pages)} pages")
    for p in pages:
        print("  ", p)


if __name__ == "__main__":
    main()
