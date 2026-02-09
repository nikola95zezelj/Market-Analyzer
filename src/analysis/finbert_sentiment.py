# finbert_sentiment.py
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm

# ---------- CONFIG ----------
TICKER = "AAPL"
YEAR = 2025

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INPUT_FILE = BASE_DIR / f"data/processed/{TICKER}/chunks/{TICKER.lower()}-{YEAR}_item7_chunks.json"
OUTPUT_FILE = BASE_DIR / f"data/processed/{TICKER}/sentiment/{TICKER.lower()}-{YEAR}_item7_sentiment.json"

MODEL_NAME = "ProsusAI/finbert"
MAX_TOKENS = 512  # FinBERT limit

# ---------- LOAD MODEL ----------
print("🔄 Loading FinBERT...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

label_map = {0: "negative", 1: "neutral", 2: "positive"}

# ---------- HELPERS ----------
def finbert_sentiment(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_TOKENS,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probs = torch.softmax(logits, dim=1).squeeze()

    probs = probs.tolist()
    sentiment = {
        "negative": probs[0],
        "neutral": probs[1],
        "positive": probs[2],
    }

    label = label_map[int(torch.argmax(logits))]
    score = sentiment["positive"] - sentiment["negative"]

    return label, score, sentiment


# ---------- MAIN ----------
def main():
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    results = []

    print(f"🧠 Running FinBERT on {len(chunks)} chunks...\n")

    for chunk in tqdm(chunks):
        label, score, probs = finbert_sentiment(chunk["text"])

        results.append({
            "ticker": chunk["ticker"],
            "year": chunk["year"],
            "item": chunk["item"],
            "chunk_id": chunk["chunk_id"],
            "sentiment_label": label,
            "sentiment_score": score,
            "probabilities": probs
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Sentiment analysis saved to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()
