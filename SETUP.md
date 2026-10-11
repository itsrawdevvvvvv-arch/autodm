# AutoDM — Setup With Zero Terminal

You will **not** install anything, run any command, or use a terminal.
Everything below is clicking buttons in a browser. Total time: about 20 minutes,
and you only ever do it once.

There are three parts. Do them in order.

---

## PART 1 — Put the engine online (≈5 minutes)

This replaces "npm start". Instead of running on your computer, the engine runs
on a free cloud host called **Render**, so it works 24/7 even when your laptop
is closed.

1. Open **https://render.com** and click **Get Started**.
2. Sign up by clicking **GitHub** (it uses the account your code is already on).
3. Once you're in, click the **New +** button (top right), then choose
   **Blueprint**.
4. It will show a list of your GitHub repositories. Click on **autodm**, then
   click **Connect**.
5. Render reads the settings file already in your repo. Click **Apply**.
6. Render will ask for two values — **META_APP_ID** and **META_APP_SECRET**.
   You don't have these yet (Part 2 gets them). Just click **Apply** / **Create**
   for now and come back — or skip ahead to Part 2 first, then return here.
7. Wait a minute or two. Render finishes and shows a web address at the top,
   something like:

   `https://autodm-abc1.onrender.com`

   **Copy that address somewhere.** That's your app.

> Tip: you can add the two values in step 6 at any time later — on the Render
> service page, open **Environment** and paste them in.

---

## PART 2 — Register your Meta app (≈10 minutes)

This is Meta's own dashboard — free, and it's all clicking.

1. Go to **https://developers.facebook.com** and log in with Facebook.
2. Click **My Apps**, then **Create App**.
3. Pick the **Business** type (if asked, choose "Other" then "Business"). Give
   it any name, like `My AutoDM`. Click **Create**.
4. In the left menu, open **App settings → Basic**.
   - Copy the **App ID** and the **App Secret** (click "Show" to reveal it).
5. Go back to your **Render** service (Part 1) → **Environment**, and paste those
   into **META_APP_ID** and **META_APP_SECRET**. Click **Save**. Render restarts
   itself automatically.
6. Back in the Meta dashboard, add the **Instagram** product. Choose
   **API setup with Instagram login**.
7. Under **Business login settings**, find **OAuth redirect URIs** and add:

   `https://YOUR-RENDER-URL/auth/callback`

   (use the address you copied in Part 1, so it looks like
   `https://autodm-abc1.onrender.com/auth/callback`). Click **Save**.
8. In the **Instagram app** on your phone: **Settings → Messages and story
   replies → Message controls → Connected Tools** → turn **ON**
   "Allow access to messages".

---

## PART 3 — Connect and go (≈2 minutes)

1. Open your Render address in a browser (the `https://autodm-….onrender.com`
   one).
2. Click **Connect Instagram**.
3. Instagram opens its own login/consent page → tap **Allow**.
4. You come back connected. That's it.

Now:
- Go to **Replies** and add a rule (e.g. keyword `price` → your reply).
- Have a friend DM your account the word `price` — you'll see it auto-reply and
  it'll appear under **Activity**.
- You can close your laptop; it keeps running.

---

## If something goes wrong

- **"Add META_APP_ID and META_APP_SECRET to .env"** → you haven't pasted them
  into Render yet (Part 2, step 5).
- **Connect shows an error** → the redirect URI in Meta (Part 2, step 7) must
  match your Render address exactly, including `/auth/callback`.
- **Nothing replies** → check the "Allow access to messages" toggle (Part 2,
  step 8) is on, and that you added a rule under **Replies**.
- **The Render app takes a few seconds to wake up** → free Render apps sleep
  when unused; the first visit after a while is slow, then it's normal.

---

## What you never have to do

- No `npm install`
- No `npm start`
- No localhost
- No terminal
- No installing Node
- No editing code
