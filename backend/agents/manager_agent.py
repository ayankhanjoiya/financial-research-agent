import datetime
import logging
from core.state import ResearchState, AgentLog
from tools.yfinance_tools import fetch_financial_overview

logger = logging.getLogger(__name__)

def manager_node(state: ResearchState) -> ResearchState:
    """Manager Agent: Validates the ticker symbol and establishes baseline company identity."""
    ticker = state.get("ticker", "").strip().upper()
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    logs = state.get("agent_logs", [])
    logs.append(AgentLog(
        timestamp=now_str,
        agent="Manager Agent",
        status="in_progress",
        message=f"Initiating research protocol for ticker: {ticker}"
    ))
    
    # Fetch base profile
    overview = fetch_financial_overview(ticker)
    
    if "error" in overview:
        logs.append(AgentLog(
            timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
            agent="Manager Agent",
            status="error",
            message=f"Failed to fetch profile: {overview.get('error')}"
        ))
        errors = state.get("errors", [])
        errors.append(f"Profile error: {overview.get('error')}")
        return {
            **state,
            "agent_logs": logs,
            "errors": errors,
            "current_step": "manager_failed"
        }
        
    logs.append(AgentLog(
        timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
        agent="Manager Agent",
        status="completed",
        message=f"Validated {overview.get('longName')} ({ticker}). Fanning out tasks to sub-agents."
    ))
    
    return {
        **state,
        "ticker": ticker,
        "company_name": overview.get("longName", ticker),
        "sector": overview.get("sector", "N/A"),
        "industry": overview.get("industry", "N/A"),
        "market_cap": str(overview.get("marketCap", "N/A")),
        "currency": overview.get("currency", "USD"),
        "agent_logs": logs,
        "current_step": "dispatched"
    }
