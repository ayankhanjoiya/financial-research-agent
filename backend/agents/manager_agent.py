import datetime
import logging
from core.state import ResearchState
from tools.yfinance_tools import fetch_financial_overview

logger = logging.getLogger(__name__)

def manager_node(state: ResearchState) -> ResearchState:
    """Manager Agent: Validates the ticker symbol and establishes baseline company identity."""
    ticker = state.get("ticker", "").strip().upper()
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    node_logs = [
        {
            "timestamp": now_str,
            "agent": "Manager Agent",
            "status": "in_progress",
            "message": f"Initiating research protocol for ticker: {ticker}"
        }
    ]
    
    # Fetch base profile
    overview = fetch_financial_overview(ticker)
    
    if "error" in overview:
        node_logs.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": "Manager Agent",
            "status": "error",
            "message": f"Failed to fetch profile: {overview.get('error')}"
        })
        return {
            "agent_logs": node_logs,
            "errors": [f"Profile error for {ticker}: {overview.get('error')}"],
            "current_step": "manager_failed"
        }
        
    node_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Manager Agent",
        "status": "completed",
        "message": f"Validated {overview.get('longName')} ({ticker}). Fanning out tasks to sub-agents."
    })
    
    return {
        "ticker": ticker,
        "company_name": overview.get("longName", ticker),
        "sector": overview.get("sector", "N/A"),
        "industry": overview.get("industry", "N/A"),
        "market_cap": str(overview.get("marketCap", "N/A")),
        "currency": overview.get("currency", "USD"),
        "agent_logs": node_logs,
        "current_step": "dispatched"
    }
