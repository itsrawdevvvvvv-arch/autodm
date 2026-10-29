# Viraloop — website

Marketing site for **Viraloop**, an Instagram DM automation product for creators.
Static HTML/CSS/JS, no build step required to serve, no trackers, no cookie banner.

Live: https://itsrawdevvvvvv-arch.github.io/autodm/

## What's here

```
index.html          Home
features.html       Feature detail
pricing.html        Plans + beta signup
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
6. **Pricing.** Free-in-beta, ₹499 Creator, ₹1,499 Agency — change in
   `pages_a.py` (pricing block) if the numbers move.

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
Push to `main` and the site updates at https://itsrawdevvvvvv-arch.github.io/autodm/.

For a custom domain: add a `CNAME` file containing the bare domain, point a
CNAME DNS record at `<user>.github.io`, enable HTTPS in repo settings, then set
`SITE` in `src/layout.py` and rebuild.
