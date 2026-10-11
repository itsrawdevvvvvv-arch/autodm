'use strict';
/**
 * Polling engine — the personal-mode alternative to webhooks.
 *
 * Instead of waiting for Meta to push events to a public webhook URL, this
 * periodically asks the Conversations API for recent messages and replies to
 * any new inbound ones. That means the app can run entirely on your own
 * machine with no public URL and no tunnel.
 *
 * Note: Meta documents that reading conversations with people who don't have a
 * role on your app may require Advanced Access. If the Conversations API
 * returns a permission error, switch receive mode to "webhook".
 */
const data = require('./data');
const meta = require('./meta');
const { handleMessage } = require('./automation');

let timer = null;
let busy = false;
let lastResult = null;

async function tick() {
  if (busy) return;
  busy = true;
  try {
    const acc = data.account.get();
    if (!acc.token) { lastResult = 'no token'; return; }

    const seen = data.poller.get();
    let newest = seen.lastSeen || 0;
    let handled = 0;

    const conversations = await meta.getConversations(acc.token);
    for (const conv of conversations) {
      const msgs = await meta.getConversationMessages(conv.id, acc.token);
      for (const m of msgs) {
        const ts = Date.parse(m.created_time || 0) || 0;
        if (ts <= (seen.lastSeen || 0)) continue;           // already handled
        const full = await meta.getMessage(m.id, acc.token);
        const fromId = full.from && full.from.id;
        // Skip our own outgoing messages
        if (fromId && acc.igId && String(fromId) === String(acc.igId)) { newest = Math.max(newest, ts); continue; }
        await handleMessage({ type: 'message', senderId: fromId, text: full.message || '', mid: full.id, isEcho: false });
        handled++;
        newest = Math.max(newest, ts);
      }
    }

    if (newest > (seen.lastSeen || 0)) data.poller.set({ lastSeen: newest });
    lastResult = handled ? `handled ${handled}` : 'idle';
  } catch (e) {
    lastResult = 'error: ' + e.message;
    console.error('[poller]', e.message);
  } finally {
    busy = false;
  }
}

function start(seconds) {
  stop();
  const ms = Math.max(10, parseInt(seconds, 10) || 30) * 1000;
  timer = setInterval(tick, ms);
  setTimeout(tick, 1500);            // first pass shortly after boot
  console.log(`[poller] polling every ${ms / 1000}s`);
}

function stop() { if (timer) { clearInterval(timer); timer = null; console.log('[poller] stopped'); } }
function status() { return { running: !!timer, lastResult }; }

module.exports = { start, stop, status, tick };
