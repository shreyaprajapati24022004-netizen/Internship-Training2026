"""
ai_helper.py
------------
Handles all communication with the local Ollama instance.
Uses plain HTTP requests against Ollama's REST API so the only
external dependency is the 'requests' package.

Ollama REST docs (local): http://localhost:11434/api/generate , /api/chat
"""

import requests
import base64
import json

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_TEXT_MODEL = "llama3.2"
DEFAULT_VISION_MODEL = "llava"
REQUEST_TIMEOUT = 60          # seconds, for text requests
IMAGE_REQUEST_TIMEOUT = 180   # seconds, vision models are slower, especially on first load


def is_ollama_running() -> bool:
    """Quick check to see if the local Ollama server is reachable."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_installed_models() -> list:
    """Return a list of model names currently pulled in Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
    except requests.exceptions.RequestException:
        return []


def _model_available(model_name: str, installed: list) -> bool:
    """Ollama tags often include a version suffix like 'llama3:latest'."""
    return any(m == model_name or m.startswith(model_name + ":") for m in installed)


def chat_with_coach(user_message: str, chat_history: list, health_context: str,
                     model: str = DEFAULT_TEXT_MODEL) -> str:
    """
    Send a message to the AI Health Coach using Ollama's /api/chat endpoint.

    chat_history: list of {"role": "user"/"assistant", "content": "..."} dicts
    health_context: a text summary of the user's recent health stats
    """
    if not is_ollama_running():
        return (
            "⚠️ I can't reach Ollama right now. Please make sure the Ollama "
            "app is running, then try again. (Expected at "
            f"{OLLAMA_BASE_URL})"
        )

    system_prompt = (
        "You are a friendly, encouraging personal health and wellness coach. "
        "You are not a doctor and should always recommend seeing a medical "
        "professional for serious concerns. Use the user's real health data "
        "below to personalize your advice. Keep answers concise, warm, and "
        "actionable.\n\n"
        f"User's recent health data:\n{health_context}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "").strip() or "I didn't get a response back — try again."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error talking to Ollama: {e}"


def analyze_food_text(food_description: str, model: str = DEFAULT_TEXT_MODEL) -> str:
    """
    Ask a text model to estimate nutrition info for a described food item.
    Used as the fallback when no vision model / image is available.
    """
    if not is_ollama_running():
        return "⚠️ Ollama isn't running. Start it and try again."

    prompt = (
        "You are a nutrition analysis assistant. Given a description of a "
        "meal or food item, estimate: approximate calories, protein (g), "
        "carbs (g), fat (g), and give one short health tip about it. "
        "Be concise and use a simple bullet list. If the description is "
        "vague, make a reasonable assumption and state it briefly.\n\n"
        f"Food description: {food_description}"
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip() or "No analysis returned — try rephrasing the food description."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error talking to Ollama: {e}"


def analyze_food_image(image_bytes: bytes, model: str = DEFAULT_VISION_MODEL) -> str:
    """
    Send an image to a vision-capable Ollama model (e.g. llava) for food
    identification + nutrition estimate. Falls back with a helpful message
    if the vision model isn't installed.
    """
    if not is_ollama_running():
        return "⚠️ Ollama isn't running. Start it and try again."

    installed = get_installed_models()
    if installed and not _model_available(model, installed):
        return (
            f"⚠️ The vision model '{model}' isn't installed in Ollama yet. "
            f"Run `ollama pull {model}` in your terminal, or type the food "
            "name instead and I'll analyze it as text."
        )

    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = (
        "Identify the food in this image, then estimate: approximate "
        "calories, protein (g), carbs (g), fat (g). Give one short health "
        "tip. Be concise and use a simple bullet list."
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
    }

    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=IMAGE_REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip() or "No analysis returned — try a clearer photo."
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error talking to Ollama: {e}"