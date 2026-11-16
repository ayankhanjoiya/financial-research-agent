import datetime
import json
import logging
from core.state import ResearchState, AgentLog
from tools.search_tools import search_competitors
from core.llm import get_gemini_llm

logger = logging.getLogger(__name__)

def competitor_node(state: ResearchState) -> ResearchState:
    """Competitor Agent: Identifies peer group, relative valuation multiples, and economic moats."""
    ticker = state["ticker"]
    sector = state.get("sector", "N/A")
    industry = state.get("industry", "N/A")
    company_name = state.get("company_name", ticker)
    
    logs = list(state.get("agent_logs", []))
    logs.append(AgentLog(
        timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
        agent="Competitor Agent",
        status="in_progress",
        message=f"Benchmarking peer competitors and industry dynamics for {company_name}..."
    ))
    
    peers = search_competitors(ticker, sector, industry)
    
    llm = get_gemini_llm()
    ai_summary = ""
    
    if llm:
        try:
            prompt = f"""You are an equity research strategist specializing in competitive advantage and moat analysis.
Subject Company: {company_name} ({ticker}) | Sector: {sector} | Industry: {industry}

Identified Peer Group Data:
{json.dumps(peers, indent=2)}

Provide:
1. Relative Valuation Comparison (How does {ticker}'s multiple compare to the peer group?)
2. Moat Assessment (High / Narrow / None - pricing power, switching costs, cost advantages)
3. Competitive Threats & Market Share Dynamics (Who poses the biggest risk to {ticker}'s market position?)"""
            
            response = llm.invoke(prompt)
            ai_summary = response.content
        except Exception as e:
            logger.warning(f"Competitor agent LLM synthesis error: {e}")
            ai_summary = "Peer group benchmarking assembled."
    else:
        peer_names = ", ".join([p.get("ticker", "") for p in peers])
        ai_summary = f"Peer group analyzed: {peer_names} in {industry}."

    competitor_data = {
        "peers": peers,
        "ai_analysis": ai_summary
    }
    
    logs.append(AgentLog(
        timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
        agent="Competitor Agent",
        status="completed",
        message=f"Peer analysis complete ({len(peers)} competitors benchmarked)."
    ))
    
    return {
        **state,
        "competitor_data": competitor_data,
        "agent_logs": logs
    }
