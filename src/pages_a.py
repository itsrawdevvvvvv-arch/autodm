"""Pages: home, features, pricing."""
from layout import (page, rel, icon, faq_block, cta_band, ORG_LD, APP_LD, SITE, EMAIL)

TICK = ["Policy-safe by design", "No follow-gating", "Official Meta API",
        "Replies in under two seconds", "Built for creators"]

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
      <p class="lede">Viraloop answers comments and story replies with the right DM in seconds — so the people who were ready to buy hear from you while they still care.</p>
      <div class="btn-row">
        <a class="btn" href="pricing.html#start">Join the free beta</a>
        <a class="btn btn--ghost" href="#how">See how it works</a>
      </div>
      <p class="hero__note muted">
        <span>{icon('check')} Free while in beta</span> &nbsp;·&nbsp;
        <span>{icon('check')} No card required</span> &nbsp;·&nbsp;
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
      <h2>Free while we're in beta.</h2>
      <p class="lede" style="margin-inline:auto">Join now and your first six months after launch are free on the Creator plan. No card, no auto-charge.</p>
    </div>
    <div class="plans mt-l">
      <div class="card plan">
        <span class="pill">Beta</span>
        <h3>Free</h3>
        <p class="plan__price">₹0 <small>/ month</small></p>
        <p class="plan__meta">Everything, while we're in beta.</p>
        <ul class="list-check">
          <li>{icon('check')}<span>1 Instagram account</span></li>
          <li>{icon('check')}<span>5 live automations</span></li>
          <li>{icon('check')}<span>1,000 automated DMs / month</span></li>
          <li>{icon('check')}<span>Email support</span></li>
        </ul>
        <a class="btn btn--ghost" href="pricing.html#start">Join beta</a>
      </div>
      <div class="card plan plan--featured">
        <span class="pill">Most popular</span>
        <h3>Creator</h3>
        <p class="plan__price">₹499 <small>/ month after beta</small></p>
        <p class="plan__meta">For creators running a real funnel.</p>
        <ul class="list-check">
          <li>{icon('check')}<span>1 Instagram account</span></li>
          <li>{icon('check')}<span>25 live automations</span></li>
          <li>{icon('check')}<span>10,000 automated DMs / month</span></li>
          <li>{icon('check')}<span>Timed follow-ups + storefront</span></li>
        </ul>
        <a class="btn" href="pricing.html#start">Join beta — free</a>
      </div>
      <div class="card plan">
        <span class="pill">Studio</span>
        <h3>Agency</h3>
        <p class="plan__price">₹1,499 <small>/ month after beta</small></p>
        <p class="plan__meta">For teams and managers.</p>
        <ul class="list-check">
          <li>{icon('check')}<span>3 Instagram accounts</span></li>
          <li>{icon('check')}<span>Unlimited automations</span></li>
          <li>{icon('check')}<span>50,000 automated DMs / month</span></li>
          <li>{icon('check')}<span>3 seats + onboarding call</span></li>
        </ul>
        <a class="btn btn--ghost" href="pricing.html#start">Talk to us</a>
      </div>
    </div>
    <p class="center muted mt-m" style="font-size:.85rem">All plans include the official Meta API integration, full message logs and unlimited manual replies. <a href="pricing.html">Full comparison →</a></p>
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
  ("Is it really free right now?",
   "Yes. The product is in open beta and costs nothing. When paid plans start, beta users get six months of Creator free — we'll email you before anything changes, and nothing auto-charges."),
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
      <a class="btn" href="pricing.html#start">Join the free beta</a>
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

{cta_band(heading="Pick a post. Add a keyword. Reply forever.", sub="The beta is free and takes about ten minutes to set up.")}
"""


# ---------------------------------------------------------------- PRICING

PRICING = f"""
<section class="hero">
  <div class="wrap stack center" style="max-width:44rem;margin-inline:auto">
    <span class="eyebrow">Pricing</span>
    <h1>Free while we're in beta. Honest after.</h1>
    <p class="lede" style="margin-inline:auto">No trials that quietly convert, no annual lock-in, no per-seat surprises. One price per account, cancel whenever.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="plans">
      <div class="card plan">
        <span class="pill">Beta</span>
        <h3>Free</h3>
        <p class="plan__price">₹0 <small>/ month</small></p>
        <p class="plan__meta">While we're in open beta. No card.</p>
        <ul class="list-check">
          <li>{icon('check')}<span>1 Instagram account</span></li>
          <li>{icon('check')}<span>5 live automations</span></li>
          <li>{icon('check')}<span>1,000 automated DMs / month</span></li>
          <li>{icon('check')}<span>Comment + story triggers</span></li>
          <li>{icon('check')}<span>Email support</span></li>
        </ul>
        <a class="btn btn--ghost" href="#start">Join beta</a>
      </div>
      <div class="card plan plan--featured">
        <span class="pill">Most popular</span>
        <h3>Creator</h3>
        <p class="plan__price">₹499 <small>/ month, after beta</small></p>
        <p class="plan__meta">Free for six months for beta users.</p>
        <ul class="list-check">
          <li>{icon('check')}<span>1 Instagram account</span></li>
          <li>{icon('check')}<span>25 live automations</span></li>
          <li>{icon('check')}<span>10,000 automated DMs / month</span></li>
          <li>{icon('check')}<span>Timed follow-ups</span></li>
          <li>{icon('check')}<span>Creator storefront + checkout</span></li>
          <li>{icon('check')}<span>Priority email support</span></li>
        </ul>
        <a class="btn" href="#start">Join beta — free</a>
      </div>
      <div class="card plan">
        <span class="pill">Studio</span>
        <h3>Agency</h3>
        <p class="plan__price">₹1,499 <small>/ month, after beta</small></p>
        <p class="plan__meta">For managers running several accounts.</p>
        <ul class="list-check">
          <li>{icon('check')}<span>3 Instagram accounts</span></li>
          <li>{icon('check')}<span>Unlimited automations</span></li>
          <li>{icon('check')}<span>50,000 automated DMs / month</span></li>
          <li>{icon('check')}<span>3 team seats</span></li>
          <li>{icon('check')}<span>CSV export + onboarding call</span></li>
        </ul>
        <a class="btn btn--ghost" href="#start">Talk to us</a>
      </div>
    </div>
    <p class="center muted mt-m" style="font-size:.85rem">Prices in INR, exclusive of GST. International cards are charged in INR; your bank converts.</p>
  </div>
</section>

<section class="section section--tan">
  <div class="wrap">
    <h2>What's in each plan</h2>
    <div class="table-wrap mt-m">
      <table>
        <caption class="sr-only">Feature comparison across the Free, Creator and Agency plans</caption>
        <thead><tr><th scope="col">Feature</th><th scope="col">Free</th><th scope="col">Creator</th><th scope="col">Agency</th></tr></thead>
        <tbody>
          <tr><td>Instagram accounts</td><td>1</td><td>1</td><td>3</td></tr>
          <tr><td>Live automations</td><td>5</td><td>25</td><td>Unlimited</td></tr>
          <tr><td>Automated DMs / month</td><td>1,000</td><td>10,000</td><td>50,000</td></tr>
          <tr><td>Comment + story triggers</td><td class="yes">Yes</td><td class="yes">Yes</td><td class="yes">Yes</td></tr>
          <tr><td>Timed follow-ups</td><td>—</td><td class="yes">Yes</td><td class="yes">Yes</td></tr>
          <tr><td>Creator storefront</td><td class="yes">Yes</td><td class="yes">Yes</td><td class="yes">Yes</td></tr>
          <tr><td>Team seats</td><td>1</td><td>1</td><td>3</td></tr>
          <tr><td>Message log retention</td><td>30 days</td><td>12 months</td><td>12 months</td></tr>
          <tr><td>Support</td><td>Email</td><td>Priority email</td><td>Onboarding call</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="section" id="start">
  <div class="wrap grid grid-2" style="align-items:start;gap:clamp(1.5rem,4vw,3rem)">
    <div class="stack">
      <span class="eyebrow">Beta access</span>
      <h2>Get in early.</h2>
      <p>Tell us where to reach you and we'll send your workspace invite, usually within one working day. Beta accounts keep six months of Creator free when paid plans begin.</p>
      <ul class="list-check">
        <li>{icon('check')}<span>No card, nothing auto-charges</span></li>
        <li>{icon('check')}<span>One email from us, then your invite</span></li>
        <li>{icon('check')}<span>Leave any time by replying to that email</span></li>
      </ul>
      <div class="card card--tan">
        <p style="font-size:.9rem"><strong>Prefer email?</strong> Write to <a href="mailto:{EMAIL}">{EMAIL}</a> with your Instagram handle and we'll set you up manually.</p>
      </div>
    </div>
    <div class="card">
      <form class="form" data-mailto action="mailto:{EMAIL}" method="post" enctype="text/plain">
        <div class="field">
          <label for="name">Your name</label>
          <input id="name" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="email">Email</label>
          <input id="email" name="email" type="email" autocomplete="email" required placeholder="you@example.com">
        </div>
        <div class="field">
          <label for="handle">Instagram handle</label>
          <input id="handle" name="handle" type="text" placeholder="@yourhandle" required>
          <span class="hint">Must be a Creator or Business account.</span>
        </div>
        <div class="field">
          <label for="plan">Plan you're interested in</label>
          <select id="plan" name="plan">
            <option>Free beta</option>
            <option>Creator (₹499/mo after beta)</option>
            <option>Agency (₹1,499/mo after beta)</option>
            <option>Not sure yet</option>
          </select>
        </div>
        <div class="field field--check">
          <input id="consent" name="consent" type="checkbox" required>
          <label for="consent" style="font-weight:400;font-size:.9rem">I agree to the <a href="terms.html">terms of service</a> and <a href="privacy.html">privacy policy</a>, and to being contacted about my beta invite.</label>
        </div>
        <button class="btn btn--block" type="submit">Request beta access</button>
        <p class="form__status" role="status" aria-live="polite"></p>
        <p class="hint muted">This form opens your email app — nothing is stored on this site.</p>
      </form>
    </div>
  </div>
</section>

{faq_block([
  ("What happens when the beta ends?",
   "Paid plans start and every beta account gets six months of Creator free, from that date. We email you at least two weeks before anything changes, and nothing charges without you adding payment details."),
  ("Do you charge per follower or per message?",
   "Per automated DM, with a generous monthly cap. Manual replies you send yourself are always unlimited and never counted."),
  ("Can I cancel?",
   "Yes, in one click from billing settings. Your automations stop, your data stays available for 30 days in case you change your mind, then it's deleted."),
  ("Do you offer refunds?",
   "If a paid month goes wrong, email us within 14 days of the charge and we'll refund it. No forms, no arguing."),
  ("Is GST included?",
   "Prices are exclusive of GST. Indian customers see GST added at checkout with a valid GSTIN for input credit."),
])}

{cta_band(heading="Ten minutes from here to your first automated reply.",
         sub="Free in beta. Bring a Creator or Business account and one post you'd like to test.",
         label="Request access", href="#start")}
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
         "Pricing — free in beta, ₹499 after | Viraloop",
         "Viraloop pricing: free during open beta, then ₹499/month for Creator and ₹1,499/month for Agency. No card required, cancel any time, GST extra.",
         PRICING, active="pricing", jsonld=[APP_LD])
