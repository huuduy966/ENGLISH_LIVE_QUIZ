# Thiết kế Đặc tả: Kho 20.000 Từ Đơn Tự Nhiên Cho English Live Quiz

- **Ngày tạo**: 2026-11-10
- **Trạng thái**: Đã phê duyệt ý tưởng, chuyển sang lập kế hoạch thực hiện
- **Mục tiêu**: Xây dựng kho từ vựng gồm 20.000 từ đơn tiếng Anh phổ biến nhất với định nghĩa tiếng Việt khẩu ngữ, tự nhiên và gần gũi với cách người Việt thực tế hiểu và sử dụng, thay thế các định nghĩa khô khan/sách vở của từ điển truyền thống.

---

## 1. Yêu cầu & Mục tiêu Thiết kế

### 1.1. Yêu cầu về Từ vựng Tiếng Anh
- **Chỉ sử dụng từ đơn (Single words only)**:
  - Định dạng bắt buộc: Regex `^[a-z]{2,16}$` (chỉ gồm các ký tự chữ cái thường `a-z`, độ dài 2-16 ký tự).
  - Tuyệt đối không chứa: khoảng trắng (space), dấu gạch nối (`-`), dấu gạch dưới (`_`), chữ số, từ ghép, phrasal verbs (*look up, give up*), hay danh từ ghép (*ice cream*).
- **Quy mô**: Đúng 20.000 từ đơn tiếng Anh thông dụng nhất, được sắp xếp và chọn lọc dựa trên tần suất Zipf của `wordfreq` (tiếng Anh) kết hợp dữ liệu phát âm IPA chuẩn xác từ `tools/dictionary-source.db`.
- **Phiên âm IPA**: Mỗi từ bắt buộc có phiên âm chuẩn quốc tế bao bọc trong hai dấu gạch chéo `/.../` (ví dụ: `/sə.ˈpɔrt/`).

### 1.2. Yêu cầu về Định nghĩa Tiếng Việt (Tự nhiên & Khẩu ngữ)
- **Nghĩa chính (`answer`)**:
  - Phải phản ánh đúng cách người Việt nói và hiểu trong đời sống thực tế hiện đại.
  - Ví dụ điển hình: `support` có nghĩa chính là **hỗ trợ** (thay vì "ủng hộ").
  - Ngắn gọn, súc tích (1-3 từ tiếng Việt, độ dài $\le 30$ ký tự) để người xem livestream dễ dàng nhận biết và gõ nhanh.
  - Loại bỏ hoàn toàn văn phong từ điển rườm rà: không có tiền tố *"sự...", "hành động...", "dạng quá khứ của...", "tính chất..."*, không chứa chú thích trong ngoặc đơn `(...)` hay dấu chấm phẩy.
- **Từ đồng nghĩa chấp nhận được (`aliases`)**:
  - Gồm 1-3 từ đồng nghĩa phổ biến trong tiếng Việt (ví dụ: `support` có aliases là `["ủng hộ", "giúp đỡ"]`).
  - Đảm bảo tính công bằng khi người chơi TikTok LIVE bình luận các từ ngữ tương đương.

### 1.3. Yêu cầu về Gameplay & Hiệu năng
- **Bốc ngẫu nhiên**: Trò chơi bốc ngẫu nhiên hoàn toàn trong toàn bộ kho 20.000 từ trong suốt buổi livestream, có cơ chế tránh lặp lại từ của vòng chơi liền kề.
- **Dung lượng & Tải**:
  - Tệp `dist/words.js` chứa 20.000 từ có dung lượng $\approx 1.8\text{ MB} - 2.0\text{ MB}$.
  - Node.js (`bridge.mjs`) nạp 20.000 từ vào RAM chiếm $< 20\text{ MB}$.
  - Trình duyệt OBS Studio / TikTok LIVE Studio chỉ tải tệp 1 lần khi khởi động, hoạt động mượt mà không bị giật lag.
- **Cơ chế ghi đè trực tiếp & Đồng bộ**:
  - Vẫn giữ nguyên tính năng sửa nghĩa nhanh trên trang Admin qua `tools/meaning_overrides.json`.
  - Vẫn giữ nguyên tính năng "Bỏ từ khó" lưu vào `excluded-words.json`.
  - Tự động băm mã SHA-256 trên 20.000 từ để sinh `WORD_SET_ID`, đảm bảo tính toàn vẹn và cảnh báo lệch phiên bản giữa server và client.

---

## 2. Kiến trúc Hệ thống & Pipeline Xử lý Dữ liệu

```
[tools/dictionary-source.db] + [wordfreq (en)]
                    │
                    ▼
  1. Trích xuất ứng viên (tools/extract_candidates.py)
     - Lọc 20.000 từ đơn [a-z]{2,16} xếp theo tần suất Zipf
     - Trích xuất phiên âm IPA chuẩn từ SQLite DB
                    │
                    ▼
  2. Batch Processing & AI Naturalization (tools/generate_natural_meanings.py)
     - Gửi từng batch 50-100 từ kèm ngữ cảnh
     - Prompt AI chuyên biệt tạo nghĩa đời sống Việt Nam + aliases
     - Checkpoint định kỳ vào tools/curated_words_20k.json
                    │
                    ▼
  3. Kiểm định & Chuẩn hóa (Validation Guard trong build_dictionary.py)
     - Regex [a-z]+ cho word
     - Kiểm tra độ dài và chuẩn hóa ký tự tiếng Việt cho answer/aliases
     - Áp dụng overrides từ meaning_overrides.json
                    │
                    ▼
  4. Đóng gói & Phát hành Game (dist/words.js)
     - Sinh export const WORD_SET_ID = "hash_12_chars";
     - Sinh export const WORDS = [...20000 items...];
```

### 2.1. Tệp trích xuất ứng viên: `tools/extract_candidates.py`
- Kết nối `tools/dictionary-source.db`.
- Lấy toàn bộ từ tiếng Anh có phát âm IPA hợp lệ (bắt đầu và kết thúc bằng `/`, không bị lỗi chuỗi).
- Dùng `wordfreq.zipf_frequency(word, 'en')` để chấm điểm và sắp xếp giảm dần.
- Lọc theo regex `^[a-z]{2,16}$`.
- Lấy đúng 20.000 từ đơn có độ phổ biến cao nhất, lưu vào tệp tạm `tools/candidates_20k.json`.

### 2.2. Tệp AI dịch tự nhiên: `tools/generate_natural_meanings.py`
- Đọc danh sách từ `tools/candidates_20k.json`.
- Tận dụng 149 từ đã biên tập sẵn trong `tools/curated_words.json` làm chuẩn (few-shot examples), đồng thời sửa từ `support` thành nghĩa chính là "hỗ trợ".
- Chia batch 50–100 từ/lần, xử lý tuần tự hoặc song song an toàn, có lưu checkpoint `tools/curated_words_20k.json`.
- System Prompt yêu cầu:
  - Trả về đúng format JSON: `[{"word": "...", "phonetic": "...", "answer": "...", "aliases": [...]}]`.
  - Nghĩa phải là từ/cụm từ người Việt hay dùng hằng ngày.

### 2.3. Tệp đóng gói game: `tools/build_dictionary.py`
- Kiểm tra tính duy nhất (không trùng lặp từ tiếng Anh).
- Áp dụng đè các từ trong `tools/meaning_overrides.json`.
- Kiểm tra hợp lệ từng trường dữ liệu:
  - `re.fullmatch(r"^[a-z]{2,16}$", item["word"])`
  - `item["phonetic"].startswith("/") and item["phonetic"].endswith("/")`
  - `answer` và từng alias trong `aliases` không quá 30 ký tự và là chuỗi tiếng Việt hợp lệ.
- Băm SHA-256 xuất ra `dist/words.js`.

---

## 3. Tương thích với Backend & Frontend Hiện có

- **`bridge.mjs`**:
  - Không cần sửa đổi kiến trúc, `import { WORDS, WORD_SET_ID } from './dist/words.js'` vẫn hoạt động trong suốt.
  - Mảng `availableIndices` kích thước 20.000 phần tử chạy các phép toán `Math.random()`, `indexOf`, `splice` trong microsecond.
  - Cơ chế bắt bình luận và so khớp `normalize(word.word) === normalize(message)` giữ nguyên tốc độ tức thì.
- **`dist/index.html`**:
  - Tải `words.js` (1.8MB) trực tiếp qua `<script type="module">`.
  - Hàm `fitLayout()` tự động căn chỉnh cỡ chữ ô đáp án theo độ dài từ tiếng Anh (từ 2 đến 16 ký tự đều vừa vặn trên màn hình).

---

## 4. Kế hoạch Kiểm thử & Nghiệm thu (Verification & Testing)

1. **Kiểm tra Dữ liệu (Data Integrity Check)**:
   - Tổng số từ chính xác là 20.000.
   - Không có từ trùng lặp (`len(set(words)) == 20000`).
   - 100% từ tiếng Anh là từ đơn thuần túy `[a-z]{2,16}` (không có space, hyphen).
   - 100% từ có phiên âm IPA chuẩn dạng `^/.+/$`.
   - 100% nghĩa tiếng Việt không chứa từ rác từ điển ("sự", "hành động", dấu ngoặc).
   - Kiểm tra đặc thù từ `support`: `answer == "hỗ trợ"`, `aliases` chứa `"ủng hộ"`.
2. **Kiểm tra Hệ thống (System Run Check)**:
   - Chạy `python tools/build_dictionary.py` hoàn thành không lỗi.
   - Chạy `node bridge.mjs` khởi động thành công, tiêu thụ RAM $< 30\text{ MB}$.
   - Chạy thử vòng lặp game 10 vòng ngẫu nhiên, xác nhận câu hỏi và đáp án hiển thị chính xác.
   - Thử nghiệm chức năng "Sửa nghĩa" và "Bỏ từ khó" trong trang Admin.
