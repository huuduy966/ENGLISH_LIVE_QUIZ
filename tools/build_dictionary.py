"""Build the quiz from the reviewed word list.

Run: python tools/build_dictionary.py
"""
import json
import hashlib
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / "tools" / "curated_words_20k.json"
if not source.exists():
    source = root / "tools" / "curated_words.json"
output = root / "dist" / "words.js"
items = json.loads(source.read_text(encoding="utf-8"))
overrides = json.loads((root / "tools" / "meaning_overrides.json").read_text(encoding="utf-8"))

if not items or len({item["word"] for item in items}) != len(items):
    raise ValueError("The reviewed word list is empty or contains duplicate English words")

for item in items:
    word = item["word"]
    answer = overrides.get(word, item["answer"])
    meanings = [answer, *item["aliases"]]
    if not re.fullmatch(r"^[a-z]{2,16}$", word) or any(
        len(value) > 40 or not re.fullmatch(r"[^\W\d_]+(?:[ -][^\W\d_]+)*", value)
        for value in meanings
    ):
        raise ValueError(f"Invalid quiz entry: {word}: {answer}")
    if not item["phonetic"].startswith("/") or not item["phonetic"].endswith("/"):
        raise ValueError(f"Missing pronunciation: {word}")
    item["answer"] = answer
    if word in overrides:
        item["aliases"] = []

output.write_text(
    "// Reviewed English/Vietnamese quiz words. Pronunciations from minhqnd/dictionary v2.0.0 (CC BY-SA 4.0).\n"
    "export const WORD_SET_ID=" + json.dumps(hashlib.sha256(",".join(item["word"] for item in items).encode()).hexdigest()[:12]) + ";\n"
    "export const WORDS=" + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
print(f"Wrote {len(items)} reviewed words to {output}.")
