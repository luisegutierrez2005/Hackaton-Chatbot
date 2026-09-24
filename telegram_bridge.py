"""Small Telegram polling adapter for the local CESA evidence pipeline."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from contextlib import closing
from datetime import datetime, timezone

import app
import smart

MAX_TOTAL = int(os.getenv("TELEGRAM_MAX_QUESTIONS", "50"))
MAX_PER_CHAT = int(os.getenv("TELEGRAM_MAX_PER_CHAT", "10"))
MIN_INTERVAL = 8.0


def telegram_call(token: str, method: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(request, timeout=40 if method == "getUpdates" else 15) as response:
        data = json.load(response)
    if not data.get("ok"):
        raise RuntimeError("Telegram rechazó la solicitud")
    return data


def format_reply(result: dict) -> str:
    message = result.get("answer", "No encontré una respuesta.")
    if result.get("status") == "ai_draft":
        message += "\n\nRespuesta generada a partir de fragmentos; verifica la fuente."
    sources = result.get("sources", [])
    if sources:
        links = [source.get("url", "") for source in sources if source.get("url")]
        if links:
            message += "\n\nFuentes:\n" + "\n".join(dict.fromkeys(links))
    return message[:3900]


def prepare_state(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS bot_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.commit()


def saved_offset(conn) -> int | None:
    row = conn.execute("SELECT value FROM bot_state WHERE key='telegram_next_offset'").fetchone()
    return int(row[0]) if row else None


def save_offset(conn, update_id: int) -> None:
    conn.execute("INSERT INTO bot_state(key,value) VALUES ('telegram_next_offset',?) "
                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(update_id + 1),))
    conn.commit()


def run():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN en el entorno local.")
    total = 0
    per_chat: dict[int, int] = {}
    last_at: dict[int, float] = {}
    with closing(app.connect()) as conn:
        app.seed_local(conn)
        prepare_state(conn)
        offset = saved_offset(conn)
        print("Bot CESA activo. Solo mensajes privados; Ctrl+C para detener.")
        while True:
            try:
                updates = telegram_call(token, "getUpdates", {
                    "offset": offset, "timeout": 25, "limit": 20,
                    "allowed_updates": ["message"],
                }).get("result", [])
                for update in updates:
                    update_id = update.get("update_id")
                    if not isinstance(update_id, int):
                        continue
                    message = update.get("message", {})
                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    text = message.get("text", "")
                    if chat.get("type") != "private" or not isinstance(chat_id, int):
                        save_offset(conn, update_id)
                        offset = update_id + 1
                        continue
                    if not isinstance(text, str) or not text:
                        reply = "Por ahora solo puedo responder preguntas escritas."
                    elif text.startswith(("/start", "/help")):
                        reply = ("Pregúntame por información pública del CESA, la malla aportada o los avisos "
                                 "registrados. No puedo ver tu cuenta, notas ni trámites privados de Nido.")
                    elif len(text) > 350:
                        reply = "Reduce tu pregunta a 350 caracteres o menos."
                    elif total >= MAX_TOTAL or per_chat.get(chat_id, 0) >= MAX_PER_CHAT:
                        reply = "Límite de preguntas de esta demostración alcanzado."
                    elif time.monotonic() - last_at.get(chat_id, 0) < MIN_INTERVAL:
                        reply = "Espera unos segundos antes de enviar otra pregunta."
                    else:
                        total += 1
                        per_chat[chat_id] = per_chat.get(chat_id, 0) + 1
                        last_at[chat_id] = time.monotonic()
                        reply = format_reply(smart.answer_question(text, conn))
                    telegram_call(token, "sendMessage", {"chat_id": chat_id, "text": reply})
                    save_offset(conn, update_id)
                    offset = update_id + 1
            except KeyboardInterrupt:
                print("Bot detenido.")
                break
            except Exception:
                # Do not print exception: transport errors may contain bot token URLs.
                print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}: fallo de canal; reintento")
                time.sleep(3)


if __name__ == "__main__":
    run()
