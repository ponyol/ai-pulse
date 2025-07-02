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
    """Extract article information from the news page with deduplication"""
    articles = []
    seen_urls = set()  # For deduplication
    seen_titles = set()  # Additional title-based deduplication
    
    # Find all article cards/links - be more specific for anthropic.com
    article_elements = soup.find_all(['a', 'article', 'div'], 
                                   class_=re.compile(r'.*card.*|.*article.*|.*post.*|.*item.*|.*link.*', re.I))
    
    # Also look for direct article links
    article_links = soup.find_all('a', href=re.compile(r'.*/news/.*|.*/research/.*|.*/engineering/.*'))
    article_elements.extend(article_links)
    
    logger.info(f"🔍 Found {len(article_elements)} potential article elements")
    
    for element in article_elements[:100]:  # Increased limit but still reasonable
        try:
            article = extract_single_article(element)
            if article:
                # Deduplication by URL and title
                url = article['url']
                title = article['title'].lower().strip()
                
                if url not in seen_urls and title not in seen_titles:
                    articles.append(article)
                    seen_urls.add(url)
                    seen_titles.add(title)
                    logger.debug(f"✅ Added: {article['title'][:50]}...")
                else:
                    logger.debug(f"🔄 Skipped duplicate: {article['title'][:50]}...")
                    
        except Exception as e:
            logger.debug(f"Error processing article element: {e}")
            continue
    
    logger.info(f"📰 Extracted {len(articles)} unique articles (removed duplicates)")
    return articles

def extract_single_article(element) -> dict:
    """Extract information from a single article element with improved quality filtering"""
    article = {}
    
    # Try to find title - be more selective
    title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
    if not title_elem:
        # Fallback: look for strong text or element itself if it has good text
        title_elem = element.find('strong') or element
    
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        
        # Filter out junk titles
        junk_patterns = [
            'press inquiries', 'no results found', 'email us', 'contact',
            'featured', 'announcements', 'latest', 'more', 'read'
        ]
        
        # Clean up concatenated titles (remove prefix categories)
        clean_title = title_text
        for prefix in ['Featured', 'Announcements', 'Product', 'Policy']:
            if clean_title.startswith(prefix):
                clean_title = clean_title[len(prefix):].strip()
        
        # Skip if junk or too short/long
        if (len(clean_title) > 10 and len(clean_title) < 200 and 
            not any(junk in clean_title.lower() for junk in junk_patterns)):
            article['title'] = clean_title
    
    # Try to find URL with better validation
    href = None
    if element.name == 'a':
        href = element.get('href')
    else:
        link_elem = element.find('a')
        href = link_elem.get('href') if link_elem else None
    
    if href:
        # Filter out bad links
        bad_patterns = ['mailto:', 'javascript:', '#', 'tel:']
        if not any(pattern in href.lower() for pattern in bad_patterns):
            # Handle relative and absolute URLs properly
            if href.startswith('http'):
                article['url'] = href
            elif href.startswith('/'):
                article['url'] = BASE_URL + href
            else:
                article['url'] = urljoin(BASE_URL, href)
    
    # Try to extract better description
    description = ""
    desc_elem = element.find(['p', 'div'], class_=re.compile(r'.*desc.*|.*summary.*|.*excerpt.*', re.I))
    if desc_elem:
        description = desc_elem.get_text(strip=True)[:200]  # Limit length
    
    # Try to extract category/type information  
    category_indicators = ['Product', 'Policy', 'Announcements', 'Research', 
                          'Interpretability', 'Alignment', 'Societal Impacts']
    
    element_text = element.get_text()
    category = 'News'  # Default
    for indicator in category_indicators:
        if indicator in element_text:
            category = indicator
            break
    
    # Only return if we have both title and valid URL
    if 'title' in article and 'url' in article:
        article['category'] = category
        article['pub_date'] = datetime.now(timezone.utc)
        
        # Better description
        if description:
            article['description'] = f"{description[:150]}..."
        else:
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
