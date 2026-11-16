import logging
from typing import Dict, Any, Optional
import yfinance as yf

logger = logging.getLogger(__name__)

def clean_value(val: Any) -> Any:
    """Safely format numbers, handling NaN / None."""
    if val is None:
        return "N/A"
    try:
        import numpy as np
        if np.isnan(val):
            return "N/A"
    except Exception:
        pass
    if isinstance(val, (int, float)):
        return round(val, 2)
    return str(val)

def fetch_financial_overview(ticker: str) -> Dict[str, Any]:
    """Fetch high-level company profile and key valuation multiples."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        
        overview = {
            "ticker": ticker.upper(),
            "shortName": info.get("shortName", ticker.upper()),
            "longName": info.get("longName", info.get("shortName", ticker.upper())),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "country": info.get("country", "N/A"),
            "website": info.get("website", "N/A"),
            "summary": info.get("longBusinessSummary", "No summary available."),
            "currency": info.get("currency", "USD"),
            "currentPrice": clean_value(info.get("currentPrice", info.get("regularMarketPrice"))),
            "targetMeanPrice": clean_value(info.get("targetMeanPrice")),
            "recommendationKey": info.get("recommendationKey", "N/A"),
            "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions", "N/A"),
            
            # Valuation Metrics
            "marketCap": clean_value(info.get("marketCap")),
            "enterpriseValue": clean_value(info.get("enterpriseValue")),
            "trailingPE": clean_value(info.get("trailingPE")),
            "forwardPE": clean_value(info.get("forwardPE")),
            "pegRatio": clean_value(info.get("pegRatio")),
            "priceToBook": clean_value(info.get("priceToBook")),
            "priceToSalesTrailing12Months": clean_value(info.get("priceToSalesTrailing12Months")),
            "enterpriseToRevenue": clean_value(info.get("enterpriseToRevenue")),
            "enterpriseToEbitda": clean_value(info.get("enterpriseToEbitda")),
            
            # Profitability & Operating Efficiency
            "profitMargins": clean_value(info.get("profitMargins")),
            "operatingMargins": clean_value(info.get("operatingMargins")),
            "grossMargins": clean_value(info.get("grossMargins")),
            "returnOnAssets": clean_value(info.get("returnOnAssets")),
            "returnOnEquity": clean_value(info.get("returnOnEquity")),
            "revenuePerShare": clean_value(info.get("revenuePerShare")),
            "trailingEps": clean_value(info.get("trailingEps")),
            "forwardEps": clean_value(info.get("forwardEps")),
            
            # Financial Health / Liquidity
            "totalCash": clean_value(info.get("totalCash")),
            "totalDebt": clean_value(info.get("totalDebt")),
            "debtToEquity": clean_value(info.get("debtToEquity")),
            "currentRatio": clean_value(info.get("currentRatio")),
            "quickRatio": clean_value(info.get("quickRatio")),
            "freeCashflow": clean_value(info.get("freeCashflow")),
            "operatingCashflow": clean_value(info.get("operatingCashflow")),
            
            # Market Performance
            "52WeekHigh": clean_value(info.get("fiftyTwoWeekHigh")),
            "52WeekLow": clean_value(info.get("fiftyTwoWeekLow")),
            "52WeekChange": clean_value(info.get("52WeekChange")),
            "beta": clean_value(info.get("beta")),
            "dividendYield": clean_value(info.get("dividendYield")),
        }
        return overview
    except Exception as e:
        logger.error(f"Error fetching overview for {ticker}: {e}")
        return {"ticker": ticker.upper(), "error": str(e)}

def fetch_financial_statements(ticker: str) -> Dict[str, Any]:
    """Fetch annual historical income statement, balance sheet, and cash flow data."""
    try:
        t = yf.Ticker(ticker)
        statements = {"years": [], "income_statement": {}, "balance_sheet": {}, "cash_flow": {}}
        
        # 1. Income Statement
        fin = t.financials
        if fin is not None and not fin.empty:
            cols = [str(c.year) if hasattr(c, 'year') else str(c)[:4] for c in fin.columns[:4]]
            statements["years"] = cols
            
            for key in ["Total Revenue", "Operating Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"]:
                if key in fin.index:
                    statements["income_statement"][key] = {
                        cols[i]: clean_value(fin.loc[key].iloc[i]) for i in range(min(len(cols), len(fin.columns)))
                    }
        
        # 2. Balance Sheet
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            bs_cols = [str(c.year) if hasattr(c, 'year') else str(c)[:4] for c in bs.columns[:4]]
            for key in ["Total Assets", "Total Liabilities Net Minority Interest", "Total Debt", "Cash And Cash Equivalents", "Stockholders Equity"]:
                if key in bs.index:
                    statements["balance_sheet"][key] = {
                        bs_cols[i]: clean_value(bs.loc[key].iloc[i]) for i in range(min(len(bs_cols), len(bs.columns)))
                    }
                    
        # 3. Cash Flow
        cf = t.cashflow
        if cf is not None and not cf.empty:
            cf_cols = [str(c.year) if hasattr(c, 'year') else str(c)[:4] for c in cf.columns[:4]]
            for key in ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]:
                if key in cf.index:
                    statements["cash_flow"][key] = {
                        cf_cols[i]: clean_value(cf.loc[key].iloc[i]) for i in range(min(len(cf_cols), len(cf.columns)))
                    }
                    
        return statements
    except Exception as e:
        logger.error(f"Error fetching statements for {ticker}: {e}")
        return {"error": str(e)}
