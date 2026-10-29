'use strict';
/**
 * Meta integration: OAuth (Instagram Login or Facebook Login) + the
 * Instagram Messaging Send API.
 *
 * Every send here targets someone who already contacted you. There is no
 * broadcast / cold-outreach function — that is what keeps the account safe.
 */
require('dotenv').config();

const APP_ID = process.env.META_APP_ID || '';
const APP_SECRET = process.env.META_APP_SECRET || '';
const ROUTE = (process.env.LOGIN_ROUTE || 'instagram').toLowerCase();
const PUBLIC_URL = (process.env.PUBLIC_URL || process.env.RENDER_EXTERNAL_URL || 'http://localhost:3000').replace(/\/$/, '');
const GRAPH = 'https://graph.instagram.com/v23.0';
const FB_GRAPH = 'https://graph.facebook.com/v21.0';
const SCOPES = 'instagram_business_basic,instagram_business_manage_messages';
const FB_SCOPES = 'instagram_basic,instagram_manage_messages,pages_manage_metadata,pages_show_list,business_management';

const configured = () => !!(APP_ID && APP_SECRET);
const redirectUri = () => PUBLIC_URL + '/auth/callback';

/** Where to send the browser to authorise. */
function authorizeUrl(state) {
  if (ROUTE === 'facebook') {
    const p = new URLSearchParams({ client_id: APP_ID, redirect_uri: redirectUri(), response_type: 'code', scope: FB_SCOPES, state: state || '' });
    return `https://www.facebook.com/v21.0/dialog/oauth?${p}`;
  }
  const p = new URLSearchParams({ client_id: APP_ID, redirect_uri: redirectUri(), response_type: 'code', scope: SCOPES, state: state || '' });
  return `https://www.instagram.com/oauth/authorize?${p}`;
}

/** Exchange the ?code from the callback for a long-lived access token. */
async function exchangeCode(code) {
  if (ROUTE === 'facebook') {
    const t = await postForm(`${FB_GRAPH}/oauth/access_token`, {
      client_id: APP_ID, client_secret: APP_SECRET, redirect_uri: redirectUri(), code,
    });
    return t.access_token;
  }
  const short = await postForm('https://api.instagram.com/oauth/access_token', {
    client_id: APP_ID, client_secret: APP_SECRET, grant_type: 'authorization_code', redirect_uri: redirectUri(), code,
  });
  // Upgrade to a long-lived (~60 day) token.
  const p = new URLSearchParams({ grant_type: 'ig_exchange_token', client_secret: APP_SECRET, access_token: short.access_token });
  const res = await fetch(`${GRAPH}/access_token?${p}`);
  const long = await res.json();
  return long.access_token || short.access_token;
}

/** Fetch the connected account's id + username. */
async function getAccount(token) {
  if (ROUTE === 'facebook') {
    const res = await fetch(`${FB_GRAPH}/me?fields=id,name&access_token=${encodeURIComponent(token)}`);
    return res.json();
  }
  const res = await fetch(`${GRAPH}/me?fields=user_id,username&access_token=${encodeURIComponent(token)}`);
  const j = await res.json();
  return { id: j.user_id || j.id, username: j.username };
}

/** Send a DM to a user who messaged you first. */
async function sendDM(igsid, text, token) {
  const igId = igIdFor(token);
  return graphPost(`${igId}/messages`, { recipient: { id: igsid }, message: { text } }, token);
}

/** Private reply that moves a comment into DMs (one per comment, per Meta). */
async function sendPrivateReply(commentId, text, token) {
  const igId = igIdFor(token);
  return graphPost(`${igId}/messages`, { recipient: { comment_id: commentId }, message: { text } }, token);
}

/** Public reply posted under a comment. */
async function replyToComment(commentId, text, token) {
  const base = ROUTE === 'facebook' ? FB_GRAPH : GRAPH;
  return graphPost(`${commentId}/replies`, { message: text }, token, base);
}

/* ---------- helpers ---------- */
function igIdFor() {
  const acc = require('./data').account.get();
  return acc.igId || (ROUTE === 'facebook' ? process.env.PAGE_ID : 'me');
}
async function postForm(url, fields) {
  const res = await fetch(url, { method: 'POST', body: new URLSearchParams(fields) });
  const j = await res.json();
  if (!res.ok) throw new Error('OAuth error: ' + JSON.stringify(j));
  return j;
}
async function graphPost(path, body, token, base) {
  const host = base || (ROUTE === 'facebook' ? FB_GRAPH : GRAPH);
  const res = await fetch(`${host}/${path}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.assign({}, body, { access_token: token })),
  });
  const j = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Send API ${res.status}: ${JSON.stringify(j)}`);
  return j;
}

/* ---------- Conversations (polling mode — no webhook needed) ---------- */
function hostBase() { return ROUTE === 'facebook' ? FB_GRAPH : GRAPH; }
function selfId() { return ROUTE === 'facebook' ? (process.env.PAGE_ID || 'me') : 'me'; }

async function getConversations(token) {
  const platform = ROUTE === 'facebook' ? 'platform=instagram&' : '';
  const url = `${hostBase()}/${selfId()}/conversations?${platform}access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Conversations API: ' + JSON.stringify(j));
  return j.data || [];
}

async function getConversationMessages(convId, token) {
  const url = `${hostBase()}/${convId}?fields=messages&access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Messages API: ' + JSON.stringify(j));
  return (j.messages && j.messages.data) || [];
}

async function getMessage(msgId, token) {
  const url = `${hostBase()}/${msgId}?fields=id,created_time,from,message&access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Message API: ' + JSON.stringify(j));
  return j;
}

/** Refresh a long-lived token (valid ~60 days). No app secret required. */
async function refreshToken(token) {
  const url = `${GRAPH}/refresh_access_token?grant_type=ig_refresh_token&access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Refresh failed: ' + JSON.stringify(j));
  return j; // { access_token, token_type, expires_in }
}


/* ---------- Media + comments (comment polling — no webhook needed) ---------- */
async function getRecentMedia(token, limit = 10) {
  const igId = igIdFor(token);
  const fields = 'id,caption,permalink,timestamp,media_type,comments.limit(50){id,text,timestamp,from,username}';
  const url = `${hostBase()}/${igId}/media?fields=${encodeURIComponent(fields)}&limit=${limit}&access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Media API: ' + JSON.stringify(j));
  return j.data || [];
}

/** Full comment list for one media object (paged, most recent first). */
async function getMediaComments(mediaId, token) {
  const url = `${hostBase()}/${mediaId}/comments?fields=id,text,timestamp,from,username&limit=50&access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Comments API: ' + JSON.stringify(j));
  return j.data || [];
}

/** Who am I — used by the dashboard to show the connected account. */
async function getProfile(token) {
  const igId = igIdFor(token);
  const url = `${hostBase()}/${igId}?fields=id,user_id,username,name,profile_picture_url,followers_count,media_count&access_token=${encodeURIComponent(token)}`;
  const res = await fetch(url);
  const j = await res.json();
  if (!res.ok) throw new Error('Profile API: ' + JSON.stringify(j));
  return j;
}

module.exports = { configured, getRecentMedia, getMediaComments, getProfile, authorizeUrl, exchangeCode, getAccount, sendDM, sendPrivateReply, replyToComment,
  getConversations, getConversationMessages, getMessage, refreshToken, ROUTE, PUBLIC_URL };
