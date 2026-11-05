
import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def generate_llm_text(system_prompt, user_prompt, max_tokens=250):
    token = os.getenv("GROQ_API_KEY")

    if not token:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"Groq API error {response.status_code}: {response.text}"
        )

    result = response.json()
    content = result["choices"][0]["message"]["content"].strip()

    if not content:
        raise RuntimeError("Groq returned an empty response.")

    print(f"[LLM] Successful inference using {GROQ_MODEL}")
    return content
