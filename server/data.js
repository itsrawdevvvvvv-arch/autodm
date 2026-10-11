'use strict';
/**
 * Tiny JSON-file store. Keeps rules, activity, settings and the connected
 * account between restarts. Swap for a real database when you scale up.
 */
const fs = require('fs');
const path = require('path');

const DIR = path.join(__dirname, '..', 'data');
if (!fs.existsSync(DIR)) fs.mkdirSync(DIR, { recursive: true });

function read(name, fallback) {
  try { return JSON.parse(fs.readFileSync(path.join(DIR, name + '.json'), 'utf8')); }
  catch { return fallback; }
}
function write(name, value) {
  fs.writeFileSync(path.join(DIR, name + '.json'), JSON.stringify(value, null, 2));
}

const DEFAULTS = {
  rules: [
    { id: 'r1', type: 'dm', name: 'Price enquiry', enabled: true, keywords: ['price', 'cost', 'how much'], match: 'contains', reply: 'Thanks for messaging! Our pricing starts at Rs.499/month — full details coming right up.' },
    { id: 'r2', type: 'dm', name: 'Greeting', enabled: true, keywords: ['hi', 'hello', 'hey'], match: 'exact', reply: 'Hey! Thanks for reaching out — what can I help you with?' },
    { id: 'r3', type: 'comment', name: 'Link request', enabled: true, keywords: ['link', 'send'], match: 'contains', publicReply: 'Sent to your DMs!', dmReply: 'Here is the link you asked for.' },
  ],
  activity: [],
  settings: { maxSends: 200, windowHours: 24, disclose: true, sendsThisHour: 0, receiveMode: 'poll', pollSeconds: 30 },
  account: { connected: false, token: '', igId: '', handle: '' },
};

module.exports = {
  rules: {
    all: () => read('rules', DEFAULTS.rules),
    set: (r) => write('rules', r),
  },
  activity: {
    all: () => read('activity', []),
    add: (item) => { const a = read('activity', []); a.unshift(item); write('activity', a.slice(0, 300)); return item; },
    clear: () => write('activity', []),
  },
  settings: {
    get: () => Object.assign({}, DEFAULTS.settings, read('settings', {})),
    set: (s) => { const cur = read('settings', {}); const next = Object.assign(cur, s); write('settings', next); return next; },
  },
  account: {
    get: () => Object.assign({}, DEFAULTS.account, read('account', {})),
    set: (a) => { const cur = read('account', {}); const next = Object.assign(cur, a); write('account', next); return next; },
  },
  poller: {
    get: () => Object.assign({ lastSeen: 0 }, read('poller', {})),
    set: (v) => { const next = Object.assign(read('poller', {}), v); write('poller', next); return next; },
  },
};
