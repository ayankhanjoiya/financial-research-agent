import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.config import settings
from core.graph import research_graph
from core.state import ResearchState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("financial_agent")

app = FastAPI(
    title="AI Financial Research Multi-Agent API",
    description="Autonomous multi-agent equity research assistant powered by LangGraph, Gemini, and SEC EDGAR.",
    version="1.0.0"
)

# Enable CORS for Next.js and local UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for recent research results
RESEARCH_CACHE: Dict[str, Dict[str, Any]] = {}

class ResearchRequest(BaseModel):
    ticker: str

class ResearchResponse(BaseModel):
    ticker: str
    company_name: str
    status: str
    final_report: Optional[str] = None
    agent_logs: list = []

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "model": settings.GEMINI_MODEL
    }

@app.post("/api/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    """Run full synchronous research graph for a given ticker."""
    ticker = request.ticker.strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker symbol is required.")
        
    initial_state: ResearchState = {
        "ticker": ticker,
        "company_name": ticker,
        "agent_logs": [],
        "errors": []
    }
    
    try:
        final_state = await asyncio.to_thread(research_graph.invoke, initial_state)
        RESEARCH_CACHE[ticker] = final_state
        return ResearchResponse(
            ticker=ticker,
            company_name=final_state.get("company_name", ticker),
            status="completed",
            final_report=final_state.get("final_report"),
            agent_logs=final_state.get("agent_logs", [])
        )
    except Exception as e:
        logger.error(f"Error executing research graph for {ticker}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/research/{ticker}")
async def get_research(ticker: str):
    """Retrieve cached research report and sub-agent payloads for a ticker."""
    clean_ticker = ticker.strip().upper()
    if clean_ticker not in RESEARCH_CACHE:
        raise HTTPException(status_code=404, detail=f"No research found for ticker {clean_ticker}. Run research first.")
    return RESEARCH_CACHE[clean_ticker]

@app.get("/api/research/stream/{ticker}")
async def stream_research(ticker: str):
    """Server-Sent Events (SSE) endpoint to stream agent node events in real-time."""
    clean_ticker = ticker.strip().upper()
    if not clean_ticker:
        raise HTTPException(status_code=400, detail="Ticker is required.")

    async def event_generator():
        initial_state: ResearchState = {
            "ticker": clean_ticker,
            "company_name": clean_ticker,
            "agent_logs": [],
            "errors": []
        }
        
        yield f"data: {json.dumps({'event': 'start', 'message': f'Initializing research graph for {clean_ticker}'})}\n\n"
        
        try:
            # Stream graph updates node by node
            accumulated_state = dict(initial_state)
            
            # Run stream in thread
            def generate_chunks():
                return list(research_graph.stream(initial_state, stream_mode="updates"))

            chunks = await asyncio.to_thread(generate_chunks)
            
            for update in chunks:
                for node_name, node_output in update.items():
                    logs = node_output.get("agent_logs", [])
                    latest_msg = logs[-1]["message"] if logs else f"{node_name} completed."
                    
                    # Merge into accumulated state
                    accumulated_state.update(node_output)
                    
                    payload = {
                        "event": "node_update",
                        "node": node_name,
                        "message": latest_msg,
                        "logs": logs,
                        "current_state": {
                            "company_name": accumulated_state.get("company_name", clean_ticker),
                            "sector": accumulated_state.get("sector", ""),
                            "financial_data": bool(accumulated_state.get("financial_data")),
                            "news_data": bool(accumulated_state.get("news_data")),
                            "sec_filing_data": bool(accumulated_state.get("sec_filing_data")),
                            "competitor_data": bool(accumulated_state.get("competitor_data")),
                            "risk_data": bool(accumulated_state.get("risk_data")),
                        }
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0.05)

            RESEARCH_CACHE[clean_ticker] = accumulated_state
            
            final_payload = {
                "event": "complete",
                "ticker": clean_ticker,
                "company_name": accumulated_state.get("company_name", clean_ticker),
                "final_report": accumulated_state.get("final_report"),
                "report_html": accumulated_state.get("report_html"),
                "financial_data": accumulated_state.get("financial_data"),
                "news_data": accumulated_state.get("news_data"),
                "sec_filing_data": accumulated_state.get("sec_filing_data"),
                "competitor_data": accumulated_state.get("competitor_data"),
                "risk_data": accumulated_state.get("risk_data"),
                "agent_logs": accumulated_state.get("agent_logs", [])
            }
            yield f"data: {json.dumps(final_payload)}\n\n"
            
        except Exception as e:
            logger.error(f"Stream error for {clean_ticker}: {e}", exc_info=True)
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Mount Static Dashboard UI
static_dir = Path(__file__).resolve().parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Financial Research Agent API is running. UI not found.</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
