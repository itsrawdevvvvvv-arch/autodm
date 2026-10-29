"""Pages: help centre (index + articles), terms, privacy, 404."""
from layout import (page, icon, cta_band, breadcrumbs, breadcrumb_ld, EMAIL,
                    SITE, BASE_PATH, UPDATED, faq_block, APP_URL, DEPLOY_URL)

# ---------------------------------------------------------------- HELP ARTICLES

HELP = [
    dict(slug="getting-started", title="Set up your first automation",
         h1="Set up your first automation in ten minutes",
         desc="A step-by-step walkthrough: connect Instagram, choose a post, add keywords, write the DM and test it before going live.",
         tag="Getting started", mins=5,
         body="""
<p>This walkthrough takes you from a fresh account to a live automation on a single post. If something doesn't behave the way this page describes, see <a href="troubleshooting.html">troubleshooting</a>.</p>

<h2 id="before">Before you start</h2>
<ul>
  <li>An Instagram <strong>Creator</strong> or <strong>Business</strong> account (not personal).</li>
  <li>A Facebook page linked to that account — Instagram requires it for API access.</li>
  <li>One post or reel you'd like to test on. Pick something with real comments.</li>
</ul>

<h2 id="connect">1. Connect the account</h2>
<p>From the workspace, choose <strong>Connect Instagram</strong> and approve the requested permissions. You'll be returned to Viraloop with the account listed and a green status. See <a href="connect-instagram.html">connect your Instagram account</a> if the connection fails.</p>

<h2 id="create">2. Create the automation</h2>
<p>Choose <strong>New automation</strong>, then pick the post or reel. Give it a name you'll recognise later — “Price list — launch reel” beats “Automation 3”.</p>

<h2 id="keywords">3. Add keywords</h2>
<p>Enter the phrases people actually type: <code>price</code>, <code>pricing</code>, <code>cost</code>, <code>how much</code>. Matching ignores case but is otherwise literal, so add the variations you see in your comments.</p>

<h2 id="message">4. Write the DM</h2>
<p>Two sentences: what this is, and what to do next. Preview it — the preview is exactly what the follower receives, including how the link renders.</p>
<div class="callout"><p>Keep the first message short. A wall of text in a DM reads like spam, and long messages get skimmed rather than read.</p></div>

<h2 id="test">5. Test before going live</h2>
<p>Use <strong>Send test</strong> to deliver the message to your own account. Check the link, the tone and the fallback text. Then switch the automation to <strong>Live</strong>.</p>

<h2 id="after">6. Watch the first day</h2>
<p>Open the log after a few hours. You're looking for three things: whether the keywords matched the comments people actually left, whether the DM copy produced replies, and whether anyone needed a human. Adjust keywords first — it's the cheapest fix.</p>
"""),
    dict(slug="connect-instagram", title="Connect your Instagram account",
         h1="Connect your Instagram account",
         desc="The one-click OAuth flow, the permissions it asks for, the requirements, and fixes for the usual connection errors.",
         tag="Setup", mins=5,
         body="""
<p>There are two ways to connect: the <strong>Connect Instagram</strong> button, which runs Meta's standard authorisation flow, or pasting a long-lived token by hand. Both end in the same place.</p>

<h2 id="oneclick">The one-click flow</h2>
<ol>
  <li>Press <strong>Connect Instagram</strong> in the dashboard (or on the <a href="../connect.html">connect page</a>).</li>
  <li>Instagram opens its own permission screen. Approve the three scopes listed below.</li>
  <li>You land back in the dashboard with the account connected and polling already running.</li>
</ol>
<p>Behind that: the app sends you to <code>instagram.com/oauth/authorize</code> with a one-time <code>state</code> value, exchanges the returned code for a long-lived token (~60 days), and stores it on your server only.</p>

<h2 id="scopes">The three permissions</h2>
<ul>
  <li><code>instagram_business_basic</code> — your profile and media list, so the app knows which posts to watch.</li>
  <li><code>instagram_business_manage_messages</code> — read and send DMs, so it can reply.</li>
  <li><code>instagram_business_manage_comments</code> — read comments, so it can spot keyword matches.</li>
</ul>

<h2 id="requirements">Requirements</h2>
<ul>
  <li>An Instagram <strong>Creator</strong> or <strong>Business</strong> account.</li>
  <li>A Meta app with the Instagram product added, and your account added as a tester.</li>
  <li><code>META_APP_ID</code> and <code>META_APP_SECRET</code> set on the server.</li>
  <li><code>PUBLIC_URL</code> set to your deployed https URL, and that exact URL registered as a Valid OAuth Redirect URI (ending <code>/auth/callback</code>).</li>
</ul>
<p>The dashboard tells you which of these is missing: open <strong>Account</strong> and read the setup note, or hit <code>/api/oauth-check</code> on your server.</p>

<h2 id="token">Connecting with a token instead</h2>
<p>In the Meta dashboard, generate a long-lived token with the three scopes above and paste it into <strong>Account → paste an access token</strong>. Useful when you can't set up a redirect URI, or when you want to connect on a machine with no public URL.</p>

<h2 id="revoke">Revoking access</h2>
<p>Dashboard → <strong>Disconnect</strong> deletes the stored token. To revoke at Meta's side as well, remove the app in Instagram → Settings → Apps and websites. Disconnecting stops all automations immediately.</p>

<h2 id="errors">Common errors</h2>
<ul>
  <li><strong>Invalid redirect URI</strong> — the registered URI and <code>PUBLIC_URL</code> differ. They must match character for character, https included.</li>
  <li><strong>App in development mode</strong> — add your account as a tester on the Meta app; no app review needed for personal use.</li>
  <li><strong>Insufficient permissions</strong> — a scope was declined. Reconnect and approve all three.</li>
  <li><strong>Link expired</strong> — the <code>state</code> value is only valid for ten minutes. Press Connect again.</li>
</ul>
"""),
    dict(slug="comment-triggers", title="Keywords and matching",
         h1="Keywords, matching, and what happens when nothing matches",
         desc="How Viraloop matches comments to triggers, how to handle misspellings and emojis, and how to set a safe catch-all reply.",
         tag="Automation", mins=5,
         body="""
<p>Matching is deliberately simple and predictable: if a comment contains one of your keywords, the automation fires. Here's how to make that behave well.</p>

<h2 id="how">How matching works</h2>
<ul>
  <li>Matching is <strong>case-insensitive</strong>: <code>Price</code> and <code>price</code> are the same trigger.</li>
  <li>Matching is <strong>substring-based</strong>: the keyword <code>link</code> also matches “link please” and “linkk”.</li>
  <li>Each trigger can hold several keywords, and several triggers can watch the same post.</li>
  <li>If two triggers match, the <strong>more specific</strong> one wins — the one with the longer matching keyword.</li>
</ul>

<h2 id="variations">Handle the variations</h2>
<p>Add the forms you actually see: <em>price</em>, <em>pricing</em>, <em>cost</em>, <em>how much</em>, <em>kitna</em>. Emoji-only comments are best handled with a catch-all rather than trying to enumerate them.</p>

<h2 id="catchall">Use a catch-all carefully</h2>
<p>A catch-all replies to every comment that didn't match anything else. It's useful on launch posts and dangerous everywhere else — nothing is more obviously automated than a generic reply to “love this”. If you enable one, keep the message short and human, and review the log weekly.</p>

<h2 id="nomatch">When nothing matches</h2>
<p>The comment stays in your normal inbox, unanswered by the automation. That's intentional: guessing produces worse outcomes than silence. If the log shows the same unmatched comment repeatedly, that phrase belongs in your keyword list.</p>

<h2 id="public">Public replies</h2>
<p>Optionally, Viraloop can also post a short public reply under the comment (“sent to your DMs”). It's off by default because it changes the feel of your comment section — turn it on for launches, off for evergreen posts.</p>
"""),
    dict(slug="message-limits", title="Message limits and follow-ups",
         h1="Message limits, follow-ups and Instagram's messaging window",
         desc="How many automated DMs you can send, how timed follow-ups stay inside the rules, and what happens when you hit a limit.",
         tag="Automation", mins=4,
         body="""
<p>Automation on Instagram works inside a conversation that's already underway. That shapes everything about limits and timing.</p>

<h2 id="window">The messaging window</h2>
<p>Instagram's messaging API is built around a recent interaction. Automated messages are expected to follow promptly from the user's last comment or message. Viraloop schedules follow-ups inside that window and refuses to send outside it — even if you configure a longer delay.</p>

<h2 id="followups">Follow-up policy</h2>
<ul>
  <li><strong>One follow-up per conversation</strong>, by default.</li>
  <li>The sequence <strong>stops immediately</strong> if the person replies.</li>
  <li>Follow-ups never send to someone who already completed your target action.</li>
</ul>

<h2 id="quotas">Plan quotas</h2>
<p>Automated DMs are counted per send against your monthly plan allowance: 1,000 on Free, 10,000 on Creator, 50,000 on Agency. Manual replies you type yourself are never counted.</p>
<p>At 80% of your allowance we email you. At 100%, automations pause — they don't silently drop messages. Nothing is lost; the queue resumes when the month resets or you upgrade.</p>

<h2 id="limits">Rate limits</h2>
<p>Instagram applies its own per-account rate limits on top of our quotas. If you post something that goes very wide, some replies may be queued rather than sent instantly. The log shows queue time for every message.</p>
"""),
    dict(slug="billing", title="Access, cost and limits",
         h1="Access, cost and limits",
         desc="Viraloop is free and runs on your own server for one Instagram account. What that means for hosting, tokens, limits and getting your data out.",
         tag="Account", mins=3,
         body="""
<h2 id="cost">What it costs</h2>
<p>Nothing. There is no subscription, no per-message charge and no paid tier. Viraloop is a single-account tool you run yourself, so there is no bill for us to send you.</p>
<p>The one optional cost is hosting, and on Cloudflare's free Workers plan that is ₹0 with no card. Replies land within a minute, because a cron trigger runs the polling pass every minute.</p>

<h2 id="account">One account per deployment</h2>
<p>Each deployment connects to one Instagram account. That keeps the token, the stored data and the blast radius small. A second account means a second deployment — which on a free host is a second free service.</p>

<h2 id="token">The access token</h2>
<ul>
  <li>Long-lived Instagram tokens last about 60 days.</li>
  <li>Refresh from the dashboard: <strong>Account → Refresh token</strong>.</li>
  <li>Revoke any time from Instagram's <strong>Apps and websites</strong> settings.</li>
  <li>The token is stored on your server only, in a file you control.</li>
</ul>

<h2 id="limits">Limits</h2>
<p>There is an hourly safety cap (default 200 replies) that exists to stop a runaway loop, not to meter you. Raise or lower it in Settings. Instagram applies its own per-account rate limits on top, which is why very high-volume posts can queue.</p>

<h2 id="data">Getting your data out</h2>
<p>Everything lives in JSON files under <code>data/</code> on your server: rules, settings, activity and the account. Copy them, edit them or delete them. Deleting the folder is a complete wipe.</p>

<h2 id="help">Something broken?</h2>
<p>Email <a href="mailto:hello@viraloop.co">hello@viraloop.co</a>, or check <a href="troubleshooting.html">troubleshooting</a> first — it covers the five usual causes.</p>
"""),
    dict(slug="troubleshooting", title="Nothing is sending",
         h1="Nothing is sending — a checklist",
         desc="Work through the five most common reasons an automation doesn't fire, in the order that resolves them fastest.",
         tag="Support", mins=4,
         body="""
<p>Work through these in order. In our experience the first two resolve most cases.</p>

<h2 id="one">1. Is the automation live?</h2>
<p>Draft automations don't send. Check the status pill on the automation — it should read <strong>Live</strong>, not <strong>Paused</strong> or <strong>Draft</strong>.</p>

<h2 id="two">2. Do the keywords match the comment?</h2>
<p>Open the log and look at recent comments. Matching is substring-based, so <code>price</code> matches “price list” but not “cost”. If the log shows comments with no trigger, add those phrases.</p>

<h2 id="three">3. Is the post the right one?</h2>
<p>Triggers are attached to specific posts and reels. A common mistake is building an automation for a reel, then testing on a carousel.</p>

<h2 id="four">4. Has the account connection expired?</h2>
<p>Meta connections can lapse if permissions are revoked or a password changes. Settings → Accounts shows a warning when this happens; reconnecting takes a minute.</p>

<h2 id="five">5. Have you hit a limit?</h2>
<p>Check usage against your plan allowance. If you're at 100%, automations pause and the queue waits rather than dropping messages. See <a href="message-limits.html">message limits</a>.</p>

<h2 id="still">Still stuck?</h2>
<p>Email <a href="mailto:hello@viraloop.co">hello@viraloop.co</a> with your account email, the automation name and the time of a comment that should have triggered. Include the comment text if you have it — that's usually enough for us to find the cause in the log.</p>
"""),
]

HELP_INDEX = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:42rem">
    <span class="eyebrow">Help centre</span>
    <h1>Short answers to the questions that come up most.</h1>
    <p class="lede">Six guides covering setup, matching, limits, billing and the usual breakages. If yours isn't here, email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap grid grid-2">
""" + "".join(f"""
    <article class="card post-card">
      <p class="meta">{a['tag']} · {a['mins']} min read</p>
      <h3><a href="{a['slug']}.html">{a['title']}</a></h3>
      <p>{a['desc']}</p>
      <a class="more" href="{a['slug']}.html">Open guide →</a>
    </article>""" for a in HELP) + f"""
  </div>
</section>

<section class="section section--tan">
  <div class="wrap grid grid-2" style="align-items:center;gap:clamp(1.5rem,4vw,3rem)">
    <div class="stack">
      <h2>Can't find it?</h2>
      <p>Email us with your account address and what you were trying to do. We answer within one working day, and we're happy to look at a screenshot of the automation.</p>
      <div class="btn-row"><a class="btn" href="../contact.html">Contact support</a></div>
    </div>
    <div class="card">
      <h3>Faster answers</h3>
      <ul class="list-check mt-m">
        <li>{icon('check')}<span><a href="troubleshooting.html">Nothing is sending</a> — the five-point checklist</span></li>
        <li>{icon('check')}<span><a href="connect-instagram.html">Connection errors</a> — the usual fixes</span></li>
        <li>{icon('check')}<span><a href="billing.html">Access and cost</a> — hosting, tokens, limits</span></li>
      </ul>
    </div>
  </div>
</section>
"""


def help_page(a):
    depth = 1
    path = f"help/{a['slug']}.html"
    crumbs = [("Home", "index.html"), ("Help", "help/index.html"), (a["title"], None)]
    heads = []
    import re
    for hid, label in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', a["body"]):
        heads.append(f'<li><a href="#{hid}">{re.sub(r"<[^>]+>", "", label)}</a></li>')
    aside = ("<ul>" + "".join(heads) + "</ul>") if heads else ""
    body = f"""
<article>
  <header class="article-head">
    <div class="wrap stack" style="max-width:44rem">
      {breadcrumbs(crumbs, depth)}
      <span class="eyebrow">{a['tag']}</span>
      <h1 style="font-size:clamp(1.9rem,4.2vw,3rem)">{a['h1']}</h1>
      <p class="muted" style="font-size:.85rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase">{a['mins']} min read · Updated {UPDATED}</p>
    </div>
  </header>
  <div class="section">
    <div class="wrap grid grid-2" style="align-items:start;gap:clamp(1.5rem,4vw,3rem)">
      <div class="prose">{a['body']}</div>
      <aside class="stack">
        <div class="card card--tan"><h3 style="font-size:1rem">On this page</h3><ul class="list-check mt-m" style="font-size:.9rem">{aside}</ul></div>
        <div class="card"><h3 style="font-size:1rem">Need a hand?</h3><p class="mt-m" style="font-size:.9rem">Email <a href="mailto:{EMAIL}">{EMAIL}</a> — one working day, usually less.</p></div>
      </aside>
    </div>
  </div>
</article>
"""
    ld = [breadcrumb_ld(crumbs, path, depth), {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": a["h1"], "description": a["desc"],
        "author": {"@type": "Organization", "name": "Viraloop"},
        "publisher": {"@type": "Organization", "name": "Viraloop"},
        "dateModified": "2026-10-29", "mainEntityOfPage": SITE + "/" + path,
    }]
    page(path, f"{a['title']} | Viraloop help", a["desc"], body, active="help", depth=depth, jsonld=ld)




# ---------------------------------------------------------------- CONNECT PAGE

def connect_cta():
    """The button when the app is deployed, setup steps when it isn't."""
    if APP_URL:
        return f"""
      <div class="card" style="border-width:4px">
        <span class="pill">Ready</span>
        <h3 style="margin-top:.8rem">Start the authorisation</h3>
        <p class="mt-m">You'll be taken to Instagram, asked to approve three permissions, then brought straight back here with your account connected.</p>
        <div class="btn-row mt-m">
          <a class="btn" href="{APP_URL.rstrip('/')}/auth/instagram" rel="noopener">Connect Instagram</a>
          <a class="btn btn--ghost" href="{APP_URL.rstrip('/')}/" rel="noopener">Open the dashboard</a>
        </div>
        <p class="small muted" style="margin-top:.9rem">Takes about thirty seconds. No password is shared with Viraloop at any point.</p>
      </div>"""
    return f"""
      <div class="card card--tan" style="border-width:4px">
        <span class="pill">Setup needed</span>
        <h3 style="margin-top:.8rem">This site isn't linked to a running app yet</h3>
        <p class="mt-m">The Connect button needs a deployed instance of the app to receive Instagram's callback. Two minutes of setup, then this page becomes a one-click connect.</p>
        <ol class="list-check mt-m">
          <li>{icon('check')}<span><strong>Deploy the app</strong> — Cloudflare Workers free plan (four commands), or <code>npm start</code> locally.</span></li>
          <li>{icon('check')}<span><strong>Add your Meta app ID and secret</strong> to that server's environment.</span></li>
          <li>{icon('check')}<span><strong>Register the redirect URI</strong> <code>https://your-app/auth/callback</code> in the Meta dashboard.</span></li>
          <li>{icon('check')}<span><strong>Set <code>APP_URL</code></strong> in the site generator so this button points at your app.</span></li>
        </ol>
        <div class="btn-row mt-m">
          <a class="btn" href="{DEPLOY_URL}" rel="noopener">Deploy it free</a>
          <a class="btn btn--ghost" href="help/connect-instagram.html">Read the setup guide</a>
        </div>
      </div>"""


CONNECT_PAGE = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:44rem">
    <span class="eyebrow">Connect</span>
    <h1>Connect your Instagram.</h1>
    <p class="lede">One button, the standard Instagram permission screen, thirty seconds. Your password never touches Viraloop — you approve specific permissions and can revoke them from Instagram at any time.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap grid grid-2" style="align-items:start;gap:clamp(1.5rem,4vw,3rem)">
    {connect_cta()}
    <div class="card">
      <h3>What the flow looks like</h3>
      <div class="step" style="margin-top:1rem">
        <div class="step__num">1</div>
        <div><h3 style="font-size:1rem">You press Connect</h3>
        <p class="small">You're sent to <code>instagram.com/oauth/authorize</code> with our app ID and the three scopes we need.</p></div>
      </div>
      <div class="step" style="margin-top:1rem">
        <div class="step__num">2</div>
        <div><h3 style="font-size:1rem">You approve</h3>
        <p class="small">Instagram shows its own permission screen — the same one every Meta app uses. You can decline any scope.</p></div>
      </div>
      <div class="step" style="margin-top:1rem">
        <div class="step__num">3</div>
        <div><h3 style="font-size:1rem">You land back connected</h3>
        <p class="small">We exchange the one-time code for a long-lived token, store it on your server, and start polling for comments and messages.</p></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tan">
  <div class="wrap">
    <div class="stack" style="max-width:44rem">
      <span class="eyebrow">Permissions</span>
      <h2>Exactly three, and why.</h2>
      <p class="muted">These are the only scopes Viraloop requests. Nothing about your password, your followers list or your other accounts.</p>
    </div>
    <div class="table-wrap mt-l">
      <table>
        <caption class="sr-only">Permissions Viraloop requests and what each is used for</caption>
        <thead><tr><th scope="col">Scope</th><th scope="col">What it allows</th><th scope="col">Why Viraloop needs it</th></tr></thead>
        <tbody>
          <tr><td><code>instagram_business_basic</code></td><td>Your profile: username, account type, media list</td><td>To show which account is connected and to find your posts and reels</td></tr>
          <tr><td><code>instagram_business_manage_messages</code></td><td>Read and send direct messages</td><td>To send the reply when someone comments or messages you</td></tr>
          <tr><td><code>instagram_business_manage_comments</code></td><td>Read comments on your media</td><td>To spot the comments that match your keywords</td></tr>
        </tbody>
      </table>
    </div>
    <p class="small muted mt-m">Revoke everything in two clicks: Instagram → Settings → Apps and websites → Viraloop → Remove. Automations stop immediately.</p>
  </div>
</section>

<section class="section">
  <div class="wrap grid grid-2" style="align-items:start;gap:clamp(1.5rem,4vw,3rem)">
    <div class="stack">
      <span class="eyebrow">Before you start</span>
      <h2>Two things Instagram requires.</h2>
      <ul class="list-check mt-m">
        <li>{icon('check')}<span><strong>A Creator or Business account.</strong> Personal accounts can't use the messaging API. Switching is free and reversible in Instagram settings.</span></li>
        <li>{icon('check')}<span><strong>A Meta app with the Instagram product added.</strong> Your own app is enough — you don't need app review for your own account.</span></li>
      </ul>
      <p class="small muted">If you'd rather not go through OAuth at all, the dashboard also accepts a long-lived access token pasted directly. Same result, fewer screens.</p>
    </div>
    <div class="card card--ink">
      <h3>No password, ever</h3>
      <p class="mt-m" style="opacity:.9">Viraloop never sees your Instagram password. It receives a token issued by Meta, scoped to the permissions above, stored only on the server you deployed. Delete the server and the token is gone.</p>
      <p class="mt-m" style="opacity:.9">This is the same authorisation model every legitimate Instagram tool uses — and the opposite of tools that ask for your login.</p>
    </div>
  </div>
</section>

{faq_block([
  ("The permission screen says the app is in development mode.",
   "That's expected for your own Meta app. Add your Instagram account as a tester under App roles, then connect — no app review is needed to use it yourself."),
  ("I get “Invalid redirect URI” after approving.",
   "The URL in Meta's Valid OAuth Redirect URIs must match the server's <code>PUBLIC_URL</code> exactly, including https and the <code>/auth/callback</code> path. Meta rejects http URLs for anything other than localhost."),
  ("It says “Insufficient permissions” when reading comments.",
   "The token was issued without <code>instagram_business_manage_comments</code>. Disconnect, then reconnect and approve every scope on the screen."),
  ("Can I connect more than one account?",
   "One account per deployment. Connect a different account and the previous token is replaced."),
  ("How do I disconnect?",
   "Dashboard → Account → Disconnect. That deletes the stored token. To revoke at Meta's side too, remove the app from Instagram's Apps and websites settings."),
], heading="When the button misbehaves.")}

{cta_band(heading="Thirty seconds from here to a working automation.",
         sub="Free forever, one account, no card.",
         label="Get it free", href="pricing.html#start")}
"""


# ---------------------------------------------------------------- LEGAL

TERMS = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:44rem">
    <span class="eyebrow">Legal</span>
    <h1>Terms of service</h1>
    <p class="muted">Last updated {UPDATED}. Plain-language summary first, then the detail.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="prose">
      <div class="callout"><p><strong>In short:</strong> Viraloop helps you reply to people who contacted you first. Don't use it for spam, don't use it to gate rewards behind a follow, and don't expect it to work if Instagram changes its API. It is free and runs on your own server, so there is nothing to cancel.</p></div>

      <h2 id="who">1. Who we are</h2>
      <p>Viraloop (“we”, “us”) is operated by <strong>[Your Legal Entity]</strong>, registered at [Registered Address], [City, State, PIN], India. By creating an account or using the service you agree to these terms. If you're agreeing on behalf of a company, you confirm you're allowed to.</p>

      <h2 id="service">2. The service</h2>
      <p>Viraloop is software that automates replies to Instagram comments, story replies and direct messages using Meta's official Instagram messaging API. The service depends on Instagram's platform, its permissions and its rate limits. We don't control those, and we can't guarantee the platform will keep working the way it does today.</p>

      <h2 id="eligibility">3. Eligibility and accounts</h2>
      <ul>
        <li>You must be at least 18, or the age of majority where you live.</li>
        <li>You must own or be authorised to manage the Instagram account you connect.</li>
        <li>You're responsible for keeping your login credentials secure and for activity under your account.</li>
        <li>One person or organisation per account. Don't share seats outside your plan.</li>
      </ul>

      <h2 id="acceptable">4. Acceptable use</h2>
      <p>You agree not to use Viraloop to:</p>
      <ul>
        <li>send unsolicited messages to people who haven't contacted you;</li>
        <li>require a follow, like or share as a condition of receiving content, a link or a reward;</li>
        <li>impersonate anyone, or misrepresent an automated message as a personal one where the law requires disclosure;</li>
        <li>promote illegal goods or services, or content that violates Meta's terms;</li>
        <li>scrape, resell or reverse-engineer the service, or attempt to bypass its limits;</li>
        <li>send anything that could reasonably be considered harassment, hate speech or fraud.</li>
      </ul>
      <p>We may suspend an account that breaches these rules. Where the breach is serious or repeated, suspension is immediate.</p>

      <h2 id="your-content">5. Your content and data</h2>
      <p>You keep ownership of your messages, automations and audience data. You grant us the limited licence needed to store and process it so the service can run. We don't sell your data and we don't use your message content to train models. See the <a href="privacy.html">privacy policy</a> for the detail.</p>

      <h2 id="billing">6. Cost</h2>
      <p>The software is provided free of charge. There is no subscription, no per-message fee and no paid tier. You run it on infrastructure you control, and any hosting or platform charges are between you and that provider.</p>

      <h2 id="refunds">7. No payment terms</h2>
      <p>Because nothing is charged, there is no billing cycle, no refund process and no payment data held. If that ever changes, it will require a new agreement with you — this page would be updated first.</p>

      <h2 id="availability">8. Availability</h2>
      <p>The software is provided as-is with no service-level guarantee. You control the host, so uptime is between you and your hosting provider.</p>

      <h2 id="termination">9. Suspension and termination</h2>
      <p>You can close your account at any time from settings. We can suspend or terminate an account that breaches these terms, that creates legal risk, or that is used in a way that endangers other users or the platform. On termination, your right to use the service ends and your data is deleted within 30 days, except where we must retain records by law.</p>

      <h2 id="liability">10. Liability</h2>
      <p>The service is provided “as is”. To the extent the law allows, we exclude implied warranties and our total liability for any claim is limited to the greater of the amount you paid us in the three months before the claim, or ₹1,000. We're not liable for lost profits, lost audience, account restrictions imposed by Meta, or indirect losses. Nothing in these terms limits liability that cannot be limited by law, including for fraud.</p>

      <h2 id="changes">11. Changes</h2>
      <p>We may update these terms. Material changes are notified by email at least 14 days before they take effect. Continuing to use the service after that date means you accept the new terms.</p>

      <h2 id="law">12. Governing law</h2>
      <p>These terms are governed by the laws of India. The courts at [City], India have exclusive jurisdiction. Before filing anything, write to us — most disputes are misunderstandings.</p>

      <h2 id="contact">13. Contact</h2>
      <p><strong>[Your Legal Entity]</strong>, [Registered Address], [City, State, PIN], India.<br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
  </div>
</section>
"""

PRIVACY = f"""
<section class="hero">
  <div class="wrap stack" style="max-width:44rem">
    <span class="eyebrow">Legal</span>
    <h1>Privacy policy</h1>
    <p class="muted">Last updated {UPDATED}. Written to describe what this product actually does — not a template.</p>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="prose">
      <div class="callout"><p><strong>In short:</strong> this website sets no cookies and loads no analytics or advertising scripts. The product stores the account details, automation settings and message logs needed to reply on your behalf, and nothing else. We don't sell data and we don't train models on your messages.</p></div>

      <h2 id="site">1. This website</h2>
      <p>These marketing pages are static files. They don't set cookies, don't use analytics, and don't include third-party scripts, pixels or fonts served from another domain. Forms on this site open your own email client with the message pre-filled — the contents never pass through our servers.</p>
      <p>The site is served by GitHub Pages, which may log standard request information (IP address, user agent, timestamp) for security and operational purposes. That logging is outside our control; see GitHub's privacy statement for details.</p>

      <h2 id="product">2. What the product collects</h2>
      <p>When you create a workspace and connect Instagram, we process:</p>
      <ul>
        <li><strong>Account data</strong> — name, email address, workspace name.</li>
        <li><strong>Instagram account data</strong> — the professional account ID, username and the access token issued by Meta.</li>
        <li><strong>Automation configuration</strong> — the posts, keywords and message templates you create.</li>
        <li><strong>Message data</strong> — the comments, story replies and DMs your automations act on, plus the automated messages sent, with timestamps and delivery status.</li>
        <li><strong>Billing data</strong> — handled by our payment processor. We never see or store card numbers.</li>
      </ul>
      <p>We don't collect data about your followers beyond the messages needed to reply to them.</p>

      <h2 id="why">3. Why we process it</h2>
      <ul>
        <li>To run the automations you configured (performance of our contract with you).</li>
        <li>To provide support and answer your emails (legitimate interest).</li>
        <li>To keep the service secure, prevent abuse and debug failures (legitimate interest).</li>
        <li>To meet tax and accounting obligations (legal obligation).</li>
      </ul>

      <h2 id="processors">4. Who we share it with</h2>
      <p>We use a small number of processors, each bound by a data-processing agreement:</p>
      <ul>
        <li><strong>Meta Platforms</strong> — the Instagram messaging API, which is how messages are sent and received.</li>
        <li><strong>Our cloud hosting and database provider</strong> — application hosting and encrypted storage.</li>
        <li><strong>Our email provider</strong> — transactional email such as invites, receipts and security notices.</li>
        <li><strong>Our payment processor</strong> — subscription billing, once paid plans begin.</li>
      </ul>
      <p>We don't sell personal data, and we don't share it for advertising.</p>

      <h2 id="retention">5. How long we keep it</h2>
      <ul>
        <li>Message logs: 30 days on Free, 12 months on paid plans, then deleted.</li>
        <li>Account and automation data: while your account is active.</li>
        <li>After you close your account: deleted within 30 days, except invoice records we must keep for tax purposes.</li>
      </ul>

      <h2 id="rights">6. Your rights</h2>
      <p>Under India's Digital Personal Data Protection Act, 2023 — and for EU/UK visitors, under GDPR — you can ask to access, correct, export or delete your data, withdraw consent, or object to processing. Email <a href="mailto:{EMAIL}">{EMAIL}</a> and we'll respond within 30 days. You can also complain to the Data Protection Board of India, or your local supervisory authority in the EU/UK.</p>

      <h2 id="security">7. Security</h2>
      <p>Data is encrypted in transit and at rest. Access tokens are stored encrypted and scoped to messaging permissions only. Access to production data is limited to the engineers who need it, and is logged. If a breach affects your data, we'll notify you and the relevant authority as required by law.</p>

      <h2 id="children">8. Children</h2>
      <p>The service isn't intended for anyone under 18, and we don't knowingly process data of children.</p>

      <h2 id="changes">9. Changes</h2>
      <p>If this policy changes materially, we'll email account holders at least 14 days before the change takes effect and update the date at the top of this page.</p>

      <h2 id="contact">10. Contact</h2>
      <p>Data controller: <strong>[Your Legal Entity]</strong>, [Registered Address], [City, State, PIN], India.<br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
  </div>
</section>
"""

NOT_FOUND = f"""
<section class="section">
  <div class="wrap err">
    <p class="eyebrow">Error 404</p>
    <p class="err__code">404</p>
    <h1 style="font-size:clamp(1.6rem,3.4vw,2.4rem)">This DM never arrived.</h1>
    <p class="lede" style="max-width:34rem">The page you're after doesn't exist — or it moved. Nothing broke on your end.</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="{BASE_PATH}/">Back to home</a>
      <a class="btn btn--ghost" href="{BASE_PATH}/help/index.html">Help centre</a>
    </div>
  </div>
</section>
"""


def build():
    page("help/index.html",
         "Help centre — setup, triggers, limits and billing | Viraloop",
         "Guides for setting up Viraloop: connecting Instagram, writing comment triggers, message limits and follow-ups, billing and troubleshooting.",
         HELP_INDEX, active="help", depth=1,
         jsonld=[breadcrumb_ld([("Home", "index.html"), ("Help", None)], "help/index.html", 1)])
    for a in HELP:
        help_page(a)
    page("connect.html",
         "Connect your Instagram | Viraloop",
         "Connect your Instagram account to Viraloop in one click. The exact permissions requested, what each is used for, and how to revoke access at any time.",
         CONNECT_PAGE, active="connect")
    page("terms.html", "Terms of service | Viraloop",
         "Viraloop's terms of service: acceptable use, plans and payment, data ownership, liability and governing law (India).",
         TERMS, active="")
    page("privacy.html", "Privacy policy | Viraloop",
         "What Viraloop collects, why, who processes it, how long it's kept and how to exercise your rights under India's DPDP Act and GDPR.",
         PRIVACY, active="")
    page("404.html", "Page not found | Viraloop",
         "That page doesn't exist. Head back to the Viraloop home page or browse the help centre.",
         NOT_FOUND, active="", noindex=True)
