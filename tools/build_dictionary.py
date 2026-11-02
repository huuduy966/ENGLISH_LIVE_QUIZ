"""Build quiz entries from minhqnd/dictionary release v2.0.0.

Run: python tools/build_dictionary.py path/to/dictionary.db
"""
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

root = Path(__file__).resolve().parents[1]
db = sqlite3.connect(sys.argv[1])
entries = []
missing = []
# Some source IPA rows are missing or truncated; verified against Cambridge Dictionary.
ipa_overrides = {
    "careful": "/ˈker.fəl/",
    "sunshine": "/ˈsʌn.ʃaɪn/",
    "orange": "/ˈɔːr.ɪndʒ/",
    "tomato": "/təˈmeɪ.t̬oʊ/",
    "neighbor": "/ˈneɪ.bɚ/",
    "pencil": "/ˈpen.səl/",
    "read": "/riːd/",
    "begin": "/bɪˈɡɪn/",
}

def normalize(text):
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " ".join(re.findall(r"[a-z0-9]+", text))

for line in (root / "tools" / "quiz_words.tsv").read_text(encoding="utf-8").splitlines():
    if not line or line.startswith("#"):
        continue
    word, answers = line.split("\t")
    answer, *aliases = answers.split("|")
    rows = db.execute("""select d.definition from words w
        join word_definitions wd on wd.word_id = w.id
        join definitions d on d.id = wd.definition_id
        where w.word = ? and w.lang_code = 'en' and d.definition_lang = 'vi'""", (word,)).fetchall()
    definitions = [" " + normalize(row[0]) + " " for row in rows]
    if not any(" " + normalize(answer) + " " in definition for definition in definitions):
        missing.append(word)
        continue
    ipa = db.execute("""select p.ipa from words w join pronunciations p on p.word_id = w.id
        where w.word = ? and w.lang_code = 'en' and p.ipa like '/%/'
        order by p.id limit 1""", (word,)).fetchone()
    entries.append({"word": word, "phonetic": ipa_overrides.get(word, ipa[0] if ipa else ""), "answer": answer, "aliases": aliases})

assert len(entries) >= 80, f"Only {len(entries)} verified entries; missing: {missing}"
assert all(entry["phonetic"] and not entry["phonetic"].startswith("/.") for entry in entries)
(root / "dist" / "words.js").write_text(
    "// Derived from minhqnd/dictionary v2.0.0, CC BY-SA 4.0.\nexport const WORDS=" + json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + ";\n",
    encoding="utf-8",
)
print(f"Wrote {len(entries)} verified words. Unmatched: {', '.join(missing) or 'none'}")
