import datetime
import logging
from core.state import ResearchState
from tools.sec_edgar_tools import fetch_latest_10k_filing
from core.llm import get_gemini_llm

logger = logging.getLogger(__name__)

def sec_node(state: ResearchState) -> ResearchState:
    """Annual Report Agent: Parses official SEC 10-K filings for management disclosures."""
    ticker = state["ticker"]
    node_logs = [
        {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": "Annual Report Agent",
            "status": "in_progress",
            "message": f"Accessing SEC EDGAR database for latest 10-K filing of {ticker}..."
        }
    ]
    
    filing = fetch_latest_10k_filing(ticker)
    
    llm = get_gemini_llm()
    ai_summary = ""
    
    if llm and filing.get("form") == "10-K":
        try:
            prompt = f"""You are a securities filings expert. Review these excerpts from the latest 10-K filing of {ticker}:

Item 1 (Business Overview Excerpt):
{filing.get('item1_business_summary', '')[:2500]}

Item 1A (Risk Factors Disclosed by Management):
{filing.get('item1a_risk_factors', '')[:2500]}

Item 7 (Management Discussion & Analysis Highlights):
{filing.get('item7_mda_highlights', '')[:2500]}

Synthesize:
1. Core Revenue Model & Structural Competitive Advantages
2. Key Operational Headwinds Disclosed by Leadership
3. Strategic Capital Priorities for the upcoming fiscal cycle"""
            
            response = llm.invoke(prompt)
            ai_summary = response.content
        except Exception as e:
            logger.warning(f"SEC agent LLM synthesis error: {e}")
            ai_summary = "10-K filing parsed successfully from SEC EDGAR."
    else:
        if filing.get("form") == "10-K":
            ai_summary = f"10-K filed on {filing.get('filingDate')}. Document URL: {filing.get('documentUrl')}"
        else:
            ai_summary = f"SEC filing note: {filing.get('message', 'No direct 10-K filing parsed')}"

    sec_data = {
        "filing": filing,
        "ai_analysis": ai_summary
    }
    
    status_msg = f"10-K filing analyzed (Filing Date: {filing.get('filingDate', 'Recent')})." if filing.get('form') == "10-K" else "SEC filing reference logged."
    node_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Annual Report Agent",
        "status": "completed",
        "message": status_msg
    })
    
    return {
        "sec_filing_data": sec_data,
        "agent_logs": node_logs
    }
