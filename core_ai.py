import json
import os
from typing import Generator
from openai import OpenAI

# ── Debug: confirm key is present at startup ──────────────────────────────────
print("OPENAI KEY LOADED:", os.getenv("OPENAI_API_KEY") is not None)

# ── Load glossary ─────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "glossary.json")) as f:
    GLOSSARY = json.load(f)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are CashCap AI, a humanitarian cash and market systems expert working in the context of Cash and Voucher Assistance (CVA), Market-Based Programming (MBP), and humanitarian coordination.

You MUST:
- Always interpret questions within a humanitarian context first
- Avoid generic meanings
- Clearly define acronyms (AA, MPCA, CWG, etc.)
- Provide practical, field-relevant insights
- Think like a CashCap advisor

If a question is short or ambiguous:
→ Interpret it in a humanitarian context

If no document context is available:
→ Answer using humanitarian best practices

Always structure your answer like:

### 🔍 Answer
<clear explanation>

### ⚙️ Practical Insight
<real-world use>

### 📌 Key Takeaway
<short summary>
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def enhance_query(user_question: str) -> str:
    return f"""In a humanitarian and CashCap context:

User question: {user_question}

Clarify meaning specifically within:
- CVA (Cash and Voucher Assistance)
- Market-based programming
- Humanitarian coordination

If acronym:
→ Define clearly
→ Explain practical use
"""

def check_glossary(user_question: str):
    words = user_question.upper().split()
    for word in words:
        if word in GLOSSARY:
            return word, GLOSSARY[word]
    return None, None

# ── Main AI function ──────────────────────────────────────────────────────────
def ask_cashcap_ai(user_question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "⚠️ **Server Configuration Error**: `OPENAI_API_KEY` is not set on the backend. "
            "Please add it in your Render dashboard under Environment Variables."
        )

    client = OpenAI(api_key=api_key)

    term, definition = check_glossary(user_question)

    glossary_context = ""
    if term:
        glossary_context = f"""
You are given an official CashCap glossary definition you MUST use:

**{term}**: {definition}

Start your answer with this exact definition.
"""

    full_prompt = f"""{SYSTEM_PROMPT}

{glossary_context}

{enhance_query(user_question)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": full_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ **AI Error**: {str(e)}"


# ── Streaming version ─────────────────────────────────────────────────────────
def ask_cashcap_ai_stream(user_question: str) -> Generator[str, None, None]:
    """Yields text chunks as they stream from OpenAI."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        yield "⚠️ **Server Configuration Error**: `OPENAI_API_KEY` is not set on the backend."
        return

    client = OpenAI(api_key=api_key)

    term, definition = check_glossary(user_question)
    glossary_context = ""
    if term:
        glossary_context = f"""
You are given an official CashCap glossary definition you MUST use:

**{term}**: {definition}

Start your answer with this exact definition.
"""

    full_prompt = f"""{SYSTEM_PROMPT}

{glossary_context}

{enhance_query(user_question)}
"""

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": full_prompt},
            ],
            temperature=0.3,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    except Exception as e:
        yield f"⚠️ **AI Error**: {str(e)}"
