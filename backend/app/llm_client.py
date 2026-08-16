"""
Shared LLM-calling helpers. Both generator.py (writes the scene) and
verifier.py (semantic leak check) need to call out to a model, so the
actual provider calls live here once rather than being duplicated or
creating a circular import between the two.

Provider priority: OpenAI -> Gemini -> Groq. Groq is OpenAI-API-compatible,
so it reuses the openai SDK with a different base_url and model name.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def available_provider() -> str:
    """Returns 'openai', 'gemini', 'groq', or 'none' -- whichever key is configured."""
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    return "none"


def _call_openai(prompt: str, system: str = None) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=600,
        temperature=0.9,
    )
    return resp.choices[0].message.content.strip()


def _call_gemini(prompt: str, system: str = None) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-pro")
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    resp = model.generate_content(full_prompt)
    return resp.text.strip()


def _call_groq(prompt: str, system: str = None) -> str:
    # Groq exposes an OpenAI-compatible chat completions API, so the same
    # SDK works with a different base_url and model name.
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=600,
        temperature=0.9,
    )
    return resp.choices[0].message.content.strip()


def call_model(prompt: str, system: str = None) -> tuple:
    """
    Calls whichever provider has a configured key, in priority order.
    Returns (text_or_None, mode_string). mode_string is always set, even
    on failure, so callers can report exactly what happened.
    """
    provider = available_provider()
    if provider == "none":
        return None, "no_key_configured"
    caller = {"openai": _call_openai, "gemini": _call_gemini, "groq": _call_groq}[provider]
    label = {"openai": "openai_gpt4o", "gemini": "gemini_1.5_pro", "groq": "groq_llama3.3_70b"}[provider]
    try:
        text = caller(prompt, system)
        return text, label
    except Exception as e:
        return None, f"{provider}_call_failed: {e}"
