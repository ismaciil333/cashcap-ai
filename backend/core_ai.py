import json
import os
from openai import AsyncOpenAI

# Debug: confirm key
print("OPENAI KEY LOADED:", os.getenv("OPENAI_API_KEY") is not None)

# Init client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load glossary
current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "glossary.json")) as f:
    GLOSSARY = json.load(f)

# System prompt
SYSTEM_PROMPT = """You are CashCap AI, a humanitarian cash and market systems expert working in the context of Cash and Voucher Assistance (CVA), Market-Based Programming (MBP), and humanitarian coordination.

You MUST:
- Always interpret questions within a humanitarian context first
- Avoid generic meanings
- Clearly define acronyms (AA, MPCA, CWG, etc.)
- Provide practical, field-relevant insights
- Think like a CashCap advisor

Always structure your answer like:

### 🔍 Answer
<clear explanation>

### ⚙️ Practical Insight
<real-world use>

### 📌 Key Takeaway
<short summary>
"""

# Helpers
def enhance_query(user_question: str) -> str:
    return f"""In a humanitarian and CashCap context:

User question: {user_question}

Clarify meaning within:
- CVA
- Market-based programming
- Humanitarian coordination
"""

def check_glossary(user_question: str):
    words = user_question.upper().split()
    for word in words:
        if word in GLOSSARY:
            return word, GLOSSARY[word]
    return None, None


# ✅ NORMAL RESPONSE (fallback)
async def ask_cashcap_ai(user_question: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "⚠️ API key missing."

    term, definition = check_glossary(user_question)

    glossary_context = ""
    if term:
        glossary_context = f"{term}: {definition}"

    full_prompt = f"""{SYSTEM_PROMPT}

{glossary_context}

{enhance_query(user_question)}
"""

    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=full_prompt
        )

        return response.output_text

    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# 🚀 STREAMING RESPONSE (FIXED)
async def ask_cashcap_ai_stream(user_question: str):
    if not os.getenv("OPENAI_API_KEY"):
        yield "⚠️ API key missing."
        return

    term, definition = check_glossary(user_question)

    glossary_context = ""
    if term:
        glossary_context = f"{term}: {definition}"

    full_prompt = f"""{SYSTEM_PROMPT}

{glossary_context}

{enhance_query(user_question)}
"""

    try:
        stream = await client.responses.stream(
            model="gpt-4o-mini",
            input=full_prompt
        )

        async for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta

    except Exception as e:
        yield f"\n\n⚠️ Streaming Error: {str(e)}"
