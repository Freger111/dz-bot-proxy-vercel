# ДЗ-Бот · бэкенд на Vercel

Serverless-прокси: держит ключ LLM в переменных окружения Vercel.
Приложение на телефоне получает только адрес.

## Деплой (5 минут)

1. <https://vercel.com> → **Sign up with GitHub** (бесплатно, без карты).
2. **Add New → Project**.
3. **Import Git Repository** → выбери `dz-bot-proxy-vercel`.
4. Framework Preset: **Other** (Vercel сам поймёт Python).
5. **Environment Variables** — добавь:
   - `LLM_BASE_URL` = `https://openrouter.ai/api/v1`
   - `LLM_API_KEY` = ключ OpenRouter (`sk-or-v1-...`)
   - `LLM_MODEL` = `nvidia/nemotron-3.5-super-vl:free`
   - `FALLBACK_BASE_URL` = `https://generativelanguage.googleapis.com/v1beta/openai/`
   - `FALLBACK_API_KEY` = ключ Gemini (`AQ...`)
   - `FALLBACK_MODEL` = `gemini-3.5-flash`
6. **Deploy** → 1–2 минуты.
7. Получишь адрес вида `https://dz-bot-proxy-vercel.vercel.app`.

## Проверка

```
https://<твой-проект>.vercel.app/health
```
→ `{"ok": true, "model": "..."}`

## Эндпоинты

- `GET /health`
- `POST /api/chat` — `{"messages": [...]}` → `{"reply": "..."}`
