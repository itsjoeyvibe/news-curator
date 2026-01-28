"""
Telegram notification module with weather API integration.
"""

import os
import requests
import html
from typing import List, Dict, Optional


def fetch_weather(city: str, timeout: int = 5) -> str:
    """
    Fetch current weather for a city using wttr.in API.
    
    Args:
        city: City name (e.g., 'Seoul', 'Daejeon')
        timeout: Request timeout in seconds (default: 5)
    
    Returns:
        Weather string (e.g., "☀️ 15°C") or "Unknown" on failure
    """
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"Weather API error (non-critical): {e}")
        return "Unknown"


def send_telegram_notification(
    bot_token: str,
    chat_id: str,
    articles: List[Dict],
    city: str,
    weather_wit: str,
    weather: Optional[str] = None
) -> bool:
    """
    Send formatted notification to Telegram.
    
    Args:
        bot_token: Telegram bot token
        chat_id: Telegram chat ID
        articles: List of relevant articles with summaries
        city: City name for weather display
        weather: Weather string
        weather_wit: Witty remark from AI
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if weather is None:
            weather = fetch_weather(city)

        # Build message using HTML mode and escape user content
        message_parts = []
        message_parts.append('<b>📡 Research Radar Daily Briefing</b>')
        message_parts.append(f'Found {len(articles)} insights.')

        for idx, article in enumerate(articles, 1):
            title = html.escape(str(article.get('title', 'No Title')))
            summary = html.escape(str(article.get('summary', 'No summary')))
            rpi_status = html.escape(str(article.get('rpi_status', '❓ Unknown')))
            url_link = article.get('url', '') or ''

            entry = f"{idx}. <b>{title}</b>\n"
            entry += f"   💡 {summary}\n"
            entry += f"   🛠 RPi Status: {rpi_status}\n"
            if url_link:
                entry += f"   🔗 <a href=\"{html.escape(url_link)}\">Link</a>\n"

            message_parts.append(entry)

        message_parts.append('---')
        message_parts.append(f'🌡 <b>{html.escape(city)}:</b> {html.escape(weather)}')
        message_parts.append(f'🤖 <b>Comment:</b> "{html.escape(weather_wit)}"')

        message = "\n".join(message_parts)

        # Send via Telegram Bot API
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        print("✅ Telegram notification sent successfully")
        return True

    except requests.exceptions.RequestException as e:
        # Avoid printing sensitive tokens; log error only
        print(f"❌ Error sending Telegram notification: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error in send_telegram_notification: {e}")
        return False
