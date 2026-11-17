import datetime
import logging
from core.state import ResearchState
from core.llm import get_gemini_llm

logger = logging.getLogger(__name__)

def risk_node(state: ResearchState) -> ResearchState:
    """Risk Analysis Agent: Synthesizes regulatory, balance sheet, and macroeconomic vulnerabilities."""
    ticker = state["ticker"]
    company_name = state.get("company_name", ticker)
    financial_data = state.get("financial_data") or {}
    sec_data = state.get("sec_filing_data") or {}
    
    node_logs = [
        {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": "Risk Analysis Agent",
            "status": "in_progress",
            "message": f"Evaluating threat matrix, debt leverage, and risk disclosures for {ticker}..."
        }
    ]
    
    fin_overview = financial_data.get("overview", {})
    sec_risks = sec_data.get("filing", {}).get("item1a_risk_factors", "")
    
    llm = get_gemini_llm()
    ai_summary = ""
    
    if llm:
        try:
            prompt = f"""You are a Chief Risk Officer evaluating an equity investment in {company_name} ({ticker}).

Financial Leverage Profile:
- Total Debt: {fin_overview.get('totalDebt', 'N/A')}
- Total Cash: {fin_overview.get('totalCash', 'N/A')}
- Debt to Equity: {fin_overview.get('debtToEquity', 'N/A')}
- Current Ratio: {fin_overview.get('currentRatio', 'N/A')}

SEC Disclosed Risk Factors Excerpt:
{sec_risks[:2500] if sec_risks else 'Standard industry risk factors.'}

Synthesize a structured risk assessment:
1. Risk Matrix (Markdown table with columns: [Risk Category, Specific Vulnerability, Likelihood (Low/Med/High), Impact (Low/Med/High), Mitigation Strategy])
2. Macro & Geopolitical Sensitivity (Interest rate exposure, currency risk, trade restrictions)
3. Balance Sheet Stress-Test Evaluation (Can the company withstand a prolonged severe downturn?)"""
            
            response = llm.invoke(prompt)
            ai_summary = response.content
        except Exception as e:
            logger.warning(f"Risk agent LLM synthesis error: {e}")
            ai_summary = "Risk assessment evaluated from financial leverage and SEC filings."
    else:
        ai_summary = (
            f"Risk Profile for {ticker}: Total debt stands at {fin_overview.get('totalDebt', 'N/A')}, "
            f"with Debt/Equity of {fin_overview.get('debtToEquity', 'N/A')}. Monitor liquidity and macro headwinds."
        )

    risk_data = {
        "debt_to_equity": fin_overview.get("debtToEquity", "N/A"),
        "total_debt": fin_overview.get("totalDebt", "N/A"),
        "ai_analysis": ai_summary
    }
    
    node_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Risk Analysis Agent",
        "status": "completed",
        "message": f"Risk matrix and leverage stress test synthesized for {ticker}."
    })
    
    return {
        "risk_data": risk_data,
        "agent_logs": node_logs
    }
