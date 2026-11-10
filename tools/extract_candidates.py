"""Extract top 20,000 single English candidate words with IPA and frequency.

Usage: python tools/extract_candidates.py
"""
import json
import re
import sqlite3
from pathlib import Path
import wordfreq

root = Path(__file__).resolve().parents[1]
db_path = root / "tools" / "dictionary-source.db"
output_path = root / "tools" / "candidates_20k.json"

if not db_path.exists():
    raise FileNotFoundError(f"Database not found at {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

word_pattern = re.compile(r"^[a-z]{2,16}$")

# 1. Fetch valid pronunciations
pronunciations = {}
for word, ipa in cursor.execute("""
    SELECT lower(w.word), p.ipa
    FROM words w
    JOIN pronunciations p ON p.word_id = w.id
    WHERE w.lang_code = 'en' AND p.ipa LIKE '/%/'
    ORDER BY p.id
"""):
    if (
        word not in pronunciations
        and word_pattern.fullmatch(word)
        and ipa.startswith("/")
        and ipa.endswith("/")
        and not ipa.startswith("/.")
        and len(ipa) < 80
    ):
        pronunciations[word] = ipa

print(f"Found {len(pronunciations)} single English words with valid IPA.")

# 2. Fetch raw Vietnamese definitions as context
word_definitions = {}
for word, definition in cursor.execute("""
    SELECT lower(w.word), d.definition
    FROM words w
    JOIN word_definitions wd ON wd.word_id = w.id
    JOIN definitions d ON d.id = wd.definition_id
    WHERE w.lang_code = 'en' AND d.definition_lang = 'vi'
    ORDER BY wd.id
"""):
    if word in pronunciations:
        if word not in word_definitions:
            word_definitions[word] = []
        if len(word_definitions[word]) < 6:
            word_definitions[word].append(definition)

# 3. Score words by Zipf frequency in English
candidates = []
for word, ipa in pronunciations.items():
    freq = round(wordfreq.zipf_frequency(word, "en"), 2)
    defs = word_definitions.get(word, [])
    candidates.append({
        "word": word,
        "phonetic": ipa,
        "frequency": freq,
        "definitions": defs
    })

# Sort descending by frequency, then alphabetically by word
candidates.sort(key=lambda item: (-item["frequency"], item["word"]))

top_20k = candidates[:20000]

output_path.write_text(
    json.dumps(top_20k, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Wrote {len(top_20k)} candidate words to {output_path}.")
