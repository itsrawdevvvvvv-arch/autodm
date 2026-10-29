# Viraloop

**Free Instagram DM automation for one account.** Comment triggers, DM keyword rules, story replies — running on your own server, on Meta's official Instagram API.

No subscription, no per-message pricing, no paid tier. You deploy it, you own it, the data stays on your machine.

---

## What's in this repo

| Path | What it is |
|---|---|
| `worker.js` | **Cloudflare Workers build** — the free, always-on deployment |
| `wrangler.toml` | Worker config: assets, D1 binding, one-minute cron |
| `migrations/` | D1 schema |
| `server/` | The same app as a Node/Express server, for running locally |
| `public/` | The dashboard UI (vanilla JS, no build step) — shared by both |
| `docs/` | The marketing site, published by GitHub Pages |
| `docs/src/` | Python generator for the marketing site (`python3 build.py`) |
| `test/` | 51-check Worker test suite + SQL validation |
| `render.yaml` | Optional Render blueprint (needs a card on their free tier) |

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

## Deploy to Cloudflare Workers (free, no card)

Cloudflare's free plan includes Workers, D1 and cron triggers — enough to run
this indefinitely without a payment method.

```bash
git clone https://github.com/itsrawdevvvvvv-arch/autodm.git
cd autodm && npm install
npx wrangler login
npx wrangler d1 create viraloop        # copy the database_id it prints
npx wrangler d1 execute viraloop --remote --file=migrations/0001_init.sql
npx wrangler deploy
```

Paste the printed `database_id` into `wrangler.toml`, then set the secrets:

```bash
npx wrangler secret put APP_KEY           # any random string; locks the dashboard
npx wrangler secret put PUBLIC_URL        # https://viraloop.<you>.workers.dev
npx wrangler secret put META_APP_ID       # for the Connect button
npx wrangler secret put META_APP_SECRET
```

Redeploy after adding secrets (`npx wrangler deploy`), open your
`*.workers.dev` URL, and press **Connect Instagram**.

How it maps onto the free plan:

| Piece | Free limit | What Viraloop uses |
|---|---|---|
| Cron trigger | every minute | one polling pass per minute |
| Workers requests | 100k/day | ~1,440 cron runs + your dashboard use |
| D1 rows written | 100k/day | a handful per poll |
| Static assets | unlimited | the dashboard in `public/` |

There is no `setInterval` and no filesystem on Workers, so the Worker uses
`scheduled()` for polling and D1 instead of `data/*.json`. The Node server in
`server/` still works if you prefer running it on your own machine.

### Optional: Render

`render.yaml` is still here, but Render's free instance type now requires a card
on file, which is why Cloudflare is the documented path.

## Connecting your Instagram account

You need an Instagram **Creator** or **Business** account (not personal).

### The one-click flow (recommended)

The dashboard has a **Connect Instagram** button that runs Meta's standard OAuth
flow: press it → Instagram's permission screen → back to the dashboard, connected.

To enable it:

1. **Create a Meta app** at [developers.facebook.com](https://developers.facebook.com)
   → *Create app* → add the **Instagram** product.
2. **Add your Instagram account as a tester**: App roles → Roles → add Instagram
   tester. (No app review needed for your own account.)
3. **Register the redirect URI**: Instagram → *API setup with Instagram login* →
   *Valid OAuth Redirect URIs* → add `https://<your-app>/auth/callback`
   — must match exactly, https included.
4. **Set the environment** on the server:
   ```
   META_APP_ID=...
   META_APP_SECRET=...
   PUBLIC_URL=https://<your-app>
   ```
5. Restart, open the dashboard, press **Connect Instagram**.

Scopes requested: `instagram_business_basic`,
`instagram_business_manage_messages`, `instagram_business_manage_comments`.

The dashboard tells you what is still missing — it calls `/api/oauth-check` and
lists the exact gaps under **Account**. Every authorisation attempt carries a
single-use `state` value (10-minute TTL) and lands back on the dashboard with
`?connected=1` or `?connect_error=…`.

### Or paste a token

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

## Tests

```bash
npm test          # 51 Worker checks + SQL validation
```

`test/worker_test.mjs` runs `worker.js` against a D1 shim and a mocked Meta API:
routing, the access key, OAuth redirect and state guards, rule CRUD, the dry-run
tester, the polling engine (DM + comment paths, de-duplication, the hourly cap)
and static asset serving. `test/sql_check.py` validates every SQL statement
against a real SQLite engine.

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
