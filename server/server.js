'use strict';
/**
 * Viraloop — single-account Instagram DM automation.
 *
 * One person, one Instagram account, no billing. Express + a JSON file store,
 * no database and no build step.
 */
require('dotenv').config();
const express = require('express');
const path = require('path');
const crypto = require('crypto');
const data = require('./data');
const meta = require('./meta');
const { verifySignature, parseEvents } = require('./webhook');
const { handleMessage, handleComment, previewMatch } = require('./automation');
const poller = require('./poller');

const app = express();
const PORT = process.env.PORT || 3000;
const APP_KEY = (process.env.APP_KEY || '').trim();

app.disable('x-powered-by');

// The dashboard can be hosted separately from the API (e.g. GitHub Pages).
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Api-Key');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.use(express.json({ limit: '256kb', verify: (req, _res, buf) => { req.rawBody = buf; } }));
app.use(express.static(path.join(__dirname, '..', 'public'), { extensions: ['html'] }));

/* ---------- optional access key ----------
   Set APP_KEY in the environment and every /api call must send it.
   Leave it empty for a local-only instance.                        */
app.use('/api', (req, res, next) => {
  if (!APP_KEY) return next();
  const sent = req.get('x-api-key') || req.query.key || '';
  if (sent && sent === APP_KEY) return next();
  return res.status(401).json({ error: 'unauthorised', hint: 'Set the access key in Settings.' });
});

/* ================= status ================= */

app.get('/api/status', (_req, res) => {
  const acc = data.account.get();
  const s = data.settings.get();
  res.json({
    app: 'viraloop',
    version: '1.0.0',
    connected: !!acc.connected && !!acc.token,
    handle: acc.handle || '',
    igId: acc.igId || '',
    metaConfigured: meta.configured(),
    tokenSet: !!acc.token,
    receiveMode: s.receiveMode || 'poll',
    needsKey: !!APP_KEY,
    poller: poller.status(),
  });
});

app.get('/api/account', async (_req, res) => {
  const acc = data.account.get();
  const out = { connected: !!acc.connected && !!acc.token, handle: acc.handle || '', igId: acc.igId || '' };
  if (acc.token) {
    try {
      const p = await meta.getProfile(acc.token);
      out.profile = { username: p.username, name: p.name, followers: p.followers_count, media: p.media_count, picture: p.profile_picture_url };
      if (p.username && p.username !== acc.handle) data.account.set({ handle: p.username });
      out.live = true;
    } catch (e) {
      out.live = false;
      out.warning = e.message;
    }
  }
  res.json(out);
});

/* ================= connect / disconnect ================= */

/* Paste a long-lived token from the Meta dashboard — no app secret needed. */
app.post('/api/token', async (req, res) => {
  const token = String(req.body.token || '').trim();
  if (!token) return res.status(400).json({ error: 'Paste an access token first.' });
  try {
    const me = await meta.getAccount(token);
    const acc = data.account.set({ connected: true, token, igId: me.id || me.user_id || '', handle: me.username || '' });
    data.activity.add({ id: id(), type: 'system', title: 'Account connected', detail: acc.handle ? '@' + acc.handle : 'Token saved', ts: Date.now() });
    const s = data.settings.get();
    if ((s.receiveMode || 'poll') === 'poll' && !poller.status().running) poller.start(s.pollSeconds);
    res.json({ ok: true, handle: acc.handle });
  } catch (e) {
    data.account.set({ connected: true, token, igId: '', handle: '' });
    res.status(200).json({ ok: true, handle: '', warning: e.message });
  }
});

app.post('/api/disconnect', (_req, res) => {
  data.account.set({ connected: false, token: '', igId: '', handle: '' });
  data.activity.add({ id: id(), type: 'system', title: 'Account disconnected', detail: 'Token removed from this server', ts: Date.now() });
  res.json({ ok: true });
});

app.post('/api/refresh-token', async (_req, res) => {
  const acc = data.account.get();
  if (!acc.token) return res.status(400).json({ error: 'No token stored.' });
  try {
    const r = await meta.refreshToken(acc.token);
    data.account.set({ token: r.access_token, expiresIn: r.expires_in });
    data.activity.add({ id: id(), type: 'system', title: 'Token refreshed', detail: `valid ~${Math.round((r.expires_in || 0) / 86400)} days`, ts: Date.now() });
    res.json({ ok: true, expiresIn: r.expires_in });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

/* ================= automations ================= */

app.get('/api/rules', (_req, res) => res.json(data.rules.all()));

app.post('/api/rules', (req, res) => {
  const b = req.body || {};
  if (!b.name || !b.type) return res.status(400).json({ error: 'A name and a type are required.' });
  const keywords = (Array.isArray(b.keywords) ? b.keywords : String(b.keywords || '').split(','))
    .map(k => String(k).trim().toLowerCase()).filter(Boolean);
  if (!keywords.length) return res.status(400).json({ error: 'Add at least one keyword.' });
  const rule = {
    id: 'r' + Date.now().toString(36),
    type: b.type === 'comment' ? 'comment' : 'dm',
    name: String(b.name).slice(0, 60),
    enabled: b.enabled !== false,
    keywords,
    match: b.match === 'exact' ? 'exact' : 'contains',
    reply: String(b.reply || '').slice(0, 900),
    publicReply: String(b.publicReply || '').slice(0, 300),
    dmReply: String(b.dmReply || '').slice(0, 900),
  };
  const rules = data.rules.all();
  rules.push(rule);
  data.rules.set(rules);
  res.json(rule);
});

app.put('/api/rules/:id', (req, res) => {
  const rules = data.rules.all();
  const i = rules.findIndex(r => r.id === req.params.id);
  if (i < 0) return res.status(404).json({ error: 'not found' });
  const b = req.body || {};
  const next = Object.assign({}, rules[i], {
    name: b.name !== undefined ? String(b.name).slice(0, 60) : rules[i].name,
    enabled: b.enabled !== undefined ? !!b.enabled : rules[i].enabled,
    match: b.match !== undefined ? (b.match === 'exact' ? 'exact' : 'contains') : rules[i].match,
    reply: b.reply !== undefined ? String(b.reply).slice(0, 900) : rules[i].reply,
    publicReply: b.publicReply !== undefined ? String(b.publicReply).slice(0, 300) : rules[i].publicReply,
    dmReply: b.dmReply !== undefined ? String(b.dmReply).slice(0, 900) : rules[i].dmReply,
  });
  if (b.keywords !== undefined) {
    next.keywords = (Array.isArray(b.keywords) ? b.keywords : String(b.keywords).split(','))
      .map(k => String(k).trim().toLowerCase()).filter(Boolean);
  }
  rules[i] = next;
  data.rules.set(rules);
  res.json(next);
});

app.delete('/api/rules/:id', (req, res) => {
  data.rules.set(data.rules.all().filter(r => r.id !== req.params.id));
  res.status(204).end();
});

/* Dry run — never sends anything. */
app.post('/api/rules/test', (req, res) => {
  const { type, text } = req.body || {};
  res.json(previewMatch(type === 'comment' ? 'comment' : 'dm', text || ''));
});

/* ================= activity ================= */

app.get('/api/activity', (_req, res) => res.json(data.activity.all()));
app.post('/api/activity/clear', (_req, res) => { data.activity.clear(); res.status(204).end(); });

/* ================= settings ================= */

app.get('/api/settings', (_req, res) => {
  const s = data.settings.get();
  res.json({
    maxSends: s.maxSends,
    windowHours: s.windowHours,
    disclose: s.disclose,
    receiveMode: s.receiveMode || 'poll',
    pollSeconds: s.pollSeconds || 30,
    autoReplyComments: s.autoReplyComments !== false,
  });
});

app.post('/api/settings', (req, res) => {
  const b = req.body || {};
  const s = data.settings.set({
    maxSends: Math.max(1, parseInt(b.maxSends, 10) || 200),
    windowHours: Math.min(24, Math.max(1, parseInt(b.windowHours, 10) || 24)),
    disclose: !!b.disclose,
    receiveMode: b.receiveMode === 'webhook' ? 'webhook' : 'poll',
    pollSeconds: Math.max(10, parseInt(b.pollSeconds, 10) || 30),
    autoReplyComments: b.autoReplyComments !== false,
  });
  if (s.receiveMode === 'poll') poller.start(s.pollSeconds); else poller.stop();
  res.json(s);
});

/* ================= polling engine ================= */

app.get('/api/poller', (_req, res) => res.json(poller.status()));

app.post('/api/poller/start', (req, res) => {
  poller.start((req.body && req.body.seconds) || data.settings.get().pollSeconds);
  res.json(poller.status());
});

app.post('/api/poller/stop', (_req, res) => { poller.stop(); res.json(poller.status()); });

/* Run one pass right now — the "Check now" button. */
app.post('/api/scan', async (req, res) => {
  const only = (req.body && req.body.only) || null;
  const result = await poller.tick({ only });
  res.json({ ok: true, result, status: poller.status() });
});

/* ================= OAuth ================= */

/* Short-lived CSRF state values, one per authorisation attempt. */
const oauthStates = new Map();
const STATE_TTL = 10 * 60 * 1000;

function issueState() {
  const now = Date.now();
  for (const [k, t] of oauthStates) if (now - t > STATE_TTL) oauthStates.delete(k);
  const state = crypto.randomBytes(16).toString('hex');
  oauthStates.set(state, now);
  return state;
}
function consumeState(state) {
  if (!state || !oauthStates.has(state)) return false;
  const t = oauthStates.get(state);
  oauthStates.delete(state);
  return Date.now() - t <= STATE_TTL;
}
const dashboardUrl = () => (process.env.DASHBOARD_URL || '').replace(/\/$/, '') || '';

/* What is still missing for the "Connect Instagram" button to work. */
app.get('/api/oauth-check', (_req, res) => {
  const redirect = meta.redirectUri();
  const hints = [];
  if (!process.env.META_APP_ID) hints.push('Set META_APP_ID on the server (Meta app → Settings → Basic).');
  if (!process.env.META_APP_SECRET) hints.push('Set META_APP_SECRET on the server.');
  if (!/^https:\/\//.test(redirect)) hints.push('PUBLIC_URL must be an https URL — Meta rejects http redirect URIs (localhost excepted).');
  if (process.env.META_APP_ID) {
    hints.push('Add ' + redirect + ' to Meta app → Instagram → API setup → Valid OAuth Redirect URIs.');
  }
  res.json({
    ready: !!(process.env.META_APP_ID && process.env.META_APP_SECRET) && /^https:\/\//.test(redirect),
    appIdSet: !!process.env.META_APP_ID,
    secretSet: !!process.env.META_APP_SECRET,
    redirectUri: redirect,
    loginRoute: meta.ROUTE,
    scopes: meta.ROUTE === 'facebook' ? meta.FB_SCOPES : meta.SCOPES,
    hints,
  });
});

app.get('/auth/instagram', (_req, res) => {
  if (!meta.configured()) {
    return res.status(400).send(notice('Meta app not configured',
      'Add META_APP_ID and META_APP_SECRET to the server environment, then restart. You can still connect with an access token from the dashboard.'));
  }
  res.redirect(meta.authorizeUrl(issueState()));
});

app.get('/auth/callback', async (req, res) => {
  const { code, error, error_description, state } = req.query;
  const back = (query) => res.redirect(dashboardUrl() + '/?' + query);

  if (error) return back('connect_error=' + encodeURIComponent(String(error_description || error)));
  if (!consumeState(state)) {
    return back('connect_error=' + encodeURIComponent('That link expired. Press Connect Instagram again.'));
  }
  if (!code) return back('connect_error=' + encodeURIComponent('Instagram did not return an authorisation code.'));

  try {
    const token = await meta.exchangeCode(code);
    const me = await meta.getAccount(token);
    const acc = data.account.set({
      connected: true, token,
      igId: me.id || me.user_id || '',
      handle: me.username || '',
    });
    data.activity.add({ id: id(), type: 'system', title: 'Account connected', detail: 'Authorised via Instagram login', ts: Date.now() });
    const s = data.settings.get();
    if ((s.receiveMode || 'poll') === 'poll' && !poller.status().running) poller.start(s.pollSeconds);
    return back('connected=1&handle=' + encodeURIComponent(acc.handle || ''));
  } catch (e) {
    return back('connect_error=' + encodeURIComponent(e.message));
  }
});

/* ================= webhook (optional) ================= */

app.get('/webhook', (req, res) => {
  if (req.query['hub.mode'] === 'subscribe' && req.query['hub.verify_token'] === process.env.WEBHOOK_VERIFY_TOKEN) {
    return res.status(200).send(req.query['hub.challenge']);
  }
  res.sendStatus(403);
});

app.post('/webhook', async (req, res) => {
  if (!verifySignature(req)) return res.sendStatus(401);
  res.sendStatus(200);
  for (const ev of parseEvents(req.body)) {
    try { if (ev.type === 'message') await handleMessage(ev); else if (ev.type === 'comment') await handleComment(ev); }
    catch (e) { console.error('[automation]', e.message); }
  }
});

app.get('/health', (_req, res) => res.send('ok'));

/* ================= boot ================= */

function notice(title, msg) {
  return `<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
  <body style="font-family:system-ui;max-width:440px;margin:60px auto;padding:0 20px;color:#1d120c;background:#f4ead9">
  <h2 style="margin:0 0 8px">${title}</h2><p style="color:#46281a;line-height:1.55">${msg}</p>
  <p><a href="/" style="color:#a84e2a">← Back to Viraloop</a></p></body>`;
}

const id = () => Math.random().toString(36).slice(2, 10);

app.listen(PORT, () => {
  console.log(`\n  Viraloop running at http://localhost:${PORT}`);
  console.log(`  Login route : ${meta.ROUTE}`);
  console.log(`  Meta app    : ${meta.configured() ? 'configured' : 'not configured (token mode works without it)'}`);
  console.log(`  Access key  : ${APP_KEY ? 'required' : 'not set (local use only)'}`);
  const s = data.settings.get();
  if ((s.receiveMode || 'poll') === 'poll') {
    poller.start(s.pollSeconds);
    console.log('  Receive mode: polling — messages + comments, no webhook needed');
  } else {
    console.log('  Receive mode: webhook');
  }
  console.log('');
});

module.exports = app;
