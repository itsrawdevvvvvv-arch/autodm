'use strict';
require('dotenv').config();
const express = require('express');
const path = require('path');
const data = require('./data');
const meta = require('./meta');
const { verifySignature, parseEvents } = require('./webhook');
const { handleMessage, handleComment } = require('./automation');
const poller = require('./poller');

const app = express();
const PORT = process.env.PORT || 3000;

// Allow the web app to be hosted separately from the server (e.g. GitHub Pages).
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.use(express.json({ verify: (req, _res, buf) => { req.rawBody = buf; } }));
app.use(express.static(path.join(__dirname, '..', 'public')));

/* ================= API ================= */

app.get('/api/status', (_req, res) => {
  const acc = data.account.get();
  const s = data.settings.get();
  res.json({
    connected: !!acc.connected && !!acc.token,
    handle: acc.handle || '',
    metaConfigured: meta.configured(),
    tokenSet: !!acc.token,
    receiveMode: s.receiveMode || 'poll',
    poller: poller.status(),
  });
});

app.get('/api/rules', (_req, res) => res.json(data.rules.all()));

app.post('/api/rules', (req, res) => {
  const rules = data.rules.all();
  const rule = Object.assign({ id: 'r' + Date.now().toString(36), enabled: true }, req.body);
  rules.push(rule); data.rules.set(rules); res.json(rule);
});

app.put('/api/rules/:id', (req, res) => {
  const rules = data.rules.all();
  const i = rules.findIndex(r => r.id === req.params.id);
  if (i < 0) return res.status(404).json({ error: 'not found' });
  rules[i] = Object.assign(rules[i], req.body, { id: req.params.id });
  data.rules.set(rules); res.json(rules[i]);
});

app.delete('/api/rules/:id', (req, res) => {
  data.rules.set(data.rules.all().filter(r => r.id !== req.params.id));
  res.status(204).end();
});

app.get('/api/activity', (_req, res) => res.json(data.activity.all()));
app.post('/api/activity/clear', (_req, res) => { data.activity.clear(); res.status(204).end(); });

app.get('/api/settings', (_req, res) => {
  const s = data.settings.get();
  res.json({
    maxSends: s.maxSends, windowHours: s.windowHours, disclose: s.disclose,
    receiveMode: s.receiveMode || 'poll', pollSeconds: s.pollSeconds || 30,
    sendsThisHour: data.activity.all().filter(a => a.type === 'message').length % (s.maxSends + 1),
  });
});
app.post('/api/settings', (req, res) => {
  const s = data.settings.set({
    maxSends: Math.max(1, parseInt(req.body.maxSends, 10) || 200),
    windowHours: Math.min(24, Math.max(1, parseInt(req.body.windowHours, 10) || 24)),
    disclose: !!req.body.disclose,
    receiveMode: req.body.receiveMode === 'webhook' ? 'webhook' : 'poll',
    pollSeconds: Math.max(10, parseInt(req.body.pollSeconds, 10) || 30),
  });
  // apply receive-mode change immediately
  if (s.receiveMode === 'poll') poller.start(s.pollSeconds); else poller.stop();
  res.json(s);
});

/* Manual token (no redirect): paste a token generated in the Meta dashboard. */
app.post('/api/token', async (req, res) => {
  const token = (req.body.token || '').trim();
  if (!token) return res.status(400).json({ error: 'empty token' });
  try {
    const me = await meta.getAccount(token);
    const acc = data.account.set({ connected: true, token, igId: me.id || '', handle: me.username || me.name || '' });
    data.activity.add({ id: 'a' + Date.now(), type: 'system', title: 'Account connected', detail: 'Access token saved', ts: Date.now() });
    res.json({ ok: true, handle: acc.handle });
  } catch (e) {
    data.account.set({ connected: true, token, igId: '', handle: '' });
    res.json({ ok: true, handle: '', warning: e.message });
  }
});

/* Refresh the long-lived token (personal mode — no app secret needed). */
app.post('/api/refresh-token', async (_req, res) => {
  const acc = data.account.get();
  if (!acc.token) return res.status(400).json({ error: 'no token' });
  try {
    const r = await meta.refreshToken(acc.token);
    data.account.set({ token: r.access_token, expiresIn: r.expires_in });
    data.activity.add({ id: 'a' + Date.now(), type: 'system', title: 'Token refreshed', detail: `valid ~${Math.round((r.expires_in || 0) / 86400)} days`, ts: Date.now() });
    res.json({ ok: true, expiresIn: r.expires_in });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

/* Polling engine control (personal mode — no public webhook URL needed). */
app.get('/api/poller', (_req, res) => res.json(poller.status()));
app.post('/api/poller/start', (req, res) => { poller.start((req.body && req.body.seconds) || data.settings.get().pollSeconds); res.json(poller.status()); });
app.post('/api/poller/stop', (_req, res) => { poller.stop(); res.json(poller.status()); });

/* ================= OAuth ================= */

app.get('/auth/instagram', (_req, res) => {
  if (!meta.configured()) {
    return res.status(400).send(page('Meta app not configured',
      'Add META_APP_ID and META_APP_SECRET to your .env file, then restart the server. See the README for the full setup.'));
  }
  res.redirect(meta.authorizeUrl('autodm'));
});

app.get('/auth/callback', async (req, res) => {
  const { code, error, error_description } = req.query;
  if (error) return res.status(400).send(page('Authorization failed', String(error_description || error)));
  if (!code) return res.status(400).send(page('Missing code', 'No authorization code returned.'));
  try {
    const token = await meta.exchangeCode(code);
    const me = await meta.getAccount(token);
    data.account.set({ connected: true, token, igId: me.id || me.user_id || '', handle: me.username || me.name || '' });
    data.activity.add({ id: 'a' + Date.now(), type: 'system', title: 'Account connected', detail: 'Authorised via Meta login', ts: Date.now() });
    res.redirect('/?connected=1');
  } catch (e) {
    res.status(500).send(page('Could not complete connection', e.message));
  }
});

/* ================= Webhook ================= */

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

function page(title, msg) {
  return `<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
  <body style="font-family:system-ui;max-width:420px;margin:60px auto;padding:0 20px;color:#000">
  <h2 style="margin:0 0 8px">${title}</h2><p style="color:#555;line-height:1.5">${msg}</p>
  <p><a href="/" style="color:#000">← Back to AutoDM</a></p></body>`;
}

app.listen(PORT, () => {
  console.log(`\n  AutoDM running at http://localhost:${PORT}`);
  console.log(`  Login route : ${meta.ROUTE}`);
  console.log(`  Meta app    : ${meta.configured() ? 'configured' : 'NOT configured (add META_APP_ID / META_APP_SECRET)'}`);
  console.log(`  Public URL  : ${meta.PUBLIC_URL}`);
  const s = data.settings.get();
  if ((s.receiveMode || 'poll') === 'poll') { poller.start(s.pollSeconds); console.log('  Receive mode: polling (no webhook needed)'); }
  else console.log('  Receive mode: webhook');
  console.log('');
});
