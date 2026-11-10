"""Generate 20,000 natural colloquial Vietnamese vocabulary entries.

Usage: python tools/generate_natural_meanings.py
"""
import json
import re
import sqlite3
from pathlib import Path
import wordfreq

root = Path(__file__).resolve().parents[1]
db_path = root / "tools" / "dictionary-source.db"
curated_source = root / "tools" / "curated_words.json"
overrides_path = root / "tools" / "meaning_overrides.json"
output_path = root / "tools" / "curated_words_20k.json"

if not db_path.exists():
    raise FileNotFoundError(f"Database not found at {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

word_pattern = re.compile(r"^[a-z]{2,16}$")
skip_prefix = re.compile(
    r"^(?:xem|số nhiều|quá khứ|động từ|dạng|viết tắt|từ viết tắt|so sánh|tiền tố|hậu tố|thì|ngôi|biến thể|cách viết|phiên âm|tham khảo|của từ|tên khoa học|như|cũng như)\b",
    re.I,
)
clean_paren = re.compile(r"\([^)]*\)|\[[^]]*\]|\{[^}]*\}")
clean_junk_prefix = re.compile(r"^(?:sự|việc|hành động|tính chất|tính|lối|thói)\s+", re.I)
junk_pattern = re.compile(r"^(?:sự|hành động|dạng quá khứ|từ viết tắt)\b", re.I)
junk_standalone = {"sự", "việc", "hành động", "tính chất", "tính", "dạng", "lối", "thói"}


def extract_clean_phrases(raw_defs):
    found = []
    for d in raw_defs:
        d = clean_paren.sub("", d).strip()
        for sentence in re.split(r"[.;\n]+", d):
            sentence = sentence.strip()
            if not sentence or skip_prefix.match(sentence):
                continue
            for phrase in re.split(r"[,/]+", sentence):
                phrase = phrase.strip(" .;:!?-\"'")
                cleaned = clean_junk_prefix.sub("", phrase).strip()
                for p in [cleaned, phrase]:
                    if (
                        p
                        and p.lower() not in junk_standalone
                        and not clean_junk_prefix.match(p)
                        and not junk_pattern.search(p)
                        and 1 <= len(p) <= 25
                        and len(p.split()) <= 4
                        and re.fullmatch(r"[^\W\d_]+(?:[ -][^\W\d_]+)*", p)
                    ):
                        p_lower = p.lower()
                        if p_lower not in found:
                            found.append(p_lower)
    return found


print("Querying dictionary-source.db for English words, IPA and definitions...")
query = """
    SELECT lower(w.word), p.ipa, d.definition
    FROM words w
    JOIN pronunciations p ON p.word_id = w.id
    JOIN word_definitions wd ON wd.word_id = w.id
    JOIN definitions d ON d.id = wd.definition_id
    WHERE w.lang_code = 'en' AND d.definition_lang = 'vi' AND p.ipa LIKE '/%/'
"""

words_found = {}
for w, ipa, defn in cursor.execute(query):
    if word_pattern.fullmatch(w) and ipa.startswith("/") and ipa.endswith("/") and len(ipa) < 80:
        if w not in words_found:
            words_found[w] = {"ipa": ipa, "defs": []}
        if len(words_found[w]["defs"]) < 6:
            words_found[w]["defs"].append(defn)

curated_list = json.loads(curated_source.read_text(encoding="utf-8"))
overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

candidates = []
seen = set()

# 1. Incorporate hand-curated baseline entries
for item in curated_list:
    w = item["word"]
    seen.add(w)
    ans = overrides.get(w, item["answer"])
    # Clean answer and aliases if needed
    if junk_pattern.search(ans):
        ans = clean_junk_prefix.sub("", ans).strip()
    raw_aliases = [] if w in overrides else item.get("aliases", [])
    aliases = [
        clean_junk_prefix.sub("", a).strip()
        for a in raw_aliases
        if not junk_pattern.search(clean_junk_prefix.sub("", a).strip())
    ]
    candidates.append({
        "word": w,
        "phonetic": item["phonetic"],
        "answer": ans,
        "aliases": [a for a in aliases if a and a != ans]
    })

# 2. Extract and score definitions from SQLite database
db_candidates = []
for w, data in words_found.items():
    if w in seen:
        continue
    phrases = extract_clean_phrases(data["defs"])
    if phrases:
        freq = round(wordfreq.zipf_frequency(w, "en"), 2)
        # Prioritize phrases by frequency in Vietnamese (colloquial usage)
        phrases.sort(key=lambda p: -wordfreq.zipf_frequency(p, "vi"))
        ans = overrides.get(w, phrases[0])
        aliases = [] if w in overrides else [p for p in phrases[1:4] if p != ans]
        db_candidates.append({
            "word": w,
            "phonetic": data["ipa"],
            "answer": ans,
            "aliases": aliases,
            "frequency": freq
        })

# Sort by English frequency descending, then alphabetically
db_candidates.sort(key=lambda x: (-x["frequency"], x["word"]))

needed = 20000 - len(candidates)
for item in db_candidates[:needed]:
    candidates.append({
        "word": item["word"],
        "phonetic": item["phonetic"],
        "answer": item["answer"],
        "aliases": item["aliases"]
    })

print(f"Generated {len(candidates)} clean colloquial entries.")

output_path.write_text(
    json.dumps(candidates, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Wrote {len(candidates)} entries to {output_path}.")
