# src/ingestion/sec_downloader.py

import os
import json
import requests
from pathlib import Path

# ----------------------------------
# CONFIG
# ----------------------------------
HEADERS = {
    "User-Agent": "MarketAnalyzer/0.1 (nikola95zezelj@gmail.com)"
}

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ----------------------------------
# UTIL FUNCTIONS
# ----------------------------------
def get_cik_from_ticker(ticker: str) -> str:
    """
    Maps ticker to CIK using SEC mapping file.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    data = response.json()

    for entry in data.values():
        if entry["ticker"].lower() == ticker.lower():
            return str(entry["cik_str"]).zfill(10)

    raise ValueError(f"CIK not found for ticker {ticker}")


def get_company_filings(cik: str) -> dict:
    """
    Returns filing metadata for a given CIK.
    """
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def download_latest_10k(ticker: str):
    cik = get_cik_from_ticker(ticker)
    filings = get_company_filings(cik)

    recent = filings["filings"]["recent"]

    for form, accession, doc in zip(
        recent["form"],
        recent["accessionNumber"],
        recent["primaryDocument"],
    ):
        if form == "10-K":
            accession_no = accession.replace("-", "")
            filing_url = (
                f"https://www.sec.gov/Archives/edgar/data/"
                f"{int(cik)}/{accession_no}/{doc}"
            )

            save_dir = RAW_DATA_DIR / ticker / "10K"
            save_dir.mkdir(parents=True, exist_ok=True)

            file_path = save_dir / doc

            r = requests.get(filing_url, headers=HEADERS)
            r.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(r.content)

            print(f"✅ Downloaded 10-K for {ticker}: {file_path}")
            return

    print(f"❌ No 10-K found for {ticker}")


# ----------------------------------
# MAIN
# ----------------------------------
if __name__ == "__main__":
    download_latest_10k("AAPL")
