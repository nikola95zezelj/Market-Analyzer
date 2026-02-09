# Market Analyzer

**Description:**  
This project analyzes financial reports and market news for selected companies using LLM models.

**Project Structure:**  
Market-analyzer

data/ # Raw and processed data

src/ # Code for ingestion, preprocessing, and analysis

notebooks/ # Jupyter notebooks for experiments and visualization

requirements.txt



**Goals:**  
- Download 10-K filings and market news  
- Preprocess data and extract key information  
- Analyze and generate insights using LLMs and NLP models  

**Getting Started:**  
1. Create a virtual environment and install dependencies from `requirements.txt`  
2. Run the ingestion scripts to download data  
3. Use the notebooks for visualization and model testing


##  Project Structure

```
Market-Analyzer/
│
├── data/
│   ├── raw/
│   │   └── AAPL/
│   │       └── 10K/
│   │           └── aapl-20250927.htm
│   │
│   └── processed/
│       └── AAPL/
│           ├── 10K/
│           │   ├── aapl-20250927.json
│           │   └── aapl-20250927_items.json
│           │
│           ├── chunks/
│           │   └── aapl-2025_item7_chunks.json
│           │
│           └── sentiment/
│               └── aapl-2025_item7_sentiment.json
│
├── src/
│   ├── ingestion/
│   │   └── sec_downloader.py
│   │
│   ├── preprocessing/
│   │   ├── extract_10k.py
│   │   ├── clean_10k_items.py
│   │   └── chunk.py
│   │
│   ├── analysis/
│   │   └── finbert_sentiment.py
│   │
│   
│
├── notebooks/
│   └── (empty – for exploratory analysis)
│
├── main.py
├── README.md
└── .gitignore
```
---

## 🔄 Data Pipeline Overview

1. **Download** SEC 10-K HTML (`sec_downloader.py`)
2. **Extract text** from HTML (`extract_10k.py`)
3. **Clean & split** into Item sections (`clean_10k_items.py`)
4. **Chunk MD&A (Item 7)** (`chunk.py`)
5. **Run FinBERT sentiment** per chunk (`finbert_sentiment.py`)

---

##  NLP Models Used

- **FinBERT** (`ProsusAI/finbert`)
  - Financial-domain sentiment analysis
  - Outputs: `positive / neutral / negative` + confidence scores

---


