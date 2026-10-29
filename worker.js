/**
 * Viraloop on Cloudflare Workers.
 *
 * Same product as the Node server in server/, re-hosted for the free plan:
 *   - fetch handler  → dashboard assets + JSON API + OAuth
 *   - scheduled()    → polling pass, every minute via a cron trigger
 *   - D1             → rules, settings, account, activity, poller state
 *
 * No cold-start spin-down, no card, no long-running timer needed.
 */

const GRAPH = 'https://graph.instagram.com/v23.0';
const FB_GRAPH = 'https://graph.facebook.com/v21.0';
const IG_SCOPES = 'instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments';
const FB_SCOPES = 'instagram_basic,instagram_manage_messages,instagram_manage_comments,pages_manage_metadata,pages_show_list,business_management';

const DEFAULTS = {
  rules: [
    { id: 'r1', type: 'comment', name: 'Link request', enabled: true, keywords: ['link', 'send', 'send it'], match: 'contains', publicReply: 'Sent it to your DMs.', dmReply: 'Here is the link you asked for: https://example.com/link' },
    { id: 'r2', type: 'comment', name: 'Price request', enabled: true, keywords: ['price', 'pricing', 'cost', 'how much'], match: 'contains', publicReply: '', dmReply: 'Here is the price list: https://example.com/pricing' },
    { id: 'r3', type: 'dm', name: 'Greeting', enabled: true, keywords: ['hi', 'hello', 'hey'], match: 'exact', reply: 'Hey! Thanks for messaging — what can I help you with?' },
  ],
  settings: { maxSends: 200, windowHours: 24, pollSeconds: 60, receiveMode: 'poll', autoReplyComments: true },
  account: { connected: false, token: '', igId: '', handle: '' },
  poller: { lastSeen: 0, handledComments: [], handledMessages: [] },
};

/* ------------------------------------------------------------------ storage */

async function kvGet(env, key, fallback) {
  const row = await env.DB.prepare('SELECT value FROM kv WHERE key = ?').bind(key).first();
  if (!row) return fallback;
  try { return JSON.parse(row.value); } catch { return fallback; }
}

async function kvSet(env, key, value) {
  await env.DB.prepare(
    'INSERT INTO kv (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value'
  ).bind(key, JSON.stringify(value)).run();
}

const getRules = async (env) => (await kvGet(env, 'rules', null)) || DEFAULTS.rules;
const setRules = (env, rules) => kvSet(env, 'rules', rules);
const getSettings = async (env) => Object.assign({}, DEFAULTS.settings, await kvGet(env, 'settings', {}));
const setSettings = async (env, patch) => {
  const next = Object.assign(await getSettings(env), patch);
  await kvSet(env, 'settings', next);
  return next;
};
const getAccount = async (env) => Object.assign({}, DEFAULTS.account, await kvGet(env, 'account', {}));
const setAccount = async (env, patch) => {
  const next = Object.assign(await getAccount(env), patch);
  await kvSet(env, 'account', next);
  return next;
};
const getPoller = async (env) => Object.assign({}, DEFAULTS.poller, await kvGet(env, 'poller', {}));
const setPoller = (env, patch) => kvSet(env, 'poller', Object.assign({}, DEFAULTS.poller, patch));

async function addActivity(env, item) {
  await env.DB.prepare('INSERT INTO activity (ts, type, title, detail) VALUES (?, ?, ?, ?)')
    .bind(item.ts || Date.now(), item.type || 'system', item.title || '', item.detail || '').run();
  await env.DB.prepare(
    'DELETE FROM activity WHERE id NOT IN (SELECT id FROM activity ORDER BY id DESC LIMIT 300)'
  ).run();
}

async function listActivity(env) {
  const { results } = await env.DB.prepare(
    'SELECT id, ts, type, title, detail FROM activity ORDER BY id DESC LIMIT 300'
  ).all();
  return results || [];
}

async function clearActivity(env) {
  await env.DB.prepare('DELETE FROM activity').run();
}

/* ------------------------------------------------------------------- config */

function cfg(env) {
  const publicUrl = (env.PUBLIC_URL || '').replace(/\/$/, '');
  return {
    appId: env.META_APP_ID || '',
    appSecret: env.META_APP_SECRET || '',
    route: (env.LOGIN_ROUTE || 'instagram').toLowerCase(),
    publicUrl,
    redirectUri: publicUrl + '/auth/callback',
    appKey: (env.APP_KEY || '').trim(),
    configured: !!(env.META_APP_ID && env.META_APP_SECRET),
  };
}

/* --------------------------------------------------------------------- meta */

function graphBase(route) { return route === 'facebook' ? FB_GRAPH : GRAPH; }
function selfId(route, acc) { return acc.igId || (route === 'facebook' ? (acc.pageId || 'me') : 'me'); }

async function gGet(url) {
  const res = await fetch(url);
  const j = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error('Graph API: ' + JSON.stringify(j).slice(0, 300));
  return j;
}

async function gPost(path, body, route) {
  const res = await fetch(graphBase(route) + '/' + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const j = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Send API ${res.status}: ` + JSON.stringify(j).slice(0, 300));
  return j;
}

function authorizeUrl(c, state) {
  const scope = c.route === 'facebook' ? FB_SCOPES : IG_SCOPES;
  const p = new URLSearchParams({
    client_id: c.appId, redirect_uri: c.redirectUri, response_type: 'code', scope, state,
  });
  return (c.route === 'facebook'
    ? 'https://www.facebook.com/v21.0/dialog/oauth?'
    : 'https://www.instagram.com/oauth/authorize?') + p;
}

async function exchangeCode(c, code) {
  if (c.route === 'facebook') {
    const p = new URLSearchParams({
      client_id: c.appId, client_secret: c.appSecret, redirect_uri: c.redirectUri, code,
    });
    const r = await fetch(FB_GRAPH + '/oauth/access_token?' + p);
    const j = await r.json();
    if (!j.access_token) throw new Error('OAuth: ' + JSON.stringify(j).slice(0, 200));
    return j.access_token;
  }
  const form = new URLSearchParams({
    client_id: c.appId, client_secret: c.appSecret,
    grant_type: 'authorization_code', redirect_uri: c.redirectUri, code,
  });
  const res = await fetch('https://api.instagram.com/oauth/access_token', { method: 'POST', body: form });
  const short = await res.json();
  if (!short.access_token) throw new Error('OAuth: ' + JSON.stringify(short).slice(0, 200));

  // Upgrade the short-lived token to a ~60 day one.
  const p = new URLSearchParams({
    grant_type: 'ig_exchange_token', client_secret: c.appSecret, access_token: short.access_token,
  });
  const long = await (await fetch(GRAPH + '/access_token?' + p)).json();
  return long.access_token || short.access_token;
}

async function refreshToken(c, token) {
  const p = new URLSearchParams({ grant_type: 'ig_refresh_token', access_token: token });
  const j = await (await fetch(GRAPH + '/refresh_access_token?' + p)).json();
  if (!j.access_token) throw new Error('Refresh failed: ' + JSON.stringify(j).slice(0, 200));
  return j;
}

async function getAccountInfo(c, token) {
  if (c.route === 'facebook') {
    const j = await gGet(`${FB_GRAPH}/me?fields=id,name&access_token=${encodeURIComponent(token)}`);
    return { id: j.id, username: j.name || '' };
  }
  const j = await gGet(`${GRAPH}/me?fields=user_id,username&access_token=${encodeURIComponent(token)}`);
  return { id: j.user_id || j.id, username: j.username || '' };
}

async function getProfile(c, token, acc) {
  const url = `${graphBase(c.route)}/${selfId(c.route, acc)}?fields=id,username,name,followers_count,media_count,profile_picture_url&access_token=${encodeURIComponent(token)}`;
  return gGet(url);
}

async function sendDM(c, token, acc, recipient, text) {
  return gPost(`${selfId(c.route, acc)}/messages`, { recipient, message: { text }, access_token: token }, c.route);
}

async function replyToComment(c, token, commentId, text) {
  return gPost(`${commentId}/replies`, { message: text, access_token: token }, c.route);
}

async function getConversations(c, token, acc) {
  const platform = c.route === 'facebook' ? 'platform=instagram&' : '';
  const url = `${graphBase(c.route)}/${selfId(c.route, acc)}/conversations?${platform}access_token=${encodeURIComponent(token)}`;
  const j = await gGet(url);
  return j.data || [];
}

async function getConversationMessages(c, token, convId) {
  const j = await gGet(`${graphBase(c.route)}/${convId}?fields=messages&access_token=${encodeURIComponent(token)}`);
  return (j.messages && j.messages.data) || [];
}

async function getMessage(c, token, msgId) {
  return gGet(`${graphBase(c.route)}/${msgId}?fields=id,created_time,from,message&access_token=${encodeURIComponent(token)}`);
}

async function getRecentMedia(c, token, acc, limit = 10) {
  const fields = 'id,caption,permalink,timestamp,comments.limit(50){id,text,timestamp,from,username}';
  const url = `${graphBase(c.route)}/${selfId(c.route, acc)}/media?fields=${encodeURIComponent(fields)}&limit=${limit}&access_token=${encodeURIComponent(token)}`;
  const j = await gGet(url);
  return j.data || [];
}

async function getMediaComments(c, token, mediaId) {
  const url = `${graphBase(c.route)}/${mediaId}/comments?fields=id,text,timestamp,from,username&limit=50&access_token=${encodeURIComponent(token)}`;
  const j = await gGet(url);
  return j.data || [];
}

/* ---------------------------------------------------------------- matching */

function matches(text, keywords, mode) {
  const t = String(text || '').toLowerCase();
  return (keywords || []).some(k => (mode === 'exact' ? t.trim() === String(k).toLowerCase() : t.includes(String(k).toLowerCase())));
}

function previewMatch(rules, type, text) {
  const active = rules.filter(r => r.enabled && r.type === type);
  const rule = active.find(r => matches(text, r.keywords, r.match));
  if (!rule) return { matched: false, checked: active.length };
  return {
    matched: true,
    checked: active.length,
    rule: { id: rule.id, name: rule.name, keywords: rule.keywords, match: rule.match },
    outgoing: type === 'comment'
      ? { publicReply: rule.publicReply || '', dm: rule.dmReply || '' }
      : { dm: rule.reply || '' },
  };
}

/* ----------------------------------------------------------------- polling */

async function sendsLastHour(env) {
  const row = await env.DB.prepare('SELECT COUNT(*) AS n FROM activity WHERE type = ? AND ts > ?')
    .bind('message', Date.now() - 3600 * 1000).first();
  return (row && row.n) || 0;
}

async function poll(env, options = {}) {
  const c = cfg(env);
  const acc = await getAccount(env);
  if (!acc.token) return { error: 'no token' };

  const settings = await getSettings(env);
  const rules = await getRules(env);
  const result = { messages: 0, comments: 0, errors: [] };
  let sent = await sendsLastHour(env);

  let capNoted = false;
  const canSend = async () => {
    if (sent >= settings.maxSends) {
      if (!capNoted) {
        capNoted = true;
        result.errors.push('hourly cap reached');
        await addActivity(env, {
          type: 'system', title: 'Rate cap reached',
          detail: `Held replies — the ${settings.maxSends}/hour safety cap was hit`,
        });
      }
      return false;
    }
    sent++;
    return true;
  };

  /* ---- messages ---- */
  if (options.only !== 'comments') {
    try {
      const state = await getPoller(env);
      let newest = state.lastSeen || 0;
      const seenIds = new Set(state.handledMessages || []);
      const conversations = await getConversations(c, acc.token, acc);

      for (const conv of conversations) {
        const msgs = await getConversationMessages(c, acc.token, conv.id);
        for (const m of msgs) {
          const ts = Date.parse(m.created_time || 0) || 0;
          newest = Math.max(newest, ts);
          if (seenIds.has(m.id)) continue;          // already handled this message
          seenIds.add(m.id);
          const full = await getMessage(c, acc.token, m.id);
          const fromId = full.from && full.from.id;
          if (fromId && acc.igId && String(fromId) === String(acc.igId)) continue;

          const rule = rules.find(r => r.enabled && r.type === 'dm' && matches(full.message, r.keywords, r.match));
          if (!rule || !rule.reply) continue;
          if (!(await canSend())) { result.errors.push('hourly cap reached'); break; }
          try {
            await sendDM(c, acc.token, acc, { id: fromId }, rule.reply);
            await addActivity(env, { type: 'message', title: 'DM replied', detail: `matched "${rule.name}"` });
            result.messages++;
          } catch (e) {
            await addActivity(env, { type: 'system', title: 'Send failed', detail: String(e.message).slice(0, 300) });
          }
        }
      }
      await setPoller(env, Object.assign({}, state, {
        lastSeen: newest,
        handledMessages: Array.from(seenIds).slice(-400),
      }));
    } catch (e) {
      result.errors.push('messages: ' + e.message);
      await addActivity(env, { type: 'system', title: 'Message poll failed', detail: String(e.message).slice(0, 300) });
    }
  }

  /* ---- comments ---- */
  if (options.only !== 'messages' && settings.autoReplyComments !== false) {
    try {
      const state = await getPoller(env);
      const handled = new Set(state.handledComments || []);
      let fresh = 0;

      const media = await getRecentMedia(c, acc.token, acc, 10);
      for (const item of media) {
        if (fresh >= 10) break;
        const comments = await getMediaComments(c, acc.token, item.id);
        for (const cm of comments) {
          if (fresh >= 10) break;
          if (handled.has(cm.id)) continue;

          const authorId = (cm.from && cm.from.id) || null;
          if (authorId && acc.igId && String(authorId) === String(acc.igId)) { handled.add(cm.id); continue; }

          const rule = rules.find(r => r.enabled && r.type === 'comment' && matches(cm.text, r.keywords, r.match));
          handled.add(cm.id);
          if (!rule) continue;

          if (rule.publicReply && (await canSend())) {
            try { await replyToComment(c, acc.token, cm.id, rule.publicReply); }
            catch (e) { result.errors.push('public reply: ' + e.message); }
          }
          if (rule.dmReply && (await canSend())) {
            try {
              await sendDM(c, acc.token, acc, { comment_id: cm.id }, rule.dmReply);
              await addActivity(env, { type: 'comment', title: 'Comment handled', detail: `matched "${rule.name}"` });
              result.comments++;
            } catch (e) {
              await addActivity(env, { type: 'system', title: 'Private reply failed', detail: String(e.message).slice(0, 300) });
            }
          }
          fresh++;
        }
      }

      if (fresh) {
        await setPoller(env, Object.assign({}, state, { handledComments: Array.from(handled).slice(-400) }));
      }
    } catch (e) {
      result.errors.push('comments: ' + e.message);
      await addActivity(env, { type: 'system', title: 'Comment poll failed', detail: String(e.message).slice(0, 300) });
    }
  }

  await kvSet(env, 'lastRun', { at: Date.now(), result });
  return result;
}

/* -------------------------------------------------------------------- http */

const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' },
});

function escapeHtml(s) {
  return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function notice(title, msg) {
  return new Response(`<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
  <body style="font-family:system-ui;max-width:440px;margin:60px auto;padding:0 20px;color:#1d120c;background:#f4ead9">
  <h2 style="margin:0 0 8px">${escapeHtml(title)}</h2><p style="color:#46281a;line-height:1.55">${escapeHtml(msg)}</p>
  <p><a href="/" style="color:#a84e2a">← Back to Viraloop</a></p></body>`,
    { status: 400, headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

async function readJson(request) {
  try { return await request.json(); } catch { return {}; }
}

function normaliseKeywords(input) {
  const arr = Array.isArray(input) ? input : String(input || '').split(',');
  return arr.map(k => String(k).trim().toLowerCase()).filter(Boolean);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const c = cfg(env);

    /* ---- OAuth ---- */
    if (path === '/auth/instagram') {
      if (!c.configured) {
        return notice('Meta app not configured',
          'Add META_APP_ID and META_APP_SECRET to this Worker, then redeploy. You can still connect with an access token from the dashboard.');
      }
      const state = crypto.randomUUID().replace(/-/g, '');
      await kvSet(env, 'state:' + state, { at: Date.now() });
      return Response.redirect(authorizeUrl(c, state), 302);
    }

    if (path === '/auth/callback') {
      const code = url.searchParams.get('code');
      const state = url.searchParams.get('state');
      const err = url.searchParams.get('error_description') || url.searchParams.get('error');

      const back = (query) => Response.redirect((c.publicUrl || url.origin) + '/?' + query, 302);
      if (err) return back('connect_error=' + encodeURIComponent(err));

      const saved = state ? await kvGet(env, 'state:' + state, null) : null;
      if (!saved || Date.now() - saved.at > 10 * 60 * 1000) {
        return back('connect_error=' + encodeURIComponent('That link expired. Press Connect Instagram again.'));
      }
      await env.DB.prepare('DELETE FROM kv WHERE key = ?').bind('state:' + state).run();
      if (!code) return back('connect_error=' + encodeURIComponent('Instagram did not return an authorisation code.'));

      try {
        const token = await exchangeCode(c, code);
        const me = await getAccountInfo(c, token);
        const acc = await setAccount(env, { connected: true, token, igId: me.id || '', handle: me.username || '' });
        await addActivity(env, { type: 'system', title: 'Account connected', detail: 'Authorised via Instagram login' });
        return back('connected=1&handle=' + encodeURIComponent(acc.handle || ''));
      } catch (e) {
        return back('connect_error=' + encodeURIComponent(e.message));
      }
    }

    /* ---- API ---- */
    if (path.startsWith('/api/')) {
      if (c.appKey) {
        const sent = request.headers.get('x-api-key') || url.searchParams.get('key') || '';
        if (sent !== c.appKey) return json({ error: 'unauthorised', hint: 'Set the access key in Settings.' }, 401);
      }

      try {
        return await apiRoute(request, env, url, path);
      } catch (e) {
        return json({ error: String(e.message || e) }, 500);
      }
    }

    if (path === '/health') return new Response('ok');

    /* ---- static dashboard ---- */
    return env.ASSETS ? env.ASSETS.fetch(request) : new Response('Not found', { status: 404 });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(poll(env));
  },
};

async function apiRoute(request, env, url, path) {
  const method = request.method;

  if (path === '/api/status' && method === 'GET') {
    const acc = await getAccount(env);
    const settings = await getSettings(env);
    const lastRun = await kvGet(env, 'lastRun', null);
    const c = cfg(env);
    return json({
      app: 'viraloop', runtime: 'cloudflare-workers', version: '1.1.0',
      connected: !!acc.connected && !!acc.token,
      handle: acc.handle || '', igId: acc.igId || '',
      metaConfigured: c.configured,
      tokenSet: !!acc.token,
      receiveMode: settings.receiveMode || 'poll',
      needsKey: !!c.appKey,
      poller: {
        running: true,
        lastRunAt: lastRun ? lastRun.at : 0,
        messages: lastRun ? `handled ${lastRun.result.messages || 0}` : 'waiting for first cron',
        comments: lastRun ? `handled ${lastRun.result.comments || 0}` : 'waiting for first cron',
        cron: 'every minute',
      },
    });
  }

  if (path === '/api/oauth-check' && method === 'GET') {
    const c = cfg(env);
    const hints = [];
    if (!c.appId) hints.push('Set META_APP_ID on this Worker (Meta app → Settings → Basic).');
    if (!c.appSecret) hints.push('Set META_APP_SECRET on this Worker.');
    if (!/^https:\/\//.test(c.publicUrl)) hints.push('Set PUBLIC_URL to this Worker\'s https URL.');
    if (c.appId) hints.push('Add ' + c.redirectUri + ' to Meta app → Instagram → API setup → Valid OAuth Redirect URIs.');
    return json({
      ready: !!(c.appId && c.appSecret) && /^https:\/\//.test(c.publicUrl),
      appIdSet: !!c.appId, secretSet: !!c.appSecret,
      redirectUri: c.redirectUri, loginRoute: c.route,
      scopes: c.route === 'facebook' ? FB_SCOPES : IG_SCOPES,
      hints,
    });
  }

  if (path === '/api/account' && method === 'GET') {
    const c = cfg(env);
    const acc = await getAccount(env);
    const out = { connected: !!acc.connected && !!acc.token, handle: acc.handle || '', igId: acc.igId || '' };
    if (acc.token) {
      try {
        const p = await getProfile(c, acc.token, acc);
        out.profile = { username: p.username, name: p.name, followers: p.followers_count, media: p.media_count, picture: p.profile_picture_url };
        if (p.username && p.username !== acc.handle) await setAccount(env, { handle: p.username });
        out.live = true;
      } catch (e) {
        out.live = false;
        out.warning = e.message;
      }
    }
    return json(out);
  }

  if (path === '/api/token' && method === 'POST') {
    const body = await readJson(request);
    const token = String(body.token || '').trim();
    if (!token) return json({ error: 'Paste an access token first.' }, 400);
    const c = cfg(env);
    try {
      const me = await getAccountInfo(c, token);
      const acc = await setAccount(env, { connected: true, token, igId: me.id || '', handle: me.username || '' });
      await addActivity(env, { type: 'system', title: 'Account connected', detail: acc.handle ? '@' + acc.handle : 'Token saved' });
      return json({ ok: true, handle: acc.handle });
    } catch (e) {
      await setAccount(env, { connected: true, token, igId: '', handle: '' });
      return json({ ok: true, handle: '', warning: e.message });
    }
  }

  if (path === '/api/disconnect' && method === 'POST') {
    await setAccount(env, { connected: false, token: '', igId: '', handle: '' });
    await addActivity(env, { type: 'system', title: 'Account disconnected', detail: 'Token removed' });
    return json({ ok: true });
  }

  if (path === '/api/refresh-token' && method === 'POST') {
    const acc = await getAccount(env);
    if (!acc.token) return json({ error: 'No token stored.' }, 400);
    try {
      const r = await refreshToken(cfg(env), acc.token);
      await setAccount(env, { token: r.access_token, expiresIn: r.expires_in });
      await addActivity(env, { type: 'system', title: 'Token refreshed', detail: `valid ~${Math.round((r.expires_in || 0) / 86400)} days` });
      return json({ ok: true, expiresIn: r.expires_in });
    } catch (e) {
      return json({ error: e.message }, 500);
    }
  }

  if (path === '/api/rules' && method === 'GET') return json(await getRules(env));

  if (path === '/api/rules' && method === 'POST') {
    const b = await readJson(request);
    if (!b.name || !b.type) return json({ error: 'A name and a type are required.' }, 400);
    const keywords = normaliseKeywords(b.keywords);
    if (!keywords.length) return json({ error: 'Add at least one keyword.' }, 400);
    const rules = await getRules(env);
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
    rules.push(rule);
    await setRules(env, rules);
    return json(rule);
  }

  if (path.startsWith('/api/rules/') && path.endsWith('/test') && method === 'POST') {
    const b = await readJson(request);
    return json(previewMatch(await getRules(env), b.type === 'comment' ? 'comment' : 'dm', b.text || ''));
  }

  if (path.startsWith('/api/rules/') && method === 'PUT') {
    const id = path.split('/')[3];
    const rules = await getRules(env);
    const i = rules.findIndex(r => r.id === id);
    if (i < 0) return json({ error: 'not found' }, 404);
    const b = await readJson(request);
    const next = Object.assign({}, rules[i]);
    if (b.name !== undefined) next.name = String(b.name).slice(0, 60);
    if (b.enabled !== undefined) next.enabled = !!b.enabled;
    if (b.match !== undefined) next.match = b.match === 'exact' ? 'exact' : 'contains';
    if (b.reply !== undefined) next.reply = String(b.reply).slice(0, 900);
    if (b.publicReply !== undefined) next.publicReply = String(b.publicReply).slice(0, 300);
    if (b.dmReply !== undefined) next.dmReply = String(b.dmReply).slice(0, 900);
    if (b.keywords !== undefined) next.keywords = normaliseKeywords(b.keywords);
    rules[i] = next;
    await setRules(env, rules);
    return json(next);
  }

  if (path.startsWith('/api/rules/') && method === 'DELETE') {
    const id = path.split('/')[3];
    await setRules(env, (await getRules(env)).filter(r => r.id !== id));
    return new Response(null, { status: 204 });
  }

  if (path === '/api/activity' && method === 'GET') return json(await listActivity(env));
  if (path === '/api/activity/clear' && method === 'POST') {
    await clearActivity(env);
    return new Response(null, { status: 204 });
  }

  if (path === '/api/settings' && method === 'GET') return json(await getSettings(env));
  if (path === '/api/settings' && method === 'POST') {
    const b = await readJson(request);
    const next = await setSettings(env, {
      maxSends: Math.max(1, parseInt(b.maxSends, 10) || 200),
      windowHours: Math.min(24, Math.max(1, parseInt(b.windowHours, 10) || 24)),
      receiveMode: b.receiveMode === 'webhook' ? 'webhook' : 'poll',
      pollSeconds: 60,
      autoReplyComments: b.autoReplyComments !== false,
    });
    return json(next);
  }

  if (path === '/api/scan' && method === 'POST') {
    const b = await readJson(request);
    const result = await poll(env, { only: b.only || null });
    return json({ ok: true, result });
  }

  if (path === '/api/poller' && method === 'GET') {
    const lastRun = await kvGet(env, 'lastRun', null);
    return json({ running: true, cron: 'every minute', lastRunAt: lastRun ? lastRun.at : 0 });
  }

  return json({ error: 'not found' }, 404);
}
