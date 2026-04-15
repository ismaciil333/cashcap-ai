import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core_ai import ask_cashcap_ai

app = FastAPI()

# Legger til CORS slik at nettleseren din (frontend) får lov til å snakke med dette api-et
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tillater forespørsler fra uansett origin under utvikling
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/api/ask")
def ask_question(q: Question):
    try:
        answer = ask_cashcap_ai(q.question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"**API Error**: {str(e)}"}

# Serve frontend files natively from FastAPI for Render compatibility
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
def read_root():
    return FileResponse(os.path.join(base_dir, "index.html"))

app.mount("/", StaticFiles(directory=base_dir), name="static")
