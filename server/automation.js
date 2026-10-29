'use strict';
/**
 * The reply engine. Given a webhook event, decides whether a rule matches
 * and sends the reply — respecting every guardrail.
 */
const data = require('./data');
const meta = require('./meta');

/* in-memory safety state */
const seen = new Map();      // de-dupe events
const lastInbound = new Map(); // senderId -> timestamp (reply window)
const sends = [];            // send timestamps (rate cap)
const TTL = 6 * 3600 * 1000;

function gc(now) {
  for (const [k, t] of seen) if (now - t > TTL) seen.delete(k);
  while (sends.length && now - sends[0] > 3600 * 1000) sends.shift();
}
function isNew(id) {
  const now = Date.now(); gc(now);
  if (seen.has(id)) return false; seen.set(id, now); return true;
}
function takeSlot(limit) {
  const now = Date.now(); gc(now);
  if (sends.length >= limit) return false; sends.push(now); return true;
}
function windowOpen(id, hours) {
  const t = lastInbound.get(id); return !!t && Date.now() - t < hours * 3600 * 1000;
}

function matches(text, keywords, mode) {
  const t = (text || '').toLowerCase();
  return keywords.some(k => mode === 'exact' ? t.trim() === k.toLowerCase() : t.includes(k.toLowerCase()));
}

async function handleMessage(ev) {
  if (ev.isEcho || !ev.senderId) return;
  if (!isNew(ev.mid)) return;
  lastInbound.set(ev.senderId, Date.now());         // opens the window

  const s = data.settings.get();
  const acc = data.account.get();
  if (!acc.token) return;

  const rule = data.rules.all().find(r => r.enabled && r.type === 'dm' && matches(ev.text, r.keywords, r.match));
  const reply = rule ? rule.reply : null;
  if (!reply) return;

  if (!takeSlot(s.maxSends)) return data.activity.add({ id: id(), type: 'system', title: 'Rate cap reached', detail: 'Held a reply — hourly send cap hit', ts: Date.now() });

  try {
    await meta.sendDM(ev.senderId, reply, acc.token);
    data.settings.set({ sendsThisHour: sends.length });
    data.activity.add({ id: id(), type: 'message', title: 'DM replied', detail: `matched "${rule.name}"`, ts: Date.now() });
  } catch (e) {
    data.activity.add({ id: id(), type: 'system', title: 'Send failed', detail: e.message, ts: Date.now() });
  }
}

async function handleComment(ev) {
  if (!ev.commentId) return;
  if (!isNew('c:' + ev.commentId)) return;

  const s = data.settings.get();
  const acc = data.account.get();
  if (!acc.token) return;

  const rule = data.rules.all().find(r => r.enabled && r.type === 'comment' && matches(ev.text, r.keywords, r.match));
  if (!rule) return;

  if (rule.publicReply && takeSlot(s.maxSends)) {
    try { await meta.replyToComment(ev.commentId, rule.publicReply, acc.token); } catch (e) { /* ignore */ }
  }
  if (rule.dmReply && takeSlot(s.maxSends)) {
    try {
      await meta.sendPrivateReply(ev.commentId, rule.dmReply, acc.token);
      data.activity.add({ id: id(), type: 'comment', title: 'Comment handled', detail: `matched "${rule.name}" → public reply + DM`, ts: Date.now() });
    } catch (e) {
      data.activity.add({ id: id(), type: 'system', title: 'Private reply failed', detail: e.message, ts: Date.now() });
    }
  }
}

const id = () => Math.random().toString(36).slice(2, 10);

/** Dry run: which rule would fire for this sample text, and what would it send? */
function previewMatch(type, text) {
  const rules = data.rules.all().filter(r => r.enabled && r.type === type);
  const rule = rules.find(r => matches(text || '', r.keywords || [], r.match));
  if (!rule) return { matched: false, checked: rules.length };
  return {
    matched: true,
    checked: rules.length,
    rule: { id: rule.id, name: rule.name, keywords: rule.keywords, match: rule.match },
    outgoing: type === 'comment'
      ? { publicReply: rule.publicReply || '', dm: rule.dmReply || '' }
      : { dm: rule.reply || '' },
  };
}

module.exports = { handleMessage, handleComment, previewMatch };
