import os
import sys
import webbrowser
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    print("=" * 65)
    print("  🚀 AI Financial Research Agent — Multi-Agent Swarm")
    print("  Powered by LangGraph, Google Gemini & FastAPI")
    print("=" * 65)
    
    port = int(os.getenv("PORT", "8000"))
    url = f"http://localhost:{port}"
    print(f"\n[INFO] Starting FastAPI Server on {url}")
    print(f"[INFO] Interactive Dashboard available at {url}")
    print("[INFO] Press Ctrl+C to stop the server.\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True, app_dir=str(backend_dir))

if __name__ == "__main__":
    main()
