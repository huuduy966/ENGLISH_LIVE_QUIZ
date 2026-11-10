"""Generate 20,000 natural colloquial Vietnamese vocabulary entries using batch translation.

Usage: python tools/generate_natural_meanings.py
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parents[1]
candidates_path = root / "tools" / "candidates_20k.json"
curated_path = root / "tools" / "curated_words.json"
overrides_path = root / "tools" / "meaning_overrides.json"
cache_path = root / "tools" / "translation_cache_20k.json"
output_path = root / "tools" / "curated_words_20k.json"

if not candidates_path.exists():
    raise FileNotFoundError(f"Candidates file not found at {candidates_path}")

candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
curated_list = json.loads(curated_path.read_text(encoding="utf-8"))
overrides = json.loads(overrides_path.read_text(encoding="utf-8"))

curated_map = {item["word"]: item for item in curated_list}

# Load or initialize translation cache
cache = {}
if cache_path.exists():
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        print(f"Loaded {len(cache)} cached translations.")
    except Exception:
        cache = {}

words_to_translate = [c["word"] for c in candidates if c["word"] not in cache]
print(f"Need to translate {len(words_to_translate)} words...")

batch_size = 80
clean_junk_prefix = re.compile(r"^(?:sự|việc|hành động|tính chất|tính|lối|thói)\s+", re.I)

for i in range(0, len(words_to_translate), batch_size):
    batch = words_to_translate[i : i + batch_size]
    batch_text = "\n".join(batch)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t&q={urllib.parse.quote(batch_text)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    success = False
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                full_trans = "".join(segment[0] for segment in data[0])
                lines = [line.strip() for line in full_trans.split("\n")]
                # Handle possible line count mismatch
                if len(lines) == len(batch):
                    for w, t in zip(batch, lines):
                        cache[w] = t
                else:
                    # Fallback single word if count mismatches
                    for w in batch:
                        single_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=vi&dt=t&q={urllib.parse.quote(w)}"
                        sreq = urllib.request.Request(single_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(sreq, timeout=5) as sresp:
                            sdata = json.loads(sresp.read().decode("utf-8"))
                            cache[w] = sdata[0][0][0].strip()
                success = True
                break
        except Exception as e:
            time.sleep(1.0 * (attempt + 1))

    if (i // batch_size) % 10 == 0 or i + batch_size >= len(words_to_translate):
        print(f"Progress: {min(i + batch_size, len(words_to_translate))}/{len(words_to_translate)} words translated.")
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")

    time.sleep(0.08)

# Save final cache
cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
print("All translations completed.")

# Build final natural vocabulary list
SPECIFIC_OVERRIDES = {
    "act": ("diễn xuất", ["hành động", "diễn"]),
    "action": ("hoạt động", ["hành động"]),
    "actions": ("hoạt động", []),
    "acronym": ("viết tắt", ["từ viết tắt"]),
    "zionist": ("người phục quốc", ["phục quốc do thái"]),
    "anarchist": ("người vô chính phủ", []),
    "impressionist": ("phái ấn tượng", []),
    "globalist": ("người toàn cầu hóa", []),
    "traditionalist": ("người truyền thống", []),
    "expansionist": ("người bành trướng", []),
}

def clean_meaning(text):
    text = text.strip(" .;:!?-\"'")
    text = clean_junk_prefix.sub("", text).strip()
    if "(" in text:
        text = re.sub(r"\(.*?\)", "", text).strip()
    if len(text) > 30 and "," in text:
        text = text.split(",")[0].strip()
    if len(text) > 30 and " người theo chủ nghĩa " in text:
        text = text.replace(" người theo chủ nghĩa ", " người ").strip()
    if len(text) > 30:
        words = text.split()
        text = " ".join(words[:4])
    return text.lower()


def make_aliases(word, answer):
    aliases = []
    # Classifiers: 'cái ghế' -> 'ghế', 'con mèo' -> 'mèo', 'quả táo' -> 'táo'
    for prefix in ["cái ", "con ", "quả ", "trái ", "ngôi ", "ngọn ", "cuốn ", "quyển ", "chiếc ", "bức "]:
        if answer.startswith(prefix):
            short = answer[len(prefix) :].strip()
            if short and short != answer and short not in aliases:
                aliases.append(short)

    if word == "support":
        for a in ["ủng hộ", "giúp đỡ"]:
            if a != answer and a not in aliases:
                aliases.append(a)
    elif word in curated_map:
        for a in curated_map[word].get("aliases", []):
            a_clean = clean_meaning(a)
            if a_clean and a_clean != answer and a_clean not in aliases and len(a_clean) <= 20:
                aliases.append(a_clean)
    return aliases[:3]


final_items = []
for c in candidates:
    w = c["word"]
    ipa = c["phonetic"]

    # 0. Specific clean overrides
    if w in SPECIFIC_OVERRIDES:
        ans, als = SPECIFIC_OVERRIDES[w]
    # 1. Overrides take precedence
    elif w in overrides:
        ans = clean_meaning(overrides[w])
        als = make_aliases(w, ans)
    # 2. Curated words baseline
    elif w in curated_map:
        ans = clean_meaning(curated_map[w]["answer"])
        als = make_aliases(w, ans)
    # 3. Translated meaning
    else:
        raw_trans = cache.get(w, "")
        ans = clean_meaning(raw_trans)
        if not ans or not re.fullmatch(r"[^\W\d_]+(?:[ -][^\W\d_]+)*", ans):
            defs = c.get("definitions", [])
            ans = clean_meaning(defs[0]) if defs else w
            if not ans or not re.fullmatch(r"[^\W\d_]+(?:[ -][^\W\d_]+)*", ans):
                ans = w
        als = make_aliases(w, ans)

    final_items.append({
        "word": w,
        "phonetic": ipa,
        "answer": ans,
        "aliases": als
    })

print(f"Generated {len(final_items)} final entries.")

output_path.write_text(
    json.dumps(final_items, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Saved to {output_path}.")
