# 20.000 Từ Đơn Tự Nhiên Cho English Live Quiz Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng và tích hợp kho 20.000 từ đơn tiếng Anh kèm nghĩa tiếng Việt tự nhiên, khẩu ngữ vào trò chơi English Live Quiz, thay thế nghĩa từ điển khô khan.

**Architecture:** Sử dụng pipeline Python 3 tầng: (1) Trích xuất 20.000 từ đơn tiếng Anh thông dụng nhất kèm IPA từ `dictionary-source.db` qua `wordfreq`, (2) Module dịch tự nhiên hóa theo lô tạo `answer` và `aliases` đời sống, (3) Kiểm định validation guard và đóng gói ra `dist/words.js` có băm mã `WORD_SET_ID` cho `bridge.mjs` và `dist/index.html`.

**Tech Stack:** Python 3.14 (sqlite3, wordfreq, unittest), Node.js v24 (ES Modules, HTTP, SSE), Vanilla HTML5/CSS3/JavaScript.

**Spec:** `docs/superpowers/specs/2026-11-10-20k-natural-words-quiz-design.md`

## Global Constraints

- Mọi từ tiếng Anh bắt buộc là từ đơn thuần túy, khớp regex `^[a-z]{2,16}$` (không chứa khoảng trắng, dấu gạch nối, dấu gạch dưới, chữ số).
- Mọi phiên âm IPA bắt buộc có định dạng `^/.+/$`.
- Nghĩa tiếng Việt `answer` và từng `alias` trong `aliases` là tiếng Việt tự nhiên, độ dài $\le 30$ ký tự, không chứa từ rác từ điển ("sự...", "hành động...", "dạng...").
- Từ `support` bắt buộc có nghĩa chính `answer: "hỗ trợ"` và aliases chứa `"ủng hộ"`.
- Giữ nguyên cơ chế ghi đè `tools/meaning_overrides.json` và loại trừ `excluded-words.json`.
- `dist/words.js` xuất `WORD_SET_ID` (12 ký tự hex SHA-256) và mảng `WORDS`.

## Review Focus

1. **Từ có dấu gạch nối hoặc khoảng trắng lọt vào kho từ**: Người chơi không thể gõ được từ ghép trên TikTok LIVE $\rightarrow$ Bắt buộc regex `^[a-z]{2,16}$` loại bỏ hoàn toàn trước khi dịch.
2. **Nghĩa tiếng Việt quá dài làm tràn ô hiển thị**: Gây vỡ layout hoặc khó đọc trên mobile $\rightarrow$ Giới hạn độ dài $\le 30$ ký tự và kiểm định tự động co chữ trong `fitLayout()`.
3. **Mất phiên âm IPA hoặc phiên âm không chuẩn**: Làm hỏng giao diện đáp án $\rightarrow$ Kiểm định chặt `phonetic.startswith('/') and phonetic.endswith('/')`.
4. **Tràn bộ nhớ RAM hoặc chậm Node.js khi nạp 20.000 từ**: Kiểm tra memory footprint của `bridge.mjs` với 20.000 phần tử đảm bảo $< 30\text{ MB}$.
5. **Mất đồng bộ giữa server và client khi đổi kho từ**: `WORD_SET_ID` phải phản ánh chính xác nội dung 20.000 từ để client cảnh báo reload khi cần.

---

### Task 1: Sửa ngay từ "support" thành "hỗ trợ" và kiểm thử hồi quy

**Files:**
- Modify: `tools/curated_words.json`
- Modify: `tools/quiz_words.tsv`
- Test: `tests/test_support_word.py`

**Interfaces:**
- Consumes: `tools/curated_words.json`, `tools/quiz_words.tsv`
- Produces: `tools/curated_words.json` với `support` có `answer: "hỗ trợ"`, `aliases: ["ủng hộ"]`

- [ ] **Step 1: Viết test kiểm tra từ "support" trong curated_words và quiz_words**

Tạo `tests/test_support_word.py`:
```python
import json
import unittest
from pathlib import Path

class TestSupportWord(unittest.TestCase):
    def test_support_meaning(self):
        root = Path(__file__).resolve().parents[1]
        curated = json.loads((root / "tools" / "curated_words.json").read_text(encoding="utf-8"))
        support_entry = next((item for item in curated if item["word"] == "support"), None)
        self.assertIsNotNone(support_entry, "Từ support phải tồn tại trong curated_words.json")
        self.assertEqual(support_entry["answer"], "hỗ trợ", "Nghĩa chính của support phải là 'hỗ trợ'")
        self.assertIn("ủng hộ", support_entry.get("aliases", []), "Aliases của support phải chứa 'ủng hộ'")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test để xác nhận test thất bại (Red)**

Run: `python -m unittest tests/test_support_word.py`
Expected: FAIL với assertion `'ủng hộ' != 'hỗ trợ'`.

- [ ] **Step 3: Cập nhật nghĩa của từ "support" trong `tools/curated_words.json` và `tools/quiz_words.tsv`**

Sửa mục `support` trong `tools/curated_words.json`:
```json
{
  "word": "support",
  "phonetic": "/sə.ˈpɔrt/",
  "answer": "hỗ trợ",
  "aliases": [
    "ủng hộ",
    "giúp đỡ"
  ]
}
```
Cập nhật dòng `support` trong `tools/quiz_words.tsv` thành `support\thỗ trợ|ủng hộ|giúp đỡ`.
Chạy `python tools/build_dictionary.py` để cập nhật `dist/words.js`.

- [ ] **Step 4: Chạy test để xác nhận test thành công (Green)**

Run: `python -m unittest tests/test_support_word.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_support_word.py tools/curated_words.json tools/quiz_words.tsv dist/words.js
git commit -m "fix: change support primary meaning to ho tro"
```

---

### Task 2: Module trích xuất 20.000 từ đơn tiếng Anh ứng viên (`extract_candidates.py`)

**Files:**
- Create: `tools/extract_candidates.py`
- Test: `tests/test_extract_candidates.py`

**Interfaces:**
- Consumes: `tools/dictionary-source.db` (SQLite DB), `wordfreq`
- Produces: `tools/candidates_20k.json` (Danh sách 20.000 từ đơn có `word`, `phonetic`, `frequency`)

- [ ] **Step 1: Viết test cho logic trích xuất ứng viên**

Tạo `tests/test_extract_candidates.py`:
```python
import json
import re
import unittest
from pathlib import Path

class TestExtractCandidates(unittest.TestCase):
    def test_candidate_properties(self):
        root = Path(__file__).resolve().parents[1]
        candidate_file = root / "tools" / "candidates_20k.json"
        self.assertTrue(candidate_file.exists(), "Tệp candidates_20k.json phải được tạo")
        
        candidates = json.loads(candidate_file.read_text(encoding="utf-8"))
        self.assertEqual(len(candidates), 20000, "Phải trích xuất đúng 20.000 từ")
        
        words = [c["word"] for c in candidates]
        self.assertEqual(len(words), len(set(words)), "Không được có từ trùng lặp")
        
        single_word_pattern = re.compile(r"^[a-z]{2,16}$")
        for c in candidates[:500]:  # Kiểm tra mẫu 500 từ đầu
            self.assertTrue(single_word_pattern.fullmatch(c["word"]), f"Từ không hợp lệ: {c['word']}")
            self.assertTrue(c["phonetic"].startswith("/") and c["phonetic"].endswith("/"), f"IPA không hợp lệ: {c['word']}")
            self.assertGreaterEqual(c["frequency"], 0.0)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test để xác nhận thất bại trước khi implement**

Run: `python -m unittest tests/test_extract_candidates.py`
Expected: FAIL vì `tools/candidates_20k.json` chưa tồn tại.

- [ ] **Step 3: Xây dựng `tools/extract_candidates.py`**

Tạo `tools/extract_candidates.py`:
- Kết nối `tools/dictionary-source.db`.
- Truy vấn tất cả các từ `w.lang_code = 'en'` có `p.ipa` bắt đầu và kết thúc bằng `/`.
- Lọc theo regex `^[a-z]{2,16}$`.
- Tính tần suất `wordfreq.zipf_frequency(word, 'en')`.
- Sắp xếp giảm dần theo tần suất.
- Lấy top 20.000 từ duy nhất, ghi ra `tools/candidates_20k.json`.

Chạy:
```bash
python tools/extract_candidates.py
```

- [ ] **Step 4: Chạy test để xác nhận trích xuất thành công**

Run: `python -m unittest tests/test_extract_candidates.py`
Expected: PASS (20.000 từ đơn hợp lệ, không trùng lặp, IPA chuẩn).

- [ ] **Step 5: Commit**

```bash
git add tools/extract_candidates.py tests/test_extract_candidates.py tools/candidates_20k.json
git commit -m "feat: extract 20k single English candidate words with IPA"
```

---

### Task 3: Pipeline AI Dịch & Tự nhiên hóa Nghĩa Tiếng Việt (`generate_natural_meanings.py`)

**Files:**
- Create: `tools/generate_natural_meanings.py`
- Test: `tests/test_natural_meanings.py`

**Interfaces:**
- Consumes: `tools/candidates_20k.json`, `tools/curated_words.json` (làm baseline/few-shot)
- Produces: `tools/curated_words_20k.json` (mảng 20.000 từ gồm `word`, `phonetic`, `answer`, `aliases`)

- [ ] **Step 1: Viết test cho bộ lọc và chất lượng dữ liệu dịch tự nhiên**

Tạo `tests/test_natural_meanings.py`:
```python
import json
import re
import unittest
from pathlib import Path

class TestNaturalMeanings(unittest.TestCase):
    def test_curated_structure_and_quality(self):
        root = Path(__file__).resolve().parents[1]
        target_file = root / "tools" / "curated_words_20k.json"
        self.assertTrue(target_file.exists(), "Tệp curated_words_20k.json phải tồn tại")
        
        items = json.loads(target_file.read_text(encoding="utf-8"))
        self.assertEqual(len(items), 20000, "Phải có đúng 20.000 từ đã được tạo nghĩa")
        
        junk_pattern = re.compile(r"^(sự|hành động|dạng quá khứ|từ viết tắt)\b", re.I)
        for item in items:
            word = item["word"]
            answer = item["answer"]
            aliases = item.get("aliases", [])
            
            self.assertTrue(len(answer) <= 30, f"Nghĩa quá dài: {word}: {answer}")
            self.assertFalse(junk_pattern.search(answer), f"Nghĩa dính từ rác từ điển: {word}: {answer}")
            self.assertFalse("(" in answer or ")" in answer, f"Nghĩa dính dấu ngoặc đơn: {word}: {answer}")
            
            for alias in aliases:
                self.assertTrue(len(alias) <= 30, f"Alias quá dài: {word}: {alias}")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test để xác nhận thất bại trước khi sinh dữ liệu**

Run: `python -m unittest tests/test_natural_meanings.py`
Expected: FAIL vì `tools/curated_words_20k.json` chưa tồn tại.

- [ ] **Step 3: Xây dựng pipeline `tools/generate_natural_meanings.py`**

- Tích hợp 149 từ đã biên tập chuẩn từ `tools/curated_words.json` làm hạt giống (đã có `support` $\rightarrow$ "hỗ trợ").
- Lấy định nghĩa gốc từ `tools/dictionary-source.db` làm ngữ cảnh tham khảo ban đầu.
- Xử lý làm sạch tự nhiên:
  - Bóc tách nghĩa khẩu ngữ cốt lõi nhất.
  - Loại bỏ các hậu tố/tiền tố giải nghĩa của từ điển cũ.
  - Tách các từ đồng nghĩa ngắn gọn vào `aliases`.
  - Có checkpoint lưu tiến trình `tools/curated_words_20k.json`.
- Chạy hoàn tất sinh đủ 20.000 từ.

- [ ] **Step 4: Chạy test kiểm tra toàn bộ 20.000 từ**

Run: `python -m unittest tests/test_natural_meanings.py`
Expected: PASS (20.000 từ đạt chuẩn tự nhiên, không rác từ điển).

- [ ] **Step 5: Commit**

```bash
git add tools/generate_natural_meanings.py tests/test_natural_meanings.py tools/curated_words_20k.json
git commit -m "feat: generate 20k natural colloquial Vietnamese vocabulary set"
```

---

### Task 4: Kiểm định & Đóng gói từ điển vào Game (`build_dictionary.py`)

**Files:**
- Modify: `tools/build_dictionary.py`
- Test: `tests/test_build_dictionary.py`
- Output: `dist/words.js`

**Interfaces:**
- Consumes: `tools/curated_words_20k.json`, `tools/meaning_overrides.json`
- Produces: `dist/words.js` (xuất `WORD_SET_ID` và `WORDS` 20.000 từ)

- [ ] **Step 1: Viết test cho quy trình build từ điển 20.000 từ**

Tạo `tests/test_build_dictionary.py`:
```python
import hashlib
import json
import re
import unittest
from pathlib import Path

class TestBuildDictionary(unittest.TestCase):
    def test_words_js_output(self):
        root = Path(__file__).resolve().parents[1]
        words_js = root / "dist" / "words.js"
        self.assertTrue(words_js.exists(), "dist/words.js phải tồn tại")
        
        content = words_js.read_text(encoding="utf-8")
        self.assertIn("export const WORD_SET_ID=", content)
        self.assertIn("export const WORDS=", content)
        
        # Trích xuất JSON mảng WORDS
        match = re.search(r"export const WORDS=(\[.*?\]);\s*$", content, re.DOTALL)
        self.assertIsNotNone(match, "Phải tìm thấy mảng WORDS xuất khẩu")
        words = json.loads(match.group(1))
        self.assertEqual(len(words), 20000, "dist/words.js phải chứa đúng 20.000 từ")
        
        # Kiểm tra từ support
        support = next((w for w in words if w["word"] == "support"), None)
        self.assertIsNotNone(support)
        self.assertEqual(support["answer"], "hỗ trợ")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy test để xác nhận thất bại với dist/words.js cũ**

Run: `python -m unittest tests/test_build_dictionary.py`
Expected: FAIL vì `dist/words.js` hiện tại chỉ có 149 từ.

- [ ] **Step 3: Cập nhật `tools/build_dictionary.py` để nạp 20.000 từ và build ra `dist/words.js`**

Cập nhật `source = root / "tools" / "curated_words_20k.json"` trong `build_dictionary.py`.
Cập nhật regex kiểm tra từ đơn `re.fullmatch(r"[a-z]{2,16}", word)`.
Áp dụng `meaning_overrides.json`.
Tính mã băm `WORD_SET_ID` SHA-256 từ 20.000 từ.
Ghi ra `dist/words.js`.
Chạy: `python tools/build_dictionary.py`.

- [ ] **Step 4: Chạy test để xác nhận build thành công**

Run: `python -m unittest tests/test_build_dictionary.py`
Expected: PASS (20.000 từ, `WORD_SET_ID` mới, `support` = "hỗ trợ").

- [ ] **Step 5: Commit**

```bash
git add tools/build_dictionary.py tests/test_build_dictionary.py dist/words.js
git commit -m "feat: build dist/words.js with 20k natural single words"
```

---

### Task 5: Kiểm thử Tích hợp Toàn diện Game (`bridge.mjs` & `dist/index.html`)

**Files:**
- Test: `tests/test_game_integration.mjs`
- Test: `tests/test_e2e_quiz.py`

**Interfaces:**
- Consumes: `dist/words.js`, `bridge.mjs`, `dist/index.html`
- Produces: Báo cáo kiểm thử tích hợp toàn diện

- [ ] **Step 1: Viết test kiểm tra nạp bộ từ trong Node.js (`bridge.mjs` runtime)**

Tạo `tests/test_game_integration.mjs`:
```javascript
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
  assert.ok(item.word && item.answer && item.phonetic);
  sampleWords.add(item.word);
}
assert.ok(sampleWords.size > 5000, 'Độ phân tán ngẫu nhiên phải tốt');

// Kiểm tra memory usage
const mem = process.memoryUsage().heapUsed / 1024 / 1024;
console.log(`Node.js heap used with 20k words: ${mem.toFixed(2)} MB`);
assert.ok(mem < 50, 'Bộ nhớ heap phải dưới 50MB');
console.log('Node.js integration check passed successfully!');
```

- [ ] **Step 2: Chạy kiểm tra Node.js runtime**

Run: `node tests/test_game_integration.mjs`
Expected: PASS (Node.js nạp 20.000 từ trong chưa đầy 20MB heap, bốc ngẫu nhiên trơn tru).

- [ ] **Step 3: Viết test tổng kiểm định toàn bộ kho từ và giao diện**

Tạo `tests/test_e2e_quiz.py`:
- Kiểm tra tính toàn vẹn của `curated_words_20k.json` và `dist/words.js`.
- Kiểm tra không có từ nào có dấu gạch ngang hoặc khoảng trắng.
- Kiểm tra các từ nhạy cảm như `support` mang nghĩa "hỗ trợ".
- Kiểm tra `package.json` và `bridge.mjs` khởi động được bằng child process.

- [ ] **Step 4: Chạy test tổng**

Run: `python -m unittest tests/test_e2e_quiz.py`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_game_integration.mjs tests/test_e2e_quiz.py
git commit -m "test: add integration test suite for 20k natural words quiz"
```
