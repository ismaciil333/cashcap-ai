from fastapi import FastAPI
from pydantic import BaseModel
from core_ai import ask_cashcap_ai
from fastapi.middleware.cors import CORSMiddleware

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

@app.post("/ask")
def ask(q: Question):
    return {"answer": ask_cashcap_ai(q.question)}
