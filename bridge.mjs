import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { TikTokLiveConnection, WebcastEvent } from 'tiktok-live-connector';
import { WORDS } from './dist/words.js';

const port = Number(process.env.PORT || 3000);
const clients = new Set();
let connection;
let username = '';
let connected = false;
let wordIndex = Math.floor(Math.random() * WORDS.length);
let round = 1;
let shown = false;
let leaders = {};
let answered = new Set();
let comments = [];
let count = 0;
const normalize = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const game = () => ({ type: 'game', wordIndex, round, shown, leaders, comments, count });

function chat(id, name, message) {
  id = String(id || name).slice(0, 80);
  name = String(name || 'Khách').slice(0, 35);
  message = String(message || '').slice(0, 180).trim();
  if (!message) return;
  const word = WORDS[wordIndex];
  const correct = !shown && !answered.has(id) && [word.answer, ...word.aliases].some(a => normalize(a) === normalize(message));
  if (correct) {
    answered.add(id);
    leaders[id] ??= { name, score: 0 };
    leaders[id].name = name;
    leaders[id].score++;
  }
  comments.unshift({ name, message, correct });
  comments = comments.slice(0, 7);
  count++;
  send({ type: 'chat', name, message, correct, leaders, count });
}

function send(event) {
  for (const client of clients) client.write(`data: ${JSON.stringify(event)}\n\n`);
}

async function connect(name) {
  if (!/^[\w.]{2,32}$/.test(name)) throw new Error('Username TikTok không hợp lệ');
  if (connection) await connection.disconnect().catch(() => {});
  username = name;
  connected = false;
  send({ type: 'status', connected, message: `Đang kết nối @${name}…` });
  const live = new TikTokLiveConnection(name);
  connection = live;
  live.on(WebcastEvent.CHAT, data => {
    chat(data.user?.userId || data.user?.uniqueId, data.user?.nickname || data.user?.uniqueId, data.comment);
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

createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/api/events') {
    res.writeHead(200, { 'content-type': 'text/event-stream; charset=utf-8', 'cache-control': 'no-cache', connection: 'keep-alive' });
    clients.add(res);
    res.write(`data: ${JSON.stringify({ type: 'status', connected, message: username ? `@${username}${connected ? ' đang nhận bình luận' : ' đang chờ LIVE'}` : 'Nhập username TikTok để kết nối LIVE.' })}\n\n`);
    res.write(`data: ${JSON.stringify(game())}\n\n`);
    req.on('close', () => clients.delete(res));
    return;
  }
  if (url.pathname === '/api/action' && req.method === 'POST') {
    let body = '';
    for await (const chunk of req) body += chunk;
    try {
      const { action } = JSON.parse(body);
      if (action === 'next') {
        const previous = wordIndex;
        while (wordIndex === previous) wordIndex = Math.floor(Math.random() * WORDS.length);
        round++;
        shown = false;
        answered = new Set();
      } else if (action === 'reveal') shown = true;
      else throw new Error('Thao tác không hợp lệ');
      send(game());
      res.writeHead(200, { 'content-type': 'application/json' }).end('{"ok":true}');
    } catch (error) {
      res.writeHead(400, { 'content-type': 'application/json' }).end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  if (url.pathname === '/api/test' && req.method === 'POST') {
    let body = '';
    for await (const chunk of req) body += chunk;
    try {
      chat('test', 'Bạn (thử)', JSON.parse(body).message);
      res.writeHead(200, { 'content-type': 'application/json' }).end('{"ok":true}');
    } catch (error) {
      res.writeHead(400, { 'content-type': 'application/json' }).end(JSON.stringify({ error: error.message }));
    }
    return;
  }
  if (url.pathname === '/api/connect' && req.method === 'POST') {
    let body = '';
    for await (const chunk of req) {
      body += chunk;
      if (body.length > 1024) { res.writeHead(413).end(); return; }
    }
    try {
      const name = String(JSON.parse(body).username || '').replace(/^@/, '').trim();
      if (!/^[\w.]{2,32}$/.test(name)) throw new Error('Username TikTok không hợp lệ');
      res.writeHead(202, { 'content-type': 'application/json' }).end(JSON.stringify({ ok: true }));
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
