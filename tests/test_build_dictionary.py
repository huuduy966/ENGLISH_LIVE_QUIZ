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

        match = re.search(r"export const WORDS=(\[.*?\]);\s*$", content, re.DOTALL)
        self.assertIsNotNone(match, "Phải tìm thấy mảng WORDS xuất khẩu")
        words = json.loads(match.group(1))
        self.assertEqual(len(words), 20000, "dist/words.js phải chứa đúng 20.000 từ")

        # Kiểm tra từ support
        support = next((w for w in words if w["word"] == "support"), None)
        self.assertIsNotNone(support)
        self.assertEqual(support["answer"], "hỗ trợ")
        self.assertIn("ủng hộ", support.get("aliases", []))

if __name__ == "__main__":
    unittest.main()
