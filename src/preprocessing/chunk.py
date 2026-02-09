# chunk.py
import json
from pathlib import Path

# ---------- CONFIG ----------
TICKER = "AAPL"
YEAR = 2025
ITEM_NAME = "Item 7 - MD&A"
CHUNK_SIZE = 500  # broj reči po chunku
MIN_WORDS = 50    # minimalan broj reči da chunk bude validan

# Automatski određuje koren projekta (Market-Analyzer)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = BASE_DIR / f"data/processed/{TICKER}/10K/{TICKER.lower()}-{YEAR}0927_items.json"
OUTPUT_DIR = BASE_DIR / f"data/processed/{TICKER}/chunks"



# ---------- HELPERS ----------
def chunk_text(text: str, chunk_size: int):
    """Break text into chunks of ~chunk_size words"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk_words = words[i:i + chunk_size]
        if len(chunk_words) >= MIN_WORDS:
            chunks.append(" ".join(chunk_words))
    return chunks

def clean_item7_text(text: str):
    """Remove empty lines, short placeholders, repeated headers etc."""
    lines = text.split("\n")
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if len(line.split()) < 5:
            continue  # preskoči kratke naslove
        clean_lines.append(line)
    return "\n".join(clean_lines)

# ---------- MAIN ----------
def main():
    # Napravi folder ako ne postoji
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Učitaj JSON fajl sa Itemima
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Proveri da li postoji Item 7
    if ITEM_NAME not in items:
        print(f"❌ {ITEM_NAME} not found in {INPUT_FILE}")
        return

    text = items[ITEM_NAME]
    text = clean_item7_text(text)
    print("Raw Item 7 length (chars):", len(text))
    print("Raw Item 7 preview:\n", text[:500])
    chunks = chunk_text(text, CHUNK_SIZE)

    if not chunks:
        print(f"❌ No valid chunks generated for {ITEM_NAME}")
        return

    # Spremi chunkove
    chunk_data = []
    for idx, chunk in enumerate(chunks):
        chunk_data.append({
            "ticker": TICKER,
            "year": YEAR,
            "item": ITEM_NAME,
            "chunk_id": idx,
            "text": chunk
        })

    output_file = OUTPUT_DIR / f"{TICKER.lower()}-{YEAR}_item7_chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunk_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Chunking done! {len(chunks)} chunks saved to {output_file}")


if __name__ == "__main__":
    main()
