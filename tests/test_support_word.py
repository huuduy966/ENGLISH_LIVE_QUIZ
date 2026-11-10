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
