import datetime
import json
import logging
import markdown
from core.state import ResearchState
from core.llm import get_gemini_llm

logger = logging.getLogger(__name__)

def report_node(state: ResearchState) -> ResearchState:
    """Report Generator Agent: Synthesizes multi-agent outputs into an institutional equity research memo."""
    ticker = state["ticker"]
    company_name = state.get("company_name", ticker)
    sector = state.get("sector", "N/A")
    industry = state.get("industry", "N/A")
    market_cap = state.get("market_cap", "N/A")
    currency = state.get("currency", "USD")
    
    financial_data = state.get("financial_data") or {}
    news_data = state.get("news_data") or {}
    sec_data = state.get("sec_filing_data") or {}
    competitor_data = state.get("competitor_data") or {}
    risk_data = state.get("risk_data") or {}
    
    node_logs = [
        {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": "Report Generator",
            "status": "in_progress",
            "message": f"Synthesizing institutional equity research report for {company_name} ({ticker})..."
        }
    ]
    
    fin_overview = financial_data.get("overview", {})
    llm = get_gemini_llm(temperature=0.1)
    
    markdown_report = ""
    if llm:
        try:
            prompt = f"""You are the Managing Director of Global Equity Research at a top-tier investment bank.
Produce an institutional-grade, highly structured equity research initiation report on {company_name} (Ticker: {ticker}).

---
### COMPANY PROFILE
- Company: {company_name} ({ticker})
- Sector: {sector} | Industry: {industry}
- Current Share Price: {fin_overview.get('currentPrice', 'N/A')} {currency}
- Market Capitalization: {market_cap}
- Valuation Multiples: P/E (Trailing: {fin_overview.get('trailingPE')}, Forward: {fin_overview.get('forwardPE')}), PEG: {fin_overview.get('pegRatio')}, P/B: {fin_overview.get('priceToBook')}
- Profitability: Gross Margin {fin_overview.get('grossMargins')}, Operating Margin {fin_overview.get('operatingMargins')}, Profit Margin {fin_overview.get('profitMargins')}
- Balance Sheet: Cash {fin_overview.get('totalCash')}, Debt {fin_overview.get('totalDebt')}, Debt/Equity {fin_overview.get('debtToEquity')}

---
### INPUT INTELLIGENCE FROM SPECIALIZED SUB-AGENTS

1. FINANCIAL DATA AGENT SYNTHESIS:
{financial_data.get('ai_analysis', 'Data parsed.')}

2. NEWS & SENTIMENT AGENT SYNTHESIS:
Sentiment: {news_data.get('sentiment', 'Neutral')}
{news_data.get('ai_analysis', 'News parsed.')}

3. SEC ANNUAL REPORT (10-K) AGENT SYNTHESIS:
{sec_data.get('ai_analysis', 'Filings parsed.')}

4. COMPETITOR & MOAT AGENT SYNTHESIS:
{competitor_data.get('ai_analysis', 'Peers analyzed.')}

5. RISK ANALYSIS AGENT SYNTHESIS:
{risk_data.get('ai_analysis', 'Risks evaluated.')}

---
### REPORT GENERATION INSTRUCTIONS
Compose a comprehensive, Wall Street-standard research report in Markdown. Adhere strictly to the following structure:

# Institutional Equity Research Report: {company_name} ({ticker})
*Date: {datetime.datetime.now().strftime('%B %d, %Y')} | Sector: {sector} | Industry: {industry}*

## 1. Executive Summary & Investment Thesis
- Clear thesis statement
- **Bull Case Scenario** (key catalysts, upside targets)
- **Base Case Scenario** (steady state expectations)
- **Bear Case Scenario** (downside risks and floor valuation)

## 2. Business Overview & Economic Moat
- Revenue streams and operational segments
- Competitive moat assessment (network effects, switching costs, cost advantages)

## 3. Financial Performance & Valuation Appraisal
- Analysis of revenue trajectory, margin expansion/compression, and cash generation
- Valuation multiples table & peer benchmarking evaluation

## 4. Competitive Dynamics & Peer Benchmarking
- Top competitor comparison
- Threats of substitution, market share gains/losses

## 5. Recent Catalysts & Sentiment Signals
- 90-day material developments, product rollouts, earnings sentiment

## 6. Comprehensive Risk Matrix
- Formatted Markdown risk table: Category, Specific Threat, Likelihood, Impact, Mitigation

## 7. Strategic Outlook & Investment Rating
- Investment Stance: [Overweight / Neutral / Underweight]
- Target Multiple Rationale
- *Regulatory Compliance Disclaimer: Educational research prototype. Not financial advice.*
"""
            response = llm.invoke(prompt)
            markdown_report = response.content
        except Exception as e:
            logger.error(f"Report agent LLM synthesis error: {e}")
            markdown_report = ""

    # Fallback template if LLM is not configured or fails
    if not markdown_report:
        markdown_report = f"""# Institutional Equity Research Report: {company_name} ({ticker})
*Date: {datetime.datetime.now().strftime('%B %d, %Y')} | Sector: {sector} | Industry: {industry}*

## 1. Executive Summary & Investment Thesis
{company_name} ({ticker}) trades at {fin_overview.get('currentPrice', 'N/A')} {currency} with a market capitalization of {market_cap}.
- **Bull Case**: Continued expansion in core {industry} operations with margin resilience.
- **Base Case**: Steady operational performance in line with broader sector benchmarks.
- **Bear Case**: Valuation compression if macroeconomic headwinds dampen consumer or enterprise spending.

## 2. Financial Overview & Valuation
| Metric | Value |
| :--- | :--- |
| **Current Price** | {fin_overview.get('currentPrice', 'N/A')} {currency} |
| **Market Capitalization** | {market_cap} |
| **Trailing P/E** | {fin_overview.get('trailingPE', 'N/A')} |
| **Forward P/E** | {fin_overview.get('forwardPE', 'N/A')} |
| **Debt to Equity** | {fin_overview.get('debtToEquity', 'N/A')} |
| **Operating Margin** | {fin_overview.get('operatingMargins', 'N/A')} |

### Financial Agent Analysis
{financial_data.get('ai_analysis', 'Financial statements evaluated.')}

## 3. News & Market Sentiment
**Overall Sentiment:** {news_data.get('sentiment', 'Neutral')}
{news_data.get('ai_analysis', 'Recent news and events evaluated.')}

## 4. SEC 10-K Filings Review
{sec_data.get('ai_analysis', 'Annual report filings parsed.')}

## 5. Competitive Landscape & Peer Benchmarking
{competitor_data.get('ai_analysis', 'Peer group benchmarking completed.')}

## 6. Comprehensive Risk Matrix
{risk_data.get('ai_analysis', 'Risk and leverage factors evaluated.')}

---
*Disclaimer: This research report was automatically generated by an autonomous multi-agent system for educational and testing purposes.*
"""

    # Convert markdown to styled HTML
    html_body = markdown.markdown(markdown_report, extensions=["tables", "fenced_code"])
    
    node_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "Report Generator",
        "status": "completed",
        "message": f"Institutional report generated successfully for {ticker}."
    })
    
    return {
        "final_report": markdown_report,
        "report_html": html_body,
        "agent_logs": node_logs,
        "current_step": "completed"
    }
