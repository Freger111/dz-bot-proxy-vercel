"""Бэкенд-прокси для ДЗ-Бота · версия для Vercel (serverless).

Ключ LLM лежит в переменных окружения Vercel, приложение его не видит.
"""
import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "nvidia/nemotron-3.5-super-vl:free").strip()

FALLBACK_BASE_URL = os.getenv("FALLBACK_BASE_URL", "").strip()
FALLBACK_API_KEY = os.getenv("FALLBACK_API_KEY", "").strip()
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "").strip()

APP_TOKEN = os.getenv("APP_TOKEN", "").strip()

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "Ты — сильный репетитор. Решай задачи пошагово: «Дано» → «Решение» → «Ответ». "
    "Формулы — обычным текстом (x², √(2), ∠ABC, ⊥, ∥, α, β, π), без LaTeX. "
    "Если данных не хватает — задай уточняющий вопрос. Отвечай на языке вопроса.",
).strip()

app = FastAPI(title="ДЗ-Бот proxy (Vercel)")


class ChatIn(BaseModel):
    messages: list[dict]
    model: str | None = None


@app.get("/health")
def health() -> dict:
    return {"ok": True, "model": LLM_MODEL}


@app.post("/api/chat")
async def chat(inp: ChatIn, request: Request) -> dict:
    if APP_TOKEN and request.headers.get("X-App-Token") != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Неверный токен приложения")
    if not LLM_API_KEY:
        raise HTTPException(status_code=500, detail="LLM_API_KEY не задан")

    messages = inp.messages
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    providers = [(LLM_BASE_URL, LLM_API_KEY, LLM_MODEL)]
    if FALLBACK_BASE_URL and FALLBACK_API_KEY and FALLBACK_MODEL:
        providers.append((FALLBACK_BASE_URL, FALLBACK_API_KEY, FALLBACK_MODEL))

    last_error = "нет провайдеров"
    for base, key, model in providers:
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(
                    base.rstrip("/") + "/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": inp.model or model,
                        "messages": messages,
                        "temperature": 0.5,
                    },
                )
        except Exception as e:  # noqa: BLE001
            last_error = f"{model}: {type(e).__name__}"
            continue

        if r.status_code != 200:
            last_error = f"{model}: HTTP {r.status_code} {r.text[:200]}"
            continue

        data = r.json()
        reply = (
            ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        ).strip()
        if reply:
            return {"reply": reply}
        last_error = f"{model}: пустой ответ"

    raise HTTPException(status_code=502, detail=last_error)
