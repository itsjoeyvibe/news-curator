"""
Data scrapers for Research Radar - Aggregates tech news from 5 major sources.
Focus: Edge AI, Vision, Hardware, TinyML
"""

import requests
import feedparser
import time
from typing import List, Dict, Optional
from datetime import datetime


def fetch_hackernews(top_n: int = 30) -> List[Dict]:
    """
    Fetch top stories from Hacker News.
    
    Args:
        top_n: Number of top stories to fetch (default: 30)
    
    Returns:
        List of dictionaries with 'title', 'url', 'source', 'date'
    """
    try:
        # Get top story IDs
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        response.raise_for_status()
        top_story_ids = response.json()[:top_n]
        
        articles = []
        for story_id in top_story_ids:
            try:
                story_response = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    timeout=10
                )
                story_response.raise_for_status()
                story = story_response.json()
                
                if story and story.get('url'):
                    articles.append({
                        'title': story.get('title', 'No Title'),
                        'url': story.get('url'),
                        'source': 'Hacker News',
                        'date': datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                        'raw_content': story.get('title', '') + ' ' + story.get('text', '')
                    })
                time.sleep(0.1)  # Rate limiting
            except Exception as e:
                print(f"Error fetching HN story {story_id}: {e}")
                continue
        
        return articles
    except Exception as e:
        print(f"Error fetching Hacker News: {e}")
        return []


def fetch_reddit(subreddits: List[str] = None) -> List[Dict]:
    """
    Fetch new posts from specified Reddit subreddits.
    
    Args:
        subreddits: List of subreddit names (default: ['LocalLLaMA', 'ComputerVision', 'TinyML'])
    
    Returns:
        List of dictionaries with 'title', 'url', 'source', 'date'
    """
    if subreddits is None:
        subreddits = ['LocalLLaMA', 'ComputerVision', 'TinyML']
    
    articles = []
    headers = {
        'User-Agent': 'Research-Radar/1.0 (Educational Project; Contact: research-radar@example.com)'
    }
    
    for subreddit in subreddits:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=10"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post.get('data', {})
                    if post_data.get('url'):
                        articles.append({
                            'title': post_data.get('title', 'No Title'),
                            'url': post_data.get('url'),
                            'source': f'Reddit r/{subreddit}',
                            'date': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                            'raw_content': post_data.get('title', '') + ' ' + post_data.get('selftext', '')
                        })
            
            time.sleep(1)  # Rate limiting between subreddits
        except Exception as e:
            print(f"Error fetching Reddit r/{subreddit}: {e}")
            continue
    
    return articles


def fetch_arxiv(max_results: int = 10) -> List[Dict]:
    """
    Fetch recent papers from arXiv (Computer Vision & Robotics).
    
    Args:
        max_results: Maximum number of papers to fetch (default: 10)
    
    Returns:
        List of dictionaries with 'title', 'url', 'source', 'date'
    """
    try:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            'search_query': 'cat:cs.CV+OR+cat:cs.RO',
            'sortBy': 'submittedDate',
            'sortOrder': 'descending',
            'max_results': max_results
        }
        
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        articles = []
        
        for entry in feed.entries:
            articles.append({
                'title': entry.get('title', 'No Title'),
                'url': entry.get('link', ''),
                'source': 'arXiv',
                'date': entry.get('published', ''),
                'raw_content': entry.get('title', '') + ' ' + entry.get('summary', '')
            })
        
        return articles
    except Exception as e:
        print(f"Error fetching arXiv: {e}")
        return []


def fetch_huggingface() -> List[Dict]:
    """
    Fetch trending papers from Hugging Face Daily Papers.
    
    Returns:
        List of dictionaries with 'title', 'url', 'source', 'date'
    """
    try:
        url = "https://huggingface.co/api/daily_papers"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        articles = []
        
        # Handle different possible response formats
        papers = data if isinstance(data, list) else data.get('papers', [])
        
        for paper in papers[:10]:  # Limit to top 10
            if isinstance(paper, dict):
                articles.append({
                    'title': paper.get('title', paper.get('name', 'No Title')),
                    'url': paper.get('url', paper.get('link', '')),
                    'source': 'Hugging Face',
                    'date': paper.get('date', datetime.now().isoformat()),
                    'raw_content': paper.get('title', '') + ' ' + paper.get('abstract', paper.get('summary', ''))
                })
        
        return articles
    except Exception as e:
        print(f"Error fetching Hugging Face: {e}")
        return []


def fetch_google_news() -> List[Dict]:
    """
    Fetch news from Google News RSS feed.
    Focus: TinyML, Raspberry Pi AI, Edge Computing, NPU
    
    Returns:
        List of dictionaries with 'title', 'url', 'source', 'date'
    """
    try:
        rss_url = (
            "https://news.google.com/rss/search?"
            "q=TinyML+OR+Raspberry+Pi+AI+OR+Edge+Computing+OR+NPU"
            "&hl=en-US&gl=US&ceid=US:en"
        )
        
        feed = feedparser.parse(rss_url)
        articles = []
        
        for entry in feed.entries[:15]:  # Limit to top 15
            articles.append({
                'title': entry.get('title', 'No Title'),
                'url': entry.get('link', ''),
                'source': 'Google News',
                'date': entry.get('published', datetime.now().isoformat()),
                'raw_content': entry.get('title', '') + ' ' + entry.get('summary', '')
            })
        
        return articles
    except Exception as e:
        print(f"Error fetching Google News: {e}")
        return []


def aggregate_all_sources() -> List[Dict]:
    """
    Aggregate articles from all 5 sources.
    
    Returns:
        Combined list of all articles from all sources
    """
    print("🔍 Aggregating articles from all sources...")
    
    all_articles = []
    
    print("  📰 Fetching Hacker News...")
    all_articles.extend(fetch_hackernews())
    
    print("  🔴 Fetching Reddit...")
    all_articles.extend(fetch_reddit())
    
    print("  📚 Fetching arXiv...")
    all_articles.extend(fetch_arxiv())
    
    print("  🤗 Fetching Hugging Face...")
    all_articles.extend(fetch_huggingface())
    
    print("  🌐 Fetching Google News...")
    all_articles.extend(fetch_google_news())
    
    print(f"✅ Aggregated {len(all_articles)} articles total")
    return all_articles
