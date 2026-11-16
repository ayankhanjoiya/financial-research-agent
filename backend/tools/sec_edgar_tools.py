import re
import json
import logging
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup
from core.config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": settings.SEC_EDGAR_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

def get_cik_for_ticker(ticker: str) -> Optional[str]:
    """Retrieve the SEC Central Index Key (CIK) for a given stock ticker."""
    try:
        headers = {"User-Agent": settings.SEC_EDGAR_USER_AGENT}
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(SEC_TICKERS_URL, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                clean_ticker = ticker.upper()
                for _, entry in data.items():
                    if entry.get("ticker") == clean_ticker:
                        return str(entry.get("cik_str")).zfill(10)
    except Exception as e:
        logger.warning(f"Failed to lookup CIK from sec.gov: {e}")
    return None

def fetch_latest_10k_filing(ticker: str) -> Dict[str, Any]:
    """Fetch metadata and key sections from the most recent 10-K SEC annual filing."""
    cik = get_cik_for_ticker(ticker)
    if not cik:
        return {
            "ticker": ticker.upper(),
            "status": "not_found",
            "message": f"CIK could not be resolved for ticker {ticker}. Non-US or ADR companies may file 20-F instead."
        }
    
    try:
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(submissions_url, headers=HEADERS)
            if resp.status_code != 200:
                return {
                    "ticker": ticker.upper(),
                    "cik": cik,
                    "status": "error",
                    "message": f"SEC EDGAR returned status {resp.status_code}"
                }
            
            sub_data = resp.json()
            recent_filings = sub_data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])
            filing_dates = recent_filings.get("filingDate", [])
            accession_numbers = recent_filings.get("accessionNumber", [])
            primary_docs = recent_filings.get("primaryDocument", [])
            
            # Find the most recent 10-K
            target_idx = -1
            for i, f in enumerate(forms):
                if f == "10-K":
                    target_idx = i
                    break
            
            if target_idx == -1:
                return {
                    "ticker": ticker.upper(),
                    "cik": cik,
                    "status": "not_found",
                    "message": "No 10-K filing found in recent SEC submissions."
                }
            
            acc_num = accession_numbers[target_idx]
            clean_acc = acc_num.replace("-", "")
            doc_name = primary_docs[target_idx]
            filing_date = filing_dates[target_idx]
            
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{clean_acc}/{doc_name}"
            
            # Fetch filing excerpt or document text
            doc_headers = {"User-Agent": settings.SEC_EDGAR_USER_AGENT}
            doc_resp = client.get(doc_url, headers=doc_headers)
            
            item1_business = ""
            item1a_risks = ""
            item7_mda = ""
            
            if doc_resp.status_code == 200:
                soup = BeautifulSoup(doc_resp.text[:1500000], "html.parser") # Read initial segment
                text_content = soup.get_text(separator="\n", strip=True)
                
                # Extract key sections using regex patterns
                def extract_section(start_pat: str, end_pat: str, text: str, max_len: int = 4000) -> str:
                    match = re.search(start_pat, text, re.IGNORECASE)
                    if match:
                        start_pos = match.end()
                        end_match = re.search(end_pat, text[start_pos:start_pos+30000], re.IGNORECASE)
                        if end_match:
                            extracted = text[start_pos:start_pos + end_match.start()].strip()
                            return extracted[:max_len]
                        return text[start_pos:start_pos + max_len].strip()
                    return "Section heading not directly parsed; please consult primary SEC URL."

                item1_business = extract_section(r"item\s+1\.\s+business", r"item\s+1a\.\s+risk", text_content, 3000)
                item1a_risks = extract_section(r"item\s+1a\.\s+risk\s+factors", r"item\s+1b\.", text_content, 4000)
                item7_mda = extract_section(r"item\s+7\.\s+management['’]?s\s+discussion", r"item\s+7a\.", text_content, 3500)

            return {
                "ticker": ticker.upper(),
                "cik": cik,
                "filingDate": filing_date,
                "form": "10-K",
                "documentUrl": doc_url,
                "item1_business_summary": item1_business if len(item1_business) > 100 else "Business description available on SEC EDGAR.",
                "item1a_risk_factors": item1a_risks if len(item1a_risks) > 100 else "Risk factors available on SEC EDGAR.",
                "item7_mda_highlights": item7_mda if len(item7_mda) > 100 else "MD&A analysis available on SEC EDGAR."
            }

    except Exception as e:
        logger.error(f"Error fetching 10-K for {ticker}: {e}")
        return {
            "ticker": ticker.upper(),
            "status": "error",
            "message": str(e)
        }
