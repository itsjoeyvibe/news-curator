"""
Research Radar - Self-Driving Research Assistant
Main orchestrator for the automated research pipeline.
"""

import os
import sys
from dotenv import load_dotenv
from scrapers import aggregate_all_sources
from ai_agent import GeminiAgent
from notifier import send_telegram_notification, fetch_weather
from notion_storage import NotionStorage
import re
import time

# Rate limiting for external APIs (seconds). Configure via env `RATE_LIMIT_SECONDS`.
RATE_LIMIT_SECONDS = int(os.environ.get('RATE_LIMIT_SECONDS', '15'))

def extract_github_url(text: str) -> str:
    """Extract GitHub URL from text if present."""
    match = re.search(r'https?://github\.com/[^\s]+', text)
    return match.group(0) if match else None

def main():
    """Main execution function."""
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_vars = [
        'GEMINI_API_KEY',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
        'NOTION_API_KEY',
        'NOTION_DB_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Initialize components
    print("🚀 Research Radar - Starting Daily Briefing...\n")
    
    gemini_agent = GeminiAgent(os.environ['GEMINI_API_KEY'])
    notion_storage = NotionStorage(
        os.environ['NOTION_API_KEY'],
        os.environ['NOTION_DB_ID']
    )
    
    city = os.environ.get('MY_CITY', 'Seoul')
    
    try:
        # Step 1: Aggregate articles from all sources
        print("--------------------------------------------------")
        print("📡 [Step 1] Fetching news from 5 sources...")
        all_articles = aggregate_all_sources()
        
        # [CCTV 1] 수집된 개수 확인
        print(f"🧐 [DEBUG] 총 수집된 원본 기사: {len(all_articles)} 개")
        
        if not all_articles:
            print("❌ [CRITICAL] 스크래퍼가 0개를 가져왔습니다. scrapers.py나 네트워크를 확인하세요.")
            return

        # 샘플 확인 (잘 가져왔는지 제목만 살짝 보기)
        print(f"   (Sample) 첫번째 기사 제목: {all_articles[0].get('title', 'No Title')}")
        print("--------------------------------------------------\n")
        
        # Step 2: Filter for relevance using Gemini
        print("🧠 [Step 2] Filtering articles with Gemini...")
        relevant_articles = []
        
        for i, article in enumerate(all_articles):
            # 너무 오래 걸리면 지루하니까 진행 상황 표시
            print(f"  [{i+1}/{len(all_articles)}] Analyzing: {article.get('title', 'Unknown')[:40]}...")
            
            # API rate limiting (configurable via RATE_LIMIT_SECONDS)
            time.sleep(RATE_LIMIT_SECONDS)

            result = gemini_agent.filter_relevance(article)
            
            if result and result.get('is_relevant'):
                print(f"    ✅ Relevant! (Summary: {result.get('summary')[:30]}...)")
                article['summary'] = result.get('summary', 'No summary')
                article['tags'] = result.get('tags', [])
                relevant_articles.append(article)
            else:
                print("    🗑️ Not relevant.")
        
        print(f"\n✅ [Result] Gemini가 승인한 기사: {len(relevant_articles)} 개")
        
        if not relevant_articles:
            print("⚠️ 관련 기사가 0개입니다. (스크래퍼는 성공했으나 AI가 다 거름)")
            print("📱 빈 메시지라도 보내서 봇 생존 신고를 합니다...")
            # 빈 메시지 전송 시도 (400 에러 방지용 멘트 추가)
            send_telegram_notification(
                os.environ['TELEGRAM_BOT_TOKEN'],
                os.environ['TELEGRAM_CHAT_ID'],
                [],
                city,
                "오늘은 Edge AI 관련 뉴스가 없습니다. (시스템은 정상 작동 중)"
            )
            return
        
        # Step 3: Audit GitHub repositories
        print("\n🔍 [Step 3] Auditing GitHub Repos (RPi 5 Check)...")
        for article in relevant_articles:
            # URL과 본문에서 깃허브 링크 찾기
            content_to_search = (article.get('url', '') or '') + ' ' + (article.get('raw_content', '') or '')
            github_url = extract_github_url(content_to_search)
            
            if github_url:
                print(f"  Auditing: {github_url}")
                article['rpi_status'] = gemini_agent.audit_github_repo(github_url)
            else:
                article['rpi_status'] = 'N/A'
        
        # Step 4: Weather & Wit
        print(f"\n🌤️ [Step 4] Fetching weather for {city}...")
        weather = fetch_weather(city)
        print(f"  Weather: {weather}")
        
        print("🤖 Generating witty closing remark...")
        weather_wit = gemini_agent.generate_weather_wit(city, weather)
        
        # Step 5: Notion
        print("\n📝 [Step 5] Archiving to Notion...")
        notion_storage.archive_articles(relevant_articles)
        
        # Step 6: Telegram
        print("\n📱 [Step 6] Sending Telegram notification...")
        send_telegram_notification(
            os.environ['TELEGRAM_BOT_TOKEN'],
            os.environ['TELEGRAM_CHAT_ID'],
            relevant_articles,
            city,
            weather_wit,
            weather=weather
        )
        
        print("\n✅ Research Radar Daily Briefing completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()