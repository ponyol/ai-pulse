#!/usr/bin/env python3
"""
AI-PULSE RSS Monitor
Desktop integration for monitoring Anthropic RSS feeds

This script provides local monitoring capabilities for the AI-PULSE RSS feeds:
- Checks for new articles in generated RSS feeds
- Provides desktop notifications for new content
- Integrates with local workflow automation

Author: AI-PULSE Project
"""

import xml.etree.ElementTree as ET
import requests
import logging
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set
import subprocess
import platform

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('rss-monitor')

# Configuration
FEEDS_CONFIG = {
    'anthropic_complete': {
        'url': 'https://raw.githubusercontent.com/your-username/ai-pulse/main/feeds/feed_anthropic_complete.xml',
        'local_path': 'feeds/feed_anthropic_complete.xml',
        'priority': 'high'
    },
    'anthropic_news': {
        'url': 'https://raw.githubusercontent.com/your-username/ai-pulse/main/feeds/feed_anthropic_news.xml',
        'local_path': 'feeds/feed_anthropic_news.xml',
        'priority': 'medium'
    },
    'anthropic_engineering': {
        'url': 'https://raw.githubusercontent.com/your-username/ai-pulse/main/feeds/feed_anthropic_engineering.xml',
        'local_path': 'feeds/feed_anthropic_engineering.xml',
        'priority': 'high'
    },
    'anthropic_alignment': {
        'url': 'https://raw.githubusercontent.com/your-username/ai-pulse/main/feeds/feed_anthropic_alignment.xml',
        'local_path': 'feeds/feed_anthropic_alignment.xml',
        'priority': 'critical'
    }
}

CACHE_FILE = Path.home() / '.ai_pulse_cache.json'
CHECK_INTERVAL_HOURS = 2

class RSSMonitor:
    def __init__(self):
        self.cache = self.load_cache()
        self.new_articles = []
    
    def load_cache(self) -> Dict:
        """Load previously seen articles from cache"""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cache: {e}")
        return {'seen_articles': set(), 'last_check': None}
    
    def save_cache(self):
        """Save current cache state"""
        try:
            cache_data = {
                'seen_articles': list(self.cache['seen_articles']),
                'last_check': datetime.now().isoformat()
            }
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def fetch_feed(self, feed_name: str, config: Dict) -> List[Dict]:
        """Fetch and parse RSS feed"""
        articles = []
        
        try:
            # Try local file first, then remote URL
            sources = [config['local_path'], config['url']]
            
            for source in sources:
                try:
                    if source.startswith('http'):
                        response = requests.get(source, timeout=30)
                        response.raise_for_status()
                        content = response.content
                    else:
                        with open(source, 'rb') as f:
                            content = f.read()
                    
                    # Parse RSS
                    root = ET.fromstring(content)
                    
                    for item in root.findall('.//item'):
                        article = {
                            'title': item.find('title').text if item.find('title') is not None else 'No Title',
                            'link': item.find('link').text if item.find('link') is not None else '',
                            'description': item.find('description').text if item.find('description') is not None else '',
                            'pubDate': item.find('pubDate').text if item.find('pubDate') is not None else '',
                            'category': item.find('category').text if item.find('category') is not None else feed_name,
                            'feed_source': feed_name,
                            'priority': config['priority']
                        }
                        
                        # Create unique ID for article
                        article_id = hashlib.md5(f"{article['title']}{article['link']}".encode()).hexdigest()
                        article['id'] = article_id
                        
                        articles.append(article)
                    
                    logger.info(f"✅ Successfully fetched {len(articles)} articles from {feed_name}")
                    break
                    
                except Exception as e:
                    logger.debug(f"Failed to fetch from {source}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Error fetching feed {feed_name}: {e}")
        
        return articles
    
    def check_for_new_articles(self) -> List[Dict]:
        """Check all feeds for new articles"""
        all_new_articles = []
        
        for feed_name, config in FEEDS_CONFIG.items():
            logger.info(f"🔍 Checking feed: {feed_name}")
            
            articles = self.fetch_feed(feed_name, config)
            
            for article in articles:
                if article['id'] not in self.cache['seen_articles']:
                    all_new_articles.append(article)
                    self.cache['seen_articles'].add(article['id'])
        
        return all_new_articles
    
    def send_notification(self, article: Dict):
        """Send desktop notification for new article"""
        title = f"🤖 AI-PULSE: New {article['feed_source']}"
        message = f"{article['title'][:100]}..."
        
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                script = f'''
                display notification "{message}" with title "{title}"
                '''
                subprocess.run(["osascript", "-e", script], check=True)
            elif system == "Linux":
                subprocess.run(["notify-send", title, message], check=True)
            elif system == "Windows":
                # Windows notification (requires win10toast)
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(title, message, duration=10)
                except ImportError:
                    logger.warning("Windows notifications require win10toast package")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def generate_summary_report(self, new_articles: List[Dict]) -> str:
        """Generate summary report of new articles"""
        if not new_articles:
            return "No new articles found."
        
        # Group by priority and source
        by_priority = {'critical': [], 'high': [], 'medium': [], 'low': []}
        by_source = {}
        
        for article in new_articles:
            priority = article.get('priority', 'medium')
            source = article.get('feed_source', 'unknown')
            
            by_priority[priority].append(article)
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)
        
        report = f"📊 AI-PULSE Summary Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"📈 Total new articles: {len(new_articles)}\n\n"
        
        # By priority
        for priority in ['critical', 'high', 'medium', 'low']:
            articles = by_priority[priority]
            if articles:
                report += f"🔥 {priority.upper()} Priority ({len(articles)} articles):\n"
                for article in articles[:5]:  # Limit to 5 per priority
                    report += f"  • {article['title'][:80]}...\n"
                    report += f"    Source: {article['feed_source']} | {article['link']}\n"
                report += "\n"
        
        # By source
        report += "📰 By Source:\n"
        for source, articles in by_source.items():
            report += f"  {source}: {len(articles)} articles\n"
        
        return report
    
    def run_check(self):
        """Run a single check cycle"""
        logger.info("🚀 Starting AI-PULSE RSS check")
        
        new_articles = self.check_for_new_articles()
        
        if new_articles:
            logger.info(f"📢 Found {len(new_articles)} new articles!")
            
            # Send notifications for high priority articles
            for article in new_articles:
                if article.get('priority') in ['critical', 'high']:
                    self.send_notification(article)
            
            # Generate and log summary
            summary = self.generate_summary_report(new_articles)
            logger.info(f"\n{summary}")
            
            # Save summary to file
            summary_file = Path.home() / 'ai_pulse_summary.txt'
            with open(summary_file, 'w') as f:
                f.write(summary)
            
        else:
            logger.info("ℹ️  No new articles found")
        
        # Save cache
        self.save_cache()
        
        return new_articles

def main():
    """Main function"""
    monitor = RSSMonitor()
    monitor.run_check()

if __name__ == "__main__":
    main()
