import os
from notion_client import Client

class NotionStorage:
    def __init__(self, api_key, database_id):
        self.client = Client(auth=api_key)
        self.database_id = database_id

    def archive_articles(self, articles):
        """여러 기사를 한 번에 저장"""
        count = 0
        for article in articles:
            if self.create_page(article):
                count += 1
        print(f"✅ Notion 저장 완료: {count}/{len(articles)} 개")

    def create_page(self, article):
        """개별 기사를 노션에 저장 (안전장치 추가됨)"""
        try:
            # 1. 데이터 안전하게 다듬기 (Sanitizing)
            title = article.get('title', 'No Title')[:2000] # 노션 글자수 제한 방지
            url = article.get('url', '')
            
            # [핵심 수정] 요약이 리스트로 오면 글자로 합치기!
            summary = article.get('summary', '')
            if isinstance(summary, list):
                summary = "\n".join(summary)
            summary = str(summary)[:2000] # 혹시 모르니 문자열 변환 및 길이 제한

            # 태그 처리
            tags = article.get('tags', [])
            if not isinstance(tags, list):
                tags = [str(tags)]
            tag_objs = [{'name': str(t).replace(',', '')[:100]} for t in tags[:10]] # 태그 개수/길이 제한

            # 2. 노션 페이로드 만들기
            properties = {
                "Title": {"title": [{"text": {"content": title}}]},
                "URL": {"url": url if url else None},
                "Summary": {"rich_text": [{"text": {"content": summary}}]},
                "Date": {"date": {"start": (article.get('published_at') or article.get('date') or '')[:10] or None}},
                "RPi_Compatibility": {"rich_text": [{"text": {"content": str(article.get('rpi_status', 'N/A'))}}]},
                "Source": {"rich_text": [{"text": {"content": str(article.get('source', 'Unknown'))}}]},
                "Tags": {"multi_select": tag_objs}
            }

            # 3. 전송
            self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            print(f"  📝 Saved to Notion: {title[:20]}...")
            return True

        except Exception as e:
            # [핵심 수정] 에러 메시지 출력하다 죽지 않도록 안전하게 처리
            try:
                error_msg = str(e).encode('utf-8', 'ignore').decode('utf-8')
            except:
                error_msg = "Unknown Error (Encoding failed)"
                
            print(f"  ❌ Failed to save '{article.get('title', 'Unknown')[:10]}...': {error_msg}")
            return False