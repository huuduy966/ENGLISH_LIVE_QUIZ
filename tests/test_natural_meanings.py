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
        word_set = set()

        for item in items:
            word = item["word"]
            self.assertNotIn(word, word_set, f"Từ bị trùng lặp: {word}")
            word_set.add(word)

            answer = item["answer"]
            aliases = item.get("aliases", [])

            self.assertTrue(1 <= len(answer) <= 30, f"Nghĩa quá dài hoặc rỗng: {word}: {answer}")
            self.assertFalse(junk_pattern.search(answer), f"Nghĩa dính từ rác từ điển: {word}: {answer}")
            self.assertFalse("(" in answer or ")" in answer, f"Nghĩa dính dấu ngoặc đơn: {word}: {answer}")
            self.assertTrue(item["phonetic"].startswith("/") and item["phonetic"].endswith("/"), f"IPA không hợp lệ: {word}")

            for alias in aliases:
                self.assertTrue(len(alias) <= 30, f"Alias quá dài: {word}: {alias}")
                self.assertFalse("(" in alias or ")" in alias, f"Alias dính dấu ngoặc đơn: {word}: {alias}")

        # Kiểm tra từ support
        support = next((w for w in items if w["word"] == "support"), None)
        self.assertIsNotNone(support, "Phải có từ support trong kho 20.000 từ")
        self.assertEqual(support["answer"], "hỗ trợ", "support phải có answer là 'hỗ trợ'")
        self.assertIn("ủng hộ", support["aliases"], "support phải có alias 'ủng hộ'")

if __name__ == "__main__":
    unittest.main()
