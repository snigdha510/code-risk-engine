import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def call_llm(prompt: str) -> str:
    print("🚀 Using Groq LLM...")   # 👈 ADD THIS

    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": "You are a senior software risk analyst. Always return valid JSON."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.2,
)

    return response.choices[0].message.content