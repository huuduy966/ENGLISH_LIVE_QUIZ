import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { TikTokLiveConnection, WebcastEvent } from 'tiktok-live-connector';
import { WORDS } from './dist/words.js';

const port = Number(process.env.PORT || 3000);
const relayPort = Number(process.env.RELAY_PORT || 3002);
const siteOrigin = 'https://english-live-quiz-20261102.comfymound1.chatgpt.site';
const viewerOrigins = new Set([siteOrigin, 'http://127.0.0.1:3000', 'http://127.0.0.1:3001']);
const ROUND_MS = 15000;
const REVEAL_MS = 5000;
const clients = new Set();
let tunnel;
let tunnelUrl = '';
let tunnelStarting;
let connection;
let username = '';
let connected = false;
let wordIndex = Math.floor(Math.random() * WORDS.length);
let round = 1;
let shown = false;
let startedAt = Date.now();
let revealedAt = null;
let leaders = {};
let answered = new Set();
let comments = [];
let count = 0;
const normalize = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const game = () => ({ type: 'game', wordIndex, round, shown, startedAt, revealedAt, leaders, comments, count, username, connected, serverTime: Date.now() });

function nextRound() {
  const previous = wordIndex;
  while (wordIndex === previous) wordIndex = Math.floor(Math.random() * WORDS.length);
  round++;
  shown = false;
  revealedAt = null;
  startedAt = Date.now();
  answered = new Set();
  send(game());
}

function revealRound() {
  if (shown) return;
  shown = true;
  revealedAt = Date.now();
  send(game());
}

setInterval(() => {
  if (shown && Date.now() - revealedAt >= REVEAL_MS) nextRound();
  else if (!shown && Date.now() - startedAt >= ROUND_MS) {
    if (answered.size === 0) revealRound();
    else nextRound();
  }
}, 100);

function chat(id, name, message, avatar = '') {
  id = String(id || name).slice(0, 80);
  name = String(name || 'Khách').slice(0, 35);
  message = String(message || '').slice(0, 180).trim();
  avatar = typeof avatar === 'string' && /^https:\/\//i.test(avatar) ? avatar.slice(0, 2048) : '';
  if (!message) return;
  const word = WORDS[wordIndex];
  const correct = !shown && Date.now() - startedAt < ROUND_MS && !answered.has(id) && [word.answer, ...word.aliases].some(a => normalize(a) === normalize(message));
  if (correct) {
    answered.add(id);
    leaders[id] ??= { name, avatar, score: 0 };
    leaders[id].name = name;
    if (avatar) leaders[id].avatar = avatar;
    leaders[id].score++;
  }
  comments.unshift({ name, avatar, message, correct });
  comments = comments.slice(0, 7);
  count++;
  send({ type: 'chat', name, avatar, message, correct, leaders, count });
}

function send(event) {
  for (const client of clients) client.write(`data: ${JSON.stringify(event)}\n\n`);
}

function serveEvents(req, res, headers = {}) {
  res.writeHead(200, { 'content-type': 'text/event-stream; charset=utf-8', 'cache-control': 'no-cache', connection: 'keep-alive', ...headers });
  clients.add(res);
  res.write(`data: ${JSON.stringify({ type: 'status', connected, message: username ? `@${username}${connected ? ' đang nhận bình luận' : ' đang chờ LIVE'}` : 'Nhập username TikTok để kết nối LIVE.' })}\n\n`);
  res.write(`data: ${JSON.stringify(game())}\n\n`);
  req.on('close', () => clients.delete(res));
}

function startTunnel() {
  if (tunnelUrl) return Promise.resolve(tunnelUrl);
  if (tunnelStarting) return tunnelStarting;
  tunnelStarting = new Promise((resolve, reject) => {
    const child = spawn('cloudflared', ['tunnel', '--no-autoupdate', '--url', `http://127.0.0.1:${relayPort}`], { windowsHide: true });
    tunnel = child;
    let settled = false;
    let log = '';
    const timeout = setTimeout(() => fail(new Error('Không tạo được link đồng bộ trong 30 giây.')), 30000);
    function fail(error) {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      child.kill();
      tunnel = undefined;
      reject(error);
    }
    function output(chunk) {
      log = (log + String(chunk)).slice(-4096);
      const match = log.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/i);
      if (!match || settled) return;
      settled = true;
      clearTimeout(timeout);
      tunnelUrl = match[0];
      resolve(tunnelUrl);
    }
    child.stdout.on('data', output);
    child.stderr.on('data', output);
    child.once('error', fail);
    child.once('exit', code => {
      tunnel = undefined;
      tunnelUrl = '';
      if (!settled) fail(new Error(`Cầu nối màn hình đã dừng (${code}).`));
    });
  });
  tunnelStarting.then(() => { tunnelStarting = undefined; }, () => { tunnelStarting = undefined; });
  return tunnelStarting;
}
process.on('exit', () => tunnel?.kill());

async function connect(name) {
  if (!/^[\w.]{2,32}$/.test(name)) throw new Error('Username TikTok không hợp lệ');
  if (connection) await connection.disconnect().catch(() => {});
  username = name;
  connected = false;
  send({ type: 'status', connected, message: `Đang kết nối @${name}…` });
  const live = new TikTokLiveConnection(name);
  connection = live;
  live.on(WebcastEvent.CHAT, data => {
    const user = data.user;
    const avatar = user?.avatarThumb?.urlList?.[0] || user?.avatarMedium?.urlList?.[0] || user?.avatarLarge?.urlList?.[0];
    chat(user?.id || user?.userId || user?.uniqueId || user?.displayId, user?.nickname || user?.displayId || user?.uniqueId, data.comment, avatar);
  });
  live.on('disconnected', () => {
    if (connection !== live) return;
    connected = false;
    send({ type: 'status', connected, message: `@${name} đã ngắt kết nối. Nhấn Kết nối để thử lại.` });
  });
  try {
    await live.connect();
    if (connection !== live) return;
    connected = true;
    send({ type: 'status', connected, message: `Đang nhận bình luận từ @${name}` });
  } catch (error) {
    if (connection === live) {
      connected = false;
      send({ type: 'status', connected, message: `Chưa kết nối được @${name}: ${error.message}` });
    }
  }
}

async function usernameFromTikTokLink(link) {
  let url;
  try { url = new URL(link); } catch { throw new Error('Link TikTok không hợp lệ'); }
  const hosts = new Set(['tiktok.com', 'www.tiktok.com', 'm.tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com']);
  for (let i = 0; i < 5; i++) {
    if (url.protocol !== 'https:' || !hosts.has(url.hostname)) throw new Error('Hãy dùng link livestream TikTok');
    const match = url.pathname.match(/^\/@([\w.]{2,32})\/live\/?$/i);
    if (match) return match[1];
    if (i === 4) break;
    let response;
    try { response = await fetch(url, { method: 'HEAD', redirect: 'manual', signal: AbortSignal.timeout(5000) }); }
    catch { break; }
    const location = response.headers.get('location');
    if (!location) break;
    url = new URL(location, url);
  }
  throw new Error('Không tìm thấy username. Hãy dùng link dạng tiktok.com/@tenkenh/live');
}

createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/api/events') {
    serveEvents(req, res);
    return;
  }
  if (url.pathname === '/api/share' && req.method === 'POST') {
    if (req.headers.origin && req.headers.origin !== `http://127.0.0.1:${port}`) { res.writeHead(403).end(); return; }
    try {
      const url = await startTunnel();
      res.writeHead(200, { 'content-type': 'application/json' }).end(JSON.stringify({ url }));
    } catch (error) {
      res.writeHead(503, { 'content-type': 'application/json' }).end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  if (url.pathname === '/api/action' && req.method === 'POST') {
    let body = '';
    for await (const chunk of req) body += chunk;
    try {
      const { action } = JSON.parse(body);
      if (action === 'next') {
        nextRound();
      } else if (action === 'reveal') revealRound();
      else throw new Error('Thao tác không hợp lệ');
      res.writeHead(200, { 'content-type': 'application/json' }).end('{"ok":true}');
    } catch (error) {
      res.writeHead(400, { 'content-type': 'application/json' }).end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  if (url.pathname === '/api/connect' && req.method === 'POST') {
    if (req.headers.origin && req.headers.origin !== `http://127.0.0.1:${port}`) { res.writeHead(403).end(); return; }
    let body = '';
    for await (const chunk of req) {
      body += chunk;
      if (body.length > 1024) { res.writeHead(413).end(); return; }
    }
    try {
      const input = JSON.parse(body);
      const name = input.link ? await usernameFromTikTokLink(input.link) : String(input.username || '').replace(/^@/, '').trim();
      if (!/^[\w.]{2,32}$/.test(name)) throw new Error('Username TikTok không hợp lệ');
      res.writeHead(202, { 'content-type': 'application/json' }).end(JSON.stringify({ ok: true, username: name }));
      connect(name).catch(error => send({ type: 'status', connected: false, message: error.message }));
    } catch (error) {
      res.writeHead(400, { 'content-type': 'application/json' }).end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  if (url.pathname === '/' || url.pathname === '/index.html') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' }).end(await readFile(new URL('./dist/index.html', import.meta.url)));
    return;
  }
  if (url.pathname === '/words.js') {
    res.writeHead(200, { 'content-type': 'text/javascript; charset=utf-8' }).end(await readFile(new URL('./dist/words.js', import.meta.url)));
    return;
  }
  res.writeHead(404).end();
}).listen(port, '127.0.0.1', () => console.log(`English Live Quiz: http://127.0.0.1:${port}`));

createServer(async (req, res) => {
  const pathname = new URL(req.url, `http://${req.headers.host}`).pathname;
  if (pathname === '/api/state' && req.method === 'GET') {
    const origin = viewerOrigins.has(req.headers.origin) ? req.headers.origin : siteOrigin;
    res.writeHead(200, { 'content-type': 'application/json', 'cache-control': 'no-store', 'access-control-allow-origin': origin, vary: 'Origin', 'x-content-type-options': 'nosniff' }).end(JSON.stringify(game()));
    return;
  }
  if (pathname === '/api/health' && req.method === 'GET') {
    res.writeHead(200, { 'content-type': 'text/plain' }).end('ok');
    return;
  }
  if (req.method === 'GET' && (pathname === '/' || pathname === '/index.html' || pathname === '/words.js')) {
    const file = pathname === '/words.js' ? 'words.js' : 'index.html';
    const contentType = file === 'words.js' ? 'text/javascript' : 'text/html';
    try {
      res.writeHead(200, { 'content-type': `${contentType}; charset=utf-8`, 'cache-control': 'no-store', 'x-robots-tag': 'noindex' }).end(await readFile(new URL(`./dist/${file}`, import.meta.url)));
    } catch { res.writeHead(500).end(); }
    return;
  }
  res.writeHead(404).end();
}).listen(relayPort, '127.0.0.1');
