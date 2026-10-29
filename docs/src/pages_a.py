"""Pages: home, features, pricing."""
from layout import (page, rel, icon, faq_block, cta_band, ORG_LD, APP_LD, SITE, EMAIL,
                    DEPLOY_URL, REPO_URL, APP_URL, connect_href)

TICK = ["Policy-safe by design", "No follow-gating", "Official Meta API",
        "Replies within a minute", "Built for creators"]

MOCK = """
<figure class="mock" aria-label="Illustration of the Viraloop automation builder">
  <div class="mock__bar" aria-hidden="true">
    <span class="mock__dot"></span><span class="mock__dot"></span><span class="mock__dot"></span>
    <span class="mock__title">Automation builder</span>
  </div>
  <div class="mock__body">
    <div class="mock__row">
      <div class="mock__label">When</div>
      <div class="mock__val">Someone comments on a reel</div>
      <div class="mock__chips">
        <span class="mock__chip">LINK</span><span class="mock__chip">PRICE</span><span class="mock__chip">GUIDE</span>
      </div>
    </div>
    <div class="mock__row mock__row--hl">
      <div class="mock__label">Then</div>
      <div class="mock__val">Send a DM with the right link</div>
    </div>
    <div class="mock__chat">
      <div class="bubble bubble--in">PRICE please</div>
      <div class="bubble bubble--meta">Comment received · matched keyword “PRICE”</div>
      <div class="bubble bubble--out">Here you go — full price list and the booking link: viraloop.co/r/price</div>
    </div>
    <div class="mock__stat"><span>Status</span><strong>Running</strong></div>
    <div class="mock__stat"><span>Queue</span><strong>0</strong></div>
  </div>
</figure>
<p class="muted" style="font-size:.78rem;margin-top:.6rem">Sample workspace. Your automations, your copy, your links.</p>
"""

HOME = f"""
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <span class="eyebrow">Instagram DM automation</span>
      <h1>Turn every comment into a <span class="hl">conversation.</span></h1>
      <p class="lede">Viraloop answers comments and story replies with the right DM within a minute — so the people who were ready to buy hear from you while they still care.</p>
      <div class="btn-row">
        <a class="btn" href="connect.html">Connect Instagram</a>
        <a class="btn btn--ghost" href="#how">See how it works</a>
      </div>
      <p class="hero__note muted">
        <span>{icon('check')} Free forever</span> &nbsp;·&nbsp;
        <span>{icon('check')} One account, no card</span> &nbsp;·&nbsp;
        <span>{icon('check')} Live in about 10 minutes</span>
      </p>
    </div>
    <div>{MOCK}</div>
  </div>
</section>

<section class="section section--tan">
  <div class="wrap">
    <div class="grid grid-2" style="align-items:center;gap:clamp(1.5rem,4vw,3rem)">
      <div class="stack">
        <span class="eyebrow">The gap</span>
        <h2>A comment is the highest-intent message you'll ever get.</h2>
      </div>
      <div class="stack">
        <p>Someone who comments “link?” on your reel is telling you exactly what they want, right now. Reply nine hours later and you're a stranger again. Reply in ten seconds and you're the obvious choice.</p>
        <p>Most creators lose this race because the inbox is manual, the day is full, and DMs don't wait. That's the whole reason Viraloop exists: the reply happens at the speed of the comment, not the speed of your calendar.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="features">
  <div class="wrap">
    <div class="stack center" style="max-width:44rem;margin-inline:auto">
      <span class="eyebrow">What it does</span>
      <h2>One automation engine, six moving parts.</h2>
      <p class="lede" style="margin-inline:auto">Build a flow once and it runs on every post, reel and story — with your words, your links, your tone.</p>
    </div>
    <div class="grid grid-3 mt-l">
      <article class="card">
        <div class="card__icon">{icon('bolt')}</div>
        <h3>Comment triggers</h3>
        <p>Match keywords on any post or reel and send the right DM instantly. One keyword can route to a link, a price list, a booking page or a whole sequence.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('chat')}</div>
        <h3>Story reply capture</h3>
        <p>Turn story replies and sticker taps into a tracked conversation instead of an unread inbox item you'll never find again.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('clock')}</div>
        <h3>Timed follow-ups</h3>
        <p>Nudge a quiet lead minutes or hours later, inside the window Instagram allows. No spam, no cold DMs — just a second chance at the conversation.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('link')}</div>
        <h3>Link delivery</h3>
        <p>Send a clean, trackable link — a resource, a checkout, a form, a call booking — and see which post actually produced the click.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('store')}</div>
        <h3>Creator storefront</h3>
        <p>A single page for your digital products, with checkout built in. Your DMs and your store finally share the same link.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('inbox')}</div>
        <h3>Human handoff</h3>
        <p>When a conversation needs you, the automation stops and hands it over with the full context attached. You never talk to someone twice about the same thing.</p>
      </article>
    </div>
  </div>
</section>

<section class="section" id="how" style="background:var(--paper-2)">
  <div class="wrap">
    <div class="stack center" style="max-width:42rem;margin-inline:auto">
      <span class="eyebrow">Setup</span>
      <h2>Three steps, then it runs itself.</h2>
    </div>
    <div class="grid grid-3 mt-l">
      <div class="step">
        <div class="step__num">1</div>
        <div><h3>Connect Instagram</h3><p>Link the Instagram professional account you already use. Viraloop runs on Meta's official messaging API — no password sharing, no browser tricks.</p></div>
      </div>
      <div class="step">
        <div class="step__num">2</div>
        <div><h3>Write one automation</h3><p>Pick a post, add keywords, write the DM. Preview it exactly as your follower will see it before anything goes live.</p></div>
      </div>
      <div class="step">
        <div class="step__num">3</div>
        <div><h3>Let it reply</h3><p>Comments get answered in seconds, day or night. You watch the conversations and step in whenever you want.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="wrap split">
    <div class="stack">
      <span class="eyebrow">Why we're careful</span>
      <h2>Policy-safe by design.</h2>
      <p>Half the DM automation advice online will get your account restricted. Requiring a follow before unlocking a link, blasting cold DMs to scraped lists, faking human replies — Meta's rules are clear that none of that is allowed, and the enforcement lands on you, not on the tool that suggested it.</p>
      <p>Viraloop only builds what the official API supports. That makes us slightly less flashy and considerably less likely to cost you your account.</p>
    </div>
    <div>
      <ul class="list-check card card--ink" style="border-color:var(--paper);box-shadow:6px 6px 0 var(--paper)">
        <li>{icon('check')}<span><strong>No follow-gating.</strong> We never require someone to follow you to receive a link. Meta prohibits it and we won't build it.</span></li>
        <li>{icon('check')}<span><strong>No cold DMs.</strong> We only reply to people who messaged or commented first.</span></li>
        <li>{icon('check')}<span><strong>Official API only.</strong> Meta-approved scopes, revocable any time from your Instagram settings.</span></li>
        <li>{icon('check')}<span><strong>You can see everything.</strong> Every automated message is logged with the trigger that caused it.</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="stack center" style="max-width:40rem;margin-inline:auto">
      <span class="eyebrow">Pricing</span>
      <h2>Free. One account. No card.</h2>
      <p class="lede" style="margin-inline:auto">Viraloop runs on your own server for your own Instagram account. There is no plan to choose and no trial that expires.</p>
    </div>
    <div class="grid grid-2 mt-l" style="align-items:start">
      <div class="card">
        <span class="pill">Everything included</span>
        <h3 style="margin-top:.8rem">What you get</h3>
        <ul class="list-check mt-m">
          <li>{icon('check')}<span>Unlimited automations and unlimited automated DMs</span></li>
          <li>{icon('check')}<span>Comment triggers, story replies and DM keywords</span></li>
          <li>{icon('check')}<span>Public reply + private DM on the same comment</span></li>
          <li>{icon('check')}<span>Dry-run tester, activity log, hourly safety cap</span></li>
          <li>{icon('check')}<span>Runs on polling — no public URL or webhook needed</span></li>
          <li>{icon('check')}<span>Your data in a JSON file you can read and delete</span></li>
        </ul>
      </div>
      <div class="card card--ink">
        <p class="small" style="opacity:.75">Cost</p>
        <p class="plan__price" style="color:var(--paper)">₹0 <small>/ forever</small></p>
        <p style="margin-top:.8rem;opacity:.9">No subscription, no per-message charge, no upsell. It runs on Cloudflare's free Workers plan, which asks for no card at all.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn" href="{DEPLOY_URL}" rel="noopener">Deploy it free</a>
          <a class="btn btn--ghost" href="pricing.html">How it works</a>
        </div>
      </div>
    </div>
  </div>
</section>

{faq_block([
  ("Will this get my Instagram account banned?",
   "No. Viraloop only uses Meta's official Instagram messaging API with approved scopes, and we deliberately do not support follow-gating, cold DMs or any pattern Meta's platform rules prohibit. If a feature can't be built within the rules, we don't ship it."),
  ("Do I need a business or creator account?",
   "Yes — automation requires an Instagram professional account (Creator or Business) linked to a Facebook page. Switching is free and reversible inside Instagram settings."),
  ("Does it reply to every comment?",
   "Only the ones you ask it to. You choose the keywords per post, and anything that doesn't match stays in your normal inbox for you to answer yourself."),
  ("What happens to my data?",
   "We store your account details, automation settings and message logs so the product can work. We don't sell data, we don't run advertising pixels on this site, and you can delete everything by disconnecting the account or emailing us. The <a href=\"privacy.html\">privacy policy</a> lists exactly what's processed."),
  ("Is it really free?",
   "Yes — no plan, no card, no trial. Viraloop is software you run yourself for a single Instagram account, and the Cloudflare Workers free plan costs nothing."),
  ("What's the catch?",
   "There isn't one. It runs on your own server, so there is no bill to send you. If you later want it hosted for you with more accounts, that would be a separate conversation — nothing on this page changes."),
])}

{cta_band()}
"""


# ---------------------------------------------------------------- FEATURES

def split_block(title, body_html, mock_html, reverse=False, eyebrow=""):
    cls = "split split--rev" if reverse else "split"
    eb = f'<span class="eyebrow">{eyebrow}</span>' if eyebrow else ""
    return f"""
<section class="section">
  <div class="wrap {cls}">
    <div class="stack">{eb}<h2>{title}</h2>{body_html}</div>
    <div class="split__media">{mock_html}</div>
  </div>
</section>"""


def mini_mock(rows, title="Automation"):
    inner = "".join(rows)
    return f"""<div class="mock">
  <div class="mock__bar" aria-hidden="true"><span class="mock__dot"></span><span class="mock__dot"></span><span class="mock__dot"></span><span class="mock__title">{title}</span></div>
  <div class="mock__body">{inner}</div>
</div>"""


FEATURES = f"""
<section class="hero">
  <div class="wrap stack center" style="max-width:46rem;margin-inline:auto">
    <span class="eyebrow">Features</span>
    <h1>Everything between a comment and a customer.</h1>
    <p class="lede" style="margin-inline:auto">Six features, one engine. Each one is built to do a specific job in the funnel — and to stay inside Instagram's rules while doing it.</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="pricing.html#start">Get it free</a>
      <a class="btn btn--ghost" href="pricing.html">See pricing</a>
    </div>
  </div>
</section>

{split_block(
  "Comment triggers that actually match how people type.",
  "<p>People comment <em>link</em>, <em>LINK!!</em>, <em>send it</em>, <em>price?</em> or a single emoji. Viraloop matches keywords case-insensitively, accepts several spellings per trigger, and supports a catch-all for everything else.</p>"
  "<ul class=\"list-check\"><li>" + icon('check') + "<span>Multiple keywords per trigger, per post</span></li><li>" + icon('check') + "<span>Separate replies for different posts and reels</span></li><li>" + icon('check') + "<span>Optional reply to the public comment as well as the DM</span></li></ul>",
  mini_mock([
    '<div class="mock__row"><div class="mock__label">Keywords</div><div class="mock__chips"><span class="mock__chip">link</span><span class="mock__chip">price</span><span class="mock__chip">kit</span><span class="mock__chip">send it</span></div></div>',
    '<div class="mock__row mock__row--hl"><div class="mock__label">DM sent</div><div class="mock__val">“Here’s the kit — one page, no fluff.”</div></div>',
  ], "Trigger"),
  eyebrow="01 — capture")}

{split_block(
  "Story replies, finally out of the void.",
  "<p>Story replies are the warmest messages you get and the easiest to lose. Viraloop picks them up, tags them against the story that produced them, and can hand back the right link straight away.</p>"
  "<ul class=\"list-check\"><li>" + icon('check') + "<span>Works with story replies and sticker taps</span></li><li>" + icon('check') + "<span>Every reply is attributed to the story it came from</span></li><li>" + icon('check') + "<span>Auto-reply, or queue it for you to answer</span></li></ul>",
  mini_mock([
    '<div class="mock__chat"><div class="bubble bubble--in">is this still available?</div><div class="bubble bubble--meta">Story reply · “Studio tour, ep. 4”</div><div class="bubble bubble--out">Yes — two spots left this month. Want the booking link?</div></div>',
    '<div class="mock__stat"><span>Attributed to</span><strong>Studio tour, ep. 4</strong></div>',
  ], "Story"),
  reverse=True, eyebrow="02 — stories")}

{split_block(
  "Follow-ups with manners.",
  "<p>A gentle nudge twelve hours after a link was sent recovers conversations that would otherwise go quiet. Viraloop schedules it inside Instagram's messaging window and stops the moment someone replies.</p>"
  "<ul class=\"list-check\"><li>" + icon('check') + "<span>Configurable delay: minutes, hours, or next day</span></li><li>" + icon('check') + "<span>Sequence stops automatically on any reply</span></li><li>" + icon('check') + "<span>Hard limit of one follow-up per conversation, by default</span></li></ul>",
  mini_mock([
    '<div class="mock__row"><div class="mock__label">Delay</div><div class="mock__val">12 hours</div></div>',
    '<div class="mock__row"><div class="mock__label">If no reply</div><div class="mock__val">Send one reminder, then stop</div></div>',
    '<div class="mock__stat"><span>Follow-ups per conversation</span><strong>1</strong></div>',
  ], "Sequence"),
  eyebrow="03 — nuture")}

<section class="section section--tan">
  <div class="wrap stack" style="max-width:48rem;margin-inline:auto">
    <span class="eyebrow">How we compare</span>
    <h2>Manual DMs, a generic chatbot, or this.</h2>
    <div class="table-wrap">
      <table>
        <caption class="sr-only">Comparison of manual replies, generic chatbots and Viraloop</caption>
        <thead><tr><th scope="col">Job to be done</th><th scope="col">Manual</th><th scope="col">Generic bot</th><th scope="col">Viraloop</th></tr></thead>
        <tbody>
          <tr><td>Reply speed at 2am</td><td>Nobody home</td><td>Instant</td><td class="yes">Instant</td></tr>
          <tr><td>Knows which post caused the DM</td><td>Sometimes</td><td>Rarely</td><td class="yes">Always</td></tr>
          <tr><td>Stays inside Meta's rules</td><td>Yes</td><td>Depends</td><td class="yes">Built that way</td></tr>
          <tr><td>Hands off to a human with context</td><td>—</td><td>Clunky</td><td class="yes">One click</td></tr>
          <tr><td>Sells digital products</td><td>Link in bio</td><td>No</td><td class="yes">Built-in storefront</td></tr>
          <tr><td>Set-up time</td><td>Zero</td><td>Days</td><td class="yes">~10 minutes</td></tr>
        </tbody>
      </table>
    </div>
    <p class="muted" style="font-size:.85rem">“Generic bot” means a keyword auto-responder that isn't connected to Instagram's official messaging API.</p>
  </div>
</section>

{cta_band(heading="Pick a post. Add a keyword. Reply forever.", sub="Free forever, one account, about ten minutes to set up.")}
"""


# ---------------------------------------------------------------- PRICING

PRICING = f"""
<section class="hero">
  <div class="wrap stack center" style="max-width:44rem;margin-inline:auto">
    <span class="eyebrow">Pricing</span>
    <h1>Free. One account. No card.</h1>
    <p class="lede" style="margin-inline:auto">Viraloop is software you run for your own Instagram account. No plan, no trial, no invoice — the only optional cost is hosting.</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="{DEPLOY_URL}" rel="noopener">Deploy it free</a>
      <a class="btn btn--ghost" href="#start">Run it locally</a>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap grid grid-2" style="align-items:start">
    <div class="card">
      <span class="pill">Everything, always</span>
      <h3 style="margin-top:.8rem">Included</h3>
      <ul class="list-check mt-m">
        <li>{icon('check')}<span>Unlimited automations, unlimited automated replies</span></li>
        <li>{icon('check')}<span>Comment triggers with public reply + private DM</span></li>
        <li>{icon('check')}<span>DM keyword rules and story reply handling</span></li>
        <li>{icon('check')}<span>Dry-run tester — see the exact reply before it sends</span></li>
        <li>{icon('check')}<span>Activity log of every automated message</span></li>
        <li>{icon('check')}<span>Hourly safety cap so a loop can never run away</span></li>
        <li>{icon('check')}<span>Optional access key to lock the dashboard</span></li>
        <li>{icon('check')}<span>Full source, no telemetry, no third-party trackers</span></li>
      </ul>
    </div>
    <div class="card card--tan">
      <h3>What it actually costs</h3>
      <div class="table-wrap" style="margin-top:.9rem;box-shadow:none">
        <table style="min-width:0">
          <tbody>
            <tr><td>Viraloop</td><td class="yes">₹0</td></tr>
            <tr><td>Meta Instagram API</td><td class="yes">₹0</td></tr>
            <tr><td>Cloudflare Workers (free plan)</td><td class="yes">₹0</td></tr>
            <tr><td>Cloudflare paid plan</td><td>optional, not needed</td></tr>
          </tbody>
        </table>
      </div>
      <p class="small" style="margin-top:.9rem">Free hosting sleeps after inactivity, so replies can be delayed by a minute or two until the next request wakes it. A paid instance removes that. Either way, the software is free.</p>
    </div>
  </div>
</section>

<section class="section" id="start">
  <div class="wrap">
    <div class="stack center" style="max-width:40rem;margin-inline:auto">
      <span class="eyebrow">Getting it running</span>
      <h2>Three steps and it's yours.</h2>
    </div>
    <div class="grid grid-3 mt-l">
      <div class="step">
        <div class="step__num">1</div>
        <div>
          <h3>Deploy</h3>
          <p>Four commands on the free Cloudflare Workers plan — or <code>npm start</code> on your own machine. No card, no build step.</p>
        </div>
      </div>
      <div class="step">
        <div class="step__num">2</div>
        <div>
          <h3>Connect your account</h3>
          <p>Paste a long-lived Instagram access token in the dashboard. It's stored on your server only, and you can revoke it from Instagram settings any time.</p>
        </div>
      </div>
      <div class="step">
        <div class="step__num">3</div>
        <div>
          <h3>Write one automation</h3>
          <p>Pick keywords, write the DM, test it against a sample comment, then leave it running. Polling starts automatically.</p>
        </div>
      </div>
    </div>
    <div class="card mt-l" style="max-width:44rem;margin-inline:auto">
      <h3>Deploy on Cloudflare — free, no card</h3>
      <p class="small muted" style="margin:.4rem 0 .7rem">Needs Node 18+ and a free Cloudflare account.</p>
      <div class="prose"><pre style="overflow-x:auto"><code>git clone https://github.com/itsrawdevvvvvv-arch/autodm.git
cd autodm &amp;&amp; npm install
npx wrangler login
npx wrangler d1 create viraloop
npx wrangler d1 execute viraloop --remote --file=migrations/0001_init.sql
npx wrangler deploy</code></pre></div>
      <p class="small" style="margin-top:.7rem">Paste the D1 id it prints into <code>wrangler.toml</code> before deploying, then add the secrets with <code>npx wrangler secret put META_APP_ID</code> (and <code>META_APP_SECRET</code>, <code>PUBLIC_URL</code>, <code>APP_KEY</code>).</p>
      <p class="small muted" style="margin-top:.5rem">Prefer your own machine? <code>npm install &amp;&amp; npm start</code> runs the same app at <code>localhost:3000</code> using a JSON file store.</p>
    </div>
  </div>
</section>

{faq_block([
  ("Is it really free, or free for now?",
   "Free, with nothing to upgrade to. Viraloop is a single-account tool that runs on your own server, so there is no subscription to bill. There is no paid tier on this site and no waitlist."),
  ("What's the catch?",
   "The honest trade-off: you host it yourself. That means a free Cloudflare account (Workers + D1, no card) or a machine that stays on, and a Meta app with messaging permission. In exchange you get no per-message pricing and no vendor holding your data."),
  ("Do I need to apply for Meta app review?",
   "Not to get started. A long-lived token from your own Meta app is enough for your own account, which is the intended use here. Public, multi-user distribution would need app review — that's out of scope."),
  ("Can I use it for more than one Instagram account?",
   "One account per deployment. That's deliberate: it keeps the token, the data and the blast radius small. A second account means a second deployment."),
  ("What happens to my data?",
   "It lives in a JSON file on your server — account details, automation rules and the activity log. Nobody else can read it, there is no telemetry, and deleting the file deletes the data. See the <a href=\"privacy.html\">privacy policy</a>."),
  ("Will this get my account restricted?",
   "It only replies to people who commented or messaged first, it caps replies per hour, and it never requires a follow to unlock anything. Those are the behaviours that get accounts restricted, and none of them exist in the code."),
])}

{cta_band(heading="Ten minutes from here to your first automated reply.",
         sub="Free forever, one account, no card.",
         label="Deploy it free", href="#start")}
"""


def build():
    page("index.html",
         "Viraloop — Instagram DM automation for creators",
         "Turn Instagram comments and story replies into instant DMs. Keyword triggers, timed follow-ups, trackable links and a storefront — on Meta's official API.",
         HOME, active="home", jsonld=[ORG_LD, APP_LD,
         {"@context": "https://schema.org", "@type": "WebSite", "name": "Viraloop",
          "url": SITE + "/", "publisher": {"@type": "Organization", "name": "Viraloop"}}],
         tick=TICK)
    page("features.html",
         "Features — comment triggers, story DMs and follow-ups | Viraloop",
         "Every part of the Viraloop engine: keyword comment triggers, story reply capture, timed follow-ups, trackable link delivery, creator storefront and human handoff.",
         FEATURES, active="features")
    page("pricing.html",
         "Pricing — free, one account, no card | Viraloop",
         "Viraloop is free: unlimited automations for one Instagram account, self-hosted. No subscription, no card, no paid tier — the only optional cost is hosting.",
         PRICING, active="pricing", jsonld=[APP_LD])
