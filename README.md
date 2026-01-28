# Research Radar 🛰️

**Self-Driving Research Assistant** - An automated pipeline that aggregates, filters, and analyzes tech news focused on Edge AI, Computer Vision, and Hardware.

## 🌟 Features

- **5 Data Sources**: Hacker News, Reddit (r/LocalLLaMA, r/ComputerVision, r/TinyML), arXiv, Hugging Face, Google News
- **AI-Powered Filtering**: Uses Google Gemini 1.5 Flash for semantic relevance filtering
- **GitHub Repository Auditing**: Automatically checks if projects are compatible with Raspberry Pi 5
- **Telegram Notifications**: Daily briefings with weather-based witty remarks
- **Notion Archiving**: Structured storage of all relevant articles
- **Serverless Execution**: Runs daily via GitHub Actions (no infrastructure costs)

## 🏗️ Architecture

```
┌─────────────┐
│   Sources   │ → Hacker News, Reddit, arXiv, HuggingFace, Google News
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Scrapers   │ → Aggregate articles
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Gemini AI   │ → Filter relevance, audit repos, generate wit
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Notifier   │ → Telegram + Weather API
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Notion    │ → Archive structured data
└─────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- Google Gemini API Key (Free tier available)
- Telegram Bot Token & Chat ID
- Notion API Key & Database ID
- GitHub account (for Actions)

## 🚀 Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd news-curator
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
NOTION_API_KEY=your_notion_api_key_here
NOTION_DB_ID=your_notion_database_id_here
MY_CITY=Daejeon
```

### 4. Get API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key to `.env`

#### Telegram Bot Token & Chat ID
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token to `.env`
4. Get your Chat ID:
   - Message your bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":123456789}` in the response
   - Copy the ID to `.env`

#### Notion API Key & Database ID
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it "Research Radar" and copy the API key
4. Create a new database in Notion
5. Click "..." → "Connections" → Add your integration
6. Copy the database ID from the URL:
   - URL format: `https://www.notion.so/workspace/<DATABASE_ID>?v=...`
   - The database ID is the 32-character hex string

#### Notion Database Schema
Your Notion database should have these properties:

| Property Name | Type | Description |
|--------------|------|-------------|
| Title | Title | Article title |
| URL | URL | Article link |
| Summary | Text | AI-generated summary |
| Tags | Multi-select | Relevant tags |
| Source | Select | Source (Hacker News, Reddit, etc.) |
| Date | Date | Publication date |
| RPi_Compatibility | Select | Raspberry Pi 5 compatibility status |

### 5. Test Locally

```bash
python main.py
```

### 6. Setup GitHub Actions (Optional)

1. Push your code to GitHub
2. Go to Repository Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `NOTION_API_KEY`
   - `NOTION_DB_ID`
   - `MY_CITY` (optional, defaults to 'Seoul')

The workflow will run daily at 08:00 KST (23:00 UTC).

## 📁 Project Structure

```
news-curator/
├── main.py              # Main orchestrator
├── scrapers.py          # Data source fetchers
├── ai_agent.py          # Gemini AI integration
├── notifier.py          # Telegram + Weather
├── notion_storage.py    # Notion archiving
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .github/
│   └── workflows/
│       └── daily.yml    # GitHub Actions workflow
└── README.md            # This file
```

## 🔧 Configuration

### Customize Sources

Edit `scrapers.py` to modify:
- Number of articles fetched per source
- Subreddits to monitor
- arXiv categories
- Google News search queries

### Adjust AI Filtering

Edit `ai_agent.py` to modify:
- Relevance criteria
- Summary format
- GitHub audit prompts

### Change Schedule

Edit `.github/workflows/daily.yml`:
```yaml
schedule:
  - cron: '0 23 * * *'  # Change to your preferred time (UTC)
```

## 🐛 Troubleshooting

### Rate Limiting Errors
- The script includes 2-second delays between Gemini API calls
- If you hit limits, increase `rate_limit_delay` in `ai_agent.py`

### Reddit 429 Errors
- Custom User-Agent is already configured
- If issues persist, add delays between subreddit requests

### Weather API Fails
- Non-critical error - defaults to "Unknown"
- Check city name spelling in `MY_CITY`

### Notion Errors
- Verify database schema matches requirements
- Ensure integration has access to the database
- Check API key permissions

## 📊 Example Output

```
📡 Research Radar Daily Briefing
Found 3 insights.

1. **TinyML Model Optimization for Edge Devices**
   💡 • 모델 크기 50% 감소
   • Raspberry Pi 5에서 실시간 추론 가능
   • 에너지 효율 3배 개선
   🛠 RPi Status: ✅ Runnable
   🔗 [Link]

2. **CUDA-Only Vision Transformer**
   💡 • 고성능 GPU 필요
   • 대규모 데이터셋 학습
   🛠 RPi Status: ❌ CUDA/x86 Only
   🔗 [Link]

---
🌡 Daejeon: ☀️ 15°C
🤖 Comment: "Perfect weather for debugging neural networks and sipping coffee!"
```

## 📝 License

MIT License - Feel free to use this project for your portfolio!

## 🤝 Contributing

This is a portfolio project, but suggestions and improvements are welcome!

---

**Built with ❤️ for the Edge AI community**
