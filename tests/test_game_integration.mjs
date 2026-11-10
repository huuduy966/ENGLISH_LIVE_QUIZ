import { WORDS, WORD_SET_ID } from '../dist/words.js';
import assert from 'node:assert';

console.log(`Checking words.js: ${WORDS.length} words, WORD_SET_ID: ${WORD_SET_ID}`);
assert.strictEqual(WORDS.length, 20000, 'WORDS phải có đúng 20.000 mục');
assert.strictEqual(typeof WORD_SET_ID, 'string');
assert.strictEqual(WORD_SET_ID.length, 12);

// Kiểm tra random bốc từ 10.000 lần không gặp lỗi
const sampleWords = new Set();
for (let i = 0; i < 10000; i++) {
  const item = WORDS[Math.floor(Math.random() * WORDS.length)];
  assert.ok(item.word && item.answer && item.phonetic, 'Mỗi từ phải có word, answer, phonetic');
  sampleWords.add(item.word);
}
assert.ok(sampleWords.size > 5000, 'Độ phân tán ngẫu nhiên phải tốt');

// Kiểm tra memory usage
const mem = process.memoryUsage().heapUsed / 1024 / 1024;
console.log(`Node.js heap used with 20k words: ${mem.toFixed(2)} MB`);
assert.ok(mem < 50, 'Bộ nhớ heap phải dưới 50MB');

// Kiểm tra từ support
const support = WORDS.find(w => w.word === 'support');
assert.ok(support, 'Từ support phải tồn tại');
assert.strictEqual(support.answer, 'hỗ trợ');
assert.ok(support.aliases.includes('ủng hộ'));

console.log('Node.js integration check passed successfully!');
