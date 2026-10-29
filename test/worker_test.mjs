/**
 * Exercise worker.js without wrangler: a small D1 shim over an in-memory store,
 * a static-asset shim over public/, and Node's own fetch/Request/Response.
 *
 *   node test/worker_test.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import worker from '../worker.js';

/* ---------------------------------------------------------- D1 shim ---- */

function makeDB() {
  const kv = new Map();
  let activity = [];
  let nextId = 1;

  const api = {
    prepare(sql) {
      const flat = sql.replace(/\s+/g, ' ').trim();
      let args = [];
      const stmt = {
        bind(...a) { args = a; return stmt; },
        async first() {
          if (flat.startsWith('SELECT value FROM kv')) return kv.has(args[0]) ? { value: kv.get(args[0]) } : null;
          if (flat.startsWith('SELECT COUNT(*) AS n FROM activity')) {
            return { n: activity.filter(r => r.type === args[0] && r.ts > args[1]).length };
          }
          throw new Error('unhandled first(): ' + flat);
        },
        async all() {
          if (flat.startsWith('SELECT id, ts, type, title, detail FROM activity')) {
            return { results: [...activity].sort((a, b) => b.id - a.id).slice(0, 300) };
          }
          throw new Error('unhandled all(): ' + flat);
        },
        async run() {
          if (flat.startsWith('INSERT INTO kv')) { kv.set(args[0], args[1]); return { success: true }; }
          if (flat.startsWith('DELETE FROM kv')) { kv.delete(args[0]); return { success: true }; }
          if (flat.startsWith('INSERT INTO activity')) {
            activity.push({ id: nextId++, ts: args[0], type: args[1], title: args[2], detail: args[3] });
            return { success: true };
          }
          if (flat.startsWith('DELETE FROM activity WHERE id NOT IN')) {
            activity = [...activity].sort((a, b) => b.id - a.id).slice(0, 300);
            return { success: true };
          }
          if (flat === 'DELETE FROM activity') { activity = []; return { success: true }; }
          throw new Error('unhandled run(): ' + flat);
        },
      };
      return stmt;
    },
  };
  return { api, kv, getActivity: () => activity };
}

/* ------------------------------------------------- static assets shim ---- */

const PUBLIC = path.join(process.cwd(), 'public');
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.woff2': 'font/woff2' };

const ASSETS = {
  async fetch(request) {
    const url = new URL(request.url);
    let p = url.pathname === '/' ? '/index.html' : url.pathname;
    const file = path.join(PUBLIC, p);
    if (!file.startsWith(PUBLIC) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
      return new Response('Not found', { status: 404 });
    }
    return new Response(fs.readFileSync(file), {
      headers: { 'Content-Type': MIME[path.extname(file)] || 'application/octet-stream' },
    });
  },
};

/* ------------------------------------------------- mocked Meta API ---- */

const sent = [];
const GRAPH_CALLS = [];
let extraComment = null;

globalThis.fetch = async (input, init = {}) => {
  const url = typeof input === 'string' ? input : input.url;
  const method = (init.method || 'GET').toUpperCase();
  GRAPH_CALLS.push(method + ' ' + url);
  const u = new URL(url);
  const body = init.body ? JSON.parse(init.body) : null;
  const reply = (obj) => new Response(JSON.stringify(obj), { headers: { 'Content-Type': 'application/json' } });

  // token exchange
  if (u.host === 'api.instagram.com') return reply({ access_token: 'SHORT', user_id: '17841400000' });
  if (u.pathname === '/v23.0/access_token') return reply({ access_token: 'LONG', expires_in: 5184000 });
  if (u.pathname === '/v23.0/refresh_access_token') return reply({ access_token: 'REFRESHED', expires_in: 5184000 });

  // profile / me
  if (u.pathname.endsWith('/me')) return reply({ user_id: '17841400000', username: 'viraloop_test' });
  if (u.pathname === '/v23.0/17841400000' && method === 'GET') {
    return reply({ id: '17841400000', username: 'viraloop_test', followers_count: 1234, media_count: 42 });
  }

  // send DM / private reply
  if (u.pathname.endsWith('/messages') && method === 'POST') {
    sent.push(body);
    return reply({ message_id: 'm' + sent.length });
  }
  // public reply
  if (u.pathname.endsWith('/replies') && method === 'POST') {
    sent.push({ publicReply: body.message, comment: u.pathname.split('/')[2] });
    return reply({ id: 'c_reply' });
  }

  // conversations
  if (u.pathname.endsWith('/conversations')) {
    return reply({ data: [{ id: 'conv1' }] });
  }
  if (u.pathname === '/v23.0/conv1') {
    return reply({ messages: { data: [{ id: 'msg_new', created_time: new Date().toISOString() }] } });
  }
  if (u.pathname === '/v23.0/msg_new') {
    return reply({ id: 'msg_new', from: { id: '999' }, message: 'hello' });
  }

  // media + comments
  if (u.pathname.endsWith('/media')) {
    return reply({ data: [{ id: 'media1' }] });
  }
  if (u.pathname === '/v23.0/media1/comments') {
    const data = [
      { id: 'cm1', text: 'send me the link please', from: { id: '999' } },
      { id: 'cm2', text: 'nice reel', from: { id: '999' } },
      { id: 'cm3', text: 'link', from: { id: '17841400000' } },
    ];
    if (extraComment) data.push(extraComment);
    return reply({ data });
  }

  return reply({ error: 'unmocked ' + method + ' ' + u.pathname });
};

/* ------------------------------------------------------------- harness ---- */

const db = makeDB();
const env = {
  DB: db.api,
  ASSETS,
  PUBLIC_URL: 'https://viraloop.example.workers.dev',
  META_APP_ID: '1234567890',
  META_APP_SECRET: 'secret',
  APP_KEY: 'test-key',
  LOGIN_ROUTE: 'instagram',
};

let pass = 0;
let fail = 0;

function check(name, cond, extra = '') {
  if (cond) { pass++; console.log('  ✓ ' + name); }
  else { fail++; console.log('  ✗ ' + name + (extra ? ' — ' + extra : '')); }
}

async function call(path, init = {}) {
  const req = new Request('https://viraloop.example.workers.dev' + path, init);
  return worker.fetch(req, env);
}

const auth = { 'Content-Type': 'application/json', 'X-Api-Key': 'test-key' };

console.log('\n— access key —');
check('no key is rejected', (await call('/api/status')).status === 401);
check('wrong key is rejected', (await call('/api/status', { headers: { 'X-Api-Key': 'nope' } })).status === 401);
check('right key is accepted', (await call('/api/status', { headers: auth })).status === 200);

console.log('\n— status & oauth-check —');
const status = await (await call('/api/status', { headers: auth })).json();
check('reports not connected', status.connected === false);
check('reports runtime', status.runtime === 'cloudflare-workers', status.runtime);
const oauth = await (await call('/api/oauth-check', { headers: auth })).json();
check('oauth ready with app id + secret + https', oauth.ready === true);
check('redirect uri is built from PUBLIC_URL', oauth.redirectUri === 'https://viraloop.example.workers.dev/auth/callback', oauth.redirectUri);
check('asks for the comments scope', oauth.scopes.includes('instagram_business_manage_comments'));

console.log('\n— authorize redirect —');
const authRes = await call('/auth/instagram', { redirect: 'manual' });
const loc = authRes.headers.get('location') || '';
check('302 to instagram', authRes.status === 302 && loc.startsWith('https://www.instagram.com/oauth/authorize?'), loc.slice(0, 60));
check('carries client_id', loc.includes('client_id=1234567890'));
check('carries encoded redirect_uri', loc.includes('redirect_uri=https%3A%2F%2Fviraloop.example.workers.dev%2Fauth%2Fcallback'));
check('carries a state', /state=[a-f0-9]{16,}/.test(loc));
check('carries all three scopes', loc.includes('instagram_business_basic') && loc.includes('manage_messages') && loc.includes('manage_comments'));

console.log('\n— callback guards —');
const badState = await call('/auth/callback?code=x&state=bogus', { redirect: 'manual' });
check('rejects an unknown state', (badState.headers.get('location') || '').includes('connect_error='));
const noCode = await call('/auth/callback?error=access_denied', { redirect: 'manual' });
check('surfaces a declined authorisation', (noCode.headers.get('location') || '').includes('access_denied'));

console.log('\n— rules —');
let rules = await (await call('/api/rules', { headers: auth })).json();
check('ships three default rules', rules.length === 3, String(rules.length));
const created = await (await call('/api/rules', {
  method: 'POST', headers: auth,
  body: JSON.stringify({ type: 'comment', name: 'Guide', keywords: 'Guide, PDF ,,', dmReply: 'Here you go', publicReply: 'Sent!' }),
})).json();
check('creates a rule', !!created.id);
check('normalises keywords', JSON.stringify(created.keywords) === '["guide","pdf"]', JSON.stringify(created.keywords));
check('rejects an empty rule', (await call('/api/rules', { method: 'POST', headers: auth, body: JSON.stringify({ name: 'x', type: 'dm', keywords: '' }) })).status === 400);
const updated = await (await call('/api/rules/' + created.id, { method: 'PUT', headers: auth, body: JSON.stringify({ enabled: false, keywords: 'a,b' }) })).json();
check('updates enabled', updated.enabled === false);
check('updates keywords', JSON.stringify(updated.keywords) === '["a","b"]');
check('deletes a rule', (await call('/api/rules/' + created.id, { method: 'DELETE', headers: auth })).status === 204);
rules = await (await call('/api/rules', { headers: auth })).json();
check('back to three rules', rules.length === 3, String(rules.length));

console.log('\n— dry-run tester —');
const t1 = await (await call('/api/rules/test', { method: 'POST', headers: auth, body: JSON.stringify({ type: 'comment', text: 'send me the link please' }) })).json();
check('matches the link rule', t1.matched && t1.rule.name === 'Link request', JSON.stringify(t1.rule));
check('returns the DM text', t1.outgoing.dm.includes('link'));
const t2 = await (await call('/api/rules/test', { method: 'POST', headers: auth, body: JSON.stringify({ type: 'dm', text: 'hello' }) })).json();
check('matches the greeting', t2.matched && t2.rule.name === 'Greeting');
const t3 = await (await call('/api/rules/test', { method: 'POST', headers: auth, body: JSON.stringify({ type: 'comment', text: 'nice reel' }) })).json();
check('no match stays silent', t3.matched === false);

console.log('\n— settings & activity —');
const s = await (await call('/api/settings', { headers: auth })).json();
check('default cap is 200/hour', s.maxSends === 200);
const s2 = await (await call('/api/settings', { method: 'POST', headers: auth, body: JSON.stringify({ maxSends: 150, autoReplyComments: false }) })).json();
check('saves settings', s2.maxSends === 150 && s2.autoReplyComments === false);
check('activity starts empty', (await (await call('/api/activity', { headers: auth })).json()).length === 0);

console.log('\n— connect / disconnect —');
const tokenRes = await (await call('/api/token', { method: 'POST', headers: auth, body: JSON.stringify({ token: 'IGAAvalid' }) })).json();
check('connects with a token', tokenRes.ok === true && tokenRes.handle === 'viraloop_test', JSON.stringify(tokenRes));
const st2 = await (await call('/api/status', { headers: auth })).json();
check('now reports connected', st2.connected === true);
const act = await (await call('/api/activity', { headers: auth })).json();
check('logs the connection', act.length >= 1 && act[0].title.includes('connected'), JSON.stringify(act[0]));
await call('/api/disconnect', { method: 'POST', headers: auth });
check('disconnect clears it', (await (await call('/api/status', { headers: auth })).json()).connected === false);

console.log('\n— polling with no token —');
const scan = await (await call('/api/scan', { method: 'POST', headers: auth, body: '{}' })).json();
check('scan reports no token instead of throwing', scan.result && scan.result.error === 'no token', JSON.stringify(scan.result));

console.log('\n— polling engine (mocked Meta API) —');
await call('/api/token', { method: 'POST', headers: auth, body: JSON.stringify({ token: 'IGAAvalid' }) });
await call('/api/settings', { method: 'POST', headers: auth, body: JSON.stringify({ maxSends: 200, autoReplyComments: true }) });
sent.length = 0;
const scan1 = await (await call('/api/scan', { method: 'POST', headers: auth, body: '{}' })).json();
check('scan reports one message and one comment', scan1.result.messages === 1 && scan1.result.comments === 1, JSON.stringify(scan1.result));
check('sent one DM for the message', sent.some(s => s.recipient && s.recipient.id === '999'), JSON.stringify(sent));
check('sent a private reply for the matching comment', sent.some(s => s.recipient && s.recipient.comment_id === 'cm1'));
check('posted the public reply too', sent.some(s => s.publicReply));
check('ignored the non-matching comment', !sent.some(s => JSON.stringify(s).includes('nice reel')));
check('ignored our own comment', !sent.some(s => JSON.stringify(s).includes('cm3')));

const actAfter = await (await call('/api/activity', { headers: auth })).json();
check('logged the DM reply', actAfter.some(a => a.type === 'message' && a.title.includes('DM replied')), JSON.stringify(actAfter.map(a => a.title)));
check('logged the comment reply', actAfter.some(a => a.type === 'comment'), JSON.stringify(actAfter.map(a => a.title)));

sent.length = 0;
const scan2 = await (await call('/api/scan', { method: 'POST', headers: auth, body: '{}' })).json();
check('second scan does not re-reply', sent.length === 0 && scan2.result.comments === 0, JSON.stringify({ sent: sent.length, res: scan2.result }));

await call('/api/settings', { method: 'POST', headers: auth, body: JSON.stringify({ maxSends: 1 }) });
sent.length = 0;
extraComment = { id: 'cm4', text: 'another link please', from: { id: '888' } };
const scan3 = await (await call('/api/scan', { method: 'POST', headers: auth, body: '{}' })).json();
check('respects the hourly cap', scan3.result.errors.some(e => e.includes('cap')), JSON.stringify(scan3.result.errors));

console.log('\n— static dashboard —');
const home = await call('/');
const homeText = await home.text();
check('serves the dashboard', home.status === 200 && homeText.includes('Connect Instagram'));
check('serves css', (await call('/css/app.css')).status === 200);
check('serves js', (await call('/js/app.js')).status === 200);
check('serves fonts', (await call('/fonts/space-grotesk-var.woff2')).status === 200);
check('unknown path 404s', (await call('/nope.html')).status === 404);
check('health check', (await call('/health')).text !== undefined);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
