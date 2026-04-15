import os
import json
from openai import OpenAI

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "glossary.json")) as f:
    GLOSSARY = json.load(f)

client = OpenAI()

SYSTEM_PROMPT = """
You are CashCap AI, a humanitarian cash and market systems expert working in the context of Cash and Voucher Assistance (CVA), Market-Based Programming (MBP), and humanitarian coordination.

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

### 📚 Glossary Update (if needed)
- <term → definition>
"""

def enhance_query(user_question: str):
    return f"""
In a humanitarian and CashCap context:

User question: {user_question}

Clarify meaning specifically within:
- CVA
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
    term, definition = check_glossary(user_question)

    glossary_context = ""
    if term:
        glossary_context = f"""
You are given an official glossary from CashCap.

You MUST use these definitions exactly.

Term:
{term}

Definition:
{definition}

If the user asks about this term:
→ Start your answer with this exact definition
"""

    prompt = f"""
{SYSTEM_PROMPT}

{glossary_context}

Question:
{enhance_query(user_question)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
