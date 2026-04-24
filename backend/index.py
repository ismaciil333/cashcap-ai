import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from core_ai import ask_cashcap_ai, ask_cashcap_ai_stream

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str


# ✅ NORMAL ENDPOINT (fallback)
@app.post("/api/ask")
async def ask_question(q: Question):
    try:
        answer = await ask_cashcap_ai(q.question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"**API Error**: {str(e)}"}


# 🚀 STREAMING ENDPOINT
@app.post("/api/ask-stream")
async def ask_stream(request: Request):
    data = await request.json()
    question = data.get("question")

    async def generator():
        try:
            async for chunk in ask_cashcap_ai_stream(question):
                yield chunk
        except Exception as e:
            yield f"\n\n⚠️ Error: {str(e)}"

    return StreamingResponse(generator(), media_type="text/plain")


# 🌐 Serve frontend (Render)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(os.path.join(base_dir, "index.html")):
    @app.get("/")
    def read_root():
        return FileResponse(os.path.join(base_dir, "index.html"))

    app.mount("/", StaticFiles(directory=base_dir), name="static")
