import datetime
import logging
from core.state import ResearchState
from tools.search_tools import fetch_company_news
from core.llm import get_gemini_llm

logger = logging.getLogger(__name__)

def news_node(state: ResearchState) -> ResearchState:
    """News Research Agent: Scours recent news, earnings commentary, and sentiment signals."""
    ticker = state["ticker"]
    company_name = state.get("company_name", ticker)
    node_logs = [
        {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "agent": "News Research Agent",
            "status": "in_progress",
            "message": f"Searching recent material news and sentiment for {company_name} ({ticker})..."
        }
    ]
    
    articles = fetch_company_news(ticker, company_name)
    
    llm = get_gemini_llm()
    sentiment = "Neutral"
    ai_summary = ""
    
    if llm and articles:
        try:
            articles_text = "\n\n".join([
                f"- Title: {a.get('title')}\n  Summary: {a.get('summary')}\n  Date: {a.get('published')}"
                for a in articles
            ])
            prompt = f"""You are a market intelligence analyst. Review the following recent headlines and summaries for {company_name} ({ticker}):

{articles_text}

Provide:
1. Overall Sentiment Verdict: [Bullish, Bearish, or Neutral]
2. Top 3 Recent Catalysts or Emerging Developments
3. Market Perception Summary (1-2 paragraphs highlighting growth drivers or headline risks)"""
            
            response = llm.invoke(prompt)
            ai_summary = response.content
            if "bullish" in ai_summary.lower()[:150]:
                sentiment = "Bullish"
            elif "bearish" in ai_summary.lower()[:150]:
                sentiment = "Bearish"
            else:
                sentiment = "Neutral"
        except Exception as e:
            logger.warning(f"News agent LLM synthesis error: {e}")
            ai_summary = "News articles collected and indexed."
    else:
        ai_summary = f"Gathered {len(articles)} recent market updates and headlines for {ticker}."

    news_data = {
        "articles": articles,
        "sentiment": sentiment,
        "ai_analysis": ai_summary
    }
    
    node_logs.append({
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        "agent": "News Research Agent",
        "status": "completed",
        "message": f"News analysis complete. Sentiment: {sentiment} ({len(articles)} articles indexed)."
    })
    
    return {
        "news_data": news_data,
        "agent_logs": node_logs
    }
