import json
import os
from openai import OpenAI

with open("glossary.json") as f:
    GLOSSARY = json.load(f)

SYSTEM_PROMPT = """
You are CashCap AI, a humanitarian expert in CVA and market-based programming.

Always:
- Define acronyms first
- Use humanitarian context
- Be clear and practical

Structure:

### 🔍 Answer
### ⚙️ Practical Insight
### 📌 Key Takeaway
"""

def enhance_query(user_question: str):
    return f"""
User question: {user_question}

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

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # 🔥 FIX

    term, definition = check_glossary(user_question)

    glossary_context = ""
    if term:
        glossary_context = f"""
Term: {term}
Definition: {definition}

You MUST use this definition.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": glossary_context},
            {"role": "user", "content": enhance_query(user_question)}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
