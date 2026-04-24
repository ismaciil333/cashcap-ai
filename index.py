import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from core_ai import ask_cashcap_ai, ask_cashcap_ai_stream

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

# ── Streaming endpoint (rask – tekst vises ord for ord) ───────────────────────
@app.post("/ask/stream")
@app.post("/api/ask/stream")
def ask_stream(q: Question):
    def generator():
        for chunk in ask_cashcap_ai_stream(q.question):
            # Send kvert chunk som Server-Sent Event
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Fortell Nginx/Render å ikke buffe
        },
    )

# ── Vanlig (ikke-streaming) endpoint – beholdt som fallback ───────────────────
@app.post("/ask")
@app.post("/api/ask")
def ask_question(q: Question):
    try:
        answer = ask_cashcap_ai(q.question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"**API Error**: {str(e)}"}

# ── Serve frontend ─────────────────────────────────────────────────────────────
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(os.path.join(base_dir, "index.html")):
    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(base_dir, "index.html"))

    app.mount("/", StaticFiles(directory=base_dir), name="static")
