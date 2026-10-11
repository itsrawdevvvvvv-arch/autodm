# AutoDM

An Instagram DM auto-reply console — automatically reply to people who
**message** you or **comment a keyword** on your posts, using Meta's **official
Instagram Messaging API**.

- **Live UI preview:** https://itsrawdevvvvvv-arch.github.io/autodm/
  *(static demo — the buttons work, but it needs the backend below to actually send DMs)*
- **Source:** https://github.com/itsrawdevvvvvv-arch/autodm

---

## No terminal needed

You don't have to install anything or run any commands. Deploy the engine to a
free cloud host with one click, then connect Instagram:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/itsrawdevvvvvv-arch/autodm)

**Full click-by-click guide (no npm, no localhost): [SETUP.md](SETUP.md)**

---

## Personal use (just you)

If this is only ever for **your own** account, it gets much simpler:

- **No App Review.** That's only required to serve Instagram accounts you
  don't own. For your own account, Standard Access is enough.
- **No OAuth redirect.** Generate a long-lived token in the Meta console and
  paste it into **Settings → Account**. It refreshes itself (**Refresh token**) —
  no app secret needed.
- **No public URL or tunnel.** Set receive mode to **Polling** and AutoDM
  checks for new messages on its own, locally. Switch to **Webhook** only if you
  want real-time delivery and have a public HTTPS URL.

Quick path:

1. `npm install && npm start` → open http://localhost:3000
2. Settings → Account → paste your long-lived token → **Save token**
3. Add your reply rules under **Replies**
4. DM your account from another account and watch it reply

> Note: Meta documents that reading conversations with people who don't have a
> role on your app may require Advanced Access. If polling returns a permission
> error, switch receive mode to **Webhook**.

---

## Read this first — how connecting actually works

To connect a **real** Instagram account and send messages, there are only two
possibilities:

| Method | Password needed? | Redirect to Instagram? | Allowed by Meta? |
|---|---|---|---|
| **OAuth** (what AutoDM uses) | No | **Yes** — Instagram's consent screen | Yes |
| Password / session login | Yes | No | No — gets accounts banned |

**No password, but yes, a redirect.** The redirect *is* the safe connection —
it's how Instagram lets you approve an app without handing over your password.
There is no working method that avoids it.

---

## Architecture

```
Browser (the web app)  ⇄  Node server  ⇄  Meta Instagram Messaging API
  manage rules,            holds your          receives webhooks,
  watch activity           app secret          sends the DMs
```

The browser never holds your app secret. The Node server does the privileged work.

---

## Run it locally

```bash
npm install
cp .env.example .env      # fill in META_APP_ID / META_APP_SECRET
npm start                 # → http://localhost:3000
```

---

## Deploy it (get a real URL)

The web app is static, but the messaging engine is a Node server — so it needs a
Node host (not GitHub Pages alone). Free options:

**Render (easiest — `render.yaml` is included)**
1. Push this repo to GitHub.
2. On [render.com](https://render.com) → New → Blueprint → pick this repo.
3. Render reads `render.yaml`, creates the service, and asks for the env vars
   (`META_APP_ID`, `META_APP_SECRET`, `PUBLIC_URL`).
4. Set `PUBLIC_URL` to the Render URL it gives you, then add that same URL +
   `/auth/callback` as the redirect URI in your Meta app.

**Docker (any host — Railway, Fly.io, a VPS)**
```bash
docker build -t autodm .
docker run -p 3000:3000 --env-file .env autodm
```

**Heroku-style (a `Procfile` is included)**
```
web: node server/server.js
```

Once deployed, open the app URL, click **Connect Instagram**, and approve.

---

## Full Meta setup

1. **Instagram Professional account** — convert to Business/Creator.
2. **Meta developer app** — developers.facebook.com → Create App → Business type.
   Note the **App ID** and **App Secret** (Settings → Basic).
3. **Add the Instagram product** → *API setup with Instagram login*.
4. **Redirect URI** — add `https://YOUR-URL/auth/callback` under Business login.
5. **Fill `.env`** with `PUBLIC_URL`, `META_APP_ID`, `META_APP_SECRET`,
   `WEBHOOK_VERIFY_TOKEN`.
6. **Connect** — open the app → Connect Instagram → approve.
7. **Webhook** — in the App Dashboard, set callback `https://YOUR-URL/webhook`,
   the same verify token, and subscribe to **`messages`** and **`comments`**.
8. **Test** — from a second account, DM your account `price` (or comment `link`)
   and watch the auto-reply land.

---

## Safety — how the account stays safe

- **OAuth only** — never a password.
- **Replies only to inbound engagement** — there is no cold/bulk DM feature.
- **24-hour window** enforced.
- **Send-rate cap** (default 200/hour).
- **Webhook signature verification** and event de-duplication.
- Keep replies **varied and useful** — identical copy-paste messages get reported
  as spam, which reduces delivery even on the official API.

Test on a **throwaway Professional account** until the flow works.

---

## Going live for other people's accounts

Running it for **your own** account needs no review. The moment it serves
Instagram accounts you don't own, you must pass **App Review** for Advanced
Access on `instagram_business_manage_messages` (and
`instagram_business_manage_comments` if comment triggers are used).

---

## Files

```
public/            the web app (index.html, css, js)
docs/              the GitHub Pages static build of the web app
server/
  server.js        routes: API, OAuth, webhook, static
  meta.js          OAuth + Send API client
  automation.js    reply engine (rule matching + guardrails)
  webhook.js       signature verification + event parsing
  data.js          JSON-file storage
Dockerfile / render.yaml / Procfile   deployment configs
.env.example       config template
```
