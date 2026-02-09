from pathlib import Path
import json
import re

# -------------------------------------------------
# CONFIG (prilagođeno tvojoj strukturi)
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
# Market-Analyzer/

TICKER = "AAPL"
FILING = "10K"
FILENAME = "aapl-20250927"

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / TICKER
    / FILING
    / f"{FILENAME}.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / TICKER
    / FILING
    / f"{FILENAME}_items.json"
)

# -------------------------------------------------
# CLEANING HELPERS
# -------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize whitespace and newlines"""
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def remove_xbrl_noise(text: str) -> str:
    """Remove XBRL / GAAP / metadata junk"""
    clean_lines = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        if (
            line.startswith(
                (
                    "us-gaap:",
                    "aapl:",
                    "xbrli:",
                    "iso4217:",
                    "dei:",
                    "srt:",
                )
            )
            or line.startswith("http://")
            or re.fullmatch(r"\d{4}-\d{2}-\d{2}", line)
            or re.fullmatch(r"\d{8,}", line)
        ):
            continue

        clean_lines.append(line)

    return "\n".join(clean_lines)

# -------------------------------------------------
# ITEM EXTRACTION
# -------------------------------------------------

ITEM_PATTERNS = {
    "Item 1 - Business": r"Item\s+1\.\s+Business",
    "Item 1A - Risk Factors": r"Item\s+1A\.\s+Risk Factors",
    "Item 1B - Unresolved Staff Comments": r"Item\s+1B\.",
    "Item 7 - MD&A": r"Item\s+7\.\s+Management[’']s Discussion and Analysis",
    "Item 7A - Quantitative and Qualitative Disclosures": r"Item\s+7A\.",
    "Item 8 - Financial Statements": r"Item\s+8\.\s+Financial Statements",
}


def extract_items_all_occurrences(text: str) -> dict:
    """
    Extract all occurrences of Item 7 and first occurrence of other items.
    Returns a dict with keys = Item names, values = text.
    """
    # Počnimo sa svim Itemima osim Item 7 (uzimamo samo prvu pojavu)
    items = {}
    positions = {}

    for name, pattern in ITEM_PATTERNS.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if not matches:
            continue
        if name == "Item 7 - MD&A":
            # za Item 7 čuvamo sve start pozicije
            positions[name] = [m.start() for m in matches]
        else:
            positions[name] = matches[0].start()  # samo prva pojava

    # Sad idemo kroz sve pozicije da izvučemo tekst
    # Itemi osim Item 7
    sorted_items = sorted(
        [(k, v) for k, v in positions.items() if k != "Item 7 - MD&A"],
        key=lambda x: x[1]
    )
    for i, (name, start) in enumerate(sorted_items):
        end = sorted_items[i + 1][1] if i + 1 < len(sorted_items) else len(text)
        items[name] = text[start:end].strip()

    # Item 7 - spajamo sve segmente
    if "Item 7 - MD&A" in positions:
        mdna_texts = []
        starts = positions["Item 7 - MD&A"]
        for idx, start in enumerate(starts):
            # kraj do sledeće start pozicije ili do kraja teksta
            end = starts[idx + 1] if idx + 1 < len(starts) else len(text)
            mdna_texts.append(text[start:end].strip())
        items["Item 7 - MD&A"] = "\n\n".join(mdna_texts)

    return items


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    print("📥 Reading:", INPUT_FILE)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    text = raw.get("text", "")
    if not text:
        raise ValueError("Input JSON has no 'text' field")

    text = normalize_text(text)
    text = remove_xbrl_noise(text)

    items = extract_items_all_occurrences(text)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print("✅ Cleaned 10-K items saved to:", OUTPUT_FILE)
    print("\n📑 Extracted sections:")
    for k in items:
        print(" -", k)


if __name__ == "__main__":
    main()
