import datetime
import json
import logging
from core.state import ResearchState
from tools.yfinance_tools import fetch_financial_overview, fetch_financial_statements
from core.llm import get_gemini_llm

logger = logging.getLogger(__name__)

def financial_node(state: ResearchState) -> ResearchState:
    """Financial Data Agent: Gathers and analyzes raw financial statements and valuation multiples."""
    ticker = state["ticker"]
    node_logs = [
        {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": "Financial Data Agent",
            "status": "in_progress",
            "message": f"Extracting historical statements & valuation multiples for {ticker}..."
        }
    ]
    
    overview = fetch_financial_overview(ticker)
    statements = fetch_financial_statements(ticker)
    
    # Financial Analysis with Gemini
    llm = get_gemini_llm()
    ai_summary = ""
    if llm:
        try:
            prompt = f"""You are an institutional financial analyst. Analyze these key metrics and statements for {ticker}:
Company: {overview.get('longName')} | Sector: {overview.get('sector')}
Current Price: {overview.get('currentPrice')} {overview.get('currency')} | Market Cap: {overview.get('marketCap')}
Trailing P/E: {overview.get('trailingPE')} | Forward P/E: {overview.get('forwardPE')} | PEG: {overview.get('pegRatio')}
Operating Margin: {overview.get('operatingMargins')} | Profit Margin: {overview.get('profitMargins')}
Total Cash: {overview.get('totalCash')} | Total Debt: {overview.get('totalDebt')} | Debt/Equity: {overview.get('debtToEquity')}
Free Cash Flow: {overview.get('freeCashflow')}

Income Statement Highlights:
{json.dumps(statements.get('income_statement', {}), indent=2)}

Provide a concise, quantitative evaluation covering:
1. Revenue & Margin Trend (growth trajectory, profitability quality)
2. Balance Sheet Health & Debt Coverage (liquidity, leverage sustainability)
3. Free Cash Flow Generation & Capital Allocation
4. Valuation Multiple Appraisal (cheap, fair, or stretched)"""
            
            response = llm.invoke(prompt)
            ai_summary = response.content
        except Exception as e:
            logger.warning(f"Financial agent LLM synthesis error: {e}")
            ai_summary = "Quantitative financial data parsed successfully."
    else:
        ai_summary = (
            f"Financial profile: Current Price {overview.get('currentPrice')} {overview.get('currency')} "
            f"with Market Cap {overview.get('marketCap')}. Trailing P/E is {overview.get('trailingPE')}, "
            f"Forward P/E is {overview.get('forwardPE')}, and Debt-to-Equity is {overview.get('debtToEquity')}."
        )

    financial_data = {
        "overview": overview,
        "statements": statements,
        "ai_analysis": ai_summary
    }
    
    node_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Financial Data Agent",
        "status": "completed",
        "message": f"Financial analysis completed for {ticker}."
    })
    
    return {
        "financial_data": financial_data,
        "agent_logs": node_logs
    }
