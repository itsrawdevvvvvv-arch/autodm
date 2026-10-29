'use strict';
/* Viraloop dashboard — vanilla JS, no dependencies. */

const $ = (sel) => document.querySelector(sel);
const KEY_STORE = 'viraloop.key';

let state = { rules: [], settings: null };

/* ---------------- api ---------------- */

function apiKey() { return localStorage.getItem(KEY_STORE) || ''; }

async function api(path, options = {}) {
  const opts = Object.assign({ headers: {} }, options);
  opts.headers['Content-Type'] = 'application/json';
  const key = apiKey();
  if (key) opts.headers['X-Api-Key'] = key;
  if (opts.body && typeof opts.body !== 'string') opts.body = JSON.stringify(opts.body);

  const res = await fetch(path, opts);
  if (res.status === 401) {
    toast('Access key needed — set it in Settings');
    $('#api-key').focus();
    throw new Error('unauthorised');
  }
  if (res.status === 204) return null;
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = { error: text }; }
  if (!res.ok) throw new Error((data && (data.error || data.hint)) || `Request failed (${res.status})`);
  return data;
}

function toast(msg) {
  const el = $('#toast');
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { el.hidden = true; }, 3600);
}

/* ---------------- status ---------------- */

async function loadStatus() {
  const s = await api('/api/status');
  const pill = $('#status-pill');
  const text = $('#status-text');
  if (s.connected) {
    pill.className = 'pill pill--on';
    text.textContent = s.handle ? '@' + s.handle : 'Connected';
  } else {
    pill.className = 'pill pill--off';
    text.textContent = 'Not connected';
  }
  $('#oauth-wrap').hidden = !s.metaConfigured;

  const engine = $('#engine-state');
  const detail = $('#engine-detail');
  if (engine) {
    const p = s.poller || {};
    engine.textContent = p.running ? 'Running' : 'Paused';
    const bits = [];
    if (p.messages) bits.push('messages: ' + p.messages);
    if (p.comments) bits.push('comments: ' + p.comments);
    if (p.lastRunAt) bits.push('last pass ' + timeAgo(p.lastRunAt));
    detail.textContent = bits.join(' · ') || 'Waiting for the first pass';
  }
  return s;
}

async function loadOauth() {
  try {
    const o = await api('/api/oauth-check');
    const btn = $('#oauth-btn');
    const hints = $('#oauth-hints');
    const list = $('#oauth-hint-list');
    const pill = $('#oauth-pill');
    if (o.ready) {
      btn.removeAttribute('aria-disabled');
      btn.style.opacity = '';
      btn.style.pointerEvents = '';
      hints.hidden = true;
      pill.className = 'pill pill--on';
      pill.innerHTML = '<span class="dot"></span>Ready to connect';
    } else {
      btn.style.opacity = '.55';
      btn.style.pointerEvents = 'none';
      btn.setAttribute('aria-disabled', 'true');
      hints.hidden = false;
      list.innerHTML = (o.hints || []).map(h => '<li>' + escapeHtml(h) + '</li>').join('');
      pill.className = 'pill pill--off';
      pill.innerHTML = '<span class="dot"></span>Setup needed';
    }
    return o;
  } catch (e) { return null; }
}

async function loadAccount() {
  const a = await api('/api/account');
  const connected = !!a.connected;
  $('#account-disconnected').hidden = connected;
  $('#account-connected').hidden = !connected;
  if (connected) {
    $('#acc-handle').textContent = a.handle ? '@' + a.handle : 'Connected';
    const bits = [];
    if (a.profile) {
      if (a.profile.followers != null) bits.push(a.profile.followers.toLocaleString() + ' followers');
      if (a.profile.media != null) bits.push(a.profile.media + ' posts');
    }
    if (a.igId) bits.push('id ' + a.igId);
    $('#acc-meta').textContent = bits.join(' · ');
    const warn = $('#acc-warning');
    if (a.warning) { warn.hidden = false; warn.textContent = 'Token problem: ' + a.warning; }
    else warn.hidden = true;
  }
  return a;
}

/* ---------------- rules ---------------- */

function ruleCard(rule) {
  const isComment = rule.type === 'comment';
  const body = isComment
    ? [rule.dmReply ? 'DM: ' + rule.dmReply : '', rule.publicReply ? 'Public: ' + rule.publicReply : ''].filter(Boolean).join('\n')
    : 'DM: ' + (rule.reply || '');
  return `
    <article class="card rule ${rule.enabled ? '' : 'rule--off'}" data-id="${rule.id}">
      <div class="rule__top">
        <span class="rule__name">${escapeHtml(rule.name)}</span>
        <span class="rule__type ${isComment ? '' : 'rule__type--dm'}">${isComment ? 'comment' : 'direct message'}</span>
        <span class="rule__kw">${(rule.keywords || []).map(k => `<span>${escapeHtml(k)}</span>`).join('')}</span>
      </div>
      <div class="rule__body">${escapeHtml(body || '—')}</div>
      <div class="rule__actions">
        <button class="btn btn--ghost btn--sm" data-act="toggle">${rule.enabled ? 'Pause' : 'Resume'}</button>
        <button class="btn btn--ghost btn--sm" data-act="edit">Edit</button>
        <button class="btn btn--danger btn--sm" data-act="delete">Delete</button>
      </div>
    </article>`;
}

function renderRules() {
  const list = $('#rules-list');
  if (!state.rules.length) {
    list.innerHTML = '<div class="empty">No automations yet. Create one on the right.</div>';
    return;
  }
  list.innerHTML = state.rules.map(ruleCard).join('');
}

async function loadRules() {
  state.rules = await api('/api/rules');
  renderRules();
}

function resetRuleForm() {
  $('#rule-form').reset();
  $('#rule-id').value = '';
  $('#rule-form-title').textContent = 'New automation';
  $('#rule-submit').textContent = 'Create automation';
  $('#rule-cancel').hidden = true;
  $('#rule-error').hidden = true;
  syncTypeFields();
}

function syncTypeFields() {
  const type = $('#rule-type').value;
  $('#comment-fields').hidden = type !== 'comment';
  $('#dm-fields').hidden = type !== 'dm';
}

function fillRuleForm(rule) {
  $('#rule-id').value = rule.id;
  $('#rule-type').value = rule.type;
  $('#rule-name').value = rule.name;
  $('#rule-keywords').value = (rule.keywords || []).join(', ');
  $('#rule-match').value = rule.match || 'contains';
  $('#rule-dm').value = rule.dmReply || '';
  $('#rule-public').value = rule.publicReply || '';
  $('#rule-reply').value = rule.reply || '';
  $('#rule-form-title').textContent = 'Edit automation';
  $('#rule-submit').textContent = 'Save changes';
  $('#rule-cancel').hidden = false;
  syncTypeFields();
  $('#rule-form-card').scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/* ---------------- activity ---------------- */

function timeAgo(ts) {
  const s = Math.max(1, Math.round((Date.now() - ts) / 1000));
  if (s < 60) return s + 's ago';
  const m = Math.round(s / 60);
  if (m < 60) return m + 'm ago';
  const h = Math.round(m / 60);
  if (h < 24) return h + 'h ago';
  return Math.round(h / 24) + 'd ago';
}

async function loadActivity() {
  const items = await api('/api/activity');
  const log = $('#log');
  if (!items.length) {
    log.innerHTML = '<div class="empty">Nothing yet. Replies will appear here as they happen.</div>';
    return;
  }
  log.innerHTML = items.slice(0, 60).map(it => `
    <div class="log__item log__item--${escapeHtml(it.type || 'system')}">
      <div><span class="log__type">${escapeHtml(it.type || 'system')}</span>
        <div class="log__time">${it.ts ? timeAgo(it.ts) : ''}</div></div>
      <div><strong>${escapeHtml(it.title || '')}</strong>
        <div class="small muted">${escapeHtml(it.detail || '')}</div></div>
    </div>`).join('');
}

/* ---------------- settings ---------------- */

async function loadSettings() {
  const s = await api('/api/settings');
  state.settings = s;
  $('#pollSeconds').value = String(s.pollSeconds || 30);
  $('#maxSends').value = s.maxSends || 200;
  $('#receiveMode').value = s.receiveMode || 'poll';
  $('#autoReplyComments').checked = s.autoReplyComments !== false;
  const st = await api('/api/status');
  $('#key-state').textContent = st.needsKey
    ? (apiKey() ? 'A key is saved in this browser.' : 'This server requires a key — none saved yet.')
    : 'This server has no access key set (fine for local use).';
}

/* ---------------- helpers ---------------- */

function escapeHtml(str) {
  return String(str == null ? '' : str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/* ---------------- wiring ---------------- */

/* Instagram hands us back with ?connected=1 or ?connect_error=… */
function handleReturn() {
  const params = new URLSearchParams(location.search);
  if (params.get('connected')) {
    const handle = params.get('handle');
    toast(handle ? 'Connected as @' + handle : 'Instagram connected');
  } else if (params.get('connect_error')) {
    toast('Could not connect: ' + params.get('connect_error'));
  } else {
    return false;
  }
  history.replaceState({}, '', location.pathname + '#account');
  return true;
}

document.addEventListener('DOMContentLoaded', () => {
  /* account */
  $('#token-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const token = $('#token').value.trim();
    const btn = e.target.querySelector('button');
    btn.disabled = true;
    try {
      const r = await api('/api/token', { method: 'POST', body: { token } });
      toast(r.handle ? 'Connected as @' + r.handle : 'Token saved' + (r.warning ? ' — but: ' + r.warning : ''));
      $('#token').value = '';
      await refreshAll();
    } catch (err) { toast(err.message); }
    finally { btn.disabled = false; }
  });

  $('#disconnect-btn').addEventListener('click', async () => {
    if (!confirm('Disconnect this account? Automations stop until you reconnect.')) return;
    try { await api('/api/disconnect', { method: 'POST' }); toast('Disconnected'); await refreshAll(); }
    catch (e) { toast(e.message); }
  });

  $('#refresh-btn').addEventListener('click', async () => {
    try {
      const r = await api('/api/refresh-token', { method: 'POST' });
      toast('Token refreshed — valid about ' + Math.round((r.expiresIn || 0) / 86400) + ' days');
    } catch (e) { toast(e.message); }
  });

  /* scan */
  $('#scan-btn').addEventListener('click', async (e) => {
    const btn = e.currentTarget;
    btn.disabled = true;
    btn.textContent = 'Checking…';
    try {
      const r = await api('/api/scan', { method: 'POST', body: {} });
      const res = r.result || {};
      const bits = [];
      if (res.messages) bits.push(res.messages + ' new message' + (res.messages > 1 ? 's' : ''));
      if (res.comments) bits.push(res.comments + ' new comment' + (res.comments > 1 ? 's' : ''));
      toast(bits.length ? 'Handled ' + bits.join(' and ') : 'No new comments or messages');
      await Promise.all([loadStatus(), loadActivity()]);
    } catch (err) { toast(err.message); }
    finally { btn.disabled = false; btn.textContent = 'Check now'; }
  });

  /* rule form */
  $('#rule-type').addEventListener('change', syncTypeFields);
  $('#rule-cancel').addEventListener('click', resetRuleForm);

  $('#rule-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = $('#rule-error');
    errEl.hidden = true;
    const id = $('#rule-id').value;
    const type = $('#rule-type').value;
    const body = {
      type,
      name: $('#rule-name').value.trim(),
      keywords: $('#rule-keywords').value,
      match: $('#rule-match').value,
      dmReply: $('#rule-dm').value.trim(),
      publicReply: $('#rule-public').value.trim(),
      reply: $('#rule-reply').value.trim(),
    };
    const needsText = type === 'comment' ? body.dmReply : body.reply;
    if (!needsText) {
      errEl.textContent = type === 'comment' ? 'Write the DM to send.' : 'Write the reply to send.';
      errEl.hidden = false;
      return;
    }
    try {
      if (id) await api('/api/rules/' + id, { method: 'PUT', body });
      else await api('/api/rules', { method: 'POST', body });
      toast(id ? 'Automation updated' : 'Automation created');
      resetRuleForm();
      await loadRules();
    } catch (err) {
      errEl.textContent = err.message;
      errEl.hidden = false;
    }
  });

  /* rule list actions */
  $('#rules-list').addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-act]');
    if (!btn) return;
    const card = btn.closest('[data-id]');
    const id = card.dataset.id;
    const rule = state.rules.find(r => r.id === id);
    if (!rule) return;
    const act = btn.dataset.act;

    if (act === 'edit') { fillRuleForm(rule); return; }
    if (act === 'toggle') {
      try {
        await api('/api/rules/' + id, { method: 'PUT', body: { enabled: !rule.enabled } });
        await loadRules();
        toast(rule.enabled ? 'Paused' : 'Resumed');
      } catch (err) { toast(err.message); }
      return;
    }
    if (act === 'delete') {
      if (!confirm('Delete "' + rule.name + '"?')) return;
      try { await api('/api/rules/' + id, { method: 'DELETE' }); await loadRules(); toast('Deleted'); }
      catch (err) { toast(err.message); }
    }
  });

  /* tester */
  $('#test-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const type = $('#test-type').value;
    const text = $('#test-text').value;
    try {
      const r = await api('/api/rules/test', { method: 'POST', body: { type, text } });
      const out = $('#test-result');
      if (!r.matched) {
        out.innerHTML = `<div class="card"><h3>No rule matched</h3>
          <p class="small muted" style="margin-top:.4rem">Checked ${r.checked} enabled ${type} rule${r.checked === 1 ? '' : 's'}.
          Nothing would be sent — the comment or message stays in your inbox.</p></div>`;
        return;
      }
      const o = r.outgoing || {};
      out.innerHTML = `<div class="card card--tan">
        <h3>Matched “${escapeHtml(r.rule.name)}”</h3>
        <p class="small muted" style="margin:.4rem 0 .6rem">keyword ${escapeHtml((r.rule.keywords || []).join(', '))} · ${escapeHtml(r.rule.match)}</p>
        ${o.dm ? `<div class="rule__body">DM: ${escapeHtml(o.dm)}</div>` : ''}
        ${o.publicReply ? `<div class="rule__body" style="margin-top:.5rem">Public reply: ${escapeHtml(o.publicReply)}</div>` : ''}
        <p class="small" style="margin-top:.6rem">Nothing was sent — this is a dry run.</p></div>`;
    } catch (err) { toast(err.message); }
  });

  /* activity */
  $('#clear-log').addEventListener('click', async () => {
    if (!confirm('Clear the activity log?')) return;
    try { await api('/api/activity/clear', { method: 'POST' }); await loadActivity(); }
    catch (e) { toast(e.message); }
  });

  /* settings */
  $('#settings-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api('/api/settings', { method: 'POST', body: {
        pollSeconds: parseInt($('#pollSeconds').value, 10),
        maxSends: parseInt($('#maxSends').value, 10),
        receiveMode: $('#receiveMode').value,
        autoReplyComments: $('#autoReplyComments').checked,
      } });
      toast('Settings saved');
      await loadStatus();
    } catch (err) { toast(err.message); }
  });

  $('#save-key').addEventListener('click', async () => {
    const key = $('#api-key').value.trim();
    if (!key) { toast('Paste the key first'); return; }
    localStorage.setItem(KEY_STORE, key);
    try { await refreshAll(); toast('Key saved'); }
    catch (e) { localStorage.removeItem(KEY_STORE); toast('That key was rejected'); }
  });

  $('#clear-key').addEventListener('click', () => {
    localStorage.removeItem(KEY_STORE);
    $('#api-key').value = '';
    toast('Key forgotten');
    refreshAll().catch(() => {});
  });

  const returning = handleReturn();
  refreshAll().then(() => { if (returning) loadAccount(); });
});

async function refreshAll() {
  try {
    await Promise.all([loadStatus(), loadOauth(), loadAccount(), loadRules(), loadActivity(), loadSettings()]);
  } catch (e) {
    if (e.message !== 'unauthorised') toast(e.message);
  }
}
