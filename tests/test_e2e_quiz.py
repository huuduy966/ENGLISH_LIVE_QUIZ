import json
import re
import subprocess
import time
import urllib.request
import unittest
from pathlib import Path

class TestE2EQuiz(unittest.TestCase):
    def test_all_20k_words_are_single_words(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "tools" / "curated_words_20k.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data), 20000)

        single_word_pattern = re.compile(r"^[a-z]{2,16}$")
        for idx, item in enumerate(data):
            w = item["word"]
            self.assertTrue(single_word_pattern.fullmatch(w), f"Từ '{w}' không phải là từ đơn hợp lệ")
            self.assertTrue(item["phonetic"].startswith("/") and item["phonetic"].endswith("/"), f"IPA '{w}' không hợp lệ")
            self.assertTrue(1 <= len(item["answer"]) <= 35, f"Nghĩa '{w}' có độ dài không hợp lệ")

    def test_key_overrides_present(self):
        root = Path(__file__).resolve().parents[1]
        data = {w["word"]: w for w in json.loads((root / "tools" / "curated_words_20k.json").read_text(encoding="utf-8"))}

        self.assertIn("support", data)
        self.assertEqual(data["support"]["answer"], "hỗ trợ")
        self.assertIn("ủng hộ", data["support"]["aliases"])

        self.assertIn("company", data)
        self.assertEqual(data["company"]["answer"], "công ty")

        self.assertIn("application", data)
        self.assertEqual(data["application"]["answer"], "ứng dụng")

        self.assertIn("account", data)
        self.assertEqual(data["account"]["answer"], "tài khoản")

    def test_bridge_server_startup(self):
        root = Path(__file__).resolve().parents[1]
        env = {"PORT": "3098", "RELAY_PORT": "3099"}
        proc = subprocess.Popen(
            ["node", str(root / "bridge.mjs")],
            env=dict(**subprocess.os.environ, **env),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            time.sleep(1.2)
            # Test health or state on relayPort
            req = urllib.request.Request("http://127.0.0.1:3099/api/health")
            with urllib.request.urlopen(req, timeout=3) as res:
                self.assertEqual(res.status, 200)
                body = res.read().decode("utf-8")
                self.assertEqual(body, "ok")

            state_req = urllib.request.Request("http://127.0.0.1:3099/api/state")
            with urllib.request.urlopen(state_req, timeout=3) as res:
                self.assertEqual(res.status, 200)
                game_state = json.loads(res.read().decode("utf-8"))
                self.assertEqual(game_state["type"], "game")
                self.assertIsNotNone(game_state["clue"])
                self.assertIsNotNone(game_state["wordSetId"])
                self.assertEqual(len(game_state["wordSetId"]), 12)
        finally:
            proc.terminate()
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                proc.stderr.close()
            proc.wait(timeout=3)

if __name__ == "__main__":
    unittest.main()
