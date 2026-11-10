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
        for c in candidates[:500]:
            self.assertTrue(single_word_pattern.fullmatch(c["word"]), f"Từ không hợp lệ: {c['word']}")
            self.assertTrue(c["phonetic"].startswith("/") and c["phonetic"].endswith("/"), f"IPA không hợp lệ: {c['word']}")
            self.assertGreaterEqual(c["frequency"], 0.0)

if __name__ == "__main__":
    unittest.main()
