"""Run a safe local simulation of main.py with all external calls mocked.

This script sets required environment variables, replaces network-bound
functions/classes with lightweight mocks, and calls main.main(). It
prevents real network calls to Gemini, Notion, Telegram, and scrapers.
"""

import os
import traceback

# Configure fast rate limit before importing main (main reads env at import)
os.environ.setdefault('RATE_LIMIT_SECONDS', '0')

# Required env vars to pass main validation
os.environ.setdefault('GEMINI_API_KEY', 'DUMMY')
os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'DUMMY')
os.environ.setdefault('TELEGRAM_CHAT_ID', '123456')
os.environ.setdefault('NOTION_API_KEY', 'DUMMY')
os.environ.setdefault('NOTION_DB_ID', 'DUMMY')
os.environ.setdefault('MY_CITY', 'Seoul')

def make_sample_articles():
    return [
        {
            'title': 'TinyML model compression for microcontrollers',
            'url': 'https://example.com/tinyml-compress',
            'source': 'Hacker News',
            'date': '2026-01-28T00:00:00',
            'raw_content': 'Repo: https://github.com/example/tinyml-compress',
        },
        {
            'title': 'CUDA-only vision transformer',
            'url': 'https://example.com/cuda-vt',
            'source': 'arXiv',
            'date': '2026-01-27T00:00:00',
            'raw_content': 'This project relies on CUDA.'
        }
    ]

class MockGeminiAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def filter_relevance(self, article):
        # Simple heuristic: mark first as relevant, second not
        if 'TinyML' in article.get('title', ''):
            return {
                'is_relevant': True,
                'summary': '• TinyML 모델 압축; RPi 가능성 높음',
                'tags': ['TinyML', 'Compression']
            }
        return {'is_relevant': False}

    def audit_github_repo(self, github_url):
        if 'cuda' in github_url.lower():
            return '❌ CUDA/x86 Only'
        return '✅ Runnable'

    def generate_weather_wit(self, city, weather_string):
        return f"{city} 날씨라면 디버깅하기 딱이네요! ☕"

class MockNotionStorage:
    def __init__(self, api_key, database_id):
        self.api_key = api_key
        self.database_id = database_id

    def archive_articles(self, articles):
        print(f"[MockNotion] Would archive {len(articles)} articles")

def mock_send_telegram_notification(bot_token, chat_id, articles, city, weather_wit, weather=None):
    print(f"[MockTelegram] bot={bot_token[:6]}... chat={chat_id} articles={len(articles)} city={city}")
    return True

def mock_fetch_weather(city, timeout=5):
    return "☀️ 12°C"

def mock_aggregate_all_sources():
    return make_sample_articles()

def run():
    try:
        import main

        # Patch functions/classes used by main
        main.GeminiAgent = MockGeminiAgent
        main.NotionStorage = MockNotionStorage
        main.send_telegram_notification = mock_send_telegram_notification
        main.fetch_weather = mock_fetch_weather
        main.aggregate_all_sources = mock_aggregate_all_sources

        # Run main
        main.main()

    except SystemExit as e:
        print(f"main() exited with SystemExit: {e}")
    except Exception:
        print("Unhandled exception during simulation:")
        traceback.print_exc()

if __name__ == '__main__':
    run()
