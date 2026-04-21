import json
import os

_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_dir, "glossary.json")) as f:
    GLOSSARY = json.load(f)

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

def enhance_query(user_question: str):
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

def check_glossary(user_question):
    words = user_question.upper().split()
    for word in words:
        if word in GLOSSARY:
            return word, GLOSSARY[word]
    return None, None

def ask_cashcap_ai(user_question: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ **Server Configuration Error**: `GEMINI_API_KEY` is not set on the backend. Please add it in your Render dashboard under Environment Variables."

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        return f"⚠️ **Backend Error**: Failed to initialise Gemini — {str(e)}"

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
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"⚠️ **AI Error**: {str(e)}"
