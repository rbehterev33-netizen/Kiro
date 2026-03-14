"""
Telegram-уведомления для Currency Tracker
Отправляет алерты когда курс пробивает пороговое значение.

Настройка:
  1. Создайте бота через @BotFather → получите TELEGRAM_BOT_TOKEN
  2. Узнайте свой chat_id через @userinfobot → TELEGRAM_CHAT_ID
  3. Добавьте в .env:
       TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
       TELEGRAM_CHAT_ID=123456789
"""

import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("telegram")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")


def is_configured() -> bool:
    return bool(BOT_TOKEN and CHAT_ID)


def send_message(text: str) -> bool:
    """Отправить сообщение в Telegram. Возвращает True при успехе."""
    if not is_configured():
        logger.debug("Telegram не настроен (нет BOT_TOKEN/CHAT_ID в .env)")
        return False
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id":    CHAT_ID,
            "text":       text,
            "parse_mode": "HTML",
        }, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Telegram ошибка отправки: {e}")
        return False


def send_alert(alert: dict) -> bool:
    """Форматирует и отправляет алерт из check_alerts()"""
    pair    = alert.get("currency_pair", "?")
    atype   = alert.get("alert_type", "")
    message = alert.get("message", "")

    icon = "📈" if "above" in atype or "выше" in message.lower() else "📉"
    text = (
        f"{icon} <b>Currency Alert</b>\n"
        f"Пара: <b>{pair}</b>\n"
        f"Тип: {atype}\n"
        f"{message}"
    )
    return send_message(text)


def send_daily_summary(rates: list[dict]) -> bool:
    """Отправить ежедневную сводку топ-5 курсов"""
    if not rates:
        return False
    lines = ["📊 <b>Ежедневная сводка курсов</b>\n"]
    for r in rates[:5]:
        lines.append(f"• <b>{r['currency_pair']}</b>: {float(r['rate']):.4f} ({r['source_name']})")
    return send_message("\n".join(lines))
