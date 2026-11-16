# AI Financial Research Multi-Agent System

An institutional-grade, multi-agent equity research assistant built with **LangGraph**, **Google Gemini**, **FastAPI**, and **Next.js**. Given any public company ticker (e.g. `NVDA`, `AAPL`, `MSFT`), the system coordinates a swarm of specialized domain agents to extract, cross-validate, and synthesize an exhaustive investment research memorandum.

---

## 🏛️ System Architecture

The system utilizes an asynchronous **Supervisor Fan-Out / Fan-In Map-Reduce** workflow powered by LangGraph:

```mermaid
flowchart TD
    User([User: Inputs Ticker e.g. NVDA]) --> Manager[Manager / Supervisor Agent]
    
    subgraph Parallel Research Swarm
        Manager -->|Task: Financials & Statements| FinAgent[Financial Data Agent\n- yfinance API\n- Balance Sheet, Income, FCF\n- Valuation Multiples]
        Manager -->|Task: 90-Day Catalysts| NewsAgent[News & Sentiment Agent\n- DuckDuckGo / Yahoo News\n- Earnings commentary\n- Bull/Bear Sentiment]
        Manager -->|Task: SEC 10-K Filings| SecAgent[Annual Report Agent\n- SEC EDGAR API\n- Item 1, 1A (Risk), Item 7 (MD&A)]
        Manager -->|Task: Peer Landscape| CompAgent[Competitor Agent\n- Peer group benchmarking\n- Relative valuation\n- Economic Moat Analysis]
        Manager -->|Task: Threat Vectors| RiskAgent[Risk Analysis Agent\n- Debt & Liquidity stress-test\n- Macro & Regulatory risks\n- Risk Impact Matrix]
    end

    FinAgent --> Aggregator[State Aggregator & Validation Barrier]
    NewsAgent --> Aggregator
    SecAgent --> Aggregator
    CompAgent --> Aggregator
    RiskAgent --> Aggregator

    Aggregator --> Synthesizer[Report Generator Agent\n- Wall Street Research Persona\n- Bull / Base / Bear thesis\n- Formatted Markdown & HTML/PDF]
    
    Synthesizer --> Output([FastAPI Server / Next.js Dashboard])
```

---

## 🤖 Domain Agents

| Agent | Responsibility | Data Sources |
| :--- | :--- | :--- |
| **Manager Agent** | Validates ticker, extracts basic profile, initializes graph telemetry. | `yfinance.Ticker.info` |
| **Financial Data Agent** | Analyzes 3-year income, balance sheet, cash flow, margins, and valuation multiples. | `yfinance` financial statements |
| **News Research Agent** | Surfaces recent material catalysts, sentiment verdict (Bullish/Neutral/Bearish), and headline risks. | Yahoo Finance News RSS & DuckDuckGo |
| **Annual Report Agent** | Extracts and analyzes structural advantages, risk factors (Item 1A), and MD&A (Item 7) from official 10-K SEC filings. | SEC EDGAR Public REST API |
| **Competitor Agent** | Identifies peer group, relative valuation multiples, and economic moat durability. | Peer ticker benchmarking |
| **Risk Analysis Agent** | Combines financial leverage, SEC risk factors, and macroeconomic sensitivities into an actionable risk matrix. | Aggregated financials + 10-K disclosures |
| **Report Generator Agent** | Synthesizes all domain intelligence into an institutional-grade investment research report. | LangGraph unified state |

---

## 🛠️ Tech Stack

* **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (cyclic graph, parallel fan-out/fan-in)
* **LLM Engine**: Google Gemini (via `langchain-google-genai`)
* **Backend API**: [FastAPI](https://fastapi.tiangolo.com/) with Server-Sent Events (SSE) for live streaming
* **Data Sources (100% Free Tier)**:
  * Financials: `yfinance`
  * SEC Filings: SEC EDGAR REST API
  * Web Search: DuckDuckGo Search API
* **Frontend UI**: Next.js & Tailwind CSS (plus standalone web app served via FastAPI)

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* Free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/ayankhanjoiya/financial-research-agent.git
cd financial-research-agent

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env and insert your GEMINI_API_KEY
```

### 3. Run the Backend API
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```
Open `http://localhost:8000` in your browser to view the interactive dashboard.

---

## 📄 License
MIT License. For educational and research purposes.
