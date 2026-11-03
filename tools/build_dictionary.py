"""Build all playable English/Vietnamese quiz entries from minhqnd/dictionary v2.0.0.

Run: python tools/build_dictionary.py path/to/dictionary.db
"""
import json
import re
import sqlite3
import sys
from pathlib import Path
from wordfreq import zipf_frequency

root = Path(__file__).resolve().parents[1]
db = sqlite3.connect(sys.argv[1])
output = root / "dist" / "words.js"

# Keep the manually checked meanings and pronunciation fixes for the original set.
original = json.loads((root / "tools" / "curated_words.json").read_text(encoding="utf-8"))
entries = {item["word"]: item for item in original if isinstance(item, dict)}
skip_definition = re.compile(
    r"^(?:xem|số nhiều|quá khứ|động từ chia|dạng|viết tắt|từ viết tắt|"
    r"so sánh|tiền tố|hậu tố|thì|ngôi thứ|biến thể|lối viết|cách viết|"
    r"phiên âm|tham khảo|của từ|tên khoa học|cũng|như|một dạng)\b",
    re.I,
)
valid_word = re.compile(r"[A-Za-z]+(?:[ -][A-Za-z]+)*\Z")


def playable_answer(value):
    value = value.strip(" .;:!?-\"'")
    words = value.split()
    if not value or len(value) > 24 or len(words) > 4 or any(len(w) > 12 for w in words):
        return None
    if re.search(r"\d|[A-Za-z]{12,}", value) or not any(ord(c) > 127 for c in value):
        return None
    return value.casefold()


pronunciations = {}
for word, ipa in db.execute("""select w.word, p.ipa from words w
    join pronunciations p on p.word_id = w.id
    where w.lang_code = 'en' order by p.id"""):
    if word not in pronunciations and ipa.startswith("/") and ipa.endswith("/") and not ipa.startswith("/.") and len(ipa) < 90:
        pronunciations[word] = ipa

for word, definition in db.execute("""select w.word, d.definition from words w
    join word_definitions wd on wd.word_id = w.id
    join definitions d on d.id = wd.definition_id
    where w.lang_code = 'en' and d.definition_lang = 'vi'
    order by wd.id"""):
    if word in entries or word not in pronunciations or not 2 <= len(word) <= 20 or not valid_word.fullmatch(word) or zipf_frequency(word, "en") < 1.5:
        continue
    definition = re.sub(r"\[[^]]*\]|\([^)]*\)", "", definition).split("(", 1)[0].strip()
    if skip_definition.match(definition):
        continue
    first_sentence = definition.split(".", 1)[0].split(";", 1)[0]
    answers = []
    for phrase in first_sentence.split(",")[:5]:
        answer = playable_answer(phrase)
        if answer and answer not in answers:
            answers.append(answer)
    if not answers:
        continue
    entries[word] = {"word": word, "phonetic": pronunciations[word], "answer": answers[0], "aliases": answers[1:4]}

items = list(entries.values())
output.write_text(
    "// Derived from minhqnd/dictionary v2.0.0, CC BY-SA 4.0.\n"
    "export const WORDS=" + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
print(f"Wrote {len(items):,} playable words to {output}.")
