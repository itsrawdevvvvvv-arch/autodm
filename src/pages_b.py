"""Pages: about, contact, blog (index + posts)."""
from layout import (page, icon, faq_block, cta_band, breadcrumbs, breadcrumb_ld,
                    ORG_LD, EMAIL, INSTAGRAM, SITE, url_for)

# ---------------------------------------------------------------- ABOUT

ABOUT = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:46rem">
    <span class="eyebrow">About</span>
    <h1>We think the inbox is the most under-used surface on the internet.</h1>
    <p class="lede">Viraloop is a small, independent product built for one narrow job: making sure the people who raise their hand in your comments hear back from you before they lose interest.</p>
  </div>
</section>

<section class="section section--tan">
  <div class="wrap grid grid-2" style="gap:clamp(1.5rem,4vw,3rem)">
    <div class="stack">
      <h2>Why we built it</h2>
      <p>Instagram rewards posting and punishes follow-through. You publish a reel, three hundred people comment “link”, and the only tool you have for answering them is your thumb.</p>
      <p>We built Viraloop because the gap between “someone is interested” and “someone got the link” is where most creator revenue quietly dies. Not for lack of audience — for lack of a reply.</p>
    </div>
    <div class="stack">
      <h2>How we work</h2>
      <p>We're a small team, we answer our own support email, and we ship on a weekly rhythm. There is no sales team and no enterprise tier to negotiate — the pricing page is the whole menu.</p>
      <p>If a feature can't be built inside Meta's platform rules, we don't build it. That costs us some growth-hack features that competitors ship, and it's the trade we've chosen.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="stack center" style="max-width:42rem;margin-inline:auto">
      <span class="eyebrow">Principles</span>
      <h2>Four rules we don't bend.</h2>
    </div>
    <div class="grid grid-2 mt-l">
      <article class="card">
        <div class="card__icon">{icon('shield')}</div>
        <h3>Your account comes first</h3>
        <p>Official API scopes, no password sharing, no grey-area automation. If we're ever unsure whether something is allowed, we assume it isn't.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('chat')}</div>
        <h3>No dark patterns</h3>
        <p>No fake scarcity, no invented testimonials, no “only 3 spots left” timers. If we quote a number it will be one we can show you.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('users')}</div>
        <h3>Humans stay in the loop</h3>
        <p>Automation should handle the first reply, not the relationship. Handoff is one click, and the automation never talks over you.</p>
      </article>
      <article class="card">
        <div class="card__icon">{icon('chart')}</div>
        <h3>You own your data</h3>
        <p>Export your automations and logs any time. Disconnect and everything is deleted within 30 days. No lock-in, no hostage data.</p>
      </article>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="wrap split">
    <div class="stack">
      <span class="eyebrow">Under the hood</span>
      <h2>Boring infrastructure, on purpose.</h2>
      <p>The product runs on Meta's official Instagram messaging API, with message processing in the EU/India regions and encrypted storage. This website is a static site — no analytics scripts, no advertising pixels, no cookie banner because there's nothing to consent to.</p>
    </div>
    <div>
      <ul class="list-check card card--ink" style="border-color:var(--paper);box-shadow:6px 6px 0 var(--paper)">
        <li>{icon('check')}<span>Instagram messaging API — approved scopes only</span></li>
        <li>{icon('check')}<span>Messages encrypted in transit and at rest</span></li>
        <li>{icon('check')}<span>Access revocable from Instagram settings, any time</span></li>
        <li>{icon('check')}<span>No third-party trackers on this site</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap grid grid-2" style="align-items:center;gap:clamp(1.5rem,4vw,3rem)">
    <div class="stack">
      <h2>Who's behind it</h2>
      <p>Viraloop is built by a small product team based in India. We're in open beta, which means you'll be talking to the people who write the code rather than a support queue.</p>
      <p class="muted">Company details: [Your Legal Entity], [Registered Address], [City, State, PIN], India. Add your CIN/GSTIN here before launch — Indian consumer-protection rules require seller identity on a commercial site.</p>
      <div class="btn-row"><a class="btn" href="contact.html">Say hello</a></div>
    </div>
    <div class="card card--tan">
      <h3>Talk to a human</h3>
      <p class="mt-m">Email <a href="mailto:{EMAIL}">{EMAIL}</a>. We answer within one working day, usually faster. For product questions, the <a href="help/index.html">help centre</a> covers the common ones.</p>
    </div>
  </div>
</section>

{cta_band(heading="Try it before you trust it.", sub="The beta is free and the setup is reversible — disconnect any time.")}
"""

# ---------------------------------------------------------------- CONTACT

CONTACT = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:40rem">
    <span class="eyebrow">Contact</span>
    <h1>Tell us what you're trying to automate.</h1>
    <p class="lede">Questions about triggers, API access or whether a specific flow is allowed — ask. A human replies, usually within one working day.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap grid grid-2" style="align-items:start;gap:clamp(1.5rem,4vw,3rem)">
    <div class="card">
      <form class="form" data-mailto action="mailto:{EMAIL}" method="post" enctype="text/plain">
        <div class="field">
          <label for="cname">Name</label>
          <input id="cname" name="name" type="text" autocomplete="name" required>
        </div>
        <div class="field">
          <label for="cemail">Email</label>
          <input id="cemail" name="email" type="email" autocomplete="email" required placeholder="you@example.com">
        </div>
        <div class="field">
          <label for="topic">What's it about?</label>
          <select id="topic" name="topic">
            <option>Beta access</option>
            <option>Product question</option>
            <option>Billing</option>
            <option>Something is broken</option>
            <option>Press or partnership</option>
          </select>
        </div>
        <div class="field">
          <label for="msg">Message</label>
          <textarea id="msg" name="message" rows="6" required placeholder="What are you trying to do? The more specific, the better the answer."></textarea>
        </div>
        <button class="btn" type="submit">Send message</button>
        <p class="form__status" role="status" aria-live="polite"></p>
        <p class="hint muted">This opens your email app with the message pre-filled. Nothing is stored on this site.</p>
      </form>
    </div>
    <div class="stack">
      <div class="card card--tan">
        <h3>Email</h3>
        <p class="mt-m"><a href="mailto:{EMAIL}">{EMAIL}</a><br><span class="muted" style="font-size:.9rem">Support and everything else.</span></p>
      </div>
      <div class="card">
        <h3>Instagram</h3>
        <p class="mt-m"><a href="{INSTAGRAM}" rel="me noopener">@viraloop</a><br><span class="muted" style="font-size:.9rem">DMs are open — fitting, really.</span></p>
      </div>
      <div class="card">
        <h3>Response times</h3>
        <p class="mt-m">Beta support: within one working day, Monday to Friday, IST. Security issues: email with “security” in the subject and we'll prioritise it.</p>
      </div>
      <div class="card card--flat" style="border-style:dashed">
        <h3>Before you write</h3>
        <p class="mt-m">Most questions are answered in the <a href="help/index.html">help centre</a> — connecting an account, keyword matching, message limits and billing are all covered there.</p>
      </div>
    </div>
  </div>
</section>
"""

# ---------------------------------------------------------------- BLOG

POSTS = [
    dict(
        slug="comment-to-dm-playbook",
        title="The comment-to-DM playbook",
        h1="The comment-to-DM playbook: writing a trigger that actually converts",
        desc="Most comment automations fail on the copy, not the tool. A practical guide to keywords, DM structure and the one follow-up that's worth sending.",
        date="2026-10-14", mins=7, tag="Playbook",
        body="""
<p>The mechanics of comment automation take ten minutes to set up. The copy takes longer, and it's the only part your audience ever sees. Here's how we'd approach it if we were starting from an empty account today.</p>

<h2>1. Choose keywords people actually type</h2>
<p>Watch your comments for a week before you build anything. You'll see the same five or six phrases over and over: <em>link</em>, <em>price</em>, <em>how much</em>, <em>send it</em>, <em>info</em>, and a pile of emojis. Those are your triggers — not the clever keyword you'd like people to use.</p>
<p>Two rules that save a lot of pain:</p>
<ul>
  <li><strong>Add the misspellings.</strong> Matching is literal. If people type “prce” you either add it or you lose them.</li>
  <li><strong>One trigger, one destination.</strong> A keyword that sends two different links depending on the phase of the moon will confuse you more than your audience.</li>
</ul>

<h2>2. Write the DM like a person, not a receipt</h2>
<p>The weakest DM in this category is a bare URL. It reads like an error message. The strongest is two sentences: what this is, and what to do next.</p>
<blockquote>Here's the pricing sheet you asked for — three plans, no add-ons. If you want, reply “call” and I'll send a booking link.</blockquote>
<p>Notice what that does. It delivers the thing, it sets expectations, and it offers a second, smaller action. That last part matters more than the first: people who won't buy today will happily take a next step that costs them nothing.</p>

<h2>3. Give the DM somewhere to go</h2>
<p>A conversation that ends with a link is a dead end. Decide what the next step is before you send anything: a booking page, a one-question reply, a saved post, a checkout. One step, not three.</p>

<h2>4. Reply to the comment too, sometimes</h2>
<p>A short public reply — “sent it to your DMs 🙌” — does two things. It tells everyone reading the comments that the account is alive and responsive, and it nudges the platform's own ranking signals. It's optional, but it's cheap.</p>

<h2>5. Send exactly one follow-up</h2>
<p>Twelve to twenty-four hours after the link goes out, if there's no reply, send one short nudge: “Did the link come through?” That's it. One. A second follow-up converts almost nobody and annoys everybody, and Instagram's own messaging rules give you limited room anyway.</p>

<h2>What to measure</h2>
<p>Ignore vanity numbers. Three things matter: how many comments matched a trigger, how many of those DMs were opened and replied to, and how many turned into the action you wanted. If replies are high but the final action is low, the problem is the destination. If replies are low, the problem is the DM copy. If matches are low, the problem is your keywords.</p>

<div class="callout"><p><strong>The one mistake to avoid:</strong> promising something in exchange for a follow. It's explicitly against Instagram's platform rules, it's the fastest way to get a tool — and an account — restricted, and it converts worse than a straight answer anyway.</p></div>
"""),
    dict(
        slug="story-replies-warm-leads",
        title="Story replies are your warmest leads",
        h1="Story replies are your warmest leads — and your most ignored inbox",
        desc="Story replies signal intent more strongly than likes or saves, yet they're the first thing creators lose track of. Here's a system for catching them.",
        date="2026-09-30", mins=6, tag="Strategy",
        body="""
<p>A like is a nod. A save is a bookmark. A story reply is someone opening a conversation with you, unprompted, in a private channel. It is the strongest signal Instagram gives you — and for most accounts it lands in a list that nobody ever opens twice.</p>

<h2>Why they get lost</h2>
<p>Story replies arrive in the same inbox as everything else, with no label, no source and no context a day later. By the time you scroll back, the story has expired, you can't tell what prompted the reply, and answering feels awkward. So it doesn't happen.</p>

<h2>What to do instead</h2>
<ul>
  <li><strong>Tag the source.</strong> Every reply should be attached to the story that produced it. “Is this still available?” means something different on a product demo than on a behind-the-scenes clip.</li>
  <li><strong>Answer with a next step, not an answer.</strong> “Yes — two spots left this month. Want the booking link?” moves the conversation; a plain “yes” ends it.</li>
  <li><strong>Let the automation take the first pass.</strong> Most story replies are the same handful of questions. Answer those instantly and keep the unusual ones for yourself.</li>
  <li><strong>Keep the human in the second message.</strong> Automation handles the greeting. The moment it turns into a real conversation, you should be the one typing.</li>
</ul>

<h2>Stories worth automating</h2>
<p>Not every story needs a reply flow. The ones that earn one are the ones with a question sticker, a product reveal, a countdown to something, or a “DM me” prompt. Those are the stories where a fast, specific answer changes the outcome.</p>

<h2>A small test you can run this week</h2>
<p>Post one story with a question sticker. Note every reply by hand for a day — how many, what they asked, what you said back. Then build one automation that answers the most common question with a link. Compare the number of people who take the next step. In our experience the difference is obvious enough after one week that you won't need a bigger sample.</p>
"""),
    dict(
        slug="meta-rules-dm-automation",
        title="What Meta actually allows",
        h1="What Meta actually allows: a creator's guide to DM automation rules",
        desc="Follow-gating, cold DMs, message windows and account bans — a plain-language summary of what Instagram's platform rules mean for automation, and how to stay safe.",
        date="2026-09-12", mins=8, tag="Policy",
        body="""
<p>This is a summary written by a product team, not legal advice — always check Meta's current platform terms yourself. But if you're deciding what to build, these are the lines that matter most.</p>

<h2>Rule one: only reply to people who spoke first</h2>
<p>Automation is for answering, not for prospecting. Sending unsolicited DMs to people who never interacted with you is spam under Meta's rules and will get an account restricted quickly. Every legitimate tool in this category works the same way: a comment, a story reply or a direct message starts the thread.</p>

<h2>Rule two: don't trade rewards for follows</h2>
<p>Requiring someone to follow you before they can receive a link, a file or a discount is the pattern known as follow-gating. It's prohibited, it's the most common reason automation setups get shut down, and it's why we don't offer it — even though it's the single most requested feature we get.</p>
<p>What you can do instead: deliver the thing immediately, and ask for the follow as a friendly, unenforced suggestion in the same message.</p>

<h2>Rule three: respect the messaging window</h2>
<p>Instagram's messaging API is designed around a conversation that's already happening. Automated messages are expected to follow promptly from the user's last message. Anything that looks like a marketing blast to a quiet thread is what gets flagged — which is why we cap follow-ups at one by default.</p>

<h2>Rule four: use the official API, not a browser trick</h2>
<p>Tools that log in as you and click around the interface are violating the terms even when they work. They also break constantly, and when Instagram decides to enforce, the account that gets restricted is yours. Official API access means approved scopes and a connection you can revoke from settings.</p>

<h2>What this means in practice</h2>
<ul>
  <li>Automate the first reply, not the relationship.</li>
  <li>Keep the copy honest and specific — no fake urgency.</li>
  <li>Cap follow-ups, and stop them the moment someone replies.</li>
  <li>Give people a way out: “reply stop” should actually stop things.</li>
  <li>Log everything, so you can prove what was sent and why.</li>
</ul>

<div class="callout"><p><strong>If a tool promises you the grey area,</strong> ask who carries the risk. The answer is always you: the platform restriction lands on your account, not on the vendor's.</p></div>
"""),
]


def post_page(p):
    depth = 1
    import datetime
    pretty = datetime.date.fromisoformat(p['date']).strftime('%d %B %Y').lstrip('0')
    path = f"blog/{p['slug']}.html"
    crumbs = [("Home", "index.html"), ("Blog", "blog/index.html"), (p["title"], None)]
    body = f"""
<article>
  <header class="article-head">
    <div class="wrap stack" style="max-width:44rem">
      {breadcrumbs(crumbs, depth)}
      <span class="eyebrow">{p['tag']}</span>
      <h1 style="font-size:clamp(2rem,4.6vw,3.2rem)">{p['h1']}</h1>
      <p class="muted" style="font-size:.85rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase">{pretty} · {p['mins']} min read · Viraloop team</p>
    </div>
  </header>
  <div class="section">
    <div class="wrap">
      <div class="prose">{p['body']}</div>
      <div class="prose mt-l">
        <div class="card card--tan">
          <h3>Put it into practice</h3>
          <p class="mt-m">Viraloop turns the playbook above into a ten-minute setup: pick a post, add keywords, write the DM. Free while we're in beta.</p>
          <div class="btn-row mt-m"><a class="btn" href="../pricing.html#start">Join the beta</a><a class="btn btn--ghost" href="../help/index.html">Read the help centre</a></div>
        </div>
      </div>
    </div>
  </div>
</article>
{cta_band(depth, heading="Read the next one.", sub="Two more guides on triggers, story replies and staying inside the rules.", label="All articles", href="index.html")}
"""
    ld = [breadcrumb_ld(crumbs, path, depth), {
        "@context": "https://schema.org", "@type": "Article",
        "headline": p["h1"], "description": p["desc"], "datePublished": p["date"],
        "dateModified": p["date"], "author": {"@type": "Organization", "name": "Viraloop"},
        "publisher": {"@type": "Organization", "name": "Viraloop", "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/og.png"}},
        "mainEntityOfPage": url_for(path), "image": SITE + "/assets/img/og.png",
    }]
    page(path, f"{p['title']} | Viraloop blog", p["desc"], body, active="blog", depth=depth, jsonld=ld)


BLOG_INDEX = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:44rem">
    <span class="eyebrow">Blog</span>
    <h1>Notes on turning attention into conversations.</h1>
    <p class="lede">Practical writing about comment triggers, story replies, DM copy and the rules that govern all of it. No growth-hack listicles.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap grid grid-3">
""" + "".join(f"""
    <article class="card post-card">
      <p class="meta">{p['tag']} · {p['mins']} min read</p>
      <h3><a href="{p['slug']}.html">{p['title']}</a></h3>
      <p>{p['desc']}</p>
      <a class="more" href="{p['slug']}.html">Read article →</a>
    </article>""" for p in POSTS) + f"""
  </div>
</section>

<section class="section section--tan">
  <div class="wrap grid grid-2" style="align-items:center;gap:clamp(1.5rem,4vw,3rem)">
    <div class="stack">
      <h2>One short email when we publish.</h2>
      <p>No drip sequence, no “10x your growth” subject lines. A note when there's something worth reading, and nothing in between.</p>
    </div>
    <div class="card">
      <form class="form" data-mailto action="mailto:{EMAIL}" method="post" enctype="text/plain">
        <div class="field">
          <label for="bemail">Email</label>
          <input id="bemail" name="email" type="email" autocomplete="email" required placeholder="you@example.com">
          <span class="hint">Subscribe to the blog.</span>
        </div>
        <button class="btn" type="submit">Subscribe</button>
        <p class="form__status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>
"""


def build():
    page("about.html",
         "About Viraloop — a small team, one narrow job",
         "Viraloop is an independent product built to close the gap between an Instagram comment and a reply. Our principles, how we work, and what we will not build.",
         ABOUT, active="about", jsonld=[ORG_LD])
    page("contact.html",
         "Contact Viraloop — support, beta access, partnerships",
         "Email hello@viraloop.co or use the form. Beta support answers within one working day, Monday to Friday, IST.",
         CONTACT, active="contact")
    page("blog/index.html",
         "Blog — comment triggers, DM copy and platform rules | Viraloop",
         "Practical guides on Instagram DM automation: writing triggers that convert, catching story replies, and staying inside Meta's platform rules.",
         BLOG_INDEX, active="blog", depth=1,
         jsonld=[breadcrumb_ld([("Home", "index.html"), ("Blog", None)], "blog/index.html", 1)])
    for p in POSTS:
        post_page(p)
