import json
import numpy as np
from pathlib import Path
import csv
import re

# ---------- CONFIG ----------
TICKER = "AAPL"
YEAR = 2025
ITEM_NAME = "Item 7 - MD&A"

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CHUNK_FILE = BASE_DIR / f"data/processed/{TICKER}/chunks/{TICKER.lower()}-{YEAR}_item7_chunks.json"
SENTIMENT_FILE = BASE_DIR / f"data/processed/{TICKER}/sentiment/{TICKER.lower()}-{YEAR}_item7_sentiment.json"

OUTPUT_DIR = BASE_DIR / f"data/processed/{TICKER}/aggregated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AGG_JSON_FILE = OUTPUT_DIR / f"{TICKER.lower()}-{YEAR}_item7_aggregated.json"
PANEL_CSV_FILE = BASE_DIR / "data/processed/text_features_panel.csv"

# ---------- SIMPLE RISK LEXICON ----------
RISK_WORDS = {
    "risk", "risks", "risky",
    "uncertain", "uncertainty",
    "volatile", "volatility",
    "adverse", "adversely",
    "loss", "losses",
    "decline", "declines",
    "litigation", "impairment",
    "weak", "weakened",
    "challenging"
}

UNCERTAINTY_WORDS = {
    "may", "might", "could", "possibly",
    "uncertain", "uncertainty",
    "approximately", "estimate",
    "assume", "assumption"
}


# ---------- HELPERS ----------
def tokenize(text: str):
    text = text.lower()
    words = re.findall(r"\b[a-z]+\b", text)
    return words


def compute_risk_metrics(texts):
    total_words = 0
    risk_count = 0
    uncertainty_count = 0

    for text in texts:
        words = tokenize(text)
        total_words += len(words)

        for w in words:
            if w in RISK_WORDS:
                risk_count += 1
            if w in UNCERTAINTY_WORDS:
                uncertainty_count += 1

    if total_words == 0:
        return 0, 0, 0

    risk_ratio = risk_count / total_words
    uncertainty_ratio = uncertainty_count / total_words

    return total_words, risk_ratio, uncertainty_ratio


def append_to_panel_csv(row_dict):
    file_exists = PANEL_CSV_FILE.exists()

    with open(PANEL_CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row_dict.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row_dict)


# ---------- MAIN ----------
def main():

    if not CHUNK_FILE.exists():
        print(f"❌ Chunk file not found: {CHUNK_FILE}")
        return

    if not SENTIMENT_FILE.exists():
        print(f"❌ Sentiment file not found: {SENTIMENT_FILE}")
        return

    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    with open(SENTIMENT_FILE, "r", encoding="utf-8") as f:
        sentiments = json.load(f)

    if len(chunks) != len(sentiments):
        print("⚠ Warning: Chunk count and sentiment count mismatch")

    # -------- Sentiment metrics --------
    sentiment_scores = [s["sentiment_score"] for s in sentiments]
    labels = [s["sentiment_label"] for s in sentiments]

    pos_probs = [s["probabilities"]["positive"] for s in sentiments]
    neg_probs = [s["probabilities"]["negative"] for s in sentiments]

    n_chunks = len(sentiment_scores)

    mean_sentiment = float(np.mean(sentiment_scores))
    std_sentiment = float(np.std(sentiment_scores))
    min_sentiment = float(np.min(sentiment_scores))
    max_sentiment = float(np.max(sentiment_scores))
    sentiment_q10 = float(np.quantile(sentiment_scores, 0.10))
    sentiment_q90 = float(np.quantile(sentiment_scores, 0.90))

    positive_ratio = labels.count("positive") / n_chunks
    neutral_ratio = labels.count("neutral") / n_chunks
    negative_ratio = labels.count("negative") / n_chunks

    avg_positive_probability = float(np.mean(pos_probs))
    avg_negative_probability = float(np.mean(neg_probs))

    # -------- Text metrics --------
    texts = [c["text"] for c in chunks]

    total_words, risk_ratio, uncertainty_ratio = compute_risk_metrics(texts)
    avg_words_per_chunk = total_words / n_chunks if n_chunks > 0 else 0

    # -------- Final feature dict --------
    aggregated = {
        "ticker": TICKER,
        "year": YEAR,
        "n_chunks": n_chunks,

        "total_words": total_words,
        "avg_words_per_chunk": avg_words_per_chunk,

        "mean_sentiment": mean_sentiment,
        "std_sentiment": std_sentiment,
        "min_sentiment": min_sentiment,
        "max_sentiment": max_sentiment,
        "sentiment_q10": sentiment_q10,
        "sentiment_q90": sentiment_q90,

        "positive_ratio": positive_ratio,
        "neutral_ratio": neutral_ratio,
        "negative_ratio": negative_ratio,

        "avg_positive_probability": avg_positive_probability,
        "avg_negative_probability": avg_negative_probability,

        "risk_word_ratio": risk_ratio,
        "uncertainty_word_ratio": uncertainty_ratio
    }

    # -------- Save JSON --------
    with open(AGG_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2)

    print(f"✅ Aggregated JSON saved to {AGG_JSON_FILE}")

    # -------- Append to panel CSV --------
    append_to_panel_csv(aggregated)
    print(f"📊 Appended to panel CSV: {PANEL_CSV_FILE}")


if __name__ == "__main__":
    main()
