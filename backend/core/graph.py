import logging
from langgraph.graph import StateGraph, START, END
from core.state import ResearchState
from agents.manager_agent import manager_node
from agents.financial_agent import financial_node
from agents.news_agent import news_node
from agents.sec_agent import sec_node
from agents.competitor_agent import competitor_node
from agents.risk_agent import risk_node
from agents.report_agent import report_node

logger = logging.getLogger(__name__)

def build_graph():
    """Build and compile the LangGraph multi-agent research graph."""
    workflow = StateGraph(ResearchState)
    
    # 1. Register Nodes
    workflow.add_node("manager", manager_node)
    workflow.add_node("financial_agent", financial_node)
    workflow.add_node("news_agent", news_node)
    workflow.add_node("sec_agent", sec_node)
    workflow.add_node("competitor_agent", competitor_node)
    workflow.add_node("risk_agent", risk_node)
    workflow.add_node("report_generator", report_node)
    
    # 2. Wire Edges (Supervisor Fan-Out -> Specialized Agents -> Risk Agent -> Report Synthesis)
    workflow.add_edge(START, "manager")
    
    # Manager fans out to Financial, News, SEC, and Competitor agents
    workflow.add_edge("manager", "financial_agent")
    workflow.add_edge("manager", "news_agent")
    workflow.add_edge("manager", "sec_agent")
    workflow.add_edge("manager", "competitor_agent")
    
    # Risk Agent runs after Financial and SEC data are gathered
    workflow.add_edge("financial_agent", "risk_agent")
    workflow.add_edge("sec_agent", "risk_agent")
    
    # Fan-in: News, Competitor, and Risk converge at Report Generator
    workflow.add_edge("news_agent", "report_generator")
    workflow.add_edge("competitor_agent", "report_generator")
    workflow.add_edge("risk_agent", "report_generator")
    
    workflow.add_edge("report_generator", END)
    
    return workflow.compile()

research_graph = build_graph()
