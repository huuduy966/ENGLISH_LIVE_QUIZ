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
        self.assertIn("giúp đỡ", support_entry.get("aliases", []), "Aliases của support phải chứa 'giúp đỡ'")

    def test_support_tsv(self):
        root = Path(__file__).resolve().parents[1]
        tsv_lines = (root / "tools" / "quiz_words.tsv").read_text(encoding="utf-8").splitlines()
        support_line = next((line for line in tsv_lines if line.startswith("support\t")), None)
        self.assertIsNotNone(support_line, "Từ support phải tồn tại trong quiz_words.tsv")
        parts = support_line.split("\t")
        meanings = parts[1].split("|")
        self.assertEqual(meanings[0], "hỗ trợ", "Nghĩa chính trong TSV phải là 'hỗ trợ'")
        self.assertIn("ủng hộ", meanings, "Aliases trong TSV phải chứa 'ủng hộ'")
        self.assertIn("giúp đỡ", meanings, "Aliases trong TSV phải chứa 'giúp đỡ'")

    def test_support_in_dist_words(self):
        root = Path(__file__).resolve().parents[1]
        content = (root / "dist" / "words.js").read_text(encoding="utf-8")
        json_part = content.split("export const WORDS=")[1].rstrip(";\n")
        words = json.loads(json_part)
        support_entry = next((item for item in words if item["word"] == "support"), None)
        self.assertIsNotNone(support_entry, "Từ support phải tồn tại trong dist/words.js")
        self.assertEqual(support_entry["answer"], "hỗ trợ")
        self.assertIn("ủng hộ", support_entry.get("aliases", []))
        self.assertIn("giúp đỡ", support_entry.get("aliases", []))

if __name__ == "__main__":
    unittest.main()
