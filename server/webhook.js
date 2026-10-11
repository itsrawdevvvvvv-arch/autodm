'use strict';
const crypto = require('crypto');

/** Verify Meta's X-Hub-Signature-256 over the raw body. */
function verifySignature(req) {
  const secret = process.env.META_APP_SECRET;
  if (!secret) return true; // dev only
  const header = req.get('x-hub-signature-256');
  if (!header || !req.rawBody) return false;
  const expected = 'sha256=' + crypto.createHmac('sha256', secret).update(req.rawBody).digest('hex');
  const a = Buffer.from(header), b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

/** Flatten a Meta webhook payload into simple events. */
function parseEvents(body) {
  const out = [];
  if (!body || !Array.isArray(body.entry)) return out;
  for (const entry of body.entry) {
    if (Array.isArray(entry.messaging)) {
      for (const m of entry.messaging) {
        if (m.message) out.push({
          type: 'message',
          senderId: m.sender && m.sender.id,
          recipientId: m.recipient && m.recipient.id,
          text: m.message.text || '', mid: m.message.mid, isEcho: !!m.message.is_echo,
        });
      }
    }
    if (Array.isArray(entry.changes)) {
      for (const c of entry.changes) {
        if (c.field === 'comments' && c.value) out.push({
          type: 'comment', commentId: c.value.id, text: c.value.text || '',
          fromId: c.value.from && c.value.from.id, mediaId: c.value.media && c.value.media.id,
        });
      }
    }
  }
  return out;
}

module.exports = { verifySignature, parseEvents };
