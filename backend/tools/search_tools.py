import logging
from typing import List, Dict, Any
import yfinance as yf

logger = logging.getLogger(__name__)

def fetch_company_news(ticker: str, company_name: str = "", max_results: int = 6) -> List[Dict[str, Any]]:
    """Fetch recent news articles combining Yahoo Finance ticker news and DuckDuckGo search."""
    articles = []
    
    # 1. First attempt: Yahoo Finance Ticker News (fast, zero key required)
    try:
        t = yf.Ticker(ticker)
        yf_news = t.news or []
        for item in yf_news[:max_results]:
            content = item.get("content", {})
            title = content.get("title") or item.get("title")
            summary = content.get("summary") or item.get("description", "")
            pub_date = content.get("pubDate") or item.get("providerPublishTime", "")
            url = ""
            if "canonicalUrl" in content and "url" in content["canonicalUrl"]:
                url = content["canonicalUrl"]["url"]
            elif "link" in item:
                url = item["link"]
            
            if title:
                articles.append({
                    "title": title,
                    "summary": summary[:400] if summary else "",
                    "source": item.get("publisher", "Yahoo Finance"),
                    "published": str(pub_date),
                    "url": url
                })
    except Exception as e:
        logger.warning(f"Failed to fetch yfinance news for {ticker}: {e}")

    # 2. Second attempt / supplement: DuckDuckGo news search
    if len(articles) < 3:
        try:
            from duckduckgo_search import DDGS
            query = f"{ticker} {company_name} stock earnings news"
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))
                for r in results:
                    articles.append({
                        "title": r.get("title", ""),
                        "summary": r.get("body", "")[:400],
                        "source": r.get("source", "Web"),
                        "published": r.get("date", ""),
                        "url": r.get("url", "")
                    })
        except Exception as e:
            logger.warning(f"DuckDuckGo search fallback failed: {e}")

    # Deduplicate articles by title
    seen = set()
    unique_articles = []
    for a in articles:
        if a["title"] and a["title"].lower() not in seen:
            seen.add(a["title"].lower())
            unique_articles.append(a)

    return unique_articles[:max_results]

def search_competitors(ticker: str, sector: str, industry: str) -> List[Dict[str, str]]:
    """Find key peers and competitors for a company."""
    # Common peer mappings for popular tickers
    KNOWN_PEERS = {
        "NVDA": ["AMD", "INTC", "QCOM", "AVGO", "ARM"],
        "AAPL": ["MSFT", "GOOGL", "AMZN", "META", "SSNLF"],
        "MSFT": ["GOOGL", "AMZN", "AAPL", "ORCL", "CRM"],
        "GOOGL": ["MSFT", "META", "AMZN", "AAPL", "BIDU"],
        "AMZN": ["MSFT", "GOOGL", "WMT", "BABA", "TGT"],
        "TSLA": ["BYDDY", "RIVN", "LCID", "F", "GM"],
        "META": ["GOOGL", "SNAP", "PINS", "MSFT", "TTD"]
    }
    
    clean_ticker = ticker.upper()
    if clean_ticker in KNOWN_PEERS:
        peers = KNOWN_PEERS[clean_ticker]
    else:
        # Fallback to general industry search or sector estimation
        peers = ["SPY", "QQQ"]
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                res = list(ddgs.text(f"top competitors of {clean_ticker} {industry} stock tickers", max_results=3))
                # Will be analyzed by the competitor agent with LLM
        except Exception:
            pass

    # Gather baseline peer metrics via yfinance
    peer_data = []
    for p in peers[:4]:
        try:
            pt = yf.Ticker(p)
            pinfo = pt.info or {}
            peer_data.append({
                "ticker": p,
                "name": pinfo.get("shortName", p),
                "marketCap": pinfo.get("marketCap", "N/A"),
                "peRatio": pinfo.get("forwardPE", pinfo.get("trailingPE", "N/A")),
                "profitMargins": pinfo.get("profitMargins", "N/A"),
                "revenueGrowth": pinfo.get("revenueGrowth", "N/A")
            })
        except Exception:
            peer_data.append({"ticker": p, "name": p, "marketCap": "N/A", "peRatio": "N/A"})

    return peer_data
