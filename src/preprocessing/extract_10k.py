import os
from pathlib import Path
from bs4 import BeautifulSoup
import json

# ----------------------------------
# CONFIG
# ----------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]  # ide do root projekta
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

def extract_text_from_10k(ticker: str, filename: str):
    raw_file = RAW_DATA_DIR / ticker / "10K" / filename
    if not raw_file.exists():
        print(f"❌ File not found: {raw_file}")
        return

    # Otvori HTML
    with open(raw_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Uzmi ceo tekst
    text = soup.get_text(separator="\n")

    # Folder za processed podatke
    save_dir = PROCESSED_DATA_DIR / ticker / "10K"
    save_dir.mkdir(parents=True, exist_ok=True)

    # Sačuvaj u JSON
    output_file = save_dir / f"{filename.replace('.htm','.json')}"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"text": text}, f, ensure_ascii=False, indent=2)

    print(f"✅ Extracted text saved to: {output_file}")
    return output_file

# ----------------------------------
# Primer pokretanja
# ----------------------------------
if __name__ == "__main__":
    ticker = "AAPL"
    filename = "aapl-20250927.htm"
    extract_text_from_10k(ticker, filename)
