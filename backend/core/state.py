import operator
from typing import Annotated, TypedDict, Optional, Dict, Any, List

class AgentLog(TypedDict):
    timestamp: str
    agent: str
    status: str  # "starting", "in_progress", "completed", "error"
    message: str

class ResearchState(TypedDict, total=False):
    # Core identifiers
    ticker: str
    company_name: str
    sector: str
    industry: str
    market_cap: str
    currency: str
    
    # Sub-agent payload containers
    financial_data: Optional[Dict[str, Any]]
    news_data: Optional[Dict[str, Any]]
    sec_filing_data: Optional[Dict[str, Any]]
    competitor_data: Optional[Dict[str, Any]]
    risk_data: Optional[Dict[str, Any]]
    
    # Synthesis & Output
    final_report: Optional[str]
    report_html: Optional[str]
    
    # Telemetry reducers (safely merge across parallel agent nodes)
    agent_logs: Annotated[List[Dict[str, Any]], operator.add]
    errors: Annotated[List[str], operator.add]
    current_step: str
