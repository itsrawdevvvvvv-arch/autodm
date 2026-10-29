'use strict';
/**
 * Polling engine — how Viraloop works without a public webhook URL.
 *
 * Two passes per tick:
 *   1. messages  — recent conversations, reply to new inbound DMs
 *   2. comments  — recent media, reply to new comments (public reply + private DM)
 *
 * Meta's rules mean a private reply to a comment is allowed once per comment,
 * which is exactly what the comment pass does.
 */
const data = require('./data');
const meta = require('./meta');
const { handleMessage, handleComment } = require('./automation');

let timer = null;
let busy = false;
let lastMessageResult = 'idle';
let lastCommentResult = 'idle';
let lastRunAt = 0;
let runs = 0;
let handledTotal = 0;

const MAX_COMMENTS_PER_TICK = 10;
const HANDLED_MEMORY = 500;

/* ---------------- messages ---------------- */

async function messagePass(acc) {
  const seen = data.poller.get();
  let newest = seen.lastSeen || 0;
  let handled = 0;

  const conversations = await meta.getConversations(acc.token);
  for (const conv of conversations) {
    const msgs = await meta.getConversationMessages(conv.id, acc.token);
    for (const m of msgs) {
      const ts = Date.parse(m.created_time || 0) || 0;
      if (ts <= (seen.lastSeen || 0)) continue;
      const full = await meta.getMessage(m.id, acc.token);
      const fromId = full.from && full.from.id;
      if (fromId && acc.igId && String(fromId) === String(acc.igId)) {
        newest = Math.max(newest, ts);
        continue;
      }
      await handleMessage({ type: 'message', senderId: fromId, text: full.message || '', mid: full.id, isEcho: false });
      handled++;
      newest = Math.max(newest, ts);
    }
  }

  if (newest > (seen.lastSeen || 0)) data.poller.set({ lastSeen: newest });
  return handled;
}

/* ---------------- comments ---------------- */

async function commentPass(acc) {
  const state = data.poller.get();
  const handled = new Set(state.handledComments || []);
  let newHandled = 0;

  const media = await meta.getRecentMedia(acc.token, 10);
  for (const item of media) {
    if (newHandled >= MAX_COMMENTS_PER_TICK) break;
    const comments = await meta.getMediaComments(item.id, acc.token);
    for (const c of comments) {
      if (newHandled >= MAX_COMMENTS_PER_TICK) break;
      if (handled.has(c.id)) continue;

      const authorId = (c.from && c.from.id) || null;
      // Our own comment (public reply) — remember and move on.
      if (authorId && acc.igId && String(authorId) === String(acc.igId)) {
        handled.add(c.id);
        continue;
      }
      await handleComment({ type: 'comment', commentId: c.id, text: c.text || '', fromId: authorId, mediaId: item.id });
      handled.add(c.id);
      newHandled++;
    }
  }

  if (newHandled) {
    const list = Array.from(handled).slice(-HANDLED_MEMORY);
    data.poller.set({ handledComments: list });
    handledTotal += newHandled;
  }
  return newHandled;
}

/* ---------------- loop ---------------- */

async function tick(options) {
  if (busy) return { skipped: true };
  busy = true;
  const opts = options || {};
  try {
    const acc = data.account.get();
    if (!acc.token) { lastMessageResult = 'no token'; lastCommentResult = 'no token'; return { error: 'no token' }; }

    let messages = 0;
    let comments = 0;

    if (opts.only !== 'comments') {
      try {
        messages = await messagePass(acc);
        lastMessageResult = messages ? `handled ${messages}` : 'idle';
      } catch (e) {
        lastMessageResult = 'error: ' + e.message;
        console.error('[poller:messages]', e.message);
      }
    }

    if (opts.only !== 'messages') {
      try {
        comments = await commentPass(acc);
        lastCommentResult = comments ? `handled ${comments}` : 'idle';
      } catch (e) {
        lastCommentResult = 'error: ' + e.message;
        console.error('[poller:comments]', e.message);
      }
    }

    lastRunAt = Date.now();
    runs++;
    return { messages, comments };
  } finally {
    busy = false;
  }
}

function start(seconds) {
  stop();
  const ms = Math.max(10, parseInt(seconds, 10) || 30) * 1000;
  timer = setInterval(() => tick(), ms);
  setTimeout(() => tick(), 1500);
  console.log(`[poller] polling every ${ms / 1000}s (messages + comments)`);
}

function stop() { if (timer) { clearInterval(timer); timer = null; console.log('[poller] stopped'); } }

function status() {
  return {
    running: !!timer,
    busy,
    lastResult: lastMessageResult,
    messages: lastMessageResult,
    comments: lastCommentResult,
    lastRunAt,
    runs,
    handledTotal,
  };
}

module.exports = { start, stop, status, tick };
