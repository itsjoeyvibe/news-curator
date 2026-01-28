import os
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiAgent:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        
        # 1. 모델 설정 (안전한 이름으로 변경)
        # 'gemini-1.5-flash' 대신 'gemini-1.5-flash-latest' 사용
        self.model = genai.GenerativeModel('gemini-flash-latest')
        
        # 2. 안전 설정 (필터링 너무 빡세게 안 하도록)
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

    def _clean_json_text(self, text):
        """Markdown 코드 블록(```json ... ```)을 제거하고 순수 JSON만 남김"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def filter_relevance(self, article):
        """뉴스가 관련 있는지 판단하고 요약"""
        prompt = f"""
        You are an expert AI Researcher specializing in Edge AI, Computer Vision, and Embedded Systems.
        
        Analyze this article:
        - Title: {article.get('title')}
        - Content: {article.get('summary', '')} {article.get('tags', '')}
        
        Is this article strictly relevant to:
        1. Edge AI / TinyML / On-device AI
        2. Computer Vision (YOLO, Object Detection, etc.)
        3. Raspberry Pi / NVIDIA Jetson / Embedded Hardware
        4. Model Optimization (Quantization, Pruning)
        
        Ignore generic AI news (like ChatGPT updates), crypto, or web dev.
        
        Return a JSON object ONLY:
        {{
            "is_relevant": true/false,
            "summary": "Summarize in 3 short Korean bullet points (Use emojis)",
            "tags": ["Tag1", "Tag2"]
        }}
        """
        
        try:
            response = self.model.generate_content(
                prompt, 
                safety_settings=self.safety_settings
            )
            
            cleaned_text = self._clean_json_text(response.text)
            return json.loads(cleaned_text)
            
        except Exception as e:
            print(f"⚠️ Error filtering article '{article.get('title', '')[:20]}...': {e}")
            return None

    def audit_github_repo(self, github_url):
        """GitHub 리포지토리가 RPi 5에서 돌아갈지 예측"""
        prompt = f"""
        Analyze this GitHub repository URL: {github_url}
        
        Predict if this project can run on a Raspberry Pi 5 (8GB RAM, ARM64 CPU).
        Check for:
        - Heavy CUDA dependencies (NVIDIA only?) -> ❌
        - x86 only binaries? -> ❌
        - Lightweight enough? -> ✅
        
        Return just one string from: "✅ Runnable", "⚠️ Heavy/Slow", "❌ CUDA/x86 Only", "❓ Unknown"
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "❓ Check Manually"

    def generate_weather_wit(self, city, weather_string):
        """날씨에 맞는 드립 생성"""
        prompt = f"""
        Current weather in {city} is: {weather_string}.
        
        Write a short, witty, one-sentence closing remark for an AI Engineer.
        Themes: Coding, Debugging, Coffee, GPUs, Deployment.
        Language: Korean.
        
        Example: "비도 오는데 모델 학습이나 돌려놓고 파전 먹으러 가시죠. ☔️"
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return "오늘도 즐거운 코딩 되세요! ☕️"