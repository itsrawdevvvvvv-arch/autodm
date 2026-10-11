/* ============================================================
   AutoDM — front end
   The app auto-detects whether it is being served by the AutoDM
   server. If it is, Connect works normally. If it is opened as a
   plain file (or hosted statically with no server), it runs on demo
   data and lets you point it at a server address.
   ============================================================ */
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const uid = () => Math.random().toString(36).slice(2, 9);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---- server detection ---- */
let SERVER_MODE = false;                                       // true when served by the AutoDM server
let SERVER = (localStorage.getItem('autodm.server') || '').replace(/\/$/, '');  // manually set address (standalone)
const base = () => (SERVER_MODE ? '' : SERVER);
const apiActive = () => SERVER_MODE || !!SERVER;

async function detectServer() {
  try {
    const r = await fetch('/api/status', { headers: { Accept: 'application/json' } });
    const ct = r.headers.get('content-type') || '';
    if (r.ok && ct.includes('application/json')) SERVER_MODE = true;
  } catch { /* not served by the server — standalone */ }
}

const ICONS = {
  message: '<svg viewBox="0 0 24 24"><path d="M21 12a8 8 0 01-11.5 7.2L4 21l1.8-5.5A8 8 0 1121 12z"/></svg>',
  comment: '<svg viewBox="0 0 24 24"><path d="M4 5h16v10H8l-4 4z"/></svg>',
  system: '<svg viewBox="0 0 24 24"><path d="M12 8v5m0 3h.01M12 3l9 16H3z"/></svg>',
};
const STAR = '<svg viewBox="0 0 24 24"><path d="M12 3l2.6 5.6 6.1.8-4.5 4.2 1.2 6L12 16.8 6.6 19.6l1.2-6L3.3 9.4l6.1-.8z"/></svg>';

/* ============ data layer ============ */
const LS = 'autodm.preview.v1';
function seedPreview() {
  return {
    connected: false, metaConfigured: false, handle: '', tokenSet: false,
    maxSends: 200, windowHours: 24, disclose: true, sendsThisHour: 0,
    rules: [
      { id: uid(), type: 'dm', name: 'Price enquiry', enabled: true, keywords: ['price', 'cost', 'how much'], match: 'contains', reply: 'Thanks for messaging! Our pricing starts at Rs.499/month — full details coming right up.' },
      { id: uid(), type: 'dm', name: 'Greeting', enabled: true, keywords: ['hi', 'hello', 'hey'], match: 'exact', reply: 'Hey! Thanks for reaching out — what can I help you with?' },
      { id: uid(), type: 'comment', name: 'Link request', enabled: true, keywords: ['link', 'send'], match: 'contains', publicReply: 'Sent to your DMs!', dmReply: 'Here is the link you asked for.' },
    ],
    activity: [
      { id: uid(), type: 'message', title: 'DM replied', detail: '@riya sent "price?" → matched Price enquiry', ts: Date.now() - 240000 },
      { id: uid(), type: 'comment', title: 'Comment handled', detail: '@arjun commented "link" → public reply + DM', ts: Date.now() - 2400000 },
      { id: uid(), type: 'system', title: 'Guardrail held', detail: 'Skipped a reply outside the 24-hour window', ts: Date.now() - 7200000 },
    ],
  };
}

async function api(path, opts) {
  const res = await fetch(base() + path, Object.assign({ headers: { 'Content-Type': 'application/json' } }, opts));
  const ct = res.headers.get('content-type') || '';
  if (!res.ok || !ct.includes('application/json')) throw new Error('backend-unavailable');
  return res.status === 204 ? null : res.json();
}

const store = {
  _p: null,
  preview() { if (!this._p) this._p = JSON.parse(localStorage.getItem(LS) || 'null') || seedPreview(); return this._p; },
  savePreview() { localStorage.setItem(LS, JSON.stringify(this._p)); },
  async status() { return apiActive() ? api('/api/status') : this.preview(); },
  async rules() { return apiActive() ? api('/api/rules') : this.preview().rules; },
  async activity() { return apiActive() ? api('/api/activity') : this.preview().activity; },
  async settings() { return apiActive() ? api('/api/settings') : this.preview(); },
  async saveRule(rule) {
    if (apiActive()) {
      const isNew = !rule.id;
      return api(isNew ? '/api/rules' : '/api/rules/' + rule.id, { method: isNew ? 'POST' : 'PUT', body: JSON.stringify(rule) });
    }
    const p = this.preview();
    if (rule.id) { const i = p.rules.findIndex(x => x.id === rule.id); p.rules[i] = rule; }
    else { rule.id = uid(); p.rules.push(rule); }
    this.savePreview(); return rule;
  },
  async deleteRule(id) {
    if (apiActive()) return api('/api/rules/' + id, { method: 'DELETE' });
    const p = this.preview(); p.rules = p.rules.filter(r => r.id !== id); this.savePreview();
  },
  async saveSettings(s) {
    if (apiActive()) return api('/api/settings', { method: 'POST', body: JSON.stringify(s) });
    Object.assign(this.preview(), s); this.savePreview();
  },
  async setToken(token) {
    if (apiActive()) return api('/api/token', { method: 'POST', body: JSON.stringify({ token }) });
    this.preview().tokenSet = !!token; this.savePreview();
  },
};

/* ============ state ============ */
let STATE = { status: {}, rules: [], activity: [], settings: {} };

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2600);
}
function timeAgo(ts) {
  const m = Math.floor((Date.now() - ts) / 60000);
  if (m < 1) return 'now'; if (m < 60) return m + 'm'; const h = Math.floor(m / 60);
  if (h < 24) return h + 'h'; return Math.floor(h / 24) + 'd';
}

/* ============ renderers ============ */
function guardrails() {
  return [
    ['No password is ever stored', true],
    ['Replies only after someone contacts you', true],
    [`Reply window limited to ${STATE.settings.windowHours || 24} hours`, true],
    [`Sending capped at ${STATE.settings.maxSends || 200}/hour`, true],
    ['Automation disclosed to users', !!STATE.settings.disclose],
  ];
}

function renderHeader() {
  const s = STATE.status;
  const handle = s.handle ? String(s.handle).replace(/^@/, '') : '';
  $('#handleName').textContent = s.connected && handle ? '@' + handle : 'Not connected';
  $('#avatar').textContent = s.connected && handle ? handle.charAt(0) : '?';
  $('#tagline').textContent = s.connected ? 'Auto-replies are on'
    : (apiActive() ? 'Connect your account' : 'Demo data');
  $('#badgeText').textContent = s.connected ? 'Connected' : 'Off';
}

function renderDateStrip() {
  const names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const now = new Date();
  const start = new Date(now); start.setDate(now.getDate() - now.getDay());
  let html = '';
  for (let i = 0; i < 7; i++) {
    const d = new Date(start); d.setDate(start.getDate() + i);
    const active = d.toDateString() === now.toDateString();
    html += `<div class="day ${active ? 'active' : ''}"><span class="dow">${names[d.getDay()]}</span><span class="dnum">${d.getDate()}</span></div>`;
  }
  $('#dateStrip').innerHTML = html;
}

function renderDashboard() {
  const s = STATE.status;
  const handle = s.handle ? String(s.handle).replace(/^@/, '') : '';
  const g = guardrails();
  const onCount = g.filter(x => x[1]).length;

  $('#stars').innerHTML = Array.from({ length: 5 }, (_, i) => STAR.replace('<svg', `<svg class="${i < onCount ? 'on' : ''}"`)).join('');
  $('#cardDesc').textContent = s.connected
    ? 'Your account is linked. AutoDM replies to people who message or comment — never to cold contacts.'
    : (apiActive()
        ? 'Connect your Instagram Professional account to start replying automatically.'
        : 'Showing sample data. Open Settings to point AutoDM at your server, then Connect.');

  $('#subAvatar').textContent = s.connected && handle ? handle.charAt(0) : '?';
  $('#subName').textContent = s.connected && handle ? '@' + handle : 'No account';
  $('#subTag').textContent = s.connected ? 'Instagram Professional' : (apiActive() ? 'Not connected' : 'Demo data');
  $('#subBadge').textContent = s.connected ? 'Live' : 'Off';

  const dms = STATE.activity.filter(a => a.type === 'message').length;
  const cm = STATE.activity.filter(a => a.type === 'comment').length;
  const rules = STATE.rules.filter(r => r.enabled).length;
  $('#statBoxes').innerHTML = [
    [dms, 'DMs'], [cm, 'Comments'], [rules, 'Rules'],
  ].map(([n, l], i) => `<div class="box"><div class="num">${n}</div><div class="lbl">${l}</div></div>${i < 2 ? '<span class="box-sep">:</span>' : ''}`).join('');

  $('#connectBtn').textContent = s.connected ? 'Reconnect' : 'Connect Instagram';
  $('#guardTag').textContent = onCount === 5 ? 'All active' : onCount + '/5';
  $('#guardList').innerHTML = g.map(([t, on]) => `<li><span class="tick ${on ? 'on' : ''}">${on ? '✓' : ''}</span><span>${esc(t)}</span></li>`).join('');
}

function renderRules() {
  $('#ruleCount').textContent = STATE.rules.length;
  if (!STATE.rules.length) { $('#ruleList').innerHTML = '<div class="card"><div class="empty">No auto-replies yet. Tap + to add one.</div></div>'; return; }
  $('#ruleList').innerHTML = STATE.rules.map(r => `
    <div class="rule ${r.enabled ? '' : 'off'}">
      <div class="rule-top">
        <div><div class="rule-type">${r.type === 'dm' ? 'Direct message' : 'Comment'}</div><div class="rule-name">${esc(r.name)}</div></div>
        <label class="tgl"><input type="checkbox" data-toggle="${r.id}" ${r.enabled ? 'checked' : ''}/><span></span></label>
      </div>
      <div class="kws">${r.keywords.map(k => `<span class="kw">${esc(k)}</span>`).join('')}</div>
      <div class="rule-reply">${esc(r.type === 'dm' ? r.reply : (r.dmReply || r.publicReply || ''))}</div>
      <div class="rule-actions"><button class="mini" data-edit="${r.id}">Edit</button><button class="mini danger" data-del="${r.id}">Delete</button></div>
    </div>`).join('');
}

function renderActivity() {
  $('#actCount').textContent = STATE.activity.length;
  if (!STATE.activity.length) { $('#activityFeed').innerHTML = '<div class="empty">No activity yet.</div>'; return; }
  $('#activityFeed').innerHTML = STATE.activity.slice().sort((a, b) => b.ts - a.ts).map(a => `
    <div class="feed-item">
      <div class="feed-ico ${a.type === 'message' ? 'msg' : ''}">${ICONS[a.type] || ICONS.system}</div>
      <div class="feed-body"><strong>${esc(a.title)}</strong><span>${esc(a.detail)}</span></div>
      <div class="feed-time">${timeAgo(a.ts)}</div>
    </div>`).join('');
}

let receiveMode = 'poll';
function setMode(m) {
  receiveMode = m;
  $$('#modeSeg .seg-btn').forEach(b => b.classList.toggle('is-active', b.dataset.mode === m));
  $('#modeDesc').textContent = m === 'poll'
    ? 'AutoDM checks for new messages on its own — no public URL or tunnel needed.'
    : "Meta pushes messages to this server's /webhook. Needs a public HTTPS URL.";
  $('#modeBadge').textContent = m === 'poll' ? 'Polling' : 'Webhook';
}
function renderSettings() {
  $('#apiBase').value = SERVER_MODE ? location.origin : SERVER;
  $('#apiBase').disabled = SERVER_MODE;
  setMode(STATE.settings.receiveMode || 'poll');
  $('#pollSeconds').value = STATE.settings.pollSeconds || 30;
  $('#maxSends').value = STATE.settings.maxSends || 200;
  $('#windowHours').value = STATE.settings.windowHours || 24;
  $('#disclose').checked = !!STATE.settings.disclose;
}

function renderAll() { renderHeader(); renderDateStrip(); renderDashboard(); renderRules(); renderActivity(); renderSettings(); }

/* ============ navigation ============ */
function go(view) {
  $$('.tab').forEach(t => t.classList.toggle('is-active', t.dataset.view === view));
  $$('.view').forEach(v => v.classList.toggle('is-active', v.id === 'view-' + view));
  $('#fab').hidden = view !== 'replies';
  window.scrollTo({ top: 0 });
}

/* ============ rule sheet ============ */
let trigger = 'dm';
function setTrigger(t) {
  trigger = t;
  $$('#triggerSeg .seg-btn').forEach(b => b.classList.toggle('is-active', b.dataset.trigger === t));
  $('#fldDm').hidden = t !== 'dm';
  $('#fldPublic').hidden = t === 'dm';
  $('#fldDmComment').hidden = t === 'dm';
}
function openSheet(rule) {
  $('#ruleId').value = rule ? rule.id : '';
  $('#sheetTitle').textContent = rule ? 'Edit auto-reply' : 'New auto-reply';
  setTrigger(rule ? rule.type : 'dm');
  $('#ruleName').value = rule ? rule.name : '';
  $('#ruleKeywords').value = rule ? rule.keywords.join(', ') : '';
  $('#ruleMatch').value = rule ? rule.match : 'contains';
  $('#ruleReply').value = rule && rule.reply ? rule.reply : '';
  $('#rulePublic').value = rule && rule.publicReply ? rule.publicReply : '';
  $('#ruleDmReply').value = rule && rule.dmReply ? rule.dmReply : '';
  $('#sheetBackdrop').classList.add('open');
}
function closeSheet() { $('#sheetBackdrop').classList.remove('open'); }

async function submitRule(e) {
  e.preventDefault();
  const id = $('#ruleId').value || undefined;
  const keywords = $('#ruleKeywords').value.split(',').map(k => k.trim()).filter(Boolean);
  if (!keywords.length) return toast('Add at least one keyword');
  const rule = { id, type: trigger, name: $('#ruleName').value.trim() || 'Untitled', keywords, match: $('#ruleMatch').value, enabled: true };
  if (trigger === 'dm') { rule.reply = $('#ruleReply').value.trim(); if (!rule.reply) return toast('Add a reply message'); }
  else { rule.publicReply = $('#rulePublic').value.trim(); rule.dmReply = $('#ruleDmReply').value.trim(); if (!rule.dmReply && !rule.publicReply) return toast('Add a reply'); }
  if (id) { const cur = STATE.rules.find(r => r.id === id); rule.enabled = cur ? cur.enabled : true; }
  await store.saveRule(rule); await refresh(); closeSheet();
  toast(id ? 'Auto-reply updated' : 'Auto-reply created');
}

/* ============ refresh ============ */
function useDemo() {
  const p = store.preview();
  STATE.status = p; STATE.rules = p.rules; STATE.activity = p.activity; STATE.settings = p;
  renderAll();
}
async function refresh() {
  if (!apiActive()) { useDemo(); return; }
  try {
    const [status, rules, activity, settings] = await Promise.all([store.status(), store.rules(), store.activity(), store.settings()]);
    STATE.status = status || {}; STATE.rules = rules || []; STATE.activity = activity || []; STATE.settings = settings || {};
    renderAll();
  } catch (err) {
    useDemo();
    console.error(err);
  }
}

/* ============ events ============ */
document.addEventListener('DOMContentLoaded', () => {
  $('#nav').addEventListener('click', e => { const t = e.target.closest('.tab'); if (t) go(t.dataset.view); });

  $('#connectBtn').addEventListener('click', async () => {
    if (!apiActive()) { toast('Add your server address in Settings'); go('settings'); return; }
    if (SERVER_MODE) {
      try {
        const s = await store.status();
        if (!s.metaConfigured) return toast('Add META_APP_ID and META_APP_SECRET to .env');
        window.location.href = '/auth/instagram';
      } catch { toast('Server not reachable'); }
      return;
    }
    window.location.href = SERVER + '/auth/instagram';
  });

  $('#fab').addEventListener('click', () => openSheet(null));
  $('#sheetClose').addEventListener('click', closeSheet);
  $('#sheetCancel').addEventListener('click', closeSheet);
  $('#sheetBackdrop').addEventListener('click', e => { if (e.target.id === 'sheetBackdrop') closeSheet(); });
  $('#triggerSeg').addEventListener('click', e => { const b = e.target.closest('.seg-btn'); if (b) setTrigger(b.dataset.trigger); });
  $('#ruleForm').addEventListener('submit', submitRule);

  $('#ruleList').addEventListener('click', async e => {
    const ed = e.target.closest('[data-edit]'); const dl = e.target.closest('[data-del]');
    if (ed) openSheet(STATE.rules.find(r => r.id === ed.dataset.edit));
    if (dl) { if (confirm('Delete this auto-reply?')) { await store.deleteRule(dl.dataset.del); await refresh(); toast('Deleted'); } }
  });
  $('#ruleList').addEventListener('change', async e => {
    const t = e.target.closest('[data-toggle]'); if (!t) return;
    const r = STATE.rules.find(x => x.id === t.dataset.toggle); if (!r) return;
    r.enabled = t.checked; await store.saveRule(r); await refresh();
  });

  $('#saveConnection').addEventListener('click', async () => {
    if (!SERVER_MODE) { SERVER = $('#apiBase').value.trim().replace(/\/$/, ''); localStorage.setItem('autodm.server', SERVER); }
    const token = $('#manualToken').value.trim();
    if (!token) return toast('Paste your access token');
    await store.setToken(token);
    $('#manualToken').value = '';
    await refresh(); toast('Token saved');
  });
  $('#refreshToken').addEventListener('click', async () => {
    if (!apiActive()) return toast('Needs the server running');
    try { await api('/api/refresh-token', { method: 'POST' }); await refresh(); toast('Token refreshed'); }
    catch { toast('Could not refresh token'); }
  });
  $('#modeSeg').addEventListener('click', e => { const b = e.target.closest('.seg-btn'); if (b) setMode(b.dataset.mode); });
  $('#saveLimits').addEventListener('click', async () => {
    await store.saveSettings({
      maxSends: Math.max(1, parseInt($('#maxSends').value, 10) || 200),
      windowHours: Math.min(24, Math.max(1, parseInt($('#windowHours').value, 10) || 24)),
      disclose: $('#disclose').checked,
      receiveMode,
      pollSeconds: Math.max(10, parseInt($('#pollSeconds').value, 10) || 30),
    });
    await refresh(); toast('Saved');
  });
  $('#exportRules').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(STATE.rules, null, 2)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'autodm-rules.json'; a.click(); URL.revokeObjectURL(a.href);
  });
  $('#importRules').addEventListener('change', async e => {
    const f = e.target.files[0]; if (!f) return;
    try {
      const data = JSON.parse(await f.text());
      if (!Array.isArray(data)) throw new Error();
      for (const r of data) { delete r.id; await store.saveRule(r); }
      await refresh(); toast('Imported ' + data.length + ' rules');
    } catch { toast('Invalid file'); }
    e.target.value = '';
  });

  detectServer().then(refresh);
});
