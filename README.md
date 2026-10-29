# Viraloop

**Free Instagram DM automation for one account.** Comment triggers, DM keyword rules, story replies — running on your own server, on Meta's official Instagram API.

No subscription, no per-message pricing, no paid tier. You deploy it, you own it, the data stays on your machine.

---

## What's in this repo

| Path | What it is |
|---|---|
| `server/` | The app: Express API, polling engine, reply engine, JSON store |
| `public/` | The dashboard UI (neobrutalist, vanilla JS, no build step) |
| `docs/` | The marketing site, published by GitHub Pages |
| `docs/src/` | Python generator for the marketing site (`python3 build.py`) |
| `render.yaml` | One-click Render blueprint |

The marketing site is live at **https://itsrawdevvvvvv-arch.github.io/autodm/**.
The dashboard runs wherever you deploy `server/`.

---

## Quick start (local)

```bash
git clone https://github.com/itsrawdevvvvvv-arch/autodm.git
cd autodm
npm install
cp .env.example .env
npm start
```

Open **http://localhost:3000** and paste an access token.

Node 18+. No database, no build step, two dependencies (`express`, `dotenv`).

## Deploy to Render (free)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/itsrawdevvvvvv-arch/autodm)

The blueprint creates the service and generates `APP_KEY` and
`WEBHOOK_VERIFY_TOKEN`. After the first deploy:

1. Open the service → **Environment** → copy the `APP_KEY` value.
2. Open your app URL → **Settings → Access key** → paste it. The dashboard now
   accepts requests from your browser only.
3. Go to **Account** and paste an Instagram access token.

Free instances sleep after inactivity, so a reply can be delayed by a minute or
two until the next request wakes the service. Any always-on instance removes
that delay; the software is the same.

---

## Connecting your Instagram account

You need an Instagram **Creator** or **Business** account (not personal).

**Fastest route — paste a token:**

1. Create an app at [developers.facebook.com](https://developers.facebook.com) →
   add the **Instagram** product.
2. Add your Instagram account as a tester and generate a token with
   `instagram_business_basic` and `instagram_business_manage_messages`.
3. Exchange it for a long-lived token (~60 days), paste it into the dashboard.

**Or use the login button:** set `META_APP_ID`, `META_APP_SECRET` and
`PUBLIC_URL` (your deployed URL) and use *Sign in with Instagram* on the
Account panel.

Refresh or revoke any time: **Account → Refresh token**, or Instagram →
*Apps and websites*.

---

## How it works

Every poll (default 30s) does two passes:

1. **Messages** — recent conversations; replies to new inbound DMs.
2. **Comments** — recent posts and reels; for each new comment, optionally posts
   a public reply and always sends one **private reply**, which is the
   Meta-sanctioned way to move a comment into DMs.

No webhook, no public URL, no tunnel. Webhook mode is still there if you want
push events (`/webhook`, verify token in `.env`).

**Hard limits, by design:** it only answers people who contacted you first. There
is no broadcast, no cold outreach and no follow-gating anywhere in the code.

**Safety cap:** replies per hour (default 200) so a loop can never run away.

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `3000` | HTTP port |
| `PUBLIC_URL` | `http://localhost:3000` | Public URL for OAuth redirect |
| `APP_KEY` | *(empty)* | Locks `/api/*`; empty = open (local use) |
| `META_APP_ID` / `META_APP_SECRET` | *(empty)* | Only needed for the login button |
| `LOGIN_ROUTE` | `instagram` | `instagram` or `facebook` (needs a linked Page) |
| `WEBHOOK_VERIFY_TOKEN` | — | Only for webhook mode |
| `MAX_SENDS_PER_HOUR` | `200` | Default cap, editable in the UI |

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/status` | Connection + engine state |
| GET | `/api/account` | Connected account, live profile |
| POST | `/api/token` | Connect with an access token |
| POST | `/api/disconnect` | Forget the token |
| POST | `/api/refresh-token` | Extend the long-lived token |
| GET/POST | `/api/rules` | List / create automations |
| PUT/DELETE | `/api/rules/:id` | Update / delete |
| POST | `/api/rules/test` | Dry run — which rule matches, what it sends |
| GET | `/api/activity` | Reply log |
| GET/POST | `/api/settings` | Poll interval, cap, receive mode |
| POST | `/api/scan` | Run one polling pass now |

Send `X-Api-Key: <APP_KEY>` on every `/api` call when `APP_KEY` is set.

## Where data lives

`data/*.json` on the server: `account`, `rules`, `settings`, `activity`,
`poller`. Git-ignored. Delete the folder to wipe everything.

---

## The marketing site

Generated, so nav, head tags and structured data stay consistent:

```bash
cd docs/src
python3 build.py     # writes every page into docs/
python3 qa.py        # link graph, schema, metadata, WCAG contrast
```

Edit content in `pages_a.py` (home, features, pricing), `pages_b.py` (about,
contact, blog), `pages_c.py` (help, legal, 404).

**Before pointing a domain at it:** replace `[Your Legal Entity]` and the
address in the footer/About/Terms/Privacy, set `APP_URL` in `docs/src/layout.py`
to your deployed dashboard URL, and change `EMAIL` if you use a different
mailbox. Details in `docs/site-readme.md`.

---

## Legacy

The earlier AutoDM console docs are preserved at
`docs/autodm-setup-guide.html`. The old vanilla console UI has been replaced by
the Viraloop dashboard in `public/`.

## Licence

MIT for the code in this repository.
