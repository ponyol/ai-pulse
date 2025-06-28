#!/usr/bin/env python3
"""
Anthropic News RSS Feed Generator
Parses anthropic.com/news and generates RSS feed

This module scrapes the main Anthropic news page and extracts:
- Article titles
- Categories (Product, Policy, Announcements, etc.)
- Publication dates  
- Article URLs
- Images

Author: AI-PULSE Project
"""

import requests
import logging
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from urllib.parse import urljoin, urlparse
import re

# Setup logging
logger = logging.getLogger('anthropic-news')

# Configuration
BASE_URL = "https://www.anthropic.com"
NEWS_URL = f"{BASE_URL}/news"
OUTPUT_FILE = "feeds/feed_anthropic_news.xml"
USER_AGENT = "AI-PULSE RSS Generator 1.0 (github.com/your-username/ai-pulse)"

def get_page_content(url: str) -> BeautifulSoup:
    """Fetch and parse webpage content"""
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"✅ Successfully fetched: {url}")
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        logger.error(f"❌ Failed to fetch {url}: {e}")
        raise

def extract_articles(soup: BeautifulSoup) -> list:
    """Extract article information from the news page"""
    articles = []
    
    # Find all article cards/links
    # Based on the structure seen in the web_fetch results
    article_elements = soup.find_all(['a', 'article', 'div'], 
                                   class_=re.compile(r'.*card.*|.*article.*|.*post.*', re.I))
    
    logger.info(f"🔍 Found {len(article_elements)} potential article elements")
    
    for element in article_elements[:50]:  # Limit to avoid processing too many
        try:
            article = extract_single_article(element)
            if article:
                articles.append(article)
        except Exception as e:
            logger.debug(f"Error processing article element: {e}")
            continue
    
    logger.info(f"📰 Extracted {len(articles)} articles")
    return articles

def extract_single_article(element) -> dict:
    """Extract information from a single article element"""
    article = {}
    
    # Try to find title
    title_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        if len(title_text) > 10:  # Filter out short/empty titles
            article['title'] = title_text
    
    # Try to find URL
    if element.name == 'a':
        href = element.get('href')
    else:
        link_elem = element.find('a')
        href = link_elem.get('href') if link_elem else None
    
    if href:
        article['url'] = urljoin(BASE_URL, href)
    
    # Try to extract category/type information
    # Look for text that might indicate category
    category_indicators = ['Product', 'Policy', 'Announcements', 'Research', 
                          'Interpretability', 'Alignment', 'Societal Impacts']
    
    element_text = element.get_text()
    for indicator in category_indicators:
        if indicator in element_text:
            article['category'] = indicator
            break
    
    # Only return if we have both title and URL
    if 'title' in article and 'url' in article:
        # Set default values
        article['category'] = article.get('category', 'News')
        article['pub_date'] = datetime.now(timezone.utc)
        article['description'] = f"Latest from Anthropic: {article['title']}"
        return article
    
    return None

def generate_rss_feed(articles: list) -> None:
    """Generate RSS feed from articles"""
    logger.info("📡 Generating RSS feed...")
    
    # Create feed generator
    fg = FeedGenerator()
    fg.title('Anthropic News - AI-PULSE')
    fg.link(href=NEWS_URL, rel='alternate')
    fg.description('Latest news and announcements from Anthropic')
    fg.language('en')
    fg.lastBuildDate(datetime.now(timezone.utc))
    fg.generator('AI-PULSE RSS Generator')
    
    # Add articles to feed
    for article in articles[:50]:  # Limit to 50 most recent
        fe = fg.add_entry()
        fe.title(article['title'])
        fe.link(href=article['url'])
        fe.description(article['description'])
        fe.category(term=article['category'])
        fe.pubDate(article['pub_date'])
        fe.guid(article['url'], False)
    
    # Ensure output directory exists
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write RSS feed
    fg.rss_file(OUTPUT_FILE)
    logger.info(f"✅ RSS feed saved to: {OUTPUT_FILE}")
    logger.info(f"📊 Feed contains {len(articles)} articles")

def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Anthropic News RSS generation")
        
        # Fetch and parse the news page
        soup = get_page_content(NEWS_URL)
        
        # Extract articles
        articles = extract_articles(soup)
        
        if not articles:
            logger.warning("⚠️  No articles found!")
            return
        
        # Generate RSS feed
        generate_rss_feed(articles)
        
        logger.info("🎉 Anthropic News RSS generation completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
