from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse
from app.rag import handle_query
import time

app = FastAPI(title="SuperExpat AI Agent API", version="1.0.0")

# ======================
# CORS (MANDATORY)
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vercel / localhost / public
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# HEALTH CHECK
# ======================
@app.get("/api/status")
def status():
    return {
        "status": "ok",
        "service": "SuperExpat AI Agent",
    }

# ======================
# METRICS (Frontend needs this)
# ======================
@app.get("/api/metrics")
def metrics():
    return {
        "avg_response_ms": 1200,
        "status": "healthy"
    }

# ======================
# CHAT ENDPOINT
# ======================
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    start = time.time()
    result = handle_query(
        query=req.message,
        page=req.page,
        page_size=req.page_size
    )
    return result
