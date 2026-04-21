from fastapi import FastAPI
from pydantic import BaseModel
from core_ai import ask_cashcap_ai
from fastapi.middleware.cors import CORSMiddleware
import json, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load glossary once at startup ─────────────────────────────────────────────
_dir = os.path.dirname(os.path.abspath(__file__))
_glossary_path = os.path.join(_dir, "glossary.json")
with open(_glossary_path) as f:
    _GLOSSARY_RAW: dict = json.load(f)

class Question(BaseModel):
    question: str

@app.get("/")
def health():
    return {"status": "CashCap AI backend is running ✅"}

@app.get("/glossary")
def get_glossary():
    """Return all glossary terms as a structured list, sorted alphabetically."""
    return [
        {
            "term": term,
            "definition": definition,
            "source": "CashCap Glossary Document"
        }
        for term, definition in sorted(_GLOSSARY_RAW.items())
    ]

@app.post("/ask")
def ask(q: Question):
    try:
        answer = ask_cashcap_ai(q.question)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"⚠️ **Server Error**: {str(e)}"}

